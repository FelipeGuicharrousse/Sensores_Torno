import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def drop_database():
    # Conexión a la base de datos MongoDB
    MONGO_URI = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(MONGO_URI)

    # Selecciona la base de datos que quieres eliminar
    database_name = "sensors_db"
    db = client[database_name]

    # Borra toda la base de datos
    await client.drop_database(database_name)
    print(f"La base de datos '{database_name}' ha sido eliminada exitosamente.")

    # Cierra la conexión
    client.close()

# Ejecuta la función asíncrona
asyncio.run(drop_database())
