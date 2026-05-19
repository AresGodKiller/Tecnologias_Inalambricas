#include <WiFi.h>
#include <DNSServer.h>
#include <WebServer.h>

// Variables de configuracion del sistema
// Aqui defines el nombre de la red, la contrasena y la IP que va a tener el ESP32
// Si quieres cambiar algo de la red, este es el unico lugar donde tienes que hacerlo
const char* SSID_RED   = "Hotel_WiFi_SIxSEven";  // Nombre visible de la red WiFi
const char* PASS_RED   = "";                       // Vacio significa red abierta, sin contrasena
const IPAddress IP_AP(192, 168, 4, 1);             // Direccion IP local del ESP32 en la red
const byte     DNS_PORT = 53;                      // Puerto 53 es el estandar del protocolo DNS

// Objetos globales que manejan el DNS y el servidor web
DNSServer  dnsServer;
WebServer  server(80);  // El servidor web escucha en el puerto 80, que es el de HTTP

// Pagina HTML del portal cautivo almacenada en la Flash del ESP32
// Se usa PROGMEM para no gastar RAM con este bloque de texto tan largo
// La RAM del ESP32 es limitada, por eso es mejor dejar los datos grandes en la Flash
const char PORTAL_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Hotel WiFi</title>
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{
      background:#09090f;
      min-height:100vh;
      display:flex;
      flex-direction:column;
      align-items:center;
      justify-content:center;
      font-family:-apple-system,'Helvetica Neue',sans-serif;
      color:#e8e0d0;
      padding:24px;
    }
    .card{
      background:#12121a;
      border:1px solid #2a2620;
      border-radius:20px;
      padding:36px 28px;
      width:100%;
      max-width:360px;
      text-align:center;
    }
    .icono{
      width:58px;height:58px;
      margin:0 auto 20px;
      background:#c9a96e15;
      border:1px solid #c9a96e44;
      border-radius:50%;
      display:flex;align-items:center;justify-content:center;
    }
    .icono svg{width:28px;height:28px;fill:none;stroke:#c9a96e;stroke-width:2;stroke-linecap:round;}
    h1{
      font-family:Georgia,'Times New Roman',serif;
      font-size:22px;font-weight:normal;
      letter-spacing:.12em;color:#c9a96e;
      text-transform:uppercase;margin-bottom:4px;
    }
    .sub{
      font-size:10px;letter-spacing:.25em;
      color:#5a5040;text-transform:uppercase;margin-bottom:28px;
    }
    hr{border:none;height:1px;background:#1e1c18;margin-bottom:24px;}
    label{
      display:block;font-size:10px;letter-spacing:.18em;
      text-transform:uppercase;color:#6a5f4a;
      margin-bottom:7px;text-align:left;
    }
    input[type=text]{
      width:100%;background:#0d0d14;
      border:1px solid #2a2620;border-radius:10px;
      color:#e8e0d0;font-size:15px;
      padding:13px 15px;margin-bottom:14px;
      outline:none;-webkit-appearance:none;
    }
    input[type=text]:focus{border-color:#c9a96e55;}
    input[type=text]::placeholder{color:#2e2820;}
    .check-row{
      display:flex;align-items:flex-start;
      gap:10px;margin-bottom:22px;text-align:left;
    }
    .check-row input{width:16px;height:16px;margin-top:3px;flex-shrink:0;accent-color:#c9a96e;}
    .check-row span{font-size:12px;color:#5a5040;line-height:1.5;}
    .btn{
      width:100%;background:#c9a96e;color:#09090f;
      border:none;border-radius:10px;
      font-size:13px;font-weight:700;
      letter-spacing:.18em;text-transform:uppercase;
      padding:15px;cursor:pointer;
    }
    .btn:active{opacity:.85;}
    .pie{margin-top:18px;font-size:11px;color:#2e2820;letter-spacing:.04em;}
  </style>
</head>
<body>
  <div class="card">
    <div class="icono">
      <svg viewBox="0 0 24 24">
        <path d="M1.5 8.5a14.5 14.5 0 0 1 21 0"/>
        <path d="M5 12a11 11 0 0 1 14 0"/>
        <path d="M8.5 15.5a6.5 6.5 0 0 1 7 0"/>
        <circle cx="12" cy="19" r="1" fill="#c9a96e"/>
      </svg>
    </div>
    <h1>Grand Hotel</h1>
    <p class="sub">Acceso a Internet &mdash; Wi-Fi</p>
    <hr>
    <form method="GET" action="/conectar">
      <label>Nombre del huesped</label>
      <input type="text" name="nombre" placeholder="Tu nombre" required>
      <label>Numero de habitacion</label>
      <input type="text" name="habitacion" placeholder="Ej. 204" required>
      <div class="check-row">
        <input type="checkbox" id="t" required>
        <span>Acepto los <a style="color:#c9a96e88">terminos de uso</a> de la red del hotel.</span>
      </div>
      <button class="btn" type="submit">Conectar</button>
    </form>
    <p class="pie">Velocidad hasta 20 Mbps &bull; Soporte: ext. 0</p>
  </div>
</body>
</html>
)rawliteral";

// Pagina de bienvenida que se muestra despues de llenar el formulario
// Los marcadores %NOMBRE% y %HABITACION% se reemplazan con los datos del usuario antes de enviarse
const char BIENVENIDA_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Conectado</title>
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{
      background:#09090f;min-height:100vh;
      display:flex;align-items:center;justify-content:center;
      font-family:-apple-system,'Helvetica Neue',sans-serif;
      color:#e8e0d0;padding:24px;
    }
    .card{
      background:#12121a;border:1px solid #2a2620;
      border-radius:20px;padding:44px 28px;
      width:100%;max-width:360px;text-align:center;
    }
    .ok{
      width:64px;height:64px;margin:0 auto 24px;
      background:#c9a96e18;border:1px solid #c9a96e55;
      border-radius:50%;display:flex;align-items:center;justify-content:center;
    }
    .ok svg{width:30px;height:30px;fill:none;stroke:#c9a96e;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;}
    h1{font-family:Georgia,serif;font-size:20px;font-weight:normal;color:#c9a96e;letter-spacing:.1em;margin-bottom:10px;}
    p{font-size:13px;color:#5a5040;line-height:1.6;}
    .nombre{color:#c9a96e;font-size:17px;font-weight:600;margin:14px 0 4px;}
    .hab{font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:#3a3020;}
  </style>
</head>
<body>
  <div class="card">
    <div class="ok">
      <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
    </div>
    <h1>Bienvenido</h1>
    <p class="nombre">%NOMBRE%</p>
    <p class="hab">Habitacion %HABITACION%</p>
    <br>
    <p>Ya tienes acceso a Internet.<br>Disfruta tu estadia.</p>
  </div>
</body>
</html>
)rawliteral";

// Responde con el portal cuando alguien hace cualquier peticion a la raiz del servidor
void manejarRaiz() {
  server.send(200, "text/html", PORTAL_HTML);
}

// Esta funcion se ejecuta cuando el usuario envia el formulario del portal
// Toma el nombre y el numero de habitacion, los mete en el HTML de bienvenida y lo manda
void manejarConectar() {
  String nombre     = server.arg("nombre");
  String habitacion = server.arg("habitacion");

  // Se copia el HTML base y se reemplazan los marcadores con los datos del usuario
  // Si el campo llegara vacio, se pone un valor por defecto para que no quede en blanco
  String pagina = BIENVENIDA_HTML;
  pagina.replace("%NOMBRE%",     nombre.length()     > 0 ? nombre     : "Huesped");
  pagina.replace("%HABITACION%", habitacion.length() > 0 ? habitacion : "---");

  // Se imprime en el monitor serial para poder ver quien se conecto durante las pruebas
  Serial.println("Nuevo acceso al portal:");
  Serial.println("    Nombre:     " + nombre);
  Serial.println("    Habitacion: " + habitacion);

  server.send(200, "text/html", pagina);
}

// Si alguien intenta cargar una URL que no esta registrada, se le redirige al portal
// Esto es lo que hace que el portal aparezca solo en el dispositivo al conectarse
void manejarNoEncontrado() {
  server.sendHeader("Location", "http://192.168.4.1/", true);
  server.send(302, "text/plain", "");
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("Iniciando portal cautivo...");

  // Paso 1: Se configura el ESP32 en modo punto de acceso WiFi
  // softAPConfig define la IP del ESP32, el gateway y la mascara de subred
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(IP_AP, IP_AP, IPAddress(255, 255, 255, 0));
  WiFi.softAP(SSID_RED, PASS_RED);

  Serial.println("Red WiFi activa: " + String(SSID_RED));
  Serial.println("IP del portal:   " + IP_AP.toString());

  // Paso 2: Se inicia el servidor DNS que redirige todo el trafico hacia el ESP32
  // El asterisco como dominio significa que va a responder a cualquier nombre que se consulte
  // Esto es lo que provoca que el celular muestre el portal automaticamente al conectarse
  dnsServer.start(DNS_PORT, "*", IP_AP);

  // Paso 3: Se registran las rutas del servidor web con su funcion correspondiente
  server.on("/",         manejarRaiz);     // Ruta principal, muestra el portal
  server.on("/conectar", manejarConectar); // Ruta del formulario, procesa los datos
  server.onNotFound(manejarNoEncontrado);  // Ruta comodin, redirige cualquier otra URL

  server.begin();
  Serial.println("Servidor web listo en el puerto 80");
}

// El loop se ejecuta en ciclo continuo para mantener el sistema activo
void loop() {
  dnsServer.processNextRequest();  // Atiende las solicitudes del servidor DNS
  server.handleClient();           // Atiende las solicitudes del servidor web HTTP
}
