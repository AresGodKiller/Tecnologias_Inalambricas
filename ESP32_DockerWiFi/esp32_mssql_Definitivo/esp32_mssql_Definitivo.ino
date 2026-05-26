// Código para ESP32 con leds o sin leds, o con sensor y sin sensor
// - Conexión a MSSQL vía servidor 
// Librerías necesarias:
// - WiFi (incluida en Arduino IDE para ESP32)
// - HTTPClient (incluida en Arduino IDE para ESP32)

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============ CONFIGURACIÓN ============
const char* ssid = "Totalplay"; // Nombre del internet al que estes conectado
const char* password = "Contraseña"; // La contraseña del internet al que estes conectado
const char* apiUrl = "http://192.168.100.145:3000/api"; // la ip y las demas tambien es primero la ip del servidor o del internet al que este conectado
const char* testUrl = "http://192.168.100.145:3000/api/test";
const char* insertUrl = "http://192.168.100.145:3000/api/insert";

// Pines de trabajo del ESP32 S3 Ajusta estos valores según tu proyecto

// Pines de trabajo del ESP32 S3 Ajusta estos valores según tu proyecto
  

// Variables de control
unsigned long lastBlink = 0;
bool blinkState = false;
const int BLINK_INTERVAL = 500; // 500ms para parpadeo


// ============ FUNCIONES LED INTEGRADO============
void setupLED() {
#define LED_PIN 48   
  // Apagar todos los LEDs inicialmente
  digitalWrite(LED_PIN, LOW);  // Turn the RGB LED off
}

void setLEDColor(String color) {
  if (color == "off") {
    rgbLedWrite(LED_PIN, 0, 0, 0);
  }
  else if (color == "red") {
    rgbLedWrite(LED_PIN, RGB_BRIGHTNESS, 0, 0);  // Red
  }
  else if (color == "green") {
    rgbLedWrite(LED_PIN, 0, RGB_BRIGHTNESS, 0);  //Green
  }
  else if (color == "blue") {
    rgbLedWrite(LED_PIN, 0, 0, RGB_BRIGHTNESS);  //Blue
  }
}

void blinkLED(String color) {
  unsigned long currentTime = millis();
  if (currentTime - lastBlink >= BLINK_INTERVAL) {
    lastBlink = currentTime;
    blinkState = !blinkState;
    
    if (blinkState) {
      setLEDColor(color);
    } else {
      setLEDColor("off");
    }
  }
}

// ============ FUNCIONES WiFi ============

void connectToWiFi() {
  Serial.println("\n\nInitializando conexión WiFi...");
  Serial.print("Conectando a: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attemp = 0;
  while (WiFi.status() != WL_CONNECTED && attemp < 20) {
    delay(500);
    Serial.print(".");
    attemp++;
    
    // Parpadeo azul mientras se conecta
    blinkLED("blue");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    setLEDColor("blue");
    Serial.println("\n✓ Conectado a WiFi");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    setLEDColor("red");
    Serial.println("\n✗ Error: No se pudo conectar a WiFi");
  }
}

// ============ FUNCIONES HTTP ============

bool testDatabaseConnection() {
  Serial.println("\nProbando conexión a MSSQL...");
  
  HTTPClient http;
  http.begin(testUrl);
  http.addHeader("Content-Type", "application/json");
  
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("✓ Conexión a BD exitosa");
    Serial.println(response);
    http.end();
    return true;
  } else {
    Serial.print("✗ Error conectando a BD: ");
    Serial.println(httpCode);
    http.end();
    return false;
  }
}

bool insertDataToDatabase(const char* nombre, int valor, float temperatura) {
  Serial.println("\nEnviando INSERT a MSSQL...");
  
  HTTPClient http;
  http.begin(insertUrl);
  http.addHeader("Content-Type", "application/json");
  
  // Crear JSON con los datos
  DynamicJsonDocument doc(200);
  doc["nombre"] = nombre;
  doc["valor"] = valor;
  doc["temperatura"] = temperatura;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.print("Datos enviados: ");
  Serial.println(jsonString);
  
  int httpCode = http.POST(jsonString);
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("✓ INSERT exitoso");
    Serial.println(response);
    http.end();
    return true;
  } else {
    Serial.print("✗ Error en INSERT: ");
    Serial.println(httpCode);
    String response = http.getString();
    Serial.println(response);
    http.end();
    return false;
  }
}

// ============ SETUP ============

void setup() {
  
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=== ESP32 S3 MSSQL DEBUG ===");
 



  
  setupLED();
  
  // Conectar a WiFi
  connectToWiFi();
  
  if (WiFi.status() != WL_CONNECTED) {
    setLEDColor("red");
    Serial.println("No se pudo conectar a WiFi. Reiniciando en 5 segundos...");
    delay(5000);
    ESP.restart();
  }
  
  // Parpadeo azul mientras se prueba conexión a BD
  Serial.println("\nProbando conexión a base de datos...");
  bool connectionOk = false;
  
  for (int i = 0; i < 10; i++) {
    blinkLED("blue");
    
    if (testDatabaseConnection()) {
      connectionOk = true;
      break;
    }
    delay(500);
  }
  
  if (!connectionOk) {
    setLEDColor("red");
    Serial.println("No se pudo conectar a la BD. Verifique la configuración.");
    delay(5000);
    ESP.restart();
  }
  
  // Hacer un INSERT de prueba
  Serial.println("\nRealizando INSERT de prueba...");
  
  if (insertDataToDatabase("ESP32_S3_Test", 42, 23.5)) {
    // INSERT exitoso - LED verde
    setLEDColor("green");
    Serial.println("\n✓✓✓ TODO CORRECTO - LED VERDE ✓✓✓");
  } else {
    // INSERT fallido - LED rojo
    setLEDColor("red");
    Serial.println("\n✗✗✗ ERROR EN INSERT - LED ROJO ✗✗✗");
  }
}

// ============ LOOP ============

void loop() {
  // Mantener el LED en el estado actual
  // El color ya está seteado (verde o rojo)
  
  // Cada 30 segundos, hacer otro INSERT para demostración
  static unsigned long lastInsert = 0;
  if (millis() - lastInsert > 30000) {
    lastInsert = millis();
    
    Serial.println("\n\n=== Enviando INSERT periódico ===");
    
    int valorRandom = random(0, 100);
    float temperaturaRandom = 20.0 + (random(0, 50) / 10.0);
    
    if (insertDataToDatabase("ESP32_Periodic", valorRandom, temperaturaRandom)) {
      setLEDColor("green");
      Serial.println("✓ INSERT periódico exitoso");
      

    } else {
      setLEDColor("red");
      Serial.println("✗ INSERT periódico fallido");
     
    }
  }
  
  delay(100);
  setLEDColor("off");
}
