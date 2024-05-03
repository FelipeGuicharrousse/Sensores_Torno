import socket
import asyncio
import re
from datetime import datetime
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# Configurar la información de los sensores
SENSOR_INFO = [
    {"port": 5000, "name": "Sensor 1", "pattern": r"A ([+\-]?\d+\.\d+) ([+\-]?\d+) ([+\-]?\d+) ([+\-]?\d+) 0D 0A", "collection": "sensor_1_data"},
    {"port": 5500, "name": "Sensor 2", "pattern": r"A (\d+\.\d+) (\d+\.\d+) 0D 0A", "collection": "sensor_2_data"},
    {"port": 6000, "name": "Sensor 3", "pattern": r"B (\d+) 0D 0A", "collection": "sensor_3_data"}
]

BUFFER_SIZE = 1024  # Tamaño del búfer de recepción

# Conexión a la base de datos MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["sensors_db"]

# Función para recibir los datos de un sensor y guardarlos en la base de datos
async def receive_sensor_data(sensor_info):
    sensor_name = sensor_info["name"]
    sensor_port = sensor_info["port"]
    pattern = sensor_info["pattern"]
    collection_name = sensor_info["collection"]
    print(f"Escuchando datos del {sensor_name} en el puerto {sensor_port} y guardándolos en la colección {collection_name}...")
    collection = db[collection_name]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", sensor_port))
    while True:
        data, _ = await loop.run_in_executor(None, sock.recvfrom, BUFFER_SIZE)
        decoded_data = data.decode("utf-8")
        match = re.match(pattern, decoded_data)
        if match:
            data_values = match.groups()
            # Obtener la fecha y hora actual
            timestamp = datetime.now()
            # Guardar los datos junto con la fecha y hora en la base de datos
            await collection.insert_one({"timestamp": timestamp, "sensor_name": sensor_name, "data": data_values})
            print("Datos guardados con éxito.")
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
