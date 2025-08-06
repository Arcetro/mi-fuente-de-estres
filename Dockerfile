# Utilizar una imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de requirements primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copiar el resto de los archivos del proyecto
COPY . .

# Crear directorio para tests si no existe
RUN mkdir -p tests

# Exponer puerto para futuras APIs web
EXPOSE 8000

# Comando por defecto para ejecutar el prototipo
CMD ["python", "recepcionista_swarm.py"]