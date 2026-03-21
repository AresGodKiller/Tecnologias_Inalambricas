README – Práctica de Comunicación Inalámbrica con NRF24L01 (Prueba de Alcance – TX/RX)
Fecha: 20/03/2026

Integrantes:
- Eduardo Cadengo López
- Itzel Citlalli Martell De La Cruz
- Damian Alexander Diaz Piña

Video demostrativo:
-Distancia desde Receptor
https://youtu.be/P4weEsIAYFc
-Distancia desde Transmisor
https://youtube.com/shorts/frOLnOLjUag


Repositorio GitHub:
https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/4_Practica%20NFR24L01_Distancia

--------------------------------------------------------------------
DESCRIPCIÓN DEL PROYECTO
--------------------------------------------------------------------
En esta práctica se establece comunicación inalámbrica entre dos dispositivos
utilizando dos módulos NRF24L01 y dos computadoras independientes, donde cada 
una controla un ESP32:

• Un dispositivo funciona como TRANSMISOR (TX).  
• El otro funciona como RECEPTOR (RX).

El objetivo principal fue medir el ALCANCE REAL entre ambos dispositivos.
Durante las pruebas, se logró obtener aproximadamente 57 metros en línea de 
vista antes de perder la comunicación.

El sistema implementado consiste en:

- El TX envía un mensaje cuando se presiona un botón.  
- El RX recibe el mensaje y enciende un LED mientras sigan llegando paquetes.  
- Cuando el botón se suelta, el TX deja de enviar datos, y el RX apagará el LED
  automáticamente después de un tiempo de espera.

También se implementaron configuraciones específicas que contribuyen a:
• ALCANCE → potencia, canal y velocidad de transmisión.  
• IDENTIDAD → dirección única del pipe.  
• SEGURIDAD → canal exclusivo para evitar interferencia y suplantación.

--------------------------------------------------------------------
OBJETIVO GENERAL
--------------------------------------------------------------------
Establecer comunicación inalámbrica entre dos módulos NRF24L01 y medir el 
alcance máximo real usando dos computadoras distintas para TX y RX.

--------------------------------------------------------------------
COMPONENTES UTILIZADOS
--------------------------------------------------------------------
- 2 × ESP32 (o 1 ESP32 + 1 Arduino)
- 2 × Módulos NRF24L01
- 1 × PushButton (TX)
- 1 × LED + resistencia 220 Ω (RX)
- Protoboard
- Jumpers
- Capacitor recomendado (10 µF – 47 µF)
- Cables USB

--------------------------------------------------------------------
CONEXIONES (ESP32 + NRF24L01)
--------------------------------------------------------------------
NRF24L01 → ESP32
VCC    → 3.3V
GND    → GND
CE     → GPIO 4
CSN    → GPIO 5
SCK    → GPIO 18
MOSI   → GPIO 23
MISO   → GPIO 19
IRQ    → (No usado)

CONEXIÓN DEL BOTÓN (TX)
Pin 1 → GPIO 14
Pin 2 → GND
Modo → INPUT_PULLUP (sin resistencia)

CONEXIÓN DEL LED (RX)
Ánodo → Resistencia 220 Ω → GPIO 2
Cátodo → GND

--------------------------------------------------------------------
LÓGICA DEL PROGRAMA
--------------------------------------------------------------------
1. Ambos dispositivos inicializan:
   - Canal de comunicación
   - Dirección del pipe (“00001”)
   - Potencia de transmisión
   - Velocidad de datos
   - Pines CE/CSN/SPI
   - Modo TX o RX según corresponda

2. Transmisor (TX):
   - Detecta botón con INPUT_PULLUP.
   - Mientras esté presionado, envía el valor “1”.
   - En ausencia de presión, no envía datos.

3. Receptor (RX):
   - Permanece escuchando.
   - Si recibe “1”, enciende LED y reinicia temporizador.
   - Si no llegan datos después de cierto intervalo, apaga el LED.

--------------------------------------------------------------------
PRUEBA DE ALCANCE
--------------------------------------------------------------------
El experimento consistió en alejar físicamente ambos dispositivos mientras se
grababa video para validar la distancia.

RESULTADO:
Alcance máximo obtenido: ~57 metros en línea de vista.

Cuando se superaba esa distancia:
- El LED dejaba de encender.
- El monitor serial ya no reportaba recepción de datos.

--------------------------------------------------------------------
NOTAS IMPORTANTES
--------------------------------------------------------------------
- NO alimentar el NRF24L01 con 5V.
- Mantener cables cortos para el módulo.
- Recomendado: capacitor cerca de VCC-GND.
- Usar el mismo canal y dirección en TX y RX siempre.

--------------------------------------------------------------------
FUNCIONES CLAVE DEL NRF24L01
--------------------------------------------------------------------
radio.begin() → Inicializa el módulo
radio.setChannel() → Ajusta el canal
radio.setPALevel() → Controla alcance
radio.setDataRate() → Estabilidad y robustez
openWritingPipe() / openReadingPipe() → Identidad del enlace
stopListening() / startListening() → Cambia entre TX y RX
radio.write() → Envía datos
radio.read() → Recibe datos

--------------------------------------------------------------------
CÓMO EJECUTAR
--------------------------------------------------------------------
1. Conectar módulos y componentes.
2. Cargar el código TX en la computadora 1.
3. Cargar el código RX en la computadora 2.
4. Abrir monitor serial de RX (115200).
5. Presionar botón → LED debe encender.
6. Alejar distancia entre TX y RX → registrar alcance máximo.
