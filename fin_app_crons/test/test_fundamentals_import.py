from fin_app_crons.fundamentals_import import exec_import
from db_models.models import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

import logging, os, sys, json

def test_exec_filtered_out(caplog):
    absolute_path = os.path.join(sys.path[0], 'filter_test.json')
    with open(absolute_path, 'r') as f:
        file_content_raw = f.read()
        config_json_content = json.loads(file_content_raw)
        exec_import(config_json_content, None)
        
        assert len(caplog.records) == 3
        
        assert caplog.records[0].levelname == 'INFO'
        assert caplog.records[0].name == 'fund_cron_logger'
        assert caplog.records[0].message == "The following vendor source is filtered out: vendor_1"

        assert caplog.records[1].levelname == 'INFO'
        assert caplog.records[1].name == 'fund_cron_logger'
        assert caplog.records[1].message == "The following vendor source is filtered out: vendor_2"

        assert caplog.records[2].levelname == 'CRITICAL'
        assert caplog.records[2].name == 'fund_cron_logger'
        assert caplog.records[2].message == "'NoneType' object has no attribute 'get_all_companies'"

        caplog.clear()

        absolute_path = os.path.join(sys.path[0], 'filter_test_2.json')
        exec_import(config_json_content, None)

        assert len(caplog.records) == 3
        
        assert caplog.records[0].levelname == 'INFO'
        assert caplog.records[0].name == 'fund_cron_logger'
        assert caplog.records[0].message == "The following vendor source is filtered out: vendor_1"

        assert caplog.records[1].levelname == 'INFO'
        assert caplog.records[1].name == 'fund_cron_logger'
        assert caplog.records[1].message == "The following vendor source is filtered out: vendor_2"

        assert caplog.records[2].levelname == 'CRITICAL'
        assert caplog.records[2].name == 'fund_cron_logger'
        assert caplog.records[2].message == "'NoneType' object has no attribute 'get_all_companies'"

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
    except Exception as gen_ex:
        print(str(gen_ex))

def test_empty_db_missing_records(caplog):
    absolute_path = os.path.join(sys.path[0], 'test_exec_import_empty_db.json')

    #clean up db in case
    with open(absolute_path, 'r') as f:
        config_raw = f.read()
        config = json.loads(config_raw)

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config['dbConnString'], template_name='basic') as session:
            cleanup_db(session.connection())
            exec_import(config, session)

            assert len(caplog.records) == 18

            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "Unknown exchange detected: Missing"

            assert caplog.records[1].levelname == 'WARNING'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Unknown exchange detected: OTC"

            assert caplog.records[2].levelname == 'WARNING'
            assert caplog.records[2].name == 'fund_cron_logger'
            assert caplog.records[2].message == "Unknown exchange detected: NASDAQ"

            assert caplog.records[3].levelname == 'WARNING'
            assert caplog.records[3].name == 'fund_cron_logger'
            assert caplog.records[3].message == "Unknown sector detected: Technology"

            assert caplog.records[4].levelname == 'WARNING'
            assert caplog.records[4].name == 'fund_cron_logger'
            assert caplog.records[4].message == "Unknown sector detected: Consumer Cyclical"

            assert caplog.records[5].levelname == 'WARNING'
            assert caplog.records[5].name == 'fund_cron_logger'
            assert caplog.records[5].message == "Unknown sector detected: Missing"

            assert caplog.records[6].levelname == 'WARNING'
            assert caplog.records[6].name == 'fund_cron_logger'
            assert caplog.records[6].message == "Unknown sector detected: Financial Services"

            assert caplog.records[7].levelname == 'WARNING'
            assert caplog.records[7].name == 'fund_cron_logger'
            assert caplog.records[7].message == "Unknown industry detected: Software - Application"

            assert caplog.records[8].levelname == 'WARNING'
            assert caplog.records[8].name == 'fund_cron_logger'
            assert caplog.records[8].message == "Unknown industry detected: Restaurants"

            assert caplog.records[9].levelname == 'WARNING'
            assert caplog.records[9].name == 'fund_cron_logger'
            assert caplog.records[9].message == "Unknown industry detected: Banks - Regional"

            assert caplog.records[10].levelname == 'WARNING'
            assert caplog.records[10].name == 'fund_cron_logger'
            assert caplog.records[10].message == "Unknown industry detected: Missing"

            assert caplog.records[11].levelname == 'WARNING'
            assert caplog.records[11].name == 'fund_cron_logger'
            assert caplog.records[11].message == "None result when fetching first sector matching: Technology"

            assert caplog.records[12].levelname == 'WARNING'
            assert caplog.records[12].name == 'fund_cron_logger'
            assert caplog.records[12].message == "None result when fetching first sector matching: Consumer Cyclical"

            assert caplog.records[13].levelname == 'WARNING'
            assert caplog.records[13].name == 'fund_cron_logger'
            assert caplog.records[13].message == "None result when fetching first sector matching: Missing"

            assert caplog.records[14].levelname == 'WARNING'
            assert caplog.records[14].name == 'fund_cron_logger'
            assert caplog.records[14].message == "None result when fetching first sector matching: Financial Services"

            assert caplog.records[15].levelname == 'WARNING'
            assert caplog.records[15].name == 'fund_cron_logger'
            assert caplog.records[15].message == "None result when fetching first sector matching: Technology"

            assert caplog.records[16].levelname == 'INFO'
            assert caplog.records[16].name == 'fund_cron_logger'
            assert caplog.records[16].message == "The following vendor source is filtered out: vendor_1"

            assert caplog.records[17].levelname == 'INFO'
            assert caplog.records[17].name == 'fund_cron_logger'
            assert caplog.records[17].message == "Fundamentals import exited successfully."

        
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

            reg_banking_industry = Industry(sector_id=fin_services_sectors.id, name='Banks - Regional', name_code='Reg_Banking')
            session.add(reg_banking_industry)

            missing_industry = Industry(sector_id=missing_sector.id, name='Missing', name_code='Missing')
            session.add(missing_industry)

            session.commit()
        
            #clear previously caught logs
            caplog.records.clear()

            #retry after adding previously missing records
            exec_import(config, session)

            assert len(caplog.records) == 2

            assert caplog.records[0].levelname == 'INFO'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "The following vendor source is filtered out: vendor_1"

            assert caplog.records[1].levelname == 'INFO'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Fundamentals import exited successfully."

            db_companies = session.query(Company).order_by(Company.id).all()
            assert len(db_companies) == 5

            assert db_companies[0].ticker == 'NWGN1'
            assert db_companies[0].name == 'Newgen Results Corp'
            assert db_companies[0].locked == False
            assert db_companies[0].sector_id == tech_sector.id
            assert db_companies[0].delisted == True

            assert db_companies[1].ticker == 'BBUCQ'
            assert db_companies[1].name == 'Big Buck Brewery & Steakhouse Inc'
            assert db_companies[1].locked == False
            assert db_companies[1].sector_id == cons_cyc_sector.id
            assert db_companies[1].delisted == False

            assert db_companies[2].ticker == 'AREM1'
            assert db_companies[2].name == 'Aremissoft Corp'
            assert db_companies[2].locked == False
            assert db_companies[2].sector_id == missing_sector.id
            assert db_companies[2].delisted == True

            assert db_companies[3].ticker == 'GOVB'
            assert db_companies[3].name == 'Gouverneur Bancorp Inc'
            assert db_companies[3].locked == False
            assert db_companies[3].sector_id == fin_services_sectors.id
            assert db_companies[3].delisted == False

            assert db_companies[4].ticker == 'WAVT'
            assert db_companies[4].name == 'Wave Technologies International Inc'
            assert db_companies[4].locked == False
            assert db_companies[4].sector_id == tech_sector.id
            assert db_companies[4].delisted == True

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
            apple_company = Company(sector_id=tech_sector.id, ticker='AAPL', name='Apple Inc', delisted=False)
            msft_company = Company(sector_id=tech_sector.id, ticker='MSFT', name='Microsoft Corp', delisted=False)
            amd_company = Company(sector_id=tech_sector.id, ticker='AMD', name='Advanced Micro Devices Inc', locked=True, delisted=True)
            twtr_company = Company(sector_id=tech_sector.id, ticker='TWTR', name='Twitter Inc', locked=False, delisted=False)
            cmg_company = Company(sector_id=cons_cyc_sector.id, ticker='CMG', name='Chipotle Grill', locked=True, delisted=False)
            fb_company = Company(sector_id=tech_sector.id, ticker='FB', name='Facebook Inc', locked=False, delisted=False)

            session.add_all([apple_company, msft_company, amd_company, twtr_company, cmg_company, fb_company])

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

            assert len(caplog.records) == 6

            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].name == 'fund_cron_logger'
            assert caplog.records[0].message == "Unknown industry detected: Internet Content & Information"

            assert caplog.records[1].levelname == 'WARNING'
            assert caplog.records[1].name == 'fund_cron_logger'
            assert caplog.records[1].message == "Unknown industry detected: Home Improvement Retail"

            assert caplog.records[2].levelname == 'INFO'
            assert caplog.records[2].name == 'fund_cron_logger'
            assert caplog.records[2].message == "The following ticker was updated in the company table: MSFT"

            assert caplog.records[3].levelname == 'INFO'
            assert caplog.records[3].name == 'fund_cron_logger'
            assert caplog.records[3].message == "The following ticker was updated in the company table: TWTR"

            assert caplog.records[4].levelname == 'INFO'
            assert caplog.records[4].name == 'fund_cron_logger'
            assert caplog.records[4].message == "The following vendor source is filtered out: vendor_1"

            assert caplog.records[5].levelname == 'INFO'
            assert caplog.records[5].name == 'fund_cron_logger'
            assert caplog.records[5].message == "Fundamentals import exited successfully."

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

            #untouched because input is identical to db record
            assert db_companies[5].ticker == 'FB'
            assert db_companies[5].name == 'Facebook Inc'
            assert db_companies[5].delisted == False
            assert db_companies[5].locked == False
            assert db_companies[5].update_stamp == fb_stamp

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