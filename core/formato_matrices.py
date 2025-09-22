# core/formato_matrices.py
from fractions import Fraction

# ============================
#   FUNCIONES DE APOYO
# ============================

def convertir_a_fraccion(valor):
    """Convierte un valor (str) en Fraction para cálculo."""
    try:
        if "/" in valor:
            return Fraction(valor)
        else:
            return Fraction(str(float(valor)))
    except:
        return Fraction(0)


def envolver_valor(valor):
    """Devuelve el valor como string, agregando paréntesis si es fracción."""
    if "/" in valor:
        return f"({valor})"
    return valor


def ancho_columnas(matriz):
    """Calcula el ancho máximo por columna para alinear."""
    if not matriz:
        return []
    columnas = len(matriz[0])
    anchos = [0] * columnas
    for fila in matriz:
        for j, val in enumerate(fila):
            anchos[j] = max(anchos[j], len(str(val)))
    return anchos


def formatear_matriz(matriz, corchetes=True):
    """Formatea una matriz (lista de listas) con corchetes alineados."""
    anchos = ancho_columnas(matriz)
    filas_formateadas = []
    for fila in matriz:
        partes = []
        for j, val in enumerate(fila):
            partes.append(str(val).rjust(anchos[j]))
        fila_txt = " ".join(partes)
        if corchetes:
            fila_txt = f"[ {fila_txt} ]"
        filas_formateadas.append(fila_txt)
    return "\n".join(filas_formateadas)


def formatear_detalle_operacion(expresiones):
    """Formatea los pasos intermedios de operaciones, alineando columnas."""
    anchos = ancho_columnas(expresiones)
    filas_formateadas = []
    for fila in expresiones:
        partes = []
        for j, val in enumerate(fila):
            partes.append(str(val).rjust(anchos[j]))
        fila_txt = " ".join(partes)
        fila_txt = f"[ {fila_txt} ]"
        filas_formateadas.append(fila_txt)
    return "\n".join(filas_formateadas)


def construir_procedimiento(A_raw, B_raw, operador):
    """Construye el bloque de procedimiento mostrando A y B tal como fueron ingresadas."""
    filas_A, cols_A = len(A_raw), len(A_raw[0])
    filas_B, cols_B = len(B_raw), len(B_raw[0])

    # Encabezado
    procedimiento = []
    encabezado = "Matriz A:".ljust(20) + "Matriz B:"
    procedimiento.append(encabezado)

    # Imprimir matrices con el operador centrado
    for i in range(filas_A):
        filaA = "[ " + " ".join(str(x) for x in A_raw[i]) + " ]"
        filaB = "[ " + " ".join(str(x) for x in B_raw[i]) + " ]" if i < filas_B else ""
        if i == filas_A // 2:
            procedimiento.append(f"{filaA}   {operador}   {filaB}")
        else:
            procedimiento.append(f"{filaA}       {filaB}")

    return "\n".join(procedimiento)


def resultado_en_fracciones(matriz):
    """Formatea resultado en fracciones alineadas."""
    return formatear_matriz(matriz, corchetes=True)


def resultado_en_decimales(matriz, decimales=4):
    """Formatea resultado en decimales alineados."""
    matriz_dec = [[f"{float(x):.{decimales}f}" for x in fila] for fila in matriz]
    return formatear_matriz(matriz_dec, corchetes=True)
