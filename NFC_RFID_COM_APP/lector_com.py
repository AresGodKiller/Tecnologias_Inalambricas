"""
=============================================================
 LECTOR DE PUERTO COM - SISTEMA NFC/RFID
 Archivo: lector_com.py
 
 Descripción:
   Lee datos JSON enviados por la ESP32 a través del
   puerto serial COM y los muestra en consola.
   Compatible con el servidor Flask (app.py) que
   expone los datos a la interfaz web de Laragon.

 Dependencias:
   pip install pyserial

 Uso:
   python lector_com.py
   python lector_com.py --port COM5 --baud 115200
=============================================================
"""

import serial          # Comunicación con el puerto serial (COM)
import json            # Parseo de tramas JSON enviadas por la ESP32
import time            # Control de tiempos y reintentos
import argparse        # Argumentos de línea de comandos
import sys
import threading       # Hilo paralelo para lectura no bloqueante
from datetime import datetime

# -----------------------------------------------------------
# CONFIGURACIÓN POR DEFECTO
# Cambia COM_PORT al puerto que asignó Windows a tu ESP32
# Puedes verlo en: Administrador de dispositivos → Puertos (COM y LPT)
# -----------------------------------------------------------
COM_PORT  = "COM4"     # Puerto serial asignado a la ESP32
BAUD_RATE = 115200     # Velocidad en baudios — debe coincidir con el código Arduino

# -----------------------------------------------------------
# Variable global compartida con el servidor Flask
# Almacena la última lectura recibida de la ESP32
# -----------------------------------------------------------
ultima_lectura = {
    "hex": "--",
    "dec": "--",
    "bin": "--",
    "acceso": None,
    "timestamp": "--"
}
lock = threading.Lock()   # Mutex para acceso seguro desde múltiples hilos


def parsear_linea(linea: str) -> dict | None:
    """
    Intenta decodificar una línea de texto como JSON.
    La ESP32 envía tramas con el formato:
      {"hex":"XX:XX:XX:XX","dec":123456,"bin":"...","acceso":true}
    
    Retorna el diccionario parseado o None si la línea
    no es JSON válido (p. ej., mensajes de depuración).
    """
    linea = linea.strip()
    if not linea.startswith("{"):
        return None    # Descarta líneas que no son JSON
    try:
        return json.loads(linea)
    except json.JSONDecodeError:
        return None    # Descarta JSON malformado


def formatear_tarjeta(datos: dict) -> str:
    """
    Genera una representación en texto de los datos de la tarjeta
    para mostrarlos en la consola con colores ANSI.
    """
    acceso = datos.get("acceso", False)
    estado = "\033[92m[ACCESO CONCEDIDO]\033[0m" if acceso else "\033[91m[ACCESO DENEGADO]\033[0m"
    ts     = datos.get("timestamp", "")

    return (
        f"\n{'═'*55}\n"
        f"  🏷  TARJETA DETECTADA  —  {ts}\n"
        f"{'─'*55}\n"
        f"  HEX (Base 16): {datos.get('hex', '--')}\n"
        f"  DEC (Base 10): {datos.get('dec', '--')}\n"
        f"  BIN (Base  2): {datos.get('bin', '--')}\n"
        f"  Estado       : {estado}\n"
        f"{'═'*55}\n"
    )


def leer_serial(port: str, baud: int, callback=None):
    """
    Función principal: abre el puerto serial y lee en bucle.
    
    Parámetros:
      port     — Nombre del puerto COM (ej. "COM4", "/dev/ttyUSB0")
      baud     — Velocidad en baudios (debe coincidir con la ESP32)
      callback — Función opcional a llamar con cada tarjeta leída
    
    El bucle maneja automáticamente desconexiones y reconexiones.
    """
    global ultima_lectura

    while True:
        try:
            print(f"\n[INFO] Intentando conectar a {port} a {baud} baudios...")
            
            # Abre el puerto serial con timeout de 1 segundo por línea
            # timeout=1 evita que readline() bloquee indefinidamente
            ser = serial.Serial(
                port=port,
                baudrate=baud,
                bytesize=serial.EIGHTBITS,    # 8 bits de datos por trama
                parity=serial.PARITY_NONE,    # Sin bit de paridad
                stopbits=serial.STOPBITS_ONE, # 1 bit de parada
                timeout=1                     # Timeout por línea en segundos
            )

            print(f"[OK] Conectado a {port}. Esperando tarjetas NFC/RFID...\n")
            print("     (Presiona Ctrl+C para detener)\n")

            while True:
                # Lee una línea completa hasta el salto de línea (\n)
                # La ESP32 termina cada trama JSON con Serial.println()
                raw = ser.readline()

                if not raw:
                    continue   # Timeout de 1 s sin datos → sigue esperando

                try:
                    # Decodifica bytes a string usando UTF-8
                    linea = raw.decode("utf-8", errors="replace")
                except Exception:
                    continue

                datos = parsear_linea(linea)

                if datos is None:
                    # Es un mensaje de texto plano de la ESP32 (debug)
                    print(f"[ESP32] {linea.strip()}")
                    continue

                # Agrega marca de tiempo local a los datos recibidos
                datos["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Actualiza la variable global de forma thread-safe
                with lock:
                    ultima_lectura = datos

                # Muestra los datos en consola
                print(formatear_tarjeta(datos))

                # Llama al callback si existe (lo usa el servidor Flask)
                if callback:
                    callback(datos)

        except serial.SerialException as e:
            print(f"\n[ERROR] Puerto serial: {e}")
            print(f"[INFO] Reintentando en 3 segundos...")
            time.sleep(3)   # Espera antes de reconectar (útil si la ESP32 se desconecta)

        except KeyboardInterrupt:
            print("\n[INFO] Lectura detenida por el usuario.")
            sys.exit(0)


def obtener_ultima_lectura() -> dict:
    """
    Retorna una copia de la última lectura recibida.
    Usada por el servidor Flask para responder peticiones HTTP.
    """
    with lock:
        return dict(ultima_lectura)


# -----------------------------------------------------------
# PUNTO DE ENTRADA — se ejecuta si se corre directamente
# -----------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lector de tarjetas NFC/RFID por puerto COM"
    )
    parser.add_argument(
        "--port", default=COM_PORT,
        help=f"Puerto COM (default: {COM_PORT})"
    )
    parser.add_argument(
        "--baud", type=int, default=BAUD_RATE,
        help=f"Baudios (default: {BAUD_RATE})"
    )
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════╗")
    print("║   LECTOR NFC/RFID — Puerto COM  →  Consola          ║")
    print("╚══════════════════════════════════════════════════════╝")
    
    # Inicia la lectura en modo standalone (sin Flask)
    leer_serial(args.port, args.baud)
