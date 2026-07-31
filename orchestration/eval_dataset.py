from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel


@dataclass
class EvalCase:
    name: str
    prompt: str
    system_prompt: str = "You are a helpful assistant."
    expected: Any = None
    response_model: type[BaseModel] | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "prompt": self.prompt,
            "system_prompt": self.system_prompt,
            "expected": self.expected,
            "response_model": self.response_model.__name__ if self.response_model else None,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class EvalResult:
    case: EvalCase
    passed: bool
    score: float
    latency_ms: float
    actual: Any = None
    error: str | None = None
    tokens_used: int = 0
    cost: float = 0.0
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_name": self.case.name,
            "passed": self.passed,
            "score": self.score,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "error": self.error,
            "timestamp": self.timestamp,
        }


class EvalDataset:
    def __init__(self, name: str, cases: list[EvalCase] | None = None):
        self.name = name
        self.cases: list[EvalCase] = cases or []

    def add(self, case: EvalCase) -> None:
        self.cases.append(case)

    def filter_by_tag(self, tag: str) -> list[EvalCase]:
        return [c for c in self.cases if tag in c.tags]

    def filter_by_name(self, pattern: str) -> list[EvalCase]:
        return [c for c in self.cases if pattern.lower() in c.name.lower()]

    def __len__(self) -> int:
        return len(self.cases)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "cases": [c.to_dict() for c in self.cases],
            "total_cases": len(self.cases),
        }

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    @classmethod
    def from_json(cls, path: str) -> EvalDataset:
        with open(path) as f:
            data = json.load(f)
        cases = []
        for c in data.get("cases", []):
            case = EvalCase(
                name=c["name"],
                prompt=c["prompt"],
                system_prompt=c.get("system_prompt", "You are a helpful assistant."),
                expected=c.get("expected"),
                tags=c.get("tags", []),
                metadata=c.get("metadata", {}),
            )
            cases.append(case)
        return cls(name=data["name"], cases=cases)

    def to_csv(self, path: str) -> None:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "prompt", "system_prompt", "tags"])
            for c in self.cases:
                writer.writerow([c.name, c.prompt, c.system_prompt, ";".join(c.tags)])

    @classmethod
    def from_csv(cls, path: str) -> EvalDataset:
        cases = []
        name = path.split("/")[-1].replace(".csv", "")
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                case = EvalCase(
                    name=row["name"],
                    prompt=row["prompt"],
                    system_prompt=row.get("system_prompt", "You are a helpful assistant."),
                    tags=row.get("tags", "").split(";") if row.get("tags") else [],
                )
                cases.append(case)
        return cls(name=name, cases=cases)
