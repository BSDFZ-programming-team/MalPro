from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import fastapi_cdn_host
import os
import uvicorn
import json
import pefile
from hashlib import md5
from main import process_upload_asm, detect_virus, exe2asm
from shutil import rmtree
from random import randint
def Generate_tag(args_list:list):
    tag = ''
    for args in args_list:
        tag += args + '.'
    return tag[:-1]
def NumberOfBytesHumanRepresentation(value):
    if value <= 1024:
        return '%s bytes' % value
    elif value < 1024 * 1024:
        return '%.1f KB' % (float(value) / 1024.0)
    elif value < 1024 * 1024 * 1024:
        return '%.1f MB' % (float(value) / 1024.0 / 1024.0)
    else:
        return '%.1f GB' % (float(value) / 1024.0 / 1024.0 / 1024.0)
app = FastAPI()
fastapi_cdn_host.patch_docs(app, favicon_url='./static/logo.svg')
# 定义上传文件的目标目录
UPLOAD_DIR = "./upload"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 静态文件目录
app.mount("/static", StaticFiles(directory="./static"), name="static")
app.mount("/fonts", StaticFiles(directory="./fonts"), name="fonts")

# 根路由，返回上传页面
@app.get("/", response_class=HTMLResponse)
async def get_upload_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MalPro v0.1 BETA</title>
        <style>
            @font-face {
                font-family: 'good_font';
                src: url('/fonts/good_font.ttf') format('truetype');
            }
            body {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                font-family: 'good_font', Arial, sans-serif;
                background-image: url('/static/background.png'); /* 设置背景图片 */
                background-size: cover; /* 背景图片覆盖整个页面 */
                background-repeat: no-repeat; /* 背景图片不重复 */
                background-position: center; /* 背景图片居中显示 */
            }
            #logo {
                width: 300px;
                height: auto;png
                margin-top: 20px;
            }
            h1 {
                font-size: 24px;
                color: black; /* 文字颜色改为白色，以便在背景上更清晰 */
            }
            form {
                margin-top: 20px;
            }
            button {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
                border-radius: 4px;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #45a049;
            }
            button:active {
                background-color: #367b36;
            }
            .message {
                margin-top: 20px;
                font-size: 18px;
                color: black; /* 文字颜色改为白色 */
            }
        </style>
    </head>
    <body>
        <img id="logo" src="/static/logo.png" alt="Logo">
        <h1>MalPro v0.1 Beta</h1>
        <p>Upload your file here (only .exe & ≤8MB files allowed).</p>
        <form action="/uploadfile/" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".exe">
            <button type="submit">Upload File</button>
        </form>
        <div class="message" id="message"></div>
    </body>
    </html>
    """

@app.post("/uploadfile/", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    random_name = str(randint(100000, 999999))
    file_size = file.size
    if file_size > 8*1024*1024:
        result=[[f'FILE TOO LARGE ({NumberOfBytesHumanRepresentation(file_size)})', ''], 'red']
    else:
        fn = random_name+'.exe'
        save_path = f'./upload/'
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        save_file = os.path.join(save_path, fn)
        f = open(save_file, 'wb')
        f.write(data)
        f.close()
        del f
        data_md5 = md5(data).hexdigest() #TODO MD5 tmp list
        def judge_file():
            # RETURN: [[RESULT, PLATFORM], COLOR]
            f_md5_json = open('MD5_record_list.json', 'r+')
            try:
                md5dict = json.load(f_md5_json)
            except json.decoder.JSONDecodeError:
                md5dict = {}
            if data_md5 in md5dict:
                # print(1)
                return md5dict[data_md5]
            # Caculate some basic informations
            try:
                pe = pefile.PE(save_file)
                # assert hex(pe.FILE_HEADER.Characteristics) == "0x102" #EXE file
            except Exception as e:
                if type(e) == AssertionError:
                    result = 'UNAVALIABLE PE FILE (no 0x102 found in header)'
                else:
                    result = 'UNAVALIABLE PE FILE (failed to load)'
                color = 'red'
                platform = ''
                return [[result, platform], color]
            else:
            
                # Retrieve the Machine field from the PE header
                machine = pe.FILE_HEADER.Machine
                
                # Map the Machine value to human-readable platform
                if machine == 0x14C:
                    platform = "Intel 386 or later processors "
                elif machine == 0x8664:
                    platform = "x64 (AMD64)"
                elif machine == 0x1C0:
                    platform = "ARM"
                elif machine == 0xAA64:
                    platform = "ARM64"
                else:
                    platform = "Unknown machine type: 0x{machine:04X}"
                if detect_virus(save_file):
                    #TODO 把exe反编译成asm
                    asm_file = exe2asm(data)
                    result = process_upload_asm(asm_file)
                    color = 'red'
                else:
                    result = 'NON-VIRUS'
                    color = 'green'
            finally:
                try:
                    pe.close()
                except:
                    pass
                rmtree('./upload')
                md5dict[data_md5] = [[result, platform], color]
                f_md5_json.seek(0) 
                f_md5_json.truncate()
                f_md5_json.flush()
                json.dump(md5dict, f_md5_json)
                f_md5_json.close()
            return [[result, platform], color]
        result = judge_file()   
    color = result[-1]
    result = result[0]
    tag = Generate_tag(result) #TODO add more TAG
        
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MalPro v0.1 BETA</title>
            <style>
                @font-face {
                    font-family: 'good_font';
                    src: url('/fonts/good_font.ttf') format('truetype');
                }
                .green{
            color:green;
            font-size:20px;
        }
                .red{
            color:red;
            font-size:20px;
        }
                body {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    font-family: 'good_font', Arial, sans-serif;
                    background-image: url('/static/background.png'); /* 设置背景图片 */
                    background-size: cover; /* 背景图片覆盖整个页面 */
                    background-repeat: no-repeat; /* 背景图片不重复 */
                    background-position: center; /* 背景图片居中显示 */
                }
                #logo {
                    width: 300px;
                    height: auto;
                    margin-top: 20px;
                }
                h1 {
                    font-size: 24px;
                    color: black; /* 文字颜色改为白色 */
                }
                form {
                    margin-top: 20px;
                }
                button {
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                    border-radius: 4px;
                    font-size: 16px;
                    transition: background-color 0.3s;
                }
                button:hover {
                    background-color: #45a049;
                }
                button:active {
                    background-color: #367b36;
                }
                .message {
                    margin-top: 20px;
                    font-size: 18px;
                    color: white; /* 文字颜色改为白色 */
                }
            </style>
        </head>
        <body>
        <img id="logo" src="/static/logo.png" alt="Logo">
        <p>Size: '''+NumberOfBytesHumanRepresentation(file_size)+'''</p>
        <p>MD5: '''+data_md5+'''</p>
        <h1 class="'''+color+'''">predict type: '''+tag+'''</h1>
        </body>
        </html>
        '''

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)