# 11. LRU 快取 (LRU Cache)

> 主題：雙向鏈結串列 + 雜湊表　難度：★★★　時間限制：1 秒　相關教學：`lessons/04_linked_list.md`、`lessons/06_hash_table.md`

## 題目

實作一個容量為 `C` 的 LRU（Least Recently Used，最近最少使用）快取：

| 指令 | 說明 | 輸出 |
|---|---|---|
| `get k` | 若 `k` 在快取中，輸出它的值，並把它標記為「最近使用」；否則輸出 `-1` | 一行 |
| `put k v` | 設定 `k` 的值為 `v`，並標記為「最近使用」。如果放入新 key 後超過容量，要先把 **最久沒被使用** 的 key 淘汰，並輸出 `evict x`（`x` 是被淘汰的 key） | 有淘汰才輸出 |

注意：`put` 一個已經存在的 key 只是更新值（也算使用），不會淘汰任何東西。

## 輸入

第一行 `C Q`，接下來 `Q` 行指令。

## 輸出

依照上表。

## 限制

- `1 ≤ C ≤ 10^5`，`1 ≤ Q ≤ 3×10^5`
- `0 ≤ k ≤ 10^9`，`0 ≤ v ≤ 10^9`
- 每個操作都要 `O(1)`（平均）

## 範例

輸入
```
2 7
put 1 1
put 2 2
get 1
put 3 3
get 2
put 4 4
get 1
```
輸出
```
1
evict 2
-1
evict 1
-1
```

## 提示

- 雙向串列：越靠前面越「新」，最後面就是要淘汰的。
- `unordered_map<int, list<Node>::iterator>`：用 key 直接找到串列中的節點，`O(1)` 移到最前面（`list::splice`）。
- corner case：`C = 1`；`put` 已存在的 key；`get` 會改變淘汰順序。
