#!/usr/bin/env python3
"""Serve a chosen local media review folder on loopback with byte-range seeking."""
import argparse
import functools
import http.server
import os
import re
from pathlib import Path


class ReviewHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        self.remaining = None
        path = self.translate_path(self.path)
        header = self.headers.get('Range')
        if not header or not os.path.isfile(path):
            return super().send_head()
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', header)
        size = os.path.getsize(path)
        if not match or not any(match.groups()):
            self.send_error(416, 'Only one byte range is supported')
            return None
        first, last = match.groups()
        start = int(first) if first else max(0, size - int(last))
        end = min(int(last), size - 1) if first and last else size - 1
        if start >= size or end < start:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.end_headers()
            return None
        source = open(path, 'rb')
        source.seek(start)
        self.remaining = end - start + 1
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(self.remaining))
        self.end_headers()
        return source

    def copyfile(self, source, destination):
        try:
            if self.remaining is None:
                return super().copyfile(source, destination)
            while self.remaining:
                data = source.read(min(65536, self.remaining))
                if not data:
                    break
                destination.write(data)
                self.remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            # Seeking cancels the previous stream in normal browser playback.
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--port', type=int, default=18970)
    args = parser.parse_args()
    folder = args.directory.resolve(strict=True)
    if not folder.is_dir() or not 1024 <= args.port <= 65535:
        parser.error('Choose a directory and a port between 1024 and 65535')
    handler = functools.partial(ReviewHandler, directory=str(folder))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    print(f'Review files: http://127.0.0.1:{args.port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
