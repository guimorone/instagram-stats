import logging
from modules.custom_logger_formatter import CustomLoggerFormatter


def setup_logger(
    name: str, level: int = logging.DEBUG, formatter: logging.Formatter = CustomLoggerFormatter
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter())

    logger.addHandler(ch)

    return logger


def get_runtime_text(start_time: float, end_time: float) -> str:
    full_time = end_time - start_time
    minutes = full_time // 60
    seconds = full_time - (minutes * 60)
    runtime_text = f"{int(seconds)} {'seconds' if seconds > 1 else 'second'}"

    if minutes:
        runtime_text = f"{int(minutes)} {'minutes' if minutes > 1 else 'minute'} and " + runtime_text

    return runtime_text
