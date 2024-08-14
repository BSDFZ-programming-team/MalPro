# -*- coding:utf-8 -*-
# @FileName  :MAIN.PY
# @Time      :2024/07/17 10:00:31
# @Author    :LamentXU
import train_src.combine as combine
from shutil import rmtree
from random import randint
from pandas import read_csv
import train_src.asm_image_model as asm_image_model
from os import mkdir, system
from os.path import exists, basename, isdir
import warnings
warnings.filterwarnings("ignore")
import utils.asmimage as asmimage
import utils.opcodeandngram as opcodeandngram
from rich.console import Console
from json import load
with open('./malware_families_list.json', 'r') as f:
    resultdict = load(f)
VERSION = 'V0.1 BETA'
def process_upload_asm(asm_file_name):
    filebasename = basename(asm_file_name)
    asmimage.process_ams_imagefeature(asm_file_name)
    tmpfile = opcodeandngram.process_ams_imagefeature(asm_file_name)
    opcodeandngram.fit_feature_to_model(tmpfile, filebasename)
    with open(f'./upload/{filebasename}_tmp.csv', 'w') as f:
        f.write('Id,Class\n')
        f.write(f'{filebasename},0')
    result = combine.use(asm_file_name, f'./upload/{filebasename}_tmp.csv')[0]
    if result == 0:
        return 'Unknown .asm file'
    else:
        return resultdict[str(result)]
def getfeaturenum():
    df_first_row = read_csv('./model/3gramfeature_fitting_use.csv', nrows=1, header=None)
    first_row = df_first_row.values.tolist()[0]
    first_row.pop(0)
    return len(first_row)
def detect_virus(exe_file_path):
    # 文件黑白判断接口
    #TODO
    return True #True -> 文件为病毒；False -> 文件不为病毒
def exe2asm(exe_file_path, ida_PATH):
    filename = basename(exe_file_path)
    system(f'{ida_PATH}ida64 -TPortable -Sanalysis.idc "{exe_file_path}"')
    asm_path = './upload/'+filename+'.asm'
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
[Author] BSDFZ-programming-team
[/cyan]
'''
if __name__ == '__main__':
    try:
        console = Console() 
        console.print(BANNER)
        while True:
            console.print('''
        [cyan]menu:
            [1] Extract features & Train a model
            [2] Predict malware(.asm) directly(using ./model/model.pt)
            [3] Train a model directly(with features already extracted)
            [99] Exit[/cyan]
        ''')
            choice = input(': >>> ')
            if choice == '2':
                if not exists('./upload'):
                    mkdir('./upload')
                console.log(f'[*] Loading models at ./model/model.pt')
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
                stat = console.status('Extracting ams image features......')
                stat.start()
                asmimage.train(stat)
                stat.update('Extracting Opcode 3-gram features......')
                opcodeandngram.train(stat)
                # stat.update('Training the model based on asm image features......')
                # accu = asm_image_model.train()
                # console.log(f'[+] Training DONE, Accuracy: {accu}')
                stat.update('Training the model based on opcode 3-gram features......')
                accu = combine.train()
                console.log(f'[+] Training DONE, Accuracy: {accu}')
                # copyfile('3gramfeature.csv', './model/3gramfeature_fitting_use.csv')
                with open('3gramfeature.csv', 'r') as rf:
                    opcodes = rf.readline()
                with open('./model/3gramfeature_fitting_use.csv', 'w+') as f:
                    f.write(opcodes)
                stat.stop()
                console.log('Training DONE, model saved at ./model.pt')
            elif choice == '3':
                stat = console.status('Checking features files......')
                stat.start()
                if not exists('3gramfeature.csv') or not exists('imgfeature.csv'):
                    stat.stop()
                    console.log('[-] Feature file not found. Please extract your features first.')
                else:
                    console.log('[*] Feature file found: 3gramfeature.csv & imgfeature.csv')
                stat.update('Training the model based on opcode 3-gram features......')
                accu = combine.train()
                console.log(f'[+] Training DONE, Accuracy: {accu}')
                with open('3gramfeature.csv', 'r') as rf:
                    opcodes = rf.readline()
                with open('./model/3gramfeature_fitting_use.csv', 'w+') as f:
                    f.write(opcodes)
                stat.stop()
                console.log('Training DONE, model saved at ./model.pt')
            elif choice == '99':
                break
            else:
                console.log(f'[-] Unknown command {choice}')
    except Exception as e:
        # import traceback
        # print(traceback.print_exc())
        console.print_exception()
