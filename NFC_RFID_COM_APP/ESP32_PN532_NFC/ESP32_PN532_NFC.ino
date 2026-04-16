#include <Wire.h>              // Biblioteca I2C nativa de Arduino/ESP32
#include <Adafruit_PN532.h>    // Biblioteca del módulo PN532 de Adafruit

// PINES I2C para ESP32
// SDA → GPIO 21  |  SCL → GPIO 22

#define SDA_PIN 21
#define SCL_PIN 22

// Pin de salida: LED o relé que indica acceso concedido

#define PIN_SALIDA 2           // GPIO2 = LED integrado en la mayoría de ESP32

// Tiempo en ms que permanece activa la salida al leer tarjeta válida
#define TIEMPO_ACTIVACION 2000

// Instancia del objeto PN532 usando I2C
// Los parámetros IRQ y RESET se pasan como -1 si no se usan
Adafruit_PN532 nfc(SDA_PIN, SCL_PIN);


// TARJETAS AUTORIZADAS 

byte tarjetasAutorizadas[][7] = {
  {0x49, 0x1C, 0x33, 0x07, 0x00, 0x00, 0x00},  // Tarjeta 1
  {0x9D, 0x97, 0x24, 0x07, 0x00, 0x00, 0x00}  // Tarjeta 2
};
byte numTarjetasAutorizadas = 2; 

//  Convierte un arreglo de bytes a cadena en BASE 2
//  Cada byte se imprime como 8 bits con ceros a la izquierda
void uid_a_binario(uint8_t *uid, uint8_t longitud) {
  Serial.print("  Base  2 (BIN): ");
  for (uint8_t i = 0; i < longitud; i++) {
    for (int bit = 7; bit >= 0; bit--) {
      Serial.print((uid[i] >> bit) & 1);  // Extrae bit a bit de mayor a menor peso
    }
    if (i < longitud - 1) Serial.print(" ");  // Espacio entre bytes para legibilidad
  }
  Serial.println();
}

//  Función: uid_a_decimal
//  Convierte el UID completo a un número entero largo (Base 10)
//  Los bytes se concatenan: byte0 es el más significativo
void uid_a_decimal(uint8_t *uid, uint8_t longitud) {
  unsigned long valor = 0;
  for (uint8_t i = 0; i < longitud; i++) {
    valor = (valor << 8) | uid[i];  // Desplazamiento: cada byte ocupa 8 bits
  }
  Serial.print("  Base 10 (DEC): ");
  Serial.println(valor);            // Imprime el número en base decimal
}

//  Función: uid_a_hexadecimal
//  Imprime el UID byte a byte en Base 16 con formato 0xXX
void uid_a_hexadecimal(uint8_t *uid, uint8_t longitud) {
  Serial.print("  Base 16 (HEX): ");
  for (uint8_t i = 0; i < longitud; i++) {
    if (uid[i] < 0x10) Serial.print("0");  // Cero a la izquierda para valores < 16
    Serial.print(uid[i], HEX);             // Imprime el byte en hexadecimal
    if (i < longitud - 1) Serial.print(":");  // Separador estilo MAC address
  }
  Serial.println();
}

//  Función: verificar_acceso
//  Compara el UID leído contra la lista de autorizados
//  Retorna true si hay coincidencia, false en caso contrario
bool verificar_acceso(uint8_t *uid, uint8_t longitud) {
  for (byte t = 0; t < numTarjetasAutorizadas; t++) {
    bool coincide = true;
    for (byte b = 0; b < longitud; b++) {
      if (uid[b] != tarjetasAutorizadas[t][b]) {  // Compara byte a byte
        coincide = false;
        break;
      }
    }
    if (coincide) return true;  // UID encontrado en la lista
  }
  return false;  // No coincide con ninguna tarjeta registrada
}

//  Envía los datos de la tarjeta en formato JSON al puerto COM
//  Permite que aplicaciones externas (Python/Web) los lean
void enviar_json_serial(uint8_t *uid, uint8_t longitud, bool acceso) {

  // -- Construir HEX como string --
  String hexStr = "";
  for (uint8_t i = 0; i < longitud; i++) {
    if (uid[i] < 0x10) hexStr += "0";
    hexStr += String(uid[i], HEX);
    if (i < longitud - 1) hexStr += ":";
  }
  hexStr.toUpperCase();   // Letras mayúsculas para estandarizar

  // -- Construir DEC como número largo --
  unsigned long decVal = 0;
  for (uint8_t i = 0; i < longitud; i++) {
    decVal = (decVal << 8) | uid[i];
  }

  // -- Construir BIN como string --
  String binStr = "";
  for (uint8_t i = 0; i < longitud; i++) {
    for (int bit = 7; bit >= 0; bit--) {
      binStr += String((uid[i] >> bit) & 1);
    }
    if (i < longitud - 1) binStr += " ";
  }

  // -- Emitir JSON por Serial (puerto COM) --
  // Formato: {"hex":"XX:XX:XX:XX","dec":123456,"bin":"...","acceso":true}
  Serial.print("{\"hex\":\"");
  Serial.print(hexStr);
  Serial.print("\",\"dec\":");
  Serial.print(decVal);
  Serial.print(",\"bin\":\"");
  Serial.print(binStr);
  Serial.print("\",\"acceso\":");
  Serial.print(acceso ? "true" : "false");
  Serial.println("}");  // Salto de línea es el delimitador de trama
}

//  SETUP — Se ejecuta una sola vez al encender la ESP32
void setup() {
  // Inicia comunicación serial a 115200 baudios
  // Este valor debe coincidir en el lector Python y el Monitor Serial
  Serial.begin(115200);
  delay(100);

  // Configura el pin de salida (LED/relé)
  pinMode(PIN_SALIDA, OUTPUT);
  digitalWrite(PIN_SALIDA, LOW);

  Serial.println("  SISTEMA DE CONTROL DE ACCESO NFC/RFID");
  Serial.println("  ESP32 + Modulo PN532  (I2C)");
  // Inicia el módulo PN532
  nfc.begin();

  // Obtiene la versión del firmware del PN532
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    // Si no responde el módulo, se detiene el programa
    Serial.println("[ERROR] Modulo PN532 no detectado. Revisa conexiones.");
    while (1);  // Bucle infinito = detiene la ejecución
  }

  // Imprime datos del firmware para verificar la conexión correcta
  Serial.print("[OK] PN532 detectado. Chip: ");
  Serial.print((versiondata >> 24) & 0xFF, HEX);
  Serial.print("  Firmware: ");
  Serial.print((versiondata >> 16) & 0xFF, DEC);
  Serial.print(".");
  Serial.println((versiondata >> 8) & 0xFF, DEC);

  // Configura el PN532 para leer tarjetas ISO14443A (RFID/NFC Tipo A)
  nfc.SAMConfig();

  Serial.println("\n[LISTO] Acerca una tarjeta NFC o RFID al lector...\n");
}

//  LOOP — Se ejecuta continuamente
void loop() {
  uint8_t uid[7];       // Buffer para almacenar el UID (máx. 7 bytes para NTAG/Mifare)
  uint8_t uidLength;    // Longitud real del UID leído (4 bytes = RFID, 7 bytes = NFC)
  uint8_t atqa[2];      // Answer To Request Type A (identificador de tipo de tarjeta)
  uint8_t sak;          // Select Acknowledge (informa el tipo de tarjeta)

  // Espera activa hasta detectar una tarjeta ISO14443A
  // Tiempo de espera (timeout): 0 = no bloquea, 100 = 100 ms
  boolean success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A,
                                            uid,
                                            &uidLength);

  if (success) {
    
    Serial.println("[TARJETA DETECTADA]");
    Serial.print("  Longitud UID : ");
    Serial.print(uidLength, DEC);
    Serial.println(" bytes");

    // --- Mostrar UID en las tres bases numéricas ---
    uid_a_hexadecimal(uid, uidLength);   // Base 16
    uid_a_decimal(uid, uidLength);       // Base 10
    uid_a_binario(uid, uidLength);       // Base 2

    // --- Verificar si la tarjeta tiene acceso ---
    bool accesoConcedido = verificar_acceso(uid, uidLength);

    if (accesoConcedido) {
      Serial.println("  [ACCESO CONCEDIDO] Tarjeta autorizada.");
      digitalWrite(PIN_SALIDA, HIGH);         // Activa salida (abre cerradura/LED verde)
      delay(TIEMPO_ACTIVACION);               // Mantiene la salida activa
      digitalWrite(PIN_SALIDA, LOW);          // Desactiva la salida
    } else {
      Serial.println("  [ACCESO DENEGADO]  Tarjeta no registrada.");
      // Aquí puedes agregar un buzzer o LED rojo para indicar acceso denegado
    }

    // --- Enviar datos en formato JSON para el lector Python/Web ---
    enviar_json_serial(uid, uidLength, accesoConcedido);

    Serial.println("--------------------------------------------\n");

    // Espera a que la tarjeta se retire antes de volver a leer
    delay(1500);
  }
