// Wait only for observed visible page-fade opacity. This does not approve screenshots
// or infer that images, map providers, requests or application operations succeeded.
export async function waitForVisiblePageFade(tab) {
  let states=[];
  for(let attempt=0;attempt<10;attempt++) {
    states=await tab.playwright.evaluate(()=>Array.from(document.querySelectorAll('.animated')).filter(el=>{const r=el.getBoundingClientRect();const s=getComputedStyle(el);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}).map(el=>({class_name:el.className,opacity:Number(getComputedStyle(el).opacity),animation:getComputedStyle(el).animationName})));
    if(states.every(s=>s.opacity>=.99))return {method:'read_only_visible_DOM_computed_style',states};
    await new Promise(resolve=>setTimeout(resolve,150));
  }
  throw new Error('Visible page fade has not finished; do not capture it as a loaded application view.');
}
