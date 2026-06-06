================================================================================
README - Centro Arcade con ESP32, NFC/RFID, WiFi y SQL Server en Docker
================================================================================

Nombre del proyecto:
  Centro Arcade con ESP32, NFC/RFID, WiFi y SQL Server en Docker

Materia:
  Tecnologías Inalámbricas (Proyecto Final)

Fecha:
  05 de Junio del 2026

Integrantes:
  - Eduardo Cadengo Lopez
  - Itzel Citlalli Martell De La Cruz
  - Damian Alexander Diaz Pina


DESCRIPCIÓN GENERAL
-------------------
Este proyecto implementa un sistema completo de Centro Arcade interactivo donde un
microcontrolador ESP32 actúa como hardware central de adquisición, comunicándose
con un lector NFC/RFID (PN532) para identificar jugadores a través de tarjetas o
llaveros de proximidad. 

El sistema se conecta de forma inalámbrica a un servidor central (Node.js) que 
gestiona las consultas y actualizaciones de puntajes acumulados en una base de 
datos SQL Server, la cual corre dentro de un contenedor Docker en una máquina Mac 
que funge como servidor para todo el salón. El entorno interactivo del videojuego 
(Snake) fue desarrollado en Python utilizando la librería gráfica tkinter.


ARQUITECTURA DEL SISTEMA Y FLUJO DE DATOS
------------------------------------------

  [ Lector PN532 ] 
         |  (I2C: GPIO 21/22)
         v
     [ ESP32 ] <--- Puerto Serial (USB) ---> [ Videojuego Python (PC) ]
         |                                             |
     (WiFi / HTTP POST)                           (HTTP GET)
         |                                             |
         +-----------------+   +-----------------------+
                           |   |
                           v   v
                 [ Servidor Node.js :3000 ]
                           |
                     (TCP Port 1433)
                           v
               [ SQL Server en Docker (Mac) ]

Flujo de Operación Correcto (Corregido):
  1. El ESP32 detecta una tarjeta NFC y lee su UID.
  2. El ESP32 convierte el UID a texto hexadecimal (con padding de ceros) y lo
     envía por puerto Serial a Python con el formato "UID:XXXX".
  3. El script de Python (launcher_esp32_wifi.py) recibe el UID y realiza una
     petición HTTP GET al servidor Node.js para verificar si el jugador ya existe.
  4. Si no existe, Python muestra una ventana de registro en la interfaz gráfica
     para capturar el nombre y usuario del nuevo jugador.
  5. El jugador disputa la partida en el videojuego Snake (snake_gui.py). Al terminar,
     Python calcula el puntaje obtenido en la sesión.
  6. Python le devuelve el puntaje obtenido al ESP32 por puerto Serial utilizando el
     formato estandarizado "SCORE:RFID:puntos:nombre:usr".
  7. El ESP32, aprovechando su conexión WiFi estable, toma el control de la red y
     realiza una petición HTTP POST hacia el servidor Node.js para guardar/acumular
     los datos.
  8. El servidor Node.js procesa la solicitud, actualiza SQL Server y responde un
     ACK (ACK:OK o ACK:ERROR) que el ESP32 transmite de vuelta a Python por Serial.

*NOTA CRÍTICA DE DISEÑO:* Inicialmente el flujo estaba invertido (Python mandaba los
datos directamente al servidor tras recibir el tag), lo que causaba graves problemas
de sincronización. El flujo definitivo delega la responsabilidad de la petición 
POST de actualización de puntaje al propio ESP32.


REQUISITOS PREVIOS
-------------------
En la computadora servidor (Mac del salón / PC):
  - Docker Desktop instalado y en ejecución.
  - Node.js v18 o superior con npm.

En la computadora de juego (PC del equipo):
  - Python 3.x instalado.
  - Librerías de Python: pyserial, requests (tkinter viene nativo).

En el Arduino IDE (para programar el ESP32):
  - Soporte para placas ESP32 instalado en el Gestor de Tarjetas.
  - Librerías necesarias:
    * Adafruit_PN532 (Lectura del chip NFC)
    * ArduinoJson (Parseo de objetos JSON)
    * WiFi.h y HTTPClient.h (Nativas de ESP32)


CONFIGURACIÓN DEL HARDWARE (ESP32 + PN532)
-------------------------------------------
El módulo lector PN532 se comunica con el ESP32 mediante el protocolo I2C:
  - Pin SDA del PN532 ----> GPIO 21 del ESP32
  - Pin SCL del PN532 ----> GPIO 22 del ESP32
  - Pines de alimentación: VCC a 5V (o 3.3V según módulo) y GND a GND.

*CONFIGURACIÓN DE JUMPERS:* Para activar el modo de operación I2C en el PN532, 
los interruptores físicos (jumpers) SEL0 y SEL1 deben estar AMBOS en la posición "ON".


PASO 1: CREAR EL CONTENEDOR DOCKER (SERVIDOR CENTRAL)
------------------------------------------------------
En la Mac central del equipo, ejecutar en la Terminal para descargar e iniciar 
la imagen de SQL Server optimizada para chips Apple Silicon (Azure SQL Edge):

  docker run -e 'ACCEPT_EULA=Y' -e 'MSSQL_SA_PASSWORD=C0NTR453N1!4' \
    -p 1433:1433 --name pruebaDb --hostname pruebaDB \
    -d mcr.microsoft.com/azure-sql-edge

Verificar el estado del contenedor:
  docker ps


PASO 2: CREACIÓN DE LA BASE DE DATOS Y TABLAS
----------------------------------------------
Acceder a la terminal interactiva del contenedor desde Docker Desktop (pestaña Exec)
o mediante la consola del sistema para ejecutar las sentencias SQL:

  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'C0NTR453N1!4'

Dentro de la interfaz de sqlcmd, ejecutar el siguiente script estructurado:

  1> CREATE DATABASE arcade_db;
  2> go
  1> USE arcade_db;
  2> go
  1> CREATE TABLE puntuaciones (
       ID INT PRIMARY KEY IDENTITY(1,1),
       NAME_DISP VARCHAR(50),
       USR VARCHAR(50),
       SCORE INT,
       LAST_GAME DATETIME DEFAULT GETDATE(),
       ID_RFID VARCHAR(50)
     );
  2> go

Para verificar la correcta creación de la tabla:
  1> SELECT * FROM puntuaciones;
  2> go


PASO 3: CONFIGURACIÓN Y CONFIGURACIÓN DEL FIREWALL (MAC)
----------------------------------------------------------
Dado que el firewall de macOS bloquea por defecto conexiones entrantes al puerto 
3000 de Node.js desde los ESP32 del salón, se deben ejecutar los siguientes comandos:

  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which node)
  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp $(which node)

Verificar la lista de aplicaciones autorizadas:
  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps


PASO 4: CONFIGURACIÓN DEL SERVIDOR NODE.JS (server.js)
-------------------------------------------------------
Verificar que las credenciales de conexión en el bloque dbConfig de `server.js` 
coincidan plenamente con los parámetros de Docker:

  const dbConfig = {
    user: 'sa',
    password: 'C0NTR453N1!4',
    server: '127.0.0.1', // Localhost porque corre en la misma máquina que Docker
    database: 'arcade_db',
    port: 1433,
    options: {
      encrypt: false,
      trustServerCertificate: true
    }
  };

Instalar dependencias locales e iniciar el servicio backend:
  npm install express mssql cors
  node server.js

Salida esperada en consola:
  Servidor API corriendo en http://0.0.0.0:3000
  Base de datos conectada exitosamente.


PASO 5: CONFIGURACIÓN DEL FIRMWARE ESP32 (esp32_mssql_Definitivo.ino)
----------------------------------------------------------------------
Antes de compilar y subir el código al ESP32 a través del Arduino IDE, se deben 
modificar las variables globales del WiFi y la IP del servidor central de la Mac:

  const char* WIFI_SSID     = "TP-Link_3262";  // Nombre de la red del salón
  const char* WIFI_PASSWORD = "99428167";      // Contraseña de la red WiFi
  const char* SERVER_IP     = "192.168.0.104"; // IP asignada a la Mac Servidor
  const int   SERVER_PORT   = 3000;            // Puerto de la API Node.js

Configuraciones en Arduino IDE:
  - Placa: ESP32 Dev Module (o modelo equivalente)
  - Puerto: Seleccionar el puerto COM asignado (ej. COM10 en Windows)
  - Velocidad del Serial Monitor: 115200 baudios

INDICADORES LED EN EL ESP32:
  - Azul parpadeando: Conectando a la red WiFi o validando sockets de red.
  - Verde fijo: Operación HTTP POST de inserción/actualización exitosa.
  - Rojo fijo: Error crítico de comunicación de red o fallo 500 en el backend.


ENDPOINTS CLAVE DE LA API (Node.js)
------------------------------------
1. GET /api/puntuaciones/:rfid
   - Propósito: Busca si el UID de la tarjeta escaneada ya cuenta con un registro.
   - Respuesta si existe: { existe: true, score: 450, usr: 'Damian' }
   - Respuesta si no existe: { existe: false, score: 0 }

2. POST /api/puntuaciones
   - Propósito: Recibe el puntaje final de la partida. Si el jugador ya existe en 
     la base de datos, suma los puntos de la sesión actual al acumulado histórico.
     Si es un jugador nuevo, realiza un INSERT inicial de registro completo.
   - Formato del cuerpo JSON enviado por el ESP32:
     {
       "id_rfid": "A3B2C5D1",
       "score": 50,
       "name_disp": "ESP32_Arcade_1",
       "usr": "Eduardo"
     }


PROBLEMAS COMUNES Y SOLUCIONES (TROUBLESHOOTING)
--------------------------------------------------
1. Error: "PN532 no detectado" en el Serial Monitor:
   -> Solución: Validar las soldaduras de los pines y cables. Asegurarse de que los 
      jumpers de configuración de protocolo del PN532 estén posicionados en ON/ON (I2C).
      Subir un sketch de escáner I2C para validar que el dispositivo responda en la 
      dirección 0x24.

2. Error HTTP -1 o Fallo de Conexión Completo desde el ESP32:
   -> Solución: El tráfico está bloqueado por firewalls. En Windows, abrir PowerShell 
      como administrador y agregar la regla:
      `New-NetFirewallRule -DisplayName 'Arcade API 3000' -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow`
      En Mac, revisar los pasos de desbloqueo de la herramienta `socketfilterfw`.

3. Desconexiones masivas o error de IP no válida:
   -> Causa: El router del salón asigna IPs dinámicas por DHCP. Al reiniciarse, la Mac 
      cambia de dirección local, inhabilitando los parámetros del ESP32.
   -> Solución: Se recomienda configurar una IP estática en la Mac servidor o realizar 
      una reserva de IP fija por dirección MAC en el panel de administración del router.

4. Error de autenticación (Código de error 18456 en Node.js):
   -> Solución: La contraseña definida al instanciar el contenedor Docker no coincide 
      con la de la constante `dbConfig` en `server.js`. Verificar que ambas coincidan 
      con 'C0NTR453N1!4'.

5. Herramienta 'sqlcmd' no encontrada en terminal de Mac:
   -> Solución: Las rutas internas varían entre las imágenes oficiales de Linux y Azure Edge. 
      Se puede rastrear con un comando find interno o, de forma más práctica, instalar 
      la herramienta oficial Azure Data Studio con interfaz gráfica para administrar la BD.

6. Pérdida de consistencia en las tarjetas de juego:
   -> Causa: Formato heterogéneo de strings al leer el UID en diferentes equipos.
   -> Solución: Forzar el método de conversión en el ESP32 aplicando padding con "0" 
      para aquellos bytes menores a 0x10 (ej. pasar un byte de valor 9 a "09" y no a "9"), 
      garantizando que la longitud del string hexadecimal sea homogénea.


ESTRUCTURA FINAL DE ARCHIVOS DEL PROYECTO
------------------------------------------
  ├── server.js                  # Lógica del servidor intermediario REST API (Node.js)
  ├── esp32_mssql_Definitivo.ino # Firmware de control del ESP32 y lector PN532 (Arduino)
  ├── launcher_esp32_wifi.py     # Coordinador de interfaz gráfica de registro y puerto Serial (Python)
  ├── snake_gui.py               # Código fuente del videojuego interactivo Snake (Python)
  ├── package.json               # Definición de scripts y dependencias del ecosistema Node.js
  └── README.txt                 # Este manual técnico de despliegue y documentación
================================================================================
