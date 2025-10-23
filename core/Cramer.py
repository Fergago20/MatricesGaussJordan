from fractions import Fraction
from typing import List, Any, Dict, Optional

# ------------------------------------------------------------
# Utilidades de formato
# ------------------------------------------------------------
def _to_frac(x: Any) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    if isinstance(x, float):
        return Fraction(x).limit_denominator()
    try:
        return Fraction(x)
    except Exception:
        return Fraction(str(x))

def _fmt_num(x: Fraction) -> str:
    x = _to_frac(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

def _fmt_vector(v: List[Any]) -> str:
    return "[" + ", ".join(_fmt_num(_to_frac(x)) for x in v) + "]"

def _fmt_matriz_bloque(M: List[List[Any]]) -> List[str]:
    if not M:
        return ["[]"]
    str_rows = [[_fmt_num(_to_frac(x)) for x in fila] for fila in M]
    widths = [max(len(str_rows[i][j]) for i in range(len(M))) for j in range(len(M[0]))]
    def fmt_row(r):
        return "  ".join(s.rjust(widths[j]) for j, s in enumerate(r))
    if len(M) == 1:
        return ["⎡ " + fmt_row(str_rows[0]) + " ⎤"]
    lines = ["⎡ " + fmt_row(str_rows[0]) + " ⎤"]
    for r in str_rows[1:-1]:
        lines.append("⎢ " + fmt_row(r) + " ⎥")
    lines.append("⎣ " + fmt_row(str_rows[-1]) + " ⎦")
    return lines

def _matriz_con_columna_reemplazada(A: List[List[Any]], col_idx: int, b: List[Any]) -> List[List[Fraction]]:
    A_fr = [[_to_frac(x) for x in fila] for fila in A]
    b_fr = [_to_frac(x) for x in b]
    B = []
    for i in range(len(A_fr)):
        fila = list(A_fr[i])
        fila[col_idx] = b_fr[i]
        B.append(fila)
    return B

# ------------------------------------------------------------
# Importa tu determinante por cofactores
# ------------------------------------------------------------
from core.determinante_matriz import determinante_cofactores

# ------------------------------------------------------------
# Kramer desde matriz aumentada [A|b]
# ------------------------------------------------------------
def resolver_sistema_Cramer_desde_aumentada(
    Aum_raw: List[List[Any]],
    nombres: Optional[List[str]] = None,
    expandir_por: str = "fila",
    indice_expansion: int = 0
) -> Dict[str, Any]:
    """
    Resuelve un sistema lineal usando Kramer a partir de la matriz aumentada [A|b].

    Parámetros
    ----------
    Aum_raw : lista de listas
        Matriz aumentada de tamaño n x (n+1). Las primeras n columnas son A y la última es b.
    nombres : lista opcional de nombres de variables (['x1', 'x2', ...] por defecto)
    expandir_por : 'fila' o 'columna' (cómo expandir los cofactores en el reporte)
    indice_expansion : índice base 0 de la fila/columna para la expansión

    Retorna
    -------
    dict con claves:
      "pasos": List[str]
      "rref": None
      "tipo_solucion": "única" | "sin_solucion" | "infinitas" | None
      "soluciones": [] | None
      "mensaje_tipo": str
      "solucion_parametrica": None
    """
    pasos: List[str] = []
    rref = None

    # -------- Validaciones y partición [A|b] --------
    if not Aum_raw or not Aum_raw[0]:
        return {
            "pasos": ["La matriz aumentada está vacía."],
            "rref": None,
            "tipo_solucion": None,
            "soluciones": None,
            "mensaje_tipo": "Entrada vacía.",
            "solucion_parametrica": None,
        }

    filas = len(Aum_raw)
    cols = len(Aum_raw[0])
    # Todas las filas deben tener el mismo número de columnas
    if any(len(f) != cols for f in Aum_raw):
        return {
            "pasos": ["La matriz aumentada tiene filas con longitudes distintas."],
            "rref": None,
            "tipo_solucion": None,
            "soluciones": None,
            "mensaje_tipo": "Filas de diferente tamaño.",
            "solucion_parametrica": None,
        }

    # Estructura n x (n+1)
    if cols != filas + 1:
        return {
            "pasos": [f"La matriz aumentada debe ser de tamaño n x (n+1). Recibido: {filas} x {cols}."],
            "rref": None,
            "tipo_solucion": None,
            "soluciones": None,
            "mensaje_tipo": "Dimensiones incompatibles para Kramer desde aumentada.",
            "solucion_parametrica": None,
        }

    n = filas
    A = [[_to_frac(x) for x in fila[:-1]] for fila in Aum_raw]
    b = [_to_frac(fila[-1]) for fila in Aum_raw]

    # Nombres de variables
    if not nombres or len(nombres) != n:
        nombres = [f"x{i+1}" for i in range(n)]

    # Mostrar A y b por separado
    pasos.append("Matriz A y vector b extraídos:")
    pasos.append("A:")
    pasos.extend("  " + ln for ln in _fmt_matriz_bloque(A))
    pasos.append(f"\nb: {_fmt_vector(b)}")
    pasos.append(f"Variables: {', '.join(nombres)}")
    pasos.append("")

    # -------- det(A) por cofactores --------
    detA_info = determinante_cofactores(A, expandir_por=expandir_por, indice=indice_expansion)
    detA = detA_info["det"]
    pasos.append("1) Cálculo de det(A) por cofactores:")
    pasos.extend("  " + ln for ln in detA_info["reporte"].splitlines())
    pasos.append(f"Resultado: det(A) = {_fmt_num(detA)}")
    pasos.append("")

    # -------- Casos según det(A) --------
    if detA != 0:
        soluciones = []
        for j in range(n):
            Aj = _matriz_con_columna_reemplazada(A, j, b)
            pasos.append(f"2.{j+1}) Matriz A_{j+1} (reemplazando columna {j+1} por b):")
            pasos.extend("  " + ln for ln in _fmt_matriz_bloque(Aj))
            pasos.append(f"  Determinante de A_{j+1}:")
            detAj_info = determinante_cofactores(Aj, expandir_por=expandir_por, indice=indice_expansion)
            detAj = detAj_info["det"]
            pasos.extend("    " + ln for ln in detAj_info["reporte"].splitlines())
            pasos.append(f"  Resultado: det(A_{j+1}) = {_fmt_num(detAj)}")
            xj = detAj / detA
            soluciones.append(xj)
            pasos.append(f"  {nombres[j]} = det(A_{j+1}) / det(A) = {_fmt_num(detAj)} / {_fmt_num(detA)} = {_fmt_num(xj)}")
            pasos.append("")

        mensaje = "Como det(A) ≠ 0, el sistema tiene solución única."
        pasos.append("CONCLUSIÓN:")
        pasos.append("  " + mensaje)
        for i, var in enumerate(nombres):
            pasos.append(f"  {var} = {_fmt_num(soluciones[i])}")

        return {
            "pasos": pasos,
            "rref": rref,
            "tipo_solucion": "única",
            "soluciones": soluciones,
            "mensaje_tipo": mensaje,
            "solucion_parametrica": None,
        }

    # det(A) = 0 → revisar A_j
    pasos.append("Como det(A) = 0, verificamos los determinantes A_j para decidir el tipo de solución.")
    detAjs = []
    algun_no_cero = False
    for j in range(n):
        Aj = _matriz_con_columna_reemplazada(A, j, b)
        pasos.append(f"3.{j+1}) Matriz A_{j+1} (reemplazando columna {j+1} por b):")
        pasos.extend("  " + ln for ln in _fmt_matriz_bloque(Aj))
        pasos.append(f"  Determinante de A_{j+1}:")
        detAj_info = determinante_cofactores(Aj, expandir_por=expandir_por, indice=indice_expansion)
        detAj = detAj_info["det"]
        detAjs.append(detAj)
        if detAj != 0:
            algun_no_cero = True
        pasos.extend("    " + ln for ln in detAj_info["reporte"].splitlines())
        pasos.append(f"  Resultado: det(A_{j+1}) = {_fmt_num(detAj)}")
        pasos.append("")

    if algun_no_cero:
        mensaje = (
            "det(A) = 0 pero existe al menos un det(A_j) ≠ 0. "
            "El sistema es incompatible (no tiene solución)."
        )
        pasos.append("CONCLUSIÓN:")
        pasos.append("  " + mensaje)
        return {
            "pasos": pasos,
            "rref": rref,
            "tipo_solucion": "sin_solucion",
            "soluciones": None,
            "mensaje_tipo": mensaje,
            "solucion_parametrica": None,
        }

    mensaje = (
        "det(A) = 0 y det(A_j) = 0 para todo j. "
        "El sistema es compatible indeterminado (infinitas soluciones). "
        "Kramer no produce la parametrización."
    )
    pasos.append("CONCLUSIÓN:")
    pasos.append("  " + mensaje)
    return {
        "pasos": pasos,
        "rref": rref,
        "tipo_solucion": "infinitas",
        "soluciones": None,
        "mensaje_tipo": mensaje,
        "solucion_parametrica": None,
    }
