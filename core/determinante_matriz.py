# determinante_cofactores_final.py
from fractions import Fraction
from typing import List, Any, Dict

# =====================================================
#   FUNCIONES AUXILIARES
# =====================================================

def F(x):
    if isinstance(x, Fraction): return x
    if isinstance(x, int): return Fraction(x, 1)
    return Fraction(str(x))

def fmt(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

def to_square(A_raw: List[List[Any]]):
    A = [[F(v) for v in row] for row in A_raw]
    n = len(A)
    if any(len(r) != n for r in A):
        raise ValueError("La matriz debe ser cuadrada.")
    return A

def sgn(i, j):  # i,j base 0
    return Fraction(1, 1) if (i + j) % 2 == 0 else Fraction(-1, 1)

def minor(M, i, j):
    n = len(M)
    return [[M[r][c] for c in range(n) if c != j] for r in range(n) if r != i]

def det2(B):
    return B[0][0]*B[1][1] - B[0][1]*B[1][0]

def det_rec(M):
    n = len(M)
    if n == 1: return M[0][0]
    if n == 2: return det2(M)
    total = Fraction(0,1)
    for j in range(n):
        a = M[0][j]
        if a == 0: continue
        total += sgn(0,j) * a * det_rec(minor(M,0,j))
    return total

# =====================================================
#   FORMATO DE MATRICES PARA MOSTRAR DET
# =====================================================

def fmt_det_block(M2):
    """Dibuja un menor como
       | a  b |
       | c  d |"""
    cols = len(M2[0])
    widths = [max(len(fmt(M2[r][c])) for r in range(len(M2))) for c in range(cols)]
    def row_text(r):
        cells = [fmt(M2[r][c]).rjust(widths[c]) for c in range(cols)]
        return "| " + "  ".join(cells) + " |"
    return [row_text(r) for r in range(len(M2))]

# =====================================================
#   FUNCIÓN PRINCIPAL
# =====================================================

def determinante_cofactores(A_raw: List[List[Any]], expandir_por="fila", indice=0) -> Dict[str, Any]:
    """
    Calcula y muestra el desarrollo por cofactores con formato ordenado.
    Devuelve:
        {
          "metodo": "cofactores",
          "det": Fraction,
          "reporte": str   # texto completo con expansión, cálculo y conclusión
        }
    """
    A = to_square(A_raw)
    n = len(A)
    por_fila = expandir_por.lower().startswith("fila")
    idx = max(0, min(indice, n-1))

    reporte = []
    reporte.append("MÉTODO: Expansión por cofactores")
    reporte.append("Matriz A:")
    for fila in A:
        reporte.append("  " + str([fmt(x) for x in fila]))
    reporte.append("")
    reporte.append(f"Expansión por la {'fila' if por_fila else 'columna'} {idx+1}")
    reporte.append("")

    # --- línea de expansión tipo matriz ---
    terms_idx = [(idx, j) for j in range(n)] if por_fila else [(i, idx) for i in range(n)]
    expansion = ["det A ="]
    for k, (i, j) in enumerate(terms_idx):
        aij = A[i][j]
        coef = sgn(i,j) * aij
        pref_sign = "+ " if coef >= 0 and k != 0 else ("- " if coef < 0 else "  ")
        coef_abs = fmt(abs(coef))
        prefix = f"{pref_sign}{coef_abs}·det "
        Mij = minor(A,i,j)
        block = fmt_det_block(Mij)
        expansion.append(prefix + block[0])
        for ln in block[1:]:
            expansion.append(" " * len(prefix) + ln)
    reporte.extend(expansion)
    reporte.append("")

    # --- cálculo de cada término ---
    contribs = []
    for (i, j) in terms_idx:
        aij = A[i][j]
        if aij == 0:
            contribs.append(F(0))
            continue
        s = sgn(i,j)
        Mij = minor(A,i,j)
        detM = det_rec(Mij)
        term = s * aij * detM
        contribs.append(term)
        reporte.append(f"Término a_{{{i+1},{j+1}}}:")
        reporte.append(f"  Cofactor = (-1)^({i+1}+{j+1}) = {fmt(s)}")
        reporte.append("  Menor M:")
        for ln in fmt_det_block(Mij):
            reporte.append("    " + ln)
        if len(Mij) == 2:
            a,b = Mij[0][0], Mij[0][1]
            c,d = Mij[1][0], Mij[1][1]
            ad, bc = a*d, b*c
            reporte.append(f"  det(M) = {fmt(a)}·{fmt(d)} - {fmt(b)}·{fmt(c)} = {fmt(ad)} - {fmt(bc)} = {fmt(detM)}")
        else:
            reporte.append(f"  det(M) = {fmt(detM)}")
        reporte.append(f"  Contribución = {fmt(s)} × {fmt(aij)} × {fmt(detM)} = {fmt(term)}")
        reporte.append("")

    total = sum(contribs, Fraction(0,1))
    rep_suma = " + ".join(fmt(c) for c in contribs if c >= 0)
    rep_suma += "".join(" - " + fmt(abs(c)) for c in contribs if c < 0)
    reporte.append(f"Suma de contribuciones: {rep_suma} = {fmt(total)}")
    reporte.append("")
    # --- conclusión final ---
    usados = [f"a_{{{i+1},{j+1}}}" for (i,j), c in zip(terms_idx, contribs) if c != 0]
    if usados:
        reporte.append(f"CONCLUSIÓN: Solo aportan {', '.join(usados)}.  →  det(A) = {fmt(total)}")
    else:
        reporte.append(f"CONCLUSIÓN: Todos los términos se anulan.  →  det(A) = {fmt(total)}")

    return {"metodo": "cofactores", "det": total, "reporte": "\n".join(reporte)}
