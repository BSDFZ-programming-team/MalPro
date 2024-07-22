from sklearn.ensemble import RandomForestClassifier as RF
from sklearn import model_selection
from sklearn.metrics import confusion_matrix
import os
import pandas as pd
import pickle

def train():
    subtrainLabel = pd.read_csv('subtrainLabels.csv')
    subtrainfeature1 = pd.read_csv("3gramfeature.csv")
    subtrainfeature2 = pd.read_csv("imgfeature.csv")
    subtrain = pd.merge(subtrainfeature1,subtrainfeature2,on='Id')
    subtrain = pd.merge(subtrain,subtrainLabel,on='Id')
    labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values

    X_train, X_test, y_train, y_test = model_selection.train_test_split(subtrain,labels,test_size=0.4)

    srf = RF(n_estimators=500, n_jobs=-1)
    srf.fit(X_train,y_train)
    # print(X_test)
    # print(y_test)
    with open('model.pt', 'wb') as f:
        pickle.dump(srf,f)

    # from sklearn.metrics import classification_report,roc_auc_score,roc_curve
    # from sklearn.metrics import average_precision_score,precision_recall_curve
    
    # result = classification_report(y_test, srf.predict(X_test))
    # rfc_prob = srf.predict_proba(X_test)[:,1]
    # #输出AUC的值
    # auc_score = roc_auc_score(y_true=y_test,y_score=rfc_prob)
    # #输出AP值
    # ap_score = average_precision_score(y_true=y_test,y_score=rfc_prob)
    # #画出PR曲线
    # precision_recall_curve(estimator=srf,X=X_test,y=y_test,pos_label=1)


    return srf.score(X_test,y_test)
def use(amsfile, tmpfile):
    filename = os.path.basename(amsfile)
    subtrainLabel = pd.read_csv(tmpfile)
    subtrainfeature1 = pd.read_csv(f"./upload/{filename}_imgfeature.csv")
    subtrainfeature2 = pd.read_csv(f"./upload/{filename}_3gramfeature.csv")
    subtrain = pd.merge(subtrainfeature1,subtrainfeature2,on='Id')
    subtrain = pd.merge(subtrain,subtrainLabel,on='Id')
    labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values
    with open('model.pt', 'rb') as f:
        srf=pickle.load(f)
    with open('model_backup.pt', 'rb') as fb:
        srfb=pickle.load(fb)
    try:
        return srf.predict(subtrain)
    except:
        try:
            subtrain = pd.merge(subtrainfeature1,subtrainLabel,on='Id')
            subtrain.drop(["Class","Id"], axis=1, inplace=True)
            subtrain = subtrain.values
            return srfb.predict(subtrain)
        except:
            return 0
# print(train())
# use()