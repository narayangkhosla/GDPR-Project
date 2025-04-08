import logging
import os


def setup_file_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Creates and returns a logger that writes to a specified file.

    Args:
        name (str): Logger name (usually __name__)
        log_file (str): Path to the log file
        level (int): Logging level (default: INFO)

    Returns:
        logging.Logger: Configured logger instance
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler (captured by caplog)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(file_formatter)
        logger.addHandler(stream_handler)

    # allow propagation, so the log bubbles up to root and gets captured by caplog:
    logger.propagate = True
    return logger
