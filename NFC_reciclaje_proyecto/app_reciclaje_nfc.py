# Sistema de reciclaje con NFC — EcoPoints v2
# El login es 100% por tarjeta NFC, sin PIN ni contraseña.
# Si la tarjeta no está registrada, se abre un formulario para crear la cuenta.
# Cuando el usuario presiona el botón físico, se le suman puntos por reciclar.
#
# Hardware: ESP32 + PN532 (I2C: SDA=21, SCL=22) + botón en GPIO25
# Dependencias: pip install pyserial mysql-connector-python

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import mysql.connector
from mysql.connector import Error

# Datos de conexión a la base de datos local (Laragon)
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',
    'database': 'nfc_reciclaje',
    'port':     3306
}

# Configuración del puerto serial hacia la ESP32
SERIAL_CONFIG = {
    'baudrate': 115200,
    'timeout':  1
}

PUNTOS_POR_BOTON = 5   # puntos por cada presionada del botón

# Paleta de colores de la interfaz
C_BG       = "#f0f4f8"
C_DARK     = "#1a2332"
C_DARK2    = "#243447"
C_GREEN    = "#27ae60"
C_GREEN_LT = "#2ecc71"
C_BLUE     = "#2980b9"
C_RED      = "#e74c3c"
C_ORANGE   = "#e67e22"
C_GRAY     = "#dfe6ed"
C_TEXT     = "#5d6d7e"
C_WHITE    = "#ffffff"
C_BORDER   = "#c8d6e5"
C_MUTED    = "#8395a7"

# Fuentes reutilizables
FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_SUB   = ("Segoe UI", 11)
FONT_BODY  = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 9)
FONT_BOLD  = ("Segoe UI", 12, "bold")
FONT_BIG   = ("Segoe UI", 52, "bold")


# Ventana modal que aparece cuando se detecta una tarjeta que no está en la BD.
# El usuario llena sus datos y queda registrado con ese UID vinculado a su cuenta.
class DialogoRegistrarNFC(tk.Toplevel):

    def __init__(self, parent, conexion_bd, uid_nuevo, callback_ok):
        super().__init__(parent)
        self.conexion_bd = conexion_bd
        self.uid_nuevo   = uid_nuevo
        self.callback_ok = callback_ok

        self.title("Registrar nueva tarjeta")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(bg=C_BG)
        self.grab_set()
        self.focus_force()

        # Centrar la ventana respecto a la pantalla principal
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - 420) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 480) // 2
        self.geometry(f"420x480+{px}+{py}")

        self._crear_ui()

    def _crear_ui(self):
        hdr = tk.Frame(self, bg=C_DARK)
        hdr.pack(fill=tk.X)

        tk.Label(hdr, text="Tarjeta nueva detectada",
                 font=("Segoe UI", 14, "bold"),
                 bg=C_DARK, fg=C_WHITE
                 ).pack(pady=(16, 2), padx=20, anchor=tk.W)

        tk.Label(hdr, text=f"UID: {self.uid_nuevo}   —   Regístrate para continuar",
                 font=FONT_SMALL, bg=C_DARK, fg=C_MUTED
                 ).pack(pady=(0, 14), padx=20, anchor=tk.W)

        body = tk.Frame(self, bg=C_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        campos = [
            ("Nombre *",   "nombre"),
            ("Apellido *", "apellido"),
            ("Email *",    "email"),
            ("Teléfono",   "telefono"),
        ]
        self._entradas = {}

        for etiqueta, clave in campos:
            tk.Label(body, text=etiqueta,
                     font=("Segoe UI", 10, "bold"),
                     bg=C_BG, fg=C_DARK
                     ).pack(anchor=tk.W, pady=(6, 2))

            entry = tk.Entry(body, font=FONT_BODY,
                             bg=C_WHITE, fg=C_DARK,
                             relief=tk.FLAT, bd=0,
                             highlightthickness=1,
                             highlightbackground=C_BORDER,
                             highlightcolor=C_BLUE)
            entry.pack(fill=tk.X, ipady=7)
            self._entradas[clave] = entry

        fila = tk.Frame(body, bg=C_BG)
        fila.pack(fill=tk.X, pady=(20, 0))

        tk.Button(fila, text="Cancelar",
                  font=FONT_BODY, bg=C_GRAY, fg=C_DARK,
                  relief=tk.FLAT, cursor="hand2",
                  padx=16, pady=8,
                  command=self.destroy
                  ).pack(side=tk.LEFT)

        tk.Button(fila, text="Registrar y entrar",
                  font=FONT_BOLD, bg=C_GREEN, fg=C_WHITE,
                  relief=tk.FLAT, cursor="hand2",
                  padx=16, pady=8,
                  command=self._guardar
                  ).pack(side=tk.RIGHT)

    def _guardar(self):
        datos = {k: v.get().strip() for k, v in self._entradas.items()}

        if not datos['nombre']:
            messagebox.showerror("Campo requerido", "El nombre es obligatorio.", parent=self)
            return
        if not datos['apellido']:
            messagebox.showerror("Campo requerido", "El apellido es obligatorio.", parent=self)
            return
        if not datos['email'] or "@" not in datos['email']:
            messagebox.showerror("Campo inválido", "Ingresa un email válido.", parent=self)
            return

        try:
            cur = self.conexion_bd.cursor()

            # El pin se guarda como '0000' porque ya no se usa para nada
            cur.execute(
                """INSERT INTO usuarios (nombre, apellido, email, telefono, pin)
                   VALUES (%s, %s, %s, %s, '0000')""",
                (datos['nombre'], datos['apellido'], datos['email'],
                 datos['telefono'] or None)
            )
            id_usuario = cur.lastrowid

            # Se vincula la tarjeta al usuario recién creado
            cur.execute(
                "INSERT INTO usuarios_nfc (id_usuario, uid_nfc) VALUES (%s, %s)",
                (id_usuario, self.uid_nuevo)
            )
            self.conexion_bd.commit()
            cur.close()

            # Se vuelve a consultar para tener el registro completo con todos los campos
            cur2 = self.conexion_bd.cursor(dictionary=True)
            cur2.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            usuario = cur2.fetchone()
            cur2.close()

            self.destroy()
            self.callback_ok(usuario)

        except Error as e:
            if e.errno == 1062:
                messagebox.showerror("Email duplicado",
                                     "Ya existe un usuario con ese email.",
                                     parent=self)
            else:
                messagebox.showerror("Error de base de datos", str(e), parent=self)


# Pantalla inicial que espera a que el usuario acerque su tarjeta NFC.
# También gestiona la conexión serial con la ESP32.
class PantallaEspera:

    def __init__(self, root, callback_login):
        self.root           = root
        self.callback_login = callback_login
        self.conexion_bd    = None
        self.puerto_serial  = None
        self.ejecutando     = False
        self.ultimo_uid     = None

        self.root.title("EcoPoints — Acerca tu tarjeta")
        self.root.geometry("520x600")
        self.root.resizable(False, False)
        self.root.configure(bg=C_DARK)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._conectar_bd()
        self._asegurar_tabla_nfc()
        self._crear_ui()

    def _conectar_bd(self):
        try:
            self.conexion_bd = mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo conectar a MySQL:\n{e}\n\n"
                "Asegúrate de que Laragon esté corriendo."
            )

    def _asegurar_tabla_nfc(self):
        # Se crea la tabla si no existe, para no depender de que el SQL ya se haya importado
        if not self.conexion_bd:
            return
        try:
            cur = self.conexion_bd.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS `usuarios_nfc` (
                  `id`         INT         NOT NULL AUTO_INCREMENT,
                  `id_usuario` INT         NOT NULL,
                  `uid_nfc`    VARCHAR(50) NOT NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `uid_nfc` (`uid_nfc`),
                  CONSTRAINT `fk_nfc_usuario`
                    FOREIGN KEY (`id_usuario`)
                    REFERENCES `usuarios` (`id_usuario`)
                    ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            self.conexion_bd.commit()
            cur.close()
        except Error as e:
            print(f"Error al crear tabla usuarios_nfc: {e}")

    def _buscar_usuario_por_uid(self, uid):
        # Busca si el UID ya está registrado y devuelve el usuario, o None si no existe
        try:
            cur = self.conexion_bd.cursor(dictionary=True)
            cur.execute("""
                SELECT u.*
                FROM usuarios u
                JOIN usuarios_nfc n ON u.id_usuario = n.id_usuario
                WHERE n.uid_nfc = %s AND u.estado = 'activo'
                LIMIT 1
            """, (uid,))
            usuario = cur.fetchone()
            cur.close()
            return usuario
        except Error:
            return None

    def _crear_ui(self):
        tk.Label(self.root, text="EcoPoints",
                 font=FONT_TITLE, bg=C_DARK, fg=C_WHITE
                 ).pack(pady=(50, 4))

        tk.Label(self.root, text="Sistema de Reciclaje con NFC",
                 font=FONT_SUB, bg=C_DARK, fg=C_MUTED
                 ).pack()

        tk.Frame(self.root, bg=C_GREEN, height=3).pack(fill=tk.X, pady=30)

        self.lbl_icon = tk.Label(self.root, text="📡",
                                  font=("Segoe UI", 64),
                                  bg=C_DARK, fg=C_GREEN_LT)
        self.lbl_icon.pack(pady=(0, 16))

        self.lbl_estado = tk.Label(self.root, text="Acerca tu tarjeta NFC",
                                    font=("Segoe UI", 18, "bold"),
                                    bg=C_DARK, fg=C_WHITE)
        self.lbl_estado.pack()

        self.lbl_sub = tk.Label(self.root, text="Para iniciar sesión o registrarte",
                                 font=FONT_SUB, bg=C_DARK, fg=C_MUTED)
        self.lbl_sub.pack(pady=(6, 0))

        # Panel compacto para seleccionar y conectar el puerto serial
        tk.Frame(self.root, bg=C_BORDER, height=1).pack(fill=tk.X, pady=(40, 0))

        panel = tk.Frame(self.root, bg=C_DARK2)
        panel.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(panel, text="Puerto ESP32:",
                 font=FONT_SMALL, bg=C_DARK2, fg=C_MUTED
                 ).pack(side=tk.LEFT, padx=(0, 6))

        self.combo_puertos = ttk.Combobox(panel, state="readonly", width=10)
        self.combo_puertos.pack(side=tk.LEFT, padx=(0, 4))

        tk.Button(panel, text="↺",
                  font=("Segoe UI", 10, "bold"),
                  bg=C_DARK2, fg=C_MUTED,
                  relief=tk.FLAT, cursor="hand2",
                  command=self._refrescar_puertos
                  ).pack(side=tk.LEFT, padx=(0, 6))

        self.btn_conectar = tk.Button(panel, text="Conectar",
                                       font=("Segoe UI", 9, "bold"),
                                       bg=C_GREEN, fg=C_WHITE,
                                       relief=tk.FLAT, cursor="hand2",
                                       padx=10, pady=3,
                                       command=self._alternar_serial)
        self.btn_conectar.pack(side=tk.LEFT)

        self.lbl_serial = tk.Label(panel, text="Desconectado",
                                    font=FONT_SMALL, bg=C_DARK2, fg=C_RED)
        self.lbl_serial.pack(side=tk.LEFT, padx=(10, 0))

        self._refrescar_puertos()

    def _refrescar_puertos(self):
        puertos = [p.device for p in serial.tools.list_ports.comports()]
        self.combo_puertos['values'] = puertos
        if puertos:
            self.combo_puertos.current(0)

    def _alternar_serial(self):
        if self.puerto_serial is None:
            self._conectar_serial()
        else:
            self._desconectar_serial()

    def _conectar_serial(self):
        puerto = self.combo_puertos.get()
        if not puerto:
            messagebox.showerror("Error", "Selecciona un puerto COM")
            return
        try:
            self.puerto_serial = serial.Serial(puerto, **SERIAL_CONFIG)
            self.lbl_serial.config(text=f"Conectado ({puerto})", fg=C_GREEN)
            self.btn_conectar.config(text="Desconectar", bg=C_RED)
            self.ejecutando = True
            # La lectura corre en un hilo aparte para no bloquear la interfaz
            threading.Thread(target=self._leer_serial, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar:\n{e}")

    def _desconectar_serial(self):
        self.ejecutando = False
        if self.puerto_serial:
            self.puerto_serial.close()
            self.puerto_serial = None
        self.lbl_serial.config(text="Desconectado", fg=C_RED)
        self.btn_conectar.config(text="Conectar", bg=C_GREEN)

    def _leer_serial(self):
        # Se lee carácter a carácter y se acumula hasta encontrar el salto de línea
        buffer = ""
        while self.ejecutando:
            try:
                if self.puerto_serial and self.puerto_serial.in_waiting:
                    char = self.puerto_serial.read().decode('utf-8', errors='ignore')
                    buffer += char
                    if char == '\n':
                        linea  = buffer.strip()
                        buffer = ""
                        if linea:
                            # Se procesa desde el hilo principal de Tkinter
                            self.root.after(0, lambda l=linea: self._procesar_linea(l))
            except Exception as e:
                print(f"Error serial: {e}")
                self.ejecutando = False

    def _procesar_linea(self, linea):
        if "UID CONCATENADO" in linea:
            partes = linea.split(":", 1)
            if len(partes) == 2:
                uid = partes[1].strip().upper()
                if uid and uid != self.ultimo_uid:
                    # Se guarda el UID para ignorarlo durante 3 segundos y evitar doble login
                    self.ultimo_uid = uid
                    self.root.after(3000, lambda: setattr(self, 'ultimo_uid', None))
                    self._manejar_uid(uid)

    def _manejar_uid(self, uid):
        if not self.conexion_bd:
            return

        usuario = self._buscar_usuario_por_uid(uid)

        if usuario:
            # Tarjeta conocida, se entra directo
            self._entrar(usuario)
        else:
            # Tarjeta nueva, se pide que se registre
            self.lbl_estado.config(text="Tarjeta nueva — Regístrate", fg=C_ORANGE)
            self.lbl_sub.config(text=f"UID: {uid}")

            def al_registrar(nuevo_usuario):
                self.lbl_estado.config(text="Acerca tu tarjeta NFC", fg=C_WHITE)
                self.lbl_sub.config(text="Para iniciar sesión o registrarte")
                self._entrar(nuevo_usuario)

            DialogoRegistrarNFC(self.root, self.conexion_bd, uid, al_registrar)

    def _entrar(self, usuario):
        self._desconectar_serial()
        self.root.withdraw()
        self.callback_login(usuario, self.conexion_bd)

    def mostrar(self):
        # Se llama al cerrar sesión para volver a esta pantalla
        self.root.deiconify()
        self.lbl_estado.config(text="Acerca tu tarjeta NFC", fg=C_WHITE)
        self.lbl_sub.config(text="Para iniciar sesión o registrarte")

    def _on_close(self):
        self._desconectar_serial()
        self.root.destroy()


# Pantalla que se muestra cuando el usuario ya inició sesión.
# Escucha el botón físico y suma puntos cada vez que se presiona.
class PantallaPrincipal:

    def __init__(self, root_espera, pantalla_espera, usuario, conexion_bd):
        self.root_espera     = root_espera
        self.pantalla_espera = pantalla_espera
        self.usuario         = usuario
        self.conexion_bd     = conexion_bd
        self.puerto_serial   = None
        self.ejecutando      = False

        self.root = tk.Toplevel(root_espera)
        self.root.title(f"EcoPoints — {usuario['nombre']} {usuario['apellido']}")
        self.root.geometry("980x700")
        self.root.resizable(False, False)
        self.root.configure(bg=C_BG)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._crear_ui()
        self._cargar_historial()
        self._conectar_serial_auto()

    def _crear_ui(self):
        # Barra superior con el nombre del usuario y el botón de cerrar sesión
        header = tk.Frame(self.root, bg=C_DARK, height=68)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="EcoPoints",
                 font=("Segoe UI", 18, "bold"),
                 bg=C_DARK, fg=C_WHITE
                 ).pack(side=tk.LEFT, padx=22, pady=14)

        tk.Button(header, text="Cerrar sesión",
                  font=("Segoe UI", 9, "bold"),
                  bg=C_RED, fg=C_WHITE,
                  relief=tk.FLAT, cursor="hand2",
                  padx=10, pady=5,
                  command=self._cerrar_sesion
                  ).pack(side=tk.RIGHT, padx=18, pady=16)

        tk.Label(header,
                 text=f"{self.usuario['nombre']} {self.usuario['apellido']}",
                 font=("Segoe UI", 11),
                 bg=C_DARK, fg=C_MUTED
                 ).pack(side=tk.RIGHT, padx=4, pady=16)

        tk.Frame(self.root, bg=C_GREEN, height=3).pack(fill=tk.X)

        # Cuerpo dividido en dos columnas
        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        col_izq = tk.Frame(body, bg=C_BG, width=380)
        col_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        col_izq.pack_propagate(False)

        self._crear_card_puntos(col_izq)
        self._crear_panel_serial(col_izq)
        self._crear_panel_boton(col_izq)

        col_der = tk.Frame(body, bg=C_BG)
        col_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._crear_panel_historial(col_der)

    def _crear_card_puntos(self, parent):
        card = tk.Frame(parent, bg=C_DARK)
        card.pack(fill=tk.X, pady=(0, 10))
        tk.Frame(card, bg=C_GREEN, height=4).pack(fill=tk.X)

        tk.Label(card, text="Puntos acumulados",
                 font=("Segoe UI", 10), bg=C_DARK, fg=C_MUTED
                 ).pack(pady=(14, 0))

        self.lbl_puntos = tk.Label(card,
                                    text=str(self.usuario['puntos_totales']),
                                    font=FONT_BIG, bg=C_DARK, fg=C_GREEN_LT)
        self.lbl_puntos.pack()

        tk.Label(card, text="puntos EcoPoints",
                 font=("Segoe UI", 12), bg=C_DARK, fg=C_MUTED
                 ).pack(pady=(0, 16))

    def _crear_panel_serial(self, parent):
        frame = tk.LabelFrame(parent, text=" Puerto Serial (ESP32) ",
                               font=("Segoe UI", 9),
                               bg=C_BG, fg=C_TEXT,
                               bd=1, relief=tk.GROOVE)
        frame.pack(fill=tk.X, pady=(0, 8))

        fila = tk.Frame(frame, bg=C_BG)
        fila.pack(fill=tk.X, padx=10, pady=8)

        self.combo_puertos = ttk.Combobox(fila, state="readonly", width=11)
        self.combo_puertos.pack(side=tk.LEFT, padx=(0, 4))

        tk.Button(fila, text="↺",
                  font=("Segoe UI", 10, "bold"),
                  bg=C_GRAY, fg=C_DARK,
                  relief=tk.FLAT, cursor="hand2",
                  command=self._refrescar_puertos
                  ).pack(side=tk.LEFT, padx=(0, 4))

        self.btn_conectar = tk.Button(fila, text="Conectar",
                                       font=("Segoe UI", 9, "bold"),
                                       bg=C_GREEN, fg=C_WHITE,
                                       relief=tk.FLAT, cursor="hand2",
                                       padx=8, pady=2,
                                       command=self._alternar_serial)
        self.btn_conectar.pack(side=tk.LEFT)

        self.lbl_serial = tk.Label(frame, text="Desconectado",
                                    font=FONT_SMALL, bg=C_BG, fg=C_MUTED)
        self.lbl_serial.pack(padx=10, pady=(0, 8))

        self._refrescar_puertos()

    def _crear_panel_boton(self, parent):
        self.panel_btn = tk.Frame(parent, bg=C_GRAY, bd=1, relief=tk.GROOVE)
        self.panel_btn.pack(fill=tk.BOTH, expand=True)

        self._barra_btn = tk.Frame(self.panel_btn, bg=C_BORDER, height=4)
        self._barra_btn.pack(fill=tk.X)

        self.lbl_btn_icon = tk.Label(self.panel_btn, text="🔘",
                                      font=("Segoe UI", 48), bg=C_GRAY)
        self.lbl_btn_icon.pack(pady=(28, 6))

        self.lbl_btn_titulo = tk.Label(self.panel_btn,
                                        text="Presiona el botón",
                                        font=("Segoe UI", 15, "bold"),
                                        bg=C_GRAY, fg=C_TEXT)
        self.lbl_btn_titulo.pack()

        self.lbl_btn_detalle = tk.Label(self.panel_btn,
                                         text="para registrar una botella reciclada",
                                         font=("Segoe UI", 10),
                                         bg=C_GRAY, fg=C_MUTED)
        self.lbl_btn_detalle.pack(pady=4)

        self.lbl_puntos_ganados = tk.Label(self.panel_btn, text="",
                                            font=("Segoe UI", 24, "bold"),
                                            bg=C_GRAY, fg=C_GREEN)
        self.lbl_puntos_ganados.pack(pady=(6, 28))

    def _crear_panel_historial(self, parent):
        fila = tk.Frame(parent, bg=C_BG)
        fila.pack(fill=tk.X, pady=(0, 6))

        tk.Label(fila, text="Historial de reciclaje",
                 font=("Segoe UI", 13, "bold"),
                 bg=C_BG, fg=C_DARK
                 ).pack(side=tk.LEFT)

        tk.Button(fila, text="Actualizar",
                  font=FONT_SMALL, bg=C_GRAY, fg=C_DARK,
                  relief=tk.FLAT, cursor="hand2",
                  padx=8, pady=3,
                  command=self._cargar_historial
                  ).pack(side=tk.RIGHT)

        tk.Frame(parent, bg=C_BORDER, height=1).pack(fill=tk.X, pady=(0, 8))

        frame_t = tk.Frame(parent, bg=C_BG)
        frame_t.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Eco.Treeview",
                         background=C_WHITE, fieldbackground=C_WHITE,
                         foreground=C_DARK, rowheight=28,
                         font=("Segoe UI", 10))
        style.configure("Eco.Treeview.Heading",
                         background=C_DARK, foreground=C_WHITE,
                         font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Eco.Treeview", background=[("selected", C_BLUE)])

        cols = ('Hora', 'Puntos', 'Usuario')
        self.tabla = ttk.Treeview(frame_t, columns=cols, show='headings',
                                   height=24, style="Eco.Treeview")
        for c, w in zip(cols, [100, 80, 180]):
            self.tabla.heading(c, text=c)
            self.tabla.column(c, width=w, anchor=tk.CENTER)

        sb = ttk.Scrollbar(frame_t, command=self.tabla.yview)
        self.tabla.configure(yscroll=sb.set)
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tabla.tag_configure("par",   background="#f8fafb")
        self.tabla.tag_configure("impar", background=C_WHITE)

    def _refrescar_puertos(self):
        puertos = [p.device for p in serial.tools.list_ports.comports()]
        self.combo_puertos['values'] = puertos
        if puertos:
            self.combo_puertos.current(0)

    def _conectar_serial_auto(self):
        # Al abrir la pantalla se intenta conectar automáticamente al primer puerto disponible
        puertos = [p.device for p in serial.tools.list_ports.comports()]
        if puertos:
            self.combo_puertos['values'] = puertos
            self.combo_puertos.current(0)
            self._conectar_serial()

    def _alternar_serial(self):
        if self.puerto_serial is None:
            self._conectar_serial()
        else:
            self._desconectar_serial()

    def _conectar_serial(self):
        puerto = self.combo_puertos.get()
        if not puerto:
            messagebox.showerror("Error", "Selecciona un puerto COM")
            return
        try:
            self.puerto_serial = serial.Serial(puerto, **SERIAL_CONFIG)
            self.lbl_serial.config(text=f"Conectado ({puerto})", fg=C_GREEN)
            self.btn_conectar.config(text="Desconectar", bg=C_RED)
            self.ejecutando = True
            threading.Thread(target=self._leer_serial, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar:\n{e}")

    def _desconectar_serial(self):
        self.ejecutando = False
        if self.puerto_serial:
            self.puerto_serial.close()
            self.puerto_serial = None
        self.lbl_serial.config(text="Desconectado", fg=C_MUTED)
        self.btn_conectar.config(text="Conectar", bg=C_GREEN)

    def _leer_serial(self):
        buffer = ""
        while self.ejecutando:
            try:
                if self.puerto_serial and self.puerto_serial.in_waiting:
                    char = self.puerto_serial.read().decode('utf-8', errors='ignore')
                    buffer += char
                    if char == '\n':
                        linea  = buffer.strip()
                        buffer = ""
                        if linea:
                            self.root.after(0, lambda l=linea: self._procesar_linea(l))
            except Exception as e:
                print(f"Error serial: {e}")
                self.ejecutando = False

    def _procesar_linea(self, linea):
        if linea.startswith("BOTON:"):
            self._otorgar_puntos()

    def _otorgar_puntos(self):
        try:
            # Se toma el primer tipo de botella (id_tipo=1) porque solo hay un botón
            cur = self.conexion_bd.cursor(dictionary=True)
            cur.execute(
                "SELECT id_tipo, nombre, puntos FROM tipos_botella ORDER BY id_tipo LIMIT 1"
            )
            botella = cur.fetchone()
            cur.close()

            if not botella:
                messagebox.showerror("Error", "No hay tipos de botella en la BD.")
                return

            cur2 = self.conexion_bd.cursor()
            cur2.execute(
                """INSERT INTO registro_reciclaje
                   (id_usuario, id_tipo, uid_leido, puntos_otorgados)
                   VALUES (%s, %s, 'BOTON', %s)""",
                (self.usuario['id_usuario'], botella['id_tipo'], botella['puntos'])
            )
            cur2.execute(
                "UPDATE usuarios SET puntos_totales = puntos_totales + %s WHERE id_usuario = %s",
                (botella['puntos'], self.usuario['id_usuario'])
            )
            self.conexion_bd.commit()
            cur2.close()

            # Se actualiza el contador en memoria y en pantalla
            self.usuario['puntos_totales'] += botella['puntos']
            self.lbl_puntos.config(text=str(self.usuario['puntos_totales']))

            self._flash_panel(C_GREEN,
                               f"+{botella['puntos']} puntos",
                               botella['nombre'])
            self._cargar_historial()

            try:
                import winsound
                winsound.Beep(1000, 150)
                winsound.Beep(1300, 150)
            except Exception:
                pass

        except Error as e:
            messagebox.showerror("Error al guardar", str(e))

    def _flash_panel(self, color, puntos_txt, detalle_txt):
        # Se pinta el panel de verde por 2.5 segundos como confirmación visual
        for w in [self.panel_btn, self.lbl_btn_icon, self.lbl_btn_titulo,
                  self.lbl_btn_detalle, self.lbl_puntos_ganados]:
            w.config(bg=color)
        self._barra_btn.config(bg=color)
        self.lbl_btn_titulo.config(text="¡Botella registrada!", fg=C_WHITE)
        self.lbl_btn_detalle.config(text=detalle_txt, fg=C_WHITE)
        self.lbl_puntos_ganados.config(text=puntos_txt, fg=C_WHITE)
        self.root.after(2500, self._resetear_panel)

    def _resetear_panel(self):
        for w in [self.panel_btn, self.lbl_btn_icon, self.lbl_btn_titulo,
                  self.lbl_btn_detalle, self.lbl_puntos_ganados]:
            w.config(bg=C_GRAY)
        self._barra_btn.config(bg=C_BORDER)
        self.lbl_btn_titulo.config(text="Presiona el botón", fg=C_TEXT)
        self.lbl_btn_detalle.config(text="para registrar una botella reciclada", fg=C_MUTED)
        self.lbl_puntos_ganados.config(text="", fg=C_GREEN)

    def _cargar_historial(self):
        # Trae los últimos 60 registros de toda la base de datos, no solo del usuario actual
        try:
            cur = self.conexion_bd.cursor(dictionary=True)
            cur.execute("""
                SELECT rr.fecha_hora,
                       rr.puntos_otorgados,
                       CONCAT(u.nombre, ' ', u.apellido) AS usuario
                FROM registro_reciclaje rr
                JOIN usuarios u ON rr.id_usuario = u.id_usuario
                ORDER BY rr.fecha_hora DESC
                LIMIT 60
            """)
            registros = cur.fetchall()
            cur.close()

            for item in self.tabla.get_children():
                self.tabla.delete(item)

            for i, r in enumerate(registros):
                tag = "par" if i % 2 == 0 else "impar"
                self.tabla.insert('', tk.END, tags=(tag,), values=(
                    r['fecha_hora'].strftime("%H:%M:%S"),
                    f"+{r['puntos_otorgados']}",
                    r['usuario']
                ))
        except Error as e:
            print(f"Error historial: {e}")

    def _cerrar_sesion(self):
        self._desconectar_serial()
        self.root.destroy()
        self.pantalla_espera.mostrar()

    def _on_close(self):
        # Si se cierra la ventana con la X se cierra toda la app
        self._desconectar_serial()
        self.root.destroy()
        self.root_espera.destroy()


def main():
    root = tk.Tk()
    ref = [None]

    def al_login(usuario, conexion_bd):
        PantallaPrincipal(root, ref[0], usuario, conexion_bd)

    pe = PantallaEspera(root, al_login)
    ref[0] = pe
    root.mainloop()


if __name__ == "__main__":
    main()


# Para usar 2 botones en el futuro, en el Arduino envía:
#   GPIO25 -> Serial.println("BOTON:600");
#   GPIO26 -> Serial.println("BOTON:1000");
#
# En _procesar_linea cambia a:
#   if linea.startswith("BOTON:"):
#       cap = int(linea.split(":")[1])
#       self._otorgar_puntos_por_capacidad(cap)
#
# En _otorgar_puntos_por_capacidad(self, cap_ml):
#   cur.execute("SELECT ... FROM tipos_botella WHERE capacidad_ml = %s", (cap_ml,))
