import processing.serial.*;
import gifAnimation.*;//https://github.com/extrapixel/gif-animation

Serial myPort;  // Create object from Serial class
String val;     // Data received from the serial port

Gif gatoFelizGif, gatoTristeGif, encedidoGif, apagadoGif;

void setup() {
  String portName = Serial.list()[1];
  myPort = new Serial(this, portName, 9600);

  gatoFelizGif = new Gif(this, "resources/happy-cat.gif"); 
  gatoTristeGif = new Gif(this, "resources/sad-cat.gif");
  encedidoGif = new Gif(this, "resources/cataratas.gif");
  apagadoGif = new Gif(this, "resources/desierto.gif");
  
  gatoFelizGif.play();
  gatoTristeGif.play();
  encedidoGif.play();
  apagadoGif.play();
  
  size(400, 400);
}

void draw() {
  limpiarPantalla();
  if (myPort.available() > 0 ) {
    //println("PUERTO NO DISPONIBLE");      
    val = myPort.readStringUntil('\n');         
    println(val); 
  }

  
  if (val != null) {
    val = val.trim(); // Elimina espacios en blanco al principio y al final del mensaje
    switch (val) {
      case "Fuente Encendida":
        dibujarFuenteEncendida();
        // Acciones cuando la fuente está encendida
        println("La fuente de agua para gatos está encendida.");
        break;
      case "Gatito Cerca":
        dibujarGatoFeliz();
        // Acciones cuando el gato está cerca
        println("El gatito está cerca.");
        break;
      case "Gatito Lejos":
        dibujarGatoTriste();
        // Acciones cuando el gato está lejos
        println("El gatito está lejos.");
        break;
      case "Fuente Apagada":
        dibujarFuenteApagada();
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

// Método para dibujar un gato feliz bebiendo agua
void dibujarGatoFeliz() {
  // Dibuja un fondo arcoiris
  for (int y = 0; y < height; y++) {
    for (int x = 0; x < width; x++) {
      color c = color(map(x, 0, width, 0, 255), map(y, 0, height, 0, 255), 255);
      set(x, y, c);
    }
  }
  //gatoFelizGif.play();
  image(gatoFelizGif, 0, 0, width, height);
  mostrarMensaje("El gatito está bebiendo agua.");
//image(gato_feliz, 0, 0, width, height);  

}

void dibujarGatoTriste(){
    background(180); // Color de fondo gris claro    
    image(gatoTristeGif, 0, 0, width, height);
    mostrarMensaje("El gatito no está bebiendo agua.");
}

void dibujarFuenteEncendida(){
  background(180); // Color de fondo gris claro    
  image(encedidoGif, 0, 0, width, height);
  mostrarMensaje("La fuente de agua para gatos está encendida.");
}
void dibujarFuenteApagada(){
  background(180); // Color de fondo gris claro    
  image(apagadoGif, 0, 0, width, height);
  mostrarMensaje("La fuente de agua para gatos está apagada.");
}
// Método para mostrar un mensaje en el lienzo
void mostrarMensaje(String mensaje) {
  fill(random(255),random(255),random(255)); // Color negro
  textSize(20); // Tamaño del texto
  textAlign(CENTER, CENTER); // Alineación del texto
  text(mensaje, width/2, height - 50); // Muestra el mensaje centrado en la parte inferior del lienzo
}

void limpiarPantalla() {
  background(255);
}
