import asyncio
import tkinter as tk
from tkinter import messagebox
from tkinter import CENTER

from generadores.generator_all import generate_excel
from generadores.generator_rms import generate_excel_rms

def center_window(window, width, height):
    # Obtiene las dimensiones de la pantalla
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcula la posición para centrar la ventana
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Establece la posición de la ventana
    window.geometry(f"{width}x{height}+{x}+{y}")

def generate_all():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_excel())
    messagebox.showinfo("Información", "Se han generado todos los archivos.")

def generate_rms():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_excel_rms())
    messagebox.showinfo("Información", "Se han generado los archivos RMS.")

def main():
    root = tk.Tk()
    root.title("Selección de Generación de Archivos")

    # Centra la ventana en la pantalla
    window_width = 400
    window_height = 200
    center_window(root, window_width, window_height)

    label = tk.Label(root, text="Seleccione una opción:")
    label.pack(pady=10)

    btn_all = tk.Button(root, text="Generar todos los archivos", command=generate_all)
    btn_all.pack(pady=5)

    btn_rms = tk.Button(root, text="Generar los RMS (Root Mean Square)", command=generate_rms)
    btn_rms.pack(pady=5)

    btn_exit = tk.Button(root, text="Salir", command=root.quit)
    btn_exit.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
