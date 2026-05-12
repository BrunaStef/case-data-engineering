from pathlib import Path
import pandas as pd
from colorama import Fore, Style, init

init(autoreset=True)

## PATHS

RAW_PATH = Path("data/raw")

INTERIM_PATH = Path("data/interim")

WIND_FARM_PATH = RAW_PATH / "wind_farm"

SPE_PATH = RAW_PATH / "spe"


## FUNCTIONS

def read_and_concat_csvs(folder_path: Path):
    """
    Reads and concatenates all CSV files from a folder.

    Parameters

    folder_path : Folder containing the CSV files.

    Returns

    Consolidated DataFrame with all files combined.
    """

    csv_files = sorted(folder_path.glob("*.csv"))

    dataframes = []

    for file in csv_files:

        print(
            f"{Fore.BLUE}Reading file:{Style.RESET_ALL} "
            f"{file.name}"
        )

        df = pd.read_csv(
            file,
            sep=";",
            encoding="utf-8",
            low_memory=False
        )

        ## DATE PARSING

        possible_date_columns = [
            "din_instante",
            "dat_inicio",
            "dat_fim"
        ]

        for column in possible_date_columns:

            if column in df.columns:

                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

        dataframes.append(df)

    ## VALIDATION

    if not dataframes:

        raise ValueError(
            f"No CSV files found in: {folder_path}"
        )

    final_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    return final_df


## MAIN

def main():
    """
    Consolidates monthly CSV files into unified datasets
    and saves them in CSV format.

    Returns

    None
    """

    INTERIM_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    ## WIND FARM DATASET

    wind_farm_df = read_and_concat_csvs(
        WIND_FARM_PATH
    )

    print(
        f"\n{Fore.GREEN}Wind farm consolidated dataset:"
        f"{Style.RESET_ALL}"
    )

    print(wind_farm_df.shape)

    wind_farm_output = INTERIM_PATH / "wind_farm_consolidated.csv"

    wind_farm_df.to_csv(
        wind_farm_output,
        index=False
    )

    print(
        f"{Fore.GREEN}File saved to:{Style.RESET_ALL} "
        f"{wind_farm_output}\n"
    )

    ## SPE DATASET

    spe_df = read_and_concat_csvs(
        SPE_PATH
    )

    print(
        f"\n{Fore.GREEN}SPE consolidated dataset:"
        f"{Style.RESET_ALL}"
    )

    print(spe_df.shape)

    spe_output = INTERIM_PATH / "spe_consolidated.csv"

    spe_df.to_csv(
        spe_output,
        index=False
    )

    print(
        f"{Fore.GREEN}File saved to:{Style.RESET_ALL} "
        f"{spe_output}\n"
    )

    print(
        f"{Fore.GREEN}Data consolidation completed."
        f"{Style.RESET_ALL}"
    )


if __name__ == "__main__":
    main()