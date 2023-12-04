from flask import Flask, render_template, Response, jsonify, request
import cv2
from PIL import Image
from io import BytesIO
import os
import datetime
import secrets
import numpy as np

app = Flask(__name__)

 # 全局變數，用於判斷是否套用濾鏡
cap = cv2.VideoCapture(0)
original_mode = False
black_and_white_mode = False 
canny_mode = False
adaptive_gaussian_thresholding_mode = False
gaussian_blur_mode = False
convex_mode = False

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
            if original_mode:
                frame = frame
            # 如果黑白模式為 True，套用黑白濾鏡
            if black_and_white_mode:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ret, thresholded_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)
                frame = cv2.cvtColor(thresholded_frame, cv2.COLOR_GRAY2BGR)
            if canny_mode:
                frame = cv2.Canny(frame, 100, 150)
            if adaptive_gaussian_thresholding_mode:
                img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                img_gray = cv2.medianBlur(img_gray, 5)
                frame = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            if gaussian_blur_mode:
                frame = cv2.GaussianBlur(frame, (25, 25), 0)
            if convex_mode:
                def convex(img, raw, effect):
                    nc, nr, channel = raw[:]
                    cx, cy, r = effect[:]
                    new_img = np.zeros([nr, nc, channel], dtype = np.uint8)
                    for y in range(nr):
                        for x in range(nc):
                            d = ((x - cx) * (x - cx) + (y - cy) * (y - cy)) ** 0.5
                            if d <= r:
                                nx = int((x - cx) * d / r + cx)
                                ny = int((y - cy) * d / r + cy)
                                new_img[y, x, :] = img[ny, nx, :]
                            else:
                                new_img[y, x, :] = img[y, x, :]
                    return new_img
                scale = 0.5
                w, h = int(640*scale), int(320*scale)
                cw, ch = int(w/2), int(h/2)            # 取得中心點
                frame = cv2.resize(frame,(w, h))  
                frame = convex(frame, (w, h, 3), (cw, ch, 100))

            # 將畫面水平鏡像
            frame = cv2.flip(frame, 1)
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

@app.route('/activate_original_mode', methods=['POST'])
def activate_original_mode():
    global original_mode, black_and_white_mode, canny_mode, adaptive_gaussian_thresholding_mode, gaussian_blur_mode, convex_mode
    original_mode = True
    black_and_white_mode = False
    canny_mode = False
    adaptive_gaussian_thresholding_mode = False
    gaussian_blur_mode = False
    convex_mode = False
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/activate_black_and_white_mode', methods=['POST'])
def activate_black_and_white_mode():
    global original_mode, black_and_white_mode, canny_mode, adaptive_gaussian_thresholding_mode, gaussian_blur_mode, convex_mode
    original_mode = False
    black_and_white_mode = True
    canny_mode = False
    adaptive_gaussian_thresholding_mode = False
    gaussian_blur_mode = False
    convex_mode = False
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/activate_canny_mode', methods=['POST'])
def activate_canny_mode():
    global original_mode, black_and_white_mode, canny_mode, adaptive_gaussian_thresholding_mode, gaussian_blur_mode, convex_mode
    original_mode = False
    black_and_white_mode = False
    canny_mode = True
    adaptive_gaussian_thresholding_mode = False
    gaussian_blur_mode = False
    convex_mode = False
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/activate_adaptive_gaussian_thresholding_mode', methods=['POST'])
def activate_adaptive_gaussian_thresholding_mode():
    global original_mode, black_and_white_mode, canny_mode, adaptive_gaussian_thresholding_mode, gaussian_blur_mode, convex_mode
    original_mode = False
    black_and_white_mode = False
    canny_mode = False
    adaptive_gaussian_thresholding_mode = True
    gaussian_blur_mode = False
    convex_mode = False
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/activate_gaussian_blur_mode', methods=['POST'])
def activate_gaussian_blur_mode():
    global original_mode, black_and_white_mode, canny_mode, adaptive_gaussian_thresholding_mode, gaussian_blur_mode, convex_mode
    original_mode = False
    black_and_white_mode = False
    canny_mode = False
    adaptive_gaussian_thresholding_mode = False
    gaussian_blur_mode = True
    convex_mode = False
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/activate_convex_mode', methods=['POST'])
def activate_convex_mode():
    global original_mode, black_and_white_mode, canny_mode, adaptive_gaussian_thresholding_mode, gaussian_blur_mode, convex_mode
    original_mode = False
    black_and_white_mode = False
    canny_mode = False
    adaptive_gaussian_thresholding_mode = False
    gaussian_blur_mode = False
    convex_mode = True
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/take_snapshot', methods=['POST'])
def take_snapshot():
    global original_mode, black_and_white_mode, canny_mode, adaptive_gaussian_thresholding_mode, gaussian_blur_mode, convex_mode    
    mode = request.form.get('mode')
    if mode == 'camera':
        ret, frame = cap.read()
        if ret:
            if original_mode == True:
                frame = frame
                print("ori")
                original_mode = False

            if black_and_white_mode == True:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ret, thresholded_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)
                frame = cv2.cvtColor(thresholded_frame, cv2.COLOR_GRAY2BGR)
                black_and_white_mode = False
                print("black")

            if canny_mode == True:
                frame = cv2.Canny(frame, 100, 150)
                canny_mode = False
                print("canny")

            if adaptive_gaussian_thresholding_mode == True:
                img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                img_gray = cv2.medianBlur(img_gray, 5)
                frame = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                adaptive_gaussian_thresholding_mode = False
                print("gaussian")

            if gaussian_blur_mode == True:
                frame = cv2.GaussianBlur(frame, (25, 25), 0)
                gaussian_blur_mode = False
                print("gaussian_blur")

            if convex_mode == True:
                def convex(img, raw, effect):
                    nc, nr, channel = raw[:]
                    cx, cy, r = effect[:]
                    new_img = np.zeros([nr, nc, channel], dtype = np.uint8)
                    for y in range(nr):
                        for x in range(nc):
                            d = ((x - cx) * (x - cx) + (y - cy) * (y - cy)) ** 0.5
                            if d <= r:
                                nx = int((x - cx) * d / r + cx)
                                ny = int((y - cy) * d / r + cy)
                                new_img[y, x, :] = img[ny, nx, :]
                            else:
                                new_img[y, x, :] = img[y, x, :]
                    return new_img
                scale = 0.5
                w, h = int(640*scale), int(320*scale)
                cw, ch = int(w/2), int(h/2)            # 取得中心點
                frame = cv2.resize(frame,(w, h))  
                frame = convex(frame, (w, h, 3), (cw, ch, 100))
                convex_mode = False
                print("convex")

            # 使用日期和隨機字串生成獨一無二的檔名
            frame = cv2.flip(frame, 1)
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
