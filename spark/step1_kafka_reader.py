import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StringType, IntegerType, LongType

# 🔧 Variables d'environnement Spark/HDFS
os.environ["HADOOP_USER_NAME"] = "spark"
os.environ["USER"] = "spark"

# 📁 Version actuelle à changer si besoin
VERSION = "v1"

# 🧩 Schéma du JSON reçu depuis Kafka
schema = StructType() \
    .add("nan_ope_id", LongType()) \
    .add("nan_school", StringType()) \
    .add("nan_state", StringType()) \
    .add("nan_zip_code", StringType()) \
    .add("nan_school_type", StringType()) \
    .add("subsidized_recipients", IntegerType()) \
    .add("subsidized_loans_originated_count", IntegerType()) \
    .add("subsidized_loans_originated_amount", LongType()) \
    .add("subsidized_disbursements_count", IntegerType()) \
    .add("subsidized_disbursements_amount", LongType()) \
    .add("unsubsidized_recipients", IntegerType()) \
    .add("unsubsidized_loans_originated_count", IntegerType()) \
    .add("unsubsidized_loans_originated_amount", LongType()) \
    .add("unsubsidized_disbursements_count", IntegerType()) \
    .add("unsubsidized_disbursements_amount", LongType()) \
    .add("parent_plus_recipients", IntegerType()) \
    .add("parent_plus_loans_originated_count", IntegerType()) \
    .add("parent_plus_loans_originated_amount", LongType()) \
    .add("parent_plus_disbursements_count", IntegerType()) \
    .add("parent_plus_disbursements_amount", LongType()) \
    .add("grad_plus_recipients", IntegerType()) \
    .add("grad_plus_loans_originated_count", IntegerType()) \
    .add("grad_plus_loans_originated_amount", LongType()) \
    .add("grad_plus_disbursements_count", IntegerType()) \
    .add("grad_plus_disbursements_amount", LongType()) \
    .add("processed_timestamp", StringType()) \
    .add("source_files_count", IntegerType())

# 🚀 Initialisation de Spark
spark = SparkSession.builder \
    .appName("Step1_ReadKafka") \
    .config("spark.jars", "/opt/bitnami/spark/jars/postgresql-42.6.0.jar") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.hadoop.security.authentication", "simple") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 🔌 Lecture du stream Kafka
df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "pret_etudiant") \
    .option("startingOffsets", "earliest") \
    .load()

# 🧼 Extraction JSON et parsing avec schéma
df_json = df_kafka.selectExpr("CAST(value AS STRING) AS json_str")
df_parsed = df_json.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

# ⏱ Enrichir avec timestamp d'ingestion
df_final = df_parsed.withColumn("ingestion_timestamp", current_timestamp())

# 📤 Sortie HDFS versionnée
checkpoint_path = f"hdfs://namenode:9000/user/spark/checkpoints/step1/{VERSION}"
output_path = f"hdfs://namenode:9000/user/spark/output/{VERSION}"

query = df_final.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("checkpointLocation", checkpoint_path) \
    .start(output_path)

query.awaitTermination()
