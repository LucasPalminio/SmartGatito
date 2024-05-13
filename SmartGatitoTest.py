import RPi.GPIO as GPIO
import time
import requests
import paho.mqtt.client as mqtt

# Definición de pines
trigPin = 24  # Pin trigger del sensor ultrasónico (GPIO18)
echoPin = 23  # Pin echo del sensor ultrasónico (GPIO16)
pinRele = 14   # Pin para controlar el relé (GPIO8)

# Variables
modo = 2  # Modo inicial
agua = 0  # Contador de veces que el gato bebe agua
# Configuración MQTT
broker_address = "mqtt.thingsboard.cloud"
port = 1883 
client = mqtt.Client("30vte5orp3pywd6get3n")  # Crear nuevo objeto de instancia
client.username_pw_set("emzn7leosagnh376l84e", "ouokpwl7dyfo0xdv1pwn")  # Configurar usuario y contraseña
client.connect(broker_address, port)  # Conectar al broker
def setup():
    GPIO.setmode(GPIO.BCM)  # Configuración de numeración de pines
    GPIO.setup(pinRele, GPIO.OUT)  # Pin del relé como salida
    GPIO.setup(trigPin, GPIO.OUT)  # Pin del sensor de ultrasonido como salida
    GPIO.setup(echoPin, GPIO.IN)  # Pin del sensor de ultrasonido como entrada
    GPIO.output(trigPin, False)  # Inicializar el pin del sensor de ultrasonido en bajo
    time.sleep(2)  # Esperar 2 segundos para estabilizar el sensor
    
    

def loop():
    global modo
    global contador_agua
    # Ejecución del modo actual
    if modo == 1:
        # Modo siempre encendido
        GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
        print("Fuente Encendida")
    elif modo == 2:
        print("midiendo distancia")
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
        print("Distancia:", cm, "cm")
        if cm < 30:
            print("Gatito Cerca")
            GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
            agua = 1  # Incrementar el contador de veces que el gato bebe agua
            send_telemetry(agua)
            time.sleep(3)  # Tiempo que la bomba estará encendida (8 segundos
        else:
            print("Gatito Lejos")
            GPIO.output(pinRele, GPIO.HIGH)  # Apagar la bomba
            agua = 0  # Reiniciar el contador de veces que el gato bebe agua
            send_telemetry(agua)
        time.sleep(0.1)  # Retardo para estabilidad
    elif modo == 3:
        # Modo siempre apagado
        GPIO.output(pinRele, GPIO.HIGH)  # Apagar la bomba
        print("Fuente Apagada")
    time.sleep(1)  # Retardo para estabilidad

def send_telemetry(agua):
    # Enviar el contador de veces que el gato bebe agua a ThingsBoard
    try:
        client.publish("v1/devices/me/telemetry", "{agua:"+str(agua)+"}")
    except Exception as e:
        print("Error de conexión:", e)

if __name__ == '__main__':
    try:
        setup()

        while True:
            loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
