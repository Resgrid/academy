import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { imageDimensions } from './capture-evidence-invitation-safe-20261102.mjs';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');

export async function recordReview(tab, sourceRoot, lesson, fixture) {
  const directory = path.join(sourceRoot, 'expansion/rendered', lesson + '-take-01');
  const evidence = JSON.parse(await fs.readFile(path.join(directory, 'evidence.pending.json'), 'utf8'));
  if (sha(await fs.readFile(path.join(sourceRoot, evidence.video.file))) !== evidence.video.sha256)
    throw new Error('The rendered video changed.');
  await tab.goto(fixture);
  const state = async () => {
    await tab.playwright.getByRole('button', {name:'Observe playback',exact:true}).click();
    return JSON.parse(await tab.playwright.evaluate(() => document.querySelector('#observation').textContent));
  };
  const proofs = [];
  const images = [];
  for (const position of ['beginning', 'middle', 'end']) {
    await tab.playwright.getByRole('button', {name:position,exact:true}).click();
    let before = await state();
    for (let attempt=0; attempt<15 && (before.ready_state < 3 || !before.captions.text); attempt++) before = await state();
    let after = await state();
    for (let attempt=0; attempt<15 && (after.current_time <= before.current_time + .25 || !after.captions.text); attempt++) after = await state();
    const errors = await tab.dev.logs({levels:['error'],limit:20});
    const relative = path.relative(sourceRoot, path.join(directory, `playback-${position}.jpg`));
    if (after.current_time <= before.current_time + .25 || after.paused || after.ended || after.media_error !== null ||
        after.ready_state < 3 || !after.captions.text || after.captions.mode !== 'showing' || errors.length ||
        after.screen.top < 0 || after.screen.bottom > after.screen.viewport_height)
      throw new Error(JSON.stringify({position,before,after,errors}));
    const bytes = Buffer.from(await tab.screenshot({fullPage:false}));
    const dimensions = imageDimensions(bytes);
    await fs.writeFile(path.join(sourceRoot, relative), bytes);
    const { screen, ...observed } = after;
    proofs.push({position,...observed, previous_time:before.current_time,captured_at:new Date().toISOString(),
      url:fixture,video_sha256:evidence.video.sha256,console_errors:[],
      screenshot_media_state:screen,screenshot:{file:relative,sha256:sha(bytes),...dimensions}});
    images.push(bytes);
  }
  await fs.writeFile(path.join(directory,'playback.actual.json'),JSON.stringify(proofs,null,2)+'\n');
  return {proofs,images};
}
