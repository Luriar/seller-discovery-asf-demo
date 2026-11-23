"""Independent seller discovery mock pipeline. All records are fictional."""
from __future__ import annotations
import csv
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Profile:
    code: str
    followers: int
    bio: str
    source: str = "synthetic-fixture"


@dataclass(frozen=True)
class Criteria:
    min_followers: int = 1000
    candidate_terms: tuple[str, ...] = ("review", "creator", "curation")
    exclude_terms: tuple[str, ...] = ("official company", "corporate brand")

    def __post_init__(self):
        if self.min_followers < 0:
            raise ValueError("minimum followers must be nonnegative")


def classify(p: Profile, rule: Criteria = Criteria()) -> tuple[str, str]:
    """Demo-only heuristic. Not an employer's selection or scoring policy."""
    if not p.code.strip() or p.followers < 0:
        return "invalid", "missing code or impossible followers"
    text = p.bio.casefold().strip()
    if any(t in text for t in rule.exclude_terms):
        return "excluded", "example exclusion terms"
    if p.followers < rule.min_followers:
        return "excluded", "below example minimum"
    if any(t in text for t in rule.candidate_terms):
        return "candidate", "example keyword match"
    return "review", "manual check needed"


class CandidateStore:
    def __init__(self, path: str | Path = ":memory:"):
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS candidates (
                code TEXT PRIMARY KEY,
                followers INTEGER NOT NULL,
                bio TEXT NOT NULL,
                source TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS review_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                previous TEXT,
                current TEXT NOT NULL
            );
        """)
        self.db.commit()

    def upsert(self, profiles: list[Profile], rules: Criteria = Criteria()) -> dict:
        result = {"inserted": 0, "changed": 0, "unchanged": 0, "invalid": 0}
        with self.db:
            for p in profiles:
                decision, reason = classify(p, rules)
                if decision == "invalid":
                    result["invalid"] += 1
                    continue
                existing = self.db.execute(
                    "SELECT * FROM candidates WHERE code=?", (p.code,)
                ).fetchone()
                values = (p.code, p.followers, p.bio, p.source, decision, reason)
                if existing is None:
                    self.db.execute(
                        "INSERT INTO candidates VALUES(?,?,?,?,?,?)", values
                    )
                    self.db.execute(
                        "INSERT INTO review_events(code,previous,current) "
                        "VALUES (?,NULL,?)", (p.code, decision)
                    )
                    result["inserted"] += 1
                elif tuple(existing) == values:
                    result["unchanged"] += 1
                else:
                    self.db.execute("""
                        UPDATE candidates SET followers=?,bio=?,source=?,
                        decision=?,reason=? WHERE code=?
                    """, values[1:] + (p.code,))
                    if existing["decision"] != decision:
                        self.db.execute(
                            "INSERT INTO review_events(code,previous,current) "
                            "VALUES (?,?,?)", (p.code, existing["decision"], decision)
                        )
                    result["changed"] += 1
        return result

    def list(self, status: str | None = None) -> list[dict]:
        if status:
            cur = self.db.execute(
                "SELECT * FROM candidates WHERE decision=? ORDER BY code", (status,)
            )
        else:
            cur = self.db.execute("SELECT * FROM candidates ORDER BY code")
        return [dict(row) for row in cur]

    def export_csv(self, file: str | Path, status: str = "candidate") -> int:
        rows = self.list(status)
        with open(file, "w", encoding="utf-8", newline="") as out:
            writer = csv.DictWriter(
                out, fieldnames=("code","followers","bio","source","decision","reason")
            )
            writer.writeheader()
            writer.writerows(rows)
        return len(rows)

    def close(self):
        self.db.close()


def load_fixture(path: str | Path) -> list[Profile]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("fixture must contain a list")
    profiles = []
    for obj in data:
        profiles.append(Profile(
            code=str(obj["code"]),
            followers=int(obj["followers"]),
            bio=str(obj["bio"]),
        ))
    return profiles
