// --- ESP32 (RX) ---
// Activa el relevador cuando la distancia es mayor a 20 cm
// (tinaco bajo => bomba de agua encendida)
#include <SPI.h>
#include <RF24.h>
 
RF24 radio(4, 5);                     // CE=GPIO4, CSN=GPIO5
const byte direccion[6] = "00001";    // Debe coincidir con TX
float distanciaRecibida;
 
const int PIN_RELEVADOR = 26;  // GPIO26 -> Señal IN del relevador
 
void setup() {
  Serial.begin(115200);
 
  pinMode(PIN_RELEVADOR, OUTPUT);
  digitalWrite(PIN_RELEVADOR, LOW);  // Relevador apagado al inicio
 
  if (!radio.begin()) {
    Serial.println("NRF24L01 no detectado");
    while(1);
  }
 
  radio.openReadingPipe(0, direccion);  // Pipe de lectura
  radio.setChannel(112);                // Canal 112 (debe coincidir con TX)
  radio.setPALevel(RF24_PA_LOW);
  radio.startListening();               // Modo RX
  Serial.println("Sistema listo. Esperando datos del sensor...");
}
 
void loop() {
  if (radio.available()) {             // Hay datos en el buffer de recepcion
    radio.read(&distanciaRecibida, sizeof(distanciaRecibida));
 
    Serial.print("Distancia recibida: ");
    Serial.print(distanciaRecibida);
    Serial.println(" cm");
 
    // Logica de control: distancia > 20 cm = tinaco bajo = activar bomba
    if (distanciaRecibida > 20.0) {
      digitalWrite(PIN_RELEVADOR, HIGH);  // Activa relevador (bomba encendida)
      Serial.println("[!] TINACO BAJO - BOMBA ENCENDIDA");
    } else {
      digitalWrite(PIN_RELEVADOR, LOW);   // Apaga relevador (tinaco lleno)
      Serial.println("[.] Tinaco lleno - BOMBA APAGADA");
    }
  }
}
