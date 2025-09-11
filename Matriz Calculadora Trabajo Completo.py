import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from controller.solucion import Matriz

solucion = Matriz()

# Paleta de colores
BG_COLOR = "#f4f6fb"
FRAME_COLOR = "#e3e8ee"
ACCENT_COLOR = "#3b82f6"
BTN_COLOR = "#2563eb"
TEXT_COLOR = "#22223b"
ENTRY_BG = "#ffffff"
ENTRY_FG = "#22223b"

def generar_matriz():
    try:
        m = int(entry_filas.get())
        n = int(entry_columnas.get())
        if m <= 0 or n <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Número de filas y columnas debe ser entero positivo.")
        return

    for widget in frame_matriz.winfo_children():
        widget.destroy()
    entry_matriz.clear()

    for i in range(m):
        row_entries = []
        for j in range(n+1):
            e = tk.Entry(frame_matriz, width=7, font=("Segoe UI", 12), bg=ENTRY_BG, fg=ENTRY_FG, relief="flat", justify="center")
            e.grid(row=i, column=j, padx=4, pady=4, ipady=4)
            row_entries.append(e)
        entry_matriz.append(row_entries)

def resolver():
    A = []
    try:
        for row in entry_matriz:
            fila = [float(e.get().replace(",", ".")) for e in row]
            A.append(fila)
    except ValueError:
        messagebox.showerror("Error", "Todas las entradas deben ser números válidos.")
        return

    m = len(A)
    n = len(A[0])-1
    estado, sol, historial = solucion.GaussJordan(A, m, n)

    text_output.config(state="normal")
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "=== Proceso paso a paso ===\n\n")
    for paso in historial:
        text_output.insert(tk.END, paso + "\n")
    text_output.insert(tk.END, "=== Resultado final ===\n\n")
    text_output.insert(tk.END, solucion.matriz_str(A) + "\n")
    if estado == "unique":
        text_output.insert(tk.END, "✅ Solución única:\n")
        text_output.insert(tk.END, "Variables pivote en columnas: " + ", ".join(map(str, solucion.mostrar_pivotes(A))) + "\n")
        for i, val in enumerate(sol):
            text_output.insert(tk.END, f"x{i+1} = {val:.6f}\n")
    elif estado == "infinite":
        text_output.insert(tk.END, "ℹ️ Infinitas soluciones (variables libres)\n")
        text_output.insert(tk.END, "Variables pivote en columnas: " + ", ".join(map(str, solucion.mostrar_pivotes(A))) + "\n")
    else:
        text_output.insert(tk.END, "❌ Sistema inconsistente: no tiene solución\n")
        text_output.insert(tk.END, "Variables pivote en columnas: " + ", ".join(map(str, solucion.mostrar_pivotes(A))) + "\n")
    text_output.config(state="disabled")

root = tk.Tk()
root.title("Calculadora Gauss-Jordan Visual")
root.geometry("900x700")
root.configure(bg=BG_COLOR)

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 12, "bold"), background=BTN_COLOR, foreground="white", borderwidth=0, focusthickness=3, focuscolor=ACCENT_COLOR)
style.map("TButton", background=[("active", ACCENT_COLOR)])

# Encabezado
header = tk.Label(root, text="Calculadora Gauss-Jordan", font=("Segoe UI", 24, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
header.pack(pady=(30, 10))

# Frame superior
frame_top = tk.Frame(root, bg=FRAME_COLOR, bd=0, relief="flat")
frame_top.pack(pady=15, padx=30, fill="x")

tk.Label(frame_top, text="Ecuaciones (filas):", font=("Segoe UI", 13), bg=FRAME_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, padx=10, pady=10)
entry_filas = tk.Entry(frame_top, width=5, font=("Segoe UI", 13), bg=ENTRY_BG, fg=ENTRY_FG, relief="flat", justify="center")
entry_filas.grid(row=0, column=1, padx=5)

tk.Label(frame_top, text="Incógnitas (columnas):", font=("Segoe UI", 13), bg=FRAME_COLOR, fg=TEXT_COLOR).grid(row=0, column=2, padx=10)
entry_columnas = tk.Entry(frame_top, width=5, font=("Segoe UI", 13), bg=ENTRY_BG, fg=ENTRY_FG, relief="flat", justify="center")
entry_columnas.grid(row=0, column=3, padx=5)

btn_generar = ttk.Button(frame_top, text="Generar matriz", command=generar_matriz)
btn_generar.grid(row=0, column=4, padx=20)

# Frame para matriz
frame_matriz = tk.Frame(root, bg=BG_COLOR)
frame_matriz.pack(pady=10)

entry_matriz = []

# Botón de resolver
btn_resolver = ttk.Button(root, text="Resolver", command=resolver)
btn_resolver.pack(pady=15)

# Cuadro de texto para mostrar historial
text_output = scrolledtext.ScrolledText(root, width=100, height=25, font=("Consolas", 12), bg=ENTRY_BG, fg=TEXT_COLOR, relief="flat", borderwidth=0)
text_output.pack(pady=20, padx=30)
text_output.config(state="disabled")

root.mainloop()
