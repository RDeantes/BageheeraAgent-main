# Imagen base
FROM python:3.11-slim

# Evita problemas de buffer
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema (para docx2pdf)
RUN apt-get update && apt-get install -y \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Comando para correr el bot
CMD ["python", "BagheeraTelegram.py"]
