"""Public projection regression tests; no private fixture values are read."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
PRODUCTION=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PRODUCTION.parents[1]/'scripts'))
from audit_public_repo import scan_bytes
spec=importlib.util.spec_from_file_location('native_public_projector',PRODUCTION/'project_native_call_sources_public_20261029.py')
projector=importlib.util.module_from_spec(spec);spec.loader.exec_module(projector)


class NativeCallPublicProjectionTests(unittest.TestCase):
    def test_file_keyed_css_fingerprint_false_positive_becomes_safe_rows(self):
        digest=hashlib.sha256(b'public CSS source').hexdigest()
        original={'theme-'+'tokens.css':digest,'src/app/calls.tsx':hashlib.sha256(b'public source').hexdigest()}
        self.assertIn('possible embedded credential assignment',scan_bytes(json.dumps(original).encode()))
        result=projector.Projector().project(original)
        self.assertEqual(result['file_hash_rows'],[{'file':name,'sha256':value}for name,value in original.items()])
        self.assertEqual(scan_bytes(json.dumps(result).encode()),[])

    def test_credential_fields_are_omitted_not_relabelled_as_fingerprints(self):
        data={'api_'+'token':'SYNTHETIC_TEST_ONLY_NOT_A_SECRET','password':'SYNTHETIC_TEST_ONLY','call_id':51016,'credentials_or_map_values_logged':False}
        result=projector.Projector().project(data)
        self.assertEqual(result,{'call_id':51016,'credentials_or_map_values_logged':False})
        self.assertNotIn('file_hash_rows',result)

    def test_device_identifier_removed_from_fields_and_incidental_strings(self):
        marker='synthetic-owned-device-identifier'
        data={'provenance':{'simulator_udid':marker,'command':['capture',marker]},'note':'private host '+marker,'call_id':'51016'}
        result=projector.Projector({marker}).project(data)
        self.assertEqual(result,{'provenance':{},'call_id':'51016'})
        self.assertNotIn(marker,json.dumps(result))

    def test_private_credential_source_reference_omitted_without_traversal(self):
        result=projector.Projector().project({'credential_sources':{'opaque':object()},'source_only':True})
        self.assertEqual(result,{'source_only':True})

    def test_known_source_paths_portable_unknown_host_path_omitted(self):
        result=projector.Projector().project({'code':'/Users/shawn/Documents/dev/Unit/src/app/calls.tsx','local':'/private/tmp/host-artifact','state':'Closed'})
        self.assertEqual(result,{'code':'Unit/src/app/calls.tsx','state':'Closed'})

    def test_projection_preserves_original_objects_and_public_AX_values(self):
        data={'elements':[{'label':'FD51-2026-0008','value':'Released','hittable_observed':False}],'source_only':True}
        before=deepcopy(data)
        result=projector.Projector().project(data)
        self.assertEqual(data,before);self.assertEqual(result,before)
        self.assertIsNot(result,data)

    def test_publication_and_control_acceptance_not_inferred(self):
        data={'publication_approved':False,'reviewed_visible_labels':False,'observation_is_dom':False}
        self.assertEqual(projector.Projector().project(data),data)

    def test_new_only_writer_refuses_existing_directory(self):
        with tempfile.TemporaryDirectory()as temp:
            output=Path(temp)/'held';output.mkdir();old=output/'original.bin';old.write_bytes(b'preserve')
            audit={'public_asset_count':0,'fingerprint_rows':0,'omitted_field_count':0}
            with patch.object(projector,'OUT',output),patch.object(projector,'build',return_value=({'index.json':b'{}'},audit)):
                with self.assertRaisesRegex(ValueError,'New-only'):
                    projector.main(['--write-projection'])
            self.assertEqual(old.read_bytes(),b'preserve');self.assertEqual(len(list(output.iterdir())),1)


if __name__=='__main__':unittest.main()
