"""
Eliminación de Gauss (sin Gauss-Jordan):
- Construye REF registrando operaciones de fila.
- Clasifica: única / infinita / sin solución (por rangos).
- Si es única: sustitución hacia atrás **paso a paso**.

Este módulo NO maneja entradas de texto ni UI.
"""
from fractions import Fraction
from typing import List, Tuple, Dict, Any
from soporte import (
    matriz_alineada, matriz_alineada_con_titulo, encabezado_operacion,
    formatear_ecuacion_linea, fraccion_a_str, bloque_matriz   # <<< añade bloque_matriz
)


def _copiar(m):
    return [fila.copy() for fila in m]

def _fr_str(fr: Fraction) -> str:
    return fraccion_a_str(fr)

def _rango_por_ref(ref: List[List[Fraction]], incluir_b: bool, nvars: int) -> int:
    cols = nvars + (1 if incluir_b else 0)
    r = 0
    for fila in ref:
        if any(val != 0 for val in fila[:cols]):
            r += 1
    return r

def _a_ref_con_pasos(matriz_aumentada: List[List[Fraction]]) -> Tuple[List[str], List[List[Fraction]], List[int]]:
    m = _copiar(matriz_aumentada)
    pasos: List[str] = []
    filas = len(m)
    cols_a = len(m[0]) - 1
    fila_act = 0
    cols_pivote: List[int] = []

    for col in range(cols_a):
        fila_pivote = None
        for f in range(fila_act, filas):
            if m[f][col] != 0:
                fila_pivote = f
                break
        if fila_pivote is None:
            continue

        if fila_pivote != fila_act:
            m[fila_act], m[fila_pivote] = m[fila_pivote], m[fila_act]
            pasos.append(encabezado_operacion(f"Permutar: F{fila_act+1} ↔ F{fila_pivote+1}"))
            pasos.append(bloque_matriz(m))

        pivote = m[fila_act][col]
        cols_pivote.append(col)

        for f in range(fila_act+1, filas):
            if m[f][col] == 0:
                continue
            factor = Fraction(m[f][col], pivote)
            pasos.append(encabezado_operacion(
                f"F{f+1} ← F{f+1} + ({_fr_str(-factor)})·F{fila_act+1}"
            ))
            for c in range(col, cols_a+1):
                m[f][c] = m[f][c] - factor*m[fila_act][c]
            pasos.append(bloque_matriz(m))

        fila_act += 1
        if fila_act == filas:
            break

    pasos.append(matriz_alineada_con_titulo("Matriz en forma escalonada (REF):", m, con_barra=True))
    return pasos, m, cols_pivote

def _sustitucion_con_pasos(ref: List[List[Fraction]], cols_pivote: List[int], nvars: int):
    pasos: List[str] = []
    pasos.append("\nSustitución hacia atrás:\n")
    x = [Fraction(0,1) for _ in range(nvars)]

    for k_rev in reversed(range(len(cols_pivote))):
        col = cols_pivote[k_rev]
        fila = k_rev

        pasos.append(f"Ecuación F{fila+1}: {formatear_ecuacion_linea(ref[fila])}")

        b_k = ref[fila][nvars]
        a_kk = ref[fila][col]

        simb = f"x{col+1} = ( {_fr_str(b_k)}"
        hay = False
        for c in range(col+1, nvars):
            coef = ref[fila][c]
            if coef != 0:
                simb += f" - ({_fr_str(coef)}*x{c+1})"
                hay = True
        simb += f" ) / {_fr_str(a_kk)}"
        pasos.append(simb)

        if hay:
            sub = f"x{col+1} = ( {_fr_str(b_k)}"
            for c in range(col+1, nvars):
                coef = ref[fila][c]
                if coef != 0:
                    sub += f" - ({_fr_str(coef)}*{_fr_str(x[c])})"
            sub += f" ) / {_fr_str(a_kk)}"
            pasos.append("Sustituyendo valores: " + sub)

        numerador = b_k
        for c in range(col+1, nvars):
            numerador -= ref[fila][c]*x[c]
        pasos.append(f"x{col+1} = ( {_fr_str(numerador)} ) / {_fr_str(a_kk)}")

        valor = numerador / a_kk
        x[col] = valor
        pasos.append(f"x{col+1} = {_fr_str(valor)}\n")

    return x, pasos

def _solucion_parametrica(ref, cols_pivote, nvars):
    """
    Devuelve una lista de expresiones simbólicas para cada variable:
    expr[i] = {"const": Fraction, "terms": {j: Fraction}} donde j son variables libres.
    Para variable libre j: const=0, terms={j:1}.
    """
    from fractions import Fraction
    expr = [None] * nvars
    libres = [j for j in range(nvars) if j not in cols_pivote]

    # variables libres como identidad
    for j in libres:
        expr[j] = {"const": Fraction(0,1), "terms": {j: Fraction(1,1)}}

    # recorrer pivotes de abajo hacia arriba
    for k_rev in reversed(range(len(cols_pivote))):
        col = cols_pivote[k_rev]
        fila = k_rev
        a_kk = ref[fila][col]
        b_k  = ref[fila][nvars]

        # x_col = b_k/a_kk  -  sum_{c>col} (a_kc/a_kk) * x_c
        const = b_k / a_kk
        terms = {}

        for c in range(col+1, nvars):
            a_kc = ref[fila][c]
            if a_kc == 0:
                continue
            factor = a_kc / a_kk
            # restar factor * expr[c]
            ec = expr[c]
            if ec is None:
                # si no es libre, debe haberse calculado como pivote a la derecha
                # (por el orden de recorrido). En ese caso ec existe.
                ec = {"const": Fraction(0,1), "terms": {}}
            const -= factor * ec["const"]
            for var, coef in ec["terms"].items():
                terms[var] = terms.get(var, Fraction(0,1)) - factor * coef

        expr[col] = {"const": const, "terms": terms}

    return expr, libres

def _formatear_parametrica(expr, indice_variable):
    """
    Devuelve la línea 'xk = ...' usando fracciones y variables libres (xj),
    o 'xk es libre' si corresponde.
    """
    from fractions import Fraction
    const = expr.get("const", Fraction(0,1))
    terms = expr.get("terms", {})

    if terms == {indice_variable: Fraction(1,1)} and const == 0:
        return f"x{indice_variable+1} es libre"

    partes = []
    # constante
    if const != 0:
        partes.append(fraccion_a_str(const))

    # términos con variables libres en orden
    for var in sorted(terms.keys()):
        coef = terms[var]
        if coef == 0:
            continue
        signo = " - " if coef < 0 else (" + " if partes else "")
        abs_txt = fraccion_a_str(abs(coef))
        partes.append(f"{signo}{abs_txt}x{var+1}")

    if not partes:
        partes = ["0"]

    return f"x{indice_variable+1} = {''.join(partes)}"

# --- MODIFICADA: función principal ----------------------------------------

def clasificar_y_resolver(matriz_aumentada: List[List[Fraction]]) -> Dict[str, Any]:
    pasos, ref, cols_pivote = _a_ref_con_pasos(matriz_aumentada)
    nvars = len(matriz_aumentada[0]) - 1

    rango_a  = _rango_por_ref(ref, incluir_b=False, nvars=nvars)
    rango_ab = _rango_por_ref(ref, incluir_b=True,  nvars=nvars)

    resultado = {"pasos": pasos, "ref": ref, "tipo_solucion": None,
                 "soluciones": None, "mensaje_tipo": "", "solucion_parametrica": None}

    if rango_a < rango_ab:
        resultado["tipo_solucion"] = "inconsistente"
        resultado["mensaje_tipo"] = "Sin solución (sistema incompatible): rango(A) < rango([A|b])."
        return resultado

    if rango_a == rango_ab == nvars:
        soluciones, pasos_subs = _sustitucion_con_pasos(ref, cols_pivote, nvars)
        resultado["tipo_solucion"] = "única"
        resultado["soluciones"] = soluciones
        resultado["mensaje_tipo"] = "Solución única (sistema compatible determinado)."
        resultado["pasos"].extend(pasos_subs)
        return resultado

    # Caso de infinitas soluciones: construir solución paramétrica en x_j libres
    exprs, libres = _solucion_parametrica(ref, cols_pivote, nvars)
    lineas = []
    for i in range(nvars):
        lineas.append(_formatear_parametrica(exprs[i], i))

    resultado["tipo_solucion"] = "infinita"
    resultado["mensaje_tipo"] = "Infinitas soluciones (sistema compatible indeterminado)."
    resultado["solucion_parametrica"] = lineas
    return resultado
