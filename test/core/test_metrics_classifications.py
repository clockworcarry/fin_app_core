from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

import core.company_metrics_classifications as metrics_classifications_core
from db.models import *

client = TestClient(app)

class TestCompanyMetricsApi:
    
    def test_group_fine_classifications(self):
        rough_classifications = []

        cls_rel_one = CompanyMetricClassificationAccountRelation(company_metric_classification_id=6, account_id=None)
        cls_rel_two = CompanyMetricClassificationAccountRelation(company_metric_classification_id=2, account_id=None)
        cls_rel_three = CompanyMetricClassificationAccountRelation(company_metric_classification_id=1, account_id=None)
        cls_rel_four = CompanyMetricClassificationAccountRelation(company_metric_classification_id=3, account_id=None)
        cls_rel_five = CompanyMetricClassificationAccountRelation(company_metric_classification_id=4, account_id=None)
        cls_rel_six = CompanyMetricClassificationAccountRelation(company_metric_classification_id=5, account_id=None)
        cls_rel_seven = CompanyMetricClassificationAccountRelation(company_metric_classification_id=7, account_id=None)

        cls_one = CompanyMetricClassification(id = 6, category_name='whatever', parent_category_id=3)
        cls_two = CompanyMetricClassification(id = 2, category_name='revenue', parent_category_id=1)
        cls_three = CompanyMetricClassification(id = 1, category_name='financials', parent_category_id=None)
        cls_four = CompanyMetricClassification(id = 3, category_name='revenue_growth_2y', parent_category_id=2)
        cls_five = CompanyMetricClassification(id = 4, category_name='revenue_growth_5y', parent_category_id=2)
        cls_six = CompanyMetricClassification(id = 5, category_name='net_income', parent_category_id=1)
        cls_seven = CompanyMetricClassification(id = 7, category_name='misc', parent_category_id=None)

        input = [(cls_rel_one, cls_one), (cls_rel_two, cls_two), (cls_rel_three, cls_three), (cls_rel_four, cls_four), (cls_rel_five, cls_five), (cls_rel_six, cls_six), (cls_rel_seven, cls_seven)]

        fine_classifications = metrics_classifications_core.transform_rough_classifications_to_fine(input)
        grouped_classifications = metrics_classifications_core.group_fine_classifications(fine_classifications, None)
        
        assert len(grouped_classifications) == 2

        assert grouped_classifications[0].id == 1
        assert grouped_classifications[0].category_name == 'financials'
        assert len(grouped_classifications[0].classifications) == 2
        fin_cls = grouped_classifications[0]
        
        assert fin_cls.classifications[0].id == 2
        assert fin_cls.classifications[0].category_name == 'revenue'
        assert len(fin_cls.classifications[0].classifications) == 2
        rev_cls = fin_cls.classifications[0]

        assert rev_cls.classifications[0].id == 3
        assert rev_cls.classifications[0].category_name == 'revenue_growth_2y'
        assert len(rev_cls.classifications[0].classifications) == 1
        rev_growth_2_y_cls = rev_cls.classifications[0]

        assert rev_growth_2_y_cls.classifications[0].id == 6
        assert rev_growth_2_y_cls.classifications[0].category_name == 'whatever'
        assert len(rev_growth_2_y_cls.classifications[0].classifications) == 0

        assert rev_cls.classifications[1].id == 4
        assert rev_cls.classifications[1].category_name == 'revenue_growth_5y'
        assert len(rev_cls.classifications[1].classifications) == 0

        assert grouped_classifications[0].classifications[1].id == 5
        assert grouped_classifications[0].classifications[1].category_name == 'net_income'
        assert len(grouped_classifications[0].classifications[1].classifications) == 0

        assert grouped_classifications[1].id == 7
        assert grouped_classifications[1].category_name == 'misc'
        assert len(grouped_classifications[1].classifications) == 0
