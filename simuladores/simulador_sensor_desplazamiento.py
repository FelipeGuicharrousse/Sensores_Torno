import socket
import time
import random

# Configuración del servidor UDP
UDP_IP = "127.0.0.1"  # Dirección IP local
UDP_PORT = 5000    # Puerto para la comunicación UDP

# Crear un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Función para simular datos del sensor
def simulate_sensor_desplazamiento():
    # Simular algún tipo de lectura del sensor
    temperatura = round(random.uniform(0, 99), 1)  # Simular temperatura entre 20°C y 30°C con 1 decimal
    vibracion_x = random.randint(-999, 999)        # Simular vibración en el eje X entre -999 y 999
    vibracion_y = random.randint(-999, 999)        # Simular vibración en el eje Y entre -999 y 999
    vibracion_z = random.randint(-999, 999)        # Simular vibración en el eje Z entre -999 y 999
    return temperatura, vibracion_x, vibracion_y, vibracion_z
# Ciclo principal del servidor
while True:
    temperatura, vibracion_x, vibracion_y, vibracion_z = simulate_sensor_desplazamiento()
    # Formato de los datos a enviar
    data = f"A {temperatura:.1f} {'+' if vibracion_x >= 0 else '-'}{abs(vibracion_x):03d} {'+' if vibracion_y >= 0 else '-'}{abs(vibracion_y):03d} {'+' if vibracion_z >= 0 else '-'}{abs(vibracion_z):03d}"
    
    # Envía los datos al cliente
    sock.sendto(data.encode(), (UDP_IP, UDP_PORT))
    print(f"Datos enviados: {data}")

    # Espera aproximadamente un segundo antes de enviar la próxima actualización
    time.sleep(1)
