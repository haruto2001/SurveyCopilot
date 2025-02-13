from dataclasses import dataclass


@dataclass(frozen=True)
class ArxivQueryParams:
    category: str
    start: str
    end: str
    max_results: int


@dataclass(frozen=True)
class AclAnthologyQueryParams:
    year: int
    conference: str
