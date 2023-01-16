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
import api.routers.metrics_classification_api as metrics_classification_api
import api.routers.metrics_classifications_api as metrics_classifications_api
import api.routers.account_api as account_api
import api.routers.equities_group_api as equities_group_api
import api.routers.equities_groups_api as equities_groups_api
import api.routers.companies_api as companies_api
import api.routers.company_business_segment_api as company_business_segment_api
import api.routers.metric_description_api as metric_description_api
import api.routers.metric_descriptions_api as metric_descriptions_api
import api.routers.metric_data_api as metric_data_api

import api.security.security as app_security

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from db.models import *

import api.config as api_config
import api.constants as api_constants

tags_metadata = [
    {
        "name": "account",
        "description": "Account operations. Create user, login, etc.",
        "externalDocs": {
            "description": "Account external docs.",
            "url": "https://docs.google.com/document/d/1ea0NFrCMWB91tJq5kPePWPilN0sbtNZlE_DFto3vnDU/edit",
        },
    },
    {
        "name": "companies",
        "description": "Retrieve data for multiple companies based on search parameters for the user.",
    },
    {
        "name": "company",
        "description": "Manage companies.",
        "externalDocs": {
            "description": "Company external docs.",
            "url": "https://docs.google.com/document/d/1ea0NFrCMWB91tJq5kPePWPilN0sbtNZlE_DFto3vnDU/edit",
        },
    },
    {
        "name": "companyBusinessSegment",
        "description": "Manage business segments and retrieve data for individual segments.",
        "externalDocs": {
            "description": "Business segment external docs.",
            "url": "https://docs.google.com/document/d/1ea0NFrCMWB91tJq5kPePWPilN0sbtNZlE_DFto3vnDU/edit",
        },
    },
    {
        "name": "equitiesGroup",
        "description": "Manage company groups and retrieve detailed data for individual groups (segments, metrics, etc.).",
        "externalDocs": {
            "description": "Company group external docs.",
            "url": "https://docs.google.com/document/d/1ea0NFrCMWB91tJq5kPePWPilN0sbtNZlE_DFto3vnDU/edit",
        },
    },
    {
        "name": "equitiesGroups",
        "description": "Retrieve basic info for multiple groups based on search parameters for the user.",
    },
    {
        "name": "industries",
        "description": "Retrieve data for multiple industries based on search parameters.",
    },
    {
        "name": "industry",
        "description": "Manage industries. Limited to system user.",
        "externalDocs": {
            "description": "Industry external docs.",
            "url": "https://docs.google.com/document/d/1ea0NFrCMWB91tJq5kPePWPilN0sbtNZlE_DFto3vnDU/edit",
        },
    },
    {
        "name": "metricData",
        "description": "Manage the actual data related to metrics.",
        "externalDocs": {
            "description": "Metric data external docs.",
            "url": "https://docs.google.com/document/d/1ea0NFrCMWB91tJq5kPePWPilN0sbtNZlE_DFto3vnDU/edit",
        },
    },
    {
        "name": "metricDescription",
        "description": "Manage metrics.",
        "externalDocs": {
            "description": "Metric description external docs.",
            "url": "https://docs.google.com/document/d/1ea0NFrCMWB91tJq5kPePWPilN0sbtNZlE_DFto3vnDU/edit",
        },
    },
    {
        "name": "metricDescriptions",
        "description": "Retrieve metric descriptions. These will be the actual metric descriptions with no data associated."
    },
    {
        "name": "metricsCategory",
        "description": "Manage metric categories.",
        "externalDocs": {
            "description": "Metrics category external docs.",
            "url": "https://docs.google.com/document/d/1ea0NFrCMWB91tJq5kPePWPilN0sbtNZlE_DFto3vnDU/edit",
        },
    },
    {
        "name": "metricsCategories",
        "description": "Retrieve metric categories for a user."
    },
    {
        "name": "sector",
        "description": "Manage sectors. Limited to system user."
    },
    {
        "name": "sectors",
        "description": "Retrieve sectors based on search parameters."
    },
]

description = """
Compare and value companies 🚀

Latest release notes external docs: https://docs.google.com/document/d/1XWxqScJy5BqzkqUcmQThAWnbZBFgyhl0BgawRUhIRC8/edit \n
Latest entities document: https://docs.google.com/document/d/1ea0NFrCMWB91tJq5kPePWPilN0sbtNZlE_DFto3vnDU/edit
"""

app = FastAPI(title='Financial App', version=api_constants.version, openapi_tags=tags_metadata, description=description)

#app.include_router(company_financials_api.router)
app.include_router(company_api.router)
app.include_router(industry_api.router)
app.include_router(industries_api.router)
app.include_router(sector_api.router)
app.include_router(sectors_api.router)
app.include_router(metrics_classification_api.router)
app.include_router(metrics_classifications_api.router)
app.include_router(account_api.router)
app.include_router(equities_group_api.router)
app.include_router(equities_groups_api.router)
app.include_router(companies_api.router)
app.include_router(company_business_segment_api.router)
app.include_router(metric_description_api.router)
app.include_router(metric_descriptions_api.router)
app.include_router(metric_data_api.router)



@app.get("/" + api_constants.app_name + "/version", response_description="The current version of the running application.")
def version():
    return {"version": api_constants.version}

@app.middleware("http")
async def request_handler_common(request: Request, call_next):
    #response = await call_next(request)
    #return response
    try:
        manager = SqlAlchemySessionManager()

        no_validation = False
        
        start_idx = len(request.base_url._url)
        url = request.url._url[start_idx:]
        url_parts = url.split('/')

        if len(url_parts) == 1 and (url_parts[0] == 'docs' or url_parts[0] == 'openapi.json'):
            no_validation = True
        elif len(url_parts) > 1 and ((request.method == 'POST' and url_parts[1] == 'account') or url_parts[1] == 'version'):
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
    
    uvicorn.run("server:app", host="0.0.0.0", port=8080, workers=1)

    print("Initialization done.")

if __name__ == '__main__':
    initialize()
