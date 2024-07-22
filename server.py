from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_201_CREATED
import fastapi_cdn_host
import os
import uvicorn
from main import process_upload_asm, detect_virus, exe2asm
from shutil import rmtree
from random import randint

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
        <p>Upload your file here (only .asm files allowed).</p>
        <form action="/uploadfile/" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".asm">
            <button type="submit">Upload File</button>
        </form>
        <div class="message" id="message"></div>
    </body>
    </html>
    """

# 文件上传的API端点
@app.post("/uploadfile/", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    random_name = str(randint(100000, 999999))
    fn = random_name+'.exe'
    save_path = f'./upload/'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    save_file = os.path.join(save_path, fn)

    f = open(save_file, 'wb')
    data = await file.read()
    f.write(data)
    if detect_virus(save_file):
        #TODO 把exe反编译成asm
        asm_file = exe2asm(data)
        result = process_upload_asm(asm_file)
        rmtree('./upload')
    else:
        result = 'NON-VIRUS'
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
        <h1>predict type: """+result+"""</h1>
        </body>
        </html>
        """

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)