#!/bin/bash

set -e
LOGFILE="pipeline.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "📁 Logs enregistrés dans $LOGFILE"
echo "==================== $(date) ===================="

echo "🚀 Étape 1 : Démarrage de Kafka et HDFS (namenode + datanode)"
docker compose up -d zookeeper kafka namenode datanode

echo "⏳ Attente de HDFS (5 secondes)..."
sleep 5

echo "🧹 Étape 2 : Nettoyage et envoi du fichier fusionné vers HDFS"
docker compose build cleaner
docker compose run --rm cleaner
sleep 15

echo "📤 Étape 3 : Envoi des données vers Kafka via Spark Producer"
docker compose run --rm spark-producer

sleep 15

echo "🧰 Étape 4 : Démarrage de PostgreSQL et Spark Consumer"
docker compose up -d postgres spark-consumer

echo "✅ Pipeline exécuté avec succès !"

echo "🧾 Étape 5 : Vérification de la base et des tables dans PostgreSQL"
docker compose exec postgres psql -U admin -d pret_etudiant_db -c "\dt"
docker compose exec postgres psql -U admin -d pret_etudiant_db -c "SELECT COUNT(*) FROM pret_etudiant;"

# Option nettoyage
read -p "🧹 Voulez-vous nettoyer les conteneurs et volumes ? (y/n) : " confirm
if [ "$confirm" = "y" ]; then
    docker compose down -v
    docker image prune -f
    echo "✅ Nettoyage terminé."
else
    echo "ℹ️ Nettoyage ignoré."
fi
