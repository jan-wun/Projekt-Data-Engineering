import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (from_unixtime, col, avg, min, max, sum, year, quarter, countDistinct, to_date,
                                   round, lit, when)

# PostgreSQL connection settings
POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

POSTGRES_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Initialize Spark
spark = SparkSession.builder \
    .appName("Bitcoin Data Preprocessing & Aggregation") \
    .config("spark.jars", "/opt/spark-app/postgresql-42.7.3.jar") \
    .getOrCreate()

# Load raw data from PostgreSQL
raw_df = spark.read \
    .format("jdbc") \
    .option("url", POSTGRES_URL) \
    .option("dbtable", "raw_bitcoin_data") \
    .option("user", POSTGRES_USER) \
    .option("password", POSTGRES_PASSWORD) \
    .option("driver", "org.postgresql.Driver") \
    .option("partitionColumn", "timestamp") \
    .option("lowerBound", "0") \
    .option("upperBound", "2000000000") \
    .option("numPartitions", "8") \
    .load()

print(f"[INFO] Total records in raw data: {raw_df.count()}")

# Transform timestamp to datetime
staged_df = raw_df.withColumn("datetime", from_unixtime(col("timestamp")).cast("timestamp")) \
    .drop("timestamp") \
    .select("datetime", "open", "high", "low", "close", "volume")

# Data validation: Check for nulls in critical columns
null_counts = staged_df.select([col(c).isNull().alias(c) for c in staged_df.columns]).groupBy().sum().collect()[0].asDict()
null_summary = {k.replace("sum(", "").replace(")", ""): v for k, v in null_counts.items()}
print(f"[INFO] Null value summary: {null_summary}")

# Filter out invalid rows
valid_df = staged_df.dropna(subset=["datetime", "open", "high", "low", "close", "volume"])
invalid_count = staged_df.count() - valid_df.count()
print(f"[INFO] Dropping {invalid_count} invalid rows with nulls")

# Write to staged table
valid_df.write \
    .format("jdbc") \
    .option("url", POSTGRES_URL) \
    .option("dbtable", "staged_bitcoin_data") \
    .option("user", POSTGRES_USER) \
    .option("password", POSTGRES_PASSWORD) \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()

print(f"[SUCCESS] {valid_df.count()} records written to staged_bitcoin_data.")

# Aggregation by year and quarter
valid_df = valid_df.withColumn("date", to_date("datetime"))
aggregated_df = valid_df.withColumn("year", year("datetime")) \
    .withColumn("quarter", quarter("datetime")) \
    .groupBy("year", "quarter") \
    .agg(
        round(avg("open"), 2).alias("avg_open"),
        round(avg("close"), 2).alias("avg_close"),
        round(min("low"), 2).alias("min_low"),
        round(max("high"), 2).alias("max_high"),
        round(sum("volume"), 2).alias("total_volume"),
        countDistinct("date").alias("count_days")
    )

# Add flag for partial quarters
current_info = spark.sql("SELECT year(current_date()) AS y, quarter(current_date()) AS q").collect()[0]
aggregated_df = aggregated_df.withColumn(
    "is_partial",
    when(
        (col("year") == current_info['y']) & (col("quarter") == current_info['q']),
        lit(True)
    ).otherwise(lit(False))
)

# Write to aggregated table
aggregated_df.write \
    .format("jdbc") \
    .option("url", POSTGRES_URL) \
    .option("dbtable", "aggregated_bitcoin_data") \
    .option("user", POSTGRES_USER) \
    .option("password", POSTGRES_PASSWORD) \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()

print(f"[SUCCESS] {aggregated_df.count()} aggregated records written to aggregated_bitcoin_data.")

spark.stop()
