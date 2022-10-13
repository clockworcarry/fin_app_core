from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
import api.config as api_config

from db.models import *
from core.shared_models import *
import json

import core.constants as core_global_constants

class MetricsClassificationFine:
    def __init__(self, id, category_name, account_id, parent_id, classifications):
        self.id = id
        self.category_name = category_name
        self.account_id = account_id
        self.parent_id = parent_id
        self.classifications = classifications
        self.metrics = []

    @staticmethod
    def to_json(mcf, json_obj):
        json_obj['id'] = mcf.id
        json_obj['category_name'] = mcf.category_name
        json_obj['account_id'] = mcf.account_id
        json_obj['parent_id'] = mcf.parent_id
        json_obj['classifications'] = []
        for c in mcf.classifications:
            json_obj['classifications'].append(MetricsClassificationFine.to_json(c, json_obj))


def group_metric_categories_model(classifications, parent) -> List[MetricCategoryModel]:
    fine_classifications = []
    for rc in classifications:
        if (rc.parent_id is None and parent is None) or (parent is not None and rc.parent_id == parent.id):
            children = group_metric_categories_model(classifications, rc)
            already_exists = False
            
            for fc in fine_classifications:
                if fc.id == rc.id:
                    fc.categories.extend(children)
                    already_exists = True
                    break
            
            if not already_exists:
                rc.categories.extend(children)
                fine_classifications.append(rc)
        
    return fine_classifications

def remove_empty_categories(categories):
    for i in reversed(range(len(categories))):
        if len(categories[i].metrics) == 0 and len(categories[i].categories) == 0:
            del categories[i]
        elif len(categories[i].categories) > 0:
            remove_empty_categories(categories[i].categories)
            if len(categories[i].categories) == 0:
                del categories[i]


def categorize_metrics(fine_classifications, metrics):
    for fc in fine_classifications:
        for m in metrics:
            if m.metric_classification_id == fc.id:
                fc.metrics.append(m)
        if len(fc.classifications) > 0:
            categorize_metrics(fc.classifications, metrics)
        

"""
    classifications_account_relation_tuple -> [(CompanyMetricClassificationAccountRelation, CompanyMetricClassification)]
"""
"""def transform_rough_classifications_to_fine(classifications_account_relation_tuple):
    ret = []
    for cart in classifications_account_relation_tuple:
        ret.append(MetricsClassificationFine(id=cart[1].id, category_name=cart[1].category_name, account_id=cart[0].account_id, parent_id=cart[1].parent_category_id, classifications=[]))
    
    return ret"""

def transform_metric_classifications_to_categories_model(metric_classifications_rough, account_id):
    ret = []
    for mcr in metric_classifications_rough:
        mcm = MetricCategoryModel(id=mcr.id, category_name=mcr.category_name, parent_id=mcr.parent_category_id)
        ret.append(mcm)

    return ret



def get_user_metric_categories(account_id, session) -> List[MetricCategoryModel]:
    db_classifications_account_relation_tuple = session.query(MetricClassification) \
                                                        .join(UserMetricClassification, MetricClassification.id == UserMetricClassification.metric_classification_id) \
                                                        .filter(or_(UserMetricClassification.account_id == account_id, UserMetricClassification.account_id == core_global_constants.system_user_id)).all()

    ret = transform_metric_classifications_to_categories_model(db_classifications_account_relation_tuple, account_id)
    return ret

def get_metrics_classifications_by_creator(creator_id, session):
    db_classifications = session.query(MetricClassification).filter(MetricClassification.creator_id == creator_id).all()
    
    ret = transform_metric_classifications_to_categories_model(db_classifications, creator_id)
    ret = group_fine_classifications(ret, None)

    return ret


"""def make_metric_categories(metric_classifications, metric_descriptions, metric_data):
    classifications = transform_rough_classifications_to_fine(metric_classifications, None)
    classifications = group_fine_classifications(ret, None)
    categorize_metrics(classifications, )
    return ret"""


