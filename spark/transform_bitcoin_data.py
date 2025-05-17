import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_unixtime, col

# PostgreSQL connection settings
POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

POSTGRES_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Initialize Spark
spark = SparkSession.builder \
    .appName("Bitcoin Data Preprocessing") \
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
staged_df = raw_df.withColumn("datetime", from_unixtime(col("timestamp"))) \
    .drop("timestamp") \
    .select("datetime", "open", "high", "low", "close", "volume")

# Data validation: Check for nulls in critical columns
null_counts = staged_df.select([col(c).isNull().alias(c) for c in staged_df.columns]).groupBy().sum().collect()[0].asDict()

null_summary = {k.replace("sum(", "").replace(")", ""): v for k, v in null_counts.items()}
null_summary_str = ", ".join([f"{k}={v}" for k, v in null_summary.items()])
print(f"[INFO] Null value summary: {null_summary_str}")

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

spark.stop()
