"""Real-input guard regressions; no synthetic approvals or media are written."""
from contextlib import redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
PRODUCTION = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, PRODUCTION / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SEAL = load('seal_core_administration_frame_reviews_20261030')
QUALIFY = load('qualify_core_administration_releases_20261030')


class GenuineReviewGuards(unittest.TestCase):
    def test_all_actual_frame_bundles_leave_only_browser_proof_gate(self):
        for lesson in ('billing', 'shifts', 'training'):
            with self.subTest(lesson=lesson):
                config, evidence, audit = SEAL.prepare(lesson)
                self.assertEqual(len(audit['strict_partial_evidence_report']['issues']), 4)
                self.assertTrue(all(x.startswith('browser_playback:') for x in
                                    audit['strict_partial_evidence_report']['issues']))
                self.assertEqual(evidence['browser_playback'], [])
                self.assertEqual((SEAL.SOURCES / config['take'] / 'evidence.frames-reviewed.json').read_bytes(),
                                 SEAL.encoded(evidence))

    def test_repeat_sealing_refuses_to_replace_actual_history(self):
        for lesson in ('billing', 'shifts', 'training'):
            with self.subTest(lesson=lesson), redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, 'New-only review'):
                    SEAL.main([lesson, '--write-review'])

    def test_missing_genuine_proof_and_receipt_cannot_qualify(self):
        catalog = json.loads(QUALIFY.CATALOG.read_text())
        for lesson in ('billing', 'shifts', 'training'):
            with self.subTest(lesson=lesson):
                take = QUALIFY.SOURCES / catalog['lessons'][lesson]['take']
                existing = {p: QUALIFY.sha(p) for p in (take / 'evidence.frames-reviewed.json',
                                                       take / 'frame-review.audit.json')}
                with self.assertRaisesRegex(ValueError, 'Exact actual proof'):
                    QUALIFY.prepare(lesson, '_reports/missing-genuine-browser-proof.json', '0' * 64,
                                    '_reports/missing-genuine-root-review.json', '0' * 64)
                for path, digest in existing.items():
                    self.assertEqual(QUALIFY.sha(path), digest)

    def test_changed_reviewed_input_is_rejected_before_any_playback_read(self):
        catalog = json.loads(QUALIFY.CATALOG.read_text())
        config = catalog['lessons']['training']
        target = QUALIFY.SOURCES / config['take'] / (config['lesson_id'] + '.mp4')
        actual_sha = QUALIFY.sha
        with patch.object(QUALIFY, 'sha', side_effect=lambda path: '0' * 64 if Path(path) == target else actual_sha(path)):
            with self.assertRaisesRegex(ValueError, 'Changed genuine reviewed input'):
                QUALIFY.prepare('training', '_reports/missing-genuine-browser-proof.json', '0' * 64,
                                '_reports/missing-genuine-root-review.json', '0' * 64)

    def test_unreviewed_or_wrong_order_playback_is_rejected(self):
        config = json.loads(QUALIFY.CATALOG.read_text())['lessons']['billing']
        # These are deliberately incomplete in-memory negative inputs. They
        # never become proof files, review receipts or accepted playback.
        for rows in ([], [{'position': p} for p in ('beginning', 'middle', 'end')],
                     [{'position': p} for p in ('beginning', 'end', 'middle')]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                QUALIFY.validate_playback(deepcopy(rows), {}, config, '0' * 64)


if __name__ == '__main__':
    unittest.main()
