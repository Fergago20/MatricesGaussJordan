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
# Normalización de la cadena (potencias y exponentes negativos)
# ---------------------------
def _normalizar_cadena(expr_str: str) -> str:
    """
    Normaliza detalles de sintaxis en cadenas para evitar ambigüedades con exponentes:
      - '^' -> '**'
      - '÷' -> '/'
      - Agrupa fracciones en exponentes: **1/3, **-1/2 -> **(1/3), **(-1/2)
      - Envuelve exponentes negativos simples: **-2.5 -> **(-2.5), **-3 -> **(-3)
      - Maneja también el caso escrito como x^-1/2 (tras convertir ^->**)
    """
    s = expr_str.strip()
    s = s.replace('÷', '/')
    s = s.replace('^', '**')

    # 1) Agrupar fracciones en exponentes: ** [sign]int / [sign]int  -> **(num/den)
    #    Ej: x**1/3 -> x**(1/3), x**-1/2 -> x**(-1/2)
    s = re.sub(r'\*\*\s*([+-]?\d+)\s*/\s*([+-]?\d+)', r'**(\1/\2)', s)

    # 2) Envolver exponentes negativos decimales o enteros: **-2.5 -> **(-2.5), **-3 -> **(-3)
    #    (Si ya está entre paréntesis no pasa nada, regex no lo toca)
    s = re.sub(r'\*\*\s*-\s*(\d+(?:\.\d+)?)', r'**(-\1)', s)

    # 3) Caso borde: espacios raros, p.ej. **   -  4  -> **(-4)
    s = re.sub(r'\*\*\s*-\s*(\d+)\b', r'**(-\1)', s)

    return s

# ---------------------------
# Evaluación segura en un punto
# ---------------------------
def evaluar_en_punto(ecuacion_str, x_val, imag_tol=1e-12):
    """
    Evalúa la ecuación (string o expresión sympy) en x_val y devuelve un float real cuando corresponde.

    Reglas especiales:
      - root(a,n): n impar -> real_root(a,|n|) con signo; n par -> a**(1/n) (rama principal)
        Si n < 0, se toma el recíproco: root(a,-n) = 1/root(a,n).
      - cbrt(a)  : real_root(a,3)
      - ln(x)    : logaritmo natural, base e
      - log(x)   : log base 10
      - log(x,b) : logaritmo base b (b cualquier número)
      - Acepta exponentes negativos en cualquier forma (enteros, fracciones y decimales).
      - Si el resultado es complejo pero |Im| <= imag_tol, devuelve la parte real.
    """
    print(f"Evaluando '{ecuacion_str}' en x={x_val}...")
    x = sp.symbols('x')

    def _root_real_or_pow(a, n):
        n = int(n)
        if n == 0:
            raise ValueError("root(a, 0) no está definido.")
        if n < 0:
            return 1 / _root_real_or_pow(a, -n)
        # si n es impar, usamos raíz real
        if n % 2 == 1:
            return sp.real_root(a, n)
        # si es par, usamos potencia normal
        return a**sp.Rational(1, n)


    def _log_personalizado(*args):
        """
        log(x)    -> log base 10
        log(x,b)  -> log base b
        """
        if len(args) == 1:
            x_arg = args[0]
            # log base 10 por defecto
            return sp.log(x_arg, 10)
        elif len(args) == 2:
            x_arg, base = args
            return sp.log(x_arg, base)
        else:
            raise ValueError("log() debe usarse como log(x) o log(x, base).")

    local_dict = {
        'x': x,
        'e': sp.E, 'E': sp.E,

        # Logaritmos
        'ln': sp.log,              # ln(x) -> log natural base e
        'log': _log_personalizado, # log(x) -> base 10, log(x,b) -> base b

        # Raíces
        'root': _root_real_or_pow,
        'cbrt': lambda a: sp.real_root(a, 3),

        # Trigonométricas y otros alias
        'sen': sp.sin,   # alias ES
        'tg': sp.tan,    # alias ES
        'sqrt': sp.sqrt,
    }

    try:
        # Normalizar cadena si viene como string
        if isinstance(ecuacion_str, str):
            ecuacion_normalizada = _normalizar_cadena(ecuacion_str)
        else:
            ecuacion_normalizada = ecuacion_str

        # Construir expresión sympy con las funciones locales
        expr = sp.sympify(ecuacion_normalizada, locals=local_dict)

        # Sustituir x
        resultado = expr.subs(x, x_val)
        resultado_eval = sp.N(resultado)

        # Si es claramente real
        if resultado_eval.is_real:
            return float(resultado_eval)

        # Si es "casi real" (parte imaginaria muy pequeña)
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
# PRUEBAS RÁPIDAS
# ---------------------------
if __name__ == "__main__":
    casos = [
        "x^-2",           # ^ -> ** y exponente negativo entero
        "x**-3",          # negativo entero
        "x**-2.5",        # negativo decimal
        "x**-1/2",        # fracción negativa sin paréntesis -> **(-1/2)
        "x^-1/3",         # con ^ -> **(-1/3)
        "root(x, -3)",    # raíz con índice negativo (recíproco de cúbica)
        "root(-8, 3)",    # cúbica real de negativo
        "root(-8, -3)",   # recíproco de cúbica real ( = -1/2 )
        "root(x, 2)",     # raíz cuadrada (rama principal)
    ]
    for s in casos:
        try:
            print(s, "=>", evaluar_en_punto(s, 4))
        except Exception as e:
            print(s, "-> Error:", e)
