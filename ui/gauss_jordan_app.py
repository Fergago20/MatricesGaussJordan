# ui/gauss_jordan_app.py
import tkinter as tk
from tkinter import messagebox

from soporte import (
    a_fraccion, fraccion_a_str, hay_fracciones_en_lista,
    formatear_ecuacion_linea, matriz_alineada_con_titulo,
    patron_valido_para_coeficiente, preparar_ventana
)
from core.gauss_jordan import clasificar_y_resolver_gauss_jordan


class AppGaussJordan(tk.Toplevel):
    """Pantalla del método de Gauss-Jordan (RREF) con tema claro."""

    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(master=toplevel_parent)
        self.title("Método de Gauss-Jordan")
        # --- Tema blanco ---
        self.configure(bg="#ffffff")
        preparar_ventana(self, usar_maximizada=True)

        self._on_volver = on_volver  # callback opcional para botón "Volver al menú"

        # Estado
        self.numero_variables = tk.IntVar(value=1)
        self.entradas_coeficientes = []
        self.sistema_actual = []
        self.soluciones_guardadas = None

        self._construir_ui()
        self.generar_plantilla()

        # X cierra toda la aplicación
        self.protocol("WM_DELETE_WINDOW", self._cerrar_toda_la_app)

    # ---------- Construcción de UI ----------
    def _construir_ui(self):
        # Paleta clara
        fondo = "#ffffff"      # fondo general
        texto = "#111827"      # texto principal
        bg_caja = "#f8fafc"    # fondo de Text/Listbox
        fg_caja = "#111827"    # texto en cajas
        sel_bg = "#e5e7eb"     # selección en listbox

        estilo_btn = {
            "bg": "#f3f4f6", "fg": "#111827",
            "activebackground": "#e5e7eb", "activeforeground": "#111827",
            "relief": "raised", "bd": 2, "cursor": "hand2"
        }

        # Barra superior
        barra = tk.Frame(self, bg=fondo)
        barra.pack(fill="x", padx=10, pady=(8, 6))

        tk.Button(barra, text="← Volver al menú", command=self._volver_al_menu, **estilo_btn)\
            .pack(side="left", padx=(0, 10))

        tk.Label(barra, text="Incógnitas:", fg=texto, bg=fondo).pack(side="left")
        tk.Spinbox(barra, from_=1, to=12, width=5, textvariable=self.numero_variables)\
            .pack(side="left", padx=(6, 10))

        tk.Button(barra, text="Generar plantilla", command=self.generar_plantilla, **estilo_btn)\
            .pack(side="left")

        # Panel central
        panel = tk.Frame(self, bg=fondo)
        panel.pack(fill="both", expand=True, padx=10, pady=6)

        # Columna izquierda (plantilla + sistema + acciones)
        izq = tk.Frame(panel, bg=fondo)
        izq.pack(side="left", fill="y", padx=(0, 10))

        marco_plant = tk.LabelFrame(
            izq, text="Plantilla de ecuación (coeficientes y término independiente)",
            fg=texto, bg=fondo
        )
        marco_plant.pack(fill="x", pady=(0, 8))

        fila_plant = tk.Frame(marco_plant, bg=fondo)
        fila_plant.pack(fill="x", padx=6, pady=8)

        self.contenedor_plantilla = tk.Frame(fila_plant, bg=fondo)
        self.contenedor_plantilla.pack(side="left")

        tk.Button(fila_plant, text="Agregar ecuación", command=self.agregar_ecuacion, **estilo_btn)\
            .pack(side="left", padx=(12, 0))

        marco_sis = tk.LabelFrame(izq, text="Sistema de ecuaciones", fg=texto, bg=fondo)
        marco_sis.pack(fill="both", expand=True)

        self.lista_sistema = tk.Listbox(
            marco_sis, width=48, height=18,
            bg=bg_caja, fg=fg_caja, selectbackground=sel_bg
        )
        self.lista_sistema.pack(fill="both", expand=True, padx=6, pady=6)

        fila_btns = tk.Frame(izq, bg=fondo)
        fila_btns.pack(fill="x", pady=(8, 0))
        tk.Button(fila_btns, text="Quitar", command=self.quitar_ecuacion, **estilo_btn).pack(side="left", padx=4)
        tk.Button(fila_btns, text="Limpiar", command=self.limpiar_sistema, **estilo_btn).pack(side="left", padx=4)
        tk.Button(fila_btns, text="Resolver", command=self.resolver_sistema, **estilo_btn).pack(side="left", padx=4)

        # Columna derecha (procedimiento + solución)
        der = tk.Frame(panel, bg=fondo)
        der.pack(side="left", fill="both", expand=True)

        self.marco_proc = tk.LabelFrame(der, text="Procedimiento (Gauss-Jordan: RREF)", fg=texto, bg=fondo)
        self.marco_proc.pack(fill="both", expand=True)

        self.texto_proc = tk.Text(self.marco_proc, bg=bg_caja, fg=fg_caja)
        self.texto_proc.pack(fill="both", expand=True, padx=6, pady=6)

        self.marco_sol = tk.LabelFrame(der, text="Solución", fg=texto, bg=fondo)
        self.marco_sol.pack(fill="x", pady=(8, 0))

        self.texto_sol = tk.Text(self.marco_sol, height=8, bg=bg_caja, fg=fg_caja)
        self.texto_sol.pack(fill="x", padx=6, pady=6)

        self.btn_convertir = tk.Button(self.marco_sol, text="Mostrar en decimales",
                                       command=self.convertir_a_decimales, **estilo_btn)
        self.btn_convertir.pack(padx=6, pady=(0, 8))
        self.btn_convertir.pack_forget()

    # ---------- Plantilla ----------
    def _crear_entry_coef(self, contenedor):
        """Entry validada, 0 por defecto, selección al enfocar y reposición de 0 al salir."""
        e = tk.Entry(contenedor, width=7, justify="right", bg="#ffffff", fg="#111827")
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
            tk.Label(self.contenedor_plantilla, text=f"x{i+1} =", fg="#111827",
                     bg=self.contenedor_plantilla["bg"]).pack(side="left", padx=(4, 2))
            entrada = self._crear_entry_coef(self.contenedor_plantilla)
            entrada.pack(side="left", padx=(0, 6))
            self.entradas_coeficientes.append(entrada)

        tk.Label(self.contenedor_plantilla, text="= ", fg="#111827",
                 bg=self.contenedor_plantilla["bg"]).pack(side="left")
        entrada_b = self._crear_entry_coef(self.contenedor_plantilla)
        entrada_b.pack(side="left", padx=(0, 6))
        self.entradas_coeficientes.append(entrada_b)

    def _leer_fila_plantilla(self):
        return [a_fraccion(c.get()) for c in self.entradas_coeficientes]

    # ---------- cierre ----------
    def _cerrar_toda_la_app(self):
        """Cierra completamente la aplicación al pulsar la X en esta ventana."""
        raiz = self.master
        if isinstance(raiz, tk.Tk):
            raiz.destroy()

    def _volver_al_menu(self):
        """Botón opcional: vuelve al menú; la X cierra todo."""
        try:
            self.destroy()
        finally:
            if callable(self._on_volver):
                self._on_volver()

    # ---------- acciones ----------
    def agregar_ecuacion(self):
        fila = self._leer_fila_plantilla()
        coefs, b = fila[:-1], fila[-1]

        # Bloquear 0 = 0
        if all(c == 0 for c in coefs) and b == 0:
            messagebox.showwarning("Ecuación inválida", "La ecuación es 0 = 0; no será agregada.")
            for c in self.entradas_coeficientes:
                c.delete(0, "end"); c.insert(0, "0")
            if self.entradas_coeficientes:
                self.entradas_coeficientes[0].focus_set()
            return

        self.sistema_actual.append(fila)
        self.lista_sistema.insert("end", formatear_ecuacion_linea(fila))

        # Limpiar y enfocar
        for c in self.entradas_coeficientes:
            c.delete(0, "end"); c.insert(0, "0")
        if self.entradas_coeficientes:
            self.entradas_coeficientes[0].focus_set()

    def quitar_ecuacion(self):
        sel = self.lista_sistema.curselection()
        if not sel:
            return
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

        # Procedimiento (solo matrices)
        self.texto_proc.delete("1.0", "end")
        self.texto_proc.insert(
            "end",
            matriz_alineada_con_titulo("Matriz inicial (A|b):", self.sistema_actual, con_barra=True)
        )
        resultado = clasificar_y_resolver_gauss_jordan(self.sistema_actual)
        self.texto_proc.insert("end", "".join(resultado["pasos"]))

        # Solución
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
        t = self.btn_convertir.cget("text")
        self.texto_sol.delete("1.0", "end")
        if t.startswith("Mostrar en decimales"):
            self.texto_sol.insert("end", "Solución única (decimales):\n\n")
            for i, v in enumerate(self.soluciones_guardadas, start=1):
                self.texto_sol.insert("end", f"x{i} = {float(v)}\n")
            self.btn_convertir.config(text="Ver fracciones")
        else:
            self.texto_sol.insert("end", "Solución única (fracciones):\n\n")
            for i, v in enumerate(self.soluciones_guardadas, start=1):
                self.texto_sol.insert("end", f"x{i} = {fraccion_a_str(v)}\n")
            self.btn_convertir.config(text="Mostrar en decimales")
