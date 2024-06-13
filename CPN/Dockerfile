# Usar una imagen base de Debian
FROM debian:buster

# Instalar Java 11, que es necesario para tu servidor Spring Boot
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean;

# Agregar la arquitectura i386 para los paquetes que lo requieran
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y libc6:i386 libncurses6:i386 libstdc++6:i386

# Limpiar la cache de apt para reducir el tamaño de la imagen
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Agregar tu archivo JAR al contenedor
ADD cpnsim.jar /app/cpnsim.jar

# Exponer el puerto que tu aplicación utiliza
EXPOSE 8080

# Comando para ejecutar tu aplicación
CMD ["java", "-jar", "/app/cpnsim.jar"]

