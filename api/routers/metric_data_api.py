from tokenize import Number
from fastapi import APIRouter, status, HTTPException, File, UploadFile, Query, Response, Request
from typing import Optional, List, Union
from pydantic import BaseModel, ValidationError, validator
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK, HTTP_501_NOT_IMPLEMENTED

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *

from fastapi.responses import JSONResponse

import core.shared_models as shared_models_core


import api.config as api_config
import api.constants as api_constants
import core.constants as core_global_constants
import api.shared_models as api_shared_models


router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/metric/data",
    tags=["metricData"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class MetricDataSaveModelIn(BaseModel):
    metric_description_id: int
    business_segment_id: int
    data: float

class MetricDataUpdateModelIn(BaseModel):
    data: float


@router.post("", status_code=status.HTTP_201_CREATED, response_model=api_shared_models.ResourceCreationBasicModel, summary="Associate actual metric data to a metric.",
            description="The data for a metric is business AND user specific. A metric description only describes the metrics, but the data for the metric will differ by business. A user \
                         can also override data for a metric for his own if he wants. Only he will see his version of the data.", response_description="The id of the created metric data entity.")
def associate_data_to_metric_description(request: Request, body: MetricDataSaveModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            metric_data = MetricData(metric_description_id=body.metric_description_id, company_business_segment_id=body.business_segment_id, data=body.data, user_id = request.state.rctx.user_id)
            session.add(metric_data)
            session.flush()
                   
            return api_shared_models.ResourceCreationBasicModel(id=metric_data.id)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.put("/{data_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Update the actual metric data for a metric.", 
            description="Update data associated to a metric only for this user. If the user is system, will impact all users who use this data.")
def update_metric_data(data_id, body: MetricDataSaveModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_data = session.query(MetricData).filter(MetricData.id == data_id).first()
            if db_data is None:
                raise Exception("No metric data with id: " + data_id + " exists.")
            
            db_data.data = body.data

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.delete("/{data_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete the actual metric data for a metric.", 
                description="Delete the data associated to a metric only for this user. If the user is system, will impact all users who use this data.")
def delete_metric_data(data_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_data = session.query(MetricData).filter(MetricData.id == data_id).first()
            if db_data is None:
                raise Exception("No metric data with id: " + data_id + " exists.")
            
            session.delete(db_data)

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

        