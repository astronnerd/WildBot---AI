import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    rfh = RotatingFileHandler("wildlife_rag.log", maxBytes=5242880, backupCount=5)  # 5 MB
    rfh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    rfh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(rfh)
    logger.addHandler(ch)

    return logger