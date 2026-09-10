import argparse
import datetime
import json
from pathlib import Path

import numpy as np
import optuna
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import KFold

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

N_TRIALS = 100
N_FOLDS = 5
SEED = 42

TAXONOMY_COLS = ["kingdom", "phylum", "class", "order", "family", "genus", "species"]


# ---------------------------------------------------------------------------
# Shared helper (copied from decision_tree.py)
# ---------------------------------------------------------------------------


def align_categories(train_df, test_df):
    """
    This function ensures that both the test and training set contain
    all unique categories from both sets for each column.
    It also adds

    Args:
        train_df (pandas dataframe): _description_
        test_df (pandas dataframe): _description_

    Returns:
        a tuple of the reformatted x_train and x_test with shared
        categories and UNK added
    """
    for col in train_df.select_dtypes(include="str").columns:
        train_df[col] = train_df[col].astype("category")
        test_df[col] = test_df[col].astype("category")

        # adds the UNK category and both train and test categories
        categories = list(
            set(train_df[col].cat.categories)
            | set(list(test_df[col].cat.categories))
            | {"UNK"}  # noqa: E501
        )

        train_df[col] = train_df[col].cat.set_categories(categories)
        test_df[col] = test_df[col].cat.set_categories(categories)

    return train_df, test_df


# ---------------------------------------------------------------------------
# GPBoost helper (adapted from gpboost_model.py — single-df, no test alignment)
# ---------------------------------------------------------------------------


def align_gpboost(df, cols):
    """Convert taxonomy columns to Categorical with UNK sentinel."""
    out = df[cols].copy()
    for col in cols:
        out[col] = out[col].fillna("UNK")
        cats = sorted(set(out[col].unique()) | {"UNK"})
        out[col] = pd.Categorical(out[col], categories=cats)
    return out


# ---------------------------------------------------------------------------
# Entity Embeddings helpers (copied from entity_embeddings_model.py)
# ---------------------------------------------------------------------------

EMB_DIMS = {
    "kingdom": 4,
    "phylum": 8,
    "class": 8,
    "order": 16,
    "family": 16,
    "genus": 32,
    "species": 32,
}
TOTAL_DIM = sum(EMB_DIMS.values())  # 116


def build_vocabs(train_df):
    """Build per-column vocabulary from training data; UNK always at index 0."""
    vocabs = {}
    for col in TAXONOMY_COLS:
        unique_vals = sorted(train_df[col].dropna().astype(str).unique())
        vocabs[col] = ["UNK"] + unique_vals  # 0 = UNK
    return vocabs


def encode(df, vocabs):
    """Map each column to its integer index; unknowns → 0 (UNK)."""
    n = len(df)
    out = np.zeros((n, len(TAXONOMY_COLS)), dtype=np.int64)
    for j, col in enumerate(TAXONOMY_COLS):
        v2i = {v: i for i, v in enumerate(vocabs[col])}
        vals = df[col].fillna("UNK").astype(str)
        out[:, j] = [v2i.get(v, 0) for v in vals]
    return out


def make_emb_features(df, embeddings):
    """Build (n, TOTAL_DIM) float32 matrix from embedding lookup tables."""
    n = len(df)
    X = np.zeros((n, TOTAL_DIM), dtype=np.float32)
    offset = 0
    for col in TAXONOMY_COLS:
        dim = EMB_DIMS[col]
        col_embs = embeddings[col]
        unk_vec = np.array(col_embs["UNK"], dtype=np.float32)
        vals = df[col].fillna("UNK").astype(str)
        for i, val in enumerate(vals):
            vec = col_embs.get(val, unk_vec)
            X[i, offset : offset + dim] = vec
        offset += dim
    return X


def _build_embedding_mlp_and_train(X_codes, y, vocabs, device):
    """Train a PyTorch EmbeddingMLP and return (model, get_embeddings_fn)."""
    import torch
    import torch.nn as nn
    from torch.optim.lr_scheduler import OneCycleLR
    from torch.utils.data import DataLoader, TensorDataset

    STAGE1_EPOCHS = 100
    STAGE1_BATCH_SIZE = 256
    STAGE1_LR = 1e-3

    class EmbeddingMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.emb_layers = nn.ModuleList(
                [
                    nn.Embedding(len(vocabs[col]), EMB_DIMS[col], padding_idx=None)
                    for col in TAXONOMY_COLS
                ]
            )
            self.mlp = nn.Sequential(
                nn.Linear(TOTAL_DIM, 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1),
            )

        def forward(self, x):
            embs = [self.emb_layers[j](x[:, j]) for j in range(len(TAXONOMY_COLS))]
            h = torch.cat(embs, dim=1)
            return self.mlp(h).squeeze(1)

        def get_embeddings(self):
            result = {}
            for j, col in enumerate(TAXONOMY_COLS):
                W = self.emb_layers[j].weight.detach().cpu().numpy()
                v2e = {v: W[i].tolist() for i, v in enumerate(vocabs[col])}
                v2e["UNK"] = (  # noqa: E501
                    W[1:].mean(axis=0).tolist() if len(W) > 1 else W[0].tolist()
                )
                result[col] = v2e
            return result

    model = EmbeddingMLP().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=STAGE1_LR)
    X_t = torch.from_numpy(X_codes).long().to(device)
    y_t = torch.from_numpy(y.astype(np.float32)).to(device)
    ds = TensorDataset(X_t, y_t)
    dl = DataLoader(ds, batch_size=STAGE1_BATCH_SIZE, shuffle=True, drop_last=False)
    sched = OneCycleLR(
        opt, max_lr=STAGE1_LR, epochs=STAGE1_EPOCHS, steps_per_epoch=len(dl)
    )  # noqa: E501
    loss_fn = nn.L1Loss()

    model.train()
    for epoch in range(1, STAGE1_EPOCHS + 1):
        total_loss = 0.0
        for xb, yb in dl:
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()
            sched.step()
            total_loss += loss.item() * len(xb)
        if epoch % 10 == 0:
            print(f"  Epoch {epoch:3d}/{STAGE1_EPOCHS}  MAE={total_loss/len(ds):.4f}")

    model.eval()
    return model


# ---------------------------------------------------------------------------
# XGBoost tuner
# ---------------------------------------------------------------------------


def tune_xgboost():
    train = pd.read_csv(REPO_ROOT / "data" / "split" / "train.csv")
    test = pd.read_csv(REPO_ROOT / "data" / "split" / "test.csv")
    train["mass_g"] = np.log10(train["mass_g"])

    y_full = train["mass_g"]
    x_full = train.drop(["mass_g"], axis=1)
    x_test = test.drop(["mass_g"], axis=1)
    x_full, x_test = align_categories(x_full, x_test)

    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

    def objective(trial):
        params = dict(
            objective="reg:absoluteerror",
            enable_categorical=True,
            random_state=SEED,
            n_estimators=trial.suggest_int("n_estimators", 200, 900, step=50),
            max_depth=trial.suggest_int("max_depth", 5, 50),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.30, log=True),
            subsample=trial.suggest_float("subsample", 0.5, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
            gamma=trial.suggest_float("gamma", 0.0, 1.0),
            min_child_weight=trial.suggest_int("min_child_weight", 1, 10),
        )
        fold_maes = []
        for train_idx, val_idx in kf.split(x_full):
            model = xgb.XGBRegressor(**params)
            model.fit(x_full.iloc[train_idx], y_full.iloc[train_idx])
            preds = model.predict(x_full.iloc[val_idx])
            fold_maes.append(float(np.mean(np.abs(y_full.iloc[val_idx] - preds))))
        return float(np.mean(fold_maes))

    sampler = optuna.samplers.TPESampler(seed=SEED)
    study = optuna.create_study(
        study_name="tbml_tuning",
        storage="sqlite:///" + str(RESULTS_DIR / "tuning.db"),
        direction="minimize",
        sampler=sampler,
        load_if_exists=True,
    )
    study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=True)

    results = {
        "best_params": study.best_params,
        "best_cv_mae": study.best_value,
        "n_trials": N_TRIALS,
        "n_folds": N_FOLDS,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "current_params": {
            "n_estimators": 600,
            "max_depth": 40,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "gamma": 0,
            "min_child_weight": 1,
        },
        "all_trials": [
            {"number": t.number, "params": t.params, "cv_mae": t.value}
            for t in study.trials
            if t.state == optuna.trial.TrialState.COMPLETE
        ],
    }
    out = RESULTS_DIR / "tuning_study.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nBest CV MAE : {study.best_value:.4f} log10")
    print(f"Best params : {study.best_params}")
    print(f"Saved       -> {out}")


# ---------------------------------------------------------------------------
# GPBoost tuner
# ---------------------------------------------------------------------------


def tune_gpboost():
    import gpboost as gpb

    GROUP_COLS = ["species", "genus", "family", "order", "class"]

    train = pd.read_csv(REPO_ROOT / "data" / "split" / "train.csv")
    train["mass_g"] = np.log10(train["mass_g"])

    X_gpb = align_gpboost(train, TAXONOMY_COLS)
    y_gpb = train["mass_g"].values
    gd_full = train[GROUP_COLS].fillna("UNK").astype(str).to_numpy()

    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

    def objective(trial):
        params = {
            "objective": "regression",
            "verbose": -1,
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.30, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "num_leaves": trial.suggest_int("num_leaves", 7, 63),
            "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 1, 20),
        }
        num_boost_round = trial.suggest_int("num_boost_round", 50, 300, step=25)
        fold_maes = []
        for train_idx, val_idx in kf.split(X_gpb):
            X_tr = X_gpb.iloc[train_idx].reset_index(drop=True)
            X_vl = X_gpb.iloc[val_idx].reset_index(drop=True)
            y_tr, y_vl = y_gpb[train_idx], y_gpb[val_idx]
            gd_tr, gd_vl = gd_full[train_idx], gd_full[val_idx]
            gp_model = gpb.GPModel(group_data=gd_tr, likelihood="gaussian")
            gp_model.set_optim_params(
                {"optimizer_cov": "lbfgs", "use_nesterov_acc": True, "maxit": 20}
            )
            dataset = gpb.Dataset(X_tr, label=y_tr, free_raw_data=False)
            booster = gpb.train(
                params=params,
                train_set=dataset,
                gp_model=gp_model,
                num_boost_round=num_boost_round,
            )
            preds = booster.predict(data=X_vl, group_data_pred=gd_vl)["response_mean"]
            fold_maes.append(float(np.mean(np.abs(y_vl - preds))))
        return float(np.mean(fold_maes))

    sampler = optuna.samplers.TPESampler(seed=SEED)
    study = optuna.create_study(
        study_name="tbml_gpboost",
        storage="sqlite:///" + str(RESULTS_DIR / "tuning_gpboost.db"),
        direction="minimize",
        sampler=sampler,
        load_if_exists=True,
    )

    def _stop_at_n(study, trial):
        done = sum(
            1 for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE
        )  # noqa: E501
        if done >= N_TRIALS:
            study.stop()

    study.optimize(
        objective, n_trials=N_TRIALS, show_progress_bar=True, callbacks=[_stop_at_n]
    )  # noqa: E501

    results = {
        "best_params": study.best_params,
        "best_cv_mae": study.best_value,
        "n_trials": N_TRIALS,
        "n_folds": N_FOLDS,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "current_params": {
            "num_boost_round": 500,
            "learning_rate": 0.05,
            "max_depth": 12,
            "num_leaves": 127,
            "min_data_in_leaf": 1,
        },
        "all_trials": [
            {"number": t.number, "params": t.params, "cv_mae": t.value}
            for t in study.trials
            if t.state == optuna.trial.TrialState.COMPLETE
        ],
    }
    out = RESULTS_DIR / "tuning_study_gpboost.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nBest CV MAE : {study.best_value:.4f} log10")
    print(f"Best params : {study.best_params}")
    print(f"Saved       -> {out}")


# ---------------------------------------------------------------------------
# Entity Embeddings Stage 2 tuner
# ---------------------------------------------------------------------------


def tune_ee():
    import torch

    torch.set_num_threads(1)  # prevent libomp conflict with xgboost/sklearn OpenMP

    train = pd.read_csv(REPO_ROOT / "data" / "split" / "train.csv")
    train["mass_g"] = np.log10(train["mass_g"])
    y_full_ee = train["mass_g"].values

    vocabs = build_vocabs(train)
    X_codes = encode(train, vocabs)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Stage 1: pre-training MLP for EE tuning (done once)...")
    mlp = _build_embedding_mlp_and_train(X_codes, y_full_ee, vocabs, device)
    embeddings = mlp.get_embeddings()
    X_emb_full = make_emb_features(train, embeddings)

    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

    def objective(trial):
        params = dict(
            objective="reg:absoluteerror",
            random_state=SEED,
            n_estimators=trial.suggest_int("n_estimators", 200, 800, step=50),
            max_depth=trial.suggest_int("max_depth", 4, 15),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.30, log=True),
            subsample=trial.suggest_float("subsample", 0.5, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
            min_child_weight=trial.suggest_int("min_child_weight", 1, 10),
        )
        fold_maes = []
        for train_idx, val_idx in kf.split(X_emb_full):
            model = xgb.XGBRegressor(**params)
            model.fit(X_emb_full[train_idx], y_full_ee[train_idx])
            preds = model.predict(X_emb_full[val_idx])
            fold_maes.append(float(np.mean(np.abs(y_full_ee[val_idx] - preds))))
        return float(np.mean(fold_maes))

    sampler = optuna.samplers.TPESampler(seed=SEED)
    study = optuna.create_study(
        study_name="tbml_ee",
        storage="sqlite:///" + str(RESULTS_DIR / "tuning_ee.db"),
        direction="minimize",
        sampler=sampler,
        load_if_exists=True,
    )
    study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=True)

    results = {
        "best_params": study.best_params,
        "best_cv_mae": study.best_value,
        "n_trials": N_TRIALS,
        "n_folds": N_FOLDS,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "current_params": {
            "n_estimators": 400,
            "max_depth": 8,
            "learning_rate": 0.1,
            "subsample": 0.8,
        },
        "all_trials": [
            {"number": t.number, "params": t.params, "cv_mae": t.value}
            for t in study.trials
            if t.state == optuna.trial.TrialState.COMPLETE
        ],
    }
    out = RESULTS_DIR / "tuning_study_ee.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nBest CV MAE : {study.best_value:.4f} log10")
    print(f"Best params : {study.best_params}")
    print(f"Saved       -> {out}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hyperparameter tuning for TaxonBodyMassML models."
    )
    parser.add_argument(
        "--model",
        choices=["xgboost", "gpboost", "ee"],
        default="xgboost",
        help="Which model to tune (default: xgboost)",
    )
    args = parser.parse_args()

    if args.model == "xgboost":
        tune_xgboost()
    elif args.model == "gpboost":
        tune_gpboost()
    elif args.model == "ee":
        tune_ee()
