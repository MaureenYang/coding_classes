# CL10. 字串雜湊表 (Hash Map in C)

> 主題：用 C 實作 ADT、`struct` + 指標陣列、字串複製、擴容（rehash）、記憶體管理　難度：★★★★　時間限制：1 秒　相關教學：`c/lessons/12_data_structures_in_c.md`

## 題目

用 **分離鏈結法 (separate chaining)** 實作「字串 → 整數」的雜湊表：

```c
typedef struct Entry {
    char *key;               /* 自己複製一份（xmalloc），不能直接存呼叫者的指標 */
    long long val;
    struct Entry *next;      /* 同一個桶子裡的下一個 */
} Entry;

typedef struct {
    Entry **buckets;         /* 長度 nbuckets 的陣列，每個元素是一條串列的開頭 */
    size_t nbuckets;
    size_t size;             /* 目前有幾個 key */
} HashMap;
```

| 函式 | 作用 |
|---|---|
| `void hm_init(HashMap *m)` | 建立空的雜湊表，一開始 **8** 個桶子（全部是 `NULL`） |
| `void hm_free(HashMap *m)` | 釋放所有東西（每個 `Entry`、每個 `key`、桶子陣列） |
| `long long *hm_get(HashMap *m, const char *key)` | 找到的話回傳 **指向值的指標**（呼叫者可以透過它修改值）；找不到回傳 `NULL` |
| `void hm_put(HashMap *m, const char *key, long long val)` | 已存在就覆蓋，不存在就新增 |
| `int hm_del(HashMap *m, const char *key)` | 刪除；成功回傳 1，不存在回傳 0 |

雜湊函式已經提供（djb2）：`unsigned long hash_str(const char *s)`，桶子編號是 `hash_str(key) % nbuckets`。

**效能要求**：最多 `2 × 10^5` 個 key。如果桶子數一直是 8，每條串列會很長，一定會超時。
請在 `size > 2 × nbuckets`（平均每個桶子超過 2 個）時，把桶子數 **加倍** 並把所有 `Entry` 重新分配到新的桶子（rehash）。

`main` 處理的指令：

| 指令 | 動作 | 輸出 |
|---|---|---|
| `put k v` | `hm_put` | — |
| `get k` | `hm_get` | 值，或 `not found` |
| `add k d` | 存在就把值加上 `d`（透過 `hm_get` 回傳的指標），不存在就 `put k d` | — |
| `del k` | `hm_del` | `ok` 或 `not found` |
| `size` | | 目前的 key 數 |

最後輸出 `leak check: ok`。**記憶體一律用 `xmalloc` / `xfree`。**

## 輸入

第一行 `Q`，接下來 `Q` 行指令。

## 限制

- `1 ≤ Q ≤ 2 × 10^5`
- key 是 1 ~ 20 個小寫字母；`|v|, |d| ≤ 10^9`，值的絕對值永遠 `≤ 10^15`

## 範例

輸入
```
9
put apple 3
put pear 5
get apple
add apple 10
add kiwi 7
get apple
del pear
get pear
size
```
輸出
```
3
13
ok
not found
2
leak check: ok
```

## 提示

- 複製字串：`char *copy = xmalloc(strlen(key) + 1); strcpy(copy, key);`（`+ 1` 是結尾的 `'\0'`）。
- 比較字串要用 `strcmp(a, b) == 0`，**不能** 用 `a == b`（那是在比較兩個指標的位址）。
- 新節點插在桶子串列的 **最前面** 最簡單。
- rehash：配置新的桶子陣列，走過舊的每一個 `Entry`，用新的 `nbuckets` 算出位置後 **把節點本身搬過去**（改 `next` 指標就好，不用重新配置 `Entry` 或複製 `key`），最後釋放舊的桶子陣列。
- 刪除可以用 CL05 的 `Entry **pp` 技巧。刪除時 `key` 和 `Entry` 都要釋放。
