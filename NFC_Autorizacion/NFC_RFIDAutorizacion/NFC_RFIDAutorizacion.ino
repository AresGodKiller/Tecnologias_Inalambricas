#include <Wire.h>
#include <Adafruit_PN532.h>

// ------------------ Pines I2C (ESP32) ------------------
#define SDA_PIN 21
#define SCL_PIN 22

Adafruit_PN532 nfc(SDA_PIN, SCL_PIN);

// UID autorizado (ejemplo). Sustituir por el UID real de la tarjeta válida.
uint8_t tarjetaAutorizada[4] = {0x3D, 0x3C, 0xFD, 0x06};

// Simulación de "maquinaria": LED/relay. (En muchas placas ESP32 es GPIO2)
const int PIN_MAQUINA = 2;

void setup() {
  Serial.begin(115200);

  // Inicializa I2C con los pines elegidos
  Wire.begin(SDA_PIN, SCL_PIN);

  pinMode(PIN_MAQUINA, OUTPUT);
  digitalWrite(PIN_MAQUINA, LOW);

  nfc.begin();

  // Verifica que el PN532 responda
  uint32_t version = nfc.getFirmwareVersion();
  if (!version) {
    Serial.println("ERROR: PN532 no encontrado.");
    while (1) { delay(10); }
  }

  // Configuración para lectura de tarjetas
  nfc.SAMConfig();
  Serial.println("Listo. Acerca una tarjeta...\n");
}

void loop() {
  uint8_t uid[7];
  uint8_t uidLen = 0;

  // Lee tarjetas ISO14443A (NFC-A / MIFARE)
  bool encontrada = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLen, 1000);

  if (encontrada) {

    // -------- BASE 16 (HEX) --------
    Serial.print("HEX (Base 16): ");
    for (uint8_t i = 0; i < uidLen; i++) {
      if (uid[i] < 0x10) Serial.print("0");
      Serial.print(uid[i], HEX);
      if (i < uidLen - 1) Serial.print(":");
    }
    Serial.println();

    // -------- BASE 10 (DEC) --------
    Serial.print("DEC (Base 10): ");
    for (uint8_t i = 0; i < uidLen; i++) {
      Serial.print(uid[i], DEC);
      if (i < uidLen - 1) Serial.print("-");
    }
    Serial.println();

    // -------- BASE 2 (BIN) --------
    Serial.print("BIN (Base  2): ");
    for (uint8_t i = 0; i < uidLen; i++) {
      for (int b = 7; b >= 0; b--) {
        Serial.print((uid[i] >> b) & 1);
      }
      if (i < uidLen - 1) Serial.print(" ");
    }
    Serial.println();

    // -------- VALIDACIÓN --------
    bool autorizada = (uidLen == 4);
    for (uint8_t i = 0; i < 4 && autorizada; i++) {
      if (uid[i] != tarjetaAutorizada[i]) autorizada = false;
    }

    Serial.println();
    if (autorizada) {
      Serial.println("ACCESO CONCEDIDO");
      Serial.println("Simulación: MAQUINARIA ENCENDIDA");
      digitalWrite(PIN_MAQUINA, HIGH);
    } else {
      Serial.println("ACCESO DENEGADO");
      Serial.println("Simulación: MAQUINARIA APAGADA");
      digitalWrite(PIN_MAQUINA, LOW);
    }

    delay(2000);
  }
}

