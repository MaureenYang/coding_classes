# 第 16 章　High-Level Strings（高階字串）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.269–295

---

## 1. 本章定位

### 1.1 C 字串慣例的兩個重大缺點

第 15 章的 `Str` 擴充了 C 處理字串的慣例，但「以 NUL 結尾的字元陣列」這種表示方式本身有兩個缺點：

1. **計算長度要 O(N)**：必須掃過整個字串找到結尾的 NUL。
2. **不必要的配置**：Str 和部分標準函式庫函式**假設字串可以被修改**，所以它們或呼叫者必須為結果配置空間。在**不修改字串**的應用中，很多配置其實是不必要的。

### 1.2 `Text` 的解法

用**稍微不同的字串表示方式**同時解決這兩個問題：

| 問題 | Text 的解法 |
|---|---|
| 長度 O(N) | **長度和字串一起存放**，O(1) 取得 |
| 不必要的配置 | **字串不可變（immutable）**，子字串可以**共用**底層字元，**只在必要時才配置** |

**額外好處**：字串**可以包含 NUL 字元**。

**代價**：需要在 Text 的表示方式和 **C 字串之間轉換**。

| | Str（第 15 章） | Text |
|---|---|---|
| 表示方式 | `char *`，以 NUL 結尾 | **`{len, str}` 描述子** |
| 長度 | O(N) | **O(1)** |
| 可以修改嗎 | 可以 | **不可以** |
| 包含 NUL | 不可以 | **可以** |
| 子字串 | 配置新字串 | **共用，不配置** |
| 記憶體管理 | client 釋放每個結果 | **Text 管理字串空間**（堆疊式 save/restore） |

---

## 2. 介面（16.1 Interface）

### 2.1 ⭐ 描述子：公開表示方式、以傳值方式傳遞

```c
/* text.h */
#ifndef TEXT_INCLUDED
#define TEXT_INCLUDED
#include <stdarg.h>

#define T Text_T

typedef struct T {
    int len;            /* 長度 */
    const char *str;    /* 指向第一個字元（不以 NUL 結尾！）*/
} T;

/* ... exported data / functions ... */

#undef T
#endif
```

- `str` 指向的字串**不以 NUL 結尾**，而且**可以包含任何字元，包括 NUL**。
- **Text 公開描述子的表示方式**，client 可以直接存取欄位：`s.len` 是長度，`s.str[0..s.len-1]` 是字元。
- 注意這裡是 **`typedef struct T T;`**，**不是**不透明指標。這就是第 2 章提到的「公開表示方式、以傳值方式傳遞結構的 ADT」。

**⭐ 以傳值方式傳遞描述子**：
> Text 的函式**直接傳遞和回傳描述子本身**，而不是描述子的指標。所以 **Text 的函式從來不配置描述子**。

描述子只有兩個 word 大，傳值很便宜，而且完全不用管描述子的記憶體。

### 2.2 合約

| 類別 | 內容 |
|---|---|
| **可以做** | 讀取欄位和字元 |
| **不可以做** | 修改欄位或字元，除非透過介面函式、是 client 自己初始化的 `Text_T`，或是 `Text_box` 回傳的 |
| **Unchecked** | **修改** `Text_T` 描述的字串 |
| **Checked** | 傳入 `len` 為負數或 `str` 為 NULL 的 `Text_T` |
| **Unchecked** | **用 `free`、`Mem_free` 等外部方式釋放字串**，因為字串空間完全由 Text 管理 |

### 2.3 和 C 字串互相轉換

```c
extern T     Text_put(const char *str);
extern char *Text_get(char *str, int size, T s);
extern T     Text_box(const char *str, int len);
```

| 函式 | 方向 | 行為 |
|---|---|---|
| `Text_put(str)` | C → Text | **複製** C 字串到字串空間，回傳描述子；可能丟出 `Mem_Failed` |
| `Text_get(str, size, s)` | Text → C | 複製到 `str[0..size-2]` 並補上 NUL；**`str` 是 NULL 就用 `Mem_alloc` 配置**（client 負責釋放）；`size < s.len+1` 是 checked error |
| `Text_box(str, len)` | 包裝 | **不複製**，直接把 `str` 和 `len`「裝箱」成描述子 |

**`Text_box` 的用途**：為**常數字串**或 **client 自己配置的字串**建立描述子。

```c
static char editmsg[] = "Last edited by: ";
...
Text_T msg = Text_box(editmsg, sizeof (editmsg) - 1);   /* 注意 -1 */
```

> ⚠ 第二個參數**要扣掉結尾的 NUL**，否則 NUL 會被當成字串的一部分。

### 2.4 位置與子字串

位置的定義**和 Str 完全相同**：

```
            1   2   3   4   5   6   7   8   9   10
              I   n   t   e   r   f   a   c   e
           −9  −8  −7  −6  −5  −4  −3  −2  −1   0
```

```c
extern T   Text_sub(T s, int i, int j);
extern int Text_pos(T s, int i);
```

```c
Text_T s = Text_put("Interface");
Text_sub(s, 6, 10)     /* 以下全都是 "face" */
Text_sub(s, 0, -4)
Text_sub(s, 10, -4)
Text_sub(s, 6, 0)
Text_pos(s, -4)        /* 6 */
```

**⭐ `Text_sub` 不配置記憶體**：
- 因為字串**不會被修改**，也**不需要 NUL 結尾**，`Text_sub` 只要回傳一個 `str` 指向子字串第一個字元、`len` 是子字串長度的描述子就好。
- ⇒ s 和回傳值**可能共用**同一份字元。
- **但 client 不能假設一定會共用**，因為 Text 可能對空字串和單一字元字串做特別處理。

> 因此，**Text 的大多數函式不接受位置參數**（不像 Str），因為 `Text_sub` 幾乎不用成本就能提供同樣的能力，先取子字串再操作就好。

### 2.5 字串操作

```c
extern T Text_cat    (T s1, T s2);
extern T Text_dup    (T s, int n);
extern T Text_reverse(T s);
extern T Text_map    (T s, const T *from, const T *to);
extern int Text_cmp  (T s1, T s2);
```

| 函式 | 行為 |
|---|---|
| `Text_cat(s1, s2)` | 串接；**其中一個是空字串就直接回傳另一個**；**只在必要時**才複製 |
| `Text_dup(s, n)` | n 份 s 的串接；n 是負數是 checked error |
| `Text_reverse(s)` | 反轉 |
| `Text_map(s, &from, &to)` | 字元對應轉換；from、to 都是 NULL 時用最近一次的對應關係；只有一個是 NULL 或長度不同是 checked error |
| `Text_cmp(s1, s2)` | 字典順序比較 |

前四個都可能丟出 `Mem_Failed`。

### 2.6 預先定義的描述子

```c
extern const T Text_cset;     /* 全部 256 個 8 位元字元 */
extern const T Text_ascii;    /* 128 個 ASCII 字元 */
extern const T Text_ucase;    /* "ABCDEFGHIJKLMNOPQRSTUVWXYZ" */
extern const T Text_lcase;    /* "abcdefghijklmnopqrstuvwxyz" */
extern const T Text_digits;   /* "0123456789" */
extern const T Text_null;     /* 空字串 */
```

```c
Text_map(s, &Text_ucase, &Text_lcase);   /* 轉成小寫 */
```

client 可以取這些字串的**子字串**來組出其他常用的字元集合。

### 2.7 分析函式

和 Str **幾乎完全相同**，而且**仍然接受位置參數**，因為這些位置通常**記錄了分析的狀態**（例如掃描到哪裡了）。

```c
extern int Text_chr  (T s, int i, int j, int c);
extern int Text_rchr (T s, int i, int j, int c);
extern int Text_upto (T s, int i, int j, T set);
extern int Text_rupto(T s, int i, int j, T set);
extern int Text_any  (T s, int i, T set);
extern int Text_many (T s, int i, int j, T set);
extern int Text_rmany(T s, int i, int j, T set);
extern int Text_find  (T s, int i, int j, T str);
extern int Text_rfind (T s, int i, int j, T str);
extern int Text_match (T s, int i, int j, T str);
extern int Text_rmatch(T s, int i, int j, T str);
```

差別只在於 **set 和 str 參數也是 `Text_T`**，所以它們也可以包含 NUL。

### 2.8 `Text_fmt`：為什麼傳指標？

```c
extern void Text_fmt(int code, va_list *app,
    int put(int c, void *cl), void *cl,
    unsigned char flags[], int width, int precision);
```

- 可以搭配 Fmt 當作轉換函式使用，格式化方式和 `%s` 相同。
- **⚠ 它消耗的是 `Text_T *`（指標），而不是 `Text_T`！**

> **原因**：在標準 C 中，**把小結構放在可變參數部分傳遞可能不可攜**。Text_T 通常是兩個 word，而**沒有可攜的方法區分兩個 word 的結構和 `double`**，所以有些 C 實作沒辦法在可變參數裡可靠地以傳值方式傳遞兩個 word 的結構。傳指標在所有實作上都沒有問題。

```c
Fmt_register('T', Text_fmt);
Text_T name = Text_put("world");
Fmt_print("Hello, %T!\n", &name);   /* 傳位址 */
```

### 2.9 ⭐ 字串空間的管理：`Text_save` / `Text_restore`

```c
typedef struct Text_save_T *Text_save_T;

extern Text_save_T Text_save(void);
extern void        Text_restore(Text_save_T *save);
```

- Text 把結果字串存在它自己管理的**字串空間（string space）**，並讓 client 用**堆疊**的方式做有限的控制。
- **`Text_save()`**：回傳一個不透明值，記錄字串空間目前的「**頂端**」。
- **`Text_restore(&h)`**：**釋放** h 建立之後配置的所有字串空間。
  - ⇒ h 之後建立的**所有描述子和 `Text_save_T` 值都失效**。
- 傳 NULL 給 `Text_restore` 是 checked error；**使用已經失效的值**是 unchecked error。
- `Text_save` 可能丟出 `Mem_Failed`。

```c
Text_save_T mark = Text_save();
/* ... 大量的暫時字串運算 ... */
Text_T result = ...;
char *keep = Text_get(NULL, 0, result);   /* 把要保留的結果複製出去 */
Text_restore(&mark);                       /* 一次釋放所有的暫時字串 */
```

> 這其實就是第 6 章 **Arena** 的概念，套用在字串上。

---

## 3. 實作（16.2 Implementation）

和 Str 的實作很像，但 **Text 的函式可以利用好幾個重要的特殊情況**。

### 3.1 ⭐ 預先定義的描述子：全部指向同一個字串

```c
static char cset[] =
    "\000\001\002\003\004\005\006\007\010\011\012\013\014\015\016\017"
    "\020\021 ... "
    ...
    "\360\361\362\363\364\365\366\367\370\371\372\373\374\375\376\377";

const T Text_cset   = { 256, cset };
const T Text_ascii  = { 128, cset };
const T Text_ucase  = {  26, cset + 'A' };
const T Text_lcase  = {  26, cset + 'a' };
const T Text_digits = {  10, cset + '0' };
const T Text_null   = {   0, cset };
```

**巧妙之處**：`cset` 依序存放**全部 256 個字元**（`cset[c] == c`），所以：
- 大寫字母就是**從 `'A'` 開始的 26 個字元**，數字就是**從 `'0'` 開始的 10 個字元**。
- **六個描述子共用同一個陣列**，完全靠指標和長度切出不同的範圍。
- 這正是「描述子 + 共用」設計的最佳示範。（同樣假設是 ASCII 字元順序。）

### 3.2 位置轉換

```c
#define idx(i, len) ((i) <= 0 ? (i) + (len) : (i) - 1)

int Text_pos(T s, int i) {
    assert(s.len >= 0 && s.str);       /* 所有 Text_T 的基本檢查 */
    i = idx(i, s.len);
    assert(i >= 0 && i <= s.len);      /* 位置 1..N+1 ↔ 索引 0..N */
    return i + 1;
}

/* convert i and j to indices in 0..s.len */
assert(s.len >= 0 && s.str);
i = idx(i, s.len);
j = idx(j, s.len);
if (i > j) { int t = i; i = j; j = t; }
assert(i >= 0 && j <= s.len);
```

N 個字元的字串，合法索引是 0 到 N−1，但合法**位置**是 1 到 N+1，所以 assert 接受到 N 為止的索引。

### 3.3 `Text_box` 和 `Text_sub`：只建立描述子

```c
T Text_box(const char *str, int len) {
    T text;
    assert(str);
    assert(len >= 0);
    text.str = str;
    text.len = len;
    return text;
}

T Text_sub(T s, int i, int j) {
    T text;
    /* convert i and j to indices in 0..s.len */
    text.len = j - i;
    text.str = s.str + i;       /* 指向原字串，不複製 */
    return text;
}
```

### 3.4 ⭐ 專用的配置函式 `alloc`

Text 實作**自己的** `alloc(int len)` 來配置字串空間，原因有三：

1. **沒有區塊標頭**：一般配置器每個區塊都有標頭，`alloc` 沒有，所以**連續配置的字串會緊鄰在一起**，這讓 `Text_dup` 和 `Text_cat` 可以做重要的最佳化。
2. **不用管對齊**：字元沒有對齊限制。
3. **要配合 `Text_save` 和 `Text_restore`**。

```c
static struct chunk {
    struct chunk *link;
    char *avail;            /* 第一個空閒位元組 */
    char *limit;            /* 區塊結尾的下一個位元組 */
} head = { NULL, NULL, NULL }, *current = &head;

static char *alloc(int len) {
    assert(len >= 0);
    if (current->avail + len > current->limit) {
        current = current->link =
            ALLOC(sizeof (*current) + 10*1024 + len);   /* 至少 10KB */
        current->avail = (char *)(current + 1);
        current->limit = current->avail + 10*1024 + len;
        current->link = NULL;
    }
    current->avail += len;
    return current->avail - len;
}
```

- 這是第 6 章 **Arena 配置器**的簡單變形，字串空間就像**一個單一的 arena**。
- `current` 一開始指向一個**長度為 0 的區塊**（`head`），所以第一次配置時就會接上一個新區塊。
- 常見情況只是**一次指標加法**。

### 3.5 ⭐ `isatend`：判斷字串是否在字串空間的尾端

```c
#define isatend(s, n) ((s).str+(s).len == current->avail \
    && current->avail + (n) <= current->limit)
```

- `current->avail` 是字串空間尾端的**第一個空閒位元組**。
- 如果 `s.str + s.len == current->avail`，**s 剛好在字串空間的最尾端**。
- 第二個條件確保目前的區塊**還有至少 n 個位元組**的空間。

**這是 Text 最核心的最佳化依據**：如果 s 在尾端，要在它後面接東西，**只要接著配置就好，s 本身不用移動也不用複製**。

### 3.6 `Text_put` 和 `Text_get`

```c
T Text_put(const char *str) {
    T text;
    assert(str);
    text.len = strlen(str);
    text.str = memcpy(alloc(text.len), str, text.len);   /* 不加 NUL */
    return text;
}

char *Text_get(char *str, int size, T s) {
    assert(s.len >= 0 && s.str);
    if (str == NULL)
        str = ALLOC(s.len + 1);       /* 用 Mem 配置，client 負責釋放 */
    else
        assert(size >= s.len + 1);
    memcpy(str, s.str, s.len);        /* 用 memcpy，可能有內嵌的 NUL */
    str[s.len] = '\0';
    return str;
}
```

- `Text_put` 用 `memcpy` 而**不用 `strcpy`**，因為**不能**在 `text.str` 後面加 NUL。
- `Text_get` 用 `memcpy` 而**不用 `strncpy`**，因為要**複製 s 裡面可能出現的 NUL**（`strncpy` 遇到 NUL 就會停）。

### 3.7 ⭐ `Text_dup`：避免配置的特例

```c
T Text_dup(T s, int n) {
    assert(s.len >= 0 && s.str);
    assert(n >= 0);
    if (n == 0 || s.len == 0)
        return Text_null;              /* 特例 1：結果是空字串 */
    if (n == 1)
        return s;                      /* 特例 2：直接回傳自己 */
    {
        T text;
        char *p;
        text.len = n*s.len;
        if (isatend(s, text.len - s.len)) {   /* 特例 3：s 在尾端 */
            text.str = s.str;                 /* 原本的 s 就是第一份 */
            p = alloc(text.len - s.len);      /* 只配置 n-1 份 */
            n--;
        } else
            text.str = p = alloc(text.len);
        for ( ; n-- > 0; p += s.len)
            memcpy(p, s.str, s.len);
        return text;
    }
}
```

**特例 3 的圖解：**

```
字串空間：  [ ... other ... ][ s = "ab" ][ 空閒 ...
                                         ↑ current->avail

Text_dup(s, 3)：
            [ ... other ... ][ "ab" ][ "ab" ][ "ab" ][ 空閒 ...
                             ↑ text.str（就是原本的 s.str）
                             └──── 只新配置了這兩份 ────┘
```

如果 s 剛建立，它很可能就在字串空間的尾端，這時**原本的 s 可以當作第一份**，只需要再配置 n−1 份。

### 3.8 ⭐ `Text_cat`：四種情況

```c
T Text_cat(T s1, T s2) {
    assert(s1.len >= 0 && s1.str);
    assert(s2.len >= 0 && s2.str);
    if (s1.len == 0)                         /* 情況 1：s1 是空字串 */
        return s2;
    if (s2.len == 0)                         /* 情況 1：s2 是空字串 */
        return s1;
    if (s1.str + s1.len == s2.str) {         /* 情況 2：本來就相鄰！ */
        s1.len += s2.len;
        return s1;                           /* 完全不用複製 */
    }
    {
        T text;
        text.len = s1.len + s2.len;
        if (isatend(s1, s2.len)) {           /* 情況 3：s1 在尾端 */
            text.str = s1.str;
            memcpy(alloc(s2.len), s2.str, s2.len);   /* 只複製 s2 */
        } else {                             /* 情況 4：一般情況 */
            char *p;
            text.str = p = alloc(s1.len + s2.len);
            memcpy(p,          s1.str, s1.len);
            memcpy(p + s1.len, s2.str, s2.len);
        }
        return text;
    }
}
```

| 情況 | 條件 | 成本 |
|---|---|---|
| 1 | 其中一個是空字串 | **零** |
| 2 | s1 和 s2 在記憶體中**本來就相鄰** | **零**，只改長度 |
| 3 | s1 在字串空間尾端 | 只複製 s2 |
| 4 | 其他 | 兩個都複製 |

> **情況 2 很常見**：例如把一個字串用 `Text_sub` 切開，處理後再接回去；或是連續 `Text_put` 的兩個字串。正是因為 `alloc` **沒有區塊標頭**，連續配置的字串才會緊鄰在一起。

### 3.9 `Text_reverse`

```c
T Text_reverse(T s) {
    assert(s.len >= 0 && s.str);
    if (s.len == 0)
        return Text_null;
    else if (s.len == 1)
        return s;                  /* 一個字元的反轉就是自己 */
    else {
        T text;
        char *p;
        int i = s.len;
        text.len = s.len;
        text.str = p = alloc(s.len);
        while (--i >= 0)
            *p++ = s.str[i];
        return text;
    }
}
```

### 3.10 `Text_map`：需要 `inited` 旗標

```c
T Text_map(T s, const T *from, const T *to) {
    static char map[256];
    static int inited = 0;
    assert(s.len >= 0 && s.str);
    if (from && to) {
        /* rebuild map */
        int k;
        for (k = 0; k < (int)sizeof map; k++)
            map[k] = k;
        assert(from->len == to->len);
        for (k = 0; k < from->len; k++)
            map[(unsigned char)from->str[k]] = to->str[k];
        inited = 1;
    } else {
        assert(from == NULL && to == NULL);
        assert(inited);
    }
    if (s.len == 0)
        return Text_null;
    else {
        T text;
        int i;
        char *p;
        text.len = s.len;
        text.str = p = alloc(s.len);
        for (i = 0; i < s.len; i++)
            *p++ = map[(unsigned char)s.str[i]];
        return text;
    }
}
```

> **和 `Str_map` 的對比**：`Str_map` 不可能把字元對應到 NUL，所以用 `map['a'] != 0` 就能判斷有沒有初始化過。**`Text_map` 允許所有可能的對應，包括對應到 NUL**，所以沒辦法用 map 裡的值來判斷，**必須用一個獨立的 `inited` 旗標**。

### 3.11 `Text_cmp`

```c
int Text_cmp(T s1, T s2) {
    assert(s1.len >= 0 && s1.str);
    assert(s2.len >= 0 && s2.str);
    if (s1.str == s2.str)
        return s1.len - s2.len;        /* 特例：指向同一個位置 → 短的比較小 */
    else if (s1.len < s2.len) {
        int cond = memcmp(s1.str, s2.str, s1.len);
        return cond == 0 ? -1 : cond;  /* 是前綴 → 比較小 */
    } else if (s1.len > s2.len) {
        int cond = memcmp(s1.str, s2.str, s2.len);
        return cond == 0 ? +1 : cond;
    } else
        return memcmp(s1.str, s2.str, s1.len);
}
```

- **重要的特例**：s1 和 s2 **指向同一個字串**（共用的結果），這時短的一定是長的前綴，直接比較長度。
- 用 **`memcmp`** 而不是 `strncmp`，因為字串**可能包含 NUL**。

### 3.12 `Text_save` 和 `Text_restore`

```c
struct Text_save_T {
    struct chunk *current;
    char *avail;
};

Text_save_T Text_save(void) {
    Text_save_T save;
    NEW(save);
    save->current = current;
    save->avail = current->avail;
    alloc(1);                          /* ⭐ 製造一個「洞」 */
    return save;
}

void Text_restore(Text_save_T *save) {
    struct chunk *p, *q;
    assert(save && *save);
    current = (*save)->current;
    current->avail = (*save)->avail;   /* 恢復尾端位置 */
    FREE(*save);
    for (p = current->link; p; p = q) {   /* 釋放之後的所有區塊 */
        q = p->link;
        FREE(p);
    }
    current->link = NULL;
}
```

**⭐ 為什麼 `Text_save` 要 `alloc(1)`？**
- 在字串空間裡**製造一個 1 位元組的「洞」**，讓**之前配置的任何字串用 `isatend` 檢查都會失敗**。
- 否則可能發生：save 之前的字串 s 剛好在尾端 → save 之後 `Text_cat(s, x)` 走了「s 在尾端」的最佳化，把 x 接在 s 後面 → 結果字串**橫跨了 save 點** → restore 之後，結果的後半段被釋放了，但前半段還在。
- 有了這個洞，**不可能有字串橫跨回傳給 client 的那個尾端位置**。

### 3.13 分析函式：`memchr` 和 `memcmp`

實作和 Str 幾乎一樣，**差別在於字串可能包含 NUL**：

```c
int Text_upto(T s, int i, int j, T set) {
    assert(set.len >= 0 && set.str);
    /* convert i and j to indices in 0..s.len */
    for ( ; i < j; i++)
        if (memchr(set.str, s.str[i], set.len))   /* 不用 strchr */
            return i + 1;
    return 0;
}

#define equal(s, i, t) \
    (memcmp(&(s).str[i], (t).str, (t).len) == 0)  /* 不用 strncmp */

int Text_find(T s, int i, int j, T str) {
    assert(str.len >= 0 && str.str);
    /* convert i and j to indices in 0..s.len */
    if (str.len == 0)
        return i + 1;
    else if (str.len == 1) {
        for ( ; i < j; i++)
            if (s.str[i] == *str.str)
                return i + 1;
    } else
        for ( ; i + str.len <= j; i++)
            if (equal(s, i, str))
                return i + 1;
    return 0;
}
```

| Str 用 | Text 改用 | 原因 |
|---|---|---|
| `strchr(set, c)` | `memchr(set.str, c, set.len)` | set 可能包含 NUL；`strchr` 會把 NUL 當成結尾 |
| `strncmp` | `memcmp` | 字串可能包含 NUL |

其他函式（`rchr`、`rupto`、`any`、`many`、`rmany`、`rfind`、`match`、`rmatch`）都是同樣的對應改寫，邏輯和 Str 版本相同（例如 `Text_rmany` 也回傳 `j + 2`）。

### 3.14 `Text_fmt`

```c
void Text_fmt(int code, va_list *app,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    T *s;
    assert(app && flags);
    s = va_arg(*app, T*);              /* 取指標 */
    assert(s && s->len >= 0 && s->str);
    Fmt_puts(s->str, s->len, put, cl, flags, width, precision);
}
```

因為有長度，可以直接交給 `Fmt_puts`，**不需要 NUL 結尾**。

---

## 4. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **換一種表示方式解決根本問題** | `{len, str}` 讓長度 O(1)、可以包含 NUL |
| **不可變 → 共用** | 不可變讓子字串可以共用，`Text_sub` 零配置 |
| **⭐ 公開表示方式 + 傳值** | 描述子只有兩個 word，傳值很便宜，函式從不配置描述子 |
| **不承諾共用** | client 不能依賴共用，保留實作的彈性 |
| **專用配置器** | 沒有標頭、不用對齊，連續配置的字串緊鄰 → 可以做 `isatend` 最佳化 |
| **特例最佳化** | `Text_cat` 的四種情況、`Text_dup` 的三個特例 |
| **常數共用一個陣列** | `cset` 加上不同的偏移量和長度 |
| **Arena 式的堆疊回收** | `Text_save`/`Text_restore` |
| **用「洞」保護不變式** | `alloc(1)` 避免字串橫跨 save 點 |
| **可攜性** | `Text_fmt` 傳指標，避開可變參數傳遞結構的問題 |
| **NUL 安全** | `memchr`/`memcmp`/`memcpy` 取代 `str*` 函式 |

### Str vs. Text：什麼時候用哪個？

| 情境 | 選擇 |
|---|---|
| 和大量 C 函式庫互動、需要 NUL 結尾 | **Str** |
| 大量子字串、串接、分析，字串不修改 | **Text** |
| 資料可能包含 NUL（二進位資料） | **Text** |
| 頻繁需要長度 | **Text** |
| 暫時字串很多、想要成批回收 | **Text**（save/restore） |

---

## 5. 延伸閱讀重點

- Text_T 的語意和實作都和 **SNOBOL4**、**Icon** 的字串很像。這兩個都是通用的字串處理語言，內建了和 Text 函式類似的功能。
- 類似的字串表示技巧很早就用在**編譯器**等分析字串的應用中，**XPL 編譯器產生器**（McKeeman, Horning & Wortman, 1970）就是一個早期的例子。
- **垃圾回收**：如果系統知道所有的 Text_T，就可以用 GC 管理字串空間。Icon 用 XPL 的 GC 演算法回收沒有被任何已知 Text_T 參考的字串空間（Hanson, 1980），做法是把已知 Text_T 的字串複製到字串空間的開頭來壓縮。
- **Hansen (1992)**：完全不同的表示方式，子字串描述子帶有足夠的資訊能找回它所屬的較大字串，因此可以把字串**向左或向右延伸**。
- **Ropes**（Boehm, Atkinson & Plass, 1995）：用**子字串組成的樹**表示字串。
  - 走訪字元是線性時間（和 Text_T、C 字串一樣）。
  - 取子字串是**對數時間**。
  - **串接是常數時間**，快很多。
  - 還可以用一個「產生第 i 個字元的函式」來描述一條 rope。

---

## 6. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 16.1 | 用 Text 函式重寫第 15 章的 `ids.c` | 比較兩種介面的寫法 |
| 16.2 | `Text_save`/`Text_restore` 不夠穩健：先 save x、再 save y、restore x、再 restore y，**錯誤不會被發現**（restore x 之後 y 已經失效）。讓這變成 **checked** runtime error | 例如維護一個 save 堆疊或序號 |
| 16.3 | 只能堆疊式配置的限制太大；設計可以**註冊** Text_T 的介面，加上 `Text_compact` 用 Hanson (1980) 的方法**壓縮**所有已註冊的字串，回收沒註冊的空間 | 簡易的字串垃圾回收 |
| 16.4 | 讓 `Text_find`、`Text_match` 等函式接受**正規表示式**形式的 Text_T | Kernighan & Plauger (1976) 的自動機實作 |
| 16.5 | 依 Hansen (1992) 的子字串模型設計介面和實作 | 可以延伸的子字串 |

---

## 7. 本章重點整理

1. **C 字串的兩個缺點**：長度 O(N)，以及假設字串可以修改所造成的不必要配置。
2. **Text 用 `{len, str}` 描述子**：長度 O(1)、**不可變**、**可以包含 NUL**、不以 NUL 結尾。
3. **公開表示方式、以傳值方式傳遞**，所以函式從不配置描述子。
4. **轉換**：`Text_put`（複製進來）、`Text_get`（複製出去，str 是 NULL 時自動配置）、`Text_box`（包裝，不複製，記得扣掉 NUL）。
5. **`Text_sub` 零配置**，所以大多數函式不需要位置參數；分析函式仍然保留位置，用來記錄掃描狀態。
6. **字串空間由 Text 管理**，client 不能自己釋放；用 `Text_save`/`Text_restore` 做堆疊式回收。
7. **實作的核心**：沒有標頭的 arena 配置器加上 `isatend` → `Text_cat`/`Text_dup` 盡量不複製，例如相鄰時直接合併、在尾端時只接上新的部分。
8. **細節**：六個常數描述子共用 `cset`；`Text_save` 用 `alloc(1)` 製造洞；`Text_map` 需要 `inited` 旗標；改用 `mem*` 函式處理 NUL；`Text_fmt` 傳指標以確保可攜性。

> **一句話**：Text 用「長度 + 指標」的不可變描述子取代以 NUL 結尾的字串，讓子字串可以共用、串接常常不用複製，再用 arena 式的字串空間成批回收，是一個以表示方式換取效率的典範。
