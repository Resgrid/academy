#!/usr/bin/env python3
"""INERT V2 PROPOSAL: native raw PNG + measured points/DPR + streamed JS digest.

Not imported by any existing evidence/render/export/site gate. No commands,
network, simulator access, application changes or files are written. This is a
separate proposal, never publication approval or a browser provenance adapter.

V1 identity/session/normal-UI/raw-PNG/literal-label review constraints remain.
V2 replaces retention of a possibly key-bearing development bundle with hashed
metadata receipts for complete response streams and a separate current-session
load observation. No bundle URL, query, header, body or bundle-file path is
accepted. Incremental hashing measures bytes only: it NEVER establishes execution.
Lazy entry-only coverage fails; capture-specific complete observed load-set
correspondence needs an actual separately reviewed runtime observation. This is
still an attestation limitation, not cryptographic proof of executed code.

Four read roots: assets (PNG and nonsecret receipts), app (installed .app), source
(exact managed source), dependencies (module sources). Mach-O/plist, source Git
revision, package, Pod lock and relevant source/module hashes remain mandatory.
Only the known development_metro build branch is proposed here.

Display binds actual raw pixels, measured native screen/window logical points,
DPR, orientation and a hashed measurement receipt. Only measured landscape is
supported by the OPTIONAL fit proposal. The raw PNG is never resized/replaced.
Fit reports raw-pixel scale and output-pixels-per-logical-point separately, keeps
the whole PNG outside header/captions, and enforces minimum logical UI geometry.
It returns source/metadata/build/label/fit digests for a future independently
reviewed rendered-frame binding. It renders nothing and approves no frame.

CLI: python native_capture_contract_v2.py document.json --assets ROOT --app ROOT
  --source ROOT --dependencies ROOT [--propose-fit]
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import plistlib
import re
import struct
import uuid
import zlib

SCHEMA = 'academy.native-capture-proposal.v2'
ROOTS = ('assets', 'app', 'source', 'dependencies')
BUNDLES = {'Unit': 'com.resgrid.unit.development', 'Responder': 'com.wavetech.Resgrid.development'}
UI_METHODS = {'human_simulator_ui', 'xcuitest', 'maestro', 'appium_xcuitest'}
UI_KINDS = {'tap', 'scroll', 'type_text', 'sensitive_typing_redacted', 'select', 'observe_screen', 'wait_for_visible'}
FLAGS = ('normal_ui_only', 'no_hidden_writes', 'no_attestation_bypass', 'no_state_or_keychain_reset', 'no_automatic_permission_grants', 'no_launch_hooks', 'no_real_hardware_claim')
REVIEW_FLAGS = ('passed', 'application_visible', 'raw_full_screen_unmodified', 'literal_labels_reviewed', 'controls_fully_visible', 'controls_unobstructed', 'normal_ui_correspondence_reviewed', 'identity_binding_reviewed', 'no_blocking_error')
HEX = re.compile(r'[0-9a-f]{64}\Z')
REVISION = re.compile(r'[0-9a-f]{40}\Z')
STREAM_SCHEMA = 'academy.native-js-stream-receipt.v2'
GEOMETRY_METHODS = {'xcuitest_frame_and_uiscreen_scale', 'native_screen_window_geometry_review'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def review_digest(document):
    return digest({k: v for k, v in document.items() if k != 'review'})


def build_digest(build):
    return digest({k: v for k, v in build.items() if k != 'binding_review'})


def source_identity_digest(build):
    return digest({k: build[k] for k in ('mode', 'source_git_revision', 'native_sdk', 'bundle_id', 'executable', 'info_plist', 'sources', 'modules')})


def stream_hash(chunks):
    """Measure a caller-supplied byte stream; no URL, logging, retention or IO.

    An interrupted/empty stream never returns a successful receipt. The caller
    must separately retain truthful response/load observations; hashing alone
    does not show that any app received or executed these bytes.
    """
    h, count = hashlib.sha256(), 0
    for chunk in chunks:
        if not isinstance(chunk, (bytes, bytearray, memoryview)):
            raise ValueError('stream chunks must be bytes; payload is not logged')
        count += len(chunk)
        if count > 256 * 1024 * 1024:
            raise ValueError('stream exceeds bounded proposal byte limit')
        h.update(chunk)
    if count == 0:
        raise ValueError('empty stream cannot establish a response measurement')
    return {'hash_algorithm': 'sha256', 'sha256': h.hexdigest(), 'byte_length': count,
            'stream_completed': True, 'raw_bundle_retained': False,
            'executed_or_loaded_identity_proven': False}


def unique_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON value')))


class Check:
    def __init__(self, roots, now):
        self.roots = {name: Path(roots[name]).resolve() for name in ROOTS}
        self.now = now
        for name in ('app', 'source', 'dependencies'):
            self.need(not self.roots[name].is_relative_to(self.roots['assets']), 'roots.' + name, 'installed binary and source roots must remain outside public screenshot assets')

    def need(self, condition, field, message):
        if not condition:
            raise ValueError(field + ': ' + message)

    def obj(self, value, field, keys):
        self.need(isinstance(value, dict), field, 'must be an object')
        self.need(set(value) == set(keys.split()), field, 'requires exactly fields ' + keys + '; invented DOM/URL/command fields are forbidden')
        return value

    def text(self, value, field):
        self.need(isinstance(value, str) and bool(value.strip()), field, 'must be nonempty text')
        return value

    def when(self, value, field):
        self.text(value, field)
        try:
            result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError as exc:
            raise ValueError(field + ': needs an ISO timestamp with timezone') from exc
        self.need(result.tzinfo is not None and result <= self.now, field, 'needs a timezone and must not be in the future')
        return result

    def ident(self, value, field):
        try:
            self.need(isinstance(value, str) and str(uuid.UUID(value)).lower() == value.lower(), field, 'must be an explicit UUID, never booted')
        except (ValueError, AttributeError) as exc:
            raise ValueError(field + ': must be an explicit UUID, never booted') from exc

    def asset(self, value, root, field):
        self.obj(value, field, 'file sha256')
        name = self.text(value['file'], field + '.file')
        rel = PurePosixPath(name)
        self.need(not rel.is_absolute() and '\\' not in name and all(x not in ('', '.', '..') for x in name.split('/')), field + '.file', 'must be a confined relative POSIX path')
        path = (self.roots[root] / name).resolve()
        self.need(path.is_relative_to(self.roots[root]) and path.is_file(), field + '.file', 'must exist inside its explicit read root; symlink escape is forbidden')
        self.need(isinstance(value['sha256'], str) and bool(HEX.fullmatch(value['sha256'])), field + '.sha256', 'needs lowercase SHA256')
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        self.need(actual == value['sha256'], field + '.sha256', 'asset bytes changed or hash is missing/wrong')
        return path

    def records(self, values, root, field):
        self.need(isinstance(values, list) and bool(values), field, 'requires actual hashed source files')
        seen = set()
        for index, value in enumerate(values):
            self.asset(value, root, f'{field}[{index}]')
            self.need(value['file'] not in seen, field, 'duplicate identity source')
            seen.add(value['file'])
        return seen

    def png(self, path):
        self.need(path.stat().st_size <= 128 * 1024 * 1024, 'capture.image', 'raw image unexpectedly large')
        data = path.read_bytes()
        self.need(data[:8] == b'\x89PNG\r\n\x1a\n', 'capture.image', 'requires actual PNG bytes, not renamed JPEG/illustration metadata')
        offset, chunks, size = 8, [], None
        while offset < len(data):
            self.need(offset + 12 <= len(data), 'capture.image', 'truncated PNG chunk')
            length = struct.unpack('>I', data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            end = offset + 12 + length
            self.need(end <= len(data), 'capture.image', 'truncated PNG payload')
            body = data[offset + 8:offset + 8 + length]
            crc = struct.unpack('>I', data[offset + 8 + length:end])[0]
            self.need(zlib.crc32(kind + body) & 0xffffffff == crc, 'capture.image', 'PNG chunk CRC mismatch')
            if kind == b'IHDR':
                self.need(not chunks and length == 13, 'capture.image', 'invalid PNG header')
                size = struct.unpack('>II', body[:8])
            chunks.append(kind)
            offset = end
            if kind == b'IEND':
                self.need(length == 0 and end == len(data), 'capture.image', 'trailing bytes or invalid PNG end')
                break
        self.need(size and b'IDAT' in chunks and chunks[-1] == b'IEND' and chunks.count(b'IHDR') == 1, 'capture.image', 'incomplete PNG structure')
        self.need(all(320 <= x <= 16384 for x in size), 'capture.image', 'requires legible full native-screen dimensions')
        return size

    def runtime_streams(self, value, build, session, bundle, created):
        self.obj(value, 'build.runtime_js', 'method coverage lazy entry_stream_sha256 stream_receipts load_observation')
        self.need(value['method'] == 'stream_hashed_observed_load_set' and value['coverage'] == 'complete_observed_session_load_set', 'build.runtime_js', 'entry-only/unknown execution coverage cannot bind the current captured load set')
        self.need(type(value['lazy']) is bool, 'build.runtime_js.lazy', 'retain actual lazy-loading mode')
        self.need(isinstance(value['stream_receipts'], list) and bool(value['stream_receipts']), 'build.runtime_js.stream_receipts', 'requires actual completed stream-hash receipts; no retained bundle body')
        identities, hashes, finishes, starts, receipt_files, entry_hashes, categories = [], [], [], [], set(), [], set()
        source_identity = source_identity_digest(build)
        for index, reference in enumerate(value['stream_receipts']):
            field = f'build.runtime_js.stream_receipts[{index}]'
            p = self.asset(reference, 'assets', field)
            self.need(reference['file'] not in receipt_files, field, 'duplicate stream receipt')
            receipt_files.add(reference['file'])
            receipt = unique_json(p.read_text())
            self.obj(receipt, field + '.content', 'schema session_id udid bundle_id request_id request_target_sha256 resource_category source_identity_sha256 method hash_stage hash_algorithm sha256 byte_length stream_started_at stream_finished_at response_status content_kind stream_completed raw_bundle_retained transport_client_identity executed_or_loaded_identity_proven')
            self.need(receipt['schema'] == STREAM_SCHEMA and receipt['method'] == 'development_response_stream_sha256', field, 'requires a truthful development-response stream measurement receipt')
            self.need(receipt['session_id'] == session['id'] and receipt['udid'] == session['udid'] and receipt['bundle_id'] == bundle and receipt['source_identity_sha256'] == source_identity, field, 'stream receipt has stale/wrong app/session/binary/source identity')
            self.ident(receipt['request_id'], field + '.request_id')
            self.need(receipt['request_id'] not in identities, field, 'request IDs must be unique')
            identities.append(receipt['request_id'])
            self.need(receipt['transport_client_identity'] == 'not_authenticated_by_transport' and receipt['executed_or_loaded_identity_proven'] is False, field, 'response hashing cannot authenticate a simulator client or prove loaded/executed identity')
            self.need(isinstance(receipt['request_target_sha256'], str) and bool(HEX.fullmatch(receipt['request_target_sha256'])) and receipt['resource_category'] in ('entry_bundle', 'lazy_chunk', 'script_segment'), field, 'retain only target digest and bounded script resource category, never URL/query bytes')
            categories.add(receipt['resource_category'])
            self.need(receipt['hash_stage'] == 'decoded_response_body' and receipt['hash_algorithm'] == 'sha256' and isinstance(receipt['sha256'], str) and bool(HEX.fullmatch(receipt['sha256'])), field, 'missing/wrong stream SHA256 or byte-stage measurement')
            self.need(type(receipt['byte_length']) is int and 0 < receipt['byte_length'] <= 256 * 1024 * 1024, field, 'requires actual positive bounded stream byte count')
            self.need(receipt['response_status'] == 200 and type(receipt['response_status']) is int and receipt['stream_completed'] is True and receipt['raw_bundle_retained'] is False, field, 'response must complete successfully without retaining key-bearing bundle bytes')
            self.need(receipt['content_kind'] in ('javascript_source', 'hermes_bytecode'), field, 'record actual response content kind; unknown build/runtime format is unsupported')
            start = self.when(receipt['stream_started_at'], field + '.stream_started_at')
            end = self.when(receipt['stream_finished_at'], field + '.stream_finished_at')
            self.need(created <= start <= end, field, 'stream chronology predates session or is reordered')
            starts.append(start); finishes.append(end); hashes.append(receipt['sha256'])
            if receipt['resource_category'] == 'entry_bundle':
                entry_hashes.append(receipt['sha256'])
        self.need(value['entry_stream_sha256'] in entry_hashes, 'build.runtime_js.entry_stream_sha256', 'entry stream hash missing from measured entry load set')
        self.need(not value['lazy'] or bool(categories & {'lazy_chunk', 'script_segment'}), 'build.runtime_js', 'lazy entry-only hash cannot establish the required bounded load-set coverage')
        observed = unique_json(self.asset(value['load_observation'], 'assets', 'build.runtime_js.load_observation').read_text())
        self.obj(observed, 'load_observation', 'session_id udid bundle_id source_identity_sha256 method observed_through load_window_started_at request_ids entry_only all_observed_loads_included foreground_app_observed')
        self.need(observed['session_id'] == session['id'] and observed['udid'] == session['udid'] and observed['bundle_id'] == bundle and observed['source_identity_sha256'] == source_identity, 'load_observation', 'wrong/stale binary/source/session load observation')
        self.need(observed['method'] == 'native_runtime_and_metro_load_review' and observed['entry_only'] is False and observed['all_observed_loads_included'] is True and observed['foreground_app_observed'] is True, 'load_observation', 'a served entry bundle alone does not establish captured app load/execution correspondence, especially with lazy=true')
        self.need(isinstance(observed['request_ids'], list) and len(observed['request_ids']) == len(identities) and set(observed['request_ids']) == set(identities), 'load_observation.request_ids', 'all observed entry/lazy chunk loads must bind to exact measured stream receipts')
        through = self.when(observed['observed_through'], 'load_observation.observed_through')
        began = self.when(observed['load_window_started_at'], 'load_observation.load_window_started_at')
        self.need(created <= began <= min(starts) and max(finishes) <= through, 'load_observation', 'observation window does not contain actual completed measured streams')
        return through

    def display(self, display, capture, session, previous, at):
        self.obj(display, 'capture.display', 'orientation dpr screen_points app_viewport_points method measured_at receipt')
        self.need(display['orientation'] in ('landscape_left', 'landscape_right', 'portrait', 'portrait_upside_down'), 'capture.display.orientation', 'requires actually measured native orientation; unknown is not landscape')
        self.need(type(display['dpr']) in (int, float) and math.isfinite(display['dpr']) and display['dpr'] in (1, 2, 3), 'capture.display.dpr', 'requires explicit measured native DPR, never a raw-pixel scale substitute')
        self.obj(display['screen_points'], 'capture.display.screen_points', 'width height')
        self.obj(display['app_viewport_points'], 'capture.display.app_viewport_points', 'x y width height')
        screen, viewport, dpr = display['screen_points'], display['app_viewport_points'], display['dpr']
        for field, values in [('screen_points', screen), ('app_viewport_points', viewport)]:
            self.need(all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in values.values()) and values['width'] > 0 and values['height'] > 0, 'capture.display.' + field, 'requires finite nonnegative native point geometry with positive extent')
        self.need(abs(screen['width'] * dpr - capture['width']) < 0.01 and abs(screen['height'] * dpr - capture['height']) < 0.01, 'capture.display', 'DPR/logical screen dimensions disagree with measured immutable raw PNG pixels')
        self.need(viewport['x'] + viewport['width'] <= screen['width'] and viewport['y'] + viewport['height'] <= screen['height'], 'capture.display.app_viewport_points', 'logical app viewport lies outside full native screen')
        landscape = display['orientation'].startswith('landscape')
        self.need((screen['width'] > screen['height']) == landscape and (viewport['width'] > viewport['height']) == landscape, 'capture.display.orientation', 'native orientation and actual point/pixel axes disagree')
        self.need(display['method'] in GEOMETRY_METHODS, 'capture.display.method', 'requires native screen/window measurement; browser/guessed DPR is forbidden')
        measured = self.when(display['measured_at'], 'capture.display.measured_at')
        self.need(previous <= measured <= at and (at - measured).total_seconds() <= 5, 'capture.display.measured_at', 'native geometry observation is stale or predates current UI')
        receipt = unique_json(self.asset(display['receipt'], 'assets', 'capture.display.receipt').read_text())
        self.obj(receipt, 'geometry_receipt', 'session_id udid method measured_at orientation dpr screen_points app_viewport_points pixel_width pixel_height')
        self.need(receipt['session_id'] == session['id'] and receipt['udid'] == session['udid'] and receipt['pixel_width'] == capture['width'] and receipt['pixel_height'] == capture['height'], 'geometry_receipt', 'wrong native session/device/raw pixel geometry')
        self.need(all(receipt[k] == display[k] for k in ('method', 'measured_at', 'orientation', 'dpr', 'screen_points', 'app_viewport_points')), 'geometry_receipt', 'declared DPR/viewport differs from actual hash-bound native measurement')

    def run(self, d):
        self.obj(d, 'document', 'schema app kind session build ui_ledger capture review')
        self.need(d['schema'] == SCHEMA, 'schema', 'unsupported proposal version')
        self.need(d['app'] in BUNDLES and d['kind'] == 'application_screenshot', 'kind/app', 'only actual Unit/Responder native application screenshots; illustrated substitutes are forbidden')
        bundle = BUNDLES[d['app']]
        session = self.obj(d['session'], 'session', 'id udid device_type runtime os_version created_at owner dedicated user_session_reused creation_receipt')
        self.ident(session['id'], 'session.id'); self.ident(session['udid'], 'session.udid')
        self.need(session['owner'] == 'academy_training' and session['dedicated'] is True and session['user_session_reused'] is False, 'session', 'requires our own newly created dedicated training simulator; never existing user apps')
        self.need(str(session['device_type']).startswith('com.apple.CoreSimulator.SimDeviceType.') and str(session['runtime']).startswith('com.apple.CoreSimulator.SimRuntime.iOS-'), 'session', 'requires recorded simulator type/runtime')
        self.need(re.fullmatch(r'\d+\.\d+(?:\.\d+)?', str(session['os_version'])) is not None, 'session.os_version', 'requires actual OS version')
        self.need(session['runtime'] == 'com.apple.CoreSimulator.SimRuntime.iOS-' + session['os_version'].replace('.', '-'), 'session.runtime', 'runtime and actual OS version must agree')
        created = self.when(session['created_at'], 'session.created_at')
        receipt = unique_json(self.asset(session['creation_receipt'], 'assets', 'session.creation_receipt').read_text())
        self.obj(receipt, 'creation_receipt', 'session_id udid created_at command exit_code')
        self.need(receipt['session_id'] == session['id'] and receipt['udid'] == session['udid'] and receipt['created_at'] == session['created_at'] and receipt['exit_code'] == 0, 'creation_receipt', 'must match actual dedicated session creation')
        cmd = receipt['command']
        self.need(isinstance(cmd, list) and len(cmd) == 6 and cmd[:3] == ['xcrun', 'simctl', 'create'] and str(cmd[3]).startswith('Academy Training ') and cmd[4:6] == [session['device_type'], session['runtime']], 'creation_receipt.command', 'requires exact retained normal simulator creation invocation')
        build = self.obj(d['build'], 'build', 'mode source_git_revision native_sdk bundle_id executable info_plist sources modules runtime_js binding_review')
        self.need(build['mode'] == 'development_metro', 'build.mode', 'unknown build branch; release/embedded/unspecified builds need separate reviewed contract')
        self.need(isinstance(build['source_git_revision'], str) and bool(REVISION.fullmatch(build['source_git_revision'])), 'build.source_git_revision', 'pin exact base source Git revision in addition to current managed source/lock hashes')
        self.need(isinstance(build['native_sdk'], str) and bool(re.fullmatch(r'iphonesimulator\d+\.\d+', build['native_sdk'])), 'build.native_sdk', 'requires actual native SDK identity')
        self.need(build['bundle_id'] == bundle, 'build.bundle_id', 'wrong application bundle')
        executable = self.asset(build['executable'], 'app', 'build.executable')
        with executable.open('rb') as stream: magic = stream.read(4)
        self.need(magic in (b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xca\xfe\xba\xbe', b'\xca\xfe\xba\xbf'), 'build.executable', 'requires actual Mach-O/fat executable bytes')
        info = plistlib.loads(self.asset(build['info_plist'], 'app', 'build.info_plist').read_bytes())
        self.need(info.get('CFBundleIdentifier') == bundle and info.get('DTPlatformName') == 'iphonesimulator', 'build.info_plist', 'must identify the same actual simulator application')
        self.need(info.get('CFBundleExecutable') == build['executable']['file'], 'build.executable', 'must match CFBundleExecutable')
        self.need(info.get('DTSDKName') == build['native_sdk'], 'build.native_sdk', 'declared SDK differs from actual installed Info.plist')
        sources = self.records(build['sources'], 'source', 'build.sources')
        self.need({'package.json', 'ios/Podfile.lock'} <= sources, 'build.sources', 'pin app package and native dependency lock plus screen source')
        self.records(build['modules'], 'dependencies', 'build.modules')
        observed_through = self.runtime_streams(build['runtime_js'], build, session, bundle, created)
        binding = self.obj(build['binding_review'], 'build.binding_review', 'passed reviewer reviewed_at identity_sha256 binary_source_runtime_correspondence known_build_reviewed stream_load_correspondence_reviewed')
        self.need(binding['passed'] is True and binding['binary_source_runtime_correspondence'] is True and binding['known_build_reviewed'] is True and binding['stream_load_correspondence_reviewed'] is True and binding['identity_sha256'] == build_digest(build), 'build.binding_review', 'requires actual current binary/source/module/observed-stream correspondence review; hashing alone is insufficient')
        self.text(binding['reviewer'], 'build.binding_review.reviewer')
        bound_at = self.when(binding['reviewed_at'], 'build.binding_review.reviewed_at')
        self.need(bound_at >= observed_through >= created, 'build.binding_review.reviewed_at', 'identity review predates actual current load-set observation')
        ledger = unique_json(self.asset(d['ui_ledger'], 'assets', 'ui_ledger').read_text())
        self.obj(ledger, 'ui_ledger.content', 'session_id udid bundle_id policy actions')
        self.need(ledger['session_id'] == session['id'] and ledger['udid'] == session['udid'] and ledger['bundle_id'] == bundle, 'ui_ledger', 'wrong simulator/session/app')
        policy = self.obj(ledger['policy'], 'ui_ledger.policy', ' '.join(FLAGS))
        self.need(all(policy[x] is True for x in FLAGS), 'ui_ledger.policy', 'ordinary UI only; no hidden writes, permission/attestation bypass, reset, launch hooks or hardware claim')
        self.need(isinstance(ledger['actions'], list) and bool(ledger['actions']), 'ui_ledger.actions', 'requires genuine recorded normal UI actions')
        previous, action_ids = created, set()
        for i, action in enumerate(ledger['actions']):
            field = f'ui_ledger.actions[{i}]'
            self.obj(action, field, 'id at method kind target normal_ui typed_value_recorded')
            self.need(action['method'] in UI_METHODS and action['kind'] in UI_KINDS and action['normal_ui'] is True, field, 'only supported ordinary visible UI interaction, no injected API/script/storage action')
            self.text(action['target'], field + '.target'); self.text(action['id'], field + '.id')
            self.need(action['id'] not in action_ids, field, 'action IDs must be unique')
            action_ids.add(action['id'])
            self.need(action['typed_value_recorded'] is False, field, 'never store typed credential values; target is a control label only')
            current = self.when(action['at'], field + '.at')
            self.need(current >= previous, field + '.at', 'UI action chronology is stale or reordered')
            previous = current
        capture = self.obj(d['capture'], 'capture', 'method image width height display started_at captured_at finished_at command exit_code output_sha256 last_action_id foreground visible_labels required_labels ui_sources')
        self.need(capture['method'] == 'ios_simulator_screenshot', 'capture.method', 'must retain genuine native provenance; browser_screenshot is forbidden here')
        started = self.when(capture['started_at'], 'capture.started_at'); at = self.when(capture['captured_at'], 'capture.captured_at'); finished = self.when(capture['finished_at'], 'capture.finished_at')
        self.need(previous <= started <= at <= finished and (finished - started).total_seconds() <= 15, 'capture', 'capture must follow its current UI ledger within the recorded screenshot invocation')
        self.need(observed_through <= started and (at - observed_through).total_seconds() <= 5, 'build.runtime_js', 'load-set observation must cover the current capture, not an old startup or entry-only measurement')
        self.need(capture['last_action_id'] == ledger['actions'][-1]['id'] and ledger['actions'][-1]['kind'] == 'observe_screen', 'capture.last_action_id', 'last action must actually observe this screen')
        self.need((at - previous).total_seconds() <= 30, 'capture', 'last visible UI observation is stale')
        self.need(capture['command'] == ['xcrun', 'simctl', 'io', session['udid'], 'screenshot', '--type=png', capture['image']['file']] and capture['exit_code'] == 0, 'capture.command', 'requires exact explicit dedicated-device simctl PNG invocation and success')
        path = self.asset(capture['image'], 'assets', 'capture.image')
        self.need(capture['output_sha256'] == capture['image']['sha256'], 'capture.output_sha256', 'raw simctl output does not match retained bytes')
        self.need((capture['width'], capture['height']) == self.png(path), 'capture.width/height', 'dimensions do not match immutable full PNG bytes')
        self.display(capture['display'], capture, session, previous, at)
        fg = self.obj(capture['foreground'], 'capture.foreground', 'bundle_id state surface method checked_at')
        self.need(fg['bundle_id'] == bundle and fg['state'] == 'running_foreground' and fg['surface'] in ('app', 'app_alert') and fg['method'] in UI_METHODS, 'capture.foreground', 'requires actual app/app-alert foreground observation, not a browser or unrelated system UI')
        checked = self.when(fg['checked_at'], 'capture.foreground.checked_at')
        self.need(previous <= checked <= at and (at - checked).total_seconds() <= 5, 'capture.foreground.checked_at', 'foreground observation must immediately precede capture')
        for name in ('visible_labels', 'required_labels', 'ui_sources'):
            value = capture[name]
            self.need(isinstance(value, list) and bool(value) and all(isinstance(x, str) and x.strip() for x in value) and len(set(value)) == len(value), 'capture.' + name, 'requires unique nonempty actual literals/source paths')
        self.need(set(capture['required_labels']) <= set(capture['visible_labels']), 'capture.required_labels', 'spoken control is not visibly reviewed in this exact screen')
        self.need(set(capture['ui_sources']) <= sources, 'capture.ui_sources', 'mapped screen source is missing from exact source identity')
        review = self.obj(d['review'], 'review', 'reviewer reviewed_at metadata_sha256 ' + ' '.join(REVIEW_FLAGS))
        self.text(review['reviewer'], 'review.reviewer')
        self.need(self.when(review['reviewed_at'], 'review.reviewed_at') >= max(finished, bound_at), 'review.reviewed_at', 'actual review must follow capture and identity review')
        self.need(review['metadata_sha256'] == review_digest(d) and all(review[x] is True for x in REVIEW_FLAGS), 'review', 'requires current actual pixel/identity/normal-UI review bound to all exact metadata and bytes')


def validate(document, roots, now=None):
    """Read declared files only; return actionable failure and never publishable."""
    issues = []
    try:
        Check(roots, now or datetime.now(timezone.utc)).run(document)
    except (ValueError, KeyError, TypeError, OSError, plistlib.InvalidFileException, struct.error) as exc:
        issues.append(str(exc))
    return {'schema': SCHEMA, 'proposal_only': True, 'valid_traceability': not issues, 'publishable': False, 'pixel_authenticity_proven': False, 'issues': issues}


def propose_landscape_fit(document, roots, now=None):
    """Return an inert full-PNG layout recipe, never an image or frame approval."""
    result = validate(document, roots, now)
    result['fit_proposal'] = None
    if not result['valid_traceability']:
        return result
    try:
        capture = document['capture']
        display = capture['display']
        if not display['orientation'].startswith('landscape'):
            raise ValueError('fit.orientation: measured portrait/unknown geometry is unsupported; never rotate or invent a landscape capture')
        viewport = display['app_viewport_points']
        if viewport['width'] < 960 or viewport['height'] < 540:
            raise ValueError('fit.logical_viewport: requires at least960x540 native logical UI points')
        width, height, dpr = capture['width'], capture['height'], display['dpr']
        canvas_width, canvas_height, header, captions = 1920, 1080, 48, 120
        available_height = canvas_height - header - captions
        raw_scale = min(canvas_width / width, available_height / height)
        logical_scale = raw_scale * dpr
        fitted_width, fitted_height = round(width * raw_scale), round(height * raw_scale)
        if not 0.75 <= logical_scale <= 2.0 or viewport['width'] * logical_scale < 1100 or viewport['height'] * logical_scale < 650:
            raise ValueError('fit.readability: logical UI would be too small or excessively enlarged; actual landscape/text recapture and review required')
        fit = {
            'kind': 'native_landscape_full_png_fit_proposal', 'proposal_only': True,
            'canvas_pixels': {'width': canvas_width, 'height': canvas_height, 'header': header, 'captions': captions},
            'source_pixel_dimensions': {'width': width, 'height': height},
            'source_logical_screen_points': display['screen_points'],
            'source_logical_app_viewport_points': viewport, 'measured_native_dpr': dpr,
            'raw_pixel_scale': raw_scale, 'output_pixels_per_logical_point': logical_scale,
            'image_rect_pixels': {'x': (canvas_width - fitted_width) // 2,
                                  'y': header + (available_height - fitted_height) // 2,
                                  'width': fitted_width, 'height': fitted_height},
            'cropped': False, 'source_png_unchanged': True,
            'minimum_logical_point_scale': 0.75,
            'minimum_fitted_app_pixels': {'width': 1100, 'height': 650},
            'rendered_frame_created': False, 'rendered_frame_reviewed': False,
            'bindings': {'source_png_sha256': capture['image']['sha256'],
                         'native_metadata_sha256': review_digest(document),
                         'native_pixel_review_sha256': digest(document['review']),
                         'geometry_receipt_sha256': display['receipt']['sha256'],
                         'build_identity_sha256': build_digest(document['build']),
                         'source_identity_sha256': source_identity_digest(document['build']),
                         'literal_labels_sha256': digest(capture['visible_labels']),
                         'required_labels_sha256': digest(capture['required_labels'])},
            'adoption_requirement': 'Future rendered-frame proof must bind this exact fit digest, unchanged PNG, current master/frame hashes and actual literal-label/caption/legibility review. Existing gates remain unchanged.',
        }
        fit['fit_sha256'] = digest(fit)
        result['fit_proposal'] = fit
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        result['issues'].append(str(exc))
    result['valid_fit_proposal'] = bool(result['fit_proposal']) and not result['issues']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', type=Path)
    for name in ROOTS:
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--propose-fit', action='store_true', help='Propose full-frame landscape geometry only; create no render or public evidence.')
    args = parser.parse_args()
    try:
        document = unique_json(args.document.read_text())
        validator = propose_landscape_fit if args.propose_fit else validate
        result = validator(document, {name: getattr(args, name) for name in ROOTS})
    except (ValueError, OSError) as exc:
        result = {'proposal_only': True, 'valid_traceability': False, 'publishable': False, 'issues': [str(exc)]}
    print(json.dumps(result, indent=2))
    return 0 if result['valid_traceability'] and (not args.propose_fit or result.get('valid_fit_proposal')) else 1


if __name__ == '__main__':
    raise SystemExit(main())
