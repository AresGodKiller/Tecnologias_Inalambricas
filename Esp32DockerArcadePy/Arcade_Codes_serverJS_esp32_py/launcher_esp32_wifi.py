"""
launcher_esp32_wifi.py — Lanzador principal del Arcade RFID


Este archivo es el punto de entrada del sistema en la PC del equipo.
Se encarga de coordinar todo el flujo entre el ESP32, el servidor
Node.js y el juego Snake.

El flujo que sigue es este:
  1. Espera a que el ESP32 mande un UID por puerto Serial
  2. Consulta al servidor si ese jugador ya existe en la base de datos
  3. Si no existe, abre una ventana para que el jugador escriba su nombre
  4. Abre el juego Snake con los datos del jugador
  5. Cuando el jugador termina, manda el puntaje al ESP32 por Serial
  6. El ESP32 hace el POST al servidor para actualizar el acumulado
  7. Vuelve al paso 1 esperando la siguiente tarjeta

Dependencias que hay que tener instaladas:
  pip install pyserial requests
"""

import sys
import time
import serial
import serial.tools.list_ports
import requests
import tkinter as tk
from tkinter import font as tkfont

# El juego Snake está en el mismo directorio que este archivo
from snake_gui import SnakeApp


# CONFIGURACIÓN 

# IP de la Mac donde corre server.js.
# Si la Mac tiene una IP diferente en la red, cambiar este valor.
SERVER_URL  = 'http://192.168.0.104:3000'

# Puerto Serial al que está conectado el ESP32 en esta computadora.
# En Windows suele ser COM3, COM4, COM10, etc.
# En Mac o Linux suele ser /dev/ttyUSB0 o /dev/cu.usbserial-XXXX
SERIAL_PORT = 'COM10'
BAUD_RATE   = 115200

# Tiempo máximo en segundos que se espera la confirmación del ESP32
# después de mandarle el puntaje. Si pasa este tiempo sin respuesta,
# se considera que hubo un error.
ACK_TIMEOUT = 10


#  Helpers de puerto 

def listar_puertos():
    """
    Imprime en consola todos los puertos COM disponibles en el sistema.
    Útil para saber el nombre correcto del puerto antes de cambiar SERIAL_PORT.
    """
    puertos = serial.tools.list_ports.comports()
    if puertos:
        print("Puertos COM disponibles:")
        for p in puertos:
            print(f"  {p.device}  —  {p.description}")
    else:
        print("  No se encontraron puertos COM.")
    print()


#  Funciones de comunicación con el servidor 

def verificar_servidor() -> bool:
    """
    Hace un GET al endpoint /api/ultimo-movimiento para confirmar que
    el servidor Node.js está corriendo y accesible en la red.

    Retorna True si el servidor respondió correctamente, False si no.
    Si retorna False, el programa se detiene porque sin servidor no
    hay forma de guardar ni consultar puntajes.
    """
    try:
        r = requests.get(f"{SERVER_URL}/api/ultimo-movimiento", timeout=4)
        if r.ok:
            return True
        print(f"  ERROR: el servidor Node.js respondió con estado {r.status_code}.")
        return False
    except requests.RequestException as e:
        print(f"  ERROR conectando al servidor Node.js: {e}")
        return False


def verificar_tarjeta(uid: str) -> dict | None:
    """
    Consulta al servidor si el UID de la tarjeta ya tiene un jugador
    registrado en la base de datos.

    Hace un GET a /api/puntuaciones/{uid} y procesa la respuesta:
      - Si el jugador existe: retorna un dict con su nombre y puntaje acumulado
      - Si no existe: retorna None para que el programa abra el registro

    En caso de error de red, termina el programa porque no se puede
    continuar sin saber si el jugador existe.
    """
    try:
        r = requests.get(f"{SERVER_URL}/api/puntuaciones/{uid}", timeout=5)
        r.raise_for_status()
        data = r.json()

        if data.get('existe'):
            # El jugador ya tiene registro: devolver sus datos para cargarlos en el juego
            return {
                'name_disp': data.get('name_disp', data.get('usr', 'Jugador')),
                'usr':       data.get('usr', ''),
                'score':     data.get('score', 0),
                'id_rfid':   uid
            }
        # El UID no está registrado
        return None

    except requests.RequestException as e:
        print(f"  ERROR conectando al servidor Node.js: {e}")
        sys.exit(1)


def registrar_jugador(uid: str, name_disp: str, usr: str) -> dict | None:
    """
    Registra un jugador nuevo en la base de datos haciendo un POST
    al servidor con los datos que el jugador escribió en la ventana
    de registro.

    El score inicial es 0 porque es la primera vez que juega.

    Retorna el dict del jugador si el registro fue exitoso,
    o None si hubo un error de red.

    Nota: este POST lo hace Python (y no el ESP32) porque ocurre
    antes de que empiece la partida, cuando el ESP32 ya entregó
    el UID y está esperando la siguiente tarjeta.
    """
    try:
        payload = {
            'name_disp': name_disp,
            'usr':       usr,
            'score':     0,
            'id_rfid':   uid
        }
        r = requests.post(f"{SERVER_URL}/api/puntuaciones", json=payload, timeout=5)
        r.raise_for_status()
        print(f"  ✓ Jugador '{name_disp}' registrado en el servidor.")
        return {
            'name_disp': name_disp,
            'usr':       usr,
            'score':     0,
            'id_rfid':   uid
        }
    except requests.RequestException as e:
        print(f"  ERROR al registrar jugador: {e}")
        return None


#  Enviar score al ESP32 para que lo reenvíe al servidor 

def enviar_score_via_esp32(ser: serial.Serial, jugador: dict, puntos: int) -> bool:
    """
    Manda el puntaje de la sesión al ESP32 por puerto Serial para que
    el ESP32 sea quien haga el HTTP POST al servidor.

    El formato del mensaje es:
      SCORE:RFID:puntos:name_disp:usr

    Los ':' en el nombre y usuario se reemplazan por '-' porque ':'
    es el delimitador del protocolo y rompería el parseo en el ESP32.

    Después de mandar el mensaje, espera hasta ACK_TIMEOUT segundos
    por una respuesta del ESP32:
      ACK:OK    → el POST al servidor fue exitoso
      ACK:ERROR → el POST falló (sin WiFi, servidor caído, etc.)

    Retorna True si se recibió ACK:OK, False en cualquier otro caso.
    """
    rfid      = jugador['id_rfid']
    name_disp = jugador.get('name_disp', 'Jugador').replace(':', '-')
    usr       = jugador.get('usr', 'unknown').replace(':', '-')

    mensaje = f"SCORE:{rfid}:{puntos}:{name_disp}:{usr}\n"

    print(f"  → Enviando al ESP32: {mensaje.strip()}")

    try:
        ser.write(mensaje.encode('utf-8'))
        ser.flush()  # Asegurar que el mensaje salió completo antes de esperar respuesta
    except serial.SerialException as e:
        print(f"  ERROR escribiendo al ESP32: {e}")
        return False

    # Esperar la confirmación del ESP32 hasta el límite de tiempo
    print(f"  Esperando confirmación del ESP32 (máx {ACK_TIMEOUT}s)...")
    deadline = time.time() + ACK_TIMEOUT

    while time.time() < deadline:
        try:
            linea = ser.readline().decode('utf-8', errors='ignore').strip()
        except serial.SerialException:
            break

        if not linea:
            continue

        # Mostrar cualquier mensaje del ESP32 en consola para debug
        print(f"  [ESP32] {linea}")

        if linea == "ACK:OK":
            print("  ✓ ESP32 confirmó: score enviado al servidor correctamente.")
            return True
        elif linea == "ACK:ERROR":
            print("  ✗ ESP32 reportó ERROR al enviar el score al servidor.")
            return False

    print("  ✗ Timeout: el ESP32 no respondió a tiempo.")
    return False


#  Lectura del puerto Serial 

def esperar_tarjeta(ser: serial.Serial) -> str:
    """
    Se queda bloqueado leyendo el puerto Serial hasta recibir una línea
    con el formato 'UID:XXXX' que manda el ESP32 cuando detecta una tarjeta.

    Cualquier otra línea que llegue (mensajes de debug del ESP32) se imprime
    en consola pero no interrumpe la espera.

    Retorna el UID de la tarjeta como string en mayúsculas.
    Termina el programa si se pierde la conexión con el ESP32.
    """
    print("Acerca tu tarjeta RFID al lector...")
    while True:
        try:
            linea = ser.readline().decode('utf-8', errors='ignore').strip()
        except serial.SerialException:
            print("ERROR: Se perdió la conexión con el ESP32.")
            sys.exit(1)

        if linea.startswith('UID:'):
            uid = linea[4:]  # Quitar el prefijo 'UID:' y quedarse solo con el identificador
            print(f"  Tarjeta detectada: {uid}")
            return uid

        # Imprimir otros mensajes del ESP32 para tener visibilidad de lo que está pasando
        if linea:
            print(f"  [ESP32] {linea}")


#  Ventana de registro de jugador nuevo 

class VentanaRegistro(tk.Tk):
    """
    Ventana emergente que aparece cuando se detecta una tarjeta que no
    está registrada en la base de datos.

    El jugador escribe su nombre en el campo de texto y hace clic en
    'Inscribirme y jugar' para crear su cuenta con puntaje inicial en 0.

    Si cancela o cierra la ventana, self.resultado queda en None y el
    launcher salta esta tarjeta y vuelve a esperar la siguiente.

    El estilo visual sigue la estética gótica del juego Snake:
    colores oscuros, tipografía Georgia, acentos en dorado.
    """

    # Paleta de colores consistente con snake_gui.py
    BG          = '#1C1A18'
    BG_INPUT    = '#17150F'
    CLR_GOLD    = '#C8A84B'
    CLR_GOLD_DIM= '#7A6030'
    CLR_PARCH   = '#D4C5A9'
    CLR_DIM     = '#5A5040'
    CLR_BORDER  = '#5C4A1E'
    CLR_RED     = '#8B1A1A'
    CLR_BTN_BG  = '#2A2318'
    CLR_BTN_FG  = '#C8A84B'
    CLR_BTN_BD  = '#5C4A1E'

    def __init__(self, uid: str):
        super().__init__()
        self.uid       = uid       # UID de la tarjeta que se va a registrar
        self.resultado = None      # Se llena con el dict del jugador si se registra bien

        self.title('Nuevo Jugador — Arcade')
        self.resizable(False, False)
        self.configure(bg=self.BG)

        # Centrar la ventana en la pantalla
        self.update_idletasks()
        w, h = 420, 300
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

        # Fuentes tipográficas del proyecto
        self._f_title  = tkfont.Font(family='Georgia', size=16, weight='bold')
        self._f_sub    = tkfont.Font(family='Georgia', size=9,  slant='italic')
        self._f_label  = tkfont.Font(family='Georgia', size=11)
        self._f_input  = tkfont.Font(family='Georgia', size=13)
        self._f_btn    = tkfont.Font(family='Georgia', size=11, weight='bold')
        self._f_err    = tkfont.Font(family='Georgia', size=9)
        self._f_uid    = tkfont.Font(family='Courier',  size=9)

        self._build_ui()
        self.protocol('WM_DELETE_WINDOW', self._cancelar)

    def _build_ui(self):
        """Construye todos los elementos visuales de la ventana de registro."""

        # Borde dorado superior
        tk.Frame(self, bg=self.CLR_BORDER, height=2).pack(fill='x')

        # Encabezado con título y UID de la tarjeta
        hdr = tk.Frame(self, bg=self.BG, pady=18)
        hdr.pack(fill='x')
        tk.Label(hdr, text='✦  Nuevo Iniciado  ✦',
                 font=self._f_title,
                 bg=self.BG, fg=self.CLR_GOLD).pack()
        tk.Label(hdr, text='Tarjeta no reconocida — inscríbete para jugar',
                 font=self._f_sub,
                 bg=self.BG, fg=self.CLR_DIM).pack(pady=(2, 0))
        # Mostrar el UID para que se pueda identificar la tarjeta si hace falta
        tk.Label(hdr, text=f'UID: {self.uid}',
                 font=self._f_uid,
                 bg=self.BG, fg=self.CLR_DIM).pack(pady=(6, 0))

        tk.Frame(self, bg=self.CLR_BORDER, height=1).pack(fill='x', padx=20)

        # Área del formulario con el campo de nombre
        form = tk.Frame(self, bg=self.BG, pady=20, padx=30)
        form.pack(fill='x')

        tk.Label(form, text='Tu nombre',
                 font=self._f_label,
                 bg=self.BG, fg=self.CLR_PARCH,
                 anchor='w').pack(fill='x')
        tk.Label(form, text='Así aparecerás en el juego y el marcador',
                 font=self._f_sub,
                 bg=self.BG, fg=self.CLR_DIM,
                 anchor='w').pack(fill='x', pady=(0, 4))

        # Campo de texto donde el jugador escribe su nombre
        self._entry_name = tk.Entry(form,
                                    font=self._f_input,
                                    bg=self.BG_INPUT,
                                    fg=self.CLR_PARCH,
                                    insertbackground=self.CLR_GOLD,
                                    relief='flat', bd=0,
                                    highlightthickness=1,
                                    highlightbackground=self.CLR_BORDER,
                                    highlightcolor=self.CLR_GOLD)
        self._entry_name.pack(fill='x', ipady=7)
        self._entry_name.focus()  # El cursor va directo al campo al abrir la ventana

        # Etiqueta donde se muestran los mensajes de error de validación
        self._lbl_err = tk.Label(form, text='',
                                  font=self._f_err,
                                  bg=self.BG, fg=self.CLR_RED)
        self._lbl_err.pack(pady=(8, 0))

        tk.Frame(self, bg=self.CLR_BORDER, height=1).pack(fill='x', padx=20)

        # Botones de acción en la parte inferior
        bot = tk.Frame(self, bg=self.BG, pady=16)
        bot.pack()

        def _btn(parent, txt, cmd, primary=True):
            """Crea un botón con el estilo visual del proyecto."""
            fg = self.CLR_BTN_FG if primary else self.CLR_DIM
            b = tk.Button(parent, text=txt, command=cmd,
                          font=self._f_btn,
                          bg=self.CLR_BTN_BG, fg=fg,
                          activebackground='#3A3020',
                          activeforeground=self.CLR_GOLD,
                          relief='flat', bd=0,
                          highlightthickness=1,
                          highlightbackground=self.CLR_BTN_BD,
                          padx=18, pady=7, cursor='hand2')
            b.pack(side='left', padx=6)

        _btn(bot, 'Inscribirme y jugar', self._registrar)
        _btn(bot, 'Cancelar',            self._cancelar, primary=False)

        # Enter también funciona para confirmar el registro
        self.bind('<Return>', lambda e: self._registrar())

        # Borde dorado inferior
        tk.Frame(self, bg=self.CLR_BORDER, height=2).pack(fill='x', side='bottom')

    def _registrar(self):
        """
        Valida el nombre ingresado y llama a registrar_jugador() para
        crear el registro en la base de datos.

        Validaciones:
          - El nombre no puede estar vacío
          - El nombre no puede tener más de 50 caracteres

        Si el registro es exitoso, guarda el dict del jugador en
        self.resultado y cierra la ventana para que el launcher continúe.
        """
        name_disp = self._entry_name.get().strip()
        usr       = name_disp.replace(" ", "_")  # El usr no tiene espacios

        if not name_disp:
            self._lbl_err.config(text="El nombre no puede estar vacío.")
            return
        if len(name_disp) > 50:
            self._lbl_err.config(text="Nombre demasiado largo (máx. 50 caracteres).")
            return

        # Mostrar mensaje de espera mientras se hace la petición al servidor
        self._lbl_err.config(text="Registrando...", fg=self.CLR_GOLD)
        self.update()

        jugador = registrar_jugador(self.uid, name_disp, usr)
        if jugador:
            self.resultado = jugador
            self.destroy()  # Cerrar la ventana y devolver el control al launcher
        else:
            self._lbl_err.config(
                text="Error al conectar con la base de datos. Intenta de nuevo.",
                fg=self.CLR_RED
            )

    def _cancelar(self):
        """
        Cierra la ventana sin registrar al jugador.
        El launcher detecta que self.resultado es None y vuelve a
        esperar la siguiente tarjeta.
        """
        self.resultado = None
        self.destroy()


#  Función principal 

def main():
    print("=" * 52)
    print("    ARCADE RFID  —  Snake")
    print("=" * 52)

    # Verificar que el servidor Node.js esté corriendo antes de continuar.
    # Sin servidor no hay base de datos y el sistema no puede funcionar.
    if not verificar_servidor():
        print("  El servidor Node.js no está activo. Arranca server.js en la Mac.")
        sys.exit(1)

    # Mostrar los puertos disponibles para facilitar la configuración de SERIAL_PORT
    listar_puertos()

    # Abrir la conexión Serial con el ESP32
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Conectado al ESP32 en {SERIAL_PORT}\n")
    except serial.SerialException as e:
        print(f"ERROR abriendo {SERIAL_PORT}: {e}")
        sys.exit(1)

    # Esperar 2 segundos para que el ESP32 termine de inicializarse después
    # de abrir el Serial (el ESP32 se resetea al conectar en muchos modelos)
    time.sleep(2)
    ser.flushInput()  # Descartar cualquier basura que haya llegado durante el reset

    # Ciclo principal: se repite para cada jugador que acerque su tarjeta
    while True:

        # Paso 1: Bloquear hasta que el ESP32 mande un UID
        uid = esperar_tarjeta(ser)

        # Paso 2: Cerrar el Serial antes de abrir ventanas tkinter.
        # tkinter y pyserial pueden tener conflictos si ambos están activos
        # al mismo tiempo en Windows, por eso se cierra aquí y se reabre después.
        ser.close()

        # Paso 3: Consultar si la tarjeta ya tiene un jugador en la base de datos
        print("  Consultando base de datos...")
        jugador = verificar_tarjeta(uid)

        if jugador is None:
            # Tarjeta nueva: abrir ventana de registro
            print("  Tarjeta no registrada. Abriendo ventana de registro...")
            ventana = VentanaRegistro(uid)
            ventana.mainloop()
            jugador = ventana.resultado

            if jugador is None:
                # El jugador canceló el registro: volver a esperar otra tarjeta
                print("  Registro cancelado. Esperando siguiente tarjeta.\n")
                try:
                    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                    time.sleep(2)
                    ser.flushInput()
                except serial.SerialException as e:
                    print(f"ERROR reabriendo puerto Serial: {e}")
                    sys.exit(1)
                continue

        print(f"   Bienvenido, {jugador['name_disp']}!")
        print(f"    Puntaje acumulado: {jugador['score']} pts")

        # Paso 4: Lanzar el juego Snake con los datos del jugador.
        # El jugador ve su nombre y puntaje previo desde el inicio.
        print("\nAbriendo Snake...\n")
        app = SnakeApp(jugador=jugador)
        app.mainloop()  # Bloqueante: espera hasta que el jugador cierre el juego

        # Paso 5: Reabrir el Serial para mandar el score al ESP32.
        # app.score tiene los puntos que el jugador acumuló en esta sesión.
        puntos_sesion = app.score
        print(f"\nSesión terminada. Puntos ganados: {puntos_sesion}")

        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(1)
            ser.flushInput()
        except serial.SerialException as e:
            print(f"ERROR reabriendo puerto Serial: {e}")
            sys.exit(1)

        # Paso 6: Mandar el score al ESP32 solo si el jugador hizo puntos.
        # Si cerró el juego sin jugar, no hay nada que guardar.
        if puntos_sesion > 0:
            print("  Enviando score al ESP32 para que lo mande al servidor...")
            ok = enviar_score_via_esp32(ser, jugador, puntos_sesion)
            if not ok:
                print("  ERROR: ESP32 falló al enviar los datos.")
        else:
            print("  Sin puntos nuevos, no se actualiza.")

        print("\n" + "=" * 52)
        print("  ¿Otro jugador? Acerca una tarjeta.")
        print("=" * 52 + "\n")

        # Limpiar el buffer Serial antes de volver a esperar tarjetas
        ser.flushInput()


if __name__ == '__main__':
    main()
