import sys

from src.cli import parse_args


def main():
    args = parse_args()
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Directory: {args.directory}")


if __name__ == "__main__":
    main()
