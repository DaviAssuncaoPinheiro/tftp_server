import struct

# Constantes

BLOCK_SIZE = 512

OP_RRQ   = 1
OP_WRQ   = 2
OP_DATA  = 3
OP_ACK   = 4
OP_ERROR = 5

ERR_UNDEFINED        = 0
ERR_FILE_NOT_FOUND   = 1
ERR_ACCESS_VIOLATION = 2
ERR_DISK_FULL        = 3
ERR_ILLEGAL_OP       = 4
ERR_UNKNOWN_TID      = 5
ERR_FILE_EXISTS      = 6
ERR_NO_SUCH_USER     = 7

ERROR_MESSAGES = {
    ERR_UNDEFINED:        "Undefined error",
    ERR_FILE_NOT_FOUND:   "File not found",
    ERR_ACCESS_VIOLATION: "Access violation",
    ERR_DISK_FULL:        "Disk full or allocation exceeded",
    ERR_ILLEGAL_OP:       "Illegal TFTP operation",
    ERR_UNKNOWN_TID:      "Unknown transfer ID",
    ERR_FILE_EXISTS:      "File already exists",
    ERR_NO_SUCH_USER:     "No such user",
}

SUPPORTED_MODES = {"netascii", "octet", "mail"}


# Exceções

class TFTPError(Exception):
    def __init__(self, message: str, error_code: int = ERR_ILLEGAL_OP):
        super().__init__(message)
        self.error_code = error_code


# Parsing

def parse_packet(data: bytes) -> dict:
    if len(data) < 2:
        raise TFTPError("Packet too short")

    opcode = struct.unpack("!H", data[:2])[0]

    if opcode in (OP_RRQ, OP_WRQ):
        return _parse_request(opcode, data)
    if opcode == OP_DATA:
        return _parse_data(data)
    if opcode == OP_ACK:
        return _parse_ack(data)
    if opcode == OP_ERROR:
        return _parse_error(data)

    raise TFTPError(f"Unknown opcode: {opcode}")


def _parse_request(opcode, data):
    try:
        body  = data[2:]
        i     = body.index(0)
        filename = body[:i].decode("ascii")
        rest  = body[i + 1:]
        j     = rest.index(0)
        mode  = rest[:j].decode("ascii").lower()
    except (ValueError, UnicodeDecodeError) as exc:
        raise TFTPError(f"Malformed request: {exc}") from exc

    if mode not in SUPPORTED_MODES:
        raise TFTPError(f"Unsupported mode: '{mode}'")

    return {"opcode": opcode, "filename": filename, "mode": mode}


def _parse_data(data):
    if len(data) < 4:
        raise TFTPError("DATA packet too short")
    block   = struct.unpack("!H", data[2:4])[0]
    payload = data[4:]
    if len(payload) > BLOCK_SIZE:
        raise TFTPError(f"DATA payload exceeds {BLOCK_SIZE} bytes")
    return {"opcode": OP_DATA, "block": block, "payload": payload}


def _parse_ack(data):
    if len(data) < 4:
        raise TFTPError("ACK packet too short")
    block = struct.unpack("!H", data[2:4])[0]
    return {"opcode": OP_ACK, "block": block}


def _parse_error(data):
    if len(data) < 4:
        raise TFTPError("ERROR packet too short")
    error_code = struct.unpack("!H", data[2:4])[0]
    try:
        message = data[4:].rstrip(b"\x00").decode("ascii")
    except UnicodeDecodeError:
        message = ERROR_MESSAGES.get(error_code, "Unknown error")
    return {"opcode": OP_ERROR, "error_code": error_code, "message": message}


# Montar as requisições

def build_rrq(filename: str, mode: str = "octet") -> bytes:
    return _build_request(OP_RRQ, filename, mode)

def build_wrq(filename: str, mode: str = "octet") -> bytes:
    return _build_request(OP_WRQ, filename, mode)

def _build_request(opcode, filename, mode):
    return (
        struct.pack("!H", opcode)
        + filename.encode("ascii") + b"\x00"
        + mode.lower().encode("ascii") + b"\x00"
    )

def build_data(block: int, payload: bytes) -> bytes:
    if len(payload) > BLOCK_SIZE:
        raise ValueError(f"Payload too large: {len(payload)} bytes")
    return struct.pack("!HH", OP_DATA, block) + payload

def build_ack(block: int) -> bytes:
    return struct.pack("!HH", OP_ACK, block)

def build_error(error_code: int, message: str = "") -> bytes:
    msg = message or ERROR_MESSAGES.get(error_code, "Unknown error")
    return struct.pack("!HH", OP_ERROR, error_code) + msg.encode("ascii") + b"\x00"


def is_last_block(payload: bytes) -> bool:
    return len(payload) < BLOCK_SIZE
