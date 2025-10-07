"""
GUI para verificar independencia lineal usando reglas básicas.
- Sin librerías externas (solo tkinter de la librería estándar).
- Paleta de colores tomada de ui/estilos.py (si existe). Si no existe, usa valores por defecto.
- El usuario ingresa dimensión (entradas por vector) y número de vectores; luego rellena los componentes.
- Botón "Verificar" ejecuta las reglas y muestra explicación clara.
"""

# ==========================
# Importes y tema de colores
# ==========================
import tkinter as tk
from tkinter import ttk, messagebox
from core.solucion_dependencia import analizar_conjunto, TOL
from soporte.helpers import preparar_ventana
from ui import estilos


# ==========================

class AppVectores(tk.Toplevel):
    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(master=toplevel_parent)
        self.title("Independencia Lineal • Verificador")
        self.configure(bg=estilos.GAUSS_FONDO)
        self.geometry("900x650")
        preparar_ventana(self, usar_maximizada=True)
        self.minsize(820, 560)
        self._on_volver = on_volver
        self._configurar_estilos()
        self._construir_layout()
        self.protocol("WM_DELETE_WINDOW", self._cerrar_toda_la_app)

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
    # ----------------- UI helpers -----------------
    def _configurar_estilos(self):
        style = ttk.Style(self)
        # Usar tema "clam" para mejor control de colores
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TLabel", background=estilos.GAUSS_FONDO, foreground=estilos.GAUSS_TEXTO, font=estilos.FUENTE_GENERAL)
        style.configure("Titulo.TLabel", font=estilos.FUENTE_TITULO, foreground=estilos.GAUSS_TEXTO)
        style.configure("Sub.TLabel", font=estilos.FUENTE_SUBTITULO, foreground=estilos.GAUSS_TEXTO)
        style.configure("Card.TFrame", background=estilos.CARD_BG, borderwidth=1, relief="solid")
        style.configure("TButton", background=estilos.GAUSS_BTN_BG, foreground=estilos.GAUSS_BTN_FG, font=estilos.FUENTE_BOTON)
        style.map("TButton", background=[("active", estilos.GAUSS_BTN_BG_ACT)])
        style.configure("TEntry", fieldbackground=estilos.GAUSS_CAJA_BG, foreground=estilos.GAUSS_CAJA_FG, bordercolor=estilos.BORDE)

    def _construir_layout(self):
        # Header
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=24, pady=(18, 10))
        ttk.Label(header, text="Verificador de Independencia Lineal", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(header, text="Ingrese dimensión y cantidad de vectores; luego complete los componentes.", style="Sub.TLabel").pack(anchor="w", pady=(4,0))

        # Panel de parámetros (dimensión y número de vectores)
        params = ttk.Frame(self, style="Card.TFrame")
        params.pack(fill="x", padx=24, pady=8)
        for w in (params,):
            w.configure(padding=14)

        ttk.Label(params, text="Entradas por vector (dimensión):").grid(row=0, column=0, sticky="w", padx=(0,8), pady=6)
        ttk.Label(params, text="Número de vectores:").grid(row=0, column=2, sticky="w", padx=(24,8), pady=6)

        # Validadores: solo enteros positivos
        vcmd_int = (self.register(self._validar_entero_positivo), "%P")
        self.ent_dim = ttk.Entry(params, validate="key", validatecommand=vcmd_int, width=10)
        self.ent_n = ttk.Entry(params, validate="key", validatecommand=vcmd_int, width=10)
        self.ent_dim.grid(row=0, column=1, sticky="w")
        self.ent_n.grid(row=0, column=3, sticky="w")

        self.btn_generar = ttk.Button(params, text="Generar tabla", command=self._generar_tabla)
        self.btn_generar.grid(row=0, column=4, padx=(24,0))

        # Contenedor para la matriz de entradas con scrollbar
        tabla_card = ttk.Frame(self, style="Card.TFrame")
        tabla_card.pack(fill="both", expand=True, padx=24, pady=8)
        tabla_card.configure(padding=14)

        self.canvas = tk.Canvas(tabla_card, bg=estilos.GAUSS_CAJA_BG, highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(tabla_card, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(tabla_card, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.frame_matriz = ttk.Frame(self.canvas, style="TFrame")
        self.frame_matriz_id = self.canvas.create_window((0,0), window=self.frame_matriz, anchor="nw")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.frame_matriz.bind("<Configure>", self._on_frame_configure)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        tabla_card.rowconfigure(0, weight=1)
        tabla_card.columnconfigure(0, weight=1)

        # Barra de acciones
        acciones = ttk.Frame(self, style="TFrame")
        acciones.pack(fill="x", padx=24, pady=(0,8))
        self.btn_verificar = ttk.Button(acciones, text="Verificar independencia", command=self._verificar, state="disabled")
        self.btn_limpiar = ttk.Button(acciones, text="Limpiar", command=self._limpiar_todo)
        self.btn_verificar.pack(side="left")
        self.btn_limpiar.pack(side="left", padx=(8,0))

        # Resultado
        self.card_result = ttk.Frame(self, style="Card.TFrame")
        self.card_result.pack(fill="x", padx=24, pady=(8,18))
        self.card_result.configure(padding=14)
        self.lbl_resultado = ttk.Label(self.card_result, text="Resultado aparecerá aquí.")
        self.lbl_resultado.pack(anchor="w", pady=(0,8))
        self.txt_explicacion = tk.Text(self.card_result, height=6, bg=estilos.GAUSS_CAJA_BG, fg=estilos.GAUSS_CAJA_FG, relief="flat", wrap="word")
        self.txt_explicacion.pack(fill="x")
        self.txt_explicacion.configure(state="disabled")

        # Datos
        self.entradas = []  # matriz de Entry
        # Botón para volver al menú principal
        acciones_inf = ttk.Frame(self, style="TFrame")
        acciones_inf.pack(fill="x", padx=24, pady=(0, 8))
        btn_volver = ttk.Button(acciones_inf, text="← Volver al menú", command=self._volver_al_menu)
        btn_volver.pack(side="left")

    # -------- Validación de entradas --------
    def _validar_entero_positivo(self, nuevo_texto):
        if nuevo_texto == "":
            return True
        if not nuevo_texto.isdigit():
            return False
        try:
            val = int(nuevo_texto)
        except ValueError:
            return False
        return val > 0

    def _validar_numero_real(self, texto):
        # Acepta flotantes con signo y punto decimal; rechaza letras
        try:
            float(texto)
            return True
        except ValueError:
            return False

    # -------- Generación de tabla --------
    def _generar_tabla(self):
        dim_txt = self.ent_dim.get().strip()
        n_txt = self.ent_n.get().strip()
        if not dim_txt or not n_txt:
            messagebox.showwarning("Datos incompletos", "Ingrese dimensión y número de vectores.")
            return
        dim = int(dim_txt)
        n = int(n_txt)
        if dim <= 0 or n <= 0:
            messagebox.showerror("Valores inválidos", "Los valores deben ser enteros positivos.")
            return

        # Limpiar matriz anterior
        for fila in self.frame_matriz.winfo_children():
            fila.destroy()
        self.entradas.clear()

        # Encabezados
        ttk.Label(self.frame_matriz, text="Componente ", style="Sub.TLabel").grid(row=0, column=0, padx=6, pady=6)
        for j in range(n):
            ttk.Label(self.frame_matriz, text=f"v{j+1}", style="Sub.TLabel").grid(row=0, column=j+1, padx=6, pady=6)

        # Celdas
        vcmd_num = (self.register(self._validar_numero_real), "%P")
        for i in range(dim):
            ttk.Label(self.frame_matriz, text=f"x{i+1}").grid(row=i+1, column=0, padx=6, pady=4, sticky="e")
            fila_entries = []
            for j in range(n):
                e = ttk.Entry(self.frame_matriz, width=10, validate="focusout", validatecommand=vcmd_num)
                e.grid(row=i+1, column=j+1, padx=4, pady=4)
                e.insert(0, "0")
                fila_entries.append(e)
            self.entradas.append(fila_entries)

        self.btn_verificar.configure(state="normal")
        self._ajustar_scroll()

    # -------- Scroll behavior --------
    def _on_canvas_configure(self, event):
        # Ajustar el ancho del frame interno al canvas visible
        self.canvas.itemconfig(self.frame_matriz_id, width=event.width)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_scroll(self):
        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # -------- Acciones --------
    def _leer_vectores(self):
        if not self.entradas:
            return []
        dim = len(self.entradas)
        n = len(self.entradas[0])
        # Construir por columnas (vectores v_j con dim componentes)
        vectores = []
        for j in range(n):
            v = []
            for i in range(dim):
                txt = self.entradas[i][j].get().strip()
                if txt == "":
                    messagebox.showwarning("Campo vacío", f"Componente x{i+1} de v{j+1} está vacío.")
                    return None
                try:
                    val = float(txt)
                except ValueError:
                    messagebox.showerror("Dato inválido", f"x{i+1} de v{j+1} no es número válido.")
                    return None
                v.append(val)
            vectores.append(v)
        return vectores

    def _verificar(self):
        vectores = self._leer_vectores()
        if vectores is None:
            return
        if len({len(v) for v in vectores}) != 1:
            messagebox.showerror("Dimensiones inconsistentes", "Todos los vectores deben tener la misma dimensión.")
            return
        resultado = analizar_conjunto(vectores)
        self._mostrar_resultado(resultado)

    def _mostrar_resultado(self, r):
        self.txt_explicacion.configure(state="normal")
        self.txt_explicacion.delete("1.0", "end")
        # Cabecera
        if "error" in r:
            self.lbl_resultado.configure(text="Error en los datos", foreground="red")
            self.txt_explicacion.insert("end", r["error"])
        else:
            if r.get("independiente", False):
                self.lbl_resultado.configure(text="Conjunto INDEPENDIENTE", foreground="#0B6E4F")
            else:
                self.lbl_resultado.configure(text="Conjunto DEPENDIENTE", foreground="#B00020")

            # Explicación amigable
            regla = r.get("regla")
            detalle = r.get("detalle", {})
            explicacion = self._explicar_regla(regla, detalle)
            self.txt_explicacion.insert("end", explicacion)
        self.txt_explicacion.configure(state="disabled")

    def _explicar_regla(self, regla, detalle):
        if regla == "vector_cero":
            return (
                "Regla aplicada: Vector cero.\n"
                "Un conjunto que contiene al menos un vector nulo es necesariamente dependiente, \n"
                "porque ese vector es combinación lineal trivial de los demás."
            )
        if regla == "multiplo_de_otro":
            i, j = detalle.get("indices", (None, None))
            return (
                "Regla aplicada: Múltiplos escalares.\n"
                f"Se detectó que v{i+1} es múltiplo escalar de v{j+1} (o viceversa), lo que genera dependencia."
            )
        if regla == "mas_vectores_que_entradas":
            return (
                "Regla aplicada: Más vectores que entradas.\n"
                "Si hay más vectores que la dimensión del espacio (n > dim), entonces son dependientes."
            )
        if regla == "combinacion_lineal":
            idx = detalle.get("indice_objetivo")
            return (
                "Regla aplicada: Uno es combinación lineal de los otros.\n"
                f"Se encontró que v{idx+1} puede escribirse como combinación lineal de los demás, por lo tanto hay dependencia."
            )
        if regla == "solo_solucion_trivial":
            return (
                "Regla aplicada: Solo solución trivial.\n"
                "El sistema homogéneo A·c = 0 solo admite la solución c = 0, por lo que los vectores son independientes."
            )
        if regla == "no_trivial_detectado_por_rango":
            return (
                "Se detectó una solución no trivial en el sistema homogéneo (por rango), indicando dependencia."
            )
        return "No se pudo determinar una explicación específica."

    def _limpiar_todo(self):
        self.ent_dim.delete(0, "end")
        self.ent_n.delete(0, "end")
        for w in self.frame_matriz.winfo_children():
            w.destroy()
        self.entradas.clear()
        self.btn_verificar.configure(state="disabled")
        self.lbl_resultado.configure(text="Resultado aparecerá aquí.")
        self.txt_explicacion.configure(state="normal")
        self.txt_explicacion.delete("1.0", "end")
        self.txt_explicacion.configure(state="disabled")
        self._ajustar_scroll()