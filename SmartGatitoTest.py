import RPi.GPIO as GPIO
import time
import requests

# Definición de pines
pingPin = 17  # Pin de disparo del sensor ultrasónico (GPIO17)
echoPin = 18  # Pin de eco del sensor ultrasónico (GPIO18)
pinRele = 4   # Pin para controlar el relé (GPIO4)

# Variables
modo = 3  # Modo inicial

def setup():
    GPIO.setmode(GPIO.BCM)  # Configuración de numeración de pines
    GPIO.setup(pinRele, GPIO.OUT)  # Pin del relé como salida
    GPIO.setup(pingPin, GPIO.OUT)  # Pin del sensor de ultrasonido como salida

def loop():
    global modo
    # Ejecución del modo actual
    if modo == 1:
        # Modo siempre encendido
        GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
        print("Fuente Encendida")
    elif modo == 2:
        # Modo dependiendo de la medición del ultrasonido
        GPIO.output(pingPin, GPIO.LOW)  # Enviar pulso corto
        time.sleep(0.000002)
        GPIO.output(pingPin, GPIO.HIGH)  # Enviar pulso largo
        time.sleep(0.00001)
        GPIO.output(pingPin, GPIO.LOW)  # Detener pulso
        GPIO.setup(echoPin, GPIO.IN)  # Establecer pin de eco como entrada
        start_time = time.time()
        stop_time = time.time()
        while GPIO.input(echoPin) == 0:
            start_time = time.time()
        while GPIO.input(echoPin) == 1:
            stop_time = time.time()
        duration = stop_time - start_time
        cm = microsecondsToCentimeters(duration * 1000000)  # Convertir a centímetros
        if cm < 30:
            print("Gatito Cerca")
            GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
        else:
            print("Gatito Lejos")
            GPIO.output(pinRele, GPIO.HIGH)  # Apagar la bomba
        time.sleep(0.1)  # Retardo para estabilidad
    elif modo == 3:
        # Modo siempre apagado
        GPIO.output(pinRele, GPIO.HIGH)  # Apagar la bomba
        print("Fuente Apagada")

def check_mode():
    global modo
    # Consultar ThingsBoard para obtener el modo actual
    url = 'http://thingsboard.cloud/api/v1/7mTCa4pj3NWSnJFZ9hlo/telemetry/mode'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            modo = int(response.json()['modo'])
            print("Modo actual:", modo)
        else:
            print("Error al obtener el modo:", response.text)
    except Exception as e:
        print("Error de conexión:", e)

def microsecondsToCentimeters(microseconds):
    return microseconds / 29 / 2

if __name__ == '__main__':
    try:
        setup()

        while True:
            check_mode()
            loop()
            time.sleep(1)  # Esperar un segundo entre cada iteración
    except KeyboardInterrupt:
        GPIO.cleanup()
