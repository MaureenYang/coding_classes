# CL05. C 語言的鏈結串列 (Linked List in C)

> 主題：`struct` + 指標、`malloc` / `free`、`Node **` 指標的指標　難度：★★★　時間限制：1 秒　相關教學：`c/lessons/12_data_structures_in_c.md`

## 題目

用 C 實作 **單向鏈結串列**，並且記錄 `tail`（最後一個節點）讓「加到尾端」也是 `O(1)`：

```c
typedef struct Node {
    int val;
    struct Node *next;
} Node;

typedef struct {
    Node *head;    /* 第一個節點；空串列時是 NULL */
    Node *tail;    /* 最後一個節點；空串列時是 NULL */
    size_t size;
} List;
```

| 函式 | 作用 |
|---|---|
| `void list_init(List *l)` | 變成空串列 |
| `void list_free(List *l)` | 釋放所有節點，變回空串列 |
| `void push_front(List *l, int x)` | 加在最前面 |
| `void push_back(List *l, int x)` | 加在最後面（要用 `tail`，`O(1)`） |
| `int pop_front(List *l)` | 移除並回傳第一個（`main` 保證不是空的） |
| `int remove_first(List *l, int x)` | 刪除 **第一個** 值等於 `x` 的節點；有刪除回傳 1，找不到回傳 0 |
| `void list_reverse(List *l)` | 反轉整個串列 |
| `void list_unique(List *l)` | 刪除 **相鄰重複** 的節點，只留每一段的第一個（`1 1 2 1 1` → `1 2 1`） |

**任何時候 `head`、`tail`、`size` 都要正確**（這是這個資料結構的不變量）。
節點用 `xmalloc` 配置、`xfree` 釋放；程式結束時會檢查記憶體洩漏。

`main` 處理的指令：

| 指令 | 輸出 |
|---|---|
| `pushf x` / `pushb x` | — |
| `popf` | 被移除的值；空的時候輸出 `empty` |
| `del x` | `ok` 或 `not found` |
| `rev` / `uniq` | — |
| `size` | 節點數 |
| `ends` | 第一個和最後一個節點的值（檢查 `head` / `tail`）；空的時候輸出 `empty` |
| `print` | 所有值；空的時候輸出 `empty` |

最後輸出 `leak check: ok`。

## 輸入

第一行 `Q`，接下來 `Q` 行指令。

## 限制

- `1 ≤ Q ≤ 2 × 10^5`，`|x| ≤ 10^9`
- `del`、`rev`、`uniq` 合計最多 2000 次（每次可以 `O(n)`）

## 範例

輸入
```
10
pushb 2
pushb 3
pushf 1
pushb 3
print
del 3
ends
rev
pushb 0
print
```
輸出
```
1 2 3 3
ok
1 3
3 2 1 0
leak check: ok
```

## 提示

- **最容易錯的是 `tail`**：刪掉最後一個節點、刪到變成空串列、反轉之後，`tail` 都要跟著更新。`ends` 指令就是在檢查這個。
- 刪除節點的經典寫法：用 `Node **pp` 指向「指向目前節點的那個指標」（一開始是 `&l->head`），找到之後 `*pp = cur->next;` —— 刪除第一個節點和中間的節點寫法完全一樣，不用特別處理。
- 反轉：三個指標 `prev`、`cur`、`next`，一個一個把 `next` 指向反過來。反轉前的 `head` 會變成新的 `tail`。
- `list_free`：先把 `next` 存起來，再 `xfree` 目前的節點（`free` 之後就不能再讀 `cur->next` 了）。
