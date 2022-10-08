from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator


"""class MetricDescriptionModelOut(BaseModel):
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

    group_ids: List[int] = []

class MetricDataModelOut(BaseModel):
    data: float
    description: MetricDescriptionModelOut

class MetricCategoryModelOut(BaseModel):
    id: int
    category_name: str
    parent_id: int = None
    metrics: List[MetricDataModelOut] = []
    classifications: List['MetricCategoryModelOut'] = []

class BusinessSegmentModelOut(BaseModel):
    id: int
    code: str
    display_name: str
    company_id: int
    company_name: str
    company_ticker: str
    metric_categories: List[MetricCategoryModelOut] = []

#only important fields
class CompanyGroupModelShortOut(BaseModel):
    id: int
    name_code: str
    name: str

#only important fields
class CompanyGroupMetricsModelOut(BaseModel):
    group_info: CompanyGroupModelShortOut
    business_segments: List[BusinessSegmentModelOut]"""