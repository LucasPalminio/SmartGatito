//#include <Adafruit_LiquidCrystal.h>

//Adafruit_LiquidCrystal lcd_1(0);
const int pingPin = A0; // Trigger Pin of Ultrasonic Sensor
const int echoPin = A1; // Echo Pin of Ultrasonic Sensor
const int pinOut = 6;
const double r2 = 0.2809; //Radio del estanque en metros al cuadrado
const double pi = 3.1415926535897932384626433832795;
double v = 0;
void setup() {
   Serial.begin(9600); // Starting Serial Terminal
   //lcd_1.begin(16, 2);
   //lcd_1.setBacklight(1);
   pinMode(6, OUTPUT);
   
}

void loop() {
   //lcd_1.setCursor(0, 0);
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
   //v = 1000-h*pi*r2*1000;
   // lcd_1.print(v);
   //lcd_1.print("L               ");

  if(cm>30){
    //lcd_1.setCursor(0, 1);
    //lcd_1.print("Gatito Cerca         ");
    //Apagar Bomba
     digitalWrite(pinOut, HIGH);
  }else{
    //lcd_1.setCursor(0, 1);
    //lcd_1.print("Gatito Lejo         ");
    //Prender Bomba
     digitalWrite(pinOut, LOW);
  }
    delay(100);

  
}

long microsecondsToInches(long microseconds) {
   return microseconds / 74 / 2;
}

long microsecondsToCentimeters(long microseconds) {
   return microseconds / 29 / 2;
}