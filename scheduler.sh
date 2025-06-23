#!/bin/bash

echo "[scheduler] Lancement de l'exécution périodique de run_metrics.sh toutes les 24h."

while true
do
  echo "[scheduler] $(date): Exécution de run_metrics.sh"
  /app/run_metrics.sh >> /app/cron_metrics.log 2>&1
  sleep 86400  # 24h
done
