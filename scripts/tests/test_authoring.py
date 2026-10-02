import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_sources import verify


class AuthoringInputTests(unittest.TestCase):
    def fixture(self, root):
        def write(relative, data):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data)

        write('course.json', json.dumps({'lessons': [{'id': '01-demo', 'voice': 'Warm Lulu', 'video': 'media/demo.mp4', 'poster': 'media/demo.jpg', 'subtitle': 'media/demo.vtt'}], 'features': []}))
        write('deep-dive/course.json', '{"lessons": []}')
        write('deep-dive/audio/sources.json', '{}')
        write('production/descript/01-demo-edit-brief.json', '{"scenes": [{"title": "Demo"}]}')
        for relative in ('scripts/01-demo.txt', 'production/descript/slides/01-demo-slide-01.png', 'production/descript/natural/audio/01-demo.m4a', 'production/descript/natural/captions/01-demo-raw.srt', 'media/demo.mp4', 'media/demo.jpg', 'media/demo.vtt', 'captures/firehouse51/narration.m4a', 'captures/firehouse51/narration-raw.srt', 'captures/firehouse51/narration-script.json'):
            write(relative, 'synthetic fixture')
        write('evidence/resgrid/example.cs', 'original source')
        write('evidence/source-manifest.json', json.dumps({'files': [{'path': 'example.cs', 'sha256': hashlib.sha256(b'original source').hexdigest()}]}))

    def test_missing_narration_input_stops_source_build(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            self.assertTrue(verify(root)['passed'])
            (root / 'production/descript/natural/audio/01-demo.m4a').unlink()
            result = verify(root)
            self.assertFalse(result['passed'])
            self.assertTrue(any('01-demo.m4a' in issue for issue in result['issues']))

    def test_recorded_source_evidence_change_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / 'evidence/resgrid/example.cs').write_text('changed source')
            result = verify(root)
            self.assertFalse(result['passed'])
            self.assertTrue(any('Recorded source evidence changed' in issue for issue in result['issues']))


if __name__ == '__main__':
    unittest.main()
