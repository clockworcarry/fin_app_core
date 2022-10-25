from urllib import response
from fastapi import APIRouter, status, HTTPException, File, UploadFile, Query, Response, Request
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
import api.shared_models as api_shared_models


router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/company",
    tags=["company"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("/{search_key}", status_code=status.HTTP_200_OK, response_model=shared_models_core.CompanyBusinessSegmentsShortModel, summary="Get the basic info for a company.",
            response_description="Basic info of the company.")
def get_company(search_key, ticker: Union[bool, None]=False):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_rows = None
            if ticker is None or ticker is False:
                db_rows = session.query(Company, CompanyBusinessSegment).join(CompanyBusinessSegment, CompanyBusinessSegment.company_id == Company.id).filter(Company.id == search_key).all()
            else:
               db_rows = session.query(Company, CompanyBusinessSegment).join(CompanyBusinessSegment, CompanyBusinessSegment.company_id == Company.id).filter(Company.ticker == search_key).all() 
            
            if len(db_rows) == 0:
                raise Exception("Failed to load any company for search key: " + search_key)
            
            cpny_info = shared_models_core.CompanyModel.from_orm(db_rows[0][0])
            ret = shared_models_core.CompanyBusinessSegmentsShortModel(company_info=cpny_info, business_segments=[])
            for dc, dcbs in db_rows:
                ret.business_segments.append(shared_models_core.BusinessSegmentModelShort.from_orm(dcbs))
            
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.post("", status_code=status.HTTP_201_CREATED, tags=["company"], response_model=api_shared_models.ResourceCreationBasicModel, summary="Create a company with the basic info.", 
             description="A company will be created, but it will only contain the basic info. No business segments will be associated to it yet.",
             response_description="The id of the created company.")
def create_company(request: Request, company_body: shared_models_core.CompanyModel):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            company = Company(ticker=company_body.ticker, name=company_body.name, delisted=company_body.delisted, creator_id=request.state.rctx.user_id)
            session.add(company)
            session.flush()
            #todo: create default bus segment
            session.add(CompanyBusinessSegment(company_id=company.id, code=company.ticker + '.default', display_name=company.ticker + ' default business segment', creator_id=request.state.rctx.user_id))
        
        return api_shared_models.ResourceCreationBasicModel(id=company.id)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.put("/{company_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Update the company's basic info.",
            description="Only updates the company's basic info. To update the underlying business segments or the metric related to the company, use the proper apis.")
def update_company(company_id, company_body: shared_models_core.CompanyModel):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_company = session.query(Company).filter(Company.id == company_id).first()
            if db_company is None:
                raise HTTPException(status_code=500, detail="No company with id: " + company_id + " exists.")
            
            db_company.ticker = company_body.ticker
            db_company.name = company_body.name
            db_company.delisted = company_body.delisted
            db_company.creator_i= company_body.creator_id

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete the company.", 
                description="This will also delete all the entities that are dependent on this company. Refer to the erd.")
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