# Usa una imagen base oficial de Ubuntu
FROM ubuntu:20.04

# Define el timezone para evitar interacciones durante la instalación de paquetes
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Actualiza el índice de paquetes y instala Python y pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY ServidorYOLO.py /app/
COPY requirements.txt /app/
COPY yolov8x.pt /app/

# Instala las dependencias de Python listadas en el archivo requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8000
EXPOSE 8000

# Comando para iniciar el servidor cuando el contenedor esté corriendo
CMD ["python3", "ServidorYOLO.py"]
