import logging
from pathlib import Path
from datetime import datetime

LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

LOG_FILE = LOG_PATH / f"pipeline_{timestamp}.log"


def get_logger():
    """
    Creates and configures the project logger.

    Returns

    Configured logger instance.
    """

    logger = logging.getLogger("cdv_pipeline")

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler = logging.FileHandler(LOG_FILE)

        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()

        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger