import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import sympy as sp
import re
from sympy import symbols, pi, E
from core.biserccion import calcular_biseccion as metodo_biseccion
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
            ).grid(row=(i - 1) // 3, column=(i - 1) % 3, padx=2, pady=2)
        ctk.CTkButton(self.frame_derecho, text="0",
                      command=lambda: self.al_presionar_boton("0"),
                      fg_color=MN_BTN_BG, text_color=MN_BTN_FG,
                      hover_color=MN_BTN_BG_ACT).grid(row=3, column=0, padx=2, pady=2)

    def crear_botones_aritmeticos(self):
        for i, op in enumerate(['+', '-', '*', '/']):
            ctk.CTkButton(
                self.frame_derecho, text=op,
                fg_color=MN_BTN_BG, text_color=MN_BTN_FG,
                hover_color=MN_BTN_BG_ACT,
                command=lambda t=op: self.al_presionar_boton(t)
            ).grid(row=i, column=3, padx=2, pady=2)

    def crear_boton_limpiar(self):
        ctk.CTkButton(self.frame_derecho, text="C",
                      command=lambda: self.parent_textbox.delete(0, 'end'),
                      fg_color="#D9534F", text_color="white").grid(row=4, column=1, padx=2, pady=2)

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
            .replace('^', '**'))

        # ---------------------------
        # 1) Unicode √ con o sin índice → sqrt o root
        # ---------------------------

        # √[n](expr) -> sqrt(expr) si n==2, si no -> root(expr, n)
        def _repl_rad_n(m):
            n = m.group(1)
            expr = m.group(2)
            return f"sqrt({expr})" if n == '2' else f"root({expr}, {n})"

        f = re.sub(r'√\s*\[\s*(\d+)\s*\]\s*\(\s*([^)]+?)\s*\)', _repl_rad_n, f)

        # √(expr) -> sqrt(expr) (cuadrada por defecto)
        f = re.sub(r'√\s*\(\s*([^)]+?)\s*\)', r'sqrt(\1)', f)

        # ---------------------------
        # 2) sqrt(...) y cbrt(...) → destino
        # ---------------------------

        # Caso A: sqrt(n, expr) -> sqrt(expr) si n==2; si no -> root(expr, n)
        def _repl_sqrt_n_expr(m):
            n = m.group(1)
            expr = m.group(2)
            return f"sqrt({expr})" if n == '2' else f"root({expr}, {n})"

        f = re.sub(r'sqrt\(\s*(\d+)\s*,\s*([^)]+?)\s*\)', _repl_sqrt_n_expr, f)

        # Caso B: sqrt(expr, n) -> sqrt(expr) si n==2; si no -> root(expr, n)
        def _repl_sqrt_expr_n(m):
            expr = m.group(1)
            n = m.group(2)
            return f"sqrt({expr})" if n == '2' else f"root({expr}, {n})"

        f = re.sub(r'sqrt\(\s*([^)]+?)\s*,\s*(\d+)\s*\)', _repl_sqrt_expr_n, f)

        # cbrt(expr) -> root(expr, 3)
        f = re.sub(r'cbrt\(\s*([^)]+?)\s*\)', r'root(\1, 3)', f)

        # Nota: sqrt(expr) simple se deja tal cual (raíz cuadrada)

        # ---------------------------
        # 3) Potencias fraccionarias **(1/n) → sqrt o root
        # ---------------------------

        # Arregla precedencia: **1/n -> **(1/n)
        f = re.sub(r'\*\*\s*1\s*/\s*(\d+)', r'**(1/\1)', f)

        # (base)**(1/n) -> sqrt(base) si n==2; si no -> root(base, n)
        def _repl_pow_paren(m):
            base = m.group(1)
            n = m.group(2)
            return f"sqrt({base})" if n == '2' else f"root({base}, {n})"

        f = re.sub(r'\(\s*([^\(\)]+?)\s*\)\s*\*\*\s*\(\s*1\s*/\s*(\d+)\s*\)', _repl_pow_paren, f)

        # base_simple**(1/n) -> sqrt(base_simple) si n==2; si no -> root(base_simple, n)
        def _repl_pow_simple(m):
            base = m.group(1)
            n = m.group(2)
            return f"sqrt({base})" if n == '2' else f"root({base}, {n})"

        f = re.sub(
            r'([A-Za-z_]\w*(?:\([^\)]*\))?|\d+(?:\.\d+)?)\s*\*\*\s*\(\s*1\s*/\s*(\d+)\s*\)',
            _repl_pow_simple,
            f
        )

        # ---------------------------
        # 4) Multiplicación implícita básica
        # ---------------------------
        # 2x -> 2*x, 2( -> 2*(, )( -> )*(, )x -> )*x
        f = re.sub(r'(\d)\s*([a-zA-Z\(])', r'\1*\2', f)
        f = re.sub(r'(\))\s*([a-zA-Z\(])', r'\1*\2', f)
        print(f)
        return f




# ============================================================
#   INTERFAZ PRINCIPAL: Método de Bisección
# ============================================================

class AppMetodosNumericos(BaseApp):
    """Interfaz visual con el método de bisección."""
    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(toplevel_parent, on_volver, titulo="Método de Bisección")
        self.configure(bg=MN_FONDO)

        self.entry_ecuacion = tk.StringVar()
        self.entry_tolerancia = tk.DoubleVar(value=0.0001)
        self.entry_intervalo_inferior = tk.StringVar()
        self.entry_intervalo_superior = tk.StringVar()

        self._construir_ui()

    def _construir_ui(self):
        estilo_btn = {
            "bg": MN_BTN_BG, "fg": MN_BTN_FG,
            "activebackground": MN_BTN_BG_ACT, "activeforeground": MN_BTN_FG,
            "relief": "raised", "bd": 2, "cursor": "hand2",
            "font": FUENTE_BOLD, "padx": 8, "pady": 4
        }

        raiz = tk.Frame(self, bg=MN_FONDO)
        raiz.pack(fill="both", expand=True, padx=10, pady=10)

        # ==== Ecuación ====
        panel_ecuacion = tk.Frame(raiz, bg=MN_FONDO)
        panel_ecuacion.pack(fill="x", pady=(5, 10))
        tk.Label(panel_ecuacion, text="Ecuación:", font=FUENTE_SUBTITULO, bg=MN_FONDO, fg=MN_TEXTO).pack(side="left", padx=5)
        self.entry_ecuacion_widget = tk.Entry(panel_ecuacion, textvariable=self.entry_ecuacion,
                                              font=("Segoe UI", 14), width=50,
                                              bg="white", fg="black", insertbackground="black")
        self.entry_ecuacion_widget.pack(side="left", fill="x", expand=True, padx=5)

        # ==== Calculadora científica ====
        self.teclado_frame = CalculadoraCientificaFrame(raiz, self.entry_ecuacion_widget)
        self.teclado_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ==== Intervalos y botones de acción ====
        frame_intervalos = tk.Frame(raiz, bg=MN_FONDO)
        frame_intervalos.pack(fill="x", pady=5)

        # Intervalo inferior
        tk.Label(frame_intervalos, text="Intervalo inferior (a):", bg=MN_FONDO, fg=MN_TEXTO).pack(side="left", padx=5)
        tk.Entry(frame_intervalos, textvariable=self.entry_intervalo_inferior, font=("Segoe UI", 12),
                 width=10, bg=MN_CAJA_BG, fg=MN_CAJA_FG, justify="center").pack(side="left", padx=5)

        # Intervalo superior
        tk.Label(frame_intervalos, text="Intervalo superior (b):", bg=MN_FONDO, fg=MN_TEXTO).pack(side="left", padx=5)
        tk.Entry(frame_intervalos, textvariable=self.entry_intervalo_superior, font=("Segoe UI", 12),
                 width=10, bg=MN_CAJA_BG, fg=MN_CAJA_FG, justify="center").pack(side="left", padx=5)

        # Tolerancia
        tk.Label(frame_intervalos, text="Tolerancia:", bg=MN_FONDO, fg=MN_TEXTO).pack(side="left", padx=5)
        tk.Entry(frame_intervalos, textvariable=self.entry_tolerancia, font=("Segoe UI", 12),
                 width=10, bg=MN_CAJA_BG, fg=MN_CAJA_FG, justify="center").pack(side="left", padx=5)

        # Botones Graficar y Calcular al lado derecho
        tk.Button(frame_intervalos, text="Graficar Función",
                  command=lambda: graficar_funcion(self.teclado_frame.obtener_funcion()), **estilo_btn)\
            .pack(side="right", padx=6)
        tk.Button(frame_intervalos, text="Calcular Bisección", command=self.calcular_biseccion, **estilo_btn)\
            .pack(side="right", padx=6)

        # ==== Tabla de iteraciones ====
        panel_tabla = tk.Frame(raiz, bg=MN_FONDO)
        panel_tabla.pack(fill="both", expand=True, pady=10)
        tk.Label(panel_tabla, text="Iteraciones del Método de Bisección:", font=FUENTE_SUBTITULO,
                 bg=MN_FONDO, fg=MN_TEXTO).pack(anchor="w", pady=5)
        columnas = ("Iteración", "a", "b", "c", "f(a)", "f(b)", "f(c)")
        self.tree = ttk.Treeview(panel_tabla, columns=columnas, show="headings", height=10)
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(panel_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # ==== Resultado ====
        self.label_resultado = tk.Label(
            raiz,
            text="Aún no se ha realizado ningún cálculo.",
            font=("Segoe UI", 12, "bold"),
            bg=MN_FONDO, fg=MN_TEXTO, anchor="w", justify="left"
        )
        self.label_resultado.pack(fill="x", padx=10, pady=(5, 10))

        # ==== Barra inferior ====
        barra_inf = tk.Frame(raiz, bg=MN_FONDO)
        barra_inf.pack(fill="x", pady=(5, 10))
        tk.Button(barra_inf, text="← Volver al menú", command=self._volver_al_menu, **estilo_btn)\
            .pack(side="left", padx=5)

    # ------------------------------------------------------------
    def calcular_biseccion(self):
        """Ejecuta el método de bisección y muestra los resultados con validaciones mejoradas."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        ecuacion = self.teclado_frame.obtener_funcion().strip()
        ecuacion = ecuacion.replace("=0", "").strip()  # 🔹 elimina el "=0" si lo escribieron

        tol_str = str(self.entry_tolerancia.get()).strip()
        a_str = self.entry_intervalo_inferior.get().strip()
        b_str = self.entry_intervalo_superior.get().strip()

        # ------------------------------------------------------
        # 🔹 VALIDACIONES DE CAMPOS VACÍOS
        # ------------------------------------------------------
        if not ecuacion:
            messagebox.showwarning("Ecuación vacía", "Por favor, ingresa una ecuación antes de calcular.")
            return

        if not a_str or not b_str or not tol_str:
            messagebox.showwarning(
                "Campos incompletos",
                "Debes llenar los campos de intervalo inferior (a), intervalo superior (b) y tolerancia."
            )
            return

        # ------------------------------------------------------
        # 🔹 CONVERTIR A VALORES NUMÉRICOS
        # ------------------------------------------------------
        try:
            a = float(a_str)
            b = float(b_str)
        except ValueError:
            messagebox.showerror(
                "Error de formato",
                "Los valores de los intervalos deben ser numéricos."
            )
            return

        # Interpretar la tolerancia correctamente (permite 10^-4, 1e-3, etc.)
        try:
            tol = float(eval(tol_str, {"__builtins__": None}, {"e": 2.71828, "E": 2.71828, "pow": pow}))
        except Exception:
            messagebox.showerror(
                "Error en tolerancia",
                "La tolerancia no es válida.\nEjemplo de formatos permitidos: 0.001, 1e-4, 10^-4."
            )
            return

        # ------------------------------------------------------
        # 🔹 VALIDAR LA ECUACIÓN SINTÁCTICAMENTE
        # ------------------------------------------------------
        try:
            sp.sympify(ecuacion)
        except Exception:
            messagebox.showerror(
                "Ecuación no válida",
                "La ecuación ingresada no es válida.\nPor favor revisa los paréntesis, operadores o variables usadas."
            )
            return

        # ------------------------------------------------------
        # 🔹 VERIFICAR SIGNOS EN LOS EXTREMOS DEL INTERVALO
        # ------------------------------------------------------

        # ------------------------------------------------------
        # 🔹 CÁLCULO DEL MÉTODO DE BISECCIÓN
        # ------------------------------------------------------
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
