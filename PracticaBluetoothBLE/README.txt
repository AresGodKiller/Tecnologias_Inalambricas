README – Control de LEDs por BLE con ESP32 y MIT App Inventor

Fecha: 19/02/2026

Integrantes:
Eduardo Cadengo López - 
Itzel Citlalli Martell De La Cruz - 
Damian Alexander Diaz Piña -

Placa utilizada y Componentes utilizados:

ESP32 (compatible con cualquier ESP32 estándar con Bluetooth BLE)
ESP32 S3 (o ESP32 DevKit)
3 LEDs (Verde, Azul, Rojo)
3 resistencias de 220–330 Ω
Protoboard
Jumpers
Teléfono con Android (para MIT App Inventor; iOS también soportado)

Descripción del proyecto:

Este proyecto implementa un control inalámbrico vía Bluetooth (BLE) para manejar 3 LEDs conectados a un ESP32 mediante una App móvil creada en MIT App Inventor.

La aplicación móvil es capaz de:

Escanear dispositivos BLE cercanos.
Mostrar la lista de dispositivos encontrados.
Conectarse al ESP32.
Enviar caracteres vía BLE para encender/apagar LEDs.
La ESP32 funciona como servidor BLE (GATT Server), recibe comandos en una característica BLE y ejecuta acciones sobre los LEDs.

Objetivo del código:

Crear un servidor BLE en la ESP32 para recibir comandos desde la App móvil.
Enviar mensajes desde MIT App Inventor a la ESP32 mediante una característica BLE.
Controlar LEDs externos con dichos comandos (‘A’, ‘a’, ‘B’, ‘b’, ‘C’, ‘c’).
Permitir conexión desde Android y iOS utilizando la extensión BluetoothLE.


Componentes necesarios

ESP32 S3 (o ESP32 DevKit)
3 LEDs (Verde, Azul, Rojo)
3 resistencias de 220–330 Ω
Protoboard
Jumpers
Teléfono con Android (para MIT App Inventor; iOS también soportado)


Lógica del programa
1. Inicialización

Se configura BLE con:
Service UUID: 12345678-1234-1234-1234-1234567890ab
Characteristic UUID: abcd1234-5678-1234-5678-abcdef123456

2. Conexión desde App

La app escanea y muestra el dispositivo ESP32_EquipoSicsSeven.
Al conectarse:
Serial: “Conectado”
Se habilitan botones de control en la app

3. Recepción de comandos
La app envía un carácter a la característica BLE:
Comando Acción que le envia la app al esp32.
‘A’Enciende LED Verde
‘a’Apaga LED Verde
‘B’Enciende LED Azul
‘b’Apaga LED Azul
‘C’Enciende LED Rojo
‘c’Apaga LED Rojo

4. Desconexión
Serial: “Desconectado” y vuelve a buscar dispositivos nuevos
el esp32 se desconecta de la aplicación o del teléfono para que otro teléfono con la aplicación pueda conectarse

Funciones clave
MyServerCallbacks: Maneja conexión/desconexión.
MyCallbacks: Recibe caracteres de la app y ejecuta acciones.
setEstado(): Controla LEDs de estado (verde/azul/rojo).
setLedByCommand(): Ejecuta comando recibido (“A”, “a”, etc.).


Cómo usar la App en MIT App Inventor
Instalar extensión BluetoothLE.

Agregar componentes:
BluetoothLE1
ListView para dispositivos
Botones de control (A/a, B/b, C/c, X)


Escanear luego seleccionar ESP32 y conectarlo conectar
La interfaz cambia a botones de control
Cada botón envía un carácter a la ESP32 para que se pueda prender o apagar un led


Configuración BLE para el Funcionamiento de la practica:
Callbacks para conexión/desconexión
Interpretación de comandos BLE
Control de 3 LEDs físicos
Mensajes por monitor serial


Cómo ejecutar
Conectar ESP32 a la PC
Cargar el programa proporcionado
Abrir monitor serial (115200) para ver si manda los mensajes de conectado, desconectado y el botón que se presiono en la aplicación 

En MIT App Inventor:
Abrir App, luego Escanear y Conectamos el esp32
Usar los botones para encender/apagar LEDs en tiempo real


Características especiales que se usaron:
Comunicación BLE compatible con Android y iOS
App cambia automáticamente de interfaz al conectarse haciendo que ahora pase a conectado
Comandos simples (1 carácter), baja latencia
Estados visuales con LEDs físicos

Video demostrativo:
https://youtube.com/shorts/lvOKkD2mKzA?feature=share