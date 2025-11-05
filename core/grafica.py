import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import math


def limpiar_ecuacion(ecuacion_str):
    """Normaliza expresiones comunes (ln, e^x, ^ → **, etc.)"""
    reemplazos = {
        '^': '**',
        'ln(': 'log(',
        'e^': 'exp(',
        '√': 'sqrt(',
        '÷': '/',
    }
    for viejo, nuevo in reemplazos.items():
        ecuacion_str = ecuacion_str.replace(viejo, nuevo)
    return ecuacion_str


def pasar_funcion_a_callable(ecuacion_str):
    """
    Convierte una ecuación en string a una función numpy-safe.
    Admite expresiones como ln(x), e^x, cos(x), etc.
    También limpia ecuaciones del tipo 'f(x)=0'.
    """
    x = sp.symbols('x')
    try:
        # 🔹 Limpieza adicional
        ecuacion_str = ecuacion_str.strip()
        ecuacion_str = ecuacion_str.replace("=0", "").strip()  # elimina el =0 si existe
        ecuacion_str = limpiar_ecuacion(ecuacion_str)  # normaliza ln, e^x, etc.

        expr = sp.sympify(ecuacion_str, convert_xor=True)
        return sp.lambdify(x, expr, modules=['numpy'])
    except Exception as e:
        raise ValueError(f"No se pudo interpretar la ecuación '{ecuacion_str}': {e}")


def manejar_valores_invalidos(y):
    """Convierte valores complejos, infinitos o indefinidos a NaN."""
    try:
        if np.isnan(y) or np.isinf(y):
            return np.nan
        if isinstance(y, complex):
            return np.nan
        return y
    except Exception:
        return np.nan


def inicio_grafica(ecuacion):
    """
    Grafica la función ingresada en un rango adaptativo [-10, 10].
    Maneja errores y valores inválidos de forma segura.
    """
    try:
        # Crear función evaluable
        f = pasar_funcion_a_callable(ecuacion)
    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error de ecuación", f"No se pudo interpretar la ecuación:\n\n{e}")
        return

    # Determinar rango inteligente
    # Si hay log o sqrt, evitamos x ≤ 0
    ecuacion_lower = ecuacion.lower()
    if "log" in ecuacion_lower or "ln" in ecuacion_lower or "sqrt" in ecuacion_lower:
        x = np.linspace(0.01, 10, 800)
    else:
        x = np.linspace(-10, 10, 800)

    # Calcular f(x) y limpiar valores problemáticos
    try:
        y = f(x)
        y = np.vectorize(manejar_valores_invalidos)(y)
    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error al graficar", f"No se pudo evaluar la función:\n\n{e}")
        return

    # Crear gráfica
    plt.figure(figsize=(9, 6))
    plt.plot(x, y, color='blue', label=f"f(x) = {ecuacion}")
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.axvline(0, color='black', linewidth=0.8, linestyle='--')
    plt.title(f"Gráfica de la función: {ecuacion}", fontsize=13)
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def mostrar_ecuacion_latex(ecuacion_str):
    """Muestra la ecuación en formato LaTeX (solo para propósitos didácticos)."""
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, f"${ecuacion_str}$", fontsize=20, ha='center', va='center')
    ax.axis('off')
    plt.show()
