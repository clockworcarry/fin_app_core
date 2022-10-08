from pydantic import BaseModel, ValidationError, validator
from typing import Optional, List

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


class MetricDescriptionModel(BaseModel):
    id: int
    code: str
    display_name: str
    metric_data_type: int
    metric_duration: int
    metric_duration_type: int
    look_back: bool
    year_recorded: int = None
    quarter_recorded: int = None
    metric_fixed_year: int = None
    metric_fixed_quarter: int = None
    _metric_classification_id: int = None

    class Config:
        orm_mode = True
        underscore_attrs_are_private = True

class MetricDataModel(BaseModel):
    data: float
    description: MetricDescriptionModel

class MetricCategoryModel(BaseModel):
    id: int
    category_name: str
    parent_id: int = None
    metrics: List[MetricDataModel] = []
    categories: List['MetricCategoryModel'] = []

MetricCategoryModel.update_forward_refs()

class BusinessSegmentModel(BaseModel):
    id: int
    code: str
    display_name: str
    company_id: int
    company_name: str
    company_ticker: str
    metric_categories: List[MetricCategoryModel] = []

#only important fields
class CompanyGroupInfoShortModel(BaseModel):
    id: int
    name_code: str
    name: str

#only important fields
class CompanyGroupMetricsModel(BaseModel):
    group_info: CompanyGroupInfoShortModel
    business_segments: List[BusinessSegmentModel]

