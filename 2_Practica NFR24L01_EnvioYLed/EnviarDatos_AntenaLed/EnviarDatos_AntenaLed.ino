// --- TRANSMISOR ESP32 ---
// Envia 'mensaje=1' repetidamente mientras el boton está PRESIONADO (LOW)

#include <SPI.h>
#include <RF24.h>

#define CE_PIN   4
#define CSN_PIN  5
#define BOTON   14   // Boton a GND, entrada con pull-up

// SPI VSPI: SCK=18, MISO=19, MOSI=23, SS=5
RF24 radio(CE_PIN, CSN_PIN);

// Dirección de 5 bytes (RF24 usa 5 bytes efectivos)
const byte direccion[6] = "00001";

void setup() {
  Serial.begin(115200);
  delay(200);

  pinMode(BOTON, INPUT_PULLUP);

  // Inicializa SPI en ESP32 con pines explícitos
  SPI.begin(18, 19, 23, 5);

  Serial.println("Iniciando TRANSMISOR...");
  if (!radio.begin()) {
    Serial.println("ERROR: NRF24 no detectado en TX");
    while (1);
  }
  Serial.println("NRF24 OK (TX)");

  // Configuración de radio (igual que en RX)
  radio.setChannel(13);              // mismo canal en TX/RX
  radio.setPALevel(RF24_PA_LOW);     // ajusta si hace falta alcance
  radio.setDataRate(RF24_250KBPS);   // robustez
  // radio.setRetries(5, 15);        // (opcional) reintentos/espaciado

  radio.openWritingPipe(direccion);
  radio.stopListening();             // Modo TX

  Serial.println("TX listo. Presiona el boton para transmitir...");
}

void loop() {
  int estado = digitalRead(BOTON);

  if (estado == LOW) { // activo
    int mensaje = 1;
    bool ok = radio.write(&mensaje, sizeof(mensaje));
    if (ok) {
      Serial.println("TX: paquete enviado (1)");
    } else {
      Serial.println("TX: ERROR al enviar");
    }
    delay(35); // periodo corto para que el RX mantenga el LED encendido
  } else {
    // No enviamos nada; el RX apagará el LED tras el timeout
    delay(10);
  }
}