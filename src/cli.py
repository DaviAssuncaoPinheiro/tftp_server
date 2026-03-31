import argparse
import sys
from pathlib import Path


def validate_directory(path_str):
    path = Path(path_str).resolve()
    if not path.exists():
        print(f"Error: directory '{path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    if not path.is_dir():
        print(f"Error: '{path}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    return path


def parse_args():
    parser = argparse.ArgumentParser(description="TFTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind")
    parser.add_argument("--port", type=int, default=69, help="UDP port to listen on")
    parser.add_argument(
        "--directory", default=".", help="Root directory for file transfers"
    )
    args = parser.parse_args()
    args.directory = validate_directory(args.directory)
    return args
