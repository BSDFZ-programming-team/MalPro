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
VERSION = 'V0.1 BETA'
resultlist=['Ramnit', 'Lollipop', 'Kelihos_ver3', 'Vundo', 'Simda','Tracur','Kelihos_ver1','Obfuscator.ACY','Gatak']
def process_upload_asm(asm_file_name):
    filebasename = basename(asm_file_name)
    asmimage.process_ams_imagefeature(asm_file_name)
    tmpfile = opcodeandngram.process_ams_imagefeature(asm_file_name)
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
                stat = console.status('Analyzing...')
                stat.start()
                result = process_upload_asm(file_location)
                stat.stop()
                console.bell()
                if result == 'Unknown .asm file':
                    console.log('[-] Failed, unknown .asm file')
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
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from starlette.status import HTTP_201_CREATED
# import os

# app = FastAPI()

# # 定义上传文件的目标目录
# UPLOAD_DIR = "./upload"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# # 静态文件目录
# app.mount("/static", StaticFiles(directory="./static"), name="static")
# app.mount("/fonts", StaticFiles(directory="./fonts"), name="fonts")

# # 根路由，返回上传页面
# @app.get("/", response_class=HTMLResponse)
# async def get_upload_page():
#     return """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta http-equiv="X-UA-Compatible" content="IE=edge">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>File Upload Demo</title>
#     <style>
#         @font-face {
#             font-family: 'good_font'; /* 定义自定义字体名称 */
#             src: url('/fonts/good_font.ttf') format('truetype'); /* 引用字体文件路径 */
#             /* 添加其他格式，例如woff2或woff，以提供跨浏览器支持 */
#         }
#         body {
#             display: flex;
#             flex-direction: column;
#             align-items: center;
#             justify-content: center;
#             height: 100vh; /* 让页面占据整个视窗高度 */
#             margin: 0;
#             font-family: 'YourCustomFont', Arial, sans-serif; /* 应用自定义字体 */
#         }
#         #logo {
#             width: 300px; /* 调整logo的宽度 */
#             height: auto; /* 让高度根据宽度自适应 */
#             margin-top: 20px; /* 顶部间距 */
#         }
#         h1 {
#             font-size: 24px; /* 标题字体大小 */
#             font-family: 'good_font', Arial, sans-serif;
#         }
#         form {
#             margin-top: 20px; /* 顶部间距 */
#         }
#         /* 按钮样式 */
#         button {
#             padding: 10px 20px; /* 按钮内边距 */
#             background-color: #4CAF50; /* 按钮背景色 */
#             color: white; /* 按钮文本颜色 */
#             border: none; /* 去除边框 */
#             cursor: pointer; /* 鼠标悬停时显示手型 */
#             border-radius: 4px; /* 圆角边框 */
#             font-size: 16px; /* 字体大小 */
#             transition: background-color 0.3s; /* 鼠标悬停过渡效果 */
#         }
#         button:hover {
#             background-color: #45a049; /* 悬停时的背景色 */
#         }
#         button:active {
#             background-color: #367b36; /* 按下时的背景色 */
#         }
#     </style>
# </head>
# <body>
#     <img id="logo" src="/static/logo.png" alt="Logo">
#     <h1>File Upload Demo</h1>
#     <form action="/uploadfile/" method="post" enctype="multipart/form-data">
#         <input type="file" name="file">
#         <button type="submit">Upload File</button>
#     </form>
# </body>
# </html>

#     """

# # 文件上传的API端点
# @app.post("/uploadfile/")
# async def upload_file(file: UploadFile = File(...)):
#     try:
#         randomid = str(randint(1000000, 9999999))
#         # 将文件保存到指定目录
#         file_location = os.path.join(UPLOAD_DIR, randomid+'asm')
#         with open(file_location, "wb") as buffer:
#             buffer.write(file.file.read())
#         result = process_upload_asm(file_location)
#         return {"result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")

# # 使用uvicorn运行FastAPI应用
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)

    