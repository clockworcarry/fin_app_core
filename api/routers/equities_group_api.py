from xmlrpc.client import boolean
from fastapi import APIRouter, status, HTTPException, Request, Response, Depends
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from db.models import *

import api.shared_models as shared_models
import core.shared_models as shared_models_core
import core.metrics_classifications as metrics_classifications_core
import core.metrics as core_metrics

import api.security.security as app_security


import simplejson as json

import api.config as api_config
import api.constants as api_constants
import core.constants as core_global_constants

import copy

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/" + "equities/group",
    tags=["equitiesGroup"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def create_company_group(request: Request, body: shared_models_core.CompanyGroupInfoShortModel):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.name_code == body.name_code).first()
            if db_grp is not None:
                raise Exception("A company group with name code: " + body.name_code + " already exists.")
            
            new_grp = CompanyGroup(name_code=body.name_code, name=body.name, description=body.description, creator_id=request.state.rctx.user_id)
            session.add(new_grp)
            session.flush()
            session.add(UserCompanyGroup(group_id=new_grp.id, account_id=request.state.rctx.user_id))

            return Response(status_code=HTTP_201_CREATED)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{grp_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_company_group(grp_id, request: Request, body: shared_models_core.CompanyGroupInfoShortModel):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No company group with id: " + grp_id + " exists.")
            
            db_grp.name_code = body.name_code
            db_grp.name = body.name
            db_grp.description = body.description

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/{grp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_group(grp_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No company group with id: " + grp_id + " exists.")
            
            session.delete(db_grp)

        return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/user/{grp_id}", status_code=HTTP_204_NO_CONTENT)
def add_group_to_user_groups(grp_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_row = session.query(CompanyGroup, UserCompanyGroup).join(UserCompanyGroup, UserCompanyGroup.group_id == CompanyGroup.id) \
                             .filter(and_(UserCompanyGroup.account_id == request.state.rctx.user_id, UserCompanyGroup.group_id == grp_id)).first()
            
            if db_row is None:
                session.add(UserCompanyGroup(group_id=grp_id, account_id=request.state.rctx.user_id))
            else:
                raise HTTPException(status_code=500, detail="User with id: " + str(request.state.rctx.user_id) + " is already in group with id: " + grp_id)

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/user/{grp_id}", status_code=HTTP_204_NO_CONTENT)
def remove_group_from_user_groups(grp_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_row = session.query(CompanyGroup, UserCompanyGroup).join(UserCompanyGroup, UserCompanyGroup.group_id == CompanyGroup.id) \
                             .filter(and_(UserCompanyGroup.account_id == request.state.rctx.user_id, UserCompanyGroup.group_id == grp_id)).first()
            
            if db_row is None:
                raise Exception("User with id: " + str(request.state.rctx.user_id) + " is not in group with id: " + grp_id)
            else:
                session.delete(db_row[1])

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/metricDescription/{grp_id}/{desc_id}", status_code=HTTP_204_NO_CONTENT)
def add_metric_description_to_group(grp_id, desc_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No group with id: " + str(grp_id) + " exists.")
            
            db_metric_desc = session.query(MetricDescription).filter(MetricDescription.id == desc_id).first()
            if db_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + str(desc_id) + " exists.")
            
            session.add(CompanyGroupMetricDescription(metric_description_id=desc_id, company_group_id=grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/businessSegment/{grp_id}/{bs_id}", status_code=HTTP_204_NO_CONTENT)
def add_business_segment_to_group(grp_id, bs_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No group with id: " + str(grp_id) + " exists.")
            
            db_bs = session.query(CompanyBusinessSegment).filter(CompanyBusinessSegment.id == bs_id).first()
            if db_bs is None:
                raise HTTPException(status_code=500, detail="No business segment with id: " + str(bs_id) + " exists.")
            
            session.add(CompanyInGroup(company_business_segment_id=bs_id, group_id=grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/metricDescription/{grp_id}/{desc_id}", status_code=HTTP_204_NO_CONTENT)
def remove_metric_description_from_group(grp_id, desc_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            group_metrics = session.query(CompanyGroupMetricDescription).filter(CompanyGroupMetricDescription.company_group_id == grp_id).all()
            
            deleted = False
            for gm in group_metrics:
                if gm.metric_description_id == int(desc_id):
                    session.delete(gm)
                    deleted = True
                    break
            
            if not deleted:
                raise Exception("Could not find metric description with id: " + str(desc_id) + " in group with id: " + str(grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))

    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/businessSegment/{grp_id}/{bs_id}", status_code=HTTP_204_NO_CONTENT)
def remove_business_segment_from_group(grp_id, bs_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            companies_in_group = session.query(CompanyInGroup).filter(CompanyInGroup.group_id == grp_id).all()
            
            deleted = False
            for cig in companies_in_group:
                if cig.company_business_segment_id == int(bs_id):
                    session.delete(cig)
                    deleted = True
                    break
            
            if not deleted:
                raise Exception("Could not find business segment with id: " + str(bs_id) + " in group with id: " + str(grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))

    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


"""Get all the metric data for a group
   /equities/group/metrics/{grp_id}

Raises:
    HTTPException: _description_
    HTTPException: _description_
    HTTPException: _description_

Returns:
    the metric data for the group
"""
@router.get("/{grp_id}", response_model=shared_models_core.CompanyGroupMetricsModel)
def get_group(grp_id, request: Request, force_system_data : bool = False):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            #rctx = app_security.authenticate_request(request, session)
            rctx = request.state.rctx
            
            metric_categories = metrics_classifications_core.get_user_metric_categories(rctx.user_id, session)

            query = session.query(CompanyGroup, CompanyInGroup, CompanyGroupMetricDescription, MetricDescription, MetricData, CompanyBusinessSegment, Company) \
                                                                                                .join(CompanyInGroup, CompanyInGroup.group_id == CompanyGroup.id) \
                                                                                                .join(CompanyGroupMetricDescription, CompanyGroupMetricDescription.company_group_id == CompanyGroup.id) \
                                                                                                .join(MetricDescription, MetricDescription.id == CompanyGroupMetricDescription.metric_description_id) \
                                                                                                .join(MetricData, and_(MetricData.metric_description_id == MetricDescription.id, MetricData.company_business_segment_id == CompanyInGroup.company_business_segment_id)) \
                                                                                                .join(CompanyBusinessSegment, CompanyBusinessSegment.id == MetricData.company_business_segment_id) \
                                                                                                .join(Company, Company.id == CompanyBusinessSegment.company_id) \
                                                                                                .filter(CompanyGroup.id == grp_id)

            if force_system_data:
                query = query.filter(MetricData.user_id == core_global_constants.system_user_id)
            else:
                query = query.filter(or_(MetricData.user_id == core_global_constants.system_user_id, MetricData.user_id == rctx.user_id))
            
            db_rows = query.all()

            if len(db_rows) == 0:
                raise Exception("No data found for group_id: " + str(grp_id))

            business_segments = []

            #time.sleep(5) # Sleep for 3 seconds

            #initialize business segments
            for row in db_rows:
                row_business_segment = row[5]
                row_company = row[6]
                ebs = None
                for bs in business_segments:
                    if bs.id == row_business_segment.id:
                        ebs = bs
                        break
                
                if ebs is None:
                    business_segments.append(shared_models_core.BusinessSegmentModel(id=row_business_segment.id, code=row_business_segment.code, display_name=row_business_segment.display_name, \
                                                                                     company_id=row_business_segment.company_id, company_name=row_company.name, company_ticker=row_company.ticker))
                    ebs = business_segments[-1]
                    ebs.metric_categories = copy.deepcopy(metric_categories)
            
            #add metrics to proper categories in the proper business segment
            for row in db_rows:
                row_metric_description = row[3]
                row_metric_data = row[4]
                row_business_segment = row[5]
                metric_desc_model = shared_models_core.MetricDescriptionModel.from_orm(row_metric_description)
                metric_desc_model.metric_classification_id = row_metric_description.metric_classification_id
                metric_data = shared_models_core.MetricDataModel(data=row_metric_data.data, description=metric_desc_model)
                metric_data._user_id = row_metric_data.user_id
                
                ebs = None
                for bs in business_segments:
                    if bs.id == row_business_segment.id:
                        ebs = bs
                        break
                if ebs is not None:
                    core_metrics.add_metric_to_business_segment(ebs, metric_desc_model, metric_data, request.state.rctx.user_id)
                
                """if ebs is not None:
                    for cat in ebs.metric_categories:
                        if cat.id == row_metric_description.metric_classification_id:
                            duplicate_metric = None
                            for idx, metric in enumerate(cat.metrics):
                                if metric.description.id == metric_data.description.id:
                                    duplicate_metric = metric
                                    break
                            
                            if duplicate_metric is None:
                                cat.metrics.append(metric_data)
                            elif row_metric_data.user_id != core_global_constants.system_user_id:
                                cat.metrics.append(metric_data) #override existing system metric with user's one
                                del cat.metrics[idx]
                            break"""
            
            #group categories in business segment (tree hierarchy, categories can be nested recursively)
            for bs in business_segments:
                bs.metric_categories = metrics_classifications_core.group_metric_categories_model(bs.metric_categories, None)
                #remove categories with no metrics or sub categories
                metrics_classifications_core.remove_empty_categories(bs.metric_categories)

            group_info = shared_models_core.CompanyGroupInfoShortModel(id=db_rows[0][0].id, name_code=db_rows[0][0].name_code, name=db_rows[0][0].name)

            ret = shared_models_core.CompanyGroupMetricsModel(group_info=group_info, business_segments=business_segments)

            return ret                                      


    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))