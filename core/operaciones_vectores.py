from fractions import Fraction
from core.formato_matrices import (
    convertir_a_fraccion,
    envolver_valor,
    construir_procedimiento,
    formatear_detalle_operacion,
    resultado_en_fracciones,
    resultado_en_decimales,
)

# ============================================
#    SUMA DE VECTORES
# ============================================

def sumar_vectores_con_pasos(A_raw, B_raw):
    if len(A_raw) != len(B_raw):
        return {"error": "Para sumar: Los vectores deben tener el mismo tamaño."}

    procedimiento = [f"Suma de vectores: {A_raw} + {B_raw}"]

    expresiones = []
    resultado = []
    for i in range(len(A_raw)):
        a_val = A_raw[i]
        b_val = B_raw[i]
        expresiones.append(f"{envolver_valor(str(a_val))}+{envolver_valor(str(b_val))}")
        resultado.append(convertir_a_fraccion(str(a_val)) + convertir_a_fraccion(str(b_val)))

    procedimiento.append("\nDetalles de operación A + B:")
    procedimiento.append(formatear_detalle_operacion([expresiones]))

    return {
        "procedimiento": "\n".join(procedimiento),
        "resultado_lista": resultado,
        "resultado_frac": resultado_en_fracciones([resultado]),
        "resultado_dec": resultado_en_decimales([resultado]),
    }

# ============================================
#    RESTA DE VECTORES
# ============================================

def restar_vectores_con_pasos(A_raw, B_raw):
    if len(A_raw) != len(B_raw):
        return {"error": "Para restar: Los vectores deben tener el mismo tamaño."}

    procedimiento = [f"Resta de vectores: {A_raw} - {B_raw}"]

    expresiones = []
    resultado = []
    for i in range(len(A_raw)):
        a_val = A_raw[i]
        b_val = B_raw[i]
        expresiones.append(f"{envolver_valor(str(a_val))}-{envolver_valor(str(b_val))}")
        resultado.append(convertir_a_fraccion(str(a_val)) - convertir_a_fraccion(str(b_val)))

    procedimiento.append("\nDetalles de operación A - B:")
    procedimiento.append(formatear_detalle_operacion([expresiones]))

    return {
        "procedimiento": "\n".join(procedimiento),
        "resultado_lista": resultado,
        "resultado_frac": resultado_en_fracciones([resultado]),
        "resultado_dec": resultado_en_decimales([resultado]),
    }

# ============================================
#    PRODUCTO ESCALAR DE VECTORES
# ============================================

def producto_escalar_con_pasos(A_raw, B_raw):
    if len(A_raw) != len(B_raw):
        return {"error": "Para producto escalar: Los vectores deben tener el mismo tamaño."}

    procedimiento = [f"Producto escalar: {A_raw} · {B_raw}"]

    sumandos = []
    resultado = Fraction(0)
    for i in range(len(A_raw)):
        a_val = A_raw[i]
        b_val = B_raw[i]
        sumandos.append(f"{envolver_valor(str(a_val))}·{envolver_valor(str(b_val))}")
        resultado += convertir_a_fraccion(str(a_val)) * convertir_a_fraccion(str(b_val))

    procedimiento.append("\nDetalles de operación escalar:")
    procedimiento.append(" + ".join(sumandos))

    return {
        "procedimiento": "\n".join(procedimiento),
        "resultado_lista": resultado,
        "resultado_frac": str(resultado),
        "resultado_dec": str(float(resultado)),
    }