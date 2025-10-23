# core/Cramer_simb.py
from typing import List, Dict, Any

# =====================================================
#   FUNCIONES AUXILIARES
# =====================================================

import re

import re

def simplificar_expr_simbolica(expr: str) -> str:
    """
    Simplifica expresiones simbólicas básicas sin usar SymPy.
    Reglas:
      - Quita dobles signos (-- → +, +- → -)
      - Reemplaza (a)·1 o 1·(a) por a
      - Reemplaza s·s por s²
      - Reemplaza · por * (para evitar errores como a7 o 23)
    """
    e = expr.replace(" ", "")

    # Quitar dobles signos redundantes
    e = e.replace("--", "+").replace("+-", "-").replace("-+", "-").replace("++", "+")

    # Simplificar multiplicaciones triviales
    e = re.sub(r"(\(?[a-zA-Z0-9]+\)?)·1", r"\1", e)
    e = re.sub(r"1·(\(?[a-zA-Z0-9]+\)?)", r"\1", e)

    # Reemplazar cuadrados repetidos (s·s → s²)
    e = re.sub(r"([a-zA-Z])·\1", r"\1²", e)

    # Reemplazar el punto medio por un asterisco
    e = e.replace("·", "*")

    # Reglas adicionales de limpieza visual
    e = e.replace(")*(", ")*(")  # evitar pegotes como )(

    return e


def fmt(x):
    """Formatea un valor simbólico, agregando paréntesis si tiene signos o letras."""
    if isinstance(x, str):
        x = x.strip()
        if any(op in x for op in ["+", "-", "/"]) and not (x.startswith("(") and x.endswith(")")):
            return f"({x})"
        return x
    return str(x)


def mult(a, b):
    """Multiplicación simbólica con paréntesis."""
    return f"{fmt(a)}·{fmt(b)}"


def resta(a, b):
    """Resta simbólica con paréntesis."""
    return f"{fmt(a)} - {fmt(b)}"


def minor(M, i, j):
    """Devuelve el menor eliminando fila i y columna j."""
    return [[M[r][c] for c in range(len(M)) if c != j] for r in range(len(M)) if r != i]


def det2(B):
    """Determinante 2x2 simbólico."""
    a, b = B[0]
    c, d = B[1]
    return f"{fmt(a)}·{fmt(d)} - {fmt(b)}·{fmt(c)}"


def det_rec(M, pasos=None, nivel=0):
    """Calcula el determinante simbólicamente (sin evaluar)."""
    if pasos is None:
        pasos = []
    n = len(M)
    if n == 1:
        return fmt(M[0][0])
    if n == 2:
        det_text = det2(M)
        pasos.append("  " * nivel + f"det(M) = {det_text}")
        return det_text

    expansion = []
    for j in range(n):
        aij = M[0][j]
        signo = "+" if j % 2 == 0 else "-"
        Mij = minor(M, 0, j)
        detM = det_rec(Mij, pasos, nivel + 1)
        expansion.append(f"{signo}{fmt(aij)}·({detM})")

    det_text = " ".join(expansion)
    pasos.append("  " * nivel + f"det(M) = {det_text}")
    return det_text


def matriz_con_columna_reemplazada(A: List[List[Any]], col_idx: int, b: List[Any]) -> List[List[Any]]:
    """Reemplaza una columna por b."""
    B = []
    for i in range(len(A)):
        fila = list(A[i])
        fila[col_idx] = b[i]
        B.append(fila)
    return B


def fmt_matriz(M: List[List[Any]]) -> List[str]:
    """Formatea la matriz con corchetes."""
    if not M:
        return ["[]"]
    cols = len(M[0])
    widths = [max(len(fmt(M[r][c])) for r in range(len(M))) for c in range(cols)]
    lines = []
    for i, fila in enumerate(M):
        celdas = [fmt(fila[c]).rjust(widths[c]) for c in range(cols)]
        if i == 0:
            lines.append("⎡ " + "  ".join(celdas) + " ⎤")
        elif i == len(M) - 1:
            lines.append("⎣ " + "  ".join(celdas) + " ⎦")
        else:
            lines.append("⎢ " + "  ".join(celdas) + " ⎥")
    return lines

# =====================================================
#   FUNCIÓN PRINCIPAL
# =====================================================

def resolver_sistema_Cramer_simb(Aum_raw: List[List[str]]) -> Dict[str, Any]:
    """
    Resuelve un sistema simbólico con el método de Cramer (texto).
    Devuelve:
      - pasos: List[str]
      - tipo_solucion: "simbólico"
      - soluciones: List[str]
      - mensaje_tipo: str
    """
    pasos = []
    n = len(Aum_raw)
    if n == 0:
        return {"pasos": ["Matriz vacía."], "tipo_solucion": None}

    A = [fila[:-1] for fila in Aum_raw]
    b = [fila[-1] for fila in Aum_raw]
    nombres = [f"x{i+1}" for i in range(n)]

    pasos.append("Matriz A y vector b extraídos:")
    pasos.append("A:")
    pasos.extend("  " + ln for ln in fmt_matriz(A))
    pasos.append(f"b = [{', '.join(fmt(x) for x in b)}]")
    pasos.append("")

    # --- Determinante principal ---
    pasos.append("1) Cálculo de det(A):")
    pasos_detA = []
    detA = det_rec(A, pasos_detA)
    pasos.extend("  " + ln for ln in pasos_detA)
    pasos.append(f"det(A) = {detA}")
    pasos.append("")

    # --- Determinantes A_j ---
    soluciones = []
    for j in range(n):
        pasos.append(f"2.{j+1}) Matriz A_{j+1} (reemplazando columna {j+1} por b):")
        Aj = matriz_con_columna_reemplazada(A, j, b)
        pasos.extend("  " + ln for ln in fmt_matriz(Aj))
        pasos.append(f"  Determinante de A_{j+1}:")
        pasos_detAj = []
        detAj = det_rec(Aj, pasos_detAj)
        pasos.extend("    " + ln for ln in pasos_detAj)
        pasos.append(f"  det(A_{j+1}) = {detAj}")
        pasos.append("")

        expr_bruta = f"({detAj}) / ({detA})"
        expr_simplificada = simplificar_expr_simbolica(expr_bruta)

        pasos.append(f"  {nombres[j]} = {expr_simplificada}")
        soluciones.append(expr_simplificada)
        pasos.append("")

    mensaje = "Sistema simbólico resuelto mediante Cramer."
    pasos.append("CONCLUSIÓN:")
    pasos.append("  " + mensaje)
    for i, var in enumerate(nombres):
        pasos.append(f"  {var} = {soluciones[i]}")

    return {
        "pasos": pasos,
        "tipo_solucion": "simbólico",
        "soluciones": soluciones,
        "mensaje_tipo": mensaje,
    }
