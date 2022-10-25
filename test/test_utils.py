from db.models import *
from db.company_financials import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from passlib.context import CryptContext

def cleanup_db_conn_from_conn_obj(conn):
    try:
        with conn.begin():
            stmt = delete(Account.__table__)
            conn.execute(stmt)

            """stmt = delete(AccountTrade.__table__)
            conn.execute(stmt)"""
            
            stmt = delete(Company.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyBusinessSegment.__table__)
            conn.execute(stmt)

            """stmt = delete(CompanyDevelopment.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyExchangeRelation.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyFinancialData.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyFundamentalRatios.__table__)
            conn.execute(stmt)"""

            stmt = delete(CompanyGroup.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyGroupMetricDescription.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyGroupMetricDescription.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyInGroup.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyIndustryRelation.__table__)
            conn.execute(stmt)

            stmt = delete(CompanySectorRelation.__table__)
            conn.execute(stmt)

            """stmt = delete(CompanySummary.__table__)
            conn.execute(stmt)

            stmt = delete(CountryInfo.__table__)
            conn.execute(stmt)"""

            stmt = delete(CronJobRun.__table__)
            conn.execute(stmt)

            """stmt = delete(CurrencyBarData.__table__)
            conn.execute(stmt)

            stmt = delete(EquityBarData.__table__)
            conn.execute(stmt)

            stmt = delete(Exchange.__table__)
            conn.execute(stmt)"""

            stmt = delete(Industry.__table__)
            conn.execute(stmt)

            stmt = delete(Log.__table__)
            conn.execute(stmt)

            stmt = delete(MetricClassification.__table__)
            conn.execute(stmt)

            stmt = delete(MetricData.__table__)
            conn.execute(stmt)

            stmt = delete(MetricDescription.__table__)
            conn.execute(stmt)
            
            stmt = delete(ScreenerPreset.__table__)
            conn.execute(stmt)

            stmt = delete(ScreenerPresetData.__table__)
            conn.execute(stmt)

            stmt = delete(Sector.__table__)
            conn.execute(stmt)

            stmt = delete(UserCompanyGroup.__table__)
            conn.execute(stmt)

            stmt = delete(UserMetricClassification.__table__)
            conn.execute(stmt)

            stmt = delete(UserMetricDescription.__table__)
            conn.execute(stmt)

            stmt = delete(UserScreenerPreset.__table__)
            conn.execute(stmt)

    except Exception as gen_ex:
        print(str(gen_ex))

def cleanup_db_from_db_str(db_conn_str, keep_users = False):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=db_conn_str, template_name='default_session') as session:
            if not keep_users:
                session.query(Account).delete()
            #session.query(AccountTrade).delete()
            session.query(Company).delete()
            session.query(CompanyBusinessSegment).delete()
            #session.query(CompanyDevelopment).delete()
            #session.query(CompanyExchangeRelation).delete()
            #session.query(CompanyFinancialData).delete()
            #session.query(CompanyFundamentalRatios).delete()
            session.query(CompanyGroup).delete()
            session.query(CompanyGroupMetricDescription).delete()
            session.query(CompanyInGroup).delete()
            session.query(CompanyIndustryRelation).delete()
            session.query(CompanySectorRelation).delete()
            #session.query(CompanySummary).delete()
            #session.query(CountryInfo).delete()
            session.query(CronJobRun).delete()
            #session.query(CurrencyBarData).delete()
            #session.query(EquityBarData).delete()
            #session.query(Exchange).delete()
            session.query(Industry).delete()
            session.query(Log).delete()
            session.query(MetricClassification).delete()
            session.query(MetricData).delete()
            session.query(MetricDescription).delete()
            session.query(ScreenerPreset).delete()
            session.query(ScreenerPresetData).delete()
            session.query(Sector).delete()
            session.query(UserCompanyGroup).delete()
            session.query(UserMetricClassification).delete()
            session.query(UserMetricDescription).delete()
            session.query(UserScreenerPreset).delete()

    except Exception as gen_ex:
        print(str(gen_ex))

def create_system_user(session):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_pwd = pwd_context.hash('system')
    account_system = Account(id=1, userName='system', password=hashed_pwd, email='email@gmail.com', phone='514-222-2222', disabled=False)
    session.add(account_system)
    session.flush()


def create_default_users(session):
    create_system_user(session)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_pwd = pwd_context.hash('ghelie123')
    ghelie_user = Account(id=2, userName='ghelie', password=hashed_pwd, email='ghelie@gmail.com', phone='514-214-6004', disabled=False)
    session.add(ghelie_user)
    session.flush()

def create_default_companies(session):
    amd_company = Company(id=1, ticker='AMD', name='Advanced Micro Devices Inc.', delisted=False, creator_id=1)
    zm_company = Company(id=2, ticker='ZM', name='Zoom Video Communications Inc.', delisted=False, creator_id=1)
    msft_company = Company(id=3, ticker='MSFT', name='Microsoft Corp.', delisted=False, creator_id=1)
    aapl_company = Company(id=4, ticker='AAPL', name='Apple Inc.', delisted=False, creator_id=1)
    baba_company = Company(id=5, ticker='BABA', name='Alibaba Group Holdings Ltd.', delisted=False, creator_id=1)
    bac_company = Company(id=6, ticker='BAC', name='Bank of America', delisted=False, creator_id=1)
    jpm_company = Company(id=7, ticker='JPM', name='JP MORGAN CHASE', delisted=False, creator_id=1)
    session.add_all([amd_company, zm_company, msft_company, aapl_company, baba_company, bac_company, jpm_company])
    session.flush()

def create_default_business_segments(session):
    default_bus_segment_amd = CompanyBusinessSegment(id=1, company_id=1, code='AMD.default', display_name='AMD default business', creator_id=1)
    default_bus_segment_zm = CompanyBusinessSegment(id=2, company_id=2, code='ZM.default', display_name='ZM default business', creator_id=1)
    default_bus_segment_msft = CompanyBusinessSegment(id=3, company_id=3, code='MSFT.default', display_name='MSFT default business', creator_id=1)
    cloud_bus_segment_msft = CompanyBusinessSegment(id=4, company_id=3, code='MSFT.cloud', display_name='MSFT cloud business', creator_id=1)
    default_bus_segment_aapl = CompanyBusinessSegment(id=5, company_id=4, code='AAPL.default', display_name='AAPL default business', creator_id=1)
    default_bus_segment_baba = CompanyBusinessSegment(id=6, company_id=5, code='BABA.default', display_name='BABA default business', creator_id=1)
    cloud_bus_segment_baba = CompanyBusinessSegment(id=7, company_id=5, code='BABA.cloud', display_name='BABA cloud business', creator_id=1)
    default_bus_segment_bac = CompanyBusinessSegment(id=8, company_id=6, code='BAC.default', display_name='BAC default business', creator_id=1)
    default_bus_segment_jpm = CompanyBusinessSegment(id=9, company_id=7, code='JPM.default', display_name='JPM default business', creator_id=1)
    session.add_all([default_bus_segment_amd, default_bus_segment_zm, default_bus_segment_msft, cloud_bus_segment_msft, 
                     default_bus_segment_aapl, default_bus_segment_baba, cloud_bus_segment_baba, default_bus_segment_bac, default_bus_segment_jpm])
    session.flush()

def create_default_groups(session):
    group_defaults = CompanyGroup(id=1, name_code='defaults_grp', name='Group Of All Defaults', creator_id=1)
    group_cloud = CompanyGroup(id=2, name_code='cloud_grp', name='Group Of Cloud Businesses', creator_id=1)
    session.add_all([group_defaults, group_cloud])
    session.flush()

def create_default_sectors(session):
    sector_it = Sector(id=1, name_code='it_sector', name='Information Technology')
    sector_fin = Sector(id=2, name_code='fin_sector', name='Financials')
    session.add_all([sector_it, sector_fin])
    session.flush()

def create_default_sector_relations(session):
    rel_one = CompanySectorRelation(sector_id=1, company_business_segment_id=1)
    rel_two = CompanySectorRelation(sector_id=1, company_business_segment_id=2)
    rel_three = CompanySectorRelation(sector_id=1, company_business_segment_id=3)
    rel_four = CompanySectorRelation(sector_id=1, company_business_segment_id=4)
    rel_five = CompanySectorRelation(sector_id=1, company_business_segment_id=5)
    rel_six = CompanySectorRelation(sector_id=1, company_business_segment_id=6)
    rel_seven = CompanySectorRelation(sector_id=1, company_business_segment_id=7)
    rel_eight = CompanySectorRelation(sector_id=2, company_business_segment_id=8)
    rel_nine = CompanySectorRelation(sector_id=2, company_business_segment_id=9)
    session.add_all([rel_one, rel_two, rel_three, rel_four, rel_five, rel_six, rel_seven, rel_eight, rel_nine])
    session.flush()

def create_default_industry_relations(session):
    rel_one = CompanyIndustryRelation(industry_id=1, company_business_segment_id=1)
    rel_two = CompanyIndustryRelation(industry_id=3, company_business_segment_id=2)
    rel_three = CompanyIndustryRelation(industry_id=4, company_business_segment_id=3)
    rel_four = CompanyIndustryRelation(industry_id=5, company_business_segment_id=4)
    rel_five = CompanyIndustryRelation(industry_id=4, company_business_segment_id=5)
    rel_six = CompanyIndustryRelation(industry_id=4, company_business_segment_id=6)
    rel_seven = CompanyIndustryRelation(industry_id=5, company_business_segment_id=7)
    rel_eight = CompanyIndustryRelation(industry_id=2, company_business_segment_id=8)
    rel_nine = CompanyIndustryRelation(industry_id=2, company_business_segment_id=9)
    session.add_all([rel_one, rel_two, rel_three, rel_four, rel_five, rel_six, rel_seven, rel_eight, rel_nine])
    session.flush()

def create_default_industries(session):
    industry_semis = Industry(id=1, sector_id=1, name='Semiconductors', name_code='semis')
    industry_banking = Industry(id=2, sector_id=2, name='Banking Industry', name_code='banking')
    industry_communications = Industry(id=3, sector_id=1, name='Communications', name_code='comm')
    industry_big_tech = Industry(id=4, sector_id=1, name='Big Tech', name_code='big_tech')
    industry_cloud = Industry(id=5, sector_id=1, name='Cloud Services', name_code='cloud')
    session.add_all([industry_semis, industry_banking, industry_communications, industry_big_tech, industry_cloud])
    session.flush()

def create_default_metric_classifications(session):
    metric_cls_income_statement = MetricClassification(id=1, category_name='Income Statement', parent_category_id=None, creator_id=1)
    metric_cls_cloud_metrics = MetricClassification(id=2, category_name='Cloud Metrics', parent_category_id=None, creator_id=1)
    session.add_all([metric_cls_income_statement, metric_cls_cloud_metrics])
    session.flush()
    metric_cls_revenue = MetricClassification(id=3, category_name='Revenue', parent_category_id=metric_cls_income_statement.id, creator_id=1)
    metric_cls_ebitda = MetricClassification(id=4, category_name='EBITDA', parent_category_id=metric_cls_income_statement.id, creator_id=1)
    session.add_all([metric_cls_revenue, metric_cls_ebitda])
    session.flush()

def create_default_user_metric_classifications(session):
    session.add(UserMetricClassification(metric_classification_id=1, account_id=1))
    session.add(UserMetricClassification(metric_classification_id=2, account_id=1))
    session.add(UserMetricClassification(metric_classification_id=3, account_id=1))
    session.add(UserMetricClassification(metric_classification_id=4, account_id=1))
    session.flush()


def create_default_metric_descriptions(session):
    metric_desc_rev_2021 = MetricDescription(id=1, code='rev_2021', display_name='2021 Revenue', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                        year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                        metric_classification_id=3, creator_id=1)
                
    metric_desc_revenue_ttm = MetricDescription(id=2, code='rev_ttm', display_name='Trailing 12 Months Revenue', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=METRIC_DURATION_QUARTER, \
                                                year_recorded=2022, quarter_recorded=3, metric_duration=4, look_back=True, metric_fixed_year=-1, metric_fixed_quarter=-1, \
                                                metric_classification_id=3, creator_id=1)
    
    metric_desc_ebitda_2021 = MetricDescription(id=3, code='ebitda_2021', display_name='2021 EBITDA', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                metric_classification_id=4, creator_id=1)
    
    metric_desc_ebitda_ttm = MetricDescription(id=4, code='ebitda_ttm', display_name='Trailing 12 Months EBITDA', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=METRIC_DURATION_QUARTER, \
                                                year_recorded=2022, quarter_recorded=3, metric_duration=4, look_back=True, metric_fixed_year=-1, metric_fixed_quarter=-1, \
                                                metric_classification_id=4, creator_id=1)

    metric_desc_nb_enterprise_customers = MetricDescription(id=5, code='nb_cloud_customers_2021', display_name='2021 Number of Cloud Customers', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                metric_classification_id=2, creator_id=1)

    session.add_all([metric_desc_rev_2021, metric_desc_revenue_ttm, metric_desc_ebitda_2021, metric_desc_ebitda_ttm, metric_desc_nb_enterprise_customers])
    session.flush()

def create_default_user_metric_descriptions(session):
    session.add(UserMetricDescription(metric_description_id=1, account_id=1))
    session.add(UserMetricDescription(metric_description_id=2, account_id=1))
    session.add(UserMetricDescription(metric_description_id=3, account_id=1))
    session.add(UserMetricDescription(metric_description_id=4, account_id=1))
    session.add(UserMetricDescription(metric_description_id=5, account_id=1))

def create_default_metric_data(session):
    #AMD
    session.add(MetricData(id=1, metric_description_id=1, company_business_segment_id=1, data=200000, user_id=1))
    session.add(MetricData(id=50, metric_description_id=1, company_business_segment_id=1, data=4000, user_id=2))
    session.add(MetricData(id=2, metric_description_id=2, company_business_segment_id=1, data=220000, user_id=1))
    session.add(MetricData(id=3, metric_description_id=3, company_business_segment_id=1, data=30000, user_id=1))
    session.add(MetricData(id=4, metric_description_id=4, company_business_segment_id=1, data=31000, user_id=1))

    #ZM
    session.add(MetricData(id=5, metric_description_id=1, company_business_segment_id=2, data=40000, user_id=1))
    session.add(MetricData(id=6, metric_description_id=2, company_business_segment_id=2, data=40500, user_id=1))
    session.add(MetricData(id=7, metric_description_id=3, company_business_segment_id=2, data=10000, user_id=1))
    session.add(MetricData(id=8, metric_description_id=4, company_business_segment_id=2, data=11000, user_id=1))

    #MSFT
    session.add(MetricData(id=9, metric_description_id=1, company_business_segment_id=3, data=10000000, user_id=1))
    session.add(MetricData(id=10, metric_description_id=2, company_business_segment_id=3, data=12000000, user_id=1))
    session.add(MetricData(id=11, metric_description_id=3, company_business_segment_id=3, data=100000, user_id=1))
    session.add(MetricData(id=12, metric_description_id=4, company_business_segment_id=3, data=110000, user_id=1))
    session.add(MetricData(id=13, metric_description_id=5, company_business_segment_id=4, data=7000, user_id=1))

    #AAPL
    session.add(MetricData(id=14, metric_description_id=1, company_business_segment_id=5, data=50000, user_id=1))
    session.add(MetricData(id=15, metric_description_id=2, company_business_segment_id=5, data=40500, user_id=1))
    session.add(MetricData(id=16, metric_description_id=3, company_business_segment_id=5, data=13000, user_id=1))
    session.add(MetricData(id=17, metric_description_id=4, company_business_segment_id=5, data=14000, user_id=1))

    #BABA
    session.add(MetricData(id=18, metric_description_id=1, company_business_segment_id=6, data=300, user_id=1))
    session.add(MetricData(id=19, metric_description_id=2, company_business_segment_id=6, data=310, user_id=1))
    session.add(MetricData(id=20, metric_description_id=3, company_business_segment_id=6, data=200, user_id=1))
    session.add(MetricData(id=21, metric_description_id=4, company_business_segment_id=6, data=210, user_id=1))
    session.add(MetricData(id=22, metric_description_id=5, company_business_segment_id=7, data=500, user_id=1))
    session.flush()

def get_access_token(client, base_url, username, password):
    login_url = base_url + "/account/token"
    input = {'username': username, 'password': password}
    response = client.post(login_url, headers = {'Content-Type': 'application/x-www-form-urlencoded'}, data=input)
    assert response.status_code == 200
    response = response.json()
    return response['access_token']

def get_access_tokens(client, base_url, credentials):
    ret = []
    for username, password in credentials:
        ret.append(get_access_token(client, base_url, username, password))
    return ret
