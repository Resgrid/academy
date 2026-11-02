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


def topic_scenes(item):
    scenes = [fields(scene, ('title', 'narration')) for scene in item['scenes']]
    # Keep source scripts intact. These two exact historical recorder notes
    # become equivalent instructions for the person using the public guide.
    replacements = {
        '22-relay': ('A recorder will need the supported Relay application and an audio test setup to turn this briefing into a live walkthrough.',
                     'Use the supported Relay application and an audio test setup to verify the workflow.'),
        '23-self-hosting': ('Detailed infrastructure capture needs the chosen deployment layout: Linux Compose, Windows, Kubernetes or k3s, or an Incident Command Kit.',
                           'Choose the deployment layout you will verify: Linux Compose, Windows, Kubernetes or k3s, or an Incident Command Kit.'),
    }
    if item['id'] in replacements:
        original, replacement = replacements[item['id']]
        for scene in scenes:
            scene['narration'] = scene['narration'].replace(original, replacement)
    return scenes


def topic_examples(item):
    examples = dict(item.get('sector_examples', {}))
    if 'Fire / EMS' not in examples:
        # The original primers teach fire/EMS as their primary context and
        # retain five explicit companion sectors. Reuse their exact practice
        # guidance to make the sixth public example explicit, without new
        # feature claims or edits to the canonical authoring records.
        practice = topic_scenes(item)[-1]['narration']
        examples = {'Fire / EMS': 'Use a fictional fire or EMS department for this exercise. ' + practice, **examples}
    return examples


def learner_course(original):
    """Publish learning content, keeping voice, capture and review metadata internal."""
    return {
        'title': 'Resgrid Academy',
        'learning_paths': original['learning_paths'],
        'lessons': [dict(fields(item, ('id', 'area', 'title', 'role', 'features')),
                         kind='topic_guide', href=f'topics/{item["id"]}/', transcript=f'scripts/{item["id"]}.txt',
                         scenes=topic_scenes(item), sector_examples=topic_examples(item))
                    for item in original['lessons']],
        'features': [dict(fields(item, ('id', 'area', 'lesson', 'label', 'purpose', 'value', 'setup', 'release_status', 'location', 'docs_url', 'sector_examples')), requirements=requirements_text(item.get('requirements', []))) for item in original['features']],
        'settings': [fields(item, ('id', 'area', 'lesson', 'label', 'help', 'location', 'default', 'availability')) for item in original['settings']],
    }


from academy_brand import CSS, brand_head, brand_header, brand_footer, write_brand_assets


def page(title, content, prefix='', js='', expansion=False):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Learn Resgrid with video tutorials, practical configuration guides and examples for your department."><title>{esc(title)} | Resgrid Academy</title>{brand_head(prefix)}<style>{CSS}</style></head><body><a class="skip" href="#main">Skip to content</a>{brand_header(prefix, expansion)}<main id="main">{content}</main>{brand_footer(prefix)}{('<script>' + js + '</script>') if js else ''}</body></html>'''


def sectors(examples):
    return '<dl>' + ''.join(f'<dt>{esc(name)}</dt><dd>{esc(example)}</dd>' for name, example in examples.items()) + '</dl>'


def topic_sections(lesson):
    return ''.join(f'<section id="topic-step-{index}"><h3>{esc(scene["title"])}</h3><p>{esc(scene["narration"])}</p></section>'
                   for index, scene in enumerate(lesson['scenes'], 1))


def topic_outline(lesson):
    return ''.join(f'<a class="chapter" href="#topic-step-{index}">{esc(scene["title"])}</a>'
                   for index, scene in enumerate(lesson['scenes'], 1))


TOPIC_JS = '''const COURSE=COURSE_DATA;
const $=id=>document.getElementById(id);
function escapeText(text){const node=document.createElement('span');node.textContent=text;return node.innerHTML;}
function chooseLesson(id,scroll=true){const lesson=COURSE.lessons.find(item=>item.id===id);if(!lesson)return;
$('lesson-title').textContent=lesson.title;$('lesson-audience').textContent=lesson.role;
$('transcript-link').href=lesson.transcript;$('topic-page-link').href=lesson.href;
$('transcript').innerHTML=lesson.scenes.map((scene,index)=>'<section id="topic-step-'+(index+1)+'"><h3>'+escapeText(scene.title)+'</h3><p>'+escapeText(scene.narration)+'</p></section>').join('');
$('topic-outline').innerHTML=lesson.scenes.map((scene,index)=>'<a class="chapter" href="#topic-step-'+(index+1)+'">'+escapeText(scene.title)+'</a>').join('');
$('lesson-sectors').innerHTML='<dl>'+Object.entries(lesson.sector_examples).map(([name,text])=>'<dt>'+escapeText(name)+'</dt><dd>'+escapeText(text)+'</dd>').join('')+'</dl>';
document.querySelectorAll('[data-lesson-link]').forEach(link=>{if(link.dataset.lesson===id)link.setAttribute('aria-current','true');else link.removeAttribute('aria-current');});
if(scroll){history.replaceState(null,'','#lesson='+encodeURIComponent(id));$('learn').scrollIntoView({behavior:'smooth',block:'start'});}}
document.querySelectorAll('[data-lesson-link]').forEach(link=>link.addEventListener('click',event=>{if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();chooseLesson(link.dataset.lesson);}));
function filterLessons(){const allowed=COURSE.learning_paths[$('path').value]||COURSE.lessons.map(item=>item.id);const query=$('lesson-search').value.toLowerCase();let count=0;document.querySelectorAll('.lesson-card').forEach(card=>{const item=COURSE.lessons.find(lesson=>lesson.id===card.dataset.lesson);const searchText=(card.textContent+' '+(item?.scenes||[]).map(scene=>scene.title+' '+scene.narration).join(' ')).toLowerCase();const show=allowed.includes(card.dataset.lesson)&&searchText.includes(query);card.classList.toggle('hidden',!show);if(show)count++;});$('lesson-count').textContent=count+' topic guides';$('lesson-empty').classList.toggle('hidden',count!==0);}
$('path').value='Complete series';['path','lesson-search'].forEach(id=>$(id).addEventListener(id==='path'?'change':'input',filterLessons));document.querySelectorAll('[data-path]').forEach(button=>button.addEventListener('click',()=>{$('path').value=button.dataset.path;$('lesson-search').value='';filterLessons();$('lessons').scrollIntoView({behavior:'smooth'});}));filterLessons();
const quickSearch=$('quick-search');if(quickSearch)quickSearch.addEventListener('submit',event=>{event.preventDefault();$('path').value='Complete series';$('lesson-search').value=$('quick-query').value;filterLessons();$('lessons').scrollIntoView({behavior:'smooth',block:'start'});});
function filterGuides(kind){const query=$(kind+'-search').value.toLowerCase();let count=0;document.querySelectorAll('.'+kind+'-card').forEach(card=>{const show=!query||card.dataset.search.includes(query);card.classList.toggle('hidden',!show);if(show)count++;});$(kind+'-count').textContent=count+(kind==='feature'?' feature guides':' settings');$(kind+'-empty').classList.toggle('hidden',count!==0);}
['feature','setting'].forEach(kind=>{$(kind+'-search').addEventListener('input',()=>filterGuides(kind));filterGuides(kind);});
function selectFromHash(scroll){let id;try{id=location.hash.startsWith('#lesson=')?decodeURIComponent(location.hash.slice(8)):null;}catch(error){id=null;}chooseLesson(COURSE.lessons.some(item=>item.id===id)?id:COURSE.lessons[0].id,scroll);}
selectFromHash(location.hash.startsWith('#lesson='));window.addEventListener('hashchange',()=>{if(location.hash.startsWith('#lesson='))selectFromHash(true);});
'''


def timestamp(seconds):
    seconds = int(seconds)
    return f'{seconds // 60}:{seconds % 60:02}'


def chapter_buttons(chapters):
    return ''.join(f'<button class="chapter" type="button" data-start="{chapter["start"]}"><span>{timestamp(chapter["start"])}</span>{esc(chapter["title"])}</button>' for chapter in chapters)


PLAYER_JS = '''const player=document.getElementById('lesson-video');const message=document.getElementById('player-message');document.querySelectorAll('[data-start]').forEach(button=>button.addEventListener('click',()=>{player.currentTime=Number(button.dataset.start);player.scrollIntoView({block:'start'});player.play().catch(()=>{message.textContent='Press Play to continue the lesson.'});}));player.addEventListener('error',()=>{message.textContent='The video could not load. Reload this page or use the download link.'});player.addEventListener('timeupdate',()=>{const buttons=[...document.querySelectorAll('.chapter')];buttons.forEach((button,index)=>button.setAttribute('aria-pressed',player.currentTime>=Number(button.dataset.start)&&(!buttons[index+1]||player.currentTime<Number(buttons[index+1].dataset.start))?'true':'false'));});'''


def player(video, poster, caption, chapters, download_caption, subtitle=''):
    return f'''<div class="layout"><div class="watch"><video id="lesson-video" controls playsinline preload="metadata" src="{esc(video)}" poster="{esc(poster)}"><track default kind="captions" label="English" srclang="en" src="{esc(caption)}"></video><p class="meta" style="margin:14px 0">English captions · {esc(subtitle)}</p><a id="download-video" href="{esc(video)}" download>Download video</a> · <a id="download-captions" href="{esc(download_caption)}" download>Download captions</a><p id="player-message" role="status"></p></div><aside class="card chapters"><h3>In this lesson</h3><div id="chapters">{chapter_buttons(chapters)}</div></aside></div>'''


def expansion_section(lessons, prefix='', limit=None):
    if not lessons:
        return ''
    visible = lessons
    if limit is not None:
        visible = []
        for app in ('Dispatch', 'Responder', 'Unit', 'IC'):
            match = next((item for item in lessons if item['app'] == app), None)
            if match:
                visible.append(match)
        visible = (visible or lessons)[:limit]
    cards = ''
    for item in visible:
        thumb = f'<a class="video-thumbnail" href="{prefix}{esc(item["href"])}" aria-label="Watch {esc(item["title"])}"><img loading="lazy" src="{prefix}{esc(item["poster"])}" alt="{esc(item["app"])} application walkthrough" width="1280" height="720"></a>' if item.get('poster') else ''
        cards += f'<article class="card video-card">{thumb}<p class="eyebrow">{esc(item["app"])} · {esc(item["kind"])}</p><h3>{esc(item["title"])}</h3><a href="{prefix}{esc(item["href"])}">' + ('Watch walkthrough' if item['mode'] == 'video' else 'Open screenshot guide') + ' →</a></article>'
    return '<section id="app-walkthroughs" class="panel"><p class="eyebrow">Learn the apps. Follow the workflow.</p><h2>Apps and configuration</h2><p>Follow real Resgrid screens and practice the workflows with examples for your department.</p><div class="grid">' + cards + f'</div><p style="margin-top:20px"><a href="{prefix}walkthroughs/">Explore apps and configuration →</a></p></section>'


def write_public_site(destination, sources, course, ready, expansion=None):
    destination, sources = Path(destination), Path(sources)
    expansion = expansion or []
    def render(title, content, prefix='', js=''):
        return page(title, content, prefix, js, expansion=bool(expansion))
    def write(relative, content):
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    write_brand_assets(destination, sources)
    paths = ''.join(f'<article class="card"><p class="eyebrow">Learning path</p><h3>{esc(role)}</h3><p>{esc(description)}</p><button type="button" data-path="{esc(role)}">Explore lessons →</button></article>' for role, description in [
        ('Administrator', 'Set up your department, organize people and units, and understand how settings affect daily work.'),
        ('Dispatcher', 'Coordinate calls, find available resources, and follow communications and response status.'),
        ('Member', 'Use your apps, update availability, follow shifts, and complete assigned learning and checks.'),
        ('Specialist', 'Manage equipment, inventory, records, deployments and supporting department workflows.')])
    first = course['lessons'][0]
    lesson_cards = ''.join(f'<article class="card lesson-card" data-lesson="{esc(lesson["id"])}"><p class="eyebrow">Topic guide · {esc(lesson["area"].replace("-", " "))}</p><h3>{esc(lesson["title"])}</h3><p class="meta">{esc(lesson["role"])}</p><a href="{esc(lesson["href"])}" data-lesson-link data-lesson="{esc(lesson["id"])}">Read guide →</a></article>' for lesson in course['lessons'])
    feature_cards = ''
    for feature in course['features']:
        requirements = '<p><b>Before you begin:</b> ' + esc('; '.join(feature['requirements'])) + '</p>' if feature.get('requirements') else ''
        availability = '' if feature.get('release_status') == 'available' else f'<p><b>Availability:</b> {esc(feature.get("release_status", "Check your department access"))}. Check your department’s version and enabled modules.</p>'
        location = feature.get('location', {})
        screen = ' → '.join(str(location[key]) for key in ('Controller', 'Action') if location.get(key))
        feature_cards += f'''<details class="card feature-card" data-lesson="{esc(feature['lesson'])}" data-search="{esc(' '.join(str(feature.get(key, '')) for key in ('label', 'purpose', 'value', 'setup', 'area')).lower())}"><summary>{esc(feature['label'])}</summary><div><p>{esc(feature['purpose'])}</p><h3>Why it helps</h3><p>{esc(feature['value'])}</p><h3>How to configure it</h3><p>{esc(feature['setup'])}</p>{requirements}{availability}<p class="meta">In Resgrid: {esc(screen)}</p><details><summary>Examples for other departments</summary>{sectors(feature.get('sector_examples', {}))}</details><p style="margin-top:18px"><a href="topics/{esc(feature['lesson'])}/" data-lesson-link data-lesson="{esc(feature['lesson'])}">Open topic guide</a> <a href="scripts/feature-{esc(feature['id'])}.txt">Read the guide</a>{(' · <a href="' + esc(feature['docs_url']) + '">Documentation</a>') if feature.get('docs_url') else ''}</p></div></details>'''
    settings_cards = ''.join(f'<details class="card setting-card" data-search="{esc((setting["label"]+" "+setting["help"]+" "+setting["area"]).lower())}"><summary>{esc(setting["label"])}</summary><div><p>{esc(setting["help"])}</p><p class="meta">Screen: {esc(setting.get("location", {}).get("Controller", "Department"))} → {esc(setting.get("location", {}).get("Action", "Settings"))}{(" · Default: " + esc(setting["default"])) if "default" in setting else ""}</p></div></details>' for setting in course['settings'])
    options = ''.join(f'<option value="{esc(role)}">{esc(role)}</option>' for role in course['learning_paths'])
    lesson_anchors = ''.join(f'<span id="lesson={esc(item["id"])}" aria-hidden="true"></span>' for item in course['lessons'])
    content = f'''<section class="hero home-hero"><div><p class="eyebrow">The Resgrid learning center</p><h1>Learn Resgrid.<br><span>Put it to work.</span></h1><p>Practical video walkthroughs and guides for the people who dispatch, respond, and run the department. Find the right tools, understand your settings, and learn at your own pace.</p><div class="actions"><a class="button primary" href="deep-dive/">Watch Resgrid walkthroughs</a><a class="button" href="#lessons">Explore topic guides</a></div><form class="quick-search" id="quick-search" role="search"><label for="quick-query">What would you like to learn?</label><div><input id="quick-query" type="search" placeholder="Try run cards, shifts, or mapping…"><button class="button primary" type="submit">Find a guide <span aria-hidden="true">→</span></button></div></form></div><a class="hero-feature" href="captures/firehouse51/" aria-label="Watch a connected department workflow"><span class="feature-label">A good place to begin</span><h2>See a connected department in action.</h2><img src="captures/firehouse51/01-dashboard.jpg" alt="Resgrid dashboard showing the fictional Firehouse 51 department" width="1280" height="720"><span class="feature-meta"><span>Real Resgrid screens · Captions and chapters</span><span class="play-badge" aria-hidden="true">▶</span></span></a></section><div class="academy-stats" aria-label="Academy library"><div><strong>{1 + len(ready) + sum(item['mode'] == 'video' for item in expansion)}</strong><span>video walkthroughs</span></div><div><strong>{len(course['lessons'])}</strong><span>topic guides</span></div><div><strong>{len(course['settings'])}</strong><span>configuration references</span></div></div><section class="learning-paths"><div class="section-heading"><div><p class="eyebrow">Start with your role</p><h2>Find your learning path.</h2></div><p>Focus on the workflows and decisions that matter to your day.</p></div><div class="grid">{paths}</div></section>{expansion_section(expansion, limit=4)}<section id="lessons"><div class="section-title"><p class="eyebrow">Explore the system</p><h2>Topic guides</h2><p>Read the purpose, setup decisions and practical use of each area.</p></div><div class="toolbar"><label class="small">Learning path<select id="path" aria-label="Learning path">{options}</select></label><label>Find a guide<input id="lesson-search" type="search" placeholder="Search shifts, inventory, records…"></label></div><p id="lesson-count" class="meta" role="status"></p><div class="grid" id="lesson-list">{lesson_cards}</div><p id="lesson-empty" class="empty hidden">No guides match. Try another topic or choose Complete series.</p></section><section id="learn">{lesson_anchors}<div class="section-title"><p class="eyebrow">Topic guide</p><h2 id="lesson-title">{esc(first['title'])}</h2><p id="lesson-audience" class="lead">{esc(first['role'])}</p></div><div class="layout"><article class="card transcript"><div id="transcript">{topic_sections(first)}</div><p style="margin-top:24px"><a id="transcript-link" href="{esc(first['transcript'])}" download>Download transcript</a> · <a id="topic-page-link" href="{esc(first['href'])}">Open topic page</a></p></article><aside class="card chapters"><h3>In this guide</h3><nav id="topic-outline" aria-label="Guide sections">{topic_outline(first)}</nav></aside></div><section class="panel"><h3>Apply this guide to your department</h3><div id="lesson-sectors">{sectors(first['sector_examples'])}</div></section></section><section id="videos" class="panel"><p class="eyebrow">See the steps in Resgrid</p><h2>Video walkthroughs</h2><p>Follow actual Resgrid screens through configuration and daily workflows using a fictional department. Videos include captions, chapters and downloads.</p><a class="button primary" href="deep-dive/">Watch the walkthroughs →</a> <a class="button" href="captures/firehouse51/">Follow a connected department workflow</a></section><section id="features"><div class="section-title"><p class="eyebrow">Find the right tool</p><h2>Feature guides</h2><p>Understand what a feature does, which problem it solves and how to prepare it.</p></div><div class="toolbar"><label>Search feature guides<input id="feature-search" type="search" placeholder="Search roles, run cards, workforce…"></label></div><p id="feature-count" class="meta" role="status"></p><div id="feature-list">{feature_cards}</div><p id="feature-empty" class="empty hidden">No feature guides match your search.</p></section><section id="settings"><div class="section-title"><p class="eyebrow">Make informed choices</p><h2>Configuration reference</h2><p>Review a setting’s purpose and its effects before changing your department configuration.</p></div><div class="toolbar"><label>Search settings<input id="setting-search" type="search" placeholder="Search dispatch, staffing, maps…"></label></div><p id="setting-count" class="meta" role="status"></p><div id="setting-list">{settings_cards}</div><p id="setting-empty" class="empty hidden">No settings match your search.</p></section>'''
    js = TOPIC_JS
    write('index.html', render('Learn the Resgrid system', content, js=js.replace('COURSE_DATA', script_data(course))))
    for lesson in course['lessons']:
        text = [lesson['title'], 'Audience: ' + lesson['role'], '']
        for scene in lesson['scenes']:
            text += [scene['title'], scene['narration'], '']
        text += ['Examples for your department'] + [name + ': ' + example for name, example in lesson.get('sector_examples', {}).items()]
        write(f'scripts/{lesson["id"]}.txt', '\n'.join(text) + '\n')
    for lesson in course['lessons']:
        body = f'<p class="eyebrow">Topic guide</p><h1>{esc(lesson["title"])}</h1><p class="lead">{esc(lesson["role"])}</p><div class="layout"><article class="card transcript">{topic_sections(lesson)}</article><aside class="card chapters"><h3>In this guide</h3><nav aria-label="Guide sections">{topic_outline(lesson)}</nav></aside></div><section class="panel"><h2>Apply it to your department</h2>{sectors(lesson["sector_examples"])}</section><p><a href="../../{esc(lesson["transcript"])}" download>Download transcript</a> · <a href="../../#lesson={esc(lesson["id"])}">Browse topic guides</a> · <a href="../../deep-dive/">Watch Resgrid walkthroughs</a></p>'
        write(f'topics/{lesson["id"]}/index.html', render(lesson['title'], body, '../../'))
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
        write(f'deep-dive/lessons/{ident}/index.html', render(lesson['title'], body, '../../../', PLAYER_JS))
        target = f'../../lessons/{ident}/'
        write(f'deep-dive/review/{ident}/index.html', '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=' + target + '"><title>' + esc(lesson['title']) + ' | Resgrid Academy</title></head><body><p><a href="' + target + '">Watch ' + esc(lesson['title']) + '</a></p></body></html>')
    write('deep-dive/index.html', render('Configuration walkthroughs', '<section class="hero"><p class="eyebrow">Put learning into practice</p><h1>Configure with confidence.</h1><p>See where to make a change, understand what it affects, and check the result. Follow these walkthroughs using a fictional department, then apply the lessons to your own operating needs.</p><div class="actions"><a class="button" href="sectors.html">Examples for your department</a><a class="button" href="../captures/firehouse51/">A connected department workflow</a></div></section><div class="grid">' + cards + '</div>' + expansion_section(expansion, '../') + '<section class="panel"><h2>Find another topic</h2><p>Explore topic guides and feature guides for personnel, permissions, run cards, shifts, mapping, inventory, records, training, workforce, billing and more.</p><a class="button primary" href="../#lessons">Browse the lesson library →</a></section>', '../'))

    sector_data = json.loads((sources / 'deep-dive/sector-examples.json').read_text())
    sector_data = {'sectors': list(course['lessons'][0]['sector_examples']), 'deep_lessons': [fields(item, ('id', 'title', 'topics', 'sector_examples')) for item in sector_data['deep_lessons']], 'primer_lessons': [fields(item, ('id', 'title', 'sector_examples')) for item in course['lessons']]}
    write('deep-dive/sector-examples.json', json.dumps(sector_data, ensure_ascii=False, indent=2) + '\n')
    write('deep-dive/course.json', json.dumps({'title': 'Resgrid configuration topics', 'lessons': sector_data['deep_lessons']}, ensure_ascii=False, indent=2) + '\n')
    sector_options = ''.join(f'<option>{esc(name)}</option>' for name in sector_data['sectors'])
    cards = ''.join(f'<article class="card sector-card" data-index="{index}"><p class="eyebrow">Department example</p><h3>{esc(item["title"])}</h3><p class="sector-example">{esc(item["sector_examples"][sector_data["sectors"][0]])}</p><a href="../#lesson={esc(item["id"])}">Explore this topic →</a></article>' for index, item in enumerate(sector_data['primer_lessons']))
    sector_js = 'const EXAMPLES=' + script_data(sector_data['primer_lessons']) + ''';const selector=document.getElementById('sector');const search=document.getElementById('sector-search');function update(){let count=0;document.querySelectorAll('.sector-card').forEach(card=>{const item=EXAMPLES[Number(card.dataset.index)];const text=item.sector_examples[selector.value];card.querySelector('.sector-example').textContent=text;const show=(item.title+' '+text).toLowerCase().includes(search.value.toLowerCase());card.classList.toggle('hidden',!show);if(show)count++;});document.getElementById('sector-count').textContent=count+' department examples';document.getElementById('sector-empty').classList.toggle('hidden',count!==0);}selector.addEventListener('change',update);search.addEventListener('input',update);update();'''
    write('deep-dive/sectors.html', render('Examples for your department', f'<section class="hero"><p class="eyebrow">Many departments. Shared coordination needs.</p><h1>Make Resgrid work for your team.</h1><p>Use Resgrid to coordinate people, resources and information across fire and EMS, community paramedicine and mental health response, search and rescue, security, wildland contracting and industrial emergency response.</p><p>Choose a department type to explore examples for each area. Use the roles, resources and procedures that fit your organization.</p></section><div class="toolbar"><label>Department type<select id="sector" aria-label="Department type">{sector_options}</select></label><label>Find a topic<input id="sector-search" type="search" placeholder="Search roster, visits, equipment…"></label></div><p id="sector-count" class="meta" role="status"></p><div class="grid">{cards}</div><p id="sector-empty" class="empty hidden">No examples match your search.</p>', '../', sector_js))

    chapters = json.loads((sources / 'captures/firehouse51/firehouse51-walkthrough.chapters.json').read_text())
    chapters[0]['title'] = 'Meet the example department'
    write('captures/firehouse51/firehouse51-walkthrough.chapters.json', json.dumps(chapters, indent=2) + '\n')
    manifest = json.loads((sources / 'captures/firehouse51/manifest.json').read_text())
    selected = ['02-personnel.jpg', '04-unit-configuration.jpg', '08-calls.jpg', '12-deployment-saved.jpg', '13-deployment-roster.jpg', '14-calendar.jpg', '15-custom-statuses.jpg']
    gallery = ''.join(f'<figure class="card"><img loading="lazy" src="{esc(item["file"])}" alt="{esc(item["title"])}"><figcaption>{esc(item["title"])}</figcaption></figure>' for item in manifest if item['file'] in selected)
    body = '<p class="eyebrow">A connected department workflow</p><h1>From people and resources to response and follow-up.</h1><p class="lead">Follow Firehouse 51 through roster setup, unit configuration, call handling, deployment and everyday readiness. The people and incidents in this example are fictional training data.</p>' + player('firehouse51-walkthrough.mp4', '01-dashboard.jpg', 'firehouse51-walkthrough.vtt', chapters, 'firehouse51-walkthrough.srt', '3.1 minutes · Resgrid screens') + '<section class="panel"><h2>Use the same workflow in your organization</h2><p>A community response team can coordinate a scheduled visit, a search team can assemble a deployment roster, and a security department can assign a patrol. Wildland contractors and industrial teams can connect resource assignments with equipment and readiness records.</p><a href="../../deep-dive/sectors.html">Explore examples for your department →</a></section><h2 class="section-title">Explore the workflow screens</h2><div class="grid">' + gallery + '</div>'
    write('captures/firehouse51/index.html', render('A connected department workflow', body, '../../', PLAYER_JS))
    body = '<section class="hero"><p class="eyebrow">Welcome to Resgrid Academy</p><h1>Learn, configure, apply.</h1><p>The Academy helps members, dispatchers and department administrators understand Resgrid and use it in daily work.</p></section><section class="panel"><h2>Choose how you learn</h2><p>Start with a role-based learning path, read a topic guide, or watch a configuration walkthrough. Videos include English captions, chapter navigation and downloadable transcripts. Feature guides explain a tool’s purpose, configuration and department impact.</p><a class="button primary" href="../#lessons">Explore topic guides</a> <a class="button" href="../deep-dive/">Follow a walkthrough</a></section><section class="panel"><h2>Practice with purpose</h2><p>Use a practice exercise to check your understanding. Identify the intended result, make a controlled change, save it, and review the outcome with the people and devices involved. Check feature availability, department permissions and any connected providers in your own Resgrid system.</p><p>Firehouse 51 is a fictional example department. Its names, incidents and configuration illustrate the workflow; your department’s procedures guide how you use it.</p></section><section class="panel"><h2>Apply the examples to your team</h2><p>The Academy includes examples for community paramedicine and mental health response, search and rescue, security companies and departments, wildland contractors and industrial emergency response teams, alongside fire and EMS.</p><a href="../deep-dive/sectors.html">Browse examples for your department →</a></section><section class="panel"><h2>Keep the reference close</h2><p>Use the <a href="../#features">feature guides</a> and <a href="../#settings">configuration reference</a> when reviewing settings. For additional product guidance, visit <a href="https://docs.resgrid.com/">Resgrid documentation</a>.</p></section>'
    write('about/index.html', render('About the Academy', body, '../'))
    # Preserve previously shared links without exposing authoring instructions.
    write('production/production-guide.html', render('About the Academy', body, '../'))
