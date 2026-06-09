import re
import sys

css_file = 'static/style.css'
try:
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace :root
    content = re.sub(r':root\s*\{.*?\b--sidebar-width:\s*320px;\s*\}', 
    r':root {\n    --bg: #04080f;\n    --panel: rgba(8, 15, 24, 0.78);\n    --panel-strong: rgba(15, 23, 42, 0.94);\n    --text: #f8fafc;\n    --muted: rgba(203, 213, 225, 0.72);\n    --accent: #0f766e;\n    --accent-dark: #115e59;\n    --accent-warm: #b45309;\n    --danger: #b91c1c;\n    --border: rgba(148, 163, 184, 0.14);\n    --shadow: 0 18px 40px rgba(2, 6, 23, 0.28);\n    --sidebar-width: 320px;\n}', content, flags=re.DOTALL)

    # Replace body background
    content = re.sub(r'body\s*\{\s*margin:\s*0;\s*font-family:\s*Georgia,\s*"Times New Roman",\s*serif;\s*color:\s*var\(--text\);\s*background:[\s\S]*?linear-gradient\(180deg,\s*#fcf8f1\s*0%,\s*var\(--bg\)\s*100%\);\s*\}', 
    r'body {\n    margin: 0;\n    font-family: Georgia, "Times New Roman", serif;\n    color: var(--text);\n    background:\n        radial-gradient(circle at 18% 12%, rgba(16, 185, 129, 0.10), transparent 18%),\n        radial-gradient(circle at 82% 10%, rgba(37, 99, 235, 0.12), transparent 20%),\n        linear-gradient(180deg, #04080f 0%, #06101a 46%, #08111b 100%);\n}', content)

    # Replace sidebar
    content = re.sub(r'\.sidebar\s*\{[\s\S]*?border-right:\s*1px\s*solid\s*rgba\(255,\s*255,\s*255,\s*0\.08\);\s*\}', 
    r'.sidebar {\n    position: fixed;\n    inset: 0 auto 0 0;\n    width: var(--sidebar-width);\n    padding: 2rem 1.5rem;\n    background:\n        linear-gradient(180deg, rgba(3, 10, 18, 0.98), rgba(5, 21, 28, 0.96)),\n        linear-gradient(180deg, rgba(15, 118, 110, 0.12), transparent 44%);\n    color: #f9f5ee;\n    display: flex;\n    flex-direction: column;\n    gap: 2rem;\n    border-right: 1px solid rgba(148, 163, 184, 0.14);\n}', content)

    # Replace input, select, textarea
    content = re.sub(r'input,\s*select,\s*textarea\s*\{\s*width:\s*100%;\s*padding:\s*0\.82rem\s*0\.9rem;\s*border-radius:\s*14px;\s*border:\s*1px\s*solid\s*rgba\(81,\s*67,\s*54,\s*0\.14\);\s*background:\s*var\(--panel-strong\);\s*\}',
    r'input,\nselect,\ntextarea {\n    width: 100%;\n    padding: 0.82rem 0.9rem;\n    border-radius: 14px;\n    border: 1px solid rgba(148, 163, 184, 0.18);\n    background: rgba(2, 6, 23, 0.52);\n    color: var(--text);\n}\n\ninput::placeholder,\ntextarea::placeholder {\n    color: rgba(203, 213, 225, 0.48);\n}', content)

    # Replace .eyebrow
    content = re.sub(r'\.eyebrow\s*\{[\s\S]*?color:\s*var\(--accent-dark\);\s*\}',
    r'.eyebrow {\n    margin: 0 0 0.5rem;\n    text-transform: uppercase;\n    letter-spacing: 0.12em;\n    font-size: 0.78rem;\n    color: #67e8f9;\n}', content)

    # Replace .text-link
    content = re.sub(r'\.text-link\s*\{\s*color:\s*var\(--accent-dark\);\s*text-decoration:\s*none;\s*font-weight:\s*600;\s*\}',
    r'.text-link {\n    color: #67e8f9;\n    text-decoration: none;\n    font-weight: 600;\n}', content)

    # Replace .category-list li
    content = re.sub(r'\.category-list\s*li\s*\{\s*padding:\s*0\.85rem\s*1rem;\s*border-radius:\s*16px;\s*background:\s*rgba\(255,\s*255,\s*255,\s*0\.72\);\s*\}',
    r'.category-list li {\n    padding: 0.85rem 1rem;\n    border-radius: 16px;\n    background: rgba(148, 163, 184, 0.08);\n    border: 1px solid rgba(148, 163, 184, 0.10);\n}', content)

    # Replace .progress-track
    content = re.sub(r'\.progress-track\s*\{\s*width:\s*100%;\s*height:\s*12px;\s*margin-top:\s*1rem;\s*border-radius:\s*999px;\s*background:\s*rgba\(15,\s*118,\s*110,\s*0\.12\);\s*overflow:\s*hidden;\s*\}',
    r'.progress-track {\n    width: 100%;\n    height: 12px;\n    margin-top: 1rem;\n    border-radius: 999px;\n    background: rgba(103, 232, 249, 0.12);\n    overflow: hidden;\n}', content)

    # Replace th, td
    content = re.sub(r'th,\s*td\s*\{\s*text-align:\s*left;\s*padding:\s*0\.9rem\s*0\.7rem;\s*border-bottom:\s*1px\s*solid\s*rgba\(81,\s*67,\s*54,\s*0\.12\);\s*\}',
    r'th,\ntd {\n    text-align: left;\n    padding: 0.9rem 0.7rem;\n    border-bottom: 1px solid rgba(148, 163, 184, 0.12);\n}', content)

    # Replace .card-illustration
    content = re.sub(r'\.card-illustration\s*\{\s*width:\s*100%;\s*height:\s*160px;\s*object-fit:\s*cover;\s*display:\s*block;\s*margin-bottom:\s*1rem;\s*border-radius:\s*18px;\s*background:\s*rgba\(255,\s*255,\s*255,\s*0\.55\);\s*\}',
    r'.card-illustration {\n    width: 100%;\n    height: 160px;\n    object-fit: cover;\n    display: block;\n    margin-bottom: 1rem;\n    border-radius: 18px;\n    background: rgba(148, 163, 184, 0.10);\n}', content)

    # Replace budget alert banner block
    content = re.sub(r'\.budget-alert-banner\s*\{[\s\S]*?line-height:\s*1\.5;\s*\}',
    r'.budget-alert-banner {\n    display: flex;\n    align-items: center;\n    gap: 1.25rem;\n    padding: 1.25rem;\n    border-radius: 20px;\n    background: linear-gradient(135deg, rgba(185, 28, 28, 0.18), rgba(127, 29, 29, 0.10));\n    border: 1px solid rgba(248, 113, 113, 0.22);\n    margin-bottom: 1.5rem;\n    box-shadow: 0 10px 24px rgba(185, 28, 28, 0.04);\n}\n\n.budget-alert-banner .alert-icon {\n    font-size: 2rem;\n    line-height: 1;\n}\n\n.budget-alert-banner h3 {\n    margin: 0 0 0.25rem 0;\n    color: #fecaca;\n    font-size: 1.15rem;\n    font-weight: 700;\n}\n\n.budget-alert-banner p {\n    margin: 0;\n    color: rgba(226, 232, 240, 0.76);\n    font-size: 0.95rem;\n    line-height: 1.5;\n}', content)

    # Delete body:has(.app-shell) block completely, from `body:has(.app-shell) {` up to right before `.logout-form {`
    content = re.sub(r'body:has\(\.app-shell\) \{[\s\S]*?(?=\.logout-form \{)', '', content)

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("CSS updated successfully")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
