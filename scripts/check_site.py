"""Validate the generated site without a browser or third-party dependencies."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from xml.etree import ElementTree as ET

from build_site import BASE, DATA, OUTPUT, PAGES, ROOT, build


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def select(self, tag, **attrs):
        return [a for t, a in self.elements if t == tag and all(a.get(k) == v for k, v in attrs.items())]


build()
pages = {}
titles, descriptions = set(), set()
for url, path in PAGES:
    target = ROOT / path / 'index.html'
    text = target.read_text()
    assert text == OUTPUT[path + 'index.html'], f'Stale generated page: {target}'
    page = pages[url] = Page(text)
    assert len(page.select('h1')) == 1, target
    assert page.select('html', lang='pl'), target
    canonical = page.select('link', rel='canonical')
    assert len(canonical) == 1 and canonical[0]['href'] == url, target
    assert page.select('meta', property='og:url')[0]['content'] == url, target
    title = text.split('<title>', 1)[1].split('</title>', 1)[0]
    description = page.select('meta', name='description')[0]['content']
    assert title not in titles and description not in descriptions, f'Duplicate metadata: {target}'
    titles.add(title)
    descriptions.add(description)
    assert 'noindex' not in page.select('meta', name='robots')[0]['content'], target
    ids = [attrs['id'] for _, attrs in page.elements if 'id' in attrs]
    assert len(ids) == len(set(ids)), f'Duplicate ID: {target}'
    for img in page.select('img'):
        assert img.get('alt') and int(img['width']) > 0 and int(img['height']) > 0, target
    schema = json.loads(text.split('<script type="application/ld+json">', 1)[1].split('</script>', 1)[0])
    assert schema['@context'] == 'https://schema.org'
    graph_ids = {entry['@id'] for entry in schema['@graph']}
    assert url + '#webpage' in graph_ids and BASE + '#organization' in graph_ids
    assert not any(entry['@type'] == 'LocalBusiness' for entry in schema['@graph']), 'No verified business address yet'
    for link in page.select('a'):
        assert link.get('href'), f'Uncrawlable link: {target}'

references = 0
inbound = {url: 0 for url in pages}
for url, page in pages.items():
    for tag, attrs in page.elements:
        value = attrs.get('src') if tag in ('img', 'script') else attrs.get('href') if tag in ('a', 'link') else None
        if not value:
            continue
        resolved = urljoin(url, value)
        if not resolved.startswith(BASE):
            continue
        parsed = urlparse(resolved)
        relative = unquote(parsed.path.removeprefix(urlparse(BASE).path))
        target = ROOT / relative
        if target.is_dir():
            target /= 'index.html'
        assert target.is_file(), f'Broken link from {url}: {value}'
        references += 1
        destination = resolved.split('#')[0]
        if tag == 'a' and destination in inbound and destination != url:
            inbound[destination] += 1
        if parsed.fragment and target.suffix == '.html':
            destination_page = Page(target.read_text())
            assert any(a.get('id') == parsed.fragment for _, a in destination_page.elements), f'Missing anchor: {resolved}'
assert all(count > 0 for count in inbound.values()), f'Orphan pages: {inbound}'
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'i': 'http://www.google.com/schemas/sitemap-image/1.1'}
sitemap = ET.parse(ROOT / 'sitemap.xml')
assert {entry.text for entry in sitemap.findall('s:url/s:loc', ns)} == set(pages)
image_urls = [entry.text for entry in sitemap.findall('s:url/i:image/i:loc', ns)]
expected = {BASE + item['src'] for category in DATA['galleries'].values() for project in category['projects'] for item in project['images']}
assert set(image_urls) == expected and len(image_urls) == len(expected)
assert (ROOT / 'robots.txt').read_text() == OUTPUT['robots.txt']
print(f'PASS: {len(pages)} static pages; {references} local references; {len(image_urls)} sitemap images; unique metadata; JSON-LD; anchors; no orphan pages.')
