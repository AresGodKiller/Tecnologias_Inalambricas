#include <WiFi.h>
#include <esp_wifi.h>
#include "lwip/lwip_napt.h"
#include "lwip/tcpip.h"

// Credenciales de la red a la que el ESP32 se va a conectar (la red de tu PC o router)
const char* WIFI_SSID = "MiRedWiFi";      // Cambia esto por el nombre de tu red
const char* WIFI_PASS = "MiContrasena";   // Cambia esto por la contrasena de tu red

// Datos de la red propia que va a crear el ESP32
const char* AP_SSID  = "ESP32_ACCESPOINT_SIxSEven"; // Nombre de la red que crea el ESP32
const char* AP_PASS  = "12345678";                   // Minimo 8 caracteres para WPA2
const int   AP_CANAL = 6;                            // Canal WiFi entre 1 y 13
const int   AP_MAX_CLIENTES = 5;                     // Maximo de dispositivos al mismo tiempo

// Variables para controlar el estado de la conexion y los reintentos
bool conectadoAPC = false;
unsigned long ultimoIntento = 0;
const unsigned long INTERVALO_REINTENTO = 10000; // Tiempo en milisegundos entre cada reintento

// Intenta conectar el ESP32 a la red WiFi indicada en WIFI_SSID
// Regresa true si logro conectarse, false si no pudo despues de varios intentos
bool conectarAPC() {
  Serial.println("\n[STA] Conectando a: " + String(WIFI_SSID));
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[STA] Conectado!");
    Serial.println("[STA] IP asignada: " + WiFi.localIP().toString());
    Serial.println("[STA] Gateway:     " + WiFi.gatewayIP().toString());
    return true;
  } else {
    Serial.println("\n[STA] No se pudo conectar. Reintentando en 10s...");
    return false;
  }
}

// Levanta el punto de acceso propio del ESP32
// Usa WIFI_AP_STA para que el ESP32 funcione como cliente y como AP al mismo tiempo
void activarAP() {
  Serial.println("\n[AP] Iniciando Access Point...");

  WiFi.mode(WIFI_AP_STA); // Modo dual: el ESP32 se conecta a otra red y a la vez crea la suya

  // La IP del AP debe estar en una subred diferente a la de la red a la que se conecta
  IPAddress apIP(192, 168, 99, 1);
  IPAddress mascara(255, 255, 255, 0);
  WiFi.softAPConfig(apIP, apIP, mascara);

  WiFi.softAP(AP_SSID, AP_PASS, AP_CANAL, 0, AP_MAX_CLIENTES);

  Serial.println("[AP] Red creada: " + String(AP_SSID));
  Serial.println("[AP] IP del AP:  " + WiFi.softAPIP().toString());
}

// Activa el NAT para que los clientes del AP puedan usar internet de la red de la PC
// NAT traduce las direcciones IP para que los paquetes puedan viajar entre las dos redes
// La funcion ip_napt_enable necesita que el nucleo TCP/IP este bloqueado antes de llamarse
void activarNAT() {
  Serial.println("\n[NAT] Activando reenvio de trafico...");

  LOCK_TCPIP_CORE();
  ip_napt_enable(WiFi.softAPIP(), 1);
  UNLOCK_TCPIP_CORE();

  Serial.println("[NAT] NAT activo, los clientes ya tienen internet");
}

// Muestra en el monitor serial un resumen del estado de la red una vez que todo esta listo
void imprimirResumen() {
  Serial.println("\nResumen de red:");
  Serial.println("  Red de PC:     " + String(WIFI_SSID));
  Serial.println("  IP en esa red: " + WiFi.localIP().toString());
  Serial.println("  Red propia:    " + String(AP_SSID));
  Serial.println("  IP del ESP32:  " + WiFi.softAPIP().toString());
  Serial.println("  Clave del AP:  " + String(AP_PASS));
  Serial.println("  Conecta tu celular a: " + String(AP_SSID) + " y tendra internet");
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("ESP32 ACCESS POINT + REPETIDOR WiFi");

  // Paso 1: se levanta el AP primero para que otros dispositivos ya puedan verse
  //         aunque todavia no tengan internet hasta que el ESP32 se conecte a la PC
  activarAP();

  // Paso 2: el ESP32 intenta conectarse a la red de la PC
  conectadoAPC = conectarAPC();

  // Paso 3: si ya hay conexion, se activa el NAT para compartir internet
  if (conectadoAPC) {
    activarNAT();
    imprimirResumen();
  } else {
    Serial.println("[!] AP activo pero sin internet hasta conectar a la red");
  }
}

// El loop revisa cada cierto tiempo si el ESP32 sigue conectado a la red de la PC
// Si se perdio la conexion, intenta reconectarse automaticamente
void loop() {
  if (millis() - ultimoIntento >= INTERVALO_REINTENTO) {
    ultimoIntento = millis();

    if (WiFi.status() != WL_CONNECTED) {
      if (conectadoAPC) {
        conectadoAPC = false;
        Serial.println("\n[!] Se perdio la conexion. Reconectando...");
      }
      conectadoAPC = conectarAPC();
      if (conectadoAPC) {
        activarNAT();
        imprimirResumen();
      }
    }
  }
}

