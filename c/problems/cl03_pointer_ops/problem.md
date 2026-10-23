# CL03. 用指標操作陣列 (Pointer Operations)

> 主題：指標參數、「輸出參數」、指標算術、`[begin, end)` 範圍　難度：★★☆　時間限制：1 秒　相關教學：`c/lessons/05_pointers.md`

## 題目

C 的函式只能 **傳值**。想讓函式修改呼叫者的變數、或一次「回傳」好幾個值，就要傳 **指標**。
請實作下面五個函式（`main` 已經寫好，會呼叫它們）：

| 函式 | 作用 |
|---|---|
| `void swap_int(int *a, int *b)` | 交換 `*a` 和 `*b` |
| `void min_max(const int *begin, const int *end, int *mn, int *mx)` | 找出範圍 `[begin, end)` 的最小值和最大值，透過 `mn`、`mx` 傳回去（範圍保證非空） |
| `void reverse_range(int *begin, int *end)` | 把範圍 `[begin, end)` 反轉 |
| `int *find_first(int *begin, int *end, int x)` | 回傳範圍內第一個等於 `x` 的元素的 **指標**；找不到回傳 `NULL` |
| `void rotate_left(int *a, int n, int k)` | 把整個陣列 **向左旋轉** `k` 格（`k` 可能比 `n` 大） |

`[begin, end)` 的意思是：從 `begin` 指向的元素開始，到 `end` **之前** 為止（`end` 本身不算）。

`main` 讀入長度 `n` 的陣列 `a`，接著處理指令（索引從 0 開始）：

| 指令 | `main` 呼叫的方式 | 輸出 |
|---|---|---|
| `swap i j` | `swap_int(&a[i], &a[j])` | — |
| `minmax l r` | `min_max(a + l, a + r + 1, &mn, &mx)` | `mn mx` |
| `rev l r` | `reverse_range(a + l, a + r + 1)` | — |
| `find x` | `p = find_first(a, a + n, x)` | `p - a`（索引），找不到輸出 `-1` |
| `rot k` | `rotate_left(a, n, k)` | — |
| `print` | | 整個陣列，空白分隔 |

向左旋轉 1 格：`1 2 3 4 5` → `2 3 4 5 1`。

## 輸入

第一行 `n`，第二行 `n` 個整數。第三行 `Q`，接下來 `Q` 行指令。

## 限制

- `1 ≤ n ≤ 1000`，`1 ≤ Q ≤ 20000`，`|a[i]|, |x| ≤ 10^9`
- `0 ≤ l ≤ r < n`，`0 ≤ i, j < n`，`0 ≤ k ≤ 10^9`

## 範例

輸入
```
5
3 1 4 1 5
7
minmax 0 4
find 1
rev 1 3
print
rot 2
print
find 9
```
輸出
```
1 5
1
3 1 4 1 5
4 1 5 3 1
-1
```

（`rev 1 3` 反轉 `1 4 1` 還是 `1 4 1`；`rot 2` 把 `3 1` 移到後面。）

## 提示

- `*a` 是「`a` 指向的那個 `int`」。`swap_int` 就是三行：`int t = *a; *a = *b; *b = t;`
- 走訪範圍：`for (const int *p = begin; p != end; p++) { ... *p ... }`
- 反轉：一個指標從頭、一個從尾（`end - 1`），交換後往中間靠攏，直到相遇。
- 旋轉的經典技巧：**三次反轉**。先 `k %= n`；反轉前 `k` 個、反轉剩下的、再反轉整個陣列。可以直接用你寫好的 `reverse_range`。
- 小心 `swap i i`（同一個元素和自己交換）。
