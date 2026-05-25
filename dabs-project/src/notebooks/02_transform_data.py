# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Transform Data
# MAGIC Applies business logic and writes to Silver layer.

# COMMAND ----------
dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "default")

catalog = dbutils.widgets.get("catalog")
schema  = dbutils.widgets.get("schema")

# COMMAND ----------
from pyspark.sql import functions as F

bronze_df = spark.table(f"{catalog}.{schema}.bronze_raw")

silver_df = (
    bronze_df
    .dropDuplicates()
    .filter(F.col("value").isNotNull())
    .withColumn("processed_date", F.to_date("ingestion_ts"))
    .withColumn("value_clean", F.trim(F.col("value")))
)

# COMMAND ----------
(
    silver_df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .saveAsTable(f"{catalog}.{schema}.silver_processed")
)

print("Transformation complete.")
