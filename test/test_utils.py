from db.models import *
from db.company_financials import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

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