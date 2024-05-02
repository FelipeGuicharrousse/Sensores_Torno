import socket
import asyncio
import re
from fastapi import FastAPI

app = FastAPI()

# Configurar la información de los sensores
SENSOR_INFO = [
    {"port": 5000, "name": "Sensor 1", "pattern": r"A ([+\-]?\d+\.\d+) ([+\-]?\d+) ([+\-]?\d+) ([+\-]?\d+) 0D 0A"},
    {"port": 5500, "name": "Sensor 2", "pattern": r"A (\d+\.\d+) (\d+\.\d+) 0D 0A"},
    {"port": 6000, "name": "Sensor 3", "pattern": r"B (\d+) 0D 0A"}
]

BUFFER_SIZE = 1024  # Tamaño del búfer de recepción

# Función para recibir los datos de un sensor
async def receive_sensor_data(sensor_info):
    sensor_name = sensor_info["name"]
    sensor_port = sensor_info["port"]
    pattern = sensor_info["pattern"]
    print(f"Escuchando datos del {sensor_name} en el puerto {sensor_port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", sensor_port))
    while True:
        data, _ = await loop.run_in_executor(None, sock.recvfrom, BUFFER_SIZE)
        decoded_data = data.decode("utf-8")
        match = re.match(pattern, decoded_data)
        if match:
            data_values = match.groups()
            print(f"Datos del {sensor_name} recibidos:", data_values)
        else:
            print(f"No se pudieron extraer datos del {sensor_name}:", decoded_data)

# Ruta para mostrar el estado de la API
@app.get("/sensor-data/")
async def get_sensor_data():
    return {"message": "La API está escuchando datos de los sensores"}

# Iniciar la recepción de datos de los sensores
async def start_sensor_listening():
    tasks = [receive_sensor_data(sensor_info) for sensor_info in SENSOR_INFO]
    await asyncio.gather(*tasks)

# Iniciar el bucle de eventos de asyncio y mantenerlo activo
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_sensor_listening())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
