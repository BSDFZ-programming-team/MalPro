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
            print (k,v)
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
    df.to_csv(f"./upload/{basename}_3gramfeature.csv",index=False)
# process_ams_imagefeature('./train/0AwWs42SUQ19mI7eDcTC.asm')