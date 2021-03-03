from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from api.routers.company_metric_api import *

client = TestClient(app)


class TestCompanyMetricApi:
    @classmethod
    def setup_class(cls):
        absolute_path = os.path.join(sys.path[0], 'config.json')
        with open(absolute_path, 'r') as f:
            file_content_raw = f.read()
            config_json_content = json.loads(file_content_raw)
            init_config(config_json_content)
            TestCompanyMetricApi.db_conn_str = config_json_content['dbConnString']


    def test_get_version(self):
        response = client.get("/version")
        assert response.status_code == 200
        assert response.json() == {"version": "0.0.1"}

    def test_create_metric_description_missing_data(self):
        response = client.post(
                                    "/companyMetric/description",
                                    json={
                                            "code": "123",
                                            "display_name": 1,
                                            "metric_data_type": "0"
                                        }
                            )

        assert response.status_code == 422

    def test_create_metric_description_valid(self):
        response = client.post(
                                    "/companyMetric/description",
                                    json={
                                            "code": "rev_usa",
                                            "display_name": "Revenue United States",
                                            "metric_data_type": 0
                                        }
                            )
                            
        assert response.status_code == 201
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            query_res = session.query(CompanyMetricDescription).all()
            assert len(query_res) == 1
            assert query_res[0].code == 'rev_usa'
            assert query_res[0].display_name == 'Revenue United States'
            assert query_res[0].metric_data_type == 0
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)

    def test_update_metric_description_valid(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)
            session.commit()

            url = "/companyMetric/description/" + str(new_desc.id)
            response = client.post(
                                    url,
                                    json={
                                            "code": "updated_code",
                                            "display_name": "Revenue United States",
                                            "metric_data_type": 2
                                        }
                            )
                            
            assert response.status_code == 200
            session.expire_all()     
            query_res = session.query(CompanyMetricDescription).all()
            assert len(query_res) == 1
            assert query_res[0].code == 'updated_code'
            assert query_res[0].display_name == 'Revenue United States'
            assert query_res[0].metric_data_type == 2
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)

    def test_delete_metric_description_valid(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)
            session.commit()

            url = "/companyMetric/description/" + str(new_desc.id)
            response = client.delete(
                                    url,
                                    json={
                                            "code": "updated_code",
                                            "display_name": "Revenue United States",
                                            "metric_data_type": 2
                                        }
                            )
                            
            assert response.status_code == 200
            session.expire_all()     
            query_res = session.query(CompanyMetricDescription).all()
            assert len(query_res) == 0
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)


    def test_create_metric_missing_data(self):
        response = client.post(
                                    "/companyMetric/20614",
                                    json={}
                            )
        assert response.status_code == 405

        response = client.post(
                                    "/companyMetric/20614/123",
                                    json={}
                            )
        assert response.status_code == 422

    def test_create_metric_invalid_desc_id(self):
        response = client.post(
                                    "/companyMetric/20614/123",
                                    json={
                                            "look_back": -1,
                                            "data": 64,
                                            "date_recorded": "2019-06-30"
                                        }
                            )
        assert response.status_code == 500
        assert "psycopg2.errors.ForeignKeyViolation" in response.text

    def test_create_metric_valid(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            apple_company = Company(ticker='AAPL', name='Apple Inc', delisted=False)
            session.add(apple_company)

            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)
            session.commit()
            
            new_metric = CompanyMetric(data='10', look_back=LOOK_BACK_QUARTER, company_id=apple_company.id, company_metric_description_id=new_desc.id, date_recorded=datetime.date(2019, 12, 31))
            session.add(new_metric)
            session.commit()

            url = "/companyMetric/" + str(apple_company.id) + "/" + str(new_desc.id)
            response = client.post(
                                    url,
                                    json={
                                            "code": "updated_code",
                                            "display_name": "Revenue United States",
                                            "metric_data_type": 2
                                        }
                            )
                            
            assert response.status_code == 201
            session.expire_all()     
            query_res = session.query(CompanyMetric).all()
            assert len(query_res) == 1
            assert query_res[0].data == 10
            assert query_res[0].look_back == LOOK_BACK_QUARTER
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
