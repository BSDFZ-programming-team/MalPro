import re
from collections import *
import os
import pandas as pd
from rich.progress import track
def getOpcodeSequence(filename):
    opcode_seq = []
    p = re.compile(r'\s([a-fA-F0-9]{2}\s)+\s*([a-z]+)')
    with open(filename, errors='ignore') as f:
        for line in f:
            if line.startswith(".text"):
                m = re.findall(p,line)
                if m:
                    opc = m[0][1]
                    if opc != "align":
                        opcode_seq.append(opc)
    return opcode_seq

def train_opcode_lm(ops, order=4):
    lm = defaultdict(Counter)
    prefix = ["~"] * order
    prefix.extend(ops)
    data = prefix
    for i in range(len(data)-order):
        history, char = tuple(data[i:i+order]), data[i+order]
        lm[history][char]+=1
    def normalize(counter):
        s = float(sum(counter.values()))
        return [(c,cnt/s) for c,cnt in counter.iteritems()]
    outlm = {hist:chars for hist, chars in lm.iteritems()}
    return outlm

def getOpcodeNgram(ops, n=3):
    opngramlist = [tuple(ops[i:i+n]) for i in range(len(ops)-n)]
    opngram = Counter(opngramlist)
    return opngram
def train(stat):
    basepath = "./subtrain/"
    map3gram = defaultdict(Counter)
    subtrain = pd.read_csv('subtrainLabels.csv')
    count = 1
    stat.stop()
    for sid in track(subtrain.Id, description='Extracting Opcode 3-gram feature', total=len(subtrain.Id)):
        # print ("counting the 3-gram of the {0} file...".format(str(count)))
        count += 1
        filename = basepath + sid + ".asm"
        ops = getOpcodeSequence(filename)
        op3gram = getOpcodeNgram(ops)
        map3gram[sid] = op3gram
    stat.start()
    stat.update('Saving the features to 3gramfeature.csv......')
    cc = Counter([])
    for d in map3gram.values():
        cc += d
    selectedfeatures = {}
    tc = 0
    for k,v in cc.items():
        if v >= 500:
            selectedfeatures[k] = v
            # print (k,v)
            tc += 1
    dataframelist = []
    for fid,op3gram in map3gram.items():
        standard = {}
        standard["Id"] = fid
        for feature in selectedfeatures:
            if feature in op3gram:
                standard[feature] = op3gram[feature]
            else:
                standard[feature] = 0
        dataframelist.append(standard)
    df = pd.DataFrame(dataframelist)
    df.to_csv("3gramfeature.csv",index=False)
def process_ams_imagefeature(asmfile):
    map3gram = defaultdict(Counter)
    basename = os.path.basename(asmfile)
    ops = getOpcodeSequence(asmfile)
    op3gram = getOpcodeNgram(ops)
    map3gram[basename] = op3gram

    cc = Counter([])
    for d in map3gram.values():
        cc += d
    selectedfeatures = {}
    tc = 0
    for k,v in cc.items():
        # if v >= 500:
        selectedfeatures[k] = v
        # print (k,v)
        tc += 1
    dataframelist = []
    for fid,op3gram in map3gram.items():
        standard = {}
        standard["Id"] = fid
        for feature in selectedfeatures:
            if feature in op3gram:
                standard[feature] = op3gram[feature]
            else:
                standard[feature] = 0
        dataframelist.append(standard)
    df = pd.DataFrame(dataframelist)
    df.to_csv(f"./upload/{basename}_3gramfeature_tmp.csv",index=False)
    return f"./upload/{basename}_3gramfeature_tmp.csv"
def fit_feature_to_model(tmp_csv, basename):
    df_first_row = pd.read_csv('./model/3gramfeature_fitting_use.csv', nrows=1, header=None)
    first_row = df_first_row.values.tolist()[0]
    first_row.pop(0)
    _tmp_first_row = pd.read_csv(tmp_csv, nrows=2, header=None)
    tmp_first_row = _tmp_first_row.values.tolist()[0]
    tmp_second_row = _tmp_first_row.values.tolist()[1]
    tmp_first_row.pop(0)
    tmp_second_row.pop(0)
    data = {}
    for i in first_row:
        if i in tmp_first_row:
            index = tmp_first_row.index(i)
            value = tmp_second_row[index]
        else:
            value = '0'
        data[i] = value
    # df = pd.DataFrame(data)
    with open('./upload/'+basename+'_3gramfeature.csv', 'w+') as f:
        buf = 'Id,'
        for keys in data.keys():
            buf += '"'+keys+'",'
        buf = buf[:-1]
        buf += ('\n'+basename+',')
        for vals in data.values():
            buf += vals+','
        buf = buf[:-1]
        f.write(buf)
# process_ams_imagefeature('./train/5Wj7vbRmSAoHI2Dfsql3.asm')
# fit_feature_to_model("./upload/5Wj7vbRmSAoHI2Dfsql3.asm_3gramfeature_tmp.csv", '0AwWs42SUQ19mI7eDcTC.asm')