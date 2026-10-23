# CL04. 動態陣列 (Dynamic Array with malloc / realloc)

> 主題：`malloc` / `realloc` / `free`、容量倍增、記憶體洩漏　難度：★★☆　時間限制：1 秒　相關教學：`c/lessons/07_dynamic_memory.md`

## 題目

C 沒有 `vector`，長度會變的陣列要自己用 `malloc` / `realloc` 管理。請完成 `IntVec`：

```c
typedef struct {
    int *data;     /* 指向 heap 上的陣列 */
    size_t size;   /* 目前有幾個元素 */
    size_t cap;    /* 目前配置的空間能放幾個 */
} IntVec;
```

| 函式 | 作用 |
|---|---|
| `void vec_init(IntVec *v)` | 變成空陣列：`data = NULL`、`size = cap = 0`（還不用配置記憶體） |
| `void vec_free(IntVec *v)` | 釋放記憶體，並把 `v` 變回空陣列 |
| `void vec_push(IntVec *v, int x)` | 加在最後面 |
| `int vec_pop(IntVec *v)` | 移除並回傳最後一個（`main` 保證不是空的） |
| `void vec_insert(IntVec *v, size_t pos, int x)` | 在位置 `pos` 插入，後面的元素往後移（`0 ≤ pos ≤ size`） |
| `int vec_erase(IntVec *v, size_t pos)` | 移除並回傳位置 `pos` 的元素，後面的元素往前移（`0 ≤ pos < size`） |

**容量規則**（`cap` 指令會檢查）：
- 空間不夠時（`size == cap` 又要加元素），新的容量是 `cap == 0 ? 1 : cap * 2`，用 `xrealloc` 擴大。
- 移除元素時 **不縮小** 容量。
- `vec_free` 之後容量變回 0。

**記憶體一律透過樣板提供的 `xmalloc` / `xrealloc` / `xfree`**（直接用 `malloc` 會編譯失敗），程式結束時會檢查有沒有洩漏。

`main` 處理的指令（索引從 0 開始，範圍不合法的指令由 `main` 輸出 `out of range`，不會呼叫你的函式）：

| 指令 | 輸出 |
|---|---|
| `push x` | — |
| `pop` | 被移除的值；空的時候輸出 `empty` |
| `get i` / `set i x` | `get` 輸出 `data[i]`；`set` 沒有輸出 |
| `insert i x` | — |
| `erase i` | 被移除的值 |
| `size` / `cap` | 目前的 `size` / `cap` |
| `print` | 所有元素（空白分隔）；空的時候輸出 `empty` |
| `clear` | 呼叫 `vec_free` 再 `vec_init` |

最後輸出 `leak check: ok`（有洩漏的話會輸出還沒釋放的區塊數）。

## 輸入

第一行 `Q`，接下來 `Q` 行指令。

## 限制

- `1 ≤ Q ≤ 10^5`，`|x| ≤ 10^9`，`i` 可能是負數或超出範圍
- `insert` 和 `erase` 合計最多 2000 次（每次 `O(n)`）

## 範例

輸入
```
11
cap
push 10
push 20
push 30
cap
insert 0 5
print
erase 2
get 7
pop
size
```
輸出
```
0
4
5 10 20 30
20
out of range
30
2
leak check: ok
```

## 提示

- `push` 和 `insert` 都需要「空間不夠就擴大」，寫一個輔助函式 `static void grow_if_full(IntVec *v)`。
- `xrealloc(NULL, n)` 等於 `xmalloc(n)`，所以第一次擴大也可以直接用 `xrealloc`。
- `realloc` 的大小單位是 **byte**：要放 `n` 個 `int` 是 `n * sizeof(int)`。
- 搬移元素可以用迴圈，也可以用 `<string.h>` 的 `memmove`（區域重疊時要用 `memmove`，不能用 `memcpy`）。
- 忘了在 `vec_free` 裡 `xfree`，最後的 leak check 就會失敗；`clear` 之後再 `push` 也要能正常運作。
