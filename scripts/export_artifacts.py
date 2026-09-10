"""
Export model artifacts for the TaxonBodyMassML R and Python packages.

Run from the repository root:
    python scripts/export_artifacts.py

Outputs (in artifacts/):
    model.ubj              -- XGBoost model (~2 GB, binary UBJSON)
    calibration.json       -- pooled XGBoost conformal calibration residuals
    calibration_by_rank.json -- rank-stratified XGBoost calibration residuals
    categories.json        -- valid training category sets per column
    lookup.json            -- species → {mass_g, source} lookup
    model_gpboost.json     -- GPBoost model (trees + GP parameters + BLUPs)
    calibration_gpboost.json -- GPBoost conformal calibration residuals
    embeddings.json        -- EE embedding lookup {col: {value: [floats]}}
    model_ee.ubj           -- Entity Embeddings Stage 2 XGBoost model
    calibration_ee.json    -- EE conformal calibration residuals
    checksums.json         -- SHA-256 for all artifact files above

Prerequisites: run the training scripts first to generate the new method artifacts:
    python predictive_models/gpboost_model.py
    python predictive_models/entity_embeddings_model.py

Upload all files to the Hugging Face model repository:
    https://huggingface.co/marknovak/TaxonBodyMassML

Using the huggingface_hub CLI:
    pip install huggingface_hub
    huggingface-cli login
    huggingface-cli upload marknovak/TaxonBodyMassML artifacts/ . --repo-type model

The Python and R packages download these files on first use and cache them locally.
Bundle checksums from artifacts/checksums.json into the package source files.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pickleslicer
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_PKL = REPO_ROOT / "regressor_microservice" / "sliced_model" / "xgboost_model.pkl"
TRAIN_CSV = REPO_ROOT / "data" / "split" / "train.csv"
RAW_CSV = REPO_ROOT / "data" / "TaxonBodyMass.csv"
OUT_DIR = REPO_ROOT / "artifacts"
OUT_DIR.mkdir(exist_ok=True)

TAXONOMY_COLS = ["kingdom", "phylum", "class", "order", "family", "genus", "species"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# 1. Load pickleslicer bundle
# ---------------------------------------------------------------------------
print("Loading pickleslicer bundle...")
bundle = pickleslicer.load(str(MODEL_PKL))
model = bundle["model"]
print("  Model loaded.")

# ---------------------------------------------------------------------------
# 2. Export XGBoost model to binary UBJSON format
#    .ubj is ~25% smaller than .json and faster to load; still cross-platform
# ---------------------------------------------------------------------------
model_path = OUT_DIR / "model.ubj"
model.save_model(str(model_path))
size_gb = model_path.stat().st_size / 1e9
print(f"  Saved model → {model_path}  ({size_gb:.2f} GB)")

# ---------------------------------------------------------------------------
# 3. Extract category sets in training-time code order from model cats.enc
#    This ordering is critical: R's xgb.DMatrix uses 0-based factor codes,
#    so categories must be listed in the order the model assigned integer codes
#    during training. Alphabetical order (used before) caused wrong R predictions.
#    We extract these FIRST so they can be used to encode calibration data with
#    the exact same integer codes the model saw at training time.
# ---------------------------------------------------------------------------
print("Extracting category sets from model (training-time code order)...")
booster = model.get_booster()
model_raw = json.loads(booster.save_raw(raw_format="json"))
cats_data = model_raw["learner"]["gradient_booster"]["model"]["cats"]
enc = cats_data["enc"]
feature_names_model = model_raw["learner"]["feature_names"]

categories = {}
for feat_idx, fname in enumerate(feature_names_model):
    e = enc[feat_idx]
    offsets = e["offsets"]
    values = e["values"]
    strings = [
        bytes(v & 0xFF for v in values[offsets[i] : offsets[i + 1]]).decode("utf-8")
        for i in range(len(offsets) - 1)
    ]
    categories[fname] = strings  # index == training-time integer code
    print(f"  {fname}: {len(strings)} categories (incl. UNK)")

# ---------------------------------------------------------------------------
# 4. Rebuild calibration residuals.
#    The model was trained with x_train2 / x_calib produced by a 80/20 split
#    of (train.csv after align_categories with test.csv).  We cannot reproduce
#    that exact category encoding from the stored JSON because a XGBoost
#    serialisation bug mis-counts the byte offsets for categories that contain
#    multi-byte UTF-8 characters, making the offset-based extraction unreliable.
#    Instead we pass the raw train.csv string columns (object dtype) directly so
#    that XGBoost performs its own internal string→code lookup, which is always
#    correct.  The rebuilt q will be very close to (but not identical to) the
#    stored q because the calibration split includes a handful of species that
#    only appeared in test.csv during training (treated as UNK here vs. known
#    there); the 90th-percentile shift is on the order of 0.004 log10 (~0.9%)
#    and is scientifically negligible.
# ---------------------------------------------------------------------------
print("Rebuilding calibration residuals from train.csv...")
train = pd.read_csv(TRAIN_CSV)
train["mass_g"] = np.log10(train["mass_g"])

y_train_full = train["mass_g"]
x_train_full = train.drop(["mass_g"], axis=1)

# Use the unique values from train.csv + UNK as categories.  This matches
# the structure of the training Categorical (which used align_categories on
# train+test; train-only values are a valid subset of the model's categories,
# and any train-only value will be found in the model's internal hash map).
for col in TAXONOMY_COLS:
    x_train_full[col] = x_train_full[col].astype("category")
    cats = list(set(x_train_full[col].cat.categories) | {"UNK"})
    x_train_full[col] = x_train_full[col].cat.set_categories(cats)

x_train2, x_calib, y_train2, y_calib = train_test_split(
    x_train_full, y_train_full, test_size=0.2, random_state=42
)

y_calib_pred = model.predict(x_calib)
residuals = np.abs(y_calib.values - y_calib_pred)
residuals_sorted = sorted(float(r) for r in residuals)

calibration_path = OUT_DIR / "calibration.json"
with open(calibration_path, "w") as f:
    json.dump({"residuals": residuals_sorted}, f)
print(f"  Saved {len(residuals_sorted)} residuals → {calibration_path}")

q_rebuilt = float(np.quantile(residuals, 0.90))
q_stored = float(bundle["q"])
print(f"  q rebuilt: {q_rebuilt:.6f}  |  q stored: {q_stored:.6f}")
if abs(q_rebuilt - q_stored) > 0.05:
    raise RuntimeError(
        f"Rebuilt q ({q_rebuilt:.6f}) differs from stored q ({q_stored:.6f}) "
        "by more than 0.05 — likely wrong training data or wrong random_state."
    )

# ---------------------------------------------------------------------------
# 4b. Build rank-stratified calibration residuals.
#     For each rank, mask all finer-rank columns to "UNK" in the calibration
#     set and recompute predictions.  This matches the inference condition for
#     each rank (e.g. genus-level queries have species=UNK; family-level have
#     genus=UNK and species=UNK) and is used by the "stratified" interval
#     method to approximate rank-conditional coverage guarantees.
# ---------------------------------------------------------------------------
print("Building rank-stratified calibration residuals...")
RANKS_FINER = {
    "genus": ["species"],
    "family": ["genus", "species"],
    "order": ["family", "genus", "species"],
    "class": ["order", "family", "genus", "species"],
    "phylum": ["class", "order", "family", "genus", "species"],
    "kingdom": ["phylum", "class", "order", "family", "genus", "species"],
}

by_rank_residuals = {}
for rank, finer_cols in RANKS_FINER.items():
    x_masked = x_calib.copy()
    for col in finer_cols:
        x_masked[col] = pd.Categorical(
            ["UNK"] * len(x_masked),
            categories=x_calib[col].cat.categories,
        )
    y_pred_rank = model.predict(x_masked)
    res_rank = np.abs(y_calib.values - y_pred_rank)
    by_rank_residuals[rank] = sorted(float(r) for r in res_rank)
    q_rank = float(np.quantile(res_rank, 0.90))
    print(f"  {rank}: {len(res_rank)} samples, q90={q_rank:.4f}")

by_rank_path = OUT_DIR / "calibration_by_rank.json"
with open(by_rank_path, "w") as f:
    json.dump(by_rank_residuals, f)
print(f"  Saved rank-stratified residuals → {by_rank_path}")

categories_path = OUT_DIR / "categories.json"
with open(categories_path, "w") as f:
    json.dump(categories, f, indent=2)
print(f"  Saved categories → {categories_path}")

# ---------------------------------------------------------------------------
# 5. Build species → {mass_g, source} lookup table from raw training data.
#    Keys are space-normalized species names (underscores replaced with spaces)
#    matching the species_resolved values returned by the taxonomy lookup.
# ---------------------------------------------------------------------------
print("Building species lookup table from raw training data...")
raw = pd.read_csv(RAW_CSV)
raw["_key"] = raw["taxon"].astype(str).str.replace("_", " ", regex=False)
n_before = len(raw)
raw = raw.drop_duplicates(subset="_key", keep="first")
if len(raw) < n_before:
    print(
        f"  WARNING: {n_before - len(raw)} duplicate taxon(s) dropped (keeping first row)."  # noqa: E501
    )  # noqa: E501
lookup = {
    row["_key"]: {
        "mass_g": float(row["mass_g"]),
        "source": str(row["source_mass"]),
    }
    for _, row in raw.iterrows()
}
lookup_path = OUT_DIR / "lookup.json"
with open(lookup_path, "w") as f:
    json.dump(lookup, f)
print(f"  Saved {len(lookup)} species → {lookup_path}")

# ---------------------------------------------------------------------------
# 6. Compute per-file SHA256 checksums (core four XGBoost artifacts)
# ---------------------------------------------------------------------------
print("Computing SHA256 checksums...")
checksums = {}
for fname, path in [
    ("model.ubj", model_path),
    ("calibration.json", calibration_path),
    ("calibration_by_rank.json", by_rank_path),
    ("categories.json", categories_path),
    ("lookup.json", lookup_path),
]:
    checksums[fname] = sha256_file(path)
    print(f"  {fname}: {checksums[fname]}")

# ---------------------------------------------------------------------------
# 7. Compute checksums for new-method artifacts (if present)
#    These are generated by:
#        python predictive_models/gpboost_model.py
#        python predictive_models/entity_embeddings_model.py
# ---------------------------------------------------------------------------
new_artifacts = [
    "model_gpboost.json",
    "calibration_gpboost.json",
    "calibration_by_rank_gpboost.json",
    "embeddings.json",
    "model_ee.ubj",
    "calibration_ee.json",
    "calibration_by_rank_ee.json",
]
for fname in new_artifacts:
    path = OUT_DIR / fname
    if path.exists():
        checksums[fname] = sha256_file(path)
        print(f"  {fname}: {checksums[fname]}")
    else:
        print(f"  {fname}: MISSING — run the training script first (see docstring)")

checksums_path = OUT_DIR / "checksums.json"
with open(checksums_path, "w") as f:
    json.dump(checksums, f, indent=2)
print(f"  Written to {checksums_path}")

# ---------------------------------------------------------------------------
# 8. Instructions
# ---------------------------------------------------------------------------
print("""
Done. To publish:

    make publish          # uploads artifacts/ and creates the r-v<version> HF tag

Then copy the checksums from artifacts/checksums.json into the package
source files (Python: packages/python/taxonbodymassml/_checksums.py; R:
packages/r/R/model.R).
""")
