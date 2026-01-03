# Usamos una imagen ligera de Python
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Copiamos los archivos necesarios
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto que usa Cloud Run
ENV PORT 8080

# Comando para arrancar la app usando Gunicorn para mayor estabilidad
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
