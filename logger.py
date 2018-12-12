import logging


def create_logger(log_name):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARN)
    fh = logging.FileHandler(log_name, mode='w')
    fh.setLevel(logging.WARN)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
