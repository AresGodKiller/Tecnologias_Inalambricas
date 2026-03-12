// --- RECEPTOR ESP32 ---
// Enciende LED mientras lleguen paquetes con 'mensaje=1'.
// Si no llegan paquetes por 'TIMEOUT_MS', apaga el LED.

#include <SPI.h>
#include <RF24.h>

#define CE_PIN   4
#define CSN_PIN  5
#define LED_PIN  2

RF24 radio(CE_PIN, CSN_PIN);
const byte direccion[6] = "00001";

const unsigned long TIMEOUT_MS = 200;  // ventana sin paquetes para apagar LED
unsigned long ultimoPaqueteMs = 0;

void setup() {
  Serial.begin(115200);
  delay(200);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  SPI.begin(18, 19, 23, 5);

  Serial.println("Iniciando RECEPTOR...");
  if (!radio.begin()) {
    Serial.println("ERROR: NRF24 no detectado en RX");
    while (1);
  }
  Serial.println("NRF24 OK (RX)");

  radio.setChannel(13);
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);

  radio.openReadingPipe(0, direccion);
  radio.startListening();

  Serial.println("RX listo. Esperando paquetes...");
}

void loop() {
  // 1) Revisión de paquetes disponibles
  while (radio.available()) {
    int mensaje = 0;
    radio.read(&mensaje, sizeof(mensaje));
    Serial.print("RX: paquete recibido -> ");
    Serial.println(mensaje);

    if (mensaje == 1) {
      digitalWrite(LED_PIN, HIGH);        // enciende LED
      ultimoPaqueteMs = millis();         // reinicia ventana de tiempo
    }
  }

  // 2) Control de timeout: si pasa el tiempo sin paquetes, apaga LED
  if (digitalRead(LED_PIN) == HIGH) {
    if (millis() - ultimoPaqueteMs > TIMEOUT_MS) {
      digitalWrite(LED_PIN, LOW);
      Serial.println("RX: timeout sin paquetes, LED apagado");
    }
  }
}