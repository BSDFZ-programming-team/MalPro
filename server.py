from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse,FileResponse, Response
from fastapi.staticfiles import StaticFiles
# import fastapi_cdn_host
from io import StringIO
import sys
import os
import uvicorn
import zipfile
import json
import utils.PE_analyse
from hashlib import md5
from main import process_upload_asm, detect_virus, exe2asm
from shutil import rmtree
from random import randint

def Generate_tag(args_list:list):
    tag = ''
    for args in args_list:
        tag += args + '.'
    while True:
        if tag.endswith('.'):
            tag = tag[:-1]
        else:
            return tag
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
# fastapi_cdn_host.patch_docs(app, favicon_url='./static/logo.svg')
# 定义上传文件的目标目录
os.makedirs("./upload", exist_ok=True)
os.makedirs("./download", exist_ok=True)
# 静态文件目录
app.mount("/static", StaticFiles(directory="./static"), name="static")
# app.mount("/download", StaticFiles(directory="./download"), name="download")
app.mount("/fonts", StaticFiles(directory="./fonts"), name="fonts")
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('./static/favicon.ico')
@app.get("/downloadfile")
async def download(file_name:str):
    # 需要下载文件名，从服务器保存文件地址拼接
    file_path = "./download/"+file_name
    return FileResponse(file_path, filename='analyze detail.zip', media_type="application/octet-stream")
# 根路由，返回上传页面
@app.get("/", response_class=HTMLResponse)
async def get_upload_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link id="favicon" rel="icon" type="image/x-icon" href="static/favicon.ico">
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
        <p>Upload your file here (only PE & ≤8MB files allowed).</p>
        <form action="/uploadfile/" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
        
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
    is_same = False
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
        def judge_file(random_name):
            # RETURN: [[[RESULT, PLATFORM], COLOR], RANDOM_NAME]
            f_md5_json = open('MD5_record_list.json', 'r+')
            try:
                md5dict = json.load(f_md5_json)
            except json.decoder.JSONDecodeError:
                md5dict = {}
            if data_md5 in md5dict:
                # print(1)
                return md5dict[data_md5]
            # Caculate some basic informations
            analyze_result = utils.PE_analyse.check_avaliable(save_file)
            if analyze_result == 'Load failed':
                return [[['UNAVALIABLE PE FILE (failed to load)', ''], 'red'], random_name]
            elif analyze_result == 'Header broken':
                return [[['UNAVALIABLE PE FILE (header broken)', ''], 'red'], random_name]
            else:
                pe = analyze_result
                buffer = StringIO()
                sys.stdout = buffer
                print(pe)
                with open(f'./upload/{random_name}_exe_details.txt', 'w+') as f:
                    f.write(buffer.getvalue())
                sys.stdout = sys.__stdout__
                del f
                platform = utils.PE_analyse.analyze_machine(pe)
                pe.close()
                if detect_virus(save_file):
                    #TODO 把exe反编译成asm
                    asm_file = exe2asm(data)
                    result = process_upload_asm(asm_file)
                    color = 'red'
                else:
                    result = 'NON-VIRUS'
                    color = 'green'
                md5dict[data_md5] = [[[result, platform], color], random_name]
                f_md5_json.seek(0) 
                f_md5_json.truncate()
                f_md5_json.flush()
                json.dump(md5dict, f_md5_json)
                f_md5_json.close()
                with zipfile.ZipFile(f'./download/{random_name}.zip', 'w') as zip_file:
                    zip_file.write(f'./upload/{random_name}_exe_details.txt')
                    if result != 'NON-VIRUS':
                        zip_file.write(f'./upload/'+random_name+'.asm_3gramfeature.csv')
                        zip_file.write(f'./upload/'+random_name+'.asm_imgfeature.csv')
                rmtree('./upload')
            return [[[result, platform], color], random_name]
        result = judge_file(random_name)   
    color = result[0][-1]
    if random_name != result[-1]:
        is_same = True
        random_name = result[-1]
    result = result[0][0]
    tag = Generate_tag(result) #TODO add more TAG
        
    html = '''
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
                .small {
                font-size: xx-small;
                }
                .larger {
                font-size: larger;
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
        <p class="small">Size: '''+NumberOfBytesHumanRepresentation(file_size)+'''</p>
        <p class="small">MD5: '''+data_md5+'''</p>
        <p class="small">ID: '''+random_name+'''</p>
        <h1 class="'''+color+''' larger">predict type: '''+tag+'''</h1>'''
    if os.path.exists('./download/'+random_name+'.zip'):
        html += '''
        <p></p>
                <div>
        <a href="/downloadfile/?file_name='''+random_name+'''.zip" download>Download details</a>
    </div>
        </body>
        </html>
        '''
    elif result[0][0] == 'UNAVALIABLE PE FILE (failed to load)' or result[0][0] == 'UNAVALIABLE PE FILE (header broken)' or result[0][0] == f'FILE TOO LARGE ({NumberOfBytesHumanRepresentation(file_size)})':
        pass
    if is_same:
        html +=f'''
        <p></p>
        <p></p>
        <p></p>
        <p></p>
        <p></p>
                <div>
        <p class="red small">This file has already been uploaded(same file uploaded with ID {random_name})</p>
    </div>
        </body>
        </html>
        '''
    return html
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)