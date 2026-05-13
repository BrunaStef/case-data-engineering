from pathlib import Path
import pandas as pd

## PATHS

DATA_PATH = Path("data/processed")
OUTPUT_PATH = Path("data/final_parquet")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


## LOAD DATA

def load_data():
    """
    Loads joined dataset.

    Returns
    DataFrame
    """

    return pd.read_csv(
        DATA_PATH / "cdv_spe_wind_joined.csv"
    )


## PREPARE PARTITIONS

def prepare_partitions(df: pd.DataFrame):
    """
    Creates year and month partition columns.

    Parameters 
    DataFrame

    Returns
    DataFrame
    """

    df = df.copy()

    df["din_instante"] = pd.to_datetime(
        df["din_instante"],
        errors="coerce"
    )

    df["year"] = df["din_instante"].dt.year
    df["month"] = df["din_instante"].dt.month

    return df


## SAVE PARQUET

def save_parquet(df: pd.DataFrame):
    """
    Saves dataset in partitioned Parquet format.

    Parameters
    DataFrame

    Returns
    None
    """

    df.to_parquet(
        OUTPUT_PATH,
        engine="pyarrow",
        partition_cols=["year", "month"],
        index=False
    )


## MAIN

def main():
    """
    Executes Parquet persistence pipeline.
    """

    df = load_data()

    df = prepare_partitions(df)

    save_parquet(df)

    print("\nParquet dataset saved successfully.")
    print("Output:", OUTPUT_PATH)


if __name__ == "__main__":
    main()