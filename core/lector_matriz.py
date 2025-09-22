from fractions import Fraction
from soporte import a_fraccion  # tu helper que ya convierte strings a Fraction

def limpiar_matriz(entries):
    """
    Convierte la grilla de Entry en una matriz estilo Matrix Calculator:
    - Quita filas/columnas completamente vacías.
    - Celdas vacías dentro de una fila o columna activa se rellenan con 0.
    """
    filas_raw = []
    for fila in entries:
        fila_vals = [e.get().strip() for e in fila]
        # La fila solo cuenta si tiene al menos un valor distinto de vacío
        if any(val != "" for val in fila_vals):
            filas_raw.append(fila_vals)

    if not filas_raw:
        return []  # Matriz vacía

    # Determinar qué columnas tienen al menos un valor
    cols = len(filas_raw[0])
    columnas_activas = [any(f[j] != "" for f in filas_raw) for j in range(cols)]

    # Construir la matriz final rellenando vacíos con 0
    matriz = []
    for fila in filas_raw:
        nueva_fila = []
        for j, val in enumerate(fila):
            if columnas_activas[j]:
                nueva_fila.append(a_fraccion(val if val != "" else "0"))
        matriz.append(nueva_fila)

    return matriz