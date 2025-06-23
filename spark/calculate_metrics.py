import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum
import matplotlib.pyplot as plt

# 🔧 Spark setup
os.environ["HADOOP_USER_NAME"] = "spark"
os.environ["USER"] = "spark"

spark = SparkSession.builder \
    .appName("Metrics_Calculation") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 📥 Lecture des données depuis HDFS
df = spark.read.parquet("hdfs://namenode:9000/user/spark/output/v1")

# 🧮 Nombre total de prêts par État (filtrage des états vides ou nuls)
df_pret_par_etat = df.filter(df.nan_state.isNotNull() & (df.nan_state != '')) \
    .groupBy("nan_state").agg(
        sum("subsidized_loans_originated_amount").alias("total_subsidized"),
        sum("unsubsidized_loans_originated_amount").alias("total_unsubsidized"),
        sum("parent_plus_loans_originated_amount").alias("total_parent_plus")
    )

# 💬 Affichage pour capture terminal
print("📊 Résumé du nombre de prêts par État")
df_pret_par_etat.show(10, truncate=False)

# 📊 Conversion en Pandas pour tracé
df_plot = df_pret_par_etat.toPandas()
df_plot["total"] = df_plot["total_subsidized"] + df_plot["total_unsubsidized"] + df_plot["total_parent_plus"]

# 📈 Courbe matplotlib
plt.figure(figsize=(12, 6))
df_plot.sort_values("total", ascending=False).plot(
    x="nan_state",
    y="total",
    kind="bar",
    legend=False,
    title="📈 Nombre total de prêts par État"
)
plt.ylabel("Montant total des prêts ($)")
plt.tight_layout()
plt.savefig("/tmp/pret_par_etat.png")

# 📝 Sauvegarde parquet facultative
df_pret_par_etat.write.mode("overwrite").parquet("hdfs://namenode:9000/user/spark/metrics/pret_par_etat")

print("✅ Métriques par État calculées et courbe générée : /tmp/pret_par_etat.png")
