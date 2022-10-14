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
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_pwd = pwd_context.hash('system')
        account_system = Account(id=1, userName='system', password=hashed_pwd, email='email@gmail.com', phone='514-222-2222', disabled=False)
        session.add(account_system)

    except Exception as gen_ex:
        print(str(gen_ex))

def create_default_companies(session):
    amd_company = Company(id=1, ticker='AMD', name='Advanced Micro Devices Inc.', delisted=False)
    zm_company = Company(id=2, ticker='ZM', name='Zoom Video Communications Inc.', delisted=False)
    msft_company = Company(id=3, ticker='MSFT', name='Microsoft Corp.', delisted=False)
    aapl_company = Company(id=4, ticker='AAPL', name='Apple Inc.', delisted=False)
    baba_company = Company(id=5, ticker='BABA', name='Alibaba Group Holdings Ltd.', delisted=False)
    session.add_all([amd_company, zm_company, msft_company, aapl_company, baba_company])

def create_default_business_segments(session):
    default_bus_segment_amd = CompanyBusinessSegment(id=1, company_id=1, code='AMD.default', display_name='AMD default business')
    default_bus_segment_zm = CompanyBusinessSegment(id=2, company_id=2, code='ZM.default', display_name='ZM default business')
    default_bus_segment_msft = CompanyBusinessSegment(id=3, company_id=3, code='MSFT.default', display_name='MSFT default business')
    cloud_bus_segment_msft = CompanyBusinessSegment(id=4, company_id=3, code='MSFT.cloud', display_name='MSFT cloud business')
    default_bus_segment_aapl = CompanyBusinessSegment(id=5, company_id=4, code='AAPL.default', display_name='AAPL default business')
    default_bus_segment_baba = CompanyBusinessSegment(id=6, company_id=5, code='BABA.default', display_name='BABA default business')
    cloud_bus_segment_baba = CompanyBusinessSegment(id=7, company_id=5, code='BABA.cloud', display_name='BABA cloud business')
    session.add_all([default_bus_segment_amd, default_bus_segment_zm, default_bus_segment_msft, cloud_bus_segment_msft, default_bus_segment_aapl, default_bus_segment_baba, cloud_bus_segment_baba])

def create_default_groups(session):
    group_defaults = CompanyGroup(id=1, name_code='defaults_grp', name='Group Of All Defaults', creator_id=1)
    group_cloud = CompanyGroup(id=2, name_code='cloud_grp', name='Group Of Cloud Businesses', creator_id=1)
    session.add_all([group_defaults, group_cloud])