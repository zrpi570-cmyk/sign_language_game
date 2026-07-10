c = open("templates/learn-dashboard.html", "r", encoding="utf-8").read()

# Find hero-card section and replace CSS
# 1. Change hero-card CSS - remove margin-bottom, add flex properties
c = c.replace(
    ".hero-card{\n  background:var(--card);border:1px solid var(--card-edge);border-radius:var(--radius);\n  padding:24px 28px;margin-bottom:28px;\n  display:flex;align-items:center;gap:24px;flex-wrap:wrap;\n  box-shadow:0 1px 3px rgba(0,0,0,0.03);\n}",
    ".hero-card{\n  flex:2;\n  background:var(--card);border:1px solid var(--card-edge);border-radius:var(--radius);\n  padding:24px 28px;\n  display:flex;align-items:center;gap:24px;flex-wrap:wrap;\n  box-shadow:0 1px 3px rgba(0,0,0,0.03);\n}"
)

# 2. Change stats-row CSS - make it a flex child
c = c.replace(
    ".stats-row{display:flex;gap:12px;margin-bottom:28px;flex-wrap:wrap}",
    ".stats-row{flex:3;display:flex;gap:12px;flex-wrap:wrap}"
)

# 3. Wrap hero-card + stats-row in a single flex row 
# Find the start of hero-card div and end of stats-row div
hero_start = c.find('<div class="hero-card">')
# Find end of hero-card (match closing div)
pos = hero_start + len('<div class="hero-card">')
depth = 1
while depth > 0:
    if c[pos:pos+5] == '<div ' or c[pos:pos+5] == '<div>':
        depth += 1
    if c[pos:pos+6] == '</div>':
        depth -= 1
    pos += 1
hero_end = pos

stats_start = c.find('<div class="stats-row">')
# Find end of stats-row
pos2 = stats_start + len('<div class="stats-row">')
depth2 = 1
while depth2 > 0:
    if c[pos2:pos2+5] == '<div ' or c[pos2:pos2+5] == '<div>':
        depth2 += 1
    if c[pos2:pos2+6] == '</div>':
        depth2 -= 1
    pos2 += 1
stats_end = pos2

# Wrap in a single row div
row_html = '<div class="top-row">\n' + c[hero_start:stats_end] + '\n</div>'
c = c[:hero_start] + row_html + c[stats_end:]

# 4. Add CSS for the new top-row
css_insert = '.top-row{display:flex;gap:14px;margin-bottom:28px;flex-wrap:wrap}\n'
pos3 = c.find('.hero-card{')
c = c[:pos3] + css_insert + c[pos3:]

# 5. Fix responsive
c = c.replace(
    ".hero-card{flex-direction:column;text-align:center}\n  .hero-card .welcome{flex-direction:column}\n  .stats-row{flex-direction:column}",
    ".top-row{flex-direction:column}\n  .hero-card{flex-direction:column;text-align:center}\n  .hero-card .welcome{flex-direction:column}\n  .stats-row{flex-direction:column}"
)

open("templates/learn-dashboard.html", "w", encoding="utf-8").write(c)
print("Layout fixed: hero (2/5) + stats (3/5)")
