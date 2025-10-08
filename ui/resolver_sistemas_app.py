import tkinter as tk
from tkinter import messagebox, ttk
from fractions import Fraction

from soporte.validaciones import (
    a_fraccion,
    fraccion_a_str,
    hay_fracciones_en_lista,
    patron_valido_para_coeficiente,
)
from soporte.formato_matrices import matriz_alineada_con_titulo
from soporte.helpers import preparar_ventana
from core.gauss import clasificar_y_resolver
from core.gauss_jordan import clasificar_y_resolver_gauss_jordan
from ui.estilos import (
    GAUSS_FONDO,
    GAUSS_TEXTO,
    GAUSS_CAJA_BG,
    GAUSS_CAJA_FG,
    GAUSS_SEL,
    GAUSS_BTN_BG,
    GAUSS_BTN_FG,
    GAUSS_BTN_BG_ACT,
)

class AppResolverSistemas(tk.Toplevel):
    """Ventana unificada para resolver sistemas con Gauss o Gauss-Jordan."""

    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(master=toplevel_parent)
        self.title("Resolver Sistemas — Gauss / Gauss-Jordan")
        self.configure(bg=GAUSS_FONDO)
        preparar_ventana(self, usar_maximizada=True)

        self._on_volver = on_volver

        # Estado general
        self.metodo = tk.StringVar(value="Gauss")  # ⬅ selector
        self.numero_variables = tk.IntVar(value=1)
        self.entradas_coeficientes = []
        self.sistema_actual = []
        self.soluciones_guardadas = None

        self._construir_ui()
        self.generar_plantilla()

        self.protocol("WM_DELETE_WINDOW", self._cerrar_toda_la_app)

    # ---------- UI ----------
    def _construir_ui(self):
        estilo_btn = {
            "bg": GAUSS_BTN_BG,
            "fg": GAUSS_BTN_FG,
            "activebackground": GAUSS_BTN_BG_ACT,
            "activeforeground": GAUSS_BTN_FG,
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
            "font": ("Segoe UI", 10, "bold"),
            "padx": 10,
            "pady": 6,
        }

        raiz = tk.Frame(self, bg=GAUSS_FONDO)
        raiz.pack(fill="both", expand=True)
        raiz.grid_columnconfigure(0, weight=0)
        raiz.grid_columnconfigure(1, weight=1)
        raiz.grid_rowconfigure(0, weight=1)
        raiz.grid_rowconfigure(1, weight=0)
        raiz.grid_rowconfigure(2, weight=0)

        # ===== Panel izquierdo =====
        izq = tk.Frame(raiz, bg=GAUSS_FONDO)
        izq.grid(row=0, column=0, sticky="nsew", padx=(10, 6), pady=(8, 6))
        izq.grid_columnconfigure(0, weight=1)

        # --- fila superior ---
        fila_superior = tk.Frame(izq, bg=GAUSS_FONDO)
        fila_superior.grid(row=0, column=0, sticky="w", pady=(0, 6))

        tk.Label(
            fila_superior,
            text="Método:",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        combo_metodo = ttk.Combobox(
            fila_superior,
            textvariable=self.metodo,
            values=["Gauss", "Gauss-Jordan"],
            state="readonly",
            width=12,
        )
        combo_metodo.pack(side="left", padx=(6, 10))

        tk.Label(
            fila_superior,
            text="Incógnitas:",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        tk.Spinbox(
            fila_superior,  
            from_=1,
            to=12,
            width=5,
            textvariable=self.numero_variables,
            bg=GAUSS_CAJA_BG,
            fg=GAUSS_CAJA_FG,
            justify="right", state='readonly'
        ).pack(side="left", padx=(6, 10))

        tk.Button(
            fila_superior, text="Generar plantilla", command=self.generar_plantilla, **estilo_btn
        ).pack(side="left")

        # --- Plantilla ecuaciones ---
        marco_plant = tk.LabelFrame(
            izq,
            text="Plantilla de ecuación (coeficientes y término independiente)",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        )
        marco_plant.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        marco_plant.grid_columnconfigure(0, weight=1)
        fila_plant = tk.Frame(marco_plant, bg=GAUSS_FONDO)
        fila_plant.grid(row=0, column=0, sticky="ew", padx=6, pady=8)

        self.contenedor_plantilla = tk.Frame(fila_plant, bg=GAUSS_FONDO)
        self.contenedor_plantilla.pack(side="left")

        tk.Button(
            fila_plant, text="Agregar ecuación", command=self.agregar_ecuacion, **estilo_btn
        ).pack(side="left", padx=(12, 0))

        # --- Lista de ecuaciones ---
        marco_sis = tk.LabelFrame(
            izq,
            text="Sistema de ecuaciones",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        )
        marco_sis.grid(row=2, column=0, sticky="ew")

        self.lista_sistema = tk.Listbox(
            marco_sis,
            width=40,
            height=10,
            bg=GAUSS_CAJA_BG,
            fg=GAUSS_CAJA_FG,
            selectbackground=GAUSS_SEL,
            highlightthickness=1,
        )
        self.lista_sistema.pack(fill="both", expand=True, padx=6, pady=6)

        fila_botones_sis = tk.Frame(izq, bg=GAUSS_FONDO)
        fila_botones_sis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        fila_botones_sis.grid_columnconfigure(1, weight=1)

        tk.Button(fila_botones_sis, text="Quitar", command=self.quitar_ecuacion, **estilo_btn).grid(
            row=0, column=0, padx=(0, 6)
        )
        tk.Button(fila_botones_sis, text="Limpiar", command=self.limpiar_sistema, **estilo_btn).grid(
            row=0, column=1, sticky="w"
        )
        tk.Button(fila_botones_sis, text="Resolver", command=self.resolver_sistema, **estilo_btn).grid(
            row=0, column=2, sticky="e"
        )

        # ===== Panel derecho =====
        der = tk.Frame(raiz, bg=GAUSS_FONDO)
        der.grid(row=0, column=1, rowspan=1, sticky="nsew", padx=(6, 10), pady=(8, 6))
        der.grid_columnconfigure(0, weight=1)
        der.grid_rowconfigure(0, weight=1)
        der.grid_rowconfigure(1, weight=0)

        self.marco_proc = tk.LabelFrame(
            der,
            text="Procedimiento",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        )
        self.marco_proc.grid(row=0, column=0, sticky="nsew")
        self.texto_proc = tk.Text(self.marco_proc, bg=GAUSS_CAJA_BG, fg=GAUSS_CAJA_FG)
        self.texto_proc.pack(fill="both", expand=True, padx=6, pady=6)

        self.marco_sol = tk.LabelFrame(
            raiz,
            text="Solución",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        )
        self.marco_sol.grid(row=1, column=1, sticky="ew", padx=(6, 10))
        self.texto_sol = tk.Text(self.marco_sol, height=8, bg=GAUSS_CAJA_BG, fg=GAUSS_CAJA_FG)
        self.texto_sol.pack(fill="x", padx=6, pady=6)

        self.btn_convertir = tk.Button(
            self.marco_sol, text="Mostrar en decimales", command=self.convertir_a_decimales, **estilo_btn
        )
        self.btn_convertir.pack(padx=6, pady=(0, 8))
        self.btn_convertir.pack_forget()

        barra_inf = tk.Frame(raiz, bg=GAUSS_FONDO)
        barra_inf.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        tk.Button(barra_inf, text="← Volver al menú", command=self._volver_al_menu, **estilo_btn).pack(side="left")

    # ---------- Helpers ----------
    def _crear_entry_coef(self, contenedor):
        e = tk.Entry(contenedor, width=7, justify="right", bg=GAUSS_CAJA_BG, fg=GAUSS_CAJA_FG)
        vcmd = (e.register(patron_valido_para_coeficiente), "%P")
        e.config(validate="key", validatecommand=vcmd)
        e.insert(0, "0")
        e.bind("<FocusIn>", lambda _ev: e.select_range(0, "end"))
        e.bind("<FocusOut>", lambda _ev: (e.insert(0, "0") if e.get().strip() == "" else None))
        return e

    def generar_plantilla(self):
        for w in self.contenedor_plantilla.winfo_children():
            w.destroy()
        self.entradas_coeficientes.clear()

        n = self.numero_variables.get()
        if n < 1:
            n = 1
            self.numero_variables.set(1)

        for i in range(n):
            tk.Label(self.contenedor_plantilla, text=f"x{i+1} =", fg=GAUSS_TEXTO, bg=self.contenedor_plantilla["bg"],
                     font=("Segoe UI", 10, "bold")).pack(side="left", padx=(4, 2))
            entrada = self._crear_entry_coef(self.contenedor_plantilla)
            entrada.pack(side="left", padx=(0, 6))
            self.entradas_coeficientes.append(entrada)

        tk.Label(self.contenedor_plantilla, text="= ", fg=GAUSS_TEXTO,
                 bg=self.contenedor_plantilla["bg"], font=("Segoe UI", 10, "bold")).pack(side="left")
        entrada_b = self._crear_entry_coef(self.contenedor_plantilla)
        entrada_b.pack(side="left", padx=(0, 6))
        self.entradas_coeficientes.append(entrada_b)

    # ---------- Acciones ----------
    def agregar_ecuacion(self):
        fila_textos = [c.get().strip() for c in self.entradas_coeficientes]

        # Validar caracteres incompletos
        if any(x in {".", "-", "/"} for x in fila_textos):
            messagebox.showerror("Error", "Coeficientes incompletos: no puede usar '.', '-', o '/' solos.")
            for c in self.entradas_coeficientes:
                c.delete(0, "end")
                c.insert(0, "0")
            return

        fila = [a_fraccion(v) for v in fila_textos]
        coeficientes, b = fila[:-1], fila[-1]

        # Evitar ecuaciones nulas
        if all(c == 0 for c in coeficientes) and b == 0:
            messagebox.showwarning("Ecuación inválida", "La ecuación es 0 = 0; no será agregada.")
            for c in self.entradas_coeficientes:
                c.delete(0, "end")
                c.insert(0, "0")
            return

        # Guardar la ecuación internamente
        self.sistema_actual.append(fila)

        partes = []
        for i, c in enumerate(coeficientes):
            if c == 0:
                continue
            signo = " + " if c > 0 and partes else (" - " if c < 0 else "")
            coef_abs = abs(c)
            if coef_abs == 1:
                partes.append(f"{signo}x{i+1}")
            else:
                partes.append(f"{signo}{coef_abs}x{i+1}")

        ecuacion_texto = "".join(partes) if partes else "0"
        self.lista_sistema.insert("end", f"{ecuacion_texto} = {b}")

        # Limpiar entradas
        for c in self.entradas_coeficientes:
            c.delete(0, "end")
            c.insert(0, "0")


    def quitar_ecuacion(self):
        sel = self.lista_sistema.curselection()
        if sel:
            idx = sel[0]
            self.lista_sistema.delete(idx)
            self.sistema_actual.pop(idx)

    def limpiar_sistema(self):
        self.lista_sistema.delete(0, "end")
        self.sistema_actual.clear()
        self.texto_proc.delete("1.0", "end")
        self.texto_sol.delete("1.0", "end")
        self.btn_convertir.pack_forget()
        self.soluciones_guardadas = None

    def resolver_sistema(self):
        if len(self.sistema_actual) < 2:
            messagebox.showerror("Error", "Agrega al menos dos ecuaciones para resolver.")
            return

        metodo = self.metodo.get()
        self.texto_proc.delete("1.0", "end")

        self.texto_proc.insert("end", matriz_alineada_con_titulo("Matriz inicial (A|b):", self.sistema_actual, con_barra=True))

        if metodo == "Gauss":
            resultado = clasificar_y_resolver(self.sistema_actual)
        else:
            resultado = clasificar_y_resolver_gauss_jordan(self.sistema_actual)

        self.texto_proc.insert("end", "\n".join(resultado["pasos"]))
        self.texto_sol.delete("1.0", "end")
        self.texto_sol.insert("end", resultado["mensaje_tipo"] + "\n\n")

        self.soluciones_guardadas = None
        self.btn_convertir.pack_forget()

        tipo = resultado["tipo_solucion"]
        if tipo == "única":
            self.soluciones_guardadas = resultado["soluciones"]
            for i, v in enumerate(self.soluciones_guardadas, start=1):
                self.texto_sol.insert("end", f"x{i} = {fraccion_a_str(v)}\n")
            if hay_fracciones_en_lista(self.soluciones_guardadas):
                self.btn_convertir.config(text="Mostrar en decimales")
                self.btn_convertir.pack(padx=6, pady=(0, 8))
        elif tipo == "infinita":
            for linea in (resultado.get("solucion_parametrica") or []):
                self.texto_sol.insert("end", linea + "\n")

    def convertir_a_decimales(self):
        if not self.soluciones_guardadas:
            return

        # Detectar modo actual
        t = self.btn_convertir.cget("text")
        es_modo_decimal = t.startswith("Mostrar en decimales")

        # Obtener encabezado existente
        contenido_actual = self.texto_sol.get("1.0", "end").strip().split("\n")
        encabezado = contenido_actual[0] if contenido_actual else "Solución única."

        # Limpiar solo la zona de texto, pero mantener encabezado
        self.texto_sol.delete("1.0", "end")

        # Mostrar valores según el modo
        if es_modo_decimal:
            self.texto_sol.insert("end", "Solución única (decimales):\n\n")
            for i, v in enumerate(self.soluciones_guardadas, start=1):
                self.texto_sol.insert("end", f"x{i} = {float(v)}\n")
            self.btn_convertir.config(text="Ver fracciones")
        else:
            self.texto_sol.insert("end", "Solución única (fracciones):\n\n")
            for i, v in enumerate(self.soluciones_guardadas, start=1):
                self.texto_sol.insert("end", f"x{i} = {fraccion_a_str(v)}\n")
            self.btn_convertir.config(text="Mostrar en decimales")

    # ---------- Navegación ----------
    def _cerrar_toda_la_app(self):
        raiz = self.master
        if isinstance(raiz, tk.Tk):
            raiz.destroy()

    def _volver_al_menu(self):
        try:
            self.destroy()
        finally:
            if callable(self._on_volver):
                self._on_volver()
