import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_public_repo import private_file, scan_bytes, scan_git_blobs, scan_repository, scan_stream


class PublicRepositoryAuditTests(unittest.TestCase):
    def test_detects_key_token_and_authenticated_url_without_echoing_values(self):
        examples = [
            (b'-----BEGIN ' + b'PRIVATE KEY-----\nsynthetic', 'private-key material'),
            (b'ghp_' + b'a' * 36, 'GitHub credential'),
            (b'pk.' + b'a' * 24 + b'.' + b'b' * 24, 'embedded Mapbox access token'),
            (b'https://account:' + b'privatevalue@github.com/repo', 'credential-bearing URL'),
        ]
        for value, rule in examples:
            self.assertEqual(scan_bytes(value), [rule])
            self.assertNotIn(value.decode(), str(scan_bytes(value)))

    def test_detects_known_private_value_across_read_boundary(self):
        value = b'known-synthetic-credential-value'
        data = b' ' * (1024 * 1024 - 7) + value + b' trailing'
        self.assertEqual(scan_stream(io.BytesIO(data), [value]), ['known private training-stack credential'])

    def test_prefilters_retain_every_credential_format_and_case_insensitive_rule(self):
        examples = [
            *[(b'gh' + kind + b'_' + b'a' * 36, 'GitHub credential') for kind in (b'p', b'o', b'u', b's', b'r')],
            (b'github_' + b'pat_' + b'a' * 36, 'GitHub credential'),
            *[(prefix + b'A' * 16, 'AWS access credential') for prefix in (b'AK' + b'IA', b'AS' + b'IA')],
            (b'AI' + b'za' + b'a' * 35, 'Google API credential'),
            *[(prefix + b'.' + b'a' * 24 + b'.' + b'b' * 24, 'embedded Mapbox access token') for prefix in (b'pk', b'sk')],
            *[(b'xox' + kind + b'-' + b'a' * 24, 'Slack credential') for kind in (b'b', b'a', b'p', b'r', b's')],
            *[(kind + b'_' + mode + b'_' + b'a' * 24, 'Stripe secret credential')
              for kind in (b'sk', b'rk') for mode in (b'live', b'test')],
            (b'ey' + b'J' + b'a' * 20 + b'.' + b'b' * 24 + b'.' + b'c' * 24, 'JWT bearer credential'),
            (b'HTTPS://account:' + b'privatevalue@example.com', 'credential-bearing URL'),
            (b'HTTPS://SHARE.DESCRIPT.COM/' + b'VIEW/' + b'a' * 24, 'private editor or signed URL'),
            *[(b'HTTPS://WEB.DESCRIPT.COM/' + kind + b'/' + b'a' * 24, 'private editor or signed URL')
              for kind in (b'PROJECT', b'EDITOR')],
            *[(b'https://example.com/?' + key + b'=' + b'a' * 24, 'private editor or signed URL')
              for key in (b'X-GOOG-' + b'SIGNATURE', b'X-AMZ-' + b'SIGNATURE', b'ACCESS_' + b'TOKEN', b'SIG')],
        ]
        for data, rule in examples:
            with self.subTest(rule=rule):
                self.assertIn(rule, scan_bytes(b'\x00\xff' + data + b'\x00\xff'))
        for key in (b'PASSWORD', b'PASSWD', b'SECRET', b'TOKEN', b'APIKEY', b'API_KEY', b'API-KEY',
                    b'ACCOUNTKEY', b'CONNECTIONSTRING', b'SIGNINGKEY', b'ENCRYPTIONKEY'):
            value = b'aF8wS2eR6tY0uI4oP9qL3dH7jK1zX5cV'
            for assignment in (key + b'="' + value + b'"', b'{"' + key + b'": "' + value + b'"}'):
                self.assertIn('possible embedded credential assignment', scan_bytes(assignment))

    def test_sized_stream_stops_at_object_boundary_and_rejects_truncation(self):
        value = b'gh' + b'p_' + b'a' * 36
        data = b'\x00' * (1024 * 1024 - 7) + value
        stream = io.BytesIO(data + b'\nnext object header\n')
        self.assertEqual(scan_stream(stream, size=len(data)), ['GitHub credential'])
        self.assertEqual(stream.read(), b'\nnext object header\n')
        with self.assertRaises(ValueError):
            scan_stream(io.BytesIO(data), size=len(data) + 1)

    def test_batch_scans_binary_and_unreachable_blobs_without_leaking_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()

            def git(*args, data=None):
                return subprocess.run(['git', '-C', str(root), *args], input=data,
                                      capture_output=True, check=True).stdout.strip()

            git('init', '--quiet')
            git('mktree', data=b'')  # Non-blob objects must not disrupt batch framing.
            empty = git('hash-object', '-w', '--stdin', data=b'').decode()
            token = b'gh' + b'p_' + b'a' * 36
            binary = b'\x00\xff\n' + b'\x00' * (1024 * 1024 - 10) + token + b'\x00\n'
            ident = git('hash-object', '-w', '--stdin', data=binary).decode()
            known_value = b'known-synthetic-private-value'
            known_ident = git('hash-object', '-w', '--stdin', data=known_value).decode()
            (root / 'index.html').write_text('Academy')
            git('add', 'index.html')
            git('config', 'academy.password', known_value.decode())
            progress = []
            result = scan_repository(root, [known_value], progress.append)
            self.assertFalse(result['passed'])
            self.assertEqual(result['stored_git_blobs_scanned'], 4)
            self.assertEqual(result['reachable_commits'], 0)
            self.assertIn({'path': 'Git blob ' + ident, 'rule': 'GitHub credential'}, result['findings'])
            self.assertIn({'path': 'Git blob ' + known_ident, 'rule': 'known private training-stack credential'}, result['findings'])
            self.assertIn({'path': '.git/config (local metadata)', 'rule': 'known private training-stack credential'}, result['findings'])
            self.assertFalse(any(row['path'] == 'Git blob ' + empty for row in result['findings']))
            self.assertNotIn(token.decode(), json.dumps(result) + str(progress))
            self.assertNotIn(known_value.decode(), json.dumps(result) + str(progress))
            self.assertTrue(progress)

    def test_batch_git_errors_fail_the_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(subprocess.CalledProcessError):
                scan_git_blobs(Path(directory))

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

    def test_only_exact_map_razor_reference_is_treated_as_source_code(self):
        field = b'mapaccesstoken'
        reference = b'@mapConfig.AccessToken'
        self.assertEqual(scan_bytes(field + b'="' + reference + b'"'), [])
        for key, value in [(b'api_key', reference), (field, reference + b'Extra'),
                           (field, b'@' + b'aF8wS2eR6tY0uI4oP9qL3dH7jK1zX5cV')]:
            self.assertIn('possible embedded credential assignment', scan_bytes(key + b'="' + value + b'"'))

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

            with patch('audit_public_repo.git', side_effect=fake_git), patch('audit_public_repo.scan_git_blobs', return_value=(0, [])):
                self.assertTrue(scan_repository(root)['passed'])

            def tracked_key(_root, *arguments):
                if arguments[0] == 'ls-files':
                    return b'index.html\0credentials.key\0'
                return fake_git(_root, *arguments)

            with patch('audit_public_repo.git', side_effect=tracked_key), patch('audit_public_repo.scan_git_blobs', return_value=(0, [])):
                result = scan_repository(root)
                self.assertFalse(result['passed'])
                self.assertTrue(any(item['rule'] == 'private-key material' for item in result['findings']))


if __name__ == '__main__':
    unittest.main()
