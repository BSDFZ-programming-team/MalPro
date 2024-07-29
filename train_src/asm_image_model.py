from sklearn.ensemble import RandomForestClassifier as RF
from sklearn import model_selection
from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np
import pickle
def train():
    subtrainLabel = pd.read_csv('TrainLabels.csv')
    subtrainfeature = pd.read_csv("imgfeature.csv")
    subtrain = pd.merge(subtrainLabel,subtrainfeature,on='Id')
    labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values 
    X_train, X_test, y_train, y_test = model_selection.train_test_split(subtrain,labels,test_size=0.4)

    srf = RF(n_estimators=500, n_jobs=-1)
    srf.fit(X_train,y_train)
    with open('./model/model_backup.pt', 'wb') as f:
        pickle.dump(srf,f)
    return srf.score(X_test,y_test)
# def predict(amsfile):

