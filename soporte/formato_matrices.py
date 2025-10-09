
# soporte/formato_matrices.py
from fractions import Fraction

# =====================================================
#   FUNCIONES DE FORMATO Y PRESENTACIÓN DE MATRICES
# =====================================================

def convertir_a_fraccion(valor):
    """
    Convierte un valor (str o numérico) a Fraction sin perder precisión.
    Soporta enteros, decimales y fracciones.
    """
    try:
        if isinstance(valor, Fraction):
            return valor
        if isinstance(valor, (int, float)):
            return Fraction(valor)
        if not isinstance(valor, str):
            return Fraction(0)

        valor = valor.strip()
        if valor in ("", "-"):
            return Fraction(0)

        if "/" in valor:
            num, den = valor.split("/", 1)
            num = num.strip() or "0"
            den = den.strip() or "1"
            return Fraction(int(num), int(den))

        return Fraction(valor)
    except Exception:
        return Fraction(0)
    
def envolver_valor(valor: str) -> str:
    """
    Envuelve el valor entre paréntesis si es negativo, fracción o decimal.
    Ejemplos:
      "5"      -> "5"
      "-3"     -> "(-3)"
      "2/3"    -> "(2/3)"
      "-1.5"   -> "(-1.5)"
    """
    valor_str = str(valor).strip()
    if valor_str.startswith("-") or "/" in valor_str or "." in valor_str:
        return f"({valor_str})"
    return valor_str


def ancho_columnas(matriz):
    """Devuelve el ancho máximo por columna para alinear valores."""
    if not matriz:
        return []
    columnas = len(matriz[0])
    anchos = [0] * columnas
    for fila in matriz:
        for j, val in enumerate(fila):
            anchos[j] = max(anchos[j], len(str(val)))
    return anchos


def formatear_matriz(matriz, corchetes=True):
    """Devuelve una matriz alineada como texto."""
    anchos = ancho_columnas(matriz)
    filas_fmt = []
    for fila in matriz:
        partes = [str(val).rjust(anchos[j]) for j, val in enumerate(fila)]
        fila_txt = " ".join(partes)
        if corchetes:
            fila_txt = f"[ {fila_txt} ]"
        filas_fmt.append(fila_txt)
    return "\n".join(filas_fmt)

def formatear_detalle_operacion(expresiones):
    """Alinea visualmente los pasos de una operación entre matrices."""
    anchos = ancho_columnas(expresiones)
    filas_fmt = []
    for fila in expresiones:
        partes = [str(val).rjust(anchos[j]) for j, val in enumerate(fila)]
        fila_txt = f"[ {' '.join(partes)} ]"
        filas_fmt.append(fila_txt)
    return "\n".join(filas_fmt)

def construir_procedimiento(A_raw, B_raw, operador):
    """
    Muestra matrices A y B alineadas lado a lado con el operador (+, -, ×),
    sin encabezado textual ('Matriz A:' / 'Matriz B:').
    """
    filas_A, cols_A = len(A_raw), len(A_raw[0])
    filas_B, cols_B = len(B_raw), len(B_raw[0])

    texto_A = formatear_matriz(A_raw, corchetes=True).split("\n")
    texto_B = formatear_matriz(B_raw, corchetes=True).split("\n")

    max_filas = max(filas_A, filas_B)
    procedimiento = []

    # Alinear cada fila y colocar el operador centrado verticalmente
    for i in range(max_filas):
        filaA = texto_A[i] if i < len(texto_A) else " " * len(texto_A[0])
        filaB = texto_B[i] if i < len(texto_B) else ""

        if i == max_filas // 2:
            # Línea central: mostrar el operador en el medio
            procedimiento.append(f"{filaA}   {operador}   {filaB}")
        else:
            # Líneas restantes: espacio para mantener alineación
            procedimiento.append(f"{filaA}       {filaB}")

    return "\n".join(procedimiento)


def formatear_ecuacion_linea(fila):
    """
    Devuelve una cadena legible como '2x1 + 3x2 - 5x3 = 7'
    omitiendo los coeficientes que son 0, pero sin alterar la matriz interna.
    """
    n = len(fila) - 1
    partes = []
    for i in range(n):
        coef = fila[i]
        if coef == 0:
            continue  # no mostrar términos nulos
        signo = " + " if coef > 0 and partes else (" - " if coef < 0 else "")
        coef_abs = abs(coef)
        if coef_abs == 1:
            partes.append(f"{signo}x{i+1}")
        else:
            partes.append(f"{signo}{coef_abs}x{i+1}")
    b = fila[-1]
    if not partes:
        partes = ["0"]
    return f"{''.join(partes)} = {b}"


def matriz_alineada_con_titulo(titulo, matriz, con_barra=False):
    """Devuelve una matriz alineada con un título arriba."""
    texto = f"{titulo}\n" if titulo else ""
    if con_barra:
        texto += formatear_matriz(
            [fila[:-1] + ['|'] + [fila[-1]] for fila in matriz],
            corchetes=True
        )
    else:
        texto += formatear_matriz(matriz)
    return texto + "\n"


def resultado_en_fracciones(matriz):
    """Formatea la matriz resultado en fracciones."""
    return formatear_matriz(matriz, corchetes=True)


def resultado_en_decimales(matriz, decimales=4):
    """Formatea la matriz resultado en decimales con alineación."""
    matriz_dec = [[f"{float(x):.{decimales}f}" for x in fila] for fila in matriz]
    return formatear_matriz(matriz_dec, corchetes=True)