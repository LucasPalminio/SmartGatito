import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import threading
import json
import requests

def read_credentials():
    with open('credentials.json') as file:
        credentials = json.load(file)
    return credentials

credentials = read_credentials()
clientId = credentials["broker"]['clientId']
username = credentials["broker"]['username']
password = credentials["broker"]['password']
broker_address = credentials["broker"]["host"]
port = credentials["broker"]["port"]


def on_connect(client, userdata, flags, rc): # Función que se ejecuta cuando se conecta al broker
    print("Connected with result code "+str(rc))
    client.subscribe("v1/devices/me/attributes")


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
            #print("Distancia:", cm, "cm")   
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()


def modeSwitch(): # Función para cambiar modo de la fuente
    global modo
    global cm
    try:
        while True:
            print("Modo:", modo)
            if modo == 1:
                GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
                print("Fuente Encendida")
            elif modo == 2:
                if cm < 30:
                    GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
                    send_telemetry()
                    time.sleep(15)
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
    

def send_telemetry(): # Función para enviar señal a ThingsBoard cada vez que el gato bebe agua
    try:
        print("Enviando telemetría")
        url = "http://iot.ceisufro.cl:8080/api/plugins/telemetry/DEVICE/"+credentials["API"]["deviceId"]+"/SHARED_SCOPE"
        headers = {'Content-Type': 'application/json', 'X-Authorization': 'Bearer ' + token, 'connection':'keep-alive'}
        data = {'agua': 1}
        response = requests.post(url, json=data, headers=headers)
        print(response.status_code)
    except Exception as e:
        print("Error de conexión:", e)

def getToken():
    global token
    url = "http://iot.ceisufro.cl:8080/api/auth/login"
    headers = {'Content-Type': 'application/json'}
    data = {'username': credentials["API"]["username"], 'password': credentials["API"]["password"]}
    response = requests.post(url, json=data, headers=headers)
    token = response.json()["token"]

if __name__ == '__main__':
    getToken()
    # Definir hilos
    t1 = threading.Thread(target=distanceMonitor, name='Distance Monitor', daemon=True)
    t2 = threading.Thread(target=subscriber, name='Subscriber', daemon=True)
    t3 = threading.Thread(target=modeSwitch, name='Mode Switch', daemon=True)
    # Iniciar hilos
    t1.start()
    t2.start()
    t3.start()
    try:
        # Esperar a que los hilos terminen
        t1.join()
        t2.join()
        t3.join()
    except KeyboardInterrupt:
        GPIO.cleanup()



