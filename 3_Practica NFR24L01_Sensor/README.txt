Integrantes

Eduardo Cadengo López
Itzel Citlalli Martell De La Cruz
Damian Alexander Díaz Piña


 Video demostrativo
https://youtu.be/xSb_0cPzFfY

 Repositorio GitHub
https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/3_Practica%20NFR24L01_Sensor

 Descripción del proyecto
En esta práctica se establece una comunicación inalámbrica entre dos dispositivos usando módulos NRF24L01:

El Transmisor (TX) es un Arduino que utiliza un sensor ultrasónico HC‑SR04 para medir distancia y enviarla periódicamente.
El Receptor (RX) es un ESP32, el cual recibe los valores enviados y los muestra en el monitor serial, confirmando que la comunicación se encuentra activa.

El objetivo se cumple cuando:
 El RX imprime un mensaje indicando que la comunicación se estableció.
 El RX muestra periódicamente las distancias recibidas.

 Placas y componentes utilizados [README | Txt]

1 Arduino UNO (TX)
1 ESP32 (RX)
2 módulos NRF24L01
1 sensor ultrasónico HC‑SR04
Jumpers
Protoboard
Cables USB


 Descripción de módulos
* ESP32 [README | Txt]
Microcontrolador con WiFi, BLE, múltiples buses de comunicación (SPI, I²C, UART), excelente para tareas de recepción e interpretación de datos inalámbricos. En esta práctica su función es operar como receptor.

* NRF24L01 [README | Txt]
Transceptor de 2.4 GHz con comunicación SPI. Permite la transmisión de datos con baja potencia y buena estabilidad.
Permite:

125 canales
Hasta 2 Mbps
Múltiples pipes de recepción
Auto-ACK y reintentos

* Diferencias entre NRF24L01 con y sin PA+LNA [README | Txt]


NRF24 estándar (sin PA+LNA)

Antena en PCB
Bajo consumo
Alcance corto–medio



NRF24 con PA+LNA + antena externa

Mayor potencia de transmisión
Mejor sensibilidad
Alcance mayor
Requiere fuente 3.3 V más estable




 Descripción del sensor ultrasónico HC‑SR04
El HC‑SR04 mide distancia mediante ultrasonido:

Se envía un pulso en el pin TRIG.
El pulso rebota en un objeto y retorna al sensor.
El pin ECHO se mantiene en alto durante el tiempo que tarda este rebote.
La distancia se calcula como:

distancia = tiempo * 0.034 / 2


 Conexiones
 Transmisor – Arduino UNO + HC‑SR04 + NRF24L01
NRF24L01 → Arduino

VCC → 3.3 V
GND → GND
CE → D9
CSN → D10
SCK → D13
MOSI → D11
MISO → D12

HC‑SR04 → Arduino

TRIG → D6
ECHO → D7
VCC → 5 V
GND → GND

 IMPORTANTE: El NRF24L01 NO debe conectarse a 5 V.

 Receptor – ESP32 + NRF24L01
NRF24L01 → ESP32 (VSPI) [README | Txt]

VCC → 3.3 V
GND → GND
CE → GPIO 4
CSN → GPIO 5
SCK → GPIO 18
MOSI → GPIO 23
MISO → GPIO 19


 Lógica del programa
1. Inicialización
Ambos dispositivos configuran:

Canal (112)
Dirección de pipe ("00001")
Potencia
SPI + pines CE y CSN

2. Transmisor (Arduino)

Mide distancia cada segundo con HC‑SR04.
Envía el valor flotante al RX con radio.write().
Imprime en serial el valor enviado.

3. Receptor (ESP32)

Permanece en modo escucha (startListening()).
Cuando recibe un valor:

Lo muestra como “Distancia recibida: X cm”.
Confirma que la comunicación está activa.




 Funciones clave [README | Txt]

radio.begin() – Inicializa el módulo
openWritingPipe() / openReadingPipe() – Dirección TX/RX
stopListening() – Modo transmisión
startListening() – Modo recepción
write() – Envía datos
read() – Recibe datos


 Cómo ejecutar
1. Preparación

Conectar cada módulo como se indica.
Colocar capacitor en el NRF24L01.

2. Cargar programas

Cargar TX.ino al Arduino.
Cargar RX.ino al ESP32.

3. Pruebas

Abrir el monitor serial del RX a 115200 baudios.
Se deberá ver:

NRF24L01 detectado - RX listo
Distancia recibida: XX cm


Aleja y acerca un objeto al sensor para ver cambios en tiempo real.
Si la comunicación falla, el RX dejará de imprimir valores.


 Características destacadas

Comunicación inalámbrica en 2.4 GHz
Mediciones de distancia en tiempo real
Enlace punto a punto entre microcontroladores
Uso de SPI
Lectura sensorial remota