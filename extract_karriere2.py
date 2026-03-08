from bs4 import BeautifulSoup, NavigableString
import re, sys

with open(r'MPCG_original_Seite\mpcg.de\karriere\deine-karriere-bei-der-mpcg\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Remove script, style, noscript
for tag in soup(['script', 'style', 'noscript', 'link', 'meta']):
    tag.decompose()

body = soup.find('body')
if not body:
    print("NO BODY FOUND")
    sys.exit(1)

# Get content div
content = body.find('div', id='content')
if not content:
    content = body

# Collect all visible text sections
results = []

# Helper to get clean text
def clean(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Find hero section
hero = content.find(class_=re.compile(r'mpcg-hero'))
if hero:
    results.append("=== HERO SECTION ===")
    for tag in hero.find_all(['h1','h2','h3','p','span']):
        t = clean(tag.get_text())
        if t and len(t) > 1:
            results.append(f"[{tag.name}] {t}")
    # Get background images
    for tag in hero.find_all(True, style=True):
        style = tag.get('style', '')
        urls = re.findall(r'url\(["\']?(https?://[^"\')\s]+)["\']?\)', style)
        for url in urls:
            results.append(f"[bg-image] {url}")
    for img in hero.find_all('img'):
        src = img.get('src', img.get('data-src', ''))
        if src and not src.startswith('data:'):
            results.append(f"[img] {src} alt={img.get('alt','')}")

# Find all main text sections (h1-h6 and p tags in main content, not in nav/footer)
results.append("\n=== ALL HEADINGS AND PARAGRAPHS ===")
nav = content.find_all(class_=re.compile(r'nav|header|footer|menu'))
nav_ids = set(id(n) for n in nav)

def is_in_nav(el):
    for parent in el.parents:
        if id(parent) in nav_ids:
            return True
        cls = ' '.join(parent.get('class', []))
        if re.search(r'nav|header|footer|menu', cls, re.I):
            return True
    return False

for tag in content.find_all(['h1','h2','h3','h4','h5','h6','p']):
    if is_in_nav(tag):
        continue
    t = clean(tag.get_text())
    if t and len(t) > 2:
        results.append(f"\n[{tag.name}] {t}")

# Find images with actual URLs (not data URIs)
results.append("\n\n=== IMAGES ===")
for img in content.find_all('img'):
    src = img.get('src', img.get('data-src', ''))
    alt = img.get('alt', '')
    if src and not src.startswith('data:') and 'svg' not in src:
        results.append(f"  {src}  |  alt: {alt}")

# Background images
results.append("\n=== BACKGROUND IMAGES ===")
for tag in content.find_all(True, style=True):
    style = tag.get('style', '')
    urls = re.findall(r'url\(["\']?(https?://[^"\')\s]+)["\']?\)', style)
    for url in urls:
        if 'svg' not in url:
            results.append(f"  {url}")

# Elementor toggles (FAQ)
results.append("\n\n=== ELEMENTOR TOGGLES (FAQ) ===")
for item in content.find_all(class_='elementor-toggle-item'):
    title = item.find(class_='elementor-toggle-title')
    body_div = item.find(class_='elementor-tab-content')
    if title:
        results.append(f"\nQ: {clean(title.get_text())}")
    if body_div:
        results.append(f"A: {clean(body_div.get_text())}")

# Testimonials
results.append("\n\n=== TESTIMONIALS ===")
for slide in content.find_all(class_='swiper-slide'):
    text_el = slide.find(class_=re.compile(r'elementor-testimonial__text'))
    name_el = slide.find(class_=re.compile(r'elementor-testimonial__name'))
    title_el = slide.find(class_=re.compile(r'elementor-testimonial__title'))
    img_el = slide.find('img')
    if text_el or name_el:
        if text_el:
            results.append(f'\nQUOTE: "{clean(text_el.get_text())}"')
        if name_el:
            results.append(f"NAME: {clean(name_el.get_text())}")
        if title_el:
            results.append(f"TITLE: {clean(title_el.get_text())}")
        if img_el:
            src = img_el.get('src', img_el.get('data-src', ''))
            if src and not src.startswith('data:'):
                results.append(f"IMG: {src}")

# Email links
results.append("\n\n=== EMAIL LINKS ===")
for a in content.find_all('a', href=re.compile(r'mailto:')):
    results.append(f"  {a.get('href')}")

output = '\n'.join(results)
print(output[:200000])  # Limit output
