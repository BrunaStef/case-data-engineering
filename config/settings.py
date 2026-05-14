from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")

RAW_PATH = Path("data/raw")

DB_PATH = Path("data/duckdb/cdv_pipeline.duckdb")

REPORT_PATH = Path("data/reports")

FINAL_PARQUET_PATH = Path(
    "data/final_parquet_pipeline"
)