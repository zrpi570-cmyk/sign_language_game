import os
for fn in os.listdir('templates'):
    if not fn.endswith('.html'): continue
    content = open('templates/'+fn, 'r', encoding='utf-8').read()
    if link in content:
        content = content.replace(link+'\\n', '')
        open('templates/'+fn, 'w', encoding='utf-8').write(content)
        print(fn+' cleaned')
