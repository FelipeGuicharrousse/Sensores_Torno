import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta


# Conexión a la base de datos MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["sensors_db"]

fecha_inicial = datetime(2024, 5, 1) 
fecha_final = datetime.now()  

async def generate_excel_for_date():

    file_name = f"sensor_data.xlsx"
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for sensor_info in SENSOR_INFO:
            sensor_name = sensor_info["name"]
            collection_name = sensor_info["collection"]
            collection = db[collection_name]
            collection_hum_temp = db["hum_temp_data"]

            fecha_actual = fecha_inicial    
            df_final = pd.DataFrame()
            while fecha_actual <= fecha_final:
                # Consultar los datos del sensor solo para la fecha seleccionada
                sensor_data = []
                cursor = collection.find({"timestamp": {"$gte": datetime.combine(fecha_actual, datetime.min.time()), "$lt": datetime.combine(fecha_actual + pd.Timedelta(days=1), datetime.min.time())}})
                async for document in cursor:
                    sensor_data.append(document)
                
                if not sensor_data:
                    fecha_actual += timedelta(days=1) 
                    continue
                
                #Obtencion de datos de humedad y temperatura
                hum_temp_data = []
                hum_temp = collection_hum_temp.find({"timestamp": {"$gte": datetime.combine(fecha_actual, datetime.min.time()), "$lt": datetime.combine(fecha_actual + pd.Timedelta(days=1), datetime.min.time())}})
                async for document in hum_temp:
                    hum_temp_data.append(document)
                
                # Crear un DataFrame de Pandas con los datos del sensor
                df = pd.DataFrame(sensor_data)
                df_hum_temp = pd.DataFrame(hum_temp_data)
                new_df = pd.DataFrame()

                # Procesar cada dato individualmente
                for index, row in df.iterrows():
                    data_length = len(row["data"])
                    if data_length == 1:
                        try:
                            dato = float(row["data"][0])
                        except ValueError:
                            print(f"No se pudo convertir el dato {row['data'][0]} a número.")
                            continue
                        new_df = pd.DataFrame([[dato]], columns=["Velocidad (RPM)"])
                        pass
                    elif data_length == 4:
                        try:
                            datos = [float(value) for value in row["data"]]
                        except ValueError as e:
                            print(f"No se pudo convertir los datos {row['data']} a números: {e}.")
                            continue
                        new_df = pd.DataFrame([datos], columns=["Temperatura (°C)", "Eje X", "Eje Y", "Eje Z"])
                        pass
                    else:
                        print(f"Longitud de datos no compatible para el sensor {sensor_name}")
                    df = pd.concat([df, new_df], ignore_index=False)
                # df ya esta con todos sus datos

                # Crear columnas para cada sensor según el orden definido

                columns_hum_temp = ["Humedad (%)", "Temperatura (°C)"]
                df_hum_temp = pd.DataFrame(df_hum_temp["data"].tolist(), columns=columns_hum_temp)

                for column in df_hum_temp.columns:
                    df_hum_temp[column] = pd.to_numeric(df_hum_temp[column])
                
                # Calcular el promedio, máximo y mínimo para cada columna numérica
                stats = {}
                for column in df.columns:
                    if pd.api.types.is_numeric_dtype(df[column]):
                        stats[column] = {
                            'Promedio': df[column].mean(),
                            'Máximo': df[column].max(),
                            'Mínimo': df[column].min()
                        }
                
                # Calcular ahora lo mismo pero del sensor de humedad y temperatura
                stats_hum_temp = {}
                for column in df_hum_temp.columns:
                    if pd.api.types.is_numeric_dtype(df_hum_temp[column]):
                        stats_hum_temp[column] = {
                            'Promedio': df_hum_temp[column].mean(),
                            'Máximo': df_hum_temp[column].max(),
                            'Mínimo': df_hum_temp[column].min()
                        }

                # Crear un DataFrame para las filas 'Promedio', 'Máximo' y 'Mínimo'
                stats_df = pd.DataFrame(stats)
                stats_df.index = ['Promedio', 'Máximo', 'Mínimo']
                stats_df = stats_df.reset_index()
                stats_df = stats_df.rename(columns={'index': fecha_final.strftime("%d-%m-%Y")})
                
                stats_hum_temp_df = pd.DataFrame(stats_hum_temp)
                stats_df.index = ['Promedio', 'Máximo', 'Mínimo']

                stats_df = pd.concat([stats_df, stats_hum_temp_df], axis=1)
                # Agregar las filas al final del DataFrame del sensor
                df_final = pd.concat([df_final, stats_df], ignore_index=True)

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
        {"port": 6000, "name": "Torno 8", "collection": "torno_8_data"}
    ]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_excel_for_date())
