from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self.skip_tags = {'style', 'script', 'link', 'meta', 'noscript'}
        self.current_skip = 0
        
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in self.skip_tags:
            self.current_skip += 1
        if tag == 'img':
            src = d.get('src', '')
            alt = d.get('alt', '')
            if src and not src.startswith('data:'):
                self.texts.append(f'[IMG: src={src} alt="{alt}"]')
        if tag == 'source':
            src = d.get('src', '')
            typ = d.get('type', '')
            if src and not src.startswith('data:'):
                self.texts.append(f'[SOURCE: src={src} type={typ}]')
        if tag == 'video':
            self.texts.append('[VIDEO]')
        if tag == 'a':
            href = d.get('href', '')
            if 'mailto:' in href:
                self.texts.append(f'[MAILTO: {href}]')
                
    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.current_skip -= 1
            
    def handle_data(self, data):
        if self.current_skip == 0:
            text = data.strip()
            if text and len(text) < 5000:
                self.texts.append(text)

with open(r'MPCG_original_Seite\mpcg.de\karriere\deine-karriere-bei-der-mpcg\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract just the body
body_start = html.find('<body')
body_end = html.find('</body>')
body = html[body_start:body_end+7] if body_start > 0 else html

parser = TextExtractor()
parser.feed(body)

output = '\n'.join(parser.texts)
with open('karriere_text_extract.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print(f'Extracted {len(parser.texts)} text segments, total length: {len(output)} chars')
