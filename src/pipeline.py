from src.extract.extract_data import main as extract
from src.load.load_duckdb import load_csvs
from src.transform.transform_duckdb import transform

from src.utils.logger import get_logger

logger = get_logger()


def run_pipeline():
    """
    Executes the complete ELT pipeline.

    Pipeline stages:
    - Extract
    - Load
    - Transform

    Returns

    None
    """

    logger.info("Pipeline started")

    extract()

    load_csvs()

    transform()

    logger.info("Pipeline finished")


if __name__ == "__main__":

    run_pipeline()