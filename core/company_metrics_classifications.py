from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
import api.config as api_config

from db.models import *
import json

class MetricsClassificationFine:   
    def __init__(self, id, category_name, account_id, parent_id, classifications):
        self.id = id
        self.category_name = category_name
        self.account_id = account_id
        self.parent_id = parent_id
        self.classifications = classifications

    @staticmethod
    def to_json(mcf, json_obj):
        json_obj['id'] = mcf.id
        json_obj['category_name'] = mcf.category_name
        json_obj['account_id'] = mcf.account_id
        json_obj['parent_id'] = mcf.parent_id
        json_obj['classifications'] = []
        for c in mcf.classifications:
            json_obj['classifications'].append(MetricsClassificationFine.to_json(c, json_obj))


def group_fine_classifications(classifications, parent):
    fine_classifications = []
    for rc in classifications:
        if (rc.parent_id is None and parent is None) or (parent is not None and rc.parent_id == parent.id):
            children = group_fine_classifications(classifications, rc)
            already_exists = False
            
            for fc in fine_classifications:
                if fc.id == rc.id:
                    fc.classifications.extend(children)
                    already_exists = True
                    break
            
            if not already_exists:
                rc.classifications.extend(children)
                fine_classifications.append(rc)
        
    return fine_classifications
        

"""
    classifications_account_relation_tuple -> [(CompanyMetricClassificationAccountRelation, CompanyMetricClassification)]
"""
def transform_rough_classifications_to_fine(classifications_account_relation_tuple):
    ret = []
    for cart in classifications_account_relation_tuple:
        ret.append(MetricsClassificationFine(id=cart[1].id, category_name=cart[1].category_name, account_id=cart[0].account_id, parent_id=cart[1].parent_category_id, classifications=[]))
    
    return ret

def get_metrics_classifications(account_id):
    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
        db_classifications_account_relation_tuple = session.query(CompanyMetricClassificationAccountRelation, CompanyMetricClassification) \
                                                        .join(CompanyMetricClassification, CompanyMetricClassification.id == CompanyMetricClassificationAccountRelation.company_metric_classification_id) \
                                                        .filter(or_(CompanyMetricClassificationAccountRelation.account_id == account_id, CompanyMetricClassificationAccountRelation.account_id == None)).all()

        ret = transform_rough_classifications_to_fine(db_classifications_account_relation_tuple)
        ret = group_fine_classifications(ret, None)

        return ret