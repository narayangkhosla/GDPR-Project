import logging
import os


# def setup_file_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
#     """
#     Creates and returns a logger that writes to a specified file.

#     Args:
#         name (str): Logger name (usually __name__)
#         log_file (str): Path to the log file
#         level (int): Logging level (default: INFO)

#     Returns:
#         logging.Logger: Configured logger instance
#     """
#     # If logs/ is not writable (like in Lambda), redirect to /tmp/
#     log_file_path = log_file
#     if not os.access(os.path.dirname(log_file), os.W_OK):
#         log_file_path = f"/tmp/{os.path.basename(log_file)}"

#     os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

#     logger = logging.getLogger(name)
#     logger.setLevel(level)

#     if not logger.handlers:
#         # File handler
#         file_handler = logging.FileHandler(log_file)
#         file_formatter = logging.Formatter(
#             "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
#             datefmt="%Y-%m-%d %H:%M:%S",
#         )
#         file_handler.setFormatter(file_formatter)
#         logger.addHandler(file_handler)

#         # Console handler (captured by caplog)
#         stream_handler = logging.StreamHandler()
#         stream_handler.setFormatter(file_formatter)
#         logger.addHandler(stream_handler)

#     # allow propagation, so the log bubbles up to root and gets captured by caplog:
#     logger.propagate = True
#     return logger


def setup_file_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Creates a logger that logs to a file. If the default path is not writable (like in Lambda),
    it falls back to /tmp/log_name.log
    """
    # If logs/ is not writable (like in Lambda), redirect to /tmp/
    if not os.access(os.path.dirname(log_file), os.W_OK):
        log_file = f"/tmp/{os.path.basename(log_file)}"

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    logger.propagate = True
    return logger
