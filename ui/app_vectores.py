import tkinter as tk
from fractions import Fraction
from tkinter import ttk, messagebox
from soporte.helpers import preparar_ventana
from soporte.formato_vectores import formatear_combinacion_lineal
from core.solucion_dependencia import analizar_independencia
from soporte.formato_matrices import matriz_alineada_con_titulo
from core.gauss_jordan import clasificar_y_resolver_gauss_jordan
from ui.estilos import (
    GAUSS_FONDO,
    GAUSS_TEXTO,
    GAUSS_CAJA_BG,
    GAUSS_CAJA_FG,
    GAUSS_BTN_BG,
    GAUSS_BTN_FG,
    GAUSS_BTN_BG_ACT,
)

class AppIndependenciaLineal(tk.Toplevel):
    """Interfaz para analizar la independencia lineal de un conjunto de vectores."""

    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(master=toplevel_parent)
        self.title("Independencia Lineal")
        self.configure(bg=GAUSS_FONDO)
        preparar_ventana(self, usar_maximizada=True)

        self._on_volver = on_volver

        self.dimension = tk.IntVar(value=3)
        self.numero_vectores = tk.IntVar(value=3)
        self.entradas = []

        self._construir_ui()
        self._crear_tabla()

    # =====================================================
    #   CONSTRUCCIÓN DE INTERFAZ
    # =====================================================
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
            "padx": 8,
            "pady": 4,
        }

        raiz = tk.Frame(self, bg=GAUSS_FONDO)
        raiz.pack(fill="both", expand=True, padx=10, pady=10)
        raiz.grid_columnconfigure(0, weight=1, uniform="cols")
        raiz.grid_columnconfigure(1, weight=1, uniform="cols")
        raiz.grid_rowconfigure(0, weight=1)
        raiz.grid_rowconfigure(1, weight=1)

        # =====================================================
        #   PANEL IZQUIERDO
        # =====================================================
        panel_izq = tk.Frame(raiz, bg=GAUSS_FONDO)
        panel_izq.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8))
        panel_izq.grid_rowconfigure(1, weight=1)
        panel_izq.grid_rowconfigure(3, weight=1)

        # --- PARÁMETROS DEL CONJUNTO ---
        marco_param = tk.LabelFrame(
            panel_izq,
            text="Parámetros del conjunto",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        )
        marco_param.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        marco_param.grid_columnconfigure(5, weight=1)

        tk.Label(marco_param, text="Dimensión:", bg=GAUSS_FONDO, fg=GAUSS_TEXTO).grid(row=0, column=0, padx=(8, 4))
        tk.Spinbox(marco_param, from_=1, to=10, textvariable=self.dimension,
                   width=5, justify="right", state="readonly",
                   bg=GAUSS_CAJA_BG, fg=GAUSS_CAJA_FG).grid(row=0, column=1, padx=(0, 12))

        tk.Label(marco_param, text="Número de vectores:", bg=GAUSS_FONDO, fg=GAUSS_TEXTO).grid(row=0, column=2)
        tk.Spinbox(marco_param, from_=1, to=10, textvariable=self.numero_vectores,
                   width=5, justify="right", state="readonly",
                   bg=GAUSS_CAJA_BG, fg=GAUSS_CAJA_FG).grid(row=0, column=3, padx=(0, 12))

        tk.Button(marco_param, text="Generar tabla", command=self._crear_tabla, **estilo_btn).grid(row=0, column=4)

        # --- TABLA DE VECTORES ---
        marco_tabla = tk.LabelFrame(
            panel_izq,
            text="Componentes de los vectores",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        )
        marco_tabla.grid(row=1, column=0, sticky="nsew")
        self.frame_tabla = tk.Frame(marco_tabla, bg=GAUSS_FONDO)
        self.frame_tabla.pack(fill="x", pady=4)

        # --- BOTONES ---
        fila_botones = tk.Frame(panel_izq, bg=GAUSS_FONDO)
        fila_botones.grid(row=2, column=0, sticky="ew", pady=(8, 8))
        tk.Button(fila_botones, text="Verificar independencia", command=self._verificar_independencia, **estilo_btn).grid(row=0, column=0, padx=4)
        tk.Button(fila_botones, text="Ver proceso Gauss-Jordan", command=self._ver_proceso_gauss, **estilo_btn).grid(row=0, column=1, padx=4)
        tk.Button(fila_botones, text="Limpiar", command=self._limpiar_todo, **estilo_btn).grid(row=0, column=2, padx=4)

        # --- RESULTADO / RAZONAMIENTO ---
        marco_resultado = tk.LabelFrame(
            panel_izq,
            text="Resolución",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        )
        marco_resultado.grid(row=3, column=0, sticky="nsew", pady=(0, 6))
        self.texto_resultado = tk.Text(marco_resultado, bg=GAUSS_CAJA_BG, fg=GAUSS_CAJA_FG, height=10)
        self.texto_resultado.pack(fill="both", expand=True, padx=6, pady=6)

        # --- BOTÓN VOLVER ---
        barra_inf = tk.Frame(panel_izq, bg=GAUSS_FONDO)
        barra_inf.grid(row=4, column=0, sticky="ew", pady=(4, 0))
        tk.Button(barra_inf, text="← Volver al menú", command=self._volver_al_menu, **estilo_btn).pack(side="left", padx=6, pady=4)

        # =====================================================
        #   PANEL DERECHO
        # =====================================================
        panel_der = tk.Frame(raiz, bg=GAUSS_FONDO)
        panel_der.grid(row=0, column=1, rowspan=2, sticky="nsew")
        panel_der.grid_rowconfigure(0, weight=1)
        panel_der.grid_rowconfigure(1, weight=1)

        # --- COMBINACIÓN LINEAL ---
        self.marco_comb = tk.LabelFrame(
            panel_der,
            text="Combinación lineal y sistema homogéneo",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        )
        self.marco_comb.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=(0, 6))
        self.texto_combinacion = tk.Text(self.marco_comb, bg=GAUSS_CAJA_BG, fg=GAUSS_CAJA_FG)
        self.texto_combinacion.pack(fill="both", expand=True, padx=6, pady=6)

        # --- PROCEDIMIENTO ---
        self.marco_proc = tk.LabelFrame(
            panel_der,
            text="Procedimiento",
            fg=GAUSS_TEXTO,
            bg=GAUSS_FONDO,
            font=("Segoe UI", 10, "bold"),
        )
        self.marco_proc.grid(row=1, column=0, sticky="nsew", padx=(0, 4))
        self.texto_procedimiento = tk.Text(self.marco_proc, bg=GAUSS_CAJA_BG, fg=GAUSS_CAJA_FG)
        self.texto_procedimiento.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Ocultar ambos al inicio
        self.marco_comb.grid_remove()
        self.marco_proc.grid_remove()

    # =====================================================
    #   FUNCIONALIDAD
    # =====================================================
    def _crear_tabla(self):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        self.entradas.clear()

        filas = self.dimension.get()
        columnas = self.numero_vectores.get()

        tk.Label(self.frame_tabla, text="Componente", bg=GAUSS_FONDO, fg=GAUSS_TEXTO,
                font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=4)
        for j in range(columnas):
            tk.Label(self.frame_tabla, text=f"v{j+1}", bg=GAUSS_FONDO, fg=GAUSS_TEXTO,
                    font=("Segoe UI", 10, "bold")).grid(row=0, column=j+1, padx=4)

        # === Validación de texto ===
        def validar_entrada(texto):
            if texto == "" or texto == "-":
                return True
            for ch in texto:
                if ch not in "0123456789/.-":
                    return False
            return True

        validacion = self.register(validar_entrada)

        # === Selección automática al enfocar ===
        def seleccionar_todo(event):
            event.widget.select_range(0, 'end')
            event.widget.icursor('end')
            return "break"

        for i in range(filas):
            tk.Label(self.frame_tabla, text=f"x{i+1}", bg=GAUSS_FONDO, fg=GAUSS_TEXTO).grid(row=i+1, column=0, padx=4)
            fila_entradas = []
            for j in range(columnas):
                e = tk.Entry(self.frame_tabla, width=7, justify="center",
                            bg=GAUSS_CAJA_BG, fg=GAUSS_CAJA_FG,
                            validate="key", validatecommand=(validacion, "%P"))
                e.grid(row=i+1, column=j+1, padx=3, pady=2)
                
                # 👇 nuevo: selección automática
                e.bind("<FocusIn>", seleccionar_todo)

                # Si hace clic con el mouse, esperar un poco y luego seleccionar todo
                e.bind("<ButtonRelease-1>", lambda event: event.widget.select_range(0, 'end'))

                fila_entradas.append(e)
            self.entradas.append(fila_entradas)

    def _leer_vectores(self):
        filas = len(self.entradas)
        columnas = len(self.entradas[0])
        vectores = []
        for j in range(columnas):
            v = []
            for i in range(filas):
                texto = self.entradas[i][j].get().strip()
                try:
                    if texto == "" or texto == "-":  # vacío o solo signo
                        valor = 0.0
                    elif "/" in texto:
                        valor = float(Fraction(texto))  # fracción
                    else:
                        valor = float(texto)  # decimal o entero
                except Exception:
                    valor = 0.0
                v.append(valor)
            vectores.append(v)
        return vectores


    def _verificar_independencia(self):
        self.texto_resultado.delete("1.0", "end")
        self.texto_combinacion.delete("1.0", "end")
        self.texto_procedimiento.delete("1.0", "end")

        vectores = self._leer_vectores()
        if not vectores:
            messagebox.showwarning("Aviso", "Debe ingresar los componentes de los vectores.")
            return

        resultado = analizar_independencia(vectores)
        salida = [
            f"Conclusión: Conjunto {'INDEPENDIENTE' if resultado['independiente'] else 'DEPENDIENTE'}",
            f"Razonamiento: {resultado.get('razonamiento', '')}",
        ]

        if resultado["independiente"]:
            salida.append("Criterio algebraico → No hay variables libres, solo la solución trivial (c = 0).")
        else:
            salida.append("Criterio algebraico → Hay variables libres, existen combinaciones no triviales (dependencia).")

        self.texto_resultado.insert("end", "\n".join(salida))

    def _ver_proceso_gauss(self):
        """Muestra todo el procedimiento algebraico:
        - Combinación lineal y sistema homogéneo
        - Matriz inicial (A|0)
        - Proceso Gauss–Jordan
        - Solución detallada
        - Análisis final
        """
        # Mostrar ambos paneles
        self.marco_comb.grid()
        self.marco_proc.grid()
        
        # Limpiar campos previos
        self.texto_combinacion.delete("1.0", "end")
        self.texto_procedimiento.delete("1.0", "end")

        # Leer vectores
        vectores = self._leer_vectores()
        if not vectores:
            messagebox.showwarning("Aviso", "Debe ingresar los componentes de los vectores.")
            return

        # =====================================================
        # COMBINACIÓN LINEAL Y SISTEMA HOMOGÉNEO
        # =====================================================
        bloque_combinacion = formatear_combinacion_lineal(vectores)
        self.texto_combinacion.insert("end", bloque_combinacion.strip() + "\n\n")

        # =====================================================
        # MATRIZ INICIAL (A|0)
        # =====================================================
        self.texto_procedimiento.insert("end", "MATRIZ INICIAL (A|0):\n")
        matriz = [list(map(Fraction, fila)) + [Fraction(0)] for fila in zip(*vectores)]
        self.texto_procedimiento.insert("end", matriz_alineada_con_titulo("", matriz, con_barra=True) + "\n")

        # =====================================================
        # PROCESO GAUSS–JORDAN
        # =====================================================
        self.texto_procedimiento.insert("end", "APLICANDO EL MÉTODO DE GAUSS–JORDAN:\n")
        resultado = clasificar_y_resolver_gauss_jordan(matriz)
        pasos = resultado["pasos"]
        self.texto_procedimiento.insert("end", "\n".join(pasos) + "\n")

        # =====================================================
        # SOLUCIÓN FINAL
        # =====================================================
        self.texto_procedimiento.insert("end", "\nSOLUCIÓN:\n")

        tipo = resultado["tipo_solucion"]
        soluciones = resultado.get("soluciones", [])
        parametricas = resultado.get("solucion_parametrica", [])

        # --- Caso inconsistente (teóricamente no debería darse en A·c=0)
        if tipo == "inconsistente":
            self.texto_procedimiento.insert(
                "end", "El sistema homogéneo es inconsistente (sin solución).\n"
            )

        # --- Caso solución única
        elif tipo == "única":
            self.texto_procedimiento.insert("end", "Solución única.\n\n")
            for i, val in enumerate(soluciones, start=1):
                self.texto_procedimiento.insert("end", f"x{i} = {val}\n")

        # --- Caso infinitas soluciones
        elif tipo == "infinita":
            self.texto_procedimiento.insert("end", "Infinitas soluciones.\n\n")
            for linea in parametricas:
                self.texto_procedimiento.insert("end", linea + "\n")

        # =====================================================
        # ANÁLISIS FINAL
        # =====================================================
        self.texto_procedimiento.insert("end", "\nANÁLISIS FINAL:\n")

        if tipo == "única":
            self.texto_procedimiento.insert(
                "end",
                "Criterio algebraico → No hay variables libres, el único vector que satisface A·c = 0 es el vector nulo.\n"
                "Por tanto, no existe combinación no trivial → independencia lineal confirmada.\n"
            )
        elif tipo == "infinita":
            self.texto_procedimiento.insert(
                "end",
                "Criterio algebraico → Hay variables libres, existen combinaciones no triviales.\n"
                "Por tanto, el conjunto de vectores es linealmente dependiente.\n"
            )

    def _limpiar_todo(self):
        """Limpia todos los campos y resultados, dejando los Entry vacíos."""
        # Limpiar áreas de texto
        self.texto_resultado.delete("1.0", "end")
        self.texto_combinacion.delete("1.0", "end")
        self.texto_procedimiento.delete("1.0", "end")
        
        # Ocultar los paneles derechos
        self.marco_comb.grid_remove()
        self.marco_proc.grid_remove()

        # Vaciar las entradas de la tabla
        for fila in self.entradas:
            for e in fila:
                e.delete(0, "end")  # quitamos la parte que insertaba '0'

    def _volver_al_menu(self):
        self.destroy()
        if callable(self._on_volver):
            self._on_volver()
    