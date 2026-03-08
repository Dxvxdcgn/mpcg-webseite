from bs4 import BeautifulSoup
import re, os

path = r"MPCG_original_Seite\mpcg.de\karriere\deine-karriere-bei-der-mpcg\index.html"

# Read with explicit UTF-8
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

lines = []

def add(title):
    lines.append(f"\n=== {title} ===\n")

# 1) HERO SECTION
add("HERO SECTION")
hero = soup.find(class_="mpcg-hero")
if hero:
    for tag in hero.find_all(["h1","h2","h3","p","a","span"]):
        txt = tag.get_text(strip=True)
        if txt:
            lines.append(f"[{tag.name}] {txt}")
    # background images
    for el in hero.find_all(style=True):
        m = re.search(r'url\(["\']?(https?://[^"\')\s]+)', el.get("style",""))
        if m:
            lines.append(f"[bg-image] {m.group(1)}")

# 2) ALL SECTION HEADINGS AND TEXT (body, outside nav/header/footer)
add("ALL BODY TEXT (headings + paragraphs)")
body = soup.find("body")
if body:
    # Remove nav, header, footer to focus on main content
    for unwanted in body.find_all(["nav", "header", "footer"]):
        unwanted.decompose()
    
    for tag in body.find_all(["h1","h2","h3","h4","h5","h6","p","li"]):
        # skip if inside a toggle (FAQ) or testimonial - we handle those separately
        parent_classes = " ".join(tag.get("class", []))
        # Get all parent classes
        skip = False
        for p in tag.parents:
            pc = " ".join(p.get("class", []))
            if "elementor-toggle-item" in pc or "elementor-testimonial" in pc:
                skip = True
                break
        if skip:
            continue
        txt = tag.get_text(strip=True)
        if txt and len(txt) > 1:
            lines.append(f"[{tag.name}] {txt}")

# Re-parse for toggles and testimonials since we decomposed elements
soup2 = BeautifulSoup(html, "html.parser")

# 3) IMAGES
add("IMAGES")
for img in soup2.find("body").find_all("img"):
    src = img.get("src","") or img.get("data-src","")
    if src and not src.startswith("data:") and "svg" not in src.lower():
        alt = img.get("alt","")
        lines.append(f"[img] {src}")
        if alt:
            lines.append(f"      alt: {alt}")

# 4) BACKGROUND IMAGES (all)
add("BACKGROUND IMAGES")
seen_bg = set()
for el in soup2.find("body").find_all(style=True):
    m = re.search(r'url\(["\']?(https?://[^"\')\s]+)', el.get("style",""))
    if m and m.group(1) not in seen_bg:
        seen_bg.add(m.group(1))
        lines.append(f"[bg] {m.group(1)}")

# 5) ELEMENTOR TOGGLES (Entry Levels + FAQ)
add("ELEMENTOR TOGGLES (Einstiegslevel + FAQ)")
for toggle in soup2.find_all(class_="elementor-toggle-item"):
    title_el = toggle.find(class_="elementor-toggle-title")
    content_el = toggle.find(class_="elementor-tab-content")
    q = title_el.get_text(strip=True) if title_el else ""
    a = content_el.get_text(strip=True) if content_el else ""
    if q:
        lines.append(f"\nQ: {q}")
        lines.append(f"A: {a}")

# 6) TESTIMONIALS
add("TESTIMONIALS")
for slide in soup2.find_all(class_="swiper-slide"):
    txt_el = slide.find(class_="elementor-testimonial__text")
    name_el = slide.find(class_="elementor-testimonial__name")
    title_el = slide.find(class_="elementor-testimonial__title")
    if txt_el:
        lines.append(f"\nQUOTE: {txt_el.get_text(strip=True)}")
        if name_el: lines.append(f"NAME: {name_el.get_text(strip=True)}")
        if title_el: lines.append(f"TITLE: {title_el.get_text(strip=True)}")

# 7) EMAIL LINKS
add("EMAIL LINKS")
for a in soup2.find_all("a", href=True):
    if "mailto:" in a["href"]:
        lines.append(f"[email] {a['href']}")

output = "\n".join(lines)

# Write to file with explicit UTF-8 BOM so read_file can handle it
outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "karriere_out2.txt")
with open(outpath, "w", encoding="utf-8") as f:
    f.write(output)

print(f"Written to {outpath} ({len(output)} chars)")
