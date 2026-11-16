# 演算法圖鑑 Algo Field Guide

一頁一個演算法的複習網站。每一頁都用同一套順序講完一個演算法：

**直覺 → 步驟 → 手算範例 → 複雜度 → Python 實作 → 常見陷阱 → 相關演算法**

🔗 網站：https://zhaoweiliu113703005.github.io/algo-field-guide/

## 這個專案的重點：一套讓 AI 能接手的規則

網站本身不是終點，重點是 [`AGENTS.md`](AGENTS.md)：它把版型、命名、登錄方式、寫作風格與檢查流程寫清楚，讓 AI（或任何人）只要說一句「新增 merge sort」，就能做出與現有頁面一致的新頁面。

| 檔案 | 角色 |
|---|---|
| `AGENTS.md` | 專案規則（唯一真相來源） |
| `algorithms/_template.html` | 新頁面的範本，7 個固定區塊 |
| `data/algorithms.js` | 演算法登錄表，首頁卡片與上一頁／下一頁都由它產生 |
| `scripts/check.py` | 把規則變成可執行的檢查：區塊順序、佔位符、registry 一致性、連結，並**實際執行每頁的 Python 程式碼** |

## 本機預覽

不需要安裝任何東西，直接用瀏覽器打開 `index.html` 即可。

## 新增一個演算法

照 `AGENTS.md` 第 5 節，最後執行：

```bash
python3 scripts/check.py   # 必須看到 ALL CHECKS PASSED
```

## 目前收錄

二分搜尋、快速排序、廣度優先搜尋、Dijkstra 最短路徑
