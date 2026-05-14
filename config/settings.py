from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")

RAW_PATH = Path(os.getenv("RAW_PATH"))

DB_PATH = Path(os.getenv("DB_PATH"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")