import RPi.GPIO as GPIO
import time
import requests
import paho.mqtt.client as mqtt
import threading
import json

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("v1/devices/me/rpc/request/+")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    global modo
    data = json.loads(msg.payload)
    if data["method"] == "setMode":
        if modo=="3":
            modo = "1"
        else:
            modo = str(int(modo)+1)

# Definición de pines
trigPin = 24  # Pin trigger del sensor ultrasónico (GPIO18)
echoPin = 23  # Pin echo del sensor ultrasónico (GPIO16)
pinRele = 14   # Pin para controlar el relé (GPIO8)

# Variables
cm = 0  # Distancia en centímetros
modo = "2"  # Modo inicial
agua = 0  # Contador de veces que el gato bebe agua
# Configuración MQTT
broker_address = "mqtt.thingsboard.cloud"
port = 1883 
client = mqtt.Client("30vte5orp3pywd6get3n")  # Crear nuevo objeto de instancia
client.username_pw_set("emzn7leosagnh376l84e", "ouokpwl7dyfo0xdv1pwn")  # Configurar usuario y contraseña
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, port)  # Conectar al broker

GPIO.setmode(GPIO.BCM)  # Configuración de numeración de pines
GPIO.setup(pinRele, GPIO.OUT)  # Pin del relé como salida
GPIO.setup(trigPin, GPIO.OUT)  # Pin del sensor de ultrasonido como salida
GPIO.setup(echoPin, GPIO.IN)  # Pin del sensor de ultrasonido como entrada
GPIO.output(trigPin, False)  # Inicializar el pin del sensor de ultrasonido en bajo
time.sleep(2)  # Esperar 2 segundos para estabilizar el sensor
    
def distanceMonitor():
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


def modeSwitch():
    global modo
    global cm
    try:
        while True:
            print("Modo:", modo)
            if modo == "1":
                GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
                print("Fuente Encendida")
            elif modo == "2":
                if cm < 30:
                    GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
                    send_telemetry()
                    time.sleep(3)  # Tiempo que la bomba estará encendida (3 segundos)
                else:
                    GPIO.output(pinRele, GPIO.HIGH)  # Apagar la bomba    
            elif modo == "3":
                # Modo siempre apagado
                GPIO.output(pinRele, GPIO.HIGH)  # Apagar la bomba
                print("Fuente Apagada")       
            time.sleep(1)  # Tiempo de espera para cambiar de modo
    except KeyboardInterrupt:
        GPIO.cleanup()

def subscriber():
    client.loop_forever()
    

def send_telemetry():
    # Enviar señal a ThingsBoard cada vez que el gato bebe agua
    try:
        #print("Enviando telemetría")
        client.publish("v1/devices/me/telemetry", "{agua:1}")
    except Exception as e:
        print("Error de conexión:", e)

if __name__ == '__main__':
    try:
        t1 = threading.Thread(target=distanceMonitor, name='Distance Monitor')
        t2 = threading.Thread(target=subscriber, name='Subscriber')
        t3 = threading.Thread(target=modeSwitch, name='Mode Switch')
    
        t1.start()
        t2.start()
        t3.start()
    
        t1.join()
        t2.join()
        t3.join()
    except KeyboardInterrupt:
        GPIO.cleanup()



