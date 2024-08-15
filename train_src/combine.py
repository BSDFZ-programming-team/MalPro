from sklearn.ensemble import RandomForestClassifier as RF
from sklearn import model_selection
from sklearn.metrics import confusion_matrix
import os
import pandas as pd
import pickle
from sklearn.metrics import classification_report
def train():
    subtrainLabel = pd.read_csv('TrainLabels.csv')
    subtrainfeature1 = pd.read_csv("3gramfeature.csv")
    # subtrainfeature2 = pd.read_csv("../imgfeature.csv")
    # subtrain = pd.merge(subtrainfeature1,subtrainfeature2,on='Id')
    subtrain = pd.merge(subtrainfeature1,subtrainLabel,on='Id')
    labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values
    X_train, X_test, y_train, y_test = model_selection.train_test_split(subtrain,labels,test_size=0.1)
    srf = RF(n_estimators=500, n_jobs=-1)
    srf.fit(X_train,y_train)
    y_pred = srf.predict(X_test)
    print(classification_report(y_test, y_pred))
    # print(X_test)
    # print(y_test)
    with open('./model/model.pt', 'wb') as f:
        pickle.dump(srf,f)

    return srf.score(X_test,y_test)
def examine(srf_pickle_path='./model/model.pt'):
    with open(srf_pickle_path, 'rb') as f:
        srf=pickle.load(f)
    subtrainLabel = pd.read_csv('TrainLabels.csv')
    subtrainfeature1 = pd.read_csv("3gramfeature.csv")
    # subtrainfeature2 = pd.read_csv("../imgfeature.csv")
    # subtrain = pd.merge(subtrainfeature1,subtrainfeature2,on='Id')
    subtrain = pd.merge(subtrainfeature1,subtrainLabel,on='Id')
    labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values
    y_pred = srf.predict(subtrain)
    print(classification_report(labels, y_pred))
    return srf.score(subtrain, labels)
def loop_train(loops: int):
    subtrainLabel = pd.read_csv('TrainLabels.csv')
    subtrainfeature1 = pd.read_csv("3gramfeature.csv")
    # subtrainfeature2 = pd.read_csv("../imgfeature.csv")
    # subtrain = pd.merge(subtrainfeature1,subtrainfeature2,on='Id')
    subtrain = pd.merge(subtrainfeature1,subtrainLabel,on='Id')
    labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values
    X_train, X_test, y_train, y_test = model_selection.train_test_split(subtrain,labels,test_size=0.1)
    from rich.progress import track
    srfs = {}
    for i in track(range(loops)):
        srf = RF(n_estimators=137, n_jobs=-1)
        srf.fit(X_train,y_train)
        srfs[srf.score(X_test,y_test)] = srf
    max_ = 0
    for i in srfs:
        if i > max_:
            max_ = i
    print(max_)
    print(srfs)
    y_pred = srfs[max_].predict(X_test)
    print(classification_report(y_test, y_pred))
    with open('./model/model.pt', 'wb') as f:
        pickle.dump(srfs[max_],f)

    return srf.score(X_test,y_test)
# print(examine())
def random_forest_parameter_tuning1():
    subtrainLabel = pd.read_csv('../TrainLabels.csv')
    subtrainfeature1 = pd.read_csv("../3gramfeature.csv")
    # subtrainfeature2 = pd.read_csv("../imgfeature.csv")
    # subtrain = pd.merge(subtrainfeature1,subtrainfeature2,on='Id')
    subtrain = pd.merge(subtrainfeature1,subtrainLabel,on='Id')
    labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values
    from sklearn.model_selection import cross_val_score
    import matplotlib.pyplot as plt
    from tqdm import tqdm
    cross = []
    for i  in tqdm(range(135,145,1)):
        rf = RF(n_estimators=i+1, n_jobs=-1,random_state=42)
        cross_score = cross_val_score(rf, subtrain, labels, cv=5).mean()
        cross.append(cross_score)
    plt.plot(range(136,146,1),cross)
    plt.xlabel('n_estimators')
    plt.ylabel('acc')
    plt.show()
    print((cross.index(max(cross))*10)+1,max(cross))
def random_forest_parameter_tuning2():
    import numpy as np
    subtrainLabel = pd.read_csv('../TrainLabels.csv')
    subtrainfeature1 = pd.read_csv("../3gramfeature.csv")
    subtrainfeature2 = pd.read_csv("../imgfeature.csv")
    subtrain = pd.merge(subtrainfeature1,subtrainfeature2,on='Id')
    subtrain = pd.merge(subtrain,subtrainLabel,on='Id')
    labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values
    from sklearn.model_selection import GridSearchCV
    #调整max_depth
    param_grid = {'max_depth' : np.arange(1,20,1)}
    #一般根据数据大小进行尝试，像该数据集 可从1-10 或1-20开始
    rf = RF(n_estimators=137,random_state=42)
    GS = GridSearchCV(rf,param_grid,cv=5)
    GS.fit(subtrain,labels)
    print(GS.best_params_)  #最佳参数组合
    print(GS.best_score_)   #最佳得分
# random_forest_parameter_tuning2()
# random_forest_parameter_tuning()
def use(amsfile, tmpfile):
    filename = os.path.basename(amsfile)
    subtrainLabel = pd.read_csv(tmpfile)
    subtrainfeature1 = pd.read_csv(f"./upload/{filename}_3gramfeature.csv")
    # subtrainfeature2 = pd.read_csv("../imgfeature.csv")
    # subtrain = pd.merge(subtrainfeature1,subtrainfeature2,on='Id')
    subtrain = pd.merge(subtrainfeature1,subtrainLabel,on='Id')
    # labels = subtrain.Class
    subtrain.drop(["Class","Id"], axis=1, inplace=True)
    subtrain = subtrain.values
    with open('model/model.pt', 'rb') as f:
        srf=pickle.load(f)
    return srf.predict(subtrain)
    # with open('model/model_backup.pt', 'rb') as fb:
    #     srfb=pickle.load(fb)
    # try:
    #     return srf.predict(subtrain)
    # except Exception as e:
    #     print(e)
    #     try:
    #         subtrain = pd.merge(subtrainfeature1,subtrainLabel,on='Id')
    #         subtrain.drop(["Class","Id"], axis=1, inplace=True)
    #         subtrain = subtrain.values
    #         return srfb.predict(subtrain)
    #     except:
    #         return 0
# print(train())
# use()