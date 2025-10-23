from fractions import Fraction

# =====================================================
#     DETECCIÓN DE TIPOS DE MATRIZ Y TEOREMAS
# =====================================================

def es_cuadrada(M):
    return all(len(fila) == len(M) for fila in M)

def es_diagonal(M):
    n = len(M)
    return all(M[i][j] == 0 for i in range(n) for j in range(n) if i != j)

def es_triangular_superior(M):
    n = len(M)
    return all(M[i][j] == 0 for i in range(1, n) for j in range(i))

def es_triangular_inferior(M):
    n = len(M)
    return all(M[i][j] == 0 for i in range(n) for j in range(i+1, n))

def es_identidad(M):
    n = len(M)
    return all((M[i][j] == 1 if i == j else M[i][j] == 0) for i in range(n) for j in range(n))

def producto_diagonal(M):
    from functools import reduce
    from operator import mul
    return reduce(mul, (Fraction(M[i][i]) for i in range(len(M))), Fraction(1, 1))

def fmt_num(x):
    return str(x.numerator) if isinstance(x, Fraction) and x.denominator == 1 else str(x)

def formato_matriz(M):
    """Devuelve la matriz alineada como texto"""
    n = len(M)
    cols = len(M[0])
    widths = [max(len(fmt_num(M[r][c])) for r in range(n)) for c in range(cols)]
    filas = []
    for fila in M:
        celdas = [fmt_num(fila[c]).rjust(widths[c]) for c in range(cols)]
        filas.append("  | " + "  ".join(celdas) + " |")
    return "\n".join(filas)

# =====================================================
#     APLICAR TEOREMAS Y MOSTRAR PROCEDIMIENTO
# =====================================================

def aplicar_teorema(M):
    """
    Detecta y aplica teoremas de determinantes.
    Devuelve un diccionario:
    {
        "aplica": bool,
        "teorema": str,
        "det": Fraction,
        "reporte": str,     # explicación + pasos
        "conclusion": str   # solo la conclusión final
    }
    """
    if not es_cuadrada(M):
        return {"aplica": False}

    n = len(M)
    reporte = ["Matriz A:", formato_matriz(M), ""]

    # 1️⃣ Matriz identidad
    if es_identidad(M):
        reporte.append("Teorema aplicado: Si A es la matriz identidad, entonces det(A) = 1.")
        reporte.append("\nProcedimiento:")
        reporte.append("1. Todos los elementos de la diagonal son 1.")
        reporte.append("2. Todos los demás elementos son 0.")
        reporte.append("3. Por definición, det(A) = 1.")
        return {
            "aplica": True,
            "teorema": "Matriz identidad",
            "det": Fraction(1, 1),
            "reporte": "\n".join(reporte),
            "conclusion": "Matriz identidad → det(A) = 1"
        }

    # 2️⃣ Matriz diagonal
    if es_diagonal(M):
        diag = [M[i][i] for i in range(n)]
        prod = producto_diagonal(M)
        reporte.append("Teorema aplicado: Si A es una matriz diagonal, su determinante es el producto de los elementos de la diagonal principal.")
        reporte.append("\nProcedimiento:")
        reporte.append(f"1. Diagonal principal: {', '.join(map(fmt_num, diag))}")
        reporte.append(f"2. Producto: {' × '.join(map(fmt_num, diag))} = {fmt_num(prod)}")
        return {
            "aplica": True,
            "teorema": "Matriz diagonal",
            "det": prod,
            "reporte": "\n".join(reporte),
            "conclusion": f"Matriz diagonal → det(A) = {fmt_num(prod)}"
        }

    # 3️⃣ Matriz triangular
    if es_triangular_superior(M) or es_triangular_inferior(M):
        tipo = "superior" if es_triangular_superior(M) else "inferior"
        diag = [M[i][i] for i in range(n)]
        prod = producto_diagonal(M)
        reporte.append(f"Teorema aplicado: Si A es una matriz triangular {tipo}, det(A) es el producto de las entradas sobre la diagonal principal.")
        reporte.append("\nProcedimiento:")
        reporte.append("1. Verificar que los elementos fuera de la zona triangular son 0.")
        reporte.append(f"2. Diagonal principal: {', '.join(map(fmt_num, diag))}")
        reporte.append(f"3. Producto: {' × '.join(map(fmt_num, diag))} = {fmt_num(prod)}")
        return {
            "aplica": True,
            "teorema": f"Matriz triangular {tipo}",
            "det": prod,
            "reporte": "\n".join(reporte),
            "conclusion": f"Matriz triangular {tipo} → det(A) = {fmt_num(prod)}"
        }

    # 4️⃣ Fila o columna nula
    if any(all(M[i][j] == 0 for j in range(n)) for i in range(n)):
        reporte.append("Teorema aplicado: Si A tiene una fila compuesta solo de ceros, entonces det(A) = 0.")
        reporte.append("\nProcedimiento:")
        reporte.append("1. Verificar fila nula: existe al menos una fila con todos los valores 0.")
        reporte.append("2. Por definición, el determinante es 0.")
        return {
            "aplica": True,
            "teorema": "Fila nula",
            "det": Fraction(0, 1),
            "reporte": "\n".join(reporte),
            "conclusion": "Fila nula → det(A) = 0"
        }

    if any(all(M[i][j] == 0 for i in range(n)) for j in range(n)):
        reporte.append("Teorema aplicado: Si A tiene una columna compuesta solo de ceros, entonces det(A) = 0.")
        reporte.append("\nProcedimiento:")
        reporte.append("1. Verificar columna nula: existe al menos una columna con todos los valores 0.")
        reporte.append("2. Por definición, el determinante es 0.")
        return {
            "aplica": True,
            "teorema": "Columna nula",
            "det": Fraction(0, 1),
            "reporte": "\n".join(reporte),
            "conclusion": "Columna nula → det(A) = 0"
        }

    return {"aplica": False}
