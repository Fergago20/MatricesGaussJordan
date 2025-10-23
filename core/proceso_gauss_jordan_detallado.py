# core/proceso_gauss_jordan_detallado.py
from fractions import Fraction
from soporte.formato_matrices import formatear_matriz, matriz_alineada_con_titulo


def proceso_gauss_jordan_detallado(A):
    """
    Ejecuta el método de Gauss–Jordan mostrando los pasos al estilo 'Matrix Calculator'.
    Se usa principalmente para el cálculo de la inversa o para mostrar la eliminación por filas.
    Si la matriz no es invertible, muestra los pasos hasta detectarlo.
    """

    n = len(A)
    I = [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    Aum = [list(map(Fraction, A[i])) + list(map(Fraction, I[i])) for i in range(n)]

    pasos = []
    pasos.append("ALGORITMO PARA DETERMINAR A⁻¹ (Método de Gauss–Jordan):")
    pasos.append("Se construye la matriz aumentada [A | I]. Si A es equivalente por filas a I, entonces [A I] es equivalente por filas a [I A⁻¹].\n")
    pasos.append("Matriz aumentada inicial:")
    pasos.append(matriz_alineada_con_titulo("[A | I]", Aum, con_barra=False))

    # ===== INICIO DEL PROCESO =====
    for col in range(n):
        pasos.append(f"\n>>> Columna {col+1}")

        # Buscar pivote
        pivote_fila = None
        for f in range(col, n):
            if Aum[f][col] != 0:
                pivote_fila = f
                break

        if pivote_fila is None:
            pasos.append(f"→ No se encontró pivote en la columna {col+1}. Columna libre.\n")
            continue

        pivote = Aum[pivote_fila][col]
        pasos.append(f"Pivote encontrado en F{pivote_fila+1}, C{col+1}: {pivote}")

        # Intercambiar filas si el pivote no está en la posición esperada
        if pivote_fila != col:
            Aum[col], Aum[pivote_fila] = Aum[pivote_fila], Aum[col]
            pasos.append(f"\nPermutar filas: F{col+1} ↔ F{pivote_fila+1}")
            pasos.append(formatear_matriz(Aum, corchetes=True))

        # Normalizar la fila del pivote
        pivote = Aum[col][col]
        if pivote != 1:
            pasos.append(f"\nF{col+1} / ({pivote}) → F{col+1}")
            Aum[col] = [x / pivote for x in Aum[col]]
            pasos.append(formatear_matriz(Aum, corchetes=True))

        # Eliminar otras filas en la columna
        for r in range(n):
            if r == col:
                continue
            factor = Aum[r][col]
            if factor == 0:
                continue
            signo = "-" if factor > 0 else "+"
            pasos.append(f"\nF{r+1} {signo} {abs(factor)}·F{col+1} → F{r+1}")
            Aum[r] = [Aum[r][c] - factor * Aum[col][c] for c in range(2 * n)]
            pasos.append(formatear_matriz(Aum, corchetes=True))

    # ===== RESULTADO FINAL =====
    izquierda = [fila[:n] for fila in Aum]
    derecha = [fila[n:] for fila in Aum]

    # Verificar si la parte izquierda es la identidad
    es_identidad = all(
        all((izquierda[i][j] == 1 if i == j else izquierda[i][j] == 0) for j in range(n))
        for i in range(n)
    )

    pasos.append("\nMatriz final obtenida:")
    pasos.append(matriz_alineada_con_titulo("[A | I]", Aum, con_barra=False))

    if es_identidad:
        # No imprimir conclusión aquí; se mostrará en el resultado final
        return "\n".join(pasos), derecha
    else:
        pasos.append("Durante el proceso, se detectó que A no puede transformarse en la identidad.")
        pasos.append("Por tanto, A es singular (no invertible).")
        return "\n".join(pasos), None
