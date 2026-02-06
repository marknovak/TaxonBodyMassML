"""
pasquang
pasquang@oregonstate.edu
2/6/2026
"""

import xgboost as xgb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import mean_squared_error, r2_score

#import training and testing data
train = pd.read_csv("./data/train.csv")
test = pd.read_csv("./data/test.csv")
train["mass_g"] = np.log10(train["mass_g"])
test["mass_g"] = np.log10(test["mass_g"])

print("The Training Data is\n", train.head())
print("The Testing Data is\n", test.head())

#needs to remove other data when full taxonomy is created
# keep and remove labels from training and test data

y_train = train["mass_g"]
x_train = train.drop(["mass_g"], axis=1)

y_test = test["mass_g"]
x_test = test.drop(["mass_g"], axis=1)

combined = pd.concat([x_train, x_test], axis=0)

for col in combined.columns:
    if combined[col].dtype == "object":

        combined[col] = combined[col].astype("category")
        
x_train = combined.iloc[:len(x_train)].copy()
x_test = combined.iloc[len(x_train):].copy()

model = xgb.XGBRegressor(
    objective="reg:squarederror",
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    enable_categorical=True,
    random_state=42
)

model.fit(x_train, y_train)

y_pred = model.predict(x_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("RMSE:", rmse)
print("R2 Score:", r2)

# need to convert log10 mass to actual mass
y_test = np.power(10, y_test)
y_pred = np.power(10, y_pred)

# Plot predicted vs actual
plt.loglog()
plt.scatter(y_test, y_pred)
plt.xlabel("Actual Mass (g)")
plt.ylabel("Predicted Mass (g)")
plt.title("XGBoost: Actual vs Predicted")
plt.plot([y_test.min(), y_test.max()],
         [y_test.min(), y_test.max()],
         "--")

plt.savefig("xgboost_mass_prediction.png")
plt.show()

