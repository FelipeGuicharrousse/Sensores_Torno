import socket
import time
import random

# Configuración del servidor UDP
UDP_IP = "127.0.0.1"  # Dirección IP local
UDP_PORT = 6000      # Puerto para la comunicación UDP

# Crear un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Función para simular datos del sensor
def simulate_sensor_rpm():
    # Simular algún tipo de lectura del sensor
    velocidad = random.randint(0, 250) * 20  # Simular velocidad entre 0 RPM y 5000 RPM
    return velocidad

# Función para simular datos del sensor de desplazamiento
def simulate_sensor_desplazamiento():
    # Simular algún tipo de lectura del sensor
    temperatura = round(random.uniform(0, 99), 1)  # Simular temperatura entre 20°C y 30°C con 1 decimal
    vibracion_x = random.randint(-999, 999)        # Simular vibración en el eje X entre -999 y 999
    vibracion_y = random.randint(-999, 999)        # Simular vibración en el eje Y entre -999 y 999
    vibracion_z = random.randint(-999, 999)        # Simular vibración en el eje Z entre -999 y 999
    return temperatura, vibracion_x, vibracion_y, vibracion_z

# Ciclo principal del servidor
while True:
    # Determinar aleatoriamente qué tipo de datos enviar
    if random.random() < 0.5:  
        velocidad = simulate_sensor_rpm()
        data = f"B {velocidad}"
        print(f"Datos de velocidad en RPM enviados: {data}")
    else:
        temperatura, vibracion_x, vibracion_y, vibracion_z = simulate_sensor_desplazamiento()
        data = f"A {temperatura:.1f} {'+' if vibracion_x >= 0 else '-'}{abs(vibracion_x):03d} {'+' if vibracion_y >= 0 else '-'}{abs(vibracion_y):03d} {'+' if vibracion_z >= 0 else '-'}{abs(vibracion_z):03d}"
        print(f"Datos de desplazamiento enviados: {data}")

    # Envía los datos al cliente
    sock.sendto(data.encode(), (UDP_IP, UDP_PORT))

    # Espera aproximadamente un segundo antes de enviar la próxima actualización
    time.sleep(1)
