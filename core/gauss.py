# core/gauss.py
from fractions import Fraction
from typing import List, Tuple, Dict, Any
from soporte.formato_matrices import matriz_alineada_con_titulo
from soporte.validaciones import fraccion_a_str

# =====================================================
#     FUNCIONES AUXILIARES INTERNAS
# =====================================================

def _copiar(matriz):
    """Devuelve una copia profunda de la matriz."""
    return [fila.copy() for fila in matriz]


def _fr(fr: Fraction) -> str:
    """Convierte una fracción a texto legible (entero o a/b)."""
    return fraccion_a_str(fr)


def _a_ref_con_pasos(matriz_aumentada: List[List[Fraction]]) -> Tuple[List[str], List[List[Fraction]], List[int]]:
    """
    Lleva una matriz aumentada [A|b] a su forma escalonada (REF)
    mostrando solo las operaciones que modifican la matriz:
    - Permutar filas (si ocurre)
    - Eliminaciones debajo del pivote
    """
    m = _copiar(matriz_aumentada)
    filas = len(m)
    columnas_a = len(m[0]) - 1
    fila_pivote = 0
    columnas_pivote: List[int] = []
    pasos: List[str] = []

    for col in range(columnas_a):
        # Buscar el pivote (primer no cero desde fila_pivote)
        fila_encontrada = None
        for f in range(fila_pivote, filas):
            if m[f][col] != 0:
                fila_encontrada = f
                break
        if fila_encontrada is None:
            continue  # columna libre, sin pivote

        # Permutar si es necesario
        if fila_encontrada != fila_pivote:
            m[fila_pivote], m[fila_encontrada] = m[fila_encontrada], m[fila_pivote]
            pasos.append(f"\nPermutar filas: F{fila_pivote+1} ↔ F{fila_encontrada+1}")
            pasos.append(matriz_alineada_con_titulo("", m, con_barra=True))

        columnas_pivote.append(col)
        pivote = m[fila_pivote][col]

        # Eliminar debajo del pivote (Gauss clásico)
        for r in range(fila_pivote + 1, filas):
            if m[r][col] == 0:
                continue
            factor = m[r][col] / pivote
            pasos.append(f"\nOperación: F{r+1} ← F{r+1} + ({_fr(-factor)})·F{fila_pivote+1}")
            for c in range(col, columnas_a + 1):  # hasta b inclusive
                m[r][c] = m[r][c] - factor * m[fila_pivote][c]
            pasos.append(matriz_alineada_con_titulo("", m, con_barra=True))

        fila_pivote += 1
        if fila_pivote == filas:
            break

    pasos.append(matriz_alineada_con_titulo("Matriz en forma escalonada (REF):", m, con_barra=True))
    return pasos, m, columnas_pivote


def _rango_por_forma(m: List[List[Fraction]], incluir_b: bool, nvars: int) -> int:
    """Calcula el rango de una matriz, con o sin la columna aumentada."""
    columnas = nvars + (1 if incluir_b else 0)
    rango = 0
    for fila in m:
        if any(val != 0 for val in fila[:columnas]):
            rango += 1
    return rango


def _sustitucion_hacia_atras(ref: List[List[Fraction]]) -> Tuple[List[str], List[Fraction]]:
    """Aplica sustitución hacia atrás (back-substitution) para hallar las incógnitas."""
    filas = len(ref)
    nvars = len(ref[0]) - 1
    x = [Fraction(0, 1) for _ in range(nvars)]
    pasos: List[str] = ["\n--- Sustitución hacia atrás ---"]

    # Buscar la última fila útil
    idx_fila = filas - 1
    while idx_fila >= 0 and all(ref[idx_fila][j] == 0 for j in range(nvars)):
        idx_fila -= 1

    # Recorremos hacia arriba
    for i in range(idx_fila, -1, -1):
        col_piv = None
        for j in range(nvars):
            if ref[i][j] != 0:
                col_piv = j
                break
        if col_piv is None:
            continue

        # Calcular la suma de términos a la derecha del pivote
        suma = Fraction(0, 1)
        for j in range(col_piv + 1, nvars):
            if ref[i][j] != 0:
                suma += ref[i][j] * x[j]

        ai = ref[i][col_piv]
        bi = ref[i][nvars]
        numerador = bi - suma
        xi = numerador / ai
        x[col_piv] = xi

        # Describir el paso
        term_sum = " + ".join(f"({_fr(ref[i][j])})·x{j+1}" for j in range(col_piv+1, nvars) if ref[i][j] != 0)
        if term_sum == "":
            # Solo hay un pivote y un término independiente
            detalle = f"x{col_piv+1} = ({_fr(bi)}) / ({_fr(ai)}) = {_fr(xi)}"
        else:
            # Hay varios términos en la fila
            detalle = f"x{col_piv+1} = ({_fr(bi)} - ({term_sum})) / ({_fr(ai)}) = {_fr(xi)}"
        pasos.append(detalle)
    return pasos, x

# =====================================================
#     FUNCIÓN PRINCIPAL: GAUSS CON CLASIFICACIÓN
# =====================================================

def clasificar_y_resolver(matriz_aumentada: List[List[Fraction]]) -> Dict[str, Any]:
    """
    Resuelve un sistema lineal usando el método de Gauss (REF + sustitución).
    Devuelve:
      - pasos: lista de texto con el procedimiento
      - ref: matriz en forma escalonada
      - tipo_solucion: 'única', 'infinita' o 'inconsistente'
      - soluciones: lista de fracciones si es única
      - mensaje_tipo: explicación textual
    """
    pasos_ref, ref, columnas_pivote = _a_ref_con_pasos(matriz_aumentada)
    nvars = len(matriz_aumentada[0]) - 1

    rango_a = _rango_por_forma(ref, incluir_b=False, nvars=nvars)
    rango_ab = _rango_por_forma(ref, incluir_b=True, nvars=nvars)

    resultado = {
        "pasos": [],
        "ref": ref,
        "tipo_solucion": None,
        "soluciones": None,
        "mensaje_tipo": "",
        "solucion_parametrica": None
    }
    resultado["pasos"].extend(pasos_ref)

    # Clasificación por rangos
    if rango_a < rango_ab:
        resultado["tipo_solucion"] = "inconsistente"
        resultado["mensaje_tipo"] = "Sin solución (aparece una fila [0 … 0 | c≠0] en la forma escalonada)."
        return resultado

    if rango_a < nvars:
        resultado["tipo_solucion"] = "infinita"
        resultado["mensaje_tipo"] = "Usa Gauss-Jordan para obtener la forma paramétrica."
        return resultado

    # Caso determinado
    pasos_sust, soluciones = _sustitucion_hacia_atras(ref)
    resultado["pasos"].extend(pasos_sust)
    resultado["tipo_solucion"] = "única"
    resultado["soluciones"] = soluciones
    resultado["mensaje_tipo"] = "Solución única."
    return resultado
