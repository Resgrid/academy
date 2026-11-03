"""Keep application screens large and screen changes tied to actual speech."""
import sys
import json
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'sources/production'))
import deep_dive


class CaptureReadabilityTests(unittest.TestCase):
    def test_landscape_capture_uses_most_of_frame_without_stretching(self):
        x,y,width,height=deep_dive.capture_layout(1530,840)
        self.assertGreater(width/1920,.84)
        self.assertLess(abs(width/1530-height/840),.001)
        self.assertGreaterEqual(x,0)
        self.assertLessEqual(x+width,deep_dive.NOTES_BOX[0]-12)
        self.assertLessEqual(y+height,960)  # Captions have their own lower band.

    def test_portrait_and_small_browser_captures_require_recapture(self):
        for size in ((848,816),(833,802),(1920,3000),(1000,600)):
            with self.subTest(size=size),self.assertRaisesRegex(ValueError,'landscape'):
                deep_dive.capture_layout(*size)

    def test_reviewed_detail_can_enlarge_existing_authentic_evidence(self):
        with self.assertRaises(ValueError):deep_dive.capture_layout(570,340)
        x,y,w,h=deep_dive.capture_layout(570,340,detail=True)
        self.assertLess(abs(w/570-h/340),.001)
        self.assertLessEqual(y+h,960)
        with self.assertRaises(ValueError):deep_dive.capture_layout(400,240,detail=True)

    def test_screen_changes_use_exact_exported_cue_times(self):
        cues=[{'start':'00:00:01,123'},{'start':'00:00:03,456'}]
        self.assertEqual(deep_dive.capture_boundaries({'capture_cues':[2]},2,cues,0,5),[0,3.456,5])
        self.assertEqual(deep_dive.capture_boundaries({'capture_cues':[]},1,cues,0,5),[0,5])

    def test_invalid_and_out_of_scene_speech_cuts_are_rejected(self):
        cues=[{'start':'00:00:01,123'},{'start':'00:00:03,456'}]
        for cuts,count,start,end in (([0],2,0,5),([3],2,0,5),([True],2,0,5),([],2,0,5),([2,1],3,0,5),([1],2,2,5),([2],2,0,3)):
            with self.subTest(cuts=cuts,start=start,end=end),self.assertRaises(ValueError):
                deep_dive.capture_boundaries({'capture_cues':cuts},count,cues,start,end)

    def test_full_narration_requires_video_frames_through_the_closing_hold(self):
        deep_dive.validate_video_coverage(12099,403.291)
        for count in (0,11425,12000,12200):
            with self.subTest(count=count),self.assertRaisesRegex(ValueError,'all 403.291 seconds'):
                deep_dive.validate_video_coverage(count,403.291)

    def test_every_original_lesson_uses_explicit_speech_timed_wide_views(self):
        lessons=sorted((deep_dive.ROOT/'lessons').glob('*.json'))
        self.assertEqual(len(lessons),7)
        for path in lessons:
            lesson=json.loads(path.read_text())
            cues=deep_dive.parse_srt((deep_dive.ROOT/'review'/lesson['id']/'captions.srt').read_text())
            chapters=json.loads((deep_dive.ROOT/'review'/lesson['id']/'chapters.json').read_text())
            for scene,chapter in zip(lesson['scenes'],chapters):
                with self.subTest(lesson=lesson['id'],scene=scene['title']):
                    self.assertIn('capture_cues',scene)
                    boundaries=deep_dive.capture_boundaries(scene,len(scene['captures']),cues,chapter['start'],chapter['end'])
                    self.assertEqual(len(boundaries),len(scene['captures'])+1)
                    if 'capture_views' in scene:
                        self.assertEqual(len(scene['capture_views']),len(scene['captures']))
                        for view in scene['capture_views']:
                            self.assertTrue(view['visible_labels'])
                            self.assertTrue(view['rationale'])
                            _,_,width,height=view['region']
                            x,y,w,h=deep_dive.capture_layout(width,height,detail=True)
                            self.assertGreaterEqual(w/1920,.75)
                            self.assertLessEqual(y+h,960)


if __name__=='__main__':unittest.main()
