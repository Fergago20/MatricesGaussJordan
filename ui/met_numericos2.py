# ui/Met_numericos.py

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import sympy as sp
import re
from sympy import symbols, pi, E
from core.newton import calcular_newton_raphson as metodo_newton
from core.secante import calcular_secante as metodo_secante
from core.grafica import inicio_grafica as graficar_funcion
from ui.estilos import (
    GAUSS_FONDO as MN_FONDO,
    GAUSS_TEXTO as MN_TEXTO,
    GAUSS_CAJA_BG as MN_CAJA_BG,
    GAUSS_CAJA_FG as MN_CAJA_FG,
    GAUSS_BTN_BG as MN_BTN_BG,
    GAUSS_BTN_FG as MN_BTN_FG,
    GAUSS_BTN_BG_ACT as MN_BTN_BG_ACT,
    FUENTE_BOLD,
    FUENTE_SUBTITULO
)
from soporte.base_app import BaseApp
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy.printing.latex import LatexPrinter
from ui.ayuda_entrada import VentanaAyudaEntrada
class CustomLatexPrinter(LatexPrinter):

    def _print_log(self, expr):
        """
        log(x)        -> ln(x)        (logaritmo natural)
        log(x, base)  -> log_base(x)  (cuando Sympy sí conserva la base)
        """
        args = expr.args

        # log(x) (un solo argumento) -> ln(x)
        if len(args) == 1:
            arg_tex = self._print(args[0])
            return r"\ln\left(%s\right)" % arg_tex

        # log(x, base) -> log_base(x)
        x_tex = self._print(args[0])
        base_tex = self._print(args[1])
        return r"\log_{%s}\left(%s\right)" % (base_tex, x_tex)

    def _print_log10(self, expr):
        """
        log10(x) -> log(x)   (logaritmo base 10)
        """
        arg_tex = self._print(expr.args[0])
        return r"\log\left(%s\right)" % arg_tex

    def _print_Mul(self, expr):
        """
        Detecta patrones del tipo log(x)/log(b) y los imprime como log_b(x).

        Sympy convierte log(x, b) automáticamente a log(x)/log(b),
        así que aquí reconstruimos esa notación para el LaTeX.
        """
        num, den = expr.as_numer_denom()

        # ¿Es de la forma log(x)/log(b)?
        if (
            isinstance(num, sp.log) and
            isinstance(den, sp.log) and
            len(num.args) == 1 and
            len(den.args) == 1
        ):
            x_arg = num.args[0]
            base_arg = den.args[0]
            x_tex = self._print(x_arg)
            base_tex = self._print(base_arg)
            return r"\log_{%s}\left(%s\right)" % (base_tex, x_tex)

        # En cualquier otro caso, usamos el comportamiento normal
        return super()._print_Mul(expr)
    
def custom_latex(expr) -> str:
    """Usa el printer personalizado para generar LaTeX."""
    return CustomLatexPrinter().doprint(expr)

def convert_log_bases(s: str) -> str:
    """
    Convierte la notación del USUARIO a la notación que Sympy entiende:
    - ln(x)        -> se deja igual (Sympy lo toma como log(x) natural)
    - log(x)       -> log10(x)     (logaritmo base 10)
    - log(x, b)    -> log(x, b)    (logaritmo base b, cualquier b)
    """
    out = []
    i = 0
    L = len(s)

    while i < L:
        # Buscamos 'log('
        if s.startswith('log(', i):
            # Encontrar el paréntesis que cierra este log(...)
            j = i + 4  # después de 'log('
            depth = 1
            while j < L and depth > 0:
                c = s[j]
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                j += 1

            # contenido dentro de log( ... )
            inner = s[i+4:j-1]

            # ¿hay coma de nivel superior? -> log(x, base)
            # Ejemplos: log(x,2), log(2*x, 10)
            if ',' in inner:
                # lo dejamos como log(x,base)
                out.append('log(' + inner + ')')
            else:
                # log(x) sin base explícita -> log10(x)
                out.append('log10(' + inner + ')')

            i = j
            continue

        # Cualquier otro carácter pasa tal cual
        out.append(s[i])
        i += 1

    return ''.join(out)

x = symbols('x')

# ============================================================
#   CALCULADORA CIENTÍFICA (teclado)
# ============================================================

class CalculadoraCientificaFrame(ctk.CTkFrame):
    def __init__(self, parent, parent_textbox):
        super().__init__(parent, fg_color="#6889AA")
        self.parent_textbox = parent_textbox
        self.expresion = ""
        self.modo_superindice = False

        self.frame_superior = ctk.CTkFrame(self, fg_color="#6889AA")
        self.frame_superior.pack(expand=True, padx=10, pady=5, fill='x')

        self.frame_inferior = ctk.CTkFrame(self, fg_color="#6889AA")
        self.frame_inferior.pack(fill="x", expand=True, padx=10, pady=5)

        self.frame_derecho = ctk.CTkFrame(self.frame_inferior, fg_color="#6889AA")
        self.frame_derecho.pack(side="right", fill="y", expand=True, padx=5, pady=5)

        self.frame_izquierdo = ctk.CTkFrame(self.frame_inferior, fg_color="#6889AA")
        self.frame_izquierdo.pack(side="left", fill="y", expand=True, padx=5, pady=5)

        # Grid del teclado
        for r in range(5):
            self.frame_derecho.grid_rowconfigure(r, weight=1)
        for c in range(4):
            self.frame_derecho.grid_columnconfigure(c, weight=1)

        self.categorias = {
            "Trigonometría": ['sen', 'cos', 'tan', 'sec'],
            "Funciones": ['ln', 'log', '√'],
            "Exponenciales": ['^2', '^3', 'x^x', '(', ')', 'pi', 'e']
        }

        self.categoria_var = ctk.StringVar(value="Exponenciales")
        self.menu_desplegable = ctk.CTkOptionMenu(
            self.frame_superior,
            variable=self.categoria_var,
            values=list(self.categorias.keys()),
            command=self.mostrar_botones_categoria,
            width=200,
            font=("Segoe UI", 14),
            fg_color=MN_BTN_BG,
            button_color=MN_BTN_BG,
            text_color=MN_BTN_FG,
            button_hover_color=MN_BTN_BG_ACT
        )
        self.menu_desplegable.pack(fill="x", padx=2, pady=2, side="left")

        self.categoria_botones_frame = ctk.CTkFrame(self.frame_izquierdo, fg_color="#6889AA")
        self.categoria_botones_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.mostrar_botones_categoria(self.categoria_var.get())
        self.crear_botones_numericos()
        self.crear_botones_aritmeticos()
        self.crear_boton_limpiar()

    # ------------------------------------------------------------
    def mostrar_botones_categoria(self, nombre_categoria):
        for w in self.categoria_botones_frame.winfo_children():
            w.destroy()

        try:
            self.categoria_botones_frame.grid_columnconfigure((0, 1, 2), weight=1)
        except Exception:
            for i in (0, 1, 2):
                self.categoria_botones_frame.grid_columnconfigure(i, weight=1)

        for idx, texto in enumerate(self.categorias[nombre_categoria]):
            ctk.CTkButton(
                self.categoria_botones_frame,
                text=texto,
                fg_color=MN_BTN_BG,
                text_color=MN_BTN_FG,
                hover_color=MN_BTN_BG_ACT,
                command=lambda t=texto: self.al_presionar_boton(t)
            ).grid(row=idx // 3, column=idx % 3, padx=3, pady=3, sticky="nsew")

    def crear_botones_numericos(self):
        for i in range(1, 10):
            ctk.CTkButton(
                self.frame_derecho, text=str(i),
                fg_color=MN_BTN_BG, text_color=MN_BTN_FG,
                hover_color=MN_BTN_BG_ACT,
                command=lambda t=str(i): self.al_presionar_boton(t)
            ).grid(row=(i - 1) // 3, column=(i - 1) % 3, padx=2, pady=2, sticky="nsew")
        ctk.CTkButton(
            self.frame_derecho, text="0",
            command=lambda: self.al_presionar_boton("0"),
            fg_color=MN_BTN_BG, text_color=MN_BTN_FG,
            hover_color=MN_BTN_BG_ACT
        ).grid(row=3, column=0, padx=2, pady=2, sticky="nsew")

    def crear_botones_aritmeticos(self):
        for i, op in enumerate(['+', '-', '*', '/']):
            ctk.CTkButton(
                self.frame_derecho, text=op,
                fg_color=MN_BTN_BG, text_color=MN_BTN_FG,
                hover_color=MN_BTN_BG_ACT,
                command=lambda t=op: self.al_presionar_boton(t)
            ).grid(row=i, column=3, padx=2, pady=2, sticky="nsew")

    def crear_boton_limpiar(self):
        ctk.CTkButton(
            self.frame_derecho, text="C",
            command=lambda: self.parent_textbox.delete(0, 'end'),
            fg_color="#D9534F", text_color="white"
        ).grid(row=4, column=1, padx=2, pady=2, sticky="nsew")

    def al_presionar_boton(self, texto):
        self.parent_textbox.insert("insert", texto)

    def obtener_funcion(self):
        f = self.parent_textbox.get().strip().lower()

        # Reemplazos básicos
        f = (f.replace('²', '**2')
               .replace('³', '**3')
               .replace('sen', 'sin')
               .replace('^', '**')
               .replace('÷', '/'))

        # √[n](expr) -> sqrt(expr, n)
        f = re.sub(r'√\s*\[\s*(\d+)\s*\]\s*\(\s*([^)]+?)\s*\)', r'sqrt(\2, \1)', f)
        # √(expr) -> sqrt(expr)
        f = re.sub(r'√\s*\(\s*([^)]+?)\s*\)', r'sqrt(\1)', f)

        # Potencias fraccionarias **1/n → **(1/n)
        f = re.sub(r'\*\*\s*1\s*/\s*(\d+)', r'**(1/\1)', f)

        def _repl_pow_paren(m):
            base = m.group(1); n = m.group(2)
            return f"sqrt({base})" if n == '2' else f"root({base}, {n})"

        f = re.sub(
            r'\(\s*([^\(\)]+?)\s*\)\s*\*\*\s*\(\s*1\s*/\s*(\d+)\s*\)',
            _repl_pow_paren, f
        )

        def _repl_pow_simple(m):
            base = m.group(1); n = m.group(2)
            return f"sqrt({base})" if n == '2' else f"root({base}, {n})"

        f = re.sub(
            r'([A-Za-z_]\w*(?:\([^\)]*\))?|\d+(?:\.\d+)?)\s*\*\*\s*\(\s*1\s*/\s*(\d+)\)',
            _repl_pow_simple, f
        )

        # Convertir sqrt(expr, n) → root(expr, n)
        def _convert_sqrt_with_index(s: str) -> str:
            out = []
            i = 0
            L = len(s)
            while i < L:
                if s.startswith('sqrt(', i):
                    j = i + 5
                    depth = 1
                    comma_pos = None
                    while j < L and depth > 0:
                        c = s[j]
                        if c == '(':
                            depth += 1
                        elif c == ')':
                            depth -= 1
                        elif c == ',' and depth == 1 and comma_pos is None:
                            comma_pos = j
                        j += 1
                    if depth == 0:
                        inner = s[i+5:j-1]
                        if comma_pos is not None:
                            expr = s[i+5:comma_pos].strip()
                            n = s[comma_pos+1:j-1].strip()
                            if n == '2':
                                out.append(f"sqrt({expr})")
                            else:
                                out.append(f"root({expr}, {n})")
                        else:
                            out.append(f"sqrt({inner})")
                        i = j
                        continue
                out.append(s[i])
                i += 1
            return ''.join(out)

        f = _convert_sqrt_with_index(f)
        f = convert_log_bases(f)

        # Coma decimal entre dígitos -> punto
        f = re.sub(r'(?<=\d),(?=\d)', '.', f)

        # Multiplicación implícita básica
        f = re.sub(r'(\d)\s*([A-Za-z\(])', r'\1*\2', f)
        f = re.sub(r'(\))\s*([A-Za-z\(])', r'\1*\2', f)
        f = re.sub(r'([A-Za-z_]\w*)\s*(?=sqrt\()', r'\1*', f)
        f = re.sub(r'([A-Za-z_]\w*)\s*(?=root\()', r'\1*', f)

        return f


# ============================================================
#   INTERFAZ PRINCIPAL: Newton-Raphson y Secante
# ============================================================

class AppMetodosNumericos(BaseApp):
    """Interfaz visual para Newton-Raphson y Secante con puntos iniciales."""
    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(toplevel_parent, on_volver, titulo="Métodos Numéricos: Newton y Secante")
        self.configure(bg=MN_FONDO)

        self.entry_ecuacion = tk.StringVar()
        self.entry_tolerancia = tk.DoubleVar(value=0.0001)
        self.entry_x0 = tk.StringVar()          # x0
        self.entry_x1 = tk.StringVar()          # x1 (secante)
        self.mostrar_notacion_cientifica = tk.BooleanVar(value=True)

        self._ultimo_error = None               # siempre Ea de la última fila
        self.metodo_var = tk.StringVar(value="newton")

        self._construir_ui()

    def _formatear_error(self) -> str:
        """Devuelve el error (Ea último) formateado según el Checkbutton."""
        if self._ultimo_error is None:
            return "N/A"

        valor = self._ultimo_error

        if self.mostrar_notacion_cientifica.get():
            # Notación científica automática
            return f"{valor:.6e}"
        else:
            # Notación decimal fija (sin científica)
            # 10 decimales siempre — ajusta si quieres otro número
            return f"{valor:.10f}"


    def _actualizar_margen_formato(self):
        """
        Solo cambia el FORMATO del margen de error,
        pero el valor SIEMPRE viene de self._ultimo_error (Ea último).
        """
        texto = self.label_resultado.cget("text")
        if "Margen de error:" not in texto or self._ultimo_error is None:
            return

        nuevo_error = f"Margen de error: {self._formatear_error()}"
        nuevo_texto = re.sub(r"Margen de error:.*", nuevo_error, texto)
        self.label_resultado.config(text=nuevo_texto)

    # ------------------------------------------------------------
    def _construir_ui(self):
        estilo_btn = {
            "bg": MN_BTN_BG, "fg": MN_BTN_FG,
            "activebackground": MN_BTN_BG_ACT, "activeforeground": MN_BTN_FG,
            "relief": "raised", "bd": 2, "cursor": "hand2",
            "font": FUENTE_BOLD, "padx": 8, "pady": 4
        }

        raiz = tk.Frame(self, bg=MN_FONDO)
        raiz.pack(fill="both", expand=True, padx=10, pady=10)

        # GRID maestro
        raiz.grid_rowconfigure(0, weight=0)
        raiz.grid_rowconfigure(1, weight=1)
        raiz.grid_rowconfigure(2, weight=0)
        raiz.grid_columnconfigure(0, weight=1)

        # FILA 0: Controles + Teclado
        fila0 = tk.Frame(raiz, bg=MN_FONDO)
        fila0.grid(row=0, column=0, sticky="nsew")
        fila0.grid_columnconfigure(0, weight=1)
        fila0.grid_columnconfigure(1, weight=0)

        # Columna izquierda
        col_izq = tk.Frame(fila0, bg=MN_FONDO)
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=2)
        col_izq.grid_columnconfigure(0, weight=1)

        # Ecuación
        panel_ecuacion = tk.Frame(col_izq, bg=MN_FONDO)
        panel_ecuacion.grid(row=0, column=0, sticky="ew", pady=(2, 4))
        panel_ecuacion.grid_columnconfigure(1, weight=1)

        tk.Label(
            panel_ecuacion, text="Ecuación:",
            font=FUENTE_SUBTITULO,
            bg=MN_FONDO, fg=MN_TEXTO
        ).grid(row=0, column=0, padx=5, sticky="w")

        self.entry_ecuacion_widget = tk.Entry(
            panel_ecuacion, textvariable=self.entry_ecuacion,
            font=("Segoe UI", 14), width=1,
            bg="white", fg="black", insertbackground="black"
        )
        self.entry_ecuacion_widget.grid(row=0, column=1, sticky="ew", padx=5)

        # Preview tipografiado compacto
        panel_preview = tk.Frame(col_izq, bg=MN_FONDO)
        panel_preview.grid(row=1, column=0, sticky="ew", pady=(2, 6))

        self.lbl_ok = tk.Label(
            panel_preview, text="", bg=MN_FONDO,
            fg="white", font=("Segoe UI", 12, "bold")
        )
        self.lbl_ok.pack(anchor="w", padx=5, pady=(0, 2))

        self._fig = Figure(figsize=(3.0, 0.5), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._ax.axis("off")
        self._canvas_preview = FigureCanvasTkAgg(self._fig, master=panel_preview)
        cv = self._canvas_preview.get_tk_widget()
        cv.pack(anchor="w", padx=5, fill="x")
        try:
            cv.configure(height=60)
        except Exception:
            pass

        # Puntos iniciales x0, x1 + Tolerancia
        frame_intervalos = tk.Frame(col_izq, bg=MN_FONDO)
        frame_intervalos.grid(row=2, column=0, sticky="ew", pady=(0, 4))

        for i in range(6):
            frame_intervalos.grid_columnconfigure(i, weight=1 if i % 2 else 0)

        # x0
        tk.Label(
            frame_intervalos, text="x0:",
            bg=MN_FONDO, fg=MN_TEXTO
        ).grid(row=0, column=0, padx=5, sticky="e")
        tk.Entry(
            frame_intervalos, textvariable=self.entry_x0,
            font=("Segoe UI", 12), width=10,
            bg=MN_CAJA_BG, fg=MN_CAJA_FG,
            justify="center"
        ).grid(row=0, column=1, padx=(0, 8), sticky="ew")

        # x1 (para secante)
        tk.Label(
            frame_intervalos, text="x1 (secante):",
            bg=MN_FONDO, fg=MN_TEXTO
        ).grid(row=0, column=2, padx=5, sticky="e")
        tk.Entry(
            frame_intervalos, textvariable=self.entry_x1,
            font=("Segoe UI", 12), width=10,
            bg=MN_CAJA_BG, fg=MN_CAJA_FG,
            justify="center"
        ).grid(row=0, column=3, padx=(0, 8), sticky="ew")

        # Tolerancia
        tk.Label(
            frame_intervalos, text="Tol.:",
            bg=MN_FONDO, fg=MN_TEXTO
        ).grid(row=0, column=4, padx=5, sticky="e")
        tk.Entry(
            frame_intervalos, textvariable=self.entry_tolerancia,
            font=("Segoe UI", 12), width=10,
            bg=MN_CAJA_BG, fg=MN_CAJA_FG,
            justify="center"
        ).grid(row=0, column=5, padx=(0, 8), sticky="ew")

        # Método (Newton / Secante)
        frame_metodo = tk.Frame(col_izq, bg=MN_FONDO)
        frame_metodo.grid(row=3, column=0, sticky="ew", pady=(0, 4))
        tk.Label(
            frame_metodo, text="Método:",
            bg=MN_FONDO, fg=MN_TEXTO
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            frame_metodo, text="Newton-Raphson",
            variable=self.metodo_var, value="newton",
            bg=MN_FONDO, fg=MN_TEXTO,
            selectcolor=MN_FONDO, activebackground=MN_FONDO,
            command=self._on_cambio_metodo
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            frame_metodo, text="Secante",
            variable=self.metodo_var, value="secante",
            bg=MN_FONDO, fg=MN_TEXTO,
            selectcolor=MN_FONDO, activebackground=MN_FONDO,
            command=self._on_cambio_metodo
        ).pack(side="left", padx=5)

        # Botones acción
        actions_frame = tk.Frame(col_izq, bg=MN_FONDO)
        actions_frame.grid(row=4, column=0, sticky="ew", pady=(2, 6))
        actions_frame.grid_columnconfigure(0, weight=1)

        tk.Checkbutton(
            actions_frame,
            text="Mostrar notación científica",
            variable=self.mostrar_notacion_cientifica,
            bg=MN_FONDO,
            fg=MN_TEXTO,
            selectcolor=MN_FONDO,
            activebackground=MN_FONDO,
            command=self._actualizar_margen_formato
        ).grid(row=0, column=0, sticky="w", padx=6)

        tk.Button(
            actions_frame, text="Graficar Función",
            command=lambda: graficar_funcion(self.teclado_frame.obtener_funcion()),
            **estilo_btn
        ).grid(row=0, column=1, sticky="e", padx=6)

        tk.Button(
            actions_frame, text="Calcular",
            command=self.calcular,
            **estilo_btn
        ).grid(row=0, column=2, sticky="e", padx=6)

        # Resultado
        self.label_resultado = tk.Label(
            col_izq,
            text="Aún no se ha realizado ningún cálculo.",
            font=("Segoe UI", 11, "bold"),
            bg=MN_FONDO, fg=MN_TEXTO, anchor="w", justify="left",
            wraplength=700
        )
        self.label_resultado.grid(row=5, column=0, sticky="ew", padx=4, pady=(0, 4))

        # Columna derecha (teclado científico)
        col_der = tk.Frame(fila0, bg=MN_FONDO)
        col_der.grid(row=0, column=1, sticky="ns")
        self.teclado_frame = CalculadoraCientificaFrame(col_der, self.entry_ecuacion_widget)
        self.teclado_frame.pack(fill="y", expand=False, padx=0, pady=0)

        # FILA 1: Tabla
        panel_tabla = tk.Frame(raiz, bg=MN_FONDO)
        panel_tabla.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        panel_tabla.grid_rowconfigure(1, weight=1)
        panel_tabla.grid_columnconfigure(0, weight=1)

        tk.Label(
            panel_tabla, text="Iteraciones:",
            font=FUENTE_SUBTITULO,
            bg=MN_FONDO, fg=MN_TEXTO
        ).grid(row=0, column=0, sticky="w", pady=(0, 4), padx=2)

        cont_tabla = tk.Frame(panel_tabla, bg=MN_FONDO)
        cont_tabla.grid(row=1, column=0, sticky="nsew")
        cont_tabla.grid_rowconfigure(0, weight=1)
        cont_tabla.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            cont_tabla,
            show="headings", height=12
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(cont_tabla, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(cont_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configuración inicial (Newton: exactamente como antes)
        self._configurar_tabla("newton")

        # Eventos preview ecuación
        self.entry_ecuacion_widget.bind("<KeyRelease>", self._on_ecuacion_change)
        self._on_ecuacion_change(None)

        # ==== FILA 2: Barra inferior ====
        barra_inf = tk.Frame(raiz, bg=MN_FONDO)
        barra_inf.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        tk.Button(barra_inf, text="← Volver al menú", command=self._volver_al_menu, **estilo_btn)\
            .pack(side="left", padx=5)
        
        tk.Button(barra_inf, text="Ayuda", command=lambda: VentanaAyudaEntrada(self.winfo_toplevel()), **estilo_btn)\
        .pack(side="right", padx=5)

    # ------------------------------------------------------------
    def _configurar_tabla(self, metodo: str):
        """Configura las columnas de la tabla según el método."""
        if metodo == "newton":
            # EXACTAMENTE como lo tenías:
            columnas = ("Iteración", "xi", "xi+1", "Ea", "f(xi)", "f'(xi)")
        else:  # secante
            # Solo aquí usamos xi-1, xi, xi+1
            columnas = ("Iteración", "xi-1", "xi", "xi+1", "Ea", "f(xi-1)", "f(xi)")
        self.tree["columns"] = columnas
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

    def _on_cambio_metodo(self):
        """Se llama al cambiar el RadioButton de método."""
        metodo = self.metodo_var.get()
        # Limpiar tabla y texto
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._ultimo_error = None
        self.label_resultado.config(text="Aún no se ha realizado ningún cálculo.")
        self._configurar_tabla(metodo)

    # ------------------------------------------------------------
    def calcular(self):
        """Ejecuta el método seleccionado y muestra resultados."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        ecuacion = self.teclado_frame.obtener_funcion().strip().replace("=0", "").strip()
        tol_str = str(self.entry_tolerancia.get()).strip()
        x0_str = self.entry_x0.get().strip()
        x1_str = self.entry_x1.get().strip()
        metodo = self.metodo_var.get()

        if not ecuacion:
            messagebox.showwarning("Ecuación vacía", "Por favor, ingresa una ecuación antes de calcular.")
            return
        if not tol_str or not x0_str:
            messagebox.showwarning(
                "Campos incompletos",
                "Debes llenar al menos x0 y tolerancia."
            )
            return

        # Validar x0
        try:
            x0 = float(x0_str)
        except ValueError:
            messagebox.showerror("Error de formato", "El valor de x0 debe ser numérico.")
            return

        # Validar x1 si se usa secante
        if metodo == "secante":
            if not x1_str:
                messagebox.showwarning(
                    "Campos incompletos",
                    "Para el método de la secante debes llenar x0 y x1."
                )
                return
            try:
                x1 = float(x1_str)
            except ValueError:
                messagebox.showerror("Error de formato", "El valor de x1 debe ser numérico.")
                return
            if x0 == x1:
                messagebox.showerror(
                    "Valores inválidos",
                    "En el método de la secante se requieren x0 y x1 diferentes."
                )
                return

        # Validar tolerancia
        try:
            tol = float(eval(tol_str, {"__builtins__": None}, {"e": 2.71828, "E": 2.71828, "pow": pow}))
        except Exception:
            messagebox.showerror(
                "Error en tolerancia",
                "La tolerancia no es válida.\nEjemplo: 0.001, 1e-4, 10**-4."
            )
            return

        # Comprobar ecuación parseable
        try:
            sp.sympify(ecuacion)
        except Exception:
            messagebox.showerror(
                "Ecuación no válida",
                "La ecuación ingresada no es válida.\nRevisa paréntesis, operadores o variables."
            )
            return

        try:
            if metodo == "newton":
                # Newton recibe ecuación, x0, tol
                resultado, iteraciones, filas = metodo_newton(ecuacion, x0, tol)
                titulo = "Método de Newton-Raphson"

                # filas: [iter, xi, xi1, Ea, f(xi), f'(xi)]
                for fila in filas:
                    iter_, xi, xi1, Ea, fxi, fpxi = fila
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            f"{int(iter_)}",
                            f"{xi:.8f}",    # xi
                            f"{xi1:.8f}",   # xi+1
                            f"{Ea:.8f}",
                            f"{fxi:.8f}",
                            f"{fpxi:.8f}",
                        )
                    )

            else:  # secante
                # Secante recibe ecuación, x0, x1, tol
                resultado, iteraciones, filas = metodo_secante(ecuacion, x0, x1, tol)
                titulo = "Método de la Secante"

                # filas: [iter, xi_1, xi, xi1, Ea, fxi_1, fxi]
                for fila in filas:
                    iter_, xi_1, xi, xi1, Ea, fxi_1, fxi = fila
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            f"{int(iter_)}",
                            f"{xi_1:.8f}",  # x0
                            f"{xi:.8f}",    # x1
                            f"{xi1:.8f}",   # x2
                            f"{Ea:.8f}",
                            f"{fxi_1:.8f}", # f(x0)
                            f"{fxi:.8f}",   # f(x1)
                        )
                    )

            # Margen de error = Ea de la ÚLTIMA fila
            try:
                self._ultimo_error = abs(filas[-1][4])
            except Exception:
                self._ultimo_error = 0.0

            error_fmt = self._formatear_error()

            self.label_resultado.config(
                text=(
                    f"{titulo} converge en {iteraciones} iteraciones.\n"
                    f"Raíz aproximada: {resultado:.10f}\n"
                    f"Margen de error: {error_fmt}"
                )
            )

        except Exception as e:
            messagebox.showerror(
                "Error durante el cálculo",
                f"Ocurrió un problema al ejecutar el método ({metodo.replace('_', ' ')}):\n\n{e}"
            )
            self.label_resultado.config(text="Error: no se pudo completar el cálculo.")
            self._ultimo_error = None

    

    # ------------------------------------------------------------
        # ------------------------------------------------------------
    def _on_ecuacion_change(self, event):
        texto_usuario = self.entry_ecuacion_widget.get().strip()

        if not texto_usuario:
            self.lbl_ok.config(text="", bg=MN_FONDO)
            self._render_preview(None)
            return

        try:
            ecuacion_parseable = self.teclado_frame.obtener_funcion()
        except Exception:
            self.lbl_ok.config(text="⚠ Ecuación no válida", bg="#C27C0E")
            self._render_preview(None)
            return

        try:
            expr = sp.sympify(ecuacion_parseable)
            tex = custom_latex(expr)
            self.lbl_ok.config(text="✓ Ecuación válida", bg="#198754")
            self._render_preview(tex)
        except Exception:
            self.lbl_ok.config(text="⚠ Ecuación no válida", bg="#C27C0E")
            self._render_preview(None)

    def _render_preview(self, tex_or_none: str | None):
        """
        Dibuja el LaTeX en el Figure embebido.
        Si tex_or_none es None, limpia el lienzo.
        """
        self._ax.clear()
        self._ax.axis("off")

        if tex_or_none:
            self._ax.text(
                0.01, 0.5, f"${tex_or_none}$",
                va="center", ha="left", fontsize=16
            )
            self._fig.subplots_adjust(
                left=0.02, right=0.98, top=0.95, bottom=0.05
            )

        self._canvas_preview.draw_idle()
