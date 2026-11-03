// Observe real DOM-titled map toolbar buttons; this never creates a passed review.
import fs from 'node:fs/promises';
import {createCapture} from './capture-evidence-raster-20261102.mjs';
export async function captureLayerControls(tab,sources,id,titles){
 const observed=await tab.playwright.evaluate(names=>names.map(name=>{
  const group=Array.from(document.querySelectorAll('[title]')).find(el=>el.title===name);
  const el=group?.querySelector('a[role="button"]');
  if(!el)throw new Error('Missing actual titled button: '+name);
  const r=el.getBoundingClientRect(),style=getComputedStyle(el);
  if(r.width<=0||r.height<=0||r.left<0||r.top<0||r.right>innerWidth||r.bottom>innerHeight||style.visibility==='hidden'||style.display==='none')throw new Error('Button not fully in viewport: '+name);
  return{accessible_name:group.title,role:el.getAttribute('role'),icon_only:true,provenance:'browser_dom',fully_visible:true,clipped:false,occluded:false,rect:{x:r.x,y:r.y,width:r.width,height:r.height},name_source:'actual parent DOM title; the child is the painted toolbar button'};
 }),titles);
 const folder='captures/expansion/core-map-layer-authoring-20261102';
 const capture=await createCapture(sources,folder);
 const row=await capture(tab,id,'Core',['Layer Elements','Add Layer']);
 const sx=row.width/row.css_viewport.width,sy=row.height/row.css_viewport.height;
 row.visible_controls=observed.map(c=>({...c,rect:{x:c.rect.x*sx,y:c.rect.y*sy,width:c.rect.width*sx,height:c.rect.height*sy}}));
 row.control_observation_note='Numeric DOM bounds and actual names only; Root must personally inspect this exact screenshot before supplying a control review.';
 const path=sources+'/'+folder+'/manifest.json';
 const rows=JSON.parse(await fs.readFile(path,'utf8'));const i=rows.findIndex(x=>x.id===id);rows[i]=row;await fs.writeFile(path,JSON.stringify(rows,null,2)+'\n');
 return row;
}
