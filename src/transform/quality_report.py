import duckdb
import json

from config.settings import (
    DB_PATH,
    REPORT_PATH
)

from src.utils.logger import get_logger

logger = get_logger()


def get_nulls(conn, table_name):
    columns = conn.execute(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
    """).fetchall()

    result = {}

    for (col,) in columns:
        null_pct = conn.execute(f"""
            SELECT
                ROUND(
                    100.0 * SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) / COUNT(*),
                    2
                )
            FROM {table_name}
        """).fetchone()[0]

        result[col] = float(null_pct or 0)

    return result


def generate_quality_report():

    REPORT_PATH.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(DB_PATH))

    logger.info("Generating quality report")

    ## ======================
    ## ROW COUNTS
    ## ======================

    raw_spe_rows = conn.execute(
        "SELECT COUNT(*) FROM raw_spe"
    ).fetchone()[0]

    spe_clean_rows = conn.execute(
        "SELECT COUNT(*) FROM spe_clean"
    ).fetchone()[0]

    raw_wind_rows = conn.execute(
        "SELECT COUNT(*) FROM raw_wind"
    ).fetchone()[0]

    wind_clean_rows = conn.execute(
        "SELECT COUNT(*) FROM wind_clean"
    ).fetchone()[0]

    ## ======================
    ## DUPLICATES (IDENTIFY + TREATED)
    ## ======================

    spe_distinct = conn.execute("""
        SELECT COUNT(*) FROM (SELECT DISTINCT * FROM raw_spe)
    """).fetchone()[0]

    spe_duplicates_removed = raw_spe_rows - spe_distinct

    wind_distinct = conn.execute("""
        SELECT COUNT(*) FROM (SELECT DISTINCT * FROM raw_wind)
    """).fetchone()[0]

    wind_duplicates_removed = raw_wind_rows - wind_distinct

    ## ======================
    ## INVALID WIND (IDENTIFY + TREATED)
    ## ======================

    invalid_wind = conn.execute("""
        SELECT COUNT(*)
        FROM raw_spe
        WHERE flg_dadoventoinvalido = 1
    """).fetchone()[0]

    ## ======================
    ## INVALID DATES (VALIDATION)
    ## ======================

    invalid_dates = conn.execute("""
        SELECT COUNT(*)
        FROM raw_spe
        WHERE TRY_CAST(din_instante AS TIMESTAMP) IS NULL
    """).fetchone()[0]

    ## ======================
    ## INVALID NUMERIC (VALIDATION)
    ## ======================

    spe_invalid_numeric = {}

    for col in [
        "val_ventoverificado",
        "val_geracaoestimada",
        "val_geracaoverificada"
    ]:
        count = conn.execute(f"""
            SELECT COUNT(*)
            FROM raw_spe
            WHERE {col} IS NOT NULL
            AND TRY_CAST({col} AS DOUBLE) IS NULL
        """).fetchone()[0]

        spe_invalid_numeric[col] = int(count)

    wind_invalid_numeric = {}

    for col in [
        "val_geracao",
        "val_geracaolimitada",
        "val_disponibilidade",
        "val_geracaoreferencia",
        "val_geracaoreferenciafinal"
    ]:
        count = conn.execute(f"""
            SELECT COUNT(*)
            FROM raw_wind
            WHERE {col} IS NOT NULL
            AND TRY_CAST({col} AS DOUBLE) IS NULL
        """).fetchone()[0]

        wind_invalid_numeric[col] = int(count)

    ## ======================
    ## NULLS (FINAL DATASET)
    ## ======================

    spe_nulls = get_nulls(conn, "spe_clean")
    wind_nulls = get_nulls(conn, "wind_clean")

    ## ======================
    ## FINAL REPORT
    ## ======================

    report = [
        {
            "spe_nulls": spe_nulls,
            "wind_nulls": wind_nulls,

            "spe_stats": {
                "initial_rows": int(raw_spe_rows),
                "duplicates_removed": int(spe_duplicates_removed),
                "invalid_wind_filtered": int(invalid_wind),
                "invalid_dates": int(invalid_dates),
                "invalid_numeric_values": spe_invalid_numeric,
                "final_rows": int(spe_clean_rows)
            },

            "wind_stats": {
                "initial_rows": int(raw_wind_rows),
                "duplicates_removed": int(wind_duplicates_removed),
                "invalid_dates": 0,
                "invalid_numeric_values": wind_invalid_numeric,
                "final_rows": int(wind_clean_rows)
            }
        }
    ]

    output_path = (
        REPORT_PATH
        / "data_quality_report_pipeline.json"
    )

    with open(output_path, "w") as file:
        json.dump(report, file, indent=4)

    logger.info(f"Quality report saved: {output_path}")

    conn.close()


if __name__ == "__main__":
    generate_quality_report()