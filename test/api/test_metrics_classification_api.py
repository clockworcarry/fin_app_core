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

class TestMetricsClassification:
    @classmethod
    def setup_class(cls):
        try:
            TestMetricsClassification.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestMetricsClassification.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestMetricsClassification.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestMetricsClassification.db_conn_str)
                           
                create_default_users(session)
            
            toks = get_access_tokens(client, TestMetricsClassification.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestMetricsClassification.system_access_token = toks[0]
            TestMetricsClassification.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_create_metrics_category(self):
        base_url = TestMetricsClassification.base_url + "/metrics/category"
        
        body = {'category_name': 'new_cat', 'parent_id': 222}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestMetricsClassification.ghelie_access_token}, json=body)             
        assert response.status_code == 500
        response = response.json()
        assert response['detail'] == "Parent id 222 could not be associated to any existing categories."

        body = {'category_name': 'new_cat', 'parent_id': None}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestMetricsClassification.ghelie_access_token}, json=body)             
        assert response.status_code == 201

        body = {'category_name': 'new_cat', 'parent_id': None}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestMetricsClassification.ghelie_access_token}, json=body)             
        assert response.status_code == 500
        response = response.json()
        assert response['detail'] == "A category with name: new_cat already exists for this user."

        new_cat_id = 0
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricsClassification.db_conn_str, template_name='default_session') as session:
            db_categories = session.query(MetricClassification).filter(MetricClassification.parent_category_id == None).all()
            assert len(db_categories) == 1
            assert db_categories[0].category_name == "new_cat"
            assert db_categories[0].parent_category_id == None
            assert db_categories[0].creator_id == 2
            new_cat_id = db_categories[0].id

        body = {'category_name': 'new_cat_sub', 'parent_id': new_cat_id}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestMetricsClassification.ghelie_access_token}, json=body)             
        assert response.status_code == 201

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricsClassification.db_conn_str, template_name='default_session') as session:
            db_categories = session.query(MetricClassification).filter(MetricClassification.parent_category_id == new_cat_id).all()
            assert len(db_categories) == 1
            assert db_categories[0].category_name == "new_cat_sub"
            assert db_categories[0].parent_category_id == new_cat_id
            assert db_categories[0].creator_id == 2

    def test_update_metrics_category(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricsClassification.db_conn_str, template_name='default_session') as session:
            session.query(MetricClassification).delete()
            session.add(MetricClassification(id=1000, category_name='cat_up_one', parent_category_id=None, creator_id=2))
            session.add(MetricClassification(id=1001, category_name='cat_up_two', parent_category_id=1000, creator_id=2))
            session.flush()
            session.add(UserMetricClassification(account_id=1, metric_classification_id=1000))
            session.add(UserMetricClassification(account_id=1, metric_classification_id=1001))

        base_url = TestMetricsClassification.base_url + "/metrics/category"
        url = base_url + "/" + str(1000)
        body = {'category_name': 'cat_up_one_mode', 'parent_id': 222}
        response = client.put(url, headers={"Authorization": "Bearer " + TestMetricsClassification.system_access_token}, json=body)             
        assert response.status_code == 500
        response = response.json()
        assert response['detail'] == "Parent id 222 could not be associated to any existing categories."

        body = {'category_name': 'cat_up_one_mode', 'parent_id': 1001}
        response = client.put(url, headers={"Authorization": "Bearer " + TestMetricsClassification.system_access_token}, json=body)             
        assert response.status_code == 500
        response = response.json()
        assert response['detail'] == "Cannot set parent to a category whose parent is this category. Circular dependency."

        url = base_url + "/" + str(1001)
        body = {'category_name': 'cat_up_two_mode', 'parent_id': None, 'creator_id': 234}
        response = client.put(url, headers={"Authorization": "Bearer " + TestMetricsClassification.system_access_token}, json=body)             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricsClassification.db_conn_str, template_name='default_session') as session:
            db_categories = session.query(MetricClassification).all()
            assert len(db_categories) == 2
            db_categories.sort(key=lambda x: x.id, reverse=False)
            assert db_categories[0].id == 1000
            assert db_categories[0].category_name == "cat_up_one"
            assert db_categories[0].parent_category_id == None
            assert db_categories[0].creator_id == 2

            assert db_categories[1].id == 1001
            assert db_categories[1].category_name == "cat_up_two_mode"
            assert db_categories[1].parent_category_id == None
            assert db_categories[1].creator_id == 2

    def test_delete_metrics_category(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricsClassification.db_conn_str, template_name='default_session') as session:
            session.query(MetricClassification).delete()
            session.add(MetricClassification(id=1000, category_name='cat_up_one', parent_category_id=None, creator_id=2))
            session.add(MetricClassification(id=1001, category_name='cat_up_two', parent_category_id=1000, creator_id=2))
            session.add(MetricClassification(id=1002, category_name='cat_up_three', parent_category_id=1001, creator_id=2))
            session.flush()
            session.add(UserMetricClassification(account_id=1, metric_classification_id=1000))
            session.add(UserMetricClassification(account_id=1, metric_classification_id=1001))
            session.add(UserMetricClassification(account_id=1, metric_classification_id=1002))

        base_url = TestMetricsClassification.base_url + "/metrics/category"
        url = base_url + "/" + str(1000)
        response = client.delete(url, headers={"Authorization": "Bearer " + TestMetricsClassification.system_access_token})             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricsClassification.db_conn_str, template_name='default_session') as session:
            db_categories = session.query(MetricClassification).all()
            assert len(db_categories) == 2
            db_categories.sort(key=lambda x: x.id, reverse=False)
            assert db_categories[0].id == 1001
            assert db_categories[0].category_name == "cat_up_two"
            assert db_categories[0].parent_category_id == None
            assert db_categories[0].creator_id == 2

            assert db_categories[1].id == 1002
            assert db_categories[1].category_name == "cat_up_three"
            assert db_categories[1].parent_category_id == 1001
            assert db_categories[1].creator_id == 2
