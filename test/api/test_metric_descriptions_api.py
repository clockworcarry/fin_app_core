from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str, create_default_user_metric_classifications, create_default_user_metric_descriptions, create_default_industry_relations, create_default_metric_classifications, create_default_metric_descriptions, create_default_sector_relations, create_default_sectors, create_default_users, get_access_tokens

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from db.models import *

from  test.test_utils import cleanup_db_from_db_str, create_default_business_segments, create_default_companies, create_system_user

import api.constants as api_constants
from passlib.context import CryptContext

client = TestClient(app)

class TestMetricDescriptionsApi:
    @classmethod
    def setup_class(cls):
        try:
            TestMetricDescriptionsApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestMetricDescriptionsApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestMetricDescriptionsApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestMetricDescriptionsApi.db_conn_str)
                           
                create_default_users(session)

            
            toks = get_access_tokens(client, TestMetricDescriptionsApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestMetricDescriptionsApi.system_access_token = toks[0]
            TestMetricDescriptionsApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_get_metric_descriptions(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDescriptionsApi.db_conn_str, template_name='default_session') as session:
            create_default_metric_classifications(session)
            create_default_metric_descriptions(session)
            create_default_user_metric_classifications(session)
            create_default_user_metric_descriptions(session)
        
        base_url = TestMetricDescriptionsApi.base_url + "/metric/descriptions"
        response = client.get(base_url, headers={"Authorization": "Bearer " + TestMetricDescriptionsApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 2

        response.sort(key=lambda x: x['id'], reverse=False)

        assert response[0]['id'] == 1
        assert response[0]['category_name'] == "Income Statement"
        assert len(response[0]['metrics']) == 0
        assert len(response[0]['categories']) == 2

        category = response[0]['categories'][0]
        assert category['id'] == 3
        assert category['category_name'] == "Revenue"
        assert len(category['metrics']) == 2
        category['metrics'].sort(key=lambda x: x['description']['id'], reverse=False)
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == None
        assert category_metrics[0]['description']['id'] == 1
        assert category_metrics[0]['description']['code'] == 'rev_2021'
        assert category_metrics[0]['description']['display_name'] == '2021 Revenue'
        assert category_metrics[0]['description']['metric_data_type'] == METRIC_TYPE_NUMBER
        assert category_metrics[0]['description']['metric_duration_type'] == -1
        assert category_metrics[0]['description']['year_recorded'] == -1
        assert category_metrics[0]['description']['quarter_recorded'] == -1
        assert category_metrics[0]['description']['metric_duration'] == -1
        assert category_metrics[0]['description']['look_back'] == True
        assert category_metrics[0]['description']['metric_fixed_year'] == 2021
        assert category_metrics[0]['description']['metric_fixed_quarter'] == -1
        assert category_metrics[1]['data'] == None
        assert category_metrics[1]['description']['id'] == 2
        assert category_metrics[1]['description']['code'] == 'rev_ttm'
        assert category_metrics[1]['description']['display_name'] == 'Trailing 12 Months Revenue'
        assert category_metrics[1]['description']['metric_data_type'] == METRIC_TYPE_NUMBER
        assert category_metrics[1]['description']['metric_duration_type'] == METRIC_DURATION_QUARTER
        assert category_metrics[1]['description']['year_recorded'] == 2022
        assert category_metrics[1]['description']['quarter_recorded'] == 3
        assert category_metrics[1]['description']['metric_duration'] == 4
        assert category_metrics[1]['description']['look_back'] == True
        assert category_metrics[1]['description']['metric_fixed_year'] == -1
        assert category_metrics[1]['description']['metric_fixed_quarter'] == -1

        category = response[0]['categories'][1]
        assert category['id'] == 4
        assert category['category_name'] == "EBITDA"
        assert len(category['metrics']) == 2
        category['metrics'].sort(key=lambda x: x['description']['id'], reverse=False)
        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == None
        assert category_metrics[0]['description']['id'] == 3
        assert category_metrics[0]['description']['code'] == 'ebitda_2021'
        assert category_metrics[0]['description']['display_name'] == '2021 EBITDA'
        assert category_metrics[0]['description']['metric_data_type'] == METRIC_TYPE_NUMBER
        assert category_metrics[0]['description']['metric_duration_type'] == -1
        assert category_metrics[0]['description']['year_recorded'] == -1
        assert category_metrics[0]['description']['quarter_recorded'] == -1
        assert category_metrics[0]['description']['metric_duration'] == -1
        assert category_metrics[0]['description']['look_back'] == True
        assert category_metrics[0]['description']['metric_fixed_year'] == 2021
        assert category_metrics[0]['description']['metric_fixed_quarter'] == -1
        assert category_metrics[1]['data'] == None
        assert category_metrics[1]['description']['id'] == 4
        assert category_metrics[1]['description']['code'] == 'ebitda_ttm'
        assert category_metrics[1]['description']['display_name'] == 'Trailing 12 Months EBITDA'
        assert category_metrics[1]['description']['metric_data_type'] == METRIC_TYPE_NUMBER
        assert category_metrics[1]['description']['metric_duration_type'] == METRIC_DURATION_QUARTER
        assert category_metrics[1]['description']['year_recorded'] == 2022
        assert category_metrics[1]['description']['quarter_recorded'] == 3
        assert category_metrics[1]['description']['metric_duration'] == 4
        assert category_metrics[1]['description']['look_back'] == True
        assert category_metrics[1]['description']['metric_fixed_year'] == -1
        assert category_metrics[1]['description']['metric_fixed_quarter'] == -1


        assert response[1]['id'] == 2
        assert response[1]['category_name'] == "Cloud Metrics"
        assert len(response[1]['metrics']) == 1
        assert len(response[1]['categories']) == 0
        category_metrics = response[1]['metrics']
        assert category_metrics[0]['data'] == None
        assert category_metrics[0]['description']['id'] == 5
        assert category_metrics[0]['description']['code'] == 'nb_cloud_customers_2021'
        assert category_metrics[0]['description']['display_name'] == '2021 Number of Cloud Customers'
        assert category_metrics[0]['description']['metric_data_type'] == METRIC_TYPE_NUMBER
        assert category_metrics[0]['description']['metric_duration_type'] == -1
        assert category_metrics[0]['description']['year_recorded'] == -1
        assert category_metrics[0]['description']['quarter_recorded'] == -1
        assert category_metrics[0]['description']['metric_duration'] == -1
        assert category_metrics[0]['description']['look_back'] == True
        assert category_metrics[0]['description']['metric_fixed_year'] == 2021
        assert category_metrics[0]['description']['metric_fixed_quarter'] == -1


