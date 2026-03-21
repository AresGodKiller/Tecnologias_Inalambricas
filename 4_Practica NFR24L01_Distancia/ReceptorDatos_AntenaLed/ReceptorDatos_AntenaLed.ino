// --- RECEPTOR ESP32 ---
// ALCANCE: misma configuración de canal, potencia y tasa.
// SEGURIDAD: canal exclusivo reduce interferencias.
// IDENTIDAD: solo acepta paquetes de la dirección definida.

#include <SPI.h>
#include <RF24.h>

#define CE_PIN 4
#define CSN_PIN 5
#define LED_PIN 2

RF24 radio(CE_PIN, CSN_PIN);
const byte direccion[6] = "00001"; // IDENTIDAD
const unsigned long TIMEOUT_MS = 200;
unsigned long ultimoPaquete = 0;

void setup(){
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  SPI.begin(18,19,23,5);

  radio.begin();
  radio.setChannel(13); // SEGURIDAD
  radio.setPALevel(RF24_PA_LOW); // ALCANCE
  radio.setDataRate(RF24_250KBPS); // ALCANCE
  radio.openReadingPipe(0, direccion); // IDENTIDAD
  radio.startListening();
}

void loop(){
  while(radio.available()){
    int mensaje;
    radio.read(&mensaje, sizeof(mensaje));
    if(mensaje==1){
      digitalWrite(LED_PIN,HIGH);
      ultimoPaquete=millis();
    }
  }
  if(millis()-ultimoPaquete > TIMEOUT_MS){
    digitalWrite(LED_PIN,LOW);
  }
}

