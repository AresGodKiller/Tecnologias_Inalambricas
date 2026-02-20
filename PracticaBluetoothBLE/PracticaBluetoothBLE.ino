#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>


// ID para identificar el dispsitivo y mandar las acciones desde mit app inventor //
#define SERVICE_UUID        "12345678-1234-1234-1234-1234567890ab"
#define CHARACTERISTIC_UUID "abcd1234-5678-1234-5678-abcdef123456"

// numero de pines de los leds //
#define LED1_PIN 16
#define LED2_PIN 17
#define LED3_PIN 18

bool dispositivoConectado = false;

void setAll(bool on) {
  digitalWrite(LED1_PIN, on ? HIGH : LOW);
  digitalWrite(LED2_PIN, on ? HIGH : LOW);
  digitalWrite(LED3_PIN, on ? HIGH : LOW);
}

class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) override {
    dispositivoConectado = true;
    Serial.println("Conectado");
  }
  void onDisconnect(BLEServer* pServer) override {
    dispositivoConectado = false;
    Serial.println("Desconectado");
    pServer->getAdvertising()->start(); // desconcetarse de el esp32
  }
};

class MyCallbacks : public BLECharacteristicCallbacks {
  
void onWrite(BLECharacteristic* pCharacteristic) override {
  String rx = pCharacteristic->getValue();   // ahora lo recibe como texto para que cuando en la aplicacion se ejecute un boton, el esp32 lo tome y pueda hacer la accion segun correponda con el boton que se presiono
  if (rx.length() == 0) return;

  char c = rx.charAt(0);                     // tomamos el primer caracter o letra que da la aplicacion o el boton presionado
  Serial.print("Recibido: ");
  Serial.println(c);

  switch (c) {
    case 'A': digitalWrite(LED1_PIN, HIGH); break;
    case 'a': digitalWrite(LED1_PIN, LOW);  break;
    case 'B': digitalWrite(LED2_PIN, HIGH); break;
    case 'b': digitalWrite(LED2_PIN, LOW);  break;
    case 'C': digitalWrite(LED3_PIN, HIGH); break;
    case 'c': digitalWrite(LED3_PIN, LOW);  break;
    default:
      Serial.println("Comando no reconocido");
      break;
  }
}

};

void setup() {
  Serial.begin(115200);

  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  pinMode(LED3_PIN, OUTPUT);
  setAll(false);

  BLEDevice::init("ESP32_EquipoSicsSeven"); 
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);

  BLECharacteristic *pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_WRITE     |
    BLECharacteristic::PROPERTY_WRITE_NR  | // por si la app escribe sin respuesta
    BLECharacteristic::PROPERTY_READ
  );

  pCharacteristic->setCallbacks(new MyCallbacks());

  pService->start();
  pServer->getAdvertising()->start();

  Serial.println("ESP32 listo (BLE)");
}

void loop() {
  // no es necesario hacer nada aqui ya que el funcionamiento se hace afuera del loop porque desde ahi se puede hacer
}

