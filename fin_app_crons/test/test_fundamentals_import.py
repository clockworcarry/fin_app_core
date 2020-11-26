from fin_app_crons.fundamentals_import import exec_import
from db_models.models import *

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

import logging, os, sys, json

def test_exec_import_invalid_config_file(caplog):
    exec_import("bad_file")
    for record in caplog.records:
        assert record.levelname == 'CRITICAL'
        assert record.name == 'root_logger'
        assert record.message == "[Errno 2] No such file or directory: 'bad_file'"

def test_exec_filtered_out(caplog):
    absolute_path = os.path.join(sys.path[0], 'filter_test.json')
    exec_import(absolute_path)
    
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
    exec_import(absolute_path)

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
    try:
        absolute_path = os.path.join(sys.path[0], 'test_exec_import_empty_db.json')

        #clean up db in case
        with open(absolute_path, 'r') as f:
            config_raw = f.read()
            config = json.loads(config_raw)
            engine = create_engine(config['dbConnString'])
            with engine.connect() as connection:
                cleanup_db(connection)

        exec_import(absolute_path)

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

        with open(absolute_path, 'r') as f:
            config_raw = f.read()
            config = json.loads(config_raw)
            engine = create_engine(config['dbConnString'])
            with engine.connect() as connection:
                cleanup_db(connection)
                Session = sessionmaker(bind=engine)
                session = Session()
                
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
            exec_import(absolute_path)

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
            assert db_companies[0].sector_id == 1
            assert db_companies[0].delisted == True

            assert db_companies[0].ticker == 'BBUCQ'
            assert db_companies[0].name == 'Big Buck Brewery & Steakhouse Inc'
            assert db_companies[0].locked == False
            assert db_companies[0].sector_id == 2
            assert db_companies[0].delisted == False

            assert db_companies[0].ticker == 'AREM1'
            assert db_companies[0].name == 'Aremissoft Corp'
            assert db_companies[0].locked == False
            assert db_companies[0].sector_id == 4
            assert db_companies[0].delisted == True

            assert db_companies[0].ticker == 'GOVB'
            assert db_companies[0].name == 'Gouverneur Bancorp Inc'
            assert db_companies[0].locked == False
            assert db_companies[0].sector_id == 3
            assert db_companies[0].delisted == False

            assert db_companies[0].ticker == 'WAVT'
            assert db_companies[0].name == 'Wave Technologies International Inc'
            assert db_companies[0].locked == False
            assert db_companies[0].sector_id == 1
            assert db_companies[0].delisted == True

            cleanup_db(connection)
    
    except Exception as gen_ex:
        print(str(gen_ex))




def test_existing_db_missing_records(caplog):
    try:
        absolute_path = os.path.join(sys.path[0], 'test_exec_import_existing_db_missing_records.json')

        #clean up db in case
        with open(absolute_path, 'r') as f:
            config_raw = f.read()
            config = json.loads(config_raw)
            engine = create_engine(config['dbConnString'])

            with engine.connect() as connection:
                cleanup_db(connection)

                Session = sessionmaker(bind=engine)
                session = Session()

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

                session.add_all([apple_company, msft_company, amd_company, twtr_company, cmg_company])

                session.commit()

                #now that db is populated with records, execute an import than will contain some of those and new ones

                exec_import(absolute_path)

                assert len(caplog.records) == 4

                assert caplog.records[0].levelname == 'WARNING'
                assert caplog.records[0].name == 'fund_cron_logger'
                assert caplog.records[0].message == "Unknown industry detected: Internet Content & Information"

                assert caplog.records[1].levelname == 'WARNING'
                assert caplog.records[1].name == 'fund_cron_logger'
                assert caplog.records[1].message == "Unknown industry detected: Home Improvement Retail"

                assert caplog.records[2].levelname == 'INFO'
                assert caplog.records[2].name == 'fund_cron_logger'
                assert caplog.records[2].message == "The following vendor source is filtered out: vendor_1"

                assert caplog.records[3].levelname == 'INFO'
                assert caplog.records[3].name == 'fund_cron_logger'
                assert caplog.records[3].message == "Fundamentals import exited successfully."

                #check db has correct records after import
                db_companies = session.query(Company).all()
                assert len(db_companies) == 8

    except Exception as gen_ex:
        print(gen_ex)

def test_existing_db_no_missing_records(caplog):
    pass


    