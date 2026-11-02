"""Shared Resgrid branding for every learner-facing Academy layout."""
from datetime import datetime, timezone
import html
from pathlib import Path
import shutil

BRAND_DIRECTORY = Path(__file__).resolve().parents[1] / 'sources/brand'
CSS = (BRAND_DIRECTORY / 'academy.css').read_text(encoding='utf-8')
ASSETS = ('resgrid-logo.png', 'favicon.ico', 'favicon.svg', 'favicon-16x16.png',
          'favicon-32x32.png', 'apple-touch-icon.png')


def brand_head(prefix=''):
    prefix = html.escape(prefix, quote=True)
    return f'''<link rel="icon" href="{prefix}favicon.ico" sizes="48x48"><link rel="icon" href="{prefix}favicon-32x32.png" sizes="32x32" type="image/png"><link rel="icon" href="{prefix}favicon-16x16.png" sizes="16x16" type="image/png"><link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&family=Noto+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">'''


def brand_header(prefix='', expansion=False):
    home = prefix or './'
    links = [(prefix + 'deep-dive/', 'Video tutorials'),
             (prefix + '#lessons', 'Topic guides')]
    if expansion:
        links.append((prefix + 'walkthroughs/', 'Apps and configuration'))
    links.append((prefix + '#features', 'Feature guides'))
    nav = ''.join(f'<a href="{html.escape(url, quote=True)}">{label}</a>' for url, label in links)
    resources = '<a href="https://resgrid.com/">Resgrid.com</a><a href="https://docs.resgrid.com/">Docs</a><a class="button primary login-link" href="https://app.resgrid.com/Account/LogOn">Log in <span aria-hidden="true">↗</span></a>'
    return f'''<header class="site-header"><div class="bar"><a class="brand" href="{html.escape(home, quote=True)}" aria-label="Resgrid Academy home"><img src="{html.escape(prefix, quote=True)}assets/resgrid-logo.png" alt="Resgrid" width="112" height="44"><span>Academy</span></a><nav class="desktop-nav" aria-label="Academy">{nav}</nav><nav class="header-resources" aria-label="Resgrid resources">{resources}</nav><details class="mobile-nav"><summary>Menu <span aria-hidden="true">☰</span></summary><nav aria-label="Academy mobile">{nav}{resources}</nav></details></div></header>'''


def brand_footer(prefix=''):
    prefix = html.escape(prefix, quote=True)
    year = datetime.now(timezone.utc).year
    return f'''<footer class="site-footer"><div class="footer-grid"><div class="footer-intro"><img src="{prefix}assets/resgrid-logo.png" alt="Resgrid" width="112" height="44"><p class="footer-title">Resgrid Academy</p><p>Learn the tools. Configure with confidence. Put your knowledge to work.</p></div><nav aria-label="Academy learning resources"><h2>Keep learning</h2><a href="{prefix}deep-dive/">Video tutorials</a><a href="{prefix}#lessons">Topic guides</a><a href="{prefix}#settings">Configuration reference</a><a href="{prefix}deep-dive/sectors.html">Examples for your department</a><a href="{prefix}about/">About the Academy</a></nav><nav aria-label="Resgrid platform resources"><h2>Resgrid resources</h2><a href="https://resgrid.com/">Resgrid website</a><a href="https://docs.resgrid.com/">Documentation</a><a href="https://app.resgrid.com/Account/LogOn">Application login</a><a href="https://resgrid.com/apps">Resgrid applications</a><a href="https://github.com/Resgrid">Open source</a></nav><nav aria-label="Help and support"><h2>Need a hand?</h2><a href="https://resgrid.zohodesk.com/portal">Knowledge center</a><a href="https://resgrid.zohodesk.com/portal/en/newticket">Submit a support ticket</a><a href="https://resgrid.com/contact">Contact Resgrid</a><a href="https://blog.resgrid.com/">Resgrid blog</a></nav></div><div class="footer-bottom"><span>© {year} Resgrid, LLC. Learn, configure, apply.</span><span><a href="https://resgrid.com/privacy">Privacy</a><a href="https://resgrid.com/terms">Terms</a></span></div></footer>'''


def write_brand_assets(destination, sources):
    destination, source = Path(destination), Path(sources) / 'brand'
    for name in ASSETS:
        original = source / name
        if original.is_symlink() or not original.is_file():
            raise ValueError('Missing or symlinked Academy brand asset: ' + name)
        target = destination / ('assets/' + name if name == 'resgrid-logo.png' else name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
