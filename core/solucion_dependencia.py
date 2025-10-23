from soporte.formato_matrices import formatear_matriz, matriz_alineada_con_titulo
from soporte.formato_vectores import formatear_vector, formatear_ecuaciones, formatear_matriz_aumentada

TOL = 1e-8

# =====================================================
#   FUNCIONES AUXILIARES
# =====================================================
def es_cero(valor, tol=TOL):
    return abs(valor) < tol

def es_vector_cero(vector, tol=TOL):
    return all(es_cero(v, tol) for v in vector)

def copiar_matriz(A):
    return [fila[:] for fila in A]

# =====================================================
#   GAUSS–JORDAN
# =====================================================
def aplicar_gauss_jordan(A):
    """
    Aplica el método de Gauss–Jordan mostrando los pasos intermedios.
    Devuelve la matriz reducida final y el texto de los pasos.
    """
    M = copiar_matriz(A)
    pasos = []
    filas, columnas = len(M), len(M[0])
    fila_pivote = 0

    pasos.append(matriz_alineada_con_titulo("Matriz aumentada inicial (A|0):", M, con_barra=True))

    for col in range(columnas - 1):
        # Buscar pivote
        pivote = None
        for i in range(fila_pivote, filas):
            if not es_cero(M[i][col]):
                pivote = i
                break
        if pivote is None:
            continue

        # Intercambiar filas si es necesario
        if pivote != fila_pivote:
            M[fila_pivote], M[pivote] = M[pivote], M[fila_pivote]
            pasos.append(f"F{fila_pivote+1} ↔ F{pivote+1}")
            pasos.append(formatear_matriz(M, corchetes=True))

        # Normalizar pivote
        pivote_valor = M[fila_pivote][col]
        if not es_cero(pivote_valor - 1.0):
            M[fila_pivote] = [x / pivote_valor for x in M[fila_pivote]]
            pasos.append(f"F{fila_pivote+1} ÷ {pivote_valor:.4g}")
            pasos.append(formatear_matriz(M, corchetes=True))

        # Eliminar en otras filas
        for i in range(filas):
            if i != fila_pivote and not es_cero(M[i][col]):
                factor = M[i][col]
                M[i] = [x - factor * y for x, y in zip(M[i], M[fila_pivote])]
                pasos.append(f"F{i+1} ← F{i+1} - ({factor:.4g})·F{fila_pivote+1}")
                pasos.append(formatear_matriz(M, corchetes=True))

        fila_pivote += 1
        if fila_pivote == filas:
            break

    pasos.append("Matriz reducida final (RREF):")
    pasos.append(formatear_matriz(M, corchetes=True))
    return M, pasos

def rango_matriz(A):
    copia = copiar_matriz(A)
    M, _ = aplicar_gauss_jordan(copia)
    return sum(not es_vector_cero(f) for f in M)

# =====================================================
#   ANÁLISIS PRINCIPAL
# =====================================================
def analizar_independencia(vectores):
    """
    Determina si los vectores son linealmente dependientes o independientes.
    Retorna un diccionario con: conclusión, razonamiento y criterio algebraico.
    """
    if not vectores:
        return {
            "independiente": True,
            "regla": "conjunto_vacio",
            "conclusion": "Conjunto INDEPENDIENTE",
            "razonamiento": "Conjunto vacío: por convención siempre es independiente.",
            "criterio": "No hay ecuaciones que resolver, independencia trivial."
        }

    # Vector nulo → dependencia inmediata
    for idx, v in enumerate(vectores, start=1):
        if es_vector_cero(v):
            return {
                "independiente": False,
                "regla": "vector_cero",
                "conclusion": "Conjunto DEPENDIENTE",
                "razonamiento": f"v{idx} es el vector cero → dependencia inmediata.",
                "criterio": "→ combinación no trivial posible (c≠0)."
            }

    # Más vectores que la dimensión
    dimension = len(vectores[0])
    if len(vectores) > dimension:
        return {
            "independiente": False,
            "regla": "teorema_1",
            "conclusion": "Conjunto DEPENDIENTE",
            "razonamiento": "Si n > dimensión, el conjunto es linealmente dependiente.",
            "criterio": "Criterio algebraico → sistema con más incógnitas que ecuaciones, variables libres → dependencia."
        }

    # Múltiplos escalares (comparación par a par)
    for i in range(len(vectores)):
        for j in range(i + 1, len(vectores)):
            vi, vj = vectores[i], vectores[j]
            cociente = None
            multiples = True

            for a, b in zip(vi, vj):
                if es_cero(a) and es_cero(b):
                    continue  # ambos ceros: siguen siendo proporcionales
                elif es_cero(a) or es_cero(b):
                    multiples = False
                    break  # uno es cero y el otro no → no múltiplos
                else:
                    ratio = b / a
                    if cociente is None:
                        cociente = ratio
                    elif abs(ratio - cociente) > 1e-6:
                        multiples = False
                        break

            if multiples and cociente is not None:
                # Mostrar limpio sin .0
                if abs(cociente - round(cociente)) < 1e-6:
                    multiplo_str = str(int(round(cociente)))
                else:
                    multiplo_str = f"{cociente:.2f}"

                return {
                    "independiente": False,
                    "regla": "multiplo_escalar",
                    "conclusion": "Conjunto DEPENDIENTE",
                    "razonamiento": (
                        f"v{j+1} = {multiplo_str}·v{i+1} → "
                        "Si un vector es múltiplo escalar de otro, el conjunto es dependiente."
                    ),
                    "criterio": "Criterio algebraico → combinación no trivial: una fila depende de otra."
                }

    # Sistema homogéneo A·c = 0
    A_cols = list(zip(*vectores))
    matriz = [list(f) + [0] for f in A_cols]
    rango = rango_matriz(matriz)
    num_vectores = len(vectores)

    # Evaluación algebraica
    if rango == num_vectores:
        return {
            "independiente": True,
            "regla": "criterio_algebraico_trivial",
            "conclusion": "Conjunto INDEPENDIENTE",
            "razonamiento": "No hay relaciones lineales entre los vectores.",
            "criterio": "Criterio algebraico → No hay variables libres, única solución trivial (c = 0)."
        }
    else:
        return {
            "independiente": False,
            "regla": "Combinacion_lineal",
            "conclusion": "Conjunto DEPENDIENTE",
            "razonamiento": "Existen combinaciones no triviales entre los vectores.",
            "criterio": "Criterio algebraico → Hay variables libres, infinitas soluciones → combinación no trivial (dependencia), un vector es la combinacion lineal de otro."
        }

# =====================================================
#   DESARROLLO ALGEBRAICO DETALLADO
# =====================================================

def generar_proceso_algebraico(vectores):
    """
    Genera texto completo: combinación lineal → sistema homogéneo → Gauss–Jordan → conclusión.
    """
    texto = []
    n = len(vectores)
    if n == 0:
        return "No se han ingresado vectores."

    # ============================================
    # COMBINACIÓN LINEAL
    # ============================================
    texto.append("COMBINACIÓN LINEAL:")
    texto.append("Buscamos escalares c₁, c₂, …, cₙ tales que:")
    texto.append("   " + " + ".join([f"c{j+1}·v{j+1}" for j in range(n)]) + " = 0\n")

    texto.append("Sustituyendo los vectores dados:")
    for j, v in enumerate(vectores):
        texto.append(f"   v{j+1} = {formatear_vector(v)}")
    texto.append("")

    # ============================================
    # SISTEMA HOMOGÉNEO
    # ============================================
    texto.append("Esto equivale a resolver el sistema homogéneo A·c = 0:")
    texto.append(formatear_ecuaciones(vectores))
    texto.append("")

    # ============================================
    # FORMA MATRICIAL
    # ============================================
    texto.append("Forma matricial aumentada (A|0):")
    texto.append(formatear_matriz_aumentada(vectores))
    texto.append("")

    # ============================================
    # GAUSS–JORDAN
    # ============================================
    texto.append("Aplicando el método de Gauss–Jordan:")
    matriz = [list(f) + [0] for f in zip(*vectores)]
    M_final, pasos = aplicar_gauss_jordan(matriz)
    texto.extend(pasos)
    texto.append("")

    # ============================================
    # CONCLUSIÓN
    # ============================================
    identidad = all(
        len(M_final) > i and len(M_final[0]) > i and abs(M_final[i][i] - 1.0) < TOL
        for i in range(min(len(M_final), len(M_final[0]) - 1))
    )

    texto.append("Conclusión:")
    if identidad:
        texto.append("   La matriz reducida es la identidad → solo solución trivial (c = 0).")
        texto.append("   ⇒ Los vectores son LINEALMENTE INDEPENDIENTES.")
    else:
        texto.append("   Existen variables libres → soluciones no triviales (c ≠ 0).")
        texto.append("   ⇒ Los vectores son LINEALMENTE DEPENDIENTES.")

    return "\n".join(texto)
