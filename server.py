import sys

from src.cli import parse_args


def main():
    args = parse_args()
    host = args.host
    port = args.port
    root_dir = args.directory

    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Root directory: {root_dir}")
    print("Server bootstrap complete. Ready to accept connections.")


if __name__ == "__main__":
    main()
