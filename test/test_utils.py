from db.models import *
from db.company_financials import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from passlib.context import CryptContext

def cleanup_db_conn_from_conn_obj(conn):
    try:
        with conn.begin():
            stmt = delete(Account.__table__)
            conn.execute(stmt)

            stmt = delete(AccountTrade.__table__)
            conn.execute(stmt)
            
            stmt = delete(Company.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyBusinessSegment.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyDevelopment.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyExchangeRelation.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyFinancialData.__table__)
            conn.execute(stmt)

            stmt = delete(CompanyFundamentalRatios.__table__)
            conn.execute(stmt)

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

            stmt = delete(CompanySummary.__table__)
            conn.execute(stmt)

            stmt = delete(CountryInfo.__table__)
            conn.execute(stmt)

            stmt = delete(CronJobRun.__table__)
            conn.execute(stmt)

            stmt = delete(CurrencyBarData.__table__)
            conn.execute(stmt)

            stmt = delete(EquityBarData.__table__)
            conn.execute(stmt)

            stmt = delete(Exchange.__table__)
            conn.execute(stmt)

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

def cleanup_db_from_db_str(db_conn_str):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=db_conn_str, template_name='default_session') as session:
            session.query(Account).delete()
            session.query(AccountTrade).delete()
            session.query(Company).delete()
            session.query(CompanyBusinessSegment).delete()
            session.query(CompanyDevelopment).delete()
            session.query(CompanyExchangeRelation).delete()
            session.query(CompanyFinancialData).delete()
            session.query(CompanyFundamentalRatios).delete()
            session.query(CompanyGroup).delete()
            session.query(CompanyGroupMetricDescription).delete()
            session.query(CompanyInGroup).delete()
            session.query(CompanyIndustryRelation).delete()
            session.query(CompanySectorRelation).delete()
            session.query(CompanySummary).delete()
            session.query(CountryInfo).delete()
            session.query(CronJobRun).delete()
            session.query(CurrencyBarData).delete()
            session.query(EquityBarData).delete()
            session.query(Exchange).delete()
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
    default_bus_segment_amd = CompanyBusinessSegment(id=1, company_id=1, code='AMD.default', display_name='AMD default business')
    default_bus_segment_zm = CompanyBusinessSegment(id=2, company_id=2, code='ZM.default', display_name='ZM default business')
    default_bus_segment_msft = CompanyBusinessSegment(id=3, company_id=3, code='MSFT.default', display_name='MSFT default business')
    cloud_bus_segment_msft = CompanyBusinessSegment(id=4, company_id=3, code='MSFT.cloud', display_name='MSFT cloud business')
    default_bus_segment_aapl = CompanyBusinessSegment(id=5, company_id=4, code='AAPL.default', display_name='AAPL default business')
    default_bus_segment_baba = CompanyBusinessSegment(id=6, company_id=5, code='BABA.default', display_name='BABA default business')
    cloud_bus_segment_baba = CompanyBusinessSegment(id=7, company_id=5, code='BABA.cloud', display_name='BABA cloud business')
    default_bus_segment_bac = CompanyBusinessSegment(id=8, company_id=6, code='BAC.default', display_name='BAC default business')
    default_bus_segment_jpm = CompanyBusinessSegment(id=9, company_id=7, code='JPM.default', display_name='JPM default business')
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
