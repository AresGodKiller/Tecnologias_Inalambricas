============================================================
README – Práctica: Control de Acceso con NFC / RFID
ESP32 + PN532 + Comunicación por Puerto COM
============================================================

Nombre de la práctica:
Lectura y Validación de Tarjetas NFC/RFID para Control de Acceso

Materia:
Tecnologías Inalámbricas

Fecha:
Abril 2026

Integrantes:
- Eduardo Cadengo López
- Itzel Citlalli Martell De La Cruz
- Damian Alexander Díaz Piña

------------------------------------------------------------
DESCRIPCIÓN DE LA PRÁCTICA
------------------------------------------------------------
En esta práctica se desarrolla un sistema de control de acceso
utilizando tecnología NFC/RFID. El sistema está basado en una
ESP32 como microcontrolador y un módulo NFC PN532 configurado en
modo I2C.

El objetivo principal es leer el UID (Identificador Único) de una
tarjeta NFC o RFID, mostrarlo en diferentes bases numéricas y
utilizarlo como identificador para permitir o denegar el acceso
a un proceso, simulando aplicaciones reales como cerraduras
electrónicas o el inicio y término de operaciones.

Además, la ESP32 envía la información de la tarjeta en formato
JSON a través del puerto COM, para que pueda ser leída y mostrada
desde un programa externo desarrollado en Python.

------------------------------------------------------------
OBJETIVO DE LA PRÁCTICA
------------------------------------------------------------
El objetivo se considera cumplido cuando:

- El sistema detecta una tarjeta NFC/RFID.
- El UID de la tarjeta se muestra en el Monitor Serial.
- El UID se presenta en Base 16, Base 10 y Base 2.
- Se valida el UID para conceder o denegar el acceso.
- Los datos son recuperados desde el puerto COM mediante un
  lenguaje de programación externo.

------------------------------------------------------------
TECNOLOGÍA RFID / NFC
------------------------------------------------------------
RFID (Radio Frequency Identification) es una tecnología que
permite identificar objetos o personas utilizando radiofrecuencia.

NFC (Near Field Communication) es una variante de RFID de alta
frecuencia (13.56 MHz) diseñada para comunicación a corta
distancia. Está basada en normas como ISO/IEC 14443 y es común en
sistemas de acceso, pagos sin contacto y credenciales digitales.

------------------------------------------------------------
MÓDULO UTILIZADO: PN532
------------------------------------------------------------
El PN532 es un controlador NFC que permite la lectura de tarjetas
sin contacto. Soporta los protocolos ISO14443A y puede comunicarse
con microcontroladores mediante I2C, SPI o UART.

En esta práctica se utiliza en modo lector mediante I2C para
detectar tarjetas NFC tipo A y obtener su UID.

------------------------------------------------------------
MATERIALES UTILIZADOS
------------------------------------------------------------
- ESP32 (DevKit o similar)
- Módulo NFC PN532 (modo I2C)
- Tarjeta NFC/RFID compatible (ISO14443A)
- Cables Dupont
- Protoboard (opcional)
- LED o relé para simular acceso (opcional)

------------------------------------------------------------
CONEXIONES (ESP32 <-> PN532) [I2C]
------------------------------------------------------------
ESP32            PN532
--------------------------------
3V3   ----------> VCC
GND   ----------> GND
GPIO21 ----------> SDA
GPIO22 ----------> SCL

Salida de control:
GPIO2 ----------> LED o relé

NOTA:
Es indispensable verificar que el módulo PN532 esté configurado
en modo I2C.

------------------------------------------------------------
ENTORNO DE DESARROLLO
------------------------------------------------------------
- Arduino IDE
- Librerías empleadas:
  - Wire.h
  - Adafruit_PN532.h

------------------------------------------------------------
FUNCIONAMIENTO DEL SISTEMA
------------------------------------------------------------
1. La ESP32 inicializa la comunicación serial y el módulo PN532.
2. El lector NFC espera la presencia de una tarjeta.
3. Al detectar una tarjeta, se lee su UID.
4. El UID se muestra en el Monitor Serial en:
   - Base 16 (HEX)
   - Base 10 (DEC)
   - Base 2 (BIN)
5. El UID se compara con una lista de tarjetas autorizadas.
6. Si la tarjeta está autorizada:
   - Se concede el acceso
   - Se activa una salida digital
7. Si no está autorizada:
   - Se deniega el acceso
8. La información se envía por el puerto COM en formato JSON.

------------------------------------------------------------
FORMATO DE DATOS ENVIADOS POR SERIAL (JSON)
------------------------------------------------------------
Ejemplo de salida:

{
  "hex":"49:1C:33:07",
  "dec":12345678,
  "bin":"01001001 00011100 00110011 00000111",
  "acceso":true
}

------------------------------------------------------------
LECTURA DEL PUERTO COM DESDE PYTHON
------------------------------------------------------------
Se utiliza un programa en Python (lector_com.py) que permite:

- Abrir el puerto COM asignado a la ESP32
- Leer las tramas enviadas por Serial
- Decodificar los datos JSON
- Mostrar el UID y el estado de acceso en pantalla

Esto permite integrar el sistema con aplicaciones de escritorio
o plataformas web.

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
- El PN532 no es detectado:
  - Revisar conexiones VCC y GND
  - Verificar modo I2C
  - Revisar pines SDA y SCL

- No aparecen datos en el Monitor Serial:
  - Verificar baudrate (115200)
  - Confirmar el puerto COM correcto

------------------------------------------------------------
EVIDENCIAS
------------------------------------------------------------

GitHub del proyecto: 
https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/NFC_RFID_COM_APP_BD

Video de demostración: 
https://youtube.com/shorts/i_WNlqsTOLc

