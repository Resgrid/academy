"""Bind the complete invoice lifecycle speech to reviewed actual UI screen holds. No approval is inferred."""
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / "sources"
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
CFG={'invoice': {'name': 'core-invoice-offline-payments-and-aging', 'cues': 102, 'source_sha256': '7f71378146868441fcdfd1a2f5c436d220191cd1c63322c20051e5d80cb987e8', 'captures_sha256': 'd5c44ba4873a2d7305f290cc979be76679927c328157a5521103da0ec8e8dd3a', 'audio_sha256': 'ec9a663d39cb92c649d857ec686e9c87a1c48135d9df413a442a487e389f0724', 'captions_sha256': '170f9837815971ea37cbe6668f80894af7e867f17fa710521ffeace13a387203', 'qa_sha256': 'eb67697eb9c958258826115f568917074d74a8ab14b27139fdd69834141325b1', 'spans': [['01', 1, 1, 1], ['01', 2, 9, 2], ['02', 10, 13, 3], ['02', 14, 18, 4], ['03', 19, 20, 5], ['03', 21, 25, 6], ['04', 26, 32, 7], ['04', 33, 35, 8], ['05', 36, 37, 8], ['05', 38, 42, 9], ['05', 43, 44, 8], ['06', 45, 53, 10], ['07', 54, 56, 11], ['07', 57, 61, 12], ['07', 62, 62, 11], ['08', 63, 70, 13], ['09', 71, 75, 14], ['09', 76, 78, 15], ['10', 79, 86, 16], ['11', 87, 88, 17], ['11', 89, 93, 18], ['11', 94, 94, 16], ['12', 95, 100, 18], ['12', 101, 101, 16], ['12', 102, 102, 15]], 'refs': {1: {'New invoice': 'New invoice'}, 2: {'Academy Logistics Desk (fictional)': 'Academy Logistics Desk'}, 3: {'Customer': 'Customer'}, 4: {'Set up billing profile': 'Set up billing profile'}, 5: {'Create draft': 'Create draft'}, 10: {'Billing e-mail': 'Billing e-mail'}, 11: {'Terms (net days)': 'net days', 'Default discount %': 'Default discount'}, 12: {'30': 'thirty'}, 13: {'0': 'zero', 'Default discount %': 'default discount'}, 14: {'Notes': 'Notes'}, 15: {'Save': 'Save'}, 19: {'New invoice': 'New invoice'}, 20: {'USD': 'U S dollars', 'Create draft': 'Create draft'}, 21: {'Invoice #1': 'Invoice number one', 'Draft': 'Draft'}, 22: {'Due': 'Due'}, 23: {'Leave empty to use the profile terms: net days 30': 'thirty net days'}, 24: {'Notes': 'Notes', 'Terms': 'Terms'}, 26: {'Add line': 'Add line', 'TRAINING ONLY - Standby exercise': 'TRAINING ONLY, Standby exercise'}, 27: {'Qty': 'quantity', '2': 'two', 'Rate': 'rate', '50': 'fifty', 'Taxable': 'Taxable'}, 29: {'Amount': 'Amount', '100.00': 'one hundred'}, 30: {'Total': 'Total', '0.00': 'zero'}, 31: {'Save': 'save'}, 32: {'Save': 'Save', 'Preview & send': 'Preview and send'}, 33: {'Total': 'total', '100.00 USD': 'one hundred U S dollars'}, 34: {'Balance': 'balance'}, 36: {'Mark as sent (no e-mail)': 'Mark as sent, no email'}, 38: {'Invoice marked as sent.': 'Invoice marked as sent', 'Sent': 'Sent'}, 39: {'Issued': 'Issued', 'Due': 'Due', 'Amount paid': 'Amount paid', '0.00': 'zero'}, 40: {'Balance': 'Balance', '100.00 USD': 'one hundred'}, 45: {'Record payment': 'Record payment'}, 46: {'Manual payments only; online payments are recorded automatically.': 'manual payments', 'Amount': 'Amount'}, 47: {'Method': 'Method', 'Reference': 'Reference', 'Notes': 'Notes'}, 48: {'40': 'forty'}, 49: {'Other': 'Other', 'TRAINING-ONLY-PAYMENT-01': 'training reference ending in zero one'}, 50: {'Notes': 'note'}, 51: {'Record payment': 'Record payment'}, 55: {'Partially paid': 'Partially paid'}, 56: {'Total': 'Total', '100.00 USD': 'one hundred', 'Amount paid': 'Amount paid', '40.00': 'forty', 'Balance': 'Balance', '60.00 USD': 'sixty U S dollars'}, 57: {'Payments': 'Payments', 'Other': 'Other'}, 58: {'Reference': 'reference', '40.00': 'forty'}, 59: {'Succeeded': 'Succeeded'}, 63: {'Accounts receivable aging': 'Aging'}, 64: {'Accounts receivable aging': 'Accounts receivable aging'}, 65: {'Current': 'Current', '60.00 USD': 'sixty U S dollars', '1 invoices': 'one invoice'}, 66: {'#1': 'invoice number one'}, 67: {'Total': 'total', 'Balance': 'balance'}, 70: {'#1': 'invoice number link'}, 71: {'Record payment': 'Record payment'}, 72: {'60': 'sixty', 'Other': 'Other', 'Method': 'method'}, 73: {'TRAINING-ONLY-PAYMENT-02': 'training reference ending in zero two'}, 74: {'Notes': 'note'}, 75: {'Record payment': 'Save the entry'}, 76: {'Paid': 'Paid'}, 77: {'Amount paid': 'Amount paid', '100.00': 'one hundred', 'Total': 'Total', 'Balance': 'Balance', '0.00 USD': 'zero U S dollars'}, 79: {'Payments': 'Payments'}, 80: {'40.00': 'forty'}, 81: {'60.00': 'sixty'}, 82: {'Other': 'Other', 'Succeeded': 'Succeeded'}, 85: {'Method': 'method', 'Reference': 'reference'}, 87: {'Accounts receivable aging': 'Aging'}, 88: {'0 invoices': 'zero open invoices', 'No outstanding invoices.': 'No outstanding invoices'}, 89: {'Invoices': 'Invoices', 'Paid': 'Paid', 'Status': 'Status', 'Filter': 'Filter'}, 90: {'#1': 'Invoice number one', 'Paid': 'Paid'}, 91: {'Total': 'total', '0.00 USD': 'zero'}, 93: {'Status': 'status filter'}, 101: {}, 102: {'Balance': 'balance', 'Paid': 'invoice status'}, 43: {'Mark as sent (no e-mail)': 'no-email control'}, 94: {'Payments': 'payment records'}}, 'context_notes': ['Source002 shows the selected customer with a disabled Create draft; source005 shows the enabled button after profile save even though its no-profile hint remains. Successful draft and inherited30-day terms provide the saved result.', 'Source007 has line Amount100.00 and subtotal100.00 but Total0.00 pending Save. Source008 proves the saved total100.00.', 'The ordinary no-email UI confirmation was accepted by the User before source009. No external invoice email was sent.', 'Source011 and015 were reloaded after the respective manual payment entries. Manual Succeeded is not an external bank-settlement assertion.', 'Aging shows the open balance60 in source013, then no outstanding invoices in017. The final Paid filter is018.', 'Final generic review context revisits the actual invoice list, payment rows and paid summary. No new controls or product settings are introduced.', 'Mapping v2 revisits the literal no-email button for cues43-44 and shows the actual payment rows when cue94 names line items and payment records. Script and audio unchanged.']}}

def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(key, write=False):
 from PIL import Image, ImageDraw, ImageFont
 from render_walkthrough import load_cues, words, caption_wrap, find_font, WIDTH
 from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
 from expansion_site import lesson_content_digest
 cfg=CFG[key];name=cfg['name'];base=Path('expansion/plans')/(name+'-source-proposal-20261101')
 audio=Path('expansion/audio')/(name+'.m4a');cap=Path('expansion/audio')/(name+'.actual.corrected.srt');qa_path=Path('expansion/audio')/(name+'.actual.qa.json')
 for path,digest in [(base/'lesson.candidate.json',cfg['source_sha256']),(base/'captures.reviewed.json',cfg['captures_sha256']),
                     (audio,cfg['audio_sha256']),(cap,cfg['captions_sha256']),(qa_path,cfg['qa_sha256'])]:
  assert sha(S/path)==digest,str(path)
 lesson=json.loads((S/base/'lesson.candidate.json').read_text());manifest=json.loads((S/base/'captures.reviewed.json').read_text());qa=json.loads((S/qa_path).read_text())
 assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps'] and qa['silent_corrected_cues']==0
 assert qa['audio']['full_decode']=='passed' and qa['audio']['full_scale_samples']==0
 assert qa['lesson']['sha256']==cfg['source_sha256'] and qa['audio']['sha256']==cfg['audio_sha256']
 rows={row['id']:row for row in manifest['screenshots']};numbered={int(row['id'][:3]):row for row in rows.values()};observed={}
 for row in rows.values():
  assert sha(S/row['file'])==row['sha256'] and sha(S/row['dom_file'])==row['dom_sha256']
  validator=_Validator(S);observed[row['id']]=validator.observations(row,row['id']);assert not validator.issues,validator.issues
 cues=load_cues(S/cap);assert len(cues)==cfg['cues']
 assert words(' '.join(cue['text'] for cue in cues))==words(' '.join(scene['narration'] for scene in lesson['scenes']))
 duration=qa['audio']['duration_seconds'];holds=[];entries=[]
 for index,(scene_id,first,last,number) in enumerate(cfg['spans']):
  capture_id=numbered[number]['id'];start=0.0 if index==0 else cues[first-1]['start']
  end=cues[cfg['spans'][index+1][1]-1]['start'] if index+1<len(cfg['spans']) else duration
  holds.append({'scene_id':scene_id,'screenshot_id':capture_id,'first_cue':first,'last_cue':last,'start':start,'end':end})
  for count in range(first,last+1):
   cue=cues[count-1];aliases=cfg['refs'].get(count,{})
   assert cue['start']>=start and cue['end']<=end
   labels={_normalized(label) for label in aliases};assert labels<=observed[capture_id],(count,capture_id)
   entry=dict(cue,cue=count,scene_id=scene_id,screenshot_id=capture_id,required_labels=list(aliases),spoken_references=aliases,instructional=bool(aliases))
   validator=_Validator(S);validator.spoken_references(entry,labels,str(count),True);assert not validator.issues,validator.issues
   entries.append(entry)
 assert [row['cue'] for row in entries]==list(range(1,cfg['cues']+1))
 learner=deepcopy(lesson);learner['scope_limits']=[v for v in learner['scope_limits'] if not v.startswith('Source proposal only')]
 scenes=[]
 for original,projection in zip(lesson['scenes'],learner['scenes']):
  selected=[h for h in holds if h['scene_id']==original['id']]
  captions=[{k:v for k,v in row.items() if k!='scene_id'} for row in entries if row['scene_id']==original['id']]
  assert words(' '.join(row['text'] for row in captions))==words(original['narration'])
  assert {_normalized(v) for v in original['required_labels']}<=set().union(*(observed[h['screenshot_id']] for h in selected))
  projection['capture_refs']=list(dict.fromkeys([*projection['capture_refs'],*[h['screenshot_id'] for h in selected]]))
  scene={'id':original['id'],'title':original['title'],'kind':'operational','start':selected[0]['start'],'end':selected[-1]['end'],
         'visual_required_labels':original['required_labels'],'screens':[{k:h[k] for k in ['screenshot_id','start','end']} for h in selected],'captions':captions}
  scene['proposed_mapping_sha256']=instruction_scene_digest(scene,rows);scenes.append(scene)
 assert lesson_content_digest(learner)==lesson_content_digest(lesson)
 draw=ImageDraw.Draw(Image.new('RGB',(1920,1080)));font=ImageFont.truetype(str(find_font()),30)
 metrics={'kind':'numeric_caption_layout_measurement_only','cues':[{'cue':row['cue'],'lines':caption_wrap(draw,row['text'],font,WIDTH-120)} for row in entries],
          'actual_encoded_frame_review':False,'listening_review':False}
 proposal={'created_at':datetime.now(timezone.utc).isoformat(),'lesson_id':name,'lesson_file':str(base/'lesson.candidate.json'),'lesson_sha256':cfg['source_sha256'],
           'audio_file':str(audio),'audio_sha256':cfg['audio_sha256'],'captions_file':str(cap),'captions_sha256':cfg['captions_sha256'],
           'qa_file':str(qa_path),'qa_sha256':cfg['qa_sha256'],'duration_seconds':duration,'duration_source':'Complete decode of the specifically approved private Descript export',
           'scenes':scenes,'holds':holds,'cues':entries,'cue_count':len(cues),'scenes_count':len(scenes),'holds_count':len(holds),
           'source_images':len(rows),'distinct_source_images':len({row['sha256'] for row in rows.values()}),'learner_content_sha256':lesson_content_digest(learner),
           'context_notes':cfg['context_notes'],'review_state':'complete_audio_and_cue_map_proposal_requires_actual_Root_and_User_reviews','export_ready':False}
 if write:
  dest=S/'expansion/plans'/(name+'-complete-correspondence-v2-20261101');assert not dest.exists();dest.mkdir()
  for filename,data in [('correspondence.proposed.json',proposal),('captures.source-relative.json',manifest),('lesson.learner-projection.proposed.json',learner),('caption-layout-measurements.json',metrics)]:
   (dest/filename).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
  (dest/'cue-screen-correspondence.txt').write_text('\n\n'.join(f"Cue{row['cue']:03} · scene{row['scene_id']} · {row['start']:.3f}–{row['end']:.3f} · {row['screenshot_id']}\n{row['text']}\n{json.dumps(row['spoken_references'],ensure_ascii=False)}" for row in entries)+'\n')
 return {'passed':True,'lesson_id':name,'scenes':len(scenes),'holds':len(holds),'cues':len(cues),'actual_screens':len(rows),'max_caption_lines':max(len(row['lines']) for row in metrics['cues']),'written':write,'final_approval_inferred':False}


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('lesson',choices=CFG);parser.add_argument('--write',action='store_true');args=parser.parse_args()
 print(json.dumps(prepare(args.lesson,args.write),indent=2))
