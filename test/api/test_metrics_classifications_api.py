from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str, create_default_groups, create_default_industries, create_default_industry_relations, create_default_metric_classifications, create_default_sector_relations, create_default_sectors, create_default_user_metric_classifications, create_default_users, get_access_tokens

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from db.models import *

from  test.test_utils import cleanup_db_from_db_str, create_default_business_segments, create_default_companies, create_system_user

import api.constants as api_constants
from passlib.context import CryptContext

client = TestClient(app)

class TestMetricsClassificationsApi:
    @classmethod
    def setup_class(cls):
        try:
            TestMetricsClassificationsApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestMetricsClassificationsApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestMetricsClassificationsApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestMetricsClassificationsApi.db_conn_str)
                           
                create_default_users(session)

                create_default_metric_classifications(session)

                create_default_user_metric_classifications(session)
            
            toks = get_access_tokens(client, TestMetricsClassificationsApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestMetricsClassificationsApi.system_access_token = toks[0]
            TestMetricsClassificationsApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_get_metrics_classifications(self):
        base_url = TestMetricsClassificationsApi.base_url + "/metrics/categories"
        response = client.get(base_url, headers={"Authorization": "Bearer " + TestMetricsClassificationsApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        
        
        assert len(response) == 2

        response.sort(key=lambda x: x['id'], reverse=False)

        assert response[0]['id'] == 1
        assert response[0]['category_name'] == "Income Statement"
        assert response[0]['parent_id'] == None
        categories = response[0]['categories']
        assert len(categories) == 2
        categories.sort(key=lambda x: x['id'], reverse=False)
        assert categories[0]['id'] == 3
        assert categories[0]['category_name'] == "Revenue"
        assert categories[0]['parent_id'] == 1
        assert len(categories[0]['categories']) == 0
        assert categories[1]['id'] == 4
        assert categories[1]['category_name'] == "EBITDA"
        assert categories[1]['parent_id'] == 1
        assert len(categories[1]['categories']) == 0
        

        assert response[1]['id'] == 2
        assert response[1]['category_name'] == "Cloud Metrics"
        assert response[1]['parent_id'] == None
        categories = response[1]['categories']
        assert len(categories) == 0