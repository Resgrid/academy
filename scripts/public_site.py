"""Build learner-facing pages while retaining production records in sources/."""
import csv
import hashlib
import html
import json
import re
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def script_data(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c')


def fields(value, names):
    return {name: value[name] for name in names if name in value}


def requirements_text(items):
    labels = {'ReadinessPro': 'Readiness Pro', 'BusinessOperations': 'Business Operations', 'PTT': 'Push-to-Talk', 'ADP': 'Advanced Data Protection', 'EnhancedAi': 'Enhanced AI'}
    result = []
    for item in items:
        if isinstance(item, str):
            text = item
        else:
            kind = item.get('Kind', '')
            ident = item.get('Id', '')
            label = labels.get(ident, re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', ident))
            text = {'module': label + ' module enabled', 'addon': label + ' add-on access', 'flag': 'Feature access enabled by your system operator', 'permission': label + ' permission', 'protection': 'Data protection enrollment completed'}.get(kind, label)
        if text not in result:
            result.append(text)
    return result


def learner_course(original):
    """Publish learning content, keeping voice, capture and review metadata internal."""
    return {
        'title': 'Resgrid Academy',
        'learning_paths': original['learning_paths'],
        'lessons': [fields(item, ('id', 'area', 'title', 'role', 'features', 'scenes', 'video', 'subtitle', 'poster', 'duration_seconds', 'sector_examples')) for item in original['lessons']],
        'features': [dict(fields(item, ('id', 'area', 'lesson', 'label', 'purpose', 'value', 'setup', 'release_status', 'location', 'docs_url', 'sector_examples')), requirements=requirements_text(item.get('requirements', []))) for item in original['features']],
        'settings': [fields(item, ('id', 'area', 'lesson', 'label', 'help', 'location', 'default', 'availability')) for item in original['settings']],
    }


CSS = '''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f5f7fa;color:#183047}a{color:#155b70;text-underline-offset:3px}a:hover{color:#b93933}h1,h2,h3{line-height:1.2;color:#102c43}h1{font-size:clamp(2.2rem,4vw,3.5rem);letter-spacing:-.035em;margin:12px 0 22px}h2{font-size:1.85rem;margin:0 0 18px}h3{font-size:1.17rem;margin:0 0 12px}p{margin:0 0 18px}header{background:#102b42;color:white}header .bar{max-width:1240px;margin:auto;display:flex;justify-content:space-between;align-items:center;gap:24px;padding:20px 28px}header a{color:#e7f1f7;text-decoration:none}header nav{display:flex;gap:24px;flex-wrap:wrap}.brand{font-size:1.05rem;letter-spacing:.1em;font-weight:800}.brand b{color:#ff8276}main{max-width:1240px;margin:auto;padding:32px 28px 60px}.hero{background:#e7eff2;border-radius:20px;padding:38px 42px;margin:8px 0 32px;position:relative;border-left:5px solid #ef554b}.hero p{max-width:850px;font-size:1.1rem}.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-weight:700;font-size:.75rem;color:#497183;margin-bottom:10px}.lead{font-size:1.1rem;color:#466174}.actions{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0 0}.button,button{display:inline-block;font:inherit;font-weight:650;border:1px solid #b6cbd6;background:white;padding:9px 15px;border-radius:8px;text-decoration:none;color:#183e56;cursor:pointer}.button.primary{background:#155c70;border-color:#155c70;color:white}.button:hover,button:hover{background:#dcecf0;color:#102c43}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:18px}.card,section.panel{background:white;border:1px solid #d7e1e8;border-radius:14px;padding:24px}.card p{color:#4e6578}.card a{font-weight:650}.card .meta,.meta{font-size:.87rem;color:#536e80}.section-title{margin:38px 0 20px}section.panel{margin:24px 0}.layout{display:grid;grid-template-columns:minmax(0,2.15fr) minmax(255px,1fr);gap:24px}.watch{padding:18px;background:#fff;border:1px solid #d7e1e8;border-radius:14px}video{display:block;width:100%;aspect-ratio:16/9;background:#102b42;border-radius:8px}video::cue{color:#fff;background:rgba(0,0,0,.86)}.controls{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}button[aria-pressed=true]{background:#155c70;color:white}.chapter{display:flex;text-align:left;gap:12px;align-items:baseline;width:100%;margin:7px 0;background:#f4f8fa}.chapter span{font-size:.8rem;color:#567487;min-width:42px}.chapter[aria-pressed=true] span{color:#dfedf3}.chapters h3{margin-bottom:16px}.chapters{max-height:620px;overflow:auto}.toolbar{display:flex;align-items:end;gap:16px;flex-wrap:wrap;margin:20px 0}.toolbar label{display:grid;gap:5px;font-weight:600;flex:1;min-width:220px}.toolbar label.small{flex:0 1 250px}input,select{font:inherit;padding:10px 12px;border:1px solid #9fb8c7;border-radius:8px;background:white;color:#183047;width:100%}summary{cursor:pointer;font-weight:700}.transcript p{margin:16px 0 0}.pill{display:inline-block;background:#e9f1f4;color:#335d71;font-size:.8rem;padding:3px 9px;border-radius:20px;margin-bottom:12px}figure{margin:24px 0}img{max-width:100%;height:auto;border-radius:10px}figcaption{color:#526e81;font-size:.9rem}dt{font-weight:700;margin-top:20px}dd{margin:4px 0 0}details.card{margin-bottom:12px}details.card summary{font-size:1.03rem}details.card>div{padding-top:18px}.hidden{display:none!important}.empty{padding:24px;border:1px dashed #9fb8c7;border-radius:10px}footer{border-top:1px solid #cfdae3;max-width:1184px;margin:auto;padding:24px 0 38px;color:#536b7d;font-size:.9rem;display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap}.skip{position:absolute;top:-100px}.skip:focus{top:8px;left:8px;background:white;padding:10px;z-index:100}:focus-visible{outline:3px solid #ed665b;outline-offset:3px}[id]{scroll-margin-top:18px}@media(max-width:800px){header .bar{align-items:flex-start;flex-direction:column;gap:14px}header nav{gap:16px;font-size:.9rem}main{padding:20px 16px 40px}.hero{padding:26px 22px}.layout{grid-template-columns:1fr}.chapters{max-height:400px}footer{margin:0 16px}.grid{grid-template-columns:1fr}}'''


def page(title, content, prefix='', js=''):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Learn Resgrid with video tutorials, practical configuration guides and examples for your department."><title>{esc(title)} | Resgrid Academy</title><link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml"><style>{CSS}</style></head><body><a class="skip" href="#main">Skip to content</a><header><div class="bar"><a class="brand" href="{prefix or './'}"><b>RESGRID</b> ACADEMY</a><nav aria-label="Academy"><a href="{prefix}#lessons">Video lessons</a><a href="{prefix}deep-dive/">Walkthroughs</a><a href="{prefix}#features">Feature guides</a><a href="{prefix}deep-dive/sectors.html">Your department</a></nav></div></header><main id="main">{content}</main><footer><span>Resgrid Academy · Learn, configure, apply.</span><span><a href="{prefix}about/">About the Academy</a> · <a href="https://docs.resgrid.com/">Resgrid documentation</a></span></footer>{('<script>' + js + '</script>') if js else ''}</body></html>'''


def sectors(examples):
    return '<dl>' + ''.join(f'<dt>{esc(name)}</dt><dd>{esc(example)}</dd>' for name, example in examples.items()) + '</dl>'


def timestamp(seconds):
    seconds = int(seconds)
    return f'{seconds // 60}:{seconds % 60:02}'


def chapter_buttons(chapters):
    return ''.join(f'<button class="chapter" type="button" data-start="{chapter["start"]}"><span>{timestamp(chapter["start"])}</span>{esc(chapter["title"])}</button>' for chapter in chapters)


PLAYER_JS = '''const player=document.getElementById('lesson-video');const message=document.getElementById('player-message');document.querySelectorAll('[data-start]').forEach(button=>button.addEventListener('click',()=>{player.currentTime=Number(button.dataset.start);player.play().catch(()=>{message.textContent='Press Play to continue the lesson.'});}));player.addEventListener('error',()=>{message.textContent='The video could not load. Reload this page or use the download link.'});player.addEventListener('timeupdate',()=>{const buttons=[...document.querySelectorAll('.chapter')];buttons.forEach((button,index)=>button.setAttribute('aria-pressed',player.currentTime>=Number(button.dataset.start)&&(!buttons[index+1]||player.currentTime<Number(buttons[index+1].dataset.start))?'true':'false'));});'''


def player(video, poster, caption, chapters, download_caption, subtitle=''):
    return f'''<div class="layout"><div class="watch"><video id="lesson-video" controls playsinline preload="metadata" src="{esc(video)}" poster="{esc(poster)}"><track default kind="captions" label="English" srclang="en" src="{esc(caption)}"></video><p class="meta" style="margin:14px 0">English captions · {esc(subtitle)}</p><a id="download-video" href="{esc(video)}" download>Download video</a> · <a id="download-captions" href="{esc(download_caption)}" download>Download captions</a><p id="player-message" role="status"></p></div><aside class="card chapters"><h3>In this lesson</h3><div id="chapters">{chapter_buttons(chapters)}</div></aside></div>'''


def write_public_site(destination, sources, course, ready):
    destination, sources = Path(destination), Path(sources)
    def write(relative, content):
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    write('favicon.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><title>Resgrid Academy</title><rect width="64" height="64" rx="14" fill="#ef554b"/><path d="M19 48V16H34C48 16 48 34 34 34H19M32 34L46 48" fill="none" stroke="white" stroke-width="6" stroke-linejoin="round"/></svg>')
    paths = ''.join(f'<article class="card"><p class="eyebrow">Learning path</p><h3>{esc(role)}</h3><p>{esc(description)}</p><button type="button" data-path="{esc(role)}">Explore lessons →</button></article>' for role, description in [
        ('Administrator', 'Set up your department, organize people and units, and understand how settings affect daily work.'),
        ('Dispatcher', 'Coordinate calls, find available resources, and follow communications and response status.'),
        ('Member', 'Use your apps, update availability, follow shifts, and complete assigned learning and checks.'),
        ('Specialist', 'Manage equipment, inventory, records, deployments and supporting department workflows.')])
    first = course['lessons'][0]
    chapters = json.loads((sources / f'media/{first["id"]}.chapters.json').read_text())
    lesson_cards = ''.join(f'<article class="card lesson-card" data-lesson="{esc(lesson["id"])}"><p class="eyebrow">{esc(lesson["area"].replace("-", " "))}</p><h3>{esc(lesson["title"])}</h3><p class="meta">{round(lesson["duration_seconds"] / 60, 1)} min · {esc(lesson["role"])}</p><button type="button" data-lesson="{esc(lesson["id"])}">Watch lesson →</button></article>' for lesson in course['lessons'])
    feature_cards = ''
    for feature in course['features']:
        requirements = '<p><b>Before you begin:</b> ' + esc('; '.join(feature['requirements'])) + '</p>' if feature.get('requirements') else ''
        availability = '' if feature.get('release_status') == 'available' else f'<p><b>Availability:</b> {esc(feature.get("release_status", "Check your department access"))}. Check your department’s version and enabled modules.</p>'
        location = feature.get('location', {})
        screen = ' → '.join(str(location[key]) for key in ('Controller', 'Action') if location.get(key))
        feature_cards += f'''<details class="card feature-card" data-lesson="{esc(feature['lesson'])}" data-search="{esc(' '.join(str(feature.get(key, '')) for key in ('label', 'purpose', 'value', 'setup', 'area')).lower())}"><summary>{esc(feature['label'])}</summary><div><p>{esc(feature['purpose'])}</p><h3>Why it helps</h3><p>{esc(feature['value'])}</p><h3>How to configure it</h3><p>{esc(feature['setup'])}</p>{requirements}{availability}<p class="meta">In Resgrid: {esc(screen)}</p><details><summary>Examples for other departments</summary>{sectors(feature.get('sector_examples', {}))}</details><p style="margin-top:18px"><button type="button" data-lesson="{esc(feature['lesson'])}">Watch the topic lesson</button> <a href="scripts/feature-{esc(feature['id'])}.txt">Read the guide</a>{(' · <a href="' + esc(feature['docs_url']) + '">Documentation</a>') if feature.get('docs_url') else ''}</p></div></details>'''
    settings_cards = ''.join(f'<details class="card setting-card" data-search="{esc((setting["label"]+" "+setting["help"]+" "+setting["area"]).lower())}"><summary>{esc(setting["label"])}</summary><div><p>{esc(setting["help"])}</p><p class="meta">Screen: {esc(setting.get("location", {}).get("Controller", "Department"))} → {esc(setting.get("location", {}).get("Action", "Settings"))}{(" · Default: " + esc(setting["default"])) if "default" in setting else ""}</p></div></details>' for setting in course['settings'])
    options = ''.join(f'<option value="{esc(role)}">{esc(role)}</option>' for role in course['learning_paths'])
    lesson_anchors = ''.join(f'<span id="lesson={esc(item["id"])}" aria-hidden="true"></span>' for item in course['lessons'])
    content = f'''<section class="hero"><p class="eyebrow">Learn Resgrid. Support your department.</p><h1>Build confidence in every part of your operation.</h1><p>Learn what Resgrid does, how to configure it, and how each choice helps your people work together. Follow a learning path or go straight to the task you need.</p><div class="actions"><a class="button primary" href="#learn">Start learning</a><a class="button" href="deep-dive/">Explore configuration walkthroughs</a></div></section><h2>Choose your learning path</h2><div class="grid">{paths}</div><section id="learn">{lesson_anchors}<div class="section-title"><p class="eyebrow">Video lesson</p><h2 id="lesson-title">{esc(first['title'])}</h2><p id="lesson-audience" class="lead">{esc(first['role'])}</p></div>{player(first['video'],first['poster'],first['subtitle'],chapters,'media/00-start.srt','Chapter navigation and fullscreen playback')}<section class="panel transcript"><details><summary>Read the transcript</summary><div id="transcript"></div><p style="margin-top:18px"><a id="transcript-link" href="scripts/00-start.txt">Download transcript</a></p></details></section><section class="panel"><h3>Apply this lesson to your department</h3><div id="lesson-sectors">{sectors(first['sector_examples'])}</div></section></section><section id="lessons"><div class="section-title"><p class="eyebrow">Explore the system</p><h2>Video lessons</h2><p>Learn the purpose, setup decisions and practical use of each area.</p></div><div class="toolbar"><label class="small">Learning path<select id="path" aria-label="Learning path">{options}</select></label><label>Find a lesson<input id="lesson-search" type="search" placeholder="Search shifts, inventory, records…"></label></div><p id="lesson-count" class="meta" role="status"></p><div class="grid" id="lesson-list">{lesson_cards}</div><p id="lesson-empty" class="empty hidden">No lessons match. Try another topic or choose Complete series.</p></section><section class="panel"><p class="eyebrow">See the steps in Resgrid</p><h2>Configuration walkthroughs</h2><p>Follow the Setup Wizard, department settings, custom statuses, dispatch, chat, Assistant and Admin Assist using a fictional department.</p><a class="button primary" href="deep-dive/">Watch the walkthroughs →</a> <a class="button" href="captures/firehouse51/">Follow a connected department workflow</a></section><section id="features"><div class="section-title"><p class="eyebrow">Find the right tool</p><h2>Feature guides</h2><p>Understand what a feature does, which problem it solves and how to prepare it.</p></div><div class="toolbar"><label>Search feature guides<input id="feature-search" type="search" placeholder="Search roles, run cards, workforce…"></label></div><p id="feature-count" class="meta" role="status"></p><div id="feature-list">{feature_cards}</div><p id="feature-empty" class="empty hidden">No feature guides match your search.</p></section><section id="settings"><div class="section-title"><p class="eyebrow">Make informed choices</p><h2>Configuration reference</h2><p>Review a setting’s purpose and its effects before changing your department configuration.</p></div><div class="toolbar"><label>Search settings<input id="setting-search" type="search" placeholder="Search dispatch, staffing, maps…"></label></div><p id="setting-count" class="meta" role="status"></p><div id="setting-list">{settings_cards}</div><p id="setting-empty" class="empty hidden">No settings match your search.</p></section>'''
    js = '''const COURSE=COURSE_DATA;
const $=id=>document.getElementById(id);
''' + PLAYER_JS + '''
function escapeText(text){const node=document.createElement('span');node.textContent=text;return node.innerHTML;}
function chooseLesson(id,scroll=true){const lesson=COURSE.lessons.find(item=>item.id===id);if(!lesson)return;player.pause();player.src=lesson.video;player.poster=lesson.poster;const track=player.querySelector('track');track.src=lesson.subtitle;track.default=true;player.load();$('lesson-title').textContent=lesson.title;$('lesson-audience').textContent=lesson.role;$('download-video').href=lesson.video;$('download-captions').href='media/'+lesson.id+'.srt';$('transcript-link').href='scripts/'+lesson.id+'.txt';$('transcript').innerHTML=lesson.scenes.map(scene=>'<h3 style="margin-top:20px">'+escapeText(scene.title)+'</h3><p>'+escapeText(scene.narration)+'</p>').join('');$('lesson-sectors').innerHTML='<dl>'+Object.entries(lesson.sector_examples).map(([name,text])=>'<dt>'+escapeText(name)+'</dt><dd>'+escapeText(text)+'</dd>').join('')+'</dl>';$('chapters').replaceChildren();lesson.scenes.forEach(scene=>{const button=document.createElement('button');button.type='button';button.className='chapter';button.dataset.start=scene.start_seconds;button.textContent=Math.floor(scene.start_seconds/60)+':'+String(Math.floor(scene.start_seconds%60)).padStart(2,'0')+'  '+scene.title;button.addEventListener('click',()=>{player.currentTime=scene.start_seconds;player.play().catch(()=>{message.textContent='Press Play to continue the lesson.';});});$('chapters').append(button);});message.textContent='';document.querySelectorAll('button[data-lesson]').forEach(button=>button.setAttribute('aria-pressed',button.dataset.lesson===id?'true':'false'));if(scroll)history.replaceState(null,'','#lesson='+encodeURIComponent(id));if(scroll)$('learn').scrollIntoView({behavior:'smooth',block:'start'});}
document.querySelectorAll('button[data-lesson]').forEach(button=>button.addEventListener('click',()=>chooseLesson(button.dataset.lesson)));
function filterLessons(){const allowed=COURSE.learning_paths[$('path').value]||COURSE.lessons.map(item=>item.id);const query=$('lesson-search').value.toLowerCase();let count=0;document.querySelectorAll('.lesson-card').forEach(card=>{const show=allowed.includes(card.dataset.lesson)&&card.textContent.toLowerCase().includes(query);card.classList.toggle('hidden',!show);if(show)count++;});$('lesson-count').textContent=count+' lessons';$('lesson-empty').classList.toggle('hidden',count!==0);}
$('path').value='Complete series';['path','lesson-search'].forEach(id=>$(id).addEventListener(id==='path'?'change':'input',filterLessons));document.querySelectorAll('[data-path]').forEach(button=>button.addEventListener('click',()=>{$('path').value=button.dataset.path;$('lesson-search').value='';filterLessons();$('lessons').scrollIntoView({behavior:'smooth'});}));filterLessons();
function filterGuides(kind){const query=$(kind+'-search').value.toLowerCase();let count=0;document.querySelectorAll('.'+kind+'-card').forEach(card=>{const show=!query||card.dataset.search.includes(query);card.classList.toggle('hidden',!show);if(show)count++;});$(kind+'-count').textContent=count+(kind==='feature'?' feature guides':' settings');$(kind+'-empty').classList.toggle('hidden',count!==0);}
['feature','setting'].forEach(kind=>{$(kind+'-search').addEventListener('input',()=>filterGuides(kind));filterGuides(kind);});const initial=location.hash.startsWith('#lesson=')?decodeURIComponent(location.hash.slice(8)):COURSE.lessons[0].id;chooseLesson(initial,location.hash.startsWith('#lesson='));
'''
    write('index.html', page('Learn the Resgrid system', content, js=js.replace('COURSE_DATA', script_data(course))))
    for lesson in course['lessons']:
        text = [lesson['title'], 'Audience: ' + lesson['role'], '']
        for scene in lesson['scenes']:
            text += [scene['title'], scene['narration'], '']
        text += ['Examples for your department'] + [name + ': ' + example for name, example in lesson.get('sector_examples', {}).items()]
        write(f'scripts/{lesson["id"]}.txt', '\n'.join(text) + '\n')
    for feature in course['features']:
        text = [feature['label'], '', feature['purpose'], '', 'Why it helps', feature['value'], '', 'How to configure it', feature['setup'], '', 'Before you begin', '; '.join(feature.get('requirements', [])) or 'Check your department access and intended audience.', '', 'Examples for your department']
        text += [name + ': ' + example for name, example in feature.get('sector_examples', {}).items()]
        if feature.get('docs_url'): text += ['', 'Documentation: ' + feature['docs_url']]
        write(f'scripts/feature-{feature["id"]}.txt', '\n'.join(text) + '\n')
    for name, items, names in [('coverage.csv', course['features'], ('id', 'label', 'area', 'purpose', 'value', 'setup')), ('settings.csv', course['settings'], ('id', 'label', 'area', 'help', 'default', 'availability'))]:
        with (destination / name).open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=names, extrasaction='ignore', lineterminator='\n');writer.writeheader();writer.writerows(items)

    cards = ''
    for audit in ready:
        ident = audit['id']
        lesson = json.loads((sources / f'deep-dive/lessons/{ident}.json').read_text())
        chapters = json.loads((sources / f'deep-dive/review/{ident}/chapters.json').read_text())
        cards += f'<article class="card"><p class="eyebrow">Step-by-step walkthrough</p><h3>{esc(lesson["title"])}</h3><p class="meta">{round(audit["duration_seconds"]/60,1)} min · Resgrid screens · English captions</p><a href="lessons/{ident}/">Watch the walkthrough →</a></article>'
        sections = ''
        storyboard = json.loads((sources / f'deep-dive/review/{ident}/storyboard.json').read_text())
        for index, scene in enumerate(lesson['scenes']):
            shot = next(item for item in storyboard if item['scene'] == index)
            sections += f'<section class="panel transcript" id="step-{index+1}"><p class="eyebrow">Step {index+1}</p><h2>{esc(scene["title"])}</h2><figure><img loading="lazy" src="{esc(Path(shot["frame"]).name)}" alt="Resgrid screen: {esc(scene["title"])}"></figure><details><summary>Read the transcript</summary><p>{esc(scene["narration"].replace("Rez grid","Resgrid"))}</p></details></section>'
        version = audit['sha256'][:16]
        body = f'<p class="eyebrow">Configuration walkthrough</p><h1>{esc(lesson["title"])}</h1><p class="lead">Follow each step, understand its impact, and try the practice exercise with your department.</p>' + player(f'../../media/{ident}.mp4?v={version}', '01-01.jpg', f'captions.vtt?v={version}', chapters, 'captions.srt', f'{round(audit["duration_seconds"]/60,1)} minutes · Resgrid screens') + sections + f'<section class="panel"><h2>Apply it to your department</h2>{sectors(lesson.get("cross_sector_examples", lesson.get("sector_examples", {})))}</section><section class="panel"><h2>Put it into practice</h2><p>Check your department’s enabled modules, permissions and provider configuration. Save each change on its own screen, review the retained value, and confirm the result with the people and devices that will use it.</p></section><p><a href="../../">← All configuration walkthroughs</a></p>'
        write(f'deep-dive/lessons/{ident}/index.html', page(lesson['title'], body, '../../../', PLAYER_JS))
        target = f'../../lessons/{ident}/'
        write(f'deep-dive/review/{ident}/index.html', '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=' + target + '"><title>' + esc(lesson['title']) + ' | Resgrid Academy</title></head><body><p><a href="' + target + '">Watch ' + esc(lesson['title']) + '</a></p></body></html>')
    write('deep-dive/index.html', page('Configuration walkthroughs', '<section class="hero"><p class="eyebrow">Put learning into practice</p><h1>Configure with confidence.</h1><p>See where to make a change, understand what it affects, and check the result. Follow these walkthroughs using a fictional department, then apply the lessons to your own operating needs.</p><div class="actions"><a class="button" href="sectors.html">Examples for your department</a><a class="button" href="../captures/firehouse51/">A connected department workflow</a></div></section><div class="grid">' + cards + '</div><section class="panel"><h2>Find another topic</h2><p>Explore video lessons and feature guides for personnel, permissions, run cards, shifts, mapping, inventory, records, training, workforce, billing and more.</p><a class="button primary" href="../#lessons">Browse the lesson library →</a></section>', '../'))

    sector_data = json.loads((sources / 'deep-dive/sector-examples.json').read_text())
    sector_data = {'sectors': sector_data['sectors'], 'deep_lessons': [fields(item, ('id', 'title', 'topics', 'sector_examples')) for item in sector_data['deep_lessons']], 'primer_lessons': [fields(item, ('id', 'title', 'sector_examples')) for item in sector_data['primer_lessons']]}
    write('deep-dive/sector-examples.json', json.dumps(sector_data, ensure_ascii=False, indent=2) + '\n')
    write('deep-dive/course.json', json.dumps({'title': 'Resgrid configuration topics', 'lessons': sector_data['deep_lessons']}, ensure_ascii=False, indent=2) + '\n')
    sector_options = ''.join(f'<option>{esc(name)}</option>' for name in sector_data['sectors'])
    cards = ''.join(f'<article class="card sector-card" data-index="{index}"><p class="eyebrow">Department example</p><h3>{esc(item["title"])}</h3><p class="sector-example">{esc(item["sector_examples"][sector_data["sectors"][0]])}</p><a href="../#lesson={esc(item["id"])}">Explore this topic →</a></article>' for index, item in enumerate(sector_data['primer_lessons']))
    sector_js = 'const EXAMPLES=' + script_data(sector_data['primer_lessons']) + ''';const selector=document.getElementById('sector');const search=document.getElementById('sector-search');function update(){let count=0;document.querySelectorAll('.sector-card').forEach(card=>{const item=EXAMPLES[Number(card.dataset.index)];const text=item.sector_examples[selector.value];card.querySelector('.sector-example').textContent=text;const show=(item.title+' '+text).toLowerCase().includes(search.value.toLowerCase());card.classList.toggle('hidden',!show);if(show)count++;});document.getElementById('sector-count').textContent=count+' department examples';document.getElementById('sector-empty').classList.toggle('hidden',count!==0);}selector.addEventListener('change',update);search.addEventListener('input',update);update();'''
    write('deep-dive/sectors.html', page('Examples for your department', f'<section class="hero"><p class="eyebrow">Many departments. Shared coordination needs.</p><h1>Make Resgrid work for your team.</h1><p>Use Resgrid to coordinate people, resources and information across fire and EMS, community paramedicine and mental health response, search and rescue, security, wildland contracting and industrial emergency response.</p><p>Choose a department type to explore examples for each area. Use the roles, resources and procedures that fit your organization.</p></section><div class="toolbar"><label>Department type<select id="sector" aria-label="Department type">{sector_options}</select></label><label>Find a topic<input id="sector-search" type="search" placeholder="Search roster, visits, equipment…"></label></div><p id="sector-count" class="meta" role="status"></p><div class="grid">{cards}</div><p id="sector-empty" class="empty hidden">No examples match your search.</p>', '../', sector_js))

    chapters = json.loads((sources / 'captures/firehouse51/firehouse51-walkthrough.chapters.json').read_text())
    chapters[0]['title'] = 'Meet the example department'
    write('captures/firehouse51/firehouse51-walkthrough.chapters.json', json.dumps(chapters, indent=2) + '\n')
    manifest = json.loads((sources / 'captures/firehouse51/manifest.json').read_text())
    selected = ['02-personnel.jpg', '04-unit-configuration.jpg', '08-calls.jpg', '12-deployment-saved.jpg', '13-deployment-roster.jpg', '14-calendar.jpg', '15-custom-statuses.jpg']
    gallery = ''.join(f'<figure class="card"><img loading="lazy" src="{esc(item["file"])}" alt="{esc(item["title"])}"><figcaption>{esc(item["title"])}</figcaption></figure>' for item in manifest if item['file'] in selected)
    body = '<p class="eyebrow">A connected department workflow</p><h1>From people and resources to response and follow-up.</h1><p class="lead">Follow Firehouse 51 through roster setup, unit configuration, call handling, deployment and everyday readiness. The people and incidents in this example are fictional training data.</p>' + player('firehouse51-walkthrough.mp4', '01-dashboard.jpg', 'firehouse51-walkthrough.vtt', chapters, 'firehouse51-walkthrough.srt', '3.1 minutes · Resgrid screens') + '<section class="panel"><h2>Use the same workflow in your organization</h2><p>A community response team can coordinate a scheduled visit, a search team can assemble a deployment roster, and a security department can assign a patrol. Wildland contractors and industrial teams can connect resource assignments with equipment and readiness records.</p><a href="../../deep-dive/sectors.html">Explore examples for your department →</a></section><h2 class="section-title">Explore the workflow screens</h2><div class="grid">' + gallery + '</div>'
    write('captures/firehouse51/index.html', page('A connected department workflow', body, '../../', PLAYER_JS))
    body = '<section class="hero"><p class="eyebrow">Welcome to Resgrid Academy</p><h1>Learn, configure, apply.</h1><p>The Academy helps members, dispatchers and department administrators understand Resgrid and use it in daily work.</p></section><section class="panel"><h2>Choose how you learn</h2><p>Start with a role-based learning path, watch a topic lesson, or follow a configuration walkthrough. Videos include English captions, chapter navigation and downloadable transcripts. Feature guides explain a tool’s purpose, configuration and department impact.</p><a class="button primary" href="../#lessons">Explore video lessons</a> <a class="button" href="../deep-dive/">Follow a walkthrough</a></section><section class="panel"><h2>Practice with purpose</h2><p>Use a practice exercise to check your understanding. Identify the intended result, make a controlled change, save it, and review the outcome with the people and devices involved. Check feature availability, department permissions and any connected providers in your own Resgrid system.</p><p>Firehouse 51 is a fictional example department. Its names, incidents and configuration illustrate the workflow; your department’s procedures guide how you use it.</p></section><section class="panel"><h2>Apply the examples to your team</h2><p>The Academy includes examples for community paramedicine and mental health response, search and rescue, security companies and departments, wildland contractors and industrial emergency response teams, alongside fire and EMS.</p><a href="../deep-dive/sectors.html">Browse examples for your department →</a></section><section class="panel"><h2>Keep the reference close</h2><p>Use the <a href="../#features">feature guides</a> and <a href="../#settings">configuration reference</a> when reviewing settings. For additional product guidance, visit <a href="https://docs.resgrid.com/">Resgrid documentation</a>.</p></section>'
    write('about/index.html', page('About the Academy', body, '../'))
    # Preserve previously shared links without exposing authoring instructions.
    write('production/production-guide.html', page('About the Academy', body, '../'))
