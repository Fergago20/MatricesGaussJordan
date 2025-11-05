import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

def inicio_grafica(ecuacion):
    """
    Grafica la función en un rango fijo [0, 10].

    Parámetros:
    ecuacion (str): La ecuación en string (ej. "x**2 - 2").
    """
    # Convertir la ecuación a una función callable
    funcion_callable = pasar_funcion_a_callable(ecuacion)
    
    # Definir el rango fijo de x (como en tu código original)
    x = np.linspace(0, 10, 1000)
    
    # Calcular y usando la función callable (vectorizada para eficiencia)
    y = np.vectorize(funcion_callable)(x)
    
    # Crear la gráfica
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label=f'f(x) = {ecuacion}', color='blue')
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Línea en y=0
    plt.axvline(0, color='black', linewidth=0.8, linestyle='--')  # Línea en x=0
    plt.title(f'Gráfica de la función: {ecuacion}')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.grid(True)
    plt.legend()
    plt.show()

def mostrar_ecuacion_latex(ecuacion_str):
    """Muestra la ecuación en formato LaTeX dentro de un canvas."""
    # Usamos matplotlib para representar la ecuación en LaTeX
    fig, ax = plt.subplots()
    
    # Usamos el formato LaTeX en matplotlib
    ax.text(0.5, 0.5, f"${ecuacion_str}$", fontsize=20, ha='center', va='center')
    
    # Eliminamos los ejes para que solo se vea la ecuación
    ax.axis('off')
    
    # Mostrar la ecuación
    plt.show()

def pasar_funcion_a_callable(ecuacion_str):
    """Convierte una ecuación en string a una función callable."""
    x = sp.symbols('x')
    expr = sp.sympify(ecuacion_str)
    
    return sp.lambdify(x, expr, modules=['numpy'])
