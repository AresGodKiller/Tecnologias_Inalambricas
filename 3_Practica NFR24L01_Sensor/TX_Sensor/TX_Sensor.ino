// --- Arduino UNO (TX) ---
// Lee distancia del HC-SR04 y la envía como float por NRF24L01
#include <RF24.h>

RF24 radio(9,10); // CE, CSN
const byte direccion[6] = "00001"; // Pipe de escritura

#define TRIG 6
#define ECHO 7

long duracion;     // tiempo en microsegundos del pulso ECHO
float distancia;   // distancia en cm

void setup() {
  Serial.begin(9600);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  if (!radio.begin()) {
    Serial.println("NRF24L01 no detectado");
    while(1); // detente si no hay radio
  }

  radio.openWritingPipe(direccion);   // establece destino
  radio.setChannel(112);               // canal 112 (debe coincidir con RX)
  radio.setPALevel(RF24_PA_LOW);       // potencia baja para pruebas de mesa
  radio.stopListening();               // modo transmisión

  Serial.println("Transmisor listo con sensor ultrasonico");
}

void loop() {
  // Disparo ultrasónico
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  duracion = pulseIn(ECHO, HIGH);           // mide ancho del pulso
  distancia = duracion * 0.034 / 2.0;       // convierte a cm (ida y vuelta)

  bool ok = radio.write(&distancia, sizeof(distancia));
  if (ok) {
    Serial.print("Distancia enviada: ");
    Serial.print(distancia); Serial.println(" cm");
  } else {
    Serial.println("Error al enviar");
  }

  delay(1000); // periodo ~1 s
}
