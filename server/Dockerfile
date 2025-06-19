# server/Dockerfile
FROM python:3.9

WORKDIR /app

# Copiamos el archivo de requerimientos y lo instalamos.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto de la aplicación
COPY . .

# Exponemos el puerto en el que corre el chat (configúralo según tu código, aquí usamos 5000 como ejemplo)
EXPOSE 5000

# Comando para iniciar el servidor
CMD ["python", "server.py"]
