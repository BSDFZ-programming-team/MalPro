import os
import numpy
from collections import *
import pandas as pd
import binascii
from rich.progress import track
import time

def getMatrixfrom_asm(filename, startindex = 0, pixnum = 5000):
    with open(filename, 'rb') as f:
        f.seek(startindex, 0)
        content = f.read(pixnum)
    hexst = binascii.hexlify(content)
    fh = numpy.array([int(hexst[i:i+2],16) for i in range(0, len(hexst), 2)])
    fh = numpy.uint8(fh)
    return fh


def train(stat):
    subtrain = pd.read_csv('subtrainLabels.csv')
    basepath = "./subtrain/"
    mapimg = defaultdict(list)
    i = 0
    stat.stop()
    for sid in track(subtrain.Id, description='Extracting .asm file features', total=len(subtrain.Id)):
        i += 1
        # print ("dealing with {0}th file...".format(str(i)))
        filename = basepath + sid + ".asm"
        im = getMatrixfrom_asm(filename, startindex = 0, pixnum = 1500)
        mapimg[sid] = im
    stat.start()
    stat.update('Saving the features to imgfeature.csv......')
    dataframelist = []
    for sid,imf in mapimg.items():
        standard = {}
        standard["Id"] = sid
        for index,value in enumerate(imf):
            colName = "pix{0}".format(str(index))
            standard[colName] = value
        dataframelist.append(standard)

    df = pd.DataFrame(dataframelist)
    df.to_csv("imgfeature.csv",index=False)
def process_ams_imagefeature(amsfile):
    # filename = randomid+amsfile
    filename = os.path.basename(amsfile)
    im = getMatrixfrom_asm(amsfile, startindex = 0, pixnum = 1500)
    standard = {}
    dataframelist = []
    standard["Id"] = filename
    for index,value in enumerate(im):
        colName = "pix{0}".format(str(index))
        standard[colName] = value
    dataframelist.append(standard)
    df = pd.DataFrame(dataframelist)
    df.to_csv("./upload/"+filename+"_"+"imgfeature.csv",index=False)
# process_ams_imagefeature('./train/0A32eTdBKayjCWhZqDOQ.asm')
# train()