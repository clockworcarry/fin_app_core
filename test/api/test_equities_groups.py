from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str, create_default_groups

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from api.routers.company_metrics_api import *

from  test.test_utils import cleanup_db_from_db_str, create_default_business_segments, create_default_companies, create_system_user

import api.constants as api_constants
from passlib.context import CryptContext

client = TestClient(app)

class TestEquitiesGroupsApi:
    @classmethod
    def setup_class(cls):
        try:
            TestEquitiesGroupsApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestEquitiesGroupsApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestEquitiesGroupsApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestEquitiesGroupsApi.db_conn_str)
                
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                hashed_pwd = pwd_context.hash('ghelie123')
                ghelie_user = Account(id=2, userName='ghelie', password=hashed_pwd, email='ghelie@gmail.com', phone='514-214-6004', disabled=False)
                session.add(ghelie_user)
                           
                create_system_user(session)
                
                create_default_companies(session)
                session.flush()

                create_default_groups(session)

                session.add(CompanyGroup(id=3, name_code='grp_test', name='Test Group', creator_id=2))
                session.flush()

                session.add(UserCompanyGroup(account_id=1, group_id=1))
                session.add(UserCompanyGroup(account_id=1, group_id=2))
                
                session.add(UserCompanyGroup(account_id=2, group_id=1))
                session.add(UserCompanyGroup(account_id=2, group_id=2))
                session.add(UserCompanyGroup(account_id=2, group_id=3))
            
            login_url = TestEquitiesGroupsApi.base_url + "/account/token"
            input = {'username': 'system', 'password': 'system'}
            response = client.post(login_url, headers = {'Content-Type': 'application/x-www-form-urlencoded'}, data=input)
            assert response.status_code == 200
            response = response.json()
            TestEquitiesGroupsApi.access_token = response['access_token']

            input = {'username': 'ghelie', 'password': 'ghelie123'}
            response = client.post(login_url, headers = {'Content-Type': 'application/x-www-form-urlencoded'}, data=input)
            assert response.status_code == 200
            response = response.json()
            TestEquitiesGroupsApi.ghelie_access_token = response['access_token']

        
        except Exception as gen_ex:
            print(str(gen_ex))

    
    def test_get_user_groups(self):
        base_url = TestEquitiesGroupsApi.base_url + "/equities/groups/"
        
        url = base_url + "1"
        response = client.get(url, headers={"Authorization": "Bearer " + TestEquitiesGroupsApi.access_token})             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 2
        response.sort(key=lambda x: x['id'], reverse=False)
        assert response[0]['id'] == 1
        assert response[0]['name'] == "Group Of All Defaults"
        assert response[0]['name_code'] == "defaults_grp"
        assert response[1]['id'] == 2
        assert response[1]['name'] == "Group Of Cloud Businesses"
        assert response[1]['name_code'] == "cloud_grp"

        url = base_url + "2"
        response = client.get(url, headers={"Authorization": "Bearer " + TestEquitiesGroupsApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 3
        response.sort(key=lambda x: x['id'], reverse=False)
        assert response[0]['id'] == 1
        assert response[0]['name'] == "Group Of All Defaults"
        assert response[0]['name_code'] == "defaults_grp"
        assert response[1]['id'] == 2
        assert response[1]['name'] == "Group Of Cloud Businesses"
        assert response[1]['name_code'] == "cloud_grp"
        assert response[2]['id'] == 3
        assert response[2]['name'] == "Test Group"
        assert response[2]['name_code'] == "grp_test"

        url = base_url + "2"
        bad_token = "abcdef"
        response = client.get(url, headers={"Authorization": "Bearer " + bad_token})             
        assert response.status_code == 500
        
        