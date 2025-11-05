import tkinter as tk
import sympy as sp
from tkinter import messagebox, ttk  # Añadido ttk para Treeview
import customtkinter as ctk  # Añadido para compatibilidad con el teclado
from core.biserccion import calcular_biseccion as metodo_biseccion
from core.grafica import inicio_grafica as graficar_funcion

# Copia de la clase CalculadoraCientificaFrame del segundo código (para integrarla directamente)
import re
from sympy import symbols, pi, E

x = symbols('x')  # Definir símbolo para la expresión

class CalculadoraCientificaFrame(ctk.CTkFrame):
    def __init__(self, parent, parent_textbox):
        super().__init__(parent)
        self.parent_textbox = parent_textbox
        self.expresion = ""
        self.modo_superindice = False  # Modo superíndice

        self.frame_superior = ctk.CTkFrame(self)
        self.frame_superior.pack(expand=True, padx=10, pady=5, fill='x')

        self.frame_inferior = ctk.CTkFrame(self)
        self.frame_inferior.pack(fill="x", expand=True, padx=10, pady=5)

        self.frame_derecho = ctk.CTkFrame(self.frame_inferior)
        self.frame_derecho.pack(side="right", fill="y", expand=True, padx=5, pady=5)

        self.frame_izquierdo = ctk.CTkFrame(self.frame_inferior)
        self.frame_izquierdo.pack(side="left", fill="y", expand=True, padx=5, pady=5)

        self.categorias = {
            "Trigonometría": ['sen', 'cos', 'tan', 'sec'],
            "Funciones": ['ln', 'log', '√'],  # Quité 'log2'
            "Exponenciales": ['^2', '^3', 'x^x', '(', ')', 'pi', 'e']
        }

        self.categoria_var = ctk.StringVar(value="Exponenciales")
        self.menu_desplegable = ctk.CTkOptionMenu(self.frame_superior, variable=self.categoria_var,
                                                  values=list(self.categorias.keys()),
                                                  command=self.mostrar_botones_categoria, width=200, font=("Times New Roman", 15))
        self.menu_desplegable.pack(fill="x", padx=2, pady=2, side="left")

        self.categoria_botones_frame = ctk.CTkFrame(self.frame_izquierdo)
        self.categoria_botones_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.mostrar_botones_categoria(self.categoria_var.get())

        self.crear_botones_numericos()
        self.crear_botones_aritmeticos()
        self.crear_boton_limpiar()

        # Vincular eventos de teclado
        self.parent_textbox.bind("<Key>", self.procesar_tecla)
        self.parent_textbox.bind("<Shift_L>", self.activar_superindice)
        self.parent_textbox.bind("<KeyRelease-Shift_L>", self.desactivar_superindice)

        # Vincular las flechas del teclado
        self.parent_textbox.bind("<Left>", self.mover_caret_izquierda)
        self.parent_textbox.bind("<Right>", self.mover_caret_derecha)

    def activar_superindice(self, event):
        """Activar modo superíndice cuando se presiona Shift."""
        self.modo_superindice = True

    def desactivar_superindice(self, event):
        """Desactivar modo superíndice al soltar Shift."""
        self.modo_superindice = False

    def mover_caret_izquierda(self, event):
        """Mover el cursor hacia la izquierda."""
        pos_actual = self.parent_textbox.index("insert")
        nueva_pos = max(0, int(pos_actual) - 1)
        self.parent_textbox.icursor(nueva_pos)
        return "break"

    def mover_caret_derecha(self, event):
        """Mover el cursor hacia la derecha."""
        pos_actual = self.parent_textbox.index("insert")
        nueva_pos = min(len(self.parent_textbox.get()), int(pos_actual) + 1)
        self.parent_textbox.icursor(nueva_pos)
        return "break"

    def procesar_tecla(self, event):
        """Procesar entrada del teclado."""
        tecla = event.keysym  # Usar keysym para detectar teclas como Backspace
        caret_pos = self.parent_textbox.index("insert")  # Posición actual del cursor

        if tecla == "BackSpace":
            if int(caret_pos) > 0:  # Asegurarse de no borrar fuera de los límites
                expresion_actual = self.parent_textbox.get()
                # Borrar el carácter antes del cursor
                nueva_expresion = expresion_actual[:int(caret_pos) - 1] + expresion_actual[int(caret_pos):]
                self.parent_textbox.delete(0, "end")
                self.parent_textbox.insert(0, nueva_expresion)
                # Ajustar la posición del cursor después de borrar
                self.parent_textbox.icursor(int(caret_pos) - 1)
            return "break"  # Evitar que se ejecute el comportamiento predeterminado

        elif self.modo_superindice and event.char.isdigit():
            # Convertir el dígito a superíndice
            superindices = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
                            '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', 'x': 'ˣ'}
            texto_superindice = superindices.get(event.char, event.char)
            self.parent_textbox.insert("insert", texto_superindice)
            return "break"  # Evitar que la tecla normal se agregue
        elif self.modo_superindice and event.char in ('x', 'X'):
            texto_superindice = 'ˣ'
            self.parent_textbox.insert("insert", texto_superindice)
            return "break"  # Evitar que la tecla normal se agregue

        elif event.char in ('+', '-', '*', '/', '.', 'x', '(', ')'):
            # Permitir caracteres especiales
            return

        elif event.char.isdigit():
            # Permitir números si no está en modo superíndice
            return

        else:
            # Bloquear cualquier otra entrada
            return "break"

    def mostrar_botones_categoria(self, nombre_categoria):
        for widget in self.categoria_botones_frame.winfo_children():
            widget.destroy()

        botones = self.categorias[nombre_categoria]
        for idx, texto in enumerate(botones):
            boton = ctk.CTkButton(self.categoria_botones_frame, text=texto,
                                  command=lambda t=texto: self.al_presionar_boton(t))
            boton.grid(row=idx // 3, column=idx % 3, padx=2, pady=2, sticky="nsew")

    def crear_botones_numericos(self):
        for i in range(1, 10):
            boton = ctk.CTkButton(self.frame_derecho, text=str(i),
                                  command=lambda t=str(i): self.al_presionar_boton(t))
            boton.grid(row=(i - 1) // 3, column=(i - 1) % 3, sticky="nsew", padx=2, pady=2)
        boton_cero = ctk.CTkButton(self.frame_derecho, text="0", command=lambda: self.al_presionar_boton("0"))
        boton_cero.grid(row=3, column=0, sticky="nsew", padx=2, pady=2)
        boton_punto = ctk.CTkButton(self.frame_derecho, text=".", command=lambda: self.al_presionar_boton("."))
        boton_punto.grid(row=3, column=2, sticky="nsew", padx=2, pady=2)
        boton_coma = ctk.CTkButton(self.frame_derecho, text=",", command=lambda: self.al_presionar_boton(","))
        boton_coma.grid(row=4, column=2, sticky="nsew", padx=2, pady=2)
        boton_x = ctk.CTkButton(self.frame_derecho, text="x", command=lambda: self.al_presionar_boton("x"))
        boton_x.grid(row=3, column=1, sticky="nsew", padx=2, pady=2)

    def crear_botones_aritmeticos(self):
        operaciones = ['+', '-', '*', '/']
        for i, op in enumerate(operaciones):
            boton = ctk.CTkButton(self.frame_derecho, text=op, command=lambda t=op: self.al_presionar_boton(t))
            boton.grid(row=i, column=3, sticky="nsew", padx=2, pady=2)

    def crear_boton_limpiar(self):
        boton_limpiar = ctk.CTkButton(self.frame_derecho, text="C", command=lambda: self.al_presionar_boton("C"))
        boton_limpiar.grid(row=4, column=1, sticky="nsew", padx=2, pady=2)
        boton_borrar = ctk.CTkButton(self.frame_derecho, text="Borrar", command=lambda: self.al_presionar_boton("Borrar"))
        boton_borrar.grid(row=4, column=0, padx=2, pady=2)

    def mostrar_logaritmo_con_base(self, ecuacion_str):
        """Convierte logaritmos de la forma log{base}(x) en log{base}ₓ(x)"""
        # Reemplaza cualquier logaritmo log{base}(x) por log{base}ₓ(x) con la base en subíndice
        ecuacion_str = re.sub(r'log\((\d+)\)\(([^)]+)\)', r'log\1ₓ\2', ecuacion_str)
        return ecuacion_str

    def al_presionar_boton(self, texto_boton):
        """Maneja la lógica al presionar un botón."""
        # Obtiene la posición actual del caret (cursor)
        caret_pos = self.parent_textbox.index("insert")
        expresion_actual = self.parent_textbox.get()

        if texto_boton == 'C':
            self.expresion = expresion_actual[:int(caret_pos) - 1] + expresion_actual[int(caret_pos):]
        elif texto_boton == 'Borrar':
            self.expresion = ""
        elif texto_boton == '^2':
            self.expresion = expresion_actual[:int(caret_pos)] + '²' + expresion_actual[int(caret_pos):]
        elif texto_boton == '^3':
            self.expresion = expresion_actual[:int(caret_pos)] + '³' + expresion_actual[int(caret_pos):]
        elif texto_boton == 'x^x':
            if not self.modo_superindice:
                self.modo_superindice = True
                self.expresion = expresion_actual 
            else:
                self.modo_superindice = False
        elif texto_boton in {'sen', 'cos', 'tan', 'ln', 'sec', 'log'}:
            self.expresion = expresion_actual[:int(caret_pos)] + f"{texto_boton}(" + expresion_actual[int(caret_pos):]
        elif texto_boton == 'pi':
            self.expresion = expresion_actual[:int(caret_pos)] + 'pi' + expresion_actual[int(caret_pos):]
        elif texto_boton == 'e':
            self.expresion = expresion_actual[:int(caret_pos)] + 'E' + expresion_actual[int(caret_pos):]
        elif texto_boton == '√':
            self.expresion = expresion_actual[:int(caret_pos)] + '√' + expresion_actual[int(caret_pos):]
        else:
            if self.modo_superindice and texto_boton.isdigit():
                # Mapea el número al superíndice Unicode si estamos en modo superíndice
                superindices = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
                                '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
                self.expresion = (expresion_actual[:int(caret_pos)] +
                                  superindices.get(texto_boton, texto_boton) +
                                  expresion_actual[int(caret_pos):])
            elif texto_boton == 'x' and self.modo_superindice:
                self.expresion = expresion_actual[:int(caret_pos)] + 'ˣ' + expresion_actual[int(caret_pos):]
            
            else:
                self.expresion = expresion_actual[:int(caret_pos)] + texto_boton + expresion_actual[int(caret_pos):]
         # Desactiva el modo superíndice después de insertar

        # Actualiza el contenido del textbox
        self.parent_textbox.delete(0, 'end')
        self.parent_textbox.insert(0, self.expresion)

        # Mueve el caret a la posición después del texto insertado
        nueva_pos = int(caret_pos) + len(texto_boton)
        if texto_boton in {'^2', '^3', '²', '³', '√'}:  # Ajusta para caracteres especiales
            nueva_pos -= len(texto_boton) - 1
        self.parent_textbox.icursor(nueva_pos + 1)

    def procesar_shift(self, event):
        """Desactiva el modo superíndice al presionar Shift."""
        if event.keysym == "Shift_L" or event.keysym == "Shift_R":
            self.modo_superindice = False

    def obtener_funcion(self):
        """Obtiene la función ingresada y la procesa para su evaluación."""
        funcion = self.parent_textbox.get()
    

        # Reemplaza superíndices Unicode por '**' para interpretación en Python
        funcion_modificada = funcion.replace('²', '**2').replace('³', '**3') \
            .replace('⁴', '**4').replace('⁵', '**5') \
            .replace('⁶', '**6').replace('⁷', '**7') \
            .replace('⁸', '**8').replace('⁹', '**9') \
            .replace('⁰', '**0').replace('ˣ', '**x')

        # Reemplazar nombres de funciones y corregir instancias como 3x a 3*x
        funcion_modificada = funcion_modificada.replace('sen', 'sin').replace('√', 'sqrt').replace('^', '**')


        # Reemplazar 'log' para convertir a logaritmo natural con base e
        funcion_modificada = re.sub(r'log\((.*?)\)', r'log(\1)', funcion_modificada)

        # Añadir un operador * entre número y variable (por ejemplo, 3x -> 3*x)
        funcion_modificada = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', funcion_modificada)
        
        funcion_modificada = re.sub(r'log(\d+)\(([^)]+)\)', r'log(\2, \1)', funcion_modificada)

        return funcion_modificada

class AppMetodosNumericos(tk.Toplevel):
    """Interfaz para realizar el método de bisección de una ecuación."""

    def __init__(self, toplevel_parent=None, on_volver=None):
        super().__init__(master=toplevel_parent)
        self.title("Método de Bisección")
        self.geometry("800x600")
        self._on_volver = on_volver
        self.configure(bg="#EAF5FF")

        # Maximizar ventana al abrir
        self.state("zoomed")  # Maximiza la ventana al abrir

        # Inicializar variables
        self.entry_ecuacion = tk.StringVar()
        self.entry_tolerancia = tk.DoubleVar(value=0.0001)
        self.entry_intervalo_inferior = tk.DoubleVar(value=0.55)
        self.entry_intervalo_superior = tk.DoubleVar(value=1.1)

        self._construir_ui()

    def _construir_ui(self):
        # Estilo de los botones
        estilo_btn = {
            "bg": "#0E3A5B",
            "fg": "white",
            "activebackground": "#104467",
            "activeforeground": "white",
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
            "font": ("Segoe UI", 12, "bold"),
            "padx": 10,
            "pady": 8,
        }

        raiz = tk.Frame(self, bg="#EAF5FF")
        raiz.pack(fill="both", expand=True, padx=10, pady=10)
        # Panel para ingresar ecuación
        panel_ecuacion = tk.Frame(raiz, bg="#EAF5FF")
        panel_ecuacion.pack(fill="x", padx=10, pady=10)
        tk.Label(panel_ecuacion, text="Ecuación:", font=("Segoe UI", 14), bg="#EAF5FF", fg="#0E3A5B").pack(side="left")
        # Cambiado a ctk.CTkEntry para compatibilidad con el teclado
        self.entry_ecuacion_widget = ctk.CTkEntry(panel_ecuacion, textvariable=self.entry_ecuacion, font=("Segoe UI", 14), width=400)
        self.entry_ecuacion_widget.pack(side="left", fill="x", expand=True)
        # Añadir el teclado de funciones aquí
        self.teclado_frame = CalculadoraCientificaFrame(raiz, self.entry_ecuacion_widget)
        self.teclado_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Panel para ingresar tolerancia
        panel_tolerancia = tk.Frame(raiz, bg="#EAF5FF")
        panel_tolerancia.pack(fill="x", padx=10, pady=10)
        tk.Label(panel_tolerancia, text="Tolerancia:", font=("Segoe UI", 14), bg="#EAF5FF", fg="#0E3A5B").pack(side="left")
        tk.Entry(panel_tolerancia, textvariable=self.entry_tolerancia, font=("Segoe UI", 14), width=10).pack(side="left", padx=10)
        # Panel para ingresar los intervalos

        panel_intervalos = tk.Frame(raiz, bg="#EAF5FF")
        panel_intervalos.pack(fill="x", padx=10, pady=10)
        tk.Label(panel_intervalos, text="Intervalo Inferior (a):", font=("Segoe UI", 12), bg="#EAF5FF", fg="#0E3A5B").pack(side="left")
        tk.Entry(panel_intervalos, textvariable=self.entry_intervalo_inferior, font=("Segoe UI", 12), width=10).pack(side="left", padx=10)
        tk.Label(panel_intervalos, text="Intervalo Superior (b):", font=("Segoe UI", 12), bg="#EAF5FF", fg="#0E3A5B").pack(side="left")
        tk.Entry(panel_intervalos, textvariable=self.entry_intervalo_superior, font=("Segoe UI", 12), width=10).pack(side="left", padx=10)
        # Panel para mostrar las iteraciones (nuevo: grid con Treeview)
        panel_iteraciones = tk.Frame(raiz, bg="#EAF5FF")
        panel_iteraciones.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(panel_iteraciones, text="Iteraciones del Método de Bisección:", font=("Segoe UI", 14), bg="#EAF5FF", fg="#0E3A5B").pack(anchor="w", pady=5)
        # Crear Treeview para la tabla
        columnas = ("Iteración", "a", "b", "c", "f(a)", "f(b)", "f(c)")
        self.tree = ttk.Treeview(panel_iteraciones, columns=columnas, show="headings", height=10)
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        # Scrollbar vertical para la tabla

        scrollbar = ttk.Scrollbar(panel_iteraciones, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        #Boton para graficar la función
         # Botón para graficar la función (opcional, si lo quieres)
        # Frame para botones alineados horizontalmente
        frame_botones = tk.Frame(raiz, bg="#EAF5FF")
        frame_botones.pack(fill="x", padx=10, pady=10)

        boton_graficar = tk.Button(frame_botones, text="Graficar Función",
                       command=lambda: graficar_funcion(self.teclado_frame.obtener_funcion()),
                       **estilo_btn)
        boton_calcular = tk.Button(frame_botones, text="Calcular Bisección",
                       command=self.calcular_biseccion,
                       **estilo_btn)
        self.boton_volver = tk.Button(frame_botones, text="← Volver al menú",
                          command=self._volver_al_menu,
                          **estilo_btn)
        self.boton_cerrar = tk.Button(frame_botones, text="Cerrar Aplicación",
                          command=self._cerrar_toda_la_app,
                          **estilo_btn)

        # Empaquetar horizontalmente y permitir que se expandan para ocupar el ancho disponible
        for b in (boton_graficar, boton_calcular, self.boton_volver, self.boton_cerrar):
            b.pack(side="left", padx=8, pady=6, expand=True, fill="x")


    def _volver_al_menu(self):
        """Vuelve a la ventana anterior y cierra la ventana actual"""
        try:
            self.destroy()
        finally:
            if callable(self._on_volver):
                self._on_volver()
    
    def _cerrar_toda_la_app(self):
        """Cerrar la aplicación completamente"""
        raiz = self.master
        if isinstance(raiz, tk.Tk):
            raiz.destroy()

    def calcular_biseccion(self):
        """Calcula la raíz con el método de bisección y muestra el resultado y las iteraciones"""
        # Limpiar la tabla antes de calcular
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener la ecuación procesada desde el teclado
        ecuacion = self.teclado_frame.obtener_funcion()
        tolerancia = float(self.entry_tolerancia.get())
        intervalo_inferior = float(self.entry_intervalo_inferior.get())
        intervalo_superior = float(self.entry_intervalo_superior.get())

        try:
            # Llamada al método de bisección
            resultado, iteraciones, resultados = metodo_biseccion(ecuacion, intervalo_inferior, intervalo_superior, tolerancia)
            
            # Mostrar el resultado final en un messagebox
            messagebox.showinfo("Resultado", f"La raíz encontrada es: {resultado}\nIteraciones: {iteraciones}")
            
            # Poblar la tabla con las iteraciones
            for fila in resultados:
                self.tree.insert("", "end", values=fila)

        except Exception as e:
            messagebox.showerror("Error", f"Hubo un error: {e}")
