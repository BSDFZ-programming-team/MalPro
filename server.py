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
from hashlib import sha256, md5
from main import process_upload_asm, exe2asm, detect_virus, getfeaturenum
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
ida_PATH = input('your IDA path: >>> ')
if not ida_PATH.endswith('/') or not ida_PATH.endswith('\\'):
    ida_PATH += '/'
if not os.path.exists(ida_PATH):
    print('[-] Path not found')
    exit()
if not os.path.isdir(ida_PATH):
    print('[-] Input your install dir, ex: D:/IDApro/')
if not 'idat64.exe' in os.listdir(ida_PATH):
    print('[-] idat64.exe missing')
app = FastAPI()
# fastapi_cdn_host.patch_docs(app, favicon_url='./static/logo.svg')
# 定义上传文件的目标目录
os.makedirs("./upload", exist_ok=True)
os.makedirs("./download", exist_ok=True)
# 静态文件目录
app.mount("/static", StaticFiles(directory="./static"), name="static")
app.mount("/js", StaticFiles(directory="./js"), name="js")
# app.mount("/css", StaticFiles(directory="./css"), name="css")
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
            .text_display {
                flex: left;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                font-family: 'good_font', Arial, sans-serif;
            }
            .container{
                overflow: hiddden;
                display: flex;
                background-color: #eaeaea;
            }            
            .box {
                float: left;
                width: 100%;
                height: 50%;
                margin-right: 10px;
            }         
            .fire{
                flex: right;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
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
                              .enter-x-left {
        z-index: 9;
        opacity: 0;
        animation: enter-x-left 0.4s ease-in-out 0.3s;
        animation-fill-mode: forwards;
        transform: translateX(-50px);
      }
      .enter-x-right {
        z-index: 9;
        opacity: 0;
        animation: enter-x-right 0.4s ease-in-out 0.3s;
        animation-fill-mode: forwards;
        transform: translateX(50px);
      }
      .enter-x-left:nth-child(1),
      .enter-x-right:nth-child(1) {
        animation-delay: 0.1s;
      }
      .enter-x-left:nth-child(2),
      .enter-x-right:nth-child(2) {
        animation-delay: 0.2s;
      }
      .enter-x-left:nth-child(3),
      .enter-x-right:nth-child(3) {
        animation-delay: 0.3s;
      }
      .enter-x-left:nth-child(4),
      .enter-x-right:nth-child(4) {
        animation-delay: 0.4s;
      }
      

      @keyframes enter-x-left {
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
      @keyframes enter-x-right {
        to {
          opacity: 1;
          transform: translateY(0);
        }
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
                color: blue;
                font-family: 'good_font', Arial, sans-serif;
                                justify-content: top;
            }
        </style>
    </head>
    <body>

        <div class="container">
        <div class="box enter-x-left">
    <div class="text_display">
        <img id="logo" src="/static/logo.png" alt="Logo">
        <h1>MalPro v0.1 Beta</h1>
        <p>Upload your file here (only PE & ≤1MB files allowed).</p>
        <form action="/uploadfile/" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload File</button>
        </form>
        <p></p>
                                <div>
        <a href="https://github.com/BSDFZ-programming-team/MalPro" class="message">Need Help?</a>
    </div>
        </div>
        </div>
        <div class="box enter-x-right">
    <div class="fire">
           <svg class="flameSVG" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">

	<defs> 
		<rect class="flame" x="400" y="310" width="5" height="5" rx="0.5"  ry="0.5" fill="#FFDD02"/>
		<circle class="spark" cx="400" cy="300" r="0.05" fill="#FFDD02"/>
		<filter id="shadow" x="-100%" y="-100%" width="250%" height="250%">
			<feOffset in="SourceAlpha" dx="4" dy="4" result="offsetOut"></feOffset>        
			<feGaussianBlur stdDeviation="3" in="offsetOut" result="drop" />
			<feOffset dx="0" dy="0" result="offsetblur"></feOffset>
			<feFlood id="glowAlpha" flood-color="#0F1217" flood-opacity="0.42"></feFlood>
			<feComposite in2="offsetblur" operator="in"></feComposite>
			<feMerge>
				<feMergeNode/>          
				<feMergeNode in="SourceGraphic"></feMergeNode>
			</feMerge>
		</filter>   
	</defs>
	
	<g class="whole">
		<g class="flameContainer" />
		<g class="sparksContainer" />
		<g class="logs" opacity="1">
			<path d="M446.68,299.63l-91.46,29.22a3,3,0,0,1-3.68-2.12L349.2,318a3,3,0,0,1,2.12-3.68l91.46-29.22a3,3,0,0,1,3.68,2.12L448.8,296A3,3,0,0,1,446.68,299.63Z" fill="#612e25"/>
			<path filter="url(#shadow)" d="M349.2,296l2.34-8.69a3,3,0,0,1,3.68-2.12l91.46,29.22A3,3,0,0,1,448.8,318l-2.34,8.69a3,3,0,0,1-3.68,2.12l-91.46-29.22A3,3,0,0,1,349.2,296Z" fill="#70392f"/>
		</g>
	</g>

	<rect class="hit" width="200" height="260" x="300" y="230" fill="transparent">
	</rect>

</svg>

<script src='js/TweenMax.min.js'></script>
<script src='js/CustomEase.min.js'></script>
<script src="js/index.js"></script>
</div></div>
        </div>
    </body>
    </html>
    """

@app.post("/uploadfile/", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    random_name = str(randint(100000, 999999))
    is_same = False
    file_size = file.size
    data_md5 = sha256(data).hexdigest()
    if file_size > 1024*1024:
        result=[[[f'FILE TOO LARGE ({NumberOfBytesHumanRepresentation(file_size)})', ''], 'red'], random_name]
    else:
        fn = random_name+'.exe'
        if not os.path.exists('./upload/'):
            os.mkdir('./upload/')
        save_file = os.path.join('./upload/', fn)
        f = open(save_file, 'wb')
        f.write(data)
        f.close()
        del f
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
            if analyze_result == 'Header broken':
                result = 'UNAVALIABLE PE FILE (header broken)'
                platform = ''
                color = 'red'
            if analyze_result == 'Load failed':
                result = 'UNAVALIABLE PE FILE (failed to load)'
                platform = ''
                color = 'red'
            else:
                pe = analyze_result
                buffer = StringIO()
                sys.stdout = buffer
                print(pe)
                with open(f'./upload/{random_name}_exe_details.txt', 'w+') as f:
                    f.write(buffer.getvalue())
                sys.stdout = sys.__stdout__
                del f
                try:
                    platform = utils.PE_analyse.analyze_machine(pe)
                    pe.close()
                except:
                    platform = ''
                if detect_virus(save_file): #TODO: detect virus
                    asm_file = exe2asm(save_file, ida_PATH)
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
            if result !=  'UNAVALIABLE PE FILE (failed to load)' and result != 'UNAVALIABLE PE FILE (header broken)' and result != f'FILE TOO LARGE ({NumberOfBytesHumanRepresentation(file_size)})':
                with zipfile.ZipFile(f'./download/{random_name}.zip', 'w') as zip_file:
                    zip_file.write(f'./upload/{random_name}_exe_details.txt', random_name+'PE_details.txt')
                    if result != 'NON-VIRUS':
                        zip_file.write(f'./upload/'+random_name+'.exe.asm_3gramfeature.csv', './features/'+random_name+'_3gramfeature.csv')
                        zip_file.write(f'./upload/'+random_name+'.exe.asm_imgfeature.csv', './features/'+random_name+'_imgfeature.csv')
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
                          .green{
            color:green;
            font-size:20px;
        }
                .red{
            color:red;
            font-size:20px;
        }
            .text_display {
                flex: left;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                font-family: 'good_font', Arial, sans-serif;
            }
                  .enter-x-left {
        z-index: 9;
        opacity: 0;
        animation: enter-x-left 0.4s ease-in-out 0.3s;
        animation-fill-mode: forwards;
        transform: translateX(-50px);
      }
      .enter-x-right {
        z-index: 9;
        opacity: 0;
        animation: enter-x-right 0.4s ease-in-out 0.3s;
        animation-fill-mode: forwards;
        transform: translateX(50px);
      }
      .enter-x-left:nth-child(1),
      .enter-x-right:nth-child(1) {
        animation-delay: 0.1s;
      }
      .enter-x-left:nth-child(2),
      .enter-x-right:nth-child(2) {
        animation-delay: 0.2s;
      }
      .enter-x-left:nth-child(3),
      .enter-x-right:nth-child(3) {
        animation-delay: 0.3s;
      }
      .enter-x-left:nth-child(4),
      .enter-x-right:nth-child(4) {
        animation-delay: 0.4s;
      }
      

      @keyframes enter-x-left {
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
      @keyframes enter-x-right {
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
            .details_display {
                flex: left;
                display: flex;
                flex-direction: column;
                align-items: left;
                justify-content: left;
                height: 100vh;
                margin: 0;
                font-family: 'good_font', Arial, sans-serif;
            }
            .container{
                overflow: hiddden;
                display: flex;
                background-color: #eaeaea;
            }            
            .box {
                float: left;
                width: 100%;
                height: 100%;
                margin-right: 10px;
            }         
            .fire{
                flex: right;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            
            #logo {
                width: 300px;
                height: auto;png
                margin-top: 20px;
            }
            h1 {
                font-size: 24px;
                color: black; 
            }
            form {
                margin-top: 20px;
            }
            .message {
                margin-top: 20px;
                font-size: 18px;
                color: blue;
                font-family: 'good_font', Arial, sans-serif;
                                justify-content: top;
            }
        </style>
    </head>
    <body>
        <div class="container">
        <div class="box enter-x-left">
    <div class="text_display">
        <img id="logo" src="/static/logo.png" alt="Logo">
        <h1>MalPro v0.1 Beta</h1>
        <h3 class="'''+color+''' larger">predict type: '''+tag+'''</h3>    
<svg class="flameSVG" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">

	<defs> 
		<rect class="flame" x="400" y="310" width="5" height="5" rx="0.5"  ry="0.5" fill="#FFDD02"/>
		<circle class="spark" cx="400" cy="300" r="0.05" fill="#FFDD02"/>
		<filter id="shadow" x="-100%" y="-100%" width="250%" height="250%">
			<feOffset in="SourceAlpha" dx="4" dy="4" result="offsetOut"></feOffset>        
			<feGaussianBlur stdDeviation="3" in="offsetOut" result="drop" />
			<feOffset dx="0" dy="0" result="offsetblur"></feOffset>
			<feFlood id="glowAlpha" flood-color="#0F1217" flood-opacity="0.42"></feFlood>
			<feComposite in2="offsetblur" operator="in"></feComposite>
			<feMerge>
				<feMergeNode/>          
				<feMergeNode in="SourceGraphic"></feMergeNode>
			</feMerge>
		</filter>   
	</defs>
	
	<g class="whole">
		<g class="flameContainer" />
		<g class="sparksContainer" />
		<g class="logs" opacity="1">
			<path d="M446.68,299.63l-91.46,29.22a3,3,0,0,1-3.68-2.12L349.2,318a3,3,0,0,1,2.12-3.68l91.46-29.22a3,3,0,0,1,3.68,2.12L448.8,296A3,3,0,0,1,446.68,299.63Z" fill="#612e25"/>
			<path filter="url(#shadow)" d="M349.2,296l2.34-8.69a3,3,0,0,1,3.68-2.12l91.46,29.22A3,3,0,0,1,448.8,318l-2.34,8.69a3,3,0,0,1-3.68,2.12l-91.46-29.22A3,3,0,0,1,349.2,296Z" fill="#70392f"/>
		</g>
	</g>

	<rect class="hit" width="200" height="260" x="300" y="230" fill="transparent">
	</rect>

</svg>
<div>
        <a href="https://github.com/BSDFZ-programming-team/MalPro" class="message">Need Help?</a>
    </div>
    </body>
    </html>
<script src='../js/TweenMax.min.js'></script>
<script src='../js/CustomEase.min.js'></script>
<script src="../js/index.js"></script>
        </div>
        </div>
        <div class="box enter-x-right">
<div class="details_display">                            
'''
    if result[0] == 'UNAVALIABLE PE FILE (failed to load)' or result[0] == 'UNAVALIABLE PE FILE (header broken)' or result[0] == f'FILE TOO LARGE ({NumberOfBytesHumanRepresentation(file_size)})':
        error = True
    else:
        error = False
    if os.path.exists('./download/'+random_name+'.zip'):
        html += '''
        <h2>FILE INFO</h2>
        <p>&emsp;Size: '''+NumberOfBytesHumanRepresentation(file_size)+'''</p>
        <p>&emsp;ID: '''+random_name+'''</p>
        <p>&emsp;Filename: '''+file.filename+'''</p>
        <p>&emsp;Sha256: '''+data_md5+'''</p>
        <p>&emsp;MD5: '''+md5(data).hexdigest()+'''</p>
                <h2>ANALYZE DETAILS</h2>

                <div>
        <a href="/downloadfile/?file_name='''+random_name+'''.zip" download>Download PE & feature details</a>
    </div>
        <h2>MODEL INFO</h2>
        <h5>&emsp;Asmimage features</h5>
        <p>&emsp;&emsp;Deprecated</p>
        <h5>&emsp;Opcode-ngram features</h5>
        <p>&emsp;&emsp;n: 3</p>
        <p>&emsp;&emsp;loaded features: '''+str(getfeaturenum())+'''</p>
        '''
    elif error:
        pass
    if is_same:
        if not error:
            html +=f'''
                    <div>
            <p class="red small">This file has already been uploaded(ID {random_name})</p>
            </div>
        '''
    html += f'''</div>
        </div>
        </div>
        </body>
        </html>
        '''
#     html += f'''
# <div>
#         <a href="https://github.com/BSDFZ-programming-team/MalPro" class="message">Need Help?</a>
#     </div>
# </div></div>
#         </div>
#     </body>
#     </html>
# '''
    return html
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7777)