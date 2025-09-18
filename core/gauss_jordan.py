# core/gauss_jordan.py
from fractions import Fraction                     # Fracciones exactas (a/b)
from typing import List, Tuple, Dict, Any          # Tipos para anotar funciones
from soporte import (                              # Utilidades de formato/impresión
    matriz_alineada_con_titulo, encabezado_operacion, fraccion_a_str,
    bloque_matriz
)

def _copiar(m):
    return [fila.copy() for fila in m]             # Copia profunda por filas (evitar mutar el original)

def _fr(fr: Fraction) -> str:
    return fraccion_a_str(fr)                      # Convierte Fraction → texto "a/b" o entero

def _a_rref_con_pasos(matriz_aumentada: List[List[Fraction]]) -> Tuple[List[str], List[List[Fraction]], List[int]]:
    """
    Lleva [A|b] a RREF (Gauss-Jordan) mostrando SOLO operaciones que cambian la matriz.
    (Sin mensajes de pivote si no hay permuta/normalización/eliminación).
    Devuelve: pasos_matrices, rref, columnas_pivote.
    """
    m = _copiar(matriz_aumentada)
    filas = len(m)
    cols_a = len(m[0]) - 1
    fila_pivote = 0
    columnas_pivote: List[int] = []

    pasos_matrices: List[str] = []

    for col in range(cols_a):
        # 1) Buscar pivote (primer no-cero desde fila_pivote)
        fila_encontrada = None
        for f in range(fila_pivote, filas):
            if m[f][col] != 0:
                fila_encontrada = f
                break
        if fila_encontrada is None:
            continue  # columna libre; no hay pivote aquí

        # 2) Permutar si es necesario (solo mostramos si realmente permutamos)
        if fila_encontrada != fila_pivote:
            m[fila_pivote], m[fila_encontrada] = m[fila_encontrada], m[fila_pivote]
            op = encabezado_operacion(f"Permutar: F{fila_pivote+1} ↔ F{fila_encontrada+1}")
            pasos_matrices.append(op + bloque_matriz(m))

        # 3) Normalizar pivote a 1 (solo mostramos si realmente normalizamos)
        pivote = m[fila_pivote][col]
        if pivote != 1:
            op = encabezado_operacion(f"F{fila_pivote+1} ← (1/{_fr(pivote)})·F{fila_pivote+1}")
            for c in range(col, cols_a+1):
                m[fila_pivote][c] = m[fila_pivote][c] / pivote
            pasos_matrices.append(op + bloque_matriz(m))

        columnas_pivote.append(col)

        # 4) Eliminar arriba y abajo (hacer ceros en la columna del pivote)
        for r in range(filas):
            if r == fila_pivote or m[r][col] == 0:
                continue
            factor = m[r][col]  # pivote ya es 1
            op = encabezado_operacion(f"F{r+1} ← F{r+1} + ({_fr(-factor)})·F{fila_pivote+1}")
            for c in range(col, cols_a+1):
                m[r][c] = m[r][c] - factor * m[fila_pivote][c]
            pasos_matrices.append(op + bloque_matriz(m))

        fila_pivote += 1
        if fila_pivote == filas:
            break

    # Matriz final
    pasos_matrices.append(matriz_alineada_con_titulo("Matriz final (RREF):", m, con_barra=True))
    return pasos_matrices, m, columnas_pivote


def _rango_por_forma(m: List[List[Fraction]], incluir_b: bool, nvars: int) -> int:
    cols = nvars + (1 if incluir_b else 0)         # considerar o no la columna b
    r = 0
    for fila in m:
        if any(val != 0 for val in fila[:cols]):   # fila no-nula dentro de las cols consideradas
            r += 1
    return r                                       # rango(A) o rango(A|b)

def _solucion_parametrica_desde_rref(rref: List[List[Fraction]], cols_pivote: List[int], nvars: int):
    """
    Construye solución paramétrica:
      - variables libres (sin pivote) quedan como parámetros
      - variables pivote se expresan en función de libres y b
    """
    libres = [j for j in range(nvars) if j not in cols_pivote]   # índices libres
    fila_de_pivote = {col: i for i, col in enumerate(cols_pivote)}  # col pivote → fila

    lineas = []
    for var in range(nvars):
        if var in libres:                                        # x_k libre
            lineas.append(f"x{var+1} es libre")
            continue
        fila = fila_de_pivote[var]                               # fila donde x_var es pivote
        b = rref[fila][nvars]                                    # término independiente de esa fila
        partes = []
        if b != 0:
            partes.append(f"{_fr(b)}")                           # constante
        for j in libres:
            coef = rref[fila][j]                                 # coeficiente de x_j libre
            if coef == 0:
                continue
            signo = " - " if coef > 0 else (" + " if partes else "")
            partes.append(f"{signo}{_fr(abs(coef))}x{j+1}")      # mover a la derecha (cambia signo)
        if not partes:
            partes = ["0"]                                       # caso todo 0
        lineas.append(f"x{var+1} = {''.join(partes)}")           # ecuación de x_var
    return lineas, libres

def clasificar_y_resolver_gauss_jordan(matriz_aumentada: List[List[Fraction]]) -> Dict[str, Any]:
    """
    Ejecuta Gauss-Jordan y clasifica el sistema:
      - 'única': solución única
      - 'infinita': solución paramétrica
      - 'inconsistente': sin solución (fila [0 … 0 | c≠0])
    Devuelve dict con pasos, rref, tipo, soluciones o paramétrica y mensaje.
    """
    pasos_mat, rref, cols_pivote = _a_rref_con_pasos(matriz_aumentada)  # procedimiento y RREF
    nvars = len(matriz_aumentada[0]) - 1                                # número de incógnitas

    rango_a  = _rango_por_forma(rref, incluir_b=False, nvars=nvars)     # rango(A)
    rango_ab = _rango_por_forma(rref, incluir_b=True,  nvars=nvars)     # rango(A|b)

    resultado = {
        "pasos": pasos_mat,                  # SOLO matrices (con anuncios de pivote)
        "rref": rref,
        "tipo_solucion": None,
        "soluciones": None,
        "mensaje_tipo": "",
        "solucion_parametrica": None
    }

    if rango_a < rango_ab:                                                   # inconsistente
        resultado["tipo_solucion"] = "inconsistente"
        resultado["mensaje_tipo"] = "Sin solución: aparece una fila [0 … 0 | c≠0] en RREF."
        return resultado

    if rango_a == rango_ab == nvars:                                         # única
        x = [Fraction(0, 1) for _ in range(nvars)]
        for i, col in enumerate(cols_pivote):                                # leer b en filas pivote
            x[col] = rref[i][nvars]
        resultado["tipo_solucion"] = "única"
        resultado["soluciones"] = x
        resultado["mensaje_tipo"] = "Solución única."
        return resultado

    # rango_a == rango_ab < nvars → infinitas (paramétrica)
    lineas, _ = _solucion_parametrica_desde_rref(rref, cols_pivote, nvars)
    resultado["tipo_solucion"] = "infinita"
    resultado["mensaje_tipo"] = "Infinitas soluciones."
    resultado["solucion_parametrica"] = lineas
    return resultado
