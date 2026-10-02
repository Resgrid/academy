#!/usr/bin/env python3
"""Generate a guarded, first-use seed for the dedicated Academy PostgreSQL DB."""
import base64, collections, datetime as dt, hashlib, json, secrets, struct, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / 'fixtures.json').read_text())
credentials = json.loads((ROOT / 'private/credentials.json').read_text())
schema = collections.defaultdict(dict)
for column in json.loads((ROOT / 'schema.json').read_text()):
    schema[column['table_name']][column['column_name']] = column
namespace = uuid.UUID('1c03f4c7-ef29-4c38-9178-6d2b19878651')
def uid(value):
    result = str(uuid.uuid5(namespace, value))
    return result.upper() if value.startswith('person:') else result
now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None, microsecond=0)
admin = uid('person:boden')
department = fixtures['department']['id']
if department != 51:
    raise ValueError('This guarded fixture is reserved for department 51.')
counts = collections.Counter()
sql = ["\\set ON_ERROR_STOP on", "BEGIN;", "SELECT pg_advisory_xact_lock(81510051);", "DO $$ BEGIN IF current_database() <> 'resgrid_academy' THEN RAISE EXCEPTION 'Academy seed refuses another database'; END IF; IF EXISTS (SELECT 1 FROM departments WHERE departmentid=51) THEN RAISE EXCEPTION 'Department 51 already exists; baseline seed refuses to overwrite department data'; END IF; END $$;"]
sql.append("DO $$ BEGIN IF EXISTS (SELECT 1 FROM inventoryoperations WHERE departmentid=51 AND requestid='00000000-0000-0000-0000-000000000001' AND state=2) OR EXISTS (SELECT 1 FROM rmsdepartmentcutovers WHERE departmentid=51) THEN RAISE EXCEPTION 'Baseline seed is closed after Inventory initialization or Records activation; preserve workflow history and add subsequent fixtures through the application'; END IF; END $$;")
def literal(value):
    if value is None: return 'NULL'
    if isinstance(value, bool): return 'true' if value else 'false'
    if isinstance(value, (int, float)): return str(value)
    if isinstance(value, bytes): return "decode('"+value.hex()+"','hex')"
    if isinstance(value, (dt.datetime, dt.date)): value = value.isoformat()
    if isinstance(value, (dict, list)): value = json.dumps(value, ensure_ascii=False)
    return "'"+str(value).replace("'", "''")+"'"
def add(table, primary, **values):
    fields = schema[table]
    unknown = set(values) - set(fields)
    if unknown: raise ValueError(f'{table}: unknown columns {unknown}')
    missing = [k for k,c in fields.items() if c['is_nullable']=='NO' and c['column_default'] is None and k not in values and k != primary]
    if missing: raise ValueError(f'{table}: missing required columns {missing}')
    columns = ','.join('"'+k+'"' for k in values)
    update = ','.join('"'+k+'"=EXCLUDED."'+k+'"' for k in values if k != primary)
    sql.append(f'INSERT INTO "{table}" ({columns}) OVERRIDING SYSTEM VALUE VALUES ({",".join(literal(v) for v in values.values())}) ON CONFLICT ("{primary}") DO '+('UPDATE SET '+update if update else 'NOTHING')+';')
    counts[table] += 1
def password_hash():
    # ASP.NET Identity V3: HMAC-SHA512, network byte order header, 16-byte salt.
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac('sha512', credentials['demo_password'].encode(), salt, 100000, 32)
    return base64.b64encode(b'\x01'+struct.pack('>III',2,100000,16)+salt+key).decode()

add('addresses','addressid',addressid=51001,address1='1000 Training Avenue (fictional)',city='Chicago',state='IL',postalcode='60607',country='United States')
add('departments','departmentid',departmentid=department,name=fixtures['department']['name'],code='FH51',managinguserid=admin,showwelcome=False,createdon=now,updatedon=now,timezone=fixtures['department']['timezone'],departmenttype='Fire Department',addressid=51001,use24hourtime=True,linkcode='DEMO51')
roles = {name:51001+i for i,name in enumerate(dict.fromkeys(p['role'] for p in fixtures['people']))}
for i,(name,role_id) in enumerate(roles.items()):
    add('personnelroles','personnelroleid',personnelroleid=role_id,departmentid=department,name=name,description='Training assignment for software demonstrations')
    add('ranks','rankid',rankid=role_id,departmentid=department,name=name,code='DEMO-'+str(i+1),sortweight=i,tradeweight=i,color='#2563eb')
groups = {name:51001+i for i,name in enumerate(fixtures['groups'])}
for name,group_id in groups.items():
    add('departmentgroups','departmentgroupid',departmentgroupid=group_id,departmentid=department,name=name,type=2 if name=='Firehouse 51' else 1,addressid=51001 if name=='Firehouse 51' else None,parentdepartmentgroupid=None if name=='Firehouse 51' else groups['Firehouse 51'],latitude='41.8721',longitude='-87.6523',dispatchtoprinter=False,dispatchtofax=False)
for i,person in enumerate(fixtures['people']):
    user_id=uid('person:'+person['username']); person['id']=user_id
    email=person['username']+'@firehouse51.example'
    add('aspnetusers','id',id=user_id,username=person['username'],normalizedusername=person['username'].upper(),email=email,normalizedemail=email.upper(),emailconfirmed=True,passwordhash=password_hash(),securitystamp=uid('stamp:'+person['username']),concurrencystamp=uid('concurrency:'+person['username']),phonenumberconfirmed=False,twofactorenabled=False,lockoutenabled=True,accessfailedcount=0)
    add('aspnetusersext','userid',userid=user_id,createdate=now,lastactivitydate=now)
    add('aspnetuserroles','id',id=51001+i,userid=user_id,roleid='38b461d7-e848-46ef-8c06-ece5b618d9d1')
    add('userprofiles','userprofileid',userprofileid=51001+i,userid=user_id,firstname=person['first'],lastname=person['last'],timezone=fixtures['department']['timezone'],mobilecarrier=0,sendemail=False,sendpush=False,sendsms=False,sendmessageemail=False,sendmessagepush=False,sendmessagesms=False,donotrecievenewsletters=True,sendnotificationemail=False,sendnotificationpush=False,sendnotificationsms=False,voiceforcall=False,voicecallmobile=False,voicecallhome=False,custompushsounds=False,lastupdated=now,startdate=now-dt.timedelta(days=365),identificationnumber='DEMO-'+str(5101+i))
    add('departmentmembers','departmentmemberid',departmentmemberid=51001+i,departmentid=department,userid=user_id,isadmin=person['admin'],isdisabled=False,ishidden=False,isdefault=True,isactive=True,isdeleted=False,rankid=roles[person['role']])
    add('departmentgroupmembers','departmentgroupmemberid',departmentgroupmemberid=51001+i,departmentid=department,departmentgroupid=groups[person['group']],userid=user_id,isadmin=person['admin'])
    add('personnelroleusers','personnelroleuserid',personnelroleuserid=51001+i,departmentid=department,personnelroleid=roles[person['role']],userid=user_id)
    add('userstates','userstateid',userstateid=51001+i,departmentid=department,userid=user_id,state=person['staffing'],timestamp=now,note='Firehouse 51 training roster')
    add('actionlogs','actionlogid',actionlogid=51001+i,departmentid=department,userid=user_id,actiontypeid=person['status'],timestamp=now,note='Training status demonstration',geolocationdata='41.8721,-87.6523')
unit_types={name:51001+i for i,name in enumerate(dict.fromkeys(u['type'] for u in fixtures['units']))}
for name,type_id in unit_types.items(): add('unittypes','unittypeid',unittypeid=type_id,departmentid=department,type=name)
units={u['name']:51001+i for i,u in enumerate(fixtures['units'])}
for i,unit in enumerate(fixtures['units']):
    unit_id=units[unit['name']]
    add('units','unitid',unitid=unit_id,departmentid=department,name=unit['name'],type=unit['type'],stationgroupid=groups['Firehouse 51'],vin='DEMO-APPARATUS-'+str(i+1),platenumber='TRAINING',fourwheel=False,specialpermit=False)
    add('unitstates','unitstateid',unitstateid=51001+i,unitid=unit_id,state=unit['state'],timestamp=now,localtimestamp=now-dt.timedelta(hours=5),geolocationdata='41.8721,-87.6523',latitude=41.8721,longitude=-87.6523,note='Training demonstration — no live apparatus')
    add('unitlogs','unitlogid',unitlogid=51001+i,unitid=unit_id,timestamp=now-dt.timedelta(hours=1),narrative='Shift readiness handover completed. Sample equipment checked and fuel level recorded.')
    add('unitroles','unitroleid',unitroleid=51001+i,unitid=unit_id,name='Officer / Team Lead',personnelrolerequired=False)
for i,name in enumerate(['Routine','Urgent','Emergency']):
    add('departmentcallpriorities','departmentcallpriorityid',departmentcallpriorityid=51001+i,departmentid=department,name=name,color=['#2563eb','#f59e0b','#dc2626'][i],sort=i,isdeleted=False,isdefault=i==0,dispatchpersonnel=True,dispatchunits=True,forcenotifyallpersonnel=False,tone=0)
for i,name in enumerate(dict.fromkeys(c['type'] for c in fixtures['calls'])): add('calltypes','calltypeid',calltypeid=51001+i,departmentid=department,type=name)
dispatch_id=51000
for i,call in enumerate(fixtures['calls']):
    call_id=51001+i; closed=i==3; logged=now-dt.timedelta(hours=30 if closed else (3-i)*0.5)
    add('calls','callid',callid=call_id,departmentid=department,reportinguserid=admin,name=call['name'],natureofcall=call['nature'],notes='Fictional exercise for Resgrid Academy. Do not dispatch real resources.',loggedon=logged,priority=51002 if i==0 else 51001,iscritical=False,address='Training site '+str(i+1)+' (fictional), Chicago, IL',geolocationdata=f"{call['lat']},{call['lon']}",state=1 if closed else 0,isdeleted=False,type=call['type'],incidentnumber='DEMO-2026-'+str(i+1).zfill(4),number='DEMO-'+str(i+1).zfill(4),public=False,closedbyuserid=admin if closed else None,closedon=logged+dt.timedelta(hours=1) if closed else None,completednotes='Training exercise complete; accountability confirmed.' if closed else None,callsource=0,dispatchcount=1,lastdispatchedon=logged)
    for name in call['units']:
        dispatch_id+=1
        add('calldispatchunits','calldispatchunitid',calldispatchunitid=dispatch_id,callid=call_id,unitid=units[name],dispatchcount=1,lastdispatchedon=logged)
        for person in fixtures['people']:
            if person['group']==name:
                dispatch_id+=1
                add('calldispatches','calldispatchid',calldispatchid=dispatch_id,callid=call_id,userid=person['id'],groupid=groups[name],dispatchcount=1,lastdispatchedon=logged)
add('logs','logid',logid=51001,departmentid=department,narrative='Completed training smoke investigation. Engine 51 performed a simulated assessment; no hazard found. Personnel accountability and apparatus return were recorded.',startedon=now-dt.timedelta(hours=30),endedon=now-dt.timedelta(hours=29),loggedon=now-dt.timedelta(hours=28),loggedbyuserid=admin,logtype=1,type='Investigation',stationgroupid=groups['Firehouse 51'],callid=51004,officeruserid=uid('person:herrmann'),location='Training site 4 (fictional), Chicago')
add('logunits','logunitid',logunitid=51001,logid=51001,unitid=units['Engine 51'],dispatched=now-dt.timedelta(hours=30),enroute=now-dt.timedelta(hours=30)+dt.timedelta(minutes=2),onscene=now-dt.timedelta(hours=30)+dt.timedelta(minutes=8),released=now-dt.timedelta(hours=29),inquarters=now-dt.timedelta(hours=29)+dt.timedelta(minutes=10))
for i,person in enumerate(p for p in fixtures['people'] if p['group']=='Engine 51'):
    add('logusers','loguserid',loguserid=51001+i,logid=51001,unitid=units['Engine 51'],userid=person['id'])
for i,title in enumerate(fixtures['trainings']):
    training_id=51001+i
    add('trainings','trainingid',trainingid=training_id,departmentid=department,createdbyuserid=admin,name=title,description='Software training exercise for Firehouse 51 personnel.',trainingtext='<h2>'+title+'</h2><p>Review your profile, confirm your station and role, update your availability, and locate the training call. Use the demonstration data to practise recording a result.</p>',minimumscore=80,createdon=now-dt.timedelta(days=5-i),tobecompletedby=now+dt.timedelta(days=14))
    add('trainingquestions','trainingquestionid',trainingquestionid=training_id,trainingid=training_id,question='Where should you confirm your availability for the department?')
    add('trainingquestionanswers','trainingquestionanswerid',trainingquestionanswerid=51001+i*2,trainingquestionid=training_id,answer='In your personnel staffing status',correct=True)
    add('trainingquestionanswers','trainingquestionanswerid',trainingquestionanswerid=51002+i*2,trainingquestionid=training_id,answer='Only in a personal notebook',correct=False)
    for j,person in enumerate(fixtures['people']):
        complete=(j+i)%3==0
        add('trainingusers','traininguserid',traininguserid=51001+i*100+j,trainingid=training_id,userid=person['id'],complete=complete,score=100 if complete else 0,viewed=complete,completedon=now-dt.timedelta(days=1) if complete else None)
for i,title in enumerate(['A Shift — Daily Briefing','Resgrid onboarding workshop','Equipment readiness review']):
    start=now.replace(hour=13,minute=0,second=0)+dt.timedelta(days=i+1)
    add('calendaritems','calendaritemid',calendaritemid=51001+i,departmentid=department,title=title,start=start,end=start+dt.timedelta(hours=1),starttimezone=fixtures['department']['timezone'],endtimezone=fixtures['department']['timezone'],description='Fictional department training event.',itemtype=0,isallday=False,location='Firehouse 51 training room',signuptype=1,creatoruserid=admin,public=False,isv2schedule=True)
add('notes','noteid',noteid=51001,departmentid=department,userid=admin,title='Firehouse 51 — shift briefing',body='<p>Confirm availability, review assigned apparatus, and open the training incident before the exercise.</p>',isadminonly=False,color='#2563eb',addedon=now,category='Shift Briefings')
guide=(fixtures['notice']+'\n\nFirehouse 51 software training\n1. Review your personnel profile.\n2. Confirm staffing and status.\n3. Review assigned calls and apparatus.\n4. Complete the onboarding training.\n').encode()
add('documents','documentid',documentid=51001,departmentid=department,name='Firehouse 51 onboarding guide',category='Training',description='Guide to the fictional software exercise.',adminsonly=False,data=guide,userid=admin,addedon=now,type='text/plain',filename='Firehouse-51-Onboarding.txt')
for i,item in enumerate(fixtures['inventory']):
    type_id=51001+i
    add('inventorytypes','inventorytypeid',inventorytypeid=type_id,departmentid=department,type=item['name'],expiresdays=item['expires_days'],description='Demonstration inventory item',unitofmesasure=item['unit'])
    add('inventories','inventoryid',inventoryid=type_id,departmentid=department,groupid=groups['Firehouse 51'],typeid=type_id,batch='DEMO-2026-10',note='Opening training stock',amount=item['amount'],timestamp=now,addedbyuserid=admin,unitid=units['Ambulance 61'] if i<2 else None,location='Medical cabinet' if i<2 else 'Equipment bay')
for i,name in enumerate(['Firefighter qualification','Paramedic qualification','Driver / operator endorsement']):
    add('departmentcertificationtypes','departmentcertificationtypeid',departmentcertificationtypeid=51001+i,departmentid=department,type=name,code='DEMO-CERT-'+str(i+1),description='Synthetic training certificate',issuingauthority='Academy Training Board (fictional)',defaultvaliditymonths=24,neverexpires=False,requiresverification=True,isactive=True,isdeleted=False,addedon=now,addedbyuserid=admin)
for i,person in enumerate(fixtures['people']):
    category=1 if person['role']=='Paramedic' else 2 if person['role']=='Driver / Operator' else 0
    add('personnelcertifications','personnelcertificationid',personnelcertificationid=51001+i,departmentid=department,userid=person['id'],name=['Firefighter qualification','Paramedic qualification','Driver / operator endorsement'][category],number='DEMO-CERT-'+str(i+1),type='Training',area='Software demonstration',expireson=now+dt.timedelta(days=20 if i==10 else 365),recievedon=now-dt.timedelta(days=365),issuedby='Academy Training Board (fictional)',departmentcertificationtypeid=51001+category,isdeleted=False,verifiedbyuserid=admin,verifiedon=now)
for i,(name,assignment) in enumerate([('A Shift — Firehouse 51',0),('Community standby signup',1)]):
    shift_id=51001+i
    add('shifts','shiftid',shiftid=shift_id,departmentid=department,name=name,code='A51' if i==0 else 'STBY',scheduletype=2 if i==0 else 1,assignmenttype=assignment,color='#2563eb' if i==0 else '#16a34a',startday=now-dt.timedelta(days=3),starttime='08:00',endtime='08:00' if i==0 else '12:00',hours=24 if i==0 else 4,allowpartials=False,requireapproval=i==1)
    add('shiftgroups','shiftgroupid',shiftgroupid=shift_id,shiftid=shift_id,departmentgroupid=groups['Firehouse 51'])
    add('shiftadmins','shiftadminid',shiftadminid=shift_id,shiftid=shift_id,userid=admin)
    for j in range(7): add('shiftdays','shiftdayid',shiftdayid=51001+i*100+j,shiftid=shift_id,day=now.replace(hour=0,minute=0,second=0)+dt.timedelta(days=j),processed=False)
    for j,person in enumerate(fixtures['people'][:10]):
        add('shiftpersons','shiftpersonid',shiftpersonid=51001+i*100+j,shiftid=shift_id,userid=person['id'],groupid=groups[person['group']])
        if i==1 and j<4:
            add('shiftsignups','shiftsignupid',shiftsignupid=51001+j,shiftid=shift_id,userid=person['id'],signuptimestamp=now,shiftday=now.replace(hour=0,minute=0,second=0)+dt.timedelta(days=1),denied=False,departmentgroupid=groups[person['group']],approvalpending=j==3)
for i,(kind,value) in enumerate([(5,'41.8721,-87.6523'),(3,'51001'),(1,'12'),(4,'false'),(53,'true')]):
    add('departmentsettings','departmentsettingid',departmentsettingid=51001+i,departmentid=department,settingtype=kind,setting=value)
for i,person in enumerate(fixtures['people']):
    add('messages','messageid',messageid=51001+i,subject='Welcome to the Firehouse 51 training exercise',isbroadcast=False,sendinguserid=admin,receivinguserid=person['id'],body='Review the onboarding guide, confirm your availability, and check the training calls. All data in this department is fictional.',senton=now,isdeleted=False,systemgenerated=False,type=0,departmentid=department)
for i,name in enumerate(['Training Warehouse', 'Community Centre', 'Fleet Workshop']):
    add('contacts','contactid',contactid=uid('contact:'+name),departmentid=department,contacttype=1,companyname=name+' (fictional)',email='training'+str(i+1)+'@firehouse51.example',physicaladdressid=51001,description='Fictional location contact for tutorial configuration.',officephonenumber='312-555-01'+str(i+10),locationgpscoordinates='41.8721,-87.6523',isdeleted=False,addedon=now,addedbyuserid=admin)
for i,name in enumerate(['Engine 51 — daily readiness', 'Ambulance 61 — equipment check', 'Firehouse 51 — facility opening']):
    definition=uid('checklist:'+str(i)); version=uid('checklist-version:'+str(i))
    form={'Name':name,'Instructions':'Training checklist for the software demonstration. Record the exercise result and add a note for a failed item.', 'Category':1 if i<2 else 4,'TargetType':1 if i<2 else 2,'PassThreshold':100,'RequireLocation':False,'RequiresIndependentWitness':False,
      'Sections':[{'Id':uid('checklist-section:'+str(i)),'Name':'Readiness check','Items':[{'Id':uid('checklist-item:'+str(i)+':'+str(j)),'Name':label,'Type':0,'Required':True,'Critical':j==0,'AllowNotApplicable':False,'RequireNoteOnFail':True,'Weight':1,'PassingValue':'true','CreateWorkOrderOnFail':j==0} for j,label in enumerate(['Equipment ready for the exercise','Stock and supplies recorded','Handover notes reviewed'])]}]}
    add('checklistdefinitions','id',id=definition,departmentid=department,content=form,revision=1,createdon=now,updatedon=now,createdby=admin,isprotected=False,currentversionid=version,publishedversion=1,retired=False)
    add('checklistdefinitionversions','id',id=version,departmentid=department,parentid=definition,content=form,revision=1,createdon=now,updatedon=now,createdby=admin,isprotected=False,version=1)
for i,title in enumerate(['Reserve Engine 51 — warning lamp investigation','Ambulance 61 — scheduled equipment inspection']):
    add('workorders','id',id=uid('workorder:'+str(i)),departmentid=department,content={'Fields':{'Title':title,'Description':'Fictional maintenance request for the tutorial. No real equipment fault is reported.','Currency':'USD','EstimatedCost':150 if i==0 else 75,'Steps':[{'Text':'Record the demonstration inspection result','Completed':False}]}},revision=1,createdon=now,updatedon=now,createdby=admin,isprotected=False,requestid=uid('workorder-request:'+str(i)),numberyear=now.year,numbersequence=i+1,type=i,priority=2 if i==0 else 1,status=2 if i==0 else 0,sourcetype=0,targetunitid=units['Reserve Engine 51'] if i==0 else units['Ambulance 61'],assignedtouserid=uid('person:herrmann') if i==0 else None,dueon=now+dt.timedelta(days=i+1),setunitoutofservice=i==0,restoreunitstateonclose=False,isdeleted=False,currencycode='USD')
if (ROOT/'feature-flags.json').exists():
    for flag in json.loads((ROOT/'feature-flags.json').read_text()):
        key=flag['flagkey']
        if key.startswith(('Ai.','Payments.','Security.','Chatbot.')) or key in ('Invoicing.OnlinePayments','Dispatch.AiTemplate','Admin.Assist'): continue
        add('featureflagoverrides','featureflagoverrideid',featureflagoverrideid=61000+flag['featureflagid'],featureflagid=flag['featureflagid'],departmentid=department,isenabled=True,flagvalue='true',reason='Academy tutorial fixture. Local checkout features may be unreleased; no production feature policy is changed.',expireson=now+dt.timedelta(days=365),createdon=now,createdbyuserid=admin)
# Preserve UI serial inserts after explicit demo identifiers.
sql.append("DO $$ DECLARE r record; m bigint; BEGIN FOR r IN SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' AND (column_default LIKE 'nextval(%' OR is_identity='YES') LOOP EXECUTE format('SELECT max(%I) FROM public.%I',r.column_name,r.table_name) INTO m; IF m IS NOT NULL THEN PERFORM setval(pg_get_serial_sequence('public.'||r.table_name,r.column_name),m,true); END IF; END LOOP; END $$;")
sql.append('COMMIT;')
(ROOT / 'private/seed.sql').write_text('\n'.join(sql)+'\n')
(ROOT / 'private/seed.sql').chmod(0o600)
(ROOT / 'seed-manifest.json').write_text(json.dumps({'department_id':department,'name':fixtures['department']['name'],'created_at':now.isoformat()+'Z','notice':fixtures['notice'],'character_reference':fixtures['character_reference'],'counts':counts,'users':[{'username':p['username'],'id':p['id'],'name':p['first']+' '+p['last'],'admin':p['admin']} for p in fixtures['people']]},indent=2))
print('Generated guarded Academy seed:',sum(counts.values()),'rows in',len(counts),'tables.')
