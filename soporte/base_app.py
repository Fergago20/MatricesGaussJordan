import tkinter as tk
from tkinter import messagebox
from soporte.helpers import preparar_ventana
from soporte.validaciones import patron_valido_para_coeficiente

class BaseApp(tk.Toplevel):
    """Clase base reutilizable para las pantallas de la calculadora."""

    COLOR_CAJA_BG = "#FFFFFF"
    COLOR_CAJA_FG = "#000000"

    def __init__(self, toplevel_parent=None, on_volver=None, titulo="Ventana"):
        super().__init__(master=toplevel_parent)
        self._on_volver = on_volver
        self.title(titulo)
        preparar_ventana(self, usar_maximizada=True)
        self.protocol("WM_DELETE_WINDOW", self._cerrar_toda_la_app)

    # ------------------- Métodos comunes -------------------

    def _cerrar_toda_la_app(self):
        """Cierra toda la aplicación si la raíz es Tk."""
        raiz = self.master
        if isinstance(raiz, tk.Tk):
            raiz.destroy()

    def _volver_al_menu(self):
        """Cierra esta ventana y vuelve al menú principal."""
        try:
            self.destroy()
        finally:
            if callable(self._on_volver):
                self._on_volver()

    def _crear_entry_coef(self, parent, width=7):
        """Crea un campo Entry validado para coeficientes o fracciones (inicia vacío)."""
        e = tk.Entry(
            parent, width=width, justify="right",
            bg=self.COLOR_CAJA_BG, fg=self.COLOR_CAJA_FG
        )

        # Validación: solo números válidos, fracciones o decimales
        vcmd = (e.register(patron_valido_para_coeficiente), "%P")
        e.config(validate="key", validatecommand=vcmd)

        # Al enfocar, selecciona el contenido (si lo hay)
        e.bind("<FocusIn>", lambda _ev: e.select_range(0, "end"))

        # Al salir, si está vacío, se mantiene vacío (no inserta 0)
        e.bind("<FocusOut>", lambda _ev: None)
        return e

    def _mostrar_error(self, mensaje, titulo="Error"):
        """Muestra un mensaje de error estándar."""
        messagebox.showwarning(titulo, mensaje)
