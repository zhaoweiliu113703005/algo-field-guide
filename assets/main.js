/* =========================================================
   演算法圖鑑 — 全站共用腳本
   規則：只新增、不刪改既有函式（見 AGENTS.md 第 10 節）
   依賴：data/algorithms.js 必須先載入（window.ALGORITHMS）
   ========================================================= */

const REPO_URL = "https://github.com/zhaoweiliu113703005/algo-field-guide";

// 分類表：新增分類時，同步修改 AGENTS.md 第 6 節與 style.css
const CATEGORIES = {
  search:  "搜尋",
  sorting: "排序",
  graph:   "圖論",
  dp:      "動態規劃",
  greedy:  "貪婪",
};

const ALGOS = window.ALGORITHMS || [];

function difficultyDots(n) {
  return "●".repeat(n) + "<span>" + "●".repeat(3 - n) + "</span>";
}

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* ---------- 首頁：卡片、搜尋、分類篩選 ---------- */
function renderHome() {
  const grid = document.getElementById("grid");
  const chips = document.getElementById("chips");
  const search = document.getElementById("search");
  const count = document.getElementById("count");
  if (!grid) return;

  let active = "all";

  const used = Object.keys(CATEGORIES).filter(k => ALGOS.some(a => a.category === k));
  chips.innerHTML =
    `<button class="chip" data-cat="all" aria-pressed="true">全部</button>` +
    used.map(k => `<button class="chip cat-${k}" data-cat="${k}" aria-pressed="false"><span class="dot"></span>${CATEGORIES[k]}</button>`).join("");

  function draw() {
    const q = search.value.trim().toLowerCase();
    const list = ALGOS.filter(a => {
      if (active !== "all" && a.category !== active) return false;
      if (!q) return true;
      const hay = [a.name, a.en, a.summary, ...(a.tags || [])].join(" ").toLowerCase();
      return hay.includes(q);
    });
    count.textContent = `${list.length} / ${ALGOS.length} 種演算法`;
    grid.innerHTML = list.length
      ? list.map(a => `
        <a class="card cat-${a.category}" href="algorithms/${a.slug}.html">
          <div class="meta"><span class="tag">${CATEGORIES[a.category]}</span><span class="diff" title="難度 ${a.difficulty}/3">${difficultyDots(a.difficulty)}</span></div>
          <h2>${a.name}</h2>
          <div class="en">${a.en}</div>
          <p>${a.summary}</p>
          <div class="time">平均 ${a.time}</div>
        </a>`).join("")
      : `<div class="empty">找不到符合的演算法。</div>`;
  }

  chips.addEventListener("click", e => {
    const b = e.target.closest(".chip");
    if (!b) return;
    active = b.dataset.cat;
    chips.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", c === b ? "true" : "false"));
    draw();
  });
  search.addEventListener("input", draw);
  draw();
}

/* ---------- 演算法頁：上一頁／下一頁 ---------- */
function renderPager() {
  const slug = document.body.dataset.slug;
  const pager = document.getElementById("pager");
  if (!slug || !pager) return;
  const i = ALGOS.findIndex(a => a.slug === slug);
  if (i < 0) return;
  const prev = ALGOS[i - 1], next = ALGOS[i + 1];
  pager.innerHTML =
    (prev ? `<a class="prev" href="${prev.slug}.html"><small>← 上一個</small><span>${prev.name}</span></a>` : "") +
    (next ? `<a class="next" href="${next.slug}.html"><small>下一個 →</small><span>${next.name}</span></a>` : "");
}

/* ---------- 程式碼：註解上色 + 複製按鈕 ---------- */
function enhanceCode() {
  document.querySelectorAll("pre > code").forEach(code => {
    const raw = code.textContent;
    code.innerHTML = raw.split("\n").map(line => {
      const m = line.match(/^(.*?)(#.*)$/);
      return m ? escapeHtml(m[1]) + `<span class="c">${escapeHtml(m[2])}</span>` : escapeHtml(line);
    }).join("\n");

    const pre = code.parentElement;
    const wrap = document.createElement("div");
    wrap.className = "code-block";
    pre.replaceWith(wrap);
    wrap.appendChild(pre);
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "複製";
    btn.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(raw); btn.textContent = "已複製"; }
      catch { btn.textContent = "請手動選取"; }
      setTimeout(() => (btn.textContent = "複製"), 1500);
    });
    wrap.appendChild(btn);
  });
}

/* ---------- 目錄：標示目前閱讀的區塊 ---------- */
function trackToc() {
  const links = [...document.querySelectorAll(".toc a")];
  if (!links.length || !("IntersectionObserver" in window)) return;
  const byId = Object.fromEntries(links.map(a => [a.getAttribute("href").slice(1), a]));
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        links.forEach(a => a.classList.remove("active"));
        byId[en.target.id]?.classList.add("active");
      }
    });
  }, { rootMargin: "-20% 0px -70% 0px" });
  document.querySelectorAll("article section[id]").forEach(s => io.observe(s));
}

/* ---------- 頁尾 ---------- */
function renderFooter() {
  const f = document.getElementById("site-footer");
  if (!f) return;
  f.innerHTML = `演算法圖鑑 · 共 ${ALGOS.length} 種演算法 · 內容依 <a href="${REPO_URL}/blob/main/AGENTS.md">AGENTS.md</a> 規則撰寫 · <a href="${REPO_URL}">GitHub</a>`;
}

document.addEventListener("DOMContentLoaded", () => {
  renderHome();
  renderPager();
  enhanceCode();
  trackToc();
  renderFooter();
});
