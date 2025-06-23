# etape1_kafka_connection.py
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Step1_ReadKafka") \
    .config("spark.jars", "/opt/bitnami/spark/jars/postgresql-42.6.0.jar") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "pret_etudiant") \
    .option("startingOffsets", "earliest") \
    .load()

df_text = df_raw.selectExpr("CAST(value AS STRING) AS json_value")

# Pour valider : affichage des messages Kafka en brut
query = df_text.writeStream \
    .format("console") \
    .outputMode("append") \
    .start()

query.awaitTermination()
