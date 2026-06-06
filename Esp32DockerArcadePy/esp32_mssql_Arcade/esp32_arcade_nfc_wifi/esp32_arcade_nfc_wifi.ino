/*
 *  ESP32 ARCADE NFC — Modo WiFi + Serial
 *
 *  Este es el firmware final del ESP32 para el proyecto Arcade.
 *  Se encarga de dos cosas principales:
 *    1. Leer tarjetas NFC y mandar el UID a Python por puerto Serial
 *    2. Recibir el puntaje de Python por Serial y enviarlo al servidor
 *       Node.js que corre en la Mac del equipo mediante HTTP POST
 *
 *  Protocolo de comunicación Serial con Python (launcher_esp32_wifi.py):
 *    ESP32 → Python :  UID:AABBCCDD
 *    Python → ESP32 :  SCORE:AABBCCDD:150:NombreJugador:usr_jugador
 *    ESP32 → Python :  ACK:OK  (o ACK:ERROR si falló el POST)
 *
 *  Conexiones físicas del PN532 en modo I2C:
 *    PN532 VCC  -> 3.3V   (no conectar a 5V, puede dañar el módulo)
 *    PN532 GND  -> GND
 *    PN532 SDA  -> GPIO 21
 *    PN532 SCL  -> GPIO 22
 *    PN532 IRQ  -> GPIO 4
 *    PN532 RST  -> GPIO 5
 *
 *  IMPORTANTE — Jumpers del PN532:
 *    SEL0 (SW1) → ON
 *    SEL1 (SW2) → ON
 *    Los dos en ON = modo I2C. En cualquier otra combinación
 *    el módulo no responde por I2C aunque el cableado esté bien.
 *
 *  Librerías que hay que instalar desde el Library Manager:
 *    - Adafruit PN532   (by Adafruit)
 *    - ArduinoJson      (by Benoit Blanchon)
 *    - Wire             (ya viene incluida)
 *    - WiFi, HTTPClient (ya vienen incluidas con el soporte de ESP32)
 */

// Librerías para conectarse a WiFi y hacer peticiones HTTP
#include <WiFi.h>
#include <HTTPClient.h>

// Librería para construir y leer JSON de manera sencilla
#include <ArduinoJson.h>

// Librerías para comunicarse con el módulo NFC por I2C
#include <Wire.h>
#include <Adafruit_PN532.h>



//  CONFIGURACIÓN — ajustar estos valores antes de correr el codigo porque puede cambiar la red wifi o el de la computadore donde se encuentre el servidor corriendo


// Credenciales de la red WiFi a la que se va a conectar el ESP32
const char* WIFI_SSID     = "TP-Link_3262";
const char* WIFI_PASSWORD = "99428167";

// IP de la Mac donde corre server.js (puerto 3000).
// Si la Mac tiene una IP diferente en tu red, cambiar este valor.
const char* SERVER_IP   = "192.168.0.104";
const int   SERVER_PORT = 3000;

// URL base del servidor, se construye con la IP y el puerto de arriba
const char* API_BASE = "http://192.168.0.104:3000";


//  PINES


// Pines del módulo PN532 conectados al ESP32
#define PN532_IRQ_PIN   4    // Interrupción: el PN532 avisa cuando detecta una tarjeta
#define PN532_RST_PIN   5    // Reset del PN532, útil si el módulo se cuelga
#define I2C_SDA_PIN    21    // Línea de datos del bus I2C (estándar en el ESP32)
#define I2C_SCL_PIN    22    // Línea de reloj del bus I2C (estándar en el ESP32)

// LED integrado del ESP32 (GPIO 2 = LED azul en la mayoría de módulos genéricos)
// Si usas un ESP32-S3, cambiar este valor a 48
#define LED_PIN         2

// Tiempo mínimo en milisegundos entre lecturas de la misma tarjeta.
// Evita que si el jugador deja la tarjeta pegada al lector se mande
// el UID muchas veces seguidas.
#define COOLDOWN_MS   4000



//  VARIABLES GLOBALES QUE SE USAN PARA DEPSUES SUBIRLOS A LA BASE DE DATOS

// Estructura para guardar los datos del puntaje que manda Python.
// Agrupa todo en un solo objeto para que sea más fácil pasarlo entre funciones.
struct ScoreData {
  String rfid;        // UID de la tarjeta del jugador
  int    puntos;      // Puntos ganados en esa sesión
  String name_disp;   // Nombre del jugador tal como aparece en el juego
  String usr;         // Nombre de usuario (sin espacios, para la base de datos)
  bool   valido;      // Indica si el mensaje se parseó correctamente
};

// Objeto principal para interactuar con el módulo PN532
Adafruit_PN532 nfc(PN532_IRQ_PIN, PN532_RST_PIN);

// Guarda el UID de la última tarjeta leída para aplicar el cooldown
String        lastRFID     = "";
unsigned long lastReadTime = 0;

// Bandera que indica si el módulo NFC se inicializó bien en el setup
bool nfcOK = false;



//  LED — funciones de ayuda para ver si el esp32 funciona pero el juego de python no


void ledOn()  { digitalWrite(LED_PIN, HIGH); }
void ledOff() { digitalWrite(LED_PIN, LOW);  }

// Hace parpadear el LED una cantidad de veces con un intervalo dado.
// Se usa para dar retroalimentación visual sin pantalla:
//   - pocos destellos lentos = éxito
//   - muchos destellos rápidos = error
void flashLED(int veces, int ms) {
  for (int i = 0; i < veces; i++) {
    ledOn();  delay(ms);
    ledOff(); delay(ms);
  }
}



//  WiFi, conectar con reintentos


// Conecta el ESP32 a la red WiFi configurada arriba.
// Intenta hasta 30 veces con medio segundo de espera entre cada intento
// (15 segundos en total). Si no logra conectarse, el ESP32 sigue funcionando
// en modo Solo-Serial pero no podrá hacer peticiones HTTP al servidor.
void conectarWifi() {
  Serial.printf("\nConectando a WiFi: %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);              // Modo estación: cliente de un router existente
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 30) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    // Muestra la IP que le asignó el router al ESP32
    Serial.printf("\nWiFi OK — IP: %s\n", WiFi.localIP().toString().c_str());
    flashLED(5, 80);  // 5 destellos rápidos = WiFi conectado
  } else {
    Serial.println("\nERROR: No se pudo conectar al WiFi.");
    Serial.println("Revisa WIFI_SSID y WIFI_PASSWORD en el codigo.");
    // El ESP32 continúa sin WiFi; solo leerá tarjetas pero no enviará scores
    flashLED(10, 50);
  }
}



//  HTTP POST → /api/puntuaciones

// Envía el puntaje del jugador al servidor Node.js usando HTTP POST.
// El servidor recibe los datos, busca al jugador en la base de datos
// y suma los puntos nuevos a su acumulado histórico.
//
// Retorna true si el servidor respondió con 200 o 201 (éxito),
// false si hubo cualquier otro error.
bool enviarScoreAlServidor(String rfid, int puntos, String name_disp, String usr) {

  // Si no hay WiFi, intentar reconectar antes de fallar
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] Sin WiFi, intentando reconectar...");
    conectarWifi();
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("[HTTP] ERROR: No hay WiFi, no se pudo enviar el score.");
      return false;
    }
  }

  // Construir la URL completa del endpoint
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/puntuaciones";

  // Armar el JSON con los datos del jugador usando ArduinoJson
  StaticJsonDocument<256> doc;
  doc["id_rfid"]   = rfid;
  doc["score"]     = puntos;
  doc["name_disp"] = name_disp;
  doc["usr"]       = usr;

  String payload;
  serializeJson(doc, payload);  // Convierte el objeto a texto JSON

  Serial.printf("[HTTP] POST %s\n", url.c_str());
  Serial.printf("[HTTP] Body: %s\n", payload.c_str());

  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(payload);

  if (httpCode > 0) {
    // El servidor respondió algo (puede ser 200, 201, 500, etc.)
    String respuesta = http.getString();
    Serial.printf("[HTTP] Respuesta %d: %s\n", httpCode, respuesta.c_str());
    http.end();
    return (httpCode == 200 || httpCode == 201);
  } else {
    // Error de conexión (timeout, servidor caído, etc.)
    Serial.printf("[HTTP] ERROR: %s\n", http.errorToString(httpCode).c_str());
    http.end();
    return false;
  }
}

//  Leer tarjeta NFC

// Intenta detectar una tarjeta NFC durante 100ms.
// Si encuentra una, convierte los bytes del UID a un String
// hexadecimal en mayúsculas (ejemplo: "A4B3C201") y lo retorna.
// Si no hay ninguna tarjeta cerca, retorna un String vacío.
String leerNFC() {
  uint8_t uid[7];       // Buffer para los bytes del UID (máximo 7 bytes)
  uint8_t uidLen = 0;   // Cuántos bytes tiene el UID de esta tarjeta

  // Espera hasta 100ms por una tarjeta tipo ISO 14443A (Mifare y similares)
  bool found = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLen, 100);
  if (!found || uidLen == 0) return "";

  // Convierte cada byte a su representación hexadecimal de 2 dígitos
  String rfid = "";
  for (uint8_t i = 0; i < uidLen; i++) {
    if (uid[i] < 0x10) rfid += "0";  // Padding: asegura que sean siempre 2 dígitos
    rfid += String(uid[i], HEX);
  }
  rfid.toUpperCase();  // Siempre en mayúsculas para que coincida con lo que hay en la BD
  return rfid;
}


//  Parsear mensaje SCORE de Python

// Recibe una línea de texto con el formato:
//   SCORE:RFID:puntos:name_disp:usr
//   Ejemplo: SCORE:AABB1122:150:Juan Perez:Juan_Perez
//
// Separa cada campo usando ':' como delimitador y llena un struct ScoreData.
// Si el mensaje no tiene el formato correcto, retorna el struct con valido=false
// para que el loop lo ignore sin crashear.
ScoreData parsearScore(String linea) {
  ScoreData d;
  d.valido = false;

  // Verificar que el mensaje empiece con "SCORE:" antes de procesar
  if (!linea.startsWith("SCORE:")) return d;
  linea = linea.substring(6);  // Quitar el prefijo "SCORE:"

  // Primer campo: RFID
  int idx1 = linea.indexOf(':');
  if (idx1 < 0) return d;
  d.rfid = linea.substring(0, idx1);
  linea  = linea.substring(idx1 + 1);

  // Segundo campo: puntos
  int idx2 = linea.indexOf(':');
  if (idx2 < 0) return d;
  d.puntos = linea.substring(0, idx2).toInt();
  linea    = linea.substring(idx2 + 1);

  // Tercer y cuarto campo: name_disp y usr
  int idx3 = linea.indexOf(':');
  if (idx3 < 0) {
    // Si no hay más ':', usar el mismo valor para name_disp y usr
    d.name_disp = linea;
    d.usr       = linea;
  } else {
    d.name_disp = linea.substring(0, idx3);
    d.usr       = linea.substring(idx3 + 1);
  }

  // El mensaje es válido si tiene RFID y los puntos son un número no negativo
  d.valido = (d.rfid.length() > 0 && d.puntos >= 0);
  return d;
}

//  SETUP — se ejecuta una sola vez al arrancar o al resetear

void setup() {
  Serial.begin(115200);  // Velocidad del monitor serial y comunicación con Python
  delay(500);            // Pausa para que el Serial se estabilice antes de imprimir

  pinMode(LED_PIN, OUTPUT);
  ledOff();  // Arrancar con el LED apagado

  Serial.println("\n");
  Serial.println("  ESP32 Arcade NFC — WiFi + NFC ");
  Serial.println(" ");

  // Paso 1: Conectar a WiFi
  conectarWifi();

  // Paso 2: Inicializar el bus I2C con los pines definidos
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

  // Paso 3: Inicializar el módulo PN532 y verificar que responda
  nfc.begin();
  uint32_t fw = nfc.getFirmwareVersion();

  // Si fw viene en 0, el PN532 no respondió. Las causas más comunes son:
  // cableado incorrecto, jumpers en modo SPI o UART en vez de I2C, o
  // alimentación a 5V en lugar de 3.3V.
  if (!fw) {
    Serial.println("ERROR: PN532 no detectado.");
    Serial.println("Revisa cables SDA/SCL y jumpers en modo I2C (ambos ON)");
    // Parpadeo infinito de 1 destello lento = error de NFC
    while (true) {
      flashLED(1, 100);
      delay(400);
    }
  }

  // Mostrar la versión del firmware del PN532 como confirmación visual
  Serial.printf("PN532 OK — Firmware v%d.%d\n",
                (fw >> 16) & 0xFF, (fw >> 8) & 0xFF);

  // SAMConfig configura el PN532 para operar en modo normal de lectura de tarjetas
  nfc.SAMConfig();
  nfcOK = true;

  flashLED(3, 100);  // 3 destellos = NFC inicializado correctamente
  Serial.println("Listo. Acerca tu tarjeta NFC...\n");
  ledOn();  // LED fijo encendido = el sistema está esperando una tarjeta
}

//  LOOP — se repite continuamente mientras el ESP32 esté encendido

void loop() {
  // Si el NFC no arrancó bien, no hay nada que hacer
  if (!nfcOK) return;

  // ── Parte A: Revisar si Python mandó un SCORE por Serial ──
  // Python puede mandar el puntaje en cualquier momento después de que
  // el jugador termine una partida, así que revisamos el Serial primero.
  if (Serial.available()) {
    String linea = Serial.readStringUntil('\n');
    linea.trim();  // Quitar espacios y saltos de línea al inicio y al final

    if (linea.startsWith("SCORE:")) {
      Serial.printf("[Serial] Recibido: %s\n", linea.c_str());
      ScoreData d = parsearScore(linea);

      if (d.valido) {
        Serial.printf("[Score] RFID=%s | Pts=%d | Nombre=%s\n",
                      d.rfid.c_str(), d.puntos, d.name_disp.c_str());

        flashLED(3, 100);  // 3 destellos = procesando el score

        // Intentar enviar el score al servidor Node.js
        bool ok = enviarScoreAlServidor(d.rfid, d.puntos, d.name_disp, d.usr);

        if (ok) {
          Serial.println("[Score] ✓ Score enviado al servidor correctamente.");
          Serial.println("ACK:OK");    // Python lee este mensaje para confirmar el envío
          flashLED(5, 80);             // 5 destellos rápidos = éxito
        } else {
          Serial.println("[Score] ✗ ERROR al enviar score.");
          Serial.println("ACK:ERROR"); // Python lee este mensaje para saber que falló
          flashLED(2, 400);            // 2 destellos lentos = error
        }

        ledOn();  // Volver a estado de espera con LED encendido
      } else {
        // El mensaje llegó con formato incorrecto, se ignora para no crashear
        Serial.println("[Serial] Mensaje SCORE inválido, ignorado.");
      }
    }
    // Cualquier otro mensaje que no sea SCORE: se descarta
    return;
  }

  // ── Parte B: Intentar leer una tarjeta NFC ──
  // Solo llega aquí si no había nada en el Serial
  String rfid = leerNFC();

  if (rfid == "") {
    // No hay tarjeta cerca, esperar un poco antes de volver a intentar
    delay(50);
    return;
  }

  unsigned long ahora = millis();

  // Cooldown: si es la misma tarjeta y no pasó suficiente tiempo, ignorarla.
  // Esto evita mandar el UID varias veces si el jugador deja la tarjeta pegada.
  if (rfid == lastRFID && (ahora - lastReadTime) < COOLDOWN_MS) {
    delay(200);
    return;
  }

  // Tarjeta válida y fuera del cooldown: actualizar el registro
  lastRFID     = rfid;
  lastReadTime = ahora;

  ledOff();  // Apagar LED mientras se procesa la tarjeta

  // Mandar el UID a Python por Serial en el formato que espera el launcher
  Serial.print("UID:");
  Serial.println(rfid);

  flashLED(2, 150);  // 2 destellos = tarjeta leída y UID enviado a Python
  delay(300);
  ledOn();  // Volver a estado de espera

  Serial.println("Listo para siguiente tarjeta...\n");
}
