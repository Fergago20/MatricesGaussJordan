import sympy as sp
from fractions import Fraction

def fraccion(x):
    """Convierte la entrada a fracción si es posible (cadena como '1/2' o número)."""
    if isinstance(x, Fraction): 
        return x  # Si ya es una fracción, devuélvela tal cual
    if isinstance(x, int): 
        return Fraction(x, 1)  # Si es un entero, lo convierte a fracción
    try:
        return Fraction(str(x))  # Intenta convertir la cadena a fracción
    except ValueError:
        raise ValueError(f"No se puede convertir {x} a una fracción válida.")

def punto_medio(a, b):
    """Calcula el punto medio entre a y b."""
    return (a + b) / 2

def evaluar_en_punto(ecuacion_str, x_val):
    """Evalúa la ecuación en un punto x_val.
    La ecuacion_str debe ser compatible con sympy.sympify."""
    x = sp.symbols('x')
    try:
        # Normalizar notación común en la cadena (si es string)
        if isinstance(ecuacion_str, str):
            # asignar el resultado de replace, no modificar in-place
            ecuacion_normalizada = ecuacion_str.replace('÷', '/')
           
        else:
            ecuacion_normalizada = ecuacion_str

        # Pasar símbolos y constantes conocidas a sympify para que reconozca 'x' y 'e'
        local_dict = {'x': x, 'e': sp.E, 'E': sp.E, 'ln': sp.log, 'log': sp.log}
        print(ecuacion_normalizada)
        expr = sp.sympify(ecuacion_normalizada, locals=local_dict)
        resultado = expr.subs(x, x_val)
        return float(resultado)  # Convertir a flotante para cálculos numéricos
    except (sp.SympifyError, TypeError, ValueError, AttributeError) as e:
        raise ValueError(f"Error al evaluar la función '{ecuacion_str}' en x={x_val}: {e}")

def valor_funcion(funcion_input, x):
    """Evalúa la función en el punto x.
    'funcion_input' puede ser un string o un callable."""
    if isinstance(funcion_input, str):
        return evaluar_en_punto(funcion_input, x)
    elif callable(funcion_input):
        return funcion_input(x)
    else:
        raise TypeError("El argumento 'funcion' debe ser un string o un callable.")

def valores_intervalos(fa, fc):
    """Determina en qué subintervalo se encuentra la raíz."""
    if fa * fc < 0:
        return True
    return False

def evaluar_tolerancia(fc, tol):
    """Verifica si el valor absoluto de fc es menor que la tolerancia."""
    return abs(fc) < tol

def evaluar_primera_condicion(fa, fb):
    """Verifica si los valores en los extremos del intervalo tienen signos opuestos."""
    return fa * fb < 0

def calcular_biseccion(funcion, a, b, tol):
    print(funcion)
    intervalo1 = fraccion(a)
    intervalo2 = fraccion(b)
    c = punto_medio(intervalo1, intervalo2)

    # Verificar que 'funcion' es un string y pasa el string a una función evaluable
    if isinstance(funcion, str):
        fa = valor_funcion(funcion, intervalo1)
        print(fa)
        fb = valor_funcion(funcion, intervalo2)
    elif callable(funcion):
        fa = funcion(intervalo1)
        fb = funcion(intervalo2)
    else:
        raise TypeError("El argumento 'funcion' debe ser un string o un callable.")

    if not evaluar_primera_condicion(fa, fb):
        raise ValueError("La función debe tener signos opuestos en los extremos del intervalo [a, b].")

    fc = valor_funcion(funcion, c)
    print(fc)
    iteraciones = 0
    resultados = []

    while not evaluar_tolerancia(fc, tol):  # Iterar hasta que se cumpla la tolerancia
        if valores_intervalos(fa, fc):
            intervalo2 = c
            fb = fc
        else:
            intervalo1 = c
            fa = fc

        c = punto_medio(intervalo1, intervalo2)  # Nuevo punto medio
        fc = valor_funcion(funcion, c)  # Evaluar en el nuevo punto medio
        # Almacenar los resultados de esta iteración, convirtiéndolos a float
        resultados.append([iteraciones + 1, float(intervalo1), float(intervalo2), float(c), float(fa), float(fb), float(fc)])

        iteraciones += 1

    # Devolver el resultado en formato decimal
    return float(c), iteraciones, resultados
#print(calcular_biseccion("ln(x)-e**-x", 1.1, 1.5, 10^-5))
#print(calcular_biseccion("x**1/3", -0.5, 1, 10**-5))