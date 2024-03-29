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

class TestIndustryApi:
    @classmethod
    def setup_class(cls):
        try:
            TestIndustryApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestIndustryApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestIndustryApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestIndustryApi.db_conn_str)
                           
                create_default_users(session)

                create_default_sectors(session)
            
            toks = get_access_tokens(client, TestIndustryApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestIndustryApi.system_access_token = toks[0]
            TestIndustryApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_create_industry(self):
        base_url = TestIndustryApi.base_url + "/industry"
        body = {'sector_id': 1, 'name': "industry_one", 'name_code': 'i1'}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestIndustryApi.ghelie_access_token}, json=body)             
        assert response.status_code == 401

        response = client.post(base_url, headers={"Authorization": "Bearer " + TestIndustryApi.system_access_token}, json=body)             
        assert response.status_code == 201

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestIndustryApi.db_conn_str, template_name='default_session') as session:
            db_industries = session.query(Industry).all()
            assert len(db_industries) == 1
            assert db_industries[0].name == "industry_one"
            assert db_industries[0].name_code == "i1"

    def test_update_industry(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestIndustryApi.db_conn_str, template_name='default_session') as session:
            session.query(Industry).delete()
            session.add(Industry(id=1000, name='industry_one', name_code='i1', sector_id=1))

        base_url = TestIndustryApi.base_url + "/industry"
        url = base_url + "/" + str(1000)
        body = {'sector_id': 1, 'name': "blabla", 'name_code': 'blabla'}
        response = client.put(url, headers={"Authorization": "Bearer " + TestIndustryApi.system_access_token}, json=body)             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestIndustryApi.db_conn_str, template_name='default_session') as session:
            db_industries = session.query(Industry).filter(Industry.id == 1000).all()
            assert len(db_industries) == 1
            assert db_industries[0].name == "blabla"
            assert db_industries[0].name_code == "blabla"

    def test_delete_industry(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestIndustryApi.db_conn_str, template_name='default_session') as session:
            session.query(Industry).delete()
            session.add(Industry(id=1000, name='industry_one', name_code='i1', sector_id=1))

        base_url = TestIndustryApi.base_url + "/industry"
        url = base_url + "/" + str(1000)
        response = client.delete(url, headers={"Authorization": "Bearer " + TestIndustryApi.system_access_token})             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestIndustryApi.db_conn_str, template_name='default_session') as session:
            db_sector = session.query(Sector).filter(Sector.id == 1000).all()
            assert len(db_sector) == 0