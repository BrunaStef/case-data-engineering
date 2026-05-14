from pathlib import Path
import duckdb

from config.settings import (
    RAW_PATH,
    DB_PATH
)

from src.utils.logger import get_logger

logger = get_logger()


def load_csvs():
    """
    Loads raw CSV files into DuckDB tables.

    Creates or replaces raw tables for
    SPE and Wind Farm datasets.

    Returns

    None
    """

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = duckdb.connect(str(DB_PATH))

    logger.info("Loading raw CSVs into DuckDB")

    conn.execute("""
        CREATE OR REPLACE TABLE raw_spe AS
        SELECT *
        FROM read_csv_auto(
            'data/raw/spe/*.csv'
        )
    """)

    conn.execute("""
        CREATE OR REPLACE TABLE raw_wind AS
        SELECT *
        FROM read_csv_auto(
            'data/raw/wind_farm/*.csv'
        )
    """)

    logger.info("Load completed")

    conn.close()


if __name__ == "__main__":

    load_csvs()