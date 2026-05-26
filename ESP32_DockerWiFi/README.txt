README - ESP32 -> API REST Node.js -> SQL Server en Docker
===========================================================

Nombre del proyecto:
  Comunicacion ESP32 con Base de Datos SQL Server mediante API REST

Materia:
  Tecnologias Inalambricas

Fecha:
  Mayo 2026

Integrantes:
  - Eduardo Cadengo Lopez
  - Itzel Citlalli Martell De La Cruz
  - Damian Alexander Diaz Pina


DESCRIPCION GENERAL
--------------------
Este proyecto implementa un sistema de telemetria donde un microcontrolador
ESP32 envia datos periodicamente a una base de datos SQL Server que corre
dentro de un contenedor Docker, usando como capa intermedia un servidor API
REST desarrollado con Node.js.

El ESP32 se conecta a la red WiFi local, construye un objeto JSON con los
datos a registrar, y realiza una peticion HTTP POST al servidor Node.js.
El servidor recibe los datos, los valida y ejecuta un INSERT en la base de
datos SQL Server. El resultado se indica visualmente con el LED RGB de la
placa (verde = exito, rojo = error).


OBJETIVO
---------
- Establecer comunicacion WiFi desde el ESP32 hacia un servidor en la red local.
- Implementar un servidor API REST con Node.js que reciba datos del ESP32.
- Almacenar los datos recibidos en una base de datos SQL Server en Docker.
- Verificar el almacenamiento correcto consultando los registros insertados.


ARQUITECTURA DEL SISTEMA
--------------------------

  [ESP32] ---WiFi/HTTP POST---> [Servidor Node.js :3000] ---TCP 1433---> [SQL Server en Docker]

  Cada componente cumple una funcion especifica:
  - ESP32: adquisicion y envio de datos via HTTP
  - Node.js (Express): validacion de datos y ejecucion de consultas SQL
  - Docker + SQL Server 2022: almacenamiento persistente de registros


NOTA SOBRE LA IMAGEN DE DOCKER UTILIZADA
------------------------------------------
Inicialmente se intentó usar la imagen azure-sql-edge, pero el contenedor
sufrio corrupcion de datos durante el desarrollo. Al recrearlo surgieron
conflictos en el puerto 1433 que impidieron continuar con esa imagen.

Se migro a la imagen oficial mssql/server:2022-latest, que funciona sin
problemas. La diferencia tecnica principal es la ubicacion de sqlcmd:

  azure-sql-edge:        /opt/mssql-tools/bin/sqlcmd
  mssql/server:2022:     /opt/mssql-tools18/bin/sqlcmd


REQUISITOS PREVIOS
-------------------
En la computadora:
  - Docker Desktop instalado y en ejecucion
  - Node.js v18 o superior
  - npm

En Arduino IDE:
  - Soporte de placas ESP32 instalado (gestor de placas)
  - Libreria: ArduinoJson (instalar desde Library Manager)
  - Librerias incluidas: WiFi, HTTPClient


PASO 1: Crear el contenedor Docker
------------------------------------
Ejecutar en PowerShell (modo administrador):

  docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=C0NTR453N1!4" ^
    -p 1433:1433 --name pruebaDb --hostname pruebaDB ^
    -d mssql/server:2022-latest

Verificar que este corriendo:
  docker ps


PASO 2: Crear la base de datos y la tabla
------------------------------------------
En Docker Desktop, ir al contenedor pruebaDb -> pestana Exec y ejecutar:

  /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "C0NTR453N1!4" -C

Dentro de sqlcmd:
  1> create database basicos;
  2> go
  1> USE basicos;
  2> go
  1> CREATE TABLE test (
       id INT PRIMARY KEY IDENTITY(1,1),
       nombre VARCHAR(50),
       valor INT,
       temperatura FLOAT,
       fecha_creacion DATETIME DEFAULT GETDATE()
     );
  2> go

Verificar:
  1> SELECT * FROM test;
  2> go


PASO 3: Configurar el servidor Node.js
----------------------------------------
Editar servidor_api_esp32.js y asegurarse de que el bloque config sea:

  const config = {
    server: '192.168.100.145',   // IP de tu equipo en la red local
    port: 1433,
    user: 'sa',
    password: 'C0NTR453N1!4',
    database: 'basicos',
    options: {
      encrypt: false,
      trustServerCertificate: true
    }
  };

Tambien verificar que el INSERT apunte a la tabla correcta:
  INSERT INTO test (nombre, valor, temperatura) VALUES (...)

Instalar dependencias e iniciar el servidor:
  npm install
  node servidor_api_esp32.js

Salida esperada:
  Servidor API corriendo en http://0.0.0.0:3000
  Esperando conexiones de ESP32...

Probar en el navegador:
  http://192.168.100.145:3000/api/test
  Respuesta esperada: {"success":true,"message":"Conexion a MSSQL exitosa"}


PASO 4: Configurar y cargar el codigo en el ESP32
---------------------------------------------------
En el archivo esp32_mssql_Definitivo.ino, ajustar:

  const char* ssid     = "NombreDeTuRed";
  const char* password = "ContrasenaDeRed";
  const char* apiUrl   = "http://192.168.100.145:3000/api";

En Arduino IDE:
  - Board: ESP32 Dev Module (o tu placa especifica)
  - Port: el COM que aparezca al conectar el ESP32
  - Subir el sketch (Ctrl+U)

Abrir el Serial Monitor a 115200 baud para ver el estado del sistema.


PASO 5: Verificar datos en la base de datos
--------------------------------------------
En el Exec del contenedor:

  /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "C0NTR453N1!4" -C
  1> USE basicos;
  2> go
  1> SELECT * FROM test ORDER BY fecha_creacion DESC;
  2> go

Se pueden ver todos los registros que el ESP32 ha insertado.


INDICADORES LED DEL ESP32
---------------------------
  Azul parpadeando   ->  Conectando a WiFi / probando conexion BD
  Verde fijo         ->  INSERT exitoso, sistema funcionando
  Rojo fijo          ->  Error de conexion o fallo en el INSERT


ENDPOINTS DE LA API
---------------------
  GET  /api/test     Prueba de conexion a SQL Server
  POST /api/insert   Inserta un registro en la tabla test

  Cuerpo del POST (JSON):
  {
    "nombre":      "ESP32_Sensor",
    "valor":       42,
    "temperatura": 23.5
  }


PROBLEMAS COMUNES
------------------
El modulo express no se encuentra:
  -> Ejecutar: npm install

Error 500 desde el ESP32:
  -> El servidor Node.js esta corriendo pero no puede conectar a SQL Server.
  -> Verificar contrasena en config, nombre de BD y que Docker este activo.

sqlcmd no encontrado en /opt/mssql-tools/bin/:
  -> Con la imagen 2022 la ruta correcta es /opt/mssql-tools18/bin/sqlcmd

Base de datos no existe (error 18456):
  -> Ejecutar los CREATE DATABASE y CREATE TABLE del Paso 2.

ESP32 no se conecta al WiFi:
  -> Verificar SSID y contrasena. El ESP32 solo soporta redes 2.4 GHz.


ESTRUCTURA DE ARCHIVOS
-----------------------
  servidor_api_esp32.js       Servidor REST intermediario (Node.js)
  esp32_mssql_Definitivo.ino  Firmware del ESP32 (Arduino)
  package.json                Dependencias del proyecto Node.js
  README.txt                  Este archivo


REPOSITORIO Y VIDEO
------------
GitHub: https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/ESP32_DockerWiFi

YouTube Video: https://youtube.com/shorts/i1MqJNeStbQ?feature=share

