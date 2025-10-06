# ui/matrices_app.py
import tkinter as tk
from soporte.validaciones import limpiar_matriz, matriz_esta_vacia
from core import operaciones_matrices as opm
from ui.estilos import (
    GAUSS_FONDO as MAT_FONDO,
    GAUSS_TEXTO as MAT_TEXTO,
    GAUSS_CAJA_BG as MAT_CAJA_BG,
    GAUSS_CAJA_FG as MAT_CAJA_FG,
    GAUSS_BTN_BG as MAT_BTN_BG,
    GAUSS_BTN_FG as MAT_BTN_FG,
    GAUSS_BTN_BG_ACT as MAT_BTN_BG_ACT,
    FUENTE_BOLD
)
from soporte.base_app import BaseApp


class AppMatrices(BaseApp):
    """Ventana para operaciones con matrices — rediseñada al estilo Gauss/Gauss-Jordan."""

    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(toplevel_parent, on_volver, titulo="Operaciones con Matrices")
        self.configure(bg=MAT_FONDO)

        # Estado inicial
        self.matriz_A = []
        self.matriz_B = []
        self.resultado = None

        # Tamaños por defecto
        self.filas_A = self.columnas_A = 3
        self.filas_B = self.columnas_B = 3

        self._construir_ui()
        self._generar_matriz("A")
        self._generar_matriz("B")

    # --------------------------------------------------------
    # Construcción de interfaz
    # --------------------------------------------------------
    def _construir_ui(self):
        estilo_btn = {
            "bg": MAT_BTN_BG, "fg": MAT_BTN_FG,
            "activebackground": MAT_BTN_BG_ACT, "activeforeground": MAT_BTN_FG,
            "relief": "raised", "bd": 2, "cursor": "hand2",
            "font": FUENTE_BOLD, "padx": 8, "pady": 4
        }

        raiz = tk.Frame(self, bg=MAT_FONDO)
        raiz.pack(fill="both", expand=True)
        raiz.grid_columnconfigure(0, weight=0)
        raiz.grid_columnconfigure(1, weight=1)
        raiz.grid_rowconfigure(0, weight=1)
        raiz.grid_rowconfigure(1, weight=0)
        raiz.grid_rowconfigure(2, weight=0)

        # ==== Panel izquierdo (Matrices) ====
        panel_izq = tk.Frame(raiz, bg=MAT_FONDO)
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(10, 6), pady=(8, 6))
        panel_izq.grid_columnconfigure(0, weight=1)

        # --- Tamaños de matrices en esquina superior izquierda ---
        marco_tamano = tk.LabelFrame(
            panel_izq, text="Tamaño de matrices",
            fg=MAT_TEXTO, bg=MAT_FONDO, font=FUENTE_BOLD
        )
        marco_tamano.grid(row=0, column=0, sticky="w", pady=(0, 8))
        self._crear_input_tamano(marco_tamano, "A")
        self._crear_input_tamano(marco_tamano, "B")
        tk.Button(marco_tamano, text="Aplicar", command=self._aplicar_tamanos, **estilo_btn)\
            .grid(row=0, column=4, rowspan=2, padx=10)

        # --- Matrices y botón intercambiar ---
        fila_matrices = tk.Frame(panel_izq, bg=MAT_FONDO)
        fila_matrices.grid(row=1, column=0, sticky="nsew", pady=(10, 6))
        fila_matrices.grid_columnconfigure(0, weight=1)
        fila_matrices.grid_columnconfigure(2, weight=1)

        self._crear_marco_matriz(fila_matrices, "A", 0)

        # Botón ↔ centrado perfectamente
        contenedor_interc = tk.Frame(fila_matrices, bg=MAT_FONDO)
        contenedor_interc.grid(row=0, column=1, sticky="ns", padx=10)
        contenedor_interc.grid_rowconfigure(0, weight=1)
        tk.Button(contenedor_interc, text="↔", command=self._intercambiar, **estilo_btn)\
            .grid(row=0, column=0, pady="40")

        self._crear_marco_matriz(fila_matrices, "B", 2)

        # --- Botones de operaciones en columna ---
        fila_ops = tk.Frame(panel_izq, bg=MAT_FONDO)
        fila_ops.grid(row=3, column=0, pady=(10, 10))
        botones_ops = [
            ("A + B", self._op_suma),
            ("A - B", self._op_resta),
            ("A × B", self._op_mult),
            ("Limpiar todo", self._limpiar_todo),
        ]
        for i, (txt, cmd) in enumerate(botones_ops):
            tk.Button(fila_ops, text=txt, command=cmd, **estilo_btn)\
                .grid(row=i, column=0, pady=4)

        # ==== Panel derecho (Procedimiento / Resultado) ====
        panel_der = tk.Frame(raiz, bg=MAT_FONDO)
        panel_der.grid(row=0, column=1, rowspan=1, sticky="nsew", padx=(6, 10), pady=(8, 6))
        panel_der.grid_columnconfigure(0, weight=1)
        panel_der.grid_rowconfigure(0, weight=1)
        panel_der.grid_rowconfigure(1, weight=0)

        # Procedimiento (más alto)
        self.marco_proc = tk.LabelFrame(
            panel_der, text="Procedimiento",
            fg=MAT_TEXTO, bg=MAT_FONDO, font=FUENTE_BOLD
        )
        self.marco_proc.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        self.texto_proc = tk.Text(self.marco_proc, bg=MAT_CAJA_BG, fg=MAT_CAJA_FG, height=14)
        self.texto_proc.pack(fill="both", expand=True, padx=6, pady=6)

        # Resultado (más pequeño)
        self.marco_res = tk.LabelFrame(
            panel_der, text="Resultado",
            fg=MAT_TEXTO, bg=MAT_FONDO, font=FUENTE_BOLD
        )
        self.marco_res.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        self.texto_res = tk.Text(self.marco_res, bg=MAT_CAJA_BG, fg=MAT_CAJA_FG, height=8)
        self.texto_res.pack(fill="x", padx=6, pady=6)

        # ==== Barra inferior ====
        barra_inf = tk.Frame(raiz, bg=MAT_FONDO)
        barra_inf.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        tk.Button(barra_inf, text="← Volver al menú", command=self._volver_al_menu, **estilo_btn)\
            .pack(side="left")

    # --------------------------------------------------------
    # Subcomponentes
    # --------------------------------------------------------
    def _crear_input_tamano(self, parent, etiqueta):
        fila = 0 if etiqueta == "A" else 1
        tk.Label(parent, text=f"Filas {etiqueta}:", bg=MAT_FONDO, fg=MAT_TEXTO)\
            .grid(row=fila, column=0, padx=4, pady=2)

        # Variable vinculada con valor inicial 3
        var_filas = tk.IntVar(value=3)
        ent_filas = tk.Spinbox(
            parent,
            from_=1,
            to=10,  # límite superior
            width=4,
            justify="center",
            bg=MAT_CAJA_BG,
            fg=MAT_CAJA_FG,
            wrap=True,
            textvariable=var_filas,  # <-- valor inicial
            state="readonly",
        )
        ent_filas.grid(row=fila, column=1, padx=4, pady=2)

        tk.Label(parent, text=f"Columnas {etiqueta}:", bg=MAT_FONDO, fg=MAT_TEXTO)\
            .grid(row=fila, column=2, padx=4, pady=2)

        # Variable vinculada con valor inicial 3
        var_cols = tk.IntVar(value=3)
        ent_cols = tk.Spinbox(
            parent,
            from_=1,
            to=10,
            width=4,
            justify="center",
            bg=MAT_CAJA_BG,
            fg=MAT_CAJA_FG,
            wrap=True,
            textvariable=var_cols,  # <-- valor inicial
            state="readonly",
        )
        ent_cols.grid(row=fila, column=3, padx=4, pady=2)

        # Validación adicional (aunque en readonly no se escribe texto)
        vcmd = (parent.register(lambda val: val.isdigit() and 1 <= int(val) <= 10 if val else True), "%P")
        ent_filas.config(validate="key", validatecommand=vcmd)
        ent_cols.config(validate="key", validatecommand=vcmd)

        if etiqueta == "A":
            self.ent_filas_A, self.ent_cols_A = ent_filas, ent_cols
        else:
            self.ent_filas_B, self.ent_cols_B = ent_filas, ent_cols


    def _crear_marco_matriz(self, parent, etiqueta, col):
        marco = tk.LabelFrame(
            parent, text=f"Matriz {etiqueta}",
            fg=MAT_TEXTO, bg=MAT_FONDO, font=FUENTE_BOLD
        )
        marco.grid(row=0, column=col, padx=20, pady=(10, 4), sticky="n")
        contenedor = tk.Frame(marco, bg=MAT_FONDO)
        contenedor.pack(pady=6)
        btn = tk.Button(marco, text="Limpiar", command=lambda: self._limpiar_matriz(etiqueta),
                        bg=MAT_BTN_BG, fg=MAT_BTN_FG,
                        activebackground=MAT_BTN_BG_ACT, activeforeground=MAT_BTN_FG,
                        font=FUENTE_BOLD, padx=8, pady=4)
        btn.pack(pady=4)
        if etiqueta == "A": self.contenedor_A = contenedor
        else: self.contenedor_B = contenedor

    def _crear_area_texto(self, parent, titulo, fila):
        marco = tk.LabelFrame(parent, text=titulo,
                              fg=MAT_TEXTO, bg=MAT_FONDO, font=FUENTE_BOLD)
        marco.grid(row=fila, column=0, padx=10, pady=6, sticky="nsew")
        txt = tk.Text(marco, height=12, bg=MAT_CAJA_BG, fg=MAT_CAJA_FG)
        txt.pack(fill="both", expand=True, padx=6, pady=6)
        return txt

    # --------------------------------------------------------
    # Lógica principal
    # --------------------------------------------------------
    def _aplicar_tamanos(self):
        try:
            fA, cA = int(self.ent_filas_A.get()), int(self.ent_cols_A.get())
            fB, cB = int(self.ent_filas_B.get()), int(self.ent_cols_B.get())
            if any(n <= 0 for n in (fA, cA, fB, cB)):
                raise ValueError
        except ValueError:
            self._mostrar_error("Introduce números enteros positivos para los tamaños.")
            self._limpiar_todo()
            return
        self.filas_A, self.columnas_A, self.filas_B, self.columnas_B = fA, cA, fB, cB
        self._generar_matriz("A")
        self._generar_matriz("B")

    def _generar_matriz(self, cual):
        """
        Genera o ajusta la matriz indicada ('A' o 'B') sin perder datos previos.
        Si se aumenta el tamaño, las nuevas celdas quedan vacías.
        Si se reduce, se recorta la matriz y se eliminan solo las filas/columnas sobrantes.
        """
        if cual == "A":
            contenedor, filas, cols = self.contenedor_A, self.filas_A, self.columnas_A
            matriz_actual = getattr(self, "matriz_A", [])
        else:
            contenedor, filas, cols = self.contenedor_B, self.filas_B, self.columnas_B
            matriz_actual = getattr(self, "matriz_B", [])

        # Leer valores actuales (si existen)
        valores_previos = []
        for fila in matriz_actual:
            fila_vals = []
            for e in fila:
                fila_vals.append(e.get().strip())
            valores_previos.append(fila_vals)

        # Destruir solo lo necesario y regenerar la cuadrícula
        for w in contenedor.winfo_children():
            w.destroy()

        nueva_matriz = []
        for i in range(filas):
            fila = []
            for j in range(cols):
                e = self._crear_entry_coef(contenedor)
                e.grid(row=i, column=j, padx=2, pady=2)

                # Recuperar el valor previo si existe
                if i < len(valores_previos) and j < len(valores_previos[i]):
                    valor = valores_previos[i][j]
                    e.delete(0, "end")
                    e.insert(0, valor)

                fila.append(e)
            nueva_matriz.append(fila)

        # Guardar referencia actualizada
        if cual == "A":
            self.matriz_A = nueva_matriz
        else:
            self.matriz_B = nueva_matriz


    def _leer_matriz(self, cual):
        return limpiar_matriz(self.matriz_A if cual == "A" else self.matriz_B)

    # --------------------------------------------------------
    # Operaciones
    # --------------------------------------------------------
    def _op_suma(self):
        if matriz_esta_vacia(self.matriz_A) or matriz_esta_vacia(self.matriz_B):
            self._mostrar_error("Por favor, llena al menos una celda en ambas matrices antes de operar.")
            return
        A, B = self._leer_matriz("A"), self._leer_matriz("B")
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            self._mostrar_error("Para sumar: A y B deben tener el mismo tamaño.")
            return
        self._mostrar_desde_core(opm.sumar_con_pasos(A, B))

    def _op_resta(self):
        if matriz_esta_vacia(self.matriz_A) or matriz_esta_vacia(self.matriz_B):
            self._mostrar_error("Por favor, llena al menos una celda en ambas matrices antes de operar.")
            return
        A, B = self._leer_matriz("A"), self._leer_matriz("B")
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            self._mostrar_error("Para restar: A y B deben tener el mismo tamaño.")
            return
        self._mostrar_desde_core(opm.restar_con_pasos(A, B))

    def _op_mult(self):
        if matriz_esta_vacia(self.matriz_A) or matriz_esta_vacia(self.matriz_B):
            self._mostrar_error("Por favor, llena al menos una celda en ambas matrices antes de operar.")
            return
        A, B = self._leer_matriz("A"), self._leer_matriz("B")
        if len(A[0]) != len(B):
            self._mostrar_error("Para multiplicar: columnas de A deben coincidir con filas de B.")
            return
        self._mostrar_desde_core(opm.multiplicar_con_pasos(A, B))

    def _mostrar_desde_core(self, resultado):
        from soporte.validaciones import hay_fracciones_en_lista

        # Limpiar áreas de texto
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")

        # Ocultar botón de decimales si existe
        if hasattr(self, "btn_decimales"):
            self.btn_decimales.pack_forget()

        if "error" in resultado:
            self._mostrar_error(resultado["error"])
            return

        # Mostrar procedimiento y resultado
        self.texto_proc.insert("end", resultado["procedimiento"] + "\n")
        self.texto_res.insert("end", resultado["resultado_frac"])
        self.resultado = resultado["resultado_lista"]

        # ======================================================
        #  BOTONES DENTRO DEL MARCO DE RESULTADO
        # ======================================================
        # Crear contenedor si no existe
        if not hasattr(self, "frame_botones_res"):
            self.frame_botones_res = tk.Frame(self.marco_res, bg=MAT_FONDO)
            self.frame_botones_res.pack(fill="x", pady=(6, 4))

            estilo_btn = {
                "bg": MAT_BTN_BG, "fg": MAT_BTN_FG,
                "activebackground": MAT_BTN_BG_ACT, "activeforeground": MAT_BTN_FG,
                "relief": "raised", "bd": 2, "cursor": "hand2",
                "font": FUENTE_BOLD, "padx": 8, "pady": 4
            }

            # Botón Encadenar (se crea UNA sola vez)
            self.btn_encadenar = tk.Button(
                self.frame_botones_res, text="Encadenar", command=self._encadenar, **estilo_btn
            )
            self.btn_encadenar.pack(side="left", padx=(6, 4))

            # Botón Decimales (se crea una vez, pero puede mostrarse/ocultarse)
            self.btn_decimales = tk.Button(
                self.frame_botones_res, text="Decimales", command=self._toggle_decimales, **estilo_btn
            )

        # Asegurar que el botón “Encadenar” siempre esté visible
        if not self.btn_encadenar.winfo_ismapped():
            self.btn_encadenar.pack(side="left", padx=(6, 4))

        # Mostrar “Decimales” solo si hay fracciones verdaderas
        if any(hay_fracciones_en_lista(fila) for fila in resultado["resultado_lista"]):
            self.btn_decimales.config(text="Decimales")
            if not self.btn_decimales.winfo_ismapped():
                self.btn_decimales.pack(side="left", padx=4)
        else:
            self.btn_decimales.pack_forget()

    # ---------- Alternar entre fracciones y decimales ----------
    def _toggle_decimales(self):
        """Alterna la visualización entre fracciones y decimales."""
        texto = self.btn_decimales.cget("text")
        if texto == "Decimales":
            self.texto_res.delete("1.0", "end")
            self.texto_res.insert("end", "Resultado (decimales):\n\n")
            from soporte.formato_matrices import resultado_en_decimales
            self.texto_res.insert("end", resultado_en_decimales(self.resultado))
            self.btn_decimales.config(text="Fracciones")
        else:
            self.texto_res.delete("1.0", "end")
            self.texto_res.insert("end", "Resultado (fracciones):\n\n")
            from soporte.formato_matrices import resultado_en_fracciones
            self.texto_res.insert("end", resultado_en_fracciones(self.resultado))
            self.btn_decimales.config(text="Decimales")


    # --------------------------------------------------------
    # Funciones de utilidad
    # --------------------------------------------------------
    def _convertir_a_decimales(self):
        if not self.resultado:
            return
        self.texto_res.delete("1.0", "end")
        self.texto_res.insert("end", "Resultado (decimales):\n\n")
        for fila in self.resultado:
            self.texto_res.insert("end", " ".join(f"{float(x):.4f}" for x in fila) + "\n")

    def _encadenar(self):
        """
        Copia el resultado actual a la matriz A.
        Si la matriz A ya tiene datos, se limpia completamente antes de pegar.
        Soporta tanto resultados en fracciones como en decimales.
        """
        if not self.resultado:
            self._mostrar_error("No hay resultado para encadenar.")
            return

        # Determinar si el resultado está en modo decimal (según texto del botón)
        modo_decimal = (
            hasattr(self, "btn_decimales") and self.btn_decimales.winfo_ismapped() and
            self.btn_decimales.cget("text") == "Fracciones"
        )

        # Actualizar dimensiones de matriz A
        self.filas_A = len(self.resultado)
        self.columnas_A = len(self.resultado[0])
        self._generar_matriz("A")

        # Borrar todo contenido previo
        for fila in self.matriz_A:
            for e in fila:
                e.delete(0, "end")

        # Insertar los valores nuevos (decimales o fracciones)
        for i, fila in enumerate(self.resultado):
            for j, val in enumerate(fila):
                texto = str(float(val)) if modo_decimal else str(val)
                self.matriz_A[i][j].insert(0, texto)


    def _limpiar_matriz(self, cual):
        matriz = self.matriz_A if cual == "A" else self.matriz_B
        for fila in matriz:
            for e in fila:
                e.delete(0, "end")
    
        # ---------- Alternar vista de decimales / fracciones ----------
    def _toggle_decimales(self):
        """Alterna entre mostrar fracciones o decimales en el resultado."""
        if not self.resultado:
            return

        texto_actual = self.btn_decimales.cget("text")
        self.texto_res.delete("1.0", "end")

        if texto_actual == "Decimales":
            # Mostrar en decimales (4 cifras)
            from soporte.formato_matrices import resultado_en_decimales
            self.texto_res.insert("end", "Resultado (decimales):\n\n")
            self.texto_res.insert("end", resultado_en_decimales(self.resultado, decimales=4))
            self.btn_decimales.config(text="Fracciones")
        else:
            # Mostrar en fracciones exactas
            from soporte.formato_matrices import resultado_en_fracciones
            self.texto_res.insert("end", "Resultado (fracciones):\n\n")
            self.texto_res.insert("end", resultado_en_fracciones(self.resultado))
            self.btn_decimales.config(text="Decimales")


    def _limpiar_todo(self):
        for m in (self.matriz_A, self.matriz_B):
            for fila in m:
                for e in fila:
                    e.delete(0, "end")
        self.texto_proc.delete("1.0", "end")
        self.texto_res.delete("1.0", "end")
        self.resultado = None
        self.btn_decimales.pack_forget()

    def _intercambiar(self):
        A, B = self._leer_matriz("A"), self._leer_matriz("B")
        self.filas_A, self.columnas_A, self.filas_B, self.columnas_B = len(B), len(B[0]), len(A), len(A[0])
        self._generar_matriz("A")
        self._generar_matriz("B")
        for i, fila in enumerate(B):
            for j, val in enumerate(fila):
                self.matriz_A[i][j].insert(0, str(val))
        for i, fila in enumerate(A):
            for j, val in enumerate(fila):
                self.matriz_B[i][j].insert(0, str(val))
