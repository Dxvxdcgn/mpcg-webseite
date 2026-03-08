"""Extract all Erfolge (success cases) from the original MPCG site."""
from bs4 import BeautifulSoup
import os
import re
import json

BASE = r"MPCG_original_Seite\mpcg.de\erfolge"

# Pages to check: main index + page/2 through page/6
pages_to_check = [
    os.path.join(BASE, "index.html"),
    os.path.join(BASE, "page", "2", "index.html"),
    os.path.join(BASE, "page", "3", "index.html"),
    os.path.join(BASE, "page", "4", "index.html"),
    os.path.join(BASE, "page", "5", "index.html"),
    os.path.join(BASE, "page", "6", "index.html"),
]

all_cases = []
categories = []

for page_path in pages_to_check:
    if not os.path.exists(page_path):
        print(f"  MISSING: {page_path}")
        continue
    
    print(f"\n--- Reading: {page_path} ---")
    with open(page_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract categories (only from first page)
    if not categories:
        cat_list = soup.find("ul", class_="mpcg-category-list")
        if cat_list:
            for li in cat_list.find_all("li", class_="mpcg-category-item"):
                a = li.find("a")
                if a:
                    cat_title = a.get("title", "")
                    cat_text = a.get_text(strip=True)
                    cat_href = a.get("href", "")
                    # Extract slug from href
                    slug_match = re.search(r'erfolge-kategorien/([^/]+)/', cat_href)
                    cat_slug = slug_match.group(1) if slug_match else ""
                    categories.append({
                        "title": cat_title,
                        "text": cat_text,
                        "slug": cat_slug,
                        "href": cat_href,
                    })
    
    # Extract erfolge items
    items = soup.find_all("div", class_="mpcg-insights-erfolg-item")
    print(f"  Found {len(items)} items")
    
    for item in items:
        # Title and link
        title_tag = item.find("h3", class_="mpcg-erfolg-teaser-title")
        title = ""
        link = ""
        slug = ""
        if title_tag:
            a = title_tag.find("a")
            if a:
                title = a.get_text(strip=True)
                link = a.get("href", "")
                # Extract slug from link
                slug_match = re.search(r'(?:erfolge/)?([^/]+)/index\.html', link)
                if slug_match:
                    slug = slug_match.group(1)
                else:
                    slug = link.replace("/index.html", "").replace("index.html", "").strip("/")
        
        # Excerpt
        excerpt_div = item.find("div", class_="mpcg-erfolg-teaser-excerpt")
        excerpt = excerpt_div.get_text(strip=True) if excerpt_div else ""
        
        # Image
        img = item.find("img")
        img_alt = ""
        img_src_snippet = ""
        if img:
            img_alt = img.get("alt", "")
            # Check for real src (not base64)
            src = img.get("src", "")
            if src.startswith("data:"):
                # Try srcset or data-src
                srcset = img.get("srcset", "")
                data_src = img.get("data-src", "")
                if data_src:
                    img_src_snippet = data_src
                elif srcset:
                    img_src_snippet = srcset.split(",")[0].strip().split(" ")[0]
                else:
                    img_src_snippet = "(embedded base64)"
            else:
                img_src_snippet = src
        
        case = {
            "num": len(all_cases) + 1,
            "title": title,
            "slug": slug,
            "excerpt": excerpt[:200] + "..." if len(excerpt) > 200 else excerpt,
            "img_alt": img_alt,
            "img_src": img_src_snippet,
        }
        all_cases.append(case)

# Now read each individual erfolge page to get its category
print("\n\n--- Reading individual pages for categories ---")
erfolge_dir = os.path.join("MPCG_original_Seite", "mpcg.de", "erfolge")
for case in all_cases:
    slug = case["slug"]
    individual_path = os.path.join(erfolge_dir, slug, "index.html")
    if os.path.exists(individual_path):
        with open(individual_path, "r", encoding="utf-8") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        
        # Look for category in breadcrumb or category links
        # Try finding erfolge-kategorien links
        cat_links = soup.find_all("a", href=re.compile(r"erfolge-kategorien"))
        if cat_links:
            cats = []
            for cl in cat_links:
                cat_text = cl.get_text(strip=True)
                if cat_text:
                    cats.append(cat_text)
            case["category"] = ", ".join(cats) if cats else "Unknown"
        else:
            # Try schema.org or other metadata
            case["category"] = "Unknown"
        
        # Also try to get the real image URL from og:image or the header image
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            img_url = og_img["content"]
            # Extract just the filename
            img_filename = img_url.split("/")[-1]
            case["img_filename"] = img_filename
        else:
            case["img_filename"] = ""
    else:
        case["category"] = "Not found"
        case["img_filename"] = ""

# Print results
print("\n" + "=" * 80)
print("CATEGORIES / FILTER OPTIONS")
print("=" * 80)
for i, cat in enumerate(categories, 1):
    print(f"  {i:2d}. {cat['title']} ({cat['slug']})")
    print(f"      Count text: {cat['text']}")

print(f"\n{'=' * 80}")
print(f"ALL {len(all_cases)} SUCCESS CASES")
print("=" * 80)

for case in all_cases:
    print(f"\n#{case['num']:02d}: {case['title']}")
    print(f"    Slug: {case['slug']}")
    print(f"    Category: {case.get('category', 'N/A')}")
    print(f"    Image: {case.get('img_filename', 'N/A')}")
    print(f"    Excerpt: {case['excerpt'][:150]}...")

# Save as JSON for further use
output = {
    "categories": categories,
    "total_cases": len(all_cases),
    "cases": all_cases,
}
with open("erfolge_data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n\nData saved to erfolge_data.json")
print(f"Total success cases found: {len(all_cases)}")
