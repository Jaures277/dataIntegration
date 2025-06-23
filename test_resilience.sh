#!/bin/bash

echo "📦 Test de résilience - Kafka + Spark Streaming"

echo "⛔️ Étape 1 : Arrêt du conteneur Spark (simulateur de panne)"
docker compose stop spark-consumer
sleep 5

echo "🔁 Étape 2 : Envoi d’un nouveau batch dans Kafka (pendant panne)"
docker compose run --rm spark-producer python /app/producer.py

echo "⏳ Étape 3 : Attente que les messages s’accumulent dans Kafka"
sleep 10

echo "🚀 Étape 4 : Relancer le Spark consumer (reprise automatique du streaming)"
docker compose up -d spark-consumer
sleep 15

echo "🗂️ Étape 5 : Observation des fichiers HDFS (sortie Parquet)"
docker exec namenode hdfs dfs -ls -R /user/spark/output/v1

echo "📊 Étape 6 : Calcul des métriques"
docker compose run --rm spark-consumer bash -c "spark-submit /app/calculate_metrics.py"

echo "📁 Étape 7 : Observation des métriques HDFS"
docker exec namenode hdfs dfs -ls /user/spark/metrics

echo "✅ Test terminé. Résilience + Traitement + Métriques ✔️"
