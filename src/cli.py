import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="TFTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind")
    parser.add_argument("--port", type=int, default=69, help="UDP port to listen on")
    parser.add_argument("--directory", default=".", help="Root directory for file transfers")
    return parser.parse_args()
