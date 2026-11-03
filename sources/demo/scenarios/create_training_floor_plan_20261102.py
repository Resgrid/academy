"""Create a fictional software-training floor plan. Not a real building or safety plan."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent/'assets';ROOT.mkdir(exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
def font(n):return ImageFont.truetype(FONT,n)
im=Image.new('RGB',(1600,1000),'#f7fafc');d=ImageDraw.Draw(im)
d.rectangle((0,0,1600,140),fill='#162b42');d.text((55,28),'COMMUNITY COORDINATION CENTRE',font=font(46),fill='white');d.text((58,88),'GROUND FLOOR  |  FICTIONAL SOFTWARE TRAINING EXERCISE',font=font(24),fill='#a9d9e9')
rooms=[(100,210,610,480,'Briefing room','#e7f3fb'),(610,210,1110,480,'Training room','#e7f3fb'),(1110,210,1500,480,'Equipment store','#eff5e4'),(100,610,610,850,'Consultation room','#edf3fa'),(610,610,1110,850,'Team workspace','#edf3fa'),(1110,610,1500,850,'Handover room','#fff1dd')]
for x1,y1,x2,y2,label,color in rooms:
 d.rectangle((x1,y1,x2,y2),fill=color,outline='#263c51',width=6);box=d.textbbox((0,0),label,font=font(29));w=box[2]-box[0];d.text(((x1+x2-w)/2,(y1+y2)/2-17),label,font=font(29),fill='#18384d')
d.rectangle((100,480,1500,610),fill='#e0e9ef',outline='#263c51',width=6);d.text((575,520),'Central corridor',font=font(30),fill='#18384d')
for x in [350,850,1300]:
 for y in [480,610]:d.line((x-40,y,x+40,y),fill='#f7fafc',width=10)
d.text((100,885),'TRAINING ONLY — no real room numbers, routes, occupants or operational guidance',font=font(24),fill='#354c60');d.text((100,930),'Diagram is schematic and is not to scale.',font=font(24),fill='#354c60')
p=ROOT/'community-centre-ground-floor-training-20261102.png';im.save(p);print(p)
