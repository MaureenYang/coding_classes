# 第 12 章　Rings（環）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.183–197

---

## 1. 本章定位

**環（ring）**很像序列：存放 N 個值，對應整數索引 0 到 N−1；空環沒有值；**值都是指標**；也可以用索引存取。

**和序列不同的地方：**
1. **可以在任何位置加入值**，也**可以移除任何一個值**，不限於兩端。
2. **可以重新編號**：
   - **向左旋轉**：每個值的索引 −1（對環的長度取模）。
   - **向右旋轉**：每個值的索引 +1（對環的長度取模）。

**代價**：
> 換來「在任意位置加入或移除」的彈性，代價是**存取第 i 個值不再保證是常數時間**。

| | Seq（第 11 章） | Ring |
|---|---|---|
| 用索引存取 | **O(1)** | O(N)（最多走半圈） |
| 兩端加入或移除 | O(1)（攤銷） | **O(1)** |
| 任意位置加入或移除 | 不支援 | **支援**（找到位置要 O(N)，插入本身 O(1)） |
| 旋轉 | 不支援 | **支援** |
| 表示方式 | 環狀緩衝區 | **雙向環狀串列** |

> 這是第 2 章「效能也是合約的一部分」的再一次示範：Seq 和 Ring 的介面很像，但**效能承諾不同**，client 依需求選擇。

---

## 2. 介面（12.1 Interface）

```c
/* ring.h */
#ifndef RING_INCLUDED
#define RING_INCLUDED

#define T Ring_T
typedef struct T *T;

extern T     Ring_new   (void);
extern T     Ring_ring  (void *x, ...);
extern void  Ring_free  (T *ring);
extern int   Ring_length(T ring);
extern void *Ring_get   (T ring, int i);
extern void *Ring_put   (T ring, int i, void *x);
extern void *Ring_add   (T ring, int pos, void *x);
extern void *Ring_addlo (T ring, void *x);
extern void *Ring_addhi (T ring, void *x);
extern void *Ring_remove(T ring, int i);
extern void *Ring_remlo (T ring);
extern void *Ring_remhi (T ring);
extern void  Ring_rotate(T ring, int n);

#undef T
#endif
```

雖然名字暗示它是雙向串列的抽象，**介面只透露環是一個不透明指標型別**。傳 NULL 的 `T` 給任何函式都是 checked runtime error。

### 2.1 建立、釋放、存取（和 Seq 對應）

```c
Ring_T names;
names = Ring_ring("Lists", "Tables", "Sets", "Sequences", "Rings", NULL);
```

| 函式 | 行為 |
|---|---|
| `Ring_new()` | 建立空環（沒有 hint 參數，因為串列不需要預先配置） |
| `Ring_ring(x, ...)` | 用非 NULL 的指標參數初始化，以 NULL 結束；**非 `char *` / `void *` 的指標要轉型** |
| `Ring_free(&ring)` | 釋放並設成 NULL |
| `Ring_length(ring)` | 值的個數 |
| `Ring_get(ring, i)` | 回傳第 i 個值 |
| `Ring_put(ring, i, x)` | 換掉第 i 個值，回傳舊值 |

`i` 不在範圍內是 checked runtime error。`Ring_new`、`Ring_ring` 可能丟出 `Mem_Failed`。

### 2.2 ⭐ 位置（position）vs. 索引（index）

`Ring_add(ring, pos, x)` 用的是**位置**，而不是索引。**位置指的是值與值之間的間隙**：

```
一個 5 個元素的環，存放整數 0 到 4：

正位置：    1     2     3     4     5     6
            ↓     ↓     ↓     ↓     ↓     ↓
索引：         [0]   [1]   [2]   [3]   [4]
            ↑     ↑     ↑     ↑     ↑     ↑
非正位置： −5    −4    −3    −2    −1     0
```

- **中間那列**是索引，**上面**是正位置，**下面**是非正位置。
- **非正位置**從環的**尾端**算起，**不需要知道環的長度**。例如 0 永遠代表「最後面」。
- **空環**時，位置 0 和 1 也都合法。
- 指定**不存在的位置**是 checked runtime error，也就是正位置超過長度 + 1，或負位置的絕對值超過長度。
- 加入新值後，它**右邊**所有值的索引 +1，長度 +1。

> 這套位置表示法來自 **Icon** 語言。第 15 章的 `Str` 介面也會用同樣的表示法來表示字串位置。

### 2.3 兩端加入

| 函式 | 等同於 |
|---|---|
| `Ring_addlo(ring, x)` | `Ring_add(ring, 1, x)`：加到最前面 |
| `Ring_addhi(ring, x)` | `Ring_add(ring, 0, x)`：加到最後面 |

### 2.4 移除

| 函式 | 行為 | 等同於 |
|---|---|---|
| `Ring_remove(ring, i)` | 移除並回傳第 **i** 個值（這裡是**索引**），右邊的值索引 −1 | |
| `Ring_remlo(ring)` | 移除最前面的值 | `Ring_remove(ring, 0)` |
| `Ring_remhi(ring)` | 移除最後面的值 | `Ring_remove(ring, Ring_length(ring) - 1)` |

`i` 超出範圍，或對空環呼叫 `remlo`/`remhi`，都是 checked runtime error。

> 注意不對稱：**加入用「位置」**（值之間的間隙，有 N+1 個），**移除用「索引」**（值本身，有 N 個）。這很合理，因為插入的目標是一個間隙，而移除的目標是一個值。

### 2.5 ⭐ 旋轉：「環」這個名字的由來

```c
extern void Ring_rotate(T ring, int n);
```

- **n > 0**：向**右**（順時針）旋轉 n 個值，每個值的索引 +n（對長度取模）。
- **n < 0**：向**左**（逆時針）旋轉 |n| 個值，每個值的索引 −|n|（對長度取模）。
- n 對長度取模為 0 時沒有作用。
- |n| 超過環的長度是 checked runtime error。

```
8 個值 A..H 的環，向右旋轉 3（箭頭指向第一個元素）：

  旋轉前：          旋轉後：
     B  C              G  H
   A      D   →      F      A
   H      E          E      B
     G  F              D  C
  （A 是第 0 個）   （F 是第 0 個）
```

旋轉不搬動任何資料，只是**改變「誰是第 0 個」**。

---

## 3. 實作（12.2 Implementation）

### 3.1 資料結構：雙向環狀串列

```c
#define T Ring_T

struct T {
    struct node {
        struct node *llink, *rlink;   /* 左（前一個）、右（下一個）*/
        void *value;
    } *head;                          /* 指向索引 0 的節點 */
    int length;
};
```

- `head` 指向**索引 0** 的值；後面的值透過 **`rlink`** 依序連接（順時針），每個節點的 **`llink`** 指向前一個（逆時針）。
- **環狀**：最後一個節點的 `rlink` 指回 `head`，`head` 的 `llink` 指向最後一個節點。
  ⇒ **`head->llink` 就是最後一個值**，所以尾端操作是 O(1)。
- **空環**：`length == 0`，`head == NULL`。

```
6 個值的環：

         ┌──────────── rlink（順時針）────────────┐
         ↓                                          │
 head → [0] ⇄ [1] ⇄ [2] ⇄ [3] ⇄ [4] ⇄ [5] ──────────┘
         ↑                                    │
         └──────────── llink（逆時針）─────────┘
```

### 3.2 建立與釋放

```c
T Ring_new(void) {
    T ring;
    NEW0(ring);
    ring->head = NULL;
    return ring;
}

T Ring_ring(void *x, ...) {
    va_list ap;
    T ring = Ring_new();
    va_start(ap, x);
    for ( ; x; x = va_arg(ap, void *))
        Ring_addhi(ring, x);
    va_end(ap);
    return ring;
}

void Ring_free(T *ring) {
    struct node *p, *q;
    assert(ring && *ring);
    if ((p = (*ring)->head) != NULL) {
        int n = (*ring)->length;
        for ( ; n-- > 0; p = q) {      /* 用計數決定何時停，因為環沒有 NULL 結尾 */
            q = p->rlink;
            FREE(p);
        }
    }
    FREE(*ring);
}

int Ring_length(T ring) {
    assert(ring);
    return ring->length;
}
```

`Ring_free` 釋放節點的順序無所謂，所以就沿著 `rlink` 走。因為**環狀串列沒有 NULL 結尾**，所以用 `length` 計數決定什麼時候停（習題 12.1 要你改用串列結構本身判斷）。

### 3.3 ⭐ 找第 i 個節點：走最短的路

```c
/* q ← ith node */
{
    int n;
    q = ring->head;
    if (i <= ring->length/2)
        for (n = i; n-- > 0; )
            q = q->rlink;              /* 前半：順時針往右走 */
    else
        for (n = ring->length - i; n-- > 0; )
            q = q->llink;              /* 後半：逆時針往左走 */
}
```

- **雙向串列的好處**：i 不超過長度的一半就往右走，否則往左走。
- 例如 6 個值的環：索引 0 到 3 往右走，索引 4、5 往左走。
- 最多走 **N/2** 步。

```c
void *Ring_get(T ring, int i) {
    struct node *q;
    assert(ring);
    assert(i >= 0 && i < ring->length);
    /* q ← ith node */
    return q->value;
}

void *Ring_put(T ring, int i, void *x) {
    struct node *q;
    void *prev;
    assert(ring);
    assert(i >= 0 && i < ring->length);
    /* q ← ith node */
    prev = q->value;
    q->value = x;
    return prev;
}
```

### 3.4 加入：`Ring_addhi`

```c
void *Ring_addhi(T ring, void *x) {
    struct node *p, *q;
    assert(ring);
    NEW(p);
    if ((q = ring->head) != NULL)
        /* insert p to the left of q */
    else
        /* make p ring's only value */
    ring->length++;
    return p->value = x;
}
```

**空環**：新節點的兩個鏈結都指向自己。

```c
ring->head = p->llink = p->rlink = p;
```

**非空環**：插在 `head` 的**左邊**，也就是最後一個節點和 `head` 之間，就等於「加到最後面」。

```c
/* insert p to the left of q */
{
    p->llink = q->llink;      /* ① p 的左邊 = q 原本的左邊 */
    q->llink->rlink = p;      /* ② q 原本左邊那個節點的右邊 = p */
    p->rlink = q;             /* ③ p 的右邊 = q */
    q->llink = p;             /* ④ q 的左邊 = p */
}
```

```
插入前：   ... ⇄ [L] ⇄ [q] ⇄ ...
插入後：   ... ⇄ [L] ⇄ [p] ⇄ [q] ⇄ ...
```

**插入需要四次指標賦值。** 作者建議：自己畫一遍**只有一個節點**時的情況，會發現同樣的程式碼也是對的（這時 L 就是 q 自己）。

### 3.5 ⭐ `Ring_addlo`：用 addhi 加上旋轉

```c
void *Ring_addlo(T ring, void *x) {
    assert(ring);
    Ring_addhi(ring, x);
    ring->head = ring->head->llink;   /* 向右旋轉一格：head 改成它的前一個 */
    return x;
}
```

**巧妙之處**：環狀結構裡，「加到最後面」再把 `head` 往前移一格，**剛好就等於**「加到最前面」。不需要寫另一套插入邏輯。

### 3.6 `Ring_add`：任意位置

```c
void *Ring_add(T ring, int pos, void *x) {
    assert(ring);
    assert(pos >= -ring->length && pos <= ring->length+1);
    if (pos == 1 || pos == -ring->length)
        return Ring_addlo(ring, x);             /* 最前面 */
    else if (pos == 0 || pos == ring->length + 1)
        return Ring_addhi(ring, x);             /* 最後面 */
    else {
        struct node *p, *q;
        int i = pos < 0 ? pos + ring->length : pos - 1;   /* 位置 → 右邊那個值的索引 */
        /* q ← ith node */
        NEW(p);
        /* insert p to the left of q */
        ring->length++;
        return p->value = x;
    }
}
```

- **兩端交給 `addlo`/`addhi`**，順便處理掉**空環**的特殊情況。
- 其他位置：換算成**位置右邊那個值的索引** i，找到那個節點，把新節點插在它**左邊**。
  - 正位置 pos 右邊的值索引是 `pos - 1`。
  - 負位置 pos 右邊的值索引是 `pos + length`。

### 3.7 移除

**刪除只需要兩次指標賦值：**

```c
/* delete node q */
q->llink->rlink = q->rlink;   /* 左邊節點直接連到右邊 */
q->rlink->llink = q->llink;   /* 右邊節點直接連到左邊 */
FREE(q);
if (--ring->length == 0)
    ring->head = NULL;        /* 最後一個節點被刪掉了 */
```

```c
void *Ring_remove(T ring, int i) {
    void *x;
    struct node *q;
    assert(ring);
    assert(ring->length > 0);
    assert(i >= 0 && i < ring->length);
    /* q ← ith node */
    if (i == 0)
        ring->head = ring->head->rlink;     /* 刪除的是 head，先把 head 移到下一個 */
    x = q->value;
    /* delete node q */
    return x;
}

void *Ring_remhi(T ring) {
    void *x;
    struct node *q;
    assert(ring);
    assert(ring->length > 0);
    q = ring->head->llink;                  /* 最後一個 = head 的左邊，O(1) */
    x = q->value;
    /* delete node q */
    return x;
}

void *Ring_remlo(T ring) {
    assert(ring);
    assert(ring->length > 0);
    ring->head = ring->head->rlink;         /* 先向左旋轉一格 */
    return Ring_remhi(ring);                /* 原本的第一個現在變成最後一個 */
}
```

- 移除比加入簡單，因為邊界條件比較少，**唯一的特例是刪掉最後一個值**，這時要把 `head` 設成 NULL。
- **`Ring_remlo` 是 `Ring_addlo` 的對稱技巧**：先把 `head` 移到下一個，原本的第一個就變成最後一個，再呼叫 `Ring_remhi`。
- 作者建議：自己畫一遍從**一個節點**和**兩個節點**的串列刪除節點的過程。

### 3.8 `Ring_rotate`

```c
void Ring_rotate(T ring, int n) {
    struct node *q;
    int i;
    assert(ring);
    assert(n >= -ring->length && n <= ring->length);
    if (n >= 0)
        i = n%ring->length;
    else
        i = n + ring->length;       /* 刻意不用 n % length */
    /* q ← ith node */
    ring->head = q;
}
```

- **n ≥ 0**（順時針）：索引 `n mod N` 的值變成新的 head。
- **n < 0**（逆時針）：head 移到索引 `n + N` 的值。
- 用「找第 i 個節點」的區塊，所以**旋轉也會走最短的路**。
- **為什麼負數時寫 `n + ring->length` 而不是 `n % ring->length`？**（習題 12.2）
  因為 **C 的 `%` 遇到負數時，結果由實作決定**（第 2 章），可能得到負數，變成不合法的索引。介面限制了 |n| ≤ N，所以 `n + N` 一定落在 0 到 N 之間。（n = −N 時得到 0，等於沒有旋轉。）

> ⚠ 邊界情況：對**空環**呼叫 `Ring_rotate(ring, 0)`，assert 會通過，但接著會計算 `0 % 0`，**除以零**。自己實作時可以先檢查 `length == 0` 就直接返回。

---

## 4. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **相似的介面、不同的效能承諾** | Ring 和 Seq 的操作幾乎一樣，但取捨相反 |
| **位置 vs. 索引** | 插入用位置（間隙），移除用索引（值）；非正位置從尾端算起 |
| **雙向串列走最短路** | 依 i 在前半或後半選擇方向 |
| **環狀結構消除特例** | `head->llink` 就是尾端；`addlo` = `addhi` + 旋轉；`remlo` = 旋轉 + `remhi` |
| **重複使用程式碼** | 「找第 i 個節點」和「插在 q 左邊」兩個區塊被多個函式共用 |
| **旋轉不搬資料** | 只改 `head` 指標 |
| **避免負數取模** | `Ring_rotate` 用 `n + length` |
| **只有一個特例** | 加入時是空環，刪除時是刪掉最後一個節點 |

### 什麼時候用 Ring？

- 需要在**中間**插入或刪除。
- 需要**旋轉**（例如輪流排程、約瑟夫問題）。
- 需要用到「**目前位置附近**」的值（搭配習題 12.3 的快取）。
- 如果主要是**隨機存取**，應該選 **Seq**。

---

## 5. 延伸閱讀重點

- **Knuth (1973a)**、**Sedgewick (1990)**：詳細介紹雙向串列的演算法。
- **Icon** 的串列有些加入和移除操作和 Ring 類似；**`Ring_add` 的位置表示法也來自 Icon**。

---

## 6. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 12.1 | 改寫 `Ring_free` 的迴圈，去掉變數 n，改用串列結構判斷什麼時候結束 | 例如走到又回到 `head` 時停止，要小心先釋放再比較的問題 |
| 12.2 | 為什麼 `Ring_rotate` 負數的情況必須寫成 `i = n + ring->length`？ | **C 的 `%` 遇到負數時結果由實作決定** |
| 12.3 | `Ring_get(ring, i)` 後面常常緊接著 `Ring_get(ring, i + 1)`，讓環**記住最近存取的索引和節點**，盡量省掉迴圈 | 加入和移除時要更新快取；設計能量測出效益的測試 |
| 12.4 | 改用 Icon 的方式：**雙向串列，每個節點是一個環狀緩衝區陣列**（存 N 個值） | 找第 i 個值大約走 i/N 個陣列。比較複雜，但大環的效能比較好。環要多大才看得出改進？ |

---

## 7. 本章重點整理

1. **Ring = 可以在任意位置加入或移除、可以旋轉的指標序列**，代價是索引存取不再是 O(1)。
2. **位置表示法**：位置是值之間的間隙；正位置 1 到 N+1，非正位置 −N 到 0（從尾端算起）。插入用位置，移除用索引。
3. **實作 = 雙向環狀串列**，`head` 指向索引 0，`head->llink` 就是最後一個值。
4. **找第 i 個節點走最短的路**，最多 N/2 步。
5. **插入 4 次指標賦值，刪除 2 次**；特例只有空環和刪掉最後一個節點。
6. **巧妙的對稱**：`addlo` = `addhi` + head 往前；`remlo` = head 往後 + `remhi`。
7. **旋轉只改 `head`**；負數旋轉用 `n + length`，避免 `%` 對負數的實作相依行為。

> **一句話**：Ring 用雙向環狀串列換來「任意位置插入、刪除和旋轉」的彈性，並透過走最短的路和環狀結構的對稱性，讓實作既簡潔又只有很少的特例。
