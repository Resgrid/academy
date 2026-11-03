"""Pin complete speech to the actually reviewed member and independent-approval UI."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CFG={}
for key,name,cues in [('members','core-member-creation-access',82),('approval','core-deployment-time-submission-approval',72)]:
 b=S/'expansion/plans'/(name+'-source-20261102')
 CFG[key]=dict(name=name,source_folder=b.name,source_sha256=sha(b/'lesson.candidate.json'),captures_sha256=sha(b/'captures.reviewed.json'),audio_sha256=sha(S/'expansion/audio'/(name+'.m4a')),captions_sha256=sha(S/'expansion/audio'/(name+'.actual.corrected.srt')),qa_sha256=sha(S/'expansion/audio'/(name+'.actual.qa.json')),cues=cues,scene_apps={},supporting_applications=[],additional_labels={},refs={},context_notes=[])
CFG['members'].update(
 context_notes=['Root personally inspected the selected unchanged screenshots on all four member source sheets; loading transition016 is excluded.', 'Source019 is an unsaved replay of the exact identity fields after the successful creation; no duplicate was submitted.', 'The checked Normal User radio has value false for IsDepartmentAdmin; no administrator privilege grant occurred.', 'Saved state Normal→Normal, Disabled→Normal is distinct from Available staffing and Standing By status. No member sign-in or rejection was executed.', 'Central time zone, group and role are verified on fully loaded reopened source020.'],
 spans=[['01',1,7,1],['02',8,8,9],['02',9,16,10],['03',17,23,19],['04',24,31,6],['05',32,37,7],['05',38,40,8],['06',41,47,11],['07',48,51,12],['07',52,53,13],['07',54,55,14],['08',56,58,14],['08',59,64,15],['09',65,65,15],['09',66,67,17],['09',68,73,18],['10',74,82,20]],
 refs={1:{'Personnel':'Personnel'},2:{'Add a Person':'Add a Person','Manage Invites':'Manage Invites','Manage Roles':'Manage Roles'},3:{'Add a Person':'Add a Person'},
 8:{'Account Information':'Account Information','Username':'Username'},9:{'New Password':'New Password','Confirm Password':'Confirm Password'},10:{'Passwords must be 8 characters or longer and include a digit (number), an uppercase and lowercase letter':'at least eight characters'},
 17:{'User Details':'User Details','ID Number':'I D Number','First Name':'First Name'},18:{'Last Name':'Last Name','Email Address':'Email Address'},19:{'Peter':'Peter','Mills':'Mills'},20:{'Email Addresses must be unique':'Email Addresses must be unique'},
 24:{'Group Details':'Group Details','TRAINING ONLY - Community coordination 20261028':'community coordination training group'},25:{'Is Group Admin?':'Is Group Admin'},26:{'Roles':'Roles','×TRAINING ONLY - Community response navigator':'community response navigator training role'},
 32:{'Notify User?':'Notify User','Require Password Change':'Require Password Change'},33:{'Notify User?':'Notify User'},36:{'Require Password Change':'Require Password Change'},38:{'Add Person':'Add Person'},
 41:{'Personnel':'Personnel','Search:':'Search'},42:{'Peter Mills':'Peter Mills'},43:{'TRAINING ONLY - Community response navigator':'community response navigator role','Normal':'Normal'},44:{'Staffing':'Staffing','Available':'Available','Status':'Status','Standing By':'Standing By'},47:{'Edit':'Edit'},
 48:{'Edit Peter Mills Profile':'reopened profile'},49:{'Time Zone':'Time Zone'},50:{'(GMT-10:00) Hawaii':'Hawaii'},52:{'(GMT-06:00) Central Time (US & Canada)':'Central Time, U S and Canada'},54:{'Save':'Save'},55:{'Department Settings':'department settings'},
 56:{'Department Settings':'Department Settings','User Type':'User Type','Normal User':'Normal User'},57:{'Department Admin':'Department Admin'},58:{'Disable User':'Disable User','Hide User':'Hide User','Save':'Save'},59:{'Personnel':'Personnel','Normal, Disabled':'Normal, Disabled'},60:{'Available':'Available','Staffing':'Staffing','Standing By':'Standing By','Status':'Status'},
 65:{'Edit':'Edit'},66:{'Normal User':'Normal User','Disable User':'Disable User','Hide User':'Hide User'},67:{'Save':'Save'},68:{'Search:':'Search','Peter Mills':'Peter'},69:{'State':'State','Normal':'Normal'},70:{'TRAINING ONLY - Community response navigator':'navigator role'},
 74:{'(GMT-06:00) Central Time (US & Canada)':'Central Time'},75:{'TRAINING ONLY - Community coordination 20261028':'community coordination group','×TRAINING ONLY - Community response navigator':'navigator role'},76:{'Is Group Admin?':'Is Group Admin'}})
CFG['approval'].update(
 context_notes=['Root personally inspected all eight selected unchanged actual source images on the two approval source contact sheets.', 'Wallace Boden submitted at16:39:55; the submitter restriction is visibly recorded. Kelly Severide separately approved at16:45:06.', 'Source007/009 subject select text is clipped in the wide table. This narration describes the visible column controls without claiming the clipped full subject names are legible.', 'Source010 shows the saved Fuel24.50USD and actual attachment icon, no new receipt download.', 'No signature, PDF, invoice, payment, payroll or deployment-status transition is claimed. The separate deployment badge remains Demobilizing.'],
 spans=[['01',1,9,4],['02',10,11,4],['02',12,16,5],['03',17,24,5],['04',25,32,6],['05',33,40,7],['06',41,48,8],['07',49,50,9],['07',51,56,10],['08',57,57,8],['08',58,64,11],['09',65,72,11]],
 refs={1:{'Daily Time Report #2':'Daily Time Report number two'},3:{'Draft':'Draft'},4:{'Crew: TRAINING ONLY - Community van 20261028':'crew','Incident #':'incident reference','Resource order #':'resource order','Request #':'request number'},5:{'Cost code':'code','Point of hire':'point of hire'},
 10:{'Actions':'Actions','Save':'Save','Save and submit':'Save and submit'},11:{'Save and submit':'Save and submit'},12:{'Saved.':'Saved','Submitted':'Submitted'},13:{'Approved':'Approved'},17:{'Save':'Save','Submitted':'Submitted'},19:{'Approved':'Approved'},
 25:{'Review':'Review','Wallace Boden':'Wallace Boden'},26:{'You submitted this time report or have hours on it, so another approver must approve it.':'you submitted this time report or have hours on it'},
 34:{'Kelly Severide':'Kelly Severide'},35:{'Subject':'subjects','Entry type':'entry types','Start':'start','End':'end'},36:{'Paid break (min)':'breaks','Km':'distance'},37:{'Approve':'Approve','Review':'Review'},38:{'Approve':'Approve'},
 41:{'Approved':'Approved'},42:{'Actions':'Actions','Submitted':'submission time','Approved':'approval time'},44:{'Incident #':'reference fields'},
 50:{'Subject':'entry controls'},51:{'Expenses':'Expenses','Fuel':'Fuel','TRAINING ONLY - Fuel receipt demo':'training receipt description'},52:{'24.50 USD':'twenty-four dollars and fifty cents'},54:{'Signatures':'signature fields'},
 57:{'Back to deployment':'Back to deployment'},58:{'Status':'Status','Approved':'Approved'},59:{'Submitted':'Submitted','Wallace Boden · 11/02/2026 16:39:55':'Wallace Boden'},60:{'Kelly Severide · 11/02/2026 16:45:06':'Severide'},62:{'Invoice':'Invoice'},
 70:{'Submitted':'submit the report'},71:{'Approved':'approve it'}})
out=S/'production/members_deployment_approval_complete_inputs_20261102.json'
assert not out.exists()
out.write_text(json.dumps(CFG,indent=2,ensure_ascii=False)+'\n')
text=(S/'production/prepare_deployment_complete_20261102.py').read_text().replace("CONFIG_FILE=S/'production/deployment_complete_inputs_20261102.json'","CONFIG_FILE=S/'production/members_deployment_approval_complete_inputs_20261102.json'").replace('3406a0544f3d8b9c339c9ee8de8a23ecc4265c7c19ee07fb0de2ef7438824c1e',sha(out))
dest=S/'production/prepare_members_deployment_approval_complete_20261102.py'
assert not dest.exists();dest.write_text(text)
print(json.dumps({'config':out.name,'review_inferred':False}))
