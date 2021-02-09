from fin_app_crons.market_data_import import *
from db.models import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

import logging, os, sys, json, datetime

def test_exec_filtered_out(caplog):
    absolute_path = os.path.join(sys.path[0], 'filter_test.json')
    with open(absolute_path, 'r') as f:
        file_content_raw = f.read()
        config_json_content = json.loads(file_content_raw)
        exec_import(config_json_content, None)
        
        assert len(caplog.records) == 4
        
        assert caplog.records[0].levelname == 'INFO'
        assert caplog.records[0].name == 'fund_cron_logger'
        assert caplog.records[0].message == "The following vendor source is filtered out: vendor_1"

        assert caplog.records[1].levelname == 'INFO'
        assert caplog.records[1].name == 'fund_cron_logger'
        assert caplog.records[1].message == "The following vendor source is filtered out: vendor_2"

        assert caplog.records[2].levelname == 'CRITICAL'
        assert caplog.records[2].name == 'fund_cron_logger'
        assert caplog.records[2].message == "Vendor: vendor_3 is unknown."

        assert caplog.records[3].levelname == 'CRITICAL'
        assert caplog.records[3].name == 'fund_cron_logger'
        assert caplog.records[3].message == "'NoneType' object has no attribute 'add'"

        caplog.clear()

        absolute_path = os.path.join(sys.path[0], 'filter_test_2.json')
        exec_import(config_json_content, None)

        assert len(caplog.records) == 4
        
        assert caplog.records[0].levelname == 'INFO'
        assert caplog.records[0].name == 'fund_cron_logger'
        assert caplog.records[0].message == "The following vendor source is filtered out: vendor_1"

        assert caplog.records[1].levelname == 'INFO'
        assert caplog.records[1].name == 'fund_cron_logger'
        assert caplog.records[1].message == "The following vendor source is filtered out: vendor_2"

        assert caplog.records[2].levelname == 'CRITICAL'
        assert caplog.records[2].name == 'fund_cron_logger'
        assert caplog.records[2].message == "Vendor: vendor_3 is unknown."

        assert caplog.records[3].levelname == 'CRITICAL'
        assert caplog.records[3].name == 'fund_cron_logger'
        assert caplog.records[3].message == "'NoneType' object has no attribute 'add'"


def cleanup_db(conn):
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
    except Exception as gen_ex:
        print(str(gen_ex))


def test_log_exceptions_to_db(caplog):
    absolute_path = os.path.join(sys.path[0], 'filter_test.json')
    with open(absolute_path, 'r') as f:
        file_content_raw = f.read()
        config_json_content = json.loads(file_content_raw)
        del config_json_content['sources']

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config_json_content['dbConnString'], template_name='basic') as session:
            cleanup_db(session.connection())
            session.commit()
            exec_import(config_json_content, session)
            
            assert len(caplog.records) == 1
            
            assert caplog.records[0].levelname == 'CRITICAL'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "'sources'"

            session.commit()
            session.expire_all()

            logs = session.query(Log).all()
            assert len(logs) == 1
            assert logs[0].log_type == EXEC_IMPORT_BEGIN
            assert logs[0].message == "Exception"
            assert logs[0].data is not None
            assert logs[0].update_stamp is not None
            cron_job_runs = session.query(CronJobRun).all()
            assert len(cron_job_runs) == 1
            assert cron_job_runs[0].success == False
            assert cron_job_runs[0].log_id == logs[0].id


def test_empty_db_missing_records(caplog):
    absolute_path = os.path.join(sys.path[0], 'test_exec_import_empty_db.json')

    #clean up db in case
    with open(absolute_path, 'r') as f:
        config_raw = f.read()
        config = json.loads(config_raw)

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config['dbConnString'], template_name='basic') as session:
            cleanup_db(session.connection())
            session.commit()
            exec_import(config, session)

            assert len(caplog.records) == 19

            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "Importing tickers with no date filter."

            assert caplog.records[1].levelname == 'WARNING'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Unknown exchange detected: Missing"

            assert caplog.records[2].levelname == 'WARNING'
            assert caplog.records[2].name == 'fund_cron_logger'
            assert caplog.records[2].message == "Unknown exchange detected: OTC"

            assert caplog.records[3].levelname == 'WARNING'
            assert caplog.records[3].name == 'fund_cron_logger'
            assert caplog.records[3].message == "Unknown exchange detected: NASDAQ"

            assert caplog.records[4].levelname == 'WARNING'
            assert caplog.records[4].name == 'fund_cron_logger'
            assert caplog.records[4].message == "Unknown sector detected: Technology"

            assert caplog.records[5].levelname == 'WARNING'
            assert caplog.records[5].name == 'fund_cron_logger'
            assert caplog.records[5].message == "Unknown sector detected: Consumer Cyclical"

            assert caplog.records[6].levelname == 'WARNING'
            assert caplog.records[6].name == 'fund_cron_logger'
            assert caplog.records[6].message == "Unknown sector detected: Missing"

            assert caplog.records[7].levelname == 'WARNING'
            assert caplog.records[7].name == 'fund_cron_logger'
            assert caplog.records[7].message == "Unknown sector detected: Financial Services"

            assert caplog.records[8].levelname == 'WARNING'
            assert caplog.records[8].name == 'fund_cron_logger'
            assert caplog.records[8].message == "Unknown industry detected: Software - Application"

            assert caplog.records[9].levelname == 'WARNING'
            assert caplog.records[9].name == 'fund_cron_logger'
            assert caplog.records[9].message == "Unknown industry detected: Restaurants"

            assert caplog.records[10].levelname == 'WARNING'
            assert caplog.records[10].name == 'fund_cron_logger'
            assert caplog.records[10].message == "Unknown industry detected: Banks - Regional"

            assert caplog.records[11].levelname == 'WARNING'
            assert caplog.records[11].name == 'fund_cron_logger'
            assert caplog.records[11].message == "Unknown industry detected: Missing"

            assert caplog.records[12].levelname == 'WARNING'
            assert caplog.records[12].name == 'fund_cron_logger'
            assert caplog.records[12].message == "None result when fetching first sector matching: Technology"

            assert caplog.records[13].levelname == 'WARNING'
            assert caplog.records[13].name == 'fund_cron_logger'
            assert caplog.records[13].message == "None result when fetching first sector matching: Consumer Cyclical"

            assert caplog.records[14].levelname == 'WARNING'
            assert caplog.records[14].name == 'fund_cron_logger'
            assert caplog.records[14].message == "None result when fetching first sector matching: Missing"

            assert caplog.records[15].levelname == 'WARNING'
            assert caplog.records[15].name == 'fund_cron_logger'
            assert caplog.records[15].message == "None result when fetching first sector matching: Financial Services"

            assert caplog.records[16].levelname == 'WARNING'
            assert caplog.records[16].name == 'fund_cron_logger'
            assert caplog.records[16].message == "None result when fetching first sector matching: Technology"

            assert caplog.records[17].levelname == 'INFO'
            assert caplog.records[17].name == 'fund_cron_logger'
            assert caplog.records[17].message == "The following vendor source is filtered out: vendor_1"

            assert caplog.records[18].levelname == 'INFO'
            assert caplog.records[18].name == 'fund_cron_logger'
            assert caplog.records[18].message == "Market data import exited successfully."

            session.expire_all()

            logs = session.query(Log).all()
            assert len(logs) == 1
            assert logs[0].log_type == EXEC_IMPORT_COMPANIES_LOG_TYPE
            assert logs[0].message == "Successfully imported companies supported by: mock_vendor to database."
            assert logs[0].data is None
            assert logs[0].update_stamp is not None
            cron_job_runs = session.query(CronJobRun).all()
            assert len(cron_job_runs) == 1
            assert cron_job_runs[0].success == True
            assert cron_job_runs[0].log_id == logs[0].id

        
        #cleanup
        with manager.session_scope(db_url=config['dbConnString'], template_name='new_session') as session:
            cleanup_db(session.connection())
                
            #add necessary records to db

            #add exchanges

            #1 = USA
            nasdaq_exch = Exchange(country_info_id='1', name_code='NASDAQ', name='NASDAQ')
            session.add(nasdaq_exch)

            otc_exch = Exchange(country_info_id='1', name_code='OTC', name='Over the counter')
            session.add(otc_exch)

            #when no exchange is provided
            missing_exch = Exchange(country_info_id='1', name_code='Missing', name='Missing')
            session.add(missing_exch)

            #add sectors
            tech_sector = Sector(name_code='Tech', name='Technology')
            session.add(tech_sector)

            cons_cyc_sector = Sector(name_code='Cons_Cycl', name='Consumer Cyclical')
            session.add(cons_cyc_sector)

            fin_services_sector = Sector(name_code='Fin_Srv', name='Financial Services')
            session.add(fin_services_sector)

            missing_sector = Sector(name_code='Missing', name='Missing')
            session.add(missing_sector)

            #will create ids for previous records that are needed for next steps
            session.flush()

            #add industries
            software_app_industry = Industry(sector_id=tech_sector.id, name='Software - Application', name_code='Software/App')
            session.add(software_app_industry)

            restaurant_industry = Industry(sector_id=cons_cyc_sector.id, name='Restaurants', name_code='Restaurants')
            session.add(restaurant_industry)

            reg_banking_industry = Industry(sector_id=fin_services_sector.id, name='Banks - Regional', name_code='Reg_Banking')
            session.add(reg_banking_industry)

            missing_industry = Industry(sector_id=missing_sector.id, name='Missing', name_code='Missing')
            session.add(missing_industry)

            session.commit()
        
            #clear previously caught logs
            caplog.records.clear()

            #retry after adding previously missing records
            exec_import(config, session)

            #force push to db
            session.commit()

            #to test it really is in db
            session.expire_all()

            assert len(caplog.records) == 3

            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "Importing tickers with no date filter."

            assert caplog.records[1].levelname == 'INFO'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "The following vendor source is filtered out: vendor_1"

            assert caplog.records[2].levelname == 'INFO'
            assert caplog.records[2].name == 'fund_cron_logger'
            assert caplog.records[2].message == "Market data import exited successfully."

            db_companies = session.query(Company).order_by(Company.id).all()
            assert len(db_companies) == 5

            assert db_companies[0].ticker == 'NWGN1'
            assert db_companies[0].name == 'Newgen Results Corp'
            assert db_companies[0].locked == False
            assert db_companies[0].delisted == True

            assert db_companies[1].ticker == 'BBUCQ'
            assert db_companies[1].name == 'Big Buck Brewery & Steakhouse Inc'
            assert db_companies[1].locked == False
            assert db_companies[1].delisted == False

            assert db_companies[2].ticker == 'AREM1'
            assert db_companies[2].name == 'Aremissoft Corp'
            assert db_companies[2].locked == False
            assert db_companies[2].delisted == True

            assert db_companies[3].ticker == 'GOVB'
            assert db_companies[3].name == 'Gouverneur Bancorp Inc'
            assert db_companies[3].locked == False
            assert db_companies[3].delisted == False

            assert db_companies[4].ticker == 'WAVT'
            assert db_companies[4].name == 'Wave Technologies International Inc'
            assert db_companies[4].locked == False
            assert db_companies[4].delisted == True

            
            #verify proper relations were inserted
            
            stmt = select([t_company_exchange_relation]).order_by(t_company_exchange_relation.c.company_id.asc())
            res = session.connection().execute(stmt).fetchall()
            assert len(res) == 5
            assert res[0].company_id == db_companies[0].id
            assert res[0].exchange_id == missing_exch.id
            assert res[1].company_id == db_companies[1].id
            assert res[1].exchange_id == otc_exch.id
            assert res[2].company_id == db_companies[2].id
            assert res[2].exchange_id == nasdaq_exch.id
            assert res[3].company_id == db_companies[3].id
            assert res[3].exchange_id == otc_exch.id
            assert res[4].company_id == db_companies[4].id
            assert res[4].exchange_id == nasdaq_exch.id


            stmt = select([t_company_sector_relation]).order_by(t_company_sector_relation.c.company_id.asc())
            res = session.connection().execute(stmt).fetchall()
            assert len(res) == 5
            assert res[0].company_id == db_companies[0].id
            assert res[0].sector_id == tech_sector.id
            assert res[1].company_id == db_companies[1].id
            assert res[1].sector_id == cons_cyc_sector.id
            assert res[2].company_id == db_companies[2].id
            assert res[2].sector_id == missing_sector.id
            assert res[3].company_id == db_companies[3].id
            assert res[3].sector_id == fin_services_sector.id
            assert res[4].company_id == db_companies[4].id
            assert res[4].sector_id == tech_sector.id

            session.expire_all()

            logs = session.query(Log).all()
            assert len(logs) == 1
            assert logs[0].log_type == EXEC_IMPORT_COMPANIES_LOG_TYPE
            assert logs[0].message == "Successfully imported companies supported by: mock_vendor to database."
            assert logs[0].data is None
            assert logs[0].update_stamp is not None
            cron_job_runs = session.query(CronJobRun).all()
            assert len(cron_job_runs) == 1
            assert cron_job_runs[0].success == True
            assert cron_job_runs[0].log_id == logs[0].id

            cleanup_db(session.connection())


def test_existing_db_missing_records(caplog):
    absolute_path = os.path.join(sys.path[0], 'test_exec_import_existing_db_missing_records.json')

    #clean up db in case
    with open(absolute_path, 'r') as f:
        config_raw = f.read()
        config = json.loads(config_raw)
        engine = create_engine(config['dbConnString'])

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config['dbConnString'], template_name='first_session') as session:
            cleanup_db(session.connection())

            #add necessary records to db

            #add exchanges

            #1 = USA
            nasdaq_exch = Exchange(country_info_id='1', name_code='NASDAQ', name='NASDAQ')
            session.add(nasdaq_exch)

            otc_exch = Exchange(country_info_id='1', name_code='OTC', name='Over the counter')
            session.add(otc_exch)

            nyse_exch = Exchange(country_info_id='1', name_code='NYSE', name='New York Stock Exchange')
            session.add(nyse_exch)

            #when no exchange is provided
            missing_exch = Exchange(country_info_id='1', name_code='Missing', name='Missing')
            session.add(missing_exch)

            #add sectors
            tech_sector = Sector(name_code='Tech', name='Technology')
            session.add(tech_sector)

            cons_cyc_sector = Sector(name_code='Cons_Cycl', name='Consumer Cyclical')
            session.add(cons_cyc_sector)

            fin_services_sectors = Sector(name_code='Fin_Srv', name='Financial Services')
            session.add(fin_services_sectors)

            missing_sector = Sector(name_code='Missing', name='Missing')
            session.add(missing_sector)

            #will create ids for previous records that are needed for next steps
            session.flush() 

            #add industries
            software_app_industry = Industry(sector_id=tech_sector.id, name='Software - Application', name_code='Software/App')
            session.add(software_app_industry)

            restaurant_industry = Industry(sector_id=cons_cyc_sector.id, name='Restaurants', name_code='Restaurants')
            session.add(restaurant_industry)

            soft_inf = Industry(sector_id=cons_cyc_sector.id, name='Software - Infrastructure', name_code='soft_inf')
            session.add(soft_inf)

            cons_elec = Industry(sector_id=cons_cyc_sector.id, name='Consumer Electronics', name_code='cons_elec')
            session.add(cons_elec)

            semi_cond = Industry(sector_id=cons_cyc_sector.id, name='Semiconductors', name_code='Semiconductors')
            session.add(semi_cond)

            reg_banking_industry = Industry(sector_id=fin_services_sectors.id, name='Banks - Regional', name_code='Reg_Banking')
            session.add(reg_banking_industry)

            missing_industry = Industry(sector_id=missing_sector.id, name='Missing', name_code='Missing')
            session.add(missing_industry)

            #add companies
            apple_company = Company(ticker='AAPL', name='Apple Inc', delisted=False)
            msft_company = Company(ticker='MSFT', name='Microsoft Corp', delisted=False)
            amd_company = Company(ticker='AMD', name='Advanced Micro Devices Inc', locked=True, delisted=True)
            twtr_company = Company(ticker='TWTR', name='Twitter Inc', locked=False, delisted=False)
            cmg_company = Company(ticker='CMG', name='Chipotle Grill', locked=True, delisted=False)
            fb_company = Company(ticker='FB', name='Facebook Inc', locked=False, delisted=False)

            session.add_all([apple_company, msft_company, amd_company, twtr_company, cmg_company, fb_company])

            session.flush()

            #add relations
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=apple_company.id, exchange_id=nasdaq_exch.id)
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=msft_company.id, exchange_id=nasdaq_exch.id)
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=amd_company.id, exchange_id=nasdaq_exch.id)
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=twtr_company.id, exchange_id=nyse_exch.id)
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=cmg_company.id, exchange_id=nyse_exch.id)
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=fb_company.id, exchange_id=nasdaq_exch.id)


            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=apple_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=msft_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=amd_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=twtr_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=cmg_company.id, sector_id=cons_cyc_sector.id)
            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=fb_company.id, sector_id=tech_sector.id)

            session.commit()

            #now that db is populated with records, execute an import than will contain some of those and new ones

            exec_import(config, session)

            #save old timestamps
            aapl_stamp = apple_company.update_stamp
            msft_stamp = msft_company.update_stamp
            amd_stamp = amd_company.update_stamp
            twtr_stamp = twtr_company.update_stamp
            cmg_stamp = cmg_company.update_stamp
            fb_stamp = fb_company.update_stamp

            #force update_stamp change. Needed since it is a trigger in db
            session.commit()

            assert len(caplog.records) == 11

            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "Importing tickers with no date filter."

            assert caplog.records[1].levelname == 'WARNING'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Unknown industry detected: Internet Content & Information"

            assert caplog.records[2].levelname == 'WARNING'
            assert caplog.records[2].name == 'fund_cron_logger'
            assert caplog.records[2].message == "Unknown industry detected: Home Improvement Retail"

            assert caplog.records[3].levelname == 'INFO'
            assert caplog.records[3].name == 'fund_cron_logger'
            assert caplog.records[3].message == "The following ticker was updated in the company table: MSFT"

            assert caplog.records[4].levelname == 'INFO'
            assert caplog.records[4].name == 'fund_cron_logger'
            assert caplog.records[4].message == "Company with ticker TWTR name changed from Twitter Inc to twatter"

            assert caplog.records[5].levelname == 'INFO'
            assert caplog.records[5].name == 'fund_cron_logger'
            assert caplog.records[5].message == "The following ticker was updated in the company table: TWTR"

            assert caplog.records[6].levelname == 'INFO'
            assert caplog.records[6].name == 'fund_cron_logger'
            assert caplog.records[6].message == "The following ticker was updated in the company table: FB"

            assert caplog.records[7].levelname == 'INFO'
            assert caplog.records[7].name == 'fund_cron_logger'
            assert caplog.records[7].message == "Company with name Facebook Inc ticker changed from FB to FB2"

            assert caplog.records[8].levelname == 'INFO'
            assert caplog.records[8].name == 'fund_cron_logger'
            assert caplog.records[8].message == "The following ticker was updated in the company table: FB2"

            assert caplog.records[9].levelname == 'INFO'
            assert caplog.records[9].name == 'fund_cron_logger'
            assert caplog.records[9].message == "The following vendor source is filtered out: vendor_1"

            assert caplog.records[10].levelname == 'INFO'
            assert caplog.records[10].name == 'fund_cron_logger'
            assert caplog.records[10].message == "Market data import exited successfully."

            #check db has correct records after import
            db_companies = session.query(Company).order_by(Company.id.asc()).all()
            assert len(db_companies) == 9

            #untouched
            assert db_companies[0].ticker == 'AAPL'
            assert db_companies[0].name == 'Apple Inc'
            assert db_companies[0].delisted == False
            assert db_companies[0].locked == False
            assert db_companies[0].update_stamp == aapl_stamp

            #delisted modified
            assert db_companies[1].ticker == 'MSFT'
            assert db_companies[1].name == 'Microsoft Corp'
            assert db_companies[1].delisted == True
            assert db_companies[1].locked == False
            assert db_companies[1].update_stamp != msft_stamp

            #untouched because locked
            assert db_companies[2].ticker == 'AMD'
            assert db_companies[2].name == 'Advanced Micro Devices Inc'
            assert db_companies[2].delisted == True
            assert db_companies[2].locked == True
            assert db_companies[2].update_stamp == amd_stamp

            #name modified
            assert db_companies[3].ticker == 'TWTR'
            assert db_companies[3].name == 'twatter'
            assert db_companies[3].delisted == False
            assert db_companies[3].locked == False
            assert db_companies[3].update_stamp != twtr_stamp

            #untouched because locked
            assert db_companies[4].ticker == 'CMG'
            assert db_companies[4].name == 'Chipotle Grill'
            assert db_companies[4].delisted == False
            assert db_companies[4].locked == True
            assert db_companies[4].update_stamp == cmg_stamp

            assert db_companies[5].ticker == 'FB2'
            assert db_companies[5].name == 'Facebook Inc'
            assert db_companies[5].delisted == False
            assert db_companies[5].locked == False
            assert db_companies[5].update_stamp != fb_stamp

            assert db_companies[6].ticker == 'FSLY'
            assert db_companies[6].name == 'Fastly Inc'
            assert db_companies[6].delisted == False
            assert db_companies[6].locked == False

            assert db_companies[7].ticker == 'HD'
            assert db_companies[7].name == 'Home Depot Inc'
            assert db_companies[7].delisted == False
            assert db_companies[7].locked == False

            assert db_companies[8].ticker == 'NVDA'
            assert db_companies[8].name == 'Nvidia Corp'
            assert db_companies[8].delisted == False
            assert db_companies[8].locked == False

            #check relations
            stmt = select([t_company_exchange_relation]).order_by(t_company_exchange_relation.c.company_id.asc())
            res = session.connection().execute(stmt).fetchall()
            assert len(res) == 9
            assert res[0].company_id == db_companies[0].id
            assert res[0].exchange_id == nasdaq_exch.id
            assert res[1].company_id == db_companies[1].id
            assert res[1].exchange_id == nasdaq_exch.id
            assert res[2].company_id == db_companies[2].id
            assert res[2].exchange_id == nasdaq_exch.id
            assert res[3].company_id == db_companies[3].id
            assert res[3].exchange_id == nyse_exch.id
            assert res[4].company_id == db_companies[4].id
            assert res[4].exchange_id == nyse_exch.id
            assert res[5].company_id == db_companies[5].id
            assert res[5].exchange_id == nasdaq_exch.id
            assert res[6].company_id == db_companies[6].id
            assert res[6].exchange_id == nyse_exch.id
            assert res[7].company_id == db_companies[7].id
            assert res[7].exchange_id == nyse_exch.id
            assert res[8].company_id == db_companies[8].id
            assert res[8].exchange_id == nasdaq_exch.id


            stmt = select([t_company_sector_relation]).order_by(t_company_sector_relation.c.company_id.asc())
            res = session.connection().execute(stmt).fetchall()
            assert len(res) == 9
            assert res[0].company_id == db_companies[0].id
            assert res[0].sector_id == tech_sector.id
            assert res[1].company_id == db_companies[1].id
            assert res[1].sector_id == tech_sector.id
            assert res[2].company_id == db_companies[2].id
            assert res[2].sector_id == tech_sector.id
            assert res[3].company_id == db_companies[3].id
            assert res[3].sector_id == tech_sector.id
            assert res[4].company_id == db_companies[4].id
            assert res[4].sector_id == cons_cyc_sector.id
            assert res[5].company_id == db_companies[5].id
            assert res[5].sector_id == tech_sector.id
            assert res[6].company_id == db_companies[6].id
            assert res[6].sector_id == tech_sector.id
            assert res[7].company_id == db_companies[7].id
            assert res[7].sector_id == cons_cyc_sector.id
            assert res[8].company_id == db_companies[8].id
            assert res[8].sector_id == tech_sector.id

            logs = session.query(Log).all()
            assert len(logs) == 1
            assert logs[0].log_type == EXEC_IMPORT_COMPANIES_LOG_TYPE
            assert logs[0].message == "Successfully imported companies supported by: mock_vendor to database."
            assert logs[0].data is None
            assert logs[0].update_stamp is not None
            cron_job_runs = session.query(CronJobRun).all()
            assert len(cron_job_runs) == 1
            assert cron_job_runs[0].success == True
            assert cron_job_runs[0].log_id == logs[0].id

            cleanup_db(session.connection())

def test_existing_db_not_first_cron(caplog):
    absolute_path = os.path.join(sys.path[0], 'test_exec_import_empty_db.json')

    #clean up db in case
    with open(absolute_path, 'r') as f:
        config_raw = f.read()
        config = json.loads(config_raw)

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config['dbConnString'], template_name='basic') as session:
            cleanup_db(session.connection())
            
            log_one = Log(log_type='exc_imp_fund', message='msg')
            log_two = Log(log_type='exc_imp_tec', message='msg2')

            session.add_all([log_one, log_two])
            session.flush()

            cron_one = CronJobRun(log_id=log_one.id, success=True)
            cron_two = CronJobRun(log_id=log_two.id, success=True)

            session.add_all([cron_one, cron_two])

            session.commit()

            exec_import(config, session)

def test_exec_import_companies_fundamental_data(caplog):
    absolute_path = os.path.join(sys.path[0], 'test_exec_import_fundamental_data.json')

    #clean up db in case
    with open(absolute_path, 'r') as f:
        config_raw = f.read()
        config = json.loads(config_raw)
        engine = create_engine(config['dbConnString'])

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config['dbConnString'], template_name='first_session') as session:
            cleanup_db(session.connection())

            #1 = USA
            nasdaq_exch = Exchange(country_info_id='1', name_code='NASDAQ', name='NASDAQ')
            session.add(nasdaq_exch)

            otc_exch = Exchange(country_info_id='1', name_code='OTC', name='Over the counter')
            session.add(otc_exch)

            nyse_exch = Exchange(country_info_id='1', name_code='NYSE', name='New York Stock Exchange')
            session.add(nyse_exch)

            #when no exchange is provided
            missing_exch = Exchange(country_info_id='1', name_code='Missing', name='Missing')
            session.add(missing_exch)

            #add sectors
            tech_sector = Sector(name_code='Tech', name='Technology')
            session.add(tech_sector)

            cons_cyc_sector = Sector(name_code='Cons_Cycl', name='Consumer Cyclical')
            session.add(cons_cyc_sector)

            fin_services_sectors = Sector(name_code='Fin_Srv', name='Financial Services')
            session.add(fin_services_sectors)

            missing_sector = Sector(name_code='Missing', name='Missing')
            session.add(missing_sector)

            #will create ids for previous records that are needed for next steps
            session.flush() 

            #add industries
            software_app_industry = Industry(sector_id=tech_sector.id, name='Software - Application', name_code='Software/App')
            session.add(software_app_industry)

            restaurant_industry = Industry(sector_id=cons_cyc_sector.id, name='Restaurants', name_code='Restaurants')
            session.add(restaurant_industry)

            soft_inf = Industry(sector_id=cons_cyc_sector.id, name='Software - Infrastructure', name_code='soft_inf')
            session.add(soft_inf)

            cons_elec = Industry(sector_id=cons_cyc_sector.id, name='Consumer Electronics', name_code='cons_elec')
            session.add(cons_elec)

            semi_cond = Industry(sector_id=cons_cyc_sector.id, name='Semiconductors', name_code='Semiconductors')
            session.add(semi_cond)

            reg_banking_industry = Industry(sector_id=fin_services_sectors.id, name='Banks - Regional', name_code='Reg_Banking')
            session.add(reg_banking_industry)

            missing_industry = Industry(sector_id=missing_sector.id, name='Missing', name_code='Missing')
            session.add(missing_industry)

            #add companies
            apple_company = Company(ticker='AAPL', name='Apple Inc', delisted=False)
            msft_company = Company(ticker='MSFT', name='Microsoft Corp', delisted=False)
            amd_company = Company(ticker='AMD', name='Advanced Micro Devices Inc', locked=True, delisted=True)

            session.add_all([apple_company, msft_company, amd_company])

            session.flush()

            #add relations
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=apple_company.id, exchange_id=nasdaq_exch.id)
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=msft_company.id, exchange_id=nasdaq_exch.id)
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=amd_company.id, exchange_id=nasdaq_exch.id)
            stmt = t_company_exchange_relation.insert()


            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=apple_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=msft_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=amd_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()

            session.commit()

            exec_import(config, session)

            session.commit()

            assert len(caplog.records) == 4
            
            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "Importing fundamental data with no date filter."

            assert caplog.records[1].levelname == 'WARNING'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Company with ticker: FSLY does not exist in the database."

            assert caplog.records[2].levelname == 'INFO'
            assert caplog.records[2].name == 'fund_cron_logger'
            assert caplog.records[2].message == "The following vendor source is filtered out: vendor_1"

            assert caplog.records[3].levelname == 'INFO'
            assert caplog.records[3].name == 'fund_cron_logger'
            assert caplog.records[3].message == "Market data import exited successfully."

            bal_sheet_data = session.query(BalanceSheetData).all()
            cf_data = session.query(CashFlowStatementData).all()
            inc_stmt_data = session.query(IncomeStatementData).all()

            assert len(bal_sheet_data) == 14
            assert len(cf_data) == 14
            assert len(inc_stmt_data) == 14

            msft_bal_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id == msft_company.id).all()
            assert len(msft_bal_sheet_data) == 7
            msft_cash_flow_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id == msft_company.id).all()
            assert len(msft_cash_flow_data) == 7
            msft_inc_stmt_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id == msft_company.id).all()
            assert len(msft_inc_stmt_data) == 7

            aapl_bal_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id == apple_company.id).all()
            assert len(aapl_bal_sheet_data) == 6
            aapl_cash_flow_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id == apple_company.id).all()
            assert len(aapl_cash_flow_data) == 6
            aapl_inc_stmt_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id == apple_company.id).all()
            assert len(aapl_inc_stmt_data) == 6

            amd_bal_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id == amd_company.id).all()
            assert len(amd_bal_sheet_data) == 1
            amd_cash_flow_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id == amd_company.id).all()
            assert len(amd_cash_flow_data) == 1
            amd_inc_stmt_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id == amd_company.id).all()
            assert len(amd_inc_stmt_data) == 1

            bal = session.query(BalanceSheetData).filter(BalanceSheetData.calendar_date == '2020-09-30').all()
            assert len(bal) == 3

            cf = session.query(CashFlowStatementData).filter(CashFlowStatementData.calendar_date == '2020-09-30').all()
            assert len(cf) == 3

            inc_stmt = session.query(IncomeStatementData).filter(IncomeStatementData.calendar_date == '2020-09-30').all()
            assert len(cf) == 3

            msft_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == msft_company.id).order_by(CompanyMiscInfo.date_recorded).all()
            assert len(msft_misc_info) == 7
            assert msft_misc_info[0].date_recorded.year == 2019
            assert msft_misc_info[0].date_recorded.month == 3
            assert msft_misc_info[0].date_recorded.day == 31
            assert msft_misc_info[0].shares_bas == 7672213446
            assert msft_misc_info[0].shares_dil == None

            aapl_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == apple_company.id).order_by(CompanyMiscInfo.date_recorded).all()
            assert len(aapl_misc_info) == 6
            assert aapl_misc_info[5].date_recorded.year == 2020
            assert aapl_misc_info[5].date_recorded.month == 9
            assert aapl_misc_info[5].date_recorded.day == 30
            assert aapl_misc_info[5].shares_bas == 17102536000
            assert aapl_misc_info[5].shares_dil == None

            amd_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == amd_company.id).order_by(CompanyMiscInfo.date_recorded).all()
            assert len(amd_misc_info) == 1
            assert amd_misc_info[0].date_recorded.year == 2020
            assert amd_misc_info[0].date_recorded.month == 9
            assert amd_misc_info[0].date_recorded.day == 30
            assert amd_misc_info[0].shares_bas == 1174056713
            assert amd_misc_info[0].shares_dil == None

            #redo now that db already has data
            caplog.records.clear()
            session.expire_all()
            config['sources'][0]['vendorConfigFilePath'] = "/home/ghelie/fin_app/fin_app_core/fin_app_crons/test/test_mock_vendor_fundamental_not_empty_db.json"
            exec_import(config, session)

            session.commit()
            
            assert len(caplog.records) == 4
            
            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert "Importing companies fundamental data that was updated after or on" in  caplog.records[0].message

            assert caplog.records[1].levelname == 'WARNING'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Company with ticker: FSLY does not exist in the database."

            assert caplog.records[2].levelname == 'INFO'
            assert caplog.records[2].name == 'fund_cron_logger'
            assert caplog.records[2].message == "The following vendor source is filtered out: vendor_1"

            assert caplog.records[3].levelname == 'INFO'
            assert caplog.records[3].name == 'fund_cron_logger'
            assert caplog.records[3].message == "Market data import exited successfully."

            bal_sheet_data = session.query(BalanceSheetData).all()
            cf_data = session.query(CashFlowStatementData).all()
            inc_stmt_data = session.query(IncomeStatementData).all()

            assert len(bal_sheet_data) == 15
            assert len(cf_data) == 15
            assert len(inc_stmt_data) == 15

            msft_bal_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id == msft_company.id).all()
            assert len(msft_bal_sheet_data) == 7
            msft_cash_flow_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id == msft_company.id).all()
            assert len(msft_cash_flow_data) == 7
            msft_inc_stmt_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id == msft_company.id).all()
            assert len(msft_inc_stmt_data) == 7

            aapl_bal_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id == apple_company.id).all()
            assert len(aapl_bal_sheet_data) == 6
            aapl_cash_flow_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id == apple_company.id).all()
            assert len(aapl_cash_flow_data) == 6
            aapl_inc_stmt_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id == apple_company.id).all()
            assert len(aapl_inc_stmt_data) == 6

            amd_bal_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id == amd_company.id).all()
            assert len(amd_bal_sheet_data) == 2
            amd_cash_flow_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id == amd_company.id).all()
            assert len(amd_cash_flow_data) == 2
            amd_inc_stmt_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id == amd_company.id).all()
            assert len(amd_inc_stmt_data) == 2

            bal = session.query(BalanceSheetData).filter(BalanceSheetData.calendar_date == '2020-09-30').all()
            assert len(bal) == 3

            cf = session.query(CashFlowStatementData).filter(CashFlowStatementData.calendar_date == '2020-09-30').all()
            assert len(cf) == 3

            inc_stmt = session.query(IncomeStatementData).filter(IncomeStatementData.calendar_date == '2020-09-30').all()
            assert len(cf) == 3

            msft_bal_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id == msft_company.id).all()
            assert len(msft_bal_sheet_data) == 7
            msft_bal_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id == msft_company.id, BalanceSheetData.calendar_date == datetime.date(2019, 12, 31)).all()
            assert len(msft_bal_sheet_data) == 1
            assert msft_bal_sheet_data[0].assets == 65750


            msft_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == msft_company.id).order_by(CompanyMiscInfo.date_recorded).all()
            assert len(msft_misc_info) == 7
            msft_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == msft_company.id, CompanyMiscInfo.date_recorded == datetime.date(2019, 12, 31)).order_by(CompanyMiscInfo.date_recorded).all()
            assert len(msft_misc_info) == 1
            assert msft_misc_info[0].date_recorded.year == 2019
            assert msft_misc_info[0].date_recorded.month == 12
            assert msft_misc_info[0].date_recorded.day == 31
            assert msft_misc_info[0].shares_bas == 77777
            assert msft_misc_info[0].shares_dil == None
            

            aapl_cf_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id == apple_company.id).all()
            assert len(aapl_cf_data) == 6
            aapl_cf_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id == apple_company.id, CashFlowStatementData.calendar_date == datetime.date(2019, 6, 30)).all()
            assert len(aapl_cf_data) == 1
            assert aapl_cf_data[0].capex == 35321

            aapl_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == apple_company.id).order_by(CompanyMiscInfo.date_recorded).all()
            assert len(aapl_misc_info) == 6
            aapl_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == apple_company.id, CompanyMiscInfo.date_recorded == datetime.date(2019, 6, 30)).order_by(CompanyMiscInfo.date_recorded).all()
            assert len(msft_misc_info) == 1
            assert aapl_misc_info[0].date_recorded.year == 2019
            assert aapl_misc_info[0].date_recorded.month == 6
            assert aapl_misc_info[0].date_recorded.day == 30
            assert aapl_misc_info[0].shares_bas == 777
            assert aapl_misc_info[0].shares_dil == None


            amd_inc_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id == amd_company.id).all()
            assert len(amd_inc_data) == 2
            amd_inc_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id == amd_company.id, IncomeStatementData.calendar_date == datetime.date(2020, 9, 30)).all()
            assert len(amd_inc_data) == 1
            assert amd_inc_data[0].revenue == 121

            amd_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == amd_company.id).order_by(CompanyMiscInfo.date_recorded).all()
            assert len(amd_misc_info) == 2
            amd_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == amd_company.id).order_by(CompanyMiscInfo.date_recorded).all()
            assert len(amd_misc_info) == 2
            assert amd_misc_info[0].date_recorded.year == 2020
            assert amd_misc_info[0].date_recorded.month == 6
            assert amd_misc_info[0].date_recorded.day == 30
            assert amd_misc_info[0].shares_bas == 5555
            assert amd_misc_info[0].shares_dil == None
            assert amd_misc_info[1].date_recorded.year == 2020
            assert amd_misc_info[1].date_recorded.month == 9
            assert amd_misc_info[1].date_recorded.day == 30
            assert amd_misc_info[1].shares_bas == 5555
            assert amd_misc_info[1].shares_dil == None

def test_exec_import_stock_prices(caplog):
    absolute_path = os.path.join(sys.path[0], 'test_exec_import_stock_prices.json')

    #clean up db in case
    with open(absolute_path, 'r') as f:
        config_raw = f.read()
        config = json.loads(config_raw)
        engine = create_engine(config['dbConnString'])

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config['dbConnString'], template_name='first_session') as session:
            cleanup_db(session.connection())

            nasdaq_exch = Exchange(country_info_id='1', name_code='NASDAQ', name='NASDAQ')
            session.add(nasdaq_exch)

            otc_exch = Exchange(country_info_id='1', name_code='OTC', name='Over the counter')
            session.add(otc_exch)

            nyse_exch = Exchange(country_info_id='1', name_code='NYSE', name='New York Stock Exchange')
            session.add(nyse_exch)

            #when no exchange is provided
            missing_exch = Exchange(country_info_id='1', name_code='Missing', name='Missing')
            session.add(missing_exch)

            #add sectors
            tech_sector = Sector(name_code='Tech', name='Technology')
            session.add(tech_sector)

            cons_cyc_sector = Sector(name_code='Cons_Cycl', name='Consumer Cyclical')
            session.add(cons_cyc_sector)

            fin_services_sectors = Sector(name_code='Fin_Srv', name='Financial Services')
            session.add(fin_services_sectors)

            missing_sector = Sector(name_code='Missing', name='Missing')
            session.add(missing_sector)

            #will create ids for previous records that are needed for next steps
            session.flush() 

            #add industries
            software_app_industry = Industry(sector_id=tech_sector.id, name='Software - Application', name_code='Software/App')
            session.add(software_app_industry)

            restaurant_industry = Industry(sector_id=cons_cyc_sector.id, name='Restaurants', name_code='Restaurants')
            session.add(restaurant_industry)

            soft_inf = Industry(sector_id=cons_cyc_sector.id, name='Software - Infrastructure', name_code='soft_inf')
            session.add(soft_inf)

            cons_elec = Industry(sector_id=cons_cyc_sector.id, name='Consumer Electronics', name_code='cons_elec')
            session.add(cons_elec)

            semi_cond = Industry(sector_id=cons_cyc_sector.id, name='Semiconductors', name_code='Semiconductors')
            session.add(semi_cond)

            reg_banking_industry = Industry(sector_id=fin_services_sectors.id, name='Banks - Regional', name_code='Reg_Banking')
            session.add(reg_banking_industry)

            missing_industry = Industry(sector_id=missing_sector.id, name='Missing', name_code='Missing')
            session.add(missing_industry)

            #add companies
            apple_company = Company(ticker='AAPL', name='Apple Inc', delisted=False)
            msft_company = Company(ticker='MSFT', name='Microsoft Corp', delisted=False)
            amd_company = Company(ticker='AMD', name='Advanced Micro Devices Inc', locked=True, delisted=True)

            session.add_all([apple_company, msft_company, amd_company])

            session.flush()

            #add relations
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=apple_company.id, exchange_id=nasdaq_exch.id)
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=msft_company.id, exchange_id=nasdaq_exch.id)
            stmt = t_company_exchange_relation.insert()
            session.connection().execute(stmt, company_id=amd_company.id, exchange_id=nasdaq_exch.id)
            stmt = t_company_exchange_relation.insert()


            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=apple_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=msft_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()
            session.connection().execute(stmt, company_id=amd_company.id, sector_id=tech_sector.id)
            stmt = t_company_sector_relation.insert()

            session.commit()

            exec_import(config, session)

            session.commit()

            assert len(caplog.records) == 2
            
            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "Importing stock prices with no date filter."

            '''assert caplog.records[1].levelname == 'WARNING'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Company with ticker SNAP was not loaded from the db. Stock prices will not be saved."'''

            assert caplog.records[1].levelname == 'INFO'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Market data import exited successfully."

            logs = session.query(Log).all()
            assert len(logs) == 1
            assert logs[0].log_type == EXEC_IMPORT_STOCK_PRICES_LOG_TYPE
            assert logs[0].message == "Successfully imported stock prices supported by: mock_vendor to database."
            assert logs[0].data is None
            assert logs[0].update_stamp is not None
            cron_job_runs = session.query(CronJobRun).all()
            assert len(cron_job_runs) == 1
            assert cron_job_runs[0].success == True
            assert cron_job_runs[0].log_id == logs[0].id

            bar_data = session.query(EquityBarData).all()
            assert len(bar_data) == 4
            
            apple_bar_data = session.query(EquityBarData).filter(EquityBarData.company_id == apple_company.id).all()
            assert len(apple_bar_data) == 1

            assert apple_bar_data[0].bar_date.year == 2201
            assert apple_bar_data[0].bar_date.month == 1
            assert apple_bar_data[0].bar_date.day == 1
            assert apple_bar_data[0].bar_open == 300
            assert apple_bar_data[0].bar_high == 301
            assert apple_bar_data[0].bar_low == 290
            assert apple_bar_data[0].bar_close == 300.25
            assert apple_bar_data[0].bar_volume == 400


            msft_bar_data = session.query(EquityBarData).filter(EquityBarData.company_id == msft_company.id).all()
            assert len(msft_bar_data) == 2
            assert msft_bar_data[0].bar_date.year == 2200
            assert msft_bar_data[0].bar_date.month == 1
            assert msft_bar_data[0].bar_date.day == 1
            assert msft_bar_data[0].bar_open == 100
            assert msft_bar_data[0].bar_high == 105
            assert msft_bar_data[0].bar_low == 98
            assert msft_bar_data[0].bar_close == 99
            assert msft_bar_data[0].bar_volume == 200

            assert msft_bar_data[1].bar_date.year == 2200
            assert msft_bar_data[1].bar_date.month == 2
            assert msft_bar_data[1].bar_date.day == 2
            assert msft_bar_data[1].bar_open == 200
            assert msft_bar_data[1].bar_high == 210
            assert msft_bar_data[1].bar_low == 150
            assert msft_bar_data[1].bar_close == 155
            assert msft_bar_data[1].bar_volume == 300


            amd_bar_data = session.query(EquityBarData).filter(EquityBarData.company_id == amd_company.id).all()
            assert len(amd_bar_data) == 1
            assert amd_bar_data[0].bar_date.year == 2202
            assert amd_bar_data[0].bar_date.month == 10
            assert amd_bar_data[0].bar_date.day == 10
            assert amd_bar_data[0].bar_open == 400
            assert amd_bar_data[0].bar_high == 402
            assert amd_bar_data[0].bar_low == 290
            assert amd_bar_data[0].bar_close == 405
            assert amd_bar_data[0].bar_volume == 500

            amd_bar_data[0].locked = True
            session.commit()

            caplog.records.clear()
            exec_import(config, session)

            session.commit()

            assert len(caplog.records) == 2
            
            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert "Importing stock prices that was updated after or on:" in caplog.records[0].message

            assert caplog.records[1].levelname == 'INFO'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Market data import exited successfully."

            logs = session.query(Log).all()
            assert len(logs) == 2
            assert logs[0].log_type == EXEC_IMPORT_STOCK_PRICES_LOG_TYPE
            assert logs[0].message == "Successfully imported stock prices supported by: mock_vendor to database."
            assert logs[0].data is None
            assert logs[0].update_stamp is not None
            assert logs[1].log_type == EXEC_IMPORT_STOCK_PRICES_LOG_TYPE
            assert logs[1].message == "Successfully imported stock prices supported by: mock_vendor to database."
            assert logs[1].data is None
            assert logs[1].update_stamp is not None
            cron_job_runs = session.query(CronJobRun).all()
            assert len(cron_job_runs) == 2
            assert cron_job_runs[0].success == True
            assert cron_job_runs[0].log_id == logs[0].id
            assert cron_job_runs[1].success == True
            assert cron_job_runs[1].log_id == logs[1].id

            bar_data = session.query(EquityBarData).all()
            assert len(bar_data) == 6
            
            apple_bar_data = session.query(EquityBarData).filter(EquityBarData.company_id == apple_company.id).all()
            assert len(apple_bar_data) == 1
            assert apple_bar_data[0].bar_date.year == 2201
            assert apple_bar_data[0].bar_date.month == 1
            assert apple_bar_data[0].bar_date.day == 1
            assert apple_bar_data[0].bar_open == 3000
            assert apple_bar_data[0].bar_high == 3010
            assert apple_bar_data[0].bar_low == 2900
            assert apple_bar_data[0].bar_close == 3000.250
            assert apple_bar_data[0].bar_volume == 4000


            msft_bar_data = session.query(EquityBarData).filter(EquityBarData.company_id == msft_company.id).all()
            assert len(msft_bar_data) == 3
            assert msft_bar_data[0].bar_date.year == 2200
            assert msft_bar_data[0].bar_date.month == 1
            assert msft_bar_data[0].bar_date.day == 1
            assert msft_bar_data[0].bar_open == 1000
            assert msft_bar_data[0].bar_high == 1050
            assert msft_bar_data[0].bar_low == 980
            assert msft_bar_data[0].bar_close == 990
            assert msft_bar_data[0].bar_volume == 2000

            assert msft_bar_data[1].bar_date.year == 2200
            assert msft_bar_data[1].bar_date.month == 2
            assert msft_bar_data[1].bar_date.day == 2
            assert msft_bar_data[1].bar_open == 2000
            assert msft_bar_data[1].bar_high == 2100
            assert msft_bar_data[1].bar_low == 1500
            assert msft_bar_data[1].bar_close == 1550
            assert msft_bar_data[1].bar_volume == 3000

            assert msft_bar_data[2].bar_date.year == 2200
            assert msft_bar_data[2].bar_date.month == 3
            assert msft_bar_data[2].bar_date.day == 3
            assert msft_bar_data[2].bar_open == 3000
            assert msft_bar_data[2].bar_high == 3100
            assert msft_bar_data[2].bar_low == 2500
            assert msft_bar_data[2].bar_close == 2550
            assert msft_bar_data[2].bar_volume == 3000


            amd_bar_data = session.query(EquityBarData).filter(EquityBarData.company_id == amd_company.id).order_by(EquityBarData.bar_date).all()
            assert len(amd_bar_data) == 2
            assert amd_bar_data[0].bar_date.year == 2202
            assert amd_bar_data[0].bar_date.month == 10
            assert amd_bar_data[0].bar_date.day == 10
            assert amd_bar_data[0].bar_open == 400
            assert amd_bar_data[0].bar_high == 402
            assert amd_bar_data[0].bar_low == 290
            assert amd_bar_data[0].bar_close == 405
            assert amd_bar_data[0].bar_volume == 500

            assert amd_bar_data[1].bar_date.year == 2202
            assert amd_bar_data[1].bar_date.month == 11
            assert amd_bar_data[1].bar_date.day == 10
            assert amd_bar_data[1].bar_open == 5000
            assert amd_bar_data[1].bar_high == 6000
            assert amd_bar_data[1].bar_low == 7000
            assert amd_bar_data[1].bar_close == 8000
            assert amd_bar_data[1].bar_volume == 6000


def test_exec_import_fx_data(caplog):
    absolute_path = os.path.join(sys.path[0], 'test_exec_import_fx_data.json')

    #clean up db in case
    with open(absolute_path, 'r') as f:
        config_raw = f.read()
        config = json.loads(config_raw)
        engine = create_engine(config['dbConnString'])

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config['dbConnString'], template_name='first_session') as session:
            cleanup_db(session.connection())

            exec_import(config, session)

            session.commit()

            assert len(caplog.records) == 2
            
            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "Importing fx data with no date filter."

            assert caplog.records[1].levelname == 'INFO'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Market data import exited successfully."

            logs = session.query(Log).all()
            assert len(logs) == 1
            assert logs[0].log_type == EXEC_IMPORT_FX_DATA_LOG_TYPE
            assert logs[0].message == "Successfully imported fx data supported by: mock_vendor to database."
            assert logs[0].data is None
            assert logs[0].update_stamp is not None
            cron_job_runs = session.query(CronJobRun).all()
            assert len(cron_job_runs) == 1
            assert cron_job_runs[0].success == True
            assert cron_job_runs[0].log_id == logs[0].id

            bar_data = session.query(CurrencyBarData).all()
            assert len(bar_data) == 3
            
            usd_cad_bar_data = session.query(CurrencyBarData).filter(CurrencyBarData.symbol == "USD.CAD").all()
            assert len(usd_cad_bar_data) == 2

            assert usd_cad_bar_data[0].bar_date.year == 2200
            assert usd_cad_bar_data[0].bar_date.month == 1
            assert usd_cad_bar_data[0].bar_date.day == 1
            assert usd_cad_bar_data[0].bar_open == 100
            assert usd_cad_bar_data[0].bar_high == 105
            assert usd_cad_bar_data[0].bar_low == 98
            assert usd_cad_bar_data[0].bar_close == 99
            assert usd_cad_bar_data[0].bar_volume == 200
            assert usd_cad_bar_data[1].bar_date.year == 2201
            assert usd_cad_bar_data[1].bar_date.month == 1
            assert usd_cad_bar_data[1].bar_date.day == 1
            assert usd_cad_bar_data[1].bar_open == 300
            assert usd_cad_bar_data[1].bar_high == 301
            assert usd_cad_bar_data[1].bar_low == 290
            assert usd_cad_bar_data[1].bar_close == 300.25
            assert usd_cad_bar_data[1].bar_volume == 400


            eur_usd_bar_data = session.query(CurrencyBarData).filter(CurrencyBarData.symbol == "EUR.USD").all()
            assert len(eur_usd_bar_data) == 1
            assert eur_usd_bar_data[0].bar_date.year == 2200
            assert eur_usd_bar_data[0].bar_date.month == 2
            assert eur_usd_bar_data[0].bar_date.day == 2
            assert eur_usd_bar_data[0].bar_open == 200
            assert eur_usd_bar_data[0].bar_high == 210
            assert eur_usd_bar_data[0].bar_low == 150
            assert eur_usd_bar_data[0].bar_close == 155
            assert eur_usd_bar_data[0].bar_volume == 300

            usd_cad_bar_data[0].locked = True
            session.commit()

            caplog.records.clear()
            exec_import(config, session)

            session.commit()

            assert len(caplog.records) == 2
            
            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert "Importing fx data that was updated after or on:" in caplog.records[0].message

            assert caplog.records[1].levelname == 'INFO'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Market data import exited successfully."

            logs = session.query(Log).all()
            assert len(logs) == 2
            assert logs[0].log_type == EXEC_IMPORT_FX_DATA_LOG_TYPE
            assert logs[0].message == "Successfully imported fx data supported by: mock_vendor to database."
            assert logs[0].data is None
            assert logs[0].update_stamp is not None
            assert logs[1].log_type == EXEC_IMPORT_FX_DATA_LOG_TYPE
            assert logs[1].message == "Successfully imported fx data supported by: mock_vendor to database."
            assert logs[1].data is None
            assert logs[1].update_stamp is not None
            cron_job_runs = session.query(CronJobRun).all()
            assert len(cron_job_runs) == 2
            assert cron_job_runs[0].success == True
            assert cron_job_runs[0].log_id == logs[0].id
            assert cron_job_runs[1].success == True
            assert cron_job_runs[1].log_id == logs[1].id
            
            bar_data = session.query(CurrencyBarData).all()
            assert len(bar_data) == 4
            
            usd_cad_bar_data = session.query(CurrencyBarData).filter(CurrencyBarData.symbol == "USD.CAD").all()
            assert len(usd_cad_bar_data) == 2

            assert usd_cad_bar_data[0].bar_date.year == 2200
            assert usd_cad_bar_data[0].bar_date.month == 1
            assert usd_cad_bar_data[0].bar_date.day == 1
            assert usd_cad_bar_data[0].bar_open == 100
            assert usd_cad_bar_data[0].bar_high == 105
            assert usd_cad_bar_data[0].bar_low == 98
            assert usd_cad_bar_data[0].bar_close == 99
            assert usd_cad_bar_data[0].bar_volume == 200
            assert usd_cad_bar_data[1].bar_date.year == 2201
            assert usd_cad_bar_data[1].bar_date.month == 1
            assert usd_cad_bar_data[1].bar_date.day == 1
            assert usd_cad_bar_data[1].bar_open == 3000
            assert usd_cad_bar_data[1].bar_high == 3010
            assert usd_cad_bar_data[1].bar_low == 2900
            assert usd_cad_bar_data[1].bar_close == 3000.25
            assert usd_cad_bar_data[1].bar_volume == 4000


            eur_usd_bar_data = session.query(CurrencyBarData).filter(CurrencyBarData.symbol == "EUR.USD").all()
            assert len(eur_usd_bar_data) == 1
            assert eur_usd_bar_data[0].bar_date.year == 2200
            assert eur_usd_bar_data[0].bar_date.month == 2
            assert eur_usd_bar_data[0].bar_date.day == 2
            assert eur_usd_bar_data[0].bar_open == 2000
            assert eur_usd_bar_data[0].bar_high == 2100
            assert eur_usd_bar_data[0].bar_low == 1500
            assert eur_usd_bar_data[0].bar_close == 1550
            assert eur_usd_bar_data[0].bar_volume == 3000


            usd_jpy_bar_data = session.query(CurrencyBarData).filter(CurrencyBarData.symbol == "USD.JPY").all()
            assert len(usd_jpy_bar_data) == 1
            assert usd_jpy_bar_data[0].bar_date.year == 2200
            assert usd_jpy_bar_data[0].bar_date.month == 1
            assert usd_jpy_bar_data[0].bar_date.day == 1
            assert usd_jpy_bar_data[0].bar_open == 10000
            assert usd_jpy_bar_data[0].bar_high == 10000
            assert usd_jpy_bar_data[0].bar_low == 10000
            assert usd_jpy_bar_data[0].bar_close == 10000
            assert usd_jpy_bar_data[0].bar_volume == 10000
            