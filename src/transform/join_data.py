import duckdb

from config.settings import DB_PATH

from src.utils.logger import get_logger

logger = get_logger()


def join_datasets():
    """
    Joins SPE and Wind Farm datasets.

    Returns

    None
    """

    conn = duckdb.connect(str(DB_PATH))

    logger.info("Joining datasets")

    conn.execute("""

    CREATE OR REPLACE TABLE cdv_joined AS

    SELECT
        s.*,
        w.nom_subsistema,
        w.nom_estado,
        w.val_geracao,
        w.val_disponibilidade,
        w.val_geracaoreferencia,
        w.val_geracaoreferenciafinal,
        w.cod_razaorestricao  

    FROM spe_cdv s

    LEFT JOIN wind_cdv w

        ON UPPER(TRIM(s.nom_conjuntousina))
        = UPPER(TRIM(w.nom_usina))

        AND s.din_instante = w.din_instante

    """)

    logger.info("Join completed")

    conn.close()


if __name__ == "__main__":

    join_datasets()
