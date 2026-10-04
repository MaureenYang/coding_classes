# 09. 圖：BFS、DFS 與拓撲排序

> 練習題：`15_maze_bfs`、`16_topo_sort`

## 1. 圖的表示法

圖 = 點 (vertex) + 邊 (edge)。邊可以有方向（有向圖）或沒有（無向圖）。

```
1 ── 2
|    |
4 ── 3 ── 5
```

**鄰接串列 (adjacency list)**：最常用，空間 `O(V + E)`。

```cpp
vector<vector<int>> adj(n + 1);
for (int i = 0; i < m; i++) {
    int a, b; cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);   // 無向圖要加兩次
}
```

**鄰接矩陣**：`g[a][b] = true`，空間 `O(V^2)`，只適合點很少的圖。

**網格 (grid)** 也是圖：每一格是一個點，上下左右相鄰的格子之間有邊。

```cpp
const int dr[4] = {-1, 1, 0, 0}, dc[4] = {0, 0, -1, 1};
for (int d = 0; d < 4; d++) {
    int nr = r + dr[d], nc = c + dc[d];
    if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;  // 先檢查邊界！
    if (g[nr][nc] == '#') continue;
    ...
}
```

## 2. BFS 廣度優先搜尋

用 **queue**，一層一層往外擴散，像水波：

```
距離 0: S
距離 1: S 的鄰居
距離 2: 距離 1 的點的鄰居（還沒走過的）
...
```

```cpp
vector<int> dist(n + 1, -1);
queue<int> q;
dist[s] = 0; q.push(s);
while (!q.empty()) {
    int u = q.front(); q.pop();
    for (int v : adj[u]) {
        if (dist[v] != -1) continue;   // 已經走過
        dist[v] = dist[u] + 1;
        q.push(v);
    }
}
```

**重點**：在 **放進 queue 的時候** 就標記已走過，不要等到拿出來才標記，否則同一個點會被放進很多次。

**性質**：每條邊權重都是 1 時，BFS 第一次到達某點的距離就是 **最短距離**。複雜度 `O(V + E)`。

## 3. DFS 深度優先搜尋

一條路走到底，走不通再退回來。用 **遞迴**（或自己的 stack）。

```cpp
vector<bool> vis(n + 1);
void dfs(int u) {
    vis[u] = true;
    for (int v : adj[u]) if (!vis[v]) dfs(v);
}
```

用途：找連通塊、判斷有沒有環、拓撲排序、回溯法。

> ⚠️ DFS **不能** 找最短路徑。而且遞迴深度可能等於點的數量 —— `1000×1000` 的蛇形迷宮，
> 遞迴深度是 50 萬層，會 **stack overflow**。

## 4. 拓撲排序 (Topological Sort)

有向無環圖 (DAG) 中，把點排成一列，使每條邊 `a → b` 都滿足 `a` 在 `b` 前面。
例子：修課順序、編譯相依性、工作排程。

### Kahn 演算法（BFS 版）

1. 算每個點的 **入度**（有幾條邊指向它）。
2. 入度 0 的點都可以先做，放進 queue。
3. 拿出一個點 `u` 輸出，把 `u` 的所有出邊刪掉（鄰居入度 −1），入度變 0 的鄰居放進 queue。
4. 如果最後輸出的點 **不到 n 個** → 圖中有 **環**，不可能排序。

```cpp
for (int v = 1; v <= n; v++) if (indeg[v] == 0) q.push(v);
while (!q.empty()) {
    int u = q.front(); q.pop();
    order.push_back(u);
    for (int v : adj[u]) if (--indeg[v] == 0) q.push(v);
}
if ((int)order.size() < n) → 有環
```

**要字典序最小**：把 `queue` 換成 `priority_queue<int, vector<int>, greater<int>>`，
每次都拿目前可以做的點中編號最小的。複雜度變成 `O((V + E) log V)`。

## 5. 加權最短路徑（延伸）

邊有權重時 BFS 就不對了，要用 **Dijkstra**（權重非負，用 priority_queue）：

```cpp
vector<ll> d(n + 1, INF);
priority_queue<pair<ll,int>, vector<pair<ll,int>>, greater<>> pq;
d[s] = 0; pq.push({0, s});
while (!pq.empty()) {
    auto [du, u] = pq.top(); pq.pop();
    if (du > d[u]) continue;            // 過期的資料
    for (auto [v, w] : adj[u])
        if (d[u] + w < d[v]) { d[v] = d[u] + w; pq.push({d[v], v}); }
}
```

## 6. Corner case checklist

- 起點等於終點？起點被牆圍住？走不到？
- 網格只有一列或一行（`1 × C`）。
- 最大的網格 + 最長的路徑（蛇形）。
- 圖有 **自環** `a → a`（拓撲排序一定失敗）、**重複的邊**。
- 圖 **不連通**：有環的部分不一定和其他部分相連。
- 點的編號是 1-based 還是 0-based？陣列要開 `n + 1`。
