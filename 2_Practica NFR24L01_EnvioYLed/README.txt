README – Comunicación Inalámbrica con NRF24L01 (TX/RX) usando ESP32 y PushButton/LED
Fecha: 11/03/2026

Integrantes
Eduardo Cadengo López -
Itzel Citlalli Martell De La Cruz - 
Damian Alexander Diaz Piña -


Video demostrativo
https://youtube.com/shorts/ukE-nj5UNh0?feature=share

Repositorio GitHub
https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/2_Practica%20NFR24L01_EnvioYLed

Placa utilizada y Componentes utilizados

2 Módulos NRF24L01 (con o sin PA+LNA)
2 ESP32 (o 1 ESP32 + 1 Arduino)
Protoboard
Jumpers
PushButton (para el TX)
LED + resistencia de 220 Ω (para el RX)
Cables USB


Descripción del proyecto
En esta práctica se establece una comunicación inalámbrica utilizando dos NRF24L01, donde uno funciona como transmisor (TX) y el otro como receptor (RX).
La diferencia principal respecto a prácticas previas es que:

El TX solo envía un mensaje cuando se presiona un botón.
El RX enciende un LED mientras se estén recibiendo mensajes.
Cuando el botón deja de presionarse, el TX deja de enviar datos, por lo que el RX dejará de recibirlos y apagará el LED automáticamente después de un breve tiempo.

Con esto se simula un sistema básico de control inalámbrico donde un evento físico (el botón) activa una señal remota (el encendido del LED).

Objetivo del código

Configurar dos microcontroladores para usar el NRF24L01 mediante SPI.
Hacer que el transmisor detecte un botón, y al presionarlo envíe un dato.
Hacer que el receptor detecte ese dato, lo imprima en el monitor serie y active un LED.
Mantener el LED encendido mientras los mensajes sigan llegando.
Apagar el LED automáticamente cuando se deje de recibir información.


Componentes necesarios

2 × ESP32 (o ESP32 + Arduino UNO/Nano)
2 × NRF24L01
1 × PushButton
1 × LED
1 × Resistencia 220 Ω
Cables(Jumpers) y protoboard


Lógica del programa
1. Inicialización
En ambos dispositivos se configura:

Canal específico de comunicación
Dirección del “pipe” (ej. "00001")
Potencia de transmisión
Velocidad de datos
Pines CE/CSN + SPI


2. Transmisor (TX) – Con botón

Se configura el botón con INPUT_PULLUP.
Mientras el botón esté presionado (lectura LOW), se envía un mensaje "1".
El envío se repite rápidamente para que el RX pueda mantener el LED encendido.
Al soltar el botón, deja de transmitir.


3. Receptor (RX) – Con LED

Permanece en modo escucha (startListening()).
Cuando recibe un mensaje, lo imprime y enciende el LED.
Cada recepción reinicia un contador interno.
Si pasa cierto tiempo sin recibir datos, el LED se apaga.

Esta lógica cumple exactamente el objetivo de que el LED permanezca encendido solo mientras los mensajes se estén recibiendo.

4. Indicador de funcionamiento

Botón presionado en TX → LED encendido en RX.
Botón liberado → LED se apaga tras un breve tiempo.
El monitor serie del RX muestra cada recepción.


Conexiones necesarias (ESP32)
VCC  →  3.3V
GND  →  GND
CE   →  GPIO 4
CSN  →  GPIO 5
SCK  →  GPIO 18
MOSI →  GPIO 23
MISO →  GPIO 19
IRQ  →  (no se usa)

Conexión del botón (solo Transmisor)
Un pin del botón  →  GPIO 14
El otro pin        →  GND
El pin se configura como INPUT_PULLUP, por lo que NO necesita resistencia externa.

Conexión del LED (solo Receptor)
Ánodo del LED (pierna larga) → Resistencia de 220 ohm → GPIO 2
Cátodo del LED (pierna corta) → GND

Notas importantes:

No usar 5 V para alimentar el NRF24L01.
Mantener los cables cortos.
Usar capacitor cerca del módulo para evitar caídas momentáneas de voltaje.


Funciones clave

radio.begin() → Inicializa el módulo
radio.setChannel() → Configura el canal
openWritingPipe() / openReadingPipe() → Establecen la dirección
stopListening() → Pone el módulo en modo TX
startListening() → Pone el módulo en RX
radio.write() → Envía un mensaje
radio.read() → Recibe un mensaje


Cómo ejecutar
1. Preparación

Conectar correctamente el NRF24L01
Añadir capacitor
Conectar LED y resistencia en el RX
Conectar botón en el TX

2. Cargar programas

Subir código transmisor al ESP32 del botón
Subir código receptor al ESP32 del LED

3. Monitoreo

Abrir el monitor serial del RX a 115200 baudios
Presionar el botón
Verás:

Mensajes de recepción
LED encendido mientras se reciba información

4. Pruebas

Soltar el botón → LED se apaga tras un breve tiempo
Mantener el botón → LED encendido
Apagar TX → RX deja de recibir
Encender TX → RX vuelve a recibir normalmente


Características especiales utilizadas

Comunicación inalámbrica de 2.4 GHz
Uso del protocolo SPI
Dirección de comunicación personalizada
Control de un evento físico remoto (botón → LED)
Temporizador para verificar ausencia de paquetes en el RX
Indicadores visuales y por monitor serial


