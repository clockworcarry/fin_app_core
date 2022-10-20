from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str, create_default_groups, create_default_industries, create_default_industry_relations, create_default_metric_classifications, create_default_metric_data, create_default_metric_descriptions, create_default_sector_relations, create_default_sectors, create_default_user_metric_classifications, create_default_users, get_access_tokens

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from  test.test_utils import cleanup_db_from_db_str, create_default_business_segments, create_default_companies, create_system_user

import api.constants as api_constants
from passlib.context import CryptContext

from db.models import *

client = TestClient(app)

class TestCompanyBusinessSegmentApi:
    @classmethod
    def setup_class(cls):
        try:
            TestCompanyBusinessSegmentApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestCompanyBusinessSegmentApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestCompanyBusinessSegmentApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestCompanyBusinessSegmentApi.db_conn_str)
                           
                create_default_users(session)

                create_default_companies(session)
            
            toks = get_access_tokens(client, TestCompanyBusinessSegmentApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestCompanyBusinessSegmentApi.system_access_token = toks[0]
            TestCompanyBusinessSegmentApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_create_business_segment(self):
        base_url = TestCompanyBusinessSegmentApi.base_url + "/company/businessSegment"
        body = {'code': "bs1", 'display_name': 'bs one', 'company_id': 1}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestCompanyBusinessSegmentApi.ghelie_access_token}, json=body)             
        assert response.status_code == 201

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyBusinessSegmentApi.db_conn_str, template_name='default_session') as session:
            db_segments = session.query(CompanyBusinessSegment).filter(CompanyBusinessSegment.company_id == 1).all()
            
            assert len(db_segments) == 1
            assert db_segments[0].code == "bs1"
            assert db_segments[0].display_name == "bs one"
            assert db_segments[0].company_id == 1

    def test_update_business_segment(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyBusinessSegmentApi.db_conn_str, template_name='default_session') as session:
            session.query(CompanyBusinessSegment).delete()
            session.add(CompanyBusinessSegment(id=1000, code='bs2', display_name='bs two', company_id=1, creator_id=1))

        base_url = TestCompanyBusinessSegmentApi.base_url + "/company/businessSegment"
        url = base_url + "/" + str(1000)
        body = {'code': "bs2_mod", 'display_name': 'bs two mod', 'company_id': 100}
        response = client.put(url, headers={"Authorization": "Bearer " + TestCompanyBusinessSegmentApi.system_access_token}, json=body)             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyBusinessSegmentApi.db_conn_str, template_name='default_session') as session:
            db_segments = session.query(CompanyBusinessSegment).filter(CompanyBusinessSegment.company_id == 1).all()
            assert len(db_segments) == 1
            assert db_segments[0].code == "bs2_mod"
            assert db_segments[0].display_name == "bs two mod"
            assert db_segments[0].company_id == 1

    def test_get_company_business_segment(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyBusinessSegmentApi.db_conn_str, template_name='default_session') as session:
            cleanup_db_from_db_str(TestCompanyBusinessSegmentApi.db_conn_str, True)
            create_default_companies(session)
            create_default_business_segments(session)
            create_default_metric_classifications(session)
            create_default_user_metric_classifications(session)
            create_default_metric_descriptions(session)
            create_default_metric_data(session)
        
        base_url = TestCompanyBusinessSegmentApi.base_url + "/company/businessSegment"
        url = base_url + "/3"
        response = client.get(url, headers={"Authorization": "Bearer " + TestCompanyBusinessSegmentApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()

        bs = response
        assert bs['id'] == 3
        assert bs['code'] == "MSFT.default"
        assert bs['display_name'] == "MSFT default business"
        assert bs['company_id'] == 3
        assert bs['company_name'] == "Microsoft Corp."
        assert bs['company_ticker'] == "MSFT"
        assert len(bs['metric_categories']) == 1
        inc_stmt_category = bs['metric_categories'][0]
        assert inc_stmt_category['id'] == 1
        assert inc_stmt_category['category_name'] == "Income Statement"
        assert len(inc_stmt_category['metrics']) == 0
        assert len(inc_stmt_category['categories']) == 2
        category = inc_stmt_category['categories'][0]
        assert category['id'] == 3
        assert category['category_name'] == "Revenue"
        assert len(category['metrics']) == 2

        category['metrics'].sort(key=lambda x: x['description']['id'], reverse=False)

        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 10000000
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
        assert category_metrics[1]['data'] == 12000000
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
        category = inc_stmt_category['categories'][1]
        assert category['id'] == 4
        assert category['category_name'] == "EBITDA"
        assert len(category['metrics']) == 2

        category['metrics'].sort(key=lambda x: x['description']['id'], reverse=False)

        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 100000
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
        assert category_metrics[1]['data'] == 110000
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

    def test_delete_company_business_segment(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyBusinessSegmentApi.db_conn_str, template_name='default_session') as session:
            session.query(CompanyBusinessSegment).delete()
            session.add(CompanyBusinessSegment(id=1000, code='bs2', display_name='bs two', company_id=1, creator_id=1))
        
        base_url = TestCompanyBusinessSegmentApi.base_url + "/company/businessSegment"
        url = base_url + "/1000"
        response = client.delete(url, headers={"Authorization": "Bearer " + TestCompanyBusinessSegmentApi.ghelie_access_token})             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyBusinessSegmentApi.db_conn_str, template_name='default_session') as session:
            db_companies = session.query(CompanyBusinessSegment).filter(CompanyBusinessSegment.company_id == 1).all()
            assert len(db_companies) == 0