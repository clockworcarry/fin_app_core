import sys
import json
import requests
import pandas as pd
import logging
from datetime import datetime
import os
from pathlib import Path
from io import StringIO
from sqlalchemy import create_engine, select, insert
from db_models.models import t_company
#import Fin_App_Core_Db_Models.Models

print(sys.path)
sys.path.insert(1, '/path/to/application/app/folder')

script_location = Path(__file__).absolute().parent
print(script_location)
fundamentals_config_location = script_location / "fundamentals_import_config.json"

try:
    config_json_content = {}
    
    with open(fundamentals_config_location, "r") as f:
        file_content_raw = f.read()
        config_json_content = json.loads(file_content_raw)

        root_logger= logging.getLogger()
        root_logger.setLevel(logging.CRITICAL)
        date_now = datetime.now()
        date_now_format_str = date_now.strftime("%Y_%m_%d") + ".log"
        log_folder_path_relative = script_location / config_json_content["logFolderPath"]
        if not os.path.exists(log_folder_path_relative):
            os.makedirs(log_folder_path_relative)
        handler = logging.FileHandler(log_folder_path_relative / date_now_format_str, "a", "utf-8")
        formatter = logging.Formatter("%(asctime)s %(message)s")
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    
    for src in config_json_content["sources"]:
        filtered_out_it = next((x for x in config_json_content["sourcesFilteredOut"] if x == src["vendor"]), None)
        if filtered_out_it != None:
            filtered_in_it = next((x for x in config_json_content["sourcesFilteredIn"] if x == src["vendor"]), None)
            if filtered_in_it == None:
                continue
        
        if src["importCompanies"]:
            url = src["base_url"] + src["companies_import_params"]["endpoint"] + "." + src["companies_import_params"]["format"] + "?"
            for query_param in src["companies_import_params"]["params"]:
                url += query_param["key"] + "=" + query_param["value"] + "&"
            url += "api_key" + "=" + src["apiKey"]
        
        r = requests.get(url)
        if r.status_code != 200:
            logging.critical("Vendor %s returned http %s while trying to import companies.", src["vendor"], r.status_code)

        engine = create_engine("postgresql://postgres:navo1234@localhost:5432/Fin_App_Core_Db", echo=True)
        conn = engine.connect()
        supported_exchanges = select([exchange])
        df = pd.read_csv(StringIO(r.text))
        for idx, row in df.iterrows():
            pass
        
        
except FileNotFoundError as file_err:
    logging.critical(str(file_err))
except KeyError as key_err:
    logging.critical("Key does not exist in dict: " + str(key_err))
except OSError as os_err:
    logging.critical("Os error caught: " + str(os_err))
except Exception as gen_ex:
    logging.critical("Generic exception caught: " + str(gen_ex))


