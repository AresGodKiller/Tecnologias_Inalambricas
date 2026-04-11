============================================================
README - Lectura de tarjeta NFC/RFID con ESP32 + PN532 (I2C)
============================================================

Nombre del proyecto:
- NFC_Basics (ESP32 + PN532)

Fecha:
- 10/04/2026

Integrantes:
- Eduardo Cadengo López
- Itzel Citlalli Martell De La Cruz
- Damian Alexander Diaz Piña

------------------------------------------------------------
1) Descripción rápida
------------------------------------------------------------
Este proyecto lee el UID (identificador) de una tarjeta NFC/RFID usando una ESP32
y el módulo PN532 mediante comunicación I2C. El UID se muestra en el monitor
serial en 3 formatos:
- Hexadecimal (Base 16)
- Decimal (Base 10)
- Binario (Base 2)

Nota:
La práctica se realizó con PN532 (NFC). También se puede realizar con RC522,
pero en este repositorio se trabajó con el PN532.

------------------------------------------------------------
2) Objetivo de la práctica
------------------------------------------------------------
Lograr que, al acercar una tarjeta NFC al PN532, el monitor serial muestre el UID
en las tres bases: 2, 10 y 16.

------------------------------------------------------------
3) Materiales
------------------------------------------------------------
- 1x ESP32 (DevKit o similar)
- 1x Módulo NFC PN532 (configurado en modo I2C)
- 1x Tarjeta NFC compatible (ej. ISO14443A / MIFARE)
- Cables Dupont (jumpers)
- (Opcional) Protoboard

------------------------------------------------------------
4) Conexiones (ESP32 <-> PN532)  [I2C]
------------------------------------------------------------
Conexión típica usada:

ESP32      ->  PN532
-------------------------
3V3        ->  VCC   (si tu módulo acepta 3.3V)
GND        ->  GND
GPIO21 SDA ->  SDA
GPIO22 SCL ->  SCL

IMPORTANTE:
- Asegura que tu módulo PN532 esté en modo I2C (algunos traen switch/jumpers).
- Si el módulo no responde, revisa alimentación, GND común y cables SDA/SCL.

------------------------------------------------------------
5) Librerías y entorno
------------------------------------------------------------
- Arduino IDE
- Librerías:
  * Wire.h
  * Adafruit_PN532.h (Adafruit PN532)

------------------------------------------------------------
6) Cómo usar (pasos rápidos)
------------------------------------------------------------
1) Abre Arduino IDE.
2) Instala la librería "Adafruit PN532" si no la tienes.
3) Conecta el PN532 a la ESP32 según la sección 4.
4) Carga el código al ESP32.
5) Abre el Monitor Serial a 115200 baudios.
6) Acerca una tarjeta NFC al lector.
7) Observa la impresión del UID en HEX/DEC/BIN.

------------------------------------------------------------
7) Salida esperada (ejemplo)
------------------------------------------------------------
Cuando detecte una tarjeta, se verá algo parecido a:

====================================
  TARJETA DETECTADA
====================================
HEX (Base 16): 04:AB:1C:2D:...
DEC (Base 10): 4-171-28-45-...
BIN (Base  2): 00000100 10101011 00011100 00101101 ...
====================================

------------------------------------------------------------
8) Estructura / Detalles del código (resumen)
------------------------------------------------------------
- Se inicializa el PN532 y se verifica su firmware.
- Se configura el modo de lectura (SAMConfig).
- En el loop:
  * Se intenta leer una tarjeta ISO14443A
  * Si se detecta, se imprime el UID:
      - Base 16 usando Serial.print(..., HEX)
      - Base 10 usando Serial.print(..., DEC)
      - Base 2 imprimiendo bit por bit con corrimientos (>>)

------------------------------------------------------------
9) Video de funcionamiento
------------------------------------------------------------
- YouTube: https://youtu.be/XhOumT1LdeU

------------------------------------------------------------
10) Repositorio (GitHub)
------------------------------------------------------------
- GitHub: https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/NFC_Basics

------------------------------------------------------------
11) Problemas comunes 
------------------------------------------------------------
- "PN532 no encontrado":
  * Revisa VCC/GND
  * Revisa que esté en modo I2C
  * Cambia cables SDA/SCL
  * Asegura que SDA=GPIO21 y SCL=GPIO22 (o ajusta en el código)

- No imprime nada en serial:
  * Revisa que el Monitor Serial esté en 115200
  * Asegura que el puerto COM/USB sea el correcto

------------------------------------------------------------
12) Créditos
------------------------------------------------------------
Práctica realizada por los integrantes listados arriba para la lectura de UID en
bases 2, 10 y 16 usando ESP32 + PN532 (I2C).