// --- TRANSMISOR ESP32 ---
// ALCANCE: setPALevel y setDataRate afectan la distancia máxima.
// SEGURIDAD: canal exclusivo y dirección como identificador de enlace.
// IDENTIDAD: la dirección actúa como ID único del transmisor.

#include <SPI.h>
#include <RF24.h>

#define CE_PIN 4
#define CSN_PIN 5
#define BOTON 14

RF24 radio(CE_PIN, CSN_PIN);
const byte direccion[6] = "00001"; // IDENTIDAD

void setup() {
  Serial.begin(115200);
  pinMode(BOTON, INPUT_PULLUP);
  SPI.begin(18,19,23,5);

  radio.begin();
  radio.setChannel(13); // SEGURIDAD: canal único
  radio.setPALevel(RF24_PA_LOW); // ALCANCE
  radio.setDataRate(RF24_250KBPS); // ALCANCE / robustez
  radio.openWritingPipe(direccion); // IDENTIDAD
  radio.stopListening();
}

void loop(){
  if(digitalRead(BOTON)==LOW){
    int mensaje = 1;
    radio.write(&mensaje, sizeof(mensaje));
  }
}
