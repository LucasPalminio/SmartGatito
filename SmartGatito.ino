#include <Adafruit_LiquidCrystal.h>

Adafruit_LiquidCrystal lcd_1(0);
const int pingPin = A0; // Trigger Pin of Ultrasonic Sensor
const int echoPin = A1; // Echo Pin of Ultrasonic Sensor
const int pinOut = 6;
byte modo = 1; // Variable para almacenar el modo actual

void setup() {
   Serial.begin(9600); // Starting Serial Terminal
   lcd_1.begin(16, 2);
   lcd_1.setBacklight(1);
   pinMode(6, OUTPUT);
   pinMode(2, INPUT_PULLUP); // Botón conectado al pin 2
}

void loop() {
  // Lectura del estado del botón
  byte estadoBoton = digitalRead(2);

  // Cambiar el modo al presionar el botón
  if (estadoBoton == HIGH) {
    modo++;
    if (modo > 3) modo = 1; // Se reinicia el ciclo
    Serial.println("Nuevo modo:");
    Serial.println(modo);
    delay(500);
  }

  // Ejecutar el modo correspondiente
  switch (modo) {
    case 1:
      // Modo siempre encendido
      digitalWrite(pinOut, LOW); // Encender el LED
      lcd_1.setCursor(0, 0);
      lcd_1.print("Fuente Apagada         ");
      break;
    case 2:
      // Modo dependiendo de la medición del ultrasonido
      long duration, inches;
      double cm;
      lcd_1.setCursor(0, 0);
      pinMode(pingPin, OUTPUT);
      digitalWrite(pingPin, LOW);
      delayMicroseconds(2);
      digitalWrite(pingPin, HIGH);
      delayMicroseconds(10);
      digitalWrite(pingPin, LOW);
      pinMode(echoPin, INPUT);
      duration = pulseIn(echoPin, HIGH);
      cm = microsecondsToCentimeters(duration);
      if (cm < 30) {
        lcd_1.setCursor(0, 0);
        lcd_1.print("Gatito Cerca         ");
        digitalWrite(pinOut, HIGH); // Apagar Bomba
      } else {
        lcd_1.setCursor(0, 0);
        lcd_1.print("Gatito Lejos         ");
        digitalWrite(pinOut, LOW); // Prender Bomba
      }
      delay(100);
      break;
    case 3:
      // Modo LED apagado
      digitalWrite(pinOut, HIGH); // Apagar el LED
      lcd_1.setCursor(0, 0);
      lcd_1.print("Fuente Encendida         ");
      break;
  }
}

long microsecondsToCentimeters(long microseconds) {
   return microseconds / 29 / 2;
}
