"""Public-safe source-only projection of held native call captures/context.

Default verifies and scans in memory. --write-projection creates NEW projection
files only. Originals are never edited/copied over; no target, capture, app, DB,
credential/env file, canonical lesson, render or Git operation is performed.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
NATIVE=SOURCES/'captures/expansion/unit-native-call-response-20261028'
CONTEXT=SOURCES/'expansion/audits/unit-native-context-addendum-20261028'
CORE=[SOURCES/'captures/expansion/unit-native-call-core-corroboration-20261029',SOURCES/'captures/expansion/unit-native-call-completion-core-20261029']
OUT=SOURCES/'expansion/plans/unit-native-call-public-source-projection-20261029'
PRIVACY_PROOF=ROOT/'_reports/native-call-completion-scoped-privacy-20261029.json'
OMIT=object()


def require(condition,message):
    if not condition:raise ValueError(message)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()


def file_key(key):
    return '/' in key or bool(re.search(r'\.(?:css|[cm]?js|tsx?|py|json|sh|md|dylib|macho|txt|xml|ya?ml|lock)$',key,re.I)) or key in {'.gitignore','.prettierignore','.yarnrc','.watchmanconfig'}


class Projector:
    def __init__(self,device_ids=()):
        self.device_ids={x for x in device_ids if isinstance(x,str) and len(x)>5}
        self.omitted=[]
        self.fingerprint_rows=0

    def drop(self,path,reason):
        self.omitted.append({'field':path,'reason':reason})
        return OMIT

    def project(self,value,path='root'):
        if isinstance(value,dict):
            result={};fingerprints=[]
            for key,child in value.items():
                here=path+'.'+key
                normalized=re.sub(r'[^a-z0-9]','',key.casefold())
                if normalized in {'simulatorudid','udid','deviceid','deviceidentifier','identifierforvendor','idfv','serialnumber','hostid','hostname','credentialsource','credentialsources'} or ('device' in normalized and normalized.endswith('id') and normalized!='bundleid'):
                    self.drop(here,'host/device identifier or private source reference omitted');continue
                if normalized in {'command','commandline','argv'}:
                    self.drop(here,'host-local command omitted; its nonsecret source receipt hash is retained');continue
                sensitive=bool(re.search(r'password|passwd|secret|token|apikey|authorization|connectionstring|signingkey|encryptionkey',normalized))
                if sensitive and not isinstance(child,(bool,int,float,type(None))) and not file_key(key):
                    self.drop(here,'potential credential-carrying field omitted without retaining its value');continue
                if isinstance(child,str) and re.fullmatch('[a-f0-9]{64}',child) and file_key(key):
                    label=self.project(key,here+'.file')
                    if label is not OMIT:
                        fingerprints.append({'file':label,'sha256':child});self.fingerprint_rows+=1
                    continue
                projected=self.project(child,here)
                if projected is not OMIT:result[key]=projected
            if fingerprints:
                require('file_hash_rows' not in result,'Ambiguous fingerprint conversion.')
                result['file_hash_rows']=fingerprints
            return result
        if isinstance(value,list):
            result=[]
            for index,child in enumerate(value):
                projected=self.project(child,path+f'[{index}]')
                if projected is not OMIT:result.append(projected)
            return result
        if isinstance(value,str):
            if any(identifier in value for identifier in self.device_ids):
                return self.drop(path,'string containing host-sensitive simulator identifier omitted')
            roots=[(str(SOURCES)+'/', 'sources/'),('/Users/shawn/Documents/dev/Unit/','Unit/'),('/Users/shawn/Documents/dev/Core/','Core/'),('/Users/shawn/Documents/dev/Responder/','Responder/'),('/Users/shawn/Documents/dev/IC/','IC/')]
            current=value
            for original,public in roots:current=current.replace(original,public)
            if re.search(r'/(?:Users|private|var/folders|tmp)/',current):
                return self.drop(path,'nonportable host-local/private path omitted')
            return current
        return value


def collect_device_ids(value,result=None):
    result=set() if result is None else result
    if isinstance(value,dict):
        for key,child in value.items():
            normalized=re.sub(r'[^a-z0-9]','',key.casefold())
            if normalized in {'simulatorudid','udid','deviceid','deviceidentifier','identifierforvendor','idfv'} and isinstance(child,str):result.add(child)
            elif normalized not in {'credentialsources','password','secret','accesstoken','refreshtoken'}:collect_device_ids(child,result)
    elif isinstance(value,list):
        for child in value:collect_device_ids(child,result)
    return result


def build():
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import _image_dimensions
    from audit_public_repo import private_file,scan_stream
    metadata=sorted(NATIVE.glob('*.native.json'));pngs=sorted(NATIVE.glob('*.png'))
    require(len(metadata)==len(pngs)==81,'Held native1–81 input inventory changed.')
    require({int(p.name[:3])for p in metadata}==set(range(1,82)),'Missing/duplicate native capture sequence.')
    contexts=sorted(CONTEXT.rglob('*.json'));css=sorted(CONTEXT.glob('*.css'))
    require(len(contexts)==183 and len(css)==3,'Held native context inventory changed; review a new revision.')
    require(all(not private_file(p) for p in metadata+contexts+css),'Private credential/environment file is outside this projection scope.')
    native_values=[json.loads(p.read_text())for p in metadata]
    context_values=[json.loads(p.read_text())for p in contexts]
    device_ids=set()
    for obj in native_values+context_values:collect_device_ids(obj,device_ids)
    projector=Projector(device_ids)
    rows=[];public_assets=[];input_paths=set(metadata+pngs+contexts+css+[PRIVACY_PROOF])
    for path,raw in zip(metadata,native_values):
        image=SOURCES/raw['file'];require(image.parent==NATIVE and image.is_file(),'Native image reference differs from held batch.')
        require(sha(image)==raw['sha256'] and _image_dimensions(image)==(raw['width'],raw['height']),'Native image hash/dimensions changed.')
        value=projector.project(raw,path.name)
        value['curation_status']='Public source metadata projection only; no new pixel acceptance, control eligibility or video qualification.'
        rows.append({'sequence':int(path.name[:3]),'original_metadata':{'file':str(path.relative_to(SOURCES)),'sha256':sha(path),'copy_original_to_public':False},'metadata':value})
        public_assets.append({'file':str(image.relative_to(SOURCES)),'sha256':sha(image),'bytes':image.stat().st_size,'kind':'unchanged native raw PNG; diagnostics/history remain raw sources'})
    context_rows=[]
    for path,raw in zip(contexts,context_values):
        context_rows.append({'original_file':str(path.relative_to(SOURCES)),'original_sha256':sha(path),'copy_original_to_public':False,'projection':projector.project(raw,str(path.relative_to(CONTEXT)))})
    core_rows=[]
    for folder in CORE:
        manifest=folder/'manifest.json';input_paths.add(manifest)
        values=json.loads(manifest.read_text())
        require(len(values)==(3 if 'corroboration' in folder.name else 6),'Held Core corroboration inventory changed.')
        for raw in values:
            for file_key_name,hash_key_name in [('file','sha256'),('dom_file','dom_sha256')]:
                path=SOURCES/raw[file_key_name]
                require(path.parent==folder and sha(path)==raw[hash_key_name],'Core corroboration dependency changed.')
                input_paths.add(path)
                public_assets.append({'file':str(path.relative_to(SOURCES)),'sha256':sha(path),'bytes':path.stat().st_size,'kind':'unchanged Core raw JPEG' if path.suffix=='.jpg' else 'unchanged captured Core DOM'})
            core_rows.append(projector.project(raw,folder.name+'.'+raw['id']))
    for path in css:public_assets.append({'file':str(path.relative_to(SOURCES)),'sha256':sha(path),'bytes':path.stat().st_size,'kind':'retained CSS source snapshot; not a credential'})
    inputs=[{'file':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size,'copy_original_to_public':p.suffix in {'.png','.jpg','.txt','.css'}}for p in sorted(input_paths)]
    common={'schema_version':1,'source_only':True,'publication_approved':False,'canonical_or_ready_or_lesson_changes':False}
    assets={'native-captures.public.json':encoded(dict(common,kind='All81 native call raw metadata public projection',captures=rows)),
            'native-context.public.json':encoded(dict(common,kind='Native call context public projection; originals preserved',contexts=context_rows)),
            'core-corroboration.public.json':encoded(dict(common,kind='3 initial plus6 completion Core corroboration rows',screenshots=core_rows)),
            'dependency-hashes.json':encoded(dict(common,kind='Exact source/dependency map; no file-keyed digest assignments',original_inputs=inputs,public_asset_dependencies=public_assets)),
            'projection-plan.json':encoded(dict(common,kind='Bounded native-call source-retention prototype',scope={'native':81,'initial_native':60,'completion_native':21,'initial_Core':3,'completion_Core':6,'context_JSON':183,'CSS_snapshots':3},
                transformations=['File-keyed SHA256 fingerprint assignments become row lists containing file and sha256. Original hash values are preserved.','Simulator/device identifiers, host-local command lines, private source references and nonportable host paths are omitted. No private credential/env files are opened.','Selected known repository path prefixes become portable logical source paths. No screenshot pixels, AX values, operation outcomes or chronological history are invented.'],
                omitted_fields=projector.omitted,fingerprint_rows=projector.fingerprint_rows,
                installation='Prototype only; no target copy. A later reviewed install can include these projections plus exact public_asset_dependencies. Original metadata/context JSON with host-local identifiers is provenance input, not a public-copy dependency.',
                limitations=['No narrative candidate, accepted capture subset, freeze, canonical readiness, timing or media qualification.','Raw diagnostic states, failed attempts and prewritten claims remain source history; copied metadata is not independent pixel approval.','Source fingerprints describe recorded code/artifacts, not bundled binaries or a full application backup. Related source profiles/support patches remain separate dependencies.','All original raw files and dated audits/checkpoints remain unchanged.']))}
    # The approved local checker is used only on the newly constructed projection
    # and the exact proposed public asset dependencies; values are never printed.
    spec=importlib.util.spec_from_file_location('approved_known_private_checker',ROOT/'_reports/install_verified.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    known=checker.known_values()
    require(len(known)==17,'Approved local privacy-check value inventory changed.')
    findings=[]
    for name,body in assets.items():
        rules=scan_stream(io.BytesIO(body),known)
        if rules:findings.append({'file':name,'rules':rules})
    for row in public_assets:
        with (SOURCES/row['file']).open('rb')as stream:rules=scan_stream(stream,known)
        if rules:findings.append({'file':row['file'],'rules':rules})
    require(not findings,'Projection privacy check failed; no output written. File/rule summary: '+json.dumps(findings))
    for row in inputs:require(sha(ROOT/row['file'])==row['sha256'],'Original changed during projection; no output written.')
    audit=dict(common,kind='Native-call public-source projection verification',recipe_sha256=sha(__file__),original_input_count=len(inputs),native_pairs=81,Core_pairs=9,
        projected_contexts=183,public_asset_count=len(public_assets),fingerprint_rows=projector.fingerprint_rows,
        omitted_field_count=len(projector.omitted),omission_reasons=dict(Counter(x['reason']for x in projector.omitted)),
        privacy={'known_private_values_checked':17,'projection_files_checked':len(assets),'asset_dependencies_checked':len(public_assets),'findings':[]},
        outputs=[{'file':name,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}for name,body in assets.items()],
        original_inputs_rehashed_unchanged=True,target_or_original_audit_or_freeze_or_canonical_or_render_or_Git_changed=False)
    assets['projection-audit.json']=encoded(audit)
    require(not scan_stream(io.BytesIO(assets['projection-audit.json']),known),'Audit privacy failed.')
    return assets,audit


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-projection',action='store_true');args=parser.parse_args(argv)
    assets,audit=build()
    if args.write_projection:
        require(not OUT.exists(),'New-only projection; preserve earlier artifacts.')
        OUT.mkdir(parents=True)
        for name,body in assets.items():
            with (OUT/name).open('xb')as stream:stream.write(body)
    elif OUT.exists():
        require({p.name for p in OUT.iterdir()}==set(assets),'Held projection inventory differs.')
        for name,body in assets.items():require((OUT/name).read_bytes()==body,'Held projection changed: '+name)
    print(json.dumps({'passed':True,'written':args.write_projection,'native_pairs':81,'Core_pairs':9,'contexts':183,'public_assets':audit['public_asset_count'],'fingerprint_rows':audit['fingerprint_rows'],'omitted_fields':audit['omitted_field_count'],'privacy_findings':0,'target_changed':False}))


if __name__=='__main__':main()
