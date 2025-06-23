import time
import pandas as pd
from kafka import KafkaProducer
from hdfs import InsecureClient
import json
import io

# Configuration HDFS & Kafka
HDFS_URL = 'http://namenode:9870'
HDFS_PATH = '/data'
FICHIER_CSV = 'FL_Dashboard_merged.csv'
KAFKA_TOPIC = 'pret_etudiant'
KAFKA_BROKER = 'kafka:9092'

# Connexion HDFS
hdfs_client = InsecureClient(HDFS_URL, user='root')

# Connexion Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"\n📂 Lecture du fichier : {FICHIER_CSV}")

try:
    # Lire le fichier CSV depuis HDFS
    with hdfs_client.read(f"{HDFS_PATH}/{FICHIER_CSV}") as reader:
        df = pd.read_csv(io.BytesIO(reader.read()))

    if df.empty:
        print(f"⚠️ Le fichier {FICHIER_CSV} est vide ou mal formaté.")
    else:
        df.dropna(how='all', inplace=True)

        for i in range(0, len(df), 100):
            batch = df.iloc[i:i+100].to_dict(orient='records')
            producer.send(KAFKA_TOPIC, value=batch)
            print(f"✅ Batch {i//100 + 1} : {len(batch)} lignes envoyées à Kafka")
            time.sleep(5)

        print(f"📤 Fichier {FICHIER_CSV} entièrement envoyé.")

except Exception as e:
    print(f"❌ Erreur lors du traitement du fichier {FICHIER_CSV} : {e}")

producer.flush()
producer.close()
print("\n✅ Tous les fichiers ont été traités.")
