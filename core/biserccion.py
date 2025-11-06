import sympy as sp
import numpy as np
import re

x = sp.Symbol('x')


# ============================================================
# LIMPIEZA Y NORMALIZACIÓN DE LA ECUACIÓN
# ============================================================
def limpiar_ecuacion(ecuacion_str: str):
    """Limpia y adapta la ecuación ingresada por el usuario para que Sympy la entienda correctamente."""
    if not ecuacion_str or not isinstance(ecuacion_str, str):
        raise ValueError("Ecuación vacía o inválida.")

    # 🔹 Eliminar caracteres invisibles y símbolos raros
    f = (
        ecuacion_str
        .replace("\u200b", "")
        .replace("\xa0", "")
        .replace("\r", "")
        .replace("\n", "")
        .replace("–", "-")   # guion largo
        .replace("−", "-")   # símbolo de resta unicode
        .replace("⁻", "-")   # superíndice menos
        .strip()
    )

    # 🔹 Eliminar espacios
    f = f.replace(" ", "")

    # 🔹 Reemplazos comunes
    reemplazos = {
        "sen": "sin",
        "√": "sqrt",
        "π": "pi",
        "^": "**",
        "²": "**2",
        "³": "**3",
    }
    for k, v in reemplazos.items():
        f = f.replace(k, v)

    # 🔹 ln(x) -> log(x)
    f = re.sub(r"\bln\(?([^)]+)\)?", r"log(\1)", f)

    # 🔹 log(x,base) -> log(x)/log(base)
    f = re.sub(r"log\(([^,]+),([^)]+)\)", r"log(\1)/log(\2)", f)

    # 🔹 e^x o e^-x -> exp(x)
    f = re.sub(r"e\^\(?([^)]+)\)?", r"exp(\1)", f)

    # 🔹 Multiplicación implícita
    f = re.sub(r"(\d)([a-zA-Z\(])", r"\1*\2", f)
    f = f.replace(")(", ")*(")

    # 🔹 Eliminar "=0"
    f = f.replace("=0", "").replace("==0", "").replace("=", "")

    return f

# ============================================================
# CREACIÓN DE FUNCIÓN NUMÉRICA SEGURA
# ============================================================
def crear_funcion(ecuacion_str):
    """Convierte el string limpio en una función numérica evaluable."""
    try:
        expr = sp.sympify(
            ecuacion_str,
            locals={
                "log": sp.log,
                "exp": sp.exp,
                "pi": sp.pi,
                "sin": sp.sin,
                "cos": sp.cos,
                "tan": sp.tan,
                "sqrt": sp.sqrt,
            },
        )
        return expr, sp.lambdify(x, expr, "numpy")
    except Exception as e:
        raise ValueError(f"No se pudo interpretar la ecuación. Revisa la sintaxis.\n\nDetalles: {e}")


# ============================================================
# EVALUACIÓN NUMÉRICA
# ============================================================
def f(funcion, val):
    """Evalúa la función numérica de forma segura."""
    try:
        resultado = funcion(val)
        if np.isnan(resultado) or np.isinf(resultado):
            raise ValueError(f"Valor indefinido al evaluar f({val}).")
        return float(resultado)
    except Exception as e:
        raise ValueError(f"No se pudo evaluar f({val}). Detalles: {e}")


# ============================================================
# MÉTODO DE BISECCIÓN
# ============================================================
def metodo_biseccion(ecuacion_str, a, b, tolerancia=1e-6, max_iter=1000):
    """
    Aplica el método de bisección a la ecuación dada.
    Recibe la ecuación tal como fue escrita (por ejemplo: ln(x) - e^-x = 0).
    """
    ecuacion_limpia = limpiar_ecuacion(ecuacion_str)
    expr, f_callable = crear_funcion(ecuacion_limpia)

    a, b = float(a), float(b)
    fa, fb = f(f_callable, a), f(f_callable, b)

    if fa * fb > 0:
        raise ValueError("La función no cambia de signo en el intervalo dado. Intenta con otro intervalo.")

    iteraciones = 0
    resultados = []

    while iteraciones < max_iter:
        iteraciones += 1
        c = (a + b) / 2
        fc = f(f_callable, c)
        error = abs(b - a) / 2

        resultados.append([
            iteraciones,
            round(a, 6),
            round(b, 6),
            round(c, 6),
            round(fa, 6),
            round(fb, 6),
            round(fc, 6)
        ])

        if abs(fc) < tolerancia or error < tolerancia:
            return c, iteraciones, resultados

        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc

    raise ValueError("El método no converge tras el número máximo de iteraciones.")

"""
# ============================================================
# PRUEBAS DE EJEMPLO
# ============================================================
if __name__ == "__main__":
    ejemplos = [
        ("cos(x) - x = 0", 0, 1),
        ("ln(x) - e^-x = 0", 0.5, 2),
        ("log(x,10) - x^2 + 1 = 0", 0.1, 2),
        ("x^4 - 5x^3 + 0.5x^2 - 11x + 10 = 0", 0, 3),
        ("sqrt(x) - 3 = 0", 1, 10),
        ("x^-2 - 0.5 = 0", 1, 3),
        ("sin(x) - 0.5 = 0", 0, 2),
        ("log(x,2) - 3 = 0", 1, 10),
    ]

    for ecuacion, a, b in ejemplos:
        print(f"\n=== Resolviendo: {ecuacion} en [{a}, {b}] ===")
        try:
            metodo_biseccion(ecuacion, a, b, tolerancia=1e-6)
        except Exception as e:
            print(f"❌ Error: {e}")"""
