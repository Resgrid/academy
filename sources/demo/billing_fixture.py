"""Read-only, local Academy billing responses. No provider or payment operations."""
import datetime, hmac, json, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

CONFIG = json.loads(Path('/config/ResgridConfig.json').read_text())
KEY = CONFIG['ApiConfig.BackendInternalApikey']
NOW = datetime.datetime.now(datetime.timezone.utc)
def stamp(days): return (NOW+datetime.timedelta(days=days)).isoformat()
PLAN = {'PlanId':33,'Name':'Academy local demo — no billing','Cost':0,'Frequency':1,'Quantity':1,
        'PlanLimits':[{'PlanId':33,'LimitType':i,'LimitValue':1000} for i in range(1,7)]}
ADDONS = [
 {'PlanAddonId':'456ed5d4-57e1-4882-b433-1d3cc239103d','AddonType':1,'Cost':0,'ExternalId':'ACADEMY-PTT'},
 {'PlanAddonId':'8a82f517-13db-4950-a514-d990248a67e6','AddonType':3,'Cost':0,'ExternalId':'ACADEMY-READINESS'},
 {'PlanAddonId':'8c2f0d6e-5b1a-4f2e-9d3c-7a6b5e4d3c2b','AddonType':4,'Cost':0,'ExternalId':'ACADEMY-BUSINESS'}]
PAYMENT={'PaymentId':51001,'DepartmentId':51,'PlanId':33,'Plan':PLAN,'Method':0,'Successful':True,
 'IsTrial':False,'PurchaseOn':stamp(-1),'EffectiveOn':stamp(-1),'EndingOn':stamp(365),'Amount':0,
 'Cancelled':False,'TransactionId':'ACADEMY-TRAINING-ONLY','Description':'Local training fixture; no charge'}
class Handler(BaseHTTPRequestHandler):
 def respond(self,status,data):
  body=json.dumps({'Data':data,'Success':status==200,'Message':'ACADEMY LOCAL FIXTURE — NO REAL BILLING'}).encode()
  self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
 def serve(self):
  if not hmac.compare_digest(self.headers.get('X-API-Key',''),KEY): return self.respond(401,None)
  url=urlparse(self.path); operation=url.path.rsplit('/',1)[-1]; query=parse_qs(url.query)
  length=int(self.headers.get('Content-Length','0')); body=json.loads(self.rfile.read(length)) if length else {}
  department=int(query.get('departmentId',[body.get('DepartmentId',body.get('departmentId',51))])[0])
  if department!=51: return self.respond(404,None)
  if operation in ('GetCurrentPlanForDepartment','GetPlanById','GetPlanByExternalId'): data=PLAN
  elif operation=='GetPlanCountsForDepartment': data={'UsersCount':14,'GroupsCount':6,'UnitsCount':6}
  elif operation=='GetCurrentPaymentForDepartment': data=PAYMENT
  elif operation in ('GetAllPaymentsForDepartment','GetAllNonFreePaymentsForDepartment'): data=[PAYMENT]
  elif operation=='GetAllAddonPlansByType': data=[a for a in ADDONS if a['AddonType']==int(query.get('type',['0'])[0])]
  elif operation=='GetCurrentPaymentAddonsForDepartmentPost':
   ids=body.get('PlanAddonIds',body.get('planAddonIds',[]))
   data=[{'PaymentAddonId':str(uuid.uuid5(uuid.NAMESPACE_URL,'academy:'+a['PlanAddonId'])),'DepartmentId':51,
    'PlanAddonId':a['PlanAddonId'],'PurchaseOn':stamp(-1),'EffectiveOn':stamp(-1),'EndingOn':stamp(365),
    'Amount':0,'Description':'Local tutorial entitlement; no charge','TransactionId':'ACADEMY-TRAINING-ONLY',
    'SubscriptionId':'ACADEMY-NO-PROVIDER','Data':'{}','IsCancelled':False,'Quantity':1} for a in ADDONS if a['PlanAddonId'] in ids]
  elif operation in ('GetHasActiveSubForDepartmentFromStripe',): data=True
  elif operation in ('GetCurrentPlanAddonsForDepartmentFromStripe',): data=ADDONS
  elif operation in ('GetPlanAddonById','GetPTTAddonPlanForDepartmentFromStripe','GetPTTAddonForCurrentSub'):
   data=next((a for a in ADDONS if a['PlanAddonId']==query.get('planAddonId',[ADDONS[0]['PlanAddonId']])[0]),None)
  else: return self.respond(404,None)
  self.respond(200,data)
 def do_GET(self): self.serve()
 def do_POST(self):
  if self.path.split('?')[0].endswith('/GetCurrentPaymentAddonsForDepartmentPost'): self.serve()
  else: self.respond(405,None)
 def log_message(self,format,*args): pass
ThreadingHTTPServer(('0.0.0.0',8090),Handler).serve_forever()
