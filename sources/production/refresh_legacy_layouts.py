"""Reviewed focus views for the original Academy lessons, using exact speech cues.

Original screenshots remain intact. Rectangles select authentic visible UI pixels;
they never reconstruct controls, reflow a screenshot or assert a new saved result.
The three wide operating-profile captures are unsaved form demonstrations. Historical
save banners, report counts, messages and command replies retain their original images.
"""
import argparse
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'deep-dive'
CAPTURES=BASE/'captures/deep-dive'


def view(prefix,y,cue,labels,checks=None,*,x=250,width=None,height=322):
    matches=list(CAPTURES.glob(prefix+'*.jpg'))
    if len(matches)!=1:raise ValueError(f'Ambiguous capture prefix: {prefix}')
    if width is None:
        from PIL import Image
        width=Image.open(matches[0]).width-x
    return dict(capture=matches[0].name,cue=cue,region=[x,y,width,height],
                visible_labels=labels,checks=checks or labels[:2],
                rationale='Show these authentic controls or retained results as their corresponding speech begins; hold through the related explanation.')


def recipes():
    V=view
    return {
      '01-setup-wizard':[
        [V('01-setup',175,None,['Welcome and goals','Department profile','Choose your modules'],['Nine setup steps','Review current findings']),V('01-setup',455,9,['People and access','Dispatch essentials','Verify and practice'],['Follow the setup journey'])],
        [V('02-wizard',340,None,['Step 1 of 9','Setup mode','Fresh setup'],['Choose the starting mode']),V('02-wizard',465,24,['Core modules','Recommended','Optional','Paid add-ons'],['Interest does not activate a service.'])],
        [V('03-operating',140,None,['Department operating profile','Operating packs'],['Choose the operating context']),V('wide-04-operating-packs',220,32,['Fire','EMS and ambulance'],['Fire + EMS'],x=260,width=1120,height=610),V('wide-04b-operating-context',0,34,['Career','14','Central dispatch','24-hour operation'],['Career · 14 members','Central dispatch · 24 hours'],x=260,width=1120,height=630),V('wide-04c-language-accessibility-reviewed',80,36,['English','Captions','Plain language'],['English','Captions + plain language'],x=260,width=1120,height=630)],
        [V('05-operating',85,None,['Save operating profile','Operating profile saved.','Return to setup and verify'],['Save, then return.']),V('54-admin',210,53,['Operating profile recorded','21 of 21 modules have a setup choice'],['Profile recorded','Verify the owning setting.'])],
        [V('06-wizard',40,None,['Training and certifications','Setup choice','Use now'],['Save each module choice']),V('07-wizard',100,63,['Automation and integrations','Setup choice','Use now'],['Module choice is a decision.']),V('54-admin',280,66,['Choose your modules','21 of 21 modules have a setup choice'],['21 choices recorded'])],
        [V('08-wizard',340,None,['Step 4 of 9','People and access','Personnel and groups'],['People and access']),V('09-wizard',335,76,['Step 5 of 9','Dispatch essentials','Call types and priorities'],['Dispatch essentials','Save on the owning screen.'])],
        [V('10-wizard',340,None,['Step 6 of 9','Your other modules','Mapping and location'],['Review prerequisites']),V('11-wizard',335,86,['Step 7 of 9','Plan and add-ons','Subscription and capacity'],['Review commercial access']),V('07-wizard',460,87,['Maintenance and work orders','Workforce and business operations','Add-on active'],['Training billing fixture']),V('16-setup',0,89,['Push-to-Talk','Advanced Data Protection','Enhanced AI','Learn later'],['Learn later does not activate.'])],
        [V('12-wizard',350,None,['Step 8 of 9','Verify and practice','15 / 23','8'],['Review the recorded checks']),V('14-setup',240,94,['15 / 23','8','2 critical'],['15 of 23 verified','8 need attention']),V('15-setup',375,96,['Administrator MFA is not enforced','Administrators need MFA enrollment'],['Critical findings remain']),V('14-setup',460,101,['Checks with unknown evidence','Modules you use that have no automated checks yet'],['Unknown is not a pass.','Some modules need manual review.'])],
        [V('13-wizard',420,None,['Step 9 of 9','Review and handover','10/16/2026','Save review date'],['Review date: October 16']),V('16-setup',325,112,['Setup review','Reviewed','Checks at the recorded administrative review'],['Review records a snapshot.','Findings remain open.'])],
        [V('14-setup',225,None,['Setup Report','Verify again','15 / 23','8'],['Save → verify → compare']),V('16-setup',330,123,['Reviewed','Download calendar reminder','Open a fresh printable report'],['Assign follow-up','Keep unresolved findings visible.'])],
      ],
      '03-custom-statuses':[
        [V('17-custom',195,None,['Current Unit Statuses','Add Unit Statuses'],['Unit status sets']),V('17-custom',445,7,['Custom Personnel Statuses (Actions)','Custom Personnel Staffing Levels'],['Activity and availability differ.'])],
        [V('18-status',350,None,['Search & Rescue','Searching','Subject Contact','Use this template'],['Choose a relevant template']),V('19-status',175,20,['Searching assigned area','Order','Button Preview'],['Review names, colors and order.']),V('20-custom',235,24,['Training — SAR Field Team','8'],['Eight options saved'])],
        [V('24-option',370,None,['Base Type','Searching','Require GPS','Detail Type','None'],['A label and its meaning differ.']),V('24-option',465,39,['Require GPS','Detail Type','None'],['Reopened values did not retain the edit.'])],
        [V('25-blank',325,None,['Ready for assignment','Base Type','Available'],['Ready → Available']),V('26-create',195,49,['Searching assigned area','Searching','Require GPS','Calls','Required'],['Searching','Calls · required note · GPS'],x=120,width=620,height=335)],
        [V('27-field',325,None,['Ready for assignment','Searching assigned area','Unavailable — maintenance','0','1','2'],['Order: 0, 1, 2']),V('27-field',455,67,['Add','Unavailable — maintenance'],['Save the entire set.'])],
        [V('22-unit',185,None,['Rescue','Actions (Custom Unit Statuses)','Update'],['Assign through the unit type']),V('23-custom',25,83,['Set Unit Status','Ready for assignment','Destination','Note','Save'],['Check the unit picker.'],x=120,width=620,height=335)],
        [V('28-search',65,None,['Searching assigned area','Destination','Note','TRAINING'],['Select the exercise','Record the accountability note'],x=120,width=620,height=335),V('29-search',195,97,['Squad 3','Searching assigned area','Timestamp'],['Verify the saved unit status.'])],
        [V('17-custom',440,None,['Custom Personnel Statuses (Actions)','Custom Personnel Staffing Levels'],['Review department-wide effects.']),V('27-field',325,114,['Ready for assignment','Searching assigned area','Unavailable — maintenance'],['Use meaningful operational choices.']),V('29-search',195,121,['Squad 3','Searching assigned area'],['Verify and assign follow-up.'])],
      ],
      '06-dispatch-settings':[
        [V('39-dispatch',210,None,['Group Dispatch Settings','Use Shift for Group Dispatch'],['Audience · transitions · intake'])],
        [V('39-dispatch',245,None,['Use Shift for Group Dispatch','Set Status for Shift Personnel on Dispatch','Person Call Dispatch Status','Person Call Release Status'],['Review empty-shift fallback.']),V('49-dispatch',390,20,['Use Shift for Group Dispatch','Responding','StandingBy'],['Responding on dispatch','Standing By on release'])],
        [V('39-dispatch',455,None,['Group-Scoped Dispatch','Scope Dispatch to Group Areas'],['Review group visibility.']),V('40-unit',360,37,['Department-Wide Dispatch Roles','Also Dispatch To Assigned Personnel','Also Dispatch To Entire Group'],['Review crew expansion.']),V('44-dispatch',0,40,['Also Dispatch To Assigned Personnel','Also Dispatch To Entire Group'],['Assigned crew: ON','Entire group: OFF'])],
        [V('44-dispatch',185,None,['Unit Call Dispatch Status','Responding','Unit Call Release Status','Released','Unit Type Status Overrides'],['Responding → Released']),V('44-dispatch',335,46,['Rescue','Responding to assignment','Ready for assignment'],['Review the Rescue overrides.']),V('43-add',90,50,['Responding to assignment','Base Type','Responding','Calls'],['Responding is the system meaning.'],x=120,width=620,height=335),V('44-dispatch',335,52,['Rescue','Responding to assignment','Ready for assignment'],['Searching is a later field update.'])],
        [V('41-call',350,None,['New Call Form Fields','Visible','Required','GPS Coordinates'],['Visibility and requirement differ.']),V('45-call',430,62,['GPS Coordinates','Visible','Required'],['GPS initially required']),V('47-missing',160,63,['geolocation is required by this department before a call can be created.','TRAINING — SAR dispatch policy exercise'],['Actual validation rejection']),V('48-location',160,65,['geolocation is required by this department before a call can be created.'],['Rejection remained.','Do not call it a success.']),V('49-dispatch',255,68,['Successfully saved Call & Dispatch Settings.','Group Dispatch Settings'],['Working settings saved'])],
        [V('42-recommendation',170,None,['Run Cards & Automatic Dispatch','Automatic Resource Selection','Off (Manual Dispatch)','Automatically dispatch recommended resources'],['Automatic selection: Off']),V('41-call',0,82,['Maximum personnel location age (seconds)','Maximum response radius (meters)','Include stale locations','Order by driving ETA'],['Review location freshness and ETA.']),V('42-recommendation',65,88,['Check-In Timer Settings','Auto-Enable Check-In Timers for New Calls'],['Automatic timers remain off.'])],
        [V('46-dispatch',230,None,['Successfully saved Call & Dispatch Settings.'],['Main settings saved']),V('wide-50-synthetic-call-inputs',140,93,['TRAINING — SAR dispatch policy exercise','Routine','Rescue','DEMO-SETTINGS-01'],['Enter the synthetic call'],x=270,width=1110,height=630),V('wide-50b-synthetic-call-narrative',230,96,['Notes','TRAINING','Location','41.8721','-87.6523'],['Accountability note + coordinates'],x=430,width=1280,height=610),V('50-call',175,98,['Units','Squad 3','Ready for assignment'],['Select Squad 3']),V('51-dispatch',315,100,['Squad 3','Responding to assignment'],['Verify the dispatch transition.']),V('52-training',55,102,['Nature of the Call','Notes','Dispatched','Squad 3'],['Inspect the saved record.'])],
        [V('52-training',50,None,['Nature of the Call','Notes','Dispatched'],['Close only the training exercise.']),V('53-custom',315,112,['Squad 3','Ready for assignment'],['Verify the release transition.'])],
      ],
      '12-chat':[
        [V('60-chat',120,None,['Chat','Search conversations'],['Open team Chat']),V('60-chat',350,3,['CHANNELS','Squad 3','Command','Firehouse 51'],['Review the channel audience.'])],
        [V('61-chat',190,None,['New conversation','Kelly Severide','Create group'],['Select explicit participants.'],x=130,width=620,height=335),V('61-chat',340,17,['Create group','Kelly Severide'],['Confirm participants before creating.'],x=130,width=620,height=335),V('62-chat',180,19,['TRAINING — Field coordination'],['Create the named training group.'])],
        [V('63-chat',300,None,['TRAINING — Field coordination','Wallace Boden','TRAINING ONLY'],['Read sender, text and timestamp.']),V('63-chat',300,36,['TRAINING — Field coordination','TRAINING ONLY'],['Reopen to verify persistence.']),V('63-chat',470,39,['Write a message','Send as urgent (requires acknowledgment)'],['Review composer controls.'])],
        [V('63-chat',465,None,['Send as urgent (requires acknowledgment)'],['Select urgent before sending.']),V('64-chat',365,49,['URGENT','0/2 acknowledged'],['Two recipients remain pending.']),V('68-chat',400,50,['0/2 acknowledged'],['Inspect the acknowledgment count.'])],
        [V('69-chat',265,None,['Thread','1 reply','Replies','TRAINING — Briefing follow-up'],['Keep follow-up in the thread.']),V('69-chat',440,62,['TRAINING — Briefing follow-up','Area Alpha','Replies'],['Read the focused reply.']),V('70-chat',385,65,['0/2 acknowledged','1 reply'],['A reply is not acknowledgment.'])],
        [V('72-chat',430,None,['0/2 acknowledged','1 reply'],['Reaction, reply and acknowledgment differ.']),V('72-chat',320,78,['TRAINING — Field coordination','URGENT'],['Review the recorded client limits.']),V('66-chat',180,81,['TRAINING — Field coordination','CHANNELS'],['Recorded workspace limitation']),V('69-chat',440,83,['Thread','Replies'],['The widget has a readable thread path.'])],
        [V('60-chat',220,None,['CHANNELS','Squad 3','Command'],['Choose the intended audience.']),V('69-chat',440,96,['TRAINING — Briefing follow-up','Replies'],['Record a focused follow-up.']),V('72-chat',430,99,['0/2 acknowledged','1 reply'],['Reopen and inspect separate counts.'])],
      ],
      '13-assistant':[
        [V('73-assistant',0,None,['Assistant','Resgrid AI assistant'],['Assistant and team Chat differ.']),V('78-assistant',110,4,['Where do I configure custom unit statuses','I didn’t understand that command','HELP'],['Recorded fallback','No AI guidance demonstrated.'])],
        [V('wide-75-assistant-controls-before',150,None,['Assistant Configuration','Enable Assistant','Allowed Platforms'],['Review enabled access and scope.'],x=270,width=1000,height=610),V('wide-76-assistant-bounded-form',150,24,['Enable Assistant','WebChat'],['This example uses WebChat.'],x=270,width=1000,height=610)],
        [V('wide-76-assistant-bounded-form',150,None,['Enable Assistant','WebChat','Confirm Status Changes','Confirm Phone Linking','Proactive Notifications'],['WebChat only','Dispatch through Assistant: OFF'],x=270,width=1000,height=610),V('76-assistant',240,33,['Assistant settings saved.','WebChat'],['Save and inspect confirmation.']),V('77-assistant',350,34,['WebChat','Allow Dispatch via Assistant'],['Reload to verify settings.']),V('wide-76-assistant-bounded-form',150,36,['Confirm Status Changes','Confirm Phone Linking','Proactive Notifications','Messages / User / Minute','Messages / Dept / Minute'],['Review confirmations and rate policy.'],x=270,width=1000,height=610)],
        [V('wide-81-assistant-provider-prerequisites',290,None,['Your own AI provider (bring your own key)','Enhanced AI add-on could not be confirmed'],['Provider prerequisites are unresolved.'],x=270,width=1000,height=550),V('wide-81-assistant-provider-prerequisites',290,51,['Provider','LLM Endpoint','LLM Model','https'],['Provider settings are requirements.','They do not prove connectivity.'],x=270,width=1000,height=550)],
        [V('79-assistant',250,None,['HELP','STATUS','STAFFING','CALLS','MESSAGES','UNITS'],['Use the supported command vocabulary.']),V('79-assistant',340,65,['HELP','PERSONNEL','DEPARTMENTS','STOP'],['Read help before a changing action.'])],
        [V('80-assistant',375,None,['CALLS','Active Calls for Firehouse 51'],['Read-only active-call query']),V('80-assistant',475,76,['51001','51002','51003'],['Inspect all three training calls.']),V('80-assistant',475,83,['Assistant is typing','Active Calls for Firehouse 51'],['Saved content is the evidence.'])],
        [V('77-assistant',285,None,['Assistant settings saved.','WebChat'],['Use a bounded configuration.']),V('79-assistant',250,99,['HELP','STATUS','STAFFING','CALLS'],['Run help and compare source records.']),V('80-assistant',375,102,['Active Calls for Firehouse 51'],['Document unverified behavior.'])],
      ],
      '14-admin-assist':[
        [V('54-admin',90,None,['Setup Wizard','Setup Report','Explore Resgrid & Addons','Admin AI'],['Return after configuration changes.']),V('54-admin',350,8,['People and access','Dispatch essentials','Verify and practice'],['Keep unresolved findings visible.'])],
        [V('55-admin',245,None,['16 / 25','9','3 critical','0'],['16 of 25 verified','9 need attention']),V('14-setup',240,17,['15 / 23','8','2 critical'],['Earlier review snapshot']),V('55-admin',245,19,['16 / 25','9','3 critical'],['Compare the scope of each snapshot.'])],
        [V('55-admin',180,None,['Verify again','16 / 25','9'],['Refresh evidence; findings remain.']),V('15-setup',375,30,['Administrator MFA is not enforced','Administrators need MFA enrollment'],['Review the retained critical findings.']),V('55-admin',430,37,['Checks with unknown evidence','Modules you use that have no automated checks yet'],['Zero unknown is not full coverage.'])],
        [V('56-admin',210,None,['Explore Resgrid & Addons','Dispatch Settings','Show paid add-ons only'],['Find the feature and prerequisites.']),V('56-admin',440,47,['Dispatch and calls','Why it matters','Example'],['Understand before recording learning.']),V('58-admin',250,51,['16 / 25','9','1 / 62'],['Learning: 1 of 62','Verified checks remain 16 of 25.'])],
        [V('57-admin',45,None,['Return to setup and verify','Save changes on this screen first'],['Save on the owning screen.']),V('57-admin',285,63,['Use Shift for Group Dispatch','Responding','StandingBy'],['Inspect the saved shift configuration.']),V('55-admin',245,65,['16 / 25','9','3 critical'],['Return and verify.'])],
        [V('59-admin',200,None,['Setup review','Reviewed','16 / 25','9'],['Review preserves unresolved findings.']),V('59-admin',240,78,['10/16/2026','Download calendar reminder','Open a fresh printable report'],['Review date: October 16','Prepare a current handover.'])],
        [V('58-admin',245,None,['16 / 25','9','1 / 62'],['Review operational consequences.']),V('57-admin',285,97,['Use Shift for Group Dispatch','Responding','StandingBy'],['Inspect the owning setting.']),V('59-admin',200,99,['Reviewed','Setup review'],['Record the review and next owner.'])],
      ],
    }


def apply():
    from PIL import Image
    for ident,scenes in recipes().items():
        path=ROOT/'lessons'/f'{ident}.json';lesson=json.loads(path.read_text())
        assert len(scenes)==len(lesson['scenes'])
        lesson['video_layout']='screen-first-v2'
        for scene,views in zip(lesson['scenes'],scenes):
            scene['captures']=[v['capture'] for v in views]
            scene['capture_cues']=[v['cue'] for v in views[1:]]
            scene['capture_views']=[{k:v[k] for k in ('region','visible_labels','checks','rationale')} for v in views]
            for v in views:
                w,h=Image.open(CAPTURES/v['capture']).size;x,y,cw,ch=v['region']
                if x<0 or y<0 or x+cw>w or y+ch>h or cw/ch<1.5:
                    raise ValueError(f'{ident}: invalid focus rectangle for {v["capture"]}: {v["region"]} within {w}x{h}')
        path.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n')
        print(ident,':',sum(map(len,scenes)),'speech-timed views')
    manifest=CAPTURES/'manifest.json';rows=json.loads(manifest.read_text())
    for row in rows:
        if row['file'].startswith('wide-'):
            p=CAPTURES/row['file'];row['width'],row['height']=Image.open(p).size
            row['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args();apply()
