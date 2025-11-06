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
    s = limpiar_ecuacion(ecuacion_str)
    local_dict = {
        'x': x,
        'e': sp.E, 'E': sp.E,
        'ln': sp.log,   # por si escriben ln(x)
        'log': sp.log,  # log natural
        'sen': sp.sin,  # alias en español
        'tg': sp.tan
    }
    expr = sp.sympify(s, locals=local_dict)
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

def _elegir_rango_x(expr_str: str, preferencia=None):
    """
    Heurística simple del rango X:
    - Si el usuario pasa (xmin, xmax) en preferencia, usarlo.
    - Si la expresión contiene log/sqrt, usar [0.01, 10].
    - En otro caso, [-10, 10].
    """
    if preferencia and len(preferencia) == 2:
        return float(preferencia[0]), float(preferencia[1])

    s = expr_str.lower()
    if ("log" in s) or ("sqrt" in s):
        return (0.01, 10.0)
    return (-10.0, 10.0)

# ==============================
# Gráfica clara (solo función)
# ==============================
def inicio_grafica(ecuacion: str, rango_x=None, puntos=1600, titulo=None):
    """
    Dibuja f(x) con:
      - Ejes X/Y marcados.
      - Manejo de discontinuidades (sin unir a través de NaN).
      - Escalado robusto del eje Y.
    Params:
      ecuacion: str, e.g. "ln(x) - 1", "e^x - 3", "x^3 - 4*x + 1"
      rango_x: (xmin, xmax) opcional; si no, elige heurístico.
      puntos: resolución del muestreo.
      titulo: título opcional.
    """
    f, expr_str = pasar_funcion_a_callable(ecuacion)
    x_min, x_max = _elegir_rango_x(expr_str, preferencia=rango_x)

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

# ==============================
# Ejemplos (quitar o comentar)
# ==============================
# graficar_funcion("ln(x) - 1")              # log natural
# graficar_funcion("e^x - 3")                # usa e = sp.E y ^ -> **
# graficar_funcion("x^3 - 4*x + 1", (-3, 3)) # rango personalizado
