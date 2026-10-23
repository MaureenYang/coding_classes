# 第 13 章　Bit Vectors（位元向量）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.199–214

---

## 1. 本章定位

第 9 章的 Set 可以存放**任意**成員，因為成員只透過 client 提供的函式操作。但**整數集合**太常用了，值得一個專門的 ADT。

**`Bit` 介面**提供**位元向量**，可以表示 **0 到 N−1 的整數集合**。例如 256 位元的向量可以有效率地表示**字元集合**。

### 1.1 Bit vs. Set

| | Set（第 9 章） | Bit |
|---|---|---|
| 成員 | 任意指標 | **0 到 N−1 的整數** |
| 全集 | **沒有** | **有明確的全集 {0, …, N−1}** |
| 補集 | 不支援 | **支援**（`Bit_not`） |
| 子集比較 | 不支援 | **支援**（`Bit_lt`、`Bit_eq`、`Bit_leq`） |
| 空間 | 每個成員一個節點 | **每個可能的成員 1 個位元** |
| 集合運算 | 逐一成員雜湊查詢 | **整個 word 一次做位元運算** |

> 因為**有明確的全集**，Bit 可以提供 Set 做不到的功能，例如**補集**。這就是第 9 章提到的「固定小全集用位元向量」。

---

## 2. 介面（13.1 Interface）

```c
/* bit.h */
#ifndef BIT_INCLUDED
#define BIT_INCLUDED

#define T Bit_T
typedef struct T *T;

extern T    Bit_new   (int length);
extern int  Bit_length(T set);
extern int  Bit_count (T set);
extern void Bit_free  (T *set);

extern int  Bit_get   (T set, int n);
extern int  Bit_put   (T set, int n, int bit);

extern void Bit_clear (T set, int lo, int hi);
extern void Bit_set   (T set, int lo, int hi);
extern void Bit_not   (T set, int lo, int hi);

extern int  Bit_lt    (T s, T t);
extern int  Bit_eq    (T s, T t);
extern int  Bit_leq   (T s, T t);

extern void Bit_map   (T set, void apply(int n, int bit, void *cl), void *cl);

extern T    Bit_union (T s, T t);
extern T    Bit_inter (T s, T t);
extern T    Bit_minus (T s, T t);
extern T    Bit_diff  (T s, T t);

#undef T
#endif
```

雖然「位元向量」這個名字已經透露了表示方式，**介面還是只匯出不透明型別**。

**通則**：傳 NULL 的 `T` 給任何函式都是 checked runtime error，**集合運算的四個函式除外**。

### 2.1 建立與基本資訊

| 函式 | 行為 |
|---|---|
| `Bit_new(length)` | 建立 `length` 個位元的向量，**全部清成 0**，代表 0 到 length−1；**長度在建立時固定**。負數是 checked error；可能丟出 `Mem_Failed` |
| `Bit_length(set)` | 位元數（全集大小） |
| `Bit_count(set)` | **值為 1 的位元數**，也就是集合的基數 |
| `Bit_free(&set)` | 釋放並設成 NULL |

### 2.2 單一位元

| 函式 | 行為 |
|---|---|
| `Bit_get(set, n)` | 回傳第 n 個位元（**測試 n 是否在集合裡**），是 1 就回傳 1，否則回傳 0 |
| `Bit_put(set, n, bit)` | 把第 n 個位元設成 `bit`，**回傳舊值** |

n 不在 0 到 length−1 之間，或 `bit` 不是 0 或 1，都是 checked runtime error。

### 2.3 ⭐ 範圍操作（子集合）

| 函式 | 行為 |
|---|---|
| `Bit_clear(set, lo, hi)` | 把 lo 到 hi（**含兩端**）清成 0 |
| `Bit_set(set, lo, hi)` | 把 lo 到 hi 設成 1 |
| `Bit_not(set, lo, hi)` | 把 lo 到 hi **反轉** |

`lo > hi`，或 lo、hi 超出範圍，都是 checked runtime error。

> 補集就是 `Bit_not(set, 0, Bit_length(set) - 1)`。

### 2.4 比較

| 函式 | 意義 |
|---|---|
| `Bit_lt(s, t)` | s ⊂ t（**真子集**） |
| `Bit_eq(s, t)` | s = t |
| `Bit_leq(s, t)` | s ⊆ t（子集） |

s 和 t 的**長度不同**是 checked runtime error。

### 2.5 ⭐ `Bit_map`：允許修改

```c
extern void Bit_map(T set, void apply(int n, int bit, void *cl), void *cl);
```

- 從第 0 個位元開始，對每個位元呼叫 `apply(n, bit, cl)`。
- **和 `Table_map`、`Set_map` 不同：`apply` 可以修改集合！**
- 語意規定：如果處理第 n 個位元時，`apply` 改了第 k 個位元（k > n），**之後的呼叫會看到新值**。因為 `Bit_map` 必須**原地**處理位元，否則就得先複製整個向量。

> 為什麼 Bit 可以允許修改，而 Table、Set 不行？因為位元向量的結構是**固定的**，修改一個位元不會讓走訪出問題；而 Table 和 Set 增刪成員會改變串列結構，可能造成懸空指標。

### 2.6 集合運算

| 函式 | 運算 | 位元運算 |
|---|---|---|
| `Bit_union(s, t)` | s + t | **OR**（`\|`） |
| `Bit_inter(s, t)` | s ∗ t | **AND**（`&`） |
| `Bit_minus(s, t)` | s − t | **s AND NOT t**（`& ~`） |
| `Bit_diff(s, t)` | s / t | **XOR**（`^`） |

- 每個函式都**回傳新的集合**。
- **其中一個可以是 NULL**（當成空集合），**但不能兩個都是**，因為需要其中一個來決定結果的長度。
- 一定回傳非 NULL 的 `T`；`Bit_union(s, NULL)` 回傳 s 的複本。
- 兩個都是 NULL，或長度不同，是 checked runtime error；可能丟出 `Mem_Failed`。

---

## 3. 實作（13.2 Implementation）

### 3.1 ⭐ 雙重視圖：bytes 和 words

```c
#define T Bit_T

struct T {
    int length;              /* 位元數 */
    unsigned char *bytes;    /* 以位元組存取 */
    unsigned long *words;    /* 以 word 存取（指向同一塊記憶體）*/
};
```

- **`bytes` 和 `words` 指向同一塊記憶體**，只是用兩種方式看它。
- **`bytes[i]` 存第 8i 到 8i+7 個位元，第 8i 個位元是這個位元組的最低位。**
- 每個字元**只用 8 個位元**；在字元超過 8 位元的機器上，多出來的位元不使用。

**為什麼要兩種視圖？**

| 視圖 | 用途 |
|---|---|
| **`bytes`** | 單一位元和範圍操作。用**查表法**實作 `Bit_count`、`Bit_set`、`Bit_clear`、`Bit_not`（表格以位元組為單位，大小可控） |
| **`words`** | 集合運算和比較，**一次處理 BPW 個位元**（BPW = 每個 word 的位元數），速度快很多 |

```c
#define BPW (8*sizeof (unsigned long))     /* bits per word */

#define nwords(len) ((((len) + BPW - 1)&(~(BPW-1)))/BPW)   /* ⌈len / BPW⌉ */
#define nbytes(len) ((((len) + 8 - 1)&(~(8-1)))/8)         /* ⌈len / 8⌉  */
```

`nwords`、`nbytes` 都是**向上取整除法**：先加 (k−1)，再用位元遮罩把結果向下對齊到 k 的倍數（k 是 2 的冪），最後除以 k。

### 3.2 `Bit_new`

```c
T Bit_new(int length) {
    T set;
    assert(length >= 0);
    NEW(set);
    if (length > 0)
        set->words = CALLOC(nwords(length), sizeof (unsigned long));
    else
        set->words = NULL;
    set->bytes = (unsigned char *)set->words;   /* 同一塊記憶體 */
    set->length = length;
    return set;
}
```

- 以 **word 為單位**配置，所以最多會多出 `sizeof(unsigned long) − 1` 個位元組。
- **⚠ 這些多出來的位元組必須是 0**，後面的函式才能正確運作，所以用 `CALLOC`。（例如 `Bit_count` 和 `Bit_eq` 會一起掃到這些位元。）

```c
void Bit_free(T *set) {
    assert(set && *set);
    FREE((*set)->words);
    FREE(*set);
}

int Bit_length(T set) {
    assert(set);
    return set->length;
}
```

### 3.3 ⭐ `Bit_count`：半位元組查表

```c
int Bit_count(T set) {
    int length = 0, n;
    static char count[] = {
        0,1,1,2,1,2,2,3,1,2,2,3,2,3,3,4 };   /* 0x0..0xF 各有幾個 1 */
    assert(set);
    for (n = nbytes(set->length); --n >= 0; ) {
        unsigned char c = set->bytes[n];
        length += count[c&0xF] + count[c>>4];   /* 低 4 位 + 高 4 位 */
    }
    return length;
}
```

- 不逐一測試每個位元，而是把每個位元組拆成**兩個 4 位元的半位元組（nibble）**，當作索引去查一個 **16 個元素**的表。
- 可能會掃到多餘的位元，但因為 `Bit_new` 把它們清成 0，**不會影響結果**。

### 3.4 單一位元：`Bit_get`、`Bit_put`

**第 n 個位元 = 第 n/8 個位元組的第 n%8 位**（位元編號從右到左，最低位是第 0 位）。

```c
/* bit n in set */
((set->bytes[n/8]>>(n%8))&1)

int Bit_get(T set, int n) {
    assert(set);
    assert(0 <= n && n < set->length);
    return /* bit n in set */;
}

int Bit_put(T set, int n, int bit) {
    int prev;
    assert(set);
    assert(bit == 0 || bit == 1);
    assert(0 <= n && n < set->length);
    prev = /* bit n in set */;
    if (bit == 1)
        set->bytes[n/8] |=   1<<(n%8);     /* 設成 1：OR 一個只有該位為 1 的遮罩 */
    else
        set->bytes[n/8] &= ~(1<<(n%8));    /* 清成 0：AND 一個只有該位為 0 的遮罩 */
    return prev;
}
```

這是位元操作的三個基本慣用寫法：**取值**（右移後 `&1`）、**設值**（`|= mask`）、**清除**（`&= ~mask`）。

### 3.5 ⭐ 範圍操作：跨位元組邊界的三段處理

範圍可能**橫跨多個位元組**。例如 60 位元的集合執行 `Bit_set(set, 3, 54)`：

```
位元組:   7        6        5   4   3   2   1        0
       [0000····][·▓▓▓▓▓▓▓][▓▓▓▓▓▓▓▓]...[▓▓▓▓▓▓▓▓][▓▓▓▓▓···]
        未使用     ③ 低位       ② 整個位元組設成 1       ① 高位
                 bits 0-6                          bits 3-7
```

- **① 第一個位元組**（lo/8）：只設**高位**（第 lo%8 位到第 7 位）。
- **② 中間的位元組**：整個設成 `0xFF`。
- **③ 最後一個位元組**（hi/8）：只設**低位**（第 0 位到第 hi%8 位）。
- 第 7 個位元組的高 4 位沒有使用，永遠是 0。

**兩張遮罩表：**

```c
unsigned char msbmask[] = {          /* msbmask[k]：第 k 位到第 7 位為 1 */
    0xFF, 0xFE, 0xFC, 0xF8,
    0xF0, 0xE0, 0xC0, 0x80
};

unsigned char lsbmask[] = {          /* lsbmask[k]：第 0 位到第 k 位為 1 */
    0x01, 0x03, 0x07, 0x0F,
    0x1F, 0x3F, 0x7F, 0xFF
};
```

```c
void Bit_set(T set, int lo, int hi) {
    /* check set, lo, and hi */
    assert(set);
    assert(0 <= lo && hi < set->length);
    assert(lo <= hi);
    if (lo/8 < hi/8) {                          /* 跨多個位元組 */
        set->bytes[lo/8] |= msbmask[lo%8];      /* ① */
        {
            int i;
            for (i = lo/8+1; i < hi/8; i++)     /* ② */
                set->bytes[i] = 0xFF;
        }
        set->bytes[hi/8] |= lsbmask[hi%8];      /* ③ */
    } else                                      /* 在同一個位元組裡 */
        set->bytes[lo/8] |= (msbmask[lo%8]&lsbmask[hi%8]);
}
```

**同一個位元組的情況**：兩個遮罩做 **AND**，重疊的部分剛好就是要設的位元。
例如 `Bit_set(set, 9, 13)` 要設第 1 個位元組的第 1 到第 5 位：`msbmask[1] & lsbmask[5]` = `0xFE & 0x3F` = **`0x3E`**。

**`Bit_clear` 和 `Bit_not` 用同樣的結構，只是換了運算：**

```c
void Bit_clear(T set, int lo, int hi) {
    /* check set, lo, and hi */
    if (lo/8 < hi/8) {
        int i;
        set->bytes[lo/8] &= ~msbmask[lo%8];     /* AND 遮罩的補數 */
        for (i = lo/8+1; i < hi/8; i++)
            set->bytes[i] = 0;
        set->bytes[hi/8] &= ~lsbmask[hi%8];
    } else
        set->bytes[lo/8] &= ~(msbmask[lo%8]&lsbmask[hi%8]);
}

void Bit_not(T set, int lo, int hi) {
    /* check set, lo, and hi */
    if (lo/8 < hi/8) {
        int i;
        set->bytes[lo/8] ^= msbmask[lo%8];      /* XOR 反轉 */
        for (i = lo/8+1; i < hi/8; i++)
            set->bytes[i] ^= 0xFF;
        set->bytes[hi/8] ^= lsbmask[hi%8];
    } else
        set->bytes[lo/8] ^= (msbmask[lo%8]&lsbmask[hi%8]);
}
```

| 操作 | 位元運算 | 遮罩 |
|---|---|---|
| set | `\|=` | mask |
| clear | `&=` | `~mask` |
| not | `^=` | mask |

### 3.6 `Bit_map`：遵守介面，放棄最佳化

```c
void Bit_map(T set, void apply(int n, int bit, void *cl), void *cl) {
    int n;
    assert(set);
    for (n = 0; n < set->length; n++)
        apply(n, /* bit n in set */, cl);
}
```

> **很誘人的最佳化**：`n/8` 每 8 次才變一次，所以可以把 `bytes[n/8]` 先複製到暫存變數，再逐一位移取出位元。
> **但這違反介面**：介面規定 `apply` 修改了**還沒看到**的位元時，之後的呼叫要看到新值。用暫存變數的話，同一個位元組裡的修改就看不到了。

> **介面的語意優先於效能。** 這是一個很好的例子：寫進合約的承諾，會限制實作可以做的最佳化。

### 3.7 比較：以 word 為單位

```c
int Bit_eq(T s, T t) {
    int i;
    assert(s && t);
    assert(s->length == t->length);
    for (i = nwords(s->length); --i >= 0; )
        if (s->words[i] != t->words[i])
            return 0;                     /* 一旦不同就可以提早結束 */
    return 1;
}

int Bit_leq(T s, T t) {
    int i;
    assert(s && t);
    assert(s->length == t->length);
    for (i = nwords(s->length); --i >= 0; )
        if ((s->words[i]&~t->words[i]) != 0)   /* s 有、t 沒有的位元 */
            return 0;
    return 1;
}

int Bit_lt(T s, T t) {
    int i, lt = 0;
    assert(s && t);
    assert(s->length == t->length);
    for (i = nwords(s->length); --i >= 0; )
        if ((s->words[i]&~t->words[i]) != 0)
            return 0;                     /* 不是子集 */
        else if (s->words[i] != t->words[i])
            lt |= 1;                      /* 至少有一處不同 */
    return lt;
}
```

**集合論 → 位元運算：**
- **s ⊆ t** ⇔ s ∩ (t 的補集) = ∅ ⇔ **`s & ~t == 0`**。這個關係**對每個 word 也成立**，所以可以逐一 word 檢查，並且提早結束。
- **s ⊂ t** ⇔ s ⊆ t **而且** s ≠ t。

### 3.8 ⭐ 集合運算：用 `setop` 巨集統一寫法

四個集合運算只在三個地方不同：
1. s 和 t **是同一個集合**時的結果；
2. 怎麼處理 **NULL 參數**；
3. 兩個非空集合時用哪個**位元運算子**。

```c
#define setop(sequal, snull, tnull, op) \
    if (s == t) { assert(s); return sequal; } \
    else if (s == NULL) { assert(t); return snull; } \
    else if (t == NULL) return tnull; \
    else { \
        int i; T set; \
        assert(s->length == t->length); \
        set = Bit_new(s->length); \
        for (i = nwords(s->length); --i >= 0; ) \
            set->words[i] = s->words[i] op t->words[i]; \
        return set; }

static T copy(T t) {
    T set;
    assert(t);
    set = Bit_new(t->length);
    if (t->length > 0)
        memcpy(set->bytes, t->bytes, nbytes(t->length));
    return set;
}
```

```c
T Bit_union(T s, T t) { setop(copy(t),               copy(t),             copy(s),             |)   }
T Bit_inter(T s, T t) { setop(copy(t),               Bit_new(t->length),  Bit_new(s->length),  &)   }
T Bit_minus(T s, T t) { setop(Bit_new(s->length),    Bit_new(t->length),  copy(s),             & ~) }
T Bit_diff (T s, T t) { setop(Bit_new(s->length),    copy(t),             copy(s),             ^)   }
```

| 運算 | s == t | s 是 NULL | t 是 NULL | op |
|---|---|---|---|---|
| 聯集 | 複本 | t 的複本 | s 的複本 | `\|` |
| 交集 | 複本 | 空集合 | 空集合 | `&` |
| 差集 | **空集合** | 空集合 | s 的複本 | `& ~` |
| 對稱差 | **空集合** | t 的複本 | s 的複本 | `^` |

**巧妙之處**：
- 巨集參數 `op` 可以是 **`& ~`** 這種**兩個 token 的組合**，展開後變成 `s->words[i] & ~t->words[i]`。
- 「s 和 t 是同一個集合」**特別處理**，例如 s − s 直接回傳空集合。
- **以 word 為單位**運算，因為這些運算和位元的編號無關，可以平行處理。

---

## 4. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **特化帶來能力** | 有明確全集 → 有補集、子集比較 |
| **雙重視圖** | 同一塊記憶體用 bytes 做查表、用 words 做平行運算 |
| **查表法** | `count[16]`、`msbmask[8]`、`lsbmask[8]` |
| **多餘位元必須是 0** | `CALLOC` 加上不變式，讓整個 word 的運算正確 |
| **三段式範圍處理** | 頭（高位）、中間（整個位元組）、尾（低位）；同一個位元組時遮罩做 AND |
| **介面限制最佳化** | `Bit_map` 不能快取位元組，因為介面承諾看得到修改 |
| **集合論 → 位元運算** | ⊆ 就是 `s & ~t == 0` |
| **用巨集消除重複** | `setop` 用一個模板寫出四種運算 |
| **map 可以修改** | 結構固定，修改不會破壞走訪 |

---

## 5. 延伸閱讀重點

- **Briggs & Torczon (1993)**：專為**大型稀疏集合**設計的表示方式，可以在**常數時間**內初始化。
- **Gimpel (1974)**：**空間多工集合**（spatially multiplexed sets），見習題 13.5。

---

## 6. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 13.1 | 為**稀疏集合**（大部分是 0）節省空間，例如不儲存一長串的 0 | run-length 等壓縮表示 |
| 13.2 | 設計並實作 Briggs & Torczon 的稀疏集合介面 | 常數時間初始化的技巧 |
| 13.3 | `Bit_set`/`Bit_clear`/`Bit_not` 中間那段迴圈，盡量改成**以 word 為單位** | **注意對齊限制**；能找到量測得出改善的應用嗎？ |
| 13.4 | 讓 Bit 記住 1 的個數，哪些函式可以簡化或加速？ | `Bit_count` 變成 O(1)，代價是每次修改都要更新；什麼條件下值得？ |
| 13.5 | **空間多工集合**：N 個 32 位元 int 組成的陣列可以放 32 個 N 位元集合，每一行是一個集合，用只有第 i 位為 1 的遮罩辨識 | 有些運算可以只操作遮罩，例如聯集；但儲存空間管理複雜很多 |

---

## 7. 本章重點整理

1. **Bit = 固定全集 {0, …, N−1} 的整數集合**，每個可能的成員用 1 個位元表示。
2. **因為有全集**，所以能提供 Set 沒有的補集（`Bit_not`）和子集比較（`lt`/`eq`/`leq`）。
3. **介面**：單一位元（get/put）、範圍（clear/set/not，含兩端）、比較、map（**允許修改**）、集合運算（可以有一個 NULL）。
4. **實作的雙重視圖**：`bytes` 給位元操作和查表用，`words` 給平行的集合運算和比較用；多出來的位元必須是 0。
5. **`Bit_count`** 用 16 個元素的半位元組表查詢。
6. **範圍操作**分三段處理，用 `msbmask`/`lsbmask` 遮罩表；同一個位元組時兩個遮罩做 AND。
7. **`setop` 巨集**統一四種集合運算；`op` 可以是 `& ~`。
8. **`Bit_map` 不能做位元組快取的最佳化**，因為介面承諾 apply 看得到之後位元的修改。

> **一句話**：Bit 用「同一塊記憶體、兩種視圖」的手法，讓單一位元操作能查表、集合運算能一次處理一整個 word，而且因為有固定的全集，還能做補集和子集比較。
