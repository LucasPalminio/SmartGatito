import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import threading
import json
import requests
import cv2 
from picamera2 import Picamera2


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

def detectCat():
    # capture frames from a camera  
    global cap
    global isGatito
    cap.start()
    while True:  
        # reads frames from a camera  
        img = cap.capture_array() 
        # convert to gray scale of each frames  
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
        # Detects faces of different sizes in the input image  
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)  
        if len(faces) > 1:  # Si len(faces) > 0 entonces se detectó un gato
            print("Gatito Detectado")
            isGatito = True
        else:
            print("Gatito no Detectado")
            isGatito = False
        time.sleep(1)

if __name__ == '__main__':
    getToken()
    # Definir hilos
    # Definir hilos
    t1 = threading.Thread(target=distanceMonitor, name='Distance Monitor', daemon=True)
    t2 = threading.Thread(target=subscriber, name='Subscriber', daemon=True)
    t3 = threading.Thread(target=modeSwitch, name='Mode Switch', daemon=True)
    t4 = threading.Thread(target=detectCat, name='Cat Detection', daemon=True)
    # Iniciar hilos
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    try:
        # Esperar a que los hilos terminen
        t1.join()
        t2.join()
        t3.join()
        t4.join()
    except KeyboardInterrupt:
        GPIO.cleanup()


