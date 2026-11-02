"""UNADOPTED private capture-stage preflight; never used by public site rebuild.

Read-only. Caller supplies current installed .app, managed source and dependency
roots explicitly. No simulator, network, shell, key, signing or bundle retrieval.
Compares retained review candidates against actual private bytes and reports
only nonsecret digests, never writes a review or promotes served bytes to loads.
"""
from pathlib import Path, PurePosixPath
import plistlib
from native_capture_public import PublicCheck, BUNDLE, REV, build_digest, need, sha, validate_mach_o_inventory, validate_public_package


MACH_O_MAGIC={b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xce\xfa\xed\xfe',b'\xfe\xed\xfa\xce',b'\xca\xfe\xba\xbe',b'\xbe\xba\xfe\xca',b'\xca\xfe\xba\xbf',b'\xbf\xba\xfe\xca'}

def installed_mach_o_inventory(installed_app):
    """Stream-hash every actual installed thin/fat Mach-O; retain no binary bytes."""
    app=Path(installed_app).resolve();need(app.is_dir(),'actual installed app root missing')
    rows=[]
    for path in sorted(app.rglob('*')):
        resolved=path.resolve()
        need(resolved.is_relative_to(app),'installed app contains an escaping symlink')
        if not path.is_file():continue
        with path.open('rb') as stream:magic=stream.read(4)
        if magic in MACH_O_MAGIC:
            rows.append({'file':path.relative_to(app).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size})
    need(rows,'actual installed Mach-O code inventory is empty')
    return rows


def inspect_private_context(package,public_assets,installed_app,source_root,dependency_root):
    """Calculate context comparisons before a reviewer authors final public receipt.

    This private-only result supplies no pixel/normal-UI/reviewer approval and is
    deliberately not imported by render/evidence/export paths.
    """
    roots={'source':Path(source_root).resolve(),'dependencies':Path(dependency_root).resolve()}
    app=Path(installed_app).resolve();public_root=Path(public_assets).resolve()
    need(app.is_dir() and all(p.is_dir() for p in roots.values()),'actual private context roots missing')
    need(not app.is_relative_to(public_root) and all(not p.is_relative_to(public_root) for p in roots.values()),'private binary/source roots must remain outside public package')
    info=(app/'Info.plist').resolve();need(info.is_relative_to(app) and info.is_file(),'actual installed Info.plist missing or escapes app')
    parsed=plistlib.loads(info.read_bytes());name=parsed.get('CFBundleExecutable')
    need(isinstance(name,str) and name==PurePosixPath(name).name and name not in {'.','..'},'installed executable name invalid')
    binary=(app/name).resolve();need(binary.is_relative_to(app) and binary.is_file(),'actual installed executable missing or escapes app')
    with binary.open('rb') as stream:
        magic=stream.read(4)
    need(magic in {b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xca\xfe\xba\xbe',b'\xbe\xba\xfe\xca'},'actual installed executable is not recognized Mach-O')
    b=package['build']
    need(b.get('mode')=='development_metro' and b.get('bundle_id')==BUNDLE and isinstance(b.get('base_source_revision'),str) and REV.fullmatch(b['base_source_revision']),'unknown private build/source identity')
    need(sha(binary)==b['installed_binary_sha256'] and sha(info)==b['installed_info_plist_sha256'],'actual installed binary/plist changed or unknown')
    need(parsed.get('CFBundleIdentifier')==b['bundle_id'] and parsed.get('DTSDKName')==b['native_sdk'],'actual installed bundle/SDK differs')
    check=PublicCheck(public_assets);manifest=check.asset(b['snapshot_manifest'],'source snapshot manifest')
    inventory=check.asset(b['installed_mach_o_inventory'],'complete installed Mach-O inventory')
    declared=validate_mach_o_inventory(inventory,b['bundle_id'])
    actual_macho=installed_mach_o_inventory(app)
    need(actual_macho==declared,'actual installed Mach-O inventory differs: changed, missing or added code file')
    comparisons=[]
    for row in manifest['snapshots']:
        root=roots[row['namespace']];actual=(root/row['original_path']).resolve()
        need(actual.is_relative_to(root) and actual.is_file(),'actual private source dependency missing or escapes explicit root')
        snapshot=check.asset(row['snapshot'],'retained public source snapshot','source')
        need(sha(actual)==row['snapshot']['sha256'] and actual.read_bytes()==snapshot.read_bytes(),'actual source/lock/module differs from reviewed public snapshot')
        comparisons.append({'namespace':row['namespace'],'original_path':row['original_path'],'sha256':sha(actual)})
    measured_receipts=[]
    ledger=check.asset(package['runtime']['served_ledger'],'actual retained served ledger')
    for association in package['runtime']['selected_streams']:
        need(association['build_identity_sha256']==build_digest(b) and association['association_method']=='reviewed_capture_context_only_not_authenticated','served observation has stale reviewed context')
        receipt=ledger['entries'][association['entry_index']]
        from native_capture_public import digest
        need(digest(receipt)==association['entry_sha256'],'actual retained served measurement changed')
        need(receipt.get('body_saved') is False and receipt.get('body_or_query_logged') is False and receipt.get('executed_or_loaded_identity_proven') is False,'runtime body retention or execution promotion forbidden')
        measured_receipts.append(association)
    return {'proposal_only':True,'publishable':False,'private_context_matches_review_candidate':True,
            'identity_sha256':build_digest(b),'installed_binary_sha256':sha(binary),'installed_info_plist_sha256':sha(info),
            'source_snapshots':comparisons,'installed_mach_o_files':actual_macho,'installed_mach_o_inventory_sha256':inventory['inventory_sha256'],'retained_snapshot_dependencies':len(check.dependencies),'stream_references':measured_receipts,
            'review_still_required':True,'review_flags_generated':False,'loaded_or_executed_identity_proven':False,
            'limitations':'Actual private bytes match this review candidate at preflight time. Foreground, normal UI, source correspondence and pixels still require the named reviewer. Served-response hashes do not establish authenticated execution or complete lazy-load coverage.'}


def validate_private_context(package,public_assets,installed_app,source_root,dependency_root):
    """Recheck final review candidate's private bytes and public bindings together."""
    report=inspect_private_context(package,public_assets,installed_app,source_root,dependency_root)
    validate_public_package(package,public_assets)
    return report
