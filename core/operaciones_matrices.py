# core/operaciones_matrices.py
from fractions import Fraction

# Importa funciones auxiliares desde soporte
from soporte.formato_matrices import (
    convertir_a_fraccion,
    envolver_valor,
    construir_procedimiento,
    formatear_detalle_operacion,
    resultado_en_fracciones,
    resultado_en_decimales,
)

# =====================================================
#    SUMA DE MATRICES
# =====================================================
def sumar_con_pasos(A_raw, B_raw):
    """Suma dos matrices mostrando procedimiento paso a paso."""
    if len(A_raw) != len(B_raw) or len(A_raw[0]) != len(B_raw[0]):
        return {"error": "Para sumar: A y B deben tener el mismo tamaño."}

    filas, cols = len(A_raw), len(A_raw[0])
    procedimiento = [construir_procedimiento(A_raw, B_raw, "+")]

    expresiones, resultado = [], []
    for i in range(filas):
        fila_exp, fila_res = [], []
        for j in range(cols):
            a_val, b_val = A_raw[i][j], B_raw[i][j]
            fila_exp.append(f"{envolver_valor(str(a_val))}+{envolver_valor(str(b_val))}")
            fila_res.append(convertir_a_fraccion(a_val) + convertir_a_fraccion(b_val))
        expresiones.append(fila_exp)
        resultado.append(fila_res)

    procedimiento.append("\nDetalles de operación A + B:")
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
def restar_con_pasos(A_raw, B_raw):
    """Resta dos matrices mostrando procedimiento paso a paso."""
    if len(A_raw) != len(B_raw) or len(A_raw[0]) != len(B_raw[0]):
        return {"error": "Para restar: A y B deben tener el mismo tamaño."}

    filas, cols = len(A_raw), len(A_raw[0])
    procedimiento = [construir_procedimiento(A_raw, B_raw, "-")]

    expresiones, resultado = [], []
    for i in range(filas):
        fila_exp, fila_res = [], []
        for j in range(cols):
            a_val, b_val = A_raw[i][j], B_raw[i][j]
            fila_exp.append(f"{envolver_valor(str(a_val))}-{envolver_valor(str(b_val))}")
            fila_res.append(convertir_a_fraccion(a_val) - convertir_a_fraccion(b_val))
        expresiones.append(fila_exp)
        resultado.append(fila_res)

    procedimiento.append("\nDetalles de operación A - B:")
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
def multiplicar_con_pasos(A_raw, B_raw):
    """Multiplica dos matrices mostrando procedimiento paso a paso."""
    if len(A_raw[0]) != len(B_raw):
        return {"error": "Para multiplicar: columnas de A deben coincidir con filas de B."}

    filas_A, cols_A = len(A_raw), len(A_raw[0])
    filas_B, cols_B = len(B_raw), len(B_raw[0])

    procedimiento = [construir_procedimiento(A_raw, B_raw, "×")]

    expresiones, resultado = [], []
    for i in range(filas_A):
        fila_exp, fila_res = [], []
        for j in range(cols_B):
            sumandos = []
            suma_total = Fraction(0)
            for k in range(cols_A):
                a_val, b_val = A_raw[i][k], B_raw[k][j]
                sumandos.append(f"{envolver_valor(str(a_val))}·{envolver_valor(str(b_val))}")
                suma_total += convertir_a_fraccion(a_val) * convertir_a_fraccion(b_val)
            fila_exp.append(f"({' + '.join(sumandos)})")
            fila_res.append(suma_total)
        expresiones.append(fila_exp)
        resultado.append(fila_res)

    procedimiento.append("\nDetalles de operación A × B:")
    procedimiento.append(formatear_detalle_operacion(expresiones))

    return {
        "procedimiento": "\n".join(procedimiento),
        "resultado_lista": resultado,
        "resultado_frac": resultado_en_fracciones(resultado),
        "resultado_dec": resultado_en_decimales(resultado),
    }
