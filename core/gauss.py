# core/gauss.py
from fractions import Fraction
from typing import List, Tuple, Dict, Any
from soporte import (
    matriz_alineada_con_titulo, encabezado_operacion,
    bloque_matriz, fraccion_a_str
)

def _copiar(m):
    return [fila.copy() for fila in m]

def _fr(fr: Fraction) -> str:
    # Fraction → "a/b" o entero
    return fraccion_a_str(fr)

def _a_ref_con_pasos(matriz_aumentada: List[List[Fraction]]) -> Tuple[List[str], List[List[Fraction]], List[int]]:
    """
    Lleva [A|b] a REF (Gauss) mostrando SOLO operaciones que cambian la matriz:
      - Permutar filas (si ocurre)
      - Eliminaciones debajo del pivote
    No imprime anuncios de pivote si no hay cambios.
    Devuelve: (pasos_matrices, ref, columnas_pivote)
    """
    m = _copiar(matriz_aumentada)
    filas = len(m)
    cols_a = len(m[0]) - 1
    fila_pivote = 0
    columnas_pivote: List[int] = []
    pasos: List[str] = []

    for col in range(cols_a):
        # 1) Buscar pivote (primer no-cero desde fila_pivote)
        fila_encontrada = None
        for f in range(fila_pivote, filas):
            if m[f][col] != 0:
                fila_encontrada = f
                break
        if fila_encontrada is None:
            continue  # columna libre

        # 2) Permutar si es necesario (solo si realmente permutamos)
        if fila_encontrada != fila_pivote:
            m[fila_pivote], m[fila_encontrada] = m[fila_encontrada], m[fila_pivote]
            op = encabezado_operacion(f"Permutar: F{fila_pivote+1} ↔ F{fila_encontrada+1}")
            pasos.append(op + bloque_matriz(m))

        columnas_pivote.append(col)
        pivote = m[fila_pivote][col]

        # 3) Eliminar DEBAJO del pivote (Gauss clásico)
        for r in range(fila_pivote + 1, filas):
            if m[r][col] == 0:
                continue
            factor = m[r][col] / pivote
            # F_r ← F_r + (-factor)·F_piv
            op = encabezado_operacion(f"F{r+1} ← F{r+1} + ({_fr(-factor)})·F{fila_pivote+1}")
            for c in range(col, cols_a + 1):  # hasta b inclusive
                m[r][c] = m[r][c] - factor * m[fila_pivote][c]
            pasos.append(op + bloque_matriz(m))

        fila_pivote += 1
        if fila_pivote == filas:
            break

    # Mostrar la REF final
    pasos.append(matriz_alineada_con_titulo("Matriz en forma escalonada (REF):", m, con_barra=True))
    return pasos, m, columnas_pivote


def _rango_por_forma(m: List[List[Fraction]], incluir_b: bool, nvars: int) -> int:
    cols = nvars + (1 if incluir_b else 0)
    r = 0
    for fila in m:
        if any(val != 0 for val in fila[:cols]):
            r += 1
    return r


def _sustitucion_hacia_atras(ref: List[List[Fraction]]) -> Tuple[List[str], List[Fraction]]:
    """
    Lee x_n, x_{n-1}, … desde la REF (asumiendo sistema determinado).
    Devuelve (pasos_texto, solucion).
    """
    filas = len(ref)
    nvars = len(ref[0]) - 1
    x = [Fraction(0, 1) for _ in range(nvars)]
    pasos: List[str] = [encabezado_operacion("Sustitución hacia atrás")]

    # Buscar últimas filas no nulas para determinar cuántas ecuaciones útiles hay
    idx_fila = filas - 1
    while idx_fila >= 0 and all(ref[idx_fila][j] == 0 for j in range(nvars)):
        idx_fila -= 1

    # Recorremos hacia arriba
    for i in range(idx_fila, -1, -1):
        # hallar primera columna no nula (posible pivote en esta fila)
        col_piv = None
        for j in range(nvars):
            if ref[i][j] != 0:
                col_piv = j
                break
        if col_piv is None:
            continue  # fila toda cero → ignórese

        # b_i - sum(a_ij * x_j) con j>col_piv
        suma = Fraction(0, 1)
        for j in range(col_piv + 1, nvars):
            if ref[i][j] != 0:
                suma += ref[i][j] * x[j]

        ai = ref[i][col_piv]
        bi = ref[i][nvars]
        # xi = (bi - suma)/ai
        numerador = bi - suma
        xi = numerador / ai
        x[col_piv] = xi

        # Documentar paso
        term_sum = " + ".join(f"{_fr(ref[i][j])}·x{j+1}" for j in range(col_piv+1, nvars) if ref[i][j] != 0)
        if term_sum == "":
            detalle = f"x{col_piv+1} = {_fr(bi)}/{_fr(ai)} = {_fr(xi)}"
        else:
            detalle = f"x{col_piv+1} = ({_fr(bi)} - ({term_sum})) / {_fr(ai)} = {_fr(xi)}"
        pasos.append(detalle + "\n")

    return pasos, x


def clasificar_y_resolver(matriz_aumentada: List[List[Fraction]]) -> Dict[str, Any]:
    """
    Gauss (REF + sustitución hacia atrás) con registro de SOLO operaciones que cambian la matriz.
    Retorna dict con:
      - pasos: lista de strings (procedimiento + REF + sustitución)
      - ref: matriz REF
      - tipo_solucion: 'única' | 'infinita' | 'inconsistente'
      - soluciones: lista Fraction si única
      - mensaje_tipo: texto explicativo
      - solucion_parametrica: None (para paramétricas usar Gauss-Jordan)
    """
    pasos_ref, ref, cols_piv = _a_ref_con_pasos(matriz_aumentada)
    nvars = len(matriz_aumentada[0]) - 1

    rango_a  = _rango_por_forma(ref, incluir_b=False, nvars=nvars)
    rango_ab = _rango_por_forma(ref, incluir_b=True,  nvars=nvars)

    resultado = {
        "pasos": [], "ref": ref, "tipo_solucion": None,
        "soluciones": None, "mensaje_tipo": "", "solucion_parametrica": None
    }
    resultado["pasos"].extend(pasos_ref)

    # Clasificación por rangos
    if rango_a < rango_ab:
        resultado["tipo_solucion"] = "inconsistente"
        resultado["mensaje_tipo"] = "Sin solución (aparece una fila [0 … 0 | c≠0] en la forma escalonada)."
        return resultado

    if rango_a < nvars:
        # Para soluciones infinitas recomendamos Gauss-Jordan,
        # aquí solo declaramos el tipo.
        resultado["tipo_solucion"] = "infinita"
        resultado["mensaje_tipo"] = "Infinitas soluciones. Usa Gauss-Jordan para la forma paramétrica."
        return resultado

    # Caso determinado: sustitución hacia atrás
    pasos_sust, soluciones = _sustitucion_hacia_atras(ref)
    resultado["pasos"].extend(pasos_sust)
    resultado["tipo_solucion"] = "única"
    resultado["soluciones"] = soluciones
    resultado["mensaje_tipo"] = "Solución única."
    return resultado
