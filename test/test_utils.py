from db.models import *
from db.company_financials import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

def cleanup_db_conn_from_conn_obj(conn):
    try:
        with conn.begin():
            stmt = delete(Company.__table__)
            conn.execute(stmt)
            stmt = delete(Exchange.__table__)
            conn.execute(stmt)
            stmt = delete(Sector.__table__)
            conn.execute(stmt)
            stmt = delete(Industry.__table__)
            conn.execute(stmt)
            stmt = delete(Log.__table__)
            conn.execute(stmt)
            stmt = delete(CronJobRun.__table__)
            conn.execute(stmt)
            stmt = delete(EquityBarData.__table__)
            conn.execute(stmt)
            stmt = delete(CurrencyBarData.__table__)
            conn.execute(stmt)
            stmt = delete(CompanyMetric.__table__)
            conn.execute(stmt)
            stmt = delete(CompanyMetricDescription.__table__)
            conn.execute(stmt)
            stmt = delete(CompanyMetricDescriptionNote.__table__)
            conn.execute(stmt)
            stmt = delete(CompanyMetricRelation.__table__)
            conn.execute(stmt)
            stmt = delete(CompanyDevelopment.__table__)
            conn.execute(stmt)
            stmt = delete(CompanySummary.__table__)
            conn.execute(stmt)
    except Exception as gen_ex:
        print(str(gen_ex))

def cleanup_db_from_db_str(db_conn_str):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=db_conn_str, template_name='default_session') as session:
            session.query(Company).delete()
            session.query(CompanyExchangeRelation).delete()
            session.query(CompanySectorRelation).delete()
            session.query(CompanyFundamentalRatios).delete()
            session.query(Exchange).delete()
            session.query(Sector).delete()
            session.query(Industry).delete()
            session.query(Log).delete()
            session.query(CronJobRun).delete()
            session.query(EquityBarData).delete()
            session.query(CurrencyBarData).delete()
            session.query(CompanyMetric).delete()
            session.query(CompanyMetricDescription).delete()
            session.query(CompanyMetricDescriptionNote).delete()
            session.query(CompanyDevelopment).delete()
            session.query(CompanySummary).delete()
            session.query(CountryInfo).delete()
            session.query(CompanyMetricRelation).delete()
            session.query(CompanyQuarterlyFinancialData).delete()
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))