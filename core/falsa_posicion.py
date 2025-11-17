from core.biserccion import valor_funcion, fraccion, evaluar_tolerancia

def condicion1(fa, fb):
    return fa * fb < 0

def calcular_falsa_posicion(funcion, a, b, tol, max_iter=1000):
    a = fraccion(a)
    b = fraccion(b)

    # evaluador coherente
    if isinstance(funcion, str):
        f = lambda x: valor_funcion(funcion, x)
    elif callable(funcion):
        f = funcion
    else:
        raise TypeError("El argumento 'funcion' debe ser un string o un callable.")

    fa = f(a)
    fb = f(b)

    resultados = []
    iteraciones = 0

    # 1) COMPROBAR SI LA RAÍZ YA ESTÁ EN ALGÚN EXTREMO
    if evaluar_tolerancia(fa, tol):
        resultados.append([0, float(a), float(b), float(a),
                           float(fa), float(fb), float(fa)])
        return float(a), 0, resultados

    if evaluar_tolerancia(fb, tol):
        resultados.append([0, float(a), float(b), float(b),
                           float(fa), float(fb), float(fb)])
        return float(b), 0, resultados

    # 2) Verificar cambio de signo
    if not condicion1(fa, fb):
        raise ValueError("No hay cambio de signo en [a,b]. El método no aplica.")

    if fa == fb:
        raise ZeroDivisionError("fa y fb son iguales; no se puede aplicar falsa posición.")

    # 3) Iteraciones
    while True:
        # Punto de falsa posición
        c = b - (fb * (a - b)) / (fa - fb)
        fc = f(c)

        resultados.append([
            iteraciones,
            float(a), float(b), float(c),
            float(fa), float(fb), float(fc)
        ])

        # Criterio estándar: f(c) suficientemente pequeño
        if evaluar_tolerancia(fc, tol):
            return float(c), iteraciones, resultados

        # Actualizar intervalo
        if condicion1(fa, fc):
            b, fb = c, fc
        else:
            a, fa = c, fc

        iteraciones += 1

        # 4) DESPUÉS DE ACTUALIZAR: ¿RAÍZ EN ALGÚN EXTREMO?
        if evaluar_tolerancia(fa, tol):
            resultados.append([
                iteraciones,
                float(a), float(b), float(a),
                float(fa), float(fb), float(fa)
            ])
            return float(a), iteraciones, resultados

        if evaluar_tolerancia(fb, tol):
            resultados.append([
                iteraciones,
                float(a), float(b), float(b),
                float(fa), float(fb), float(fb)
            ])
            return float(b), iteraciones, resultados

        # 5) límite de seguridad para evitar bucles infinitos
        if iteraciones >= max_iter:
            raise RuntimeError(
                "Falsa posición alcanzó el número máximo de iteraciones; "
                "posible estancamiento numérico."
            )
