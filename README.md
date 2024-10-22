<h1 align="center">MalPro🕵️ -- Malware classification by using assembly files!</h1>
<em><h3 align="center">Train your model & Classify malwares quickly, easily, accurately!</h3></em>
<p align="center">
<img src=https://img.shields.io/badge/python-3.7+-blue?style=for-the-badge>
<img src=https://img.shields.io/badge/License-Apache2-green?style=for-the-badge>
<img src=https://img.shields.io/badge/State-Developing-red?style=for-the-badge>
<img src=https://img.shields.io/badge/Platform-Windows-orange?style=for-the-badge>
<em><h5 align="center">malware classifier under python3 and machine learning</h5></em>
<img src=https://files.cnblogs.com/files/blogs/820580/logo.ico?t=1722150186&download=true>

ps: 1st project for Shang Hai Jiao Tong University AI application development competition

> 🚧 **Currently under developing** 🚧
>
> Malpro is currently in active development and not usable yet. For now, only 50 fixed malware families are supported.

# Background & Our Ideas

## What does our project do?

There are many products that use raw PE(.exe) file to classify malwares by using machine learning and/or extracting PE features. But instead, We are using assembly file of the raw PE file (generated by IDA) to classify it. 

Our project can classify **85** types of malware families now(for beta versions), and we will support 147 types in the future.

All families we supported is in malware_families_list.json

## Our ideas

### The background of our idea

When we are doing our research, we have noticed a bunch of project using cnn(or malconv, random forest, etc.) to classify the malware. 

Then, we saw a competition held by Microsoft (https://www.kaggle.com/competitions/malware-classification) that use .asm file to classify 9 different types of malware family. 

So could we classify more types of it? We have learned about the blogs, articles and interviews published by the champions of this competition. Finally, we decided that classifying by assembly file would be a good idea.

### Why assembly file?

Features in assembly file are easier to be learned by machines than raw PE file.

We try to prove this as rigorous as possible, but because of the lack of time and cpu(I'm dead serious), we could only say that when you got 6000s and one cpu, training random forest models by using assembly file is better than PE file.

If you are interested in it, see [blog](#blog).

### Advantage of assembly files

The powerful features in assembly files are: 

	* opgram-ncode features
	
We recommand n=3 or n=4 for the opgram-ncode features to train the random forest model.

*NOTE: You can customise the 'n' in opcode-ngram features when training models in main.py*  

# Dataset

*Testing machine: ultra7 32GB cpu*

## For primary model (9 malware families)

Dataset: [kaggle](https://www.kaggle.com/competitions/malware-classification)

### Performance

**n=3**

dataset size: 2480 malwares (train:test=9:1)  
malware families: 9 types  
accuracy: 0.9959677419354839  
time spent in extracting features: 36s(.asm image features) + 8min34s(opcode-3gram features)  
time spent in training: less than 10s  

## For advanced model (50 malware families) 

Dataset: [Vx underground dataset](https://vx-underground.org/Samples/Families) (42 malware families)

and Dataset from [kaggle](https://www.kaggle.com/competitions/malware-classification) (8 malware families)

### Performance

**check the accuracy in ./model/model_accu.txt and ./model/n=3/model_accu.txt in 50-malware-branch**  

**n=4**

dataset size: 6921 malwares (train:test=9:1)  
malware families: 50 types  
accuracy: 0.9415692821368948   

**n=3**

dataset size: 6921 malwares (train:test=9:1)  
malware families: 50 types  
accuracy: 0.9415692821368948   
time spent in training: 12s

## For super advanced model (85 malware families) 

**check the accuracy in ./model/model_accu.txt in 85-malware-branch**  

Dataset: [Vx underground dataset](https://vx-underground.org/Samples/Families) (42 malware families)

and Dataset from [kaggle](https://www.kaggle.com/competitions/malware-classification) (8 malware families)

and Dataset from [BODMAS](https://github.com/whyisyoung/BODMAS)(35 malware families)  

### Performance

**n=4**

dataset size: 9352 malwares (train:test=9:1)  
malware families: 85 types  
accuracy: 0.8728632478632479   

**n=3**

dataset size: 9352 malwares (train:test=9:1)  
malware families: 85 types  
accuracy: 0.8824786324786325 

# Project usage

there is a model trained by us in the project file (model/model.pt), so you can predict the malware without training on your own

## requirments

### install python libraries

```
pip install -r requirments.txt
```

*TIPS: we recommend you to create a new python 3.9 virtual environment for this project because it depends on some libraries in old version*

### install IDA pro

install IDA pro (7.x) from [here](https://hex-rays.com/IDA-pro/)

**Change {ida_install_dir}/idc/analysis.idc**

![image](https://files.cnblogs.com/files/blogs/820580/image.ico?t=1723102253&download=true)

line41: 

from
```
gen_file(OFILE_ASM, fhandle, 0, BADADDR, 0); // create the assembler file  
```
to
```
gen_file(OFILE_LST, fhandle, 0, BADADDR, 0); // create the assembler file  
```

**Change {ida_install_dir}/cfg/ida.cfg**

![image](https://files.cnblogs.com/files/blogs/820580/example4.ico?t=1723102635&download=true)

line 399:

from
```
OPCODE_BYTES            = 0   // display this many instruction/data bytes (0 to disable)
```
to
```
OPCODE_BYTES            = 16   // display this many instruction/data bytes (0 to disable)
```


## Examples(Quick Use)

```
python main.py
```

we upload one malware sample for each kind of the malware families(50 types). You can use main.py to examine the model. 

There are two models using n=4(deafult) and n=3 are uploaded.  

*The two model files is over 100MB(too large to upload) so we upload .zip file of it, don't forget to unzip*  

*But in the release vesion, the models are not in zip files*  

Change the model file to n=3 if you want.

choose "Predict malware(.asm) directly(using ./model/model.pt)" in the menu and enter the location of one of the examples(or you can download raw PE files of those 9 types of malwares and use IDA to generate assembly files as your own samples), then you will get a predict result.

## Examine

### predict

```
python server.py
```

It will run a web server on your host(port 7777) as the frontend of our project, open it and upload your PE file, you will see a result like this.

**ONLY SUPPORT 85 TYPES OF MALWARE FAMILIES**  

![image](https://files.cnblogs.com/files/blogs/820580/example.ico?t=1723649092&download=true)

download the analyze details if you want. 

### train

**download .asm dataset with labels**

You can download the dataset of [kaggle](https://www.kaggle.com/competitions/malware-classification) which contains 9 types of malware famlies.  

Or you can download other PE malware dataset and turn them to LST file in IDA and label them.


**create /train folder and TrainLabels.csv**

copy your data set to /train and your label file to TrainLabels.csv(same label file format in the kaggle challenge)

*TIPS: if your train set is a subset of your label file(rename it to trainLabels_all.csv), use utils/convert.py to fix it.*

**Run main.py to train the model**

`python main.py`

it will show a menu like this  

![image](https://files.cnblogs.com/files/blogs/820580/example2.ico?t=1723186123&download=true)

you can train your model in this script

# Contributors

### Project by:  

WeiLin Du([LamentXU](https://www.cnblogs.com/LAMENTXU))  
YiFan He([0D00-O721](https://github.com/0D00-O721))  
QiXun Zhong([ZQX-art](https://github.com/ZQX-art))  

### Guided by:  

XiaoBin Peng([handsongPeng](https://github.com/handsongPeng))  

# Reports
Please send bug reports and feature requests through github issue tracker. Malpro is currently under development now and it's open to any constructive suggestions.

# License
The Malpro project is released under apache2 license.

# Blog

https://www.cnblogs.com/LAMENTXU/articles/18306874
