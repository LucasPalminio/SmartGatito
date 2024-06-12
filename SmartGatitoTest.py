import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import threading
import json
import requests
import cv2 
from queue import Queue
from picamera2 import Picamera2
from flask import Flask, Response


with open('secrets.json') as file:
        secrets = json.load(file)

clientId = secrets["broker"]['clientId']
username = secrets["broker"]['username']
password = secrets["broker"]['password']
broker_address = secrets["broker"]["host"]
port = secrets["broker"]["port"]


def on_connect(client, userdata, flags, rc): # Función que se ejecuta cuando se conecta al broker
    print("Connected with result code "+str(rc))
    client.subscribe("v1/devices/me/attributes",2)

def on_message(client, userdata, msg): # Función que se ejecuta cuando se recibe un mensaje
    global t3
    global exit
    print(msg.topic+" "+str(msg.payload))
    global modo
    data = json.loads(msg.payload)
    if "modo" in data:
        modo = int(data["modo"])

# Variables
cm = 0  # Distancia en centímetros
modo = 2  # Modo inicial
agua = 0  # Contador de veces que el gato bebe agua
token = ""
face_cascade = cv2.CascadeClassifier('./CatRecognitionSystem/haarcascade_frontalcatface.xml')  
cap = Picamera2()
isGatito = False
detectado = False
app = Flask(__name__)
# Global variable for shared image
shared_image = None
image_lock = threading.Lock()  # Ensure thread-safe access to shared_image

# Configuración MQTT
client = mqtt.Client(clientId)  # Crear nuevo objeto de instancia
client.username_pw_set(username, password)  # Configurar usuario y contraseña
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, port)  # Conectar al broker

# Definición de pines
trigPin = 24  # Pin trigger del sensor ultrasónico (GPIO18)
echoPin = 23  # Pin echo del sensor ultrasónico (GPIO16)
pinRele = 14   # Pin para controlar el relé (GPIO8)
GPIO.setmode(GPIO.BCM)  # Configuración de numeración de pines
GPIO.setup(pinRele, GPIO.OUT)  # Pin del relé como salida
GPIO.setup(trigPin, GPIO.OUT)  # Pin del sensor de ultrasonido como salida
GPIO.setup(echoPin, GPIO.IN)  # Pin del sensor de ultrasonido como entrada
GPIO.output(trigPin, False)  # Inicializar el pin del sensor de ultrasonido en bajo
time.sleep(2)  # Esperar 2 segundos para estabilizar el sensor
    
def distanceMonitor(): # Función para medir distancia
    global cm
    global detectado
    try:
        while True:
            #print("midiendo distancia")
            GPIO.output(trigPin, True)
            time.sleep(0.00001)
            GPIO.output(trigPin, False)
            while GPIO.input(echoPin)==0:
                pulse_start = time.time()
            while GPIO.input(echoPin)==1:
                pulse_end = time.time()
            duration = pulse_end - pulse_start
            cm = duration * 17150
            cm =  round(cm, 2)
            if cm < 30:
                detectado = True
                send_telemetry("detectado")
            else:
                detectado = False
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()


def modeSwitch(): # Función para cambiar modo de la fuente
    global modo
    global isGatito
    global detectado
    try:
        while True:
            print("Modo:", modo)
            if modo == 1:
                GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
                print("Fuente Encendida")
            elif modo == 2:
                if detectado and isGatito:
                    GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
                    send_telemetry("agua")
                    time.sleep(2)
                else:
                    GPIO.output(pinRele, GPIO.HIGH)  # Apagar la bomba    
            elif modo == 3:
                # Modo siempre apagado
                GPIO.output(pinRele, GPIO.HIGH)  # Apagar la bomba
                print("Fuente Apagada")       
            time.sleep(1)  # Tiempo de espera para cambiar de modo
    except KeyboardInterrupt:
        GPIO.cleanup()

def subscriber(): # Función para suscribirse al topic
    client.loop_forever()
    

def send_telemetry(key): # Función para enviar señal a ThingsBoard cada vez que el gato bebe agua
    try:
        print("Enviando telemetría")
        url = "http://iot.ceisufro.cl:8080/api/plugins/telemetry/DEVICE/"+secrets["API"]["deviceId"]+"/SHARED_SCOPE"
        headers = {
            'Content-Type': 'application/json',
            'X-Authorization': 'Bearer ' + token,
            'Connection':'keep-alive',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br'
            }
        data = {key: 1}
        response = requests.post(url, json=data, headers=headers)
        print(response.status_code)
    except Exception as e:
        print("Error de conexión:", e)

def getToken():
    global token
    url = "http://iot.ceisufro.cl:8080/api/auth/login"
    headers = {'Content-Type': 'application/json'}
    data = {'username': secrets["API"]["username"], 'password': secrets["API"]["password"]}
    response = requests.post(url, json=data, headers=headers)
    token = response.json()["token"]

def generate_frames(output_queue):
    global isGatito
    try:
        last_time = time.time()
        while True:
            current_time = time.time()
            with image_lock:   
                img = shared_image  
            if img is not None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
                # Detects faces of different sizes in the input image  
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)  
                # Draw rectangles around detected faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # Calculate framerate
                time_diff = current_time - last_time
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
                if len(faces) > 0:
                    print("Gatito Detectado")
                    isGatito = True
                else:
                    print("Gatito no Detectado")
                    isGatito = False
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

def threadsInit():
    print("Iniciando aplicación")
    getToken()
    t1 = threading.Thread(target=distanceMonitor, name='Distance Monitor', daemon=True)
    t2 = threading.Thread(target=subscriber, name='Subscriber', daemon=True)
    t3 = threading.Thread(target=modeSwitch, name='Mode Switch', daemon=True)
    t4 = threading.Thread(target=cameraStartup, name='Camera Startup', daemon=True)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    print("Aplicación iniciada")


if __name__ == '__main__':
    threadsInit()
    app.run(debug=False, host='0.0.0.0', threaded=True)
