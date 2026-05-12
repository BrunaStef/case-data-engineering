from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/interim")
PROCESSED_PATH = Path("data/processed")
REPORT_PATH = Path("data/reports")

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
REPORT_PATH.mkdir(parents=True, exist_ok=True)

## LOAD DATA

def load_data():
    """
    Loads consolidated SPE and Wind Farm datasets from local storage.

    Returns
   
    spe : Consolidated SPE dataset.
    wind : Consolidated Wind Farm dataset.
    """
    spe = pd.read_csv(DATA_PATH / "spe_consolidated.csv")
    wind = pd.read_csv(DATA_PATH / "wind_farm_consolidated.csv")
    return spe, wind


## NULL REPORT

def null_report(df: pd.DataFrame):
    """
    Calculates percentage of missing values per column.

    Parameters
    
    df : Input dataset.

    Returns
    
    Percentage of null values per column.
    """
    return (df.isnull().mean() * 100).round(2)


## CLEAN SPE

def clean_spe(df: pd.DataFrame):
    """
    Cleans SPE dataset by removing duplicates, filtering invalid wind data,
    and validating data types (dates and numerics).

    Parameters
    
    df : Raw SPE dataset.

    Returns
    
    df : Cleaned SPE dataset.
    stats : Dictionary containing data quality metrics.
    """

    initial_rows = len(df)

    ## duplicates
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)

    ## invalid wind filter
    invalid_before = len(df)
    df = df[df["flg_dadoventoinvalido"] == 0.0]
    invalid_filtered = invalid_before - len(df)

    ## datetime validation
    df["din_instante"] = pd.to_datetime(df["din_instante"], errors="coerce")
    invalid_dates = df["din_instante"].isna().sum()

    ## numeric validation
    numeric_cols = [
        "val_ventoverificado",
        "val_geracaoestimada",
        "val_geracaoverificada"
    ]

    invalid_numeric = {}

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            invalid_numeric[col] = df[col].isna().sum()

    stats = {
        "initial_rows": initial_rows,
        "duplicates_removed": duplicates_removed,
        "invalid_wind_filtered": invalid_filtered,
        "invalid_dates": int(invalid_dates),
        "invalid_numeric_values": invalid_numeric,
        "final_rows": len(df)
    }

    return df, stats


## CLEAN WIND FARM

def clean_wind(df: pd.DataFrame):
    """
    Cleans Wind Farm dataset by removing duplicates and validating
    data types (dates and numeric fields).

    Parameters
    
    df : Raw Wind Farm dataset.

    Returns
    
    df : Cleaned Wind Farm dataset.
    stats : Dictionary containing data quality metrics.
    """

    initial_rows = len(df)

    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)

    df["din_instante"] = pd.to_datetime(df["din_instante"], errors="coerce")
    invalid_dates = df["din_instante"].isna().sum()

    numeric_cols = [
        "val_geracao",
        "val_geracaolimitada",
        "val_disponibilidade",
        "val_geracaoreferencia",
        "val_geracaoreferenciafinal"
    ]

    invalid_numeric = {}

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            invalid_numeric[col] = df[col].isna().sum()

    stats = {
        "initial_rows": initial_rows,
        "duplicates_removed": duplicates_removed,
        "invalid_dates": int(invalid_dates),
        "invalid_numeric_values": invalid_numeric,
        "final_rows": len(df)
    }

    return df, stats


## REPORT

def generate_report(spe, wind, spe_stats, wind_stats):
    """
    Generates a data quality report including:
    - percentage of nulls per column
    - cleaning statistics for SPE and Wind datasets

    The report is saved as a JSON file in the reports directory.

    Parameters
    
    spe : Cleaned SPE dataset.
    wind : Cleaned Wind Farm dataset.
    spe_stats : Cleaning metrics for SPE dataset.
    wind_stats : Cleaning metrics for Wind Farm dataset.

    Returns
    
    None
    """

    report = [
        {
            "spe_nulls": null_report(spe).to_dict(),
            "wind_nulls": null_report(wind).to_dict(),
            "spe_stats": spe_stats,
            "wind_stats": wind_stats
        }
    ]

    pd.DataFrame(report).to_json(
        REPORT_PATH / "data_quality_report.json",
        orient="records",
        indent=4
    )

    print("\nData quality report generated successfully.")


## MAIN

def main():
    """
    Executes the full data quality pipeline.

    Returns
    
    None
    """

    spe, wind = load_data()

    spe_clean, spe_stats = clean_spe(spe)
    wind_clean, wind_stats = clean_wind(wind)

    ## SAVE CLEAN DATA
    spe_clean.to_csv(PROCESSED_PATH / "spe_clean.csv", index=False)
    wind_clean.to_csv(PROCESSED_PATH / "wind_farm_clean.csv", index=False)

    print("\nProcessed datasets saved.")

    ## REPORT
    generate_report(spe_clean, wind_clean, spe_stats, wind_stats)


if __name__ == "__main__":
    main()