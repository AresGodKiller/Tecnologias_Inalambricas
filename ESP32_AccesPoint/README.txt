README - Access Point con ESP32 + NAT
Wifi 2 - ESP32 en modo AP + STA con reenvio de internet
------------------------------------------------------------

Nombre del proyecto:
  ESP32 Access Point con NAT (Repetidor WiFi)

Materia:
  Tecnologias Inalambricas

Fecha:
  18/05/2026

Integrantes:
  - Eduardo Cadengo Lopez
  - Itzel Citlalli Martell De La Cruz
  - Damian Alexander Diaz Pina


DESCRIPCION GENERAL
--------------------
Este proyecto extiende la practica anterior del portal cautivo. Esta vez
el ESP32 funciona como un puente entre dos redes WiFi: se conecta a una
red existente (el hotspot de una laptop o un router) y al mismo tiempo
crea su propia red WiFi a la que otros dispositivos se pueden conectar.

Lo importante es que esos dispositivos no solo ven la red del ESP32,
sino que tienen acceso real a internet gracias al NAT (Network Address
Translation), que traduce las direcciones de los paquetes entre las dos
redes para que el trafico pueda fluir correctamente.

No se necesita hardware adicional. El ESP32 hace todo con su modo dual
WiFi (AP + STA) y la libreria lwip_napt que viene incluida en su core.


OBJETIVO DE LA PRACTICA
-------------------------
- Configurar el ESP32 en modo dual WiFi (AP + STA) al mismo tiempo.
- Conectar el ESP32 a una red WiFi existente con acceso a internet.
- Crear una red WiFi propia desde el ESP32 para otros dispositivos.
- Activar el NAT para que los clientes del AP tengan internet real.
- Implementar reconexion automatica si se pierde la red de la PC.


TECNOLOGIA UTILIZADA
---------------------
Un Access Point es un punto de acceso que crea una red WiFi a la que
otros dispositivos se pueden conectar. El ESP32 puede actuar como AP
y como cliente (STA) al mismo tiempo usando el modo WIFI_AP_STA, lo
que le permite estar en dos redes distintas de forma simultanea.

El NAT (Network Address Translation) es el mecanismo que permite que
varios dispositivos en una red privada compartan una sola conexion a
internet. El ESP32 toma los paquetes de los clientes de su AP, cambia
su direccion de origen por la suya propia en la red de la PC, y los
manda hacia afuera. Cuando llega la respuesta, el proceso se invierte.

La libreria lwip_napt viene incluida en el core del ESP32 desde la
version 2.0 y es la que hace posible todo esto sin hardware extra.


MATERIAL UTILIZADO
-------------------
- 1x ESP32
- 1x Cable USB para programar y alimentar
- 1x Computadora con Arduino IDE instalado y acceso a internet
- 1x Dispositivo para pruebas (celular o computadora)


CONFIGURACION DE LA RED
------------------------
  Red a la que se conecta el ESP32:
    SSID:              MiRedWiFi  (cambia esto en el codigo)
    Contrasena:        MiContrasena  (cambia esto en el codigo)

  Red que crea el ESP32:
    SSID (nombre):     ESP32_ACCESPOINT_SIxSEven
    Contrasena:        12345678
    IP del ESP32:      192.168.99.1
    Mascara de subred: 255.255.255.0
    Canal WiFi:        6
    Max. clientes:     5 dispositivos al mismo tiempo

Nota: la subred del AP (192.168.99.x) es diferente a la de la red de
la PC para evitar conflictos entre las dos redes.


LIBRERIAS Y ENTORNO DE DESARROLLO
------------------------------------
  - Arduino IDE
  - WiFi.h            (incluida con el soporte de ESP32)
  - esp_wifi.h        (incluida con el soporte de ESP32)
  - lwip/lwip_napt.h  (incluida en el core de ESP32 desde v2.0)
  - lwip/tcpip.h      (incluida con el soporte de ESP32)

No se necesitan librerias externas. Todas vienen incluidas al instalar
el soporte para ESP32 en Arduino IDE. Solo hay que verificar que la
version del core sea 2.0 o superior para que lwip_napt este disponible.


FUNCIONAMIENTO DEL SISTEMA
----------------------------
El sistema arranca de forma secuencial en el setup y luego se mantiene
activo con reconexion automatica en el loop:

  1. El ESP32 enciende y levanta su propio AP (ESP32_ACCESPOINT_SIxSEven)
     para que los dispositivos puedan verlo y conectarse desde el inicio,
     aunque todavia no tengan internet.
  2. El ESP32 intenta conectarse a la red de la PC configurada en el codigo.
     Tiene hasta 20 intentos con 500 ms de espera entre cada uno.
  3. Si logra conectarse, activa el NAT. Desde ese momento los dispositivos
     conectados al AP ya tienen acceso a internet.
  4. Si no logra conectarse al inicio, el AP queda activo pero sin internet.
     El loop reintenta la conexion cada 10 segundos automaticamente.
  5. El monitor serial muestra un resumen con las IPs y el estado de la red
     cada vez que el sistema esta listo o se reconecta.


ESTRUCTURA DEL CODIGO
-----------------------
El codigo esta organizado en funciones separadas por responsabilidad:

  conectarAPC()     Conecta el ESP32 a la red de la PC. Regresa true si
                    lo logro, false si no pudo despues de los intentos.
  activarAP()       Levanta la red WiFi propia del ESP32 en modo WIFI_AP_STA
                    con una IP fija en una subred separada.
  activarNAT()      Activa el NAT usando lwip_napt para que los clientes
                    del AP puedan acceder a internet a traves de la red PC.
  imprimirResumen() Muestra en el monitor serial las IPs y el estado de la
                    red una vez que todo esta funcionando.
  setup()           Llama a las funciones anteriores en el orden correcto.
  loop()            Monitorea la conexion y reconecta automaticamente si
                    se pierde.


FORMATO DE SALIDA POR EL MONITOR SERIAL
-----------------------------------------
El ESP32 imprime informacion a 115200 baudios durante su ejecucion:

  Al iniciar:
    ESP32 ACCESS POINT + REPETIDOR WiFi
    [AP] Iniciando Access Point...
    [AP] Red creada: ESP32_ACCESPOINT_SIxSEven
    [AP] IP del AP:  192.168.99.1
    [STA] Conectando a: MiRedWiFi
    ..................
    [STA] Conectado!
    [STA] IP asignada: 192.168.1.105
    [NAT] Activando reenvio de trafico...
    [NAT] NAT activo, los clientes ya tienen internet

  Resumen cuando todo esta listo:
    Resumen de red:
      Red de PC:     MiRedWiFi
      IP en esa red: 192.168.1.105
      Red propia:    ESP32_ACCESPOINT_SIxSEven
      IP del ESP32:  192.168.99.1
      Clave del AP:  12345678
      Conecta tu celular a: ESP32_ACCESPOINT_SIxSEven y tendra internet

  Si se pierde la conexion:
    [!] Se perdio la conexion. Reconectando...


PROBLEMAS COMUNES
------------------
El celular se conecta al AP pero no tiene internet:
  - Verificar en el monitor serial que el NAT se activo correctamente.
  - Confirmar que el ESP32 se conecto a la red de la PC (debe aparecer
    la IP asignada en el serial antes del mensaje del NAT).
  - Revisar que las credenciales de la red de la PC esten bien escritas
    en el codigo (WIFI_SSID y WIFI_PASS).

El ESP32 no aparece en la lista de redes:
  - Verificar que el codigo se subio correctamente.
  - Abrir el monitor serial para ver si el ESP32 imprimo los mensajes
    de inicio del AP.
  - Revisar que el ESP32 este alimentado correctamente por USB.

La libreria lwip_napt no se encuentra al compilar:
  - Verificar que la version del core de ESP32 en Arduino IDE sea 2.0
    o superior. En el Gestor de Placas, buscar "esp32" y actualizar.

El ESP32 se conecta a la red pero el NAT no funciona:
  - Asegurarse de que LOCK_TCPIP_CORE y UNLOCK_TCPIP_CORE esten
    envolviendo correctamente la llamada a ip_napt_enable. Sin ese
    bloqueo, el sistema lanza un error y el NAT no se activa.

La conexion se cae frecuentemente:
  - Revisar la calidad de la senal de la red a la que se conecta el ESP32.
  - El loop reintenta cada 10 segundos, pero si la senal es muy debil
    los reintentos van a fallar igual.


ENLACES Y EVIDENCIAS
---------------------
GitHub del proyecto:
  https://github.com/AresGodKiller/Tecnologias_Inalambricas/tree/main/ESP32_AccessPoint

Video de demostracion:
  https://youtube.com/shorts/9D4zA5Ziaxo?feature=share
