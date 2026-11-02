"""Capture recorders must preserve reviewed snapshots and reject incompatible folders."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which('node'), 'Optional capture-recorder checks require Node.js')
class CaptureManifestGuardTests(unittest.TestCase):
    def run_dom_cases(self, cases):
        """Execute the recorder's actual evaluate callback against a synthetic DOM.

        This is an offline contract fixture, not browser capture or visual proof.
        """
        app_url = json.dumps((ROOT / 'sources/production/capture_application.mjs').as_uri())
        core_url = json.dumps((ROOT / 'sources/production/capture-evidence.mjs').as_uri())
        script = r'''
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
const {captureApplication} = await import(APP_URL);
const {redact} = await import(CORE_URL);
const root = await fs.mkdtemp(path.join(os.tmpdir(), 'academy-capture-dom-test-'));
let completed = 0;
function element(options = {}) {
  const box = {x:20,y:20,width:180,height:24,...options.box};
  const attributes = {...options.attributes};
  const item = {
    tagName:'INPUT',type:'text',value:'',name:'',autocomplete:'',placeholder:'',
    checked:false,readOnly:false,parentElement:null,children:[],childNodes:[],innerText:'',textContent:'',
    style:{display:'block',visibility:'visible',opacity:'1',overflowX:'visible',overflowY:'visible',...options.style},
    getBoundingClientRect:()=>({...box,left:box.x,top:box.y,right:box.x+box.width,bottom:box.y+box.height}),
    getAttribute(name){return attributes[name] ?? (name==='placeholder' ? this.placeholder : null);},
    ...options
  };
  item.style={display:'block',visibility:'visible',opacity:'1',overflowX:'visible',overflowY:'visible',...options.style};
  return item;
}
async function check(id, inputs, reject = false, snapshot = 'Synthetic DOM fixture only', environment = {}) {
  const viewport=environment.viewport ?? element({tagName:'HTML',box:{x:0,y:0,width:320,height:180}});
  viewport.clientWidth=320;viewport.clientHeight=180;
  for (const input of inputs) if (!input.parentElement) input.parentElement=viewport;
  globalThis.document={
    documentElement:viewport,
    body:environment.body,
    querySelectorAll(selector){
      if (selector==='input') return inputs.filter(e=>e.tagName==='INPUT');
      if (selector==='body *') return inputs;
      if (selector==='input,textarea') return inputs.filter(e=>['INPUT','TEXTAREA'].includes(e.tagName));
      if (selector==='select') return inputs.filter(e=>e.tagName==='SELECT');
      if (selector==='button,[role="button"]') return [];
      throw new Error('Unexpected DOM selector: '+selector);
    }
  };
  globalThis.getComputedStyle=e=>e.style;
  const calls={snapshot:0,screenshot:0,url:0};
  const tab={
    playwright:{evaluate:async callback=>callback(),domSnapshot:async()=>{calls.snapshot++;return snapshot;}},
    screenshot:async()=>{calls.screenshot++;return Buffer.from([255,216,255,217]);},
    url:async()=>{calls.url++;return 'http://localhost/fixture';}
  };
  const directory=path.join(root,id);
  const capture=()=>captureApplication(tab,{app:'Core',directory,relativeDirectory:id,id:'synthetic-fixture'},
    {redact,jpegSize:()=>({width:320,height:180})});
  if (reject) {
    await assert.rejects(capture,/visible credential-filled form/,id);
    assert.deepEqual(calls,{snapshot:0,screenshot:0,url:0},id+' rejected before any capture');
    await assert.rejects(fs.access(directory),{code:'ENOENT'},id+' wrote no assets');
  } else {
    const result=await capture();
    assert.deepEqual(calls,{snapshot:1,screenshot:1,url:1},id);
    assert.equal(result.row.eligible_for_lesson,false,id);
    assert.equal(result.row.visual_review,'pending_actual_image_review',id);
    completed++;
    return {row:result.row,directory};
  }
  completed++;
}
try {
CASES
  console.log(JSON.stringify({completed}));
} finally { await fs.rm(root,{recursive:true,force:true}); }
'''.replace('APP_URL', app_url).replace('CORE_URL', core_url).replace('CASES', cases)
        result = subprocess.run([shutil.which('node'), '--input-type=module', '-e', script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)['completed']

    def test_visible_text_credentials_reject_before_any_capture_or_write(self):
        self.assertEqual(self.run_dom_cases(r'''
  const examples=[
    {type:'password',value:'synthetic fixture only'},
    {name:'Username',value:'fixture-user'},
    {type:'email',name:'Email',value:'fixture@example.invalid'},
    {type:'email',value:'fixture@example.invalid'},
    {placeholder:'Email address',value:'fixture@example.invalid'},
    {type:'search',autocomplete:'username',value:'fixture-user'},
    {autocomplete:'current-password',value:'synthetic fixture only'},
    {type:'password',value:'synthetic fixture only',readOnly:true,attributes:{'aria-hidden':'true'}}
  ];
  for(let i=0;i<examples.length;i++) await check('credential-'+i,[element(examples[i])],true);
'''), 8)

    def test_boolean_password_reset_setting_and_nontext_controls_are_not_credentials(self):
        self.assertEqual(self.run_dom_cases(r'''
  for(const checked of [false,true]) {
    await check('password-reset-setting-'+checked,[
      element({type:'checkbox',name:'RequirePasswordResetViaEmail',value:'true',checked,box:{x:20,y:20,width:13,height:13}}),
      element({type:'hidden',name:'RequirePasswordResetViaEmail',value:'false',box:{width:0,height:0}})
    ]);
  }
  for(const type of ['radio','hidden','button','submit','reset','file','range','color','image']) {
    await check('nontext-'+type,[element({type,name:'UsernamePasswordEmail',value:'synthetic fixture only'})]);
  }
'''), 11)

    def test_partially_painted_passwords_still_reject(self):
        self.assertEqual(self.run_dom_cases(r'''
  for(const [index,box] of [{x:-10,width:20},{y:-10,height:20},{x:310,width:20},{y:170,height:20}].entries()) {
    await check('viewport-intersection-'+index,[element({type:'password',value:'synthetic fixture only',box})],true);
  }
  const clip=element({tagName:'DIV',box:{x:10,y:10,width:20,height:20},style:{overflowX:'hidden',overflowY:'hidden'}});
  await check('ancestor-partial-intersection',[element({type:'password',value:'synthetic fixture only',parentElement:clip,box:{x:20,y:20,width:40,height:24}})],true);
'''), 5)

    def test_unpainted_passwords_do_not_block_capture(self):
        self.assertEqual(self.run_dom_cases(r'''
  const examples=[
    {box:{x:-200,width:100}}, {box:{x:400}}, {box:{y:-100}}, {box:{y:200}},
    {box:{width:0,height:0}}, {style:{display:'none'}},
    {style:{visibility:'hidden'}}, {style:{opacity:'0'}},
    {parentElement:element({tagName:'DIV',style:{opacity:'0'}})},
    {parentElement:element({tagName:'DIV',box:{x:250,y:120,width:20,height:20},style:{overflowX:'hidden',overflowY:'hidden'}})}
  ];
  for(let i=0;i<examples.length;i++) {
    const result=await check('not-painted-'+i,[element({type:'password',value:'synthetic fixture only',...examples[i]})]);
    assert.deepEqual(result.row.visible_field_text,[],'hidden credential not retained');
  }
'''), 10)

    def test_accepted_fields_and_dom_still_redact_and_require_image_review(self):
        self.assertEqual(self.run_dom_cases(r'''
  const query='access_'+'token';
  const raw='http://localhost/fixture?'+query+'=synthetic-fixture-only';
  const result=await check('redacted-field',[element({tagName:'TEXTAREA',name:'Note',value:raw})],false,raw);
  assert.equal(result.row.visible_field_text[0].text,'http://localhost/fixture?'+query+'=[REDACTED]');
  assert(!JSON.stringify(result.row).includes('synthetic-fixture-only'));
  assert.equal(await fs.readFile(path.join(result.directory,'synthetic-fixture.dom.txt'),'utf8'),
    'http://localhost/fixture?'+query+'=[REDACTED]');
  assert.equal(result.row.eligible_for_lesson,false);
  assert.equal(result.row.visual_review,'pending_actual_image_review');
'''), 1)

    def test_scrolled_html_body_overflow_keeps_visible_fields_and_rejects_credentials(self):
        self.assertEqual(self.run_dom_cases(r'''
  const viewport=element({tagName:'HTML',box:{x:0,y:-600,width:320,height:180}});
  const body=element({tagName:'BODY',parentElement:viewport,box:{x:0,y:-600,width:320,height:180},
    style:{overflowX:'hidden',overflowY:'auto'}});
  const environment={viewport,body};
  const field=element({name:'NumberPattern',value:'{PREFIX}-{YYYY}-{SEQ}',parentElement:body});
  const result=await check('scrolled-body-field',[field],false,'Synthetic viewport-overflow fixture',environment);
  assert.equal(result.row.visible_field_text[0].text,'{PREFIX}-{YYYY}-{SEQ}');
  await check('scrolled-body-password',[element({type:'password',value:'synthetic fixture only',parentElement:body})],true,'',environment);
  body.style.contain='paint';
  const contained=await check('contained-body-field',[field],false,'',environment);
  assert.deepEqual(contained.row.visible_field_text,[],'contained BODY keeps its actual clipping box');
  body.style.contain='none';viewport.style.overflowX='hidden';viewport.style.overflowY='auto';
  const unpropagated=await check('nonpropagated-body-field',[field],false,'',environment);
  assert.deepEqual(unpropagated.row.visible_field_text,[],'nonpropagated BODY remains an ancestor clip');
'''), 4)

    def test_closed_select_records_selected_label_without_internal_or_unselected_values(self):
        self.assertEqual(self.run_dom_cases(r'''
  const selected=element({tagName:'SELECT',value:'0',selectedOptions:[{label:'QuickEntry',textContent:'QuickEntry'}]});
  const result=await check('native-select-label',[selected]);
  assert.deepEqual(result.row.visible_field_text.map(x=>[x.text,x.kind]),[['QuickEntry','selected_option']]);
  assert(result.row.visible_labels.includes('QuickEntry'));
  assert(!result.row.visible_labels.includes('0'));
  assert(!result.row.visible_labels.includes('ReviewRequired'));
  assert.equal(result.row.eligible_for_lesson,false);
  for(const [name,options] of [
    ['hidden',{style:{display:'none'}}],['offscreen',{box:{y:200}}],
    ['multiple',{multiple:true}],['listbox',{size:4}]
  ]) {
    const excluded=await check('native-select-'+name,[element({tagName:'SELECT',value:'0',selectedOptions:[{label:'QuickEntry'}],...options})]);
    assert.deepEqual(excluded.row.visible_field_text,[]);
  }
'''), 5)

    def test_both_recorders_reject_reviewed_snapshot_before_writing_assets(self):
        core_url = json.dumps((ROOT / 'sources/production/capture-evidence.mjs').as_uri())
        app_url = json.dumps((ROOT / 'sources/production/capture_application.mjs').as_uri())
        script = '''
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
const {createCapture} = await import(CORE_URL);
const {captureApplication} = await import(APP_URL);
const root = await fs.mkdtemp(path.join(os.tmpdir(), 'academy-capture-manifest-test-'));
try {
  for (const format of ['reviewed','other-recorder']) {
    for (const recorder of ['core','app']) {
      const folder = `${format}-${recorder}`;
      const directory = path.join(root, folder);
      await fs.mkdir(directory);
      const snapshot = format === 'reviewed' ? {app:'Core',screenshots:[{id:'reviewed-fixture'}],scope:'immutable test snapshot'} : recorder === 'core' ? {app:'Core',captures:[]} : [];
      const original = JSON.stringify(snapshot) + '\\n';
      const manifest = path.join(directory, 'manifest.json');
      await fs.writeFile(manifest, original);
      const dummyTab = {playwright:{evaluate:async()=>({labels:[],fields:[],controls:[]}),domSnapshot:async()=> 'unit-test fixture only'},screenshot:async()=>Buffer.from([255,216,255,217]),url:async()=> 'http://localhost/fixture'};
      if (recorder === 'core') {
        await assert.rejects(createCapture(root, folder), /requires a raw array manifest/);
      } else {
        await assert.rejects(captureApplication(dummyTab,{app:'Core',directory,relativeDirectory:folder,id:'new-fixture'},{redact:String,jpegSize:()=>({width:16,height:16})}), /requires a raw \\{captures:/);
      }
      assert.equal(await fs.readFile(manifest,'utf8'), original);
      assert.deepEqual(await fs.readdir(directory), ['manifest.json']);
    }
  }
} finally { await fs.rm(root,{recursive:true,force:true}); }
'''.replace('CORE_URL', core_url).replace('APP_URL', app_url)
        result = subprocess.run([shutil.which('node'), '--input-type=module', '-e', script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
