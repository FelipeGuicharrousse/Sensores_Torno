import socket
import time
import random

# Configuración del servidor UDP
UDP_IP = "127.0.0.1"  # Dirección IP local
UDP_PORT = 5006      # Puerto para la comunicación UDP

# Crear un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Función para simular datos del sensor
def simulate_sensor_rpm():
    # Simular algún tipo de lectura del sensor
    velocidad = random.randint(0, 250) * 20  # Simular velocidad entre 0 RPM y 5000 RPM
    return velocidad

# Ciclo principal del servidor
while True:
    velocidad = simulate_sensor_rpm()
    # Formato de los datos a enviar
    data = f"B {velocidad} 0D 0A"

    # Envía los datos al cliente
    sock.sendto(data.encode(), (UDP_IP, UDP_PORT))
    print(f"Datos enviados: {data}")

    # Espera aproximadamente un segundo antes de enviar la próxima actualización
    time.sleep(1)
