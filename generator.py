import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

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

async def generate_excel_for_date(selected_date):
    # Formatear la fecha seleccionada para que coincida con el formato de la base de datos
    selected_date_str = selected_date.strftime('%Y-%m-%d')
    next_day = (selected_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Crear un archivo Excel con el nombre basado en la fecha seleccionada
    file_name = f"sensor_data_{selected_date_str}.xlsx"
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for sensor_info in SENSOR_INFO:
            sensor_name = sensor_info["name"]
            collection_name = sensor_info["collection"]
            collection = db[collection_name]
            
            # Consultar los datos del sensor solo para la fecha seleccionada
            sensor_data = []
            cursor = collection.find({"timestamp": {"$gte": datetime.combine(selected_date, datetime.min.time()), "$lt": datetime.combine(selected_date + pd.Timedelta(days=1), datetime.min.time())}})
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
                df.insert(0, 'TimeStamp', timestamp_column)
            else:
                print(f"No se encontró el orden de columnas para el sensor {sensor_name}.")
                continue
            
            # Escribir los datos en una hoja de Excel con el nombre del sensor
            df.to_excel(writer, sheet_name=sensor_name, index=False)
            
            print(f"Datos del sensor {sensor_name} guardados en la hoja '{sensor_name}' del archivo Excel.")
    
    print(f"Archivo Excel '{file_name}' generado exitosamente.")

if __name__ == "__main__":
    import asyncio

    # Configurar la información de los sensores
    SENSOR_INFO = [
        {"port": 5000, "name": "Sensor 1", "collection": "sensor_1_data"},
        {"port": 5500, "name": "Sensor 2", "collection": "sensor_2_data"},
        {"port": 6000, "name": "Sensor 3", "collection": "sensor_3_data"}
    ]

    # Solicitar al usuario la fecha deseada para generar el archivo Excel
    input_date = input("Ingrese la fecha en formato YYYY-MM-DD: ")
    selected_date = datetime.strptime(input_date, "%Y-%m-%d")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_excel_for_date(selected_date))
