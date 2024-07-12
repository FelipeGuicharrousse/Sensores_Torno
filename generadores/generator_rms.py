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

def extract_numeric_value(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def calculate_rms(series):
    if isinstance(series, pd.Series):
        numeric_values = pd.to_numeric(series, errors='coerce')  # Convertir a numérico, NaN para no numéricos
        numeric_values = numeric_values.dropna()  # Eliminar NaNs y valores no numéricos

        if numeric_values.empty:
            return 0.0  # Devolver un valor por defecto o manejar de otra manera según tu caso
        else:
            return (numeric_values ** 2).mean() ** 0.5
    elif isinstance(series, (int, float)):
        return float(series)  # Tratar como número si es un solo valor numérico
    else:
        return 0.0  # Manejar otros casos como 0.0 o cualquier valor predeterminado

async def generate_excel_rms():
    file_name = "sensor_data_rms.xlsx"

    hum_temp_data = await fetch_all_data("hum_temp_data")
    hum_temp_data['timestamp'] = pd.to_datetime(hum_temp_data['timestamp'], errors='coerce')

    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for sensor_info in SENSOR_INFO:
            sensor_name = sensor_info["name"]
            collection_name = sensor_info["collection"]

            df_sensor = await fetch_all_data(collection_name)
            df_sensor['timestamp'] = pd.to_datetime(df_sensor['timestamp'], errors='coerce')

            if df_sensor.empty:
                print(f"No data found for {sensor_name}")
                continue

            # Asegurarse de que las columnas 'timestamp' sean adecuadas para concatenar
            combined_df = pd.merge_asof(df_sensor.sort_values('timestamp'), 
                                        hum_temp_data.sort_values('timestamp'), 
                                        on='timestamp', 
                                        direction='nearest')

            combined_df.set_index('timestamp', inplace=True)

            # Verificar si las columnas 'eje_x', 'eje_y', 'eje_z' existen en combined_df
            if 'eje_x' not in combined_df.columns or 'eje_y' not in combined_df.columns or 'eje_z' not in combined_df.columns:
                print(f"Data for sensor {sensor_name} does not contain expected columns 'eje_x', 'eje_y', 'eje_z'. Skipping...")
                continue
            
            numeric_columns = ['temperatura', 'eje_x', 'eje_y', 'eje_z', 'velocidad', 'humedad', 'temperatura_ambiental']
            combined_df[numeric_columns] = combined_df[numeric_columns].apply(pd.to_numeric, errors='coerce')

            # Agrupar por hora y calcular la media
            grouped_df = combined_df.groupby(pd.Grouper(freq='H')).mean()

            # Reindexar para asegurarse de que todas las horas estén presentes
            all_hours = pd.date_range(grouped_df.index.min(), grouped_df.index.max(), freq='H')
            hourly_df = grouped_df.reindex(all_hours)

            # Eliminar filas que tienen todos los valores NaN
            hourly_df.dropna(how='all', inplace=True)

            if hourly_df.empty:
                print(f"No data found for {sensor_name} in the specified time range. Skipping...")
                continue

            # Llenar NaN con 0 o cualquier valor adecuado según tu caso
            hourly_df.fillna(0, inplace=True)  # Puedes cambiar 0 por otro valor adecuado

            # Calcular RMS para cada eje si existen las columnas
            if 'eje_x' in hourly_df.columns:
                hourly_df['rms_x'] = hourly_df['eje_x'].apply(calculate_rms)
            if 'eje_y' in hourly_df.columns:
                hourly_df['rms_y'] = hourly_df['eje_y'].apply(calculate_rms)
            if 'eje_z' in hourly_df.columns:
                hourly_df['rms_z'] = hourly_df['eje_z'].apply(calculate_rms)

            hourly_df.to_excel(writer, sheet_name=sensor_name, index=True)
            print(f"Data for sensor {sensor_name} written to the '{sensor_name}' sheet in the Excel file.")

    print(f"Excel file '{file_name}' generated successfully.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_excel_rms())

    # Cerrar el cliente después de completar la operación
    client.close()
