import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import re

# ==============================
# Limpieza y parsing seguro
# ==============================
def limpiar_ecuacion(ecuacion_str: str) -> str:
    """
    Normaliza lo mínimo para SymPy y corrige ambigüedades en exponentes:
    - Elimina '=0' al final si existe.
    - ^ -> ** (potencias).
    - √x -> sqrt(x) y '÷' -> '/'.
    - **1/3, **-1/2 -> **(1/3), **(-1/2)  (evita (x**-1)/2)
    - **-2.5 -> **(-2.5)  (envuelve exponentes negativos simples)
    """
    s = ecuacion_str.strip()
    s = re.sub(r'\s*=+\s*0\s*$', '', s)
    s = s.replace('^', '**')
    s = re.sub(r'√\s*([a-zA-Z0-9_.]+)', r'sqrt(\1)', s)  # √x -> sqrt(x)
    s = s.replace('√(', 'sqrt(')
    s = s.replace('÷', '/')

    # Agrupar fracciones en exponentes: **1/3, **-1/2 -> **(1/3), **(-1/2)
    s = re.sub(r'\*\*\s*([+-]?\d+)\s*/\s*([+-]?\d+)', r'**(\1/\2)', s)
    # Envolver exponentes negativos decimales o enteros: **-2.5 -> **(-2.5), **-3 -> **(-3)
    s = re.sub(r'\*\*\s*-\s*(\d+(?:\.\d+)?)', r'**(-\1)', s)

    return s

def pasar_funcion_a_callable(ecuacion_str: str):
    """
    Convierte la ecuación a f(x) 'numpy-safe'.
    Acepta: ln/log (natural), sin/cos/tan, sqrt, root, etc.
    Usa smoke test con array en 0.0 para evitar ZeroDivisionError.
    """
    x = sp.symbols('x')

    def _root_real_or_pow(a, n):
        """
        Maneja root(a,n):
        - n impar -> real_root(a,n) (permite a<0)
        - n par   -> a**(1/n) (rama principal)
        - n negativo -> 1/root(a,|n|)
        - n no entero literal -> a**(1/n)
        """
        try:
            n_int = int(n)
            if n_int == 0:
                raise ValueError("root(a, 0) no está definido.")
            if n_int < 0:
                n_pos = -n_int
                return 1 / (_root_real_or_pow(a, n_pos))
            if n_int % 2 == 1:
                return sp.real_root(a, n_int)
            return a**sp.Rational(1, n_int)
        except Exception:
            return a**(sp.Rational(1, n))

    local_dict = {
        'x': x,
        'e': sp.E, 'E': sp.E,
        'ln': sp.log,       # log natural
        'log': sp.log,      # natural si lo usan
        'root': _root_real_or_pow,
        'cbrt': lambda a: sp.real_root(a, 3),
        'sen': sp.sin,      # alias ES
        'tg': sp.tan,
        'sqrt': sp.sqrt,
    }

    ecuacion_normalizada = limpiar_ecuacion(ecuacion_str) if isinstance(ecuacion_str, str) else ecuacion_str
    expr = sp.sympify(ecuacion_normalizada, locals=local_dict)
    f = sp.lambdify(x, expr, modules=['numpy'])

    # Smoke test robusto: con array en 0.0 numpy devuelve inf/NaN, no levanta excepción
    try:
        _ = f(np.array([0.0]))
    except ZeroDivisionError:
        pass

    return f, str(expr)

# ==============================
# Utilidades numéricas/gráficas
# ==============================
def _limpiar_y(y: np.ndarray) -> np.ndarray:
    """Convierte complejos/infinitos en NaN y se queda con parte real."""
    y = np.array(y, dtype=np.complex128)
    y = np.where(np.abs(y.imag) > 1e-12, np.nan, y.real)
    y = np.where(~np.isfinite(y), np.nan, y)
    return y

def _ajustar_limites_y(y: np.ndarray, margen=0.1):
    """
    Limita el eje Y con percentiles (5–95) para evitar que una asíntota
    arruine la escala. Si todo es NaN, usa (-1,1).
    """
    yv = y[np.isfinite(y)]
    if yv.size == 0:
        return (-1, 1)
    p5, p95 = np.percentile(yv, [5, 95])
    if p5 == p95:
        p5 -= 1
        p95 += 1
    r = p95 - p5
    return (p5 - margen*r, p95 + margen*r)

def _elegir_rango_x(expr_str: str, preferencia=None, ampliar: float = 1.0, simetrico: float | None = None):
    """
    Heurística del rango X:
      1) preferencia=(xmin, xmax)
      2) simetrico -> [-simetrico, simetrico]
      3) si contiene log/sqrt/ln -> [0.01, 10], si no -> [-10, 10]
      4) aplica 'ampliar' (>1 escala el ancho)
    """
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

    ampliar = float(ampliar) if ampliar else 1.0
    if ampliar <= 0:
        ampliar = 1.0

    if xmin > 0:  # dominio positivo (log/sqrt)
        ancho = (xmax - xmin) * ampliar
        xmax = xmin + ancho
    else:
        centro = 0.5 * (xmin + xmax)
        semi = 0.5 * (xmax - xmin) * ampliar
        xmin, xmax = centro - semi, centro + semi

    return xmin, xmax

# ==============================
# Gráfica clara (solo función)
# ==============================
def inicio_grafica(ecuacion: str, rango_x=None, puntos=1600, titulo=None, ampliar: float = 1.0, simetrico: float | None = None):
    """
    Dibuja f(x) con:
      - Ejes X/Y marcados.
      - Manejo de discontinuidades (sin unir a través de NaN).
      - Escalado robusto del eje Y.
      - Evita evaluar exactamente en x=0 cuando hay potencias negativas.
    """
    f, expr_str = pasar_funcion_a_callable(ecuacion)
    x_min, x_max = _elegir_rango_x(expr_str, preferencia=rango_x, ampliar=ampliar, simetrico=simetrico)

    # Muestreo seguro con máscara de errores numéricos
    def muestrear_segmento(a, b, n):
        xx = np.linspace(a, b, int(max(2, n)))
        with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
            yy = _limpiar_y(f(xx))
        return xx, yy

    puntos = int(puntos)
    eps = 1e-9  # hueco mínimo alrededor de 0

    plt.figure(figsize=(9.5, 6.2))

    if x_min < 0 < x_max:
        # Partimos en dos para no evaluar x=0 con exponentes negativos
        n1 = max(2, puntos // 2)
        n2 = max(2, puntos - n1)
        x1, y1 = muestrear_segmento(x_min, -eps, n1)
        x2, y2 = muestrear_segmento(eps,  x_max, n2)
        plt.plot(x1, np.ma.masked_invalid(y1), linewidth=2, label=f"f(x) = {expr_str}")
        plt.plot(x2, np.ma.masked_invalid(y2), linewidth=2)
        y_all = np.concatenate([y1, y2])
    else:
        x, y = muestrear_segmento(x_min, x_max, puntos)
        plt.plot(x, np.ma.masked_invalid(y), linewidth=2, label=f"f(x) = {expr_str}")
        y_all = y

    # Ejes
    plt.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)
    plt.axvline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)

    # Límites Y robustos
    ymin, ymax = _ajustar_limites_y(y_all)
    plt.ylim(ymin, ymax)
    plt.xlim(x_min, x_max)

    # Estética limpia
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel("x", fontsize=11)
    plt.ylabel("f(x)", fontsize=11)
    plt.title(titulo or "Gráfica de la función", fontsize=13)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.show()

# ==============================
# PRUEBAS RÁPIDAS
# ==============================
if __name__ == "__main__":
    pruebas = [
        "x^-3",
        "x**-2.5",
        "x**-1/2",        # se normaliza a x**(-1/2)
        "ln(x) - 1",
        "root(x, -3)",    # recíproco de cúbica
        "root(-8, 3)",    # -2
    ]
    for s in pruebas:
        print("Graficando:", s)
        inicio_grafica(s, ampliar=3)
