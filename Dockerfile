# Dockerfile pour Kafka Producer
FROM python:3.9-slim

# Installer les dépendances nécessaires
RUN pip install kafka-python

# Copier le fichier de dépendances
COPY app/requirements.txt /app/requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copier le script de Kafka Producer
COPY app/kafka_producer.py /app/kafka_producer.py

# Point d'entrée du conteneur
CMD ["python", "/app/kafka_producer.py"]
