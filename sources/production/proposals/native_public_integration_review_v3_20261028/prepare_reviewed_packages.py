#!/usr/bin/env python3
"""Bind NEW proposal-local native source packages to the genuine parent review.

Read-only by default. --write refuses an existing output directory. No source
pixels, frozen narration, drafts, original review receipts, app/runtime data,
production modules, canonical lessons or site files are changed. This source
review does not approve a video or publication.
"""
import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S = ROOT / 'sources'
sys.path.insert(0, str(HERE / 'proposed/scripts'))
import native_capture_public as n
from prepare_actual_drafts import OUT as DRAFTS, plan as draft_plan

OUT = HERE / 'actual-reviewed-20261029'
REVIEW = 'expansion/audits/unit-native-public-v3-parent-context-review-20261028.json'
REVIEW_SHA = '7f9e7669a7166b3b801acbed357873d0ed3a6c6e4b6cc5c0f76d441825c0c5ca'
ASSESSMENT_SHA = 'eb919656edc59f63c4137d81317438116add306526a6203c976796b427c11ae0'
PATCH_SHA = 'f3cf64ba6592e2610990f06b028d13dbe077321fe425bc2631a774d0d579f751'
OLD_ATTRIBUTION = "the owner's separately retained original-size review"
CORRECTED_ATTRIBUTION = ("the owner's separately retained actual display review "
                        "(1824 by 1367 tool previews of 2732 by 2048 PNGs; "
                        "no 100-percent-original-pixel inspection is asserted)")


def read(path):
    return n.unique_json(path.read_text())


def plan():
    check = n.PublicCheck(S)
    review_ref = {'file': REVIEW, 'sha256': REVIEW_SHA}
    review = check.asset(review_ref, 'genuine parent native context review')
    n.need(review['reviewed_at'] == '2026-10-29T03:55:02Z' and
           review['reviewer'] == 'Codex parent actual native source and context reviewer' and
           review['source_only'] is True and review['video_or_publication_approved'] is False and
           review['product_managed_native_source_unchanged'] is True,
           'require the exact genuine source-only named parent review')
    n.need(n.sha(HERE / 'native-public-integration-review.patch') == PATCH_SHA ==
           review['proposal_patch_sha256'], 'reviewed proposal patch changed')
    assessment = HERE / 'actual-drafts.unreviewed-fact-assessment.json'
    n.need(n.sha(assessment) == ASSESSMENT_SHA == review['actual_draft_fact_assessment_sha256'],
           'reviewed actual draft assessment changed')
    draft_files, index = draft_plan()
    for name, data in draft_files.items():
        n.need((DRAFTS / name).read_bytes() == data, 'preserve immutable draft factual bytes: ' + name)
    n.need(index['immutable_source_freeze']['sha256'] == review['source_freeze_sha256'],
           'parent review must bind the exact frozen count source')
    n.need(OLD_ATTRIBUTION in review['method'], 'expected historical attribution changed')
    method = review['method'].replace(OLD_ATTRIBUTION, CORRECTED_ATTRIBUTION)
    method += ' Parent authorized this narrower attribution correction; no new pixel inspection is claimed.'
    citation = ' Parent review receipt: ' + REVIEW + '; SHA256 ' + REVIEW_SHA + '.'
    files = {}

    def put(name, value):
        data = (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()
        files[name] = data
        return {'file': (OUT / name).relative_to(S).as_posix(),
                'sha256': hashlib.sha256(data).hexdigest()}

    outputs = []
    for entry in index['packages']:
        old = check.asset(entry['package'], 'held unreviewed actual package')
        package = copy.deepcopy(old)
        b = package['build']
        n.need(n.build_digest(b) == review['shared_build_identity_sha256'],
               'parent source review does not cover this build')
        identity = check.asset(b['installed_correspondence'], 'held unreviewed installed context')
        identity['recording_session']['product_managed_native_source_unchanged'] = True
        identity.update(reviewer=review['reviewer'], reviewed_at=review['reviewed_at'],
                        method=method, findings=review['installed_context_finding'] + citation)
        identity['binding_sha256'] = n.installed_review_digest(b, identity)
        b['installed_correspondence'] = put('receipts/' + entry['id'] + '.installed-context.json', identity)
        rt = package['runtime']
        rr = check.asset(rt['review_receipt'], 'held unreviewed served-context receipt')
        rr.update(reviewer=review['reviewer'], reviewed_at=review['reviewed_at'], method=method,
                  findings=review['served_metadata_finding'] + citation)
        rr['binding_sha256'] = n.digest({k:v for k,v in rt.items() if k != 'review_receipt'})
        rt['review_receipt'] = put('receipts/' + entry['id'] + '.served-context.json', rr)
        image_key = entry['id'].removeprefix('unit-native-20261028-')
        n.need(image_key in review['per_image_findings'], 'genuine per-image review missing')
        package['review'].update(
            reviewer=review['reviewer'], reviewed_at=review['reviewed_at'], method=method,
            checks={k: True for k in n.REVIEW_CHECKS},
            findings=review['native_source_finding'] + ' Per-image finding: ' +
                     review['per_image_findings'][image_key] + citation)
        package['review']['binding_sha256'] = n.review_digest(package)
        new_ref = put('packages/' + entry['id'] + '.reviewed.json', package)
        n.need(package['capture'] == old['capture'] and package['observations'] == old['observations']
               and package['normal_ui'] == old['normal_ui'] and package['limitations'] == old['limitations'],
               'review binding must not change raw capture, literal labels, UI or limits')
        outputs.append({'id': entry['id'], 'reviewed_package': new_ref,
                        'original_draft': entry['package'], 'raw_png': entry['image'],
                        'source_native_metadata': entry['source_native_metadata'],
                        'existing_owner_pixel_review': entry['existing_owner_pixel_review'],
                        'existing_parent_pixel_review': entry['existing_parent_pixel_review'],
                        'primary_app': 'Unit', 'source_review_only': True,
                        'video_or_publication_approved': False,
                        'reviewer': review['reviewer'], 'reviewed_at': review['reviewed_at']})
    provenance = {
        'kind': 'genuine_parent_native_source_review_binding_provenance',
        'proposal_only': True, 'publishable': False, 'production_gate_adopted': False,
        'new_pixel_inspection_claimed': False, 'video_or_publication_approved': False,
        'parent_review': review_ref,
        'historical_review_unchanged': True,
        'attribution_correction': {'historical_wording': OLD_ATTRIBUTION,
            'corrected_wording': CORRECTED_ATTRIBUTION,
            'authorization': 'Parent explicitly authorized this narrower accurate attribution in the task message; original receipt and reviewer/time remain unchanged.',
            'new_original_size_inspection_claimed': False},
        'immutable_source_freeze': index['immutable_source_freeze'],
        'unreviewed_draft_index': {'file': (DRAFTS / 'bridge-index.DRAFT.json').relative_to(S).as_posix(),
                                 'sha256': n.sha(DRAFTS / 'bridge-index.DRAFT.json')},
        'actual_draft_assessment': {'file': assessment.relative_to(S).as_posix(), 'sha256': ASSESSMENT_SHA},
        'review_application': 'Only the named review fields, explicitly attested unchanged-product-source value, dependent receipt references and canonical review digests change. All actual timestamps, raw PNGs/sidecars, literal labels, geometry, complete UI/served ledgers and source snapshots are retained.',
        'created_packages': outputs,
        'limits': review['limits'],
    }
    put('reviewed-source-index.json', provenance)
    return files, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    files, index = plan()
    if args.write:
        n.need(not OUT.exists(), 'preserve existing reviewed output; directory already exists')
        for name, data in files.items():
            path = OUT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({'proposal_only': True, 'publishable': False,
                      'reviewed_source_packages': len(index['created_packages']),
                      'video_or_publication_approved': False, 'written': args.write,
                      'output_files': len(files)}, indent=2))


if __name__ == '__main__':
    main()
