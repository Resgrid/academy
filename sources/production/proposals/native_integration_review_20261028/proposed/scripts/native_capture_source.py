"""Review proposal: strict Unit native source adapter, never a review generator.

This copy is isolated beneath production/proposals. It is not an adopted gate.
NativeContext is an explicit caller-supplied object: no JSON row can select roots,
declare adoption or promote an unauthenticated response hash into loaded identity.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath

import native_capture_contract as contract


class NativeContext:
    def __init__(self, roots):
        if not isinstance(roots, dict) or set(roots) != set(contract.ROOTS):
            raise ValueError('Native context requires the four explicit read roots; no runtime bundle root.')
        self.roots = {name: Path(path).resolve() for name, path in roots.items()}


def add_native_arguments(parser):
    for name in contract.ROOTS:
        parser.add_argument('--native-' + name, type=Path, help='Explicit native identity read root; all four roots required together.')


def context_from_arguments(args):
    values = {name: getattr(args, 'native_' + name, None) for name in contract.ROOTS}
    if not any(value is not None for value in values.values()):
        return None
    if not all(value is not None for value in values.values()):
        raise ValueError('Supply all four native identity read roots together.')
    return NativeContext(values)


def _need(ok, message):
    if not ok:
        raise ValueError('native source: ' + message)


def _sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _asset(root, value):
    _need(isinstance(value, dict) and set(value) == {'file', 'sha256'}, 'asset needs exact file/hash fields')
    name = value['file']; _need(isinstance(name, str) and name and '\\' not in name, 'invalid relative asset path')
    _need(not PurePosixPath(name).is_absolute() and all(p not in ('', '.', '..') for p in name.split('/')), 'asset path escapes root')
    path = (Path(root) / name).resolve()
    _need(path.is_relative_to(Path(root).resolve()) and path.is_file(), 'source asset is missing/unreadable or escapes root')
    _need(isinstance(value['sha256'], str) and bool(contract.HEX.fullmatch(value['sha256'])) and _sha(path) == value['sha256'], 'source asset hash changed')
    return path


def validate_native_source(row, asset_root, primary_app, context=None):
    """Recheck actual immutable identity assets, raw PNG and measured native fit.

    Successful source traceability still returns publishable:false. Narration,
    exact cues, actual encoded-frame review and advancing browser VIDEO playback
    remain independent gates; the native app has no fabricated browser URL.
    """
    _need(isinstance(context, NativeContext), 'explicit trusted NativeContext required; screenshot JSON cannot approve itself')
    _need(primary_app == 'Unit' and row.get('app') == 'Unit', 'explicit Unit primary identity required; no supporting app substitution')
    forbidden = {'url', 'dom_file', 'dom_sha256', 'native_context', 'native_roots', 'publishable', 'native_approved', 'integration_approved'}
    _need(not forbidden.intersection(row), 'browser/DOM, root selection and self-approval fields forbidden on native sources')
    _need(row.get('kind') == 'application_screenshot' and row.get('visible_controls', []) == [] and row.get('visible_field_text', []) == [], 'only literal native screenshots; browser icon/DOM field evidence is unsupported')
    provenance = row.get('provenance')
    _need(isinstance(provenance, dict) and set(provenance) == {'method', 'captured_at'} and provenance['method'] == 'ios_simulator_screenshot', 'retain exact native provenance, no URL or browser relabeling')
    source_root = Path(asset_root).resolve()
    _need(context.roots['assets'].is_relative_to(source_root), 'raw native screenshot/receipt root must be confined to source assets')
    image = _asset(source_root, {'file': row.get('file'), 'sha256': row.get('sha256')})
    evidence = _asset(source_root, row.get('native_evidence'))
    doc = contract.unique_json(evidence.read_text())
    _need(doc.get('app') == 'Unit', 'native contract belongs to another app')
    result = contract.propose_landscape_fit(doc, context.roots)
    _need(result.get('valid_traceability') is True and result.get('valid_fit_proposal') is True, '; '.join(result.get('issues', [])))
    capture = doc['capture']
    _need(image == _asset(context.roots['assets'], capture['image']), 'native document references a different raw screenshot')
    _need((row.get('width'), row.get('height')) == (capture['width'], capture['height']) and provenance['captured_at'] == capture['captured_at'], 'native dimensions/capture time mismatch')
    _need(row.get('visible_labels') == capture['visible_labels'] and row.get('required_labels') == capture['required_labels'], 'native literal/required observations differ from reviewed native metadata')
    fit = result['fit_proposal']; rect = fit['image_rect_pixels']
    binding = {**fit['bindings'], 'native_evidence_sha256': row['native_evidence']['sha256'], 'native_fit_sha256': fit['fit_sha256'], 'raw_pixel_scale': fit['raw_pixel_scale'], 'output_pixels_per_logical_point': fit['output_pixels_per_logical_point'], 'measured_native_dpr': fit['measured_native_dpr'], 'layout_pixels': rect}
    # All dependencies are rehashed by contract.validate. Renderer fingerprints
    # them again after assembly, including external caller-supplied identity roots.
    dependencies = [image, evidence]
    def add(reference, root_name):
        dependencies.append(_asset(context.roots[root_name], reference))
    add(doc['session']['creation_receipt'], 'assets'); add(doc['ui_ledger'], 'assets')
    add(capture['display']['receipt'], 'assets')
    for key in ('executable', 'info_plist'): add(doc['build'][key], 'app')
    for reference in doc['build']['sources']: add(reference, 'source')
    for reference in doc['build']['modules']: add(reference, 'dependencies')
    runtime = doc['build']['runtime_js']
    for reference in runtime['stream_receipts']: add(reference, 'assets')
    add(runtime['load_observation'], 'assets')
    return {'traceability_passed': True, 'publishable': False, 'native_binding': binding,
            'layout': {**rect, 'scale': fit['raw_pixel_scale'], 'raw_pixel_scale': fit['raw_pixel_scale'], 'output_pixels_per_logical_point': fit['output_pixels_per_logical_point'], 'measured_native_dpr': fit['measured_native_dpr'], 'cropped': False},
            'dependencies': list(dict.fromkeys(dependencies))}


def verify_native_frame(frame, video_hash, source_report, assembled_at):
    """Read recorded actual-frame observations, never create passed review flags."""
    expected = source_report['native_binding']
    _need(frame.get('native_binding') == expected, 'actual frame lost/staled native source/geometry/fit binding')
    _need(frame.get('reviewed_control_names', []) == [], 'native icon names are unsupported; preserve actual printed labels only')
    review = frame.get('native_frame_review')
    _need(isinstance(review, dict), 'actual hash-bound native encoded-frame review required')
    _need(review.get('passed') is True and isinstance(review.get('reviewer'), str) and review['reviewer'].strip(), 'actual native frame reviewer/pass missing')
    at = datetime.fromisoformat(str(review.get('reviewed_at', '')).replace('Z', '+00:00'))
    assembled = datetime.fromisoformat(str(assembled_at).replace('Z', '+00:00'))
    _need(at.tzinfo is not None and assembled.tzinfo is not None and assembled <= at <= datetime.now(timezone.utc), 'native frame review must follow assembly and cannot be future')
    checks = {'sha256': frame.get('sha256'), 'video_sha256': video_hash,
              'source_screenshot_sha256': expected['source_png_sha256'],
              'native_binding_sha256': contract.digest(expected),
              'visible_labels_sha256': contract.digest(frame.get('visible_labels')),
              'caption_text_sha256': contract.digest(frame.get('caption_text'))}
    _need(all(review.get(key) == value for key, value in checks.items()), 'native frame/source/master/caption/label/review digest changed')
    _need(all(review.get(key) is True for key in ['application_visible', 'raw_full_viewport_visible', 'controls_legible', 'caption_text_verified', 'no_blocking_error', 'no_private_values_visible']), 'actual full-viewport/caption/control/privacy native frame inspection incomplete')
