============================================================
README - Control de Acceso NFC/RFID mediante una aplicacion externa
ESP32 + Módulo PN532 (I2C)
============================================================

Nombre del proyecto:
Control de Acceso NFC/RFID con ESP32 y PN532

Materia:
Tecnologías Inalámbricas

Fecha:
15/04/2026

Integrantes:
• Eduardo Cadengo López
• Itzel Citlalli Martell De La Cruz
• Damian Alexander Diaz Piña

------------------------------------------------------------
DESCRIPCIÓN GENERAL
------------------------------------------------------------
Este proyecto implementa un sistema de control de acceso utilizando una ESP32 y un módulo NFC PN532. El sistema permite leer el UID (Identificador Único) de tarjetas NFC/RFID compatibles con el estándar ISO/IEC 14443A y usar dicho UID como credencial para autorizar o denegar el acceso a un proceso.

El UID leído se muestra en el monitor serial en tres representaciones numéricas:
- Base 16 (Hexadecimal)
- Base 10 (Decimal)
- Base 2 (Binaria)

Adicionalmente, la ESP32 envía la información de la tarjeta en formato JSON a través del puerto COM, permitiendo que aplicaciones externas (por ejemplo, un programa en Python) puedan leer y procesar los datos.

------------------------------------------------------------
OBJETIVO DE LA PRÁCTICA
------------------------------------------------------------
- Leer el UID de una tarjeta NFC/RFID usando el módulo PN532.
- Mostrar el UID en bases hexadecimal, decimal y binaria.
- Validar el UID contra una lista de tarjetas autorizadas.
- Simular la apertura de una cerradura o el inicio de operaciones mediante una salida digital.
- Recuperar el número de tarjeta desde el puerto COM usando un lenguaje de programación externo.

------------------------------------------------------------
TECNOLOGÍA UTILIZADA (RFID / NFC)
------------------------------------------------------------
RFID (Radio Frequency Identification) es una tecnología de identificación inalámbrica que emplea radiofrecuencia para identificar objetos o personas mediante etiquetas electrónicas.

NFC (Near Field Communication) es una variante de RFID de alta frecuencia (13.56 MHz) diseñada para comunicaciones a corta distancia. Se basa en el estándar ISO/IEC 14443, utilizado ampliamente en sistemas de control de acceso, pagos sin contacto y credenciales electrónicas.

------------------------------------------------------------
MATERIAL UTILIZADO
------------------------------------------------------------
- 1x ESP32 (DevKit o equivalente)
- 1x Módulo NFC PN532 (configurado en modo I2C)
- 1x Tarjeta NFC compatible (NFC-A / ISO14443A)
- Cables Dupont
- Protoboard (opcional)
- LED o relé para simular una cerradura o maquinaria (opcional)

------------------------------------------------------------
CONEXIONES (ESP32 <-> PN532) [I2C]
------------------------------------------------------------
ESP32        PN532
- 3V3   ---> VCC (3.3V)
- GND   ---> GND
- GPIO21 ---> SDA
- GPIO22 ---> SCL

Salida de control:
- GPIO2 ---> LED o relé (simulación de acceso)

IMPORTANTE:
- Verificar que el módulo PN532 esté configurado en modo I2C.
- Asegurar tierra común (GND) entre la ESP32 y el módulo.

------------------------------------------------------------
LIBRERÍAS Y ENTORNO DE DESARROLLO
------------------------------------------------------------
- Arduino IDE
- Librerías utilizadas:
  - Wire.h
  - Adafruit_PN532.h

------------------------------------------------------------
FUNCIONAMIENTO DEL SISTEMA
------------------------------------------------------------
1. La ESP32 inicializa el módulo PN532 y la comunicación serial.
2. El PN532 detecta la presencia de una tarjeta NFC/RFID.
3. Se lee el UID de la tarjeta.
4. El UID se imprime en HEX, DEC y BIN en el monitor serial.
5. El sistema compara el UID con una lista de tarjetas autorizadas.
6. Si el UID coincide:
   - Se concede el acceso
   - Se activa la salida digital (LED/relé)
7. Si no coincide:
   - Se deniega el acceso
8. Los datos se envían en formato JSON por el puerto COM.

------------------------------------------------------------
FORMATO DE SALIDA JSON (PUERTO COM)
------------------------------------------------------------
Ejemplo de trama enviada:
{"hex":"49:1C:33:07","dec":12345678,"bin":"01001001 ...","acceso":true}

------------------------------------------------------------
LECTURA DESDE PYTHON
------------------------------------------------------------
Se incluye un programa en Python (lector_com.py) que:
- Abre el puerto COM asignado a la ESP32
- Lee las tramas JSON enviadas por Serial
- Muestra en pantalla el UID y el estado de acceso

Este programa puede integrarse fácilmente con aplicaciones de escritorio o web.

------------------------------------------------------------
SALIDA ESPERADA (EJEMPLO)
------------------------------------------------------------
[TARJETA DETECTADA]
Base 16 (HEX): 49:1C:33:07
Base 10 (DEC): 12234567
Base 2 (BIN): 01001001 00011100 00110011 00000111
[ACCESO CONCEDIDO]

------------------------------------------------------------
PROBLEMAS COMUNES
------------------------------------------------------------
- PN532 no detectado:
  - Revisar alimentación y GND
  - Verificar modo I2C
  - Revisar pines SDA/SCL

- No hay salida por Monitor Serial:
  - Verificar baudrate (115200)
  - Confirmar puerto COM correcto

------------------------------------------------------------
ENLACES Y EVIDENCIAS
------------------------------------------------------------
GitHub del proyecto: 
https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/NFC_RFID_COM_APP

Video de demostración: 
https://youtube.com/shorts/i_WNlqsTOLc

