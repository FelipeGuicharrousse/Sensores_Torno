import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Conexión a la base de datos MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["sensors_db"]

async def fetch_all_data(collection_name):
    collection = db[collection_name]
    cursor = collection.find({})
    data = []
    async for document in cursor:
        data.append(document)
    return data

async def generate_excel():
    file_name = "sensor_data.xlsx"
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        # Fetch humidity and temperature data once
        hum_temp_data = await fetch_all_data("hum_temp_data")
        df_hum_temp = pd.DataFrame(hum_temp_data).drop(columns=["_id", "sensor_name"])

        for sensor_info in SENSOR_INFO:
            sensor_name = sensor_info["name"]
            collection_name = sensor_info["collection"]

            # Fetch all data for the specific sensor collection
            sensor_data = await fetch_all_data(collection_name)

            if not sensor_data:
                print(f"No data found for {sensor_name}")
                continue

            # Convert the sensor data to a DataFrame and exclude '_id' and 'sensor_name' columns
            df_sensor = pd.DataFrame(sensor_data).drop(columns=["_id", "sensor_name"])

            # Combine sensor data with humidity and temperature data
            combined_df = pd.concat([df_sensor, df_hum_temp], axis=1)

            # Write the DataFrame to an Excel sheet
            combined_df.to_excel(writer, sheet_name=sensor_name, index=False)
            print(f"Data for sensor {sensor_name} written to the '{sensor_name}' sheet in the Excel file.")

    print(f"Excel file '{file_name}' generated successfully.")

if __name__ == "__main__":
    # Configurar la información de los sensores
    SENSOR_INFO = [
        {"port": 5000, "name": "Torno 6", "collection": "torno_6_data"},
        {"port": 6000, "name": "Torno 8", "collection": "torno_8_data"}
    ]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_excel())
