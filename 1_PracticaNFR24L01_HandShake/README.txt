README – Comunicación Inalámbrica con NRF24L01 (TX/RX) usando ESP32 con Esp32/Arduino

Fecha: 06/03/2026

Integrantes:
Eduardo Cadengo López - 
Itzel Citlalli Martell De La Cruz - 
Damian Alexander Diaz Piña -

Video demostrativo:
https://youtu.be/Wdm9OlAvnIU?si=FW8ECXgMGvFUuMiW

Link GitHub: https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/1_PracticaNFR24L01_HandShake

Placa utilizada y Componentes utilizados:

2 Módulos NRF24L01 (o versión con antena PA+LNA)
2 ESP32 (o 1 ESP32 y 1 Arduino UNO/Nano)
Protoboard
Jumpers (cables cortos)
Cable USB para programar cada microcontrolador


Descripción del proyecto:
Este proyecto implementa una comunicación inalámbrica utilizando los módulos NRF24L01 para transmitir un mensaje desde un dispositivo configurado como Transmisor (TX) hacia otro configurado como Receptor (RX).
El objetivo de la práctica es que, mientras el dispositivo TX permanezca energizado, el RX muestre periódicamente en su monitor serial un mensaje recibido, validando así que la comunicación se estableció correctamente.
Los módulos se configuran mediante el protocolo SPI, definiendo un canal, potencia de transmisión y una dirección (“pipe”) que permite que ambos dispositivos intercambien información sin interferencias.

Objetivo del código:

Configurar dos dispositivos con NRF24L01, uno como transmisor y otro como receptor.
Enviar un mensaje desde el TX cada cierto intervalo.
Recibirlo en el RX e imprimirlo en el monitor serial.
Mantener la comunicación siempre que el TX siga encendido.


Componentes necesarios:

2 ESP32 (o combinación ESP32 + Arduino UNO).
2 NRF24L01.
Protoboard.
Cables de conexión (jumpers).


Lógica del programa
1. Inicialización
Se configura el módulo NRF24L01 con:

Canal (ejemplo: 67)
Nivel de potencia de transmisión
Dirección del “pipe” (ejemplo "00001")
Configuración SPI y pines CE/CSN

2. Transmisor (TX)

Se ejecuta stopListening() para colocarlo en modo transmisión.
Envía periódicamente un mensaje, por ejemplo "Hola".
Muestra en el monitor serial si el mensaje se envió correctamente.

3. Receptor (RX)

Entra en modo escucha usando startListening().
Cuando detecta un mensaje disponible, lo lee con radio.read().
Imprime en el monitor serial el texto recibido.

4. Indicador de funcionamiento

Mientras el TX esté encendido, el RX debe seguir recibiendo mensajes.
Si se apaga el TX, el RX deja de recibir mensajes.


Conexiones necesarias (ESP32)
NRF24L01 → ESP32

VCC → 3.3 V
GND → GND
CE → GPIO 4
CSN → GPIO 5
SCK → GPIO 18
MOSI → GPIO 23
MISO → GPIO 19
IRQ → No se usa

Nota:

No usar 5 V.
Mantener cables cortos.
Agregar un capacitor cerca del NRF24L01.

Funciones clave

radio.begin(): Inicializa el módulo.
radio.setChannel(): Define el canal de operación.
openWritingPipe() / openReadingPipe(): Establecen la dirección del enlace.
stopListening(): Coloca el módulo como TX.
startListening(): Coloca el módulo como RX.
radio.write(): Envía un mensaje.
radio.read(): Recibe un mensaje disponible.

Cómo ejecutar
1. Preparación

Realizar las conexiones indicadas entre el NRF24L01 y el microcontrolador.
Colocar capacitor en el módulo para evitar caídas de voltaje.

2. Cargar programas

Subir el código del Transmisor (TX) a un ESP32/Arduino.
Subir el código del Receptor (RX) al segundo dispositivo.

3. Monitoreo

Abrir el monitor serial del RX a 115200 baudios.
Encender primero el RX (opcional).
Encender el TX.

Deberá aparecer repetidamente:
Recibido el mensaje: Hola

4. Pruebas

Apagar el TX → el RX dejará de recibir mensajes.
Encender el TX → la transmisión se reanuda automáticamente.


Características especiales que se usaron:

Comunicación inalámbrica de 2.4 GHz con NRF24L01.
Protocolo SPI para control del módulo.
Dirección de comunicación personalizada.
Configuración de canal y potencia para mejorar estabilidad.
Recepción continua mientras el TX siga activo.


