#!/bin/bash
echo "[START] $(date) - Lancement Spark calculate_metrics.py" >> /app/cron_metrics.log
/opt/bitnami/spark/bin/spark-submit /app/calculate_metrics.py >> /app/cron_metrics.log 2>&1
echo "[END] $(date) - Fin d'exécution" >> /app/cron_metrics.log