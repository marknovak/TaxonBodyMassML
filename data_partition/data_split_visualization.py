import pandas as pd
#from ydata_profiling import ProfileReport
import seaborn as sns
import numpy as np
from sklearn.preprocessing import PowerTransformer

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# apply z normalization to the mass_g variable in the data
def z_normalization(df):

    # remove rows with missing data
    print("Number of missing values in each column:\n", df.isna().sum())
    df = df.dropna(subset=["mass_g", "taxon"])

    # normalize mass data using z-normalization
    normalized_df = df.copy()
    normalized_df["normalized_mass"] = (df["mass_g"] - df["mass_g"].mean()) / df["mass_g"].std()
    print(normalized_df)

    return normalized_df


def main():
    # read bodymass data into a pandas dataframe
    df = pd.read_csv("./data/BodyMass.csv")

    # create a new variable which is the mass_g variable with z-normalization applied
    df = z_normalization(df)

    # ydata profiliing report is saved to my_report.html
    #profile = ProfileReport(df, title="Profiling Report")
    #profile.to_file("my_report.html")

    # create log1p visualization for the mass_g variable
    sns.histplot(np.log1p(df["mass_g"]), bins=50, kde=True)
    plt.title("Log-Transformed mass_g (log1p)")
    plt.ylabel("Count")
    plt.xlabel("Mass (g)")
    plt.show(block=True)

    # use yeo-johnson method to find a transformation that makes visualizing normalized mass variable readable
    pt = PowerTransformer(method="yeo-johnson")
    normalized_mass = df["normalized_mass"].to_numpy()
    transformed = pt.fit_transform(normalized_mass.reshape(-1, 1))
    sns.histplot(transformed, bins=50, kde=True)
    plt.title("Yeo-Johnson Transformed Mass Data")
    plt.ylabel("Count")
    plt.xlabel("Z-Normalized Mass")
    plt.show(block=True)

    # test data is a random sample of 10% of the database
    test = df.sample(frac=0.1, replace=False, random_state=123)

    # train data is the remaining 90%
    train = df.drop(test.index)

    print(test)
    print(train)

    # save the train/test split to independent csv files
    test.to_csv("./data/test.csv", index=False)
    train.to_csv("./data/train.csv", index=False)

if __name__ == "__main__":
    main()
