from bs4 import BeautifulSoup
import re

with open(r"MPCG_original_Seite\mpcg.de\karriere\deine-karriere-bei-der-mpcg\index.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
body = soup.find("body")

print("=== IMG TAGS ===")
imgs = body.find_all("img")
print(f"Total: {len(imgs)}")
for i, img in enumerate(imgs):
    src = img.get("src", "")
    dsrc = img.get("data-src", "")
    alt = img.get("alt", "")
    is_data = src.startswith("data:") if src else False
    is_svg = ".svg" in (src or dsrc or "")
    print(f"  [{i}] data_uri={is_data} svg={is_svg} alt='{alt}' src_start='{(src or dsrc or '')[:100]}'")

print("\n=== BG IMAGES ===")
seen = set()
for el in body.find_all(style=True):
    for m in re.findall(r"url\(['\"]?(https?://[^'\"\)\s]+)", el.get("style", "")):
        if m not in seen:
            seen.add(m)
            print(f"  {m}")
