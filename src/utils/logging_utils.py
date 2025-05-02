import logging
import os


def setup_file_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Creates a logger that logs to a file. If the default path is not writable
    (like in Lambda), it falls back to /tmp/log_name.log
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
        stream_handler.setLevel(logging.WARNING)  # 🔥 Change this from INFO to WARNING
        logger.addHandler(stream_handler)

    logger.propagate = True
    return logger
