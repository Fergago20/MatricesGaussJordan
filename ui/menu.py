import tkinter as tk
from tkinter import messagebox
from soporte import preparar_ventana
from ui.gauss_app import AppGauss
from ui.gauss_jordan_app import AppGaussJordan

def mostrar_menu():
    root = tk.Tk()
    root.title("Resolución de Sistemas de Ecuaciones")
    root.configure(bg="#101010")
    preparar_ventana(root, usar_maximizada=True)

    titulo = tk.Label(root, text="Elige un método", fg="#EAEAEA", bg="#101010",
                      font=("Segoe UI", 16, "bold"))
    titulo.pack(pady=(18,10))

    cont = tk.Frame(root, bg="#101010")
    cont.pack(pady=6)

    def volver_a_menu():
        root.deiconify()                # vuelve a mostrar el menú
        preparar_ventana(root, True)    # asegurar tamaño/posición al volver

    def abrir_gauss():
        root.withdraw()
        AppGauss(toplevel_parent=root, on_volver=volver_a_menu)

    def abrir_gauss_jordan():
        root.withdraw()
        AppGaussJordan(toplevel_parent=root, on_volver=volver_a_menu)

    btn1 = tk.Button(cont, text="Método de Gauss", width=22, command=abrir_gauss,
                     bg="#1f1f1f", fg="#ffffff", activebackground="#2a2a2a",
                     activeforeground="#ffffff")
    btn2 = tk.Button(cont, text="Método de Gauss-Jordan", width=22, command=abrir_gauss_jordan,
                     bg="#1f1f1f", fg="#ffffff", activebackground="#2a2a2a",
                     activeforeground="#ffffff")

    btn1.grid(row=0, column=0, padx=12, pady=8)
    btn2.grid(row=0, column=1, padx=12, pady=8)

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
