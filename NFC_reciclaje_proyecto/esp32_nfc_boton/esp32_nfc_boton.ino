#include <Wire.h>
#include <Adafruit_PN532.h>

// Pines que se usaron entre el boton y el nfc 
#define PIN_BOTON   25      
#define PN532_SDA   21
#define PN532_SCL   22

// PN532 por I2C
Adafruit_PN532 nfc(PN532_SDA, PN532_SCL);

//  Antirrebote boton
unsigned long ultimoPresionado = 0;
const unsigned long DEBOUNCE_MS = 300;

//  Antilectura repetida nfc
String ultimoUID       = "";
unsigned long tsUltimoUID = 0;
const unsigned long COOLDOWN_NFC_MS = 2500;  // ms entre lecturas del mismo UID


void setup() {
  Serial.begin(115200);
  delay(200);

  // Botón con pull-up interno → LOW cuando está presionado
  pinMode(PIN_BOTON, INPUT_PULLUP);

  // Iniciar PN532
  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.println("ERROR:PN532 no encontrado");
    while (1) delay(500);  // Detener si no hay lector
  }

  nfc.SAMConfig();  // Modo normal
  Serial.println("LISTO");
}


void loop() {
  leerNFC();
  leerBoton();
}

void leerNFC() {
  uint8_t uid[7];
  uint8_t uidLen = 0;

  // Espera no bloqueante: timeout 100ms para no trabar el loop
  bool encontrado = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLen, 100);

  if (!encontrado || uidLen == 0) return;

  // Construir UID como string hexadecimal concatenado (sin espacios, mayúsculas)
  String uidStr = "";
  for (uint8_t i = 0; i < uidLen; i++) {
    if (uid[i] < 0x10) uidStr += "0";
    uidStr += String(uid[i], HEX);
  }
  uidStr.toUpperCase();

  // Cooldown: ignorar si es el mismo UID dentro de los últimos COOLDOWN_NFC_MS
  unsigned long ahora = millis();
  if (uidStr == ultimoUID && (ahora - tsUltimoUID) < COOLDOWN_NFC_MS) return;

  ultimoUID    = uidStr;
  tsUltimoUID  = ahora;

  Serial.print("UID CONCATENADO:");
  Serial.println(uidStr);
}


void leerBoton() {
  if (digitalRead(PIN_BOTON) == LOW) {
    unsigned long ahora = millis();
    if ((ahora - ultimoPresionado) > DEBOUNCE_MS) {
      ultimoPresionado = ahora;
      Serial.println("BOTON:1");
    }
  }
}
