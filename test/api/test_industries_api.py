from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str, create_default_groups, create_default_industries, create_default_industry_relations, create_default_sector_relations, create_default_sectors, create_default_users, get_access_tokens

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from api.routers.company_metrics_api import *

from  test.test_utils import cleanup_db_from_db_str, create_default_business_segments, create_default_companies, create_system_user

import api.constants as api_constants
from passlib.context import CryptContext

client = TestClient(app)

class TestIndustriesApi:
    @classmethod
    def setup_class(cls):
        try:
            TestIndustriesApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestIndustriesApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestIndustriesApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestIndustriesApi.db_conn_str)
                           
                create_default_users(session)
  
                create_default_sectors(session)

                create_default_industries(session)
            
            toks = get_access_tokens(client, TestIndustriesApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestIndustriesApi.system_access_token = toks[0]
            TestIndustriesApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_get_all_industries(self):
        base_url = TestIndustriesApi.base_url + "/industries"
        response = client.get(base_url, headers={"Authorization": "Bearer " + TestIndustriesApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 5

        response.sort(key=lambda x: x['id'], reverse=False)

        assert response[0]['id'] == 1
        assert response[0]['sector_id'] == 1
        assert response[0]['name'] == "Semiconductors"
        assert response[0]['name_code'] == "semis"

        assert response[1]['id'] == 2
        assert response[1]['sector_id'] == 2
        assert response[1]['name'] == "Banking Industry"
        assert response[1]['name_code'] == "banking"

        assert response[2]['id'] == 3
        assert response[2]['sector_id'] == 1
        assert response[2]['name'] == "Communications"
        assert response[2]['name_code'] == "comm"

        assert response[3]['id'] == 4
        assert response[3]['sector_id'] == 1
        assert response[3]['name'] == "Big Tech"
        assert response[3]['name_code'] == "big_tech"

        assert response[4]['id'] == 5
        assert response[4]['sector_id'] == 1
        assert response[4]['name'] == "Cloud Services"
        assert response[4]['name_code'] == "cloud"

    def test_get_sector_industries(self):
        base_url = TestIndustriesApi.base_url + "/industries"
        url = base_url + "/1"
        response = client.get(url, headers={"Authorization": "Bearer " + TestIndustriesApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 4

        response.sort(key=lambda x: x['id'], reverse=False)

        assert response[0]['id'] == 1
        assert response[0]['sector_id'] == 1
        assert response[0]['name'] == "Semiconductors"
        assert response[0]['name_code'] == "semis"

        assert response[1]['id'] == 3
        assert response[1]['sector_id'] == 1
        assert response[1]['name'] == "Communications"
        assert response[1]['name_code'] == "comm"

        assert response[2]['id'] == 4
        assert response[2]['sector_id'] == 1
        assert response[2]['name'] == "Big Tech"
        assert response[2]['name_code'] == "big_tech"

        assert response[3]['id'] == 5
        assert response[3]['sector_id'] == 1
        assert response[3]['name'] == "Cloud Services"
        assert response[3]['name_code'] == "cloud"

        url = base_url + "/2"
        response = client.get(url, headers={"Authorization": "Bearer " + TestIndustriesApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 1

        assert response[0]['id'] == 2
        assert response[0]['sector_id'] == 2
        assert response[0]['name'] == "Banking Industry"
        assert response[0]['name_code'] == "banking"