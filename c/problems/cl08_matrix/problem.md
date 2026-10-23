# CL08. 動態二維矩陣 (Dynamic 2D Matrix)

> 主題：指標的指標 `long long **`、動態配置二維陣列、配置與釋放要成對　難度：★★★　時間限制：1 秒　相關教學：`c/lessons/07_dynamic_memory.md`

## 題目

矩陣的大小要到執行時才知道，所以要 **動態配置**。請實作：

| 函式 | 作用 |
|---|---|
| `long long **mat_alloc(int r, int c)` | 配置 `r × c` 的矩陣，全部填 0；之後可以用 `m[i][j]` 存取 |
| `void mat_free(long long **m, int r)` | 釋放 `mat_alloc` 配置的所有記憶體 |
| `long long **mat_transpose(long long **a, int r, int c)` | 回傳 **新配置的** `c × r` 轉置矩陣 |
| `long long **mat_add(long long **a, long long **b, int r, int c)` | 回傳 **新配置的** `a + b` |
| `long long **mat_mul(long long **a, long long **b, int r, int k, int c)` | `a` 是 `r × k`、`b` 是 `k × c`，回傳 **新配置的** `r × c` 乘積 |

`main` 讀入矩陣 `A`（`r1 × c1`）和 `B`（`r2 × c2`），然後輸出：

```
transpose of A:
（A 的轉置）
A + B:
（相加的結果；大小不同時輸出 cannot add）
A * B:
（相乘的結果；c1 != r2 時輸出 cannot multiply）
```

矩陣每一列輸出一行，數字之間一個空白。`main` 會把所有矩陣都交給 `mat_free` 釋放，最後檢查記憶體洩漏（`leak check: ok`）。
**記憶體一律用 `xmalloc` / `xfree`。**

## 輸入

`r1 c1`，接著 `r1` 行每行 `c1` 個整數；`r2 c2`，接著 `r2` 行每行 `c2` 個整數。

## 限制

- `1 ≤ r1, c1, r2, c2 ≤ 200`，元素的絕對值 `≤ 1000`

## 範例

輸入
```
2 3
1 2 3
4 5 6
3 2
1 0
0 1
1 1
```
輸出
```
transpose of A:
1 4
2 5
3 6
A + B:
cannot add
A * B:
4 5
10 11
leak check: ok
```

## 提示

**做法一：每一列各配置一次**

```c
long long **m = xmalloc(r * sizeof(long long *));    /* r 個「列指標」 */
for (int i = 0; i < r; i++)
    m[i] = xmalloc(c * sizeof(long long));            /* 每一列 c 個元素 */
```

釋放時要 **反過來**：先釋放每一列，最後才釋放列指標陣列（先釋放 `m` 的話就找不到每一列了）。

**做法二：一整塊 + 列指標**（只配置兩次，記憶體連續、比較快）

```c
long long **m = xmalloc(r * sizeof(long long *));
long long *block = xmalloc((size_t)r * c * sizeof(long long));
for (int i = 0; i < r; i++) m[i] = block + (size_t)i * c;
```

釋放時：`xfree(m[0])`（就是 `block`）再 `xfree(m)`。

- `xmalloc` 給的記憶體內容是垃圾值，記得填 0（迴圈，或 `<string.h>` 的 `memset`）。
- 相乘：`res[i][j] = Σ a[i][t] * b[t][j]`，`t` 從 0 到 `k - 1`。
