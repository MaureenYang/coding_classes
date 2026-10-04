# 07. 堆積與優先佇列 (Heap / Priority Queue)

> 練習題：`12_binary_heap`、`16_topo_sort`（用到 min-heap）

## 1. 需求

一直有新資料進來，而且隨時要拿出 **最小（或最大）** 的那一個。

| 做法 | 插入 | 取最小 |
|---|---|---|
| 無序陣列 | `O(1)` | `O(n)` |
| 有序陣列 | `O(n)` | `O(1)` |
| **二元堆積** | `O(log n)` | `O(log n)` |

## 2. 二元堆積的兩個性質

1. **形狀**：完全二元樹 —— 每一層都填滿，最後一層從左邊開始填。
2. **堆積性質**（min-heap）：每個節點 ≤ 它的小孩。所以根就是最小值。

完全二元樹可以直接存在 **陣列** 裡，不需要指標：

```
              1 (0)
           /        \
        3 (1)       2 (2)
       /    \      /
    7 (3)  4 (4) 5 (5)

陣列: [1, 3, 2, 7, 4, 5]
```

0-based 索引：
- 父親：`(i - 1) / 2`
- 左小孩：`2i + 1`
- 右小孩：`2i + 2`

## 3. push：放到最後，往上浮 (sift up)

```cpp
void push(ll x) {
    a.push_back(x);
    int i = a.size() - 1;
    while (i > 0) {
        int p = (i - 1) / 2;
        if (a[p] <= a[i]) break;   // 父親比較小，符合性質，停
        swap(a[p], a[i]);
        i = p;
    }
}
```

## 4. pop：最後一個搬到根，往下沉 (sift down)

```cpp
void pop() {
    a[0] = a.back();
    a.pop_back();
    int i = 0, n = a.size();
    while (true) {
        int l = 2 * i + 1, r = 2 * i + 2, m = i;
        if (l < n && a[l] < a[m]) m = l;   // 和「比較小的小孩」比
        if (r < n && a[r] < a[m]) m = r;
        if (m == i) break;
        swap(a[i], a[m]);
        i = m;
    }
}
```

**為什麼要和比較小的小孩交換？** 交換後，那個小孩變成另一個小孩的父親，它必須比另一個小孩小。

樹高是 `log n`，所以 push / pop 都是 `O(log n)`。

## 5. 建堆 (heapify) 是 O(n)

把 `n` 個元素一個一個 push 是 `O(n log n)`。但如果已經有整個陣列，
從最後一個非葉節點往前，對每個節點做 sift down，總共只要 `O(n)`（大部分節點都在底層，沉不了幾步）。

**堆積排序 (heap sort)**：建堆 `O(n)` + pop `n` 次 `O(n log n)`。

## 6. STL：priority_queue

```cpp
priority_queue<int> maxpq;                               // 預設是 **最大** 堆積！
priority_queue<int, vector<int>, greater<int>> minpq;    // 最小堆積

minpq.push(5);
minpq.top();
minpq.pop();

// 存 pair：先比 first，再比 second
priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;
```

常見應用：Dijkstra 最短路徑、合併 k 個有序串列、找第 k 大、事件模擬、拓撲排序要字典序最小。

## 7. Corner case checklist

- 空的 heap `pop` / `top`。
- 只有一個元素時 pop。
- 節點只有左小孩、沒有右小孩（`r < n` 的檢查）。
- 重複的值。
- `long long` 的極端值（比較時不要用相減，`a - b` 可能溢位）。
