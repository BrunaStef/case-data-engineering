import duckdb

from config.settings import (
    DB_PATH,
    FINAL_PARQUET_PATH
)

from src.utils.logger import get_logger

logger = get_logger()


def export_parquet():
    """
    Exports final dataset to partitioned parquet.

    Returns

    None
    """

    FINAL_PARQUET_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = duckdb.connect(str(DB_PATH))

    logger.info("Exporting parquet")

    conn.execute(f"""

    COPY (

        SELECT
            *,
            YEAR(data_hora) AS year,
            MONTH(data_hora) AS month

        FROM cdv_joined

    )

    TO '{FINAL_PARQUET_PATH}'

    (
        FORMAT PARQUET,
        PARTITION_BY (year, month),
        OVERWRITE_OR_IGNORE TRUE
    )

    """)

    logger.info("Parquet export completed")

    conn.close()


if __name__ == "__main__":

    export_parquet()

