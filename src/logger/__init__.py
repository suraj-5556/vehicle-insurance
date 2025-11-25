import logging
from logging.handlers import RotatingFileHandler
from from_root import from_root
import os
from datetime import datetime

dir_name = "logs"
dir_path = os.path.join(from_root(),dir_name)
os.makedirs(dir_path,exist_ok=True)
log_file = f"{datetime.now().strftime('%m_%d_%y_%H_%M')}.log"
file_path = os.path.join(dir_path,log_file)
max_log_size = 1024* 1024* 5
backup = 3

def config_logger():
    """
    this build console and file handler of logging module
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(file_path, maxBytes=max_log_size, backupCount=backup)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(filename)s_%(lineno)d_%(message)s")

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

config_logger()