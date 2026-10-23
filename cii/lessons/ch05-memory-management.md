# 第 5 章　Memory Management（記憶體管理）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.67–88

---

## 1. 本章定位

每個有點規模的 C 程式都會在執行期配置記憶體。標準函式庫提供 `malloc`、`calloc`、`realloc`、`free` 四個函式，但用起來很容易出錯，而且這類 bug **很難診斷**，因為錯誤被發現的時間和地點，往往離真正出錯的地方很遠。

**`Mem` 介面**把這四個函式重新包裝成一組**比較不容易出錯**、還多了一些功能的巨集和函式，並且提供**兩種實作**：

| 實作 | 檔案 | 特性 |
|---|---|---|
| **正式版**（production） | `mem.c` | 薄薄一層包裝標準函式庫 |
| **檢查版**（checking） | `memchk.c` | 自己寫的配置器，**偵測存取錯誤**並當成 checked runtime error |

> 這是第 2 章「**一個介面、多個實作**」的最佳示範：client 程式碼完全不用改，換一個連結的實作就能切換到除錯模式。

---

## 2. 常見的記憶體錯誤

### 2.1 懸空指標（dangling pointer）

```c
p = malloc(nbytes);
...
free(p);
/* p 現在指向邏輯上已經不存在的記憶體 */
```

之後再對 `p` 解參考就是錯的。如果那塊記憶體還沒被重新配置，錯誤可能**完全不會被發現**，這正是它難以診斷的原因。

### 2.2 重複釋放（double free）

```c
free(p);
...
free(p);    /* 釋放已經釋放過的記憶體 */
```

通常會**破壞記憶體管理器的內部資料結構**，但要等到下一次呼叫配置函式時才會爆發。

### 2.3 釋放不是 malloc 來的記憶體

```c
char buf[20], *p;
if (n >= sizeof buf)
    p = malloc(n);
else
    p = buf;
...
free(p);    /* p 指向 buf 時也被 free 了！ */
```

### 2.4 綜合範例：看起來很穩健的 `itoa`

```c
void itoa(int n, char *buf, int size) {
    char *p = malloc(43);
    sprintf(p, "%d", n);
    if (strlen(p) >= size - 1) {
        while (--size > 0)
            *buf++ = '*';
        *buf = '\0';
    } else
        strcpy(buf, p);
}
```

**至少兩個錯誤**：
1. **沒有檢查 `malloc` 是否回傳 NULL。**
2. **記憶體洩漏**：配置了卻從來沒有釋放，每呼叫一次就漏一點，最後記憶體耗盡。

另外，`size < 2` 時雖然能正確運作，但它是靠把 `buf[0]` 設成 `'\0'` 做到的。比較好的設計也許是要求 `size > 2`，並用 checked runtime error 強制執行。

### 2.5 `Mem` 無法防範的錯誤

- 對**損壞的指標**解參考。
- 使用指向**已離開作用域的區域變數**的指標，這是新手常犯的錯：

```c
char *itoa(int n) {
    char buf[43];
    sprintf(buf, "%d", n);
    return buf;     /* ✗ 函式返回後 buf 就不存在了 */
}
```

---

## 3. 介面（5.1 Interface）

```c
/* mem.h */
#ifndef MEM_INCLUDED
#define MEM_INCLUDED
#include "except.h"

extern const Except_T Mem_Failed;

extern void *Mem_alloc (long nbytes, const char *file, int line);
extern void *Mem_calloc(long count, long nbytes, const char *file, int line);
extern void  Mem_free  (void *ptr, const char *file, int line);
extern void *Mem_resize(void *ptr, long nbytes, const char *file, int line);

#define ALLOC(nbytes) \
    Mem_alloc((nbytes), __FILE__, __LINE__)
#define CALLOC(count, nbytes) \
    Mem_calloc((count), (nbytes), __FILE__, __LINE__)
#define NEW(p)  ((p) = ALLOC((long)sizeof *(p)))
#define NEW0(p) ((p) = CALLOC(1, (long)sizeof *(p)))
#define FREE(ptr) ((void)(Mem_free((ptr), \
    __FILE__, __LINE__), (ptr) = 0))
#define RESIZE(ptr, nbytes) ((ptr) = Mem_resize((ptr), \
    (nbytes), __FILE__, __LINE__))

#endif
```

### 3.1 和標準函式庫的關鍵差異

| 特性 | 標準函式庫 | `Mem` |
|---|---|---|
| 大小為 0 | 行為由實作決定 | **checked runtime error** |
| 配置失敗 | 回傳 NULL | **丟出 `Mem_Failed`，永遠不回傳 NULL** |
| 參數型別 | `size_t`（無號） | **`long`（有號）** |
| 錯誤位置 | 沒有 | 自動帶入呼叫端的 `__FILE__`、`__LINE__` |
| 釋放後 | 指標保持原值（懸空） | `FREE` 會**把指標設成 NULL** |

### 3.2 `Mem_alloc` / `Mem_calloc`

- **`Mem_alloc(nbytes)`**：配置至少 `nbytes` 位元組，**對齊到最嚴格的對齊要求**，內容**未初始化**。`nbytes` 不是正數就是 checked runtime error。
- **`Mem_calloc(count, nbytes)`**：配置能放 `count` 個、每個 `nbytes` 大小的陣列，**全部清成 0**。
  - ⚠ NULL 指標和 `0.0` **不一定**以全零位元表示，所以 `Mem_calloc` 不一定能正確初始化它們。
- 後兩個參數 `file`、`line` 是呼叫位置，通常透過巨集 `ALLOC`、`CALLOC` 自動帶入。
- 配置失敗時丟出 `Mem_Failed`，並把 `file`、`line` 傳給 `Except_raise`，讓例外**回報呼叫端的位置**。`file` 是 NULL 時改用實作內部的位置。

### 3.3 為什麼參數是 `long` 而不是 `size_t`？

```c
int n = -1;
...
p = malloc(n);    /* -1 轉成 size_t 會變成一個巨大的無號數 */
```

很多 `malloc` 實作抓不到這個錯誤。用**有號的 `long`**，`Mem_alloc` 就能用 `assert(nbytes > 0)` 抓出負數。

### 3.4 `sizeof *p` 慣用寫法與 `NEW`

```c
struct T *p;
p = Mem_alloc(sizeof (struct T));   /* 可以，但脆弱 */
p = Mem_alloc(sizeof *p);           /* 比較好 */
```

**為什麼 `sizeof *p` 比較好？**
- 適用於任何指標型別（`void *` 除外），而且**和指標指向的型別無關**。
- 如果 `p` 的型別改了，`sizeof *p` 會**自動跟著變**；`sizeof (struct T)` 就得手動修改，忘了改的話：
  - 配置太多 → 浪費空間
  - 配置太少 → **災難**，client 會寫到沒有配置的記憶體

這個寫法太常見了，所以 `Mem` 提供巨集把「配置」和「賦值」包在一起：

```c
#define NEW(p)  ((p) = ALLOC((long)sizeof *(p)))      /* 未初始化 */
#define NEW0(p) ((p) = CALLOC(1, (long)sizeof *(p)))  /* 清成 0  */
```

- 提供 `NEW` 的前提是：大多數 client 配置完會**馬上初始化**。
- **`sizeof` 的運算元不會在執行期求值**，只取它的型別，所以 `NEW` 和 `NEW0` 只對 `p` **求值一次**。像 `NEW(a[i++])` 這種有副作用的參數也是安全的。

### 3.5 `Mem_free` 與 `FREE`

```c
#define FREE(ptr) ((void)(Mem_free((ptr), __FILE__, __LINE__), (ptr) = 0))
```

- `ptr` 不是 NULL 就釋放它；是 NULL 就什麼都不做。
- `FREE` 釋放後**把 `ptr` 設成 NULL**。之後再解參考**通常會讓程式立刻崩潰**（定址錯誤），這種**確定的錯誤**比懸空指標的不可預期行為好得多。
- ⚠ **`FREE` 會對 `ptr` 求值不只一次**，不要傳有副作用的運算式。

### 3.6 `Mem_resize` 與 `RESIZE`

```c
#define RESIZE(ptr, nbytes) ((ptr) = Mem_resize((ptr), (nbytes), __FILE__, __LINE__))
```

- 擴大或縮小一個**已配置**的區塊，讓它至少有 `nbytes` 位元組，而且**可能搬移**區塊。
- 邏輯上等於：配置新區塊 → 複製資料 → 釋放舊區塊。
- 變大時，多出來的部分未初始化；變小時，只複製前 `nbytes` 位元組。
- 傳 NULL 的 `ptr` 或不是正數的 `nbytes` 是 checked runtime error。
- ⚠ `RESIZE` 也會對 `ptr` 求值不只一次。

### 3.7 存取錯誤的處理：依實作而不同

| 錯誤 | 檢查版 | 正式版 |
|---|---|---|
| 傳給 `Mem_free`/`Mem_resize` 的指標**不是**由 `Mem_alloc`/`Mem_calloc`/`Mem_resize` 回傳的 | **checked** | unchecked |
| 傳入**已經**被 `Mem_free`/`Mem_resize` 處理過的指標 | **checked** | unchecked |

> 同一個介面，不同實作提供**不同強度的保證**。介面要明確寫出這一點。

### 3.8 其他規定

- `Mem` 可以和標準的 `malloc` 等函式**混用**，但檢查只適用於 `Mem` 管理的記憶體。
- **一個程式只能使用一種 `Mem` 實作。**

---

## 4. 正式版實作（5.2 Production Implementation）

```c
/* mem.c */
#include <stdlib.h>
#include <stddef.h>
#include "assert.h"
#include "except.h"
#include "mem.h"

const Except_T Mem_Failed = { "Allocation Failed" };

void *Mem_alloc(long nbytes, const char *file, int line) {
    void *ptr;
    assert(nbytes > 0);
    ptr = malloc(nbytes);
    if (ptr == NULL) {
        if (file == NULL)
            RAISE(Mem_Failed);
        else
            Except_raise(&Mem_Failed, file, line);
    }
    return ptr;
}

void *Mem_calloc(long count, long nbytes, const char *file, int line) {
    void *ptr;
    assert(count > 0);
    assert(nbytes > 0);
    ptr = calloc(count, nbytes);
    if (ptr == NULL)
        /* raise Mem_Failed（同上）*/;
    return ptr;
}

void Mem_free(void *ptr, const char *file, int line) {
    if (ptr)
        free(ptr);
}

void *Mem_resize(void *ptr, long nbytes, const char *file, int line) {
    assert(ptr);
    assert(nbytes > 0);
    ptr = realloc(ptr, nbytes);
    if (ptr == NULL)
        /* raise Mem_Failed */;
    return ptr;
}
```

**要點：**
- 沒有處理例外時，訊息會指出**呼叫端**的位置：
  ```
  Uncaught exception Allocation Failed raised @parse.c:431
  aborting...
  ```
- **`Mem_calloc`**：`calloc` 在 `count` 或 `nbytes` 為 0 時的行為由實作決定，**`Mem` 把它規定清楚**，這是它的優點之一，可以避免 bug。
- **`Mem_free`**：標準允許 `free(NULL)`，但**舊的實作可能不接受**，所以先檢查。
- **`Mem_resize` 比 `realloc` 簡單得多**：
  - `realloc` 在 `nbytes == 0` 時會**釋放**區塊，在 `ptr == NULL` 時會**配置**新區塊。
  - 這些附加功能和「改變大小」只有鬆散的關係，**容易引發 bug**。
  - `Mem_resize` 只做一件事：改變既有區塊的大小。
  - （呼應第 1 章說 `realloc` 是「混亂的傑作」。）

---

## 5. 檢查版實作（5.3 Checking Implementation）

### 5.1 核心想法

如果配置函式：
1. **永遠不回傳同一個位址兩次**，而且
2. **記得**所有回傳過的位址，以及它們目前是「已配置」還是「已釋放」，

那 `Mem_free` 和 `Mem_resize` 就能偵測存取錯誤。

**抽象模型**：維護一個集合 S，元素是 `(α, free)` 或 `(α, allocated)`：
- `Mem_alloc`/`Mem_calloc` 加入 `(ptr, allocated)`，並保證 `ptr` 之前**從未**出現在 S 裡。
- `Mem_free(ptr)` 合法 ⇔ `ptr` 是 NULL，或 `(ptr, allocated) ∈ S`；釋放後改成 `(ptr, free)`。
- `Mem_resize` 合法 ⇔ `(ptr, allocated) ∈ S`；做法是 alloc → copy → free。

**「永不重複位址」怎麼做到？**
最簡單的方法是永遠不釋放任何東西，但太浪費。比較好的方法是：**永遠不重新配置「曾經被回傳過的那個位址」的那個位元組**，區塊的其他部分可以拿去重複使用。

### 5.2 資料結構：描述子雜湊表 + 空閒串列

```c
static struct descriptor {
    struct descriptor *free;   /* 空閒串列的鏈結（NULL 代表已配置）*/
    struct descriptor *link;   /* 雜湊鏈結 */
    const void *ptr;           /* 區塊位址 */
    long size;                 /* 區塊大小 */
    const char *file;          /* 配置位置（給除錯器看的）*/
    int line;
} *htab[2048];

static struct descriptor freelist = { &freelist };   /* 環狀空閒串列的虛擬頭 */
```

- **`htab`** 保存**所有**區塊（已配置和已釋放）的描述子，它就是集合 S 的實作。
- **`free` 欄位**：已配置時是 NULL；已釋放時非 NULL，而且串在空閒串列上。
- **`freelist`** 是**環狀**串列的虛擬節點：它是串列的最後一個描述子，它的 `free` 指向第一個。
- `file`、`line` 程式本身沒用到，是**留給除錯器**在除錯時印出來的。

### 5.3 查找與雜湊

```c
#define hash(p, t) (((unsigned long)(p)>>3) & \
    (sizeof (t)/sizeof ((t)[0])-1))

static struct descriptor *find(const void *ptr) {
    struct descriptor *bp = htab[hash(ptr, htab)];
    while (bp && bp->ptr != ptr)
        bp = bp->link;
    return bp;
}
```

把位址當成位元樣式，**右移 3 位**（低位元因為對齊幾乎都是 0），再對表大小取模。表大小是 2 的冪，所以可以用 `& (n-1)`。

### 5.4 `Mem_free`：偵測三種錯誤

```c
void Mem_free(void *ptr, const char *file, int line) {
    if (ptr) {
        struct descriptor *bp;
        if (((unsigned long)ptr)%(sizeof (union align)) != 0   /* 沒對齊 */
        ||  (bp = find(ptr)) == NULL                           /* 不在表中 */
        ||  bp->free)                                          /* 已經釋放過 */
            Except_raise(&Assert_Failed, file, line);
        bp->free = freelist.free;      /* 加入空閒串列 */
        freelist.free = bp;
    }
}
```

- **對齊檢查**是一個快速過濾：沒對齊的位址**不可能**是合法的區塊指標，連 `find` 都不用呼叫。
- 錯誤時丟出 **`Assert_Failed`**，位置是**呼叫 `Mem_free` 的地方**。
- 釋放的區塊加到空閒串列，**以後可以重複使用**，但起始位址不會被重新回傳，原因見後面的 `Mem_alloc`。

### 5.5 `union align`：最嚴格的對齊

```c
union align {
    int i;
    long l;
    long *lp;
    void *p;
    void (*fp)(void);
    float f;
    double d;
    long double ld;
};
```

把**最可能有最嚴格對齊要求的型別**放進一個 union，它的大小就是這台機器上的最小安全對齊單位。`Mem_alloc` 回傳的指標一定是 `sizeof(union align)` 的倍數，**保證任何型別的資料都能放進去**。

### 5.6 `Mem_resize` 和 `Mem_calloc`：建立在 `Mem_alloc` / `Mem_free` 之上

```c
void *Mem_resize(void *ptr, long nbytes, const char *file, int line) {
    struct descriptor *bp;
    void *newptr;
    assert(ptr);
    assert(nbytes > 0);
    /* 同樣的合法性檢查 → 設定 bp */
    newptr = Mem_alloc(nbytes, file, line);
    memcpy(newptr, ptr, nbytes < bp->size ? nbytes : bp->size);
    Mem_free(ptr, file, line);
    return newptr;
}

void *Mem_calloc(long count, long nbytes, const char *file, int line) {
    void *ptr;
    assert(count > 0);
    assert(nbytes > 0);
    ptr = Mem_alloc(count*nbytes, file, line);
    memset(ptr, '\0', count*nbytes);
    return ptr;
}
```

### 5.7 描述子要分開配置

把描述子和使用者的資料放在同一塊記憶體看起來很省事，但有兩個缺點：
1. 把一大塊空閒空間切給多個小請求時會變複雜，因為每個請求都需要自己的描述子。
2. **描述子容易被破壞**：寫入時稍微超出區塊邊界，就會蓋掉描述子。

所以描述子**另外配置**，降低（但不能完全消除）被破壞的機會：

```c
#define NDESCRIPTORS 512

static struct descriptor *dalloc(void *ptr, long size,
        const char *file, int line) {
    static struct descriptor *avail;
    static int nleft;
    if (nleft <= 0) {
        avail = malloc(NDESCRIPTORS*sizeof (*avail));   /* 一次要 512 個 */
        if (avail == NULL)
            return NULL;
        nleft = NDESCRIPTORS;
    }
    avail->ptr  = ptr;
    avail->size = size;
    avail->file = file;
    avail->line = line;
    avail->free = avail->link = NULL;
    nleft--;
    return avail++;
}
```

### 5.8 `Mem_alloc`：First-Fit 演算法

```c
#define NALLOC ((4096 + sizeof (union align) - 1)/ \
    (sizeof (union align)))*(sizeof (union align))

void *Mem_alloc(long nbytes, const char *file, int line) {
    struct descriptor *bp;
    void *ptr;

    assert(nbytes > 0);
    /* 把 nbytes 向上取整到對齊邊界 */
    nbytes = ((nbytes + sizeof (union align) - 1)/
        (sizeof (union align)))*(sizeof (union align));

    for (bp = freelist.free; bp; bp = bp->free) {
        if (bp->size > nbytes) {
            /* 從這個空閒區塊的「尾端」切下 nbytes */
            bp->size -= nbytes;
            ptr = (char *)bp->ptr + bp->size;
            if ((bp = dalloc(ptr, nbytes, file, line)) != NULL) {
                unsigned h = hash(ptr, htab);
                bp->link = htab[h];
                htab[h] = bp;
                return ptr;
            } else
                /* raise Mem_Failed */;
        }
        if (bp == &freelist) {
            /* 繞了一圈都沒找到 → 向 malloc 要一塊 NALLOC+nbytes 的新空間 */
            struct descriptor *newptr;
            if ((ptr = malloc(nbytes + NALLOC)) == NULL
            ||  (newptr = dalloc(ptr, nbytes + NALLOC,
                    __FILE__, __LINE__)) == NULL)
                /* raise Mem_Failed */;
            newptr->free = freelist.free;     /* 插到空閒串列前端 */
            freelist.free = newptr;
        }
    }
    assert(0);
    return NULL;
}
```

**精妙之處：**

| 設計 | 目的 |
|---|---|
| **向上取整**：`((n + a - 1) / a) * a` | 每個回傳的指標都是 `sizeof(union align)` 的倍數 |
| **從空閒區塊的「尾端」切** | 空閒區塊的起始位址 `bp->ptr` 永遠不變 |
| **條件是 `>` 而不是 `>=`** | 保證空閒區塊**永遠至少留下一點**，所以 `bp->ptr` **永遠不會被回傳**，實現「永不重複位址」 |
| 大區塊被切到只剩 `sizeof(union align)` 時 | 不能再滿足任何請求；每塊新空間的前 `sizeof(union align)` 位元組永遠不會被配置出去 |
| 找不到就向 `malloc` 要 `NALLOC + nbytes`（約 4 KB 多） | 新空間像是「已配置又釋放」的區塊一樣有描述子，插到串列前端，下一輪迴圈就會用它 |
| 不合併相鄰的空閒區塊 | 合併會導致回傳重複的位址（見習題 5.3） |

---

## 6. 延伸閱讀重點

- **Maguire (1993)**：批評標準配置函式，並提出類似的重新包裝。
- **Purify**（Hastings & Joyce, 1992）：**檢查每一個 load/store 指令**，直接編輯目的碼，沒有原始碼也能用。這類工具的盛行說明記憶體 bug 有多普遍，甚至整間公司都靠賣這種工具維生。
- Austin 等人 (1994)：「安全指標」帶有足夠資訊，能抓出各種存取錯誤（原始碼插樁的做法）。
- **LCLint**：在編譯期偵測許多潛在的配置錯誤。
- **Knuth (1973a)**：整理了各種配置演算法，說明為什麼 **first fit 通常比 best fit 好**。本章的 first fit 類似 **K&R 第 8.7 節**的版本。
- **Quick fit**（Weinstock & Wulf, 1988）：很多應用只配置少數幾種大小，所以為最常見的 N 種大小各維護一條空閒串列。
- Grunwald & Zorn (1993)：先收集應用的配置統計，再**自動產生**為該應用量身打造的 `malloc`/`free`。

---

## 7. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 5.1 | 用特殊的位元樣式填滿未初始化的記憶體，幫助抓出讀取未初始化資料的 bug | 好的樣式要具備什麼性質？（例如看起來不像合法指標或常見數值、是奇數位址等） |
| 5.2 | 把已經縮到 `sizeof(union align)` 的空閒區塊移出串列 | 它們永遠不能用，卻拖慢搜尋 |
| 5.3 | 設計能**合併相鄰空閒區塊**、又不回傳重複位址的演算法 | 兩個保證之間的矛盾 |
| 5.4 | 實作 `Mem_log(FILE *)`：把存取錯誤寫進記錄檔，而不是丟出例外 | 取捨：嚴格中止 vs. 記錄後繼續 |
| 5.5 | 實作 `Mem_leak(apply, cl)`：走訪所有仍在使用中的區塊，找出記憶體洩漏 | **閉包（closure）= 函式指標 + 使用者資料 `cl`**，這是後面 `_map` 系列函式的前身 |

---

## 8. 本章重點整理

1. **C 記憶體錯誤**：懸空指標、重複釋放、釋放非 malloc 的記憶體、洩漏、沒檢查 NULL。這些錯誤難抓，因為**症狀和原因離得很遠**。
2. **`Mem` 的改進**：
   - 大小為 0 或負數 → checked runtime error（參數用 `long`）。
   - 失敗 → 丟出 `Mem_Failed`，永遠不回傳 NULL。
   - 自動記錄呼叫端的 `__FILE__`、`__LINE__`。
   - `FREE` 釋放後設成 NULL，把懸空指標變成**確定的崩潰**。
   - `Mem_resize` 只做一件事，不像 `realloc` 身兼三職。
3. **`NEW(p)` / `sizeof *p`**：型別改變時自動跟著變，而且只求值一次。
4. **兩種實作，同一個介面**：正式版求快，檢查版求安全，同樣的錯誤在兩邊分別是 unchecked 和 checked。
5. **檢查版的核心**：「永不重複位址」加上「記住每個位址的狀態」，用描述子雜湊表和環狀空閒串列實作。
6. **First fit 的技巧**：從尾端切、用 `>` 而不是 `>=`、用 `union align` 對齊、描述子分開配置。

> **一句話**：把標準的記憶體函式包裝成「不會回傳 NULL、規格清楚、會記錄位置」的介面，再提供一個可以抓出存取錯誤的檢查版實作，除錯時只要換一個連結的實作就好。
