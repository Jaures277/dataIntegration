from pyspark.sql import SparkSession

# Initialisation Spark
spark = SparkSession.builder \
    .appName("SQLiteExample") \
    .config("spark.jars", "/opt/spark/jars/sqlite-jdbc-3.40.1.jar") \
    .getOrCreate()

# URL JDBC pour SQLite
jdbc_url = "jdbc:sqlite:/path/to/your/database.db"

# Exemple : Écriture des données dans SQLite
data = [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
columns = ["id", "name"]
df = spark.createDataFrame(data, columns)

df.write \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "people") \
    .mode("overwrite") \
    .save()
