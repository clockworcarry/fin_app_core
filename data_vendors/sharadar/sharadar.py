from data_vendors.vendor import Vendor

import pandas as pd

import requests, io, os, sys, json

class Sharadar(Vendor):
    config = {}

    def __init__(self, config_location):
        try:
            aboslute_path = os.path.join(sys.path[0], config_location)
            with open(aboslute_path, 'r') as f:            
                config_raw = f.read()
                Sharadar.config = json.loads(config_raw)
        except FileNotFoundError as file_err:
            raise file_err
        except Exception as gen_ex:
            raise gen_ex
    
    def get_all_companies(self, **kwargs):
        try:
            full_url = Sharadar.config['domainUrl'] + "/" + Sharadar.config['apiVersion'] + "/" + Sharadar.config['baseUrlExtension'] + "/" + Sharadar.config['tickerTableUrlExtension'] + "&" + "api_key=" + Sharadar.config['apiKey'] + "&qopts.export=true"
            
            r = requests.get(full_url)
            
            if r.status_code == 200:
                r = r.json()
                zip_url = r['datatable_bulk_download']['file']['link']
                zip_req = requests.get(zip_url, stream=True)
                if zip_req.status_code == 200:
                    df = pd.read_csv(io.BytesIO(zip_req.content), compression='zip')
                    return df[['ticker']['name']['exchange']['isdelisted']['famaindustry']['sector']['industry']]
                    return df
                else:
                    raise Exception("Sharadar returned http " + str(r.status_code) + " for method get_all_companies while trying to get zip data.")
            else:
                raise Exception("Sharadar returned http " + str(r.status_code) + " for method get_all_companies while trying to get zip link.")
        except KeyError as key_err:
            raise key_err
        except ValueError as val_err:
            raise val_err
        except Exception as gen_ex:
            raise gen_ex

if __name__ == "__main__":
    sharadar = Sharadar('sharadar_config.json')
    df = sharadar.get_all_companies()
    df.to_csv('test.csv')