import uvicorn, argparse, json

from fastapi import Depends, FastAPI

from api.config import init_config

import api.routers.company_api as company_api
import api.routers.company_metric_api as company_metric_api
import api.routers.company_metrics_api as company_metrics_api
import api.routers.company_financials_api as company_financials_api
import api.routers.industry_api as industry_api
import api.routers.industries_api as industries_api
import api.routers.sector_api as sector_api
import api.routers.sectors_api as sectors_api
import api.routers.company_metrics_classifications_api as company_metrics_classifications_api


app = FastAPI()

app.include_router(company_metric_api.router)
app.include_router(company_metrics_api.router)
app.include_router(company_financials_api.router)
app.include_router(company_api.router)
app.include_router(industry_api.router)
app.include_router(industries_api.router)
app.include_router(sector_api.router)
app.include_router(sectors_api.router)
app.include_router(company_metrics_classifications_api.router)



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