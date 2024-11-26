import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType

# Initialisation de Spark
spark = SparkSession.builder \
    .appName("StudentLoanStreamSQLite") \
    .config("spark.jars", "/opt/spark/jars/sqlite-jdbc-3.46.1.2.jar") \
    .getOrCreate()

# Création automatique du dossier pour la base de données
db_folder = "/tmp/data"
db_file = f"{db_folder}/student_loan_data.db"

if not os.path.exists(db_folder):
    os.makedirs(db_folder)
    print(f"Répertoire créé : {db_folder}")
else:
    print(f"Répertoire existant : {db_folder}")

# Définir le schéma des messages Kafka
schema = StructType() \
    .add("schoolcode", StringType()) \
    .add("schoolname", StringType()) \
    .add("address", StringType()) \
    .add("city", StringType()) \
    .add("statecode", StringType()) \
    .add("zipcode", IntegerType()) \
    .add("province", StringType()) \
    .add("country", StringType()) \
    .add("postalcode", StringType())

# Lire les données de Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "student_loan_topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Extraire et traiter les données JSON
processed_df = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Fonction pour écrire dans SQLite
def write_to_sqlite(batch_df, batch_id):
    try:
        batch_df.write \
            .format("jdbc") \
            .option("url", f"jdbc:sqlite:{db_file}") \
            .option("dbtable", "school_data") \
            .option("driver", "org.sqlite.JDBC") \
            .mode("append") \
            .save()
    except Exception as e:
        print(f"Erreur lors de l'écriture du batch {batch_id} : {e}")

# Écrire dans SQLite via le streaming
processed_df.writeStream \
    .foreachBatch(write_to_sqlite) \
    .start() \
    .awaitTermination()
