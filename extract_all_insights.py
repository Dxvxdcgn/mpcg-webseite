"""Extract ALL insight articles from the original MPCG insights listing pages."""
import re
import os
import json


def extract_from_file(filepath):
    """Extract articles from a single HTML file using regex."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    articles = []
    # Match each teaser item block
    pattern = re.compile(
        r'<div\s+class="mpcg-insights-teaser-item">\s*'
        r'<a\s+href="([^"]+)"\s+class="mpcg-insights-teaser-image-link">.*?'
        r'<h2\s+class="mpcg-insights-teaser-title"><a\s+href="[^"]+">([^<]+)</a></h2>\s*'
        r'<div\s+class="mpcg-insights-teaser-excerpt">\s*(.*?)\s*</div>',
        re.DOTALL
    )
    
    for m in pattern.finditer(content):
        link = m.group(1).strip()
        title = m.group(2).strip()
        excerpt = m.group(3).strip()
        # Clean excerpt: remove HTML tags and collapse whitespace
        excerpt = re.sub(r'<[^>]+>', '', excerpt)
        excerpt = re.sub(r'\s+', ' ', excerpt).strip()
        articles.append({
            'title': title,
            'excerpt': excerpt,
            'link': link,
        })
    
    return articles


def clean_link(link):
    """Clean up relative links to get the slug."""
    if not link:
        return ''
    # Remove relative path prefixes
    link = link.replace('../../', '').replace('../', '').replace('./', '')
    # Remove index.html
    link = link.replace('index.html', '')
    # Remove trailing slash for consistency, then add back
    link = link.strip('/')
    return link


def main():
    base = r'c:\Users\david\Documents\Dev\Webseiten\Entwicklung\mpcg\MPCG_original_Seite\mpcg.de'
    
    files = [
        os.path.join(base, 'insights', 'index.html'),
        os.path.join(base, 'insights', 'page', '2', 'index.html'),
        os.path.join(base, 'insights', 'page', '3', 'index.html'),
        os.path.join(base, 'insights', 'page', '4', 'index.html'),
        os.path.join(base, 'insights', 'page', '5', 'index.html'),
        os.path.join(base, 'insights', 'page', '6', 'index.html'),
        os.path.join(base, 'insights', 'page', '7', 'index.html'),
        os.path.join(base, 'insights', 'page', '8', 'index.html'),
    ]
    
    all_articles = []
    for i, filepath in enumerate(files, 1):
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
        articles = extract_from_file(filepath)
        print(f"Page {i}: Found {len(articles)} articles")
        all_articles.extend(articles)
    
    print(f"\n{'='*80}")
    print(f"TOTAL ARTICLES FOUND: {len(all_articles)}")
    print(f"{'='*80}\n")
    
    for i, article in enumerate(all_articles, 1):
        slug = clean_link(article.get('link', ''))
        print(f"{i}. **{article['title']}**")
        if article.get('excerpt'):
            excerpt = article['excerpt'][:250]
            if len(article['excerpt']) > 250:
                excerpt += '...'
            print(f"   Excerpt: {excerpt}")
        print(f"   Slug: {slug}")
        print()
    
    # Also save as JSON
    output = []
    for i, article in enumerate(all_articles, 1):
        output.append({
            'number': i,
            'title': article['title'],
            'excerpt': article.get('excerpt', ''),
            'slug': clean_link(article.get('link', ''))
        })
    
    with open('all_insights_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to all_insights_extracted.json")


if __name__ == '__main__':
    main()
