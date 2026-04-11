============================================================
README - Validador de Acceso con NFC (ESP32 + PN532 | I2C)
============================================================

Nombre del proyecto:
- NFC_RFID Autorizacion

Fecha:
- 10/04/2026

Descripción corta:
Este proyecto utiliza una ESP32 y el módulo NFC PN532 para leer el UID de una tarjeta
NFC (ISO14443A). Con el UID se realiza una validación tipo “lista blanca”:
- Si la tarjeta coincide con el UID autorizado -> ACCESO CONCEDIDO
- Si no coincide -> ACCESO DENEGADO
Además, se simula el inicio/termino de operaciones (ej. encendido de maquinaria)
mediante mensajes en el monitor serial y un pin de salida opcional (LED/relay).

Nota:
La práctica se realizó con PN532 (NFC) en lugar de RC522 (RFID). Ambos pueden usarse
para identificación, pero aquí se trabajó con PN532 por disponibilidad.

------------------------------------------------------------
1) Integrantes
------------------------------------------------------------
- Eduardo Cadengo López
- Itzel Citlalli Martell De La Cruz
- Damian Alexander Diaz Piña

------------------------------------------------------------
2) Objetivo de la práctica
------------------------------------------------------------
Lograr que el monitor serial muestre:
1) El UID de la tarjeta en Base 16 (HEX), Base 10 (DEC) y Base 2 (BIN)
2) La respuesta de la implementación (ACCESO CONCEDIDO / ACCESO DENEGADO)
3) La simulación de inicio de operaciones (MAQUINARIA ENCENDIDA / APAGADA)

------------------------------------------------------------
3) Materiales
------------------------------------------------------------
- 1x ESP32 (DevKit o similar)
- 1x Módulo NFC PN532 (configurado en modo I2C)
- 1x Tarjeta NFC compatible (NFC-A / ISO14443A)
- Jumpers dupont
- (Opcional) Protoboard
- (Opcional) LED/Relay para simular “maquinaria”

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
- Asegura que el PN532 esté en modo I2C (algunos módulos tienen switch/jumpers).
- Si el módulo no responde, revisa alimentación, GND común y cables SDA/SCL.

------------------------------------------------------------
5) Librerías / Entorno
------------------------------------------------------------
- Arduino IDE
- Librerías:
  * Wire.h
  * Adafruit_PN532.h (Adafruit PN532)

------------------------------------------------------------
6) ¿Cómo funciona la validación?
------------------------------------------------------------
- El PN532 lee el UID de la tarjeta.
- El programa compara el UID leído con un UID autorizado (tarjetaAutorizada[]).
- Si coinciden:
    * Imprime "ACCESO CONCEDIDO"
    * Simula "MAQUINARIA ENCENDIDA"
- Si NO coinciden:
    * Imprime "ACCESO DENEGADO"
    * Simula "MAQUINARIA APAGADA"

------------------------------------------------------------
7) Código (resumen de partes importantes)
------------------------------------------------------------
A) Lectura del UID (tipo ISO14443A):
- readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLen, 1000);

B) Impresión en bases:
- HEX: Serial.print(uid[i], HEX);
- DEC: Serial.print(uid[i], DEC);
- BIN: se imprime bit por bit con (uid[i] >> b) & 1

C) Validación:
- Se revisa que el UID sea de 4 bytes y se compara con tarjetaAutorizada[4]

D) Simulación de maquinaria:
- Mensajes por Serial
- (Opcional) salida digital en un pin (ej. GPIO2)

------------------------------------------------------------
8) Salida esperada (ejemplo)
------------------------------------------------------------
HEX (Base 16): 3D:3C:FD:06
DEC (Base 10): 61-60-253-6
BIN (Base  2): 00111101 00111100 11111101 00000110

ACCESO CONCEDIDO
Simulación: MAQUINARIA ENCENDIDA

(Con una tarjeta no autorizada:)
ACCESO DENEGADO
Simulación: MAQUINARIA APAGADA

------------------------------------------------------------
9) Cómo usar (pasos rápidos)
------------------------------------------------------------
1) Conecta PN532 a ESP32 (sección 4).
2) Abre Arduino IDE e instala la librería Adafruit PN532 si hace falta.
3) Carga el sketch en la ESP32.
4) Abre Monitor Serial a 115200 baudios.
5) Acerca una tarjeta NFC:
   - Verifica el UID en HEX/DEC/BIN
   - Verifica si da acceso o lo deniega

TIP:
Si quieres autorizar tu tarjeta, primero lee su UID y luego reemplaza:
uint8_t tarjetaAutorizada[4] = { ... };

------------------------------------------------------------
10) Evidencias
------------------------------------------------------------
- Foto del montaje (ESP32 + PN532)
- Captura del monitor serial mostrando:
  * UID en HEX/DEC/BIN
  * Mensaje de acceso concedido/denegado
  * Simulación de maquinaria

------------------------------------------------------------
11) Enlaces (GitHub y Video)
------------------------------------------------------------
GitHub:
- [PEGA AQUI TU LINK DE GITHUB]

Video:
- [PEGA AQUI TU LINK DEL VIDEO]

------------------------------------------------------------
12) Problemas comunes (rápido)
------------------------------------------------------------
- "ERROR: PN532 no encontrado."
  * Revisa VCC/GND
  * Revisa modo I2C
  * Revisa SDA/SCL (GPIO21/GPIO22)
  * Cambia cables si es necesario

- No hay salida en Monitor Serial
  * Revisa baudrate: 115200
  * Verifica puerto correcto (COM/USB)


