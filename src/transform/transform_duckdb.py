import duckdb

from config.settings import DB_PATH

from src.utils.logger import get_logger

logger = get_logger()


def transform():
    """
    Executes SQL transformations inside DuckDB.

    Creates cleaned tables from raw datasets
    and removes duplicate records.

    Returns

    None
    """

    conn = duckdb.connect(str(DB_PATH))

    logger.info("Starting transformations")

    conn.execute("""

    CREATE OR REPLACE TABLE spe_clean AS

    SELECT DISTINCT *
    FROM raw_spe

    """)

    conn.execute("""

    CREATE OR REPLACE TABLE wind_clean AS

    SELECT DISTINCT *
    FROM raw_wind

    """)

    logger.info("Transformations completed")

    conn.close()


if __name__ == "__main__":

    transform()