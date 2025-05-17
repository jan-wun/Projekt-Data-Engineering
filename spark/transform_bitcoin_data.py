import os
from pyspark.sql import SparkSession

POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

POSTGRES_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

spark = SparkSession.builder \
    .appName("Bitcoin Data Transformation") \
    .config("spark.jars", "/opt/spark-app/postgresql-42.7.3.jar") \
    .getOrCreate()

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

print(f"Datensätze insgesamt: {raw_df.count()}")
raw_df.select("timestamp").show(5)


spark.stop()
