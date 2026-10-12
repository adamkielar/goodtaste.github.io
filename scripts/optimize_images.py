"""Create web assets locally from the untouched ../Good taste source images.
Requires Pillow with WebP support. Run from any directory.
"""
from pathlib import Path
from io import BytesIO
import argparse
import hashlib
import json
import re
import unicodedata
from PIL import Image, ImageOps, ImageCms

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'Good taste'
CONTENT = ROOT / 'assets/content.js'
FOLDERS = {unicodedata.normalize('NFC', p.name): p for p in SOURCE.iterdir() if p.is_dir()}


def read_image(path):
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original)
        image.load()
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')
        profile = image.info.get('icc_profile')
        if profile:
            image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(BytesIO(profile)), ImageCms.createProfile('sRGB'), outputMode=image.mode)
        if image.mode == 'RGBA' and image.getchannel('A').getextrema() == (255, 255):
            image = image.convert('RGB')
        image.info.clear()
        return image


def export_webp(source, target, max_size, quality):
    image = read_image(source)
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, 'WEBP', quality=quality, method=6)
    with Image.open(target) as check:
        check.load()
        assert check.size == image.size
    return image.size


def remove_unchanged_copy(copy, source):
    # Remove only byte-identical imported duplicates, never source originals.
    if copy.exists() and copy.resolve() != source.resolve():
        assert copy.is_relative_to(ROOT / 'assets/images')
        if hashlib.sha256(copy.read_bytes()).digest() == hashlib.sha256(source.read_bytes()).digest():
            copy.unlink()


data = json.loads(CONTENT.read_text().split('window.siteContent = ', 1)[1].rstrip().removesuffix(';'))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project', action='append', help='Optimize only this project slug; may be repeated.')
args = parser.parse_args()
known_slugs = {p['slug'] for g in data['galleries'].values() for p in g['projects']}
if args.project and not set(args.project) <= known_slugs:
    parser.error('Unknown project slug')
summary = []
original_total = web_total = thumbs_total = 0
for gallery in data['galleries'].values():
    for project in gallery['projects']:
        if args.project and project['slug'] not in args.project:
            continue
        folder = FOLDERS[project['title']]
        if all(item.get('source') for item in project['images']):
            files = [folder / item['source'] for item in project['images']]
        else:
            files = sorted((p for p in folder.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg')),
                           key=lambda p: [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)', p.name)])
        assert len(files) == len(project['images']), f'Image count changed: {folder}'
        original_bytes = sum(p.stat().st_size for p in files)
        web_bytes = 0
        for index, (source, item) in enumerate(zip(files, project['images']), 1):
            old_path = ROOT / item['src']
            target = old_path.parent / f'{index:02d}.webp'
            width, height = export_webp(source, target, 2000, 84)
            item.update(src=str(target.relative_to(ROOT)), width=width, height=height)
            item.pop('fullSrc', None)
            web_bytes += target.stat().st_size
            if index == 1:
                cover = target.parent / 'cover.webp'
                export_webp(source, cover, 800, 82)
                project['cover'] = str(cover.relative_to(ROOT))
                cover_bytes = cover.stat().st_size
                thumbs_total += cover_bytes
            # The old originals use this exact numbered naming convention.
            imported_original = target.with_suffix(source.suffix.lower())
            remove_unchanged_copy(imported_original, source)
        original_total += original_bytes
        web_total += web_bytes
        summary.append((project['title'], len(files), original_bytes, web_bytes, cover_bytes))
        print(f"{project['title']}: {original_bytes/1e6:.2f} MB -> {web_bytes/1e6:.2f} MB + {cover_bytes/1000:.0f} KB cover", flush=True)

CONTENT.write_text('// Portfolio data. After editing, run python3 scripts/build_site.py.\nwindow.siteContent = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')
if args.project:
    print(f'Selected galleries: {original_total/1e6:.2f} MB -> {(web_total + thumbs_total)/1e6:.2f} MB')
    raise SystemExit(0)

showcase_source = SOURCE / 'goodtaste 2.png'
showcase_target = ROOT / 'assets/images/showcase.webp'
hero_width, hero_height = export_webp(showcase_source, showcase_target, 2400, 84)
remove_unchanged_copy(ROOT / 'assets/images/showcase.png', showcase_source)
logo = read_image(SOURCE / 'logo.png')
logo.thumbnail((600, 600), Image.Resampling.LANCZOS)
logo.save(ROOT / 'assets/images/logo.png', 'PNG', optimize=True)
icon = read_image(SOURCE / 'GT_znak.png')
icon.thumbnail((48, 48), Image.Resampling.LANCZOS)
icon.save(ROOT / 'assets/images/GT_znak.png', 'PNG', optimize=True)

CONTENT.write_text('// Each project owns its image list; cover is a lightweight thumbnail.\n// Sources are preserved outside the repository; regenerate with scripts/optimize_images.py.\nwindow.siteContent = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')
html_path = ROOT / 'index.html'
html = html_path.read_text().replace('assets/images/showcase.png', 'assets/images/showcase.webp')
html = re.sub(r'(class="brand-logo"[^>]*width=")\d+(" height=")\d+', rf'\g<1>{logo.width}\g<2>{logo.height}', html)
html = re.sub(r'(class="showcase-image"[^>]*width=")\d+(" height=")\d+', rf'\g<1>{hero_width}\g<2>{hero_height}', html)
html_path.write_text(html)
css_path = ROOT / 'assets/styles.css'
css_path.write_text(css_path.read_text().replace('images/showcase.png', 'images/showcase.webp'))

before = original_total + showcase_source.stat().st_size + (SOURCE/'logo.png').stat().st_size + (SOURCE/'GT_znak.png').stat().st_size
other = sum((ROOT / name).stat().st_size for name in ['assets/images/showcase.webp','assets/images/logo.png','assets/images/GT_znak.png'])
after = web_total + thumbs_total + other
image_count = sum(len(p['images']) for g in data['galleries'].values() for p in g['projects'])
lines = ['# Local image optimization', '', 'Original source files in `../Good taste` are unchanged. All exports were created locally with Pillow; no images were uploaded to an external service.', '',
         f'Total image assets: **{before/1e6:.2f} MB → {after/1e6:.2f} MB** ({(1-after/before)*100:.1f}% smaller), including all {image_count} gallery images, {len(summary)} covers, showcase, logo, and favicon.', '',
         '| Project | Photos | Original MB | WebP gallery MB | Cover KB |', '| --- | ---: | ---: | ---: | ---: |']
for title, count, original, web, cover in summary:
    lines.append(f'| {title} | {count} | {original/1e6:.2f} | {web/1e6:.2f} | {cover/1000:.0f} |')
lines += ['', f'- Gallery WebP: maximum 2000 px on the long edge, quality 84; smaller sources are not enlarged.',
          '- Cover WebP: maximum 800 px on the long edge, quality 82. Only these thumbnails appear in the project grid.',
          f'- Showcase: {hero_width} × {hero_height}, {showcase_target.stat().st_size/1000:.0f} KB, also reused in Contact.',
          f'- Logo: {logo.width} × {logo.height} transparent PNG, {(ROOT/"assets/images/logo.png").stat().st_size/1000:.1f} KB.',
          f'- Favicon: {icon.width} × {icon.height} PNG, {(ROOT/"assets/images/GT_znak.png").stat().st_size/1000:.1f} KB.',
          '- Lightbox images load on demand; the entire gallery is not downloaded on initial page load.',
          '- Aspect ratios and embedded watermarks are preserved. WebP uses lossy compression.', '',
          'Rebuild with `python3 scripts/optimize_images.py` using a Python environment with Pillow and WebP support.']
(ROOT / 'IMAGE_AUDIT.md').write_text('\n'.join(lines) + '\n')
print(f'TOTAL: {before/1e6:.2f} MB -> {after/1e6:.2f} MB ({(1-after/before)*100:.1f}% smaller)', flush=True)
