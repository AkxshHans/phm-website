"""PHM Consulting site generator.
Reads the editable text in /content/*.json (changed through /admin) and writes the finished site to /public.
Run:  python3 _src/build.py            -> builds /public (Netlify runs this on every change)
      python3 _src/build.py --single X -> also writes a one-file preview to X
"""
import os, sys, html, json, base64, re, shutil, struct

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
OUT = os.path.join(ROOT, 'public')
CSS = open(os.path.join(SRC, 'style.css'), encoding='utf-8').read()
JS = open(os.path.join(SRC, 'site.js'), encoding='utf-8').read()
FORM_JS = open(os.path.join(SRC, 'form.js'), encoding='utf-8').read()

def load(name):
    return json.load(open(os.path.join(ROOT, 'content', name + '.json'), encoding='utf-8'))
SITE, HOME, ABOUT, SVC, CAN, CON, TST = (load(n) for n in ('site', 'home', 'about', 'services', 'canada', 'contact', 'testimonials'))

LIVE = 'https://www.phmconsulting.ca/'
EMAIL = (SITE.get('email') or 'phmconsulting.advisory@gmail.com').strip()
INSTA = (SITE.get('instagram_url') or '').strip()
HANDLE = (SITE.get('instagram_handle') or '').strip()
FONTS = 'https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wdth,wght@0,75..100,400..700;1,75..100,400..700&family=Geist+Mono:wght@400;500&display=swap'
ARR = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12L12 4M5.5 4H12v6.5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
IG = '<svg class="ig" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.4" cy="6.6" r="1.2" fill="currentColor"/></svg>'

def e(s):  # escape for attributes and text
    return html.escape(str(s or ''), quote=True)
def t(s):  # escape for text only (keeps apostrophes readable in the source)
    return html.escape(str(s or ''), quote=False)
def items(v):
    return [x for x in (v or []) if x not in (None, '', {})]
def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', str(s).lower()).strip('-')

PAGES = [('home', 'index.html', ''), ('about', 'about.html', ''), ('services', 'services.html', ''),
         ('canadian-market-entry', 'services/canadian-market-entry/index.html', '../../'), ('contact', 'contact.html', '')]
FILE = {p: f for p, f, _ in PAGES}
CANON = {'home': '', 'about': 'about.html', 'services': 'services.html', 'canadian-market-entry': 'services/canadian-market-entry', 'contact': 'contact.html'}
META = {'home': HOME['seo'], 'about': ABOUT['seo'], 'services': SVC['seo'], 'canadian-market-entry': CAN['seo'], 'contact': CON['seo']}

MODE, PFX = 'site', ''
def href(pid, anchor=''):
    if MODE == 'single':
        return '#' + (anchor or pid)
    return PFX + FILE[pid] + ('#' + anchor if anchor else '')

def img_path(p):
    p = str(p or '').strip().lstrip('/')
    return p if p.startswith('assets/') else 'assets/' + p
def asset(p):
    p = img_path(p)
    if MODE == 'single':
        ext = p.rsplit('.', 1)[-1].lower()
        mime = {'png': 'image/png', 'webp': 'image/webp', 'gif': 'image/gif', 'svg': 'image/svg+xml'}.get(ext, 'image/jpeg')
        return f'data:{mime};base64,' + base64.b64encode(open(os.path.join(ROOT, p), 'rb').read()).decode()
    return PFX + p
def img_size(p, fallback):
    """Width/height of a JPEG/PNG/WebP without extra libraries (used only to reserve space while loading)."""
    try:
        with open(os.path.join(ROOT, img_path(p)), 'rb') as f:
            d = f.read(512 * 1024)
        if d[:8] == b'\x89PNG\r\n\x1a\n':
            return struct.unpack('>II', d[16:24])
        if d[:4] == b'RIFF' and d[8:12] == b'WEBP':
            if d[12:16] == b'VP8X': return (int.from_bytes(d[24:27], 'little') + 1, int.from_bytes(d[27:30], 'little') + 1)
            if d[12:16] == b'VP8 ': return (struct.unpack('<H', d[26:28])[0] & 0x3fff, struct.unpack('<H', d[28:30])[0] & 0x3fff)
        if d[:2] == b'\xff\xd8':
            i = 2
            while i < len(d) - 9:
                if d[i] != 0xFF: i += 1; continue
                m = d[i + 1]
                if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack('>HH', d[i + 5:i + 9]); return (w, h)
                i += 2 + struct.unpack('>H', d[i + 2:i + 4])[0]
    except Exception:
        pass
    return fallback

def blk(h, label, cls='', attrs=''):
    return f'<a class="blk {cls}" href="{h}"{attrs}>{t(label)} {ARR}</a>'

# ---------------- services ----------------
SERVICES = []
for s in items(SVC.get('services')):
    s = dict(s); s['id'] = slug(s.get('name', '')); s['page'] = 'canadian-market-entry' if s.get('opens_canada_page') else None
    SERVICES.append(s)
CANADA_NAME = next((s['name'] for s in SERVICES if s['page']), 'Canadian Market Entry and Business Setup')
HELP_OPTIONS = [s['name'] for s in SERVICES] + ['Not Sure Yet']
SCOPE = SVC.get('scope_note', '')

ORG_LD = {"@context": "https://schema.org", "@type": "ProfessionalService", "name": "PHM Consulting", "url": LIVE, "email": EMAIL,
          "logo": LIVE + "assets/phm-logo-full.png", "slogan": SITE.get('footer_tagline', ''),
          "description": META['home']['description'], "areaServed": {"@type": "Country", "name": "Canada"}, "sameAs": [INSTA] if INSTA else []}

# ---------------- shared parts ----------------
NAV = [('home', 'Home'), ('about', 'About Us'), ('services', 'Services')]
def header(pid):
    cur = 'services' if pid == 'canadian-market-entry' else pid
    links = ''.join(f'<a href="{href(p)}"' + (' aria-current="page"' if p == cur else '') + f'>{n}</a>' for p, n in NAV)
    mlinks = ''.join(f'<li><a href="{href(p)}">{n}</a></li>' for p, n in NAV + [('contact', 'Contact')])
    back = '' if (pid == 'home' and MODE == 'site') else f'<a class="back-btn" href="{href("home")}" data-back><span aria-hidden="true">&larr;</span> Back</a>'
    cc = ' aria-current="page"' if pid == 'contact' else ''
    return f'''<header class="hdr">
  <div class="g12">
    <a class="logo" href="{href('home')}" aria-label="PHM Consulting home"><img src="{asset('phm-logo-full.png')}" alt="PHM Consulting" width="1094" height="453"></a>
    {back}
    <nav class="nav" aria-label="Main">{links}</nav>
    <a class="blk hdr-cta" href="{href('contact')}"{cc}>Contact {ARR}</a>
    <button class="blk menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu"><span>Menu</span></button>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" inert>
  <ul>{mlinks}</ul>
  <p class="label"><a href="mailto:{e(EMAIL)}">{t(EMAIL)}</a></p>
</div>
'''

def footer():
    ig = f'<li><a href="{e(INSTA)}" rel="noopener">{IG}<span>Instagram: {t(HANDLE)}</span></a></li>' if INSTA else ''
    return f'''<footer class="ftr">
  <div class="wrap">
    <div class="g12 cols">
      <div class="c1">
        <p class="f-name">{t(SITE.get('footer_name'))}</p>
        <p class="f-tag">{t(SITE.get('footer_tagline'))}</p>
        <p class="f-desc">{t(SITE.get('footer_description'))}</p>
      </div>
      <nav class="c2" aria-label="Footer">
        <ul class="f-nav"><li><a href="{href('home')}">Home</a></li><li><a href="{href('about')}">About Us</a></li><li><a href="{href('services')}">Services</a></li><li><a href="{href('contact')}">Contact</a></li></ul>
      </nav>
      <div class="c3">
        <ul class="f-links">
          {ig}
          <li><a href="mailto:{e(EMAIL)}">{t(EMAIL)}</a></li>
          <li><a href="{LIVE}">phmconsulting.ca</a></li>
        </ul>
      </div>
    </div>
    <p class="legal label">&copy; <span data-year>2026</span> PHM Consulting. All rights reserved.</p>
  </div>
</footer>
'''

def marquee():
    words = items(SITE.get('strip_words')) or ['Planning', 'High Performance', 'Momentum']
    item = ''.join(f'<span>{t(w)}</span><i class="spark"></i>' for w in words)
    static = ' <i class="spark"></i> '.join(t(w) for w in words)
    return ('<div class="mq" aria-hidden="true"><div class="mq-in"><div class="mq-t">' + item * 3 + '</div><div class="mq-t">' + item * 3 +
            f'</div></div><p class="mq-static">{static}</p></div>')

def ticker():
    if not TST.get('show_on_homepage', True):
        return ''
    lis = ''
    for q in items(TST.get('items')):
        text = str(q.get('quote', '')).strip()
        if not text:
            continue
        who = ', '.join(x for x in (str(q.get('name', '')).strip(), str(q.get('role', '')).strip(), str(q.get('organization', '')).strip()) if x)
        cite = f'<span class="tq-who">&mdash; {t(who)}</span>' if who else ''
        lis += f'<li><span class="tq-mark" aria-hidden="true">“</span>{t(text)}<span aria-hidden="true">”</span>{cite}</li>'
    if not lis:
        return ''
    return f'''<section class="tq" aria-label="What clients say">
  <h2 class="sr-only">What clients say</h2>
  <div class="tq-in"><ul class="tq-t">{lis}</ul><ul class="tq-t" aria-hidden="true">{lis}</ul></div>
</section>'''

def svc_link(s):
    if s.get('page'):
        return blk(href(s['page']), s.get('button'), 'sm')
    return blk(href('contact'), s.get('button'), 'sm', f' data-service="{e(s["name"])}"')

# ---------------- pages ----------------
def home():
    h = HOME['hero']; hw = HOME['how_we_work']; c = HOME['connect']
    cols = ''.join(f'<article class="col on"><span class="idx">{i+1:02d}</span><h3>{t(x.get("title"))}</h3><p>{t(x.get("text"))}</p></article>' for i, x in enumerate(items(hw.get('items'))))
    svc = ''
    for i, s in enumerate(SERVICES):
        link = href(s['page']) if s.get('page') else href('services', s['id'])
        lab = f'<span class="tag small">{t(s["tag"])}</span>' if s.get('tag') else ''
        svc += f'<li><a href="{link}"><span class="sn">{i+1:02d}</span><span class="st">{t(s["name"])}{lab}</span>{ARR}</a></li>'
    gold = f' <span class="gold">{t(h.get("title_gold"))}</span>' if h.get('title_gold') else ''
    return f'''
<section class="hero" data-theme="dark" aria-labelledby="h1">
  <canvas class="stars" aria-hidden="true"></canvas>
  <div class="wrap hero-top">
    <h1 id="h1" data-split>{t(h.get('title'))}{gold}</h1>
    <div class="g12 hero-copy">
      <p class="body fade" style="--d:.8s">{t(h.get('intro'))}</p>
      <div class="btns fade" style="--d:.95s">{blk(href('contact'), h.get('button_primary'), 'gold', ' data-consult')}{blk(href('services'), h.get('button_secondary'), 'ghost')}</div>
    </div>
  </div>
  <div class="hero-earth" aria-hidden="true"><img src="{asset('earth.jpg')}" alt="" width="2896" height="942" fetchpriority="high"><div class="sun"></div></div>
</section>
<section class="hero-more" data-theme="dark" aria-label="How PHM helps">
  <div class="wrap"><p>{t(HOME.get('statement'))}</p></div>
</section>
{marquee()}
<section class="help approach" data-theme="dark" aria-labelledby="ap-t">
  <canvas class="stars" aria-hidden="true"></canvas>
  <div class="wrap" style="position:relative;z-index:2">
    <h2 class="big" id="ap-t">{t(hw.get('heading'))}</h2>
    <div class="cols3">{cols}</div>
  </div>
</section>

<section class="our-svc light" aria-labelledby="os-t">
  <div class="wrap">
    <h2 class="sec-h" id="os-t">{t(HOME.get('services_heading'))}</h2>
    <ul class="svc-list5">{svc}</ul>
  </div>
</section>

{ticker()}
<section class="contact" id="get-started" data-theme="dark" aria-labelledby="ct-t">
  <div class="wrap">
    <h2 class="sec-h" id="ct-t">{t(c.get('heading'))}</h2>
    <div class="copy">
      <p>{t(c.get('text'))}</p>
      {blk(href('contact'), c.get('button'), 'gold', ' data-consult')}
      <p class="mail">{t(c.get('email_line'))} <a href="mailto:{e(EMAIL)}">{t(EMAIL)}</a></p>
    </div>
  </div>
</section>
'''

def about():
    def pcard(p):
        w, h = img_size(p.get('photo'), (1187, 1326))
        return f'''<article class="pcard">
        <img src="{asset(p.get('photo'))}" alt="{e(p.get('name'))}, {e(p.get('title'))} at PHM Consulting" width="{w}" height="{h}" loading="lazy">
        <h3>{t(p.get('name'))}</h3>
        <p class="label role">{t(p.get('title'))}</p>
        <p class="bio">{t(p.get('bio'))}</p>
      </article>'''
    why = ABOUT['why']; team = ABOUT['team']
    paras = ''.join(f'\n      <p class="muted">{t(p)}</p>' for p in items(ABOUT.get('paragraphs')))
    principles = ' <span aria-hidden="true">&bull;</span> '.join(t(p) for p in items(ABOUT.get('principles')))
    diff = f'\n      <p class="diff">{principles}</p>' if principles else ''
    pts = ''.join(f'<li>{t(p)}</li>' for p in items(why.get('points')))
    return f'''
<section class="phead about-head" style="background:var(--cream-hero)" aria-labelledby="ab-t">
  <div class="leak" aria-hidden="true"></div>
  <div class="wrap" style="position:relative">
    <span class="label">{t(ABOUT.get('label'))}</span>
    <h1 id="ab-t">{t(ABOUT.get('heading'))}</h1>
    <div class="lede">
      <p>{t(ABOUT.get('intro'))}</p>{paras}{diff}
    </div>
  </div>
</section>
{marquee()}
<section class="why" data-theme="dark" aria-labelledby="why-t">
  <div class="wrap">
    <h2 class="sec-h" id="why-t">{t(why.get('heading'))}</h2>
    <p class="why-p">{t(why.get('text'))}</p>
    <ul class="why-pts">{pts}</ul>
  </div>
</section>
<section class="light principals" aria-labelledby="pr-t">
  <div class="wrap">
    <h2 class="sec-h" id="pr-t">{t(team.get('heading'))}</h2>
    <p class="label sub">{t(team.get('subheading'))}</p>
    <div class="pgrid">
      {''.join(pcard(p) for p in items(team.get('people')))}
    </div>
    <div class="cta-one">{blk(href('contact'), ABOUT.get('button'), '', ' data-consult')}</div>
  </div>
</section>
'''

def services():
    idx = ''.join(f'<li><a href="{href("services", s["id"])}"><span class="sn">{i+1:02d}</span>{t(s["name"])}</a></li>' for i, s in enumerate(SERVICES))
    rows = ''
    for i, s in enumerate(SERVICES):
        lab = f'<span class="tag small">{t(s["tag"])}</span>' if s.get('tag') else ''
        note = f'<p class="note">{t(SCOPE)}</p>' if s.get('page') and SCOPE else ''
        hint = SVC.get('hint_page') if s.get('page') else SVC.get('hint_enquiry')
        rows += f'''<article class="row svc-row g12 nomedia" id="{s["id"]}" aria-labelledby="{s["id"]}-t">
      <div class="meta">
        <span class="idx">{i+1:02d}</span>
        {lab}
        <h2 id="{s["id"]}-t">{t(s["name"])}</h2>
        <p class="desc">{t(s.get("description"))}</p>
        <p class="get"><span class="label">{t(s.get("outcomes_label"))}</span> {t(s.get("outcomes"))}</p>
        {note}
        <div class="act">{svc_link(s)}</div>
        <p class="btn-hint">{t(hint)}</p>
      </div>
    </article>'''
    return f'''
<section class="phead svc-head" data-theme="dark" aria-labelledby="sv-t">
  <div class="wrap">
    <span class="label">{t(SVC.get('label'))}</span>
    <h1 id="sv-t">{t(SVC.get('heading'))}</h1>
    <p class="intro">{t(SVC.get('intro'))}</p>
    <nav aria-label="Services on this page"><ol class="svc-index">{idx}</ol></nav>
  </div>
</section>
<section class="light svc-rows" aria-label="Service details">
  <div class="wrap">{rows}</div>
</section>
'''

def canada():
    C = CAN
    cta = blk(href('contact'), C.get('button'), 'gold', f' data-service="{e(CANADA_NAME)}"')
    intro = ''.join(f'\n      <p>{t(p)}</p>' for p in items(C.get('intro')))
    w, h = img_size(C.get('photo'), (1536, 1024))
    photo = f'''<section class="light cm-photo" aria-label="{e(C.get('photo_alt'))}"><div class="wrap"><figure><img src="{asset(C.get('photo'))}" alt="{e(C.get('photo_alt'))}" width="{w}" height="{h}" loading="lazy"></figure></div></section>''' if C.get('photo') else ''
    who, how, ex, why, faq, talk = C['who'], C['how'], C['expect'], C['why'], C['faq'], C['talk']
    whyp = ''.join(f'\n      <p>{t(p)}</p>' for p in items(why.get('paragraphs')))
    return f'''
<section class="phead cm-head" data-theme="dark" aria-labelledby="cm-t">
  <canvas class="stars" aria-hidden="true"></canvas>
  <div class="wrap" style="position:relative;z-index:2">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{href('home')}">Home</a></li><li><a href="{href('services')}">Services</a></li><li aria-current="page">{t(C.get('breadcrumb'))}</li></ol></nav>
    {f'<span class="tag small">{t(C.get("tag"))}</span>' if C.get('tag') else ''}
    <h1 id="cm-t">{t(C.get('heading'))}</h1>
    <p class="cm-lead">{t(C.get('lead'))}</p>
    <div class="cm-intro">{intro}
    </div>
    <div class="btns">{cta}</div>
  </div>
</section>
{photo}
<section class="light cm-sec" aria-labelledby="who-t">
  <div class="wrap two">
    <div><h2 class="sec-h" id="who-t">{t(who.get('heading'))}</h2><p class="muted">{t(who.get('intro'))}</p></div>
    <ul class="ticks">{''.join(f'<li>{t(x)}</li>' for x in items(who.get('items')))}</ul>
  </div>
</section>
<section class="cm-sec cm-how" data-theme="dark" aria-labelledby="how-t">
  <div class="wrap">
    <h2 class="sec-h" id="how-t">{t(how.get('heading'))}</h2>
    <ol class="steps">{''.join(f'<li><span class="idx">{i+1:02d}</span><h3>{t(x.get("title"))}</h3><p>{t(x.get("text"))}</p></li>' for i, x in enumerate(items(how.get('items'))))}</ol>
  </div>
</section>
<section class="light cm-sec" aria-labelledby="ex-t">
  <div class="wrap two">
    <div><h2 class="sec-h" id="ex-t">{t(ex.get('heading'))}</h2><p class="muted">{t(ex.get('intro'))}</p></div>
    <div><ul class="ticks">{''.join(f'<li>{t(x)}</li>' for x in items(ex.get('items')))}</ul>
    <p class="cm-small">{t(ex.get('note'))}</p></div>
  </div>
</section>
<section class="cm-sec cm-why" style="background:var(--cream-hero)" aria-labelledby="cw-t">
  <div class="wrap two">
    <div><h2 class="sec-h" id="cw-t">{t(why.get('heading'))}</h2><p class="cm-tagline">{t(why.get('tagline'))}</p></div>
    <div class="cm-body">{whyp}
    </div>
  </div>
</section>
<section class="light cm-sec" aria-labelledby="faq-t">
  <div class="wrap two">
    <h2 class="sec-h" id="faq-t">{t(faq.get('heading'))}</h2>
    <div class="faq">{''.join(f'<details><summary>{t(x.get("question"))}</summary><p>{t(x.get("answer"))}</p></details>' for x in items(faq.get('items')))}</div>
  </div>
</section>
<section class="cm-sec cm-talk" data-theme="dark" aria-labelledby="tk-t">
  <div class="wrap">
    <h2 class="sec-h" id="tk-t">{t(talk.get('heading'))}</h2>
    <p>{t(talk.get('text'))}</p>
    <div class="btns">{cta}</div>
    <p class="note dark-note">{t(SCOPE)}</p>
    <a class="back-link" href="{href('services')}"><span aria-hidden="true">&larr;</span> {t(talk.get('back_link'))}</a>
  </div>
</section>
'''

def contact():
    C = CON
    radios = ''.join(f'<label class="chip"><input type="radio" name="service" value="{e(o)}" required><span>{t(o)}</span></label>' for o in HELP_OPTIONS)
    ig = f'<li><a href="{e(INSTA)}" rel="noopener">{IG}<span>Instagram: {t(HANDLE)}</span></a></li>' if INSTA else ''
    w, h = img_size(C.get('photo'), (1122, 1402))
    photo = f'<figure class="c-photo"><img src="{asset(C.get("photo"))}" alt="{e(C.get("photo_alt"))}" width="{w}" height="{h}" loading="lazy"></figure>' if C.get('photo') else ''
    return f'''
<section class="intake" aria-labelledby="in-t">
  <div class="leak" aria-hidden="true"></div>
  <div class="wrap" style="position:relative">
    <div class="g12">
      <div class="intro">
        <span class="label">{t(C.get('label'))}</span>
        <h1 id="in-t">{t(C.get('heading'))}</h1>
        <p class="lead">{t(C.get('lead'))}</p>
        <ul class="c-links">
          <li>{t(C.get('email_prefix'))} <a href="mailto:{e(EMAIL)}">{t(EMAIL)}</a></li>
          {ig}
        </ul>
        <figure class="qr"><img src="{asset('instagram-qr.png')}" alt="QR code that opens the PHM Consulting Instagram page, @phmconsulting" width="656" height="656" loading="lazy"><figcaption>{t(C.get('qr_caption'))}</figcaption></figure>
        {photo}
      </div>
      <div class="fcard">
        <div class="fband" aria-hidden="true"></div>
        <div class="fbody">
          <p class="fnote">Fields marked <span class="req" aria-hidden="true">*</span><span class="sr-only">with an asterisk</span> are required.</p>
          <div class="errsum" id="errsum" tabindex="-1" hidden></div>
          <form id="enquiry-form" novalidate>
            <div class="fgrid">
              <div class="field"><label for="name">Your name <span class="req" aria-hidden="true">*</span></label><input type="text" id="name" name="name" autocomplete="name" maxlength="120" required aria-describedby="name-err"><p class="err" id="name-err"></p></div>
              <div class="field"><label for="organization">Organization</label><input type="text" id="organization" name="organization" autocomplete="organization" maxlength="180"></div>
              <div class="field"><label for="email">Email address <span class="req" aria-hidden="true">*</span></label><input type="email" id="email" name="email" autocomplete="email" maxlength="254" required aria-describedby="email-err"><p class="err" id="email-err"></p></div>
              <div class="field"><label for="phone">Phone number</label><input type="tel" id="phone" name="phone" autocomplete="tel" maxlength="50"></div>
              <fieldset class="field full" aria-describedby="service-err">
                <legend>How can we help? <span class="req" aria-hidden="true">*</span></legend>
                <div class="chips">{radios}</div>
                <p class="err" id="service-err"></p>
              </fieldset>
              <div class="field full"><label for="challenge">What’s your biggest challenge?</label><textarea id="challenge" name="challenge" maxlength="3000" placeholder="Tell us a little about what’s happening."></textarea></div>
              <fieldset class="field full budget" aria-describedby="budget-err">
                <legend>What’s your approximate budget?</legend>
                <div class="bud">
                  <div class="amt"><span class="cur" aria-hidden="true">CAD $</span><label class="sr-only" for="budgetAmount">Budget amount in Canadian dollars</label><input type="text" id="budgetAmount" name="budgetAmount" inputmode="decimal" maxlength="15" placeholder="Amount"></div>
                  <span class="or" aria-hidden="true">or</span>
                  <label class="chip"><input type="checkbox" name="budgetOption" value="Not sure yet"><span>Not sure yet</span></label>
                  <label class="chip"><input type="checkbox" name="budgetOption" value="Prefer to discuss"><span>Prefer to discuss</span></label>
                </div>
                <p class="err" id="budget-err"></p>
              </fieldset>
            </div>
            <div class="hp" aria-hidden="true"><label for="websiteConfirm">Leave this field empty</label><input type="text" id="websiteConfirm" name="websiteConfirm" tabindex="-1" autocomplete="off"></div>
            <p class="privacy"><b>Privacy notice:</b> {t(C.get('privacy_note'))}</p>
            <div class="send"><button class="blk gold" type="submit" id="send-btn"><span class="lbl">{t(C.get('button'))}</span> {ARR}</button></div>
            <div class="status" id="form-status" role="status" aria-live="polite"></div>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>
'''

BUILDERS = {'home': home, 'about': about, 'services': services, 'canadian-market-entry': canada, 'contact': contact}

def head(pid, single=False):
    title, desc = (META[pid]['title'], META[pid]['description']) if not single else ('PHM Consulting · Website preview', META['home']['description'])
    canon = LIVE + CANON[pid]
    ld = f'<script type="application/ld+json">{json.dumps(ORG_LD)}</script>\n' if pid == 'home' else ''
    robots = '<meta name="robots" content="noindex">\n' if single else '''<script>/* only phmconsulting.ca is indexed; previews get noindex */
if (!/(^|\\.)phmconsulting\\.ca$/.test(location.hostname)) { var m = document.createElement('meta'); m.name = 'robots'; m.content = 'noindex, nofollow'; document.head.appendChild(m); }</script>
'''
    return f'''<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{'' if single else f'<link rel="canonical" href="{canon}">'}
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#071A30">
{robots}{ld}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js" defer></script>
<style>
{CSS}
</style>
</head>
'''

def scripts(pid=None, single=False):
    js = JS.replace("if (same && history.length > 1)", "if (history.length > 1)") if single else JS
    s = f'<script>\n{"window.PHM_SINGLE = true;" if single else ""}\n{js}\n</script>\n'
    if single or pid == 'contact':
        s += f'<script>\n{FORM_JS}\n</script>\n'
    return s

def page(pid):
    return (head(pid) + f'<body data-page="{pid}">\n<a class="skip" href="#main">Skip to content</a>\n<div class="grain" aria-hidden="true"></div>\n'
            + header(pid) + '<main id="main">\n' + BUILDERS[pid]() + '\n</main>\n' + footer() + scripts(pid) + '</body>\n</html>\n')

# ---------------- write the site to /public ----------------
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
for pid, f, pfx in PAGES:
    MODE, PFX = 'site', pfx
    path = os.path.join(OUT, f); os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(page(pid))
shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'), ignore=shutil.ignore_patterns('.gitkeep'))
shutil.copytree(os.path.join(ROOT, 'admin'), os.path.join(OUT, 'admin'))
open(os.path.join(OUT, 'client-intake.html'), 'w').write('<!DOCTYPE html><html lang="en-CA"><head><meta charset="utf-8"><title>Contact PHM Consulting</title><meta name="robots" content="noindex"><link rel="canonical" href="' + LIVE + 'contact.html"><meta http-equiv="refresh" content="0; url=contact.html"></head><body><p><a href="contact.html">Continue to the contact page</a></p></body></html>\n')
open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{LIVE}{CANON[p]}</loc></url>\n' for p, _, _ in PAGES) + '</urlset>\n')
open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {LIVE}sitemap.xml\n')
print('Built', len(PAGES), 'pages into', OUT)

# ---------------- optional one-file preview ----------------
if '--single' in sys.argv:
    dest = sys.argv[sys.argv.index('--single') + 1]
    MODE, PFX = 'single', ''
    TITLES = {p: META[p]['title'] for p in BUILDERS}
    mains = ''.join(f'<div class="page" id="{p}"{"" if p == "home" else " hidden"}>{BUILDERS[p]()}</div>\n' for p, _, _ in PAGES)
    router = open(os.path.join(SRC, 'router.js'), encoding='utf-8').read() % json.dumps(TITLES)
    doc = head('home', single=True) + '<body data-page="home">\n<a class="skip" href="#main">Skip to content</a>\n<div class="grain" aria-hidden="true"></div>\n'
    doc += header('home') + '<main id="main">\n' + mains + '</main>\n' + footer() + scripts(single=True) + f'<script>\n{router}\n</script>\n</body>\n</html>\n'
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    open(dest, 'w', encoding='utf-8').write(doc)
    print('Preview written to', dest)
