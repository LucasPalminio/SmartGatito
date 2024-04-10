import processing.serial.*; // Importa la librería para comunicación serial
import gifAnimation.*;     // Importa la librería para manipulación de GIFs

Serial myPort;             // Objeto para comunicación serial
String val;                // Variable para almacenar los datos recibidos desde el puerto serial

Gif gatoFelizGif, gatoTristeGif, encedidoGif, apagadoGif; // Variables para almacenar los GIFs

void setup() {
  // Configuración inicial
  String portName = Serial.list()[1];  // Selecciona el nombre del puerto serial
  myPort = new Serial(this, portName, 9600); // Inicializa la comunicación serial

  // Carga los GIFs desde archivos
  gatoFelizGif = new Gif(this, "resources/Chipi-chipi-chapa-chapa.gif"); 
  gatoTristeGif = new Gif(this, "resources/sad-cat.gif");
  encedidoGif = new Gif(this, "resources/cataratas.gif");
  apagadoGif = new Gif(this, "resources/desierto.gif");
  
  // Reproduce los GIFs
  gatoFelizGif.play();
  gatoTristeGif.play();
  encedidoGif.play();
  apagadoGif.play();
  
  // Configura el tamaño de la ventana
  size(400, 400);
}

void draw() {
  // Verifica si hay datos disponibles en el puerto serial
  if (myPort.available() > 0 ) {
    val = myPort.readStringUntil('\n'); // Lee los datos del puerto serial hasta encontrar un salto de línea
    println(val); // Muestra los datos recibidos en la consola
  }

  // Procesa los datos recibidos
  if (val != null) {
    val = val.trim(); // Elimina espacios en blanco al principio y al final del mensaje
    switch (val) {
      case "Fuente Encendida":
        dibujarFuenteEncendida(); // Dibuja el GIF correspondiente
        println("La fuente de agua para gatos está encendida.");
        break;
      case "Gatito Cerca":
        dibujarGatoFeliz();
        println("El gatito está cerca.");
        break;
      case "Gatito Lejos":
        dibujarGatoTriste();
        println("El gatito está lejos.");
        break;
      case "Fuente Apagada":
        dibujarFuenteApagada();
        println("La fuente de agua para gatos está apagada.");
        break;
      default:
        println("Mensaje no reconocido: " + val); // Mensaje por defecto si el mensaje no es reconocido
        break;
    }
  }
}

// Dibuja el GIF de un gato feliz
void dibujarGatoFeliz() {
  image(gatoFelizGif, 0, 0, width, height);
  mostrarMensaje("El gatito está bebiendo agua.");
}

// Dibuja el GIF de un gato triste
void dibujarGatoTriste(){
    image(gatoTristeGif, 0, 0, width, height);
    mostrarMensaje("El gatito no está bebiendo agua.");
}

// Dibuja el GIF de una fuente encendida
void dibujarFuenteEncendida(){
  image(encedidoGif, 0, 0, width, height);
  mostrarMensaje("La fuente de agua para gatos está encendida.");
}

// Dibuja el GIF de una fuente apagada
void dibujarFuenteApagada(){
  image(apagadoGif, 0, 0, width, height);
  mostrarMensaje("La fuente de agua para gatos está apagada.");
}

// Muestra un mensaje en el lienzo
void mostrarMensaje(String mensaje) {
  fill(205,205,205); // Color del texto (blanco)
  textSize(20);      // Tamaño del texto
  textAlign(CENTER, CENTER); // Alineación del texto
  text(mensaje, width/2, height - 50); // Muestra el mensaje centrado en la parte inferior del lienzo
}
