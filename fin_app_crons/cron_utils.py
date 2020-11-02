import logging
from datetime import datetime
import os

def init_logger(file_path, level):
    tokens = file_path.split("/")
    for idx, tok in enumerate(tokens):
        if idx > 0:
            
        if not os.path.exists(c):
            os.makedirs(config_json_content["logFolderPath"])

    root_logger= logging.getLogger()
    root_logger.setLevel(level)
    date_now = datetime.now()
    date_now_format_str = date_now.strftime("%Y_%m_%d") + ".log"
    if not os.path.exists(config_json_content["logFolderPath"]):
        os.makedirs(config_json_content["logFolderPath"])
    handler = logging.FileHandler(config_json_content["logFolderPath"] + "/" + date_now_format_str, "a", "utf-8")
    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
