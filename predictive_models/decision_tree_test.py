# -*- coding: utf-8 -*-
"""
Created on Sun Nov 23 16:38:44 2025

@author: IonCa
"""

from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#from sklearn.metrics import ConfusionMatrixDisplay

#import training and testing data
train = pd.read_csv("./data/train.csv")
test = pd.read_csv("./data/test.csv")

print("The Training Data is\n", train)
print("The Testing Data is\n", test)

#needs to remove other data when full taxonomy is created
# keep and remove labels from training and test data
train_mass = train["mass_g"]
train = train.drop(["mass_g"], axis=1)

test_mass = ["mass_g"]
test = test.drop(["mass_g"], axis=1)


decision_tree = DecisionTreeClassifier()
decision_tree = decision_tree.fit(train, train_mass)


##Tree Plot Option 1
MyPlot=tree.plot_tree(decision_tree,
                   feature_names=train.columns, 
                   class_names=decision_tree.classes_,
                   filled=True)

plt.savefig("mass_tree.jpg")
plt.close()

## Predict the Testing Dataset
test_prediction=decision_tree.predict(test_mass)
print(test_prediction)

