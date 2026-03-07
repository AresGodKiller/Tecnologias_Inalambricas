#include <SPI.h>
#include <RF24.h>

#define CE_PIN 4
#define CSN_PIN 5

RF24 radio(CE_PIN, CSN_PIN);

const byte direccion[6] = "00001";

void setup() {
  Serial.begin(115200);
  if (!radio.begin()) {
    Serial.println("NRF24 no detectado o no esta bien conectado");
    while (1);
  }

  radio.setChannel(67);          // Mismo canal
  radio.setPALevel(RF24_PA_LOW); // Ajustable según alcance/ruido
  // radio.setDataRate(RF24_250KBPS); // Opcional: mejor alcance

  radio.openReadingPipe(0, direccion);
  radio.startListening();        // Modo RX
  Serial.println("RX listo. Esperando mensajes...");
}

void loop() {
  if (radio.available()) {
    char texto[32] = {0}; // payload max 32 bytes
    radio.read(&texto, sizeof(texto));
    Serial.print("Recibido el mensaje: ");
    Serial.println(texto);
  }
}
``