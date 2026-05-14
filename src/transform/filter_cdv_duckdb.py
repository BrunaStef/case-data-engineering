import duckdb

from config.settings import DB_PATH

from src.utils.logger import get_logger

logger = get_logger()


def filter_cdv():
    """
    Filters Casa dos Ventos assets.

    Returns

    None
    """

    conn = duckdb.connect(str(DB_PATH))

    logger.info("Filtering Casa dos Ventos assets")

    conn.execute("""

    CREATE OR REPLACE TABLE spe_cdv AS

    SELECT
        s.*,
        r.projeto
    FROM spe_clean s
    INNER JOIN read_csv_auto(
        'data/raw/spes_casa_dos_ventos.csv'
    ) r
    ON regexp_extract(
        s.ceg,
        '(\\d{6,7}-\\d)'
    ) = r.ceg

    """)

    conn.execute("""

    CREATE OR REPLACE TABLE wind_cdv AS

    SELECT *
    FROM wind_clean
    WHERE UPPER(TRIM(nom_usina)) IN (

        SELECT DISTINCT
            UPPER(TRIM(nom_conjuntousina))
        FROM spe_cdv

    )

    """)

    logger.info("Casa dos Ventos filtering completed")

    conn.close()


if __name__ == "__main__":

    filter_cdv()

