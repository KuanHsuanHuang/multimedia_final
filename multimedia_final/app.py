from flask import Flask, render_template_string, Response, jsonify, request
import cv2
from PIL import Image
from io import BytesIO
import os
import datetime
import secrets

app = Flask(__name__)

cap = cv2.VideoCapture(0)

# 設定照片保存資料夾
photos_folder = 'photos'
if not os.path.exists(photos_folder):
    os.makedirs(photos_folder)

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # HTML 字符串，包含彩色漸層的標題和按鈕
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Filter Selection</title>
        <style>
            #right-frame {
                width: 50%;
                height: 100vh;
                box-sizing: border-box;
                background: linear-gradient(to bottom, #4CAF50, #45a049);
                color: white;
                text-align: center;
                padding: 20px;
            }

            h1 {
                font-weight: bold;
            }

            button {
                margin: 10px;
                padding: 10px;
                font-size: 16px;
                background-color: #008CBA;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div id="left-frame"></div>
        <div id="right-frame">
            <h1>請挑選濾鏡</h1>
            <button>a</button>
            <button>b</button>
            <button>c</button>
            <button>d</button>
            <button>e</button>
        </div>
    </body>
    </html>
    """

    return render_template_string(html_content)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/take_snapshot', methods=['POST'])
def take_snapshot():
    mode = request.form.get('mode')
    
    if mode == 'camera':
        ret, frame = cap.read()
        if ret:
            # 使用日期和隨機字串生成獨一無二的檔名
            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            random_string = secrets.token_hex(4)
            file_name = f"{current_time}_{random_string}.png"
            
            # 保存照片到指定資料夾
            file_path = os.path.join(photos_folder, file_name)
            cv2.imwrite(file_path, frame)
            
            return jsonify({"message": f"拍照成功，檔案已保存為 {file_name}。"})
        else:
            return jsonify({"message": "拍照失敗，請再試一次。"})
    else:
        return jsonify({"message": "模式錯誤。"})

if __name__ == "__main__":
    app.run(debug=True)
