import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("./data/BodyMass.csv")
df = df[df["mass_g"] < 1000]
print(df)
plt.hist(df["mass_g"], bins=30)
plt.show()