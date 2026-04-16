/*
 * PROYECTO: CONTROL DE ACCESO en base de datos CON NFC/RFID USANDO ESP32 Y MÓDULO PN532
 * Conexiones: PN532 SDA - GPIO 21 y PN532 SCL - GPIO 22
 */

#include <Wire.h>
#include <Adafruit_PN532.h>

// Definir pines I2C para ESP32
#define SDA_PIN 21
#define SCL_PIN 22

// Inicializar el objeto nfc usando I2C
Adafruit_PN532 nfc(SDA_PIN, SCL_PIN);

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n================================");
  Serial.println("SISTEMA NFC - LIBRERIA ADAFRUIT");
  Serial.println("================================");

  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.print("No se encontró el módulo PN532");
    while (1); // Detener si no hay módulo
  }

  // Configurar para leer tags RF
  nfc.SAMConfig();
  Serial.println("Esperando tarjeta...");
}

void loop() {
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer para el UID
  uint8_t uidLength;                        // Longitud del UID (4 o 7 bytes)

  // Intentar leer una tarjeta
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {
    Serial.println("\n========== TARJETA DETECTADA ==========");
    
    // 1. HEXADECIMAL
    Serial.print("UID HEX: ");
    nfc.PrintHex(uid, uidLength);

    // 2. DECIMAL
    Serial.print("UID DECIMAL: ");
    for (uint8_t i = 0; i < uidLength; i++) {
      Serial.print(uid[i], DEC);
      if (i < uidLength - 1) Serial.print(":");
    }
    Serial.println();

    // 3. BINARIO
    Serial.print("UID BINARIO: ");
    for (uint8_t i = 0; i < uidLength; i++) {
      imprimirBinario(uid[i]);
      if (i < uidLength - 1) Serial.print(":");
    }
    Serial.println();

    // 4. CONCATENADO (Para tu Base de Datos)
    Serial.print("UID CONCATENADO: ");
    for (uint8_t i = 0; i < uidLength; i++) {
      if (uid[i] < 0x10) Serial.print("0");
      Serial.print(uid[i], HEX);
    }
    Serial.println("\n======================================\n");

    delay(1000); // Evitar lecturas repetidas rápidas
  }
}

// Función para imprimir en binario
void imprimirBinario(uint8_t valor) {
  for (int i = 7; i >= 0; i--) {
    Serial.print((valor >> i) & 1);
  }
}