#!/bin/bash

set -e

echo "🚀 Démarrage des conteneurs Docker..."
docker compose up -d --build

echo "🕒 Attente du démarrage complet des services..."
sleep 10

echo "✅ Création du topic Kafka 'pret_etudiant'..."
docker exec -it kafka kafka-topics.sh \
  --create \
  --if-not-exists \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic pret_etudiant

echo "📁 Création du dossier HDFS /data..."
docker exec -it namenode hdfs dfs -mkdir -p /data || true

echo "📤 Transfert des fichiers Excel locaux vers le conteneur 'namenode'..."
docker cp ./data/. namenode:/tmp/data

echo "📦 Importation des fichiers dans HDFS..."
docker exec -it namenode bash -c "
  for f in /tmp/data/*; do
    echo \"➡️  Import \$f vers HDFS...\"
    hdfs dfs -put -f \$f /data/
  done
"

echo "🔍 Vérification des fichiers HDFS..."
docker exec -it namenode hdfs dfs -ls /data

echo "🐍 Lancement du producer Kafka (conteneur spark-producer)..."
docker compose up -d spark-producer

echo "📄 Logs du producer en cours d'exécution :"
docker logs -f spark-producer
