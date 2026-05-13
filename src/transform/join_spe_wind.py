from pathlib import Path
import pandas as pd

## PATHS

DATA_PATH = Path("data/filtered")
OUTPUT_PATH = Path("data/processed")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

## LOAD DATA

def load_data():
    """
    Loads SPE and Wind Farm filtered datasets.

    Returns:
        spe (DataFrame), wind (DataFrame)
    """
    spe = pd.read_csv(DATA_PATH / "spe_cdv_filtered.csv")
    wind = pd.read_csv(DATA_PATH / "wind_cdv_filtered.csv")
    return spe, wind

## NORMALIZATION

def normalize(series: pd.Series):
    """
    Standardizes text for safe joins.

    Returns:
        Cleaned string Series (uppercase, trimmed, single spaces)
    """
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
    )

## JOIN

def join_datasets(spe: pd.DataFrame, wind: pd.DataFrame):
    """
    Joins SPE (detail level) with Wind Farm (aggregate level).

    Returns:
        Merged DataFrame
    """

    spe = spe.copy()
    wind = wind.copy()

    ## create join keys
    spe["join_key"] = normalize(spe["nom_conjuntousina"])
    wind["join_key"] = normalize(wind["nom_usina"])

    wind = wind.drop_duplicates(subset=["join_key"])

    wind = wind[
        [
            "join_key",
            "nom_subsistema",
            "nom_estado",
            "val_geracao",
            "val_disponibilidade",
            "val_geracaoreferencia",
            "val_geracaoreferenciafinal",
        ]
    ]

    merged = spe.merge(
        wind,
        on="join_key",
        how="left",
        suffixes=("_spe", "_wind")
    )

    merged.drop(columns=["join_key"], inplace=True)

    return merged


## METRICS

def join_metrics(df: pd.DataFrame):
    """
    Calculates join quality metrics.

    Returns:
        dict with total rows, matched rows and match rate
    """

    total = len(df)

    matched = df["nom_estado"].notna().sum()

    return {
        "total_records": total,
        "matched_records": int(matched),
        "match_rate_%": round((matched / total) * 100, 2)
    }

## MAIN

def main():
    """
    Executes SPE - Wind Farm join pipeline.
    """

    spe, wind = load_data()

    merged = join_datasets(spe, wind)

    metrics = join_metrics(merged)

    print("\nJoin completed successfully")
    print(metrics)
    print("Final shape:", merged.shape)

    merged.to_csv(
        OUTPUT_PATH / "cdv_spe_wind_joined.csv",
        index=False
    )

    print("\nSaved to:", OUTPUT_PATH / "cdv_spe_wind_joined.csv")

if __name__ == "__main__":
    main()