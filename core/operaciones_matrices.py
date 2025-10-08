from fractions import Fraction
from core.operaciones_escalar import construir_procedimiento_con_escalares
from soporte.formato_matrices import (
    convertir_a_fraccion,
    envolver_valor,
    formatear_detalle_operacion,
    resultado_en_fracciones,
    resultado_en_decimales,
)

# =====================================================
#    SUMA DE MATRICES
# =====================================================
def sumar_con_pasos(A_raw, B_raw, escalar_A=None, escalar_B=None):
    """Suma dos matrices mostrando el procedimiento paso a paso, con soporte para escalares."""
    if len(A_raw) != len(B_raw) or len(A_raw[0]) != len(B_raw[0]):
        return {"error": "Para sumar: A y B deben tener el mismo tamaño."}

    procedimiento_texto, A_esc, B_esc = construir_procedimiento_con_escalares(
        A_raw, B_raw, escalar_A, escalar_B, "+"
    )
    procedimiento = [procedimiento_texto]

    filas, cols = len(A_esc), len(A_esc[0])
    expresiones, resultado = [], []

    for i in range(filas):
        fila_exp, fila_res = [], []
        for j in range(cols):
            a_val, b_val = A_esc[i][j], B_esc[i][j]
            fila_exp.append(f"{envolver_valor(a_val)}+{envolver_valor(b_val)}")
            fila_res.append(convertir_a_fraccion(a_val) + convertir_a_fraccion(b_val))
        expresiones.append(fila_exp)
        resultado.append(fila_res)

    procedimiento.append("Detalles de operación:")
    procedimiento.append(formatear_detalle_operacion(expresiones))

    return {
        "procedimiento": "\n".join(procedimiento),
        "resultado_lista": resultado,
        "resultado_frac": resultado_en_fracciones(resultado),
        "resultado_dec": resultado_en_decimales(resultado),
    }


# =====================================================
#    RESTA DE MATRICES
# =====================================================
def restar_con_pasos(A_raw, B_raw, escalar_A=None, escalar_B=None):
    """Resta dos matrices mostrando el procedimiento paso a paso, con soporte para escalares."""
    if len(A_raw) != len(B_raw) or len(A_raw[0]) != len(B_raw[0]):
        return {"error": "Para restar: A y B deben tener el mismo tamaño."}

    procedimiento_texto, A_esc, B_esc = construir_procedimiento_con_escalares(
        A_raw, B_raw, escalar_A, escalar_B, "-"
    )
    procedimiento = [procedimiento_texto]

    filas, cols = len(A_esc), len(A_esc[0])
    expresiones, resultado = [], []

    for i in range(filas):
        fila_exp, fila_res = [], []
        for j in range(cols):
            a_val, b_val = A_esc[i][j], B_esc[i][j]
            fila_exp.append(f"{envolver_valor(a_val)}-{envolver_valor(b_val)}")
            fila_res.append(convertir_a_fraccion(a_val) - convertir_a_fraccion(b_val))
        expresiones.append(fila_exp)
        resultado.append(fila_res)

    procedimiento.append("Detalles de operación:")
    procedimiento.append(formatear_detalle_operacion(expresiones))

    return {
        "procedimiento": "\n".join(procedimiento),
        "resultado_lista": resultado,
        "resultado_frac": resultado_en_fracciones(resultado),
        "resultado_dec": resultado_en_decimales(resultado),
    }


# =====================================================
#    MULTIPLICACIÓN DE MATRICES
# =====================================================
def multiplicar_con_pasos(A_raw, B_raw, escalar_A=None, escalar_B=None):
    """
    Multiplica dos matrices mostrando el procedimiento paso a paso.
    Si hay escalares, se muestran primero los bloques de multiplicación escalar
    antes del encabezado principal y los cálculos detallados.
    """
    if len(A_raw[0]) != len(B_raw):
        return {"error": "Para multiplicar: columnas de A deben coincidir con filas de B."}

    procedimiento_texto, A_esc, B_esc = construir_procedimiento_con_escalares(
        A_raw, B_raw, escalar_A, escalar_B, "×"
    )
    procedimiento = [procedimiento_texto]

    filas_A, cols_A = len(A_esc), len(A_esc[0])
    filas_B, cols_B = len(B_esc), len(B_esc[0])

    expresiones, resultado = [], []

    for i in range(filas_A):
        fila_exp, fila_res = [], []
        for j in range(cols_B):
            sumandos = []
            suma_total = Fraction(0)
            for k in range(cols_A):
                a_val, b_val = A_esc[i][k], B_esc[k][j]
                sumandos.append(f"{envolver_valor(a_val)}·{envolver_valor(b_val)}")
                suma_total += convertir_a_fraccion(a_val) * convertir_a_fraccion(b_val)
            fila_exp.append(f"({' + '.join(sumandos)})")
            fila_res.append(suma_total)
        expresiones.append(fila_exp)
        resultado.append(fila_res)

    procedimiento.append("Detalles de operación:")
    procedimiento.append(formatear_detalle_operacion(expresiones))

    return {
        "procedimiento": "\n".join(procedimiento),
        "resultado_lista": resultado,
        "resultado_frac": resultado_en_fracciones(resultado),
        "resultado_dec": resultado_en_decimales(resultado),
    }
