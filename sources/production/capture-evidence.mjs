/** Retain real browser screenshots, their visible controls and reproducible hashes. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

export function redact(text) {
  return String(text).replace(/([?&](?:access_token|token|key)=)[^&\s"<>]+/gi, '$1[REDACTED]')
    .replace(/\b(?:pk|sk)\.[A-Za-z0-9_.-]{16,}/g, '[REDACTED_MAP_KEY]');
}

export async function createCapture(sources, folder = 'captures/expansion') {
  const directory = path.resolve(sources, folder);
  if (!directory.startsWith(path.resolve(sources) + path.sep)) throw new Error('Unsafe capture directory');
  await fs.mkdir(directory, { recursive: true });
  const manifest = path.join(directory, 'manifest.json');
  let shots = [];
  try { shots = JSON.parse(await fs.readFile(manifest, 'utf8')); } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  if (!Array.isArray(shots)) {
    throw new Error('This recorder requires a raw array manifest. Choose a new capture directory; do not append to a {captures: []} recorder or a reviewed {screenshots: []} snapshot.');
  }
  return async function capture(tab, id, app, required = []) {
    if (!/^[a-z0-9-]+$/.test(id)) throw new Error('Invalid capture identifier');
    const witness = await tab.playwright.evaluate(() => {
      const labels = [];
      const visible = (el, measured, allowPaintedAriaDuplicate = false) => {
        const rect = measured || el.getBoundingClientRect();
        const style = getComputedStyle(el);
        if (!(rect.width && rect.height && rect.top >= 0 && rect.bottom <= innerHeight &&
          rect.left >= 0 && rect.right <= innerWidth && style.visibility !== 'hidden' &&
          style.display !== 'none' && (allowPaintedAriaDuplicate || el.getAttribute('aria-hidden') !== 'true'))) return false;
        for (let parent = el; parent; parent = parent.parentElement) {
          const css = getComputedStyle(parent);
          if (css.visibility === 'hidden' || css.display === 'none' || Number(css.opacity) === 0) return false;
          if (parent === el) continue;
          // Root scrolling clips at the viewport, not the body's translated box.
          if (parent.tagName === 'BODY' || parent.tagName === 'HTML') continue;
          const clip = parent.getBoundingClientRect();
          if (/(auto|scroll|hidden|clip)/.test(css.overflowY) && (rect.top < clip.top || rect.bottom > clip.bottom)) return false;
          if (/(auto|scroll|hidden|clip)/.test(css.overflowX) && (rect.left < clip.left || rect.right > clip.right)) return false;
        }
        return true;
      };
      for (const el of document.querySelectorAll('h1,h2,h3,h4,h5,h6,label,button,a,span,strong,b,small,li,dt,dd,td,th,p,legend,pre,code,div')) {
        // Container textContent includes collapsed menus and every select option.
        // Keep direct labels and separately capture only the selected option.
        if (el.querySelector('select')) continue;
        if (el.tagName === 'DIV' && el.querySelector('div,select,input,textarea,button,h1,h2,h3,label')) continue;
        const text = el.innerText?.trim() || '';
        if (text && text.length <= 240 && visible(el)) labels.push(text);
      }
      // Core also uses direct text nodes beside controls. Accept these only when
      // their complete containing element is visible; never read select options.
      for (const parent of document.querySelectorAll('div,label,span,p,td,th')) {
        if (!visible(parent)) continue;
        for (const node of Array.from(parent.childNodes || [])) {
          if (node.nodeType !== 3) continue;
          const text = node.textContent?.trim() || '';
          if (text && text.length <= 240) labels.push(text);
        }
      }
      const exposedCredential = Array.from(document.querySelectorAll('input:not([type=password]),textarea'))
        .some(el => visible(el, undefined, true) && /\b(?:pk|sk)\.[A-Za-z0-9_.-]{16,}|\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}/.test(el.value || ''));
      if (exposedCredential) throw new Error('A credential-bearing input must be hidden before capture.');
      const fieldText = [];
      for (const el of document.querySelectorAll('input:not([type=password]):not([type=hidden]),textarea,select')) {
        // React Native Web paints read-only display inputs with aria-hidden;
        // CSS geometry still must prove they are inside the visible viewport.
        if (!visible(el, undefined, true)) continue;
        if (el.tagName === 'SELECT') {
          for (const option of el.selectedOptions) {
            if (!el.multiple || visible(option)) labels.push(option.textContent || '');
          }
        } else {
          const placeholder = el.getAttribute('placeholder') || '';
          const textBearing = !['checkbox', 'radio', 'file', 'hidden', 'range', 'submit', 'button', 'color', 'image', 'reset'].includes(el.type);
          if (!textBearing) continue;
          const value = el.value || '';
          labels.push(placeholder);
          // Text painted inside a form field is absent from innerText. Keep it
          // alongside labels so reviewers can verify the displayed selection
          // and entered text, rather than accepting an off-screen option.
          if (value) labels.push(value);
          const rect = el.getBoundingClientRect();
          fieldText.push({ placeholder, value, tag: el.tagName.toLowerCase(),
            aria_hidden_duplicate: el.getAttribute('aria-hidden') === 'true',
            rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height } });
        }
      }
      return { url: location.href, width: innerWidth, height: innerHeight,
        visible_labels: [...new Set(labels)].filter(Boolean),
        visible_field_text: fieldText, body_text: document.body.innerText };
    });
    if (/An unhandled exception|Something went wrong|access token is required to use Mapbox|503 Service Unavailable|404.*Not Found/.test(witness.body_text))
      throw new Error('Capture rejected: application error view ' + id);
    const missing = required.filter(label => !witness.visible_labels.some(value => value.toLowerCase().includes(label.toLowerCase())));
    if (missing.length) throw new Error('Controls not in viewport: ' + JSON.stringify(missing));
    const bytes = await tab.screenshot({ fullPage: false });
    const file = folder + '/' + id + '.jpg';
    await fs.writeFile(path.join(sources, file), bytes);
    const record = { id, app, kind: 'application_screenshot', file,
      sha256: crypto.createHash('sha256').update(bytes).digest('hex'),
      width: witness.width, height: witness.height,
      provenance: { method: 'browser_screenshot', url: redact(witness.url), captured_at: new Date().toISOString() },
      visible_labels: witness.visible_labels.map(redact),
      visible_field_text: witness.visible_field_text.map(field => ({ ...field,
        value: redact(field.value), placeholder: redact(field.placeholder) })) };
    shots = shots.filter(shot => shot.id !== id).concat(record);
    await fs.writeFile(manifest, JSON.stringify(shots, null, 2) + '\n');
    await fs.writeFile(path.join(directory, id + '.txt'), redact(witness.body_text));
    return record;
  };
}
