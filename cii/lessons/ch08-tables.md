# 第 8 章　Tables（關聯表）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.115–135

---

## 1. 本章定位

**關聯表（associative table）**是一組**鍵值對（key-value pair）**的集合。它像陣列，只是**索引可以是任何型別的值**。

**應用無所不在：**
- **編譯器的符號表**：名稱 → 屬性集合。
- **視窗系統**：視窗標題 → 視窗資料結構。
- **排版系統的索引**：外層表的鍵是單字元字串（索引的各個段落），值是內層表；內層表的鍵是索引條目，值是頁碼串列。**表可以巢狀。**

**`Table` 的關鍵設計**：它**從不檢查鍵本身**，只透過 client 傳進來的函式（比較、雜湊）操作鍵。所以它能存放**任何型別**的鍵。

---

## 2. 介面（8.1 Interface）

```c
/* table.h */
#ifndef TABLE_INCLUDED
#define TABLE_INCLUDED

#define T Table_T
typedef struct T *T;

extern T     Table_new   (int hint,
                 int cmp(const void *x, const void *y),
                 unsigned hash(const void *key));
extern void  Table_free  (T *table);
extern int   Table_length(T table);
extern void *Table_put   (T table, const void *key, void *value);
extern void *Table_get   (T table, const void *key);
extern void *Table_remove(T table, const void *key);
extern void  Table_map   (T table,
                 void apply(const void *key, void **value, void *cl),
                 void *cl);
extern void **Table_toArray(T table, void *end);

#undef T
#endif
```

回到標準的**不透明指標** ADT。**通則**：傳 NULL 的 `Table_T` 或 NULL 的鍵給任何函式都是 checked runtime error。

### 2.1 `Table_new`：三個參數

| 參數 | 意義 |
|---|---|
| `hint` | **預估**的項目數。表的容量不受限制，但準確的 hint **可能提升效能**。負數是 checked runtime error |
| `cmp(x, y)` | 比較函式，回傳 `<0`、`0`、`>0`，代表 x 小於、等於、大於 y（例如 `strcmp`） |
| `hash(key)` | 雜湊函式。**必須滿足：`cmp(x,y) == 0` ⇒ `hash(x) == hash(y)`** |

- **每個表可以有自己的 `cmp` 和 `hash`。**
- **預設是 atom**：`hash` 是 NULL 時，假設鍵是 atom 並使用內建的雜湊函式；`cmp` 是 NULL 時，假設鍵是 atom，`x == y` 就相等。
- 可能丟出 `Mem_Failed`。

### 2.2 ⭐ 為多種實作留空間的代價

> `Table_new` 的三個參數提供的資訊，**比大多數實作需要的還多**：
> - 雜湊表實作只需要測試**相等**的比較函式。
> - **樹**實作不需要 `hint` 和 `hash`，但需要 `cmp` 的**大小順序**。
>
> **這種複雜度是允許多種實作所付出的代價，這也是設計好介面之所以困難的原因之一。**

這呼應第 2 章：介面要寫得夠一般，讓實作可以替換。所以 `cmp` 規定要回傳大小關係，而不只是相等與否。

### 2.3 基本操作

| 函式 | 行為 | 回傳 |
|---|---|---|
| `Table_length(t)` | 鍵值對數量 | 整數 |
| `Table_put(t, k, v)` | 鍵已存在就**覆蓋**值；否則新增一對 | 覆蓋時回傳**舊值**，新增時回傳 **NULL** |
| `Table_get(t, k)` | 查詢 | 找到就回傳值，沒找到回傳 **NULL** |
| `Table_remove(t, k)` | 刪除 | 回傳被刪除的值，沒找到回傳 NULL |
| `Table_free(&t)` | 釋放表並把 `*t` 設成 NULL | **不釋放鍵和值**（要用 `Table_map`） |

> **⚠ 歧義**：如果表裡存了 NULL 值，`Table_get` 回傳 NULL 時就**分不出**是「沒找到」還是「值剛好是 NULL」。介面直接寫明這一點。

### 2.4 走訪：`Table_map` 與 `Table_toArray`

```c
extern void Table_map(T table,
    void apply(const void *key, void **value, void *cl), void *cl);
```

- 對每個鍵值對呼叫 `apply(key, &value, cl)`，**順序不指定**。
- 傳的是 **value 的指標**，所以可以修改值；**key 是 `const`**，不能改。
- 常見用法：**釋放表之前先釋放值**。

```c
static void vfree(const void *key, void **value, void *cl) {
    FREE(*value);
}

Table_map(table, vfree, NULL);   /* 先釋放值（假設鍵是 atom，不用釋放） */
Table_free(&table);              /* 再釋放表 */
```

- **⭐ `apply` 呼叫 `Table_put` 或 `Table_remove` 修改表內容，是 checked runtime error。** 這是本章實作的亮點之一，見 4.4 節。

```c
extern void **Table_toArray(T table, void *end);
```

- 建立 **2N+1** 個元素的陣列：**鍵在偶數索引、值在下一個奇數索引**，最後索引 2N 是 `end`。
- 順序不指定；client 必須自己釋放陣列。

---

## 3. 範例：字頻統計 `wf`（8.2）

### 3.1 功能

```
% wf table.c mem.c
table.c:
3   apply
7   array
13  assert
...
mem.c:
1   allocation
7   assert
...
```

列出每個檔案裡每個單字出現的次數，**按字母順序**排列。單字是「一個字母，後面接零個或多個字母或底線」，不分大小寫。

### 3.2 通用的 `getword`

第 1 章 `double` 的 `getword` 被一般化，並**獨立成一個介面**，因為書中會反覆用到：

```c
/* getword.h */
#include <stdio.h>
extern int getword(FILE *fp, char *buf, int size,
    int first(int c), int rest(int c));
```

- 單字 = 一個讓 `first(c)` 為真的字元，後面接零個或多個讓 `rest(c)` 為真的字元。
- 字元的判斷交給**函式參數**，這又是用函式指標來參數化行為。

```c
int getword(FILE *fp, char *buf, int size,
        int first(int c), int rest(int c)) {
    int i = 0, c;
    assert(fp && buf && size > 1 && first && rest);
    c = getc(fp);
    for ( ; c != EOF; c = getc(fp))
        if (first(c)) {
            if (i < size - 1) buf[i++] = c;
            c = getc(fp);
            break;
        }
    for ( ; c != EOF && rest(c); c = getc(fp))
        if (i < size - 1) buf[i++] = c;
    if (i < size)
        buf[i] = '\0';
    else
        buf[size-1] = '\0';
    if (c != EOF)
        ungetc(c, fp);
    return i > 0;
}
```

比 `double` 的版本複雜一點，因為要處理「字元在 first 集合裡但不在 rest 集合裡」的情況：`first` 為真的那個字元存進去之後，**只有後面的字元**才交給 `rest` 判斷。

### 3.3 `wf` 主體

```c
int first(int c) { return isalpha(c); }
int rest (int c) { return isalpha(c) || c == '_'; }

void wf(char *name, FILE *fp) {
    Table_T table = Table_new(0, NULL, NULL);    /* 鍵是 atom，用預設函式 */
    char buf[128];

    while (getword(fp, buf, sizeof buf, first, rest)) {
        const char *word;
        int i, *count;
        for (i = 0; buf[i] != '\0'; i++)
            buf[i] = tolower(buf[i]);
        word = Atom_string(buf);                 /* 轉成 atom 當鍵 */
        count = Table_get(table, word);
        if (count)
            (*count)++;                           /* 注意：不是 *count++ */
        else {
            NEW(count);
            *count = 1;
            Table_put(table, word, count);
        }
    }
    if (name)
        printf("%s:\n", name);
    { /* print the words */ }
    Table_map(table, vfree, NULL);               /* 釋放計數器 */
    Table_free(&table);
}
```

**要點：**
- **鍵用 atom**，所以可以直接使用表的預設雜湊和比較函式。
- **值必須是指標**，但 `wf` 需要整數計數，所以**另外配置一個 `int`**，表裡存它的指標。
- **`(*count)++` 和 `*count++` 天差地別**：後者會遞增**指標**本身，而不是它指向的整數。
- **鍵不釋放**：atom 永遠不能被釋放，而且很可能會在後面的檔案再次出現。

### 3.4 排序輸出：把鍵值對當成一個元素

```c
int i;
void **array = Table_toArray(table, NULL);
qsort(array, Table_length(table), 2*sizeof (*array), compare);
for (i = 0; array[i]; i += 2)
    printf("%d\t%s\n", *(int *)array[i+1], (char *)array[i]);
FREE(array);

int compare(const void *x, const void *y) {
    return strcmp(*(char **)x, *(char **)y);
}
```

**巧妙之處**：告訴 `qsort` 有 **N 個元素、每個元素佔兩個指標的大小**，`qsort` 就會把**一對（鍵, 值）當成一個元素**來排序和搬移。比較函式收到的是指向「鍵值對」的指標，而第一個成員就是鍵（`char *`），所以用 `*(char **)x` 取出字串來比較。

---

## 4. 實作（8.3 Implementation）

### 4.1 資料結構

```c
struct T {
    int size;                                   /* buckets 的大小 */
    int (*cmp)(const void *x, const void *y);
    unsigned (*hash)(const void *key);
    int length;                                 /* 鍵值對數量 */
    unsigned timestamp;                         /* 修改次數 */
    struct binding {
        struct binding *link;
        const void *key;
        void *value;
    } **buckets;
};
```

- 用**雜湊表**表示，另一個顯而易見的選擇是樹（習題 8.2）。
- 每個 bucket 是一條 **binding 串列**，同一條串列上的鍵雜湊值相同。
- `cmp`、`hash` 屬於每個表，所以存在結構裡。

### 4.2 `Table_new`：用質數決定大小

```c
T Table_new(int hint,
        int cmp(const void *x, const void *y),
        unsigned hash(const void *key)) {
    T table;
    int i;
    static int primes[] = { 509, 509, 1021, 2053, 4093,
        8191, 16381, 32771, 65521, INT_MAX };

    assert(hint >= 0);
    for (i = 1; primes[i] < hint; i++)
        ;
    table = ALLOC(sizeof (*table) +
        primes[i-1]*sizeof (table->buckets[0]));
    table->size = primes[i-1];
    table->cmp  = cmp  ?  cmp  : cmpatom;
    table->hash = hash ?  hash : hashatom;
    table->buckets = (struct binding **)(table + 1);
    for (i = 0; i < table->size; i++)
        table->buckets[i] = NULL;
    table->length = 0;
    table->timestamp = 0;
    return table;
}
```

**要點：**
- 迴圈從 **索引 1** 開始，找到第一個 ≥ `hint` 的質數，然後用 `primes[i-1]`。陣列開頭重複放兩個 509，所以 `hint` 很小時也會選到 509。
- `primes` 是最接近 **2⁹ 到 2¹⁶** 的質數，涵蓋很大範圍的雜湊表大小。
- **一次 `ALLOC` 同時配置結構和 buckets 陣列**（和 Atom 同樣的技巧）。
- **⭐ 為什麼用質數，而 Atom 用 2 的冪？**
  > `Table` **無法控制**鍵的雜湊值怎麼計算，因為那是 client 的函式，品質可能不好。用質數當大小比較能分散不好的雜湊值。**Atom 自己計算雜湊值**，所以可以用比較簡單的做法。

### 4.3 atom 的預設函式

```c
static int cmpatom(const void *x, const void *y) {
    return x != y;
}

static unsigned hashatom(const void *key) {
    return (unsigned long)key>>2;
}
```

- **`cmpatom`**：相等時回傳 0，否則回傳 1。這個實作**只測相等**，不需要大小順序。
- **`hashatom`**：atom 就是一個位址，**位址本身就能當雜湊值**。右移 2 位是因為 atom 很可能從 word 邊界開始，最低兩位大概都是 0。

### 4.4 查詢、插入、計數

```c
/* search table for key */
i = (*table->hash)(key)%table->size;
for (p = table->buckets[i]; p; p = p->link)
    if ((*table->cmp)(key, p->key) == 0)
        break;

void *Table_get(T table, const void *key) {
    int i;
    struct binding *p;
    assert(table);
    assert(key);
    /* search table for key */
    return p ? p->value : NULL;
}

void *Table_put(T table, const void *key, void *value) {
    int i;
    struct binding *p;
    void *prev;
    assert(table);
    assert(key);
    /* search table for key */
    if (p == NULL) {                 /* 新鍵：加在串列前端 */
        NEW(p);
        p->key = key;
        p->link = table->buckets[i];
        table->buckets[i] = p;
        table->length++;
        prev = NULL;
    } else
        prev = p->value;             /* 舊鍵：記住舊值 */
    p->value = value;
    table->timestamp++;
    return prev;
}

int Table_length(T table) {
    assert(table);
    return table->length;
}
```

新的 binding 加在串列**前端**，這是最簡單也最有效率的做法。

### 4.5 ⭐ 用時間戳記實作「走訪時不可修改」

```c
void Table_map(T table,
        void apply(const void *key, void **value, void *cl),
        void *cl) {
    int i;
    unsigned stamp;
    struct binding *p;

    assert(table);
    assert(apply);
    stamp = table->timestamp;                 /* 進入時記下 */
    for (i = 0; i < table->size; i++)
        for (p = table->buckets[i]; p; p = p->link) {
            apply(p->key, &p->value, cl);
            assert(table->timestamp == stamp); /* 每次呼叫後檢查 */
        }
}
```

- `Table_put` 和 `Table_remove` 每次修改都會**遞增 `timestamp`**。
- `Table_map` 進入時存下 `stamp`，**每次呼叫 `apply` 之後都斷言**時間戳記沒變。
- 這樣就**低成本地**把「走訪時修改表」變成 checked runtime error，否則在走訪時刪除節點，`p->link` 可能會變成懸空指標。

> 這是「**把危險的誤用變成可偵測的錯誤**」的典型手法。現代語言的 iterator 失效檢查（例如 Java 的 `ConcurrentModificationException`）也是同樣的概念。

### 4.6 `Table_remove`：又是指標的指標

```c
void *Table_remove(T table, const void *key) {
    int i;
    struct binding **pp;

    assert(table);
    assert(key);
    table->timestamp++;
    i = (*table->hash)(key)%table->size;
    for (pp = &table->buckets[i]; *pp; pp = &(*pp)->link)
        if ((*table->cmp)(key, (*pp)->key) == 0) {
            struct binding *p = *pp;
            void *value = p->value;
            *pp = p->link;          /* 解除鏈結 */
            FREE(p);
            table->length--;
            return value;
        }
    return NULL;
}
```

`pp` 從 `&table->buckets[i]` 開始，之後指向前一個 binding 的 `link` 欄位。找到時 `*pp = p->link` 就能把節點解除鏈結，**不論它是不是第一個**。這和第 7 章 `List_append` 是同一個技巧。

### 4.7 `Table_toArray` 與 `Table_free`

```c
void **Table_toArray(T table, void *end) {
    int i, j = 0;
    void **array;
    struct binding *p;
    assert(table);
    array = ALLOC((2*table->length + 1)*sizeof (*array));
    for (i = 0; i < table->size; i++)
        for (p = table->buckets[i]; p; p = p->link) {
            array[j++] = (void *)p->key;    /* const void* → void* 需要轉型 */
            array[j++] = p->value;
        }
    array[j] = end;
    return array;
}

void Table_free(T *table) {
    assert(table && *table);
    if ((*table)->length > 0) {             /* 空表就不用走訪 */
        int i;
        struct binding *p, *q;
        for (i = 0; i < (*table)->size; i++)
            for (p = (*table)->buckets[i]; p; p = q) {
                q = p->link;
                FREE(p);
            }
    }
    FREE(*table);       /* buckets 和結構是一起配置的，一次釋放 */
}
```

---

## 5. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **鍵的型別無關** | Table 不檢查鍵，透過 client 提供的 `cmp`/`hash` 操作 |
| **合理的預設值** | `cmp`/`hash` 傳 NULL 就當作 atom，最常見的情況最簡單 |
| **為多種實作設計介面** | `cmp` 要回傳大小順序，讓樹實作也能用；`hint` 讓雜湊實作能調整大小 |
| **明確寫出歧義** | `Table_get` 回傳 NULL 的雙重意義 |
| **所有權** | 表不擁有鍵和值，client 用 `Table_map` 自己釋放 |
| **偵測走訪時的修改** | timestamp 加上 assert |
| **防禦不好的雜湊** | 無法控制雜湊函式時，表的大小用質數 |
| **指標的指標** | `Table_remove` 統一處理刪除首節點和中間節點 |
| **容器 + 標準演算法** | `Table_toArray` + `qsort`，並把「一對」當成一個元素 |
| **重複使用元件** | `getword` 獨立成介面；`wf` 結合 Atom、Table、Mem |

---

## 6. 延伸閱讀重點

- 很多語言把表做成內建型別：**AWK**（稱為 array，只能用字串和數字）、**SNOBOL4** 和它的後繼 **Icon**（鍵和值可以是任何型別）。Table 的實作用了 Icon 的部分技巧。
- **PostScript** 的 dictionary：只能用 name（PostScript 版的 atom）當鍵，值可以是任何型別。
- 物件導向語言：Smalltalk、Objective-C 的 dictionary，這類物件通常稱為**容器物件（container object）**。
- **負載因子（load factor）** = 項目數 ÷ bucket 數。Table 用**固定大小**的雜湊表，負載因子太高時效能會變差：
  - 簡單的做法：負載因子超過大約 5 時就擴大並重新雜湊所有項目（習題 8.5）。
  - **Larson (1988)** 的線性動態雜湊：**一次擴大或縮小一條雜湊鏈**，可以省掉 `hint`，所有表都能從小開始，因此節省空間。

---

## 7. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 8.1 | 討論其他設計：`Table_get` 回傳值的**指標**；`Table_put` 總是新增 binding、**遮蔽**舊的同名 binding 等 | 不同語意的優缺點，例如遮蔽式很適合巢狀作用域的符號表 |
| 8.2 | 用**二元搜尋樹**或**紅黑樹**重新實作 Table | 這就是 `cmp` 要回傳大小順序的原因 |
| 8.3 | 讓 `Table_map`/`Table_toArray` 依**插入順序**走訪 | 實用的好處（可預測、可重現） |
| 8.4 | 讓走訪依**排序順序**進行 | 會簡化 `wf` 這類 client；但 `Table_put`/`Table_get` 的平均時間會變成多少？ |
| 8.5 | 根據啟發式規則**動態調整 buckets 大小** | 設計測試程式量測效果 |
| 8.6 | 實作 Larson 的線性動態雜湊並比較 | |
| 8.7 | 量測 `wf` 因為 atom 永不釋放而浪費多少空間 | 第 3 章設計取捨的實際代價 |
| 8.8 | 讓 `wf` 依**計數遞減**排序 | 修改 `compare` 改看第二個成員 |
| 8.9 | 讓 `wf` 依**檔名字母順序**輸出 | |

---

## 8. 本章重點整理

1. **Table = 鍵值對的關聯表**，鍵可以是任何型別；Table 只透過 client 的 `cmp`/`hash` 操作鍵。
2. **`Table_new(hint, cmp, hash)`**：`cmp`/`hash` 傳 NULL 就代表鍵是 atom。參數比單一實作需要的多，**這是保留多種實作可能的代價**。
3. **操作**：`put` 回傳舊值或 NULL；`get` 和 `remove` 找不到時回傳 NULL（要注意存 NULL 值時的歧義）；`free` 不釋放鍵和值。
4. **走訪**：`Table_map` 閉包可以改值、不能改鍵；**走訪時修改表是 checked runtime error**（用 timestamp 實作）。
5. **`Table_toArray`**：鍵值交錯加上 `end` 哨兵；搭配 `qsort` 時把一對當成一個元素（`2*sizeof(void*)`）。
6. **`wf` 範例**：atom 當鍵、配置 `int` 當計數值、`(*count)++`、先用 `Table_map` 釋放值再 `Table_free`。
7. **實作**：雜湊表大小用**質數**（因為無法控制 client 的雜湊函式）；新 binding 插在串列前端；`Table_remove` 用指標的指標。

> **一句話**：Table 是一個「不關心鍵是什麼」的通用關聯表，用函式參數處理鍵、用 atom 當合理的預設值、用時間戳記抓出走訪時的誤用，是後面 Set 和 `xref` 範例的基礎。
