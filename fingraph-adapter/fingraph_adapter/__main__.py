import sys
import argparse
from pathlib import Path
from .loader import FtMLoader


def main() -> None:
    parser = argparse.ArgumentParser(description="Load OpenSanctions FtM JSON export into Neo4j")
    parser.add_argument("file", type=str, help="Path to .ftm.json export file")
    parser.add_argument("--uri", type=str, default="bolt://localhost:7687")
    parser.add_argument("--username", type=str, default="neo4j")
    parser.add_argument("--password", type=str, default="password")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Loading {args.file} into {args.uri}...")
        loader = FtMLoader(args.uri, args.username, args.password)
        stats = loader.load(str(path))
        loader.close()
        print(f"Nodes created: {stats['nodes_created']}")
        print(f"Nodes updated: {stats['nodes_updated']}")
        print(f"Edges created: {stats['edges_created']}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
