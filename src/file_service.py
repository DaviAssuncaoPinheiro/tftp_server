import os
from pathlib import Path

from src.protocol import (
    BLOCK_SIZE, TFTPError,
    ERR_FILE_NOT_FOUND, ERR_ACCESS_VIOLATION, ERR_DISK_FULL, ERR_FILE_EXISTS,
)


class FileReader:
    def __init__(self, root_dir: Path, filename: str):
        path = _safe_path(root_dir, filename)

        if not path.exists():
            raise TFTPError(f"File not found: {filename}", ERR_FILE_NOT_FOUND)
        if not path.is_file():
            raise TFTPError(f"Not a regular file: {filename}", ERR_ACCESS_VIOLATION)
        if not os.access(path, os.R_OK):
            raise TFTPError(f"Permission denied: {filename}", ERR_ACCESS_VIOLATION)

        self._fh    = open(path, "rb")
        self._block = 0

    def next_block(self) -> tuple[int, bytes]:
        self._block += 1
        return self._block, self._fh.read(BLOCK_SIZE)

    def close(self):
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class FileWriter:
    def __init__(self, root_dir: Path, filename: str):
        path = _safe_path(root_dir, filename)

        if path.exists():
            raise TFTPError(f"File already exists: {filename}", ERR_FILE_EXISTS)
        if not os.access(path.parent, os.W_OK):
            raise TFTPError(f"No write permission: {path.parent}", ERR_ACCESS_VIOLATION)

        self._fh   = open(path, "wb")
        self._path = path

    def write_block(self, payload: bytes):
        try:
            self._fh.write(payload)
        except OSError as exc:
            raise TFTPError(str(exc), ERR_DISK_FULL) from exc

    def close(self):
        self._fh.close()

    def abort(self):
        self._fh.close()
        self._path.unlink(missing_ok=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        self.abort() if exc_type else self.close()


def _safe_path(root_dir: Path, filename: str) -> Path:
    try:
        path = (root_dir / filename).resolve()
        path.relative_to(root_dir.resolve())
    except ValueError:
        raise TFTPError(f"Path traversal attempt: {filename}", ERR_ACCESS_VIOLATION)
    return path
