from pathlib import Path
import pandas as pd

## PATHS

DATA_PATH = Path("data/processed")
OUTPUT_DIM = Path("data/warehouse/dimensions")
OUTPUT_FACT = Path("data/warehouse/facts")

OUTPUT_DIM.mkdir(parents=True, exist_ok=True)
OUTPUT_FACT.mkdir(parents=True, exist_ok=True)

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


## DIMENSION - SPE

def create_dim_spe(df: pd.DataFrame):
    """
    Creates SPE dimension.

    Parameters
    df (DataFrame)

    Returns
    DataFrame
    """

    dim_spe = df[
        [
            "nom_usina",
            "id_ons",
            "ceg",
            "projeto",
            "nom_modalidadeoperacao"
        ]
    ].drop_duplicates().reset_index(drop=True)

    dim_spe["spe_key"] = dim_spe.index + 1

    return dim_spe


## DIMENSION - CONJUNTO

def create_dim_conjunto(df: pd.DataFrame):
    """
    Creates conjunto dimension.

    Parameters
    df (DataFrame)

    Returns
    DataFrame
    """

    dim_conjunto = df[
        [
            "nom_conjuntousina",
            "id_subsistema",
            "nom_subsistema",
            "id_estado",
            "nom_estado"
        ]
    ].drop_duplicates().reset_index(drop=True)

    dim_conjunto["conjunto_key"] = (
        dim_conjunto.index + 1
    )

    return dim_conjunto


## DIMENSION - TEMPO

def create_dim_tempo(df: pd.DataFrame):
    """
    Creates time dimension.

    Parameters
    df (DataFrame)

    Returns
    DataFrame
    """

    tempo = pd.DataFrame()

    tempo["din_instante"] = pd.to_datetime(
        df["din_instante"]
    )

    tempo = tempo.drop_duplicates().reset_index(drop=True)

    tempo["tempo_key"] = tempo.index + 1

    tempo["ano"] = tempo["din_instante"].dt.year
    tempo["mes"] = tempo["din_instante"].dt.month
    tempo["dia"] = tempo["din_instante"].dt.day
    tempo["hora"] = tempo["din_instante"].dt.hour

    return tempo


## FACT TABLE

def create_fact_table(
    df,
    dim_spe,
    dim_conjunto,
    dim_tempo
):
    """
    Creates fact table.

    Parameters:
    df (DataFrame)
    dim_spe (DataFrame)
    dim_conjunto (DataFrame)
    dim_tempo (DataFrame)

    Returns:
    DataFrame
    """

    fact = df.copy()

    ## SPE KEY

    fact = fact.merge(
        dim_spe[
            [
                "spe_key",
                "nom_usina",
                "id_ons",
                "ceg"
            ]
        ],
        on=[
            "nom_usina",
            "id_ons",
            "ceg"
        ],
        how="left"
    )

    ## CONJUNTO KEY

    fact = fact.merge(
        dim_conjunto[
            [
                "conjunto_key",
                "nom_conjuntousina"
            ]
        ],
        on="nom_conjuntousina",
        how="left"
    )

    ## TEMPO KEY

    fact["din_instante"] = pd.to_datetime(
        fact["din_instante"]
    )

    fact = fact.merge(
        dim_tempo[
            [
                "tempo_key",
                "din_instante"
            ]
        ],
        on="din_instante",
        how="left"
    )

    ## FINAL FACT

    fact = fact[
        [
            "spe_key",
            "conjunto_key",
            "tempo_key",
            "val_ventoverificado",
            "val_geracaoestimada",
            "val_geracaoverificada",
            "val_geracao",
            "val_disponibilidade",
            "val_geracaoreferencia",
            "val_geracaoreferenciafinal"
        ]
    ]

    return fact


## SAVE TABLES

def save_tables(
    dim_spe,
    dim_conjunto,
    dim_tempo,
    fact
):
    """
    Saves dimensions and fact tables.

    Returns:
    None
    """

    dim_spe.to_parquet(
        OUTPUT_DIM / "dim_spe.parquet",
        index=False
    )

    dim_conjunto.to_parquet(
        OUTPUT_DIM / "dim_conjunto.parquet",
        index=False
    )

    dim_tempo.to_parquet(
        OUTPUT_DIM / "dim_tempo.parquet",
        index=False
    )

    fact.to_parquet(
        OUTPUT_FACT / "fact_generation.parquet",
        index=False
    )


## MAIN

def main():
    """
    Executes star schema creation.
    """

    df = load_data()

    dim_spe = create_dim_spe(df)

    dim_conjunto = create_dim_conjunto(df)

    dim_tempo = create_dim_tempo(df)

    fact = create_fact_table(
        df,
        dim_spe,
        dim_conjunto,
        dim_tempo
    )

    save_tables(
        dim_spe,
        dim_conjunto,
        dim_tempo,
        fact
    )

    print("\nStar schema created successfully.")


if __name__ == "__main__":
    main()