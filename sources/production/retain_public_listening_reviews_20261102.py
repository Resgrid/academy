"""Retain genuine approvals without exporting private Descript preview URLs.

Only provenance hashes change. Original receipts move to the ignored private
production directory. Audio, script, captions and video bytes are unchanged.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];S=R/'sources'
NAMES=('core-deployment-setup-roster','core-deployment-time-expenses')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed={};files=[]
for name in NAMES:
    p=S/'expansion/audio'/f'{name}.listening-review.json'
    data=json.loads(p.read_text());assert data['reviewer']=='User' and data['complete_natural_narration'] is True
    if 'share_url' not in data:continue
    private=S/'demo/private/listening-review-originals'/p.name;private.parent.mkdir(exist_ok=True)
    assert not private.exists();private.write_bytes(p.read_bytes())
    before=sha(p);data.pop('share_url');p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n');changed[before]=sha(p);files.append(p.relative_to(S).as_posix())
assert changed,'Private preview URL receipts were already retained; preserve the existing receipt.'
scoped=[p for p in S.rglob('*.json') if 'demo/private/' not in p.relative_to(S).as_posix() and any(n in p.relative_to(S).as_posix() for n in NAMES)]
for iteration in range(12):
    updates=0
    for p in scoped:
        text=p.read_text();updated=text
        for before,after in changed.items():updated=updated.replace(before,after)
        if updated==text:continue
        before=sha(p);p.write_text(updated);after=sha(p);changed[before]=after;updates+=1;files.append(p.relative_to(S).as_posix())
    if not updates:break
else:raise RuntimeError('Provenance hashes did not converge; do not install.')
for p in scoped:
    text=p.read_text()
    assert not any(old in text for old in changed),'Stale provenance in '+str(p)
print(json.dumps({'private_links_removed_from_public_receipts':2,'updated_provenance_files':len(set(files)),'media_bytes_changed':False,'new_listening_approval_inferred':False}))
