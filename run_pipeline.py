"""Run the fictional ASF pipeline locally, with resumable SQLite state."""
import argparse
import json
from pathlib import Path
from asf_engine import CandidateStore, load_fixture


def main():
    parser = argparse.ArgumentParser(description="Synthetic seller discovery demo")
    parser.add_argument("--input", default=str(Path(__file__).parent / "fixtures" / "profiles.json"))
    parser.add_argument("--db", default=":memory:", help="SQLite file or :memory:")
    parser.add_argument("--export", help="Optional CSV path")
    args = parser.parse_args()
    store = CandidateStore(args.db)
    try:
        progress = store.upsert(load_fixture(args.input))
        rows = store.list()
        if args.export:
            store.export_csv(args.export)
        print(json.dumps(
            {"progress": progress, "summary": {
                name: len([x for x in rows if x["decision"] == name])
                for name in ("candidate", "review", "excluded")
            }, "synthetic_only": True},
            ensure_ascii=False, indent=2
        ))
    finally:
        store.close()


if __name__ == "__main__":
    main()
