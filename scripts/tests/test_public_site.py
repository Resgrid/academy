import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from public_site import learner_course, page
from render_public_media import publication_cut
from validate_site import validate


class PublicAcademyTests(unittest.TestCase):
    def test_authoring_metadata_is_removed_and_operational_drafts_are_preserved(self):
        original = {
            'learning_paths': {'Member': ['records']},
            'voice_status': 'Warm Lulu; human listening review pending',
            'lessons': [{'id': 'records', 'title': 'Review draft incident records',
                         'status': 'illustrated draft; live walkthrough pending', 'voice': 'Warm Lulu',
                         'sector_narration_status': 'in production',
                         'scenes': [{'title': 'Draft records', 'narration': 'Prepare an incomplete draft.'}]}],
            'features': [{'id': 'records', 'label': 'Draft records', 'capture_status': 'not recorded',
                          'verification_status': 'deployment unverified', 'release_status': 'available',
                          'purpose': 'Review incomplete draft reports.', 'source': {'path': 'internal.cs'}}],
            'settings': [{'id': 'drafts', 'label': 'Draft visibility', 'help': 'Control access to draft records.',
                          'source': {'path': 'internal.yaml'}}],
        }
        before = copy.deepcopy(original)
        published = learner_course(original)
        self.assertEqual(original, before)
        serialized = json.dumps(published)
        for internal in ('Lulu', 'in production', 'walkthrough pending', 'internal.cs', 'internal.yaml', 'not recorded'):
            self.assertNotIn(internal, serialized)
        self.assertIn('incomplete draft', serialized)
        self.assertEqual(published['features'][0]['release_status'], 'available')

    def test_publish_validation_rejects_production_badges_but_allows_records_drafts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'site-manifest.json').write_text('{"media": []}')
            (root / 'index.html').write_text('<h1>Review draft incident records</h1>')
            self.assertTrue(validate(root)['passed'])
            (root / 'index.html').write_text('<h1>Warm Lulu · Illustrated draft</h1>')
            result = validate(root)
            self.assertFalse(result['passed'])
            self.assertTrue(any('Academy production label' in issue for issue in result['issues']))

    def test_all_public_navigation_is_relative_at_nested_paths(self):
        markup = page('Settings', '<h1>Learn settings</h1>', '../../../')
        self.assertIn('href="../../../deep-dive/"', markup)
        self.assertIn('href="../../../about/"', markup)
        self.assertNotIn('href="/', markup)

    def test_editorial_tail_is_cut_between_complete_caption_cues(self):
        cues = [
            {'start': 0, 'end': 3, 'text': 'Record the result and follow-up owner.'},
            {'start': 3.4, 'end': 7, 'text': 'Use the linked feature scripts for the detailed screen recording plan.'},
        ]
        end, retained = publication_cut('01-people', cues, 7.2)
        self.assertEqual(end, 3.2)
        self.assertEqual(retained, cues[:1])
        # Rebuilding an already trimmed lesson preserves its complete narration.
        self.assertEqual(publication_cut('01-people', retained, end), (end, retained))
        draft_cue = [{'start': 0, 'end': 3, 'text': 'Prepare an incomplete draft incident report.'}]
        self.assertEqual(publication_cut('14-records', draft_cue, 3.2), (3.2, draft_cue))


if __name__ == '__main__':
    unittest.main()
