#include <Wire.h>
#include <Adafruit_PN532.h>

// ------------------ Pines I2C (ESP32) ------------------
// En ESP32 genérico: SDA=21 y SCL=22 suelen ser los más usados.  (Se pueden cambiar)
#define SDA_PIN 21
#define SCL_PIN 22

// OJO: Tu proyecto lo trae así. Si a ti te compila y funciona, lo dejamos igual.
Adafruit_PN532 nfc(SDA_PIN, SCL_PIN);

// --------- Funciones simples para imprimir el UID ---------
void imprimirHex(const uint8_t *uid, uint8_t len) {
  Serial.print("HEX (Base 16): ");
  for (uint8_t i = 0; i < len; i++) {
    if (uid[i] < 0x10) Serial.print("0");   // cero a la izquierda
    Serial.print(uid[i], HEX);
    if (i < len - 1) Serial.print(":");
  }
  Serial.println();
}

void imprimirDec(const uint8_t *uid, uint8_t len) {
  Serial.print("DEC (Base 10): ");
  for (uint8_t i = 0; i < len; i++) {
    Serial.print(uid[i], DEC);
    if (i < len - 1) Serial.print("-");
  }
  Serial.println();
}

void imprimirBin(const uint8_t *uid, uint8_t len) {
  Serial.print("BIN (Base  2): ");
  for (uint8_t i = 0; i < len; i++) {
    // siempre 8 bits por byte
    for (int b = 7; b >= 0; b--) {
      Serial.print((uid[i] >> b) & 1);
    }
    if (i < len - 1) Serial.print(" ");
  }
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  delay(50);

  Serial.println("Iniciando PN532-");

  // Iniciar I2C con los pines elegidos (en ESP32 se recomienda hacerlo explícito)
  Wire.begin(SDA_PIN, SCL_PIN);

  nfc.begin();

  // Verifica que el módulo esté respondiendo
  uint32_t version = nfc.getFirmwareVersion();
  if (!version) {
    Serial.println("ERROR: PN532 no encontrado. Revisa conexiones");
    while (1) { delay(10); }
  }

  // Configura el módulo para lectura (SAM)
  nfc.SAMConfig();

  Serial.println("PN532 listo. Acerca una tarjeta...\n");
}

void loop() {
  uint8_t uid[7];     // buffer típico (UID hasta 7 bytes en varios casos)
  uint8_t uidLen = 0;

  // Lee una tarjeta tipo ISO14443A (MIFARE/NFC-A).
  // El último parámetro es timeout (ms). Si no detecta, regresa false.
  bool encontrada = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLen, 1000);

  if (encontrada) {
    
    Serial.println("  TARJETA DETECTADA");
    

    // Aquí está lo importante: mismo UID, tres representaciones
    imprimirHex(uid, uidLen);   // Base 16
    imprimirDec(uid, uidLen);   // Base 10
    imprimirBin(uid, uidLen);   // Base 2

    Serial.println("\n");

    delay(2000);  // pausa para que no se imprima mil veces la misma tarjeta
  }
}