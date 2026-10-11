"""Render crawlable HTML with Python's standard library; commit the output for Pages.

Content: assets/content.js, site.json, templates/*.html.
No runtime dependencies or JavaScript rendering required for indexing.
"""
import argparse
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'assets/content.js').read_text().split('window.siteContent = ', 1)[1].strip().removesuffix(';'))
SITE = json.loads((ROOT / 'site.json').read_text())
BASE = SITE['url'].rstrip('/') + '/'
assert urlparse(BASE).scheme == 'https' and urlparse(BASE).netloc, 'Set the public HTTPS URL in site.json'
TEMPLATE = (ROOT / 'templates/base.html').read_text()
SERVICES = {
    'technologiczne': ('projekty-technologiczne-gastronomii/', 'Projekty technologiczne gastronomii', 'gastronomy.html',
        'Projekty technologiczne gastronomii Wrocław | Good Taste',
        'Projekty technologiczne gastronomii we Wrocławiu i na Dolnym Śląsku. Zobacz portfolio Good Taste i porozmawiaj o projekcie restauracji lub lokalu.'),
    'mieszkania': ('projektowanie-wnetrz/', 'Projektowanie wnętrz', 'interiors.html',
        'Projektowanie wnętrz Wrocław i Dolny Śląsk | Good Taste',
        'Projektowanie wnętrz mieszkań we Wrocławiu i na Dolnym Śląsku. Poznaj projekty Good Taste: salony, kuchnie, sypialnie i łazienki. Porozmawiajmy o wnętrzu.')
}
OUTPUT = {}
PAGES = []


def fill(template, **values):
    for key, value in values.items():
        template = template.replace('{{' + key + '}}', value)
    return template


def crumbs(items, root):
    links = [f'<li><a href="{root}{path}">{escape(label)}</a></li>' if path is not None
             else f'<li aria-current="page">{escape(label)}</li>' for label, path in items]
    return '<nav class="breadcrumbs" aria-label="Ścieżka nawigacji"><ol>' + ''.join(links) + '</ol></nav>'


def cards(key, root):
    result = []
    for i, project in enumerate(DATA['galleries'][key]['projects']):
        item = project['images'][0]
        path = root + 'projekty/' + project['slug'] + '/'
        result.append(f'''<article class="project-entry">
          <a class="project-card" href="{path}" data-gallery-key="{key}" data-project-index="{i}">
            <span class="project-visual"><img src="{root}{project['cover']}" alt="{escape(item['alt'])}" width="{item['width']}" height="{item['height']}" loading="lazy" decoding="async"><span class="project-enlarge" aria-hidden="true">+</span></span>
            <span class="project-caption"><strong>{escape(project['title'])}</strong></span>
          </a>
          <a class="project-details" href="{path}">O projekcie <span class="sr-only">{escape(project['title'])}</span><span aria-hidden="true"> ↗</span></a>
        </article>''')
    return '\n'.join(result)


def render(path, title, description, body, image='assets/images/showcase.webp', extra=None, trail=None, image_alt='Projekty wnętrz Good Taste'):
    root = '../' * path.count('/') if path else './'
    url = BASE + path
    organization = {'@type': 'Organization', '@id': BASE + '#organization', 'name': SITE['name'], 'url': BASE,
                    'logo': BASE + 'assets/images/logo.png', 'areaServed': {'@type': 'AdministrativeArea', 'name': 'województwo dolnośląskie'}}
    for key, schema_key in [('email', 'email'), ('phone', 'telephone')]:
        if DATA.get(key):
            organization[schema_key] = DATA[key]
    if DATA.get('facebook', '').startswith('https://'):
        organization['sameAs'] = [DATA['facebook']]
    graph = [organization, {'@type': 'WebSite', '@id': BASE + '#website', 'url': BASE, 'name': SITE['name'], 'inLanguage': 'pl-PL', 'publisher': {'@id': BASE + '#organization'}},
             {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': title, 'description': description,
              'inLanguage': 'pl-PL', 'isPartOf': {'@id': BASE + '#website'}, 'primaryImageOfPage': {'@type': 'ImageObject', 'url': BASE + image}}]
    if extra:
        graph.append(extra)
        graph[2]['mainEntity'] = {'@id': extra['@id']}
    if trail:
        graph.append({'@type': 'BreadcrumbList', '@id': url + '#breadcrumbs', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': label, 'item': BASE + (target if target is not None else path)}
            for i, (label, target) in enumerate(trail)]})
        graph[2]['breadcrumb'] = {'@id': url + '#breadcrumbs'}
    schema = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    head = f'''  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="max-image-preview:large">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pl_PL">
  <meta property="og:site_name" content="Good Taste">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{BASE}{image}">
  <meta property="og:image:alt" content="{escape(image_alt)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(description)}">
  <meta name="twitter:image" content="{BASE}{image}">
  <meta name="twitter:image:alt" content="{escape(image_alt)}">
  <script type="application/ld+json">{schema}</script>'''
    html = fill(TEMPLATE, head=head, body=body, root=root)
    # Contact details must be readable before JavaScript runs, too.
    for field, href in [('email', 'mailto:' + DATA.get('email', '')), ('phone', 'tel:' + re.sub(r'[^+\d]', '', DATA.get('phone', '')))]:
        if DATA.get(field):
            pattern = r'<span([^>]*) data-' + field + r' aria-disabled="true">[^<]*</span>'
            html = re.sub(pattern, lambda m: f'<a{m[1]} href="{escape(href)}">{escape(DATA[field])}</a>', html)
    if DATA.get('facebook', '').startswith('https://'):
        html = re.sub(r'<span class="([^"]*)" data-facebook[^>]*>[^<]*</span>',
                      lambda m: f'<a class="{m[1]}" href="{escape(DATA["facebook"])}" target="_blank" rel="noopener noreferrer" aria-label="Facebook — otwiera się w nowej karcie">' + ('f' if 'facebook-button' in m[1] else 'Facebook') + '</a>', html)
    assert '{{' not in html, f'Unresolved template in {path}'
    OUTPUT[path + 'index.html'] = html
    PAGES.append((url, path))


def build():
    OUTPUT.clear()
    PAGES.clear()
    home = fill((ROOT / 'templates/home.html').read_text(), **{key: cards(key, './') for key in SERVICES})
    render('', 'Good Taste — wnętrza i gastronomia | Wrocław, Dolny Śląsk',
           'Good Taste: projektowanie wnętrz mieszkań i projekty technologiczne gastronomii. Wrocław i Dolny Śląsk. Zobacz portfolio i porozmawiaj o swoim projekcie.', home)
    for key, (path, label, template, title, description) in SERVICES.items():
        trail = [('Start', ''), (label, None)]
        body = fill((ROOT / 'templates' / template).read_text(), breadcrumbs=crumbs(trail, '../'), projects=cards(key, '../'), root='../')
        service = {'@type': 'Service', '@id': BASE + path + '#service', 'name': label, 'serviceType': label,
                   'url': BASE + path, 'provider': {'@id': BASE + '#organization'},
                   'areaServed': {'@type': 'AdministrativeArea', 'name': 'województwo dolnośląskie'}}
        render(path, title, description, body, extra=service, trail=trail)
        for i, project in enumerate(DATA['galleries'][key]['projects']):
            project_path = 'projekty/' + project['slug'] + '/'
            trail = [('Start', ''), (label, path), (project['title'], None)]
            photos = []
            for index, item in enumerate(project['images']):
                loading = 'fetchpriority="high"' if index == 0 else 'loading="lazy"'
                photos.append(f'''<figure><a href="../../{item['src']}" data-gallery-key="{key}" data-project-index="{i}" data-photo-index="{index}" aria-label="Powiększ: {escape(item['alt'])}"><img src="../../{item['src']}" alt="{escape(item['alt'])}" width="{item['width']}" height="{item['height']}" {loading} decoding="async"></a><figcaption>{escape(item['alt'].split(' — ')[0])}</figcaption></figure>''')
            body = f'''<section class="page-intro section-wrap">
              {crumbs(trail, '../../')}<span class="eyebrow">Portfolio · {escape(label)}</span>
              <h1>{escape(project['title'])}</h1><p class="lead">{escape(project['subtitle'])}</p>
              <p class="project-description">{escape(project['description'])}</p>
              <a class="text-link" href="#kontakt">Porozmawiajmy o Twoim projekcie <span aria-hidden="true">↗</span></a>
            </section>
            <section class="photo-gallery section-wrap" aria-label="Wizualizacje projektu">{''.join(photos)}</section>
            <section class="editorial section-wrap"><h2>Poznaj pozostałe projekty</h2>
              <p><a href="../../{path}">{escape(label)} — zobacz portfolio i dowiedz się więcej o współpracy.</a></p>
            </section>'''
            work = {'@type': 'CreativeWork', '@id': BASE + project_path + '#project', 'name': project['title'],
                    'description': project['description'], 'url': BASE + project_path, 'creator': {'@id': BASE + '#organization'},
                    'image': [BASE + item['src'] for item in project['images']], 'inLanguage': 'pl-PL'}
            render(project_path, project['title'] + ' — projekt wnętrza | Good Taste',
                   project['subtitle'] + '. ' + project['description'].split('. ')[0] + '. Zobacz wizualizacje projektu Good Taste.',
                   body, image=project['images'][0]['src'], extra=work, trail=trail, image_alt=project['images'][0]['alt'])
    # No invented modification dates, priorities or change frequencies.
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ins = 'http://www.google.com/schemas/sitemap-image/1.1'
    ET.register_namespace('', ns)
    ET.register_namespace('image', ins)
    sitemap = ET.Element(f'{{{ns}}}urlset')
    by_path = {'projekty/' + p['slug'] + '/': p for cat in DATA['galleries'].values() for p in cat['projects']}
    for url, path in PAGES:
        entry = ET.SubElement(sitemap, f'{{{ns}}}url')
        ET.SubElement(entry, f'{{{ns}}}loc').text = url
        for item in by_path.get(path, {}).get('images', []):
            image = ET.SubElement(entry, f'{{{ins}}}image')
            ET.SubElement(image, f'{{{ins}}}loc').text = BASE + item['src']
    ET.indent(sitemap)
    OUTPUT['sitemap.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(sitemap, encoding='unicode') + '\n'
    OUTPUT['robots.txt'] = 'User-agent: *\nAllow: /\n\nSitemap: ' + BASE + 'sitemap.xml\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if committed output differs from source content')
    args = parser.parse_args()
    build()
    stale = []
    for name, html in OUTPUT.items():
        target = ROOT / name
        if args.check:
            if not target.exists() or target.read_text() != html:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html)
    if stale:
        raise SystemExit('Run python3 scripts/build_site.py; stale output: ' + ', '.join(stale))
    print(f'{"Checked" if args.check else "Generated"} {len(PAGES)} pages, sitemap.xml and robots.txt.')
