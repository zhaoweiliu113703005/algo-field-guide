/* =========================================================
   演算法登錄表（registry）
   - 格式見 AGENTS.md 第 8 節
   - 依分類分組，同分類內依難度由低到高；此順序即上一頁／下一頁順序
   - 新增頁面後務必執行 python3 scripts/check.py
   ========================================================= */
window.ALGORITHMS = [
  {
    slug: "binary-search",
    name: "二分搜尋",
    en: "Binary Search",
    category: "search",
    difficulty: 1,
    time: "O(log n)",
    summary: "在已排序陣列中，每次砍掉一半的搜尋範圍。",
    tags: ["陣列", "分治", "已排序"]
  },
  {
    slug: "quicksort",
    name: "快速排序",
    en: "Quicksort",
    category: "sorting",
    difficulty: 2,
    time: "O(n log n)",
    summary: "選一個基準值，把陣列分成小的一邊與大的一邊，再遞迴排序。",
    tags: ["分治", "遞迴", "原地排序"]
  },
  {
    slug: "bfs",
    name: "廣度優先搜尋",
    en: "Breadth-First Search",
    category: "graph",
    difficulty: 1,
    time: "O(V + E)",
    summary: "從起點一層一層往外擴散，找出無權圖的最短步數。",
    tags: ["佇列", "最短路徑", "遍歷"]
  },
  {
    slug: "dijkstra",
    name: "Dijkstra 最短路徑",
    en: "Dijkstra's Algorithm",
    category: "graph",
    difficulty: 2,
    time: "O((V + E) log V)",
    summary: "每次確定一個離起點最近的節點，求非負權重圖的最短路徑。",
    tags: ["優先佇列", "最短路徑", "加權圖"]
  }
];
