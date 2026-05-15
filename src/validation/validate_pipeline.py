from pathlib import Path
import pandas as pd
import json

from src.utils.logger import get_logger

logger = get_logger("validate_pipeline")

PARQUET_PATH = Path(
    "data/final_parquet_pipeline"
)

REPORT_PATH = Path(
    "data/validation_reports"
)

EXPECTED_COLUMNS = {
    "id_subsistema": "str",
    "id_estado": "str",
    "nom_modalidadeoperacao": "str",
    "nom_conjuntousina": "str",
    "nom_usina": "str",
    "id_ons": "str",
    "ceg": "str",
    "din_instante": "datetime64[us]",
    "val_ventoverificado": "float64",
    "flg_dadoventoinvalido": "float64",
    "val_geracaoestimada": "float64",
    "val_geracaoverificada": "float64",
    "projeto": "str",
    "nom_subsistema": "str",
    "nom_estado": "str",
    "val_geracao": "float64",
    "val_disponibilidade": "float64",
    "val_geracaoreferencia": "float64",
    "val_geracaoreferenciafinal": "float64",
    "year": "category",
    "month": "category"
}


def load_data():
    """
    Loads the partitioned parquet dataset.

    Returns

    DataFrame with consolidated parquet data.
    """

    logger.info("Loading parquet dataset")

    df = pd.read_parquet(
        PARQUET_PATH,
        engine="pyarrow"
    )

    df["din_instante"] = pd.to_datetime(
        df["din_instante"]
    )

    return df


def validate_schema(df):
    """
    Validates expected columns and data types.

    Parameters

    df : Input dataframe.

    Returns

    Dictionary with schema validation results.
    """

    logger.info("Running schema validation")

    missing_columns = []

    invalid_types = {}

    for column, expected_type in EXPECTED_COLUMNS.items():

        if column not in df.columns:

            missing_columns.append(column)

        else:

            current_type = str(df[column].dtype)

            if current_type != expected_type:

                invalid_types[column] = {
                    "expected": expected_type,
                    "found": current_type
                }

    return {
        "missing_columns": missing_columns,
        "invalid_types": invalid_types,
        "schema_valid": (
            len(missing_columns) == 0
            and len(invalid_types) == 0
        )
    }


def validate_freshness(df):
    """
    Validates if the latest expected month exists.

    Parameters

    df : Input dataframe.

    Returns

    Dictionary with freshness validation.
    """

    logger.info("Running freshness validation")

    latest_year = int(
        df["year"].astype(int).max()
    )

    latest_month = int(
        df[
            df["year"].astype(int) == latest_year
        ]["month"].astype(int).max()
    )

    return {
        "latest_year": latest_year,
        "latest_month": latest_month,
        "freshness_valid": True
    }


def validate_business_rules(df):
    """
    Validates business rules.

    Parameters

    df : Input dataframe.

    Returns

    Dictionary with business rule validations.
    """

    logger.info("Running business rules validation")

    negative_generation = int(
        (df["val_geracao"] < 0).sum()
    )

    invalid_estimated_generation = int(
        (df["val_geracaoestimada"] < 0).sum()
    )

    invalid_verified_generation = int(
        (df["val_geracaoverificada"] < 0).sum()
    )

    invalid_wind_speed = int(
        (
            ~df["val_ventoverificado"].between(0, 40)
        ).sum()
    )

    generation_reference_invalid = int(
        (
            df["val_geracao"]
            > df["val_geracaoreferencia"]
        ).fillna(False).sum()
    )

    invalid_availability = int(
        (
            df["val_disponibilidade"] < 0
        ).sum()
    )

    duplicate_timestamps = int(
        df.duplicated(
            subset=[
                "projeto",
                "nom_usina",
                "din_instante"
            ]
        ).sum()
    )

    invalid_null_projects = int(
        df["projeto"].isnull().sum()
    )

    return {
        "negative_generation": negative_generation,

        "invalid_estimated_generation": invalid_estimated_generation,

        "invalid_verified_generation": invalid_verified_generation,

        "invalid_wind_speed": invalid_wind_speed,

        "generation_reference_invalid": generation_reference_invalid,

        "invalid_availability": invalid_availability,

        "duplicate_timestamps": duplicate_timestamps,

        "null_projects": invalid_null_projects
    }


def validate_timestamp_continuity(df):
    """
    Checks timestamp continuity for each project and wind farm.

    Parameters

    df : Input dataframe.

    Returns

    Dictionary with projects containing gaps.
    """

    logger.info(
        "Running timestamp continuity validation"
    )

    gaps = {}

    grouped = df.groupby(
        ["projeto", "nom_usina"]
    )

    for (project, wind_farm), group in grouped:

        timestamps = (
            pd.to_datetime(
                group["din_instante"]
            )
            .dt.floor("h")
            .drop_duplicates()
            .sort_values()
        )

        differences = timestamps.diff()

        gap_count = int(
            (
                differences
                > pd.Timedelta(hours=1)
            ).sum()
        )

        gaps[
            f"{project} | {wind_farm}"
        ] = gap_count

    return gaps


def validate_completeness(
    df,
    threshold=95
):
    """
    Calculates completeness percentage by project.

    Parameters

    df : Input dataframe.

    threshold : Minimum completeness threshold.

    Returns

    Dictionary with completeness results.
    """

    logger.info(
        "Running completeness validation"
    )

    completeness = {}

    alerts = {}

    grouped = df.groupby(
        ["projeto", "nom_usina"]
    )

    for (project, wind_farm), group in grouped:

        timestamps = (
            pd.to_datetime(
                group["din_instante"]
            )
            .dt.floor("h")
        )

        timestamps = timestamps.dropna()

        timestamps = timestamps.sort_values()

        received = timestamps.nunique()

        expected = pd.date_range(
            start=timestamps.min(),
            end=timestamps.max(),
            freq="h"
        )

        expected_total = len(expected)

        percentage = round(
            (
                received
                / expected_total
            ) * 100,
            2
        )

        completeness[
            f"{project} | {wind_farm}"
        ] = percentage

        if percentage < threshold:

            alerts[
                f"{project} | {wind_farm}"
            ] = percentage

    return {
        "completeness_percentage": completeness,

        "projects_below_threshold": alerts,

        "threshold": threshold
    }


def save_report(report):
    """
    Saves validation report as JSON.

    Parameters

    report : Validation report dictionary.

    Returns

    None
    """

    REPORT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        REPORT_PATH
        / "validation_report.json"
    )

    with open(output_path, "w") as file:

        json.dump(
            report,
            file,
            indent=4,
            default=str
        )

    logger.info(
        f"Validation report saved: {output_path}"
    )


def main():
    """
    Executes all validation checks.

    Returns

    None
    """

    logger.info(
        "Validation pipeline started"
    )

    df = load_data()

    report = {
        "schema_validation": validate_schema(df),

        "freshness_validation": validate_freshness(df),

        "business_rules": validate_business_rules(df),

        "timestamp_continuity": validate_timestamp_continuity(df),

        "completeness_validation": validate_completeness(df)
    }

    save_report(report)

    logger.info(
        "Validation pipeline completed"
    )


if __name__ == "__main__":

    main()
