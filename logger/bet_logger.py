import logging


def setup_logger(module_name: str):
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')

    file_handler = logging.FileHandler('logger/logs/' + module_name + '.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger