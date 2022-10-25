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

import core.metrics_classifications as metrics_classifications_core

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/metric/descriptions",
    tags=["metricDescriptions"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("", status_code=status.HTTP_200_OK, response_model=List[shared_models_core.MetricCategoryModel], summary="Get the metric descriptions for a user.",
            description="This will only retrieve the metrics that the dealer has access to. See erd for reference.", response_description="List of metric descriptions.")
def get_metric_descriptions(request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            metric_categories = metrics_classifications_core.get_user_metric_categories(request.state.rctx.user_id, session)
            metric_categories = metrics_classifications_core.group_metric_categories_model(metric_categories, None)
            
            db_rows = session.query(MetricDescription, UserMetricDescription) \
                             .join(UserMetricDescription, UserMetricDescription.metric_description_id == MetricDescription.id) \
                             .filter(or_(UserMetricDescription.account_id == core_global_constants.system_user_id, UserMetricDescription.account_id == request.state.rctx.user_id)) \
                             .all()
            
            data_models = []
            for desc, user_desc in db_rows:
                desc_model = shared_models_core.MetricDescriptionModel.from_orm(desc)
                data_models.append(shared_models_core.MetricDataModel(data=None, description=desc_model))


            metrics_classifications_core.categorize_metrics(metric_categories, data_models)
            metrics_classifications_core.remove_empty_categories(metric_categories)


            
            return metric_categories

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.get("/{toolbox_id}", status_code=status.HTTP_200_OK, response_model=List[shared_models_core.CompanyBusinessSegmentsShortModel])
def get_metric_descriptions(toolbox_id, request: Request):
    return Response(content="Not implemented", status_code=HTTP_501_NOT_IMPLEMENTED)