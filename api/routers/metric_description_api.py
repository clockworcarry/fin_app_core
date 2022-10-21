from fastapi import APIRouter, status, HTTPException, File, UploadFile, Query, Response, Request
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
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/metric/description",
    tags=["metricDescription"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_metric_description(request: Request, body: shared_models_core.MetricDescriptionModel):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            metric_desc = MetricDescription(code=body.code, display_name=body.display_name, metric_data_type=body.metric_data_type, metric_duration_type=body.metric_duration_type, \
                                            year_recorded=body.year_recorded, quarter_recorded=body.quarter_recorded, metric_duration=body.metric_duration, look_back=body.look_back, \
                                            metric_fixed_year=body.metric_fixed_year, metric_fixed_quarter=body.metric_fixed_quarter, metric_classification_id=body.metric_classification_id, \
                                            creator_id=request.state.rctx.user_id)

            session.add(metric_desc)
            session.flush()
            session.add(UserMetricDescription(metric_description_id=metric_desc.id, account_id=request.state.rctx.user_id))
        
        return Response(status_code=HTTP_201_CREATED)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.put("/{desc_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_metric_description(desc_id, body: shared_models_core.MetricDescriptionModel):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_desc = session.query(MetricDescription).filter(MetricDescription.id == desc_id).first()
            if db_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + desc_id + " exists.")
            
            db_desc.code = body.code
            db_desc.display_name = body.display_name
            db_desc.metric_data_type = body.metric_data_type
            db_desc.metric_duration_type = body.metric_duration_type
            db_desc.year_recorded = body.year_recorded
            db_desc.quarter_recorded = body.quarter_recorded
            db_desc.metric_duration = body.metric_duration
            db_desc.look_back = body.look_back
            db_desc.metric_fixed_year = body.metric_fixed_year
            db_desc.metric_fixed_quarter = body.metric_fixed_quarter
            db_desc.metric_classification_id = body.metric_classification_id

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{desc_id}/{toolbox_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_metric_description_to_toolbox(desc_id, body: shared_models_core.MetricDescriptionModel):
    return Response(content="Not implemented", status_code=HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{desc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metric_description(desc_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_desc = session.query(MetricDescription).filter(MetricDescription.id == desc_id).first()
            if db_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + desc_id + " exists.")
            
            session.delete(db_desc)

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

        