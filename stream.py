from flask import Flask, Response
from picamera2.picamera2 import Picamera2
from threading import Thread
import cv2
import numpy as np
from queue import Queue
import time

app = Flask(__name__)

def generate_frames(output_queue):
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(main={"size": (320, 240)})
    picam2.configure(preview_config)
    picam2.start()
    last_time = time.time()
    while True:
        current_time = time.time()
        frame = picam2.capture_array()
        time_diff = current_time - last_time
        if time_diff > 0:  # Prevent division by zero
            framerate = 1 / time_diff  # Calculate the framerate
            framerate_str = f"{framerate:.2f} FPS"
            cv2.putText(frame, framerate_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', frame,[int(cv2.IMWRITE_JPEG_QUALITY), 85])
        frame = buffer.tobytes()
        output_queue.put(frame)
        last_time = current_time

def frame_generator(output_queue):
    while True:
        frame = output_queue.get()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video():
    output_queue = Queue()
    t = Thread(target=generate_frames, args=(output_queue,))
    t.start()
    return Response(frame_generator(output_queue), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')