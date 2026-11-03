// Add actual DOM title/ARIA-label evidence for a specifically observed icon.
// Source pixels are unchanged. Personal image review remains separate.
import fs from 'node:fs/promises';
export async function captureExplicitIcon(tab,capture,sourceRoot,folder,id,app,required,selector) {
  const observed=await tab.playwright.locator(selector).evaluate(e=>{
    const r=e.getBoundingClientRect();const name=e.getAttribute('aria-label')||e.getAttribute('title');
    if(!name||e.innerText.trim())throw new Error('Expected a specifically named, icon-only actual control.');
    if(r.left<0||r.top<0||r.right>innerWidth||r.bottom>innerHeight)throw new Error('Control is clipped.');
    for(const [x,y] of [[r.left+1,r.top+1],[r.right-1,r.top+1],[r.left+1,r.bottom-1],[r.right-1,r.bottom-1],[r.left+r.width/2,r.top+r.height/2]]){const hit=document.elementFromPoint(x,y);if(hit!==e&&!e.contains(hit))throw new Error('Control is obstructed.');}
    return {accessible_name:name,role:e.getAttribute('role')||e.tagName.toLowerCase(),rect:{x:r.x,y:r.y,width:r.width,height:r.height},css_viewport:{width:innerWidth,height:innerHeight},icon_only:true,provenance:'browser_dom'};
  });
  const row=await capture(tab,id,app,required);const sx=row.width/observed.css_viewport.width,sy=row.height/observed.css_viewport.height;
  const rect=Object.fromEntries(Object.entries(observed.rect).map(([k,v])=>[k,v*(['x','width'].includes(k)?sx:sy)]));
  row.visible_controls=[{accessible_name:observed.accessible_name,role:observed.role,rect,icon_only:true,provenance:'browser_dom'}];
  row.control_observation={css_rect:observed.rect,css_viewport:observed.css_viewport,raw_raster_scale:{x:sx,y:sy},method:'Actual named DOM icon with full-box corner/centre hit tests, followed by unchanged browser screenshot. Personal pixel review still required.'};
  const path=`${sourceRoot}/${folder}/manifest.json`;const rows=JSON.parse(await fs.readFile(path,'utf8'));if(!Array.isArray(rows))throw new Error('Expected array manifest.');
  const at=rows.findIndex(x=>x.id===id);if(at<0)throw new Error('Missing actual capture.');rows[at]=row;await fs.writeFile(path,JSON.stringify(rows,null,2)+'\n');return row;
}
