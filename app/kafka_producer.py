from kafka import KafkaProducer
import time
import json
import os
import pandas as pd

# Initialisation du Kafka Producer
connected = False
while not connected:
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Sérialisation JSON
        )
        connected = True
    except Exception as e:
        print(f"Retrying connection to Kafka: {e}")
        time.sleep(5)

print("Kafka connected!")

# Définition du topic
topic = 'student_loan_topic'

# Chemin vers le dossier contenant les fichiers
data_dir = '/datas'

# Vérifier si le dossier existe
if not os.path.exists(data_dir):
    print(f"Data directory {data_dir} does not exist. Exiting.")
    exit(1)

# Trouver un fichier Excel dans le dossier
file_name = next((f for f in os.listdir(data_dir) if f.endswith('.xls') or f.endswith('.xlsx')), None)
if not file_name:
    print(f"No Excel file found in {data_dir}. Exiting.")
    exit(1)

file_path = os.path.join(data_dir, file_name)
print(f"Processing Excel file: {file_name}")

# Lire le fichier Excel avec pandas
try:
    df = pd.read_excel(file_path)
    print(f"Total rows in {file_name}: {len(df)}")

    # Normaliser les noms des colonnes
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Convertir chaque ligne en dictionnaire et envoyer à Kafka
    for _, row in df.iterrows():
        message = row.to_dict()  # Utiliser toutes les colonnes présentes
        try:
            producer.send(topic, value=message)
            print(f"Message sent successfully: {message}")
        except Exception as e:
            print(f"Failed to send message: {message}, Error: {e}")
        time.sleep(2)  # Délai pour observer les messages dans Kafka

except Exception as e:
    print(f"Failed to process file {file_name}: {e}")

# Assurez-vous que tous les messages sont envoyés
producer.flush()
print("All messages sent!")
