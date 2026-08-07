from pydantic import BaseModel, Field, validator


class Critique(BaseModel):
    score: int = Field(ge=0, le=100)
    fatal_flaws: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    corrections: list[str] = Field(default_factory=list)

    @validator('fatal_flaws', 'missing_info', 'corrections', pre=True, always=True)
    def validate_list_fields(cls, v):
        if v is None or v == '' or v == 'None':
            return []
        elif isinstance(v, str):
            return [v]
        return v
