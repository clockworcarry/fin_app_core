from fastapi import APIRouter, status, HTTPException, File, UploadFile, Query, Response, Request
from typing import Optional, List, Union
from pydantic import BaseModel, JsonError, ValidationError, validator
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *

import core.shared_models as shared_models_core
import core.metrics as core_metrics
import core.metrics_classifications as metrics_classifications_core

import api.config as api_config
import api.constants as api_constants
import core.constants as core_global_constants

import copy


router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/company/businessSegment",
    tags=["companyBusinessSegment"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("/{bs_id}", status_code=status.HTTP_200_OK, response_model=shared_models_core.BusinessSegmentModel)
def get_company_business_segment(bs_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            metric_categories = metrics_classifications_core.get_user_metric_categories(request.state.rctx.user_id, session)

            db_rows = session.query(CompanyBusinessSegment, MetricData, MetricDescription, Company) \
                             .join(MetricData, MetricData.company_business_segment_id == CompanyBusinessSegment.id) \
                             .join(MetricDescription, MetricDescription.id == MetricData.metric_description_id) \
                             .join(Company, Company.id == CompanyBusinessSegment.company_id) \
                             .filter(CompanyBusinessSegment.id == bs_id) \
                             .all()
            
            if len(db_rows) == 0:
                raise Exception("Failed to load any business segment for id: " + bs_id)
            
            ret = shared_models_core.BusinessSegmentModel.from_orm(db_rows[0][0])
            ret.company_name = db_rows[0][3].name
            ret.company_ticker = db_rows[0][3].ticker
            ret.metric_categories = copy.deepcopy(metric_categories)
            for bs, mdata, mdesc, c in db_rows:
                metric_desc_model = shared_models_core.MetricDescriptionModel.from_orm(mdesc)
                metric_desc_model.metric_classification_id = mdesc.metric_classification_id
                metric_data_model = shared_models_core.MetricDataModel(data=mdata.data, description=metric_desc_model)
                metric_data_model._user_id = mdata.user_id

                core_metrics.add_metric_to_business_segment(ret, metric_desc_model, metric_data_model, request.state.rctx.user_id)
            
            ret.metric_categories = metrics_classifications_core.group_metric_categories_model(ret.metric_categories, None)
            #remove categories with no metrics or sub categories
            metrics_classifications_core.remove_empty_categories(ret.metric_categories)

            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def create_company_business_segment(request: Request, body: shared_models_core.BusinessSegmentModelShort):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_bs = session.query(CompanyBusinessSegment).filter(CompanyBusinessSegment.code == body.code).first()
            if db_bs is not None:
                raise Exception("A business segment with code: " + body.code + " already exists.")
            
            session.add(CompanyBusinessSegment(company_id=body.company_id, code=body.code, display_name=body.display_name, creator_id=request.state.rctx.user_id))

            return Response(status_code=HTTP_201_CREATED)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{bs_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_company_business_segment(bs_id, request: Request, body: shared_models_core.BusinessSegmentModelShort):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_bs = session.query(CompanyBusinessSegment).filter(CompanyBusinessSegment.id == bs_id).first()
            if db_bs is None:
                raise HTTPException(status_code=500, detail="No company business segment with id: " + bs_id + " exists.")
            
            db_bs.code = body.code
            db_bs.display_name = body.display_name

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/{bs_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_business_segment(bs_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_bs = session.query(CompanyBusinessSegment).filter(CompanyBusinessSegment.id == bs_id).first()
            if db_bs is None:
                raise HTTPException(status_code=500, detail="No company business segment with id: " + bs_id + " exists.")
            
            session.delete(db_bs)

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))