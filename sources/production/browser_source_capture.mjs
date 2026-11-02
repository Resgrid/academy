// Capture real browser viewports through the supplied, supported browser tab.
// This helper has no browser connection, credentials, login or app mutation API.
export async function createSourceRecorder({tab, fs, crypto, sourcesRoot, batch, emitImage, write}) {
  if (!/^[a-z0-9-]+$/.test(batch)) throw new Error('Use a simple new capture batch name.');
  const relative = `captures/expansion/${batch}/`;
  const directory = `${sourcesRoot}/${relative}`;
  await fs.mkdir(directory, {recursive: true});
  const manifest = `${directory}manifest.json`;
  try { await fs.access(manifest); throw new Error('Preserve an existing batch manifest.'); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  const rows = [];
  return async function capture(id, requiredLabels, state) {
    if (!/^[a-z0-9-]+$/.test(id)) throw new Error('Use a simple new capture ID.');
    const visible = await tab.playwright.evaluate(() => {
      const onScreen = e => { const r=e.getBoundingClientRect(); return r.width>0 && r.height>0 && r.bottom>0 && r.top<innerHeight; };
      return {
        url: location.href,
        populatedPassword: Array.from(document.querySelectorAll('input[type=password]')).some(e => onScreen(e) && Boolean(e.value)),
        labels: Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,label,a,button,th,td')).filter(onScreen).map(e=>e.innerText.trim()).filter(Boolean),
        fields: Array.from(document.querySelectorAll('input:not([type=hidden]):not([type=password]),select,textarea')).filter(onScreen).map(e=>({
          tag:e.tagName.toLowerCase(), id:e.id, type:e.type??null, value:e.value??e.innerText,
          checked:e.checked??null, selected_text:e.tagName==='SELECT'?e.options[e.selectedIndex]?.text:null
        }))
      };
    });
    if (/\/Account\//.test(visible.url) || visible.populatedPassword) throw new Error('Normal sign-in/privacy review required; no capture retained.');
    const dom = await tab.playwright.domSnapshot();
    const bytes = Buffer.from(await tab.screenshot({fullPage:false}));
    const jpeg = bytes[0]===255 && bytes[1]===216;
    let width, height;
    if (!jpeg) {
      if (!bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))) throw new Error('Unsupported screenshot format.');
      width=bytes.readUInt32BE(16); height=bytes.readUInt32BE(20);
    } else {
      for (let position=2;position+9<bytes.length;) {
        if (bytes[position]!==255) { position++; continue; }
        const marker=bytes[position+1];
        if ([192,193,194].includes(marker)) { height=bytes.readUInt16BE(position+5);width=bytes.readUInt16BE(position+7);break; }
        position+=2+bytes.readUInt16BE(position+2);
      }
    }
    if (!width || !height) throw new Error('Unknown screenshot dimensions.');
    const extension=jpeg?'jpg':'png';
    const digest=data=>crypto.createHash('sha256').update(data).digest('hex');
    const row={id,app:'Core',kind:'application_screenshot',file:relative+id+'.'+extension,
      sha256:digest(bytes),width,height,provenance:{method:'browser_screenshot',url:visible.url,captured_at:new Date().toISOString()},
      visible_labels:visible.labels,visible_field_text:visible.fields,dom_file:relative+id+'.dom.txt',dom_sha256:digest(dom),
      required_labels:requiredLabels,state,eligible_for_lesson:false,visual_review:'pending_actual_image_review'};
    await fs.writeFile(directory+id+'.'+extension,bytes,{flag:'wx'});
    await fs.writeFile(directory+id+'.dom.txt',dom,{flag:'wx'});
    rows.push(row);
    await fs.writeFile(manifest,JSON.stringify(rows,null,2)+'\n');
    write({id,width,height,sha256:row.sha256});
    await emitImage(bytes);
    return row;
  };
}
