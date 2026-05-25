# Databricks notebook source
# MAGIC %md
# MAGIC # DLT Pipeline
# MAGIC Delta Live Tables pipeline definition.

# COMMAND ----------
import dlt
from pyspark.sql import functions as F

# COMMAND ----------
@dlt.table(
    name="bronze_events",
    comment="Raw events ingested from source",
    table_properties={"quality": "bronze"},
)
def bronze_events():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/Volumes/landing/events/")
    )

# COMMAND ----------
@dlt.table(
    name="silver_events",
    comment="Cleaned and validated events",
    table_properties={"quality": "silver"},
)
@dlt.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
@dlt.expect_or_drop("valid_timestamp", "event_ts IS NOT NULL")
def silver_events():
    return (
        dlt.read_stream("bronze_events")
        .withColumn("event_date", F.to_date("event_ts"))
        .withColumn("processed_ts", F.current_timestamp())
        .dropDuplicates(["event_id"])
    )

# COMMAND ----------
@dlt.table(
    name="gold_event_summary",
    comment="Daily event aggregations",
    table_properties={"quality": "gold"},
)
def gold_event_summary():
    return (
        dlt.read("silver_events")
        .groupBy("event_date", "event_type")
        .agg(
            F.count("*").alias("event_count"),
            F.countDistinct("user_id").alias("unique_users"),
        )
    )
