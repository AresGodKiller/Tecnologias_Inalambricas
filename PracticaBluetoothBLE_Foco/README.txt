README – Control de un Foco por BLE con ESP32 y MIT App Inventor

Fecha: 24/02/2026

Integrantes:
Eduardo Cadengo López - 
Itzel Citlalli Martell De La Cruz - 
Damian Alexander Diaz Piña -

Links

GitHub: https://github.com/AresGodKiller/Tecnologias_Inalambricas/blob/main/PracticaBluetoothBLE_Foco

Video demostrativo: https://youtu.be/BVj0oOwOyGk

Placa utilizada y Componentes utilizados:
ESP32 (compatible con cualquier ESP32 estándar con Bluetooth BLE)
ESP32 S3 (o ESP32 DevKit)
1 Foco
1 Socket
Modulo Relevador De 1 Canal A 5v 10a Lowlevel Relay Rele Mv
Protoboard
Jumpers
Teléfono con Android (para MIT App Inventor; iOS también soportado)

Descripción del proyecto:

Este proyecto implementa un control inalámbrico vía Bluetooth (BLE) para manejar un foco conectado a un ESP32 mediante una App móvil creada en MIT App Inventor haciendo que el relevador funcione y detecte si se presiono un boton de la aplicacion para que el relevador haga la accion de permitir qu le foco prenda.

La aplicación móvil es capaz de:

Escanear dispositivos BLE cercanos.
Mostrar la lista de dispositivos encontrados.
Conectarse al ESP32.
Enviar caracteres vía BLE para encender/apagar a un foco conectado a un relevador.
La ESP32 funciona como servidor BLE (GATT Server), recibe comandos en una característica BLE y ejecuta acciones sobre el relevador para que pueda pasar la señal y así prenda el foco.

Objetivo del código:

Crear un servidor BLE en la ESP32 para recibir comandos desde la App móvil.
Enviar mensajes desde MIT App Inventor a la ESP32 mediante una característica BLE.
Controlar LEDs externos con dichos comandos (‘A’, ‘a’).
A = Es para que prenda 
a = Es para dar la señal de apagarse
Permitir conexión desde Android para utilizar la extensión BluetoothLE.


Componentes necesarios

ESP32 S3 (o ESP32 DevKit)
1 foco
1 Socket
Protoboard
Modulo Relevador De 1 Canal A 5v 10a Lowlevel Relay Rele Mv
Jumpers
Teléfono con Android (para MIT App Inventor; iOS también soportado)


Lógica del programa
1. Inicialización

Se configura BLE con:
Service UUID: 12345678-1234-1234-1234-1234567890ab
Characteristic UUID: abcd1234-5678-1234-5678-abcdef123456

2. Conexión desde App

La app escanea y muestra el dispositivo ESP32_EquipoSicsSeven, o cualquier nombre que se le puso al ESP.
Al conectarse:
Serial: “Conectado”
Se habilitan botones de control en la app

3. Recepción de comandos
La app envía un carácter a la característica BLE:
Comando Acción que le envia la app al esp32.
‘A’Enciende el Foco
‘a’Apaga el Foco


4. Desconexión
Serial: “Desconectado” y vuelve a buscar dispositivos nuevos
el esp32 se desconecta de la aplicación o del teléfono para que otro teléfono con la aplicación pueda conectarse

Funciones clave
MyServerCallbacks: Maneja conexión/desconexión.
MyCallbacks: Recibe caracteres de la app y ejecuta acciones.
setEstado(): Controla el estado del Foco('A', 'a') para ver si esta prendido o apagado.
setLedByCommand(): Ejecuta comando recibido (“A”, “a”).


Cómo usar la App en MIT App Inventor:

Instalar extensión BluetoothLE.

Agregar componentes:
BluetoothLE1
ListView para dispositivos
Botones de control (A y a)


Escanear luego seleccionar ESP32 y conectarlo conectar
La interfaz cambia a botones de control
Cada botón envía un carácter a la ESP32 para que se pueda prender o apagar a foco que este conectado el relevador


Configuración BLE para el Funcionamiento de la practica:
Callbacks para conexión/desconexión
Interpretación de comandos BLE
Control de el foco
Mensajes por monitor serial para ver si se recibió el el dato de la aplicación al el ESP


Cómo ejecutar
Conectar ESP32 a la PC
Cargar el programa proporcionado
Abrir monitor serial (115200) para ver si manda los mensajes de conectado, desconectado o el botón que se haya presionado en la aplicación 

En MIT App Inventor:
Abrir App, luego Escanear y Conectamos el esp32
Usar los botones para encender/apagar LEDs en tiempo real


Características especiales que se usaron:
Comunicación BLE compatible con Android y iOS
App cambia automáticamente de interfaz al conectarse haciendo que ahora pase a conectado
Comandos simples (1 carácter), baja latencia
Estados visuales con Un foco

