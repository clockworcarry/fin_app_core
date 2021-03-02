import uvicorn, argparse, json

from fastapi import Depends, FastAPI

from config import init_config

import api.routers.company_metric_api as company_metric_api

app = FastAPI()

app.include_router(company_metric_api.router)

@app.get("/version")
async def root():
    return {"version": "0.0.1"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Financial app http server')
    parser.add_argument('-c','--config_file_path', help='Absolute config file path', required=True)
    args = vars(parser.parse_args())

    try:
        with open(args['config_file_path'], 'r') as f:
            file_content_raw = f.read()
            config_json_content = json.loads(file_content_raw)
            init_config(config_json_content)
            

    except Exception as gen_ex:
        print(str(gen_ex))
    
    uvicorn.run(app, host="0.0.0.0", port=8000)