# 04. 單向鏈結串列 (Singly Linked List)

> 主題：鏈結串列　難度：★★☆　時間限制：2 秒　相關教學：`lessons/04_linked_list.md`

## 題目

請 **不要使用 `std::list` / `std::vector`**，用 `struct Node { int val; Node* next; }` 自己實作單向鏈結串列，支援：

| 指令 | 說明 | 失敗時輸出 |
|---|---|---|
| `push_front x` | 在最前面插入 `x` | — |
| `push_back x` | 在最後面插入 `x` | — |
| `pop_front` | 刪除第一個 | 空的輸出 `error` |
| `pop_back` | 刪除最後一個 | 空的輸出 `error` |
| `insert i x` | 插入 `x`，使它成為第 `i` 個（0-based），`0 ≤ i ≤ size` | 越界輸出 `error` |
| `erase i` | 刪除第 `i` 個，`0 ≤ i < size` | 越界輸出 `error` |
| `reverse` | 把整個串列反轉（**不能開新節點**） | — |
| `print` | 輸出所有元素，空白分隔；空串列輸出 `empty` | — |
| `size` | 輸出元素個數 | — |

## 輸入

第一行 `Q`，接下來 `Q` 行指令。

## 輸出

依照上表。

## 限制

- `1 ≤ Q ≤ 5000`
- `-10^9 ≤ x ≤ 10^9`，`i` 可能是負數
- 建議 `push_back` 用 tail 指標做到 `O(1)`

## 範例

輸入
```
10
push_back 1
push_back 2
push_front 0
print
insert 1 9
print
erase 0
reverse
print
erase 5
```
輸出
```
0 1 2
0 9 1 2
2 1 9
error
```

## 常見錯誤（corner case）

- 刪掉 **最後一個** 節點後，`tail` 指標沒有更新。
- 串列變空之後 `head`、`tail` 沒有設回 `nullptr`。
- `reverse` 之後 `tail` 應該變成原本的 `head`。
- `insert size x` 是合法的（等於 push_back）。
