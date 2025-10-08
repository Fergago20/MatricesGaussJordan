from fractions import Fraction
from soporte.formato_matrices import (
    formatear_matriz,
    resultado_en_fracciones,
    resultado_en_decimales,
    construir_procedimiento,
)


# =====================================================
#   MULTIPLICACIÓN ESCALAR CON PROCEDIMIENTO (ALINEADA)
# =====================================================
def escalar_matriz_con_pasos(matriz, escalar, nombre="A"):
    """
    Multiplica una matriz por un escalar mostrando el procedimiento alineado.
    Alinea dinámicamente las matrices según el ancho del escalar.

    Ejemplo:
    Matriz 2 × A:

         [ 1  2  3 ]     [  2  4  6 ]
    2 ⋅ [ 4  5  6 ]  = [  8 10 12 ]
         [ 7  8  9 ]     [ 14 16 18 ]
    """
    try:
        escalar_frac = Fraction(escalar)
    except Exception:
        return {"error": f"Escalar inválido: {escalar}"}

    filas, cols = len(matriz), len(matriz[0])
    resultado = []

    for i in range(filas):
        fila_res = []
        for j in range(cols):
            val = Fraction(matriz[i][j])
            fila_res.append(val * escalar_frac)
        resultado.append(fila_res)

    # Convertir matrices a texto
    mat_original = formatear_matriz(matriz).split("\n")
    mat_result = formatear_matriz(resultado).split("\n")

    # Cálculo de anchos
    ancho_orig = max(len(l) for l in mat_original)
    ancho_res = max(len(l) for l in mat_result)
    texto_escalar = f"{escalar_frac} ⋅ "
    ancho_escalar = len(texto_escalar)
    espacio_central = " " * 4  # entre matrices

    # Construcción del bloque
    bloque = [f"Matriz {escalar_frac} × {nombre}:\n"]

    for i in range(len(mat_original)):
        if i == len(mat_original) // 2:
            linea = (
                f"{texto_escalar}{mat_original[i].rjust(ancho_orig)}"
                f"  = {mat_result[i].ljust(ancho_res)}"
            )
        else:
            linea = (
                f"{' ' * ancho_escalar}{mat_original[i].rjust(ancho_orig)}"
                f"{espacio_central}{mat_result[i].ljust(ancho_res)}"
            )
        bloque.append(linea)

    proc_texto = "\n".join(bloque) + "\n"

    return {
        "procedimiento": proc_texto,
        "resultado_lista": resultado,
        "resultado_frac": resultado_en_fracciones(resultado),
        "resultado_dec": resultado_en_decimales(resultado),
    }


# =====================================================
#   CONSTRUCCIÓN DEL PROCEDIMIENTO CON ESCALARES
# =====================================================
def construir_procedimiento_con_escalares(A_raw, B_raw, escalar_A, escalar_B, simbolo):
    """
    Construye el texto del procedimiento general cuando hay escalares.
    Si no hay escalares, genera el procedimiento clásico como antes.
    Devuelve:
        procedimiento_texto (str),
        A_escalada (list),
        B_escalada (list)
    """
    procedimiento = []
    A_result, B_result = A_raw, B_raw  # sin cambios iniciales

    # =====================================================
    #   BLOQUE ESCALAR A
    # =====================================================
    if escalar_A and escalar_A not in ("", "1"):
        try:
            paso_A = escalar_matriz_con_pasos(A_raw, escalar_A, "A")
            procedimiento.append(paso_A["procedimiento"])
            A_result = paso_A["resultado_lista"]
        except Exception as e:
            procedimiento.append(f"[Advertencia] Escalar A inválido ({escalar_A}): {e}")
        procedimiento.append("")

    # =====================================================
    #   BLOQUE ESCALAR B
    # =====================================================
    if escalar_B and escalar_B not in ("", "1"):
        try:
            paso_B = escalar_matriz_con_pasos(B_raw, escalar_B, "B")
            procedimiento.append(paso_B["procedimiento"])
            B_result = paso_B["resultado_lista"]
        except Exception as e:
            procedimiento.append(f"[Advertencia] Escalar B inválido ({escalar_B}): {e}")
        procedimiento.append("")

    # =====================================================
    #   ENCABEZADO PRINCIPAL DE LA OPERACIÓN
    # =====================================================
    procedimiento.append(f"Operación A {simbolo} B:")
    procedimiento.append(construir_procedimiento(A_result, B_result, simbolo))
    procedimiento.append("")  # salto visual

    return "\n".join(procedimiento), A_result, B_result


