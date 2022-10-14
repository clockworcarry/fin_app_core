from fastapi import APIRouter, status, HTTPException, File, UploadFile, Query, Response
from typing import Optional, List, Union
from pydantic import BaseModel, ValidationError, validator
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *

import core.shared_models as shared_models_core


import api.config as api_config
import api.constants as api_constants
import core.constants as core_global_constants


router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/company",
    tags=["company"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("/{search_key}", status_code=status.HTTP_200_OK, response_model=shared_models_core.CompanyModel)
def get_company(search_key, ticker: Union[bool, None]=False):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_company = None
            if ticker is None or ticker is False:
                db_company = session.query(Company).filter(Company.id == search_key).first()
            else:
               db_company = session.query(Company).filter(Company.ticker == search_key).first() 
            
            if db_company is None:
                raise HTTPException(status_code=500, detail="Could not load company with parameter: " + search_key)

            return shared_models_core.CompanyModel(id=db_company.id, ticker=db_company.ticker, name=db_company.name, delisted=db_company.delisted, creator_id=db_company.creator_id)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_company(company_body: shared_models_core.CompanyModel):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            company = Company(ticker=company_body.ticker, name=company_body.name, delisted=company_body.delisted, creator_id=company_body.creator_id)
            session.add(company)
        
        return Response(status_code=HTTP_201_CREATED)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


router.put("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_company(company_id, company_body: shared_models_core.CompanyModel):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_company = session.query(Company).filter(Company.id == company_id).first()
            if db_company is None:
                raise HTTPException(status_code=500, detail="No company with id: " + company_id + " exists.")
            
            db_company = Company(ticker=company_body.ticker, name=company_body.name, delisted=company_body.delisted, creator_id=company_body.creator_id)

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_company = session.query(Company).filter(Company.id == company_id).first()
            if db_company is None:
                raise HTTPException(status_code=500, detail="No company with id: " + company_id + " exists.")
            
            session.delete(db_company)

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))