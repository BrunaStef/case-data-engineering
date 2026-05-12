from pathlib import Path
import argparse
import pandas as pd
import requests
from colorama import Fore, Style, init

## SETTINGS

init(autoreset=True)

BASE_URL_WIND_FARM = (
    "https://ons-aws-prod-opendata.s3.amazonaws.com/"
    "dataset/restricao_coff_eolica_tm/"
    "RESTRICAO_COFF_EOLICA_{year}_{month}.csv"
)

BASE_URL_SPE = (
    "https://ons-aws-prod-opendata.s3.amazonaws.com/"
    "dataset/restricao_coff_eolica_detail_tm/"
    "RESTRICAO_COFF_EOLICA_DETAIL_{year}_{month}.csv"
)

RAW_PATH = Path("data/raw")

## FUNCTIONS

def generate_months(start: str, end: str):
    """
    Generates a list of months between two dates.

    Parameters

    start : Start date in YYYY-MM format.
    end : End date in YYYY-MM format.

    Returns
    
    List of tuples containing year and month.
    """

    dates = pd.date_range(
        start=start,
        end=end,
        freq="MS"
    )

    return [(d.year, f"{d.month:02d}") for d in dates]


def download_file(url: str, output_path: Path):
    """
    Downloads a file from a URL and saves it locally.

    Parameters

    url : File URL.

    output_path : Local path to save the file.

    Returns
    
    None
    """

    print(f"{Fore.BLUE}Downloading:{Style.RESET_ALL} {url}")

    try:

        response = requests.get(url)

        if response.status_code == 200:

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with open(output_path, "wb") as file:
                file.write(response.content)

            print(
                f"{Fore.GREEN}File saved to:{Style.RESET_ALL} "
                f"{output_path}\n"
            )

        else:

            print(
                f"{Fore.RED}Error downloading file.{Style.RESET_ALL}"
            )

            print(
                f"{Fore.RED}Status code:{Style.RESET_ALL} "
                f"{response.status_code}\n"
            )

    except Exception as error:

        print(
            f"{Fore.RED}Unexpected error:{Style.RESET_ALL} "
            f"{error}\n"
        )


## MAIN

def main(start: str, end: str):
    """
    Executes the download process for both ONS datasets.

    Parameters

    start : Start date in YYYY-MM format.

    end : End date in YYYY-MM format.

    Returns
    
    None
    """

    months = generate_months(start, end)

    for year, month in months:

        ## WIND FARM DATASET

        wind_farm_url = BASE_URL_WIND_FARM.format(
            year=year,
            month=month
        )

        wind_farm_output = (
            RAW_PATH
            / "wind_farm"
            / f"restricao_coff_wind_farm_{year}_{month}.csv"
        )

        download_file(
            wind_farm_url,
            wind_farm_output
        )

        ## SPE DATASET

        spe_url = BASE_URL_SPE.format(
            year=year,
            month=month
        )

        spe_output = (
            RAW_PATH
            / "spe"
            / f"restricao_coff_spe_{year}_{month}.csv"
        )

        download_file(
            spe_url,
            spe_output
        )


## TERMINAL EXECUTION

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="ONS datasets download"
    )

    parser.add_argument(
        "--start",
        required=True,
        help="Start date in YYYY-MM format"
    )

    parser.add_argument(
        "--end",
        required=True,
        help="End date in YYYY-MM format"
    )

    args = parser.parse_args()

    main(
        start=args.start,
        end=args.end
    )