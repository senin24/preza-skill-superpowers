#!/usr/bin/env python3
"""
Генератор презентации из markdown-файла.
Использование: python3 build_presentation.py slides_skills.md
Результат:     slides_skills.html
"""

import sys
import re
import os

# ── Стили ────────────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Segoe UI', Arial, sans-serif;
  background: #0f0f1a; color: #e8e8f0;
  height: 100vh; display: flex; flex-direction: column;
  align-items: center; justify-content: center; overflow: hidden;
}
.deck { width: 900px; position: relative; }
.slide {
  display: none; background: #1a1a2e;
  border: 1px solid #2a2a4a; border-radius: 16px;
  padding: 56px 64px; min-height: 500px; position: relative;
  animation: fadeIn 0.3s ease;
}
.slide.active { display: flex; flex-direction: column; justify-content: center; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.slide-num { position: absolute; top: 20px; right: 28px; font-size: 12px; color: #444466; letter-spacing: 1px; }
.tag { font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: #6c63ff; margin-bottom: 16px; }
h1 { font-size: 34px; font-weight: 700; line-height: 1.2; color: #fff; margin-bottom: 16px; }
h2 { font-size: 28px; font-weight: 700; color: #fff; margin-bottom: 28px; }
.subtitle { font-size: 18px; color: #8888aa; line-height: 1.5; }
ul { list-style: none; display: flex; flex-direction: column; gap: 14px; }
ul li { display: flex; align-items: flex-start; gap: 14px; font-size: 17px; line-height: 1.5; color: #c8c8e0; }
ul li::before { content: '▸'; color: #6c63ff; flex-shrink: 0; margin-top: 2px; }
ul.warn  li::before  { content: '✕'; color: #e05c5c; }
ul.check li::before  { content: '✓'; color: #4caf82; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.col-box { background: #12122a; border: 1px solid #2a2a4a; border-radius: 10px; padding: 22px 24px; }
.col-box h3 { font-size: 12px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 14px; }
.col-box h3.bad  { color: #e05c5c; }
.col-box h3.good { color: #4caf82; }
.highlight-box {
  background: #12122a; border-left: 3px solid #6c63ff;
  border-radius: 0 8px 8px 0; padding: 20px 24px;
  font-size: 16px; color: #c8c8e0; line-height: 1.6; margin-bottom: 24px;
}
.step { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 14px; }
.step-num {
  background: #6c63ff; color: #fff; font-weight: 700; font-size: 13px;
  width: 26px; height: 26px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 3px;
}
.step-text { font-size: 16px; color: #c8c8e0; line-height: 1.5; }
.prompt-box {
  background: #0f0f1a; border: 1px solid #3a3a5a; border-radius: 8px;
  padding: 16px 20px; font-family: 'Consolas', monospace;
  font-size: 14px; color: #a78bfa; line-height: 1.6; margin: 16px 0;
}
code { background: #0f0f1a; color: #a78bfa; padding: 2px 7px; border-radius: 4px; font-family: 'Consolas', monospace; font-size: 13px; }
.big-stat { font-size: 72px; font-weight: 800; color: #6c63ff; line-height: 1; }
.stats-row { display: flex; gap: 56px; margin-bottom: 28px; }
.stat-label { font-size: 15px; color: #8888aa; margin-top: 4px; }
.quote { font-size: 18px; font-style: italic; color: #aaaacc; border-left: 3px solid #6c63ff; padding-left: 24px; line-height: 1.6; margin-top: 24px; }
.plan-list { display: flex; flex-direction: column; gap: 10px; }
.plan-row { display: flex; align-items: baseline; gap: 14px; font-size: 15px; color: #c8c8e0; line-height: 1.4; }
.plan-num { background: #12122a; border: 1px solid #2a2a4a; color: #6c63ff; font-weight: 700; font-size: 12px; min-width: 28px; height: 22px; border-radius: 4px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.nav { display: flex; align-items: center; gap: 20px; margin-top: 24px; justify-content: center; }
button { background: #1a1a2e; border: 1px solid #2a2a4a; color: #c8c8e0; padding: 10px 28px; border-radius: 8px; font-size: 15px; cursor: pointer; transition: all 0.2s; }
button:hover { background: #2a2a4a; border-color: #6c63ff; color: #fff; }
button:disabled { opacity: 0.3; cursor: default; }
.progress { display: flex; gap: 6px; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: #2a2a4a; transition: background 0.3s; }
.dot.active { background: #6c63ff; }
"""

JS = """
const slides = document.querySelectorAll('.slide');
const dotsEl = document.getElementById('dots');
let cur = 0;
slides.forEach((_, i) => {
  const d = document.createElement('div');
  d.className = 'dot' + (i === 0 ? ' active' : '');
  dotsEl.appendChild(d);
});
function go(dir) {
  slides[cur].classList.remove('active');
  dotsEl.children[cur].classList.remove('active');
  cur += dir;
  slides[cur].classList.add('active');
  dotsEl.children[cur].classList.add('active');
  document.getElementById('prev').disabled = cur === 0;
  document.getElementById('next').disabled = cur === slides.length - 1;
}
document.addEventListener('keydown', e => {
  if ((e.key === 'ArrowRight' || e.key === 'ArrowDown') && cur < slides.length - 1) go(1);
  if ((e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   && cur > 0) go(-1);
});
"""

# ── Парсер ───────────────────────────────────────────────────────────────────

def inline(text):
    """Обрабатывает инлайн-разметку: **bold**, `code`."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#fff">\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

def parse_bullets(lines, css_class=""):
    items = [l[2:].strip() for l in lines if l.startswith('- ')]
    if not items:
        return ""
    cls = f' class="{css_class}"' if css_class else ''
    lis = ''.join(f'<li>{inline(i)}</li>' for i in items)
    return f'<ul{cls}>{lis}</ul>'

def parse_md(path):
    with open(path, encoding='utf-8') as f:
        raw = f.read()

    # Заголовок презентации
    meta = {}
    for key in ('title', 'subtitle', 'tag'):
        m = re.search(rf'^{key}:\s*(.+)$', raw, re.MULTILINE)
        if m:
            meta[key] = m.group(1).strip()

    # Слайды
    blocks = re.split(r'^== SLIDE ==$', raw, flags=re.MULTILINE)
    slides = []
    for block in blocks[1:]:
        slide = {}
        lines = block.strip().splitlines()

        for key in ('title', 'tag', 'layout', 'highlight', 'prompt', 'quote'):
            m = re.search(rf'^{key}:\s*(.+)$', block, re.MULTILINE)
            if m:
                slide[key] = m.group(1).strip()

        # stats: stat: VALUE | label
        slide['stats'] = re.findall(r'^stat:\s*(.+?)\s*\|\s*(.+)$', block, re.MULTILINE)

        # bullets (строки начинающиеся с '- ')
        slide['bullets'] = [l[2:].strip() for l in lines if l.startswith('- ')]

        # steps (нумерованные строки)
        slide['steps'] = re.findall(r'^\d+\.\s+(.+)$', block, re.MULTILINE)

        # two-col секции [LEFT/RIGHT: label | style]
        slide['cols'] = []
        for side in ('LEFT', 'RIGHT'):
            m = re.search(
                rf'^\[{side}:\s*(.+?)\s*\|\s*(\w+)\](.*?)(?=^\[|\Z)',
                block, re.MULTILINE | re.DOTALL
            )
            if m:
                label, style, body = m.group(1), m.group(2), m.group(3)
                items = [l[2:].strip() for l in body.splitlines() if l.startswith('- ')]
                slide['cols'].append({'label': label, 'style': style, 'items': items})

        slides.append(slide)

    return meta, slides

# ── Рендер слайдов ────────────────────────────────────────────────────────────

def render_title(meta, num, total):
    tag   = f'<div class="tag">{meta.get("tag","")}</div>'
    title = inline(meta.get('title', ''))
    sub   = inline(meta.get('subtitle', ''))
    return f"""
<div class="slide active">
  <span class="slide-num">1 / {total}</span>
  {tag}
  <h1>{title}</h1>
  <p class="subtitle">{sub}</p>
</div>"""

def render_slide(slide, num, total):
    active = ' active' if num == 1 else ''
    tag    = f'<div class="tag">{slide.get("tag","")}</div>'
    title  = f'<h2>{inline(slide.get("title",""))}</h2>'
    layout = slide.get('layout', 'bullets')
    body   = ''

    if layout == 'two-col':
        cols_html = ''
        for col in slide['cols']:
            style_cls = 'bad' if col['style'] == 'bad' else 'good'
            lis = ''.join(f'<li>{inline(i)}</li>' for i in col['items'])
            ul_cls = 'warn' if style_cls == 'bad' else 'check'
            cols_html += f"""
        <div class="col-box">
          <h3 class="{style_cls}">{col['label']}</h3>
          <ul class="{ul_cls}">{lis}</ul>
        </div>"""
        body = f'<div class="two-col">{cols_html}</div>'

    elif layout == 'steps':
        hi = slide.get('highlight', '')
        hi_html = f'<div class="highlight-box">{inline(hi)}</div>' if hi else ''
        steps_html = ''.join(
            f'<div class="step"><div class="step-num">{i+1}</div>'
            f'<div class="step-text">{inline(s)}</div></div>'
            for i, s in enumerate(slide['steps'])
        )
        body = hi_html + steps_html

    elif layout == 'case':
        prompt = slide.get('prompt', '').replace('\\n', '<br>')
        prompt_html = (
            f'<p style="font-size:15px;color:#8888aa;margin-bottom:8px;">Входящий запрос:</p>'
            f'<div class="prompt-box">{inline(prompt)}</div>'
        ) if prompt else ''
        body = prompt_html + parse_bullets(
            ['- ' + b for b in slide['bullets']]
        )

    elif layout == 'plan':
        items_html = ''.join(
            f'<div class="plan-row">'
            f'<div class="plan-num">{i+1}</div>'
            f'<div class="plan-text">{inline(b)}</div>'
            f'</div>'
            for i, b in enumerate(slide['bullets'])
        )
        body = f'<div class="plan-list">{items_html}</div>'

    elif layout == 'stats':
        stats_html = ''.join(
            f'<div><div class="big-stat">{v}</div><div class="stat-label">{l}</div></div>'
            for v, l in slide['stats']
        )
        stats_block = f'<div class="stats-row">{stats_html}</div>' if stats_html else ''
        bullets_html = parse_bullets(['- ' + b for b in slide['bullets']], 'check')
        quote = slide.get('quote', '')
        quote_html = f'<p class="quote">{inline(quote)}</p>' if quote else ''
        body = stats_block + bullets_html + quote_html

    else:  # bullets
        body = parse_bullets(['- ' + b for b in slide['bullets']])

    return f"""
<div class="slide{active}">
  <span class="slide-num">{num} / {total}</span>
  {tag}{title}{body}
</div>"""

# ── Сборка HTML ───────────────────────────────────────────────────────────────

def build(md_path):
    meta, slides = parse_md(md_path)
    total = len(slides) + 1  # +1 титульный

    slides_html = render_title(meta, 1, total)
    for i, slide in enumerate(slides):
        slides_html += render_slide(slide, i + 2, total)

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta.get('title', 'Presentation')}</title>
<style>{CSS}</style>
</head>
<body>
<div class="deck">
{slides_html}
</div>
<div class="nav">
  <button id="prev" onclick="go(-1)" disabled>← Назад</button>
  <div class="progress" id="dots"></div>
  <button id="next" onclick="go(1)">Вперёд →</button>
</div>
<script>{JS}</script>
</body>
</html>"""

    out_path = os.path.splitext(md_path)[0] + '.html'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✓ Сохранено: {out_path}  ({total} слайдов)')

# ── Точка входа ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    md = sys.argv[1] if len(sys.argv) > 1 else 'slides_skills.md'
    build(md)
