"""Rebuild selected primer illustrations from their editable course scenes."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lesson', action='append', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / 'sources'
    sys.path.insert(0, str(root / 'production'))
    spec = importlib.util.spec_from_file_location('academy_illustrations', root / 'production/render.py')
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    course = json.loads((root / 'course.json').read_text())
    for ident in args.lesson:
        lesson = next((item for item in course['lessons'] if item['id'] == ident), None)
        if lesson is None:
            raise SystemExit('Unknown lesson: ' + ident)
        for index, scene in enumerate(lesson['scenes']):
            target = root / 'production/descript/slides' / f'{ident}-slide-{index+1:02}.png'
            renderer.image_for(lesson, scene, index, len(lesson['scenes']), target)
        print('Updated illustrations:', ident)


if __name__ == '__main__':
    main()
