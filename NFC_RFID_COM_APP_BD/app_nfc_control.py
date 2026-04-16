"""
PROYECTO: SISTEMA DE CONTROL DE ACCESO CON NFC/RFID
Aplicación de Escritorio - Python con Tkinter

Descripción:
- Lee datos del puerto COM (ESP32)
- Conecta con base de datos MySQL
- Valida tarjetas NFC contra la base de datos
- Muestra información de usuarios con imágenes
- Registra acceso en la base de datos

Requisitos:
- python-serial (pip install pyserial)
- mysql-connector-python (pip install mysql-connector-python)
- Pillow (pip install Pillow)
- tkinter (generalmente incluido con Python)

Uso:
- python app_nfc_control.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from PIL import Image, ImageTk
import os
import json


# CONFIGURACIÓN DE CONEXIÓN A BASE DE DATOS

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Sin contraseña por defecto en Laragon
    'database': 'nfc_control_acceso',
    'port': 3306
}


# CONFIGURACIÓN DEL PUERTO SERIAL

SERIAL_CONFIG = {
    'baudrate': 115200,
    'timeout': 1
}

# CLASE PRINCIPAL DE LA APLICACIÓN

class AplicacionNFCControl:
    def __init__(self, root):
        """
        Inicializa la aplicación
        
        Parámetros:
        - root: ventana principal de Tkinter
        """
        self.root = root
        self.root.title("Sistema de Control de Acceso NFC/RFID")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Variables de control
        self.puerto_serial = None
        self.conexion_bd = None
        self.thread_lectura = None
        self.ejecutando = False
        self.ultimo_uid_leido = None
        self.usuario_actual = None
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Conectar a BD al iniciar
        self.conectar_base_datos()
        
    # ========================================================
    # INTERFAZ GRÁFICA
    # ========================================================
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica de la aplicación"""
        
        # Marco superior: Estado de conexión
        marco_estado = ttk.Frame(self.root)
        marco_estado.pack(fill=tk.X, padx=10, pady=10)
        
        # Etiqueta de estado de BD
        self.label_estado_bd = ttk.Label(
            marco_estado, 
            text="Estado BD: Desconectado", 
            foreground="red"
        )
        self.label_estado_bd.pack(side=tk.LEFT, padx=5)
        
        # Etiqueta de estado de Puerto Serial
        self.label_estado_serial = ttk.Label(
            marco_estado,
            text="Estado Puerto: Desconectado",
            foreground="red"
        )
        self.label_estado_serial.pack(side=tk.LEFT, padx=5)
        
        # Marco de control de puerto serial
        marco_puerto = ttk.LabelFrame(self.root, text="Configuración de Puerto Serial")
        marco_puerto.pack(fill=tk.X, padx=10, pady=10)
        
        # Selector de puerto
        ttk.Label(marco_puerto, text="Puerto COM:").pack(side=tk.LEFT, padx=5, pady=5)
        
        self.combo_puertos = ttk.Combobox(marco_puerto, state="readonly", width=15)
        self.combo_puertos.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Botón refrescar puertos
        ttk.Button(
            marco_puerto,
            text="Refrescar",
            command=self.refrescar_puertos
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Botón conectar/desconectar
        self.boton_conectar = ttk.Button(
            marco_puerto,
            text="Conectar",
            command=self.alternar_conexion_serial
        )
        self.boton_conectar.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Refrescar puertos disponibles
        self.refrescar_puertos()
        
        # Marco principal con dos columnas
        marco_principal = ttk.Frame(self.root)
        marco_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # COLUMNA IZQUIERDA: Lectura en tiempo real
        marco_lectura = ttk.LabelFrame(marco_principal, text="Lectura en Tiempo Real")
        marco_lectura.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Monitor de UID leído
        ttk.Label(marco_lectura, text="UID Hexadecimal:").pack(anchor=tk.W, padx=10, pady=5)
        self.text_uid_hex = tk.Text(marco_lectura, height=2, width=30, state=tk.DISABLED)
        self.text_uid_hex.pack(padx=10, pady=5, fill=tk.X)
        
        ttk.Label(marco_lectura, text="UID Decimal:").pack(anchor=tk.W, padx=10, pady=5)
        self.text_uid_dec = tk.Text(marco_lectura, height=2, width=30, state=tk.DISABLED)
        self.text_uid_dec.pack(padx=10, pady=5, fill=tk.X)
        
        ttk.Label(marco_lectura, text="UID Binario:").pack(anchor=tk.W, padx=10, pady=5)
        self.text_uid_bin = tk.Text(marco_lectura, height=3, width=30, state=tk.DISABLED)
        self.text_uid_bin.pack(padx=10, pady=5, fill=tk.X)
        
        # Botón para limpiar
        ttk.Button(
            marco_lectura,
            text="Limpiar Lecturas",
            command=self.limpiar_lecturas
        ).pack(padx=10, pady=5, fill=tk.X)
        
        # COLUMNA DERECHA: Información de usuario
        marco_usuario = ttk.LabelFrame(marco_principal, text="Información de Usuario")
        marco_usuario.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Marco para imagen
        marco_imagen = ttk.Frame(marco_usuario)
        marco_imagen.pack(padx=10, pady=10)
        
        self.label_imagen = tk.Label(
            marco_imagen,
            width=150,
            height=150,
            bg="gray"
        )
        self.label_imagen.pack()
        
        # Información del usuario
        ttk.Label(marco_usuario, text="Nombre:").pack(anchor=tk.W, padx=10, pady=2)
        self.label_nombre = tk.Label(marco_usuario, text="---", font=("Arial", 12, "bold"))
        self.label_nombre.pack(anchor=tk.W, padx=20, pady=2)
        
        ttk.Label(marco_usuario, text="Email:").pack(anchor=tk.W, padx=10, pady=2)
        self.label_email = tk.Label(marco_usuario, text="---", font=("Arial", 10))
        self.label_email.pack(anchor=tk.W, padx=20, pady=2)
        
        ttk.Label(marco_usuario, text="Teléfono:").pack(anchor=tk.W, padx=10, pady=2)
        self.label_telefono = tk.Label(marco_usuario, text="---", font=("Arial", 10))
        self.label_telefono.pack(anchor=tk.W, padx=20, pady=2)
        
        ttk.Label(marco_usuario, text="Estado:").pack(anchor=tk.W, padx=10, pady=2)
        self.label_estado = tk.Label(marco_usuario, text="---", font=("Arial", 10))
        self.label_estado.pack(anchor=tk.W, padx=20, pady=2)
        
        ttk.Label(marco_usuario, text="Última lectura:").pack(anchor=tk.W, padx=10, pady=2)
        self.label_ultima_lectura = tk.Label(marco_usuario, text="---", font=("Arial", 9))
        self.label_ultima_lectura.pack(anchor=tk.W, padx=20, pady=2)
        
        # Marco inferior: Registro de acceso
        marco_registro = ttk.LabelFrame(self.root, text="Registro de Acceso Reciente")
        marco_registro.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear tabla de registro
        self.crear_tabla_registro(marco_registro)
        
    def crear_tabla_registro(self, padre):
        """
        Crea la tabla de registro de acceso
        
        Parámetros:
        - padre: widget padre donde se crea la tabla
        """
        # Columnas
        columnas = ('Hora', 'UID', 'Usuario', 'Tipo', 'Estado')
        
        # Crear Treeview
        self.tabla_registro = ttk.Treeview(
            padre,
            columns=columnas,
            height=8,
            show='headings'
        )
        
        # Definir encabezados
        self.tabla_registro.heading('Hora', text='Hora')
        self.tabla_registro.heading('UID', text='UID Hexadecimal')
        self.tabla_registro.heading('Usuario', text='Usuario')
        self.tabla_registro.heading('Tipo', text='Tipo de Acceso')
        self.tabla_registro.heading('Estado', text='Estado')
        
        # Definir ancho de columnas
        self.tabla_registro.column('Hora', width=120)
        self.tabla_registro.column('UID', width=120)
        self.tabla_registro.column('Usuario', width=150)
        self.tabla_registro.column('Tipo', width=100)
        self.tabla_registro.column('Estado', width=100)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(
            padre,
            orient=tk.VERTICAL,
            command=self.tabla_registro.yview
        )
        self.tabla_registro.configure(yscroll=scrollbar.set)
        
        # Empaquetar
        self.tabla_registro.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # ========================================================
    # FUNCIONES DE CONEXIÓN
    # ========================================================
    
    def conectar_base_datos(self):
        """Conecta con la base de datos MySQL"""
        try:
            self.conexion_bd = mysql.connector.connect(**DB_CONFIG)
            self.label_estado_bd.config(text="Estado BD: Conectado", foreground="green")
            self.cargar_accesos_recientes()
        except Error as err:
            self.label_estado_bd.config(text=f"Estado BD: Error - {err}", foreground="red")
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la BD:\n{err}\n\n¿Has importado la base de datos con Laragon?")
    
    def refrescar_puertos(self):
        """Actualiza la lista de puertos seriales disponibles"""
        puertos = [puerto.device for puerto in serial.tools.list_ports.comports()]
        self.combo_puertos['values'] = puertos
        
        if puertos:
            self.combo_puertos.current(0)
    
    def alternar_conexion_serial(self):
        """Conecta o desconecta del puerto serial"""
        if self.puerto_serial is None:
            self.conectar_puerto_serial()
        else:
            self.desconectar_puerto_serial()
    
    def conectar_puerto_serial(self):
        """Conecta con el puerto serial seleccionado"""
        puerto = self.combo_puertos.get()
        
        if not puerto:
            messagebox.showerror("Error", "Selecciona un puerto COM")
            return
        
        try:
            self.puerto_serial = serial.Serial(puerto, **SERIAL_CONFIG)
            self.label_estado_serial.config(
                text=f"Estado Puerto: Conectado ({puerto}) ✓",
                foreground="green"
            )
            self.boton_conectar.config(text="Desconectar")
            
            # Iniciar thread de lectura
            self.ejecutando = True
            self.thread_lectura = threading.Thread(target=self.leer_puerto_serial, daemon=True)
            self.thread_lectura.start()
            
            messagebox.showinfo("Éxito", f"Conectado a {puerto}")
            
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"Error al conectar:\n{e}")
    
    def desconectar_puerto_serial(self):
        """Desconecta del puerto serial"""
        if self.puerto_serial:
            self.ejecutando = False
            self.puerto_serial.close()
            self.puerto_serial = None
            
            self.label_estado_serial.config(
                text="Estado Puerto: Desconectado",
                foreground="red"
            )
            self.boton_conectar.config(text="Conectar")
            
            messagebox.showinfo("Desconectado", "Desconectado del puerto serial")
    
    # ========================================================
    # LECTURA Y PROCESAMIENTO DE DATOS
    # ========================================================
    
    def leer_puerto_serial(self):
        """
        Lee datos del puerto serial en thread separado
        Procesa los UID leídos del módulo NFC
        """
        buffer = ""
        
        while self.ejecutando:
            try:
                if self.puerto_serial and self.puerto_serial.in_waiting:
                    # Leer carácter por carácter
                    caracter = self.puerto_serial.read().decode('utf-8', errors='ignore')
                    buffer += caracter
                    
                    # Procesar cuando se detecta nueva línea
                    if caracter == '\n':
                        linea = buffer.strip()
                        buffer = ""
                        
                        # Procesar línea recibida
                        if linea:
                            self.procesar_linea_serial(linea)
                            
            except Exception as e:
                print(f"Error en lectura serial: {e}")
                self.ejecutando = False
    
    def procesar_linea_serial(self, linea):
        # Detectar qué tipo de dato se está recibiendo
        if "UID HEX" in linea:
            uid_hex = linea.split(":",1)[1].strip()
            self.actualizar_ui_hexadecimal(uid_hex)
            
        elif "UID DECIMAL" in linea:
            uid_dec = linea.split(":",1)[1].strip()
            self.actualizar_ui_decimal(uid_dec)
            
        elif "UID BINARIO" in linea:
            uid_bin = linea.split(":",1)[1].strip()
            self.actualizar_ui_binario(uid_bin)
            
        elif "UID CONCATENADO" in linea:
            # Se agrega .upper() para asegurar compatibilidad con la BD
            uid_concatenado = linea.split(":")[1].strip().upper()
            self.procesar_uid_leido(uid_concatenado)
    
    def actualizar_ui_hexadecimal(self, uid_hex):
        """Actualiza el campo de UID hexadecimal"""
        self.text_uid_hex.config(state=tk.NORMAL)
        self.text_uid_hex.delete(1.0, tk.END)
        self.text_uid_hex.insert(1.0, uid_hex)
        self.text_uid_hex.config(state=tk.DISABLED)
    
    def actualizar_ui_decimal(self, uid_dec):
        """Actualiza el campo de UID decimal"""
        self.text_uid_dec.config(state=tk.NORMAL)
        self.text_uid_dec.delete(1.0, tk.END)
        self.text_uid_dec.insert(1.0, uid_dec)
        self.text_uid_dec.config(state=tk.DISABLED)
    
    def actualizar_ui_binario(self, uid_bin):
        """Actualiza el campo de UID binario"""
        self.text_uid_bin.config(state=tk.NORMAL)
        self.text_uid_bin.delete(1.0, tk.END)
        self.text_uid_bin.insert(1.0, uid_bin)
        self.text_uid_bin.config(state=tk.DISABLED)
    
    def procesar_uid_leido(self, uid):
        """
        Procesa el UID leído y busca en la base de datos
        
        Parámetros:
        - uid: UID hexadecimal concatenado (ej: 3AB42DF1)
        """
        self.ultimo_uid_leido = uid
        
        try:
            cursor = self.conexion_bd.cursor(dictionary=True)
            
            # Consulta SQL para obtener usuario por UID
            consulta = """
                SELECT u.*, tn.id_tarjeta
                FROM usuarios u
                JOIN tarjetas_nfc tn ON u.id_usuario = tn.id_usuario
                WHERE tn.uid_hexadecimal = %s AND tn.estado = 'activa'
                LIMIT 1
            """
            
            cursor.execute(consulta, (uid,))
            usuario = cursor.fetchone()
            cursor.close()
            
            if usuario:
                # Usuario encontrado - Acceso exitoso
                self.mostrar_informacion_usuario(usuario)
                self.registrar_acceso(uid, usuario['id_usuario'], 'exitoso')
                self.reproducir_sonido_exito()
            else:
                # UID no registrado
                self.mostrar_acceso_denegado(uid)
                self.registrar_acceso(uid, None, 'no_registrado')
                self.reproducir_sonido_error()
                
        except Error as err:
            messagebox.showerror("Error de BD", f"Error al consultar: {err}")
    
    def mostrar_informacion_usuario(self, usuario):
        """
        Muestra la información del usuario en la interfaz
        
        Parámetros:
        - usuario: diccionario con datos del usuario
        """
        self.usuario_actual = usuario
        
        # Actualizar etiquetas
        self.label_nombre.config(
            text=f"{usuario['nombre']} {usuario['apellido']}",
            foreground="green"
        )
        self.label_email.config(text=usuario['email'])
        self.label_telefono.config(text=usuario['telefono'] or "No disponible")
        
        estado_color = "green" if usuario['estado'] == 'activo' else "red"
        self.label_estado.config(text=usuario['estado'], foreground=estado_color)
        
        self.label_ultima_lectura.config(
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Cargar y mostrar imagen
        if usuario['ruta_imagen'] and os.path.exists(usuario['ruta_imagen']):
            self.mostrar_imagen(usuario['ruta_imagen'])
        else:
            self.mostrar_imagen_placeholder()
    
    def mostrar_imagen(self, ruta):
        """
        Muestra una imagen en el label de imagen
        
        Parámetros:
        - ruta: ruta del archivo de imagen
        """
        try:
            imagen = Image.open(ruta)
            imagen.thumbnail((150, 150), Image.Resampling.LANCZOS)
            foto = ImageTk.PhotoImage(imagen)
            
            self.label_imagen.config(image=foto)
            self.label_imagen.image = foto  # Mantener referencia
        except Exception as e:
            print(f"Error al cargar imagen: {e}")
            self.mostrar_imagen_placeholder()
    
    def mostrar_imagen_placeholder(self):
        """Muestra imagen placeholder cuando no hay imagen disponible"""
        self.label_imagen.config(image="", text="Sin imagen", bg="lightgray")
    
    def mostrar_acceso_denegado(self, uid):
        """
        Muestra información de acceso denegado
        
        Parámetros:
        - uid: UID que se intentó usar
        """
        self.label_nombre.config(text="ACCESO DENEGADO", foreground="red")
        self.label_email.config(text="UID no registrado en el sistema")
        self.label_telefono.config(text="")
        self.label_estado.config(text="No autorizado", foreground="red")
        self.label_ultima_lectura.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.mostrar_imagen_placeholder()
    
    def reproducir_sonido_exito(self):
        """Reproduce un sonido al acceso exitoso"""
        # En Windows
        try:
            import winsound
            winsound.Beep(1000, 200)  # 1000Hz, 200ms
        except:
            pass  # No está en Windows o no hay winsound
    
    def reproducir_sonido_error(self):
        """Reproduce un sonido al acceso denegado"""
        try:
            import winsound
            winsound.Beep(300, 500)  # 300Hz, 500ms
            winsound.Beep(300, 500)  # Dos veces
        except:
            pass
    
    # ========================================================
    # REGISTRO Y BASE DE DATOS
    # ========================================================
    
    def registrar_acceso(self, uid, id_usuario, estado):
        """
        Registra un acceso en la base de datos
        
        Parámetros:
        - uid: UID leído
        - id_usuario: ID del usuario (None si no existe)
        - estado: 'exitoso', 'no_registrado'
        """
        try:
            cursor = self.conexion_bd.cursor()
            
            consulta = """
                INSERT INTO registro_acceso 
                (id_usuario, uid_leido, tipo_acceso, estado_validacion)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(consulta, (id_usuario, uid, 'entrada', estado))
            self.conexion_bd.commit()
            cursor.close()
            
            # Actualizar tabla de registro
            self.cargar_accesos_recientes()
            
        except Error as err:
            print(f"Error al registrar acceso: {err}")
    
    def cargar_accesos_recientes(self):
        """Carga los últimos accesos en la tabla"""
        try:
            cursor = self.conexion_bd.cursor(dictionary=True)
            
            consulta = """
                SELECT ra.fecha_hora, ra.uid_leido, u.nombre, u.apellido,
                       ra.tipo_acceso, ra.estado_validacion
                FROM registro_acceso ra
                LEFT JOIN usuarios u ON ra.id_usuario = u.id_usuario
                ORDER BY ra.fecha_hora DESC
                LIMIT 20
            """
            
            cursor.execute(consulta)
            accesos = cursor.fetchall()
            cursor.close()
            
            # Limpiar tabla
            for item in self.tabla_registro.get_children():
                self.tabla_registro.delete(item)
            
            # Insertar datos
            for acceso in accesos:
                nombre_usuario = f"{acceso['nombre']} {acceso['apellido']}" if acceso['nombre'] else "Desconocido"
                
                self.tabla_registro.insert('', 0, values=(
                    acceso['fecha_hora'].strftime("%H:%M:%S"),
                    acceso['uid_leido'],
                    nombre_usuario,
                    acceso['tipo_acceso'],
                    acceso['estado_validacion']
                ))
                
        except Error as err:
            print(f"Error al cargar accesos: {err}")
    
    def limpiar_lecturas(self):
        """Limpia los campos de lectura"""
        self.text_uid_hex.config(state=tk.NORMAL)
        self.text_uid_hex.delete(1.0, tk.END)
        self.text_uid_hex.config(state=tk.DISABLED)
        
        self.text_uid_dec.config(state=tk.NORMAL)
        self.text_uid_dec.delete(1.0, tk.END)
        self.text_uid_dec.config(state=tk.DISABLED)
        
        self.text_uid_bin.config(state=tk.NORMAL)
        self.text_uid_bin.delete(1.0, tk.END)
        self.text_uid_bin.config(state=tk.DISABLED)
        
        self.label_nombre.config(text="---")
        self.label_email.config(text="---")
        self.label_telefono.config(text="---")
        self.label_estado.config(text="---")
        self.label_ultima_lectura.config(text="---")
        self.mostrar_imagen_placeholder()

# ============================================================
# PUNTO DE ENTRADA DE LA APLICACIÓN
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionNFCControl(root)
    root.mainloop()