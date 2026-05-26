
# ESP32 S3 -> MSSQL via REST API

Guía completa para conectar un ESP32 S3 a MSSQL en Docker y controlar LED RGB según el resultado.

## 📋 Pre-requisitos

### En tu computadora:
- Docker corriendo con MSSQL en puerto 1433
- Node.js instalado
- Usuario MSSQL: `sa` / `Thewarlus1!`
- Base de datos: `basicos`
- Tabla: `test` (con campos: nombre, valor, temperatura)

### En Arduino IDE:
- Board: "ESP32-S3 Dev Module" (o tu placa específica)
- Librerías instaladas:
  - WiFi (incluida)
  - HTTPClient (incluida)
  - ArduinoJson (instalar desde Library Manager)

---
## 🔧 PASO -1: Crear el contenedor en docker
docker run -e 'ACCEPT_EULA=Y' -e 'MSSQL_SA_PASSWORD=C0NTR453N1!4' -p 1433:1433 --name pruebaDb --hostname pruebaDB -d mcr.microsoft.com/azure-sql-edge

## 🔧 PASO 1: Crear tabla SQL

Ejecuta esto en MSSQL:

```sql
USE basicos;

CREATE TABLE test (
    id INT PRIMARY KEY IDENTITY(1,1),
    nombre VARCHAR(50),
    valor INT,
    temperatura FLOAT,
    fecha_creacion DATETIME DEFAULT GETDATE()
);
```

---

## 🖥️ PASO 2: Configurar servidor intermediario (Node.js)

### 2.1 Instalar dependencias

```bash
npm init -y
npm install express cors body-parser mssql
```

### 2.2 Verificar tu IP

En tu computadora, ejecuta:
```bash
# En macOS/Linux
ifconfig | grep inet

# En Windows
ipconfig
```

Busca la IP que comience con 192.168.x.x o 10.x.x.x (en tu caso es 192.168.100.100)

### 2.3 Ajustar servidor_api_esp32.js (si es necesario)

Edita la línea de configuración:
```javascript
const config = {
  server: ' 192.168.100.145',  // ← Tu IP
  port: 1433,                 // Puerto MSSQL
  user: 'sa',
  password: 'Thewarlus1!',
  database: 'basicos'
};
```

### 2.4 Iniciar servidor

```bash
node servidor_api_esp32.js
```

Deberías ver:
```
Servidor API corriendo en http://0.0.0.0:3000
Esperando conexiones de ESP32...
```

---

## 📱 PASO 3: Configurar ESP32 S3

### 3.1 Ajustar los pines del LED RGB

En el archivo `esp32_mssql.ino`, busca:

```cpp
#define LED_RED 1      // ← Ajusta estos pines
#define LED_GREEN 2
#define LED_BLUE 3
```

**Nota**: Los pines dependen de tu placa. Consulta el schematic de tu ESP32 S3.
- Para ESP32-S3 Dev Kit: típicamente GPIO 39 (Red), GPIO 40 (Green), GPIO 41 (Blue)
- Para otras placas: verifica el manual

### 3.2 Ajustar WiFi y IP

En el archivo `esp32_mssql.ino`, busca:

```cpp
const char* ssid = "PH4ND4_5";
const char* password = "PH4ND4!!";
const char* apiUrl = "http://192.168.100.100:3000/api";  // ← Tu IP local
```

### 3.3 Subir código a ESP32

1. Conecta el ESP32 S3 por USB
2. En Arduino IDE: Tools → Board → "ESP32-S3 Dev Module"
3. Tools → Port → Selecciona el puerto COM
4. Sketch → Upload

---

## 🚀 PASO 4: Probar

### Secuencia esperada:

1. **LED parpadea AZUL** 🔵
   - Conectando a WiFi
   - Probando conexión a MSSQL

2. **LED VERDE** 🟢
   - ✓ INSERT exitoso
   - La aplicación está funcionando

3. **LED ROJO** 🔴
   - ✗ Error en el INSERT o conexión a BD
   - Verifica logs en Serial Monitor

### Ver logs

En Arduino IDE: Tools → Serial Monitor (115200 baud)

Deberías ver algo como:
```
=== ESP32 S3 MSSQL DEBUG ===
Conectando a: PHANDORA
✓ Conectado a WiFi
IP: 192.168.100.42

Probando conexión a MSSQL...
✓ Conexión a BD exitosa
{"success":true,"message":"Conexión a MSSQL exitosa"}

Realizando INSERT de prueba...
Datos enviados: {"nombre":"ESP32_S3_Test","valor":42,"temperatura":23.5}
✓ INSERT exitoso
{"success":true,"message":"Datos insertados correctamente","rowsAffected":1}

✓✓✓ TODO CORRECTO - LED VERDE ✓✓✓
```

---

## 🔄 Funcionalidad adicional

El ESP32 también:
- Hace INSERT automático cada 30 segundos (puedes cambiar este intervalo)
- Genera valores aleatorios para simular sensores
- Muestra todos los logs en Serial Monitor

---

## ❌ Troubleshooting

### El LED no enciende
- Verifica que los pines GPIO sean correctos
- Comprueba que el LED tenga polaridad correcta (ánodo a GPIO, cátodo a GND)

### No se conecta a WiFi
- Comprueba SSID y contraseña
- El ESP32 solo soporta WiFi 2.4GHz (no 5GHz)

### No se conecta a MSSQL
- Verifica que Docker esté corriendo
- Comprueba que la IP sea correcta (ping 173.16.17.172)
- Verifica que el puerto 1433 sea accesible
- Comprueba credenciales de MSSQL

### El servidor Node.js no arranca
```bash
npm install  # Asegúrate de haber instalado las dependencias
node servidor_api_esp32.js
```

---

## 📊 Ver datos en MSSQL

```sql
SELECT * FROM test ORDER BY fecha_creacion DESC;
```

---

## 📝 Modificar datos a insertar

En `esp32_mssql.ino`, modifica la línea del INSERT:

```cpp
// Opción 1: Valores fijos
insertDataToDatabase("MiSensor", 100, 25.5);

// Opción 2: Valores aleatorios
int valor = random(0, 100);
float temperatura = 20.0 + (random(0, 50) / 10.0);
insertDataToDatabase("Sensor_001", valor, temperatura);

// Opción 3: Lectura de sensor real
int humedad = readHumiditySensor();  // Tu función
insertDataToDatabase("Humedad", humedad, 0);
```

---

¡Listo! Deberías tener todo funcionando. 🎉
