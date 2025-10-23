from fractions import Fraction
from soporte.formato_matrices import matriz_alineada_con_titulo
from core.operaciones_matrices import multiplicar_con_pasos


def _to_str(x):
    if isinstance(x, Fraction):
        return str(x) if x.denominator != 1 else str(x.numerator)
    return str(int(x)) if float(x).is_integer() else f"{x:.4f}".rstrip("0").rstrip(".")


# ================================================================
# ======== FORMATO 2×2 (DET AD−BC) ===============================
# ================================================================
def formatear_pasos_inversa_2x2(A, inv, det):
    """Texto completo con desarrollo teórico y desarrollo de verificación."""
    a, b = A[0]
    c, d = A[1]
    texto = []

    texto.append("DEFINICIÓN TEÓRICA:\nSea A una matriz cuadrada 2×2. "
                 "Se dice que A es invertible si existe C tal que CA = I y AC = I.")
    texto.append("Una matriz no invertible se denomina singular.\n")
    texto.append("TEOREMA:\nSi ad − bc ≠ 0, entonces A es invertible y\nA⁻¹ = 1/(ad−bc) [[d, −b], [−c, a]]\n")

    texto.append("Matriz A:")
    texto.append(matriz_alineada_con_titulo("", A))
    texto.append(f"Determinante: det(A) = ({a})({d}) − ({b})({c}) = {_to_str(det)}\n")

    texto.append("Cálculo de la inversa por la fórmula:")
    texto.append(f"A⁻¹ = (1/{_to_str(det)}) × [[{_to_str(d)}, −{_to_str(b)}], [−{_to_str(c)}, {_to_str(a)}]]\n")
    texto.append("A⁻¹ =")
    texto.append(matriz_alineada_con_titulo("", inv))

    # =========== Verificación con desarrollo ===========
    texto.append("\nVERIFICACIÓN DE LOS TEOREMAS:")
    texto.append("1. Comprobación A·A⁻¹ = I\n")
    AC = multiplicar_con_pasos(A, inv)
    texto.append(AC["procedimiento"])
    texto.append("Resultado A·A⁻¹ =")
    texto.append(matriz_alineada_con_titulo("", AC["resultado_lista"]))

    texto.append("\n2. Comprobación A⁻¹·A = I\n")
    CA = multiplicar_con_pasos(inv, A)
    texto.append(CA["procedimiento"])
    texto.append("Resultado A⁻¹·A =")
    texto.append(matriz_alineada_con_titulo("", CA["resultado_lista"]))

    texto.append("\nConclusión: La matriz calculada es efectivamente A⁻¹ (matriz no singular).")

    return "\n".join(texto), inv


# ================================================================
# ======== FORMATO GAUSS–JORDAN GENERAL ==========================
# ================================================================
def formatear_pasos_inversa_gauss_jordan(A_original, pasos, A_inv):
    """Formato completo, incluyendo teoría y desarrollo del cálculo."""
    texto = []
    texto.append("DEFINICIÓN TEÓRICA:\nSea A una matriz cuadrada de n×n. "
                 "Se dice que A es invertible si existe una matriz C tal que CA = Iₙ y AC = Iₙ.\n")
    texto.append("TEOREMA:\nA es invertible ⇔ [A | I] ~ [I | A⁻¹].")
    texto.append("Si al reducir [A | I] por filas obtenemos [I | A⁻¹], entonces A es invertible.\n")

    texto.append("Matriz original A:")
    texto.append(matriz_alineada_con_titulo("", A_original))
    texto.append("\nPROCESO DE REDUCCIÓN GAUSS–JORDAN:")
    for p in pasos:
        texto.append(str(p))

    texto.append("\nResultado final [I | A⁻¹]:")
    texto.append(matriz_alineada_con_titulo("", A_inv))
    texto.append("\nA⁻¹ =")
    texto.append(matriz_alineada_con_titulo("", A_inv))

    # =========== Verificación con desarrollo ===========
    texto.append("\nVERIFICACIÓN DE LOS TEOREMAS:")
    texto.append("1. Comprobación A·A⁻¹ = I\n")
    AC = multiplicar_con_pasos(A_original, A_inv)
    texto.append(AC["procedimiento"])
    texto.append("Resultado A·A⁻¹ =")
    texto.append(matriz_alineada_con_titulo("", AC["resultado_lista"]))

    texto.append("\n2. Comprobación A⁻¹·A = I\n")
    CA = multiplicar_con_pasos(A_inv, A_original)
    texto.append(CA["procedimiento"])
    texto.append("Resultado A⁻¹·A =")
    texto.append(matriz_alineada_con_titulo("", CA["resultado_lista"]))

    texto.append("\nConclusión: La matriz calculada es efectivamente A⁻¹ (no singular).")
    return "\n".join(texto)