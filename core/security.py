from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
import api.config as api_config

from db.models import *

from passlib.context import CryptContext

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
