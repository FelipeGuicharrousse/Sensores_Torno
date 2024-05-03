# Utiliza una imagen de Python como base
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Instala las dependencias necesarias
RUN pip install fastapi uvicorn motor

# Copia el código de la aplicación al directorio de trabajo
COPY main.py .

# Expone el puerto en el que se ejecuta la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
