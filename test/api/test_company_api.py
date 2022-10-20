from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str, create_default_groups, create_default_industries, create_default_industry_relations, create_default_sector_relations, create_default_sectors, create_default_users, get_access_tokens

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from  test.test_utils import cleanup_db_from_db_str, create_default_business_segments, create_default_companies, create_system_user

import api.constants as api_constants
from passlib.context import CryptContext

from db.models import *

client = TestClient(app)

class TestCompanyApi:
    @classmethod
    def setup_class(cls):
        try:
            TestCompanyApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestCompanyApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestCompanyApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestCompanyApi.db_conn_str)
                           
                create_default_users(session)
            
            toks = get_access_tokens(client, TestCompanyApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestCompanyApi.system_access_token = toks[0]
            TestCompanyApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_create_company(self):
        base_url = TestCompanyApi.base_url + "/company"
        body = {'ticker': "AMZN", 'name': 'Amazon', 'delisted': False, 'creator_id': 2}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestCompanyApi.ghelie_access_token}, json=body)             
        assert response.status_code == 201

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyApi.db_conn_str, template_name='default_session') as session:
            db_companies = session.query(Company).all()
            assert len(db_companies) == 1
            assert db_companies[0].name == "Amazon"
            assert db_companies[0].ticker == "AMZN"
            assert db_companies[0].delisted == False
            assert db_companies[0].creator_id == 2
            
            db_bs = session.query(CompanyBusinessSegment).all()
            assert len(db_bs) == 1
            assert db_bs[0].code == "AMZN.default"
            assert db_bs[0].display_name == "AMZN default business segment"
            assert db_bs[0].company_id == db_companies[0].id

    def test_update_company(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyApi.db_conn_str, template_name='default_session') as session:
            session.query(Company).delete()
            session.add(Company(id=1000, name='cpny_one', ticker='c1', delisted=False, creator_id=2))

        base_url = TestCompanyApi.base_url + "/company"
        url = base_url + "/" + str(1000)
        body = {'name': "cpny_one_mod", 'ticker': 'c1_mod', 'delisted': False, 'creator_id': 2}
        response = client.put(url, headers={"Authorization": "Bearer " + TestCompanyApi.system_access_token}, json=body)             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyApi.db_conn_str, template_name='default_session') as session:
            db_companies = session.query(Company).filter(Company.id == 1000).all()
            assert len(db_companies) == 1
            assert db_companies[0].name == "cpny_one_mod"
            assert db_companies[0].ticker == "c1_mod"
            assert db_companies[0].delisted == False
            assert db_companies[0].creator_id == 2

    def test_get_company(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyApi.db_conn_str, template_name='default_session') as session:
            create_default_companies(session)
            session.flush()

            create_default_business_segments(session)
            session.flush()
        
        base_url = TestCompanyApi.base_url + "/company"
        url = base_url + "/3"
        response = client.get(url, headers={"Authorization": "Bearer " + TestCompanyApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        assert response['company_info']['id'] == 3
        assert response['company_info']['ticker'] == "MSFT"
        assert response['company_info']['name'] == "Microsoft Corp."
        assert response['company_info']['delisted'] == False
        assert response['company_info']['creator_id'] == 1
        
        assert len(response['business_segments']) == 2
        response['business_segments'].sort(key=lambda x: x['id'], reverse=False)

        assert response['business_segments'][0]['id'] == 3
        assert response['business_segments'][0]['code'] == "MSFT.default"
        assert response['business_segments'][0]['display_name'] == "MSFT default business"
        assert response['business_segments'][0]['company_id'] == 3
        assert response['business_segments'][1]['id'] == 4
        assert response['business_segments'][1]['code'] == "MSFT.cloud"
        assert response['business_segments'][1]['display_name'] == "MSFT cloud business"
        assert response['business_segments'][1]['company_id'] == 3

    def test_delete_company(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyApi.db_conn_str, template_name='default_session') as session:
            session.query(Company).delete()
            session.add(Company(id=1000, name='cpny_one', ticker='c1', delisted=False, creator_id=2))
        
        base_url = TestCompanyApi.base_url + "/company"
        url = base_url + "/1000"
        response = client.delete(url, headers={"Authorization": "Bearer " + TestCompanyApi.ghelie_access_token})             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyApi.db_conn_str, template_name='default_session') as session:
            db_companies = session.query(Company).all()
            assert len(db_companies) == 0