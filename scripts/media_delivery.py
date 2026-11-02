"""Canonical public Release asset names shared by packaging and validation."""
import hashlib
from pathlib import PurePosixPath
import re


def release_base(repository, tag='academy-media'):
    if not isinstance(repository, str) or not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Use a GitHub owner/repository name.')
    if repository.split('/')[1] in {'.', '..'}:
        raise ValueError('Invalid repository name.')
    if not isinstance(tag, str) or not re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]{0,99}', tag):
        raise ValueError('Use a simple Release tag name.')
    return f'https://github.com/{repository}/releases/download/{tag}'


def asset_name(path, digest):
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or '..' in parsed.parts or '\\' in path or parsed.suffix.lower() not in {'.mp4', '.webm'}:
        raise ValueError('Invalid source video path.')
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise ValueError('Invalid video SHA256.')
    return digest + parsed.suffix.lower()


def sha_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
