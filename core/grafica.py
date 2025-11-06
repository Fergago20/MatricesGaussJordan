import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import re

# ==============================
# Limpieza y parsing seguro
# ==============================
def limpiar_ecuacion(ecuacion_str: str) -> str:
    """
    Normaliza lo mínimo para Sympy:
    - Elimina '=0' al final si existe.
    - ^ -> ** (potencias).
    - √x -> sqrt(x) y '÷' -> '/'.
    Nota: 'ln' y 'log' quedan como log natural. 'e' se mapea a sp.E.
    """
    s = ecuacion_str.strip()
    s = re.sub(r'\s*=+\s*0\s*$', '', s)   # quita '=0' al final
    s = s.replace('^', '**')
    s = re.sub(r'√\s*([a-zA-Z0-9_.]+)', r'sqrt(\1)', s)  # √x -> sqrt(x)
    s = s.replace('√(', 'sqrt(')
    s = s.replace('÷', '/')
    return s

def pasar_funcion_a_callable(ecuacion_str: str):
    """
    Convierte la ecuación a f(x) 'numpy-safe'.
    Acepta: ln/log (natural), sin/cos/tan, sqrt, etc.
    """
    x = sp.symbols('x')

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


    if isinstance(ecuacion_str, str):
        ecuacion_normalizada =limpiar_ecuacion(ecuacion_str)
    else:
        ecuacion_normalizada = ecuacion_str
    expr = sp.sympify(ecuacion_normalizada, locals=local_dict)
    f = sp.lambdify(x, expr, modules=['numpy'])
    # check mínima
    _ = f(0.0)  # no importa si da nan, solo que la llamada funcione
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
    Prioridad:
      1) preferencia=(xmin, xmax)
      2) simetrico -> [-simetrico, simetrico]
      3) heurística por tipo de función
         - si contiene log/sqrt -> [0.01, 10]
         - si no -> [-10, 10]
    Luego aplica 'ampliar' (>1 escala el ancho).
    Para dominios positivos no extiende a negativos: solo aumenta el máximo.
    """
    if preferencia and len(preferencia) == 2:
        return float(preferencia[0]), float(preferencia[1])

    s = expr_str.lower()

    # Opción simétrica explícita
    if simetrico is not None:
        R = float(simetrico)
        return -R, R

    # Base por heurística
    if ("log" in s) or ("sqrt" in s) or ("ln" in s):
        xmin, xmax = 0.01, 10.0
    else:
        xmin, xmax = -10.0, 10.0

    # Aplicar factor 'ampliar'
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
    Params:
      ecuacion: str, e.g. "ln(x) - 1", "e^x - 3", "x^3 - 4*x + 1"
      rango_x: (xmin, xmax) opcional (tiene prioridad).
      puntos: resolución del muestreo.
      titulo: título opcional.
      ampliar: factor para ampliar el rango heurístico (ej. 5 => 5x más ancho).
      simetrico: si se da, fuerza rango [-simetrico, simetrico].
    """
    f, expr_str = pasar_funcion_a_callable(ecuacion)
    x_min, x_max = _elegir_rango_x(expr_str, preferencia=rango_x, ampliar=ampliar, simetrico=simetrico)

    x = np.linspace(x_min, x_max, int(puntos))
    y = _limpiar_y(f(x))

    # Evitar líneas a través de discontinuidades: máscara NaN
    y_masked = np.ma.masked_invalid(y)

    plt.figure(figsize=(9.5, 6.2))
    plt.plot(x, y_masked, linewidth=2, label=f"f(x) = {expr_str}")

    # Ejes
    plt.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)
    plt.axvline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)

    # Límites Y robustos
    ymin, ymax = _ajustar_limites_y(y)
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


"""# ==============================
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import re

# ==============================
# Limpieza y parsing seguro
# ==============================
def limpiar_ecuacion(ecuacion_str: str) -> str:
    s = ecuacion_str.strip()
    s = re.sub(r'\s*=+\s*0\s*$', '', s)   # quita '=0' al final
    s = s.replace('^', '**')
    s = re.sub(r'√\s*([a-zA-Z0-9_.]+)', r'sqrt(\1)', s)  # √x -> sqrt(x)
    s = s.replace('√(', 'sqrt(')
    s = s.replace('÷', '/')
    return s

def pasar_funcion_a_callable(ecuacion_str: str):
    x = sp.symbols('x')

    def _root_real_or_pow(a, n):
        try:
            n_int = int(n)
            if n_int % 2 == 1:           # impar -> raíz real (acepta a<0)
                return sp.real_root(a, n_int)
            else:                         # par -> potencia fraccionaria simbólica
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
        'tg': sp.tan
    }

    ecuacion_normalizada = limpiar_ecuacion(ecuacion_str) if isinstance(ecuacion_str, str) else ecuacion_str
    expr = sp.sympify(ecuacion_normalizada, locals=local_dict)
    f = sp.lambdify(x, expr, modules=['numpy'])
    _ = f(0.0)  # smoke test
    return f, str(expr)

# ==============================
# Utilidades numéricas/gráficas
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
        p5 -= 1
        p95 += 1
    r = p95 - p5
    return (p5 - margen*r, p95 + margen*r)

def _elegir_rango_x(expr_str: str, preferencia=None):
    
    Heurística base (luego forzaremos cubrir [-100,100]):
    - preferencia si viene
    - si hay log/sqrt/ln => [0.01, 10]
    - si no => [-10, 10]

    if preferencia and len(preferencia) == 2:
        return float(preferencia[0]), float(preferencia[1])

    s = expr_str.lower()
    if ("log" in s) or ("sqrt" in s) or ("ln" in s):
        return (0.01, 10.0)
    return (-10.0, 10.0)

def _forzar_cobertura_x(xmin: float, xmax: float, cover=(-100.0, 100.0)):
    Expande [xmin, xmax] para cubrir al menos cover=(cmin,cmax
    cmin, cmax = cover
    if xmin > cmin:
        xmin = cmin
    if xmax < cmax:
        xmax = cmax
    return xmin, xmax

# ==============================
# Gráfica clara (solo función)
# ==============================
def inicio_grafica(ecuacion: str, rango_x=None, puntos=1600, titulo=None, cubrir=(-100.0, 100.0)):
    
    Dibuja f(x) y asegura cubrir como mínimo el rango 'cubrir' (por defecto [-100,100]).
    - Maneja discontinuidades (NaN) sin unir la curva.
    - Autoscale robusto en Y.
    
    f, expr_str = pasar_funcion_a_callable(ecuacion)
    x_min, x_max = _elegir_rango_x(expr_str, preferencia=rango_x)
    x_min, x_max = _forzar_cobertura_x(x_min, x_max, cover=cubrir)

    # Aumenta puntos si el rango es muy grande para que se vea suave
    ancho = max(1.0, x_max - x_min)
    puntos_finales = max(int(puntos), int(min(20000, ancho * 20)))  # ~20 pts por unidad, tope 20k

    x = np.linspace(x_min, x_max, puntos_finales)
    y = _limpiar_y(f(x))
    y_masked = np.ma.masked_invalid(y)  # no unir a través de NaN

    plt.figure(figsize=(10.5, 6.5))
    plt.plot(x, y_masked, linewidth=2, label=f"f(x) = {expr_str}")

    # Ejes
    plt.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)
    plt.axvline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)

    # Límites Y robustos
    ymin, ymax = _ajustar_limites_y(y)
    plt.ylim(ymin, ymax)
    plt.xlim(x_min, x_max)

    # Estética
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel("x", fontsize=11)
    plt.ylabel("f(x)", fontsize=11)
    plt.title(titulo or f"Gráfica de la función (x ∈ [{x_min:.0f}, {x_max:.0f}])", fontsize=13)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.show()
"""
