from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, TimestampType
import os

# === Environnement utilisateur Hadoop/Spark ===
os.environ.setdefault("USER", "spark")
os.environ.setdefault("HADOOP_USER_NAME", "spark")

# === Schéma JSON aligné avec les noms de colonnes PostgreSQL ===
schema = StructType([
    StructField("nan_ope_id", LongType(), True),
    StructField("nan_school", StringType(), True),
    StructField("nan_state", StringType(), True),
    StructField("nan_zip_code", StringType(), True),
    StructField("nan_school_type", StringType(), True),
    StructField("subsidized_recipients", IntegerType(), True),
    StructField("subsidized_loans_originated_count", IntegerType(), True),
    StructField("subsidized_loans_originated_amount", LongType(), True),
    StructField("subsidized_disbursements_count", IntegerType(), True),
    StructField("subsidized_disbursements_amount", LongType(), True),
    StructField("unsubsidized_recipients", IntegerType(), True),
    StructField("unsubsidized_loans_originated_count", IntegerType(), True),
    StructField("unsubsidized_loans_originated_amount", LongType(), True),
    StructField("unsubsidized_disbursements_count", IntegerType(), True),
    StructField("unsubsidized_disbursements_amount", LongType(), True),
    StructField("parent_plus_recipients", IntegerType(), True),
    StructField("parent_plus_loans_originated_count", IntegerType(), True),
    StructField("parent_plus_loans_originated_amount", LongType(), True),
    StructField("parent_plus_disbursements_count", IntegerType(), True),
    StructField("parent_plus_disbursements_amount", LongType(), True),
    StructField("grad_plus_recipients", IntegerType(), True),
    StructField("grad_plus_loans_originated_count", IntegerType(), True),
    StructField("grad_plus_loans_originated_amount", LongType(), True),
    StructField("grad_plus_disbursements_count", IntegerType(), True),
    StructField("grad_plus_disbursements_amount", LongType(), True),
    StructField("processed_timestamp", TimestampType(), True),
    StructField("source_files_count", IntegerType(), True)
])

# === SparkSession ===
spark = SparkSession.builder \
    .appName("KafkaToPostgresStream") \
    .config("spark.jars", "/opt/bitnami/spark/jars/postgresql-42.6.0.jar") \
    .config("spark.sql.catalogImplementation", "in-memory") \
    .getOrCreate()

spark.sparkContext.setLogLevel("INFO")

# === Lecture du topic Kafka ===
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "pret_etudiant") \
    .option("startingOffsets", "earliest") \
    .load()

# === Parsing JSON et mapping vers schéma structuré ===
df_parsed = df_raw.selectExpr("CAST(value AS STRING) AS json_value") \
    .select(from_json(col("json_value"), schema).alias("data")) \
    .select("data.*")

# === Configuration JDBC PostgreSQL ===
jdbc_url = "jdbc:postgresql://postgres:5432/pret_etudiant_db"
jdbc_properties = {
    "user": "admin",
    "password": "adminpass",
    "driver": "org.postgresql.Driver"
}

# === Fonction d’écriture batch vers PostgreSQL ===
def write_to_postgres(batch_df, epoch_id):
    count = batch_df.count()
    if count > 0:
        print(f"✅ Writing batch {epoch_id} with {count} rows")
        batch_df.write \
            .jdbc(url=jdbc_url, table="pret_etudiant", mode="append", properties=jdbc_properties)
    else:
        print(f"⚠️ Batch {epoch_id} is empty")

# === Lancement du stream avec foreachBatch ===
df_parsed.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoints/pret_etudiant") \
    .start() \
    .awaitTermination()
