import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_public_repo import private_file, scan_bytes, scan_repository, scan_stream


class PublicRepositoryAuditTests(unittest.TestCase):
    def test_detects_key_token_and_authenticated_url_without_echoing_values(self):
        examples = [
            (b'-----BEGIN ' + b'PRIVATE KEY-----\nsynthetic', 'private-key material'),
            (b'ghp_' + b'a' * 36, 'GitHub credential'),
            (b'https://account:' + b'privatevalue@github.com/repo', 'credential-bearing URL'),
        ]
        for value, rule in examples:
            self.assertEqual(scan_bytes(value), [rule])
            self.assertNotIn(value.decode(), str(scan_bytes(value)))

    def test_detects_known_private_value_across_read_boundary(self):
        value = b'known-synthetic-credential-value'
        data = b' ' * (1024 * 1024 - 7) + value + b' trailing'
        self.assertEqual(scan_stream(io.BytesIO(data), [value]), ['known private training-stack credential'])

    def test_documentation_and_placeholders_are_not_credentials(self):
        for value in (b'API_TOKEN="your-token-goes-here"', b'Password="replace-me-before-use"', b'"secret": "example-placeholder-value"', b'Use a password manager and MFA.'):
            self.assertEqual(scan_bytes(value), [])
        self.assertIn('possible embedded credential assignment', scan_bytes(b'api_key="' + b'aF8wS2eR6tY0uI4oP9qL3dH7jK1zX5cV' + b'"'))

    def test_private_files_and_configs_need_review(self):
        for name in ('credential.pem', '.env.production', 'credentials.json', 'local-stack/config.json', 'private/notes.txt', 'id_ed25519'):
            self.assertTrue(private_file(Path(name)))
        for name in ('site/course.json', 'site/media/lesson.mp4', 'scripts/audit_public_repo.py'):
            self.assertFalse(private_file(Path(name)))

    def test_csharp_audit_labels_and_http_header_names_are_not_credentials(self):
        self.assertEqual(scan_bytes(b'Action = rotated ? "ScimBearerTokenRotated" : "ScimBearerTokenProvisioned";'), [])
        self.assertEqual(scan_bytes(b'public const string TokenHeader = "X-Resgrid-Connector-Token";'), [])
        self.assertIn('possible embedded credential assignment', scan_bytes(b'{"token": "' + b'aF8wS2eR6tY0uI4oP9qL3dH7jK1zX5cV' + b'"}'))

    def test_ignored_local_key_is_excluded_but_a_tracked_key_still_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'index.html').write_text('Academy')
            (root / 'credentials.key').write_bytes(b'-----BEGIN ' + b'PRIVATE KEY-----')

            def fake_git(_root, *arguments):
                if arguments[0] == 'rev-parse':
                    return str(root).encode()
                if arguments[0] == 'rev-list':
                    return b'0'
                if arguments[0] == 'cat-file':
                    return b''
                return b'index.html\0'

            with patch('audit_public_repo.git', side_effect=fake_git):
                self.assertTrue(scan_repository(root)['passed'])

            def tracked_key(_root, *arguments):
                if arguments[0] == 'ls-files':
                    return b'index.html\0credentials.key\0'
                return fake_git(_root, *arguments)

            with patch('audit_public_repo.git', side_effect=tracked_key):
                result = scan_repository(root)
                self.assertFalse(result['passed'])
                self.assertTrue(any(item['rule'] == 'private-key material' for item in result['findings']))


if __name__ == '__main__':
    unittest.main()
