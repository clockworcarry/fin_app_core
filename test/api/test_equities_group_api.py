from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from api.routers.company_metrics_api import *

import api.constants as api_constants
from passlib.context import CryptContext

client = TestClient(app)

class TestEquitiesGroupApi:
    @classmethod
    def setup_class(cls):
        try:
            TestEquitiesGroupApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestEquitiesGroupApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestEquitiesGroupApi.db_conn_str, template_name='default_session') as session:
                #create users
                cleanup_db_from_db_str(TestEquitiesGroupApi.db_conn_str)
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                hashed_pwd = pwd_context.hash('system')
                account_system = Account(id=1, userName='system', password=hashed_pwd, email='email@gmail.com', phone='514-222-2222', disabled=False)
                session.add(account_system)
                session.flush()
                
                #create companies
                amd_company = Company(id=1, ticker='AMD', name='Advanced Micro Devices Inc.', locked=False, delisted=False)
                zm_company = Company(id=2, ticker='ZM', name='Zoom Video Communications Inc.', locked=False, delisted=False)
                msft_company = Company(id=3, ticker='MSFT', name='Microsoft Corp.', locked=False, delisted=False)
                aapl_company = Company(id=4, ticker='AAPL', name='Apple Inc.', locked=False, delisted=False)
                baba_company = Company(id=5, ticker='BABA', name='Alibaba Group Holdings Ltd.', locked=False, delisted=False)
                session.add_all([amd_company, zm_company, msft_company, aapl_company, baba_company])
                session.flush()

                #create business segments
                default_bus_segment_amd = CompanyBusinessSegment(id=1, company_id=amd_company.id, code='AMD.default', display_name='AMD default business')
                default_bus_segment_zm = CompanyBusinessSegment(id=2, company_id=zm_company.id, code='ZM.default', display_name='ZM default business')
                default_bus_segment_msft = CompanyBusinessSegment(id=3, company_id=msft_company.id, code='MSFT.default', display_name='MSFT default business')
                cloud_bus_segment_msft = CompanyBusinessSegment(id=4, company_id=msft_company.id, code='MSFT.cloud', display_name='MSFT cloud business')
                default_bus_segment_aapl = CompanyBusinessSegment(id=5, company_id=aapl_company.id, code='AAPL.default', display_name='AAPL default business')
                default_bus_segment_baba = CompanyBusinessSegment(id=6, company_id=baba_company.id, code='BABA.default', display_name='BABA default business')
                cloud_bus_segment_baba = CompanyBusinessSegment(id=7, company_id=baba_company.id, code='BABA.cloud', display_name='BABA cloud business')
                session.add_all([default_bus_segment_amd, default_bus_segment_zm, default_bus_segment_msft, cloud_bus_segment_msft, default_bus_segment_aapl, default_bus_segment_baba, cloud_bus_segment_baba])
                session.flush()

                #create groups
                group_defaults = CompanyGroup(id=1, name_code='''defaults_grp''', name='Group Of All Defaults', creator_id=account_system.id)
                group_cloud = CompanyGroup(id=2, name_code='cloud_grp', name='Group Of Cloud Businesses', creator_id=account_system.id)
                session.add_all([group_defaults, group_cloud])
                session.flush()
                TestEquitiesGroupApi.group_defaults_id = group_defaults.id
                TestEquitiesGroupApi.group_cloud_id = group_cloud.id

                #add business segments to groups
                session.add(CompanyInGroup(company_business_segment_id=default_bus_segment_amd.id, group_id=group_defaults.id))
                session.add(CompanyInGroup(company_business_segment_id=default_bus_segment_zm.id, group_id=group_defaults.id))
                session.add(CompanyInGroup(company_business_segment_id=default_bus_segment_msft.id, group_id=group_defaults.id))
                session.add(CompanyInGroup(company_business_segment_id=default_bus_segment_aapl.id, group_id=group_defaults.id))
                session.add(CompanyInGroup(company_business_segment_id=default_bus_segment_baba.id, group_id=group_defaults.id))
                session.add(CompanyInGroup(company_business_segment_id=cloud_bus_segment_msft.id, group_id=group_cloud.id))
                session.add(CompanyInGroup(company_business_segment_id=cloud_bus_segment_baba.id, group_id=group_cloud.id))

                #create metric classifications
                metric_cls_income_statement = MetricClassification(id=1, category_name='Income Statement', parent_category_id=None, creator_id=account_system.id)
                metric_cls_cloud_metrics = MetricClassification(id=2, category_name='Cloud Metrics', parent_category_id=None, creator_id=account_system.id)
                session.add_all([metric_cls_income_statement, metric_cls_cloud_metrics])
                session.flush()
                metric_cls_revenue = MetricClassification(id=3, category_name='Revenue', parent_category_id=metric_cls_income_statement.id, creator_id=account_system.id)
                metric_cls_ebitda = MetricClassification(id=4, category_name='EBITDA', parent_category_id=metric_cls_income_statement.id, creator_id=account_system.id)
                session.add_all([metric_cls_revenue, metric_cls_ebitda])
                session.flush()

                #associate user to classifications
                session.add(UserMetricClassification(metric_classification_id=metric_cls_income_statement.id, account_id=account_system.id))
                session.add(UserMetricClassification(metric_classification_id=metric_cls_cloud_metrics.id, account_id=account_system.id))
                session.add(UserMetricClassification(metric_classification_id=metric_cls_revenue.id, account_id=account_system.id))
                session.add(UserMetricClassification(metric_classification_id=metric_cls_ebitda.id, account_id=account_system.id))

                #create metric descriptions
                metric_desc_rev_2021 = MetricDescription(id=1, code='rev_2021', display_name='2021 Revenue', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                        year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                        metric_classification_id=metric_cls_revenue.id, creator_id=account_system.id)
                
                metric_desc_revenue_ttm = MetricDescription(id=2, code='rev_ttm', display_name='Trailing 12 Months Revenue', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=METRIC_DURATION_QUARTER, \
                                                            year_recorded=2022, quarter_recorded=3, metric_duration=4, look_back=True, metric_fixed_year=-1, metric_fixed_quarter=-1, \
                                                            metric_classification_id=metric_cls_revenue.id, creator_id=account_system.id)
                
                metric_desc_ebitda_2021 = MetricDescription(id=3, code='ebitda_2021', display_name='2021 EBITDA', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                            year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                            metric_classification_id=metric_cls_ebitda.id, creator_id=account_system.id)
                
                metric_desc_ebitda_ttm = MetricDescription(id=4, code='ebitda_ttm', display_name='Trailing 12 Months EBITDA', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=METRIC_DURATION_QUARTER, \
                                                            year_recorded=2022, quarter_recorded=3, metric_duration=4, look_back=True, metric_fixed_year=-1, metric_fixed_quarter=-1, \
                                                            metric_classification_id=metric_cls_ebitda.id, creator_id=account_system.id)

                metric_desc_nb_enterprise_customers = MetricDescription(id=5, code='nb_cloud_customers_2021', display_name='2021 Number of Cloud Customers', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                            year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                            metric_classification_id=metric_cls_cloud_metrics.id, creator_id=account_system.id)

                session.add_all([metric_desc_rev_2021, metric_desc_revenue_ttm, metric_desc_ebitda_2021, metric_desc_ebitda_ttm, metric_desc_nb_enterprise_customers])
                session.flush()

                #add metric descriptions to appropriate groups
                session.add(CompanyGroupMetricDescription(metric_description_id=metric_desc_rev_2021.id, company_group_id=group_defaults.id))
                session.add(CompanyGroupMetricDescription(metric_description_id=metric_desc_revenue_ttm.id, company_group_id=group_defaults.id))
                session.add(CompanyGroupMetricDescription(metric_description_id=metric_desc_ebitda_2021.id, company_group_id=group_defaults.id))
                session.add(CompanyGroupMetricDescription(metric_description_id=metric_desc_ebitda_ttm.id, company_group_id=group_defaults.id))
                session.add(CompanyGroupMetricDescription(metric_description_id=metric_desc_nb_enterprise_customers.id, company_group_id=group_cloud.id))

                #create second non-system user
                hashed_pwd = pwd_context.hash('ghelie123')
                ghelie_user = Account(id=2, userName='ghelie', password=hashed_pwd, email='ghelie@gmail.com', phone='514-214-6004', disabled=False)
                session.add(ghelie_user)
                session.flush()

                #associate metric data to descriptions

                #AMD
                session.add(MetricData(id=1, metric_description_id=metric_desc_rev_2021.id, company_business_segment_id=default_bus_segment_amd.id, data=200000, user_id=1))
                session.add(MetricData(id=50, metric_description_id=metric_desc_rev_2021.id, company_business_segment_id=default_bus_segment_amd.id, data=4000, user_id=2))
                session.add(MetricData(id=2, metric_description_id=metric_desc_revenue_ttm.id, company_business_segment_id=default_bus_segment_amd.id, data=220000, user_id=1))
                session.add(MetricData(id=3, metric_description_id=metric_desc_ebitda_2021.id, company_business_segment_id=default_bus_segment_amd.id, data=30000, user_id=1))
                session.add(MetricData(id=4, metric_description_id=metric_desc_ebitda_ttm.id, company_business_segment_id=default_bus_segment_amd.id, data=31000, user_id=1))

                #ZM
                session.add(MetricData(id=5, metric_description_id=metric_desc_rev_2021.id, company_business_segment_id=default_bus_segment_zm.id, data=40000, user_id=1))
                session.add(MetricData(id=6, metric_description_id=metric_desc_revenue_ttm.id, company_business_segment_id=default_bus_segment_zm.id, data=40500, user_id=1))
                session.add(MetricData(id=7, metric_description_id=metric_desc_ebitda_2021.id, company_business_segment_id=default_bus_segment_zm.id, data=10000, user_id=1))
                session.add(MetricData(id=8, metric_description_id=metric_desc_ebitda_ttm.id, company_business_segment_id=default_bus_segment_zm.id, data=11000, user_id=1))

                #MSFT
                session.add(MetricData(id=9, metric_description_id=metric_desc_rev_2021.id, company_business_segment_id=default_bus_segment_msft.id, data=10000000, user_id=1))
                session.add(MetricData(id=10, metric_description_id=metric_desc_revenue_ttm.id, company_business_segment_id=default_bus_segment_msft.id, data=12000000, user_id=1))
                session.add(MetricData(id=11, metric_description_id=metric_desc_ebitda_2021.id, company_business_segment_id=default_bus_segment_msft.id, data=100000, user_id=1))
                session.add(MetricData(id=12, metric_description_id=metric_desc_ebitda_ttm.id, company_business_segment_id=default_bus_segment_msft.id, data=110000, user_id=1))
                session.add(MetricData(id=13, metric_description_id=metric_desc_nb_enterprise_customers.id, company_business_segment_id=cloud_bus_segment_msft.id, data=7000, user_id=1))

                #AAPL
                session.add(MetricData(id=14, metric_description_id=metric_desc_rev_2021.id, company_business_segment_id=default_bus_segment_aapl.id, data=50000, user_id=1))
                session.add(MetricData(id=15, metric_description_id=metric_desc_revenue_ttm.id, company_business_segment_id=default_bus_segment_aapl.id, data=40500, user_id=1))
                session.add(MetricData(id=16, metric_description_id=metric_desc_ebitda_2021.id, company_business_segment_id=default_bus_segment_aapl.id, data=13000, user_id=1))
                session.add(MetricData(id=17, metric_description_id=metric_desc_ebitda_ttm.id, company_business_segment_id=default_bus_segment_aapl.id, data=14000, user_id=1))

                #BABA
                session.add(MetricData(id=18, metric_description_id=metric_desc_rev_2021.id, company_business_segment_id=default_bus_segment_baba.id, data=300, user_id=1))
                session.add(MetricData(id=19, metric_description_id=metric_desc_revenue_ttm.id, company_business_segment_id=default_bus_segment_baba.id, data=310, user_id=1))
                session.add(MetricData(id=20, metric_description_id=metric_desc_ebitda_2021.id, company_business_segment_id=default_bus_segment_baba.id, data=200, user_id=1))
                session.add(MetricData(id=21, metric_description_id=metric_desc_ebitda_ttm.id, company_business_segment_id=default_bus_segment_baba.id, data=210, user_id=1))
                session.add(MetricData(id=22, metric_description_id=metric_desc_nb_enterprise_customers.id, company_business_segment_id=cloud_bus_segment_baba.id, data=500, user_id=1))
            
            login_url = TestEquitiesGroupApi.base_url + "/account/token"
            input = {'username': 'system', 'password': 'system'}
            response = client.post(login_url, headers = {'Content-Type': 'application/x-www-form-urlencoded'}, data=input)
            assert response.status_code == 200
            response = response.json()
            TestEquitiesGroupApi.access_token = response['access_token']

            input = {'username': 'ghelie', 'password': 'ghelie123'}
            response = client.post(login_url, headers = {'Content-Type': 'application/x-www-form-urlencoded'}, data=input)
            assert response.status_code == 200
            response = response.json()
            TestEquitiesGroupApi.ghelie_access_token = response['access_token']
        
        except Exception as gen_ex:
            print(str(gen_ex))

    
    def test_get_group_metrics(self):
        base_url = TestEquitiesGroupApi.base_url + "/equities/group/metrics/"
        
        url = base_url + str(TestEquitiesGroupApi.group_defaults_id)
        response = client.get(url, headers={"Authorization": "Bearer " + TestEquitiesGroupApi.ghelie_access_token})             
        assert response.status_code == 200
        response = response.json()
        
        assert response['group_info']['id'] == TestEquitiesGroupApi.group_defaults_id
        assert response['group_info']['name_code'] == "defaults_grp"
        assert response['group_info']['name'] == "Group Of All Defaults"

        assert len(response['business_segments']) == 5
        
        bs = response['business_segments'][0]
        assert bs['id'] == 1
        assert bs['code'] == "AMD.default"
        assert bs['display_name'] == "AMD default business"
        assert bs['company_id'] == 1
        assert bs['company_name'] == "Advanced Micro Devices Inc."
        assert bs['company_ticker'] == "AMD"
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
        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 4000
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
        assert category_metrics[1]['data'] == 220000
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
        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 30000
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
        assert category_metrics[1]['data'] == 31000
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


        bs = response['business_segments'][1]
        assert bs['id'] == 2
        assert bs['code'] == "ZM.default"
        assert bs['display_name'] == "ZM default business"
        assert bs['company_id'] == 2
        assert bs['company_name'] == "Zoom Video Communications Inc."
        assert bs['company_ticker'] == "ZM"
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
        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 40000
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
        assert category_metrics[1]['data'] == 40500
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
        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 10000
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
        assert category_metrics[1]['data'] == 11000
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
        
        
        bs = response['business_segments'][2]
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
        

        bs = response['business_segments'][3]
        assert bs['id'] == 5
        assert bs['code'] == "AAPL.default"
        assert bs['display_name'] == "AAPL default business"
        assert bs['company_id'] == 4
        assert bs['company_name'] == "Apple Inc."
        assert bs['company_ticker'] == "AAPL"
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
        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 50000
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
        assert category_metrics[1]['data'] == 40500
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
        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 13000
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
        assert category_metrics[1]['data'] == 14000
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


        bs = response['business_segments'][4]
        assert bs['id'] == 6
        assert bs['code'] == "BABA.default"
        assert bs['display_name'] == "BABA default business"
        assert bs['company_id'] == 5
        assert bs['company_name'] == "Alibaba Group Holdings Ltd."
        assert bs['company_ticker'] == "BABA"
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
        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 300
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
        assert category_metrics[1]['data'] == 310
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
        assert len(category['categories']) == 0
        category_metrics = category['metrics']
        assert category_metrics[0]['data'] == 200
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
        assert category_metrics[1]['data'] == 210
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


        url = base_url + str(TestEquitiesGroupApi.group_cloud_id)
        response = client.get(url, headers={"Authorization": "Bearer " + TestEquitiesGroupApi.access_token})             
        assert response.status_code == 200
        response = response.json()
        
        assert response['group_info']['id'] == TestEquitiesGroupApi.group_cloud_id
        assert response['group_info']['name_code'] == "cloud_grp"
        assert response['group_info']['name'] == "Group Of Cloud Businesses"

        assert len(response['business_segments']) == 2

        bs = response['business_segments'][0]
        assert bs['id'] == 4
        assert bs['code'] == "MSFT.cloud"
        assert bs['display_name'] == "MSFT cloud business"
        assert bs['company_id'] == 3
        assert bs['company_name'] == "Microsoft Corp."
        assert bs['company_ticker'] == "MSFT"
        assert len(bs['metric_categories']) == 1
        cloud_category = bs['metric_categories'][0]
        assert cloud_category['id'] == 2
        assert cloud_category['category_name'] == "Cloud Metrics"
        assert len(cloud_category['metrics']) == 1
        assert len(cloud_category['categories']) == 0
        category_metrics = cloud_category['metrics']
        assert category_metrics[0]['data'] == 7000
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

        bs = response['business_segments'][1]
        assert bs['id'] == 7
        assert bs['code'] == "BABA.cloud"
        assert bs['display_name'] == "BABA cloud business"
        assert bs['company_id'] == 5
        assert bs['company_name'] == "Alibaba Group Holdings Ltd."
        assert bs['company_ticker'] == "BABA"
        assert len(bs['metric_categories']) == 1
        cloud_category = bs['metric_categories'][0]
        assert cloud_category['id'] == 2
        assert cloud_category['category_name'] == "Cloud Metrics"
        assert len(cloud_category['metrics']) == 1
        assert len(cloud_category['categories']) == 0
        category_metrics = cloud_category['metrics']
        assert category_metrics[0]['data'] == 500
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

    def test_add_metric_description_to_group(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestEquitiesGroupApi.db_conn_str, template_name='default_session') as session:
            metric_test_desc = MetricDescription(id=1000, code='test_metric', display_name='Test Metric', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                        year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                        metric_classification_id=None, creator_id=None)
            session.add(metric_test_desc)
        
        base_url = TestEquitiesGroupApi.base_url + "/equities/group/metricDescription/"
        url = base_url + "1" + "/" + "1000"
        response = client.put(url, headers={"Authorization": "Bearer " + TestEquitiesGroupApi.access_token})             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestEquitiesGroupApi.db_conn_str, template_name='default_session') as session:
            db_rows = session.query(CompanyGroupMetricDescription, MetricDescription) \
                             .join(MetricDescription, CompanyGroupMetricDescription.metric_description_id == MetricDescription.id) \
                             .filter(CompanyGroupMetricDescription.company_group_id == 1).all()
            
            assert len(db_rows) == 5
            new_metric = None
            for cgmd, md in db_rows:
                if cgmd.metric_description_id == 1000:
                    new_metric = md
                    assert cgmd.company_group_id == 1
            
            assert new_metric is not None
            assert new_metric.id == 1000
            assert new_metric.code == "test_metric"
            assert new_metric.display_name == "Test Metric"
            assert new_metric.metric_data_type == METRIC_TYPE_NUMBER
            assert new_metric.metric_duration_type == -1
            assert new_metric.year_recorded == -1
            assert new_metric.quarter_recorded == -1
            assert new_metric.metric_duration == -1
            assert new_metric.look_back == True
            assert new_metric.metric_fixed_year == 2021
            assert new_metric.metric_fixed_quarter == -1
            assert new_metric.metric_classification_id == None
            assert new_metric.creator_id == None
        
            session.delete(new_metric)

    
    def test_add_business_segment_to_group(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestEquitiesGroupApi.db_conn_str, template_name='default_session') as session:
            bs_test = CompanyBusinessSegment(id=1000, company_id=1, code='AMD.cloud', display_name='AMD cloud business')
            session.add(bs_test)
        
        base_url = TestEquitiesGroupApi.base_url + "/equities/group/businessSegment/"
        url = base_url + "2" + "/" + "1000"
        response = client.put(url, headers={"Authorization": "Bearer " + TestEquitiesGroupApi.access_token})             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestEquitiesGroupApi.db_conn_str, template_name='default_session') as session:
            db_rows = session.query(CompanyInGroup, CompanyBusinessSegment) \
                             .join(CompanyBusinessSegment, CompanyInGroup.company_business_segment_id == CompanyBusinessSegment.id) \
                             .filter(CompanyInGroup.group_id == 2).all()
            
            assert len(db_rows) == 3
            new_bs = None
            for cig, cbs in db_rows:
                if cig.company_business_segment_id == 1000:
                    new_bs = cbs
                    assert cig.group_id == 2
            
            assert new_bs is not None
            assert new_bs.company_id == 1
            assert new_bs.code == "AMD.cloud"
            assert new_bs.display_name == "AMD cloud business"

            session.delete(new_bs)


    def test_remove_metric_description_from_group(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestEquitiesGroupApi.db_conn_str, template_name='default_session') as session:
            db_rows = session.query(CompanyGroupMetricDescription, MetricDescription) \
                             .join(MetricDescription, CompanyGroupMetricDescription.metric_description_id == MetricDescription.id) \
                             .filter(CompanyGroupMetricDescription.company_group_id == 1).all()
            
            assert len(db_rows) == 4
            metric_to_delete = None
            for cgmd, md in db_rows:
                if cgmd.metric_description_id == 1:
                    metric_to_delete = md
            
            assert metric_to_delete is not None
            assert metric_to_delete.id == 1
            assert metric_to_delete.code == "rev_2021"

        
        base_url = TestEquitiesGroupApi.base_url + "/equities/group/metricDescription/"
        url = base_url + "1" + "/" + "1000"
        response = client.delete(url, headers={"Authorization": "Bearer " + TestEquitiesGroupApi.access_token})             
        assert response.status_code == 500
        response = response.json()
        assert response['detail'] == "Could not find metric description with id: 1000 in group with id: 1"

        url = base_url + "1" + "/" + "1"
        response = client.delete(url, headers={"Authorization": "Bearer " + TestEquitiesGroupApi.access_token})
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestEquitiesGroupApi.db_conn_str, template_name='default_session') as session:
            db_rows = session.query(CompanyGroupMetricDescription, MetricDescription) \
                             .join(MetricDescription, CompanyGroupMetricDescription.metric_description_id == MetricDescription.id) \
                             .filter(CompanyGroupMetricDescription.company_group_id == 1).all()
            
            assert len(db_rows) == 3
            metric_to_delete = None
            for cgmd, md in db_rows:
                if cgmd.metric_description_id == 1:
                    metric_to_delete = md
            
            assert metric_to_delete is None


    def test_remove_business_segment_from_group(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestEquitiesGroupApi.db_conn_str, template_name='default_session') as session:
            db_rows = session.query(CompanyInGroup, CompanyBusinessSegment) \
                             .join(CompanyBusinessSegment, CompanyInGroup.company_business_segment_id == CompanyBusinessSegment.id) \
                             .filter(CompanyInGroup.group_id == 2).all()
            
            assert len(db_rows) == 2
            bs_to_delete = None
            for cig, cbs in db_rows:
                if cig.company_business_segment_id == 7:
                    bs_to_delete = cbs
                    assert cig.group_id == 2
            
            assert bs_to_delete is not None
            assert bs_to_delete.company_id == 5
            assert bs_to_delete.code == "BABA.cloud"
            assert bs_to_delete.display_name == "BABA cloud business"

        
        base_url = TestEquitiesGroupApi.base_url + "/equities/group/businessSegment/"
        url = base_url + "2" + "/" + "1000"
        response = client.delete(url, headers={"Authorization": "Bearer " + TestEquitiesGroupApi.access_token})             
        assert response.status_code == 500
        response = response.json()
        assert response['detail'] == "Could not find business segment with id: 1000 in group with id: 2"

        url = base_url + "2" + "/" + "7"
        response = client.delete(url, headers={"Authorization": "Bearer " + TestEquitiesGroupApi.access_token})
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestEquitiesGroupApi.db_conn_str, template_name='default_session') as session:
            db_rows = session.query(CompanyInGroup, CompanyBusinessSegment) \
                             .join(CompanyBusinessSegment, CompanyInGroup.company_business_segment_id == CompanyBusinessSegment.id) \
                             .filter(CompanyInGroup.group_id == 2).all()
            
            assert len(db_rows) == 1
            bs_to_delete = None
            for cig, cbs in db_rows:
                if cig.company_business_segment_id == 7:
                    bs_to_delete = cbs
                    assert cig.group_id == 2
            
            assert bs_to_delete is None
            