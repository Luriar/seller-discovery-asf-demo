"""Synthetic seller-candidate classification; no platform integration."""
import csv
from dataclasses import dataclass

@dataclass(frozen=True)
class Profile:
    code: str
    followers: int
    bio: str

def discover(profiles, threshold=1000):
    """Illustrative rules, not company rules."""
    seen = set()
    matched = []
    for p in profiles:
        if p.code in seen:
            continue
        seen.add(p.code)
        text = p.bio.casefold()
        is_candidate = p.followers >= threshold and any(
            token in text for token in ("review", "creator", "curation")
        )
        if is_candidate:
            matched.append({"code":p.code,"followers":p.followers,"category":"candidate"})
    return matched

def export_csv(rows, filename):
    with open(filename,"w",newline="",encoding="utf-8") as fp:
        writer=csv.DictWriter(fp,fieldnames=("code","followers","category"))
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    profiles=[Profile("demo-1",2500,"product reviewer"),
              Profile("demo-2",150,"brand"),Profile("demo-1",2500,"product reviewer")]
    print(discover(profiles))
