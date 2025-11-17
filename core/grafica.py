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
    s = re.sub(r'\s*=+\s*0\s*$', '', s)  # quitar =0 al final
    s = s.replace('^', '**').replace('÷', '/')

    # √x -> sqrt(x) y √( -> sqrt(
    s = re.sub(r'√\s*([a-zA-Z0-9_.]+)', r'sqrt(\1)', s)
    s = s.replace('√(', 'sqrt(')

    # 1️⃣ Coma decimal entre dígitos -> punto (2,5 → 2.5)
    s = re.sub(r'(?<=\d),(?=\d)', '.', s)

    # 2️⃣ √[n](expr) -> root(expr, n)
    s = re.sub(r'√\s*\[\s*([+-]?\d+)\s*\]\s*\(\s*([^()]+)\s*\)', r'root(\2,\1)', s)

    # 3️⃣ sqrt(expr, n) -> root(expr, n)
    s = re.sub(r'sqrt\(\s*([^()]+?)\s*,\s*([+-]?\d+)\s*\)', r'root(\1,\2)', s)

    # Corrige patrones erróneos comunes
    s = re.sub(r'\(1\s*/\s*x\s*-\s*1\)', r'1/(x-1)', s)

    # Agrupar fracciones en exponentes: **1/3, **-1/2 -> **(1/3), **(-1/2)
    s = re.sub(r'\*\*\s*([+-]?\d+)\s*/\s*([+-]?\d+)', r'**(\1/\2)', s)
    # Envolver exponentes negativos simples: **-2.5 -> **(-2.5)
    s = re.sub(r'\*\*\s*-\s*(\d+(?:\.\d+)?)', r'**(-\1)', s)
    # Aceptar exponentes con denominadores variables: **-1/(2+x)
    s = re.sub(
        r'\*\*\s*-\s*(\([^()]+\)\s*/\s*\([^()]+\)|[A-Za-z0-9_+*/.-]+/[A-Za-z0-9_+*/.-]+)',
        r'**(-(\1))',
        s
    )

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
            return a ** sp.Rational(1, n_int)
        except Exception:
            return a ** (sp.Rational(1, n))

    # log personalizado:
    def _log_personalizado(*args):
        """
        log(x)    -> log base 10
        log(x,b)  -> log base b
        """
        if len(args) == 1:
            x_arg = args[0]
            return sp.log(x_arg, 10)      # base 10 por defecto
        elif len(args) == 2:
            x_arg, base = args
            return sp.log(x_arg, base)    # base explícita
        else:
            raise ValueError("log() debe usarse como log(x) o log(x, base).")

    local_dict = {
        'x': x, 'e': sp.E, 'E': sp.E,

        # Logaritmos
        'ln': sp.log,               # ln(x) -> log natural base e
        'log': _log_personalizado,  # log(x) -> base 10, log(x,b) -> base b

        # Raíces
        'root': _root_real_or_pow,
        'cbrt': lambda a: sp.real_root(a, 3),

        # Trigonométricas y otros alias
        'sen': sp.sin,
        'tg': sp.tan,
        'sqrt': sp.sqrt,
    }

    try:
        ecuacion_normalizada = limpiar_ecuacion(ecuacion_str)
        expr = sp.sympify(ecuacion_normalizada, locals=local_dict)
    except (sp.SympifyError, SyntaxError, ValueError, TypeError, re.error) as e:
        raise ValueError(f"Error al interpretar la ecuación: {e}")

    # Convertir a función numpy-safe
    f = sp.lambdify(x, expr, modules=['numpy'])

    # Prueba rápida
    try:
        _ = f(np.array([0.0]))
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


def _ajustar_limites_y(y: np.ndarray, margen=0.1, max_abs=1e3):
    """
    Ajusta los límites de Y ignorando outliers enormes (picos de tan, exp, etc.).
    """
    yv = y[np.isfinite(y)]
    yv = yv[np.abs(yv) < max_abs]  # descartar valores gigantes
    if yv.size == 0:
        return (-1, 1)
    p5, p95 = np.percentile(yv, [5, 95])
    if p5 == p95:
        p5 -= 1
        p95 += 1
    r = p95 - p5
    return (p5 - margen * r, p95 + margen * r)


def _elegir_rango_x(expr_str: str, preferencia=None, ampliar=1.0, simetrico=None):
    if preferencia and len(preferencia) == 2:
        return float(preferencia[0]), float(preferencia[1])

    s = expr_str.lower()
    if simetrico is not None:
        R = float(simetrico)
        return -R, R

    # Rangos base un poco más inteligentes
    if "tan" in s or "cot" in s:
        xmin, xmax = -3.0, 3.0
    elif ("log" in s) or ("sqrt" in s) or ("ln" in s):
        xmin, xmax = 0.01, 10.0
    elif ("exp" in s) or ("e**" in s):
        xmin, xmax = -5.0, 5.0
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
# Búsqueda de raíces (simbólica + numérica)
# ==============================
def _buscar_raices_por_signo(f, x_min, x_max, n_muestras=800):
    """Busca raíces reales aproximadas detectando cambios de signo."""
    xs = np.linspace(x_min, x_max, int(max(3, n_muestras)))
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        ys = _limpiar_y(f(xs))

    raices = []

    def _agregar_raiz(r):
        for r0 in raices:
            if abs(r - r0) < 1e-3:
                return
        raices.append(r)

    for i in range(len(xs) - 1):
        x1, x2 = xs[i], xs[i + 1]
        y1, y2 = ys[i], ys[i + 1]
        if np.isnan(y1) or np.isnan(y2):
            continue

        if y1 == 0:
            _agregar_raiz(x1)
            continue

        if y1 * y2 < 0:
            a, b = x1, x2
            fa, fb = y1, y2
            for _ in range(30):
                m = 0.5 * (a + b)
                fm = _limpiar_y(f(np.array([m])))[0]
                if np.isnan(fm):
                    break
                if fa * fm <= 0:
                    b, fb = m, fm
                else:
                    a, fa = m, fm
            _agregar_raiz(0.5 * (a + b))

    return raices


def _obtener_raices_reales(expr_str: str, f, x_min0: float, x_max0: float):
    """
    Intenta obtener raíces reales en [x_min0,x_max0]:
    - primero simbólicamente si es polinomio,
    - luego por búsqueda numérica de cambios de signo.
    """
    raices = []

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
        expr = sp.sympify(expr_str, locals={'x': x})
        if expr.is_polynomial(x):
            for r in sp.nroots(expr):
                r_c = complex(r)
                if abs(r_c.imag) < 1e-8:
                    val = float(r_c.real)
                    if x_min0 <= val <= x_max0:
                        raices.append(val)
    except Exception:
        pass

    raices_num = _buscar_raices_por_signo(f, x_min0, x_max0)
    for r in raices_num:
        if not any(abs(r - r0) < 1e-3 for r0 in raices):
            raices.append(r)

    return raices

    return f, str(expr)

def _ajustar_rango_por_raices(f, expr_str: str, x_min0: float, x_max0: float):
    """
    A partir de un rango inicial [x_min0, x_max0] lo ajusta para
    que las raíces reales encontradas queden centradas y visibles.
    Devuelve (x_min, x_max, lista_raices).
    """
    raices = _obtener_raices_reales(expr_str, f, x_min0, x_max0)
    if not raices:
        return x_min0, x_max0, []

    rmin = min(raices)
    rmax = max(raices)

    if len(raices) == 1:
        c = raices[0]
        half = max((x_max0 - x_min0) / 6.0, 1.5)
        return c - half, c + half, raices

    span = rmax - rmin
    if span < 1e-6:
        span = 1.0
    pad = max(span * 0.5, 1.0)
    return rmin - pad, rmax + pad, raices


# ==============================
# Detección de asíntotas verticales
# ==============================
def _detectar_asintotas(x: np.ndarray, y: np.ndarray, umbral=1e3):
    """
    Detecta posibles asíntotas verticales donde y es no finito o muy grande.
    Devuelve una lista de posiciones x donde dibujar líneas verticales.
    """
    mask_bad = ~np.isfinite(y) | (np.abs(y) > umbral)
    asintotas = []
    n = len(x)
    i = 0
    while i < n:
        if not mask_bad[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and mask_bad[j + 1]:
            j += 1
        # usar el punto medio entre el último bueno y el primero bueno alrededor
        x_left = x[i - 1] if i > 0 else x[i]
        x_right = x[j + 1] if j + 1 < n else x[j]
        x_as = 0.5 * (x_left + x_right)
        asintotas.append(x_as)
        i = j + 1
    return asintotas


# ==============================
# Graficador robusto (ajustado a raíces + asíntotas)
# ==============================
def inicio_grafica(ecuacion: str, rango_x=None, puntos=1600,
                   titulo=None, ampliar=1.0, simetrico=None):
    """
    Dibuja la función. El rango en X se ajusta usando las raíces reales
    encontradas (simbólica o numéricamente) dentro de un rango base.
    También intenta detectar y dibujar asíntotas verticales.
    Devuelve la lista de raíces reales aproximadas.
    """
    try:
        f, expr_str = pasar_funcion_a_callable(ecuacion)
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

    # 1) rango base
    x_min0, x_max0 = _elegir_rango_x(expr_str, preferencia=rango_x,
                                     ampliar=ampliar, simetrico=simetrico)

    # 2) ajustar el rango para que las raíces reales queden visibles
    x_min, x_max, raices = _ajustar_rango_por_raices(f, expr_str, x_min0, x_max0)

    puntos = int(puntos)
    x = np.linspace(x_min, x_max, puntos)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        y = _limpiar_y(f(x))

    plt.figure(figsize=(9.5, 6.2))

    # usar máscara para no unir saltos de asintotas
    y_plot = np.ma.masked_invalid(y)
    plt.plot(x, y_plot, linewidth=2)

    # Ejes
    plt.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)
    plt.axvline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)

    # Detectar y dibujar asíntotas verticales
    asintotas = _detectar_asintotas(x, y)
    for xa in asintotas:
        plt.axvline(xa, color='gray', linestyle=':', linewidth=1)

    # Ajustar eje Y según los valores (ignorando outliers enormes)
    ymin, ymax = _ajustar_limites_y(y)
    plt.ylim(ymin, ymax)
    plt.xlim(x_min, x_max)

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel("x", fontsize=11)
    plt.ylabel("f(x)", fontsize=11)
    plt.title(titulo or "Gráfica de la función", fontsize=13)
    # Sin leyenda para no ocupar espacio
    plt.tight_layout()
    plt.show()

    return raices
