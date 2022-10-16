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

class TestSectorApi:
    @classmethod
    def setup_class(cls):
        try:
            TestSectorApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestSectorApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestSectorApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestSectorApi.db_conn_str)
                           
                create_default_users(session)


            
            toks = get_access_tokens(client, TestSectorApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestSectorApi.system_access_token = toks[0]
            TestSectorApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_create_sector(self):
        base_url = TestSectorApi.base_url + "/sector"
        body = {'name': "name_one", 'name_code': 'n1'}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestSectorApi.ghelie_access_token}, json=body)             
        assert response.status_code == 401

        response = client.post(base_url, headers={"Authorization": "Bearer " + TestSectorApi.system_access_token}, json=body)             
        assert response.status_code == 201

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestSectorApi.db_conn_str, template_name='default_session') as session:
            db_sector = session.query(Sector).all()
            assert len(db_sector) == 1
            assert db_sector[0].name == "name_one"
            assert db_sector[0].name_code == "n1"
            TestSectorApi.sector_id = db_sector[0].id

    def test_update_sector(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestSectorApi.db_conn_str, template_name='default_session') as session:
            session.query(Sector).delete()
            session.add(Sector(id=1000, name='blabla', name_code='blabla'))

        base_url = TestSectorApi.base_url + "/sector"
        url = base_url + "/" + str(1000)
        body = {'name': "name_one_mod", 'name_code': 'n1_mod'}
        response = client.put(url, headers={"Authorization": "Bearer " + TestSectorApi.system_access_token}, json=body)             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestSectorApi.db_conn_str, template_name='default_session') as session:
            db_sector = session.query(Sector).filter(Sector.id == 1000).all()
            assert len(db_sector) == 1
            assert db_sector[0].name == "name_one_mod"
            assert db_sector[0].name_code == "n1_mod"

    def test_delete_sector(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestSectorApi.db_conn_str, template_name='default_session') as session:
            session.query(Sector).delete()
            session.add(Sector(id=1000, name='blabla', name_code='blabla'))

        base_url = TestSectorApi.base_url + "/sector"
        url = base_url + "/" + str(1000)
        body = {'name': "name_one_mod", 'name_code': 'n1_mod'}
        response = client.delete(url, headers={"Authorization": "Bearer " + TestSectorApi.system_access_token}, json=body)             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestSectorApi.db_conn_str, template_name='default_session') as session:
            db_sector = session.query(Sector).filter(Sector.id == 1000).all()
            assert len(db_sector) == 0