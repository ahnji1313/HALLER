from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3, datetime, uvicorn, html

app = FastAPI()
DB = "jihunwiki.db"

# ======== 데이터베이스 초기화 ========
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS pages (
        title TEXT PRIMARY KEY,
        content TEXT,
        created_at TEXT,
        updated_at TEXT
    )""")
    conn.commit()
    conn.close()

def get_page(title):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT content FROM pages WHERE title=?", (title,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_recent():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT title, updated_at FROM pages ORDER BY updated_at DESC LIMIT 10")
    data = cur.fetchall()
    conn.close()
    return data

def save_page(title, content):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if get_page(title):
        cur.execute("UPDATE pages SET content=?, updated_at=? WHERE title=?", (content, now, title))
    else:
        cur.execute("INSERT INTO pages VALUES (?,?,?,?)", (title, content, now, now))
    conn.commit()
    conn.close()

# ======== HTML 템플릿 ========
BASE_STYLE = """
<style>
body{background:#0b1020;color:#e9ecff;font-family:system-ui,sans-serif;margin:0;padding:20px;}
a{color:#6ea8ff;text-decoration:none;}
header{border-bottom:1px solid #23305d;margin-bottom:20px;}
textarea{width:100%;height:60vh;background:#141b34;color:#e9ecff;border:1px solid #2a3566;
border-radius:6px;padding:10px;font-family:monospace;}
button{background:#365fc7;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer;}
footer{text-align:center;color:#9ba7e2;margin-top:20px;font-size:12px;}
</style>
"""

def render_base(title, body):
    return f"""<!DOCTYPE html><html lang='ko'><head>
    <meta charset='UTF-8'><title>{title} - JihunWiki</title>{BASE_STYLE}</head>
    <body><header><h1><a href='/'>🌐 JihunWiki</a></h1></header>
    {body}
    <footer>© 2025 JihunWiki — Standalone Version</footer></body></html>"""

# ======== 라우팅 ========
@app.get("/", response_class=HTMLResponse)
def home():
    pages = get_recent()
    links = "".join([f"<li><a href='/wiki/{html.escape(t)}'>{html.escape(t)}</a> <small>{u}</small></li>" for t,u in pages])
    body = f"<h2>📄 최근 수정된 문서</h2><ul>{links}</ul><br><a href='/edit/새문서'>＋ 새 문서 작성</a>"
    return render_base("홈", body)

@app.get("/wiki/{title}", response_class=HTMLResponse)
def view(title: str):
    content = get_page(title)
    if content:
        safe = html.escape(content).replace("\\n", "<br>")
        return render_base(title, f"<h2>{html.escape(title)}</h2><div>{safe}</div><br><a href='/edit/{html.escape(title)}'✏️ 수정</a>")
    else:
        return RedirectResponse(f"/edit/{title}")

@app.get("/edit/{title}", response_class=HTMLResponse)
def edit_page(title: str):
    content = get_page(title) or ""
    body = f"""
    <h2>{html.escape(title)} 편집</h2>
    <form method='post'>
      <textarea name='content'>{html.escape(content)}</textarea><br>
      <button type='submit'>저장</button>
    </form>"""
    return render_base(f"{title} 편집", body)

@app.post("/edit/{title}", response_class=HTMLResponse)
def save_edit(title: str = Form(...), content: str = Form(...)):
    banned = ["porn","sex","야짤","에로","도박","카지노","crack","warez","torrent","hentai","darkweb"]
    if any(b in content.lower() for b in banned):
        return render_base("차단됨", "<h2>🚫 유해 단어가 포함되어 저장할 수 없습니다.</h2>")
    save_page(title, content)
    return RedirectResponse(f"/wiki/{title}", status_code=303)

# ======== 실행 ========
if __name__ == "__main__":
    init_db()
    print("🌐 JihunWiki 실행 중: http://127.0.0.1:5050")
    uvicorn.run(app, host="0.0.0.0", port=5050)
