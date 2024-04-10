// Definición de pines
const int pingPin = A0; // Pin de disparo del sensor ultrasónico
const int echoPin = A1; // Pin de eco del sensor ultrasónico
const int pinRele = 7;  // Pin para controlar el relé
const int button = 2;   // Pin para el botón de cambio de modo

// Variables
byte modo = 2; // Modo inicial

void setup() {
   Serial.begin(9600); // Inicialización del puerto serial

   // Configuración de pines
   pinMode(pinRele, OUTPUT); // Pin del relé como salida
   pinMode(button, INPUT);   // Pin del botón como entrada
}

void loop() {
  // Lectura del estado del botón
  byte estadoBoton = digitalRead(button);

  // Cambio de modo al presionar el botón
  if (estadoBoton == HIGH) {
    modo++;
    if (modo > 3) modo = 1; // Reinicio del ciclo
    Serial.print("Nuevo modo:");
    Serial.println(modo);
    delay(500); // Retardo para evitar rebotes
  }

  // Ejecución del modo actual
  switch (modo) {
    case 1:
      // Modo siempre encendido
      digitalWrite(pinRele, LOW); // Encender la bomba
      Serial.println("Fuente Encendida");
      break;
    case 2:
      // Modo dependiendo de la medición del ultrasonido
      long duration, inches;
      double cm;
      pinMode(pingPin, OUTPUT);     // Establecer pin de disparo como salida
      digitalWrite(pingPin, LOW);   // Enviar pulso corto
      delayMicroseconds(2);
      digitalWrite(pingPin, HIGH);  // Enviar pulso largo
      delayMicroseconds(10);
      digitalWrite(pingPin, LOW);   // Detener pulso
      pinMode(echoPin, INPUT);      // Establecer pin de eco como entrada
      duration = pulseIn(echoPin, HIGH); // Medir duración del eco
      cm = microsecondsToCentimeters(duration); // Convertir a centímetros
      if (cm < 30) {
        Serial.println("Gatito Cerca");
        digitalWrite(pinRele, LOW); // Encender la bomba
      } else {
        Serial.println("Gatito Lejos");
        digitalWrite(pinRele, HIGH); // Apagar la bomba
      }
      delay(100); // Retardo para estabilidad
      break;
    case 3:
      // Modo siempre apagado
      digitalWrite(pinRele, HIGH); // Apagar la bomba
      Serial.println("Fuente Apagada");
      break;
  }
}

// Función para convertir microsegundos a centímetros
long microsecondsToCentimeters(long microseconds) {
   return microseconds / 29 / 2;
}
