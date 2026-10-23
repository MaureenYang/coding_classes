# CL09. 函式指標與指令表 (Function Pointers)

> 主題：函式指標、`typedef`、查表分派、`qsort` 比較函式　難度：★★★　時間限制：1 秒　相關教學：`c/lessons/09_function_pointers.md`

## 題目

有一個整數陣列，要對它做各種「套用函式」的操作。重點是：**操作的種類由輸入的名字決定**，程式要用名字查表，找到對應的 **函式指標** 再呼叫。

樣板已經定義好四種函式指標型別：

```c
typedef int (*MapFn)(int x);                         /* 把 x 變成另一個值 */
typedef int (*PredFn)(int x);                        /* 回傳 1（保留）或 0（刪掉） */
typedef long long (*FoldFn)(long long acc, int x);   /* 把 x 累積進 acc */
typedef int (*CmpFn)(const void *a, const void *b);  /* 給 qsort 用的比較函式 */
```

**你要做的：**

1. 寫出每一個小函式，並把它們填進四張 **名字 → 函式指標** 的表（樣板裡是 `NULL`，換成你的函式名稱）：

| 表 | 名字與意思 |
|---|---|
| `MAPS` | `neg`：`-x`；`abs`：`|x|`；`half`：`x / 2`（C 的整數除法，向 0 取整）；`inc`：`x + 1`；`dec`：`x - 1`；`mod10`：`x % 10`（C 的 `%`，正負號跟 `x` 一樣） |
| `PREDS` | `even`、`odd`、`pos`（`> 0`）、`neg`（`< 0`）、`nonzero` |
| `FOLDS` | `sum`：總和；`count`：個數；`prodmod`：乘積除以 `1000000007` 的餘數（要是 0 ~ 1000000006） |
| `CMPS` | `asc`：由小到大；`desc`：由大到小；`absasc`：依絕對值由小到大，絕對值相同時負數在前 |

2. 寫出三個「接受函式指標」的通用函式：

| 函式 | 作用 |
|---|---|
| `void map_all(int *a, int n, MapFn f)` | 每個元素 `a[i] = f(a[i])` |
| `int filter_keep(int *a, int n, PredFn p)` | 只留下 `p(a[i])` 為真的元素（**保持原本順序**，就地往前搬），回傳新的長度 |
| `long long fold(const int *a, int n, long long init, FoldFn f)` | 從 `init` 開始，依序 `acc = f(acc, a[i])`，回傳最後的 `acc` |

`main` 處理的指令（查表、呼叫、輸出都寫好了）：

| 指令 | 動作 | 輸出 |
|---|---|---|
| `map 名字` | `map_all` | — |
| `filter 名字` | `filter_keep` | — |
| `reduce 名字` | `fold`，初值：`sum`、`count` 是 0，`prodmod` 是 1 | 結果 |
| `reduce max` / `reduce min` | `main` 自己算（不用查表） | 結果；空陣列輸出 `empty` |
| `sort 名字` | `qsort(a, n, sizeof(int), 比較函式)` | — |
| `print` | | 陣列；空的時候輸出 `empty` |

名字在表裡找不到時，`main` 輸出 `unknown 名字`。

## 輸入

第一行 `N`，第二行 `N` 個整數；第三行 `Q`，接下來 `Q` 行指令。

## 限制

- `1 ≤ N ≤ 10^4`，`1 ≤ Q ≤ 1000`，`|a[i]| ≤ 2 × 10^9`（`int` 放得下：`int` 最大約 `2.147 × 10^9`）
- 過程中所有元素的絕對值都 `≤ 2 × 10^9 + 1000`，不會讓 `int` 溢位；但 **兩個元素相減可能會溢位**

## 範例

輸入
```
5
3 -8 5 0 -2
8
map half
print
filter nonzero
reduce prodmod
sort absasc
print
map sqrt
reduce max
```
輸出
```
1 -4 2 0 -1
8
-1 1 2 -4
unknown sqrt
2
```

說明：
- `map half`：`3/2 = 1`、`-8/2 = -4`、`5/2 = 2`、`0/2 = 0`、`-2/2 = -1`（向 0 取整）。
- `filter nonzero` 之後剩下 `1 -4 2 -1`，乘積 `1 × (-4) × 2 × (-1) = 8`。
- `sort absasc`：絕對值 `1, 1, 2, 4`，`-1` 和 `1` 絕對值相同，負數在前。
- `sqrt` 不在表裡 → `unknown sqrt`。

## 提示

- 函式指標的宣告「看起來像函式宣告，只是名字外面加 `(*名字)`」。`typedef` 之後就可以像一般型別一樣用：`MapFn f = f_neg; int y = f(5);`
- 函式名稱本身就會轉成函式指標，填表時直接寫名字：`{"neg", f_neg}`。
- `prodmod`：C 的 `%` 對負數會得到負的餘數，要調整：`((long long)x % M + M) % M`。
- 比較函式不要寫 `return x - y;`：`x` 和 `y` 很大時相減會溢位。用 `(x > y) - (x < y)`。
- `filter_keep` 用「寫入位置」`w`：讀到要保留的就 `a[w++] = a[i]`。
