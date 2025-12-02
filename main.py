# Punto de entrada: muestra el menú principal.
from ui.menu import mostrar_menu
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)

def main():
    mostrar_menu()

if __name__ == "__main__":
    main()
    