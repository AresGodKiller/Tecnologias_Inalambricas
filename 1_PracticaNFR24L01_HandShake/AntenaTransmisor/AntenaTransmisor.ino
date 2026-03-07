#include <SPI.h>
#include <RF24.h>

#define CE_PIN 4
#define CSN_PIN 5

RF24 radio(CE_PIN, CSN_PIN);

// Dirección de 5 bytes + '\0' en tu ejemplo; RF24 usa 5 bytes efectivos.
// Mantén la misma entre TX y RX.
const byte direccion[6] = "00001";

void setup() {
  Serial.begin(115200);
  if (!radio.begin()) {
    Serial.println("NRF24 no detectado o no esta bien conectado");
    while (1);
  }

  radio.setChannel(67);         // Canal 67 (debe coincidir con el RX)
  radio.setPALevel(RF24_PA_LOW); // Potencia baja (ajusta a MEDIUM/HIGH si hay fallos)
  // radio.setDataRate(RF24_250KBPS); // Opcional: mejor alcance/fiabilidad

  radio.openWritingPipe(direccion);
  radio.stopListening();         // Modo TX
}

void loop() {
  const char texto[] = "Hola";
  bool ok = radio.write(&texto, sizeof(texto));
  if (ok) {
    Serial.println("Mensaje enviado");
  } else {
    Serial.println("Error al enviar");
  }
  delay(1000); // 1 segundo
}