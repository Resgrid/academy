"""Correct source manifest dimensions from unchanged image headers; preserve prior metadata."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

S=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(S.parent/'scripts'))
from verify_capture_evidence import _image_dimensions


def main():
    for folder in ['core-records-saved-reports-source-20261102-v2',
                   'core-records-export-templates-source-20261102',
                   'core-workforce-compensation-default-approval-source-20261102']:
        directory=S/'expansion/plans'/folder
        path=directory/'captures.reviewed.json'
        before=path.read_bytes();value=json.loads(before);changed=[]
        for row in value['screenshots']:
            original=S/row['file']
            assert hashlib.sha256(original.read_bytes()).hexdigest()==row['sha256']
            width,height=_image_dimensions(original)
            if (width,height)!=(row['width'],row['height']):
                old={'width':row['width'],'height':row['height']}
                row.setdefault('css_viewport',old)
                row.update(width=width,height=height)
                changed.append({'id':row['id'],'retained_css_viewport':old,'returned_raster':{'width':width,'height':height},'unchanged_image_sha256':row['sha256']})
        assert changed,'No correction needed; preserve the existing receipt.'
        backup=directory/'captures.before-raster-metadata-correction.json'
        assert not backup.exists()
        backup.write_bytes(before)
        path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
        (directory/'raster-metadata-correction.json').write_text(json.dumps({'corrected_at':datetime.now(timezone.utc).isoformat(),
            'reason':'The browser returned some raster images at different dimensions from the DOM CSS viewport. Strict renderer preflight rejected the mismatch. Dimensions now come from the actual unchanged PNG/JPEG headers.',
            'original_manifest_sha256':hashlib.sha256(before).hexdigest(),'corrected_manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'screenshot_pixels_changed':False,'narration_changed':False,'corrections':changed},indent=2)+'\n')
        print(folder,len(changed),'metadata corrections; image hashes unchanged')


if __name__=='__main__':main()
