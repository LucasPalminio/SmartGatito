import RPi.GPIO as GPIO
import time

# Definición de pines
pingPin = 17  # Pin de disparo del sensor ultrasónico (GPIO17)
echoPin = 18  # Pin de eco del sensor ultrasónico (GPIO18)
pinRele = 4   # Pin para controlar el relé (GPIO4)
button = 3    # Pin para el botón de cambio de modo (GPIO3)

# Variables
modo = 2  # Modo inicial

def setup():
    GPIO.setmode(GPIO.BCM)  # Configuración de numeración de pines
    GPIO.setup(pinRele, GPIO.OUT)  # Pin del relé como salida
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Pin del botón como entrada

def loop():
    global modo
    # Lectura del estado del botón
    estadoBoton = GPIO.input(button)

    # Cambio de modo al presionar el botón
    if estadoBoton == GPIO.HIGH:
        modo += 1
        if modo > 3:
            modo = 1  # Reinicio del ciclo
        print("Nuevo modo:", modo)
        time.sleep(0.5)  # Retardo para evitar rebotes

    # Ejecución del modo actual
    if modo == 1:
        # Modo siempre encendido
        GPIO.output(pinRele, GPIO.LOW)  # Encender la bomba
        print("Fuente Encendida")
    elif modo == 2:
        # Modo dependiendo de la medición del ultrasonido
        GPIO.setup(pingPin, GPIO.OUT)  # Establecer pin de disparo como salida
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

def microsecondsToCentimeters(microseconds):
    return microseconds / 29 / 2

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
