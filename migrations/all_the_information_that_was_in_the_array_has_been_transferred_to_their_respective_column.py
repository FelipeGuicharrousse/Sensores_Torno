import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Conexión a la base de datos MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["sensors_db"]

async def transform_document(doc):
    timestamp = doc["timestamp"]
    sensor_name = doc["sensor_name"]
    data_values = doc["data"]

    # Nuevo documento con el formato actualizado
    if len(data_values) == 4:
        new_doc = {
            "timestamp": timestamp,
            "sensor_name": sensor_name,
            "temperatura": data_values[0],
            "eje_x": data_values[1],
            "eje_y": data_values[2],
            "eje_z": data_values[3],
        }
    elif len(data_values) == 2:
        new_doc = {
            "timestamp": timestamp,
            "sensor_name": sensor_name,
            "humedad": data_values[0],
            "temperatura_ambiental": data_values[1],
        }
    else:
        new_doc = {
            "timestamp": timestamp,
            "sensor_name": sensor_name,
            "velocidad": data_values[0]
        }

    return new_doc

async def migrate_data():
    collections = ["torno_6_data", "hum_temp_data", "torno_8_data"]
    for collection_name in collections:
        collection = db[collection_name]
        async for doc in collection.find({"data": {"$exists": True}}):
            new_doc = await transform_document(doc)
            await collection.update_one({"_id": doc["_id"]}, {"$set": new_doc, "$unset": {"data": ""}})
    print("Migración completada.")

if __name__ == "__main__":
    asyncio.run(migrate_data())
