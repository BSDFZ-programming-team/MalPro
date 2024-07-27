# -*- coding:utf-8 -*-
# @FileName  :MAIN.PY
# @Time      :2024/07/17 10:00:31
# @Author    :LamentXU
import train_src.combine as combine
from shutil import rmtree
from random import randint
import train_src.firstrandomforest as firstrandomforest
from os import mkdir
from os.path import exists, basename
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import utils.asmimage as asmimage
import utils.randomsubset as randomsubset
import utils.opcodeandngram as opcodeandngram
from rich.console import Console
from shutil import copyfile
VERSION = 'V0.1 BETA'
IDA_PATH = input('your IDA path: >>> ')
resultlist=['Ramnit', 'Lollipop', 'Kelihos_ver3', 'Vundo', 'Simda','Tracur','Kelihos_ver1','Obfuscator.ACY','Gatak']
def process_upload_asm(asm_file_name):
    filebasename = basename(asm_file_name)
    asmimage.process_ams_imagefeature(asm_file_name)
    tmpfile = opcodeandngram.process_ams_imagefeature(asm_file_name)
    copyfile('3gramfeature.csv', './model/3gramfeature_fitting_use.csv')
    opcodeandngram.fit_feature_to_model(tmpfile, filebasename)
    with open(f'./upload/{filebasename}_tmp.csv', 'w') as f:
        f.write('Id,Class\n')
        f.write(f'{filebasename},0')
    result = combine.use(asm_file_name, f'./upload/{filebasename}_tmp.csv')
    if result == 0:
        return 'Unknown .asm file'
    else:
        return resultlist[int(result)-1]
def detect_virus(exe_file_path):
    # 文件黑白判断接口
    # TODO
    return False #True -> 文件为病毒；False -> 文件不为病毒
def exe2asm(exe_file_path):
    # TODO
    # exe反编译接口
    filename = basename(exe_file_path)
    # 反编译
    asm_path = filename.split('.')[0]+'.asm'
    return asm_path
TRAIN_DIR = './train'
TEST_DIR = './test'
BANNER = f'''
[blue bold]
 _  _   __   __    ____  ____   __     ____  _  _ 
( \/ ) / _\ (  )  (  _ \(  _ \ /  \   (  _ \( \/ ) 
/ \/ \/    \/ (_/\ ) __/ )   /(  0 )_  ) __/ )  /  
\_)(_/\_/\_/\____/(__)  (__\_) \__/(_)(__)  (__/  
[/blue bold][cyan]
[Version] {VERSION}
[Author] 北京师范大学南山附属学校小组

注：本项目为上海交通大学AI夏令营比赛项目，代码为项目小组成员编写，遵循Apache2协议！
[/cyan]
'''
if __name__ == '__main__':
    try:
        console = Console() 
        console.print(BANNER)
        while True:
            console.print('''
        [cyan]menu:
            [1] Train a model
            [2] Predict malware(.asm) directly(using ./model/model.pt)
            [99] Exit[/cyan]
        ''')
            choice = input(': >>> ')
            if choice == '2':
                if not exists('./upload'):
                    mkdir('./upload')
                console.log(f'[*] Loading models at ./model/model.pt and ./model/model_backup.pt')
                file_location = input("input the .asm file location : >>> ")
                if not exists(file_location):
                    console.log('[bold red][-] File not found[/bold red]')
                    continue
                stat = console.status('Analyzing...')
                stat.start()
                result = process_upload_asm(file_location)
                stat.stop()
                console.bell()
                if result == 'Unknown .asm file':
                    console.log('[bold red][-] Failed, unknown .asm file[/bold red]')
                console.log(f'[+] Predict DONE. the malware type is [red bold]{result}[/red bold]')
                rmtree('./upload')
                console.log(f'[*] Deleted tmp file at /upload')
            elif choice == '1':
                console.log('[*] Using training file at ./train and ./subtrain')
                console.log('[*] Using label file at ./TrainLabels.csv')
                stat = console.status('Spliting subsets randomly......')
                stat.start()
                randomsubset.main()
                stat.update('Extracting ams image features......')
                asmimage.train(stat)
                stat.update('Extracting Opcode 3-gram features......')
                opcodeandngram.train(stat)
                stat.update('Training the model based on asm image features......')
                accu = firstrandomforest.train()
                console.log(f'[+] Training DONE, Accuracy: {accu}')
                stat.update('Training the model based on combining asm image features and opcode 3-gram features......')
                accu = combine.train()
                console.log(f'[+] Training DONE, Accuracy: {accu}')
                stat.stop()
                console.log('Training DONE, model saved at ./model.pt')
            elif choice == '99':
                break
            else:
                console.log(f'[-] Unknown command {choice}')
    except:
        console.print_exception()