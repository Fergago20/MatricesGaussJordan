# ============================================
#  Inversa con regla 2×2 + Gauss–Jordan (fallback)
#  - Español, sin prints
#  - Devuelve: paso a paso + conclusiones
#  - Verificación: A·A^{-1} e A^{-1}·A ≈ I (si hay inversa)
# ============================================

from fractions import Fraction
from core.operaciones_matrices import multiplicar_con_pasos

# ---------- Utilidades ----------
def forma(M):
    return (len(M), len(M[0]) if M else 0)

def copiar(M):
    return [fila[:] for fila in M]

def identidad(n, uno):
    cero = type(uno)()
    I = [[cero for _ in range(n)] for _ in range(n)]
    for i in range(n):
        I[i][i] = uno
    return I

def preparar_tipo(M, modo, convertir_a_fraccion):
    """
    Convierte M a float o Fraction según 'modo'.
    Retorna (M_convertida, uno, cero).
    """
    if modo == "fraccion":
        if convertir_a_fraccion is None:
            convertir_a_fraccion = globals().get("to_fraccion") or globals().get("_to_fraction")
        if convertir_a_fraccion is None:
            raise ValueError("Falta 'convertir_a_fraccion' para modo='fraccion'.")
        X = [[convertir_a_fraccion(x) for x in fila] for fila in M]
        return X, Fraction(1, 1), Fraction(0, 1)
    # por defecto: float
    X = [[float(x) for x in fila] for fila in M]
    return X, 1.0, 0.0

def multiplicar(A, B):
    m, k = forma(A); k2, n = forma(B)
    if k != k2:
        raise ValueError("Dimensiones incompatibles en multiplicación.")
    tipo = type(A[0][0]) if m and k else float
    cero = tipo()
    C = [[cero for _ in range(n)] for _ in range(m)]
    for i in range(m):
        Ai = A[i]
        for j in range(n):
            s = cero
            for t in range(k):
                s = s + Ai[t] * B[t][j]
            C[i][j] = s
    return C

def es_identidad(M, uno, tol=1e-10, modo="float"):
    n, m = forma(M)
    if n != m:
        return False
    for i in range(n):
        for j in range(n):
            v = M[i][j]
            if modo == "fraccion":
                if (i == j and v != uno) or (i != j and v != 0):
                    return False
            else:
                if i == j and abs(v - 1.0) > tol:
                    return False
                if i != j and abs(v) > tol:
                    return False
    return True

def formatear_matriz_simple(M):
    """Formateo de texto básico (reemplaza por tus formateadores si quieres)."""
    if M is None:
        return "—"
    filas = []
    for f in M:
        filas.append("  " + "  ".join(str(x) for x in f))
    return "[\n" + "\n".join(filas) + "\n]"

# ---------- Regla rápida 2×2 ----------
def inversa_por_formula_2x2(M, *, modo, tolerancia, convertir_a_fraccion):
    pasos = []
    X, uno, cero = preparar_tipo(M, modo, convertir_a_fraccion)
    a, b = X[0][0], X[0][1]
    c, d = X[1][0], X[1][1]
    det = a * d - b * c

    pasos.append(("Matriz 2×2: det = ad − bc", [["a","b"],["c","d"]]))
    pasos.append((f"det(A) = {det}", copiar(X)))

    # Si det≈0, NO dividir; dejemos que el orquestador haga fallback a Gauss–Jordan
    if (modo == "float" and abs(det) <= tolerancia) or (modo == "fraccion" and det == 0):
        pasos.append(("det(A) = 0 ⇒ NO usar fórmula (fallback a Gauss–Jordan)", copiar(X)))
        return None, pasos, det

    inv = [[ d/det, -b/det],
           [-c/det,  a/det]]
    pasos.append(("A^{-1} por fórmula 2×2", copiar(inv)))
    return inv, pasos, det

# ---------- Gauss–Jordan con [A | I] ----------
def inversa_por_gauss_jordan(M, *, modo, tolerancia, convertir_a_fraccion):
    pasos = []
    X, uno, _ = preparar_tipo(M, modo, convertir_a_fraccion)
    n, m = forma(X)
    if n == 0 or m == 0:
        pasos.append(("Matriz vacía", None))
        return None, pasos
    if n != m:
        pasos.append(("Matriz no cuadrada ⇒ no tiene inversa", copiar(X)))
        return None, pasos

    Aum = [X[i] + identidad(n, uno)[i] for i in range(n)]
    pasos.append(("[A | I] (inicial)", copiar(Aum)))

    for col in range(n):
        # Pivoteo parcial
        fila_piv = max(range(col, n), key=lambda i: abs(Aum[i][col]))
        piv_val = Aum[fila_piv][col]
        if (modo == "float" and abs(piv_val) <= tolerancia) or (modo == "fraccion" and piv_val == 0):
            pasos.append(("Pivote ~ 0 ⇒ A es singular, no tiene inversa", copiar(Aum)))
            return None, pasos
        if fila_piv != col:
            Aum[col], Aum[fila_piv] = Aum[fila_piv], Aum[col]
            pasos.append((f"F{col+1} ↔ F{fila_piv+1}", copiar(Aum)))

        # Normalizar fila pivote
        p = Aum[col][col]
        if (modo == "float" and abs(p - 1) > tolerancia) or (modo == "fraccion" and p != uno):
            for j in range(2*n):
                Aum[col][j] = Aum[col][j] / p
            pasos.append((f"F{col+1} ← F{col+1} / {p}", copiar(Aum)))

        # Anular el resto de la columna
        for r in range(n):
            if r == col:
                continue
            f = Aum[r][col]
            if (modo == "float" and abs(f) <= tolerancia) or (modo == "fraccion" and f == 0):
                continue
            for j in range(2*n):
                Aum[r][j] = Aum[r][j] - f * Aum[col][j]
            pasos.append((f"F{r+1} ← F{r+1} - ({f})·F{col+1}", copiar(Aum)))

    inv = [fila[n:] for fila in Aum]

    # Limpieza estética (float)
    if modo == "float":
        for i in range(n):
            for j in range(n):
                if abs(inv[i][j]) < tolerancia:
                    inv[i][j] = 0.0

    pasos.append(("[I | A^{-1}] (final)", copiar(Aum)))
    return inv, pasos

# ---------- Orquestador ----------
def inversa_matriz_con_reglas(
    matriz,
    *,
    modo="float",                # "float" | "fraccion"
    tolerancia=1e-12,
    convertir_a_fraccion=None
):
    """
    Retorna un dict:
      {
        "procedimiento": str,
        "conclusiones":  str,
        "resultado_lista": list|None,
        "resultado_frac": str
      }
    """
    try:
        procedimiento = []
        conclusiones = []
        pasos_acumulados = []

        f, c = forma(matriz)
        if f == 0 or c == 0:
            return {
                "procedimiento": "Matriz vacía.",
                "conclusiones": "No se puede calcular la inversa.",
                "resultado_lista": None,
                "resultado_frac": "—"
            }

        inversa = None
        det = None

        # --- Caso 2×2: primero fórmula; si det≈0 -> fallback Gauss–Jordan ---
        if f == 2 and c == 2:
            inv2, pasos2, det = inversa_por_formula_2x2(
                matriz, modo=modo, tolerancia=tolerancia, convertir_a_fraccion=convertir_a_fraccion
            )
            pasos_acumulados.extend(pasos2)
            if inv2 is not None:
                inversa = inv2
                procedimiento.append("Método: Regla rápida 2×2 (A^{-1} = 1/(ad−bc) [[d,-b],[-c,a]]).")
            else:
                procedimiento.append("det(A)=0 en 2×2 ⇒ Fallback: Gauss–Jordan con [A | I].")
                invG, pasosG = inversa_por_gauss_jordan(
                    matriz, modo=modo, tolerancia=tolerancia, convertir_a_fraccion=convertir_a_fraccion
                )
                pasos_acumulados.extend(pasosG)
                inversa = invG
        else:
            # --- Caso general: Gauss–Jordan ---
            invG, pasosG = inversa_por_gauss_jordan(
                matriz, modo=modo, tolerancia=tolerancia, convertir_a_fraccion=convertir_a_fraccion
            )
            pasos_acumulados.extend(pasosG)
            inversa = invG
            if f == c:
                procedimiento.append("Método: Gauss–Jordan con [A | I].")

        # Texto del procedimiento (paso a paso)
        for desc, snap in pasos_acumulados:
            if snap is None:
                procedimiento.append(f"- {desc}")
            else:
                procedimiento.append(f"- {desc}\n{formatear_matriz_simple(snap)}")

        # --- Conclusiones y verificación ---
        if inversa is None:
            if f != c:
                conclusiones.append("Conclusión: Matriz no cuadrada ⇒ no es invertible.")
            elif f == c == 2 and det is not None and ((modo == "float" and abs(det) <= tolerancia) or (modo == "fraccion" and det == 0)):
                conclusiones.append(f"Conclusión: det(A) = {det} ⇒ A no tiene inversa.")
            else:
                conclusiones.append("Conclusión: A es singular (algún pivote ~ 0) ⇒ no tiene inversa.")

            return {
                "procedimiento": "\n".join(procedimiento),
                "conclusiones": "\n".join(conclusiones),
                "resultado_lista": None,
                "resultado_frac": "No se puede calcular la inversa."
            }

        # Verificación A·A^{-1} y A^{-1}·A (solo si hay inversa)
        A_cast, _, _ = preparar_tipo(matriz, modo, convertir_a_fraccion)
        Ainv_cast, _, _ = preparar_tipo(inversa, modo, convertir_a_fraccion)

        # Verificación 1: A · A^{-1}
        ver1 = multiplicar_con_pasos(A_cast, Ainv_cast)
        procedimiento.append("Verificación 1: A · A^{-1}")
        procedimiento.append(ver1["procedimiento"])
        procedimiento.append("Resultado A·A^{-1}:\n" + ver1["resultado_frac"])
        # ver1["resultado_lista"] viene en Fraction → chequeo exacto
        ok_izq = es_identidad(ver1["resultado_lista"], Fraction(1, 1), modo="fraccion")

        # Verificación 2: A^{-1} · A
        ver2 = multiplicar_con_pasos(Ainv_cast, A_cast)
        procedimiento.append("Verificación 2: A^{-1} · A")
        procedimiento.append(ver2["procedimiento"])
        procedimiento.append("Resultado A^{-1}·A:\n" + ver2["resultado_frac"])
        ok_der = es_identidad(ver2["resultado_lista"], Fraction(1, 1), modo="fraccion")

        conclusiones.append("Verificación:")
        conclusiones.append("  • A · A^{-1} = I  ✅" if ok_izq else "  • A · A^{-1} ≠ I  ❌")
        conclusiones.append("  • A^{-1} · A = I  ✅" if ok_der else "  • A^{-1} · A ≠ I  ❌")
        if ok_izq and ok_der:
            conclusiones.append("Conclusión: La matriz calculada es efectivamente A^{-1}.")
        else:
            conclusiones.append("Conclusión: La verificación no pasó; revisa datos y tolerancia.")

        return {
            "procedimiento": "\n".join(procedimiento),
            "conclusiones": "\n".join(conclusiones),
            "resultado_lista": inversa,
            "resultado_frac": formatear_matriz_simple(inversa)
        }

    # Cinturón y tirantes: si algo externo divide por 0, no propagamos la excepción.
    except ZeroDivisionError:
        return {
            "procedimiento": "Se detectó una división entre 0 al intentar calcular la inversa. "
                             "Se canceló el cálculo para evitar un fallo.",
            "conclusiones": "Conclusión: no se puede calcular la inversa (determinante o pivote nulos).",
            "resultado_lista": None,
            "resultado_frac": "No se puede calcular la inversa."
        }
