from core.shared_models import *

""" Associate data points to their appropriate descriptions. This function
    operates on a single business segment.
"""
def associate_metric_data_to_descriptions(metric_descriptions, metric_data, bs_id):
    ret = []
    for m_desc in metric_descriptions:
        for m_data in metric_data:
            if m_desc.id == m_data.metric_description_id and m_data.company_business_segment_id == bs_id:
                #desc_model = MetricDescriptionModel(id=m_desc.id, code=m_desc.code, display_name=m_desc.display_name, metric_data_type=)
                desc_model = MetricDescriptionModel.from_orm(m_desc)
                i = 2
