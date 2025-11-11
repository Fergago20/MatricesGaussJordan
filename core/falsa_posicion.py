from biserccion import valor_funcion, fraccion, evaluar_tolerancia

def condicion1(fa, fb):
    return fa * fb < 0

def calcular_falsa_posicion(funcion, a, b, tol):
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

    if not condicion1(fa, fb):
        raise ValueError("No hay cambio de signo en [a,b]. El método no aplica.")

    if fa == fb:
        raise ZeroDivisionError("fa y fb son iguales; no se puede aplicar falsa posición.")

    resultados = []
    iteraciones = 0

    while True:
        c = b - (fb * (a - b)) / (fa - fb)
        fc = f(c)

        iteraciones += 1
        resultados.append([
            iteraciones,
            float(a), float(b), float(c),
            float(fa), float(fb), float(fc)
        ])

        if evaluar_tolerancia(fc, tol):
            return float(c), iteraciones, resultados

        
        if condicion1(fa, fc):   
            b, fb = c, fc
        else:                    
            a, fa = c, fc

raiz, iters, tabla = calcular_falsa_posicion("cos(x) - x", 0, 1, 1e-10)
print(raiz, iters)
