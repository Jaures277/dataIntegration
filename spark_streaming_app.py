from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType

# Initialisation de Spark
spark = SparkSession.builder \
    .appName("StudentLoanStreamSQLite") \
    .config("spark.jars", "/opt/spark/jars/sqlite-jdbc-3.40.1.jar") \
    .getOrCreate()

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
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:sqlite:/app/student_loan_data.db") \
        .option("dbtable", "school_data") \
        .option("driver", "org.sqlite.JDBC") \
        .mode("append") \
        .save()

# Écrire dans SQLite via le streaming
processed_df.writeStream \
    .foreachBatch(write_to_sqlite) \
    .start() \
    .awaitTermination()

# Afficher les données dans la console pour débogage
query = processed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()