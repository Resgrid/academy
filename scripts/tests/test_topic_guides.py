"""Public text-guide behavior; synthetic media is never recording evidence.

The export checks use only Python's stdlib. One optional Node check executes
the catalog selector against an in-memory DOM stub, never a browser or app.
"""
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_expansion_integration as integration
from export_site import export
from public_site import learner_course, TOPIC_JS
from validate_site import validate


class TopicGuideTests(unittest.TestCase):
    def setUp(self):
        self.fixture = integration.ExpansionIntegrationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.sources, self.output = self.fixture.sources, self.fixture.output
        project = Path(__file__).resolve().parents[2]
        self.original = json.loads((project / 'sources/course.json').read_text())
        self.assertEqual(len(self.original['lessons']), 24)
        (self.sources / 'course.json').write_text(json.dumps(self.original))
        examples = self.original['lessons'][0]['sector_examples']
        sector_data = {'sectors': list(examples), 'deep_lessons': [], 'primer_lessons': self.original['lessons']}
        (self.sources / 'deep-dive/sector-examples.json').write_text(json.dumps(sector_data))
        for lesson in self.original['lessons']:
            for key in ('video', 'poster', 'subtitle'):
                path = self.sources / urlsplit(lesson[key]).path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(('synthetic retained original ' + lesson['id'] + ' ' + key).encode())
        self.retained = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in [self.sources / 'course.json', *self.sources.joinpath('media').glob('*')]}

    def publish(self):
        result = export(self.sources, self.output)
        self.assertTrue(result['passed'], result['issues'])
        return json.loads((self.output / 'site-manifest.json').read_text())

    def test_all_24_guides_preserve_readable_text_roles_six_sectors_and_downloads(self):
        manifest = self.publish()
        self.assertEqual(manifest['topic_guide_count'], 24)
        self.assertEqual(len(manifest['topic_guides']), 24)
        self.assertNotIn('primers', manifest)
        course = json.loads((self.output / 'course.json').read_text())
        self.assertEqual(course['learning_paths'], self.original['learning_paths'])
        self.assertEqual(len(course['lessons']), 24)
        root = (self.output / 'index.html').read_text()
        for original, guide in zip(self.original['lessons'], course['lessons']):
            self.assertEqual(guide['kind'], 'topic_guide')
            self.assertEqual(guide['role'], original['role'])
            for name, example in original['sector_examples'].items():
                self.assertEqual(guide['sector_examples'][name], example)
            self.assertEqual(len(guide['sector_examples']), 6)
            self.assertIn('Fire / EMS', guide['sector_examples'])
            if original['id'] not in {'22-relay', '23-self-hosting'}:
                self.assertEqual(guide['scenes'], [{key: scene[key] for key in ('title', 'narration')}
                                                 for scene in original['scenes']])
            else:
                self.assertEqual(guide['scenes'][:-1], [{key: scene[key] for key in ('title', 'narration')}
                                                      for scene in original['scenes'][:-1]])
            for key in ('video', 'poster', 'subtitle', 'duration_seconds'):
                self.assertNotIn(key, guide)
            target = self.output / guide['href'] / 'index.html'
            markup = target.read_text()
            self.assertNotIn('<video', markup)
            self.assertNotIn('<track', markup)
            self.assertIn(html.escape(original['role'], quote=True), markup)
            for scene in guide['scenes']:
                self.assertIn(html.escape(scene['title'], quote=True), markup)
                self.assertIn(html.escape(scene['narration'], quote=True), markup)
            for name, example in guide['sector_examples'].items():
                self.assertIn('<dt>' + html.escape(name, quote=True) + '</dt>', markup)
                self.assertIn(html.escape(example, quote=True), markup)
            transcript = (self.output / guide['transcript']).read_text()
            self.assertIn(guide['scenes'][-1]['narration'], transcript)
            self.assertIn(list(original['sector_examples'].values())[-1], transcript)
            self.assertIn(f'href="{guide["href"]}" data-lesson-link', root)
            self.assertIn(f'id="lesson={guide["id"]}"', root)
        self.assertEqual(self.fixture.domain.read_text(), '{"custom_domain":"academy.resgrid.com"}\n')

    def test_only_two_approved_recorder_sentences_change_in_public_text(self):
        course = learner_course(self.original)
        by_id = {item['id']: item for item in course['lessons']}
        relay = by_id['22-relay']['scenes'][-1]['narration']
        self.assertNotIn('A recorder will need', relay)
        self.assertNotIn('turn this briefing into', relay)
        self.assertIn('Use the supported Relay application and an audio test setup to verify the workflow.', relay)
        hosting = by_id['23-self-hosting']['scenes'][-1]['narration']
        self.assertNotIn('Detailed infrastructure capture needs', hosting)
        self.assertIn('Choose the deployment layout you will verify: Linux Compose, Windows, Kubernetes or k3s, or an Incident Command Kit.', hosting)
        self.assertIn('verify installation, endpoint connectivity, backup, and recovery', hosting)
        self.assertIn('A recorder will need', next(item for item in self.original['lessons'] if item['id']=='22-relay')['scenes'][-1]['narration'])

    def test_no_primer_player_or_media_leaks_and_original_sources_remain(self):
        manifest = self.publish()
        root = (self.output / 'index.html').read_text()
        for token in ('<video', '<track', 'player.pause', 'lesson.video', 'Watch the topic lesson', 'Watch lesson →'):
            self.assertNotIn(token, root)
        self.assertNotIn('illustrated', json.dumps(manifest).lower())
        topic_ids = {x['id'] for x in self.original['lessons']}
        self.assertFalse(topic_ids & {x['id'] for x in manifest['lessons']})
        for lesson in self.original['lessons']:
            for suffix in ('.mp4', '.vtt', '.srt', '.chapters.json'):
                self.assertFalse((self.output / 'media' / (lesson['id'] + suffix)).exists())
        for path, expected in self.retained.items():
            self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(), expected)
        intro = 'captures/firehouse51/firehouse51-walkthrough.mp4'
        self.assertIn(intro, {item['path'] for item in manifest['media']})
        self.assertIn('<video', (self.output / 'captures/firehouse51/index.html').read_text())
        # Atomic re-export removes formerly public primer files, with source
        # bytes intact; no leftover video survives merely because it existed.
        old = self.output / 'media/00-start.mp4'
        old.parent.mkdir(exist_ok=True)
        old.write_bytes(b'previous illustrated export')
        self.publish()
        self.assertFalse(old.exists())

    def test_feature_and_sector_links_open_real_topic_pages_with_relative_urls(self):
        self.publish()
        root = (self.output / 'index.html').read_text()
        for feature in self.original['features']:
            self.assertIn(f'href="topics/{feature["lesson"]}/" data-lesson-link', root)
            self.assertTrue((self.output / 'scripts' / f'feature-{feature["id"]}.txt').is_file())
        self.assertIn('Learning path', root)
        self.assertIn('lesson-search', root)
        self.assertIn('feature-search', root)
        self.assertIn('setting-search', root)
        sector_page = (self.output / 'deep-dive/sectors.html').read_text()
        for lesson in self.original['lessons']:
            self.assertIn('href="../#lesson=' + lesson['id'] + '"', sector_page)
        self.assertNotIn('href="/', root)
        self.assertNotIn('src="/', root)

    def test_validator_rejects_reintroduced_primer_media_and_topic_players(self):
        self.publish()
        target = self.output / 'topics/00-start/index.html'
        target.write_text(target.read_text().replace('</main>', '<video></video></main>'))
        self.assertTrue(any('Topic guide contains a media player' in item for item in validate(self.output)['issues']))
        self.publish()
        stale = self.output / 'media/00-start.vtt'
        stale.parent.mkdir(exist_ok=True)
        stale.write_text('WEBVTT\n')
        self.assertTrue(any('Illustrated primer asset is not public' in item for item in validate(self.output)['issues']))
        self.publish()
        path = self.output / 'site-manifest.json'
        manifest = json.loads(path.read_text())
        manifest['lessons'][0]['kind'] = 'illustrated primer'
        path.write_text(json.dumps(manifest))
        self.assertTrue(any('Only actual application walkthroughs' in item for item in validate(self.output)['issues']))

    def test_selector_hash_navigation_and_role_search_do_not_require_a_player(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Optional Node runtime is unavailable; Python export checks still cover all24guides.')
        course = learner_course(self.original)
        prefix = r'''
const nodes={},listeners={};
class Element{constructor(){this.dataset={};this.attributes={};this.value='';this.textContent='';this.content='';this.events={};this.hidden=false;this.classList={toggle:(name,hidden)=>{if(name==='hidden')this.hidden=hidden;}};}
set innerHTML(value){this.content=value;}get innerHTML(){return this.content||this.textContent.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
addEventListener(kind,handler){this.events[kind]=handler;}setAttribute(key,value){this.attributes[key]=value;}removeAttribute(key){delete this.attributes[key];}scrollIntoView(){this.scrolled=true;}}
const fixture=FIXTURE, cards=fixture.lessons.map(item=>{const el=new Element();el.dataset.lesson=item.id;el.textContent=item.title+' '+item.role;return el;}),links=fixture.lessons.map(item=>{const el=new Element();el.dataset.lesson=item.id;return el;});
const document={getElementById:id=>nodes[id]||(nodes[id]=new Element()),createElement:()=>new Element(),querySelectorAll:selector=>selector==='.lesson-card'?cards:selector==='[data-lesson-link]'?links:[]};
const location={hash:'#lesson='+fixture.lessons[2].id};const history={replaceState:(a,b,value)=>{location.hash=value;}};const window={addEventListener:(kind,handler)=>{listeners[kind]=handler;}};
function check(value,message){if(!value)throw new Error(message);}
'''.replace('FIXTURE', json.dumps(course))
        assertions = r'''
check(nodes['lesson-title'].textContent===fixture.lessons[2].title,'initial old deep link');
for(const lesson of fixture.lessons){chooseLesson(lesson.id,false);check(nodes['lesson-title'].textContent===lesson.title,'title');check(nodes.transcript.content.includes(escapeText(lesson.scenes.at(-1).narration)),'complete text');check(nodes['topic-outline'].content.includes('#topic-step-'+lesson.scenes.length),'outline');check(nodes['transcript-link'].href===lesson.transcript,'download');check(nodes['topic-page-link'].href===lesson.href,'standalone page');}
const role=Object.keys(COURSE.learning_paths).find(key=>key!=='Complete series');nodes.path.value=role;nodes['lesson-search'].value='';filterLessons();check(cards.filter(item=>!item.hidden).length===COURSE.learning_paths[role].length,'role filter');
nodes.path.value='Complete series';nodes['lesson-search'].value='records';filterLessons();check(cards.filter(item=>!item.hidden).every(item=>{const lesson=fixture.lessons.find(lesson=>lesson.id===item.dataset.lesson);return (item.textContent+' '+lesson.scenes.map(scene=>scene.title+' '+scene.narration).join(' ')).toLowerCase().includes('records');}),'search includes guide content');
document.getElementById('quick-query').value='run cards';nodes['quick-search'].events.submit({preventDefault(){}});check(nodes['lesson-search'].value==='run cards'&&nodes.lessons.scrolled,'hero search reaches filtered library');check(cards.some(item=>!item.hidden),'run-card content is discoverable');
location.hash='#lesson='+fixture.lessons[0].id;listeners.hashchange();check(nodes['lesson-title'].textContent===fixture.lessons[0].title,'hash change');
let prevented=false;links[1].events.click({button:0,preventDefault:()=>{prevented=true;}});check(prevented&&location.hash==='#lesson='+fixture.lessons[1].id,'guide click');
prevented=false;links[0].events.click({button:0,ctrlKey:true,preventDefault:()=>{prevented=true;}});check(!prevented,'modified click preserves normal link');
console.log(JSON.stringify({guides:fixture.lessons.length,passed:true}));
'''
        result = subprocess.run([node, '-'], input=prefix + TOPIC_JS.replace('COURSE_DATA', json.dumps(course)) + assertions,
                                text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'guides': 24, 'passed': True})


if __name__ == '__main__':
    unittest.main()
