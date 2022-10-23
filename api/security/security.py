from urllib.request import Request
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import SignatureExpired
import jwt as jwt
import api.config as api_config
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *

import api.routers.account_api as account_api

import core.constants as core_constants
import core.security as core_security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class RequestContext:
    def __init__(self, authenticated: bool, user_id: int = None):
        self.authenticated = authenticated
        self.user_id = user_id

def authenticate_request(request: Request, session):
    if 'userName' in request.query_params and 'password' in request.query_params:
        db_acc = core_security.authenticate_user(request.query_params['userName'], request.query_params['password'], session)
        if not db_acc:
            raise Exception("Invalid credentials.")
        else:
           return RequestContext(authenticated=True, user_id=db_acc.id) 

    
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        raise SignatureExpired("Missing Authorization header.")

    scheme, _, token = auth_header.partition(" ")
    
    public_key_file = open(api_config.global_api_config.privKeyFilePath + 'publickey.crt')
    public_key = public_key_file.read()
    
    payload = jwt.decode(token, key=public_key, algorithms=["RS256"], audience="fin_app")
    account_id = payload['sub']

    db_acc = session.query(Account).filter(Account.id == account_id).first()
    if db_acc is None:
        raise Exception("Failed to load user account.")
    
    #Implement further rights

    return RequestContext(authenticated=True, user_id=db_acc.id)