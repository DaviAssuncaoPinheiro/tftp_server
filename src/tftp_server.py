import logging
import queue
import socket
import threading
from pathlib import Path

from src.file_service import FileReader, FileWriter
from src.protocol import (
    OP_RRQ, OP_WRQ, OP_ACK, OP_DATA, OP_ERROR,
    TFTPError, ERR_ILLEGAL_OP,
    build_ack, build_data, build_error, is_last_block, parse_packet,
)

log = logging.getLogger(__name__)

SESSION_TIMEOUT = 5
MAX_RETRIES     = 5


class TFTPServer:
    def __init__(self, host: str, port: int, root_dir: Path):
        self.host     = host
        self.port     = port
        self.root_dir = root_dir
        self._running = False
        self._sock    = None
        self._lock    = threading.Lock()
        self._sessions: dict[tuple, queue.Queue] = {}
        self._sessions_lock = threading.Lock()

    def start(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.settimeout(1.0)
        self._running = True

        log.info("TFTP server listening on %s:%d  root=%s", self.host, self.port, self.root_dir)
        try:
            while self._running:
                try:
                    data, addr = self._sock.recvfrom(516)
                except socket.timeout:
                    continue
                except OSError:
                    break
                self._route(data, addr)
        finally:
            self._sock.close()
            log.info("TFTP server stopped")

    def stop(self):
        self._running = False

    def send(self, pkt: bytes, addr: tuple):
        with self._lock:
            self._sock.sendto(pkt, addr)

    def register_session(self, addr: tuple, q: queue.Queue):
        with self._sessions_lock:
            self._sessions[addr] = q

    def unregister_session(self, addr: tuple):
        with self._sessions_lock:
            self._sessions.pop(addr, None)

    def _route(self, data: bytes, addr: tuple):
        with self._sessions_lock:
            q = self._sessions.get(addr)

        if q is not None:
            q.put(data)
            return

        try:
            pkt = parse_packet(data)
        except TFTPError as exc:
            log.warning("Bad packet from %s: %s", addr, exc)
            return

        if pkt["opcode"] == OP_RRQ:
            session = _RRQSession(self, addr, self.root_dir, pkt["filename"], pkt["mode"])
        elif pkt["opcode"] == OP_WRQ:
            session = _WRQSession(self, addr, self.root_dir, pkt["filename"], pkt["mode"])
        else:
            log.warning("Unexpected opcode %d from %s", pkt["opcode"], addr)
            return

        threading.Thread(target=session.run, daemon=True).start()


class _Session:
    def __init__(self, server, client_addr, root_dir, filename, mode):
        self.server      = server
        self.client_addr = client_addr
        self.root_dir    = root_dir
        self.filename    = filename
        self.mode        = mode
        self._q          = queue.Queue()

    def _send(self, pkt):
        self.server.send(pkt, self.client_addr)

    def _send_error(self, code, msg=""):
        try:
            self._send(build_error(code, msg))
        except OSError:
            pass

    def _recv(self):
        return self._q.get(timeout=SESSION_TIMEOUT)

    def _setup(self):
        self.server.register_session(self.client_addr, self._q)

    def _teardown(self):
        self.server.unregister_session(self.client_addr)


class _RRQSession(_Session):

    def run(self):
        log.info("[RRQ] %s -> '%s'", self.client_addr, self.filename)
        self._setup()
        try:
            with FileReader(self.root_dir, self.filename) as reader:
                self._transfer(reader)
        except TFTPError as exc:
            log.warning("[RRQ] error: %s", exc)
            self._send_error(exc.error_code, str(exc))
        except Exception as exc:
            log.exception("[RRQ] unexpected error")
            self._send_error(ERR_ILLEGAL_OP, str(exc))
        finally:
            self._teardown()

    def _transfer(self, reader):
        last = False
        while not last:
            block, payload = reader.next_block()
            last = is_last_block(payload)
            pkt  = build_data(block, payload)

            for attempt in range(1, MAX_RETRIES + 1):
                self._send(pkt)
                if self._wait_ack(block):
                    break
                log.debug("[RRQ] timeout block %d attempt %d", block, attempt)
            else:
                log.warning("[RRQ] gave up on block %d", block)
                return

        log.info("[RRQ] complete: '%s'", self.filename)

    def _wait_ack(self, expected):
        try:
            while True:
                pkt = parse_packet(self._recv())
                if pkt["opcode"] == OP_ACK:
                    if pkt["block"] == expected:
                        return True
                elif pkt["opcode"] == OP_ERROR:
                    raise TFTPError(pkt["message"], pkt["error_code"])
        except (queue.Empty, TFTPError):
            return False


class _WRQSession(_Session):

    def run(self):
        log.info("[WRQ] %s -> '%s'", self.client_addr, self.filename)
        self._setup()
        writer = None
        try:
            writer = FileWriter(self.root_dir, self.filename)
            self._send(build_ack(0))
            self._transfer(writer)
            writer.close()
        except TFTPError as exc:
            log.warning("[WRQ] error: %s", exc)
            self._send_error(exc.error_code, str(exc))
            if writer:
                writer.abort()
        except Exception as exc:
            log.exception("[WRQ] unexpected error")
            self._send_error(ERR_ILLEGAL_OP, str(exc))
            if writer:
                writer.abort()
        finally:
            self._teardown()

    def _transfer(self, writer):
        expected = 1
        while True:
            try:
                pkt = parse_packet(self._recv())
            except queue.Empty:
                log.warning("[WRQ] timeout waiting for block %d", expected)
                return
            except TFTPError:
                continue

            if pkt["opcode"] == OP_DATA:
                if pkt["block"] == expected:
                    writer.write_block(pkt["payload"])
                    self._send(build_ack(expected))
                    if is_last_block(pkt["payload"]):
                        log.info("[WRQ] complete: '%s'", self.filename)
                        return
                    expected += 1
                elif pkt["block"] == expected - 1:
                    self._send(build_ack(pkt["block"]))  # re-ACK retransmit
                else:
                    self._send_error(ERR_ILLEGAL_OP, f"Unexpected block {pkt['block']}")
                    return
            elif pkt["opcode"] == OP_ERROR:
                log.warning("[WRQ] client error: %s", pkt["message"])
                return
