import asyncio
from generadores.generator_all import generate_excel
from generadores.generator_rms import generate_excel_rms

def main():
    print("Seleccione una opción:")
    print("1. Generar todos los archivos")
    print("2. Generar los rms (Root Mean Square)")
    print("3. Salir")
    
    choice = input("Ingrese su elección: ")
    
    loop = asyncio.get_event_loop()
    
    if choice == "1":
        loop.run_until_complete(generate_excel())
    elif choice == "2":
        loop.run_until_complete(generate_excel_rms())
    elif choice == "3":
        print("Saliendo...")
    else:
        print("Opción inválida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()
