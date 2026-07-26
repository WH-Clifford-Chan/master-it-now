import re
from pathlib import Path
root = Path(r"c:\Users\cliff\Documents\_Personal Projects\Master It Now")
html_files = sorted(root.glob('app/templates/**/*.html'))
css_files = sorted(root.glob('app/static/styles/**/*.css'))
font_links = [
    '<link rel="preconnect" href="https://fonts.googleapis.com">',
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap" rel="stylesheet">'
]
updated_html = []
for path in html_files:
    text = path.read_text(encoding='utf-8')
    if 'fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap' in text:
        continue
    if '<head>' not in text:
        continue
    insert = '\n'.join(font_links) + '\n'
    if '<meta name="viewport" content="width=device-width, initial-scale=1">' in text:
        text = text.replace('<meta name="viewport" content="width=device-width, initial-scale=1">',
                            '<meta name="viewport" content="width=device-width, initial-scale=1">\n\n    ' + insert)
    elif '<title>' in text:
        text = text.replace('<title>', '    ' + insert + '<title>', 1)
    else:
        text = text.replace('<head>', '<head>\n    ' + insert, 1)
    path.write_text(text, encoding='utf-8')
    updated_html.append(str(path))
updated_css = []
for path in css_files:
    text = path.read_text(encoding='utf-8')
    if 'body {' not in text:
        continue
    body_start = text.find('body {')
    if body_start == -1:
        continue
    idx = body_start + len('body {')
    depth = 1
    while idx < len(text) and depth > 0:
        if text[idx] == '{':
            depth += 1
        elif text[idx] == '}':
            depth -= 1
        idx += 1
    body_block = text[body_start:idx]
    new_block, count = re.subn(r'font-family\s*:\s*[^;]+;', '    font-family: "Inter", system-ui, sans-serif;', body_block, count=1)
    if count == 0:
        new_block = body_block.replace('body {', 'body {\n    font-family: "Inter", system-ui, sans-serif;', 1)
    new_text = text[:body_start] + new_block + text[idx:]
    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
        updated_css.append(str(path))
print('UPDATED_HTML', len(updated_html))
for p in updated_html:
    print(p)
print('UPDATED_CSS', len(updated_css))
for p in updated_css:
    print(p)
