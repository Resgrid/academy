import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';

// Calls only the supported Tab browser API. It never changes the page, signs in,
// reads application stores, injects sessions, infers capture success or fabricates UI.
export async function captureApplication(tab, options, helpers) {
  const {app, directory, relativeDirectory, id, requiredLabels = [], state = 'Observed actual application view'} = options;
  const {redact, jpegSize} = helpers;
  const dom = await tab.playwright.evaluate(() => {
    const width = document.documentElement.clientWidth, height = document.documentElement.clientHeight;
    // Root overflow clips at the viewport, not at the root's scrolled box.
    // With visible root overflow, HTML also propagates BODY overflow there.
    // https://www.w3.org/TR/css-overflow-3/#overflow-propagation
    function viewportOverflow(p, style) {
      const root = document.documentElement;
      if (p === root) return true;
      if (p !== document.body || p.parentElement !== root || root.tagName !== 'HTML') return false;
      const rootStyle = getComputedStyle(root);
      return rootStyle.overflowX === 'visible' && rootStyle.overflowY === 'visible'
        && style.display !== 'none' && (!style.contain || style.contain === 'none')
        && (!rootStyle.contain || rootStyle.contain === 'none');
    }
    // RN navigation can retain a login screen with zero-size fields after a normal login.
    // Still reject every painted credential intersection, including partially clipped inputs.
    function credentialPainted(e) {
      const r = e.getBoundingClientRect();
      let left = Math.max(0,r.left), top = Math.max(0,r.top), right = Math.min(width,r.right), bottom = Math.min(height,r.bottom);
      if (r.width <= 0 || r.height <= 0) return false;
      for (let p=e;p;p=p.parentElement) {
        const style=getComputedStyle(p), bounds=p.getBoundingClientRect();
        if (style.display==='none' || style.visibility==='hidden' || Number(style.opacity)===0) return false;
        if (p!==e && !viewportOverflow(p,style) && ['auto','scroll','hidden','clip'].includes(style.overflowX)) { left=Math.max(left,bounds.left);right=Math.min(right,bounds.right); }
        if (p!==e && !viewportOverflow(p,style) && ['auto','scroll','hidden','clip'].includes(style.overflowY)) { top=Math.max(top,bounds.top);bottom=Math.min(bottom,bounds.bottom); }
      }
      return right>left && bottom>top;
    }
    // Boolean settings and action controls may mention password/email in their
    // names. Only text-bearing inputs can contain typed credentials.
    const credentialTextTypes = new Set(['text','password','email','search','tel','url','number']);
    if ([...document.querySelectorAll('input')].some(e => credentialTextTypes.has(e.type) && e.value && credentialPainted(e) && (e.type === 'password' || e.type === 'email' || /username|password|email/i.test([e.autocomplete,e.name,e.placeholder].join(' '))))) {
      throw new Error('A visible credential-filled form cannot be captured.');
    }
    function rect(element, paintedReadOnlyInput = false) {
      const r = element.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0 || r.left < 0 || r.top < 0 || r.right > width + 0.5 || r.bottom > height + 0.5) return null;
      for (let p = element; p; p = p.parentElement) {
        const s = getComputedStyle(p), b = p.getBoundingClientRect();
        const duplicate = paintedReadOnlyInput && p === element && element.tagName === 'INPUT' && element.readOnly;
        if (s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) === 0 || (p.getAttribute('aria-hidden') === 'true' && !duplicate)) return null;
        if (p !== element && !viewportOverflow(p,s) && ((['auto','scroll','hidden','clip'].includes(s.overflowY) && (r.top < b.top - 0.5 || r.bottom > b.bottom + 0.5)) || (['auto','scroll','hidden','clip'].includes(s.overflowX) && (r.left < b.left - 0.5 || r.right > b.right + 0.5)))) return null;
      }
      return {x:r.x,y:r.y,width:r.width,height:r.height};
    }
    const clean = text => String(text || '').trim().replace(/\s+/g, ' ');
    const labels = [...document.querySelectorAll('body *')].filter(e => !['SCRIPT','STYLE','NOSCRIPT','OPTION'].includes(e.tagName) && rect(e)).flatMap(e => {
      const direct = clean([...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' '));
      const leaf = e.children.length === 0 ? clean(e.innerText || e.textContent) : '';
      return [...new Set([direct,leaf].filter(Boolean))];
    });
    const fields = [...document.querySelectorAll('input,textarea')].filter(e => e.tagName !== 'INPUT' || !['checkbox','radio','file','hidden','range','submit','button','color'].includes(e.type)).map(e => ({text:e.value || e.getAttribute('placeholder') || '',kind:e.value ? 'value' : 'placeholder',rect:rect(e,true),aria_hidden_duplicate:e.getAttribute('aria-hidden') === 'true' && e.readOnly})).filter(x => x.text && x.rect);
    // A closed native select paints the selected option's label, not its stored
    // value or every option in the menu. List boxes need their own image review.
    const selections = [...document.querySelectorAll('select')].filter(e => !e.multiple && Number(e.size || 0) <= 1).map(e => ({text:clean(e.selectedOptions[0]?.label || e.selectedOptions[0]?.textContent),kind:'selected_option',rect:rect(e)})).filter(x => x.text && x.rect);
    const controls = [...document.querySelectorAll('button,[role="button"]')].map(e => ({accessible_name:e.getAttribute('aria-label') || e.getAttribute('title') || '',role:e.getAttribute('role') || e.tagName.toLowerCase(),rect:rect(e),icon_only:!clean(e.innerText),provenance:'browser_dom'})).filter(x => x.accessible_name && x.rect && x.icon_only);
    return {labels:[...labels,...fields.map(x => x.text),...selections.map(x => x.text)],fields:[...fields,...selections],controls};
  });
  const snapshot = redact(await tab.playwright.domSnapshot());
  const bytes = await tab.screenshot({fullPage:false});
  const url = redact(await tab.url()), capturedAt = new Date().toISOString();
  const hash = data => createHash('sha256').update(data).digest('hex');
  const row = {id,app,kind:'application_screenshot',file:`${relativeDirectory}/${id}.jpg`,sha256:hash(bytes),...jpegSize(bytes),url,captured_at:capturedAt,visible_labels:dom.labels.map(redact),visible_field_text:dom.fields.map(x => ({...x,text:redact(x.text)})),visible_controls:dom.controls.map(x => ({...x,accessible_name:redact(x.accessible_name)})),dom_file:`${relativeDirectory}/${id}.dom.txt`,dom_sha256:hash(snapshot),state,required_labels:requiredLabels,visual_review:'pending_actual_image_review',eligible_for_lesson:false,provenance:{method:'browser_screenshot',url,captured_at:capturedAt},label_observation_method:'Actual CSS-visible DOM text, painted input values and closed native-select selected labels, within viewport and ancestor clips. Icon names/roles/rects are DOM observations. Separate image review must remove occlusion and bind hashes before use.'};
  row.missing_required_labels = requiredLabels.filter(name => !row.visible_labels.some(value => value.toLowerCase().includes(name.toLowerCase())) && !row.visible_controls.some(control => control.accessible_name.toLowerCase() === name.toLowerCase()));
  await fs.mkdir(directory,{recursive:true});
  const manifestPath = `${directory}/manifest.json`;
  let manifest;
  try { manifest = JSON.parse(await fs.readFile(manifestPath,'utf8')); }
  catch (error) { if (error.code !== 'ENOENT') throw error; manifest = {app,capture_method:'Actual browser screenshots with separate manual review',captures:[]}; }
  if (!manifest || Array.isArray(manifest) || !Array.isArray(manifest.captures)) {
    throw new Error('This recorder requires a raw {captures: []} manifest. Choose a new capture directory; do not append to an array recorder or a reviewed {screenshots: []} snapshot.');
  }
  if (manifest.captures.some(capture => capture.id === id)) throw new Error(`Duplicate capture id: ${id}`);
  await fs.writeFile(`${directory}/${id}.jpg`,bytes);
  await fs.writeFile(`${directory}/${id}.dom.txt`,snapshot);
  manifest.captures.push(row);
  await fs.writeFile(manifestPath,JSON.stringify(manifest,null,2)+'\n');
  return {row,bytes};
}
