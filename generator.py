import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta


# Conexión a la base de datos MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["sensors_db"]

# Definir el orden de las columnas para cada sensor
SENSOR_COLUMNS = {
    "Sensor 1": ["Temperatura (°C)", "Eje X", "Eje Y", "Eje Z"],
    "Sensor 2": ["Humedad (%)", "Temperatura (°C)"],
    "Sensor 3": ["Velocidad (RPM)"]
}


fecha_inicial = datetime(2024, 5, 1) 
fecha_final = datetime.now()  

async def generate_excel_for_date():
    
    # Crear un archivo Excel con el nombre basado en la fecha seleccionada
    file_name = f"sensor_data.xlsx"
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for sensor_info in SENSOR_INFO:
            sensor_name = sensor_info["name"]
            collection_name = sensor_info["collection"]
            collection = db[collection_name]
            
            fecha_actual = fecha_inicial    
            df_final = pd.DataFrame()
            while fecha_actual <= fecha_final:
                # Consultar los datos del sensor solo para la fecha seleccionada
                sensor_data = []
                cursor = collection.find({"timestamp": {"$gte": datetime.combine(fecha_actual, datetime.min.time()), "$lt": datetime.combine(fecha_actual + pd.Timedelta(days=1), datetime.min.time())}})
                async for document in cursor:
                    sensor_data.append(document)
                
                if not sensor_data:
                    print(f"No hay datos disponibles para el sensor {sensor_name} en la fecha seleccionada.")
                    continue
                
                # Crear un DataFrame de Pandas con los datos del sensor
                df = pd.DataFrame(sensor_data)
                
                # Crear columnas para cada sensor según el orden definido
                if sensor_name in SENSOR_COLUMNS:
                    columns_order = SENSOR_COLUMNS[sensor_name]
                    timestamp_column = df['timestamp']
                    df = pd.DataFrame(df["data"].tolist(), columns=columns_order)
                    
                    # Convertir los valores a números si es posible
                    for column in df.columns:
                        df[column] = pd.to_numeric(df[column])
                    df.insert(0, 'Timestamp', timestamp_column)
                    
                    # Calcular el promedio, máximo y mínimo para cada columna numérica
                    stats = {}
                    for column in df.columns:
                        if pd.api.types.is_numeric_dtype(df[column]):
                            stats[column] = {
                                'Promedio': df[column].mean(),
                                'Máximo': df[column].max(),
                                'Mínimo': df[column].min()
                            }
                    
                    # Crear un DataFrame para las filas 'Promedio', 'Máximo' y 'Mínimo'
                    stats_df = pd.DataFrame(stats)
                    stats_df.index = ['Promedio', 'Máximo', 'Mínimo']
                    stats_df = stats_df.reset_index()
                    stats_df = stats_df.rename(columns={'index': 'Timestamp'})
                    
                    # Agregar las filas al final del DataFrame del sensor
                    df_final = pd.concat([df_final, stats_df], ignore_index=True)

                 
                else:
                    print(f"No se encontró el orden de columnas para el sensor {sensor_name}.")
                    continue

                fecha_actual += timedelta(days=1) 
                
            # Escribir los datos en una hoja de Excel con el nombre del sensor
            df_final.to_excel(writer, sheet_name=sensor_name, index=False)
            
            print(f"Datos del sensor {sensor_name} guardados en la hoja '{sensor_name}' del archivo Excel.")
    
    print(f"Archivo Excel '{file_name}' generado exitosamente.")

if __name__ == "__main__":
    import asyncio

    # Configurar la información de los sensores
    SENSOR_INFO = [
        {"port": 5000, "name": "Torno 6", "collection": "torno_6_data"},
        {"port": 5500, "name": "Hum_Temp", "collection": "hum_temp_data"},
        {"port": 6000, "name": "Torno 8", "collection": "torno_8_data"}
    ]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_excel_for_date())
