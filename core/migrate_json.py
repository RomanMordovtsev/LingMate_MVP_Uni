"""One-off migration of the old JSON files in data/ into SQLite (roadmap 1.1).

    python -m core.migrate_json                 # data/*.json -> data/lingmate.sqlite3
    python -m core.migrate_json --db other.sqlite3 --data-dir backup/

The JSON files are only read, never modified or deleted. The app also runs this
automatically on first start when the database is empty.
"""
import argparse
import sys
from pathlib import Path

from core.storage import DATA_DIR, DB_PATH, SqliteStore, migrate_json_to_sqlite


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--force", action="store_true",
                        help="import even if the database already has data (may duplicate rows)")
    args = parser.parse_args(argv)

    store = SqliteStore(args.db)
    if not store.is_empty() and not args.force:
        print(f"{args.db} already has data; nothing imported (use --force to import anyway).")
        return 1
    counts = migrate_json_to_sqlite(store, args.data_dir)
    print(f"Imported into {args.db}: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
