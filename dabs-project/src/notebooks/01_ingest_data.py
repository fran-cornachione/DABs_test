# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Ingest Data
# MAGIC Reads raw data from source and writes to Bronze layer (Delta Lake).

# COMMAND ----------
dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "default")

catalog = dbutils.widgets.get("catalog")
schema  = dbutils.widgets.get("schema")

print(f"Running ingestion → {catalog}.{schema}")

# COMMAND ----------
from pyspark.sql import functions as F

# Example: read CSV from DBFS / Volume
raw_df = (
    spark.read
    .format("csv")
    .option("header", True)
    .option("inferSchema", True)
    .load("/Volumes/landing/raw_data/*.csv")
)

# COMMAND ----------
# Write to Bronze Delta table
(
    raw_df
    .withColumn("ingestion_ts", F.current_timestamp())
    .write
    .format("delta")
    .mode("append")
    .saveAsTable(f"{catalog}.{schema}.bronze_raw")
)

print("Ingestion complete.")
