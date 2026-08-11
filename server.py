#!/usr/bin/env python3
"""A single-purpose log server: accept a file upload and preserve its subdirectories."""

import argparse
import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse


DEFAULT_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
MAX_FILE_SIZE = 256 * 1024 * 1024


def safe_relative_path(raw: str) -> str:
    path = unquote(raw).replace("\\", "/").lstrip("/")
    raw_parts = path.split("/")
    if any(part in (".", "..") for part in raw_parts):
        raise ValueError("unsafe file path")
    parts = [part for part in raw_parts if part]
    if not parts:
        raise ValueError("empty file path")
    if any(":" in part or "\x00" in part for part in parts):
        raise ValueError("unsafe file path")
    return "/".join(parts)


class UploadHandler(BaseHTTPRequestHandler):
    timeout = 30

    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def log_message(self, fmt, *args):
        try:
            msg = fmt % args
        except Exception:
            msg = str(fmt)
        print(f"[log-server] {msg}", flush=True)

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_file_path(self):
        parsed = urlparse(self.path)
        raw_header = self.headers.get("X-File-Path", "")
        try:
            header_path = raw_header.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            header_path = raw_header
        query_path = parsed.query
        if query_path.startswith("path="):
            query_path = unquote(query_path[len("path="):])
        else:
            query_path = ""
        return header_path or query_path

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/upload":
            self._send_json({"error": "not found"}, 404)
            return

        try:
            relative_path = safe_relative_path(self._read_file_path())
        except ValueError as exc:
            self._send_json({"error": str(exc)}, 400)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            self._send_json({"error": "invalid content length"}, 400)
            return

        if length <= 0:
            self._send_json({"error": "empty body"}, 400)
            return
        if length > MAX_FILE_SIZE:
            self._send_json({"error": "file too large"}, 413)
            return

        try:
            data = self.rfile.read(length)
            if len(data) != length:
                raise ValueError("incomplete request body")
            target_dir = os.path.join(self.server.upload_dir, os.path.dirname(relative_path))
            os.makedirs(target_dir, exist_ok=True)

            target = os.path.join(target_dir, os.path.basename(relative_path))
            fd, tmp_path = tempfile.mkstemp(dir=target_dir, suffix=".tmp")
            try:
                with os.fdopen(fd, "wb") as fh:
                    fh.write(data)
                os.replace(tmp_path, target)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)
            return

        self._send_json({
            "status": "ok",
            "path": relative_path,
            "size": len(data),
        })

    def do_GET(self):
        if urlparse(self.path).path != "/health":
            self._send_json({"error": "not found"}, 404)
            return
        self._send_json({
            "status": "ok",
            "upload_dir": self.server.upload_dir,
        })


class ThreadedUploadServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, addr, handler, upload_dir):
        super().__init__(addr, handler)
        self.upload_dir = upload_dir


def main():
    parser = argparse.ArgumentParser(description="Single-purpose log upload server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--upload-dir", default=DEFAULT_UPLOAD_DIR)
    args = parser.parse_args()

    os.makedirs(args.upload_dir, exist_ok=True)
    server = ThreadedUploadServer((args.host, args.port), UploadHandler, args.upload_dir)
    print(f"Log server listening on {args.host}:{args.port}")
    print(f"Upload directory: {args.upload_dir}")
    print("POST /upload with X-File-Path: sub/dir/file.log")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
