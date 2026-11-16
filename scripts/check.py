#!/usr/bin/env python3
"""演算法圖鑑 規則檢查腳本

用法：python3 scripts/check.py
檢查 AGENTS.md 中可被機器驗證的規則；全部通過才會印出 ALL CHECKS PASSED。
只用 Python 標準函式庫。
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALGO_DIR = ROOT / "algorithms"
SECTIONS = ["intuition", "steps", "example", "complexity", "code", "pitfalls", "related"]
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errors: list[str] = []


def err(where: str, msg: str) -> None:
    errors.append(f"[{where}] {msg}")


def load_categories() -> dict[str, str]:
    src = (ROOT / "assets/main.js").read_text(encoding="utf-8")
    block = re.search(r"const CATEGORIES = \{(.*?)\};", src, re.S).group(1)
    return dict(re.findall(r'(\w+):\s*"([^"]+)"', block))


def load_registry() -> list[dict]:
    src = (ROOT / "data/algorithms.js").read_text(encoding="utf-8")
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    body = src[src.index("[") : src.rindex("]") + 1]
    body = re.sub(r"^(\s*)(\w+):", r'\1"\2":', body, flags=re.M)
    return json.loads(body)


def text_of(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def check_registry(reg: list[dict], cats: dict[str, str]) -> None:
    seen = set()
    order: list[str] = []
    for i, a in enumerate(reg):
        where = f"registry #{i} {a.get('slug', '?')}"
        for key in ["slug", "name", "en", "category", "difficulty", "time", "summary", "tags"]:
            if key not in a:
                err(where, f"缺少欄位 {key}")
        slug = a.get("slug", "")
        if not SLUG_RE.match(slug):
            err(where, "slug 必須是小寫英文與 - 組成")
        if slug in seen:
            err(where, "slug 重複")
        seen.add(slug)
        if a.get("category") not in cats:
            err(where, f"category 必須是 {list(cats)} 之一")
        if a.get("difficulty") not in (1, 2, 3):
            err(where, "difficulty 只能是 1、2、3")
        s = a.get("summary", "")
        if len(s) > 30 or not s.endswith("。"):
            err(where, "summary 需 ≤ 30 字且以句號結尾")
        if not 1 <= len(a.get("tags", [])) <= 4:
            err(where, "tags 需 1–4 個")
        if "演算法" in a.get("name", ""):
            err(where, "中文名不加「演算法」")
        if not order or order[-1] != a.get("category"):
            if a.get("category") in order:
                err(where, "同分類的演算法必須排在一起")
            order.append(a.get("category"))
        elif reg[i - 1].get("difficulty", 0) > a.get("difficulty", 0):
            err(where, "同分類內需依難度由低到高排列")


def check_files(reg: list[dict]) -> None:
    registered = {a["slug"] for a in reg}
    files = {p.stem for p in ALGO_DIR.glob("*.html") if not p.name.startswith("_")}
    for s in registered - files:
        err(s, f"registry 有登錄，但找不到 algorithms/{s}.html")
    for s in files - registered:
        err(s, "頁面存在，但沒有登錄到 data/algorithms.js")
    if not (ALGO_DIR / "_template.html").exists():
        err("_template", "範本 algorithms/_template.html 不可刪除")


def run_python(where: str, code: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
    try:
        r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            err(where, "Python 實作執行失敗：\n    " + r.stderr.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        err(where, "Python 實作執行超過 10 秒")
    finally:
        Path(f.name).unlink()


def check_page(a: dict, cats: dict[str, str], all_slugs: set[str]) -> None:
    slug = a["slug"]
    path = ALGO_DIR / f"{slug}.html"
    if not path.exists():
        return
    src = path.read_text(encoding="utf-8")
    w = f"{slug}.html"

    if "{{" in src or "}}" in src:
        err(w, "殘留 {{…}} 佔位符")
    if "<style" in src or ' style="' in src:
        err(w, "不可在頁面中寫 <style> 或行內 style")

    body = re.search(r"<body([^>]*)>", src)
    attrs = body.group(1) if body else ""
    if f'data-slug="{slug}"' not in attrs:
        err(w, f'<body> 需有 data-slug="{slug}"')
    if f'class="cat-{a["category"]}"' not in attrs:
        err(w, f'<body> 需有 class="cat-{a["category"]}"')

    title = re.search(r"<title>(.*?)</title>", src)
    if not title or title.group(1) != f"{a['name']} · 演算法圖鑑":
        err(w, f"<title> 應為「{a['name']} · 演算法圖鑑」")
    desc = re.search(r'<meta name="description" content="([^"]*)"', src)
    if not desc or desc.group(1) != a["summary"]:
        err(w, "meta description 需與 registry summary 相同")
    h1 = re.search(r"<h1>(.*?)</h1>", src)
    if not h1 or text_of(h1.group(1)) != a["name"]:
        err(w, "<h1> 需與 registry name 相同")
    lede = re.search(r'<p class="lede">(.*?)</p>', src, re.S)
    if not lede or text_of(lede.group(1)) != a["summary"]:
        err(w, ".lede 需與 registry summary 相同")
    if cats.get(a["category"], "") not in src:
        err(w, "頁首需顯示分類名稱")

    ids = re.findall(r'<section id="([^"]+)"', src)
    if ids != SECTIONS:
        err(w, f"section 需依序為 {SECTIONS}，目前是 {ids}")
        return
    parts = {}
    for i, sid in enumerate(SECTIONS):
        start = src.index(f'<section id="{sid}"')
        end = src.index(f'<section id="{SECTIONS[i + 1]}"') if i + 1 < len(SECTIONS) else src.index("</article>")
        parts[sid] = src[start:end]

    if 'class="callout key"' not in parts["intuition"]:
        err(w, "直覺區塊需有 .callout.key 一句話總結")
    n_steps = len(re.findall(r"<li>", parts["steps"]))
    if 'class="steps"' not in parts["steps"] or not 3 <= n_steps <= 7:
        err(w, f"步驟需用 ol.steps 且 3–7 步（目前 {n_steps}）")
    if 'class="trace"' not in parts["example"] or 'class="hl"' not in parts["example"]:
        err(w, "手算範例需有 table.trace 並以 td.hl 標示關鍵變化")
    if parts["complexity"].count('class="cx"') < 3:
        err(w, "複雜度需至少 3 張 .cx 卡片")

    code = re.search(r"<pre><code>(.*?)</code></pre>", parts["code"], re.S)
    if not code:
        err(w, "Python 實作需放在 <pre><code>")
    else:
        py = html.unescape(code.group(1))
        if len(py.strip().splitlines()) > 40:
            err(w, "Python 實作不可超過 40 行")
        if 'if __name__ == "__main__":' not in py:
            err(w, '需附 if __name__ == "__main__": 範例呼叫')
        run_python(w, py)

    n_warn = parts["pitfalls"].count('class="callout warn"')
    if not 2 <= n_warn <= 4:
        err(w, f"常見陷阱需 2–4 個 .callout.warn（目前 {n_warn}）")

    links = re.findall(r'href="([a-z0-9-]+)\.html"', parts["related"])
    if not links:
        err(w, "相關演算法至少要連到 1 個頁面")
    for l in links:
        if l not in all_slugs:
            err(w, f"相關演算法連到不存在的頁面 {l}.html")


def check_css(cats: dict[str, str]) -> None:
    css = (ROOT / "assets/style.css").read_text(encoding="utf-8")
    for k in cats:
        if f".cat-{k}" not in css or f"--cat-{k}" not in css:
            err("style.css", f"缺少分類 {k} 的 --cat-{k} 變數或 .cat-{k} class")


def main() -> int:
    cats = load_categories()
    reg = load_registry()
    slugs = {a["slug"] for a in reg}
    check_registry(reg, cats)
    check_files(reg)
    check_css(cats)
    for a in reg:
        check_page(a, cats, slugs)

    if errors:
        print(f"✗ 發現 {len(errors)} 個問題：")
        for e in errors:
            print("  -", e)
        return 1
    print(f"✓ {len(reg)} 個頁面全部符合 AGENTS.md 規則")
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
