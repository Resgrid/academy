"""Create the explicitly fictional receipt uploaded through the normal training UI."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib,json
S=Path(__file__).resolve().parents[1]
out=S/'demo/scenarios/assets';out.mkdir(exist_ok=True)
image=Image.new('RGB',(900,620),'white');draw=ImageDraw.Draw(image)
font=ImageFont.load_default(size=26);title=ImageFont.load_default(size=38)
draw.rectangle((24,24,876,596),outline='#94a3b8',width=3)
draw.text((55,48),'TRAINING ONLY',font=title,fill='#9f1239')
draw.text((55,106),'Fictional fuel receipt',font=title,fill='#172554')
lines=['Local Academy software exercise','Reference: TRAIN-FUEL-02','Date: November 2, 2026','Type: Fuel','Description: Demo community-support vehicle','Total: USD 24.50','No purchase or payment occurred.']
for i,line in enumerate(lines):draw.text((55,182+i*49),line,font=font,fill='#111827')
p=out/'deployment-fuel-receipt-20261102.png';image.save(p)
(out/'deployment-fuel-receipt-20261102.json').write_text(json.dumps({'kind':'fictional_training_receipt_fixture','date':'2026-11-02','reference':'TRAIN-FUEL-02','expense_type':'Fuel','amount':'24.50','currency':'USD','purchase_or_payment':False,'image_file':p.relative_to(S).as_posix(),'image_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generator_file':Path(__file__).relative_to(S).as_posix()},indent=2)+'\n')
print(p)
