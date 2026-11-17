"""Database tables for the MVP (plan section 8)."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    ForeignKey,
    Index,
    MetaData,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Must match the embedding model; changing it means re-embedding every chunk.
EMBEDDING_DIM = 1024

BigIntPK = Annotated[int, mapped_column(BigInteger, primary_key=True)]
CreatedAt = Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        CheckConstraint("segment IN ('hyperscaler', 'neocloud', 'ai_lab')", name="segment"),
    )

    id: Mapped[BigIntPK]
    cik: Mapped[str] = mapped_column(String(10), unique=True)  # zero-padded to 10 digits
    ticker: Mapped[str] = mapped_column(String(16), unique=True)
    name: Mapped[str] = mapped_column(Text)
    segment: Mapped[str] = mapped_column(String(16))
    fiscal_year_end: Mapped[str] = mapped_column(String(4))  # MMDD, as EDGAR reports it


class Filing(Base):
    __tablename__ = "filings"

    id: Mapped[BigIntPK]
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    accession_no: Mapped[str] = mapped_column(String(20), unique=True)
    form: Mapped[str] = mapped_column(String(16))
    period_end: Mapped[date | None] = mapped_column(Date)
    filed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    primary_doc_url: Mapped[str] = mapped_column(Text)
    raw_sha256: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), server_default="pending")


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[BigIntPK]
    filing_id: Mapped[int] = mapped_column(ForeignKey("filings.id"), index=True)
    item_code: Mapped[str] = mapped_column(String(16))  # e.g. 1A, 7, EX-99.1
    title: Mapped[str] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text)
    char_start: Mapped[int]
    char_end: Mapped[int]


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint("section_id", "ord"),
        Index("chunks_tsv_idx", "tsv", postgresql_using="gin"),
        Index(
            "chunks_embedding_idx",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("chunks_filter_idx", "ticker", "period_end", "item_code"),
    )

    id: Mapped[BigIntPK]
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))
    ord: Mapped[int]
    text: Mapped[str] = mapped_column(Text)
    text_sha256: Mapped[str] = mapped_column(String(64))  # re-embed only when this changes
    token_count: Mapped[int]
    embedding: Mapped[Any | None] = mapped_column(Vector(EMBEDDING_DIM))
    embedding_model: Mapped[str | None] = mapped_column(Text)
    tsv: Mapped[Any] = mapped_column(
        TSVECTOR, Computed("to_tsvector('english', text)", persisted=True)
    )
    # Copied from the filing and section so filtered search needs no joins.
    ticker: Mapped[str] = mapped_column(String(16))
    form: Mapped[str] = mapped_column(String(16))
    period_end: Mapped[date | None] = mapped_column(Date)
    item_code: Mapped[str] = mapped_column(String(16))


class XbrlFact(Base):
    __tablename__ = "xbrl_facts"
    __table_args__ = (Index("facts_lookup_idx", "company_id", "concept", "calendar_quarter"),)

    id: Mapped[BigIntPK]
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    filing_id: Mapped[int | None] = mapped_column(ForeignKey("filings.id"), index=True)
    taxonomy: Mapped[str] = mapped_column(String(32))  # us-gaap, ifrs-full, dei, ...
    concept: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(32))
    value: Mapped[Decimal] = mapped_column(Numeric)  # never float
    period_start: Mapped[date | None] = mapped_column(Date)  # null for instant facts
    period_end: Mapped[date] = mapped_column(Date)
    fiscal_label: Mapped[str | None] = mapped_column(String(16))  # e.g. FY2026 Q1
    calendar_quarter: Mapped[str | None] = mapped_column(String(7))  # e.g. 2026Q1
    dimensions: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default="{}")
    is_superseded: Mapped[bool] = mapped_column(server_default="false")  # replaced by an amendment


class MetricMap(Base):
    __tablename__ = "metric_map"

    metric_key: Mapped[str] = mapped_column(String(64), primary_key=True)  # e.g. capex
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), primary_key=True)
    concepts: Mapped[list[str]] = mapped_column(ARRAY(Text))
    adjustment: Mapped[str | None] = mapped_column(Text)


class Thesis(Base):
    __tablename__ = "theses"

    id: Mapped[BigIntPK]
    text: Mapped[str] = mapped_column(Text)
    companies: Mapped[list[str]] = mapped_column(ARRAY(String(16)))  # tickers
    window_start: Mapped[date] = mapped_column(Date)
    window_end: Mapped[date] = mapped_column(Date)
    created_at: Mapped[CreatedAt]


class ThesisRun(Base):
    __tablename__ = "thesis_runs"

    id: Mapped[BigIntPK]
    thesis_id: Mapped[int] = mapped_column(ForeignKey("theses.id"), index=True)
    report: Mapped[dict[str, Any]] = mapped_column(JSONB)
    model: Mapped[str] = mapped_column(Text)
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    filings_as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[CreatedAt]


class EvalCase(Base):
    __tablename__ = "eval_cases"

    id: Mapped[BigIntPK]
    question: Mapped[str] = mapped_column(Text)
    expected: Mapped[str] = mapped_column(Text)
    expected_chunk_ids: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), server_default="{}")
    expected_fact_ids: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), server_default="{}")


class IngestJob(Base):
    __tablename__ = "ingest_jobs"
    __table_args__ = (Index("ingest_jobs_claim_idx", "status", "created_at"),)

    id: Mapped[BigIntPK]
    kind: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(16), server_default="queued")
    attempts: Mapped[int] = mapped_column(server_default="0")
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
