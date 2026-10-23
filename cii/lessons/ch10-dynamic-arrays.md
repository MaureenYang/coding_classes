# 第 10 章　Dynamic Arrays（動態陣列）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.161–170

---

## 1. 本章定位

### 1.1 陣列的分類

**陣列**是一個**同質**的值序列，元素和一段**連續範圍**的索引一一對應。

| 類別 | 大小何時決定 | 範例 |
|---|---|---|
| **靜態陣列** | **編譯期** | `int a[n]`，n 必須是常數運算式；區域陣列雖然在執行期配置，但大小在編譯期就已知 |
| **動態陣列** | **執行期** | 用 `malloc` 等函式配置，例如 `Table_toArray` 回傳的陣列 |

- 有些語言（例如 Modula-3）在語言層級支援動態陣列，也允許每個陣列有自己的上下界。
- C 的陣列索引一律從 0 開始，而且動態陣列**必須自己建構**。

### 1.2 本章提供的兩個介面

前面各章的 `toArray` 函式已經顯示動態陣列有多好用。本章提供更一般的工具：

- **`Array`**：配置與釋放動態陣列、**有邊界檢查**的存取、**擴大或縮小**陣列。
- **`ArrayRep`**：**公開**動態陣列的表示方式，給**少數需要更有效率存取**的 client 使用。

### 1.3 ⭐ 兩層介面（layered interface）

> `Array` 規定 ADT 的**高層**視圖，`ArrayRep` 規定同一個 ADT **比較低層、比較詳細**的視圖。
>
> **好處：只要看 client 有沒有引用 `ArrayRep`，就能清楚知道它依賴表示方式。** 表示方式改變時只會影響這些 client，而不會影響數量可能多得多的、只用 `Array` 的 client。

這正是第 2 章 2.5 節說的：「需要效能時，**另外建一個新介面**並說明它的效能優勢，而**不是修改現有介面**。」

---

## 2. `Array` 介面（10.1）

```c
/* array.h */
#ifndef ARRAY_INCLUDED
#define ARRAY_INCLUDED

#define T Array_T
typedef struct T *T;

extern T     Array_new   (int length, int size);
extern void  Array_free  (T *array);
extern int   Array_length(T array);
extern int   Array_size  (T array);
extern void *Array_get   (T array, int i);
extern void *Array_put   (T array, int i, void *elem);
extern void  Array_resize(T array, int length);
extern T     Array_copy  (T array, int length);

#undef T
#endif
```

### 2.1 ⭐ 元素不限於指標

> 書中大多數 ADT 存的是 `void *`，**`Array` 對元素的值沒有限制**，每個元素就是 **`size` 個位元組**。
>
> **理由：`Array_T` 最常被用來建構其他 ADT**，例如第 11 章的 Sequence。

這是 `Array` 和 List、Table、Set 最大的不同：它可以直接存 `int`、`double`、結構等**任何固定大小的值**。

### 2.2 建立與釋放

- **`Array_new(length, size)`**：
  - 建立 `length` 個元素、索引 0 到 length−1 的陣列；`length` 是 0 時沒有元素。
  - 每個元素佔 `size` 位元組，**全部初始化成 0**。
  - `size` **必須包含對齊需要的填充**，這樣陣列才能用 `length × size` 位元組配置。（通常用 `sizeof` 取得，它本身就包含結構尾端的填充。）
  - `length` 是負數或 `size` 不是正數，都是 checked runtime error；可能丟出 `Mem_Failed`。
- **`Array_free(&array)`**：釋放並把 `*array` 設成 NULL。

### 2.3 存取

```c
int n = 42;
Array_T a = Array_new(100, sizeof (int));

Array_put(a, 5, &n);              /* 複製 n 的位元組到第 5 個元素 */
int x = *(int *)Array_get(a, 5);  /* 取得第 5 個元素的指標再解參考 */
```

| 函式 | 行為 |
|---|---|
| `Array_length(a)` | 元素數 |
| `Array_size(a)` | 每個元素的大小 |
| `Array_get(a, i)` | 回傳**第 i 個元素的指標**，等同於宣告陣列的 `&a[i]` |
| `Array_put(a, i, elem)` | 把 `elem` 指向的內容**複製**到第 i 個元素，**回傳 `elem`** |

**為什麼 `Array_put` 回傳 `elem`，而不像 `Table_put` 回傳舊值？**
> 因為元素**不一定是指標**，而且可以是任意長度，沒辦法用 `void *` 回傳「舊值」。

### 2.4 合約

| 類別 | 內容 |
|---|---|
| **Checked** | `i` 超出範圍（i < 0 或 i ≥ length）；`elem` 是 NULL；傳 NULL 的 `T` 給任何函式 |
| **Unchecked** | 呼叫 `Array_get` 之後、解參考之前用 `Array_resize` 改變大小，**指標會失效**，因為底層可能被搬移 |
| **Unchecked** | `elem` 指向的空間和第 i 個元素的空間**重疊**（因為用 `memcpy`） |

> 第一條和 C++ `std::vector` 的「重新配置後 iterator 失效」是同一個問題。

### 2.5 改變大小與複製

- **`Array_resize(a, length)`**：擴大或縮小到 `length` 個元素；**新增的元素初始化成 0**；**之前 `Array_get` 回傳的所有指標都會失效**。
- **`Array_copy(a, length)`**：回傳一個新陣列，內容是 a 的前 `length` 個元素；超過原長度的部分初始化成 0。
- 兩者都可能丟出 `Mem_Failed`。

### 2.6 為什麼沒有 `Array_map` 和 `Array_toArray`？

> 因為 **`Array_get` 已經提供了做同樣事情所需的機制**，直接用索引迴圈就可以了。

---

## 3. `ArrayRep` 介面

```c
/* arrayrep.h */
#ifndef ARRAYREP_INCLUDED
#define ARRAYREP_INCLUDED

#define T Array_T

struct T {
    int length;     /* 元素數 */
    int size;       /* 每個元素的大小 */
    char *array;    /* 實際的儲存空間 */
};

extern void ArrayRep_init(T array, int length, int size, void *ary);

#undef T
#endif
```

### 3.1 描述子（descriptor / dope vector）

`Array_T` 是指向一個**描述子**的指標。描述子的欄位記錄元素數、元素大小，以及指向儲存空間的指標。

```
Array_new(100, sizeof (int))，int 為 4 位元組：

  ┌─────────────┐
  │ length  100 │
  │ size      4 │        ┌────┬────┬─────┬────┐
  │ array   ────┼──────→ │ 0  │ 1  │ ... │ 99 │
  └─────────────┘        └────┴────┴─────┴────┘
```

- 沒有元素時，`array` 欄位是 NULL。
- 這種描述子有時候也叫做 **dope vector**。

### 3.2 使用規則

- client **可以讀**描述子的欄位，**不可以寫**，寫入是 unchecked runtime error。
- **保證**：若 `0 ≤ i < array->length`，則 `array->array + i*array->size` 就是第 i 個元素的位址。
  ⇒ 需要效能的 client 可以**直接計算位址**，省掉函式呼叫和邊界檢查。

### 3.3 `ArrayRep_init`

```c
extern void ArrayRep_init(T array, int length, int size, void *ary);
```

- 用來初始化 client **內嵌在其他結構裡**的 `Array_T`。
- **Checked runtime error**：`array` 是 NULL、`size` 不是正數、`length` 不是 0 但 `ary` 是 NULL、`length` 不是正數但 `ary` 不是 NULL。
- **用 `ArrayRep_init` 以外的方式初始化 `T` 結構，是 unchecked runtime error。**

---

## 4. 實作（10.2）

**一個實作同時匯出兩個介面**：

```c
/* array.c */
#include <stdlib.h>
#include <string.h>
#include "assert.h"
#include "array.h"
#include "arrayrep.h"
#include "mem.h"
#define T Array_T
```

### 4.1 `Array_new` 與 `ArrayRep_init`

```c
T Array_new(int length, int size) {
    T array;
    NEW(array);
    if (length > 0)
        ArrayRep_init(array, length, size, CALLOC(length, size));  /* 清成 0 */
    else
        ArrayRep_init(array, length, size, NULL);
    return array;
}

void ArrayRep_init(T array, int length, int size, void *ary) {
    assert(array);
    assert(ary && length>0 || length==0 && ary==NULL);
    assert(size > 0);
    array->length = length;
    array->size   = size;
    if (length > 0)
        array->array = ary;
    else
        array->array = NULL;
}
```

### 4.2 ⭐ 為什麼一定要用 `ArrayRep_init`？降低耦合

> 呼叫 `ArrayRep_init` 初始化 `T` 結構有助於**降低耦合**：
> - 這些呼叫**清楚標示出**哪些 client 自己配置描述子，因而依賴表示方式。
> - 只要 `ArrayRep_init` 的介面不變，**就可以加新欄位而不影響這些 client**。
>
> 例如以後在 `T` 結構加一個識別用的序號欄位，讓 `ArrayRep_init` 自動初始化它，client 完全不用改。

連「公開表示方式」的介面都在盡量保留演進的空間。

### 4.3 釋放、存取

```c
void Array_free(T *array) {
    assert(array && *array);
    FREE((*array)->array);       /* FREE 接受 NULL，不用另外檢查 */
    FREE(*array);
}

void *Array_get(T array, int i) {
    assert(array);
    assert(i >= 0 && i < array->length);         /* 邊界檢查 */
    return array->array + i*array->size;         /* char* 算術，以位元組為單位 */
}

void *Array_put(T array, int i, void *elem) {
    assert(array);
    assert(i >= 0 && i < array->length);
    assert(elem);
    memcpy(array->array + i*array->size, elem, array->size);
    return elem;                                  /* 回傳第三個參數，不是元素位址 */
}

int Array_length(T array) {
    assert(array);
    return array->length;
}

int Array_size(T array) {
    assert(array);
    return array->size;
}
```

**要點：**
- **`array` 欄位宣告成 `char *`**，所以指標算術是**以位元組為單位**，`i*size` 剛好就是第 i 個元素的位移。
- `Array_put` 用 `memcpy` 複製 `size` 個位元組，這也是「重疊是 unchecked error」的原因：`memcpy` 遇到重疊時行為未定義。

### 4.4 `Array_resize`

```c
void Array_resize(T array, int length) {
    assert(array);
    assert(length >= 0);
    if (length == 0)
        FREE(array->array);                        /* 變成空陣列 */
    else if (array->length == 0)
        array->array = ALLOC(length*array->size);  /* 從空陣列開始配置 */
    else
        RESIZE(array->array, length*array->size);  /* 一般情況 */
    array->length = length;
}
```

- **和 `Mem` 的 `RESIZE` 不同，新長度為 0 是合法的**：陣列空間被釋放，之後描述子描述的是一個空的動態陣列。
- 分三種情況，是因為 `Mem_resize` 不接受 NULL 指標和大小 0（第 5 章刻意這樣設計）。

> ⚠ 細心的讀者可能注意到：介面說擴大時「新元素初始化成 0」，但 `RESIZE` 和 `ALLOC` 並不會清零。這是書中規格和實作不一致的地方，自己實作時可以在擴大後補一個 `memset`。

### 4.5 `Array_copy`

```c
T Array_copy(T array, int length) {
    T copy;
    assert(array);
    assert(length >= 0);
    copy = Array_new(length, array->size);       /* 新陣列，已經清成 0 */
    if (copy->length >= array->length && array->length > 0)
        memcpy(copy->array, array->array, array->length*array->size);
    else if (array->length > copy->length && copy->length > 0)
        memcpy(copy->array, array->array, copy->length*array->size);
    return copy;
}
```

複製的位元組數取**兩者長度比較小**的那個；用 `Array_new`（底層是 `CALLOC`）配置，所以超出原長度的部分自然是 0。

---

## 5. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **⭐ 兩層介面** | `Array`（高層、安全）+ `ArrayRep`（低層、快速），從 include 就能看出誰依賴表示方式 |
| **需要效能就另開介面** | 不修改既有介面，而是新增 `ArrayRep` 並說明它的用途 |
| **元素是位元組，不是指標** | 讓 Array 能當其他 ADT 的建構基礎 |
| **邊界檢查** | `Array_get`/`Array_put` 都會 assert 索引 |
| **指標失效寫進合約** | resize 後之前 `get` 回傳的指標失效，明確列為 unchecked error |
| **用初始化函式保留演進空間** | `ArrayRep_init` 讓描述子以後可以加欄位 |
| **不做多餘的介面** | 有 `Array_get` 就不需要 map/toArray |
| **length 0 合法** | 空陣列是正常狀態，`array` 欄位是 NULL |

### Array 在全書中的角色

```
Array  ──建構──→  Seq（第 11 章：環狀緩衝區）
       ──建構──→  Text、其他需要可變長度緩衝區的模組
```

---

## 6. 延伸閱讀重點

- **Modula-3**：可以在執行期建立任意上下界的陣列，但**不能擴大或縮小**。
- **Icon 的 list**：像是可以從**兩端**加入或刪除元素的動態陣列，很像下一章的 Sequence；Icon 也支援取出子串列，以及用不同長度的串列替換子串列。

---

## 7. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 10.1 | 設計**指標**動態陣列的 ADT，提供類似 Table 的「安全」存取函式，用 `Array` 或 `ArrayRep` 實作 | 在通用的位元組陣列上包一層型別比較明確的介面 |
| 10.2 | 設計**二維動態矩陣** ADT，用 `Array` 實作；能推廣到 N 維嗎？ | 列優先的索引計算 |
| 10.3 | 設計**稀疏**動態陣列（大部分元素是「零」），零值由每個陣列自己指定，只儲存非零元素 | 可以考慮用 Table 存「索引 → 值」 |
| 10.4 | 加入 `Array_reshape(array, length, size)`：同時改變元素數和元素大小，元素截斷或補零 | 逐一元素搬移，注意搬移方向避免覆蓋 |

---

## 8. 本章重點整理

1. **動態陣列**：大小在執行期決定，C 必須自己建構。
2. **`Array`**：元素是固定大小的**位元組區塊**（不限指標），有邊界檢查，可以 resize 和 copy。
3. **存取**：`Array_get` 回傳元素的**指標**（像 `&a[i]`）；`Array_put` 用 `memcpy` 複製並回傳 `elem`。
4. **⚠ resize 之後，之前的 `Array_get` 指標會失效**（unchecked error）。
5. **`ArrayRep`** 公開 `struct { length, size, array }`，client 可以讀不能寫；第 i 個元素的位址保證是 `array + i*size`；只能用 `ArrayRep_init` 初始化。
6. **兩層介面**的價值：依賴表示方式的 client 一目了然，表示方式改變時影響範圍最小。
7. **實作**：`char *` 讓位址計算以位元組為單位；`Array_resize` 允許長度 0；`Array_copy` 複製兩者長度中比較小的部分。

> **一句話**：Array 提供一個安全、可以改變大小、元素型別不限的動態陣列，再用 ArrayRep 為少數需要速度的 client 開一扇「看得見內部」的門，這就是兩層介面設計的範例。
