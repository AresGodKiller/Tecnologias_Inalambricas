README - Portal Cautivo con ESP32
Wifi 1 - ESP32 en modo Access Point
============================================================

Nombre del proyecto:
  Portal Cautivo con ESP32 (Hotel Grand)

Materia:
  Tecnologias Inalambricas

Fecha:
  18/05/2026

Integrantes:
  - Eduardo Cadengo Lopez
  - Itzel Citlalli Martell De La Cruz
  - Damian Alexander Diaz Pina


DESCRIPCION GENERAL
-------------------
Este proyecto implementa un portal cautivo usando unicamente una ESP32
configurada en modo Access Point (AP). Al conectarse a la red WiFi que
genera el microcontrolador, cualquier dispositivo (celular o computadora)
es redirigido automaticamente a una pagina web de bienvenida con tematica
de hotel, donde el usuario ingresa su nombre y numero de habitacion para
obtener acceso a internet.

No se necesita router, servidor externo ni conexion a internet para que
el sistema funcione. El ESP32 hace todo: crea la red, intercepta el
trafico DNS y sirve las paginas web.


OBJETIVO DE LA PRACTICA
------------------------
- Implementar un portal cautivo funcional usando solo un ESP32.
- Configurar el ESP32 en modo Access Point para crear su propia red WiFi.
- Redirigir automaticamente cualquier peticion DNS hacia la IP del ESP32.
- Mostrar una pagina de registro personalizada al usuario al conectarse.
- Generar una pantalla de bienvenida con los datos que ingreso el usuario.


TECNOLOGIA UTILIZADA
---------------------
Un portal cautivo es una pagina web que aparece automaticamente cuando
un usuario se conecta a una red WiFi, antes de que pueda navegar a
cualquier otro sitio. El truco esta en el servidor DNS: intercepta
cualquier consulta de dominio y la redirige a la IP del portal en lugar
de dejar ir al usuario a internet.

El ESP32 es un microcontrolador de Espressif Systems con WiFi y Bluetooth
integrados. Su capacidad para correr un servidor web, manejar DNS y
funcionar como Access Point al mismo tiempo lo hace perfecto para este
tipo de proyectos de red embebidos.


MATERIAL UTILIZADO
------------------
- 1x ESP32
- 1x Cable USB para programar y alimentar
- 1x Computadora con Arduino IDE instalado
- 1x Dispositivo para pruebas (celular o computadora)


CONFIGURACION DE LA RED WIFI
------------------------------
  SSID (nombre de la red):   Hotel_WiFi_SIxSEven
  Tipo de red:               Abierta (sin contrasena)
  IP del ESP32:              192.168.4.1
  Mascara de subred:         255.255.255.0
  Puerto servidor DNS:       53
  Puerto servidor web:       80


LIBRERIAS Y ENTORNO DE DESARROLLO
------------------------------------
  - Arduino IDE
  - WiFi.h        (incluida con el soporte de ESP32)
  - DNSServer.h   (incluida con el soporte de ESP32)
  - WebServer.h   (incluida con el soporte de ESP32)

No se necesitan librerias externas. Todas vienen incluidas al instalar
el soporte para ESP32 en Arduino IDE.


FUNCIONAMIENTO DEL SISTEMA
----------------------------
El sistema funciona de manera automatica desde que el ESP32 enciende:

  1. El ESP32 arranca en modo Access Point y crea la red WiFi
     "Hotel_WiFi_SIxSEven" con la IP 192.168.4.1.
  2. El usuario busca redes disponibles en su dispositivo y se conecta.
  3. El sistema operativo del dispositivo hace una prueba de conectividad.
     Esta peticion pasa por el servidor DNS del ESP32.
  4. El servidor DNS responde con la IP del ESP32 a cualquier dominio
     que se consulte, sin importar cual sea.
  5. El navegador del dispositivo carga automaticamente la pagina del portal.
  6. El usuario llena el formulario con su nombre y numero de habitacion
     y presiona el boton de conectar.
  7. El ESP32 recibe los datos, genera la pagina de bienvenida personalizada
     y la manda de vuelta al navegador.
  8. Los datos del acceso se imprimen en el monitor serial para verificacion.


ESTRUCTURA DEL CODIGO
-----------------------
El codigo esta organizado en tres partes principales:

  PORTAL_HTML       HTML del formulario de acceso, guardado en Flash con PROGMEM.
  BIENVENIDA_HTML   HTML de la pagina de bienvenida, tambien en Flash con PROGMEM.
  manejarRaiz()     Responde con el portal a cualquier peticion a la raiz.
  manejarConectar() Procesa el formulario y genera la bienvenida personalizada.
  manejarNoEncontrado() Redirige cualquier URL desconocida al portal.
  setup()           Configura el AP, el DNS y las rutas del servidor web.
  loop()            Mantiene activos el DNS y el servidor web de forma continua.

Se usa PROGMEM para guardar los HTML en la memoria Flash del ESP32 y no
desperdiciar RAM, que es un recurso limitado en el microcontrolador.


FORMATO DE SALIDA POR EL MONITOR SERIAL
-----------------------------------------
El ESP32 imprime informacion util a 115200 baudios durante su ejecucion:

  Al iniciar:
    Iniciando portal cautivo...
    Red WiFi activa: Hotel_WiFi_SIxSEven
    IP del portal:   192.168.4.1
    Servidor web listo en el puerto 80

  Al conectarse un usuario:
    Nuevo acceso al portal:
        Nombre:     Juan Perez
        Habitacion: 204


PROBLEMAS COMUNES
------------------
El portal no aparece automaticamente en el dispositivo:
  - Algunos dispositivos tardan unos segundos en detectar el portal.
  - Si no aparece solo, abrir el navegador y escribir 192.168.4.1.
  - Verificar que el dispositivo este conectado a la red correcta.

El portal tarda mas en aparecer en iOS que en Android:
  - Esto es normal. Cada sistema operativo tiene su propia forma de
    detectar portales cautivos. En iOS puede tardar entre 5 y 10 segundos.

El ESP32 no aparece en la lista de redes:
  - Verificar que el codigo se subio correctamente.
  - Abrir el monitor serial para ver si el ESP32 imprimo los mensajes de inicio.
  - Revisar que el ESP32 este alimentado correctamente por USB.

La pagina carga pero el formulario no funciona:
  - Verificar que la ruta /conectar este registrada correctamente en el setup().
  - Revisar el monitor serial para ver si llegan los datos del formulario.


ENLACES Y EVIDENCIAS
---------------------
GitHub del proyecto:
  https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/ESP32_PortalCautivo

Video de demostracion:
 https://www.youtube.com/shorts/VcKZFpCU6pw
