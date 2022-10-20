from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str, create_default_groups, create_default_industries, create_default_industry_relations, create_default_sector_relations, create_default_sectors, create_default_users, get_access_tokens

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from db.models import *

from  test.test_utils import cleanup_db_from_db_str, create_default_business_segments, create_default_companies, create_system_user

import api.constants as api_constants
from passlib.context import CryptContext

client = TestClient(app)

class TestSectorsApi:
    @classmethod
    def setup_class(cls):
        try:
            TestSectorsApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestSectorsApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestSectorsApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestSectorsApi.db_conn_str)
                           
                create_default_users(session)
  
                create_default_sectors(session)

            
            toks = get_access_tokens(client, TestSectorsApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestSectorsApi.system_access_token = toks[0]
            TestSectorsApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_get_sectors(self):
        base_url = TestSectorsApi.base_url + "/sectors"
        response = client.get(base_url, headers={"Authorization": "Bearer " + TestSectorsApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 2

        response.sort(key=lambda x: x['id'], reverse=False)

        assert response[0]['id'] == 1
        assert response[0]['name'] == "Information Technology"
        assert response[0]['name_code'] == "it_sector"

        assert response[1]['id'] == 2
        assert response[1]['name'] == "Financials"
        assert response[1]['name_code'] == "fin_sector"