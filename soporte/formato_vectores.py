from fractions import Fraction

# =====================================================
#   UTILIDADES DE FORMATO PARA COMBINACIÓN LINEAL
# =====================================================

def convertir_a_fraccion(valor):
    """Convierte un número a Fraction, manteniendo precisión."""
    try:
        if isinstance(valor, Fraction):
            return valor
        if isinstance(valor, (int, float)):
            return Fraction(valor).limit_denominator()
        return Fraction(str(valor))
    except Exception:
        return Fraction(0)


def limpiar_numero(n):
    """Quita decimales .0 y convierte a entero si es exacto."""
    if isinstance(n, float) and n.is_integer():
        n = int(n)
    return str(n)


def formatear_vector(vector):
    """Devuelve un vector formateado tipo [  3 -1  7 ] sin .0 innecesarios."""
    if not vector:
        return "[ ]"
    partes = [f"{limpiar_numero(v):>3}" for v in vector]
    return "[" + " ".join(partes) + " ]"


def formatear_ecuaciones(vectores):
    """
    Devuelve el sistema homogéneo A·c = 0 alineado visualmente:
       3·c1 + c2 + 4·c3 = 0
      -c1 + 2·c2 -2·c3 = 0
       7·c1 + c3 = 0
    """
    if not vectores:
        return ""

    dim = len(vectores[0])
    n = len(vectores)
    lineas = []

    for i in range(dim):
        partes = []
        for j in range(n):
            coef = vectores[j][i]
            if coef == 0:
                continue

            signo = " + " if coef > 0 and partes else ""
            # Omitir el 1 o -1 delante de la variable
            if coef == 1:
                partes.append(f"{signo}c{j+1}")
            elif coef == -1:
                partes.append(f"{signo}-c{j+1}")
            else:
                partes.append(f"{signo}{limpiar_numero(coef)}·c{j+1}")

        ecuacion = "".join(partes) + " = 0"
        lineas.append(f"   {ecuacion}")

    return "\n".join(lineas)


def formatear_matriz_aumentada(vectores):
    """
    Devuelve la matriz aumentada (A|0) perfectamente alineada entre corchetes:
       [  3  1  4 |  0 ]
       [ -1  2 -2 |  0 ]
       [  7  0  1 |  0 ]
    """
    if not vectores:
        return "[ ]"

    matriz = [list(f) + [0] for f in zip(*vectores)]
    matriz_str = []

    for fila in matriz:
        valores = [f"{limpiar_numero(x):>3}" for x in fila[:-1]]
        valores_str = " ".join(valores)
        fila_str = f"[ {valores_str} | {limpiar_numero(fila[-1]):>3} ]"
        matriz_str.append("   " + fila_str)

    return "\n".join(matriz_str)


def formatear_combinacion_lineal(vectores):
    """
    Genera el texto formateado que se mostrará en el panel
    'Combinación lineal y sistema homogéneo' con corchetes incluidos.
    """
    if not vectores:
        return "No se han ingresado vectores."

    n = len(vectores)
    lineas = []

    # --- COMBINACIÓN LINEAL ---
    lineas.append("COMBINACIÓN LINEAL:")
    lineas.append("Buscamos escalares c₁, c₂, …, cₙ tales que:")
    lineas.append("   " + " + ".join([f"c{j+1}·v{j+1}" for j in range(n)]) + " = 0\n")

    # --- VECTORES DADOS ---
    lineas.append("Sustituyendo los vectores dados:")
    for j, v in enumerate(vectores):
        lineas.append(f"   v{j+1} = {formatear_vector(v)}")
    lineas.append("")

    # --- SISTEMA HOMOGÉNEO ---
    lineas.append("Esto equivale a resolver el sistema homogéneo A·c = 0:")
    lineas.append(formatear_ecuaciones(vectores))
    lineas.append("")

    # --- MATRIZ AUMENTADA ---
    lineas.append("Forma matricial aumentada (A|0):")
    lineas.append(formatear_matriz_aumentada(vectores))

    return "\n".join(lineas)
