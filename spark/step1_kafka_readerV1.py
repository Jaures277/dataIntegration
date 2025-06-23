# etape1_kafka_connection.py
import os
from pyspark.sql import SparkSession

# 🔧 Pour éviter l'erreur UnixPrincipal / Kerberos
os.environ["HADOOP_USER_NAME"] = "spark"
os.environ["USER"] = "spark"

# 🔧 Construction de la session Spark
spark = SparkSession.builder \
    .appName("Step1_ReadKafka") \
    .config("spark.jars", "/opt/bitnami/spark/jars/postgresql-42.6.0.jar") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.hadoop.security.authentication", "simple") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 🔌 Lecture du topic Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "pret_etudiant") \
    .option("startingOffsets", "earliest") \
    .load()

# 📦 Extraction du message texte
df_text = df_raw.selectExpr("CAST(value AS STRING) AS json_value")

# 📝 Écriture dans HDFS au format Parquet
query = df_text.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("checkpointLocation", "hdfs://namenode:9000/user/spark/checkpoints/step1") \
    .start("hdfs://namenode:9000/user/spark/output")

query.awaitTermination()
