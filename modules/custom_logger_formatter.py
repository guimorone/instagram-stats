import logging
from utils.constants import *


class CustomLoggerFormatter(logging.Formatter):
    format = "%(asctime)s - (%(filename)s:%(lineno)d) - %(levelname)s : %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + format + RESET,
        logging.INFO: BLUE + format + RESET,
        logging.WARNING: YELLOW + format + RESET,
        logging.ERROR: RED + format + RESET,
        logging.CRITICAL: BOLD_RED + format + RESET,
    }

    def format(self, record) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)
