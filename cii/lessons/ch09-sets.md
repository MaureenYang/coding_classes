# 第 9 章　Sets（集合）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.137–159

---

## 1. 本章定位

**集合**是一組**無序、不重複**的成員。

- **基本操作**：測試成員資格、加入成員、移除成員。
- **集合運算**（設 s、t 是兩個集合）：

| 運算 | 記號 | 意義 | `Set` 函式 |
|---|---|---|---|
| 聯集（union） | s + t | 在 s **或** t 裡 | `Set_union` |
| 交集（intersection） | s ∗ t | **同時**在 s 和 t 裡 | `Set_inter` |
| 差集（difference） | s − t | 在 s 裡、**不在** t 裡 | `Set_minus` |
| 對稱差（symmetric difference） | s / t | **只**在其中一個裡 | `Set_diff` |

- 集合通常相對於一個**全集（universe）** U 來描述，例如字元集合的全集是 256 個 8 位元字元碼，有了全集才能取**補集** U − s。
- **`Set` 不依賴全集**，所以沒有補集運算。（固定的小全集適合用第 13 章的位元向量。）

**和 Table 的關係**：
> `Set` 的設計**和 Table 一樣**：介面只操作成員，**從不直接檢查成員**，由 client 提供檢查成員屬性的函式。
> 事實上 **Set 就像 Table：成員是鍵，鍵對應的值被忽略。**

---

## 2. 介面（9.1 Interface）

```c
/* set.h */
#ifndef SET_INCLUDED
#define SET_INCLUDED

#define T Set_T
typedef struct T *T;

/* 1. 配置與釋放 */
extern T     Set_new (int hint,
                 int cmp(const void *x, const void *y),
                 unsigned hash(const void *x));
extern void  Set_free(T *set);

/* 2. 基本操作 */
extern int   Set_length(T set);
extern int   Set_member(T set, const void *member);
extern void  Set_put   (T set, const void *member);
extern void *Set_remove(T set, const void *member);

/* 3. 走訪 */
extern void   Set_map    (T set,
                  void apply(const void *member, void *cl), void *cl);
extern void **Set_toArray(T set, void *end);

/* 4. 集合運算（回傳新的集合）*/
extern T Set_union(T s, T t);
extern T Set_inter(T s, T t);
extern T Set_minus(T s, T t);
extern T Set_diff (T s, T t);

#undef T
#endif
```

函式分成**四組**，前三組和 Table 介面幾乎一樣。

### 2.1 配置與釋放

- **`Set_new(hint, cmp, hash)`**：意義和 `Table_new` 相同。
  - `cmp(x,y) == 0` 時，集合裡**只會出現 x 或 y 其中一個**，而且 `hash(x)` 必須等於 `hash(y)`。
  - `cmp` 或 `hash` 是 NULL 時，**假設成員是 atom**。
  - `hint` 只要不是負數都可以。
- **`Set_free(&set)`**：釋放並設成 NULL，**不釋放成員本身**（要釋放的話用 `Set_map`）。

### 2.2 基本操作

| 函式 | 行為 |
|---|---|
| `Set_length(s)` | 集合的**基數**（成員數） |
| `Set_member(s, m)` | m 在 s 裡就回傳 1，否則回傳 0 |
| `Set_put(s, m)` | 加入 m，已經在裡面就不重複加 |
| `Set_remove(s, m)` | 移除 m，回傳被移除的成員；不在裡面就回傳 NULL |

> **注意**：`Set_remove` 回傳的是**集合中那個成員**，它可能和傳入的 `member` **不是同一個指標**（兩者只是 `cmp` 相等）。這讓 client 可以拿回原本存進去的指標並釋放它。

### 2.3 走訪

```c
extern void Set_map(T set, void apply(const void *member, void *cl), void *cl);
```

- **和 `Table_map` 的關鍵差異**：傳給 `apply` 的是**成員本身**（`const void *`），**不是成員的指標**，所以 `apply` **不能替換**集合裡的指標。
  - 為什麼？集合成員的位置由它的雜湊值決定，如果允許替換成另一個值，集合結構就壞了。
- `apply` 呼叫 `Set_put`/`Set_remove` 修改集合是 checked runtime error（同樣用 timestamp）。
- **`Set_toArray(s, end)`**：N+1 個元素的陣列，順序任意，最後一個元素是 `end`；client 負責釋放。

### 2.4 集合運算

- 四個函式都**建立並回傳新的集合**，**不修改**參數（applicative）。
- **NULL 被當成空集合**，但一定**回傳新的非 NULL 集合**。例如 `Set_union(s, NULL)` 會回傳 s 的**複本**。
- **Checked runtime error**：
  - s 和 t **都是** NULL（沒辦法知道新集合該用哪個 `cmp`/`hash`）。
  - s 和 t 都不是 NULL 時，兩者的**比較函式或雜湊函式不同**。也就是說，兩個集合必須是用相同的 `cmp` 和 `hash` 建立的。

---

## 3. 範例：交叉參照表 `xref`（9.2）

### 3.1 功能

```
% xref xref.c getword.c
...
FILE    getword.c: 6
        xref.c: 18 43 72
...
c       getword.c: 7 8 9 10 11 16 19 22 27 34 35
        xref.c: 141 142 144 147 148
```

- 列出每個識別字出現在**哪些檔案的哪幾行**，可以用來找出某個識別字在原始碼裡的所有用法。
- **同一行出現多次只列一次**，所以行號天生就是一個**集合**。
- 檔案和行號都是排序過的。
- 沒有參數時讀標準輸入，並省略檔名。

### 3.2 ⭐ 資料結構：Table 套 Table 套 Set

```
identifiers  (Table_T：識別字 → 檔案表)
   │
   ├─ "FILE" ──→ (Table_T：檔名 → 行號集合)
   │               ├─ "getword.c" ──→ Set_T { →6 }
   │               └─ "xref.c"    ──→ Set_T { →18, →43, →72 }
   ├─ "c"    ──→ (Table_T) ...
   └─ ...
```

- **頂層**：一個 Table，鍵是識別字（atom），值是**第二層的 Table**。
- **第二層**：每個識別字一個 Table，鍵是檔名（atom），值是一個 **Set**。
- **第三層**：Set 存放**指向 int 的指標**，int 就是行號。

> 這個範例的重點：**示範 Set 和 Table 怎麼組合使用**，建出一個多層的資料結構。

### 3.3 先看怎麼印出來

作者建議：**先看內容怎麼印出來，再看結構怎麼建出來**，比較容易理解。印出的過程就是沿著資料結構逐層走下去，每一層各寫一個區塊或函式。

```c
/* 第一層：識別字排序後逐一處理 */
{
    int i;
    void **array = Table_toArray(identifiers, NULL);
    qsort(array, Table_length(identifiers), 2*sizeof (*array), compare);
    for (i = 0; array[i]; i += 2) {
        printf("%s", (char *)array[i]);
        print(array[i+1]);
    }
    FREE(array);
}

/* 第二層：檔名排序後逐一處理 */
void print(Table_T files) {
    int i;
    void **array = Table_toArray(files, NULL);
    qsort(array, Table_length(files), 2*sizeof (*array), compare);
    for (i = 0; array[i]; i += 2) {
        if (*(char *)array[i] != '\0')          /* 空字串的檔名不印 */
            printf("\t%s:", (char *)array[i]);
        {   /* 第三層：行號排序後印出 */
            int j;
            void **lines = Set_toArray(array[i+1], NULL);
            qsort(lines, Set_length(array[i+1]), sizeof (*lines), cmpint);
            for (j = 0; lines[j]; j++)
                printf(" %d", *(int *)lines[j]);
            FREE(lines);
        }
        printf("\n");
    }
    FREE(array);
}

int compare(const void *x, const void *y) {
    return strcmp(*(char **)x, *(char **)y);
}

int cmpint(const void *x, const void *y) {     /* 參數是 int ** */
    if (**(int **)x < **(int **)y)
        return -1;
    else if (**(int **)x > **(int **)y)
        return +1;
    else
        return 0;
}
```

**慣例**：沒有檔名參數時，每個第二層表只有一個項目，鍵是**長度為 0 的 atom**。`print` 用這一點判斷要不要印檔名。

### 3.4 建立結構

```c
int linenum;

int first(int c) {
    if (c == '\n')
        linenum++;          /* 順便計算行號 */
    return isalpha(c) || c == '_';
}
int rest(int c) {
    return isalpha(c) || c == '_' || isdigit(c);
}

void xref(const char *name, FILE *fp, Table_T identifiers) {
    char buf[128];
    if (name == NULL)
        name = "";
    name = Atom_string(name);
    linenum = 1;
    while (getword(fp, buf, sizeof buf, first, rest)) {
        Set_T set;
        Table_T files;
        const char *id = Atom_string(buf);

        /* files ← identifiers 中 id 對應的檔案表（沒有就建立）*/
        files = Table_get(identifiers, id);
        if (files == NULL) {
            files = Table_new(0, NULL, NULL);
            Table_put(identifiers, id, files);
        }
        /* set ← files 中 name 對應的集合（沒有就建立）*/
        set = Table_get(files, name);
        if (set == NULL) {
            set = Set_new(0, intcmp, inthash);
            Table_put(files, name, set);
        }
        /* 必要時把 linenum 加入 set */
        {
            int *p = &linenum;
            if (!Set_member(set, p)) {
                NEW(p);
                *p = linenum;
                Set_put(set, p);
            }
        }
    }
}
```

**要點：**
- 程式要能處理**缺少的部分**：識別字第一次出現時，就**當場**建立第二層表；在新檔案第一次出現時，就建立新的集合。
- **`first` 一邊判斷字元、一邊計算行號**：`getword` 會把每個字元都先交給 `first` 檢查，所以剛好可以藉機數換行。

### 3.5 整數集合的比較和雜湊

```c
int intcmp(const void *x, const void *y) {
    return cmpint(&x, &y);       /* 取位址後變成 int **，直接重複使用 cmpint */
}

unsigned inthash(const void *x) {
    return *(int *)x;            /* 整數本身就是雜湊值 */
}
```

- Set 的成員是指標，所以比較的是**指標指向的整數值**，而不是指標本身。這和 atom 不同。
- `intcmp` 收到的是 `int *`，取位址後變成 `int **`，就能直接重複使用 `cmpint`。

### 3.6 ⭐ 避免記憶體洩漏的細節

**直覺但錯誤的寫法：**

```c
int *p;
NEW(p);
*p = linenum;
Set_put(set, p);    /* 如果 set 已經有 linenum，p 不會被加入 → 洩漏！ */
```

**正確寫法**：先用 `&linenum` 測試成員資格，**不存在時才配置**。

```c
int *p = &linenum;
if (!Set_member(set, p)) {   /* 用 &linenum 當探針，不用配置 */
    NEW(p);
    *p = linenum;
    Set_put(set, p);
}
```

> 因為 `intcmp` 比較的是**值**，所以拿全域變數的位址當「探針」查詢就可以了。這是個很實用的小技巧。

---

## 4. 實作（9.3 Implementation）

和 Table 的實作**非常相似**：用雜湊表表示，用 `cmp`/`hash` 找成員。

### 4.1 資料結構

```c
struct T {
    int length;                                 /* 成員數 */
    unsigned timestamp;                         /* 給 Set_map 的 checked error 用 */
    int (*cmp)(const void *x, const void *y);
    unsigned (*hash)(const void *x);
    int size;                                   /* buckets 大小 */
    struct member {
        struct member *link;
        const void *member;
    } **buckets;
};
```

和 Table 唯一的結構差異是 `struct member` **沒有 value 欄位**。

### 4.2 `Set_new`

```c
T Set_new(int hint,
        int cmp(const void *x, const void *y),
        unsigned hash(const void *x)) {
    T set;
    int i;
    static int primes[] = { 509, 509, 1021, 2053, 4093,
        8191, 16381, 32771, 65521, INT_MAX };

    assert(hint >= 0);
    for (i = 1; primes[i] < hint; i++)
        ;
    set = ALLOC(sizeof (*set) + primes[i-1]*sizeof (set->buckets[0]));
    set->size = primes[i-1];
    set->cmp  = cmp  ? cmp  : cmpatom;
    set->hash = hash ? hash : hashatom;
    set->buckets = (struct member **)(set + 1);
    for (i = 0; i < set->size; i++)
        set->buckets[i] = NULL;
    set->length = 0;
    set->timestamp = 0;
    return set;
}

static int cmpatom(const void *x, const void *y) { return x != y; }
static unsigned hashatom(const void *x) { return (unsigned long)x>>2; }
```

和 `Table_new` 完全相同的寫法：用質數決定大小、一次配置、atom 預設函式。

### 4.3 成員操作

```c
/* search set for member */
i = (*set->hash)(member)%set->size;
for (p = set->buckets[i]; p; p = p->link)
    if ((*set->cmp)(member, p->member) == 0)
        break;

int Set_member(T set, const void *member) {
    int i;
    struct member *p;
    assert(set);
    assert(member);
    /* search set for member */
    return p != NULL;
}

void Set_put(T set, const void *member) {
    int i;
    struct member *p;
    assert(set);
    assert(member);
    /* search set for member */
    if (p == NULL) {
        NEW(p);                          /* add member to set */
        p->member = member;
        p->link = set->buckets[i];
        set->buckets[i] = p;
        set->length++;
    } else
        p->member = member;              /* 已存在：換成新的指標 */
    set->timestamp++;
}

void *Set_remove(T set, const void *member) {
    int i;
    struct member **pp;
    assert(set);
    assert(member);
    set->timestamp++;
    i = (*set->hash)(member)%set->size;
    for (pp = &set->buckets[i]; *pp; pp = &(*pp)->link)
        if ((*set->cmp)(member, (*pp)->member) == 0) {
            struct member *p = *pp;
            *pp = p->link;
            member = p->member;          /* 回傳集合中原本的那個指標 */
            FREE(p);
            set->length--;
            return (void *)member;
        }
    return NULL;
}
```

`Set_remove` 用的是和 `Table_remove` 一樣的**指標的指標**技巧。

### 4.4 `Set_free`、`Set_map`、`Set_toArray`

```c
void Set_map(T set, void apply(const void *member, void *cl), void *cl) {
    int i;
    unsigned stamp;
    struct member *p;
    assert(set);
    assert(apply);
    stamp = set->timestamp;
    for (i = 0; i < set->size; i++)
        for (p = set->buckets[i]; p; p = p->link) {
            apply(p->member, cl);              /* 傳成員本身，不是它的指標 */
            assert(set->timestamp == stamp);
        }
}

void **Set_toArray(T set, void *end) {
    int i, j = 0;
    void **array;
    struct member *p;
    assert(set);
    array = ALLOC((set->length + 1)*sizeof (*array));
    for (i = 0; i < set->size; i++)
        for (p = set->buckets[i]; p; p = p->link)
            array[j++] = (void *)p->member;
    array[j] = end;
    return array;
}
```

> **⚠ 細節**：`Set_map` 傳的是成員本身，所以 `apply` 不能替換集合裡的指標。但它**仍然可以透過轉型修改成員指向的內容**，這**可能改變集合的語意**（例如改變了雜湊值），所以要小心。

`Set_free` 的寫法和 `Table_free` 相同。

### 4.5 集合運算

**共用的走訪巨集區塊：**

```c
/* for each member q in t */
int i;
struct member *q;
for (i = 0; i < t->size; i++)
    for (q = t->buckets[i]; q; q = q->link)
```

**內部函式 `copy`：**

```c
static T copy(T t, int hint) {
    T set;
    assert(t);
    set = Set_new(hint, t->cmp, t->hash);
    {   /* for each member q in t */
        /* 直接加入，不呼叫 Set_put */
        struct member *p;
        const void *member = q->member;
        int i = (*set->hash)(member)%set->size;
        /* add member to set */
    }
    return set;
}
```

`copy` 知道複本裡**不可能有重複**，所以直接把成員加進去，**省掉 `Set_put` 那次沒有意義的搜尋**。

#### 聯集 s + t

```c
T Set_union(T s, T t) {
    if (s == NULL) {
        assert(t);
        return copy(t, t->size);
    } else if (t == NULL)
        return copy(s, s->size);
    else {
        T set = copy(s, Arith_max(s->size, t->size));
        assert(s->cmp == t->cmp && s->hash == t->hash);
        {   /* for each member q in t */
            Set_put(set, q->member);
        }
        return set;
    }
}
```

先複製 s，再把 t 的每個成員 `Set_put` 進去（重複的會自動略過）。hint 用**比較大**的那個表的大小，因為結果至少和比較大的參數一樣大。

#### 交集 s ∗ t

```c
T Set_inter(T s, T t) {
    if (s == NULL) {
        assert(t);
        return Set_new(t->size, t->cmp, t->hash);
    } else if (t == NULL)
        return Set_new(s->size, s->cmp, s->hash);
    else if (s->length < t->length)
        return Set_inter(t, s);              /* 交換，讓 t 成為比較小的那個 */
    else {
        T set = Set_new(Arith_min(s->size, t->size), s->cmp, s->hash);
        assert(s->cmp == t->cmp && s->hash == t->hash);
        {   /* for each member q in t */
            if (Set_member(s, q->member))
                /* add q->member to set */;
        }
        return set;
    }
}
```

**⭐ 遞迴交換**：如果 s 比較小，就交換參數再呼叫自己，讓迴圈**走訪比較小的集合**、到比較大的集合裡查詢。hint 用比較小的表的大小。

#### 差集 s − t

```c
T Set_minus(T t, T s) {        /* 注意：參數名稱刻意交換了！ */
    if (t == NULL) {
        assert(s);
        return Set_new(s->size, s->cmp, s->hash);
    } else if (s == NULL)
        return copy(t, t->size);
    else {
        T set = Set_new(Arith_min(s->size, t->size), s->cmp, s->hash);
        assert(s->cmp == t->cmp && s->hash == t->hash);
        {   /* for each member q in t */
            if (!Set_member(s, q->member))
                /* add q->member to set */;
        }
        return set;
    }
}
```

**小技巧**：把參數名稱交換（第一個參數叫 `t`），這樣就能重複使用「for each member q in t」區塊來走訪**第一個**集合。

#### 對稱差 s / t

```c
T Set_diff(T s, T t) {
    if (s == NULL) {
        assert(t);
        return copy(t, t->size);
    } else if (t == NULL)
        return copy(s, s->size);
    else {
        T set = Set_new(Arith_min(s->size, t->size), s->cmp, s->hash);
        assert(s->cmp == t->cmp && s->hash == t->hash);
        {   /* 第一輪：t 中不在 s 的 */
            if (!Set_member(s, q->member)) /* add */;
        }
        { T u = t; t = s; s = u; }          /* 交換 s、t */
        {   /* 第二輪：（原本的）s 中不在 t 的 */
            if (!Set_member(s, q->member)) /* add */;
        }
        return set;
    }
}
```

s / t = (s − t) + (t − s)。兩輪之間**交換 s 和 t**，同一個區塊就能用兩次。

> 這些運算還有更有效率的寫法（見習題）。其中一個重要的特例是兩個集合的雜湊表**大小相同**（習題 9.7）。

---

## 5. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **Set ≈ 沒有值的 Table** | 介面和實作幾乎一樣，可以互相實作（習題 9.1、9.2） |
| **不依賴全集** | 換來彈性，代價是沒有補集 |
| **`map` 不給指標** | 成員的位置由雜湊值決定，不允許替換 |
| **集合運算是 applicative 的** | 回傳新的集合；NULL 當成空集合；兩個都是 NULL 是錯誤 |
| **函式一致性檢查** | 兩個集合的 `cmp`/`hash` 必須相同，否則結果沒有意義 |
| **利用內部資訊最佳化** | `copy` 直接插入、hint 用適當的表大小、交集走訪比較小的集合 |
| **模組組合** | `xref` = Table × Table × Set + Atom + getword + Mem |
| **用值比較的探針** | 用 `&linenum` 查詢成員資格，避免先配置造成洩漏 |

---

## 6. 延伸閱讀重點

- Set 仿照 **Icon** 的集合設計，實作也和 Icon 類似。Icon 是少數把集合當內建型別的語言之一。
- **SETL**：以集合為核心資料型別，大部分運算子和控制結構都是為了操作集合而設計的。
- **位元向量**常用來表示**固定的小全集**的集合，見第 13 章。

---

## 7. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 9.1 | 用 Table 實作 Set | 值就忽略 |
| 9.2 | 用 Set 實作 Table | 成員是「鍵值對」結構，`cmp`/`hash` 只看鍵 |
| 9.3 | 設計第三個介面，抽出 Set 和 Table 的共同部分，再用它重新實作兩者 | 去除重複的程式碼 |
| 9.4 | 設計 **bag**（多重集合，例如 { 1 1 2 2 3 }）介面，用 9.3 的支援介面實作 | |
| 9.5 | `copy` 已經知道成員數，可以一次配置所有 member 結構 | 減少配置次數 |
| 9.6 | 在 member 結構裡存雜湊值，每個成員只算一次 hash，雜湊值相同時才呼叫 cmp | 分析預期的節省，值得才實作 |
| 9.7 | s、t 的 bucket 數**相同**時，各運算可以逐條雜湊鏈處理 | 很多應用每次都用同一個 hint，這種情況很常見 |
| 9.8 | 讓 `xref` 把連續行號印成範圍，例如 `7-11 16 19` | |
| 9.9 | 讓 `xref` 最後釋放所有配置的記憶體（atom 除外） | 用習題 5.5 的 `Mem_leak` 驗證 |
| 9.10 | 為什麼 `cmpint` 不寫成 `return **(int **)x - **(int **)y;`？ | **整數相減可能溢位**，例如很大的正數減很大的負數，結果的正負號就錯了 |

---

## 8. 本章重點整理

1. **Set = 無序、不重複的成員集合**；不依賴全集，所以沒有補集。
2. **介面分四組**：配置與釋放、基本操作（length/member/put/remove）、走訪（map/toArray）、集合運算（union/inter/minus/diff）。
3. **`Set_map` 傳成員本身而不是指標**，不能替換成員。
4. **集合運算回傳新的集合**；NULL 當成空集合；兩個都是 NULL，或 `cmp`/`hash` 不同，都是 checked runtime error。
5. **`xref` 範例**：Table（識別字）→ Table（檔名）→ Set（行號指標），逐層建立、逐層排序印出；用 `&linenum` 當探針避免洩漏。
6. **實作**：幾乎就是沒有值的 Table；集合運算利用 `copy`、適當的 hint、走訪比較小的集合、交換參數重複使用程式碼。
7. 比較函式要**避免用減法**，因為可能溢位。

> **一句話**：Set 本質上是「沒有值的 Table」，它的價值在於提供集合運算，以及和 Table 組合出像 `xref` 那樣多層的資料結構。
