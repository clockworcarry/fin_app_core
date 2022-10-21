from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str, create_default_groups, create_default_industries, create_default_industry_relations, create_default_metric_classifications, create_default_metric_descriptions, create_default_sector_relations, create_default_sectors, create_default_users, get_access_tokens

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from db.models import *

from  test.test_utils import cleanup_db_from_db_str, create_default_business_segments, create_default_companies, create_system_user

import api.constants as api_constants
from passlib.context import CryptContext

client = TestClient(app)

class TestMetricDescriptionApi:
    @classmethod
    def setup_class(cls):
        try:
            TestMetricDescriptionApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestMetricDescriptionApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestMetricDescriptionApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestMetricDescriptionApi.db_conn_str)
                           
                create_default_users(session)

                create_default_metric_classifications(session)
            
            toks = get_access_tokens(client, TestMetricDescriptionApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestMetricDescriptionApi.system_access_token = toks[0]
            TestMetricDescriptionApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_create_metric_description(self):
        base_url = TestMetricDescriptionApi.base_url + "/metric/description"
        body = {'code': 'rev_3y', 'display_name': "revenue 3 years", 'metric_data_type': METRIC_TYPE_NUMBER, 'metric_duration_type': METRIC_DURATION_ANNUAL, 'year_recorded': 2022, \
                'quarter_recorded': 2, 'metric_duration': 3, 'look_back': True, 'metric_fixed_year': -1, 'metric_fixed_quarter': -1, 'metric_classification_id': 3}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestMetricDescriptionApi.ghelie_access_token}, json=body)             
        assert response.status_code == 201

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDescriptionApi.db_conn_str, template_name='default_session') as session:
            db_descs = session.query(MetricDescription).filter(MetricDescription.code == 'rev_3y').all()
            assert len(db_descs) == 1
            assert db_descs[0].code == "rev_3y"
            assert db_descs[0].display_name == "revenue 3 years"
            assert db_descs[0].metric_data_type == METRIC_TYPE_NUMBER
            assert db_descs[0].metric_duration_type == METRIC_DURATION_ANNUAL
            assert db_descs[0].year_recorded == 2022
            assert db_descs[0].quarter_recorded == 2
            assert db_descs[0].metric_duration == 3
            assert db_descs[0].look_back == True
            assert db_descs[0].metric_fixed_year == -1
            assert db_descs[0].metric_fixed_quarter == -1
            assert db_descs[0].metric_classification_id == 3
            assert db_descs[0].creator_id == 2

            db_user_desc = session.query(UserMetricDescription).filter(UserMetricDescription.metric_description_id == db_descs[0].id).all()
            assert len(db_user_desc) == 1
            assert db_user_desc[0].metric_description_id == db_descs[0].id
            assert db_user_desc[0].account_id == 2



    def test_update_metric_description(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDescriptionApi.db_conn_str, template_name='default_session') as session:
            metric_desc_rev_2021 = MetricDescription(id=1000, code='rev_2021', display_name='2021 Revenue', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                        year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                        metric_classification_id=3, creator_id=2)
            session.add(metric_desc_rev_2021)

        base_url = TestMetricDescriptionApi.base_url + "/metric/description"
        url = base_url + "/" + str(1000)
        body = {'code': 'rev_3y', 'display_name': "revenue 3 years mod", 'metric_data_type': METRIC_TYPE_PERCENTAGE, 'metric_duration_type': METRIC_DURATION_ANNUAL, 'year_recorded': 2022, \
                'quarter_recorded': 2, 'metric_duration': 3, 'look_back': True, 'metric_fixed_year': 2021, 'metric_fixed_quarter': -1, 'metric_classification_id': 1, 'creator_id': 1000}
        response = client.put(url, headers={"Authorization": "Bearer " + TestMetricDescriptionApi.system_access_token}, json=body)             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDescriptionApi.db_conn_str, template_name='default_session') as session:
            db_descs = session.query(MetricDescription).filter(MetricDescription.id == 1000).all()
            assert len(db_descs) == 1
            assert db_descs[0].code == "rev_3y"
            assert db_descs[0].display_name == "revenue 3 years mod"
            assert db_descs[0].metric_data_type == METRIC_TYPE_PERCENTAGE
            assert db_descs[0].metric_duration_type == METRIC_DURATION_ANNUAL
            assert db_descs[0].year_recorded == 2022
            assert db_descs[0].quarter_recorded == 2
            assert db_descs[0].metric_duration == 3
            assert db_descs[0].look_back == True
            assert db_descs[0].metric_fixed_year == 2021
            assert db_descs[0].metric_fixed_quarter == -1
            assert db_descs[0].metric_classification_id == 1
            assert db_descs[0].creator_id == 2

    def test_delete_metric_description(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDescriptionApi.db_conn_str, template_name='default_session') as session:
            session.query(MetricDescription).delete()
            metric_desc_rev_2021 = MetricDescription(id=1001, code='rev_2021', display_name='2021 Revenue', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                        year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                        metric_classification_id=3, creator_id=2)
            session.add(metric_desc_rev_2021)

        base_url = TestMetricDescriptionApi.base_url + "/metric/description"
        url = base_url + "/" + str(1001)
        response = client.delete(url, headers={"Authorization": "Bearer " + TestMetricDescriptionApi.system_access_token})             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDescriptionApi.db_conn_str, template_name='default_session') as session:
            db_descs = session.query(MetricDescription).filter(MetricDescription.id == 1001).all()
            assert len(db_descs) == 0