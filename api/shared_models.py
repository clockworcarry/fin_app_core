from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator


class ResourceCreationBasicModel(BaseModel):
    id: int