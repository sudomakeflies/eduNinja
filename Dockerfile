# Usa una imagen base más ligera de Python
FROM python:3.12-slim

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y postgresql-client

# Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias de Python
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Copia todo el contenido del directorio actual al directorio /app en el contenedor
COPY . .

# Da permisos de ejecución al script de inicio
RUN chmod +x /app/start_app.sh

# Copy the entry point script into the container
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entry point script to be executed
ENTRYPOINT ["/entrypoint.sh"]

# Expone el puerto 8000 para que pueda ser accedido desde el exterior
EXPOSE 8000

# Comando para ejecutar el script de inicio
#CMD ["./start_app.sh"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
