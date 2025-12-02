# ui/ayuda_entrada.py

import customtkinter as ctk
import tkinter as tk

# Importa tus colores y fuentes
from ui.estilos import (
    GAUSS_FONDO, GAUSS_TEXTO,
    GAUSS_BTN_BG, GAUSS_BTN_FG, GAUSS_BTN_BG_ACT,
    FUENTE_BOLD, FUENTE_GENERAL
)

TEXTO_AYUDA = """
Guía para ingresar ecuaciones:

1. Variable principal:
   - Solo se usa la variable: x

2. Funciones soportadas:
   Trigonométricas:
   - sen(x), cos(x), tan(x)
   Alias: sen(x), tg(x)

   Logaritmos:
   - ln(x)                 → log natural
   - log(x)                → log base 10
   - log(x, b)             → log base b

   Raíces:
   - sqrt(x)               → raíz cuadrada
   - cbrt(x)               → raíz cúbica real
   - root(a, n)            → raíz n-ésima real

3. Potencias:
   - x^2          → x**2
   - x^3          → x**3
   - x^1/3        → x**(1/3)
   - x^-2         → x**(-2)
   - x^-1/2       → x**(-1/2)

4. Multiplicación implícita:
   Se acepta, pero se convierte internamente:
   - 2x        → 2*x
   - (x+1)(x-1)→ (x+1)*(x-1)
   - 3sqrt(x)  → 3*sqrt(x)

5. Constantes:
   - pi  → 3.141592...
   - e/E → 2.718281...

6. Notas importantes:
   - Usa punto decimal: 2.5
   - Revisa que todos los paréntesis estén cerrados
   - Toda ecuación debe ser una expresión real continua (sin “=0”)

7. Dominios que debes respetar:
   - El método avisará si la función se vuelve compleja en algún punto

8. Ejemplos válidos:
   - sin(x) + x^2 - 3
   - ln(x) - sqrt(x)
   - x^1/3 + 2*x - 5
   - (x+1)(x-1)(x-2)
   - log(x, 3) + root(x, 4)
"""


class VentanaAyudaEntrada(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ─────────────────────────────────────
        #  CONFIGURACIÓN DE LA VENTANA
        # ─────────────────────────────────────
        self.title("Guía de ingreso de ecuaciones")
        self.geometry("550x520")
        self.resizable(False, True)
        self.configure(fg_color=GAUSS_FONDO)

        # Centrar ventana
        self.after(10, self.centrar_ventana)

        # ─────────────────────────────────────
        #  TÍTULO
        # ─────────────────────────────────────
        titulo = ctk.CTkLabel(
            self,
            text="Guía para ingresar ecuaciones",
            font=("Segoe UI", 20, "bold"),
            text_color=GAUSS_TEXTO
        )
        titulo.pack(pady=(15, 10))

        # ─────────────────────────────────────
        #  CUADRO DE TEXTO CON SCROLL
        # ─────────────────────────────────────
        contenedor = ctk.CTkFrame(self, fg_color=GAUSS_FONDO)
        contenedor.pack(fill="both", expand=True, padx=10, pady=10)

        cuadro = ctk.CTkTextbox(
            contenedor,
            width=520,
            height=420,
            fg_color="#FFFFFF",
            text_color="#000000",
            font=("Consolas", 13),
            wrap="word"
        )
        cuadro.pack(fill="both", expand=True)
        cuadro.insert("1.0", TEXTO_AYUDA)
        cuadro.configure(state="disabled")

        # ─────────────────────────────────────
        #  BOTÓN CERRAR
        # ─────────────────────────────────────
        boton = ctk.CTkButton(
            self,
            text="Cerrar",
            command=self.destroy,
            fg_color=GAUSS_BTN_BG,
            text_color=GAUSS_BTN_FG,
            hover_color=GAUSS_BTN_BG_ACT,
            font=FUENTE_BOLD,
            width=90
        )
        boton.pack(pady=10)

    # ─────────────────────────────────────
    #  MÉTODO PARA CENTRAR LA VENTANA
    # ─────────────────────────────────────
    def centrar_ventana(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        x = (sw - w) // 2
        y = (sh - h) // 2 - 20

        self.geometry(f"{w}x{h}+{x}+{y}")