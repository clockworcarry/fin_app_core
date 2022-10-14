import datetime
from unicodedata import category
from xmlrpc.client import boolean
from fastapi import APIRouter, status, HTTPException, Response, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.status import HTTP_204_NO_CONTENT, HTTP_501_NOT_IMPLEMENTED
from passlib.context import CryptContext
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import api.routers.company_metric_api as metric_api
import api.constants as api_constants

import simplejson as json

import jwt as jwt

import api.config as api_config

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/account",
    tags=["account"],
    dependencies=[],
    responses={404: {"description": "Not found"}}, 
)

class LoginModelIn(BaseModel):
    userName: str
    password: str

class LoginModelOut(BaseModel):
    access_token: str

class AccountDeletingConfirmationModelOut(BaseModel):
    confirmation_token: str

class CreateAccountModelIn(BaseModel):
    userName: str
    password: str
    email: str
    phone: str

class CreateAccountModelOut(BaseModel):
    id: int


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def validate_password(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)

def authenticate_user(userName, password, session):
    db_acc = session.query(Account).filter(Account.userName == userName).first()
    if db_acc is None:
        return False
    if not validate_password(password, db_acc.password):
        return False
    return db_acc
    
    

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CreateAccountModelOut)
def create_account(body: CreateAccountModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            hashed_pwd = pwd_context.hash(body.password)
            acc = Account(userName=body.userName, password=hashed_pwd, email=body.email, phone=body.phone)
            session.add(acc)
            session.flush()
        
            return CreateAccountModelOut(id=acc.id)
                   

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_account(body: CreateAccountModelIn):
    return Response(content="Not implemented", status_code=HTTP_204_NO_CONTENT)

@router.post("/token", status_code=status.HTTP_200_OK, response_model=LoginModelOut)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_acc = authenticate_user(form_data.username, form_data.password, session)
            if not db_acc:
                raise Exception("Invalid credentials.")
        
            private_key_file = open(api_config.global_api_config.privKeyFilePath + 'privkey.key')
            private_key = private_key_file.read()

            curr_stamp = datetime.datetime.now().timestamp()
            tomorrow_time_stamp = (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()

            jwt_token = jwt.encode({"sub": db_acc.id, "aud": "fin_app", "exp": tomorrow_time_stamp, "iat": curr_stamp, "iss": "fin_app"}, key=private_key, algorithm="RS256")

            return LoginModelOut(access_token=jwt_token)

                   
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{}", status_code=status.HTTP_200_OK, )
def account_deletion_confirmation(body: CreateAccountModelIn):
    return Response(content="Not implemented", status_code=HTTP_501_NOT_IMPLEMENTED)

@router.put("/confirmation/{account_id}", status_code=HTTP_204_NO_CONTENT)
def delete_account():
    return Response(content="Not implemented", status_code=HTTP_501_NOT_IMPLEMENTED)

@router.delete("/", status_code=HTTP_204_NO_CONTENT)
def delete_account():
    return Response(content="Not implemented", status_code=HTTP_501_NOT_IMPLEMENTED)