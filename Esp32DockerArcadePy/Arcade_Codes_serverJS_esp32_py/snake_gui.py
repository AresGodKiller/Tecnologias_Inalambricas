"""
snake_gui.py — Juego de Snake para el Arcade RFID


Este archivo contiene todo el juego Snake que se lanza desde
launcher_esp32_wifi.py cuando un jugador acerca su tarjeta.

El juego recibe los datos del jugador (nombre y puntaje acumulado)
como parámetro al crearse, los muestra en pantalla durante la partida
y al cerrar la ventana deja el puntaje de esa sesión en self.score
para que el launcher lo recoja y se lo mande al ESP32.

Estética: gótico suave — piedra oscura, dorado envejecido, tipografía serif.

Controles:
  W A S D  o  flechas del teclado  →  mover la serpiente
  R                                 →  reiniciar la partida
  ESC                               →  salir del juego
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import math

# Dimensiones del tablero en celdas
COLS = 22   # Cantidad de columnas
ROWS = 16   # Cantidad de filas

# Tamaño en píxeles de cada celda del tablero
CELL = 30

# Velocidad inicial del juego en milisegundos entre cada fotograma.
# Un número más alto = movimiento más lento.
FPS_INIT = 150

# Velocidad máxima que puede alcanzar el juego (límite mínimo del intervalo)
FPS_MIN  = 60

# Cuántos ms se reduce el intervalo cada vez que la serpiente come algo.
# Controla qué tan rápido aumenta la dificultad.
SPEED_STEP = 6

# Puntos que da cada tipo de comida
PTS_APPLE = 10   # Manzana normal
PTS_SKULL = 50   # Calavera (aparece menos seguido pero vale más)


class SnakeApp(tk.Tk):
    """
    Ventana principal del juego Snake.

    Hereda de tk.Tk para ser la ventana raíz de tkinter.
    El launcher la crea pasándole el dict del jugador y llama
    a mainloop() para que el juego corra hasta que el jugador
    lo cierre. Al terminar, self.score tiene los puntos de esa sesión.

    Parámetros:
      jugador (dict): datos del jugador con las claves:
        - name_disp (str): nombre que aparece en pantalla
        - score     (int): puntaje acumulado de sesiones anteriores
        - usr       (str): nombre de usuario en la base de datos
        - id_rfid   (str): UID de la tarjeta del jugador
    """

    #  Paleta de colores 
    # Todos los colores del juego están definidos aquí para que sea fácil
    # cambiar la estética sin tener que buscar valores sueltos en el código.

    BG_WIN      = '#1C1A18'   # Fondo de la ventana principal (carbón cálido)
    BG_BOARD    = '#211F1C'   # Fondo del tablero de juego (piedra oscura)
    BG_CELL_ALT = '#252320'   # Color alterno para el damero sutil del tablero
    BG_HUD      = '#17150F'   # Fondo del panel de puntaje (cuero oscuro)
    BG_HEADER   = '#17150F'   # Fondo del encabezado con el título

    CLR_BORDER  = '#5C4A1E'   # Color de los bordes y separadores (dorado envejecido)
    CLR_SNAKE_H = '#C8A84B'   # Color de la cabeza de la serpiente (dorado brillante)
    CLR_SNAKE_B = '#9B7D2E'   # Color del cuerpo de la serpiente (dorado medio)
    CLR_SNAKE_T = '#6B5520'   # Color de la cola de la serpiente (dorado oscuro)

    CLR_APPLE   = '#8B1A1A'   # Color base de la manzana (carmesí oscuro)
    CLR_APPLE_S = '#C0392B'   # Brillo de la manzana
    CLR_SKULL   = '#D4C5A9'   # Color de la calavera (hueso)

    CLR_GOLD     = '#C8A84B'  # Dorado principal para textos importantes
    CLR_GOLD_DIM = '#7A6030'  # Dorado apagado para textos secundarios
    CLR_PARCH    = '#D4C5A9'  # Pergamino para textos de información
    CLR_DIM      = '#5A5040'  # Gris cálido para etiquetas poco importantes
    CLR_DEAD     = '#6B1A1A'  # Rojo oscuro para el estado de muerte
    CLR_MSG_OK   = '#C8A84B'  # Color de mensajes de éxito
    CLR_MSG_DIE  = '#8B1A1A'  # Color del mensaje de game over

    CLR_BTN_BG  = '#2A2318'   # Fondo de los botones
    CLR_BTN_FG  = '#C8A84B'   # Texto de los botones
    CLR_BTN_BD  = '#5C4A1E'   # Borde de los botones

    # Mapa de teclas a direcciones (dx, dy).
    # Se aceptan tanto las flechas del teclado como WASD.
    DIRS = {
        'Up':    (0, -1), 'w': (0, -1),
        'Down':  (0,  1), 's': (0,  1),
        'Left':  (-1, 0), 'a': (-1, 0),
        'Right': ( 1, 0), 'd': ( 1, 0),
    }

    def __init__(self, jugador=None):
        super().__init__()

        # Datos del jugador que viene del launcher.
        # Si no se pasan datos (por ejemplo al correr el archivo solo),
        # se usan valores por defecto para poder probar el juego.
        self.jugador       = jugador or {}
        self._name_disp    = self.jugador.get('name_disp', 'Invitado')
        self._score_previo = self.jugador.get('score', 0)

        # Puntaje de esta sesión. El launcher lee este valor al cerrar
        # la ventana para saber cuántos puntos mandarle al ESP32.
        self.score = 0

        self.title('Snake — Arcade')
        self.resizable(False, False)
        self.configure(bg=self.BG_WIN)
        self.protocol('WM_DELETE_WINDOW', self._on_close)

        # Fuentes tipográficas del proyecto (todas en Georgia para consistencia visual)
        self._f_title  = tkfont.Font(family='Georgia', size=20, weight='bold')
        self._f_player = tkfont.Font(family='Georgia', size=10, slant='italic')
        self._f_score  = tkfont.Font(family='Georgia', size=30, weight='bold')
        self._f_label  = tkfont.Font(family='Georgia', size=9)
        self._f_lvl    = tkfont.Font(family='Georgia', size=22, weight='bold')
        self._f_msg    = tkfont.Font(family='Georgia', size=14, weight='bold')
        self._f_btn    = tkfont.Font(family='Georgia', size=10, weight='bold')
        self._f_sub    = tkfont.Font(family='Georgia', size=9, slant='italic')

        self._build_ui()
        self._bind_keys()
        self._init_game()

    #  Construcción de la interfaz  ───────────────────────────────────────────

    def _build_ui(self):
        """
        Construye todos los elementos visuales de la ventana del juego.

        La ventana se divide en estas secciones de arriba hacia abajo:
          1. Borde dorado superior
          2. Header: título del juego y nombre del jugador
          3. HUD: puntaje actual, nivel y récord previo
          4. Canvas: el tablero donde se dibuja el juego
          5. Barra inferior: mensaje de estado y botones
          6. Leyenda de controles
          7. Borde dorado inferior
        """
        W = COLS * CELL  # Ancho total del tablero en píxeles

        # Borde decorativo superior
        tk.Frame(self, bg=self.CLR_BORDER, height=2).pack(fill='x')

        # ── Encabezado ──
        hdr = tk.Frame(self, bg=self.BG_HEADER, pady=10)
        hdr.pack(fill='x')

        # Lado izquierdo del header: título y subtítulo
        left_hdr = tk.Frame(hdr, bg=self.BG_HEADER)
        left_hdr.pack(side='left', padx=16)
        tk.Label(left_hdr, text='✦ SNAKE ✦',
                 font=self._f_title,
                 bg=self.BG_HEADER, fg=self.CLR_GOLD).pack(anchor='w')
        tk.Label(left_hdr, text='Arcade Arcano',
                 font=self._f_sub,
                 bg=self.BG_HEADER, fg=self.CLR_GOLD_DIM).pack(anchor='w')

        # Lado derecho del header: nombre del jugador y su puntaje acumulado previo
        right_hdr = tk.Frame(hdr, bg=self.BG_HEADER)
        right_hdr.pack(side='right', padx=16)
        tk.Label(right_hdr, text=self._name_disp,
                 font=self._f_player,
                 bg=self.BG_HEADER, fg=self.CLR_PARCH).pack(anchor='e')
        tk.Label(right_hdr,
                 text=f'Alma acumulada: {self._score_previo} pts',
                 font=self._f_label,
                 bg=self.BG_HEADER, fg=self.CLR_DIM).pack(anchor='e')

        # Separador dorado entre header y HUD
        tk.Frame(self, bg=self.CLR_BORDER, height=1).pack(fill='x')

        # ── HUD (heads-up display) ──
        # Muestra el puntaje de la sesión actual, el nivel y el récord previo
        hud = tk.Frame(self, bg=self.BG_HUD, pady=10)
        hud.pack(fill='x')

        # Columna izquierda: puntaje de la sesión actual
        score_col = tk.Frame(hud, bg=self.BG_HUD)
        score_col.pack(side='left', padx=20)
        tk.Label(score_col, text='ALMAS',
                 font=self._f_label, bg=self.BG_HUD,
                 fg=self.CLR_DIM).pack(anchor='w')
        self._lbl_score = tk.Label(score_col, text='0',
                                   font=self._f_score,
                                   bg=self.BG_HUD, fg=self.CLR_GOLD)
        self._lbl_score.pack(anchor='w')

        # Columna central: nivel actual en números romanos
        lvl_col = tk.Frame(hud, bg=self.BG_HUD)
        lvl_col.pack(side='left', padx=16)
        tk.Label(lvl_col, text='CÍRCULO',
                 font=self._f_label, bg=self.BG_HUD,
                 fg=self.CLR_DIM).pack(anchor='w')
        self._lbl_level = tk.Label(lvl_col, text='I',
                                   font=self._f_lvl,
                                   bg=self.BG_HUD, fg=self.CLR_PARCH)
        self._lbl_level.pack(anchor='w')

        # Columna derecha: puntaje acumulado de sesiones anteriores (el récord histórico)
        rec_col = tk.Frame(hud, bg=self.BG_HUD)
        rec_col.pack(side='right', padx=20)
        tk.Label(rec_col, text='RÉCORD',
                 font=self._f_label, bg=self.BG_HUD,
                 fg=self.CLR_DIM).pack(anchor='e')
        self._lbl_best = tk.Label(rec_col,
                                  text=str(self._score_previo),
                                  font=tkfont.Font(family='Georgia', size=22, weight='bold'),
                                  bg=self.BG_HUD, fg=self.CLR_GOLD_DIM)
        self._lbl_best.pack(anchor='e')

        # Separador dorado entre HUD y tablero
        tk.Frame(self, bg=self.CLR_BORDER, height=1).pack(fill='x')

        # ── Canvas del tablero ──
        # El frame con padx/pady de 1 crea el borde dorado alrededor del canvas
        board_frame = tk.Frame(self, bg=self.CLR_BORDER, padx=1, pady=1)
        board_frame.pack()
        self._canvas = tk.Canvas(board_frame,
                                 width=W, height=ROWS * CELL,
                                 bg=self.BG_BOARD, highlightthickness=0)
        self._canvas.pack()

        # Separador dorado entre tablero y barra inferior
        tk.Frame(self, bg=self.CLR_BORDER, height=1).pack(fill='x')

        # ── Barra inferior ──
        bot = tk.Frame(self, bg=self.BG_WIN, pady=8)
        bot.pack(fill='x', padx=14)

        # Etiqueta donde aparece el mensaje de game over o estado del juego
        self._lbl_msg = tk.Label(bot, text='',
                                 font=self._f_msg,
                                 bg=self.BG_WIN, fg=self.CLR_MSG_DIE)
        self._lbl_msg.pack(side='left')

        # Botones de acción en el lado derecho
        btns = tk.Frame(bot, bg=self.BG_WIN)
        btns.pack(side='right')

        def _btn(txt, cmd):
            """Crea un botón con el estilo visual del proyecto."""
            b = tk.Button(btns, text=txt, command=cmd,
                          font=self._f_btn,
                          bg=self.CLR_BTN_BG, fg=self.CLR_BTN_FG,
                          activebackground='#3A3020',
                          activeforeground=self.CLR_GOLD,
                          relief='flat', bd=0,
                          highlightthickness=1,
                          highlightbackground=self.CLR_BTN_BD,
                          padx=12, pady=5, cursor='hand2')
            b.pack(side='left', padx=5)

        _btn('Nueva partida', self._init_game)
        _btn('Salir', self._on_close)

        # Leyenda de controles en la parte inferior de la ventana
        tk.Label(self,
                 text='W A S D  ·  ↑ ← ↓ →  ·  R = reiniciar  ·  ESC = salir',
                 font=self._f_sub, bg=self.BG_WIN, fg=self.CLR_DIM
                 ).pack(pady=(2, 8))

        # Borde decorativo inferior
        tk.Frame(self, bg=self.CLR_BORDER, height=2).pack(fill='x')

    #  Utilidades  

    def _roman(self, n):
        """
        Convierte un número entero a su representación en números romanos.
        Se usa para mostrar el nivel actual en el HUD.
        Solo cubre hasta el nivel X (10) que es el máximo alcanzable
        con la configuración actual de velocidad.
        """
        vals = [(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]
        r = ''
        for v, s in vals:
            while n >= v:
                r += s; n -= v
        return r

    #  Controles del teclado  

    def _bind_keys(self):
        """
        Registra los eventos de teclado que controlan el juego.
        Se aceptan tanto mayúsculas como minúsculas para WASD.
        """
        for key in ('Up','Down','Left','Right','w','a','s','d','W','A','S','D'):
            self.bind(f'<{key}>', self._on_key)
        self.bind('<r>', lambda e: self._init_game())
        self.bind('<R>', lambda e: self._init_game())
        self.bind('<Escape>', lambda e: self._on_close())

    #  Lógica del juego  

    def _init_game(self):
        """
        Inicializa o reinicia el estado del juego para una nueva partida.

        La serpiente arranca en el centro del tablero moviéndose hacia la derecha.
        El puntaje de sesión (self.score) NO se resetea al presionar R porque
        el jugador puede seguir acumulando puntos en múltiples partidas
        dentro de la misma sesión. Solo se reinicia cuando se cierra el juego
        y el launcher crea una nueva instancia de SnakeApp.
        """
        cx, cy = COLS // 2, ROWS // 2

        # La serpiente es una lista de tuplas (x, y). El primer elemento es la cabeza.
        # Arranca con 3 segmentos en el centro del tablero.
        self._snake = [(cx, cy), (cx-1, cy), (cx-2, cy)]

        # Dirección actual y la siguiente (separadas para evitar cambios a mitad de frame)
        self._dir  = (1, 0)
        self._next = (1, 0)

        self._apples = []      # Lista de frutas activas en el tablero: [(pos, tipo)]
        self._tick   = FPS_INIT  # Intervalo entre frames en milisegundos
        self._alive  = True    # False cuando la serpiente choca
        self._eaten  = 0       # Contador de items comidos (para calcular el nivel)
        self._level  = 1       # Nivel actual

        # Actualizar el HUD con el estado inicial
        self._lbl_score.config(text=str(self.score), fg=self.CLR_GOLD)
        self._lbl_level.config(text='I')
        self._lbl_msg.config(text='')

        # Generar la primera fruta y arrancar el loop
        self._spawn_apple()
        self._draw()

        # Cancelar el loop anterior si existía (para no tener dos corriendo a la vez)
        if hasattr(self, '_after_id'):
            self.after_cancel(self._after_id)
        self._loop()

    def _spawn_apple(self):
        """
        Genera una nueva fruta en una posición aleatoria del tablero
        que no esté ocupada por la serpiente ni por otra fruta.

        El tipo de fruta se elige aleatoriamente:
          - 82% de probabilidad: manzana normal (10 pts)
          - 18% de probabilidad: calavera (50 pts)

        Si no hay celdas libres (tablero lleno), no genera nada.
        """
        occupied = set(self._snake) | {a[0] for a in self._apples}
        free = [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in occupied]
        if not free:
            return  # Tablero lleno, no hay donde poner fruta

        pos  = random.choice(free)
        kind = 'skull' if random.random() < 0.18 else 'apple'
        self._apples.append((pos, kind))

    def _on_key(self, event):
        """
        Procesa la tecla presionada y actualiza la dirección siguiente.

        La dirección opuesta a la actual se ignora para evitar que la
        serpiente se doblegue sobre sí misma y muera instantáneamente.
        El cambio de dirección se aplica en el siguiente frame (_step),
        no inmediatamente, para evitar problemas si el jugador presiona
        varias teclas entre un frame y el siguiente.
        """
        key = event.keysym.lower() if len(event.keysym) == 1 else event.keysym
        if key in self.DIRS:
            nd = self.DIRS[key]
            # Verificar que la dirección nueva no sea exactamente la opuesta a la actual
            if nd[0] != -self._dir[0] or nd[1] != -self._dir[1]:
                self._next = nd

    def _loop(self):
        """
        Loop principal del juego. Se llama a sí mismo usando after()
        para que tkinter pueda seguir procesando eventos entre frames.

        El intervalo entre llamadas es self._tick, que va disminuyendo
        cada vez que la serpiente come algo, aumentando la dificultad.
        """
        if self._alive:
            self._step()
            self._after_id = self.after(self._tick, self._loop)

    def _step(self):
        """
        Avanza el juego un frame: mueve la serpiente, detecta colisiones
        y verifica si comió alguna fruta.

        Proceso de cada frame:
          1. Aplicar la dirección pendiente
          2. Calcular la nueva posición de la cabeza
          3. Verificar colisión con pared o con el cuerpo propio
          4. Mover la serpiente (agregar nueva cabeza, quitar cola)
          5. Verificar si la nueva cabeza está sobre una fruta
          6. Si comió: sumar puntos, aumentar velocidad, subir nivel
          7. Redibujar el tablero
        """
        # Aplicar la dirección que el jugador eligió en el frame anterior
        self._dir = self._next
        hx, hy   = self._snake[0]
        nx, ny   = hx + self._dir[0], hy + self._dir[1]

        # Verificar colisión con las paredes del tablero
        if not (0 <= nx < COLS and 0 <= ny < ROWS):
            self._die(); return

        # Verificar colisión con el cuerpo propio (excepto la cola, que se mueve)
        if (nx, ny) in self._snake[:-1]:
            self._die(); return

        # Mover la serpiente: agregar nueva cabeza al frente
        self._snake.insert(0, (nx, ny))

        # Verificar si la nueva cabeza cayó sobre una fruta
        eaten = next((a for a in self._apples if a[0] == (nx, ny)), None)
        if eaten:
            # La serpiente comió: no se quita la cola (crece) y se suman puntos
            self._apples.remove(eaten)
            pts = PTS_SKULL if eaten[1] == 'skull' else PTS_APPLE
            self.score  += pts
            self._eaten += 1

            # Aumentar la velocidad reduciendo el intervalo entre frames
            self._tick  = max(FPS_MIN, self._tick - SPEED_STEP)

            # El nivel sube cada 5 items comidos
            self._level = self._eaten // 5 + 1

            # Flash del puntaje en un color diferente según qué se comió
            flash_color = self.CLR_SKULL if eaten[1] == 'skull' else '#D4A017'
            self._lbl_score.config(text=str(self.score), fg=flash_color)
            self.after(250, lambda: self._lbl_score.config(fg=self.CLR_GOLD))
            self._lbl_level.config(text=self._roman(self._level))

            # Generar una nueva fruta para reemplazar la que se comió
            self._spawn_apple()
        else:
            # No comió: quitar la cola para que la serpiente se mueva sin crecer
            self._snake.pop()

        self._draw()

    def _die(self):
        """
        Maneja el fin de la partida cuando la serpiente choca.

        Cancela el loop del juego, muestra el mensaje de game over
        con el puntaje final y redibuja la serpiente en color de muerte.
        El jugador puede presionar R para reiniciar o cerrar la ventana.
        """
        self._alive = False

        # Cancelar el loop explícitamente para evitar que siga corriendo
        if hasattr(self, '_after_id'):
            self.after_cancel(self._after_id)

        self._lbl_msg.config(
            text=f'✝  {self.score} almas cosechadas  —  R para renacer',
            fg=self.CLR_MSG_DIE
        )
        self._draw(dead=True)

    #  Dibujo 

    def _draw(self, dead=False):
        """
        Redibuja el tablero completo en cada frame.

        El orden de dibujo es importante para que las capas se superpongan
        correctamente: primero el fondo, luego la comida, luego la serpiente.

        Parámetros:
          dead (bool): si es True, dibuja la serpiente en tonos oscuros
                       para indicar que el juego terminó.
        """
        c = self._canvas
        c.delete('all')  # Limpiar el canvas antes de redibujar

        # ── Fondo: damero de piedra sutil ──
        # Las celdas pares tienen un color ligeramente diferente para dar
        # profundidad al tablero sin distraer al jugador.
        for x in range(COLS):
            for y in range(ROWS):
                if (x + y) % 2 == 0:
                    c.create_rectangle(
                        x*CELL, y*CELL, x*CELL+CELL, y*CELL+CELL,
                        fill=self.BG_CELL_ALT, outline=''
                    )

        #  Dibujar la comida 
        for (ax, ay), kind in self._apples:
            cx_ = ax*CELL + CELL//2
            cy_ = ay*CELL + CELL//2
            if kind == 'skull':
                self._draw_skull(c, cx_, cy_)
            else:
                # Manzana carmesí con un destello para darle volumen
                x1, y1 = ax*CELL+4, ay*CELL+5
                x2, y2 = ax*CELL+CELL-4, ay*CELL+CELL-3
                c.create_oval(x1, y1, x2, y2,
                              fill=self.CLR_APPLE, outline='#4A0000', width=1)
                # Brillo semitransparente en la parte superior de la manzana
                c.create_oval(x1+3, y1+2, x1+8, y1+7,
                              fill='#C0392B', outline='', stipple='gray50')
                # Tallito verde
                c.create_line(cx_, y1, cx_-3, y1-5,
                              fill='#3A5A20', width=2)

        #  Dibujar la serpiente 
        n = len(self._snake)
        for i, (sx, sy) in enumerate(self._snake):
            x1, y1 = sx*CELL+2, sy*CELL+2
            x2, y2 = sx*CELL+CELL-2, sy*CELL+CELL-2

            # El color varía según si está muerta, si es cabeza, cuerpo o cola.
            # Esto crea un degradado visual de dorado brillante a dorado oscuro.
            if dead:
                fill = '#3A2A1A'   # Marrón oscuro cuando está muerta
                out  = '#2A1A0A'
            elif i == 0:
                fill = self.CLR_SNAKE_H   # Cabeza: dorado más brillante
                out  = '#A88030'
            elif i < n // 3:
                fill = self.CLR_SNAKE_B   # Primer tercio del cuerpo
                out  = '#7A5C20'
            else:
                fill = self.CLR_SNAKE_T   # Cola: dorado más oscuro
                out  = '#4A3A10'

            c.create_rectangle(x1, y1, x2, y2,
                               fill=fill, outline=out, width=1)

            # Línea diagonal sutil en cada segmento del cuerpo para simular escamas
            if not dead and i > 0:
                c.create_line(x1+4, y1+4, x2-4, y2-4,
                              fill=out, width=1)

            # Ojos en la cabeza: dos puntos negros con pupila roja
            if i == 0 and not dead:
                dx, dy = self._dir
                cx__ = sx*CELL + CELL//2
                cy__ = sy*CELL + CELL//2
                ox, oy = -dy, dx  # Vector perpendicular a la dirección de movimiento
                for sign in (1, -1):
                    ex = cx__ + ox*5*sign + dx*6
                    ey = cy__ + oy*5*sign + dy*6
                    c.create_oval(ex-3, ey-3, ex+3, ey+3,
                                  fill='#1A1008', outline='')
                    # Pupila roja para darle un toque siniestro
                    c.create_oval(ex-1, ey-1, ex+1, ey+1,
                                  fill='#8B1A1A', outline='')

    def _draw_skull(self, c, cx, cy):
        """
        Dibuja una calavera estilizada en la posición indicada.
        Se usa para el tipo de comida que vale más puntos.

        Parámetros:
          c:  el canvas de tkinter donde se dibuja
          cx: coordenada x del centro de la celda en píxeles
          cy: coordenada y del centro de la celda en píxeles
        """
        r = 9  # Radio base de la calavera

        # Cráneo: óvalo superior
        c.create_oval(cx-r, cy-r, cx+r, cy+r//2,
                      fill=self.CLR_SKULL, outline='#9A8A74', width=1)

        # Mandíbula: rectángulo inferior
        c.create_rectangle(cx-r+3, cy, cx+r-3, cy+r-2,
                            fill=self.CLR_SKULL, outline='#9A8A74', width=1)

        # Cuencas de los ojos: óvalos oscuros
        for ox in (-4, 4):
            c.create_oval(cx+ox-3, cy-5, cx+ox+3, cy+1,
                          fill=self.BG_BOARD, outline='')

        # Dientes: tres rectángulos pequeños en la mandíbula
        for tx in (-5, -1, 3):
            c.create_rectangle(cx+tx, cy+2, cx+tx+3, cy+r-3,
                               fill=self.BG_BOARD, outline='')

    #  Cierre de la ventana 

    def _on_close(self):
        """
        Maneja el cierre de la ventana del juego, ya sea por el botón
        'Salir', por la X de la ventana o por la tecla ESC.

        Cancela el loop del juego antes de destruir la ventana para evitar
        errores de callbacks que intentan acceder a widgets ya destruidos.

        Al destruir la ventana, el mainloop() del launcher termina y
        el flujo vuelve al main() que lee self.score para mandar al ESP32.
        """
        if hasattr(self, '_after_id'):
            self.after_cancel(self._after_id)
        self.destroy()


#  Punto de entrada para pruebas 

if __name__ == '__main__':
    # Al correr este archivo directamente (sin el launcher), el juego
    # arranca con el jugador de invitado y puntaje previo en 0.
    # Útil para probar cambios en el juego sin tener el hardware conectado.
    app = SnakeApp()
    app.mainloop()
