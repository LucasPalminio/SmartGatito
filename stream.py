from flask import Flask, Response
from picamera2.picamera2 import Picamera2
from threading import Thread
import cv2
import numpy as np
from queue import Queue
import time
import threading
app = Flask(__name__)
cap = Picamera2()
face_cascade = cv2.CascadeClassifier('./CatRecognitionSystem/haarcascade_frontalcatface.xml')  
shared_image = None
isGatito = False
detectado = False
image_lock = threading.Lock()
def generate_frames(output_queue):
    global isGatito
    try:
        last_time = time.time()
        while True:
            current_time = time.time()
            with image_lock:   
                img = shared_image  
            if img is not None:
               # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
                # Detects faces of different sizes in the input image  
               # faces = face_cascade.detectMultiScale(gray, 1.3, 5)  
                # Draw rectangles around detected faces
               # for (x, y, w, h) in faces:
                #    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # Calculate framerate
                time_diff = current_time - last_time
                img = cv2.flip(img, 0)
                if time_diff > 0:  # Prevent division by zero
                    framerate = 1 / time_diff  # Calculate the framerate
                    framerate_str = f"{framerate:.2f} FPS"
                    cv2.putText(img, framerate_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                # Encode the frame in JPEG format
                ret, buffer = cv2.imencode('.jpg', img,[int(cv2.IMWRITE_JPEG_QUALITY), 55])
                img = buffer.tobytes()
                # Add the frame to the output queue
                output_queue.put(img)
                # Check if any cat faces were detected
               # if len(faces) > 0:
                #    print("Gatito Detectado")
                #    isGatito = True
               # else:
                #    print("Gatito no Detectado")
                #    isGatito = False
                last_time = current_time
    except Exception as e:
        print(f"Error generating frames: {e}")


def frame_generator(output_queue):
    while True:
        frame = output_queue.get()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
def cameraCapture():
    global shared_image
    while True:
        # Capture image from camera
        img = cap.capture_array()
        with image_lock:
            shared_image = img
        time.sleep(0.01666)  # Adjust based on required capture rate


@app.route('/video')
def video():
    output_queue = Queue()   
    # Definir hilos
    print("Iniciando Stream")
    t5 = threading.Thread(target=cameraCapture, name='Camera Frame capture', daemon=True)
    t6 = threading.Thread(target=generate_frames,  args=(output_queue,), name='Video Streaming', daemon=True)
    
    # Iniciar hilos
    t5.start()
    t6.start()

        

    return Response(frame_generator(output_queue), mimetype='multipart/x-mixed-replace; boundary=frame')

def cameraStartup():
    global cap
    preview_config = cap.create_preview_configuration(main={"size": (320, 240)})
    cap.configure(preview_config)
    cap.start()



if __name__ == '__main__':
    cameraStartup()
    app.run(debug=False, host='0.0.0.0', threaded=True)