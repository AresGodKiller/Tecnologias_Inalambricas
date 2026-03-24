// --- Arduino UNO (TX) ---
// Lee distancia del HC-SR04 y la envía como float por NRF24L01
#include <RF24.h>
 
RF24 radio(9, 10);                    // CE=D9, CSN=D10
const byte direccion[6] = "00001";    
 
#define TRIG 6   // Pin Trigger del HC-SR04
#define ECHO 7   // Pin Echo del HC-SR04
 
long  duracion;   // Tiempo en microsegundos del pulso ECHO
float distancia;  // Distancia calculada en cm
 
void setup() {
  Serial.begin(9600);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
 
  if (!radio.begin()) {
    Serial.println("NRF24L01 no detectado");
    while(1);  // Detiene ejecucion si no hay radio
  }
 
  radio.openWritingPipe(direccion);  // Destino de transmision
  radio.setChannel(112);             // Canal 112 (debe coincidir con RX)
  radio.setPALevel(RF24_PA_LOW);     // Potencia baja para pruebas de mesa
  radio.stopListening();             // Modo TX
  Serial.println("Transmisor listo con sensor ultrasonico");
}
 
void loop() {
  // --- Disparo ultrasónico ---
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);            // Pulso de 10 µs para activar medicion
  digitalWrite(TRIG, LOW);
 
  duracion  = pulseIn(ECHO, HIGH);          // Mide ancho del pulso ECHO
  distancia = duracion * 0.034 / 2.0;       // Convierte a cm (ida y vuelta)
 
  // --- Envío por radio ---
  bool ok = radio.write(&distancia, sizeof(distancia));
  if (ok) {
    Serial.print("Distancia enviada: ");
    Serial.print(distancia);
    Serial.println(" cm");
  } else {
    Serial.println("Error al enviar");
  }
  delay(1000);  // Envio cada 1 segundo
}
