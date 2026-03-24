Evaluativo 2 - NRF24l01 - Sistema de control

Integrantes

Eduardo Cadengo López
Itzel Citlalli Martell De La Cruz
Damian Alexander Díaz Piña


 Video demostrativo
https://youtu.be/4Lp5CuFM2ao 

 Repositorio GitHub
https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/Evaluativo2_NRF24l01_SistemaControl


 Descripción del proyecto
En esta práctica se establece una comunicación inalámbrica entre dos dispositivos usando módulos NRF24L01,
implementando un sistema de monitoreo de nivel de agua y control de bomba para animales de granja.

El Transmisor (TX) es un Arduino UNO con un sensor ultrasónico HC-SR04 instalado en la parte superior
del tinaco. Mide continuamente la distancia al nivel del agua y la envía por radio cada segundo.

El Receptor (RX) es un ESP32 ubicado en la oficina/cuarto de máquinas. Recibe la distancia, evalúa
el nivel del tinaco y activa o desactiva el relevador que controla la bomba de agua (representada
con un LED en el prototipo).

El objetivo se cumple cuando:
 El RX recibe la distancia enviada por el TX correctamente.
 El relevador se activa automáticamente cuando el nivel del agua está bajo (distancia > 20 cm).
 El relevador se apaga cuando el tinaco está lleno (distancia <= 20 cm).


 Placas y componentes utilizados

1 Arduino UNO (TX)
1 ESP32 (RX)
2 módulos NRF24L01
1 sensor ultrasónico HC-SR04
1 módulo relevador de 5V (JQC-3FF-S-Z)
1 LED (simula la bomba de agua)
Resistencia ~220 Ω (para el LED)
Jumpers
Protoboard
Cables USB


 Descripción de módulos

* ESP32
Microcontrolador con WiFi, BLE y múltiples buses de comunicación (SPI, I²C, UART).
En esta práctica opera como receptor (RX), evalúa el nivel del tinaco y controla el relevador.

* NRF24L01
Transceptor de 2.4 GHz con comunicación SPI. Permite la transmisión de datos con baja potencia
y buena estabilidad.
Permite:

  125 canales
  Hasta 2 Mbps
  Múltiples pipes de recepción
  Auto-ACK y reintentos

* Diferencias entre NRF24L01 con y sin PA+LNA

  NRF24 estándar (sin PA+LNA)
    Antena impresa en PCB
    Bajo consumo (~12 mA)
    Alcance corto–medio (~100 m en campo abierto)
    Ideal para prácticas de laboratorio

  NRF24 con PA+LNA + antena externa (SMA)
    Mayor potencia de transmisión (+20 dBm)
    Mejor sensibilidad de recepción (LNA)
    Alcance mayor (~1000 m en campo abierto)
    Requiere fuente 3.3 V más estable (picos >100 mA en TX)

  Para este proyecto se utilizó el módulo estándar (antena PCB), suficiente
  para la distancia entre el tinaco y la oficina en el prototipo de laboratorio.


 Descripción del sensor: HC-SR04 (Ultrasónico)
El HC-SR04 mide distancia mediante ultrasonido. En este proyecto se instala apuntando
hacia abajo dentro del tinaco; a mayor distancia medida, menor nivel de agua.

  Se envía un pulso de 10 µs en el pin TRIG.
  El sensor emite 8 pulsos ultrasónicos de 40 kHz.
  El pin ECHO permanece en alto durante el tiempo de ida y vuelta de la onda.
  La distancia se calcula como:

    distancia (cm) = (duracion_us * 0.034) / 2

  Rango: 2 cm – 400 cm  |  Precisión: ±3 mm  |  Alimentación: 5 V


 Descripción del actuador: Módulo Relevador + LED
Módulo relevador de 1 canal (JQC-3FF-S-Z) controlado por el GPIO26 del ESP32.
En la aplicación real conmutaría la bomba eléctrica; en el prototipo conmuta un LED.

  Tensión de bobina: 5 V DC
  Señal de control: 3.3 V lógico (compatible con ESP32)
  Carga máxima: 10 A / 250 VAC
  Incluye optoacoplador para aislar la señal de control de la carga


 Conexiones

 Transmisor – Arduino UNO + HC-SR04 + NRF24L01

NRF24L01 → Arduino
  VCC  → 3.3 V   ← IMPORTANTE: NO conectar a 5 V
  GND  → GND
  CE   → D9
  CSN  → D10
  SCK  → D13
  MOSI → D11
  MISO → D12

HC-SR04 → Arduino
  VCC  → 5 V
  GND  → GND
  TRIG → D6
  ECHO → D7

 Receptor – ESP32 + NRF24L01 + Relevador

NRF24L01 → ESP32 (VSPI)
  VCC  → 3.3 V   ← IMPORTANTE: NO conectar a 5 V
  GND  → GND
  CE   → GPIO 4
  CSN  → GPIO 5
  SCK  → GPIO 18
  MOSI → GPIO 23
  MISO → GPIO 19

Relevador → ESP32
  VCC → 5 V / VIN
  GND → GND
  IN  → GPIO 26

LED (bomba)
  Ánodo (+) → Contacto NO del relevador → resistencia 220 Ω → 5 V
  Cátodo (-) → GND


 Lógica del programa

1. Inicialización
   Ambos dispositivos configuran:
     Canal (112)
     Dirección de pipe ("00001")
     Potencia: RF24_PA_LOW
     SPI + pines CE y CSN

2. Transmisor (Arduino UNO)
   Mide distancia cada segundo con HC-SR04.
   Envía el valor float al RX con radio.write().
   Imprime en serial el valor enviado o el error si falla.

3. Receptor (ESP32)
   Permanece en modo escucha (startListening()).
   Cuando recibe un valor evalúa el nivel:

     Distancia > 20 cm  → Tinaco BAJO  → Relevador ON  → Bomba/LED ENCENDIDO
     Distancia <= 20 cm → Tinaco LLENO → Relevador OFF → Bomba/LED APAGADO


 Funciones clave

  radio.begin()           – Inicializa el módulo NRF24L01
  openWritingPipe()       – Configura dirección de transmisión (TX)
  openReadingPipe()       – Configura dirección de recepción (RX)
  stopListening()         – Activa modo transmisión
  startListening()        – Activa modo recepción
  radio.write()           – Envía datos (float de distancia)
  radio.read()            – Recibe datos
  radio.available()       – Verifica si hay datos en el buffer
  digitalWrite(PIN, HIGH) – Activa el relevador (bomba encendida)
  digitalWrite(PIN, LOW)  – Desactiva el relevador (bomba apagada)


 Cómo ejecutar

1. Preparación
   Conectar cada módulo como se indica en la sección de conexiones.
   Se recomienda colocar un capacitor de 100 µF entre VCC y GND del NRF24L01.

2. Cargar programas
   Cargar TX.ino al Arduino UNO.
   Cargar RX.ino al ESP32.

3. Pruebas
   Abrir el monitor serial del TX a 9600 baudios.
   Abrir el monitor serial del RX a 115200 baudios.

   En el TX deberás ver:
     Transmisor listo con sensor ultrasonico
     Distancia enviada: XX cm

   En el RX deberás ver:
     Sistema listo. Esperando datos del sensor...
     Distancia recibida: XX cm
     [!] TINACO BAJO - BOMBA ENCENDIDA   (si distancia > 20 cm)
     [.] Tinaco lleno - BOMBA APAGADA    (si distancia <= 20 cm)

   Aleja y acerca un objeto al sensor para simular el nivel del tinaco.
   El LED (relevador) debe encenderse cuando el objeto esté a más de 20 cm.


 Características destacadas

  Comunicación inalámbrica en 2.4 GHz entre Arduino y ESP32
  Monitoreo de nivel de agua en tiempo real
  Control automático de bomba mediante relevador
  Enlace punto a punto con protocolo Enhanced ShockBurst (Nordic)
  Umbral de activación configurable por software (actualmente 20 cm)
  Aplicación práctica: automatización de bebederos para animales de granja
