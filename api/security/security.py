from urllib.request import Request
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt as jwt
import api.config as api_config
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class RequestContext:
    def __init__(self, authenticated: bool, user_id: int = None):
        self.authenticated = authenticated
        self.user_id = user_id

def authenticate_request(request: Request, session):
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        raise Exception("Missing Authorization header.")

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



#this function can throw exceptions
'''def authenticate_request(token: str = Depends(oauth2_scheme, ), session = None):
    try:
        public_key_file = open(api_config.global_api_config.privKeyFilePath + 'publickey.crt')
        public_key = public_key_file.read()
        payload = jwt.decode(token, key=public_key, algorithms=["RS256"], audience="fin_app")
        account_id = payload['sub']
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_acc = session.query(Account).filter(Account.id == account_id).first()
            if db_acc is None:
                raise Exception("Failed to load account.")
            return db_acc.id
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

def get_current_user(session):
    token = oauth2_scheme()

    public_key_file = open(api_config.global_api_config.privKeyFilePath + 'publickey.crt')
    public_key = public_key_file.read()
    payload = jwt.decode(token, key=public_key, algorithms=["RS256"], audience="fin_app")
    account_id = payload['sub']

    db_acc = session.query(Account).filter(Account.id == account_id).first()
    if db_acc is None:
        raise Exception("Failed to load account.")
    
    return db_acc.id'''