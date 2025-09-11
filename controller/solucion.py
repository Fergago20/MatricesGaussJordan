class Matriz:
    def __init__(self):
        pass
    
    def GaussJordan(self, A, m, n, eps=1e-10):
        fila = 0
        pivot_cols = []
        historial = []

        for col in range(n):
            # Buscar pivote
            piv = None
            best = eps
            for r in range(fila, m):
                if abs(A[r][col]) > best:
                    best = abs(A[r][col])
                    piv = r
            if piv is None:
                historial.append(f"Columna {col+1} no tiene pivote significativo.\n")
                continue

            # Intercambio de filas
            if piv != fila:
                A[fila], A[piv] = A[piv], A[fila]
                historial.append(f"Intercambiamos fila {fila+1} con fila {piv+1}.\n" + self.matriz_str(A))

            # Normalización
            p = A[fila][col]
            A[fila] = [v / p for v in A[fila]]
            historial.append(f"Normalizamos fila {fila+1} dividiendo entre {p:.4f}:\n" + self.matriz_str(A))

            # Eliminación en otras filas
            for r in range(m):
                if r != fila and abs(A[r][col]) > eps:
                    factor = A[r][col]
                    A[r] = [A[r][c] - factor * A[fila][c] for c in range(n+1)]
                    historial.append(f"Eliminamos fila {r+1} usando fila {fila+1} (F{r+1}-={factor:.4f}*F{fila+1}):\n" + self.matriz_str(A))

            pivot_cols.append(col)
            fila += 1
            if fila == m:
                break

        # Comprobación de inconsistencia
        for r in range(m):
            if all(abs(A[r][c]) < eps for c in range(n)) and abs(A[r][n]) > eps:
                historial.append("Fila inconsistente encontrada.\n")
                return "no_solution", None, historial

        rango = len(pivot_cols)
        if rango < n:
            historial.append("Rango menor que número de incógnitas → infinitas soluciones.\n")
            return "infinite", None, historial

        sol = [0.0] * n
        for r in range(min(m, n)):
            col = None
            for c in range(n):
                if abs(A[r][c] - 1.0) < 1e-9:
                    col = c
                    break
            if col is not None:
                sol[col] = A[r][n]

        historial.append("Solución única encontrada.\n")
        return "unique", sol, historial

    def matriz_str(self, A):
        m = len(A)
        n = len(A[0]) - 1
        s = ""
        for i in range(m):
            fila = "  ".join(f"{A[i][j]:>8.4f}" for j in range(n))
            s += f"[ {fila} | {A[i][n]:>8.4f} ]\n"
        return s + "\n"
    
    def mostrar_pivotes(self, A):
        columnas_pivotes = []
        tamanio = len(A)
        for i in range(tamanio):
            for j in range(tamanio):
                if A[i][j] == 1:
                    columnas_pivotes.append(j + 1)
                    break
        return columnas_pivotes
                    
