from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from api.routers.company_metric_api import *

client = TestClient(app)


class TestCompanyMetricApi:
    @classmethod
    def setup_class(cls):
        absolute_path = os.path.join(sys.path[0], 'config.json')
        with open(absolute_path, 'r') as f:
            file_content_raw = f.read()
            config_json_content = json.loads(file_content_raw)
            init_config(config_json_content)
            TestCompanyMetricApi.db_conn_str = config_json_content['dbConnString']


    def test_get_version(self):
        response = client.get("/version")
        assert response.status_code == 200
        assert response.json() == {"version": "0.0.1"}

    def test_create_metric_description_missing_data(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        response = client.post(
                                    "/companyMetric/description",
                                    json={
                                            "code": "123",
                                            "display_name": 1
                                        }
                            )

        assert response.status_code == 422

    def test_create_metric_description_valid(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        response = client.post(
                                    "/companyMetric/description",
                                    json={
                                            "code": "rev_usa",
                                            "display_name": "Revenue United States",
                                            "metric_data_type": 0
                                        }
                            )
                            
        assert response.status_code == 201
        response = response.json()
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            query_res = session.query(CompanyMetricDescription).all()
            assert len(query_res) == 1
            assert query_res[0].code == 'rev_usa'
            assert query_res[0].display_name == 'Revenue United States'
            assert query_res[0].metric_data_type == 0
            assert response['id'] == query_res[0].id
            assert response['code'] == query_res[0].code
            assert response['display_name'] == query_res[0].display_name
            assert response['metric_data_type'] == query_res[0].metric_data_type


    def test_update_metric_description_valid(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)
            session.commit()

            url = "/companyMetric/description/" + str(new_desc.id)
            response = client.post(
                                    url,
                                    json={
                                            "code": "updated_code",
                                            "display_name": "Revenue United States",
                                            "metric_data_type": 2
                                        }
                            )
                            
            assert response.status_code == 200
            response = response.json()
            session.expire_all()     
            query_res = session.query(CompanyMetricDescription).all()
            assert len(query_res) == 1
            assert query_res[0].code == 'updated_code'
            assert query_res[0].display_name == 'Revenue United States'
            assert query_res[0].metric_data_type == 2
            assert response['id'] == query_res[0].id
            assert response['code'] == query_res[0].code
            assert response['display_name'] == query_res[0].display_name
            assert response['metric_data_type'] == query_res[0].metric_data_type

    def test_delete_metric_description_valid(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)
            session.commit()

            url = "/companyMetric/description/" + str(new_desc.id)
            response = client.delete(url)
                            
            assert response.status_code == 200
            session.expire_all()     
            query_res = session.query(CompanyMetricDescription).all()
            assert len(query_res) == 0


    def test_create_metric_missing_data(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        response = client.post(
                                    "/companyMetric/20614",
                                    json={}
                            )
        assert response.status_code == 405

        response = client.post(
                                    "/companyMetric/20614/123",
                                    json={}
                            )
        assert response.status_code == 422

    def test_create_metric_invalid_desc_id(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        response = client.post(
                                    "/companyMetric/20614/123",
                                    json={
                                            "look_back": -1,
                                            "data": 64,
                                            "date_recorded": "2019-06-30"
                                        }
                            )
        assert response.status_code == 500
        assert "psycopg2.errors.ForeignKeyViolation" in response.text
        

    def test_create_metric_valid(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            apple_company = Company(ticker='AAPL', name='Apple Inc', delisted=False)
            session.add(apple_company)

            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)
            session.commit()

            url = "/companyMetric/" + str(apple_company.id) + "/" + str(new_desc.id)
            response = client.post(
                                    url,
                                    json={
                                            "look_back": LOOK_BACK_QUARTER,
                                            "data": 10,
                                            "date_recorded": "2019-12-31"
                                        }
                            )
                            
            assert response.status_code == 201
            response = response.json()
            session.expire_all()     
            query_res = session.query(CompanyMetric).all()
            assert len(query_res) == 1
            assert query_res[0].data == 10
            assert query_res[0].look_back == LOOK_BACK_QUARTER
            assert response['id'] == query_res[0].id
            assert response['data'] == query_res[0].data
            assert response['look_back'] == query_res[0].look_back

    def test_update_metric_valid(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            apple_company = Company(ticker='AAPL', name='Apple Inc', delisted=False)
            session.add(apple_company)

            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)

            session.flush()
            
            new_metric = CompanyMetric(data='10', look_back=LOOK_BACK_QUARTER, company_id=apple_company.id, company_metric_description_id=new_desc.id, date_recorded=datetime.date(2019, 12, 31))
            session.add(new_metric)
            session.commit()

            url = "/companyMetric/" + str(apple_company.id) + "/" + str(new_desc.id) + "/" + str(new_metric.id)
            response = client.post(
                                    url,
                                    json={
                                            "look_back": LOOK_BACK_NINE_MO,
                                            "data": 65,
                                            "date_recorded": "2019-9-30"
                                        }
                            )
                            
            assert response.status_code == 200
            response = response.json()
            session.expire_all()     
            query_res = session.query(CompanyMetric).all()
            assert len(query_res) == 1
            assert query_res[0].data == 65
            assert query_res[0].look_back == LOOK_BACK_NINE_MO
            assert query_res[0].date_recorded.year == 2019
            assert query_res[0].date_recorded.month == 9
            assert response['id'] == query_res[0].id
            assert response['data'] == query_res[0].data
            assert response['look_back'] == query_res[0].look_back

    def test_delete_metric_valid(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            apple_company = Company(ticker='AAPL', name='Apple Inc', delisted=False)
            session.add(apple_company)

            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)

            session.flush()
            
            new_metric = CompanyMetric(data='10', look_back=LOOK_BACK_QUARTER, company_id=apple_company.id, company_metric_description_id=new_desc.id, date_recorded=datetime.date(2019, 12, 31))
            session.add(new_metric)
            session.commit()

            url = "/companyMetric/" + str(new_metric.id)
            response = client.delete(url)
                            
            assert response.status_code == 200
            session.expire_all()     
            query_res = session.query(CompanyMetric).all()
            assert len(query_res) == 0

    def test_create_metric_description_note_valid(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)   
                            
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            apple_company = Company(ticker='AAPL', name='Apple Inc', delisted=False)
            session.add(apple_company)

            msft_company = Company(ticker='MSFT', name='Microsoft', delisted=False)
            session.add(msft_company)

            amd_company = Company(ticker='AMD', name='Advanced Micro Chip', delisted=False)
            session.add(amd_company)

            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)

            session.commit()

            data = "This represents the revenue in the usa."

            response = client.post(
                            "/companyMetric/description/note/" + str(new_desc.id),
                            json={
                                    "data": data,
                                    "note_type": NOTE_TYPE_TEXT
                                }
                    )


            assert response.status_code == 201
            response = response.json()
            note_query_res = session.query(CompanyMetricDescriptionNote).all() 
            assert len(note_query_res) == 1
            note_id = note_query_res[0].id
            assert note_query_res[0].note_type == NOTE_TYPE_TEXT
            decoded_data = note_query_res[0].note_data.decode('ascii')
            assert decoded_data == "This represents the revenue in the usa."
            relation_query_res = session.query(CompanyMetricRelation).all()
            assert len(relation_query_res) == 1
            assert relation_query_res[0].company_metric_description_id == new_desc.id
            assert relation_query_res[0].company_metric_description_note_id == note_id
            assert relation_query_res[0].company_id == None
            
            assert response['note_id'] == note_query_res[0].id
            assert response['metric_description_id'] == new_desc.id
            #resp_data = base64.b64decode(response['data'])
            #assert resp_data == data
            assert response['note_type'] == note_query_res[0].note_type
            assert 'company_ids' not in response or response['company_ids'] is None
            
            session.query(CompanyMetricDescriptionNote).delete()
            session.query(CompanyMetricRelation).delete()
            session.commit()

            data = "This represents the revenue in canada."

            response = client.post(
                            "/companyMetric/description/note/" + str(new_desc.id),
                            json={
                                    "data": data,
                                    "note_type": NOTE_TYPE_TEXT,
                                    "company_ids": [apple_company.id, msft_company.id, amd_company.id]
                                }
                    )


            assert response.status_code == 201
            response = response.json()
            note_query_res = session.query(CompanyMetricDescriptionNote).all() 
            assert len(note_query_res) == 1
            note_id = note_query_res[0].id
            assert note_query_res[0].note_type == NOTE_TYPE_TEXT
            decoded_data = note_query_res[0].note_data.decode('ascii')
            assert decoded_data == "This represents the revenue in canada."
            relation_query_res = session.query(CompanyMetricRelation).order_by(CompanyMetricRelation.company_id).all()
            assert len(relation_query_res) == 3
            assert relation_query_res[0].company_metric_description_id == new_desc.id
            assert relation_query_res[0].company_metric_description_note_id == note_id
            assert relation_query_res[0].company_id == apple_company.id

            assert relation_query_res[1].company_metric_description_id == new_desc.id
            assert relation_query_res[1].company_metric_description_note_id == note_id
            assert relation_query_res[1].company_id == msft_company.id

            assert relation_query_res[2].company_metric_description_id == new_desc.id
            assert relation_query_res[2].company_metric_description_note_id == note_id
            assert relation_query_res[2].company_id == amd_company.id
            
            assert response['note_id'] == note_query_res[0].id
            assert response['metric_description_id'] == new_desc.id
            #resp_data = base64.b64decode(response['data'])
            #assert resp_data == data
            assert response['note_type'] == note_query_res[0].note_type
            assert len(response['company_ids']) == 3




    def test_update_metric_description_note_valid(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)   
                            
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            apple_company = Company(ticker='AAPL', name='Apple Inc', delisted=False)
            session.add(apple_company)

            msft_company = Company(ticker='MSFT', name='Microsoft', delisted=False)
            session.add(msft_company)

            amd_company = Company(ticker='AMD', name='Advanced Micro Chip', delisted=False)
            session.add(amd_company)

            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)

            session.commit()

            data = "This represents the revenue in the usa."

            response = client.post(
                            "/companyMetric/description/note/" + str(new_desc.id),
                            json={
                                    "data": data,
                                    "note_type": NOTE_TYPE_TEXT
                                }
                    )


            assert response.status_code == 201
            response = response.json()
            note_query_res = session.query(CompanyMetricDescriptionNote).all() 
            assert len(note_query_res) == 1
            note_id = note_query_res[0].id
            assert note_query_res[0].note_type == NOTE_TYPE_TEXT
            decoded_data = note_query_res[0].note_data.decode('ascii')
            assert decoded_data == "This represents the revenue in the usa."
            relation_query_res = session.query(CompanyMetricRelation).all()
            assert len(relation_query_res) == 1
            assert relation_query_res[0].company_metric_description_id == new_desc.id
            assert relation_query_res[0].company_metric_description_note_id == note_id
            assert relation_query_res[0].company_id == None
            
            assert response['note_id'] == note_query_res[0].id
            assert response['metric_description_id'] == new_desc.id
            #resp_data = base64.b64decode(response['data'])
            #assert resp_data == data
            assert response['note_type'] == note_query_res[0].note_type
            assert 'company_ids' not in response or response['company_ids'] is None


            data = b"This represents the revenue in India."
            data = base64.b64encode(data)

            response = client.post(
                            "/companyMetric/description/note/" + str(new_desc.id) + "/" + str(note_query_res[0].id),
                            json={
                                    "data": data,
                                    "note_type": NOTE_TYPE_TEXT_DOC
                                }
                    )
            
            session.expire_all()
            assert response.status_code == 200
            response = response.json()
            update_note_query_res = session.query(CompanyMetricDescriptionNote).all() 
            assert len(note_query_res) == 1
            assert update_note_query_res[0].id == note_query_res[0].id
            note_id = update_note_query_res[0].id
            assert update_note_query_res[0].note_type == NOTE_TYPE_TEXT_DOC
            decoded_data = update_note_query_res[0].note_data.decode('ascii')
            assert decoded_data == "This represents the revenue in India."
            update_relation_query_res = session.query(CompanyMetricRelation).all()
            assert len(update_relation_query_res) == 1
            assert update_relation_query_res[0].company_metric_description_id == new_desc.id
            assert update_relation_query_res[0].company_metric_description_note_id == note_id
            assert update_relation_query_res[0].company_id == None
            
            assert response['note_id'] == update_note_query_res[0].id
            assert response['metric_description_id'] == new_desc.id
            #resp_data = base64.b64decode(response['data'])
            #assert resp_data == data
            assert response['note_type'] == update_note_query_res[0].note_type
            assert 'company_ids' not in response or response['company_ids'] is None


            response = client.post(
                            "/companyMetric/description/note/" + str(new_desc.id) + "/" + str(note_query_res[0].id),
                            json={
                                    "data": data,
                                    "note_type": NOTE_TYPE_TEXT_DOC,
                                    "company_ids": [apple_company.id, msft_company.id, amd_company.id]
                                }
                    )
            
            session.expire_all()
            assert response.status_code == 200
            response = response.json()
            update_note_query_res = session.query(CompanyMetricDescriptionNote).all() 
            assert len(note_query_res) == 1
            assert update_note_query_res[0].id == note_query_res[0].id
            note_id = update_note_query_res[0].id
            assert update_note_query_res[0].note_type == NOTE_TYPE_TEXT_DOC
            decoded_data = update_note_query_res[0].note_data.decode('ascii')
            assert decoded_data == "This represents the revenue in India."
            update_relation_query_res = session.query(CompanyMetricRelation).order_by(CompanyMetricRelation.company_id).all()
            assert len(update_relation_query_res) == 3
            assert update_relation_query_res[0].company_metric_description_id == new_desc.id
            assert update_relation_query_res[0].company_metric_description_note_id == note_id
            assert update_relation_query_res[0].company_id == apple_company.id

            assert update_relation_query_res[1].company_metric_description_id == new_desc.id
            assert update_relation_query_res[1].company_metric_description_note_id == note_id
            assert update_relation_query_res[1].company_id == msft_company.id

            assert update_relation_query_res[2].company_metric_description_id == new_desc.id
            assert update_relation_query_res[2].company_metric_description_note_id == note_id
            assert update_relation_query_res[2].company_id == amd_company.id
            
            assert response['note_id'] == update_note_query_res[0].id
            assert response['metric_description_id'] == new_desc.id
            #resp_data = base64.b64decode(response['data'])
            #assert resp_data == data
            assert response['note_type'] == update_note_query_res[0].note_type
            assert len(response['company_ids']) == from api.routers.company_metric_api import *3



            response = client.post(
                            "/companyMetric/description/note/" + str(new_desc.id) + "/" + str(note_query_res[0].id),
                            json={
                                    "data": data,
                                    "note_type": NOTE_TYPE_TEXT_DOC,
                                    "company_ids": [msft_company.id, amd_company.id]
                                }
                    )

            session.expire_all()
            assert response.status_code == 200
            response = response.json()
            update_note_query_res = session.query(CompanyMetricDescriptionNote).all() 
            assert len(note_query_res) == 1
            assert update_note_query_res[0].id == note_query_res[0].id
            note_id = update_note_query_res[0].id
            assert update_note_query_res[0].note_type == NOTE_TYPE_TEXT_DOC
            decoded_data = update_note_query_res[0].note_data.decode('ascii')
            assert decoded_data == "This represents the revenue in India."
            update_relation_query_res = session.query(CompanyMetricRelation).order_by(CompanyMetricRelation.company_id).all()
            assert len(update_relation_query_res) == 2
            assert update_relation_query_res[0].company_metric_description_id == new_desc.id
            assert update_relation_query_res[0].company_metric_description_note_id == note_id
            assert update_relation_query_res[0].company_id == msft_company.id

            assert update_relation_query_res[1].company_metric_description_id == new_desc.id
            assert update_relation_query_res[1].company_metric_description_note_id == note_id
            assert update_relation_query_res[1].company_id == amd_company.id
            
            assert response['note_id'] == update_note_query_res[0].id
            assert response['metric_description_id'] == new_desc.id
            #resp_data = base64.b64decode(response['data'])
            #assert resp_data == data
            assert response['note_type'] == update_note_query_res[0].note_type
            assert len(response['company_ids']) == 2

        
    def test_delete_metric_description_note_valid(self):
        cleanup_db_from_db_str(TestCompanyMetricApi.db_conn_str)
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestCompanyMetricApi.db_conn_str, template_name='default_session') as session:
            data = b'This is the data.'
            
            new_desc = CompanyMetricDescription(code='rev_usa', display_name='Revenue Usa', metric_data_type=0)
            session.add(new_desc)

            desc_note = CompanyMetricDescriptionNote(note_data=data, note_type=NOTE_TYPE_TEXT)
            session.add(desc_note)

            session.flush()

            rel = CompanyMetricRelation(company_id=None, company_metric_description_id=new_desc.id, company_metric_description_note_id=desc_note.id)
            session.add(rel)

            session.commit()

            url = "/companyMetric/description/note/" + str(desc_note.id)
            response = client.delete(url)
                            
            assert response.status_code == 200
            session.expire_all()
            query_res = session.query(CompanyMetricDescriptionNote).all()
            assert len(query_res) == 0
            


