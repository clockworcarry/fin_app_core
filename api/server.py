from itsdangerous import SignatureExpired
from jwt import ExpiredSignatureError
import uvicorn, argparse, json

from fastapi import Depends, FastAPI
from fastapi import APIRouter, status, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, validator

from api.config import init_config

import api.routers.company_api as company_api
import api.routers.company_financials_api as company_financials_api
import api.routers.industry_api as industry_api
import api.routers.industries_api as industries_api
import api.routers.sector_api as sector_api
import api.routers.sectors_api as sectors_api
import api.routers.metrics_classifications_api as metrics_classifications_api
import api.routers.account_api as account_api
import api.routers.equities_group_api as equities_group_api
import api.routers.equities_groups_api as equities_groups_api
import api.routers.companies_api as companies_api
import api.routers.company_business_segment_api as company_business_segment_api

import api.security.security as app_security

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from db.models import *

import api.config as api_config

app = FastAPI()

app.include_router(company_financials_api.router)
app.include_router(company_api.router)
app.include_router(industry_api.router)
app.include_router(industries_api.router)
app.include_router(sector_api.router)
app.include_router(sectors_api.router)
app.include_router(metrics_classifications_api.router)
app.include_router(account_api.router)
app.include_router(equities_group_api.router)
app.include_router(equities_groups_api.router)
app.include_router(companies_api.router)
app.include_router(company_business_segment_api.router)



@app.get("/version")
def version():
    return {"version": "0.0.1"}

@app.middleware("http")
async def request_handler_common(request: Request, call_next):
    try:
        manager = SqlAlchemySessionManager()
        
        no_validation = False
        if request.method == 'POST' and 'account' in request.url.path:
            no_validation = True
        
        if not no_validation:
            with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
                rctx = app_security.authenticate_request(request, session)
                request.state.rctx = rctx

        response = await call_next(request)
        return response

    except ExpiredSignatureError as sign_ex:
        return JSONResponse(status_code=401, content={'details': str(sign_ex)})
    except Exception as gen_ex:
        return JSONResponse(status_code=500, content={'details': str(gen_ex)})


def initialize():

    print("Initializing...")
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
    
    uvicorn.run("server:app", host="0.0.0.0", port=8000, workers=1)

    print("Initialization done.")

if __name__ == '__main__':
    initialize()
