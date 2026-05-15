from src.extract.extract_data import main as extract
from src.load.load_duckdb import load_csvs

from src.transform.transform_duckdb import transform
from src.transform.quality_report import generate_quality_report
from src.transform.filter_cdv_duckdb import filter_cdv
from src.transform.join_data import join_datasets
from src.transform.export_parquet import export_parquet

from src.utils.logger import get_logger

logger = get_logger("pipeline")

def run_pipeline():
    """
    Executes the complete ELT pipeline.

    Returns

    None
    """

    logger.info("Pipeline started")

    extract()

    load_csvs()

    transform()

    generate_quality_report()

    filter_cdv()

    join_datasets()

    export_parquet()

    logger.info("Pipeline finished")


if __name__ == "__main__":

    run_pipeline()
