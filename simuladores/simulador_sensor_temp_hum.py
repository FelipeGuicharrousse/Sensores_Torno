import socket
import time
import random

# Configuración del servidor UDP
UDP_IP = "127.0.0.1"  # Dirección IP local
UDP_PORT = 5500       # Puerto para la comunicación UDP

# Crear un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Función para simular datos del sensor
def simulate_sensor_temp_hum():
    # Simular algún tipo de lectura del sensor
    temperatura = random.uniform(00.0, 99.9)  # Simular temperatura entre 0°C y 99.2°C
    humedad = random.uniform(00.0, 99.9)      # Simular humedad entre 0% y 99.9%
    return temperatura, humedad

# Ciclo principal del servidor
while True:
    temperatura, humedad = simulate_sensor_temp_hum()
    # Formato de los datos a enviar
    data = f"A {humedad:.2f} {temperatura:.2f} 0D 0A"

    # Envía los datos al cliente
    sock.sendto(data.encode(), (UDP_IP, UDP_PORT))
    print(f"Datos enviados: {data}")

    # Espera aproximadamente un segundo antes de enviar la próxima actualización
    time.sleep(1)
