// Raw installed-page evidence only; the caller must personally view the image.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
export async function observeInstalledMapping(tab, sources, id, master, chapter) {
  const state = await tab.ax.get('state', {disableDiffing: true});
  const line = state.split('\n').find(row => row.trim().endsWith(`button ${chapter}`));
  if (!line) throw new Error('Chapter button missing from actual page.');
  await tab.ax.click(Number(line.trim().split(' ')[0]));
  await new Promise(resolve => setTimeout(resolve, 3100));
  const read = () => tab.playwright.evaluate(() => {
    const v = document.querySelector('video'), r = v.getBoundingClientRect();
    return {current_time: v.currentTime, paused: v.paused, ended: v.ended,
      ready_state: v.readyState, media_error: v.error ? v.error.code : null,
      current_src: v.currentSrc, video_width: v.videoWidth, video_height: v.videoHeight,
      top: r.top, bottom: r.bottom, viewport_height: document.documentElement.clientHeight};
  });
  const first = await read();
  await new Promise(resolve => setTimeout(resolve, 900));
  const row = await read();
  if (row.current_time <= first.current_time + .25 || row.paused || row.ended ||
      row.ready_state !== 4 || row.media_error !== null || row.video_width !== 1920 ||
      row.video_height !== 1080 || !row.current_src.endsWith(`/assets/${master}.mp4`) ||
      row.top < 0 || row.bottom > row.viewport_height) throw new Error('Incomplete installed playback evidence.');
  row.previous_time = first.current_time;
  row.video_sha256 = master;
  row.chapter = chapter;
  row.page = await tab.url();
  row.review_state = 'raw_actual_observation_requires_personal_screenshot_review';
  const bytes = await tab.screenshot({fullPage: false});
  const relative = `expansion/rendered/${id}-take-01/playback/installed-20261103`;
  const directory = `${sources}/${relative}`;
  await fs.mkdir(directory, {recursive: true});
  row.screenshot = {file: `${relative}/actual-full-player.jpg`, sha256: sha(bytes)};
  await fs.writeFile(`${directory}/actual-full-player.jpg`, bytes, {flag: 'wx'});
  await fs.writeFile(`${directory}/actual-observation.json`, JSON.stringify(row, null, 2)+'\n', {flag: 'wx'});
  return {row, bytes};
}
