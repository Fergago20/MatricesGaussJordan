from core.dependencia_vector import es_cero, es_vector_cero, TOL, hay_multiplo_entre_pares, mas_vectores_que_entradas
def copia_matriz(A):
    return [fila[:] for fila in A]

def rref(A, tol=TOL):
    """Forma reducida por filas (simple, suficiente para rango/consistencia)."""
    if not A:
        return [], []
    M = copia_matriz(A)
    m, n = len(M), len(M[0])
    fila = 0
    pivotes = []
    for col in range(n):
        # Buscar pivote por máximo absoluto (estabilidad básica)
        piv = fila
        for r in range(fila+1, m):
            if abs(M[r][col]) > abs(M[piv][col]):
                piv = r
        if es_cero(M[piv][col], tol):
            continue
        # Intercambiar
        M[fila], M[piv] = M[piv], M[fila]
        # Normalizar
        piv_val = M[fila][col]
        M[fila] = [x / piv_val for x in M[fila]]
        # Eliminar en otras filas
        for r in range(m):
            if r != fila and not es_cero(M[r][col], tol):
                f = M[r][col]
                M[r] = [xr - f * xc for xr, xc in zip(M[r], M[fila])]
        pivotes.append(col)
        fila += 1
        if fila == m:
            break
    # Limpieza numérica
    for i in range(m):
        for j in range(n):
            if es_cero(M[i][j], tol):
                M[i][j] = 0.0
    return M, pivotes

def rango(A, tol=TOL):
    _, piv = rref(A, tol)
    return len(piv)

def resolver_Ax_eq_b(A, b, tol=TOL):
    """Devuelve True si el sistema A x = b es consistente (no necesitamos x explícita)."""
    if not A:
        return True
    # Matriz aumentada
    Aug = [fila[:] + [bb] for fila, bb in zip(A, b)]
    R, _ = rref(Aug, tol)
    m, n1 = len(R), len(R[0]) - 1  # n1 = num columnas de A
    # Inconsistencia si [0 ... 0 | c] con c != 0
    for i in range(m):
        if all(es_cero(R[i][j], tol) for j in range(n1)) and not es_cero(R[i][n1], tol):
            return False
    return True

# --------------------------
# Reglas de dependencia claras
# --------------------------

def alguno_es_combinacion_de_los_otros(vectores, tol=TOL):
    """
    Verifica si existe v_i que sea combinación lineal de los demás:
    Resolviendo A_otros * c = v_i (consistencia basta).
    """
    n = len(vectores)
    if n <= 1:
        return False, None
    dim = len(vectores[0])

    for i in range(n):
        otros = [vectores[j] for j in range(n) if j != i]  # (n-1) vectores
        # Construir A con columnas = 'otros' -> como filas para RREF
        # A es dim x (n-1)
        A_cols = list(zip(*otros)) if otros else [[] for _ in range(dim)]
        A = [list(f) for f in A_cols]
        b = vectores[i][:]
        if resolver_Ax_eq_b(A, b, tol):
            return True, i
    return False, None

def solo_solucion_trivial(vectores, tol=TOL):
    """
    Reglas: independencia <=> el sistema homogéneo A c = 0
    solo tiene la solución trivial. Equivalente a rango(A) = número de vectores.
    """
    if not vectores:
        return True
    # Matriz con columnas = vectores -> como filas para RREF
    A_cols = list(zip(*vectores))  # dim x n
    A = [list(f) for f in A_cols]
    return rango(A, tol) == len(vectores)

# --------------------------
# Función principal
# --------------------------

def analizar_conjunto(vectores, tol=TOL):
    """
    vectores: lista de listas, todos de igual longitud.
    Devuelve dict con el veredicto y qué regla lo determinó.
    """
    # Validaciones simples
    if not vectores:
        return {"independiente": True, "motivo": "Conjunto vacío (convención)."}
    dim_set = {len(v) for v in vectores}
    if len(dim_set) != 1:
        return {"error": "Todos los vectores deben tener la misma dimensión."}

    # Regla 1: vector cero -> dependiente
    if any(es_vector_cero(v, tol) for v in vectores):
        return {"independiente": False, "regla": "vector_cero"}

    # Regla 2: si hay pares múltiplos -> dependiente
    hay_mult, par = hay_multiplo_entre_pares(vectores, tol)
    if hay_mult:
        return {"independiente": False, "regla": "multiplo_de_otro", "detalle": {"indices": par}}

    # Regla 3: más vectores que entradas (n > dim) -> dependiente
    if mas_vectores_que_entradas(vectores):
        return {"independiente": False, "regla": "mas_vectores_que_entradas"}

    # Regla 4: alguno es combinación lineal de los otros -> dependiente
    hay_comb, idx = alguno_es_combinacion_de_los_otros(vectores, tol)
    if hay_comb:
        return {"independiente": False, "regla": "combinacion_lineal", "detalle": {"indice_objetivo": idx}}

    # Regla 5: solo solución trivial -> independiente
    if solo_solucion_trivial(vectores, tol):
        return {"independiente": True, "regla": "solo_solucion_trivial"}
    else:
        # Por seguridad, si llega aquí (raro), marcamos dependiente
        return {"independiente": False, "regla": "no_trivial_detectado_por_rango"}