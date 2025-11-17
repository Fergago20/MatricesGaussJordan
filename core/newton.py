# core/newton.py

import sympy as sp
from core.biserccion import fraccion, evaluar_tolerancia

def calcular_newton_raphson(funcion, x0, tol, max_iter: int = 1000):
    """
    Método de Newton-Raphson clásico con punto inicial x0.

    Parámetros:
        funcion   : str o callable. Si es str se interpreta con sympy.
        x0        : punto inicial para la iteración.
        tol       : tolerancia para el error de aproximación (Ea).
        max_iter  : máximo de iteraciones permitidas.

    Retorna:
        (raiz, iteraciones, resultados)
        - raiz: float con la raíz aproximada.
        - iteraciones: número de iteraciones realizadas.
        - resultados: lista de filas [iter, xi, xi1, Ea, f(xi), f'(xi)]

    El error Ea se define como error RELATIVO:
        Ea = |(xi+1 - xi) / xi+1|    (si xi+1 != 0)
             |xi+1 - xi|            (si xi+1 == 0)
    """

    # Normalizar x0 (por si te gusta meter fracciones tipo 1/3)
    x0 = float(fraccion(x0))

    # Construir f y f' según el tipo de "funcion"
    if isinstance(funcion, str):
        x = sp.symbols('x')
        expr = sp.sympify(funcion)
        f_sym = sp.lambdify(x, expr, "math")
        df_expr = sp.diff(expr, x)
        df_sym = sp.lambdify(x, df_expr, "math")

        def f(xval: float) -> float:
            return float(f_sym(xval))

        def df(xval: float) -> float:
            return float(df_sym(xval))

    elif callable(funcion):
        f = funcion

        # Derivada numérica central si te pasan un callable
        def df(xval: float, h: float = 1e-6) -> float:
            return float((f(xval + h) - f(xval - h)) / (2 * h))
    else:
        raise TypeError("El argumento 'funcion' debe ser un string o un callable.")

    xi = x0
    resultados = []

    for it in range(1, max_iter + 1):
        fxi = f(xi)
        dfxi = df(xi)

        if dfxi == 0:
            raise ZeroDivisionError(
                "La derivada f'(x) se hizo cero en una iteración; "
                "el método de Newton-Raphson no puede continuar."
            )

        xi1 = xi - fxi / dfxi

        # Error relativo (como en el ejemplo)
        if xi1 != 0:
            Ea = abs((xi1 - xi) / xi1)
        else:
            Ea = abs(xi1 - xi)

        resultados.append([
            it,
            float(xi),
            float(xi1),
            float(Ea),
            float(fxi),
            float(dfxi)
        ])

        # Criterio de parada usando evaluar_tolerancia
        if evaluar_tolerancia(Ea, tol):
            return float(xi1), it, resultados

        xi = xi1

    # Si llega aquí, no convergió
    raise RuntimeError(
        "Newton-Raphson alcanzó el número máximo de iteraciones sin converger."
    )
