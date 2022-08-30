import datetime
from unicodedata import category
from xmlrpc.client import boolean
from fastapi import APIRouter, status, HTTPException, Response
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import api.routers.company_metric_api as metric_api
import core.company_metrics_classifications as metrics_classifications_core

import simplejson as json

import jwt as jwt

import api.config as api_config

router = APIRouter(
    prefix="/account",
    tags=["account"],
    dependencies=[],
    responses={404: {"description": "Not found"}}, 
)

class LoginModelIn(BaseModel):
    userName: str
    password: str

class LoginModelOut(BaseModel):
    token: str

class CreateAccountModelIn(BaseModel):
    userName: str
    password: str
    email: str
    phone: str

class CreateAccountModelOut(BaseModel):
    id: int

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CreateAccountModelOut)
def create_account(body: CreateAccountModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            acc = Account(userName=body.userName, password=body.password, email=body.email, phone=body.phone)
            session.add(acc)
            session.flush()
        
        return CreateAccountModelOut(id=acc.id)
                   

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("/session", status_code=status.HTTP_200_OK, response_model=LoginModelOut)
def login(body: LoginModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_acc = session.query(Account).filter(and_(Account.userName == body.userName, Account.password == body.password)).first()
            if db_acc is None:
                raise Exception(status_code=500, detail="Invalid credentials.")
        
            private_key_file = open('/home/ghelie/fin_app/fin_app_core/api/privkey.key')
            private_key = private_key_file.read()
            public_key_file = open('/home/ghelie/fin_app/fin_app_core/api/publickey.crt')
            public_key = public_key_file.read()

            curr_stamp = datetime.datetime.now().timestamp()
            tomorrow_time_stamp = (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()

            jwt_token = jwt.encode({"sub": db_acc.id, "aud": "fin_app", "exp": tomorrow_time_stamp, "iat": curr_stamp, "iss": "fin_app"}, key=private_key, algorithm="RS256")

            return LoginModelOut(token=jwt_token)

                   
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))