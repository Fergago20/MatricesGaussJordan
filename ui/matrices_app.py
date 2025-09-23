# ui/matrices_app.py
import tkinter as tk
from tkinter import messagebox
from soporte import (
    preparar_ventana, a_fraccion, fraccion_a_str,
    patron_valido_para_coeficiente, matriz_alineada_con_titulo,
    hay_fracciones_en_lista
)
from core.lector_matriz import limpiar_matriz
from core import operaciones_matrices as opm
from core import operaciones_vectores as opv
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
    """Pantalla para operaciones con matrices o vectores."""

    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(master=toplevel_parent)
        self.title("Operaciones con Matrices / Vectores")
        self.configure(bg=COLOR_FONDO)
        preparar_ventana(self, usar_maximizada=True)

        self._on_volver = on_volver
        self.modo_vector = False  # False = matrices, True = vectores

        # Tamaños iniciales
        self.filas_A = 3
        self.columnas_A = 3
        self.filas_B = 3
        self.columnas_B = 3

        # Entradas
        self.matriz_A = []
        self.matriz_B = []

        # Estado de resultados
        self.resultado = None
        self.resultado_str = ""
        self.resultado_dec = ""
        self.mostrando_decimales = False

        self._construir_ui()
        self._generar_matriz("A")
        self._generar_matriz("B")

        self.protocol("WM_DELETE_WINDOW", self._cerrar_toda_la_app)

    # ---------- UI ----------
    def _construir_ui(self):
        estilo_btn = {
            "bg": COLOR_BOTON_BG, "fg": COLOR_BOTON_FG,
            "activebackground": COLOR_BOTON_BG_ACT, "activeforeground": COLOR_BOTON_FG,
            "relief": "raised", "bd": 2, "cursor": "hand2",
            "font": ("Segoe UI", 10, "bold"), "padx": 8, "pady": 4
        }

        raiz = tk.Frame(self, bg=COLOR_FONDO)
        raiz.pack(fill="both", expand=True)

        # Botón Restablecer
        tk.Button(raiz, text="Restablecer", command=self._restablecer_matrices, **estilo_btn)\
            .pack(side="top", anchor="ne", padx=10, pady=8)

        # Botón cambio de modo
        self.btn_modo = tk.Button(
            raiz, text="Cambiar a modo Vectores",
            command=self._cambiar_modo, **estilo_btn
        )
        self.btn_modo.pack(side="top", anchor="nw", padx=10, pady=8)

        centro = tk.Frame(raiz, bg=COLOR_FONDO)
        centro.pack(expand=True)

        fila_matrices = tk.Frame(centro, bg=COLOR_FONDO)
        fila_matrices.pack(pady=(20, 15))

        # A
        self.marco_A = tk.LabelFrame(fila_matrices, text="Matriz A",
                                     fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                     font=("Segoe UI", 10, "bold"))
        self.marco_A.grid(row=0, column=0, padx=20, sticky="n")
        self.contenedor_A = tk.Frame(self.marco_A, bg=COLOR_FONDO)
        self.contenedor_A.pack(pady=6)

        self.fila_botones_A = tk.Frame(fila_matrices, bg=COLOR_FONDO)
        self.fila_botones_A.grid(row=1, column=0, pady=(6, 0))
        tk.Button(self.fila_botones_A, text="+", command=lambda: self._ajustar_matriz("A", 1), **estilo_btn)\
            .pack(side="left", padx=4)
        tk.Button(self.fila_botones_A, text="-", command=lambda: self._ajustar_matriz("A", -1), **estilo_btn)\
            .pack(side="left", padx=4)
        tk.Button(self.fila_botones_A, text="Limpiar", command=lambda: self._limpiar_matriz("A"), **estilo_btn)\
            .pack(side="left", padx=4)

        # Intercambiar
        tk.Button(fila_matrices, text="↔", command=self._intercambiar, **estilo_btn)\
            .grid(row=0, column=1, rowspan=2, padx=10)

        # B
        self.marco_B = tk.LabelFrame(fila_matrices, text="Matriz B",
                                     fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                     font=("Segoe UI", 10, "bold"))
        self.marco_B.grid(row=0, column=2, padx=20, sticky="n")
        self.contenedor_B = tk.Frame(self.marco_B, bg=COLOR_FONDO)
        self.contenedor_B.pack(pady=6)

        self.fila_botones_B = tk.Frame(fila_matrices, bg=COLOR_FONDO)
        self.fila_botones_B.grid(row=1, column=2, pady=(6, 0))
        tk.Button(self.fila_botones_B, text="+", command=lambda: self._ajustar_matriz("B", 1), **estilo_btn)\
            .pack(side="left", padx=4)
        tk.Button(self.fila_botones_B, text="-", command=lambda: self._ajustar_matriz("B", -1), **estilo_btn)\
            .pack(side="left", padx=4)
        tk.Button(self.fila_botones_B, text="Limpiar", command=lambda: self._limpiar_matriz("B"), **estilo_btn)\
            .pack(side="left", padx=4)

        # Operaciones
        fila_ops = tk.Frame(centro, bg=COLOR_FONDO)
        fila_ops.pack(pady=(5, 15))
        tk.Button(fila_ops, text="A × B", command=self._op_mult, **estilo_btn).grid(row=0, column=0, padx=6)
        tk.Button(fila_ops, text="A + B", command=self._op_suma, **estilo_btn).grid(row=0, column=1, padx=6)
        tk.Button(fila_ops, text="A - B", command=self._op_resta, **estilo_btn).grid(row=0, column=2, padx=6)

        # Resultado / Procedimiento
        fila_resultados = tk.Frame(centro, bg=COLOR_FONDO)
        fila_resultados.pack(pady=(0, 12))

        marco_proc = tk.LabelFrame(fila_resultados, text="Procedimiento",
                                   fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                   font=("Segoe UI", 10, "bold"))
        marco_proc.grid(row=0, column=0, padx=10, sticky="nsew")
        self.texto_proc = tk.Text(marco_proc, height=14, bg=COLOR_CAJA_BG, fg=COLOR_CAJA_FG)
        self.texto_proc.pack(fill="both", expand=True, padx=6, pady=6)

        marco_res = tk.LabelFrame(fila_resultados, text="Resultado",
                                  fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                  font=("Segoe UI", 10, "bold"))
        marco_res.grid(row=0, column=1, padx=10, sticky="nsew")
        self.texto_res = tk.Text(marco_res, height=14, bg=COLOR_CAJA_BG, fg=COLOR_CAJA_FG)
        self.texto_res.pack(fill="both", expand=True, padx=6, pady=6)

        fila_resultados.grid_columnconfigure(0, weight=1)
        fila_resultados.grid_columnconfigure(1, weight=1)

        self.btn_convertir = tk.Button(marco_res, text="Mostrar en decimales",
                                       command=self._convertir_a_decimales, **estilo_btn)
        self.btn_encadenar = tk.Button(marco_res, text="Encadenar Resultado",
                                       command=self._usar_resultado_en_A, **estilo_btn)

        tk.Button(centro, text="Limpiar todo", command=self._limpiar_todo, **estilo_btn)\
            .pack(pady=(6, 12))

        barra_inf = tk.Frame(raiz, bg=COLOR_FONDO)
        barra_inf.pack(fill="x", side="bottom", pady=(0, 8))
        tk.Button(barra_inf, text="← Volver al menú",
                  command=self._volver_al_menu, **estilo_btn).pack(side="left")

    # ---------- Cambio de modo ----------
    def _cambiar_modo(self):
        self.modo_vector = not self.modo_vector
        if self.modo_vector:
            self.btn_modo.config(text="Cambiar a modo Matrices")
            self.marco_A.config(text="Vector A")
            self.marco_B.config(text="Vector B")
            self.filas_A = self.filas_B = 1
            self.columnas_A = self.columnas_B = 3
        else:
            self.btn_modo.config(text="Cambiar a modo Vectores")
            self.marco_A.config(text="Matriz A")
            self.marco_B.config(text="Matriz B")
            self.filas_A = self.columnas_A = 3
            self.filas_B = self.columnas_B = 3
        self._generar_matriz("A")
        self._generar_matriz("B")
        self._limpiar_resultados()

    # ---------- Generación / Lectura ----------
    def _crear_entry(self, parent) -> tk.Entry:
        e = tk.Entry(parent, width=5, justify="center",
                     bg=COLOR_CAJA_BG, fg=COLOR_CAJA_FG,
                     relief="solid")
        return e

    def _generar_matriz(self, cual):
        if self.modo_vector:
            contenedor, filas, cols = (
                (self.contenedor_A, 1, self.columnas_A) if cual == "A"
                else (self.contenedor_B, 1, self.columnas_B)
            )
        else:
            contenedor, filas, cols = (
                (self.contenedor_A, self.filas_A, self.columnas_A) if cual == "A"
                else (self.contenedor_B, self.filas_B, self.columnas_B)
            )

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
        return limpiar_matriz(self.matriz_A if cual == "A" else self.matriz_B)

    def _leer_vector(self, cual):
        matriz = self.matriz_A if cual == "A" else self.matriz_B
        if not matriz or not matriz[0]:
            return []
        return [c.get() for c in matriz[0]]

    # ---------- Ajuste de tamaño ----------
    def _ajustar_matriz(self, cual, delta):
        if self.modo_vector:
            # Solo columnas
            if cual == "A":
                old_cols = self.columnas_A
                old_vals = [e.get() for e in self.matriz_A[0]]
                self.columnas_A = max(1, old_cols + delta)
                self._generar_matriz("A")
                for j in range(min(old_cols, self.columnas_A)):
                    self.matriz_A[0][j].insert(0, old_vals[j])
            else:
                old_cols = self.columnas_B
                old_vals = [e.get() for e in self.matriz_B[0]]
                self.columnas_B = max(1, old_cols + delta)
                self._generar_matriz("B")
                for j in range(min(old_cols, self.columnas_B)):
                    self.matriz_B[0][j].insert(0, old_vals[j])
        else:
            # Afecta filas y columnas simultáneamente
            if cual == "A":
                old_f, old_c = self.filas_A, self.columnas_A
                old_vals = [[e.get() for e in fila] for fila in self.matriz_A]
                self.filas_A = max(1, old_f + delta)
                self.columnas_A = max(1, old_c + delta)
                self._generar_matriz("A")
                for i in range(min(old_f, self.filas_A)):
                    for j in range(min(old_c, self.columnas_A)):
                        self.matriz_A[i][j].insert(0, old_vals[i][j])
            else:
                old_f, old_c = self.filas_B, self.columnas_B
                old_vals = [[e.get() for e in fila] for fila in self.matriz_B]
                self.filas_B = max(1, old_f + delta)
                self.columnas_B = max(1, old_c + delta)
                self._generar_matriz("B")
                for i in range(min(old_f, self.filas_B)):
                    for j in range(min(old_c, self.columnas_B)):
                        self.matriz_B[i][j].insert(0, old_vals[i][j])

    # ---------- Operaciones ----------
    def _op_suma(self):
        if self.modo_vector:
            A, B = self._leer_vector("A"), self._leer_vector("B")
            if len(A) != len(B):
                self._mostrar_error("Para sumar: Los vectores deben tener el mismo tamaño.")
                return
            res = opv.sumar_vectores_con_pasos(A, B)
        else:
            A, B = self._leer_matriz("A"), self._leer_matriz("B")
            if not A or not B or len(A) != len(B) or len(A[0]) != len(B[0]):
                self._mostrar_error("Para sumar: A y B deben tener el mismo tamaño.")
                return
            res = opm.sumar_con_pasos(A, B)
        self._mostrar_desde_core(res)

    def _op_resta(self):
        if self.modo_vector:
            A, B = self._leer_vector("A"), self._leer_vector("B")
            if len(A) != len(B):
                self._mostrar_error("Para restar: Los vectores deben tener el mismo tamaño.")
                return
            res = opv.restar_vectores_con_pasos(A, B)
        else:
            A, B = self._leer_matriz("A"), self._leer_matriz("B")
            if not A or not B or len(A) != len(B) or len(A[0]) != len(B[0]):
                self._mostrar_error("Para restar: A y B deben tener el mismo tamaño.")
                return
            res = opm.restar_con_pasos(A, B)
        self._mostrar_desde_core(res)

    def _op_mult(self):
        if self.modo_vector:
            A, B = self._leer_vector("A"), self._leer_vector("B")
            if len(A) != len(B):
                self._mostrar_error("Para producto escalar: Los vectores deben tener el mismo tamaño.")
                return
            res = opv.producto_escalar_con_pasos(A, B)
        else:
            A, B = self._leer_matriz("A"), self._leer_matriz("B")
            if not A or not B or len(A[0]) != len(B):
                self._mostrar_error("Para multiplicar: columnas de A = filas de B.")
                return
            res = opm.multiplicar_con_pasos(A, B)
        self._mostrar_desde_core(res)

    # ---------- Mostrar resultados ----------
    def _mostrar_desde_core(self, resultado):
        self._limpiar_resultados()
        if "error" in resultado:
            self._mostrar_error(resultado["error"])
            return

        self.texto_proc.insert("end", resultado["procedimiento"] + "\n")

        self.resultado = resultado["resultado_lista"]
        self.resultado_str = resultado["resultado_frac"]
        self.resultado_dec = resultado["resultado_dec"]
        self.mostrando_decimales = False

        self.texto_res.insert("end", self.resultado_str)

        tiene_fracciones = False
        if self.modo_vector:
            # Vector o escalar
            if isinstance(self.resultado, list):
                for v in self.resultado:
                    if hasattr(v, "denominator") and v.denominator != 1:
                        tiene_fracciones = True
                        break
            else:
                if hasattr(self.resultado, "denominator") and self.resultado.denominator != 1:
                    tiene_fracciones = True
        else:
            for fila in self.resultado:
                for v in fila:
                    if hasattr(v, "denominator") and v.denominator != 1:
                        tiene_fracciones = True
                        break

        if tiene_fracciones:
            self.btn_convertir.config(text="Mostrar en decimales")
            self.btn_convertir.pack(pady=(4, 4))
        self.btn_encadenar.pack(pady=(0, 4))

    def _convertir_a_decimales(self):
        if not self.resultado:
            return
        self.texto_res.delete("1.0", "end")
        if self.mostrando_decimales:
            self.texto_res.insert("end", self.resultado_str)
            self.btn_convertir.config(text="Mostrar en decimales")
            self.mostrando_decimales = False
        else:
            self.texto_res.insert("end", self.resultado_dec)
            self.btn_convertir.config(text="Mostrar en fracciones")
            self.mostrando_decimales = True

    # ---------- Encadenar ----------
    def _usar_resultado_en_A(self):
        if self.resultado is None:
            return
        if self.modo_vector:
            if isinstance(self.resultado, list):
                self.columnas_A = len(self.resultado)
                self._generar_matriz("A")
                for j, val in enumerate(self.resultado):
                    self.matriz_A[0][j].insert(0, fraccion_a_str(val))
            else:
                # Escalar (producto escalar), colocar en primera casilla
                self.columnas_A = 1
                self._generar_matriz("A")
                self.matriz_A[0][0].insert(0, str(self.resultado))
        else:
            # Matriz
            filas = len(self.resultado)
            cols = len(self.resultado[0]) if filas else 0
            self.filas_A = filas
            self.columnas_A = cols
            self._generar_matriz("A")
            for i in range(filas):
                for j in range(cols):
                    self.matriz_A[i][j].insert(0, fraccion_a_str(self.resultado[i][j]))

    # ---------- Utilidades ----------
    def _limpiar_matriz(self, cual):
        target = self.matriz_A if cual == "A" else self.matriz_B
        for fila in target:
            for e in fila:
                e.delete(0, "end")

    def _intercambiar(self):
        """Intercambia contenido y dimensiones entre A y B (robusto)."""
        if self.modo_vector:
            # Leer valores actuales (sin limpiar)
            A_vals = [e.get() for e in self.matriz_A[0]] if self.matriz_A else []
            B_vals = [e.get() for e in self.matriz_B[0]] if self.matriz_B else []

            # Nuevas dimensiones = largo del otro (mínimo 1)
            new_cols_A = max(1, len(B_vals)) if B_vals else max(1, self.columnas_A)
            new_cols_B = max(1, len(A_vals)) if A_vals else max(1, self.columnas_B)

            self.columnas_A = new_cols_A
            self.columnas_B = new_cols_B

            self._generar_matriz("A")
            self._generar_matriz("B")

            # Rellenar (A recibe B, B recibe A)
            for j, v in enumerate(B_vals[:self.columnas_A]):
                self.matriz_A[0][j].insert(0, v)
            for j, v in enumerate(A_vals[:self.columnas_B]):
                self.matriz_B[0][j].insert(0, v)
        else:
            # Leer valores actuales directamente de los Entry (sin limpiar)
            A_vals = [[e.get() for e in fila] for fila in self.matriz_A]
            B_vals = [[e.get() for e in fila] for fila in self.matriz_B]

            # Dimensiones nuevas (si listas vacías, mantener actuales)
            new_fA = len(B_vals) if B_vals else self.filas_A
            new_cA = len(B_vals[0]) if B_vals and B_vals[0] else self.columnas_A
            new_fB = len(A_vals) if A_vals else self.filas_B
            new_cB = len(A_vals[0]) if A_vals and A_vals[0] else self.columnas_B

            new_fA = max(1, new_fA); new_cA = max(1, new_cA)
            new_fB = max(1, new_fB); new_cB = max(1, new_cB)

            self.filas_A, self.columnas_A = new_fA, new_cA
            self.filas_B, self.columnas_B = new_fB, new_cB

            self._generar_matriz("A")
            self._generar_matriz("B")

            # Rellenar (A recibe antes B)
            for i in range(min(len(B_vals), new_fA)):
                for j in range(min(len(B_vals[i]), new_cA)):
                    self.matriz_A[i][j].insert(0, B_vals[i][j])

            # B recibe antes A
            for i in range(min(len(A_vals), new_fB)):
                for j in range(min(len(A_vals[i]), new_cB)):
                    self.matriz_B[i][j].insert(0, A_vals[i][j])

    def _restablecer_matrices(self):
        if self.modo_vector:
            self.filas_A = self.filas_B = 1
            self.columnas_A = self.columnas_B = 3
        else:
            self.filas_A = self.columnas_A = 3
            self.filas_B = self.columnas_B = 3
        self._generar_matriz("A")
        self._generar_matriz("B")
        self._limpiar_resultados()

    def _limpiar_resultados(self):
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        self.btn_convertir.pack_forget()
        self.btn_encadenar.pack_forget()
        self.resultado = None
        self.resultado_str = ""
        self.resultado_dec = ""
        self.mostrando_decimales = False

    def _limpiar_todo(self):
        self._limpiar_matriz("A")
        self._limpiar_matriz("B")
        self._limpiar_resultados()

    # ---------- Mensajes ----------
    def _mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)

    # ---------- Navegación ----------
    def _cerrar_toda_la_app(self):
        self.destroy()

    def _volver_al_menu(self):
        if self._on_volver:
            self._on_volver()
        self.destroy()
