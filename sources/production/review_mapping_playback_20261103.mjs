// Observe actual advancing playback through the fixture's normal UI controls.
// This records raw evidence only; it never creates a passed Root review.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const normal = value => String(value).replace(/\s+/g, ' ').trim();

function jpegSize(raw) {
  const bytes = Buffer.from(raw);
  for (let offset = 2; offset + 9 < bytes.length;) {
    if (bytes[offset] !== 255) { offset++; continue; }
    const marker = bytes[offset + 1], length = bytes.readUInt16BE(offset + 2);
    if ([192, 193, 194].includes(marker)) {
      return {width: bytes.readUInt16BE(offset + 7), height: bytes.readUInt16BE(offset + 5)};
    }
    offset += length + 2;
  }
  throw new Error('Expected an actual browser JPEG screenshot.');
}

export async function observeAdministrationPlayback(tab, sourceRoot, key, position) {
  const known={"road":["core-unit-road-guidance","ffa195b4b36922e00835e7e0448e6a8e2f33e9ff9efd38dd0d731bccceaa2768"],"layers":["core-map-layer-authoring","47c67bb6bfc506eadc40e3a9675630ba79e1abbbf531d27b4b44454e720f7400"],"indoor":["core-indoor-call-location","3c02405e2ab2060d856f8c65f5e004e22ac07b2da9d73bba2f9ff21dd911702c"],"kml":["core-kml-kmz-import","11215e3017f033bc7f8f3a20dcbeed971262e7b6f4710543cf518217e0120bb0"]};
  if(!known[key])throw new Error('Unknown lesson.');
  const [LESSON,MASTER]=known[key];
  const labels = {beginning: 'Beginning', middle: 'Middle', end: 'End'};
  if (!labels[position]) throw new Error('Choose one declared playback position.');
  const video = `${sourceRoot}/expansion/rendered/${LESSON}-take-01/${LESSON}.mp4`;
  if (sha(await fs.readFile(video)) !== MASTER) throw new Error('Changed rendered master.');
  const mapping = JSON.parse(await fs.readFile(`${sourceRoot}/expansion/plans/${LESSON}${{"core-unit-road-guidance":"-complete-correspondence-20261103-v2","core-map-layer-authoring":"-complete-correspondence-20261103","core-indoor-call-location":"-complete-correspondence-20261103-v2","core-kml-kmz-import":"-complete-correspondence-20261103"}[LESSON]}/correspondence.proposed.json`, 'utf8'));
  await tab.ax.scroll([1100, 200], 'up', 1);
  const controls = await tab.ax.get('state', {disableDiffing: true});
  const button = name => {
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const match = controls.match(new RegExp(`^\\s*(\\d+) button ${escaped}(?:,|$)`, 'm'));
    if (!match) throw new Error(`Missing actual accessible button: ${name}`);
    return Number(match[1]);
  };
  await tab.ax.click(button(labels[position]));
  await tab.ax.click(button('Enable native captions'));
  await new Promise(resolve => setTimeout(resolve, 300));
  await tab.ax.click(button('Observe actual playback state'));
  const first = JSON.parse(await tab.playwright.evaluate(() => document.querySelector('#observation').textContent));
  await new Promise(resolve => setTimeout(resolve, 900));
  await tab.ax.click(button('Observe actual playback state'));
  const row = JSON.parse(await tab.playwright.evaluate(() => document.querySelector('#observation').textContent));
  const cue = mapping.cues.find(item => item.start <= row.current_time && row.current_time < item.end);
  if (first.position !== position || row.position !== position || row.video_sha256 !== MASTER ||
      row.previous_time !== first.current_time || row.current_time < first.current_time + 0.25 ||
      row.paused || row.ended || row.media_error || row.console_errors.length ||
      row.ready_state !== 4 || row.network_state !== 1 ||
      row.video_width !== 1920 || row.video_height !== 1080 ||
      !row.current_src.includes(`${LESSON}.mp4?v=${MASTER}`) ||
      !cue || cue.end - row.current_time < 1.1 || row.captions.mode !== 'showing' ||
      normal(row.captions.text) !== normal(cue.text)) {
    throw new Error(`Playback observation does not yet establish a clean advancing ${position} sample.`);
  }
  if ((position === 'beginning' && !(row.current_time < 30)) ||
      (position === 'middle' && !(row.current_time > 0.3 * row.duration_seconds && row.current_time < 0.7 * row.duration_seconds)) ||
      (position === 'end' && !(row.current_time > 0.85 * row.duration_seconds && row.current_time < row.duration_seconds))) {
    throw new Error('Observation is outside its declared playback range.');
  }
  // AX clicks preserve the framing of the already visible controls. Confirm
  // that the screenshot still contains the complete video rectangle.
  const display = await tab.playwright.evaluate(() => {
    const video = document.querySelector('video');
    const rect = video.getBoundingClientRect();
    return {current_time: video.currentTime, top: rect.top, bottom: rect.bottom,
      viewport_height: document.documentElement.clientHeight};
  });
  if (display.top < 0 || display.bottom > display.viewport_height ||
      Math.abs(display.current_time - row.current_time) > 0.5 ||
      display.current_time < cue.start || display.current_time >= cue.end) {
    throw new Error('The complete playing video and the observed caption must remain visible.');
  }
  const bytes = await tab.screenshot({fullPage: false});
  const relative = `expansion/rendered/${LESSON}-take-01/playback/root-live-approved-20261103`;
  const directory = `${sourceRoot}/${relative}`;
  await fs.mkdir(directory, {recursive: true});
  row.screenshot = {file: `${relative}/${position}.full-video.actual.jpg`, sha256: sha(bytes), ...jpegSize(bytes)};
  row.screenshot_media_state = display;
  row.matched_caption_cue = cue.cue;
  row.review_state = 'raw_actual_observation_requires_personal_screenshot_review';
  await fs.writeFile(`${directory}/${position}.full-video.actual.jpg`, bytes, {flag: 'wx'});
  await fs.writeFile(`${directory}/${position}.full-video.actual-observation.json`, JSON.stringify(row, null, 2) + '\n', {flag: 'wx'});
  return {row, bytes};
}
