"""Regenerate primer scripts and narration briefs from the canonical course manifest."""
import json
from pathlib import Path


def sync(sources):
    sources = Path(sources)
    course = json.loads((sources / 'course.json').read_text())
    for lesson in course['lessons']:
        ident = lesson['id']
        brief_path = sources / 'production/descript' / (ident + '-edit-brief.json')
        brief = json.loads(brief_path.read_text())
        brief.update({'title': lesson['title'], 'scenes': [{key: scene[key] for key in ('title', 'start_seconds', 'duration_seconds', 'narration') if key in scene} for scene in lesson['scenes']]})
        brief_path.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + '\n')
        lines = [lesson['title'], 'Audience: ' + lesson['role'], lesson['status'], '']
        for index, scene in enumerate(lesson['scenes']):
            lines += ['SCENE ' + str(index + 1) + ': ' + scene['title'], 'ON SCREEN: ' + ' | '.join(scene['body']), 'NARRATION: ' + scene['narration'], '']
        if lesson.get('sector_examples'):
            lines += ['ADAPT THIS WORKFLOW TO YOUR DEPARTMENT (written companion):']
            lines += [sector + ': ' + example for sector, example in lesson['sector_examples'].items()]
            lines.append('')
        (sources / 'scripts' / (ident + '.txt')).write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    sync(Path(__file__).resolve().parents[1] / 'sources')
