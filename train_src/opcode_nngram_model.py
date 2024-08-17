from sklearn.ensemble import RandomForestClassifier as RF
from sklearn import model_selection
from sklearn.metrics import confusion_matrix
import pandas as pd
import pickle
from os import path
def train():
    subtrainLabel = pd.read_csv('TrainLabels.csv')
    subtrainfeature = pd.read_csv("ngramfeature.csv")
    subtrain = pd.merge(subtrainLabel,subtrainfeature,on='Id')
    labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values

    X_train, X_test, y_train, y_test = model_selection.train_test_split(subtrain,labels,test_size=0.1)

    srf = RF(n_estimators=500, n_jobs=-1)
    srf.fit(X_train,y_train)
    with open('./model/model.pt', 'wb') as f:
        pickle.dump(srf,f)
    srf.score(X_test,y_test)
# y_pred = srf.predict(X_test)
# print confusion_matrix(y_test, y_pred)
def use(amsfile, tmpfile):
    filename = path.basename(amsfile)
    subtrainLabel = pd.read_csv(tmpfile)
    subtrain = pd.read_csv(f"./upload/{filename}_ngramfeature.csv")
    subtrain = pd.merge(subtrain,subtrainLabel,on='Id')
    # labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values
    with open('model/model.pt', 'rb') as f:
        srf=pickle.load(f)
    return srf.predict(subtrain)