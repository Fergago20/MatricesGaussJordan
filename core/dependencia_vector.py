TOL = 1e-9

def es_cero(x, tol=TOL):
    return abs(x) <= tol

def es_vector_cero(v, tol=TOL):
    return all(es_cero(x, tol) for x in v)

def son_multiplos(u, v, tol=TOL):
    """True si existe k != 0 tal que u = k*v (y u,v no nulos)."""
    if len(u) != len(v):
        return False
    if es_vector_cero(u, tol) or es_vector_cero(v, tol):
        return False  # El caso del vector cero se maneja por otra regla
    k = None
    for a, b in zip(u, v):
        if es_cero(b, tol):
            if not es_cero(a, tol):
                return False
            else:
                continue
        ratio = a / b
        if k is None:
            k = ratio
        elif abs(ratio - k) > tol:
            return False
    return k is not None and not es_cero(k, tol)

def hay_multiplo_entre_pares(vectores, tol=TOL):
    n = len(vectores)
    for i in range(n):
        for j in range(i+1, n):
            if son_multiplos(vectores[i], vectores[j], tol):
                return True, (i, j)
    return False, None

def mas_vectores_que_entradas(vectores):
    n = len(vectores)
    dim = len(vectores[0]) if n > 0 else 0
    return n > dim