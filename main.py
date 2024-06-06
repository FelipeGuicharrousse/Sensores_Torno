import socket
import asyncio
import re
from datetime import datetime, time
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# Configurar la información de los sensores
SENSOR_INFO = [
    {"port": 5000, "name": "Torno 6", "collection": "torno_6_data"},
    {"port": 5500, "name": "Hum_temp", "pattern": r"A(\d+\.\d+) (\d+\.\d+)", "collection": "hum_temp_data"},
    {"port": 6000, "name": "Torno 8", "collection": "torno_8_data"}
]

pattern_a = r"A ([+\-]?\d+\.\d+) ([+\-]?\d+) ([+\-]?\d+) ([+\-]?\d+)"
pattern_b = r"B (\d+)"

BUFFER_SIZE = 1024  # Tamaño del búfer de recepción

# Conexión a la base de datos MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["sensors_db"]

# Define las horas de inicio y fin para la aceptación de datos (9am y 5pm)
start_time = time(9, 0)  # 9am
end_time = time(17, 0)   # 5pm

# Función para recibir los datos de un sensor y guardarlos en la base de datos
async def receive_sensor_data(sensor_info):
    sensor_name = sensor_info["name"]
    sensor_port = sensor_info["port"]
    collection_name = sensor_info["collection"]
    print(f"Escuchando datos del {sensor_name} en el puerto {sensor_port} y guardándolos en la colección {collection_name}...")
    collection = db[collection_name]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("192.168.0.150", sensor_port))
    while True:
        data, _ = await loop.run_in_executor(None, sock.recvfrom, BUFFER_SIZE)
        decoded_data = data.decode("utf-8")
        if sensor_port == 5500:
            match = re.match(sensor_info["pattern"], decoded_data)
        elif sensor_port == 5000 or sensor_port == sensor_port == 6000:
            if decoded_data.startswith("A"):
                match = re.match(pattern_a, decoded_data)
            elif decoded_data.startswith("B"):
                match = re.match(pattern_b, decoded_data)
            else:
                print("Error en el formato de entrega")
        else:
            print("Error en el puerto recibido, el mensaje del puerto " + sensor_port + " es inesperado")

        current_time = datetime.now().time()

        if start_time <= current_time <= end_time:
            if match:
                data_values = match.groups()
                # Obtener la fecha y hora actual
                timestamp = datetime.now()
                # Guardar los datos junto con la fecha y hora en la base de datos
                if len(data_values) == 4:
                    await collection.insert_one({"timestamp": timestamp, "sensor_name": sensor_name, "temperatura": data_values[0], "eje_x": data_values[1], "eje_y": data_values[2], "eje_z": data_values[3],})
                elif len(data_values) == 2:
                    await collection.insert_one({"timestamp": timestamp, "sensor_name": sensor_name, "humedad": data_values[0], "temperatura_ambiental": data_values[1],})
                else:
                    await collection.insert_one({"timestamp": timestamp, "sensor_name": sensor_name, "velocidad": data_values[0]})
                print("Datos guardados con éxito.")
            else:
                print(f"No se pudieron extraer datos del {sensor_name}:", decoded_data)
        else:
            print("No se están guardando datos fuera del rango de tiempo permitido (9 am - 5 pm). Hora actual: " + str(current_time))

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
