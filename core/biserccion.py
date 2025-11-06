import sympy as sp
from fractions import Fraction
import re

# ---------------------------
# Utilidades numéricas básicas
# ---------------------------
def fraccion(x):
    """Convierte la entrada a fracción si es posible (cadena '1/2' o número)."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    try:
        return Fraction(str(x))
    except ValueError:
        raise ValueError(f"No se puede convertir {x} a una fracción válida.")

def punto_medio(a, b):
    """Calcula el punto medio entre a y b."""
    return (a + b) / 2

# ---------------------------
# Normalización de la cadena
# ---------------------------
def _normalizar_cadena(expr_str: str) -> str:
    """
    Normaliza detalles de sintaxis en cadenas:
      - '÷' -> '/'
      - Arregla precedencia: x**1/3 -> x**(1/3) para evitar (x**1)/3
      - (opcional) puedes añadir: s = s.replace('^','**') si aceptas '^' como potencia
    """
    s = expr_str.replace('÷', '/').strip()
    # Corrige '**1/n' por '**(1/n)' respetando espacios
    s = re.sub(r'\*\*\s*1\s*/\s*(\d+)', r'**(1/\1)', s)
    return s

# ---------------------------
# Evaluación segura en un punto
# ---------------------------
def evaluar_en_punto(ecuacion_str, x_val, imag_tol=1e-12):
    print(f"Evaluando '{ecuacion_str}' en x={x_val}...")
    """
    Evalúa ecuación en x_val como número real cuando corresponde.
    Reglas:
      - root(a,n): si n impar -> real_root(a,n); si n par -> a**(1/n) (rama principal)
      - cbrt(a)  : real_root(a,3)
      - ln       : log natural
      - log      : log natural (si el usuario lo usa)
    Si el resultado es complejo pero |Im| <= imag_tol, devuelve la parte real.
    """
    x = sp.symbols('x')

    # Mapeo de root: real si n impar; potencia fraccionaria si n par
    def _root_real_or_pow(a, n):
        try:
            n_int = int(n)
            if n_int % 2 == 1:           # impar -> raíz real (acepta a<0)
                return sp.real_root(a, n_int)
            else:                         # par -> potencia fraccionaria simbólica
                return a**sp.Rational(1, n_int)
        except Exception:
            # Si n no es entero literal, usar exponente fraccionario simbólico
            return a**(sp.Rational(1, n))

    local_dict = {
        'x': x,
        'e': sp.E, 'E': sp.E,
        'ln': sp.log,       # log natural
        'log': sp.log,      # natural si lo usan
        'root': _root_real_or_pow,
        'cbrt': lambda a: sp.real_root(a, 3),
        'sen': sp.sin,      # alias comunes en ES
        'tg': sp.tan
    }

    try:
        if isinstance(ecuacion_str, str):
            ecuacion_normalizada = _normalizar_cadena(ecuacion_str)
        else:
            ecuacion_normalizada = ecuacion_str

        expr = sp.sympify(ecuacion_normalizada, locals=local_dict)
        resultado = expr.subs(x, x_val)

        # Evaluación numérica robusta
        resultado_eval = sp.N(resultado)
        if resultado_eval.is_real:
            return float(resultado_eval)

        # Si es complejo con parte imaginaria "casi cero", toma la real
        if hasattr(resultado_eval, 'as_real_imag'):
            re_part, im_part = resultado_eval.as_real_imag()
            im_val = float(sp.N(im_part))
            if abs(im_val) <= imag_tol:
                return float(sp.N(re_part))

        # Complejo de verdad
        raise TypeError("El resultado es complejo en el punto dado (no es función real allí).")

    except (sp.SympifyError, TypeError, ValueError, AttributeError) as e:
        raise ValueError(f"Error al evaluar la función '{ecuacion_str}' en x={x_val}: {e}")

# ---------------------------
# Helpers de bisección (tuyos)
# ---------------------------
def valor_funcion(funcion_input, x):
    """Evalúa la función en el punto x. 'funcion_input' puede ser string o callable."""
    if isinstance(funcion_input, str):
        return evaluar_en_punto(funcion_input, x)
    elif callable(funcion_input):
        return funcion_input(x)
    else:
        raise TypeError("El argumento 'funcion' debe ser un string o un callable.")

def valores_intervalos(fa, fc):
    """Determina si hay cambio de signo entre f(a) y f(c)."""
    return fa * fc < 0

def evaluar_tolerancia(fc, tol):
    """Verifica si |fc| < tol."""
    return abs(fc) < tol

def evaluar_primera_condicion(fa, fb):
    """Verifica cambio de signo en los extremos del intervalo [a,b]."""
    return fa * fb < 0

def calcular_biseccion(funcion, a, b, tol):
    """
    Bisección clásica sobre 'funcion' (str o callable).
    Devuelve (c, iteraciones, resultados) donde resultados es la tabla por iteración.
    """
    intervalo1 = fraccion(a)
    intervalo2 = fraccion(b)
    c = punto_medio(intervalo1, intervalo2)

    # Evaluar extremos
    if isinstance(funcion, str):
        fa = valor_funcion(funcion, intervalo1)
        fb = valor_funcion(funcion, intervalo2)
        print(f"f({intervalo1}) = {fa}, f({intervalo2}) = {fb}")
    elif callable(funcion):
        fa = funcion(intervalo1)
        fb = funcion(intervalo2)
    else:
        raise TypeError("El argumento 'funcion' debe ser un string o un callable.")

    if not evaluar_primera_condicion(fa, fb):
        raise ValueError("La función debe tener signos opuestos en los extremos del intervalo [a, b].")

    fc = valor_funcion(funcion, c)
    iteraciones = 0
    resultados = []

    while not evaluar_tolerancia(fc, tol):
        if valores_intervalos(fa, fc):
            intervalo2 = c
            fb = fc
        else:
            intervalo1 = c
            fa = fc

        c = punto_medio(intervalo1, intervalo2)
        fc = valor_funcion(funcion, c)

        resultados.append([
            iteraciones + 1,
            float(intervalo1), float(intervalo2), float(c),
            float(fa), float(fb), float(fc)
        ])
        iteraciones += 1

    return float(c), iteraciones, resultados

# ---------------------------
# PRUEBAS RÁPIDAS (comentar/usar)
# ---------------------------
# 1) Raíz cúbica real en negativos (root impar -> real_root)
#print(evaluar_en_punto("root(x,3)", Fraction(-1,2)))   # ~ -0.7937005259
# print(evaluar_en_punto("cbrt(x)", -0.5))               # ~ -0.7937005259

# 2) Raíz cuadrada de negativo (root par -> potencia fracc. -> complejo -> error claro)
# try:
#     print(evaluar_en_punto("root(x,2)", -1))
# except Exception as e:
#     pri
