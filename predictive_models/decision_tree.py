"""
pasquang
pasquang@oregonstate.edu
3/12/2026
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb
import pickle
from sklearn.metrics import mean_squared_error, r2_score

MODEL_WRITE_FILE = './regressor_microservice/xgboost_model.pkl'

# import training and testing data
train = pd.read_csv("./data/train.csv")
test = pd.read_csv("./data/test.csv")

# convert mass to log10 to avoid rounding error
# + reduce loss effect of large outliers
train["mass_g"] = np.log10(train["mass_g"])
test["mass_g"] = np.log10(test["mass_g"])

print("The Training Data is\n", train.head())
print("The Testing Data is\n", test.head())

# needs to remove other data when full taxonomy is created
# keep and remove labels from training and test data

y_train = train["mass_g"]
x_train = train.drop(["mass_g"], axis=1)

y_test = test["mass_g"]
x_test = test.drop(["mass_g"], axis=1)

def align_categories(train_df, test_df):
    """
    This function ensures that both the test and training set contain
    all unique categories from both sets for each column.
    It also adds

    Args:
        train_df (pandas dataframe): _description_
        test_df (pandas dataframe): _description_

    Returns:
        a tuple of the reformatted x_train and x_test with shared categories and UNK added
    """
    for col in train_df.select_dtypes(include="object").columns:
        train_df[col] = train_df[col].astype("category")
        test_df[col] = test_df[col].astype("category")

        # adds the UNK category and both train and test categories
        categories = list(set(train_df[col].cat.categories) |
                          set(list(test_df[col].cat.categories)) |
                          {"UNK"})

        train_df[col] = train_df[col].cat.set_categories(categories)
        test_df[col] = test_df[col].cat.set_categories(categories)

    return train_df, test_df

x_train, x_test = align_categories(x_train, x_test)

# define model hyperparameters
model = xgb.XGBRegressor(
    objective="reg:absoluteerror",
    n_estimators=1000,
    max_depth=50,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    enable_categorical=True,
    random_state=42,
)

# train the model
model.fit(x_train, y_train)

# evaluate the test set
y_pred = model.predict(x_test)

# evaluate in log space
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("RMSE:", rmse)
print("R2 Score:", r2)

# need to convert log10 mass to actual mass
y_test = np.pow(10, y_test)
y_pred = np.pow(10, y_pred)

# Plot predicted vs actual
plt.loglog()
plt.scatter(y_test, y_pred)
plt.xlabel("Actual Mass (g)")
plt.ylabel("Predicted Mass (g)")
plt.title("XGBoost: Actual vs Predicted")
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "--")

plt.savefig("xgboost_mass_prediction.png")
plt.show()

# Save the model using pickle
with open(MODEL_WRITE_FILE, 'wb') as f:
    pickle.dump(model, f)

# Test if unknown values will cause the model to crash in eval
print("\n")
print("-" * 80)
print("\n")
for col in x_train.select_dtypes(include="category").columns:
    unk_test = x_test.iloc[[0]].copy()
    unk_test[col] = "UNK"
    unk_test[col] = pd.Categorical(
        unk_test[col],
        categories=x_train[col].cat.categories
    )
    print(unk_test)
    print("Ground Truth Mass:", y_test.iloc[0])
    pred = model.predict(unk_test)
    print("Predicted Log Mass:", pred)
    print("Predicted Mass:", np.pow(10, pred))
    
