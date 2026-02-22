"""
Spark Structured Streaming pattern for this project.

Requires Spark and the Kafka connector package at runtime, e.g.:
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 \
  scripts/spark_structured_streaming.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import ArrayType, DoubleType, MapType, StringType, StructField, StructType


def main() -> None:
    spark = SparkSession.builder.appName("autopilot-stream-curation").getOrCreate()

    ann_schema = StructType(
        [
            StructField("annotator_id", StringType(), True),
            StructField("label_class", StringType(), True),
            StructField("bbox", MapType(StringType(), DoubleType()), True),
            StructField("quality_score", DoubleType(), True),
        ]
    )

    event_schema = StructType(
        [
            StructField("source_uri", StringType(), True),
            StructField("sensor_type", StringType(), True),
            StructField("captured_at", StringType(), True),
            StructField("weather", StringType(), True),
            StructField("scenario", StringType(), True),
            StructField("compression", StringType(), True),
            StructField("annotations", ArrayType(ann_schema), True),
        ]
    )

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "perception-events")
        .option("startingOffsets", "earliest")
        .load()
    )

    parsed = raw.select(from_json(col("value").cast("string"), event_schema).alias("event")).select("event.*")

    # Example streaming curation: keep hard scenarios for active-learning loops.
    hard_examples = parsed.filter(col("scenario").isin("occlusion", "merge") | (col("weather") == "night"))

    query = (
        hard_examples.writeStream.format("parquet")
        .option("path", "data/curated/hard_examples")
        .option("checkpointLocation", "data/curated/_checkpoints/hard_examples")
        .outputMode("append")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
