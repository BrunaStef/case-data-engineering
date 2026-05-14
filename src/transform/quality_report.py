import duckdb
import pandas as pd
import json

from config.settings import (
    DB_PATH,
    REPORT_PATH
)

from src.utils.logger import get_logger

logger = get_logger()


def calculate_nulls(df):
    """
    Calculates null percentage for each column.

    Parameters

    df : Input dataframe.

    Returns

    Dictionary with null percentages.
    """

    return {
        col: float(
            round(
                df[col].isnull().mean() * 100,
                2
            )
        )
        for col in df.columns
    }


def calculate_invalid_numeric(df, columns):
    """
    Counts invalid numeric values by column.

    Parameters

    df : Input dataframe.

    columns : Numeric columns list.

    Returns

    Dictionary with invalid numeric counts.
    """

    invalids = {}

    for col in columns:

        invalids[col] = int(
            pd.to_numeric(
                df[col],
                errors="coerce"
            ).isnull().sum()
        )

    return invalids


def generate_quality_report():
    """
    Generates a detailed data quality report.

    Returns

    None
    """

    REPORT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = duckdb.connect(str(DB_PATH))

    logger.info("Generating quality report")

    raw_spe = conn.execute(
        "SELECT * FROM raw_spe"
    ).fetchdf()

    raw_wind = conn.execute(
        "SELECT * FROM raw_wind"
    ).fetchdf()

    spe_clean = conn.execute(
        "SELECT * FROM spe_clean"
    ).fetchdf()

    wind_clean = conn.execute(
        "SELECT * FROM wind_clean"
    ).fetchdf()


    spe_duplicates = (
        len(raw_spe)
        - len(raw_spe.drop_duplicates())
    )

    invalid_wind = int(
        (
            raw_spe["flg_dadoventoinvalido"] == 1
        ).sum()
    )

    spe_invalid_numeric = calculate_invalid_numeric(
        raw_spe,
        [
            "val_ventoverificado",
            "val_geracaoestimada",
            "val_geracaoverificada"
        ]
    )


    wind_duplicates = (
        len(raw_wind)
        - len(raw_wind.drop_duplicates())
    )

    wind_invalid_numeric = calculate_invalid_numeric(
        raw_wind,
        [
            "val_geracao",
            "val_geracaolimitada",
            "val_disponibilidade",
            "val_geracaoreferencia",
            "val_geracaoreferenciafinal"
        ]
    )

    report = [
        {
            "spe_nulls": calculate_nulls(spe_clean),

            "wind_nulls": calculate_nulls(wind_clean),

            "spe_stats": {
                "initial_rows": int(len(raw_spe)),
                "duplicates_removed": int(spe_duplicates),
                "invalid_wind_filtered": int(invalid_wind),
                "invalid_dates": 0,
                "invalid_numeric_values": spe_invalid_numeric,
                "final_rows": int(len(spe_clean))
            },

            "wind_stats": {
                "initial_rows": int(len(raw_wind)),
                "duplicates_removed": int(wind_duplicates),
                "invalid_dates": 0,
                "invalid_numeric_values": wind_invalid_numeric,
                "final_rows": int(len(wind_clean))
            }
        }
    ]

    output_path = (
        REPORT_PATH
        / "data_quality_report_pipeline.json"
    )

    with open(output_path, "w") as file:

        json.dump(
            report,
            file,
            indent=4
        )

    logger.info(
        f"Detailed quality report saved: {output_path}"
    )

    conn.close()


if __name__ == "__main__":

    generate_quality_report()
