import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Conexión a la base de datos MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["sensors_db"]

SENSOR_INFO = [
    {"port": 5000, "name": "Torno 6", "collection": "torno_6_data"},
    {"port": 6000, "name": "Torno 8", "collection": "torno_8_data"}
]

async def fetch_all_data(collection_name):
    collection = db[collection_name]
    cursor = collection.find({})
    data = []
    async for document in cursor:
        data.append(document)
    return pd.DataFrame(data).drop(columns=["_id", "sensor_name"])

async def generate_excel():
    file_name = "sensor_data.xlsx"

    hum_temp_data = await fetch_all_data("hum_temp_data")

    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for sensor_info in SENSOR_INFO:
            sensor_name = sensor_info["name"]
            collection_name = sensor_info["collection"]

            df_sensor = await fetch_all_data(collection_name)

            if df_sensor.empty:
                print(f"No data found for {sensor_name}")
                continue

            combined_df = pd.concat([df_sensor, hum_temp_data], axis=1)

            combined_df.to_excel(writer, sheet_name=sensor_name, index=False)
            print(f"Data for sensor {sensor_name} written to the '{sensor_name}' sheet in the Excel file.")

    print(f"Excel file '{file_name}' generated successfully.")

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_excel())

    # Cerrar el cliente después de completar la operación
    client.close()
