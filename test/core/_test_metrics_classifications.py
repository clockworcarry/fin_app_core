from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

import core.metrics_classifications as metrics_classifications_core
from db.models import *

client = TestClient(app)

class TestCompanyMetricsApi:

    def test_transform_rough_classifications_to_fine(self):
        cls_one = MetricClassification(id = 6, category_name='whatever', parent_category_id=3)
        cls_two = MetricClassification(id = 2, category_name='revenue', parent_category_id=1)
        cls_three = MetricClassification(id = 1, category_name='financials', parent_category_id=None)
        cls_four = MetricClassification(id = 3, category_name='revenue_growth_2y', parent_category_id=2)
        cls_five = MetricClassification(id = 4, category_name='revenue_growth_5y', parent_category_id=2)
        cls_six = MetricClassification(id = 5, category_name='net_income', parent_category_id=1)
        cls_seven = MetricClassification(id = 7, category_name='misc', parent_category_id=None)

        input = [cls_one, cls_two, cls_three, cls_four, cls_five, cls_six, cls_seven]

        ret = metrics_classifications_core.transform_rough_classifications_to_fine(input, None)
        assert len(ret == 7)
    
    def test_group_fine_classifications(self):
        """cls_rel_one = UserMetricClassification(company_metric_classification_id=6, account_id=None)
        cls_rel_two = UserMetricClassification(company_metric_classification_id=2, account_id=None)
        cls_rel_three = UserMetricClassification(company_metric_classification_id=1, account_id=None)
        cls_rel_four = UserMetricClassification(company_metric_classification_id=3, account_id=None)
        cls_rel_five = UserMetricClassification(company_metric_classification_id=4, account_id=None)
        cls_rel_six = UserMetricClassification(company_metric_classification_id=5, account_id=None)
        cls_rel_seven = UserMetricClassification(company_metric_classification_id=7, account_id=None)"""

        #create metric categories
        cls_one = MetricClassification(id = 6, category_name='whatever', parent_category_id=3)
        cls_two = MetricClassification(id = 2, category_name='revenue', parent_category_id=1)
        cls_three = MetricClassification(id = 1, category_name='financials', parent_category_id=None)
        cls_four = MetricClassification(id = 3, category_name='revenue_growth_2y', parent_category_id=2)
        cls_five = MetricClassification(id = 4, category_name='revenue_growth_5y', parent_category_id=2)
        cls_six = MetricClassification(id = 5, category_name='net_income', parent_category_id=1)
        cls_seven = MetricClassification(id = 7, category_name='misc', parent_category_id=None)

        input = [cls_one, cls_two, cls_three, cls_four, cls_five, cls_six, cls_seven]

        fine_classifications = metrics_classifications_core.transform_rough_classifications_to_fine(input, None)
        grouped_classifications = metrics_classifications_core.group_fine_classifications(fine_classifications, None)
        
        assert len(grouped_classifications) == 2

        assert grouped_classifications[0].id == 1
        assert grouped_classifications[0].category_name == 'financials'
        assert len(grouped_classifications[0].categories) == 2
        fin_cls = grouped_classifications[0]
        
        assert fin_cls.categories[0].id == 2
        assert fin_cls.categories[0].category_name == 'revenue'
        assert len(fin_cls.categories[0].categories) == 2
        rev_cls = fin_cls.categories[0]

        assert rev_cls.categories[0].id == 3
        assert rev_cls.categories[0].category_name == 'revenue_growth_2y'
        assert len(rev_cls.categories[0].categories) == 1
        rev_growth_2_y_cls = rev_cls.categories[0]

        assert rev_growth_2_y_cls.categories[0].id == 6
        assert rev_growth_2_y_cls.categories[0].category_name == 'whatever'
        assert len(rev_growth_2_y_cls.categories[0].categories) == 0

        assert rev_cls.categories[1].id == 4
        assert rev_cls.categories[1].category_name == 'revenue_growth_5y'
        assert len(rev_cls.categories[1].categories) == 0

        assert grouped_classifications[0].categories[1].id == 5
        assert grouped_classifications[0].categories[1].category_name == 'net_income'
        assert len(grouped_classifications[0].categories[1].categories) == 0

        assert grouped_classifications[1].id == 7
        assert grouped_classifications[1].category_name == 'misc'
        assert len(grouped_classifications[1].categories) == 0

    def test_make_metric_categories(self):
        #create metric categories
        cls_one = MetricClassification(id = 2, category_name='revenue', parent_category_id=1)
        cls_two = MetricClassification(id = 1, category_name='financials', parent_category_id=None)
        cls_three = MetricClassification(id = 3, category_name='revenue_growth', parent_category_id=2)
        cls_four = MetricClassification(id = 5, category_name='EBITDA', parent_category_id=1)
        cls_five = MetricClassification(id = 7, category_name='misc', parent_category_id=None)

        classifications = [cls_one, cls_two, cls_three, cls_four, cls_five]

        #create metric descriptions
        metric_desc_rev_2021 = MetricDescription(id=1, code='rev_2021', display_name='2021 Revenue', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                metric_classification_id=cls_one.id, creator_id=None)
        
        metric_desc_revenue_ttm = MetricDescription(id=2, code='rev_ttm', display_name='Trailing 12 Months Revenue', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=METRIC_DURATION_QUARTER, \
                                                    year_recorded=2022, quarter_recorded=3, metric_duration=4, look_back=True, metric_fixed_year=-1, metric_fixed_quarter=-1, \
                                                    metric_classification_id=cls_one.id, creator_id=None)

        metric_desc_revenue_growth_2y = MetricDescription(id=3, code='rev_growth_2y', display_name='Past 2 Years Revenue Growth ', metric_data_type=METRIC_TYPE_PERCENTAGE, metric_duration_type=METRIC_DURATION_ANNUAL, \
                                                    year_recorded=2022, quarter_recorded=3, metric_duration=2, look_back=True, metric_fixed_year=-1, metric_fixed_quarter=-1, \
                                                    metric_classification_id=cls_three.id, creator_id=None)
        
        metric_desc_ebitda_2021 = MetricDescription(id=4, code='ebitda_2021', display_name='2021 EBITDA', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                    year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                    metric_classification_id=cls_four.id, creator_id=None)
        
        metric_desc_ebitda_ttm = MetricDescription(id=5, code='ebitda_ttm', display_name='Trailing 12 Months EBITDA', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=METRIC_DURATION_QUARTER, \
                                                    year_recorded=2022, quarter_recorded=3, metric_duration=4, look_back=True, metric_fixed_year=-1, metric_fixed_quarter=-1, \
                                                    metric_classification_id=cls_four.id, creator_id=None)

        metric_desc_nb_enterprise_customers = MetricDescription(id=6, code='nb_cloud_customers_2021', display_name='2021 Number of Cloud Customers', metric_data_type=METRIC_TYPE_NUMBER, metric_duration_type=-1, \
                                                    year_recorded=-1, quarter_recorded=-1, metric_duration=-1, look_back=True, metric_fixed_year=2021, metric_fixed_quarter=-1, \
                                                    metric_classification_id=cls_five.id, creator_id=None)

        metric_descriptions = [metric_desc_rev_2021, metric_desc_revenue_ttm, metric_desc_revenue_growth_2y, metric_desc_ebitda_2021, metric_desc_ebitda_ttm, metric_desc_nb_enterprise_customers]

        #create metric data list
        metric_rev_2021_data = MetricData(metric_description_id=metric_desc_rev_2021.id, data=200)
        metric_rev_ttm_data = MetricData(metric_description_id=metric_desc_revenue_ttm.id, data=210)
        metric_revenue_growth_2y_data = MetricData(metric_description_id=metric_desc_revenue_growth_2y.id, data=0.15)
        metric_ebitda_2021_data = MetricData(metric_description_id=metric_desc_ebitda_2021.id, data=50)
        metric_ebitda_ttm_data = MetricData(metric_description_id=metric_desc_ebitda_ttm.id, data=55)
        metric_nb_enterprise_customers_data = MetricData(metric_description_id=metric_desc_nb_enterprise_customers.id, data=10)

        metric_data = [metric_rev_2021_data, metric_rev_ttm_data, metric_revenue_growth_2y_data, metric_ebitda_2021_data, metric_ebitda_ttm_data, metric_nb_enterprise_customers_data]

        categorized_metrics = metrics_classifications_core.make_metric_categories(classifications, metric_descriptions, metric_data)
        assert len(categorized_metrics) == 2





