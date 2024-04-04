const int pingPin = A0; // Trigger Pin of Ultrasonic Sensor
const int echoPin = A1; // Echo Pin of Ultrasonic Sensor
const int pinOut = 6;
byte modo = 1; // Variable para almacenar el modo actual
const int button = 2;

void setup() {
   Serial.begin(9600); // Starting Serial Terminal

   pinMode(6, OUTPUT);
   pinMode(button, INPUT); // Botón conectado al pin 2
}

void loop() {
  // Lectura del estado del botón
  byte estadoBoton = digitalRead(button);

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
      digitalWrite(pinOut, HIGH); // Encender la Bomba
     Serial.println("Fuente Apagada");
      
      break;
    case 2:
      // Modo dependiendo de la medición del ultrasonido
      long duration, inches;
      double cm;
      pinMode(pingPin, OUTPUT);
      digitalWrite(pingPin, LOW);
      delayMicroseconds(2);
      digitalWrite(pingPin, HIGH);
      delayMicroseconds(10);
      digitalWrite(pingPin, LOW);
      pinMode(echoPin, INPUT);
      duration = pulseIn(echoPin, HIGH);
      cm = microsecondsToCentimeters(duration);
      delay(3000);
      if (cm < 30) {
        Serial.println("Gatito Cerca");
        digitalWrite(pinOut, LOW); // Prender Bomba
        delay(10000);
      } else {
        Serial.println("Gatito Lejos");
        digitalWrite(pinOut, HIGH); // Apagar Bomba
      }
      delay(100);
      break;
    case 3:
      // Modo LED apagado
      digitalWrite(pinOut, LOW); // Apagar la Bomba
      
      Serial.println("Fuente Encendida");
      break;
  }
}

long microsecondsToCentimeters(long microseconds) {
   return microseconds / 29 / 2;
}
