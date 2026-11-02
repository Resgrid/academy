#!/usr/bin/env python3
"""INERT PROPOSAL: genuine iOS simulator screenshot traceability, not publication.

This separate stdlib validator is NOT imported by Academy render/export/build or
its existing browser evidence gate. It executes no command, installs nothing,
contacts no service and changes no file. Valid here always means proposal-only.

A document has schema='academy.native-capture-proposal.v1', app Unit|Responder,
kind application_screenshot, session, build, ui_ledger, capture, and review.
Files in asset references are relative POSIX paths with sha256. Call validate
with explicit roots: assets (raw PNG/ledger/session receipt), app (installed .app),
source (exact managed sources), dependencies (module sources), runtime (PRIVATE
exact served JS bundle). The runtime bundle may contain execution secrets: keep
it private; retain only its digest in public evidence. Never copy it into assets.

Session binds a NEW dedicated simulator creation receipt, UUID/type/runtime/OS,
owner and time. Build binds installed Mach-O/Info.plist bytes, package.json and
Podfile.lock plus mapped screen sources, native-module sources, and actual JS
bundle bytes, with a separately supplied human build/runtime identity review.
Hashes do not establish that source built a binary or which JS was executed;
that reviewed binding is mandatory and must not be inferred from matching names.

A hash-bound normal-UI ledger records only human/XCTest/Maestro/Appium-visible
interaction kinds; no scripts/API writes/storage injection, state/keychain reset,
auto-granted permissions, launch hooks or attestations. Sensitive typing records
no value. Capture binds literal visible labels and mapped source paths, foreground
app observation, exact simctl io <UUID> screenshot --type=png <file> receipt and
capture timestamps to raw full-screen PNG bytes. No URL, DOM or browser provenance
is accepted. V1 supports only app/app-alert surfaces and printed labels: native
icons, system permission/picker surfaces and physical devices need later review.

review binds canonical current metadata (without review), labels, all asset and
identity hashes, and actual manual unmodified/full-frame/control/UI review.
This validates declared traceability, NOT pixels, source authenticity, genuine UI
execution, media readiness or permission. It cannot detect dishonest attestations.
Genuine speech, cue/screen mapping, rendered-frame QA and actual browser video
playback remain independent unchanged requirements; native evidence is not yet
accepted by those gates. Never label a simctl PNG browser_screenshot to pass them.

CLI: python native_capture_contract_v1.py document.json --assets ROOT --app ROOT
  --source ROOT --dependencies ROOT --runtime PRIVATE_ROOT
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import plistlib
import re
import struct
import uuid
import zlib

SCHEMA = 'academy.native-capture-proposal.v1'
ROOTS = ('assets', 'app', 'source', 'dependencies', 'runtime')
BUNDLES = {'Unit': 'com.resgrid.unit.development', 'Responder': 'com.wavetech.Resgrid.development'}
UI_METHODS = {'human_simulator_ui', 'xcuitest', 'maestro', 'appium_xcuitest'}
UI_KINDS = {'tap', 'scroll', 'type_text', 'sensitive_typing_redacted', 'select', 'observe_screen', 'wait_for_visible'}
FLAGS = ('normal_ui_only', 'no_hidden_writes', 'no_attestation_bypass', 'no_state_or_keychain_reset', 'no_automatic_permission_grants', 'no_launch_hooks', 'no_real_hardware_claim')
REVIEW_FLAGS = ('passed', 'application_visible', 'raw_full_screen_unmodified', 'literal_labels_reviewed', 'controls_fully_visible', 'controls_unobstructed', 'normal_ui_correspondence_reviewed', 'identity_binding_reviewed', 'no_blocking_error')
HEX = re.compile(r'[0-9a-f]{64}\Z')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def review_digest(document):
    return digest({k: v for k, v in document.items() if k != 'review'})


def build_digest(build):
    return digest({k: v for k, v in build.items() if k != 'binding_review'})


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
        self.need(not self.roots['runtime'].is_relative_to(self.roots['assets']), 'roots.runtime', 'executed JS bytes must remain outside public screenshot assets')
        self.need(not self.roots['app'].is_relative_to(self.roots['assets']), 'roots.app', 'installed app binary must remain outside public screenshot assets')

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
        build = self.obj(d['build'], 'build', 'bundle_id executable info_plist sources modules runtime_js binding_review')
        self.need(build['bundle_id'] == bundle, 'build.bundle_id', 'wrong application bundle')
        executable = self.asset(build['executable'], 'app', 'build.executable')
        with executable.open('rb') as stream: magic = stream.read(4)
        self.need(magic in (b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xca\xfe\xba\xbe', b'\xca\xfe\xba\xbf'), 'build.executable', 'requires actual Mach-O/fat executable bytes')
        info = plistlib.loads(self.asset(build['info_plist'], 'app', 'build.info_plist').read_bytes())
        self.need(info.get('CFBundleIdentifier') == bundle and info.get('DTPlatformName') == 'iphonesimulator', 'build.info_plist', 'must identify the same actual simulator application')
        self.need(info.get('CFBundleExecutable') == build['executable']['file'], 'build.executable', 'must match CFBundleExecutable')
        sources = self.records(build['sources'], 'source', 'build.sources')
        self.need({'package.json', 'ios/Podfile.lock'} <= sources, 'build.sources', 'pin app package and native dependency lock plus screen source')
        self.records(build['modules'], 'dependencies', 'build.modules')
        self.asset(build['runtime_js'], 'runtime', 'build.runtime_js')
        binding = self.obj(build['binding_review'], 'build.binding_review', 'passed reviewer reviewed_at identity_sha256 binary_source_runtime_correspondence')
        self.need(binding['passed'] is True and binding['binary_source_runtime_correspondence'] is True and binding['identity_sha256'] == build_digest(build), 'build.binding_review', 'requires actual current binary/source/module/executed-JS correspondence review')
        self.text(binding['reviewer'], 'build.binding_review.reviewer')
        bound_at = self.when(binding['reviewed_at'], 'build.binding_review.reviewed_at')
        self.need(bound_at >= created, 'build.binding_review.reviewed_at', 'identity review predates dedicated session')
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
        capture = self.obj(d['capture'], 'capture', 'method image width height started_at captured_at finished_at command exit_code output_sha256 last_action_id foreground visible_labels required_labels ui_sources')
        self.need(capture['method'] == 'ios_simulator_screenshot', 'capture.method', 'must retain genuine native provenance; browser_screenshot is forbidden here')
        started = self.when(capture['started_at'], 'capture.started_at'); at = self.when(capture['captured_at'], 'capture.captured_at'); finished = self.when(capture['finished_at'], 'capture.finished_at')
        self.need(previous <= started <= at <= finished and (finished - started).total_seconds() <= 15, 'capture', 'capture must follow its current UI ledger within the recorded screenshot invocation')
        self.need(capture['last_action_id'] == ledger['actions'][-1]['id'] and ledger['actions'][-1]['kind'] == 'observe_screen', 'capture.last_action_id', 'last action must actually observe this screen')
        self.need((at - previous).total_seconds() <= 30, 'capture', 'last visible UI observation is stale')
        self.need(capture['command'] == ['xcrun', 'simctl', 'io', session['udid'], 'screenshot', '--type=png', capture['image']['file']] and capture['exit_code'] == 0, 'capture.command', 'requires exact explicit dedicated-device simctl PNG invocation and success')
        path = self.asset(capture['image'], 'assets', 'capture.image')
        self.need(capture['output_sha256'] == capture['image']['sha256'], 'capture.output_sha256', 'raw simctl output does not match retained bytes')
        self.need((capture['width'], capture['height']) == self.png(path), 'capture.width/height', 'dimensions do not match immutable full PNG bytes')
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', type=Path)
    for name in ROOTS:
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    try:
        document = unique_json(args.document.read_text())
        result = validate(document, {name: getattr(args, name) for name in ROOTS})
    except (ValueError, OSError) as exc:
        result = {'proposal_only': True, 'valid_traceability': False, 'publishable': False, 'issues': [str(exc)]}
    print(json.dumps(result, indent=2))
    return 0 if result['valid_traceability'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
