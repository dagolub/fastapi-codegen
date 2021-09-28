from typing import Optional
import datetime
from pydantic import BaseModel


# Shared properties
class {{ entity }}Base(BaseModel):
    {% for field in schema_fields %}{{ schema_fields[field] }}
    {% endfor %}

# Properties to receive on {{ entity }} creation
class {{ entity }}Create({{ entity }}Base):
    pass


# Properties to receive on {{ entity }} update
class {{ entity }}Update({{ entity }}Base):
    pass


# Properties shared by models stored in DB
class {{ entity }}InDBBase({{ entity }}Base):
    id: int
    {% for field in related_fields %}{{ field }}_id: int
    {% endfor %}
    class Config:
        orm_mode = True


# Properties to return to client
class {{ entity }}({{ entity }}InDBBase):
    pass


# Properties properties stored in DB
class {{ entity }}InDB({{ entity }}InDBBase):
    pass
