from fte_core.db import Base

EXPECTED_TABLES = {
    "companies",
    "filings",
    "sections",
    "chunks",
    "xbrl_facts",
    "metric_map",
    "theses",
    "thesis_runs",
    "eval_cases",
    "ingest_jobs",
}


def test_all_mvp_tables_defined() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_financial_values_are_numeric() -> None:
    value = Base.metadata.tables["xbrl_facts"].c.value
    assert value.type.python_type.__name__ == "Decimal"
