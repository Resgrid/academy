"""Check that the editable course has its local audio, caption, visual and evidence inputs."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


def verify(root):
    root = Path(root).resolve()
    issues = []

    def require(relative):
        candidate = root / relative
        target = candidate.resolve()
        if root not in target.parents or candidate.is_symlink() or not target.is_file():
            issues.append('Missing or unsafe authoring input: ' + relative)

    course = json.loads((root / 'course.json').read_text())
    plans = json.loads((root / 'deep-dive/course.json').read_text())
    for lesson in course['lessons']:
        ident = lesson['id']
        require('scripts/' + ident + '.txt')
        require('production/descript/' + ident + '-edit-brief.json')
        brief = json.loads((root / 'production/descript' / (ident + '-edit-brief.json')).read_text())
        for number in range(1, len(brief['scenes']) + 1):
            require(f'production/descript/slides/{ident}-slide-{number:02}.png')
        if lesson.get('voice') == 'Warm Lulu':
            require('production/descript/natural/audio/' + ident + '.m4a')
            require('production/descript/natural/captions/' + ident + '-raw.srt')
        elif ident == '14-records':
            audio = list((root / 'production/original-records/audio').glob('*.aiff'))
            if len(audio) != len(brief['scenes']):
                issues.append('Original Records narration does not cover every scene.')
        for key in ('video', 'poster', 'subtitle'):
            require(urlsplit(lesson[key]).path)
    for feature in course['features']:
        require('scripts/feature-' + feature['id'] + '.txt')
    detailed = list((root / 'deep-dive/lessons').glob('*.json'))
    audio_sources = json.loads((root / 'deep-dive/audio/sources.json').read_text())
    for file in detailed:
        lesson = json.loads(file.read_text())
        ident = lesson['id']
        for scene in lesson['scenes']:
            for capture in scene['captures']:
                require('captures/deep-dive/' + capture)
        if ident in audio_sources:
            require('deep-dive/audio/' + ident + '.m4a')
            require('deep-dive/' + ident + '-raw.srt')
    require('captures/firehouse51/narration.m4a')
    require('captures/firehouse51/narration-raw.srt')
    require('captures/firehouse51/narration-script.json')
    evidence = json.loads((root / 'evidence/source-manifest.json').read_text())
    for item in evidence['files']:
        path = root / 'evidence/resgrid' / item['path']
        require('evidence/resgrid/' + item['path'])
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            issues.append('Recorded source evidence changed: ' + item['path'])
    for path in root.rglob('*.py'):
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError:
            issues.append('Production script does not parse: ' + path.relative_to(root).as_posix())
    return {'passed': not issues, 'primer_lessons': len(course['lessons']), 'detailed_lesson_plans': len(plans['lessons']), 'detailed_scripts': len(detailed), 'natural_primer_audio_sources': sum(lesson.get('voice') == 'Warm Lulu' for lesson in course['lessons']), 'detailed_audio_sources': len(audio_sources), 'source_evidence_files': len(evidence['files']), 'issues': issues}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=Path(__file__).resolve().parents[1] / 'sources')
    args = parser.parse_args()
    result = verify(args.sources)
    print(json.dumps(result, indent=2))
    if not result['passed']:
        raise SystemExit(1)
