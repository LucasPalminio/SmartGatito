import processing.serial.*;

Serial myPort;  // Create object from Serial class
String val;     // Data received from the serial port

void setup() {
  String portName = Serial.list()[1];
  myPort = new Serial(this, portName, 9600);
  size(400, 400);
}

void draw() {
  if (myPort.available() <= 0) {
    //println("PUERTO NO DISPONIBLE");
    return;   
  }
  
  val = myPort.readStringUntil('\n');         
  println(val); 
  
  if (val != null) {
    val = val.trim(); // Elimina espacios en blanco al principio y al final del mensaje
    switch (val) {
      case "Fuente Encendida":
        // Acciones cuando la fuente está encendida
        println("La fuente de agua para gatos está encendida.");
        break;
      case "Gatito Cerca":
        // Acciones cuando el gato está cerca
        println("El gatito está cerca.");
        break;
      case "Gatito Lejos":
        // Acciones cuando el gato está lejos
        println("El gatito está lejos.");
        break;
      case "Fuente Apagada":
        // Acciones cuando la fuente está apagada
        println("La fuente de agua para gatos está apagada.");
        break;
      default:
        // Acciones por defecto si se recibe un mensaje no reconocido
        println("Mensaje no reconocido: " + val);
        break;
    }
  }
}
