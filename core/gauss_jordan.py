# core/gauss_jordan.py
from fractions import Fraction
from typing import List, Tuple, Dict, Any
from soporte.formato_matrices import matriz_alineada_con_titulo
from soporte.validaciones import fraccion_a_str

# =====================================================
#     FUNCIONES AUXILIARES
# =====================================================

def _copiar(matriz):
    """Devuelve una copia profunda de la matriz."""
    return [fila.copy() for fila in matriz]


def _fr(fr: Fraction) -> str:
    """Convierte una fracción a texto legible (entero o a/b)."""
    return fraccion_a_str(fr)


def _a_rref_con_pasos(matriz_aumentada: List[List[Fraction]]) -> Tuple[List[str], List[List[Fraction]], List[int]]:
    """
    Lleva la matriz aumentada [A|b] a su forma reducida por filas (RREF),
    mostrando los pasos organizados por columnas:
      - Indica en qué columna se busca el pivote
      - Muestra normalización y operaciones con formato claro
    """
    m = _copiar(matriz_aumentada)
    filas = len(m)
    columnas_a = len(m[0]) - 1
    fila_pivote = 0
    columnas_pivote: List[int] = []
    pasos: List[str] = []

    for col in range(columnas_a):
        pasos.append(f"\n>>> Columna {col+1}")

        # Buscar pivote
        fila_encontrada = None
        for f in range(fila_pivote, filas):
            if m[f][col] != 0:
                fila_encontrada = f
                break

        if fila_encontrada is None:
            pasos.append("→ Columna libre (sin pivote)\n")
            continue

        pivote = m[fila_encontrada][col]
        pasos.append(f"Pivote encontrado en F{fila_encontrada+1}, C{col+1}: {_fr(pivote)}")

        # Permutar si es necesario
        if fila_encontrada != fila_pivote:
            m[fila_pivote], m[fila_encontrada] = m[fila_encontrada], m[fila_pivote]
            pasos.append(f"Permutar filas: F{fila_pivote+1} ↔ F{fila_encontrada+1}")
            pasos.append(matriz_alineada_con_titulo("", m, con_barra=True))

        # Normalizar pivote a 1
        pivote = m[fila_pivote][col]
        if pivote != 1:
            pivote_str = _fr(pivote)
            if not pivote_str.isdigit():
                pivote_str = f"({pivote_str})"
            pasos.append(f"Normalizar fila: F{fila_pivote+1} ← (1/{pivote_str})·F{fila_pivote+1}")
            for c in range(col, columnas_a + 1):
                m[fila_pivote][c] = m[fila_pivote][c] / pivote
            pasos.append(matriz_alineada_con_titulo("", m, con_barra=True) )

        columnas_pivote.append(col)

        # Eliminar arriba y abajo del pivote
        hubo_cambio = False
        for r in range(filas):
            if r == fila_pivote or m[r][col] == 0:
                continue
            factor = m[r][col]
            pasos.append(f"Operación: F{r+1} ← F{r+1} + ({_fr(-factor)})·F{fila_pivote+1}")
            for c in range(col, columnas_a + 1):
                m[r][c] = m[r][c] - factor * m[fila_pivote][c]
            pasos.append(matriz_alineada_con_titulo("", m, con_barra=True))
            hubo_cambio = True

        if not hubo_cambio:
            pasos.append("Sin cambios: columna ya nula en otras filas.\n")

        fila_pivote += 1
        if fila_pivote == filas:
            break

    pasos.append("Matriz final (RREF):")
    pasos.append(matriz_alineada_con_titulo("", m, con_barra=True))
    return pasos, m, columnas_pivote

def _rango_por_forma(m: List[List[Fraction]], incluir_b: bool, nvars: int) -> int:
    """Calcula el rango de una matriz (A o A|b)."""
    columnas = nvars + (1 if incluir_b else 0)
    rango = 0
    for fila in m:
        if any(val != 0 for val in fila[:columnas]):
            rango += 1
    return rango

def _solucion_parametrica_desde_rref(rref: List[List[Fraction]], columnas_pivote: List[int], nvars: int):
    """
    Construye la solución paramétrica:
      - Variables libres quedan como parámetros.
      - Variables pivote se expresan en función de las libres.
      - Se omite el coeficiente 1 o -1 en las variables libres para mejor legibilidad.
      - Se evita imprimir '+' al inicio cuando el primer término es positivo.
    """
    libres = [j for j in range(nvars) if j not in columnas_pivote]
    fila_de_pivote = {col: i for i, col in enumerate(columnas_pivote)}

    def _formatear_coeficiente(coef, var_index):
        """Devuelve un término limpio como 'x3', '-x2', '2x4', etc."""
        if coef == 1:
            return f"x{var_index}"
        elif coef == -1:
            return f"-x{var_index}"
        else:
            return f"{coef}x{var_index}"

    lineas = []
    for var in range(nvars):
        if var in libres:
            lineas.append(f"x{var+1} es libre")
            continue

        fila = fila_de_pivote[var]
        b = rref[fila][nvars]
        partes = []

        # Agregar término constante (si existe)
        if b != 0:
            partes.append(f"{b}")

        # Términos con variables libres
        for j in libres:
            coef = rref[fila][j]
            if coef == 0:
                continue

            # si es positivo y no hay partes previas, no se agrega "+"
            if coef < 0:
                signo = " + "
            else:
                signo = " - "

            partes.append(f"{signo}{_formatear_coeficiente(abs(coef), j+1)}")

        # Limpiar posible signo inicial redundante
        expresion = "".join(partes).strip()
        if expresion.startswith("+ "):
            expresion = expresion[2:]

        if not expresion:
            expresion = "0"

        lineas.append(f"x{var+1} = {expresion}")

    return lineas, libres

# =====================================================
#     FUNCIÓN PRINCIPAL: GAUSS-JORDAN COMPLETO
# =====================================================

def clasificar_y_resolver_gauss_jordan(matriz_aumentada: List[List[Fraction]]) -> Dict[str, Any]:
    """
    Ejecuta el método de Gauss-Jordan y clasifica el sistema:
      - 'única': solución única
      - 'infinita': solución paramétrica
      - 'inconsistente': sin solución
    """
    pasos_mat, rref, columnas_pivote = _a_rref_con_pasos(matriz_aumentada)
    nvars = len(matriz_aumentada[0]) - 1

    rango_a = _rango_por_forma(rref, incluir_b=False, nvars=nvars)
    rango_ab = _rango_por_forma(rref, incluir_b=True, nvars=nvars)

    resultado = {
        "pasos": pasos_mat,
        "rref": rref,
        "tipo_solucion": None,
        "soluciones": None,
        "mensaje_tipo": "",
        "solucion_parametrica": None
    }

    # Caso sin solución
    if rango_a < rango_ab:
        resultado["tipo_solucion"] = "inconsistente"
        resultado["mensaje_tipo"] = "Sin solución (fila [0 … 0 | c≠0] en RREF)."
        return resultado

    # Solución única
    if rango_a == rango_ab == nvars:
        x = [Fraction(0, 1) for _ in range(nvars)]
        for i, col in enumerate(columnas_pivote):
            x[col] = rref[i][nvars]
        resultado["tipo_solucion"] = "única"
        resultado["soluciones"] = x
        resultado["mensaje_tipo"] = "Solución única."
        return resultado

    # Solución infinita (paramétrica)
    lineas, _ = _solucion_parametrica_desde_rref(rref, columnas_pivote, nvars)
    resultado["tipo_solucion"] = "infinita"
    resultado["mensaje_tipo"] = "Infinitas soluciones."
    resultado["solucion_parametrica"] = lineas
    return resultado
