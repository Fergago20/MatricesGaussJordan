# ui/matrices_app.py
import tkinter as tk
from soporte import preparar_ventana
from soporte import (
    preparar_ventana, a_fraccion, fraccion_a_str,
    patron_valido_para_coeficiente, matriz_alineada_con_titulo,
    hay_fracciones_en_lista
)
from core.lector_matriz import limpiar_matriz
from core import operaciones_matrices as opm
from tkinter import messagebox
from core.formato_matrices import formatear_matriz

# ===== Paleta =====
COLOR_FONDO        = "#EAF5FF"
COLOR_TEXTO        = "#6889AA"
COLOR_CAJA_BG      = "#FFFFFF"
COLOR_CAJA_FG      = "#000000"
COLOR_BOTON_BG     = "#0E3A5B"
COLOR_BOTON_FG     = "#FFFFFF"
COLOR_BOTON_BG_ACT = "#104467"

class AppMatrices(tk.Toplevel):
    """Pantalla para operaciones con matrices — diseño estilo MatrixCalc simplificado."""

    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(master=toplevel_parent)
        self.title("Operaciones con Matrices")
        self.configure(bg=COLOR_FONDO)
        preparar_ventana(self, usar_maximizada=True)

        self._on_volver = on_volver
        self.matriz_A = []
        self.matriz_B = []

        # Tamaño inicial de matrices
        self.filas_A = 3
        self.columnas_A = 3
        self.filas_B = 3
        self.columnas_B = 3

        self._construir_ui()
        self._generar_matriz("A")
        self._generar_matriz("B")

        self.protocol("WM_DELETE_WINDOW", self._cerrar_toda_la_app)

    def _construir_ui(self):
        estilo_btn = {
            "bg": COLOR_BOTON_BG, "fg": COLOR_BOTON_FG,
            "activebackground": COLOR_BOTON_BG_ACT, "activeforeground": COLOR_BOTON_FG,
            "relief": "raised", "bd": 2, "cursor": "hand2",
            "font": ("Segoe UI", 10, "bold"), "padx": 8, "pady": 4
        }

        # ==== Contenedor raíz ====
        raiz = tk.Frame(self, bg=COLOR_FONDO)
        raiz.pack(fill="both", expand=True)
        
        # ---- Botón Restablecer en esquina superior derecha ----
        btn_restablecer = tk.Button(
            raiz, text="Restablecer",
            command=self._restablecer_matrices,
            bg=COLOR_BOTON_BG, fg=COLOR_BOTON_FG,
            activebackground=COLOR_BOTON_BG_ACT, activeforeground=COLOR_BOTON_FG,
            relief="raised", bd=2, cursor="hand2",
            font=("Segoe UI", 9, "bold"), padx=6, pady=2
        )
        btn_restablecer.pack(side="top", anchor="ne", padx=10, pady=8)

        # ==== Centro ====
        centro = tk.Frame(raiz, bg=COLOR_FONDO)
        centro.pack(expand=True)   # <- clave: se expande al centro

        # ---------- MATRICES ----------
        fila_matrices = tk.Frame(centro, bg=COLOR_FONDO)
        fila_matrices.pack(pady=(20, 15))  # espacio arriba y abajo

        # Matriz A
        marco_A = tk.LabelFrame(fila_matrices, text="Matriz A",
                                fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                font=("Segoe UI", 10, "bold"))
        marco_A.grid(row=0, column=0, padx=20, sticky="n")
        self.contenedor_A = tk.Frame(marco_A, bg=COLOR_FONDO)
        self.contenedor_A.pack(pady=6)

        fila_botones_A = tk.Frame(fila_matrices, bg=COLOR_FONDO)
        fila_botones_A.grid(row=1, column=0, pady=(6, 0))
        tk.Button(fila_botones_A, text="+", command=lambda: self._ajustar_matriz("A", 1), **estilo_btn).pack(side="left", padx=4)
        tk.Button(fila_botones_A, text="-", command=lambda: self._ajustar_matriz("A", -1), **estilo_btn).pack(side="left", padx=4)
        tk.Button(fila_botones_A, text="Limpiar", command=lambda: self._limpiar_matriz("A"), **estilo_btn).pack(side="left", padx=4)

        # Botón intercambiar
        tk.Button(fila_matrices, text="↔", command=self._intercambiar, **estilo_btn)\
            .grid(row=0, column=1, rowspan=2, padx=10)

        # Matriz B
        marco_B = tk.LabelFrame(fila_matrices, text="Matriz B",
                                fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                font=("Segoe UI", 10, "bold"))
        marco_B.grid(row=0, column=2, padx=20, sticky="n")
        self.contenedor_B = tk.Frame(marco_B, bg=COLOR_FONDO)
        self.contenedor_B.pack(pady=6)

        fila_botones_B = tk.Frame(fila_matrices, bg=COLOR_FONDO)
        fila_botones_B.grid(row=1, column=2, pady=(6, 0))
        tk.Button(fila_botones_B, text="+", command=lambda: self._ajustar_matriz("B", 1), **estilo_btn).pack(side="left", padx=4)
        tk.Button(fila_botones_B, text="-", command=lambda: self._ajustar_matriz("B", -1), **estilo_btn).pack(side="left", padx=4)
        tk.Button(fila_botones_B, text="Limpiar", command=lambda: self._limpiar_matriz("B"), **estilo_btn).pack(side="left", padx=4)

        # ---------- Operaciones ----------
        fila_ops = tk.Frame(centro, bg=COLOR_FONDO)
        fila_ops.pack(pady=(5, 15))
        tk.Button(fila_ops, text="A × B", command=self._op_mult, **estilo_btn).grid(row=0, column=0, padx=6)
        tk.Button(fila_ops, text="A + B", command=self._op_suma, **estilo_btn).grid(row=0, column=1, padx=6)
        tk.Button(fila_ops, text="A - B", command=self._op_resta, **estilo_btn).grid(row=0, column=2, padx=6)

        # ---------- Procedimiento y Resultado ----------
        fila_resultados = tk.Frame(centro, bg=COLOR_FONDO)
        fila_resultados.pack(pady=(0, 12))

        marco_proc = tk.LabelFrame(fila_resultados, text="Procedimiento",
                                fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                font=("Segoe UI", 10, "bold"))
        marco_proc.grid(row=0, column=0, padx=10, sticky="nsew")
        self.texto_proc = tk.Text(marco_proc, height=12, bg=COLOR_CAJA_BG, fg=COLOR_CAJA_FG)
        self.texto_proc.pack(fill="both", expand=True, padx=6, pady=6)

        marco_res = tk.LabelFrame(fila_resultados, text="Resultado",
                                fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                font=("Segoe UI", 10, "bold"))
        marco_res.grid(row=0, column=1, padx=10, sticky="nsew")
        self.texto_res = tk.Text(marco_res, height=12, bg=COLOR_CAJA_BG, fg=COLOR_CAJA_FG)
        self.texto_res.pack(fill="both", expand=True, padx=6, pady=6)

        fila_resultados.grid_columnconfigure(0, weight=1)
        fila_resultados.grid_columnconfigure(1, weight=1)

        # Botón convertir (oculto al inicio)
        self.btn_convertir = tk.Button(marco_res, text="Mostrar en decimales",
                                    command=self._convertir_a_decimales, **estilo_btn)
        self.btn_convertir.pack(padx=6, pady=(0, 8))
        self.btn_convertir.pack_forget()

        # Botón encadenar resultado (oculto al inicio)
        self.btn_encadenar = tk.Button(
            marco_res, text="Encadenar Resultado",
            command=self._usar_resultado_en_A,
            **estilo_btn
        )
        self.btn_encadenar.pack(padx=6, pady=(0, 8))
        self.btn_encadenar.pack_forget()

        # ---------- Botón limpiar todo ----------
        tk.Button(centro, text="Limpiar todo", command=self._limpiar_todo, **estilo_btn)\
            .pack(pady=(6, 12))

        # ---------- Barra inferior ----------
        barra_inf = tk.Frame(raiz, bg=COLOR_FONDO)
        barra_inf.pack(fill="x", side="bottom", pady=(0, 8))
        tk.Button(barra_inf, text="← Volver al menú",
                command=self._volver_al_menu, **estilo_btn).pack(side="left")

    def _usar_resultado_en_A(self):
        """Copiar el resultado en la Matriz A (ajustada a NxN) y limpiar B, procedimiento y resultado."""
        if not hasattr(self, "resultado") or not self.resultado:
            return  # no hacer nada si no existe resultado válido

        # Validar que sea lista de listas
        if not isinstance(self.resultado, list) or not isinstance(self.resultado[0], list):
            return

        filas_res, cols_res = len(self.resultado), len(self.resultado[0])
        n = max(filas_res, cols_res)  # tamaño cuadrado necesario

        # Ajustar dimensiones de A a NxN
        self.filas_A, self.columnas_A = n, n
        self._generar_matriz("A")

        # Copiar valores del resultado en la esquina superior izquierda
        for i in range(filas_res):
            for j in range(cols_res):
                val = self.resultado[i][j]
                self.matriz_A[i][j].delete(0, "end")
                self.matriz_A[i][j].insert(0, str(val))

        # Dejar vacías las demás celdas de A
        for i in range(filas_res, n):
            for j in range(n):
                self.matriz_A[i][j].delete(0, "end")
        for i in range(filas_res):
            for j in range(cols_res, n):
                self.matriz_A[i][j].delete(0, "end")

        # Limpiar matriz B (manteniendo su tamaño actual, pero vacía)
        for fila in self.matriz_B:
            for e in fila:
                e.delete(0, "end")

        # Limpiar cuadros de procedimiento y resultado
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")

        # Ocultar botones
        self.btn_convertir.pack_forget()
        self.btn_encadenar.pack_forget()


    def _limpiar_matriz(self, cual):
        """Limpia completamente la matriz A o B (deja todas sus celdas vacías)."""
        if cual == "A":
            for fila in self.matriz_A:
                for e in fila:
                    e.delete(0, "end")
        else:  # Matriz B
            for fila in self.matriz_B:
                for e in fila:
                    e.delete(0, "end")
                    
    def _limpiar_todo(self):
        """Deja la ventana limpia, como recién abierta."""
        # Restablecer tamaño inicial
        self.filas_A = self.columnas_A = 3
        self.filas_B = self.columnas_B = 3
        self._generar_matriz("A")
        self._generar_matriz("B")

        # Vaciar texto de procedimiento y resultado
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")

        # Ocultar botones
        self.btn_convertir.pack_forget()
        self.btn_encadenar.pack_forget()

    # ----------------- Helpers UI -----------------
    def _generar_matriz(self, cual):
        """Crea entradas de texto para matriz A o B según tamaño actual."""
        if cual == "A":
            contenedor, filas, cols = self.contenedor_A, self.filas_A, self.columnas_A
        else:
            contenedor, filas, cols = self.contenedor_B, self.filas_B, self.columnas_B

        for w in contenedor.winfo_children():
            w.destroy()

        entradas = []
        for i in range(filas):
            fila = []
            for j in range(cols):
                e = self._crear_entry(contenedor)
                e.grid(row=i, column=j, padx=2, pady=2)
                fila.append(e)
            entradas.append(fila)

        if cual == "A":
            self.matriz_A = entradas
        else:
            self.matriz_B = entradas

    def _leer_matriz(self, cual):
        if cual == "A":
            return limpiar_matriz(self.matriz_A)
        else:
            return limpiar_matriz(self.matriz_B)


    def _crear_entry(self, parent) -> tk.Entry:
        e = tk.Entry(parent, width=5, justify="center",
                    bg=COLOR_CAJA_BG, fg=COLOR_CAJA_FG)

        vcmd = (e.register(patron_valido_para_coeficiente), "%P")
        e.config(validate="key", validatecommand=vcmd)

        # Inicia vacío (no "0")
        e.insert(0, "")

        # seleccionar todo al hacer clic
        e.bind("<FocusIn>", lambda _ev: e.select_range(0, "end"))

        return e
    
    def _mostrar_resultado(self, matriz):
        # Guardar resultado como fracciones (lista de listas)
        self.resultado = matriz

        # Mostrar resultado en fracciones
        self.texto_res.delete("1.0", "end")
        self.texto_res.insert("end", "Resultado (fracciones):\n\n")
        self.texto_res.insert("end", formatear_matriz(matriz, usar_decimales=False))

        # Decidir si mostrar botón de decimales
        tiene_fracciones = any(
            any(val.denominator != 1 for val in fila)
            for fila in self.resultado
        )

        if tiene_fracciones:
            self.btn_convertir.config(text="Mostrar en decimales")
            self.btn_convertir.pack(padx=6, pady=(0, 8))

        # Botón encadenar siempre
        self.btn_encadenar.pack(padx=6, pady=(0, 8))

    
    def _mostrar_error(self, mensaje):
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        self.btn_convertir.pack_forget()
        self.btn_encadenar.pack_forget()   # ← nuevo
        messagebox.showwarning("Operación inválida", mensaje)


    def _ajustar_matriz(self, cual, delta):
        if cual == "A":
            old_filas, old_cols = self.filas_A, self.columnas_A
            old_vals = [[e.get() for e in fila] for fila in self.matriz_A]

            # nuevo tamaño
            self.filas_A = max(1, old_filas + delta)
            self.columnas_A = max(1, old_cols + delta)
            self._generar_matriz("A")

            # restaurar valores que caben en la nueva grilla
            for i in range(min(old_filas, self.filas_A)):
                for j in range(min(old_cols, self.columnas_A)):
                    self.matriz_A[i][j].delete(0, "end")
                    self.matriz_A[i][j].insert(0, old_vals[i][j])

        else:  # para matriz B
            old_filas, old_cols = self.filas_B, self.columnas_B
            old_vals = [[e.get() for e in fila] for fila in self.matriz_B]

            # nuevo tamaño
            self.filas_B = max(1, old_filas + delta)
            self.columnas_B = max(1, old_cols + delta)
            self._generar_matriz("B")

            # restaurar valores que caben en la nueva grilla
            for i in range(min(old_filas, self.filas_B)):
                for j in range(min(old_cols, self.columnas_B)):
                    self.matriz_B[i][j].delete(0, "end")
                    self.matriz_B[i][j].insert(0, old_vals[i][j])


    def _intercambiar(self):
        # Leer contenidos actuales
        valores_A = self._leer_matriz("A")
        valores_B = self._leer_matriz("B")

        # Leer dimensiones actuales
        filas_A, cols_A = self.filas_A, self.columnas_A
        filas_B, cols_B = self.filas_B, self.columnas_B

        # Intercambiar dimensiones
        self.filas_A, self.columnas_A = filas_B, cols_B
        self.filas_B, self.columnas_B = filas_A, cols_A

        # Regenerar cuadros vacíos
        self._generar_matriz("A")
        self._generar_matriz("B")

        # Insertar valores intercambiados
        for i in range(min(self.filas_A, len(valores_B))):
            for j in range(min(self.columnas_A, len(valores_B[0]))):
                self.matriz_A[i][j].delete(0, "end")
                self.matriz_A[i][j].insert(0, str(valores_B[i][j]))

        for i in range(min(self.filas_B, len(valores_A))):
            for j in range(min(self.columnas_B, len(valores_A[0]))):
                self.matriz_B[i][j].delete(0, "end")
                self.matriz_B[i][j].insert(0, str(valores_A[i][j]))

    def _restablecer_matrices(self):
        self.filas_A = self.columnas_A = 3
        self.filas_B = self.columnas_B = 3
        self._generar_matriz("A")
        self._generar_matriz("B")
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        self.btn_convertir.pack_forget()
        self.btn_encadenar.pack_forget() 

    def _limpiar_todo(self):
        self._limpiar_matriz("A")
        self._limpiar_matriz("B")
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        self.btn_convertir.pack_forget()
        self.btn_encadenar.pack_forget()   

    # ----------------- Operaciones (placeholder) -----------------
    def _op_suma(self):
        A, B = self._leer_matriz("A"), self._leer_matriz("B")

        if len(A) != len(B) or len(A[0]) != len(B[0]):
            self._mostrar_error("Para sumar: A y B deben tener el mismo tamaño.")
            return

        res = opm.sumar_con_pasos(A, B)
        self._mostrar_desde_core(res)
        
    def _op_resta(self):
        A, B = self._leer_matriz("A"), self._leer_matriz("B")

        if len(A) != len(B) or len(A[0]) != len(B[0]):
            self._mostrar_error("Para restar: A y B deben tener el mismo tamaño.")
            return

        res = opm.restar_con_pasos(A, B)
        self._mostrar_desde_core(res)
    
    def _op_mult(self):
        A, B = self._leer_matriz("A"), self._leer_matriz("B")

        # Validación antes de cualquier impresión
        if len(A[0]) != len(B):
            self._mostrar_error("Para multiplicar: el número de columnas de A debe ser igual al número de filas de B.")
            return  # <- detener aquí

        res = opm.multiplicar_con_pasos(A, B)
        self._mostrar_desde_core(res)
    
    def _mostrar_error(self, mensaje):
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        self.btn_convertir.pack_forget()
        messagebox.showwarning("Operación inválida", mensaje)

    def _mostrar(self, texto):
        self.texto_proc.delete("1.0", "end")
        self.texto_proc.insert("end", "Aquí irán los pasos...\n")
        self.texto_res.delete("1.0", "end")
        self.texto_res.insert("end", texto)

    def _convertir_a_decimales(self):
        # Verificamos que existan resultados guardados
        if not hasattr(self, "resultado_str") or not hasattr(self, "resultado_dec"):
            return

        # Cambiamos entre fracciones y decimales
        t = self.btn_convertir.cget("text")
        self.texto_res.delete("1.0", "end")

        if t.startswith("Mostrar en decimales"):
            self.texto_res.insert("end", "Resultado (decimales):\n\n" + self.resultado_dec)
            self.btn_convertir.config(text="Ver fracciones")
        else:
            self.texto_res.insert("end", "Resultado (fracciones):\n\n" + self.resultado_str)
            self.btn_convertir.config(text="Mostrar en decimales")

        
    def _mostrar_desde_core(self, resultado):
        # Limpiar antes de mostrar
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        self.btn_convertir.pack_forget()
        self.btn_encadenar.pack_forget()

        if "error" in resultado:
            self._mostrar_error(resultado["error"])
            return

        # Mostrar procedimiento
        self.texto_proc.insert("end", resultado["procedimiento"] + "\n")

        # Guardar en dos formatos
        self.resultado = resultado["resultado_lista"]       # lista de listas (para encadenar)
        self.resultado_str = resultado["resultado_frac"]    # string fracciones
        self.resultado_dec = resultado["resultado_dec"]     # string decimales

        # Mostrar fracciones por defecto
        self.texto_res.insert("end", "Resultado:\n\n" + self.resultado_str)

        # Decidir si mostrar botón de decimales
        tiene_fracciones = any(
            any(val.denominator != 1 for val in fila)
            for fila in self.resultado
        )

        if tiene_fracciones:
            self.btn_convertir.config(text="Mostrar en decimales")
            self.btn_convertir.pack(padx=6, pady=(0, 8))

        # Botón encadenar siempre
        self.btn_encadenar.pack(padx=6, pady=(0, 8))

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
