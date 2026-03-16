// --- ESP32 (RX) ---
// Recibe distancia (float) por NRF24L01 y la muestra por Serial
#include <SPI.h>
#include <RF24.h>

RF24 radio(4,5); // CE, CSN
const byte direccion[6] = "00001"; // Debe igualar al TX
float distanciaRecibida;

void setup() {
  Serial.begin(115200);

  // (Opcional) asegura pines de VSPI explícitos en algunas placas
  // SPI.begin(18, 19, 23, 5); // SCK, MISO, MOSI, SS

  if (!radio.begin()) {
    Serial.println("NRF24L01 no detectado");
    while(1);
  }

  radio.openReadingPipe(0, direccion); // abre pipe 0
  radio.setChannel(112);               // mismo canal que el TX
  radio.setPALevel(RF24_PA_LOW);
  radio.startListening();              // modo recepción

  Serial.println("Receptor listo, esperando datos...");
}

void loop() {
  if (radio.available()) {
    radio.read(&distanciaRecibida, sizeof(distanciaRecibida));
    Serial.print("Distancia recibida: ");
    Serial.print(distanciaRecibida);
    Serial.println(" cm");
  }
}
