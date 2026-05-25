"""
Unit tests for transformation logic.
These tests run locally with PySpark / Delta Spark (no Databricks cluster needed).
"""
import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("dabs-unit-tests")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .getOrCreate()
    )


def test_dedup_removes_duplicates(spark):
    data = [
        (1, "a", 10.0),
        (1, "a", 10.0),   # duplicate
        (2, "b", 20.0),
    ]
    df = spark.createDataFrame(data, ["id", "category", "amount"])
    result = df.dropDuplicates()
    assert result.count() == 2


def test_null_filter_removes_nulls(spark):
    data = [(1, "a"), (2, None), (3, "c")]
    df = spark.createDataFrame(data, ["id", "value"])
    result = df.filter(F.col("value").isNotNull())
    assert result.count() == 2


def test_gold_aggregation(spark):
    from datetime import date

    data = [
        (date(2024, 1, 1), "clicks", 1),
        (date(2024, 1, 1), "clicks", 1),
        (date(2024, 1, 2), "views",  1),
    ]
    df = spark.createDataFrame(data, ["event_date", "event_type", "cnt"])
    agg = df.groupBy("event_date", "event_type").agg(F.sum("cnt").alias("total"))

    row = agg.filter(
        (F.col("event_date") == date(2024, 1, 1)) & (F.col("event_type") == "clicks")
    ).first()

    assert row["total"] == 2
