from pathlib import Path
import pandas as pd

## PATHS

DATA_PATH = Path("data/processed")
RAW_PATH = Path("data/raw")
OUTPUT_PATH = Path("data/filtered")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


## LOAD DATA

def load_data():
    """
    Loads input datasets.

    Returns:
        spe: cleaned SPE dataset
        wind: cleaned wind farm dataset
        ref: CDV reference mapping
    """

    spe = pd.read_csv(DATA_PATH / "spe_clean.csv")
    wind = pd.read_csv(DATA_PATH / "wind_farm_clean.csv")
    ref = pd.read_csv(RAW_PATH / "spes_casa_dos_ventos.csv")

    return spe, wind, ref

## NORMALIZATION

def normalize(series: pd.Series):
    """
    Normalizes string values for matching.

    Parameters:
        series: input string column

    Returns:
        normalized strings (uppercase, trimmed)
    """

    return (
        series.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
    )

## EXTRACT CEG CORE

def extract_ceg_core(series: pd.Series):
    """
    Extracts CEG core identifier.

    Parameters:
        series: full CEG column

    Returns:
        extracted CEG core 
    """

    return series.str.extract(r"(\d{6,7}-\d)")[0]


## FILTER SPE DATASET

def filter_spe(spe: pd.DataFrame, ref: pd.DataFrame):
    """
    Filters SPE dataset to Casa dos Ventos assets.

    Parameters:
        spe: raw SPE dataset
        ref: Casa dos Ventos reference mapping

    Returns:
        filtered SPE dataset enriched with project info
    """

    spe = spe.copy()
    ref = ref.copy()

    spe["ceg_core"] = extract_ceg_core(spe["ceg"])

    valid_ceg = set(ref["ceg"])

    spe_filtered = spe[spe["ceg_core"].isin(valid_ceg)].copy()

    spe_filtered = spe_filtered.merge(
    ref[["ceg", "projeto"]],
    left_on="ceg_core",
    right_on="ceg",
    how="left"
    )

    spe_filtered.drop(columns=["ceg_y"], inplace=True, errors="ignore")
    spe_filtered.rename(columns={"ceg_x": "ceg"}, inplace=True)
    spe_filtered.drop(columns=["ceg_core"], inplace=True, errors="ignore")

    return spe_filtered


## FILTER WIND FARM DATASET

def filter_wind(wind: pd.DataFrame, spe_filtered: pd.DataFrame):
    """
    Filters wind farm dataset using SPE-derived plant mapping.

    Parameters:
        wind: wind farm dataset
        spe_filtered: filtered SPE dataset

    Returns:
        filtered wind farm dataset
    """

    wind = wind.copy()
    spe_filtered = spe_filtered.copy()

    wind["nom_usina_norm"] = normalize(wind["nom_usina"])
    spe_filtered["nom_conjuntousina_norm"] = normalize(spe_filtered["nom_conjuntousina"])

    valid_conjuntos = set(
        spe_filtered["nom_conjuntousina_norm"].dropna()
    )

    wind_filtered = wind[
        wind["nom_usina_norm"].isin(valid_conjuntos)
    ].copy()

    wind_filtered.drop(columns=["nom_usina_norm"], inplace=True, errors="ignore")
    
    return wind_filtered


## MAIN PIPELINE

def main():
    """
    Executes filtering pipeline.

    """

    spe, wind, ref = load_data()

    spe_filtered = filter_spe(spe, ref)

    wind_filtered = filter_wind(wind, spe_filtered)

    spe_filtered.to_csv(OUTPUT_PATH / "spe_cdv_filtered.csv", index=False)
    wind_filtered.to_csv(OUTPUT_PATH / "wind_cdv_filtered.csv", index=False)

    print("\nFiltering completed successfully")
    print("SPE shape:", spe_filtered.shape)
    print("Wind shape:", wind_filtered.shape)


if __name__ == "__main__":
    main()