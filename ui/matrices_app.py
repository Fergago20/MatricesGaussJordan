# ui/matrices_app.py
import tkinter as tk
from soporte import preparar_ventana
from soporte import (
    preparar_ventana, a_fraccion,
    patron_valido_para_coeficiente, matriz_alineada_con_titulo
)
from core.lector_matriz import limpiar_matriz
from core import operaciones_matrices as opm
from tkinter import messagebox

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

        # Tamaño inicial de matrices (3x3 por defecto)
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

        raiz = tk.Frame(self, bg=COLOR_FONDO)
        raiz.pack(fill="both", expand=True)

        # ==== Inputs para definir tamaño de matrices ====
        marco_tamano = tk.LabelFrame(raiz, text="Tamaños de matrices",
                                     fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                     font=("Segoe UI", 10, "bold"))
        marco_tamano.pack(pady=10)

        tk.Label(marco_tamano, text="Filas A:", bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=0, column=0, padx=4, pady=2)
        self.ent_filas_A = tk.Entry(marco_tamano, width=4, justify="center")
        self.ent_filas_A.insert(0, str(self.filas_A))
        self.ent_filas_A.grid(row=0, column=1, padx=4, pady=2)

        tk.Label(marco_tamano, text="Columnas A:", bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=0, column=2, padx=4, pady=2)
        self.ent_cols_A = tk.Entry(marco_tamano, width=4, justify="center")
        self.ent_cols_A.insert(0, str(self.columnas_A))
        self.ent_cols_A.grid(row=0, column=3, padx=4, pady=2)

        tk.Label(marco_tamano, text="Filas B:", bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=1, column=0, padx=4, pady=2)
        self.ent_filas_B = tk.Entry(marco_tamano, width=4, justify="center")
        self.ent_filas_B.insert(0, str(self.filas_B))
        self.ent_filas_B.grid(row=1, column=1, padx=4, pady=2)

        tk.Label(marco_tamano, text="Columnas B:", bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=1, column=2, padx=4, pady=2)
        self.ent_cols_B = tk.Entry(marco_tamano, width=4, justify="center")
        self.ent_cols_B.insert(0, str(self.columnas_B))
        self.ent_cols_B.grid(row=1, column=3, padx=4, pady=2)

        tk.Button(marco_tamano, text="Aplicar", command=self._aplicar_tamanos, **estilo_btn)\
            .grid(row=0, column=4, rowspan=2, padx=10)

        # ==== Contenedor principal ====
        centro = tk.Frame(raiz, bg=COLOR_FONDO)
        centro.pack(expand=True)

        fila_matrices = tk.Frame(centro, bg=COLOR_FONDO)
        fila_matrices.pack(pady=(20, 15))

        # Matriz A
        marco_A = tk.LabelFrame(fila_matrices, text="Matriz A",
                                fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                font=("Segoe UI", 10, "bold"))
        marco_A.grid(row=0, column=0, padx=20, sticky="n")
        self.contenedor_A = tk.Frame(marco_A, bg=COLOR_FONDO)
        self.contenedor_A.pack(pady=6)

        # Botón intercambiar
        tk.Button(fila_matrices, text="↔", command=self._intercambiar, **estilo_btn)\
            .grid(row=0, column=1, padx=10)

        # Matriz B
        marco_B = tk.LabelFrame(fila_matrices, text="Matriz B",
                                fg=COLOR_TEXTO, bg=COLOR_FONDO,
                                font=("Segoe UI", 10, "bold"))
        marco_B.grid(row=0, column=2, padx=20, sticky="n")
        self.contenedor_B = tk.Frame(marco_B, bg=COLOR_FONDO)
        self.contenedor_B.pack(pady=6)

        # Operaciones
        fila_ops = tk.Frame(centro, bg=COLOR_FONDO)
        fila_ops.pack(pady=(5, 15))
        tk.Button(fila_ops, text="A × B", command=self._op_mult, **estilo_btn).grid(row=0, column=0, padx=6)
        tk.Button(fila_ops, text="A + B", command=self._op_suma, **estilo_btn).grid(row=0, column=1, padx=6)
        tk.Button(fila_ops, text="A - B", command=self._op_resta, **estilo_btn).grid(row=0, column=2, padx=6)
        tk.Button(fila_ops, text="Limpiar", command=self._limpiar_todo, **estilo_btn).grid(row=0, column=3, padx=6)
        tk.Button(fila_ops, text="Encadenar", command=self._encadenar, **estilo_btn).grid(row=0, column=4, padx=6)

        # Procedimiento y resultado
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

        tk.Button(raiz, text="Volver al menú", command=self._volver_al_menu, **estilo_btn)\
            .pack(pady=(0, 10))
        
     # ---------- Ajuste de aplicar tamaños ----------
    def _aplicar_tamanos(self):
        try:
            fA, cA = int(self.ent_filas_A.get()), int(self.ent_cols_A.get())
            fB, cB = int(self.ent_filas_B.get()), int(self.ent_cols_B.get())
            if fA <= 0 or cA <= 0 or fB <= 0 or cB <= 0:
                raise ValueError
            self.filas_A, self.columnas_A, self.filas_B, self.columnas_B = fA, cA, fB, cB
        except ValueError:
            self._mostrar_error("Introduce solo números enteros positivos mayores que cero para los tamaños.")
            self._limpiar_todo()
            return
        self._generar_matriz("A")
        self._generar_matriz("B")

    #operatividad

    def _limpiar_todo(self):
        for matriz in (self.matriz_A, self.matriz_B):
            for fila in matriz:
                for e in fila:
                    e.delete(0, "end")
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        self.resultado = None

    def _encadenar(self):
        if not hasattr(self, "resultado") or self.resultado is None:
            self._mostrar_error("No hay resultado para encadenar.")
            return
        # Ajustar matriz A al tamaño del resultado
        self.filas_A = len(self.resultado)
        self.columnas_A = len(self.resultado[0]) if self.resultado else 1
        self._generar_matriz("A")
        # Copiar valores
        for i in range(self.filas_A):
            for j in range(self.columnas_A):
                self.matriz_A[i][j].insert(0, str(self.resultado[i][j]))
    
# ----------------- Operaciones -----------------

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
        if len(A[0]) != len(B):
            self._mostrar_error("Para multiplicar: columnas de A deben coincidir con filas de B.")
            return
        res = opm.multiplicar_con_pasos(A, B)
        self._mostrar_desde_core(res)

    # ----------------- Helpers (igual que antes) -----------------
    def _generar_matriz(self, cual):
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
        e = tk.Entry(parent, width=5, justify="center", bg=COLOR_CAJA_BG, fg=COLOR_CAJA_FG)
        vcmd = (e.register(patron_valido_para_coeficiente), "%P")
        e.config(validate="key", validatecommand=vcmd)
        e.insert(0, "")
        e.bind("<FocusIn>", lambda _ev: e.select_range(0, "end"))
        return e

    def _mostrar_error(self, mensaje):
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        messagebox.showwarning("Operación inválida", mensaje)

    def _mostrar_desde_core(self, resultado):
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        if "error" in resultado:
            self._mostrar_error(resultado["error"])
            return
        self.texto_proc.insert("end", resultado["procedimiento"] + "\n")
        self.resultado = resultado["resultado_lista"]
        self.texto_res.insert("end", "Resultado:\n\n" + resultado["resultado_frac"])

    def _intercambiar(self):
        valores_A = self._leer_matriz("A")
        valores_B = self._leer_matriz("B")
        filas_A, cols_A = self.filas_A, self.columnas_A
        filas_B, cols_B = self.filas_B, self.columnas_B
        self.filas_A, self.columnas_A = filas_B, cols_B
        self.filas_B, self.columnas_B = filas_A, cols_A
        self._generar_matriz("A")
        self._generar_matriz("B")
        for i in range(min(self.filas_A, len(valores_B))):
            for j in range(min(self.columnas_A, len(valores_B[0]))):
                self.matriz_A[i][j].insert(0, str(valores_B[i][j]))
        for i in range(min(self.filas_B, len(valores_A))):
            for j in range(min(self.columnas_B, len(valores_A[0]))):
                self.matriz_B[i][j].insert(0, str(valores_A[i][j]))

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
