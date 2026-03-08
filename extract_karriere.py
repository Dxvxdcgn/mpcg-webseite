from bs4 import BeautifulSoup
import re

with open(r'MPCG_original_Seite\mpcg.de\karriere\deine-karriere-bei-der-mpcg\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Remove script and style elements
for tag in soup(['script', 'style', 'noscript']):
    tag.decompose()

# Find the content div
content = soup.find('div', id='content')
if not content:
    content = soup.find('body')

# Extract all relevant sections
print("=" * 80)
print("FULL TEXT EXTRACTION FROM KARRIERE PAGE")
print("=" * 80)

# Get all image sources
print("\n\n### ALL IMAGE PATHS ###")
for img in soup.find_all('img'):
    src = img.get('src', img.get('data-src', ''))
    alt = img.get('alt', '')
    if src and 'data:' not in src[:20]:
        print(f"  SRC: {src}")
        if alt:
            print(f"  ALT: {alt}")
        print()

# Get background images from style attributes
print("\n### BACKGROUND IMAGES ###")
for tag in soup.find_all(style=True):
    style = tag.get('style', '')
    urls = re.findall(r'url\(["\']?(https?://[^"\')\s]+)["\']?\)', style)
    for url in urls:
        print(f"  {url}")

# Now extract all visible text in order
print("\n\n### FULL VISIBLE TEXT CONTENT (in page order) ###\n")

if content:
    # Get all text blocks
    for element in content.descendants:
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            text = element.get_text(strip=True)
            if text:
                level = element.name
                print(f"\n{'#' * int(level[1])} {text}")
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text and len(text) > 1:
                print(f"\n{text}")
        elif element.name == 'li':
            text = element.get_text(strip=True)
            if text:
                print(f"  • {text}")
        elif element.name == 'a' and element.get('href'):
            href = element.get('href', '')
            if 'mailto:' in href:
                print(f"  [EMAIL: {href}]")
        elif element.name == 'blockquote' or (element.name == 'div' and 'testimonial' in str(element.get('class', ''))):
            text = element.get_text(strip=True)
            if text and len(text) > 10:
                print(f'\n  QUOTE: "{text}"')
        elif element.name == 'cite':
            text = element.get_text(strip=True)
            if text:
                print(f"  CITE: {text}")

# Also try to find FAQ sections specifically 
print("\n\n### LOOKING FOR FAQ/TOGGLE SECTIONS ###")
toggles = soup.find_all(class_=re.compile(r'toggle|accordion|faq', re.I))
for t in toggles:
    title_el = t.find(class_=re.compile(r'title|heading|question', re.I))
    content_el = t.find(class_=re.compile(r'content|body|answer', re.I))
    if title_el:
        print(f"\nQ: {title_el.get_text(strip=True)}")
    if content_el:
        print(f"A: {content_el.get_text(strip=True)}")

# Elementor toggles
print("\n\n### ELEMENTOR TOGGLES ###")
toggles = soup.find_all(class_=re.compile(r'elementor-toggle'))
for t in toggles:
    items = t.find_all(class_=re.compile(r'elementor-toggle-item'))
    for item in items:
        title = item.find(class_=re.compile(r'elementor-toggle-title'))
        content_div = item.find(class_=re.compile(r'elementor-toggle-content'))
        if title:
            print(f"\nQ: {title.get_text(strip=True)}")
        if content_div:
            print(f"A: {content_div.get_text(strip=True)}")

# Testimonials specifically
print("\n\n### TESTIMONIALS ###")
testimonials = soup.find_all(class_=re.compile(r'testimonial|swiper-slide', re.I))
for t in testimonials:
    text_el = t.find(class_=re.compile(r'text|quote|content', re.I))
    name_el = t.find(class_=re.compile(r'name', re.I))
    title_el = t.find(class_=re.compile(r'job|title|position', re.I))
    img_el = t.find('img')
    if text_el:
        print(f'\nQUOTE: "{text_el.get_text(strip=True)}"')
    if name_el:
        print(f"NAME: {name_el.get_text(strip=True)}")
    if title_el:
        txt = title_el.get_text(strip=True)
        if txt and 'toggle' not in txt.lower():
            print(f"TITLE: {txt}")
    if img_el:
        src = img_el.get('src', img_el.get('data-src', ''))
        if src:
            print(f"IMG: {src}")
