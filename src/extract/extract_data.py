from pathlib import Path
import pandas as pd
import requests
import time

from config.settings import (
    START_DATE,
    END_DATE,
    RAW_PATH
)

from src.utils.logger import get_logger

logger = get_logger()


BASE_URL_WIND = (
    "https://ons-aws-prod-opendata.s3.amazonaws.com/"
    "dataset/restricao_coff_eolica_tm/"
    "RESTRICAO_COFF_EOLICA_{year}_{month}.csv"
)

BASE_URL_SPE = (
    "https://ons-aws-prod-opendata.s3.amazonaws.com/"
    "dataset/restricao_coff_eolica_detail_tm/"
    "RESTRICAO_COFF_EOLICA_DETAIL_{year}_{month}.csv"
)


def generate_months(start, end):
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


def download_with_retry(url, output_path, retries=3):
    """
    Downloads a file with retry support.

    Parameters

    url : File URL.
    output_path : Local path to save the file.
    retries : Number of retry attempts.

    Returns

    None
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if output_path.exists():

        logger.info(f"File already exists: {output_path}")

        return

    for attempt in range(retries):

        try:

            logger.info(f"Downloading: {url}")

            response = requests.get(url, timeout=30)

            if response.status_code == 200:

                with open(output_path, "wb") as file:
                    file.write(response.content)

                logger.info(f"Saved: {output_path}")

                return

            else:

                logger.warning(
                    f"Unavailable file: {url}"
                )

                return

        except Exception as error:

            logger.error(
                f"Attempt {attempt+1} failed: {error}"
            )

            time.sleep(2)

    logger.error(f"Failed download after retries: {url}")


def main():
    """
    Executes the extraction process for both ONS datasets.

    Returns

    None
    """

    months = generate_months(
        START_DATE,
        END_DATE
    )

    for year, month in months:

        wind_url = BASE_URL_WIND.format(
            year=year,
            month=month
        )

        wind_output = (
            RAW_PATH
            / "wind_farm"
            / f"restricao_coff_wind_farm_{year}_{month}.csv"
        )

        download_with_retry(
            wind_url,
            wind_output
        )

        spe_url = BASE_URL_SPE.format(
            year=year,
            month=month
        )

        spe_output = (
            RAW_PATH
            / "spe"
            / f"restricao_coff_spe_{year}_{month}.csv"
        )

        download_with_retry(
            spe_url,
            spe_output
        )


if __name__ == "__main__":

    main()