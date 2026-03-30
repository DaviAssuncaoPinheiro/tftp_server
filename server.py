import logging
import sys

from src.cli import parse_args
from src.tftp_server import TFTPServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    args = parse_args()

    server = TFTPServer(
        host=args.host,
        port=args.port,
        root_dir=args.directory,
    )

    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
