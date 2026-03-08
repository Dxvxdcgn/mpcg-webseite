"""
Extract ALL insight articles with their categories from original MPCG site.
Reads insight listing pages + category pages to build complete mapping.
"""
import os
import re
import json
from html import unescape

BASE = r"C:\Users\david\Documents\Dev\Webseiten\Entwicklung\mpcg\MPCG_original_Seite\mpcg.de"

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_articles_from_html(html):
    """Extract title, slug, and excerpt from insight teaser items."""
    articles = []
    pattern = re.compile(
        r'<div\s+class="mpcg-insights-teaser-item">\s*'
        r'<a\s+href="[^"]*?/([^/"]+)/index\.html"[^>]*>\s*'
        r'<img[^>]*>\s*</a>\s*'
        r'<div class="mpcg-insights-text">\s*'
        r'<h2 class="mpcg-insights-teaser-title"><a[^>]*>([^<]+)</a></h2>\s*'
        r'<div class="mpcg-insights-teaser-excerpt">\s*(.*?)\s*</div>',
        re.DOTALL
    )
    for m in pattern.finditer(html):
        slug = m.group(1)
        title = unescape(m.group(2).strip())
        excerpt = unescape(m.group(3).strip())
        excerpt = re.sub(r'\s+', ' ', excerpt).strip()
        articles.append({
            "title": title,
            "slug": slug,
            "excerpt": excerpt,
        })
    return articles

def extract_slugs_from_category_page(html):
    """Extract article slugs from a category listing page."""
    slugs = []
    pattern = re.compile(r'<h2 class="mpcg-insights-teaser-title"><a href="[^"]*?/([^/"]+)/index\.html"')
    for m in pattern.finditer(html):
        slugs.append(m.group(1))
    return slugs

# Category slug -> display name mapping
CATEGORIES = {
    "agile-organisation": "Agile Organisation",
    "bessere-strategien": "Bessere Strategien",
    "effizientere-prozesse": "Effizientere Prozesse",
    "gesteigerte-sales": "Mehr Sales",
    "umfassende-nachhaltigkeit": "Umfassende Nachhaltigkeit",
    "white-paper": "White Paper",
}

def main():
    # 1. Collect all articles from insights listing pages
    all_articles = {}  # slug -> article dict (preserves order from first seen)
    
    # Main insights page
    main_path = os.path.join(BASE, "insights", "index.html")
    if os.path.exists(main_path):
        html = read_file(main_path)
        for art in extract_articles_from_html(html):
            if art["slug"] not in all_articles:
                all_articles[art["slug"]] = art
    
    # Paginated pages 1-8 (and beyond, just in case)
    for page_num in range(1, 20):
        page_path = os.path.join(BASE, "insights", "page", str(page_num), "index.html")
        if os.path.exists(page_path):
            html = read_file(page_path)
            for art in extract_articles_from_html(html):
                if art["slug"] not in all_articles:
                    all_articles[art["slug"]] = art

    print(f"Total articles found from insights listing pages: {len(all_articles)}")
    
    # 2. Build category mapping from category pages (support multiple categories per article)
    slug_to_categories = {}  # slug -> list of categories
    
    for cat_slug, cat_name in CATEGORIES.items():
        cat_dir = os.path.join(BASE, "category", cat_slug)
        pages_to_check = [os.path.join(cat_dir, "index.html")]
        for page_num in range(1, 20):
            pages_to_check.append(os.path.join(cat_dir, "page", str(page_num), "index.html"))
        
        for page_path in pages_to_check:
            if os.path.exists(page_path):
                html = read_file(page_path)
                for slug in extract_slugs_from_category_page(html):
                    if slug not in slug_to_categories:
                        slug_to_categories[slug] = []
                    if cat_name not in slug_to_categories[slug]:
                        slug_to_categories[slug].append(cat_name)
                # Also extract full article data from category pages for articles not in insights listing
                for art in extract_articles_from_html(html):
                    if art["slug"] not in all_articles:
                        all_articles[art["slug"]] = art
                        print(f"  Found additional article from category page: {art['title']}")
                    if art["slug"] not in slug_to_categories:
                        slug_to_categories[art["slug"]] = []
                    if cat_name not in slug_to_categories[art["slug"]]:
                        slug_to_categories[art["slug"]].append(cat_name)
    
    print(f"Category mappings found: {len(slug_to_categories)}")
    
    # 3. For any article still missing a category, check individual article pages
    for slug in all_articles:
        if slug not in slug_to_categories or not slug_to_categories[slug]:
            art_page = os.path.join(BASE, slug, "index.html")
            if os.path.exists(art_page):
                html = read_file(art_page)
                cat_matches = re.findall(r'category/([^/"]+)/index\.html', html)
                for cat_key in cat_matches:
                    if cat_key in CATEGORIES:
                        if slug not in slug_to_categories:
                            slug_to_categories[slug] = []
                        if CATEGORIES[cat_key] not in slug_to_categories[slug]:
                            slug_to_categories[slug].append(CATEGORIES[cat_key])
                            print(f"  Found category for '{slug}' from article page: {CATEGORIES[cat_key]}")
    
    # 4. Merge category info into articles and build output
    result = []
    for i, (slug, art) in enumerate(all_articles.items(), 1):
        categories = slug_to_categories.get(slug, ["Unknown"])
        result.append({
            "number": i,
            "title": art["title"],
            "category": categories[0] if len(categories) == 1 else categories[0],
            "categories": categories,
            "excerpt": art["excerpt"],
            "slug": slug,
        })
    
    # 5. Print summary
    print(f"\n{'='*80}")
    print(f"TOTAL UNIQUE ARTICLES: {len(result)}")
    print(f"{'='*80}\n")
    
    cat_counts = {}
    multi_cat = 0
    for art in result:
        for c in art["categories"]:
            cat_counts[c] = cat_counts.get(c, 0) + 1
        if len(art["categories"]) > 1:
            multi_cat += 1
    
    print("Category breakdown (articles can appear in multiple categories):")
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count}")
    total_cat_assignments = sum(cat_counts.values())
    print(f"  Total category assignments: {total_cat_assignments}")
    print(f"  Articles with multiple categories: {multi_cat}")
    print()
    
    for art in result:
        cats = ", ".join(art["categories"])
        print(f"  {art['number']:3d}. [{cats:<45s}] {art['title']}")
    
    # 6. Save to JSON
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "all_insights_with_categories.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    main()
