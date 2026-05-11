============================================================
README - EcoPoints: Sistema de Reciclaje NFC + Botón
ESP32 + Módulo PN532 (I2C) + Botón Físico
============================================================

Nombre del proyecto:
EcoPoints: Sistema de Reciclaje NFC + Botón

Materia:
Tecnologías Inalámbricas

Fecha:
10/05/2026

Integrantes:
• Eduardo Cadengo López
• Itzel Citlalli Martell De La Cruz
• Damian Alexander Diaz Piña

------------------------------------------------------------
DESCRIPCIÓN GENERAL
------------------------------------------------------------
Este proyecto implementa una recicladora inteligente. El usuario se identifica acercando su tarjeta NFC al lector, y acumula puntos cada vez que presiona el botón físico, lo cual simula el depósito de una botella. El UID de la tarjeta actúa como credencial de identidad del usuario. Si el UID ya existe en la base de datos, inicia sesión directamente; si no existe, se abre un formulario para registrar y vincular la tarjeta al nuevo usuario.

------------------------------------------------------------
OBJETIVO DE LA PRÁCTICA
------------------------------------------------------------
- Implementar una recicladora inteligente utilizando ESP32 y un módulo NFC.
- Identificar a los usuarios mediante el UID de tarjetas NFC.
- Registrar automáticamente las tarjetas nuevas en una base de datos MySQL.
- Acumular puntos por el depósito de residuos mediante la pulsación de un botón físico.

------------------------------------------------------------
TECNOLOGÍA UTILIZADA (RFID / NFC)
------------------------------------------------------------
RFID (Radio Frequency Identification) es una tecnología de identificación inalámbrica que utiliza radiofrecuencia para leer o escribir información en una etiqueta. En alta frecuencia (HF) opera a 13.56 MHz.
NFC (Near Field Communication) es una variante de RFID orientada a distancias muy cortas. Opera sobre el estándar ISO/IEC 14443, donde el lector genera el campo electromagnético y la tarjeta pasiva responde con su identificador único (UID).

------------------------------------------------------------
MATERIAL UTILIZADO
------------------------------------------------------------
- 1x ESP32
- 1x Módulo NFC PN532 (configurado en modo I2C)
- 1x Botón físico de 2 pines
- 1x Tarjeta NFC (ISO/IEC 14443A)
- Cables Dupont
- Protoboard (opcional)

------------------------------------------------------------
CONEXIONES (ESP32 <-> PN532) [I2C]
------------------------------------------------------------
ESP32        PN532
- 3.3V  ---> VCC
- GND   ---> GND
- GPIO21 ---> SDA
- GPIO22 ---> SCL

Botón (2 pines):
- GPIO25 ---> Pin A (usa INPUT_PULLUP interno)
- GND    ---> Pin B

IMPORTANTE:
- El botón no requiere resistencia pull-up externa porque el ESP32 activa su resistencia interna mediante INPUT_PULLUP.
- El firmware incluye anti-rebote (debounce) de 300 ms.

------------------------------------------------------------
LIBRERÍAS Y ENTORNO DE DESARROLLO
------------------------------------------------------------
- Arduino IDE
- Librerías utilizadas (Arduino):
  - Wire.h
  - Adafruit_PN532.h
- Python 3 (Tkinter + pyserial + mysql-connector-python)
- Base de datos MySQL (Laragon)

------------------------------------------------------------
FUNCIONAMIENTO DEL SISTEMA
------------------------------------------------------------
1. La ESP32 inicializa la comunicación serial, el módulo PN532 y configura el GPIO25 como INPUT_PULLUP.
2. El usuario acerca una tarjeta NFC a la recicladora.
3. El ESP32 construye el UID como un string hexadecimal concatenado y lo envía por el puerto serial.
4. La aplicación en Python lee el puerto serial. Si el UID existe, hace login directo; si no, abre un diálogo para registrarlo.
5. Con la sesión iniciada, el usuario presiona el botón para depositar una botella.
6. El ESP32 envía la señal del botón por puerto serial.
7. Python detecta el mensaje, inserta un registro de reciclaje en la base de datos y suma los puntos al usuario.

------------------------------------------------------------
FORMATO DE SALIDA (PUERTO COM)
------------------------------------------------------------
Eventos enviados por el ESP32 a Python a 115200 baudios:
- Al leer una tarjeta: UID CONCATENADO:XXXXXXXX
- Al presionar el botón: BOTON:1

------------------------------------------------------------
LECTURA DESDE PYTHON
------------------------------------------------------------
Se incluye un programa en Python (app_reciclaje_nfc_v2.py) que gestiona toda la lógica del sistema mediante una interfaz gráfica de escritorio con Tkinter. Este programa escucha el puerto serial en un hilo paralelo (daemon thread) para no bloquear la interfaz y gestiona la conexión a la base de datos MySQL (nfc_reciclaje).

------------------------------------------------------------
SALIDA ESPERADA (EJEMPLO)
------------------------------------------------------------
UID CONCATENADO:0D1B1207
BOTON:1

------------------------------------------------------------
PROBLEMAS COMUNES
------------------------------------------------------------
- PN532 no detectado:
  - Revisar alimentación y GND
  - Revisar pines SDA (21) y SCL (22)

- Lecturas múltiples de la misma tarjeta:
  - El firmware tiene un cooldown de 2500 ms, mantener la tarjeta alejada del lector tras el primer registro.

- No hay conexión a la base de datos:
  - Verificar que Laragon esté en ejecución con MySQL activo.
  - Confirmar la instalación de mysql-connector-python.

------------------------------------------------------------
ENLACES Y EVIDENCIAS
------------------------------------------------------------
GitHub del proyecto: 
https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/NFC_reciclaje_proyecto

Video de demostración: 
https://youtu.be/eAWvPgxPVLo