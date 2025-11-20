# core/secante.py

import sympy as sp  # Lo dejamos por consistencia, aunque no se use directamente
from core.biserccion import fraccion, evaluar_tolerancia, evaluar_en_punto


def calcular_secante(funcion, x0, x1, tol, max_iter: int = 1000):
    """
    Método de la Secante con dos puntos iniciales x0 y x1.

    Parámetros:
        funcion   : str o callable.
        x0        : primer punto inicial.
        x1        : segundo punto inicial.
        tol       : tolerancia para el error aproximado (Ea).
        max_iter  : máximo de iteraciones.

    Retorna:
        (raiz, iteraciones, resultados)

    Donde resultados = [iter, xi_1, xi, xi1, Ea, f(xi_1), f(xi)]

        - xi_1  : x_{n-1}
        - xi    : x_n
        - xi1   : x_{n+1}
        - Ea    : error relativo aproximado en xi1
    """

    # -------------------------------
    # Normalizar x0 y x1 (permite "1/3", etc.)
    # -------------------------------
    x0 = float(fraccion(x0))
    x1 = float(fraccion(x1))

    # -------------------------------
    # Construir f de forma segura
    # -------------------------------
    if isinstance(funcion, str):
        # Usamos SIEMPRE evaluar_en_punto para respetar dominios (logs, raíces, etc.)
        def f(xval: float) -> float:
            return float(evaluar_en_punto(funcion, xval))

    elif callable(funcion):
        # Función numérica directa
        f = funcion

    else:
        raise TypeError("El argumento 'funcion' debe ser un string o callable.")

    # -------------------------------
    # Iteración de la Secante
    # -------------------------------
    xi_1 = x0  # x_{n-1}
    xi = x1    # x_n

    resultados = []

    # Evaluar f en los puntos iniciales
    fxi_1 = f(xi_1)
    fxi = f(xi)

    for it in range(1, max_iter + 1):
        # Evitar división entre cero o denominador muy pequeño
        denom = (fxi - fxi_1)
        if abs(denom) < 1e-14:
            raise ZeroDivisionError(
                f"El denominador f(x_n) - f(x_n-1) es demasiado pequeño: "
                f"f({xi}) - f({xi_1}) = {fxi} - {fxi_1}. "
                f"El método de la secante no puede continuar."
            )

        # Fórmula de la secante:
        # x_{n+1} = x_n - f(x_n) * (x_n - x_{n-1}) / (f(x_n) - f(x_{n-1}))
        xi1 = xi - fxi * (xi - xi_1) / denom

        # Error relativo aproximado
        if xi1 != 0:
            Ea = abs((xi1 - xi) / xi1)
        else:
            Ea = abs(xi1 - xi)

        resultados.append([
            it,
            float(xi_1),   # x_{n-1}
            float(xi),     # x_n
            float(xi1),    # x_{n+1}
            float(Ea),     # error relativo
            float(fxi_1),  # f(x_{n-1})
            float(fxi)     # f(x_n)
        ])

        # Criterio de paro
        if evaluar_tolerancia(Ea, tol):
            return float(xi1), it, resultados

        # Actualizar para la siguiente iteración:
        xi_1, fxi_1 = xi, fxi
        xi = xi1
        fxi = f(xi)

    # Si no hubo convergencia dentro del máximo de iteraciones
    raise RuntimeError(
        "El método de la secante alcanzó el máximo de iteraciones sin converger."
    )
