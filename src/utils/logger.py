from datetime import datetime
import logging
from pathlib import Path

LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

def get_logger(name="pipeline"):
    """
    Creates and configures the project logger.

    Returns

    Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        log_file = (
            LOG_PATH
            / f"{name}_{timestamp}.log"
        )

        file_handler = logging.FileHandler(log_file)

        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()

        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger