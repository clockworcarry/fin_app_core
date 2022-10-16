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

class TestCompaniesApi:
    @classmethod
    def setup_class(cls):
        try:
            TestCompaniesApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestCompaniesApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestCompaniesApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestCompaniesApi.db_conn_str)
                           
                create_default_users(session)
                
                create_default_companies(session)

                create_default_groups(session)

                create_default_business_segments(session)

                create_default_sectors(session)

                create_default_sector_relations(session)
                
                create_default_industries(session)

                create_default_industry_relations(session)

            
            toks = get_access_tokens(client, TestCompaniesApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestCompaniesApi.system_access_token = toks[0]
            TestCompaniesApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))
        
    def test_get_companies(self):
        base_url = TestCompaniesApi.base_url + "/companies"
        response = client.get(base_url, headers={"Authorization": "Bearer " + TestCompaniesApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 7

        response.sort(key=lambda x: x['company_info']['id'], reverse=False)

        assert response[0]['company_info']['id'] == 1
        assert response[0]['company_info']['ticker'] == "AMD"
        assert response[0]['company_info']['name'] == "Advanced Micro Devices Inc."
        assert response[0]['company_info']['delisted'] == False
        assert len(response[0]['business_segments']) == 1
        assert response[0]['business_segments'][0]['id'] == 1
        assert response[0]['business_segments'][0]['code'] == "AMD.default"
        assert response[0]['business_segments'][0]['display_name'] == "AMD default business"
        assert response[0]['business_segments'][0]['company_id'] == 1

        assert response[1]['company_info']['id'] == 2
        assert response[1]['company_info']['ticker'] == "ZM"
        assert response[1]['company_info']['name'] == "Zoom Video Communications Inc."
        assert response[1]['company_info']['delisted'] == False
        assert len(response[1]['business_segments']) == 1
        assert response[1]['business_segments'][0]['id'] == 2
        assert response[1]['business_segments'][0]['code'] == "ZM.default"
        assert response[1]['business_segments'][0]['display_name'] == "ZM default business"
        assert response[1]['business_segments'][0]['company_id'] == 2

        assert response[2]['company_info']['id'] == 3
        assert response[2]['company_info']['ticker'] == "MSFT"
        assert response[2]['company_info']['name'] == "Microsoft Corp."
        assert response[2]['company_info']['delisted'] == False
        assert len(response[2]['business_segments']) == 2
        response[2]['business_segments'].sort(key=lambda x: x['id'], reverse=False)
        assert response[2]['business_segments'][0]['id'] == 3
        assert response[2]['business_segments'][0]['code'] == "MSFT.default"
        assert response[2]['business_segments'][0]['display_name'] == "MSFT default business"
        assert response[2]['business_segments'][0]['company_id'] == 3
        assert response[2]['business_segments'][1]['id'] == 4
        assert response[2]['business_segments'][1]['code'] == "MSFT.cloud"
        assert response[2]['business_segments'][1]['display_name'] == "MSFT cloud business"
        assert response[2]['business_segments'][1]['company_id'] == 3

        assert response[3]['company_info']['id'] == 4
        assert response[3]['company_info']['ticker'] == "AAPL"
        assert response[3]['company_info']['name'] == "Apple Inc."
        assert response[3]['company_info']['delisted'] == False
        assert len(response[3]['business_segments']) == 1
        assert response[3]['business_segments'][0]['id'] == 5
        assert response[3]['business_segments'][0]['code'] == "AAPL.default"
        assert response[3]['business_segments'][0]['display_name'] == "AAPL default business"
        assert response[3]['business_segments'][0]['company_id'] == 4

        assert response[4]['company_info']['id'] == 5
        assert response[4]['company_info']['ticker'] == "BABA"
        assert response[4]['company_info']['name'] == "Alibaba Group Holdings Ltd."
        assert response[4]['company_info']['delisted'] == False
        assert len(response[4]['business_segments']) == 2
        response[4]['business_segments'].sort(key=lambda x: x['id'], reverse=False)
        assert response[4]['business_segments'][0]['id'] == 6
        assert response[4]['business_segments'][0]['code'] == "BABA.default"
        assert response[4]['business_segments'][0]['display_name'] == "BABA default business"
        assert response[4]['business_segments'][0]['company_id'] == 5
        assert response[4]['business_segments'][1]['id'] == 7
        assert response[4]['business_segments'][1]['code'] == "BABA.cloud"
        assert response[4]['business_segments'][1]['display_name'] == "BABA cloud business"
        assert response[4]['business_segments'][1]['company_id'] == 5

        assert response[5]['company_info']['id'] == 6
        assert response[5]['company_info']['ticker'] == "BAC"
        assert response[5]['company_info']['name'] == "Bank of America"
        assert response[5]['company_info']['delisted'] == False
        assert len(response[5]['business_segments']) == 1
        assert response[5]['business_segments'][0]['id'] == 8
        assert response[5]['business_segments'][0]['code'] == "BAC.default"
        assert response[5]['business_segments'][0]['display_name'] == "BAC default business"
        assert response[5]['business_segments'][0]['company_id'] == 6

        assert response[6]['company_info']['id'] == 7
        assert response[6]['company_info']['ticker'] == "JPM"
        assert response[6]['company_info']['name'] == "JP MORGAN CHASE"
        assert response[6]['company_info']['delisted'] == False
        assert len(response[6]['business_segments']) == 1
        assert response[6]['business_segments'][0]['id'] == 9
        assert response[6]['business_segments'][0]['code'] == "JPM.default"
        assert response[6]['business_segments'][0]['display_name'] == "JPM default business"
        assert response[6]['business_segments'][0]['company_id'] == 7

        #apply sector filter
        params = {'sector_id': 2}
        response = client.get(base_url, headers={"Authorization": "Bearer " + TestCompaniesApi.ghelie_access_token}, params=params)             
        assert response.status_code == 200
        response = response.json()

        response.sort(key=lambda x: x['company_info']['id'], reverse=False)

        assert len(response) == 2
        assert response[0]['company_info']['id'] == 6
        assert response[0]['company_info']['ticker'] == "BAC"
        assert response[0]['company_info']['name'] == "Bank of America"
        assert response[0]['company_info']['delisted'] == False
        assert len(response[0]['business_segments']) == 1
        assert response[0]['business_segments'][0]['id'] == 8
        assert response[0]['business_segments'][0]['code'] == "BAC.default"
        assert response[0]['business_segments'][0]['display_name'] == "BAC default business"
        assert response[0]['business_segments'][0]['company_id'] == 6

        assert response[1]['company_info']['id'] == 7
        assert response[1]['company_info']['ticker'] == "JPM"
        assert response[1]['company_info']['name'] == "JP MORGAN CHASE"
        assert response[1]['company_info']['delisted'] == False
        assert len(response[1]['business_segments']) == 1
        assert response[1]['business_segments'][0]['id'] == 9
        assert response[1]['business_segments'][0]['code'] == "JPM.default"
        assert response[1]['business_segments'][0]['display_name'] == "JPM default business"
        assert response[1]['business_segments'][0]['company_id'] == 7

        #apply industry filters
        params = {'industry_id': [5, 1]}
        response = client.get(base_url, headers={"Authorization": "Bearer " + TestCompaniesApi.ghelie_access_token}, params=params)             
        assert response.status_code == 200
        response = response.json()

        response.sort(key=lambda x: x['company_info']['id'], reverse=False)

        assert len(response) == 3
        assert response[0]['company_info']['id'] == 1
        assert response[0]['company_info']['ticker'] == "AMD"
        assert response[0]['company_info']['name'] == "Advanced Micro Devices Inc."
        assert response[0]['company_info']['delisted'] == False
        assert len(response[0]['business_segments']) == 1
        assert response[0]['business_segments'][0]['id'] == 1
        assert response[0]['business_segments'][0]['code'] == "AMD.default"
        assert response[0]['business_segments'][0]['display_name'] == "AMD default business"
        assert response[0]['business_segments'][0]['company_id'] == 1

        assert response[1]['company_info']['id'] == 3
        assert response[1]['company_info']['ticker'] == "MSFT"
        assert response[1]['company_info']['name'] == "Microsoft Corp."
        assert response[1]['company_info']['delisted'] == False
        assert len(response[1]['business_segments']) == 1
        assert response[1]['business_segments'][0]['id'] == 4
        assert response[1]['business_segments'][0]['code'] == "MSFT.cloud"
        assert response[1]['business_segments'][0]['display_name'] == "MSFT cloud business"
        assert response[1]['business_segments'][0]['company_id'] == 3

        assert response[2]['company_info']['id'] == 5
        assert response[2]['company_info']['ticker'] == "BABA"
        assert response[2]['company_info']['name'] == "Alibaba Group Holdings Ltd."
        assert response[2]['company_info']['delisted'] == False
        assert len(response[2]['business_segments']) == 1
        assert response[2]['business_segments'][0]['id'] == 7
        assert response[2]['business_segments'][0]['code'] == "BABA.cloud"
        assert response[2]['business_segments'][0]['display_name'] == "BABA cloud business"
        assert response[2]['business_segments'][0]['company_id'] == 5

        #apply industry and sector filter
        params = {'industry_id': [5, 1], 'sector_id': 2}
        response = client.get(base_url, headers={"Authorization": "Bearer " + TestCompaniesApi.ghelie_access_token}, params=params)             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 0

        params = {'industry_id': [5, 2], 'sector_id': 2}
        response = client.get(base_url, headers={"Authorization": "Bearer " + TestCompaniesApi.ghelie_access_token}, params=params)             
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 2

        response.sort(key=lambda x: x['company_info']['id'], reverse=False)

        assert response[0]['company_info']['id'] == 6
        assert response[0]['company_info']['ticker'] == "BAC"
        assert response[0]['company_info']['name'] == "Bank of America"
        assert response[0]['company_info']['delisted'] == False
        assert len(response[0]['business_segments']) == 1
        assert response[0]['business_segments'][0]['id'] == 8
        assert response[0]['business_segments'][0]['code'] == "BAC.default"
        assert response[0]['business_segments'][0]['display_name'] == "BAC default business"
        assert response[0]['business_segments'][0]['company_id'] == 6

        assert response[1]['company_info']['id'] == 7
        assert response[1]['company_info']['ticker'] == "JPM"
        assert response[1]['company_info']['name'] == "JP MORGAN CHASE"
        assert response[1]['company_info']['delisted'] == False
        assert len(response[1]['business_segments']) == 1
        assert response[1]['business_segments'][0]['id'] == 9
        assert response[1]['business_segments'][0]['code'] == "JPM.default"
        assert response[1]['business_segments'][0]['display_name'] == "JPM default business"
        assert response[1]['business_segments'][0]['company_id'] == 7
