from flask import Flask, render_template, Response, jsonify, request
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
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

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
