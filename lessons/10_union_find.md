# 10. 併查集 (Union-Find / Disjoint Set Union)

> 練習題：`14_union_find`

## 1. 要解決的問題

有 `n` 個元素，一開始各自一組。要支援：

- **union(a, b)**：把 `a` 和 `b` 所在的組合併。
- **find(a)**：`a` 在哪一組（回傳該組的代表）。→ 用來判斷 `a`、`b` 是否同組。

例子：社群網路的朋友圈、判斷圖是否連通、Kruskal 最小生成樹、判斷無向圖有沒有環。

## 2. 用樹表示每一組

每一組是一棵樹，**根** 就是代表。`parent[x]` 存 `x` 的父親，根的 `parent` 是自己。

```
組 {1,2,3,5}       組 {4,6}
     1                4
    / \               |
   2   3              6
       |
       5
parent = [_, 1, 1, 1, 4, 3, 4]
```

```cpp
int find(int x) {
    while (parent[x] != x) x = parent[x];
    return x;
}
void unite(int a, int b) {
    a = find(a); b = find(b);
    if (a != b) parent[b] = a;
}
```

**問題**：如果每次都把大樹接在一個新點下面，樹會變成一條長鏈，`find` 變成 `O(n)`。

## 3. 優化一：按大小合併 (union by size)

把 **小的樹接到大的樹下面**。這樣某個點每往下一層，它所在的樹至少變大一倍
→ 樹高最多 `log n`。

```cpp
if (sz[a] < sz[b]) swap(a, b);
parent[b] = a;
sz[a] += sz[b];
```

## 4. 優化二：路徑壓縮 (path compression)

`find(x)` 走到根之後，順便把路上每個點都 **直接接到根**，下次就一步到位。

```
find(5) 之前：          之後：
     1                      1
    / \                  / | \
   2   3                2  3  5
       |
       5
```

```cpp
// 遞迴版（簡潔，但深度可能很大）
int find(int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); }

// 迴圈版（不怕 stack overflow）
int find(int x) {
    int r = x;
    while (parent[r] != r) r = parent[r];
    while (parent[x] != r) { int nx = parent[x]; parent[x] = r; x = nx; }
    return r;
}
```

兩個優化一起用，每個操作的攤銷複雜度是 `O(α(n))`，`α` 是反阿克曼函數，
對任何實際的 `n` 都 `≤ 4` —— 可以當作常數。

> 只做按大小合併時，樹高 ≤ `log n`，遞迴版 `find` 很安全。
> 只做路徑壓縮、沒做按大小合併時，第一次 `find` 仍可能走一條很長的鏈 —— 遞迴版會 stack overflow。

## 5. 完整模板

```cpp
struct DSU {
    vector<int> parent, sz;
    int groups;
    DSU(int n) : parent(n + 1), sz(n + 1, 1), groups(n) {
        iota(parent.begin(), parent.end(), 0);   // parent[i] = i
    }
    int find(int x) { ... }
    bool unite(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;                // 已經同組
        if (sz[a] < sz[b]) swap(a, b);
        parent[b] = a; sz[a] += sz[b]; groups--;
        return true;
    }
};
```

`unite` 回傳 `false` 代表 `a`、`b` 本來就連通 —— 在無向圖中加這條邊會形成 **環**。

## 6. Corner case checklist

- `union a a`：自己跟自己，組數不能減少。
- 重複 union 同一對。
- `n = 1`。
- 長鏈（測試有沒有優化）。
- 查詢 `size` 時要用 `sz[find(a)]`，不是 `sz[a]`（只有根的 `sz` 是對的）。
