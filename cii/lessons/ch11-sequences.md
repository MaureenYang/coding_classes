# 第 11 章　Sequences（序列）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.171–181

---

## 1. 本章定位

**序列**存放 N 個值，對應整數索引 0 到 N−1；空序列沒有值。**值都是指標。**

- **像陣列**：可以用索引存取，而且是**常數時間**。
- **像雙端佇列**：可以從**兩端**加入或移除值。
- **自動擴大**：需要時會自己長大，容得下所有內容。

> 作者說：**序列是本書最有用的 ADT 之一。** 規格雖然簡單，卻可以當作**陣列、串列、堆疊、佇列、雙端佇列**來用，常常可以取代這些資料結構各自的 ADT。

**和 Array 的關係**：
> 序列可以看成第 10 章動態陣列**更抽象的版本**，它把**記帳和擴大大小的細節**藏在實作裡。

| | Array | Seq |
|---|---|---|
| 元素 | 任意大小的位元組 | **指標**（`void *`） |
| 大小 | 要手動 `Array_resize` | **自動擴大** |
| 兩端加入或移除 | 不支援 | **支援** |
| 抽象層次 | 低 | 高 |

---

## 2. 介面（11.1 Interface）

```c
/* seq.h */
#ifndef SEQ_INCLUDED
#define SEQ_INCLUDED

#define T Seq_T
typedef struct T *T;

extern T     Seq_new   (int hint);
extern T     Seq_seq   (void *x, ...);
extern void  Seq_free  (T *seq);
extern int   Seq_length(T seq);
extern void *Seq_get   (T seq, int i);
extern void *Seq_put   (T seq, int i, void *x);
extern void *Seq_addlo (T seq, void *x);
extern void *Seq_addhi (T seq, void *x);
extern void *Seq_remlo (T seq);
extern void *Seq_remhi (T seq);

#undef T
#endif
```

**通則**：傳 NULL 的 `T` 給任何函式都是 checked runtime error。

### 2.1 建立

- **`Seq_new(hint)`**：建立空序列。`hint` 是**預估的最大值數**；不知道就傳 0，會建立一個小序列。不管 hint 是多少，序列都會自動擴大。負數是 checked runtime error。
- **`Seq_seq(x, ...)`**：用非 NULL 的指標參數初始化，**以第一個 NULL 結束**。

```c
Seq_T names;
names = Seq_seq("C", "ML", "C++", "Icon", "AWK", NULL);   /* 索引 0..4 */
```

- 和 `List_list` 一樣：可變參數部分要是 `void *`，**傳 `char *` 和 `void *` 以外的指標要自己轉型**。
- 兩者都可能丟出 `Mem_Failed`。

### 2.2 釋放、長度、存取

| 函式 | 行為 |
|---|---|
| `Seq_free(&seq)` | 釋放並設成 NULL；`seq` 或 `*seq` 是 NULL 是 checked error |
| `Seq_length(seq)` | 值的個數 |
| `Seq_get(seq, i)` | 回傳第 i 個值 |
| `Seq_put(seq, i, x)` | 把第 i 個值換成 x，**回傳舊值** |

- `i` 不在 0 到 N−1 之間是 checked runtime error。
- **⭐ `Seq_get` 和 `Seq_put` 保證是常數時間**，這是寫在介面裡的效能承諾。
- `Seq_put` 能回傳舊值（不像 `Array_put`），因為值**一定是指標**。

### 2.3 兩端加入

| 函式 | 行為 | 對索引的影響 |
|---|---|---|
| `Seq_addlo(seq, x)` | 加到**低端**（開頭），回傳 x | **現有值的索引全部 +1**，長度 +1 |
| `Seq_addhi(seq, x)` | 加到**高端**（結尾），回傳 x | 長度 +1 |

兩者都可能丟出 `Mem_Failed`。

### 2.4 兩端移除

| 函式 | 行為 | 對索引的影響 |
|---|---|---|
| `Seq_remlo(seq)` | 移除並回傳低端的值 | **剩下的值索引全部 −1**，長度 −1 |
| `Seq_remhi(seq)` | 移除並回傳高端的值 | 長度 −1 |

對**空序列**呼叫這兩個函式是 checked runtime error。

### 2.5 一個 ADT，多種用法

```c
/* 堆疊（LIFO）*/
Seq_addhi(s, x);   x = Seq_remhi(s);

/* 佇列（FIFO）*/
Seq_addhi(q, x);   x = Seq_remlo(q);

/* 雙端佇列 */
Seq_addlo / Seq_addhi / Seq_remlo / Seq_remhi

/* 陣列 */
Seq_get(s, i);     Seq_put(s, i, x);
```

---

## 3. 實作（11.2 Implementation）

### 3.1 資料結構：內嵌 Array_T 的環狀緩衝區

```c
#include "array.h"
#include "arrayrep.h"     /* 需要知道 Array_T 的內部結構 */

#define T Seq_T

struct T {
    struct Array_T array;   /* 注意：是結構本身，不是指標！ */
    int length;             /* 序列中值的個數 */
    int head;               /* 第 0 個值在 array 中的位置 */
};
```

**⭐ 重點：**
- 序列是動態陣列的高層抽象，所以它的表示方式**包含一個動態陣列**：**不是 `Array_T` 指標，而是 `struct Array_T` 結構本身**。
- 因此實作**同時引用 `Array` 和 `ArrayRep`**。這正是第 10 章兩層介面的用途：`Seq` 是那種「需要知道表示方式」的 client。
- `array` 的元素數**至少**是 `length`，`length < array.length` 時有一些元素沒用到。

**環狀緩衝區（circular buffer）**：
- 序列的第 0 個值存在陣列的第 **`head`** 個元素。
- 後面的值依序存在後面的元素，**對陣列大小取模**：如果第 i 個值存在 `array.length-1`，第 i+1 個值就存在第 **0** 個元素。

```
一個 7 個值的序列，存在 16 個元素的陣列中（head = 12）：

 Seq_T                 array（16 個元素）
┌──────────────┐       索引: 0  1  2  3  4 ... 11 12 13 14 15
│ length  16   │ ← 內嵌的 Array_T
│ size     4   │            [s4][s5][s6][  ]...[  ][s0][s1][s2][s3]
│ array  ──────┼──→               ↑                 ↑
├──────────────┤             尾端繞回開頭          head=12
│ length   7   │
│ head    12   │
└──────────────┘
```

- **在開頭加入**：`head` 遞減（取模）；**從開頭移除**：`head` 遞增（取模）。
- 序列**就算是空的也一定有陣列**。

### 3.2 `Seq_new`

```c
T Seq_new(int hint) {
    T seq;
    assert(hint >= 0);
    NEW0(seq);                   /* length、head 都清成 0 */
    if (hint == 0)
        hint = 16;               /* 預設 16 個指標 */
    ArrayRep_init(&seq->array, hint, sizeof (void *),
        ALLOC(hint*sizeof (void *)));
    return seq;
}
```

用 `ArrayRep_init` 初始化**內嵌**的 `Array_T`，這正是第 10 章說這個函式存在的理由。

### 3.3 `Seq_seq`

```c
T Seq_seq(void *x, ...) {
    va_list ap;
    T seq = Seq_new(0);
    va_start(ap, x);
    for ( ; x; x = va_arg(ap, void *))
        Seq_addhi(seq, x);
    va_end(ap);
    return seq;
}
```

### 3.4 ⭐ `Seq_free`：靠結構布局的技巧

```c
void Seq_free(T *seq) {
    assert(seq && *seq);
    assert((void *)*seq == (void *)&(*seq)->array);
    Array_free((Array_T *)seq);
}
```

- 直接用 `Array_free` 釋放：它會釋放陣列的儲存空間和「描述子」，**而這裡的描述子剛好就是整個 `Seq_T` 結構**。
- **之所以可行，是因為 `*seq` 的位址等於 `&(*seq)->array`**，也就是 **`Array_T` 必須是 `Seq_T` 的第一個欄位**。這樣 `Seq_new` 裡 `NEW0` 回傳的指標**同時是** `Seq_T` 指標和 `Array_T` 指標。
- 用 `assert` 把這個假設**明確寫出來並檢查**。

> C 標準保證：結構第一個成員的位址就等於結構本身的位址。這是 C 裡「模擬繼承」的常見技巧。但這裡用 assert 守住它，以免日後有人調整欄位順序時不小心弄壞（習題 11.6 要你改寫成不需要這個假設的版本）。

### 3.5 存取：索引換算

```c
/* seq[i] */
((void **)seq->array.array)[(seq->head + i)%seq->array.length]
```

- 序列的第 i 個值存在 **`(head + i) mod array.length`**。
- `array.array` 是 `char *`，**轉型成 `void **`** 就能直接用索引存取指標。

```c
int Seq_length(T seq) {
    assert(seq);
    return seq->length;
}

void *Seq_get(T seq, int i) {
    assert(seq);
    assert(i >= 0 && i < seq->length);
    return /* seq[i] */;
}

void *Seq_put(T seq, int i, void *x) {
    void *prev;
    assert(seq);
    assert(i >= 0 && i < seq->length);
    prev = /* seq[i] */;
    /* seq[i] */ = x;
    return prev;
}
```

> 注意：實作**繞過 `Array_get`** 直接存取 `array.array`，用 `ArrayRep` 換取效率，也避免重複做邊界檢查。

### 3.6 移除

```c
void *Seq_remhi(T seq) {
    int i;
    assert(seq);
    assert(seq->length > 0);
    i = --seq->length;               /* 長度 −1，新長度就是被移除值的索引 */
    return /* seq[i] */;
}

void *Seq_remlo(T seq) {
    int i = 0;
    void *x;
    assert(seq);
    assert(seq->length > 0);
    x = /* seq[i] */;                 /* 取出索引 0 的值 */
    seq->head = (seq->head + 1)%seq->array.length;   /* head 往前 */
    --seq->length;
    return x;
}
```

- `Seq_remhi` 最簡單：長度減一就好。
- `Seq_remlo`：取出索引 0 的值，`head` 加一並取模。

### 3.7 加入

```c
void *Seq_addhi(T seq, void *x) {
    int i;
    assert(seq);
    if (seq->length == seq->array.length)     /* 滿了就擴大 */
        expand(seq);
    i = seq->length++;
    return /* seq[i] */ = x;
}

void *Seq_addlo(T seq, void *x) {
    int i = 0;
    assert(seq);
    if (seq->length == seq->array.length)
        expand(seq);
    if (--seq->head < 0)                       /* head 往回，必要時繞到尾端 */
        seq->head = seq->array.length - 1;
    seq->length++;
    return /* seq[i] */ = x;
}
```

- 陣列**滿了**（`length == array.length`）就呼叫 `expand`。
- `Seq_addlo` 遞減 `head` 時要處理負數，**明確檢查 `< 0`**，而不是依賴 `%` 對負數的行為（第 2 章說過 C 的 `%` 遇到負數時結果由實作決定）。
  - 另一種寫法是 `seq->head = Arith_mod(seq->head - 1, seq->array.length);`，這正是第 2 章 `Arith` 的用途。

### 3.8 ⭐ `expand`：擴大環狀緩衝區

```c
static void expand(T seq) {
    int n = seq->array.length;
    Array_resize(&seq->array, 2*n);        /* 大小加倍 */
    if (seq->head > 0) {
        /* slide tail down */
        void **old = &((void **)seq->array.array)[seq->head];
        memcpy(old+n, old, (n - seq->head)*sizeof (void *));
        seq->head += n;
    }
}
```

**為什麼要搬移？**
環狀緩衝區**繞回開頭**時，直接把陣列加倍會在**中間**產生一段空洞，值就不連續了。

```
擴大前（n = 8，head = 5，滿了）：
  [s3][s4][s5][s6][s7][s0][s1][s2]
                       ↑head=5

Array_resize 加倍後（中間的新空間在尾端）：
  [s3][s4][s5][s6][s7][s0][s1][s2][  ][  ][  ][  ][  ][  ][  ][  ]

把 head 之後的部分（s0..s2，共 n - head = 3 個）搬到尾端：
  [s3][s4][s5][s6][s7][??][??][??][  ][  ][  ][  ][  ][s0][s1][s2]
                                                       ↑head=5+8=13
```

- 如果 `head == 0`，值本來就是連續的，**不用搬移**。
- 否則把陣列尾端從 `head` 開始的元素，搬到擴大後陣列的**最尾端**（位移 n），把空間讓在**中間**，再把 `head` 加上 n。
- `memcpy` 的來源和目的地**不會重疊**：來源是 `[head, n)`，目的地是 `[head+n, 2n)`，因為 `head > 0`，兩段不相交。

**加倍策略**：每次擴大成兩倍，所以 `Seq_addhi`/`Seq_addlo` 的**攤銷時間是常數**。

---

## 4. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **一個 ADT 涵蓋多種用途** | 陣列、堆疊、佇列、雙端佇列都能用 Seq |
| **建立在 Array 之上** | 內嵌 `struct Array_T`，使用 `ArrayRep` 和 `ArrayRep_init` |
| **⭐ 兩層介面的實際用途** | Seq 就是那種「需要知道表示方式」的 client |
| **效能寫進介面** | `Seq_get`/`Seq_put` 保證常數時間 |
| **環狀緩衝區** | 兩端加入或移除都是 O(1)，用 `(head + i) % length` 索引 |
| **加倍擴大** | 攤銷常數時間；擴大時要處理繞回的部分 |
| **用 assert 守住布局假設** | `Seq_free` 依賴「第一個欄位」的布局 |
| **避免負數取模** | `Seq_addlo` 明確處理 `head < 0` |

### Seq vs. List

| | List（第 7 章） | Seq |
|---|---|---|
| 用索引存取 | O(N) | **O(1)** |
| 開頭加入 | O(1) | **O(1)**（攤銷） |
| 尾端加入 | O(N)（`List_append`） | **O(1)**（攤銷） |
| 表示方式 | 公開 | 隱藏 |
| 空間 | 每個值一個節點 | 連續陣列，可能有閒置空間 |

---

## 5. 延伸閱讀重點

- 序列**幾乎等同於 Icon 的 list**，但操作名稱取自 **DEC Modula-3** 函式庫的 Sequence 介面，實作方式也和 DEC 的版本類似。
- 習題 11.1 探討 Icon 的實作方式。

---

## 6. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 11.1 | 改用 Icon 的方式：**雙向串列，每個節點是一塊存 M 個值的區塊**，不用 `Array_resize` | 存取第 i 個值要 O(i/M)。如果存取 i 之後幾乎都是存取 i±1，能做到常數時間嗎？（記住上次的位置） |
| 11.2 | 不用 `Array_resize`：滿了就轉成「**指向陣列的指標陣列**」（edge vector），每個子陣列存 2N 個值 | N = 1024 時能存超過兩百萬個值，仍然是 O(1) 存取；子陣列可以延遲配置 |
| 11.3 | 禁止 `addlo`/`remlo` 的話，設計一個逐步配置空間、O(log N) 存取的實作 | 提示：**skip list**（Pugh, 1990） |
| 11.4 | 讓 `remlo`/`remhi` 在使用率低於一半時**縮小**陣列，什麼時候這是壞主意？ | 提示：**thrashing**，在邊界反覆加入和移除會一直擴大又縮小。（常見的解法是低於 1/4 才縮小） |
| 11.5 | 用序列取代集合重寫 `xref` 存行號 | 檔案是循序讀取的，行號本來就是遞增的，不用排序（但要自己避免同一行重複） |
| 11.6 | 改寫 `Seq_free`，讓它不再需要那個 assert | 不能用 `Array_free`，要自己分別釋放儲存空間和結構 |

---

## 7. 本章重點整理

1. **Seq = 自動擴大、兩端可以加入和移除、O(1) 索引存取的指標序列**，是本書最實用的 ADT 之一。
2. **介面**：`new`/`seq`/`free`/`length`/`get`/`put`/`addlo`/`addhi`/`remlo`/`remhi`。`addlo` 和 `remlo` 會讓其他值的索引整體移動。
3. **實作 = 內嵌 `struct Array_T` 的環狀緩衝區**：第 i 個值在 `(head + i) % array.length`。
4. **`Seq_free`** 依賴「`Array_T` 是第一個欄位」，用 assert 守住這個假設。
5. **`expand`** 把陣列加倍，並把 `head` 之後的部分搬到尾端，再調整 `head`。
6. **`Seq_addlo`** 明確處理 `head` 變成負數的情況，不依賴 `%` 對負數的行為。

> **一句話**：Seq 用一個會加倍長大的環狀緩衝區，同時做到陣列的常數時間索引和雙端佇列的常數時間兩端操作，而且它就建在 Array 和 ArrayRep 之上，是兩層介面設計的最佳示範。
