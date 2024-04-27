import socket
from fastapi import FastAPI

app = FastAPI()

# Configurar el servidor UDP
UDP_IP = "127.0.0.1"  # Dirección IP del servidor
UDP_PORT = 5005  # Puerto UDP que escuchará
BUFFER_SIZE = 1024  # Tamaño del búfer de recepción

# Crear el socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Ruta para mostrar los datos del sensor
@app.get("/sensor-data/")
async def get_sensor_data():
    return {"message": "La API está escuchando datos del sensor"}

# Función para recibir y mostrar los datos del sensor a través del socket UDP
def receive_sensor_data_udp():
    print("Escuchando datos del sensor...")
    while True:
        data, _ = sock.recvfrom(BUFFER_SIZE)  # Recibir datos del sensor
        # Decodificar los datos recibidos (si es necesario)
        decoded_data = data.decode("utf-8")
        print("Datos del sensor recibidos:", decoded_data)

# Iniciar la recepción de datos del sensor en un hilo separado
import threading
threading.Thread(target=receive_sensor_data_udp).start()