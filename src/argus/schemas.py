from datetime import date, datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class LedgerEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    metric: str
    value: float
    unit: str
    period: str
    source_url: str
    source_type: Literal["filing", "management", "outside"]
    doc_page: int | None = None
    snippet: str
    source_sha256: str
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cache_path: str | None = None
    company: str | None = None
    period_type: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    currency: str | None = None
    consolidation_basis: Literal["consolidated", "standalone", "unknown"] = "unknown"
    verified: bool = False
    verified_by: str | None = None
    verified_at: datetime | None = None
    denominator: str | None = None
    reporting_scope: str | None = None
    comparability_cohort: str | None = None
    comparability_note: str | None = None

class ObservationCandidate(BaseModel):
    """Machine extraction proposal. Candidates are never used in calculations."""
    id: str
    metric: str
    value: float | None = None
    unit: str | None = None
    period: str | None = None
    period_type: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    currency: str | None = None
    consolidation_basis: Literal["consolidated", "standalone", "unknown"] = "unknown"
    source_url: str
    source_type: Literal["filing", "management", "outside"]
    doc_page: int | None = None
    snippet: str
    source_sha256: str
    cache_path: str
    company: str
    status: Literal["unverified", "ambiguous", "missing", "verified", "rejected"] = "unverified"
    notes: list[str] = Field(default_factory=list)
    ledger_entry_id: str | None = None

class AngleResult(BaseModel):
    angle: str
    status: Literal["tested", "abstained"]
    abstain_reason: str | None = None
    series: dict[str, list[float | None]] = Field(default_factory=dict)
    periods: list[str] = Field(default_factory=list)
    gap_flags: list[bool] = Field(default_factory=list)
    persistence_periods: int = 0
    ledger_ids: list[str] = Field(default_factory=list)

class Candidate(BaseModel):
    id: str
    angles: list[str]
    gap_start_period: str
    summary_numbers: dict[str, float] = Field(default_factory=dict)
    hypotheses: list[str] = Field(default_factory=list)
    red_team_log: list[dict] = Field(default_factory=list)
    gate: dict = Field(default_factory=dict)
    state: Literal["explained", "unexplained", "no_reliable_finding", "rejected"] = "no_reliable_finding"

class Dossier(BaseModel):
    company: str
    discovery: str
    why_it_matters: list[str]
    evidence: list[str]
    timeline: list[dict]
    numbers: dict[str, float]
    counterargument: str
    falsification_condition: str
    evidence_score: float = Field(ge=0, le=100)
    evidence_label: Literal["Strong", "Moderate", "Weak"]
    not_tested: list[str]
    hypotheses: list[str] = Field(default_factory=list)
    red_team_log: list[dict] = Field(default_factory=list)
    score_components: dict[str, float] = Field(default_factory=dict)
    validation: dict = Field(default_factory=dict)
