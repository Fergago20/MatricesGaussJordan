# core/inversa_matriz_con_reglas.py
from fractions import Fraction
from soporte.formato_matrices import formatear_matriz
from core.operaciones_matrices import multiplicar_con_pasos
from core.proceso_gauss_jordan_detallado import proceso_gauss_jordan_detallado

def inversa_matriz_con_reglas(M, modo="fraccion", tolerancia=1e-12):
    """
    Calcula la inversa de una matriz cuadrada.
    - Si es 2x2 → usa la fórmula directa.
    - Si es mayor → usa el método de Gauss–Jordan detallado con el formato oficial.
    """

    # Validar matriz cuadrada
    if len(M) == 0 or len(M) != len(M[0]):
        return {"error": "La matriz debe ser cuadrada para calcular su inversa."}

    n = len(M)

    # =====================================================
    # CASO 2×2 — Fórmula directa
    # =====================================================
    if n == 2:
        a, b = M[0]
        c, d = M[1]
        det = a * d - b * c

        # --- Caso sin inversa ---
        if det == 0:
            return {
                "procedimiento": (
                    "DEFINICIÓN TEÓRICA:\n"
                    "Sea A una matriz cuadrada 2×2. Se dice que A es invertible si existe C tal que CA = I y AC = I.\n"
                    "Una matriz no invertible se denomina singular.\n\n"
                    "TEOREMA:\n"
                    "Si ad − bc ≠ 0, entonces A es invertible y\n"
                    "A⁻¹ = 1/(ad−bc) [[d, −b], [−c, a]]\n\n"
                    "Determinante: det(A) = ad − bc = 0 → A no es invertible."
                ),
                "resultado_frac": "Conclusión: La matriz es singular (no tiene inversa).",
                "resultado_lista": [],
                "conclusiones": "La matriz es singular (no tiene inversa)."
            }

        # --- Caso con inversa ---
        inv = [
            [d / det, -b / det],
            [-c / det, a / det],
        ]

        texto_teorico = (
            "DEFINICIÓN TEÓRICA:\n"
            "Sea A una matriz cuadrada 2×2. Se dice que A es invertible si existe C tal que CA = I y AC = I.\n"
            "Una matriz no invertible se denomina singular.\n\n"
            "TEOREMA:\n"
            "Si ad − bc ≠ 0, entonces A es invertible y\n"
            "A⁻¹ = 1/(ad−bc) [[d, −b], [−c, a]]\n\n"
            "Matriz A:\n"
            f"{formatear_matriz(M)}\n\n"
            f"Determinante: det(A) = ({a})({d}) − ({b})({c}) = {det}\n\n"
            "Cálculo de la inversa por la fórmula:\n"
            f"A⁻¹ = (1/{det}) × [[{d}, {(-b)}], [{(-c)}, {a}]]\n\n"
            "A⁻¹ =\n"
            f"{formatear_matriz(inv)}\n\n"
            "VERIFICACIÓN DE LOS TEOREMAS:\n"
            "1. Comprobación A·A⁻¹ = I\n\n"
        )

        # --- Verificación A·A⁻¹ ---
        pasos1 = multiplicar_con_pasos(M, inv)
        texto_teorico += pasos1["procedimiento"] + "\n\n"

        texto_teorico += "2. Comprobación A⁻¹·A = I\n\n"

        # --- Verificación A⁻¹·A ---
        pasos2 = multiplicar_con_pasos(inv, M)
        texto_teorico += pasos2["procedimiento"] + "\n\n"

        texto_conclusion = "Conclusión: La matriz calculada es efectivamente A⁻¹ (matriz no singular)."

        # --- Resultado final resumido ---
        texto_resultado = formatear_matriz(inv) + "\n" + texto_conclusion

        return {
            "procedimiento": texto_teorico.strip(),
            "resultado_frac": texto_resultado.strip(),
            "resultado_lista": inv,
            "conclusiones": texto_conclusion
        }

    # =====================================================
    # CASO n > 2 — Gauss–Jordan (formato oficial)
    # =====================================================
    else:
        texto_proceso, inv = proceso_gauss_jordan_detallado(M)

        # --- Si la matriz no tiene inversa ---
        if inv is None:
            texto_resultado = (
                "Conclusión: La matriz es singular (no tiene inversa), "
                "ya que durante el proceso de Gauss–Jordan se encontró al menos una columna sin pivote, "
                "lo que indica que su rango es menor que su orden (rango < n)."
            )
            return {
                "procedimiento": texto_proceso.strip(),
                "resultado_frac": texto_resultado,
                "resultado_lista": [],
                "conclusiones": texto_resultado
            }

        # --- Si se encontró la inversa ---
        texto_resultado = formatear_matriz(inv) + "\nConclusión: La matriz calculada es efectivamente A⁻¹ (no singular)."

        return {
            "procedimiento": texto_proceso.strip(),
            "resultado_frac": texto_resultado,
            "resultado_lista": inv,
            "conclusiones": "La matriz calculada es efectivamente A⁻¹ (no singular)."
        }
