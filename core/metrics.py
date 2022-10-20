from core.shared_models import *
import core.constants as core_global_constants

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

def add_metric_to_business_segment(business_segment: BusinessSegmentModel, metric_description: MetricDescriptionModel, metric_data: MetricDataModel):
    for cat in business_segment.metric_categories:
        if cat.id == metric_description.metric_classification_id:
            duplicate_metric = None
            for idx, metric in enumerate(cat.metrics):
                if metric.description.id == metric_data.description.id:
                    duplicate_metric = metric
                    break
            
            if duplicate_metric is None:
                cat.metrics.append(metric_data)
            elif metric_data._user_id != core_global_constants.system_user_id:
                cat.metrics.append(metric_data) #override existing system metric with user's one
                del cat.metrics[idx]
            break


