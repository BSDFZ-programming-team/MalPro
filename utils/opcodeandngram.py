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


def getOpcodeNgram(ops, n):
    opngramlist = [tuple(ops[i:i+n]) for i in range(len(ops)-n)]
    opngram = Counter(opngramlist)
    return opngram
def train(stat, n):
    basepath = "./train/"
    mapngram = defaultdict(Counter)
    subtrain = pd.read_csv('TrainLabels.csv')
    count = 1
    stat.stop()
    for sid in track(subtrain.Id, description=f'Extracting Opcode {n}-gram feature', total=len(subtrain.Id)):
        count += 1
        filename = basepath + sid + ".asm"
        ops = getOpcodeSequence(filename)
        opngram = getOpcodeNgram(ops, n)
        mapngram[sid] = opngram
    stat.start()
    stat.update('Saving the features to ngramfeature.csv......')
    cc = Counter([])
    for d in mapngram.values():
        cc += d
    selectedfeatures = {}
    tc = 0
    for k,v in cc.items():
        if v >= 500:
            selectedfeatures[k] = v
            # print (k,v)
            tc += 1
    dataframelist = []
    for fid,opngram in mapngram.items():
        standard = {}
        standard["Id"] = fid
        for feature in selectedfeatures:
            if feature in opngram:
                standard[feature] = opngram[feature]
            else:
                standard[feature] = 0
        dataframelist.append(standard)
    df = pd.DataFrame(dataframelist)
    df.to_csv("ngramfeature.csv",index=False)
def process_ams_imagefeature(asmfile, n):
    mapngram = defaultdict(Counter)
    basename = os.path.basename(asmfile)
    ops = getOpcodeSequence(asmfile)
    opngram = getOpcodeNgram(ops, n)
    mapngram[basename] = opngram

    cc = Counter([])
    for d in mapngram.values():
        cc += d
    selectedfeatures = {}
    tc = 0
    for k,v in cc.items():
        # if v >= 500:
        selectedfeatures[k] = v
        # print (k,v)
        tc += 1
    dataframelist = []
    for fid,opngram in mapngram.items():
        standard = {}
        standard["Id"] = fid
        for feature in selectedfeatures:
            if feature in opngram:
                standard[feature] = opngram[feature]
            else:
                standard[feature] = 0
        dataframelist.append(standard)
    df = pd.DataFrame(dataframelist)
    df.to_csv(f"./upload/{basename}_ngramfeature_tmp.csv",index=False)
    return f"./upload/{basename}_ngramfeature_tmp.csv"
def fit_feature_to_model(tmp_csv, basename):
    df_first_row = pd.read_csv('./model/ngramfeature_fitting_use.csv', nrows=1, header=None)
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
    with open('./upload/'+basename+'_ngramfeature.csv', 'w+') as f:
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
# fit_feature_to_model("./upload/5Wj7vbRmSAoHI2Dfsql3.asm_ngramfeature_tmp.csv", '0AwWs42SUQ19mI7eDcTC.asm')