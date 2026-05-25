# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Load Data
# MAGIC Builds Gold layer aggregations for reporting.

# COMMAND ----------
dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "default")

catalog = dbutils.widgets.get("catalog")
schema  = dbutils.widgets.get("schema")

# COMMAND ----------
from pyspark.sql import functions as F

silver_df = spark.table(f"{catalog}.{schema}.silver_processed")

gold_df = (
    silver_df
    .groupBy("processed_date", "category")
    .agg(
        F.count("*").alias("record_count"),
        F.sum("amount").alias("total_amount"),
        F.avg("amount").alias("avg_amount"),
    )
)

# COMMAND ----------
(
    gold_df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .saveAsTable(f"{catalog}.{schema}.gold_summary")
)

print("Load complete.")
