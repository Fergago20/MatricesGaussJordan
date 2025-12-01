import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import sympy as sp
import re
from sympy import symbols, pi, E
from core.biserccion import calcular_biseccion as metodo_biseccion
from core.falsa_posicion import calcular_falsa_posicion as metodo_falsa_posicion
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

# ============================================================
#   PRINTER PERSONALIZADO PARA MOSTRAR ln(x)
# ============================================================

class CustomLatexPrinter(LatexPrinter):
    def _print_log(self, expr):
        """
        Sobrescribe la impresión de log:
        - log(x)        -> \ln(x)
        - log(x, base)  -> \log_{base}(x)
        """
        args = expr.args

        # log(x)  (logaritmo natural) -> ln(x)
        if len(args) == 1:
            arg_tex = self._print(args[0])
            return r"\ln\left(%s\right)" % arg_tex

        # log(x, base) -> log_base(x)
        x_tex = self._print(args[0])
        base_tex = self._print(args[1])
        return r"\log_{%s}\left(%s\right)" % (base_tex, x_tex)


def custom_latex(expr) -> str:
    """Usa el printer personalizado para generar LaTeX."""
    return CustomLatexPrinter().doprint(expr)

# ============================================================
#   CALCULADORA CIENTÍFICA (teclado)
# ============================================================

x = symbols('x')

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

        # Densidad del grid del lado derecho (teclado)
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

        # estirar columnas 0..2
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
        ctk.CTkButton(self.frame_derecho, text="0",
                      command=lambda: self.al_presionar_boton("0"),
                      fg_color=MN_BTN_BG, text_color=MN_BTN_FG,
                      hover_color=MN_BTN_BG_ACT)\
            .grid(row=3, column=0, padx=2, pady=2, sticky="nsew")

    def crear_botones_aritmeticos(self):
        for i, op in enumerate(['+', '-', '*', '/']):
            ctk.CTkButton(
                self.frame_derecho, text=op,
                fg_color=MN_BTN_BG, text_color=MN_BTN_FG,
                hover_color=MN_BTN_BG_ACT,
                command=lambda t=op: self.al_presionar_boton(t)
            ).grid(row=i, column=3, padx=2, pady=2, sticky="nsew")

    def crear_boton_limpiar(self):
        ctk.CTkButton(self.frame_derecho, text="C",
                      command=lambda: self.parent_textbox.delete(0, 'end'),
                      fg_color="#D9534F", text_color="white").grid(row=4, column=1, padx=2, pady=2, sticky="nsew")

    def al_presionar_boton(self, texto):
        self.parent_textbox.insert("insert", texto)

    def obtener_funcion(self):
        f = self.parent_textbox.get().strip()

        # ---------------------------
        # Reemplazos básicos
        # ---------------------------
        f = (f.replace('²', '**2')
             .replace('³', '**3')
             .replace('sen', 'sin')
             .replace('^', '**')
             .replace('÷', '/')
             .replace('ln', 'log')  # <-- ln(x) se convierte a log(x) para SymPy
             )

        # ---------------------------
        # 0) √ con/sin índice → sqrt(...) provisional
        # ---------------------------
        # √[n](expr) -> sqrt(expr, n) (luego lo convertimos a root)
        f = re.sub(r'√\s*\[\s*(\d+)\s*\]\s*\(\s*([^)]+?)\s*\)', r'sqrt(\2, \1)', f)
        # √(expr) -> sqrt(expr)
        f = re.sub(r'√\s*\(\s*([^)]+?)\s*\)', r'sqrt(\1)', f)

        # ---------------------------
        # 2) Potencias fraccionarias **1/n → **(1/n) y luego sqrt/root
        # ---------------------------
        # Arregla precedencia: x**1/3 -> x**(1/3)
        f = re.sub(r'\*\*\s*1\s*/\s*(\d+)', r'**(1/\1)', f)

        def _repl_pow_paren(m):
            base = m.group(1); n = m.group(2)
            return f"sqrt({base})" if n == '2' else f"root({base}, {n})"

        # (base)**(1/n)
        f = re.sub(r'\(\s*([^\(\)]+?)\s*\)\s*\*\*\s*\(\s*1\s*/\s*(\d+)\s*\)', _repl_pow_paren, f)

        def _repl_pow_simple(m):
            base = m.group(1); n = m.group(2)
            return f"sqrt({base})" if n == '2' else f"root({base}, {n})"

        # base_simple**(1/n)
        f = re.sub(r'([A-Za-z_]\w*(?:\([^\)]*\))?|\d+(?:\.\d+)?)\s*\*\*\s*\(\s*1\s*/\s*(\d+)\s*\)',
                   _repl_pow_simple, f)

        # ---------------------------
        # 3) Parser: convertir sqrt(expr, n) (con paréntesis anidados) → root(expr, n)
        # ---------------------------
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

        # ---------------------------
        # 4) Coma decimal entre dígitos -> punto
        # ---------------------------
        f = re.sub(r'(?<=\d),(?=\d)', '.', f)

        # ---------------------------
        # 5) Multiplicación implícita básica
        # ---------------------------
        f = re.sub(r'(\d)\s*([A-Za-z\(])', r'\1*\2', f)
        f = re.sub(r'(\))\s*([A-Za-z\(])', r'\1*\2', f)

        # variable seguida de sqrt/root sin operador
        f = re.sub(r'([A-Za-z_]\w*)\s*(?=sqrt\()', r'\1*', f)
        f = re.sub(r'([A-Za-z_]\w*)\s*(?=root\()', r'\1*', f)

        return f


# ============================================================
#   INTERFAZ PRINCIPAL: Métodos Numéricos
# ============================================================

class AppMetodosNumericos(BaseApp):
    """Interfaz visual para Bisección / Falsa Posición con layout compacto."""
    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(toplevel_parent, on_volver, titulo="Método de Bisección")
        self.configure(bg=MN_FONDO)

        self.entry_ecuacion = tk.StringVar()
        self.entry_tolerancia = tk.DoubleVar(value=0.0001)
        self.entry_intervalo_inferior = tk.StringVar()
        self.entry_intervalo_superior = tk.StringVar()
        self.mostrar_notacion_cientifica = tk.BooleanVar(value=True) #

        self._construir_ui()
        
    def _actualizar_margen_formato(self):
        """Actualiza el texto del margen de error según el formato seleccionado."""
        texto = self.label_resultado.cget("text")

        # Si no hay margen de error mostrado aún, no hacemos nada
        if "Margen de error:" not in texto:
            return

        try:
            # Extraer el número actual del texto
            valor = float(re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", texto.split("Margen de error:")[-1])[0])
        except Exception:
            return

        # Formatear según la selección del usuario
        if self.mostrar_notacion_cientifica.get():
            nuevo_formato = f"Margen de error: {valor:.6g}"
        else:
            nuevo_formato = f"Margen de error: {valor:.10f}"

        # Reemplazar el texto actual
        nuevo_texto = re.sub(r"Margen de error:.*", nuevo_formato, texto)
        self.label_resultado.config(text=nuevo_texto)

    def _construir_ui(self):
        estilo_btn = {
            "bg": MN_BTN_BG, "fg": MN_BTN_FG,
            "activebackground": MN_BTN_BG_ACT, "activeforeground": MN_BTN_FG,
            "relief": "raised", "bd": 2, "cursor": "hand2",
            "font": FUENTE_BOLD, "padx": 8, "pady": 4
        }

        raiz = tk.Frame(self, bg=MN_FONDO)
        raiz.pack(fill="both", expand=True, padx=10, pady=10)

        # ====== GRID maestro: 3 filas (0 controles, 1 tabla, 2 barra) ======
        raiz.grid_rowconfigure(0, weight=0)
        raiz.grid_rowconfigure(1, weight=1)
        raiz.grid_rowconfigure(2, weight=0)
        raiz.grid_columnconfigure(0, weight=1)

        # ========== FILA 0: Controles (izq) + Teclado (der) ==========
        fila0 = tk.Frame(raiz, bg=MN_FONDO)
        fila0.grid(row=0, column=0, sticky="nsew")
        fila0.grid_columnconfigure(0, weight=1)  # izquierda crece
        fila0.grid_columnconfigure(1, weight=0)  # derecha ancho fijo

        # ---------- Columna izquierda ----------
        col_izq = tk.Frame(fila0, bg=MN_FONDO)
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=2)
        col_izq.grid_columnconfigure(0, weight=1)

        # Ecuación
        panel_ecuacion = tk.Frame(col_izq, bg=MN_FONDO)
        panel_ecuacion.grid(row=0, column=0, sticky="ew", pady=(2, 4))
        panel_ecuacion.grid_columnconfigure(1, weight=1)

        tk.Label(panel_ecuacion, text="Ecuación:", font=FUENTE_SUBTITULO,
                 bg=MN_FONDO, fg=MN_TEXTO).grid(row=0, column=0, padx=5, sticky="w")

        self.entry_ecuacion_widget = tk.Entry(
            panel_ecuacion, textvariable=self.entry_ecuacion,
            font=("Segoe UI", 14), width=1,
            bg="white", fg="black", insertbackground="black"
        )
        self.entry_ecuacion_widget.grid(row=0, column=1, sticky="ew", padx=5)

        # Preview tipografiado compacto
        panel_preview = tk.Frame(col_izq, bg=MN_FONDO)
        panel_preview.grid(row=1, column=0, sticky="ew", pady=(2, 6))

        self.lbl_ok = tk.Label(panel_preview, text="", bg=MN_FONDO,
                               fg="white", font=("Segoe UI", 12, "bold"))
        self.lbl_ok.pack(anchor="w", padx=5, pady=(0, 2))

        self._fig = Figure(figsize=(3.0, 0.5), dpi=100)  # compacto
        self._ax = self._fig.add_subplot(111)
        self._ax.axis("off")
        self._canvas_preview = FigureCanvasTkAgg(self._fig, master=panel_preview)
        cv = self._canvas_preview.get_tk_widget()
        cv.pack(anchor="w", padx=5, fill="x")
        try:
            cv.configure(height=60)
        except Exception:
            pass

        # Intervalos + Tolerancia
        frame_intervalos = tk.Frame(col_izq, bg=MN_FONDO)
        frame_intervalos.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        for i in range(6):
            frame_intervalos.grid_columnconfigure(i, weight=1 if i % 2 else 0)

        tk.Label(frame_intervalos, text="a:", bg=MN_FONDO, fg=MN_TEXTO)\
            .grid(row=0, column=0, padx=5, sticky="e")
        tk.Entry(frame_intervalos, textvariable=self.entry_intervalo_inferior,
                 font=("Segoe UI", 12), width=10, bg=MN_CAJA_BG, fg=MN_CAJA_FG,
                 justify="center").grid(row=0, column=1, padx=(0, 8), sticky="ew")

        tk.Label(frame_intervalos, text="b:", bg=MN_FONDO, fg=MN_TEXTO)\
            .grid(row=0, column=2, padx=5, sticky="e")
        tk.Entry(frame_intervalos, textvariable=self.entry_intervalo_superior,
                 font=("Segoe UI", 12), width=10, bg=MN_CAJA_BG, fg=MN_CAJA_FG,
                 justify="center").grid(row=0, column=3, padx=(0, 8), sticky="ew")

        tk.Label(frame_intervalos, text="Tol.:", bg=MN_FONDO, fg=MN_TEXTO)\
            .grid(row=0, column=4, padx=5, sticky="e")
        tk.Entry(frame_intervalos, textvariable=self.entry_tolerancia,
                 font=("Segoe UI", 12), width=10, bg=MN_CAJA_BG, fg=MN_CAJA_FG,
                 justify="center").grid(row=0, column=5, padx=(0, 8), sticky="ew")

        # Método (radio)
        frame_metodo = tk.Frame(col_izq, bg=MN_FONDO)
        frame_metodo.grid(row=3, column=0, sticky="ew", pady=(0, 4))
        tk.Label(frame_metodo, text="Método:", bg=MN_FONDO, fg=MN_TEXTO)\
            .pack(side="left", padx=5)
        self.metodo_var = tk.StringVar(value="biseccion")
        tk.Radiobutton(frame_metodo, text="Bisección", variable=self.metodo_var, value="biseccion",
                       bg=MN_FONDO, fg=MN_TEXTO, selectcolor=MN_FONDO,
                       activebackground=MN_FONDO).pack(side="left", padx=5)
        tk.Radiobutton(frame_metodo, text="Falsa Posición", variable=self.metodo_var, value="falsa_posicion",
                       bg=MN_FONDO, fg=MN_TEXTO, selectcolor=MN_FONDO,
                       activebackground=MN_FONDO).pack(side="left", padx=5)

        # Botones de acción a la derecha
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
        
        tk.Button(actions_frame, text="Graficar Función",
                  command=lambda: graficar_funcion(self.teclado_frame.obtener_funcion()),
                  **estilo_btn).grid(row=0, column=1, sticky="e", padx=6)
        tk.Button(actions_frame, text="Calcular", command=self.calcular,
                  **estilo_btn).grid(row=0, column=2, sticky="e", padx=6)

        # Resultado compacto (wrap)
        self.label_resultado = tk.Label(
            col_izq,
            text="Aún no se ha realizado ningún cálculo.",
            font=("Segoe UI", 11, "bold"),
            bg=MN_FONDO, fg=MN_TEXTO, anchor="w", justify="left",
            wraplength=700
        )
        self.label_resultado.grid(row=5, column=0, sticky="ew", padx=4, pady=(0, 4))

        # ---------- Columna derecha (teclado científico) ----------
        col_der = tk.Frame(fila0, bg=MN_FONDO)
        col_der.grid(row=0, column=1, sticky="ns")
        self.teclado_frame = CalculadoraCientificaFrame(col_der, self.entry_ecuacion_widget)
        self.teclado_frame.pack(fill="y", expand=False, padx=0, pady=0)

        # ========== FILA 1: Tabla (se expande) ==========
        panel_tabla = tk.Frame(raiz, bg=MN_FONDO)
        panel_tabla.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        panel_tabla.grid_rowconfigure(1, weight=1)
        panel_tabla.grid_columnconfigure(0, weight=1)

        tk.Label(panel_tabla, text="Iteraciones:", font=FUENTE_SUBTITULO,
                 bg=MN_FONDO, fg=MN_TEXTO).grid(row=0, column=0, sticky="w", pady=(0, 4), padx=2)

        cont_tabla = tk.Frame(panel_tabla, bg=MN_FONDO)
        cont_tabla.grid(row=1, column=0, sticky="nsew")
        cont_tabla.grid_rowconfigure(0, weight=1)
        cont_tabla.grid_columnconfigure(0, weight=1)

        columnas = ("Iteración", "a", "b", "c", "f(a)", "f(b)", "f(c)")
        self.tree = ttk.Treeview(cont_tabla, columns=columnas, show="headings", height=12)
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(cont_tabla, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(cont_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # ==== Eventos iniciales preview ====
        self.entry_ecuacion_widget.bind("<KeyRelease>", self._on_ecuacion_change)
        self._on_ecuacion_change(None)

        # ==== FILA 2: Barra inferior ====
        barra_inf = tk.Frame(raiz, bg=MN_FONDO)
        barra_inf.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        tk.Button(barra_inf, text="← Volver al menú", command=self._volver_al_menu, **estilo_btn)\
            .pack(side="left", padx=5)

    # ------------------------------------------------------------
    def calcular(self):
        """Ejecuta el método seleccionado (bisección o falsa posición) y muestra resultados."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        ecuacion = self.teclado_frame.obtener_funcion().strip().replace("=0", "").strip()
        tol_str = str(self.entry_tolerancia.get()).strip()
        a_str = self.entry_intervalo_inferior.get().strip()
        b_str = self.entry_intervalo_superior.get().strip()

        if not ecuacion:
            messagebox.showwarning("Ecuación vacía", "Por favor, ingresa una ecuación antes de calcular.")
            return
        if not a_str or not b_str or not tol_str:
            messagebox.showwarning(
                "Campos incompletos",
                "Debes llenar los campos de intervalo inferior (a), intervalo superior (b) y tolerancia."
            )
            return
        try:
            a = float(a_str); b = float(b_str)
        except ValueError:
            messagebox.showerror("Error de formato", "Los valores de los intervalos deben ser numéricos.")
            return

        try:
            tol = float(eval(tol_str, {"__builtins__": None}, {"e": 2.71828, "E": 2.71828, "pow": pow}))
        except Exception:
            messagebox.showerror(
                "Error en tolerancia",
                "La tolerancia no es válida.\nEjemplo de formatos permitidos: 0.001, 1e-4, 10^-4."
            )
            return

        try:
            sp.sympify(ecuacion)
        except Exception:
            messagebox.showerror(
                "Ecuación no válida",
                "La ecuación ingresada no es válida.\nRevisa paréntesis, operadores o variables."
            )
            return

        metodo = self.metodo_var.get()
        try:
            if metodo == "biseccion":
                resultado, iteraciones, filas = metodo_biseccion(ecuacion, a, b, tol)
                titulo = "Iteraciones del Método de Bisección:"
            else:
                resultado, iteraciones, filas = metodo_falsa_posicion(ecuacion, a, b, tol)
                titulo = "Iteraciones del Método de Falsa Posición:"

            # Inserción normalizada (formato fijo de decimales)
            for fila in filas:
                i, A, B, C, FA, FB, FC = fila
                self.tree.insert("", "end", values=(
                    int(i),
                    f"{A:.10f}", f"{B:.10f}", f"{C:.10f}",
                    f"{FA:.10f}", f"{FB:.10f}", f"{FC:.10f}",
                ))

            # Si filas trae error como último elemento en FC, evitamos romper:
            try:
                ultimo_fc = float(filas[-1][-1])
            except Exception:
                ultimo_fc = 0.0

            if self.mostrar_notacion_cientifica.get():
                error_fmt = f"{abs(ultimo_fc):.6g}"
            else:
                error_fmt = f"{abs(ultimo_fc):.10f}"

            self.label_resultado.config(
                text=f"{titulo.split(':')[0]} converge en {iteraciones} iteraciones.\n"
                    f"Raíz aproximada: {resultado:.10f}\n"
                    f"Margen de error: {error_fmt}"
            )

        except Exception as e:
            messagebox.showerror(
                "Error durante el cálculo",
                f"Ocurrió un problema al ejecutar el método ({metodo.replace('_', ' ')}):\n\n{e}"
            )
            self.label_resultado.config(text="Error: no se pudo completar el cálculo.")

    # ------------------------------------------------------------
    def calcular_biseccion(self):
        """Versión antigua (opcional) — mantenida por compatibilidad."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        ecuacion = self.teclado_frame.obtener_funcion().strip().replace("=0", "").strip()
        tol_str = str(self.entry_tolerancia.get()).strip()
        a_str = self.entry_intervalo_inferior.get().strip()
        b_str = self.entry_intervalo_superior.get().strip()

        if not ecuacion:
            messagebox.showwarning("Ecuación vacía", "Por favor, ingresa una ecuación antes de calcular.")
            return
        if not a_str or not b_str or not tol_str:
            messagebox.showwarning(
                "Campos incompletos",
                "Debes llenar los campos de intervalo inferior (a), intervalo superior (b) y tolerancia."
            )
            return
        try:
            a = float(a_str); b = float(b_str)
        except ValueError:
            messagebox.showerror("Error de formato", "Los valores de los intervalos deben ser numéricos.")
            return

        try:
            tol = float(eval(tol_str, {"__builtins__": None}, {"e": 2.71828, "E": 2.71828, "pow": pow}))
        except Exception:
            messagebox.showerror(
                "Error en tolerancia",
                "La tolerancia no es válida.\nEjemplo de formatos permitidos: 0.001, 1e-4, 10^-4."
            )
            return

        try:
            sp.sympify(ecuacion)
        except Exception:
            messagebox.showerror(
                "Ecuación no válida",
                "La ecuación ingresada no es válida.\nPor favor revisa los paréntesis, operadores o variables usadas."
            )
            return

        try:
            resultado, iteraciones, filas = metodo_biseccion(ecuacion, a, b, tol)

            for fila in filas:
                self.tree.insert("", "end", values=fila)

            self.label_resultado.config(
                text=f"El método converge en {iteraciones} iteraciones.\n"
                     f"La raíz aproximada es: {resultado:.10f}\n"
                     f"Margen de error: ±{tol:.6g}"
            )

        except Exception as e:
            messagebox.showerror(
                "Error durante el cálculo",
                f"Ocurrió un problema al intentar ejecutar el método de bisección:\n\n{e}"
            )
            self.label_resultado.config(text="Error: no se pudo completar el cálculo.")

    # ------------------------------------------------------------
    def _on_ecuacion_change(self, event):
        """
        Lee el texto EXACTO del input, lo normaliza SOLO para parsear (sin modificar el input),
        y si es válido, muestra el render tipografiado; si no, muestra aviso.
        """
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
            # USAMOS EL PRINTER PERSONALIZADO
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
            self._ax.text(0.01, 0.5, f"${tex_or_none}$",
                          va="center", ha="left", fontsize=16)
            self._fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)

        self._canvas_preview.draw_idle()
