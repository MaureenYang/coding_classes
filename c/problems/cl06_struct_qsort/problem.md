# CL06. 學生成績排名 (struct + qsort + bsearch)

> 主題：`struct`、比較函式、`qsort`、`bsearch`　難度：★★☆　時間限制：1 秒　相關教學：`c/lessons/08_struct_union_enum.md`、`c/lessons/09_function_pointers.md`

## 題目

有 `N` 位學生，每位有名字、分數、年齡：

```c
typedef struct {
    char name[21];
    int score;
    int age;
    int rank;      /* 排名（1 開始），由 main 在排序後填入 */
} Student;
```

**第一部分：排名。** 依照下面的規則排序，輸出排名表：
1. 分數 **高** 的在前；
2. 分數相同，年齡 **小** 的在前；
3. 都相同，名字 **字典序小** 的在前（名字保證不重複）。

**第二部分：查詢。** 接著有 `Q` 個查詢，每個給一個名字，輸出那位學生的資料和排名。
查詢要用 **二分搜尋**（`bsearch`）：`main` 會先把陣列 **依名字排序**，再呼叫你寫的 `find_by_name`。

你要寫的三個函式：

| 函式 | 作用 |
|---|---|
| `int cmp_rank(const void *a, const void *b)` | 給 `qsort` 用：依照排名規則比較 |
| `int cmp_name(const void *a, const void *b)` | 給 `qsort` 用：依照名字比較 |
| `Student *find_by_name(Student *arr, int n, const char *name)` | 在「依名字排序過的」陣列中用 `bsearch` 找人；找不到回傳 `NULL` |

## 輸入

第一行 `N`，接下來 `N` 行 `name score age`。然後一行 `Q`，接下來 `Q` 行，每行一個名字。

## 輸出

先輸出 `N` 行排名表：`rank name score age`。
再對每個查詢輸出一行：`name score age rank`；找不到輸出 `name not found`。

## 限制

- `1 ≤ N ≤ 10^5`，`0 ≤ Q ≤ 10^5`
- 名字是 1 ~ 20 個小寫英文字母，學生的名字互不相同
- `0 ≤ score ≤ 100`，`1 ≤ age ≤ 150`

## 範例

輸入
```
4
amy 90 20
bob 95 22
cat 90 19
dan 90 19
3
cat
eve
bob
```
輸出
```
1 bob 95 22
2 cat 90 19
3 dan 90 19
4 amy 90 20
cat 90 19 2
eve not found
bob 95 22 1
```

## 提示

- `qsort` 會把 **兩個元素的位址** 傳給比較函式，型別是 `const void *`，要先轉回 `const Student *`：

```c
int cmp_rank(const void *a, const void *b) {
    const Student *x = a, *y = b;
    if (x->score != y->score) return y->score - x->score;   /* 分數高的在前 */
    ...
}
```

- 回傳值：負數表示 `a` 排在前面、正數表示 `b` 排在前面、0 表示一樣。
- `bsearch(key, base, n, size, cmp)` 會用 **同一個比較函式** 比較「`key`」和「陣列元素」。最簡單的做法：建一個暫時的 `Student`，只填 `name`，把它的位址當成 `key`，比較函式就能直接用 `cmp_name`。
- `bsearch` 回傳 `void *`（找不到是 `NULL`），轉成 `Student *` 回傳。
