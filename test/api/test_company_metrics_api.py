from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from api.routers.company_metrics_api import *

client = TestClient(app)

class TestCompanyMetricsApi:
    
    def test_group_fine_classifications(self):
        rough_classifications = []
        rough_classifications.append(CompanyMetricClassification(id = 6, category_name='whatever', parent_category_id=3))
        rough_classifications.append(CompanyMetricClassification(id = 2, category_name='revenue', parent_category_id=1))
        rough_classifications.append(CompanyMetricClassification(id = 1, category_name='financials', parent_category_id=None))
        rough_classifications.append(CompanyMetricClassification(id = 3, category_name='revenue_growth_2y', parent_category_id=2))
        rough_classifications.append(CompanyMetricClassification(id = 4, category_name='revenue_growth_5y', parent_category_id=2))
        rough_classifications.append(CompanyMetricClassification(id = 5, category_name='net_income_growth_1y', category_parent_id=1))

        fine_classifications = transform_rough_classifications_to_fine(rough_classifications)

        group_fine_classifications(fine_classifications)



