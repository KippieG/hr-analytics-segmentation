"""
Pandera schema-definities voor brondata.

Employer- en interactieschema's valideren kolommen, types en waardebereiken
voordat de data de transformatielaag ingaat.
"""

import pandera as pa
from pandera import Column, DataFrameSchema, Check

VALID_SECTORS = {"tech", "healthcare", "manufacturing", "retail", "finance", "construction", "logistics"}
VALID_SIZES = {"micro", "small", "medium", "large"}
VALID_STATUSES = {"Active", "Inactive", "Prospect"}
VALID_INTERACTION_TYPES = {"call", "email", "meeting", "event", "linkedin"}
VALID_OUTCOMES = {"positive", "neutral", "negative", "no_response"}


employer_schema = DataFrameSchema(
    columns={
        "employer_id": Column(str, nullable=False, unique=True),
        "company_size": Column(str, Check.isin(VALID_SIZES), nullable=False),
        "status": Column(str, Check.isin(VALID_STATUSES), nullable=False),
        "sector": Column(str, Check.isin(VALID_SECTORS), nullable=True),
        "revenue_potential": Column(float, Check.greater_than(0), nullable=True),
        "last_contact_date": Column(str, nullable=True),
        "frequency_12m": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    },
    coerce=True,
    strict=False,  # extra kolommen zijn toegestaan
)

interaction_schema = DataFrameSchema(
    columns={
        "interaction_id": Column(str, nullable=False, unique=True),
        "employer_id": Column(str, nullable=False),
        "interaction_date": Column(str, nullable=False),
        "interaction_type": Column(str, Check.isin(VALID_INTERACTION_TYPES), nullable=True),
        "outcome": Column(str, Check.isin(VALID_OUTCOMES), nullable=True),
    },
    coerce=True,
    strict=False,
)
