from pydantic import BaseModel, Field, validator


class Critique(BaseModel):
    """Модель даних для результату аудиту критика."""
    score: int = Field(ge=0, le=100)
    fatal_flaws: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    corrections: list[str] = Field(default_factory=list)

    @validator(
        'fatal_flaws',
        'missing_info',
        'corrections',
        pre=True,
        always=True,
    )
    def validate_list_fields(cls, v):
        """Валідує та приводить поля до списку рядків."""
        if v is None or v == '' or v == 'None':
            return []
        if isinstance(v, str):
            return [v]
        return v
