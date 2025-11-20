# core/newton.py

import sympy as sp  # lo puedes dejar aunque no se use mucho ahora
from core.biserccion import fraccion, evaluar_tolerancia, evaluar_en_punto


def calcular_newton_raphson(funcion, x0, tol, max_iter: int = 1000):
    """
    Método de Newton-Raphson clásico con punto inicial x0.

    Parámetros:
        funcion   : str o callable.
        x0        : punto inicial.
        tol       : tolerancia para el error aproximado (Ea).
        max_iter  : máximo de iteraciones.

    Retorna:
        (raiz, iteraciones, resultados)

    Donde resultados = [iter, xi, xi1, Ea, f(xi), f'(xi)]
    """

    # -------------------------------
    # Normalizar x0 (permite "1/3")
    # -------------------------------
    x0 = float(fraccion(x0))

    # -------------------------------
    # Construir f y f'
    # -------------------------------
    if isinstance(funcion, str):
        # Usamos SIEMPRE evaluar_en_punto para respetar dominios (logs, root, etc.)
        def f(xval: float) -> float:
            return float(evaluar_en_punto(funcion, xval))

        # Derivada numérica central usando la misma f “segura”
        def df(xval: float, h: float = 1e-6) -> float:
            return float((f(xval + h) - f(xval - h)) / (2 * h))

    elif callable(funcion):
        # Función numérica directa
        f = funcion

        def df(xval: float, h: float = 1e-6) -> float:
            return float((f(xval + h) - f(xval - h)) / (2 * h))

    else:
        raise TypeError("El argumento 'funcion' debe ser un string o callable.")

    # -------------------------------
    # Iteración de Newton-Raphson
    # -------------------------------
    xi = x0
    resultados = []

    for it in range(1, max_iter + 1):
        # Evaluar función y derivada en el punto actual
        fxi = f(xi)
        dfxi = df(xi)

        # Evitar división entre cero o derivada peligrosa
        if abs(dfxi) < 1e-14:
            raise ZeroDivisionError(
                f"La derivada es demasiado pequeña (f'({xi}) = {dfxi}). "
                f"Newton-Raphson no puede continuar."
            )

        # Cálculo de Newton
        xi1 = xi - fxi / dfxi

        # Error relativo
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

        # Criterio de paro
        if evaluar_tolerancia(Ea, tol):
            return float(xi1), it, resultados

        xi = xi1

    # Si no logró converger
    raise RuntimeError(
        "Newton-Raphson alcanzó el máximo de iteraciones sin converger."
    )
