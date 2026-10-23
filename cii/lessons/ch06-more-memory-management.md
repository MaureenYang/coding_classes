# 第 6 章　More Memory Management（Arena：區域式記憶體配置）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.89–102

---

## 1. 本章定位

### 1.1 以「大小」為主 vs. 以「生命週期」為主

- 大多數 `malloc`/`free` 的實作（例如第 5 章的 first fit）是**以物件大小為基礎**的演算法。
- 但有些應用的釋放是**成批、同時發生**的：
  - **圖形介面**：建立視窗時配置捲軸、按鈕等空間，關閉視窗時一起釋放。
  - **編譯器**：lcc 編譯一個函式時配置記憶體，**編譯完就一次全部釋放**。
- 這類應用更適合**以物件生命週期為基礎**的演算法。
  - **堆疊式配置**是其中一種，但只適用於生命週期**巢狀**的情況，實務上往往不是如此。

### 1.2 Arena 的做法

**從一個 arena 配置記憶體，然後一次釋放整個 arena。**

| | `malloc` / `free` | Arena |
|---|---|---|
| 釋放的責任 | 每個 `malloc` 都要對應一個 `free` | **只需要一次呼叫**就能釋放 arena 裡所有東西 |
| 常見錯誤 | 忘記 free、重複 free、free 不該 free 的東西 | 大致都消失了 |
| 效率 | 一般 | 配置和釋放**都更快** |
| 洩漏 | 可能 | **沒有儲存空間洩漏** |

### 1.3 最重要的好處：**讓程式碼更簡單**

> Arena 配置器鼓勵使用簡單的 **applicative 演算法**：配置新的資料結構，而不是修改既有的結構。這取代了那些也許比較省空間、但**一定比較複雜**的演算法，因為那種演算法必須記得什麼時候要呼叫 `free`。

### 1.4 缺點

1. **可能用掉更多記憶體**，因為個別物件不能提早釋放。
2. **可能產生懸空指標**：物件配置在錯的 arena，而那個 arena 在程式用完物件之前就被釋放了。
3. 反過來，物件配置在一個比預期**更晚**才釋放的 arena，就會造成洩漏。

> 但實務上 arena 管理非常容易，這些問題**很少發生**。

---

## 2. 介面（6.1 Interface）

```c
/* arena.h */
#ifndef ARENA_INCLUDED
#define ARENA_INCLUDED
#include "except.h"

#define T Arena_T
typedef struct T *T;

extern const Except_T Arena_NewFailed;
extern const Except_T Arena_Failed;

extern T     Arena_new    (void);
extern void  Arena_dispose(T *ap);
extern void *Arena_alloc  (T arena, long nbytes,
                           const char *file, int line);
extern void *Arena_calloc (T arena, long count, long nbytes,
                           const char *file, int line);
extern void  Arena_free   (T arena);

#undef T
#endif
```

又一個標準的 ADT：不透明指標 `T`、`#define T` / `#undef T`、`_dispose(T *)`。

### 2.1 各函式語意

| 函式 | 功能 | 失敗時 |
|---|---|---|
| `Arena_new()` | 建立新的 arena，回傳不透明指標 | 丟出 `Arena_NewFailed` |
| `Arena_dispose(&ap)` | 釋放 arena 的所有記憶體、**arena 本身**，並把 `*ap` 設成 NULL | — |
| `Arena_alloc(arena, n, ...)` | 在 arena 裡配置至少 n 位元組，對齊到最嚴格的要求，**未初始化** | 丟出 `Arena_Failed` |
| `Arena_calloc(arena, count, n, ...)` | 配置 count × n 位元組，**清成 0** | 丟出 `Arena_Failed` |
| `Arena_free(arena)` | 釋放 arena 裡**自建立或上次 `Arena_free` 以來**配置的所有空間，但 arena 本身保留，可以繼續用 | — |

**注意 `Arena_free` 和 `Arena_dispose` 的差別**：
- `Arena_free`：清空內容，**arena 還能重複使用**。
- `Arena_dispose`：連 arena 本身都銷毀。

### 2.2 合約

- **Checked runtime error**：
  - 傳 NULL 的 `T` 給任何函式。
  - 傳 NULL 的 `ap` 或 `*ap` 給 `Arena_dispose`。
  - `count` 或 `nbytes` 不是正數。
- `file`/`line` 的處理和 `Mem` 一樣：例外會回報呼叫端的位置，`file` 是 NULL 時用實作內部的位置。
- 可以和 `Mem` 以及其他以 `malloc`/`free` 為基礎的配置器**混用**。

### 2.3 典型用法

```c
Arena_T arena = Arena_new();

for (each function to compile) {
    /* 編譯期間大量配置 */
    Node *n = Arena_alloc(arena, sizeof *n, __FILE__, __LINE__);
    ...
    Arena_free(arena);     /* 一次釋放這個函式用到的所有記憶體 */
}

Arena_dispose(&arena);
```

---

## 3. 實作（6.2 Implementation）

### 3.1 核心資料結構

```c
struct T {
    T prev;        /* 指向前一個 chunk 的開頭 */
    char *avail;   /* 目前 chunk 的第一個空閒位置 */
    char *limit;   /* 目前 chunk 結尾的下一個位置 */
};
```

一個 arena 描述**一塊 chunk**：
- `avail` 到 `limit` 之間是可以配置的空間。
- **配置 N 位元組**（N ≤ `limit - avail` 時）：把 `avail` 往前推 N，回傳原本的值。這**非常快**，就是一次指標加法。
- **不夠時**：用 `malloc` 要一塊新 chunk，把目前的 `*arena` **「推入」**（存在新 chunk 的開頭），再讓 arena 改成描述新 chunk。

結果，arena 結構就是一條 **chunk 鏈結串列的頭**，鏈結是每個 chunk 開頭那份 arena 結構複本裡的 `prev` 欄位：

```
 arena                chunk 3              chunk 2              chunk 1
┌───────┐          ┌───────────┐        ┌───────────┐        ┌───────────┐
│ prev ─┼────────→ │ prev     ─┼──────→ │ prev     ─┼──────→ │ prev=NULL │
│ avail─┼──┐       │ avail     │        │ avail     │        │ avail     │
│ limit─┼─┐│       │ limit     │        │ limit     │        │ limit     │
└───────┘ ││       ├───────────┤        ├───────────┤        ├───────────┤
          ││       │ ▓▓▓▓▓▓▓▓▓ │        │ ▓▓▓▓▓▓▓▓▓ │        │ ▓▓▓▓▓▓▓▓▓ │
          │└─────→ │ (free)    │        │ (wasted)  │        │ ▓▓▓▓▓▓▓▓▓ │
          └──────→ └───────────┘        └───────────┘        └───────────┘
```

（▓ = 已配置；chunk 大小可以不同，尾端可能有沒用到的空間。）

### 3.2 `Arena_new` / `Arena_dispose`

```c
T Arena_new(void) {
    T arena = malloc(sizeof (*arena));
    if (arena == NULL)
        RAISE(Arena_NewFailed);
    arena->prev = NULL;
    arena->limit = arena->avail = NULL;    /* 全部 NULL = 空的 arena */
    return arena;
}

void Arena_dispose(T *ap) {
    assert(ap && *ap);
    Arena_free(*ap);
    free(*ap);
    *ap = NULL;
}
```

> **設計決策**：`Arena` 直接用 `malloc`/`free`，**而不用 `Mem_alloc`/`Mem_free`**，這樣它就**不依賴其他配置器**。

### 3.3 `Arena_alloc`：極快的常見情況

```c
void *Arena_alloc(T arena, long nbytes, const char *file, int line) {
    assert(arena);
    assert(nbytes > 0);
    nbytes = ((nbytes + sizeof (union align) - 1)/
        (sizeof (union align)))*(sizeof (union align));   /* 對齊 */
    while (nbytes > arena->limit - arena->avail) {
        /* get a new chunk（見下）*/
    }
    arena->avail += nbytes;
    return arena->avail - nbytes;
}
```

- 大多數呼叫時，目前的 chunk 空間足夠，**`while` 的主體根本不會執行**，整個配置就是「取整、比較、加法」。
- 空閒的 arena（全部是 NULL）時 `limit - avail == 0`，第一次配置自然就會去要 chunk。
- `union align` 和第 5 章相同，用來取得最嚴格的對齊。

### 3.4 取得新 chunk

```c
union header {
    struct T b;
    union align a;
};

/* get a new chunk */
T ptr;
char *limit;
/* ptr ← a new chunk（見下）*/
*ptr = *arena;                                         /* 把目前狀態推入新 chunk 開頭 */
arena->avail = (char *)((union header *)ptr + 1);     /* 跳過 header，而且已經對齊 */
arena->limit = limit;
arena->prev  = ptr;
```

- **`*ptr = *arena`**：用**結構賦值**把目前的 arena 狀態整個存進新 chunk 的開頭，這就是「推入」。
- **`union header`**：把 `struct T` 和 `union align` 放在一起，大小一定是對齊單位的倍數，所以 `(union header *)ptr + 1` 得到的第一個可配置位址**保證是對齊的**。
- 換新 chunk 時，**舊 chunk 尾端剩下的空間就浪費了**（上圖的 chunk 2）。

### 3.5 空閒 chunk 串列：重複使用

```c
static T freechunks;    /* 所有 arena 共用的空閒 chunk 串列 */
static int nfree;       /* 串列上的 chunk 數 */

/* ptr ← a new chunk */
if ((ptr = freechunks) != NULL) {          /* 優先重複使用 */
    freechunks = freechunks->prev;
    nfree--;
    limit = ptr->limit;
} else {                                    /* 否則向 malloc 要 */
    long m = sizeof (union header) + nbytes + 10*1024;
    ptr = malloc(m);
    if (ptr == NULL) {
        if (file == NULL)
            RAISE(Arena_Failed);
        else
            Except_raise(&Arena_Failed, file, line);
    }
    limit = (char *)ptr + m;
}
```

- 新 chunk 的大小 = header + 這次的請求 + **額外 10 KB**，讓後續的配置不用一直要新 chunk。
- 空閒串列透過 chunk 開頭 arena 結構的 `prev` 串起來，`limit` 記錄 chunk 的結尾。
- **為什麼是 `while` 不是 `if`？** 從 `freechunks` 拿到的 chunk **可能太小**，裝不下這次的請求，所以要再試一次。

### 3.6 `Arena_calloc`

```c
void *Arena_calloc(T arena, long count, long nbytes,
        const char *file, int line) {
    void *ptr;
    assert(count > 0);
    ptr = Arena_alloc(arena, count*nbytes, file, line);
    memset(ptr, '\0', count*nbytes);
    return ptr;
}
```

### 3.7 `Arena_free`：彈出所有 chunk

```c
#define THRESHOLD 10

void Arena_free(T arena) {
    assert(arena);
    while (arena->prev) {
        struct T tmp = *arena->prev;      /* 取出前一個狀態 */
        /* free the chunk described by arena */
        if (nfree < THRESHOLD) {
            arena->prev->prev = freechunks;      /* 放回空閒串列 */
            freechunks = arena->prev;
            nfree++;
            freechunks->limit = arena->limit;
        } else
            free(arena->prev);                   /* 太多了就真的 free */
        *arena = tmp;                     /* 「彈出」 */
    }
    assert(arena->limit == NULL);          /* 回到初始的空狀態 */
    assert(arena->avail == NULL);
}
```

**要點：**
- `tmp = *arena->prev` 加上 `*arena = tmp` 就是從 chunk 堆疊**彈出**一層。走完整條串列後，arena 回到**全部 NULL 的初始狀態**，最後兩個 `assert` 驗證這件事。
- **`THRESHOLD` 限制空閒串列的長度**：
  - `freechunks` 收集**所有 arena** 的空閒 chunk，可能變得很大。
  - 串列長度本身不是問題，但它佔住的記憶體在其他配置器看來是「已配置」，**可能導致其他地方的 `malloc` 失敗**。
  - 所以最多保留 10 個，超過就呼叫 `free`。每個 chunk 至少 10 KB，空閒串列大約最多佔 100 KB。

---

## 4. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **依應用特性選演算法** | 生命週期成批結束 → 用 arena，而不是逐一 free |
| **讓常見情況極快** | 配置通常只是「取整 + 比較 + 指標加法」 |
| **以結構賦值實作堆疊** | `*ptr = *arena` 推入，`*arena = tmp` 彈出；chunk 本身就是堆疊節點 |
| **用 union 解決對齊** | `union align`、`union header` |
| **模組獨立** | 不依賴 `Mem`，直接用 `malloc`/`free` |
| **資源上限** | 用 `THRESHOLD` 避免空閒串列佔住太多記憶體 |
| **簡化 client 程式碼** | 不用追蹤每個物件的釋放時機，可以放心使用 applicative 演算法 |

### Arena vs. Mem vs. 垃圾回收

```
Mem（malloc/free）  ──→  每個物件都要明確釋放
Arena               ──→  很多個釋放合併成一個
垃圾回收（GC）       ──→  完全不用明確釋放
```

---

## 5. 延伸閱讀重點

- Arena 配置器也叫做 **pool allocator**。
- 本章的配置器（Hanson, 1990）原本是為 **lcc** 開發的。lcc 的版本更簡單：arena 是靜態配置的，釋放時不呼叫 `free`；早期版本的配置甚至用**巨集直接操作 arena 結構**，只有需要新 chunk 時才呼叫函式。
- **Barrett & Zorn (1993)**：自動選擇適當的 arena。實驗顯示，**到達配置點的執行路徑**（呼叫鏈加上配置點位址）能很好地預測該區塊的生命週期。
- **Vmalloc**（Vo, 1996）：更通用的配置器，可以同時實作 `Mem` 和 `Arena` 介面，讓 client 把記憶體組織成多個區域並自訂管理函式。
- **垃圾回收**：
  - 有 GC 的語言裡，程式設計師幾乎可以忽略儲存空間的配置，**配置相關的 bug 不可能發生**，作者說這個好處「怎麼強調都不為過」。
  - GC 從程式變數出發，找出所有可以到達的區塊，其餘的就可以重複使用。
  - 通常需要語言提供足夠的型別資訊（LISP、Icon、Smalltalk、ML、Modula-3）。
  - **保守式 GC**（Boehm & Weiser, 1988）可以用在 C/C++：把任何看起來像指標、而且有對齊的位元樣式都當成指標。它會高估可以到達的區塊，但在某些程式裡效果出奇地好。

---

## 6. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 6.1 | 目前的 chunk 空間不夠時，先找串列中**其他 chunk** 有沒有足夠的空間 | 空間利用率 vs. 速度，要量測 |
| 6.2 | 從 `freechunks` 選**最大**而且夠用的 chunk，並追蹤最大值；這樣 `while` 可以改成 `if` | 會不會明顯變慢？能不能更省記憶體？ |
| 6.3 | 根據配置模式**動態計算 `THRESHOLD`** | 空閒串列小 vs. 少呼叫 `malloc` |
| 6.4 | 為什麼介面**沒有** `Arena_resize`？要支援的話怎麼改？ | Arena 不記錄個別區塊的大小，也不能單獨釋放一個區塊，所以沒辦法知道要複製多少 |
| 6.5 | 設計**堆疊配置器**（mark / pop 到某個高度）的介面 | 能用哪些 checked error 抓出釋放錯誤？ |
| 6.6 | 設計一個同時支援兩種配置器的單一介面（「配置環境」，可以 push/pop） | 多個配置介面並存時，其他介面不知道該選哪一個 |

---

## 7. 本章重點整理

1. **兩類配置演算法**：以大小為主（malloc、first fit）vs. **以生命週期為主**（arena、stack）。
2. **Arena = 配置很多次，一次全部釋放**：適合 GUI 視窗、編譯器處理單一函式這類成批結束的情況。
3. **優點**：快、沒有洩漏、不用逐一 free，**最重要的是讓程式碼更簡單**（鼓勵 applicative 演算法）。
4. **缺點**：比較耗記憶體；物件放錯 arena 會產生懸空指標或洩漏，但實務上很少發生。
5. **介面**：`Arena_new`、`Arena_dispose`、`Arena_alloc`、`Arena_calloc`、`Arena_free`；注意 free 和 dispose 的差別。
6. **實作**：
   - `struct T { prev, avail, limit }` 描述目前的 chunk。
   - 配置通常只是指標加法。
   - 換 chunk 時用**結構賦值**把舊狀態推入新 chunk 開頭，形成堆疊。
   - `union header` 保證對齊。
   - 所有 arena 共用的 `freechunks` 重複使用 chunk，用 `THRESHOLD = 10` 限制數量。
7. Arena 是介於 `malloc`/`free` 和**垃圾回收**之間的一種選擇。

> **一句話**：如果物件的生命週期是成批結束的，就把它們放進同一個 arena，一次釋放。這樣配置變快、洩漏消失，程式碼也簡單得多。
