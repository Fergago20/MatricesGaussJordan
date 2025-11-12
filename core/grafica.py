import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import re

# ==============================
# Verificación de paréntesis
# ==============================
def _balance_ok(s: str) -> bool:
    """Verifica que los paréntesis estén balanceados correctamente."""
    c = 0
    for ch in s:
        if ch == '(':
            c += 1
        elif ch == ')':
            c -= 1
        if c < 0:
            return False
    return c == 0

# ==============================
# Limpieza y normalización
# ==============================
def limpiar_ecuacion(ecuacion_str: str) -> str:
    """
    Normaliza texto para SymPy y corrige errores comunes:
    - ^ → **, ÷ → /
    - √(...) → sqrt(...)
    - √(..., n) → root(..., n)
    - √[n](...) → root(..., n)
    - coma decimal 2,5 → 2.5
    - agrupación de exponentes negativos/fraccionarios (**-1/2 → **(-1/2))
    """

    if not isinstance(ecuacion_str, str):
        raise TypeError("La ecuación debe ser una cadena de texto (str).")

    s = ecuacion_str.strip()
    if not s:
        raise ValueError("La ecuación está vacía.")
    if not _balance_ok(s):
        raise ValueError("Paréntesis desbalanceados en la ecuación.")

    # Normalización base
    s = re.sub(r'\s*=+\s*0\s*$', '', s)
    s = s.replace('^', '**').replace('÷', '/')

    # √x -> sqrt(x) y √( -> sqrt(
    s = re.sub(r'√\s*([a-zA-Z0-9_.]+)', r'sqrt(\1)', s)
    s = s.replace('√(', 'sqrt(')

    # 1️⃣ Coma decimal entre dígitos -> punto (2,5 → 2.5)
    s = re.sub(r'(?<=\d),(?=\d)', '.', s)

    # 2️⃣ √[n](expr) -> root(expr, n)
    s = re.sub(r'√\s*\[\s*([+-]?\d+)\s*\]\s*\(\s*([^()]+)\s*\)', r'root(\2,\1)', s)

    # 3️⃣ sqrt(expr, n) o √(expr, n) -> root(expr, n)
    s = re.sub(r'sqrt\(\s*([^()]+?)\s*,\s*([+-]?\d+)\s*\)', r'root(\1,\2)', s)

    # Corrige patrones erróneos comunes
    s = re.sub(r'\(1\s*/\s*x\s*-\s*1\)', r'1/(x-1)', s)

    # Agrupar fracciones en exponentes: **1/3, **-1/2 -> **(1/3), **(-1/2)
    s = re.sub(r'\*\*\s*([+-]?\d+)\s*/\s*([+-]?\d+)', r'**(\1/\2)', s)
    # Envolver exponentes negativos simples: **-2.5 -> **(-2.5)
    s = re.sub(r'\*\*\s*-\s*(\d+(?:\.\d+)?)', r'**(-\1)', s)
    # Aceptar exponentes con denominadores variables: **-1/(2+x)
    s = re.sub(r'\*\*\s*-\s*(\([^()]+\)\s*/\s*\([^()]+\)|[A-Za-z0-9_+*/.-]+/[A-Za-z0-9_+*/.-]+)',
               r'**(-(\1))', s)

    return s

# ==============================
# Conversión a función evaluable
# ==============================
def pasar_funcion_a_callable(ecuacion_str: str):
    """Convierte texto en función NumPy-safe; maneja errores de SymPy con claridad."""
    x = sp.symbols('x')

    def _root_real_or_pow(a, n):
        try:
            n_int = int(n)
            if n_int == 0:
                raise ValueError("root(a,0) no está definido.")
            if n_int < 0:
                n_pos = -n_int
                return 1 / _root_real_or_pow(a, n_pos)
            if n_int % 2 == 1:
                return sp.real_root(a, n_int)
            return a**sp.Rational(1, n_int)
        except Exception:
            return a**(sp.Rational(1, n))

    local_dict = {
        'x': x, 'e': sp.E, 'E': sp.E,
        'ln': sp.log, 'log': sp.log,
        'root': _root_real_or_pow,
        'cbrt': lambda a: sp.real_root(a, 3),
        'sen': sp.sin, 'tg': sp.tan,
        'sqrt': sp.sqrt,
    }

    try:
        ecuacion_normalizada = limpiar_ecuacion(ecuacion_str)
        expr = sp.sympify(ecuacion_normalizada, locals=local_dict)
    except (sp.SympifyError, SyntaxError, ValueError, TypeError, re.error) as e:
        raise ValueError(f"Error al interpretar la ecuación: {e}")

    f = sp.lambdify(x, expr, modules=['numpy'])

    try:
        _ = f(np.array([0.0]))  # prueba segura
    except Exception:
        pass

    return f, str(expr)

# ==============================
# Utilidades numéricas / gráficas
# ==============================
def _limpiar_y(y: np.ndarray) -> np.ndarray:
    y = np.array(y, dtype=np.complex128)
    y = np.where(np.abs(y.imag) > 1e-12, np.nan, y.real)
    y = np.where(~np.isfinite(y), np.nan, y)
    return y

def _ajustar_limites_y(y: np.ndarray, margen=0.1):
    yv = y[np.isfinite(y)]
    if yv.size == 0:
        return (-1, 1)
    p5, p95 = np.percentile(yv, [5, 95])
    if p5 == p95:
        p5 -= 1; p95 += 1
    r = p95 - p5
    return (p5 - margen*r, p95 + margen*r)

def _elegir_rango_x(expr_str: str, preferencia=None, ampliar=1.0, simetrico=None):
    if preferencia and len(preferencia) == 2:
        return float(preferencia[0]), float(preferencia[1])
    s = expr_str.lower()
    if simetrico is not None:
        R = float(simetrico)
        return -R, R
    if ("log" in s) or ("sqrt" in s) or ("ln" in s):
        xmin, xmax = 0.01, 10.0
    else:
        xmin, xmax = -10.0, 10.0
    ampliar = max(1.0, float(ampliar))
    if xmin > 0:
        ancho = (xmax - xmin) * ampliar
        xmax = xmin + ancho
    else:
        centro = 0.5 * (xmin + xmax)
        semi = 0.5 * (xmax - xmin) * ampliar
        xmin, xmax = centro - semi, centro + semi
    return xmin, xmax

# ==============================
# Graficador robusto
# ==============================
def inicio_grafica(ecuacion: str, rango_x=None, puntos=1600, titulo=None, ampliar=1.0, simetrico=None):
    try:
        f, expr_str = pasar_funcion_a_callable(ecuacion)
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    x_min, x_max = _elegir_rango_x(expr_str, preferencia=rango_x, ampliar=ampliar, simetrico=simetrico)

    def muestrear_segmento(a, b, n):
        xx = np.linspace(a, b, int(max(2, n)))
        with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
            yy = _limpiar_y(f(xx))
        return xx, yy

    puntos = int(puntos)
    eps = 1e-9
    plt.figure(figsize=(9.5, 6.2))

    try:
        if x_min < 0 < x_max:
            n1 = max(2, puntos // 2)
            n2 = max(2, puntos - n1)
            x1, y1 = muestrear_segmento(x_min, -eps, n1)
            x2, y2 = muestrear_segmento(eps, x_max, n2)
            plt.plot(x1, np.ma.masked_invalid(y1), linewidth=2, label=f"f(x) = {expr_str}")
            plt.plot(x2, np.ma.masked_invalid(y2), linewidth=2)
            y_all = np.concatenate([y1, y2])
        else:
            x, y = muestrear_segmento(x_min, x_max, puntos)
            plt.plot(x, np.ma.masked_invalid(y), linewidth=2, label=f"f(x) = {expr_str}")
            y_all = y
    except Exception as e:
        print(f"⚠️ Error al evaluar o graficar: {e}")
        return

    plt.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)
    plt.axvline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)

    ymin, ymax = _ajustar_limites_y(y_all)
    plt.ylim(ymin, ymax)
    plt.xlim(x_min, x_max)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel("x", fontsize=11)
    plt.ylabel("f(x)", fontsize=11)
    plt.title(titulo or "Gráfica de la función", fontsize=13)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.show()
