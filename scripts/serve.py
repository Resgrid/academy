#!/usr/bin/env python3
"""Loopback-only Academy preview with byte ranges for video playback and seeking."""
import argparse
import re
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class AcademyHandler(SimpleHTTPRequestHandler):
    mount = '/Resgrid-Academy'

    def translate_path(self, path):
        parsed = urlsplit(path)
        if self.mount and parsed.path.startswith(self.mount + '/'):
            path = parsed.path[len(self.mount):]
            if parsed.query:
                path += '?' + parsed.query
        return super().translate_path(path)

    def send_head(self):
        self.remaining = None
        path = Path(self.translate_path(self.path)).resolve()
        try:
            relative = path.relative_to(Path(self.directory).resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return None
        if 'local-stack' in relative.parts:
            self.send_error(HTTPStatus.FORBIDDEN)
            return None
        if path.is_dir():
            return super().send_head()
        try:
            source = path.open('rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return None
        size = path.stat().st_size
        start, end = 0, size - 1
        requested = self.headers.get('Range')
        if requested:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested.strip())
            valid = bool(match and (match[1] or match[2]) and size)
            if valid:
                if match[1]:
                    start = int(match[1])
                    end = min(int(match[2]), end) if match[2] else end
                else:
                    count = int(match[2])
                    start = max(0, size - count)
                    valid = count > 0
                valid = valid and 0 <= start <= end < size
            if not valid:
                source.close()
                self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                self.send_header('Content-Range', f'bytes */{size}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return None
        self.send_response(HTTPStatus.PARTIAL_CONTENT if requested else HTTPStatus.OK)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Last-Modified', self.date_time_string(path.stat().st_mtime))
        if requested:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        source.seek(start)
        self.remaining = end - start + 1
        return source

    def copyfile(self, source, outputfile):
        if self.remaining is None:
            return super().copyfile(source, outputfile)
        remaining = self.remaining
        try:
            while remaining:
                data = source.read(min(256 * 1024, remaining))
                if not data:
                    break
                outputfile.write(data)
                remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8769)
    parser.add_argument('--site', type=Path, default=ROOT / 'site')
    parser.add_argument('--project-path', default='/Resgrid-Academy')
    args = parser.parse_args()
    AcademyHandler.mount = args.project_path.rstrip('/')
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(AcademyHandler, directory=str(args.site.resolve())))
    print(f'Resgrid Academy preview: http://127.0.0.1:{args.port}/', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
