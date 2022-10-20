from fastapi import APIRouter, status, HTTPException, File, UploadFile, Query as FQuery, Response, Request
from typing import Optional, List, Union
from pydantic import BaseModel, ValidationError, validator
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK, HTTP_501_NOT_IMPLEMENTED

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *

import core.shared_models as shared_models_core

import api.config as api_config
import api.constants as api_constants
import core.constants as core_global_constants

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/companies",
    tags=["companies"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

"""/" + api_constants.app_name + "/" + api_constants.version + "/companies/"

Raises:
    HTTPException: _description_
    HTTPException: _description_

Returns:
    List[shared_models_core.CompanyBusinessSegmentsModel]: All the companies that match the provided parameters. If a sector id is provided, this api
    will return all the companies that have >= 1 business segments associated to it that are part of this sector.
    Same for an industry id.
    """
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[shared_models_core.CompanyBusinessSegmentsShortModel])
def get_companies(request: Request, sector_id: Union[List[int], None]=FQuery(default=None), industry_id: Union[List[int], None]=FQuery(default=None)):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            query = session.query(Company, CompanyBusinessSegment)    
            query = query.join(CompanyBusinessSegment, CompanyBusinessSegment.company_id == Company.id)
            if sector_id is not None:
                query = query.join(CompanySectorRelation, CompanySectorRelation.company_business_segment_id == CompanyBusinessSegment.id)
            if industry_id is not None:
                query = query.join(CompanyIndustryRelation, CompanyIndustryRelation.company_business_segment_id == CompanyBusinessSegment.id)
            if sector_id is not None:
                query = query.filter(CompanySectorRelation.sector_id.in_(sector_id))
            if industry_id is not None:
                query = query.filter(CompanyIndustryRelation.industry_id.in_(industry_id))
            
            query = query.filter(or_(Company.creator_id == core_global_constants.system_user_id, Company.creator_id == request.state.rctx.user_id))
            
            db_rows = query.all()
            
            ret = []
            for dc, bs in db_rows:
                cpny = None
                for oc in ret:
                    if oc.company_info.ticker == dc.ticker:
                        cpny = oc
                        break
                
                if cpny is None:
                    cpny_info = shared_models_core.CompanyModel(id=dc.id, ticker=dc.ticker, name=dc.name, delisted=dc.delisted, creator_id=dc.creator_id)
                    cpny = shared_models_core.CompanyBusinessSegmentsShortModel(company_info=cpny_info, business_segments = [])
                    ret.append(cpny)
                
                obs = shared_models_core.BusinessSegmentModelShort.from_orm(bs)
                cpny.business_segments.append(obs)

            
            return ret



    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/watchList/{watchlist_id}", status_code=status.HTTP_200_OK, response_model=List[shared_models_core.CompanyModel])
def get_companies(watchlist_id):
    return Response(content="Not implemented", status_code=HTTP_501_NOT_IMPLEMENTED)