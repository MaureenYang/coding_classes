# C14. 智慧指標串列 (unique_ptr)

> 主題：智慧指標、所有權、移動語意、解構的遞迴陷阱　難度：★★★　時間限制：1 秒　相關教學：`cpp/lessons/06_memory_raii.md`

## 題目

用 `std::unique_ptr` 實作單向鏈結串列，**程式裡不准出現 `new` 和 `delete`**：

```cpp
struct Node {
    long long val;
    unique_ptr<Node> next;   // 「擁有」下一個節點
};
```

| 指令 | 輸出 |
|---|---|
| `push x` | 在最前面插入 `x` |
| `pushmany n` | 依序對 `1, 2, ..., n` 做 `push`（做完後最前面是 `n`） |
| `pop` | 輸出並移除最前面的元素；空的輸出 `empty` |
| `front` | 輸出最前面的元素；空的輸出 `empty` |
| `reverse` | 反轉整個串列 |
| `size` | 元素個數 |
| `sum` | 所有元素的總和 |
| `print k` | 輸出前 `min(k, size)` 個元素（空白分隔）；空的輸出 `empty` |
| `clear` | 清空串列 |

## 輸入

第一行 `Q`，接下來 `Q` 行指令。

## 限制

- `1 ≤ Q ≤ 2×10^5`
- 任何時刻串列長度 `≤ 2×10^6`；`|x| ≤ 10^9`；`print` 輸出的元素總數 `≤ 2×10^5`

## 範例

輸入
```
7
pushmany 3
push 10
print 5
reverse
pop
sum
size
```
輸出
```
10 3 2 1
1
15
3
```

## 最重要的陷阱：解構時的遞迴

當 `head` 被銷毀時，它會銷毀 `head->next`，`next` 又銷毀它的 `next` …… **這是遞迴**！
串列有 100 萬個節點時，解構會遞迴 100 萬層 → **堆疊溢位，程式在結束時當掉（RE）**。

`clear` 和 **程式結束時的解構** 都要處理這個問題：寫一個解構子（或 `clear`），用 **迴圈** 一個一個拆：

```cpp
while (head) head = std::move(head->next);   // 每次只銷毀一個節點
```

想一想為什麼這一行就夠了（提示：`head->next` 先被移走，舊的 `head` 被銷毀時它的 `next` 已經是空的）。

## 提示

- `unique_ptr` **不能複製，只能移動**：`a = b;` 編譯不過，要寫 `a = std::move(b);`。
- 插入：`auto nd = make_unique<Node>(); nd->val = x; nd->next = std::move(head); head = std::move(nd);`
- 反轉：和普通指標的版本一樣，但每一次「轉移指向」都要用 `std::move`。
- 走訪不需要擁有權：用普通指標 `for (Node* p = head.get(); p; p = p->next.get())`。
- `sum` 可能超過 `int`，用 `long long`。
