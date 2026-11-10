"""Data contracts for snapshot scores and historical trend points."""
from __future__ import annotations

from typing import List, Optional, TypedDict


class SnapshotCompanyScores(TypedDict, total=False):
    company: str
    is_target: bool
    overall: Optional[float]
    career_growth: Optional[float]
    compensation: Optional[float]
    benefits: Optional[float]
    culture: Optional[float]
    work_life_balance: Optional[float]


class SnapshotPayload(TypedDict, total=False):
    schema_version: int
    captured_at: str
    url: str
    title: str
    companies: List[SnapshotCompanyScores]


class OverTimePoint(TypedDict, total=False):
    month_id: int
    value: float
    company: str
    date_label: str


class OverTimeSeries(TypedDict, total=False):
    series_id: str
    company: str
    color: str
    points: List[OverTimePoint]


class OverTimePayload(TypedDict, total=False):
    schema_version: int
    captured_at: str
    url: str
    title: str
    company_name: Optional[str]
    series: List[OverTimeSeries]
    timepoints: List[str]
    trends_by_dimension: dict  # dim_key -> List[OverTimePoint]
