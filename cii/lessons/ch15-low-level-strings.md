# 第 15 章　Low-Level Strings（低階字串）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.241–267

---

## 1. 本章定位

### 1.1 C 的字串

C 本身不是字串處理語言，但它能操作字元陣列，一般稱為**字串**。依照慣例，**N 個字元的字串是 N+1 個字元的陣列，最後一個是 NUL**（值為 0）。

語言本身只有兩個功能幫得上忙：
1. **字元指標**可以走訪字元陣列。
2. **字串常值**可以初始化字元陣列。

```c
char msg[] = "File not found";
/* 等同於 */
char msg[] = { 'F','i','l','e',' ','n','o','t',' ','f','o','u','n','d','\0' };

char *msg = "File not found";
/* 等同於（t376 是編譯器產生的內部名稱）*/
static char t376[] = "File not found";
char *msg = t376;
```

- **小知識**：`'F'` 這種字元常數的型別是 **`int`**，不是 `char`，所以 `sizeof 'F' == sizeof (int)`。
- 字串常值可以用在任何能用**唯讀陣列名稱**的地方，例如第 14 章的 `"0123456789abcdef"[m&0xf]`。

### 1.2 ⭐ `string.h` 的兩個缺點

以 `strcat(char *dst, const char *src)` 為例：

1. **client 必須自己配置結果的空間**（例如 `dst`）。
2. **最重要的是：這些函式都不安全**。沒有一個能檢查結果字串夠不夠大；`dst` 不夠大時，`strcat` 會寫到沒有配置的記憶體，或是別的資料用的記憶體。
   - `strncat` 這類函式多了限制字元數的參數，有幫助，但**仍然可能發生配置錯誤**。

### 1.3 `Str` 的做法

- **大多數 `Str` 函式自己配置結果的空間**，因此比 `string.h` 安全。
- **配置的成本就是安全的代價。** 不過這些配置往往本來就需要，因為結果大小取決於計算結果時，`string.h` 的 client 也得自己配置。
- client **仍然要負責釋放**結果。
- 提供方便的方式操作參數字串的**子字串**。
- 下一章的 `Text` 提供另一組函式，可以**避免一部分配置的成本**。

---

## 2. ⭐ 位置（Position）：本章的核心概念

### 2.1 定義

和第 12 章 Ring 的位置一樣，**字串位置指的是字元之間的位置**，包括最後一個字元之後的位置：

```
正位置：    1   2   3   4   5   6   7   8   9   10
            ↓   ↓   ↓   ↓   ↓   ↓   ↓   ↓   ↓   ↓
字元：        I   n   t   e   r   f   a   c   e
            ↑   ↑   ↑   ↑   ↑   ↑   ↑   ↑   ↑   ↑
非正位置： −9  −8  −7  −6  −5  −4  −3  −2  −1   0
```

- **正位置**從**左端**算起：位置 1 是第一個字元的左邊。
- **非正位置**從**右端**算起：位置 0 是最後一個字元的右邊。

### 2.2 子字串記法 `s[i:j]`

兩個位置 i、j 指定它們**之間**的子字串，記作 **`s[i:j]`**。

若 `s` 是 `"Interface"`：

| 記法 | 結果 | 說明 |
|---|---|---|
| `s[-4:0]` | `face` | 從右邊數 |
| `s[0:-4]` | `face` | **順序可以顛倒** |
| `s[6:10]` | `face` | 從左邊數 |
| `s[3:3]` | （空） | n 和 t 之間的**空子字串** |
| `s[3:-7]` | （空） | 同上，用兩種記法表示同一個位置 |
| `s[i:i+1]` | 位置 i 右邊的字元 | 除了最右邊的位置以外 |
| `s[1:0]` | `Interface` | **整個字串** |

### 2.3 ⭐ 為什麼用位置，而不用索引？

用**字元索引**（0 到 9）指定子字串看起來比較自然，但有一些麻煩：

- **順序很重要**：用索引時，兩個索引的先後不能顛倒。
- 如果規定「子字串從第一個索引之後開始、在第二個索引之前結束」：
  - `s[1..6]` 是 `terf`。
  - 要表示 `face` 就得用 `s[4..9]`，而 9 是 **NUL 字元的索引**，這個慣例必須允許它。
  - 而且**沒辦法表示開頭的空子字串**。
- 如果改成「子字串在第二個索引**之後**結束」，就**沒辦法表示空子字串**。
- 其他用負索引的慣例也可以，但比位置更麻煩。

> **位置避免了這些令人困惑的邊界情況。** 而且**非正位置可以存取字串尾端，而不需要知道它的長度**。

> 這套表示法來自 **Icon** 語言。Python 的切片 `s[i:j]` 和負索引也是類似的概念。

---

## 3. 介面（15.1 Interface）

```c
/* str.h */
#ifndef STR_INCLUDED
#define STR_INCLUDED
#include <stdarg.h>

/* 建立字串（都會配置記憶體）*/
extern char *Str_sub    (const char *s, int i, int j);
extern char *Str_dup    (const char *s, int i, int j, int n);
extern char *Str_cat    (const char *s1, int i1, int j1,
                         const char *s2, int i2, int j2);
extern char *Str_catv   (const char *s, ...);
extern char *Str_reverse(const char *s, int i, int j);
extern char *Str_map    (const char *s, int i, int j,
                         const char *from, const char *to);

/* 查詢資訊（不配置）*/
extern int Str_pos(const char *s, int i);
extern int Str_len(const char *s, int i, int j);
extern int Str_cmp(const char *s1, int i1, int j1,
                   const char *s2, int i2, int j2);

/* 搜尋 */
extern int Str_chr  (const char *s, int i, int j, int c);
extern int Str_rchr (const char *s, int i, int j, int c);
extern int Str_upto (const char *s, int i, int j, const char *set);
extern int Str_rupto(const char *s, int i, int j, const char *set);
extern int Str_find (const char *s, int i, int j, const char *str);
extern int Str_rfind(const char *s, int i, int j, const char *str);

/* 跨越（step over）*/
extern int Str_any   (const char *s, int i, const char *set);
extern int Str_many  (const char *s, int i, int j, const char *set);
extern int Str_rmany (const char *s, int i, int j, const char *set);
extern int Str_match (const char *s, int i, int j, const char *str);
extern int Str_rmatch(const char *s, int i, int j, const char *str);

/* Fmt 轉換函式 */
extern void Str_fmt(int code, va_list *app,
    int put(int c, void *cl), void *cl,
    unsigned char flags[], int width, int precision);

#undef T
#endif
```

所有字串參數都是**以 NUL 結尾的字元陣列加上位置**。

**通則**：
- 傳 NULL 的字串指標給任何函式都是 checked runtime error（`Str_catv` 和 `Str_map` 的例外見下）。
- 傳入的 i、j 不能指定 s 裡的子字串，是 checked runtime error。

### 3.1 建立字串的函式

這些函式**都會配置結果的空間**，也**都可能丟出 `Mem_Failed`**。

| 函式 | 功能 | 範例 |
|---|---|---|
| `Str_sub(s, i, j)` | 回傳 `s[i:j]` | `Str_sub("Interface", 6, 10)` → `face` |
| `Str_dup(s, i, j, n)` | 回傳 n 份 `s[i:j]` 的串接；**常用來複製字串** | `Str_dup("Interface", 1, 0, 1)` → 複本 |
| `Str_cat(s1, i1, j1, s2, i2, j2)` | 串接 `s1[i1:j1]` 和 `s2[i2:j2]` | |
| `Str_catv(s, i, j, ..., NULL)` | 串接**零個或多個**（字串, i, j）三元組，以 NULL 結束 | `Str_catv("Interface", -4, 0, " plant", 1, 0, NULL)` → `face plant` |
| `Str_reverse(s, i, j)` | `s[i:j]` 反轉 | |
| `Str_map(s, i, j, from, to)` | 依 from→to 對應轉換字元 | 見下 |

`Str_sub("Interface", 6, 10)`、`(6, 0)`、`(-4, 10)`、`(-4, 0)` **全都回傳 `face`**。`Str_dup` 的 n 是負數是 checked runtime error。

**`Str_map` 的細節**：

```c
Str_map(s, 1, 0, "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                 "abcdefghijklmnopqrstuvwxyz");   /* 轉小寫 */
```

- `s[i:j]` 裡出現在 `from` 的字元，換成 `to` 裡對應位置的字元；其他字元不變。
- **`from` 和 `to` 都是 NULL**：使用**最近一次**呼叫設定的對應關係。
- **`s` 是 NULL**：忽略 i、j，只用 from、to **設定預設的對應關係**，並回傳 NULL。
- **Checked runtime error**：from 和 to 只有一個是 NULL；兩者長度不同；s、from、to 全部是 NULL；**第一次呼叫**時 from 和 to 都是 NULL。

### 3.2 查詢資訊的函式（不配置）

| 函式 | 功能 |
|---|---|
| `Str_pos(s, i)` | 回傳 `s[i:i]` 對應的**正位置**。正位置減 1 就是索引，所以需要索引時常用它 |
| `Str_len(s, i, j)` | `s[i:j]` 的字元數 |
| `Str_cmp(s1, i1, j1, s2, i2, j2)` | 依字典順序比較兩個子字串，回傳 `<0`、`0`、`>0` |

```c
/* s 是 "Interface" */
printf("%s\n", &s[Str_pos(s, -4)-1]);   /* 印出 face */
```

### 3.3 搜尋函式

成功時回傳**正位置**，失敗時回傳 **0**。名稱有 **`r`** 的函式**從右邊**開始搜尋，其他從左邊開始搜尋。

| 函式 | 尋找 | 回傳 |
|---|---|---|
| `Str_chr` / `Str_rchr` | 字元 c 最左邊或最右邊的出現 | 該字元**左邊**的位置 |
| `Str_upto` / `Str_rupto` | `set` 中**任一**字元最左邊或最右邊的出現 | 該字元**左邊**的位置 |
| `Str_find` / `Str_rfind` | 字串 `str` 最左邊或最右邊的出現 | 該字串**左邊**的位置 |

`set` 或 `str` 是 NULL 是 checked runtime error。

```c
Str_find ("The rain in Spain", 1, 0, "rain")   /* 5 */
Str_rfind("The rain in Spain", 1, 0, "rain")   /* 5，只出現一次 */
Str_find ("The rain in Spain", 1, 0, "in")     /* 7 */
Str_rfind("The rain in Spain", 1, 0, "in")     /* 16，in 出現三次 */
```

> 注意：`r` 系列**從右邊找**，但**回傳的仍然是目標左邊的位置**。

### 3.4 ⭐ 跨越函式（step over）

這些函式**不搜尋**，而是在子字串的**開頭或結尾**「跨過」符合的部分，回傳跨過之後的位置。

| 函式 | 行為 | 回傳 |
|---|---|---|
| `Str_any(s, i, set)` | 字元 `s[i:i+1]` 在 set 裡嗎？ | 是就回傳該字元**之後**的位置，否則回傳 0 |
| `Str_many(s, i, j, set)` | 跨過 `s[i:j]` **開頭**一段連續、屬於 set 的字元（至少一個） | 那段字元**之後**的位置 |
| `Str_rmany(s, i, j, set)` | 跨過 `s[i:j]` **結尾**一段連續、屬於 set 的字元 | 那段字元**之前**的位置 |
| `Str_match(s, i, j, str)` | `s[i:j]` 以 str **開頭**嗎？ | str **之後**的位置 |
| `Str_rmatch(s, i, j, str)` | `s[i:j]` 以 str **結尾**嗎？ | str **之前**的位置 |

**規則**：`many` 和 `match` **向右走**，回傳跨過的字元**之後**的位置；`rmany` 和 `rmatch` **向左走**，回傳跨過的字元**之前**的位置。

```c
/* 去掉尾端的空白和 tab */
Str_sub(name, 1, Str_rmany(name, 1, 0, " \t"));
```

> ⚠ 如果 name 結尾**沒有**空白，`Str_rmany` 回傳 0，`Str_sub(name, 1, 0)` 剛好就是**整個字串**。位置 0 代表「最右邊」，這個設計讓失敗的情況也自然地得到正確結果。

### 3.5 範例：`basename`

```c
char *basename(char *path, int i, int j, const char *suffix) {
    i = Str_rchr(path, i, j, '/');          /* 最右邊 '/' 的左邊位置，沒有就回傳 0 */
    j = Str_rmatch(path, i + 1, 0, suffix); /* 後綴之前的位置，沒有後綴就回傳 0 */
    return Str_dup(path, i + 1, j, 1);
}
```

| 呼叫 | 結果 |
|---|---|
| `basename("/usr/jenny/main.c", 1, 0, ".c")` | `main` |
| `basename("../src/main.c", 1, 0, "")` | `main.c` |
| `basename("main.c", 1, 0, "c")` | `main.` |
| `basename("main.c", 1, 0, ".obj")` | `main.c` |
| `basename("examples/wfmain.c", 1, 0, "main.c")` | `wf` |

**巧妙之處**：
- 有 `/` 時，i 是 `/` 左邊的位置，檔名從 `i + 1` 開始。
- **沒有 `/` 時 i = 0，`i + 1 = 1`，剛好就是字串開頭。**
- 有後綴時 j 是後綴之前的位置；**沒有後綴時 j = 0，剛好就是字串結尾。**
- ⇒ **失敗回傳 0 的設計，讓每種情況都不用特別處理。**

### 3.6 `Str_fmt`：搭配 Fmt 使用

```c
extern void Str_fmt(int code, va_list *app,
    int put(int c, void *cl), void *cl,
    unsigned char flags[], int width, int precision);
```

- 一個**符合 `Fmt_T` 的轉換函式**，用來格式化**子字串**。
- **消耗三個參數**：字串指標和兩個位置；格式化方式和 `%s` 相同。
- 字串指標、`app` 或 `flags` 是 NULL，是 checked runtime error。

```c
Fmt_register('S', Str_fmt);
Fmt_print("%10S\n", "Interface", -4, 0);   /* 印出 "      face" */
```

---

## 4. 範例：印出識別字 `ids`（15.2）

```c
#include <stdlib.h>
#include <stdio.h>
#include "fmt.h"
#include "str.h"

int main(int argc, char *argv[]) {
    char line[512];
    static char set[] = "0123456789_"
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    Fmt_register('S', Str_fmt);
    while (fgets(line, sizeof line, stdin) != NULL) {
        int i = 1, j;
        while ((i = Str_upto(line, i, 0, &set[10])) > 0) {  /* 找識別字的開頭 */
            j = Str_many(line, i, 0, set);                  /* 跨過整個識別字 */
            Fmt_print("%S\n", line, i, j);                   /* 直接印出子字串 */
            i = j;
        }
    }
    return EXIT_SUCCESS;
}
```

- **`&set[10]`**：跳過前 10 個數字字元，剩下的是「底線 + 字母」，也就是**識別字開頭可以用的字元**。`set` 全部則是「識別字中可以用的字元」。**同一個陣列兩種用法**。
- `Str_upto` 找到下一個識別字的開頭 → `Str_many` 跨過整個識別字 → 印出 `line[i:j]` → 從 j 繼續。

```
            j: 4     9   13      18     24      30
               int main (int argc , char *argv []) {
            i: 1     5   10      14     20      26
```

> **這個程式完全沒有配置記憶體。** 用位置操作子字串，常常可以在這類應用中**避免配置**；`Str_fmt` 直接印出子字串，連複製都不需要。

---

## 5. 實作（15.3 Implementation）

### 5.1 ⭐ 位置 → 索引的轉換

函式內部要用**索引**存取字元，所以需要把位置轉成索引：
- 正位置 i 右邊字元的索引是 **i − 1**。
- 負位置 i 右邊字元的索引是 **i + len**。

```c
#define idx(i, len) ((i) <= 0 ? (i) + (len) : (i) - 1)

#define convert(s, i, j) do { int len; \
    assert(s); len = strlen(s); \
    i = idx(i, len); j = idx(j, len); \
    if (i > j) { int t = i; i = j; j = t; } \
    assert(i >= 0 && j <= len); } while (0)
```

- `convert` 把 i、j 轉成 **0 到 len** 之間的索引，**必要時交換**，確保 i ≤ j。
- 最後的 assert 實作「i、j 必須是合法位置」這個 checked runtime error。
- 轉換之後，**`j − i` 就是子字串的長度**。
- 結尾位置轉成的是「子字串後面那個字元」的索引，**可能就是 NUL**，所以 assert 允許 `j == len`。

### 5.2 建立字串

```c
char *Str_sub(const char *s, int i, int j) {
    char *str, *p;
    convert(s, i, j);
    p = str = ALLOC(j - i + 1);       /* 長度 + NUL */
    while (i < j)
        *p++ = s[i++];
    *p = '\0';
    return str;
}

char *Str_dup(const char *s, int i, int j, int n) {
    int k;
    char *str, *p;
    assert(n >= 0);
    convert(s, i, j);
    p = str = ALLOC(n*(j - i) + 1);
    if (j - i > 0)
        while (n-- > 0)
            for (k = i; k < j; k++)
                *p++ = s[k];
    *p = '\0';
    return str;
}

char *Str_reverse(const char *s, int i, int j) {
    char *str, *p;
    convert(s, i, j);
    p = str = ALLOC(j - i + 1);
    while (j > i)
        *p++ = s[--j];                /* 倒著複製 */
    *p = '\0';
    return str;
}

char *Str_cat(const char *s1, int i1, int j1,
              const char *s2, int i2, int j2) {
    char *str, *p;
    convert(s1, i1, j1);
    convert(s2, i2, j2);
    p = str = ALLOC(j1 - i1 + j2 - i2 + 1);
    while (i1 < j1)
        *p++ = s1[i1++];
    while (i2 < j2)
        *p++ = s2[i2++];
    *p = '\0';
    return str;
}
```

`Str_cat` 其實可以直接呼叫 `Str_catv`，但它**太常用了**，值得一個量身打造的實作。

### 5.3 `Str_catv`：走訪參數兩次

```c
char *Str_catv(const char *s, ...) {
    char *str, *p;
    const char *save = s;
    int i, j, len = 0;
    va_list ap;

    va_start(ap, s);
    while (s) {                           /* 第一輪：計算總長度 */
        i = va_arg(ap, int);
        j = va_arg(ap, int);
        convert(s, i, j);
        len += j - i;
        s = va_arg(ap, const char *);
    }
    va_end(ap);

    p = str = ALLOC(len + 1);             /* 一次配置剛好的大小 */

    s = save;
    va_start(ap, s);
    while (s) {                           /* 第二輪：複製 */
        i = va_arg(ap, int);
        j = va_arg(ap, int);
        convert(s, i, j);
        while (i < j)
            *p++ = s[i++];
        s = va_arg(ap, const char *);
    }
    va_end(ap);
    *p = '\0';
    return str;
}
```

- **可變參數可以重新 `va_start` 再走訪一次**，前提是先 `va_end`。
- 第一輪算出長度，**一次配置剛好的大小**，第二輪複製。

### 5.4 `Str_map`：查表轉換

```c
char *Str_map(const char *s, int i, int j,
        const char *from, const char *to) {
    static char map[256] = { 0 };          /* 跨呼叫保留的對應表 */
    if (from && to) {
        /* rebuild map */
        unsigned c;
        for (c = 0; c < sizeof map; c++)
            map[c] = c;                    /* 先設成「對應到自己」 */
        while (*from && *to)
            map[(unsigned char)*from++] = *to++;
        assert(*from == 0 && *to == 0);    /* 長度必須相同 */
    } else {
        assert(from == NULL && to == NULL && s);
        assert(map['a']);                  /* 第一次呼叫不可以兩個都是 NULL */
    }
    if (s) {
        /* map s[i:j] into a new string */
        char *str, *p;
        convert(s, i, j);
        p = str = ALLOC(j - i + 1);
        while (i < j)
            *p++ = map[(unsigned char)s[i++]];   /* 轉 unsigned char 避免負數索引 */
        *p = '\0';
        return str;
    } else
        return NULL;
}
```

**⭐ 用 `map['a']` 判斷是否初始化過的技巧**：
- `map` 一開始全部是 0。
- 用 `Str_map` **不可能把字元對應到 NUL**，因為 `to` 是 C 字串，不能包含 NUL。
- 所以只要初始化過，`map['a']` 一定**不是 0**，不需要另外的旗標變數。
- （第 16 章的 `Text_map` 允許對應到 NUL，就必須用一個 `inited` 旗標。）

### 5.5 查詢資訊

```c
int Str_pos(const char *s, int i) {
    int len;
    assert(s);
    len = strlen(s);
    i = idx(i, len);
    assert(i >= 0 && i <= len);
    return i + 1;                         /* 索引 + 1 = 正位置 */
}

int Str_len(const char *s, int i, int j) {
    convert(s, i, j);
    return j - i;
}

int Str_cmp(const char *s1, int i1, int j1,
            const char *s2, int i2, int j2) {
    convert(s1, i1, j1);
    convert(s2, i2, j2);
    s1 += i1;                             /* 直接指向子字串的開頭 */
    s2 += i2;
    if (j1 - i1 < j2 - i2) {              /* s1 比較短 */
        int cond = strncmp(s1, s2, j1 - i1);
        return cond == 0 ? -1 : cond;     /* 是 s2 的前綴 → 比較小 */
    } else if (j1 - i1 > j2 - i2) {       /* s1 比較長 */
        int cond = strncmp(s1, s2, j2 - i2);
        return cond == 0 ? +1 : cond;
    } else
        return strncmp(s1, s2, j1 - i1);
}
```

**⚠ `strncmp` 的可攜性陷阱**：
- 標準規定 `strncmp`（和 `memcmp`）必須把字元當成 **unsigned char** 比較，所以字元值大於 127 時結果是定義清楚的。例如 `strncmp("\344", "\127", 1)` 必須回傳**正數**。
- 但**有些實作錯誤地比較 plain char**（可能是有號的），會回傳負數。有些 `memcmp` 也有同樣的錯誤。

### 5.6 搜尋

```c
int Str_chr(const char *s, int i, int j, int c) {
    convert(s, i, j);
    for ( ; i < j; i++)
        if (s[i] == c)
            return i + 1;          /* 該字元左邊的正位置 */
    return 0;
}

int Str_rchr(const char *s, int i, int j, int c) {
    convert(s, i, j);
    while (j > i)
        if (s[--j] == c)
            return j + 1;
    return 0;
}

int Str_upto(const char *s, int i, int j, const char *set) {
    assert(set);
    convert(s, i, j);
    for ( ; i < j; i++)
        if (strchr(set, s[i]))     /* s[i] 在 set 裡嗎？ */
            return i + 1;
    return 0;
}
```

`Str_rupto` 和 `Str_rchr` 對稱。

```c
int Str_find(const char *s, int i, int j, const char *str) {
    int len;
    convert(s, i, j);
    assert(str);
    len = strlen(str);
    if (len == 0)
        return i + 1;                         /* 空字串：一定成功 */
    else if (len == 1) {                      /* 一個字元：等同於 Str_chr */
        for ( ; i < j; i++)
            if (s[i] == *str)
                return i + 1;
    } else
        for ( ; i + len <= j; i++)            /* 不能超出子字串的結尾 */
            if (strncmp(&s[i], str, len) == 0)
                return i + 1;
    return 0;
}

int Str_rfind(const char *s, int i, int j, const char *str) {
    int len;
    convert(s, i, j);
    assert(str);
    len = strlen(str);
    if (len == 0)
        return j + 1;
    else if (len == 1) {
        while (j > i)
            if (s[--j] == *str)
                return j + 1;
    } else
        for ( ; j - len >= i; j--)            /* 不能超出子字串的開頭 */
            if (strncmp(&s[j-len], str, len) == 0)
                return j - len + 1;
    return 0;
}
```

- **長度 0 和 1 特別處理**：空字串一定成功；單一字元直接比較，比呼叫 `strncmp` 快。
- 一般情況**不能接受延伸到子字串邊界之外的符合**，這是迴圈條件 `i + len <= j` 和 `j - len >= i` 的作用。

### 5.7 跨越

```c
int Str_any(const char *s, int i, const char *set) {
    int len;
    assert(s);
    assert(set);
    len = strlen(s);
    i = idx(i, len);
    assert(i >= 0 && i <= len);
    if (i < len && strchr(set, s[i]))
        return i + 2;              /* 索引 i+1 轉成正位置要再 +1 */
    return 0;
}

int Str_many(const char *s, int i, int j, const char *set) {
    assert(set);
    convert(s, i, j);
    if (i < j && strchr(set, s[i])) {
        do
            i++;
        while (i < j && strchr(set, s[i]));
        return i + 1;
    }
    return 0;
}

int Str_rmany(const char *s, int i, int j, const char *set) {
    assert(set);
    convert(s, i, j);
    if (j > i && strchr(set, s[j-1])) {
        do
            --j;
        while (j >= i && strchr(set, s[j]));
        return j + 2;
    }
    return 0;
}
```

**`Str_any` 為什麼回傳 `i + 2`？** 符合時要回傳**該字元之後**的位置：下一個字元的索引是 i+1，轉成正位置再加 1，所以是 i+2。

**`Str_rmany` 為什麼回傳 `j + 2`？** 迴圈結束時有兩種情況：
1. j 是一個**不在 set 裡**的字元的索引 → 要回傳它**右邊**的位置，也就是 j + 2。
2. j 等於 **i − 1**（整段都在 set 裡）→ 要回傳位置 i + 1 = (i − 1) + 2 = j + 2。

**兩種情況都是 `j + 2`。**

```c
int Str_match(const char *s, int i, int j, const char *str) {
    int len;
    convert(s, i, j);
    assert(str);
    len = strlen(str);
    if (len == 0)
        return i + 1;
    else if (len == 1) {
        if (i < j && s[i] == *str)
            return i + 2;
    } else if (i + len <= j && strncmp(&s[i], str, len) == 0)
        return i + len + 1;
    return 0;
}

int Str_rmatch(const char *s, int i, int j, const char *str) {
    int len;
    convert(s, i, j);
    assert(str);
    len = strlen(str);
    if (len == 0)
        return j + 1;
    else if (len == 1) {
        if (j > i && s[j-1] == *str)
            return j;
    } else if (j - len >= i && strncmp(&s[j-len], str, len) == 0)
        return j - len + 1;
    return 0;
}
```

### 5.8 `Str_fmt`

```c
void Str_fmt(int code, va_list *app,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    char *s;
    int i, j;
    assert(app && flags);
    s = va_arg(*app, char *);          /* 消耗三個參數 */
    i = va_arg(*app, int);
    j = va_arg(*app, int);
    convert(s, i, j);
    Fmt_puts(s + i, j - i, put, cl, flags, width, precision);
}
```

**重點**：一個轉換函式可以**消耗多個參數**。位置算出子字串的長度，再交給 `Fmt_puts` 依照 flags、width、precision 輸出。這正是第 14 章 `Fmt_puts` 存在的理由。

---

## 6. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **安全優先** | 結果由函式自己配置，不會溢位；代價是配置的成本 |
| **⭐ 位置取代索引** | 消除邊界情況；可以從尾端存取；順序可以顛倒；能表示空子字串 |
| **失敗回傳 0** | 位置 0 剛好代表「最右邊」，讓 `basename`、去除尾端空白自然正確 |
| **子字串為一級公民** | 幾乎所有函式都接受 `(s, i, j)`，不用先複製子字串 |
| **巨集統一轉換** | `idx` 和 `convert` |
| **特例最佳化** | 搜尋時長度 0、1 特別處理；`Str_cat` 自己實作 |
| **兩輪處理** | `Str_catv` 先算長度、一次配置、再複製 |
| **利用值域特性省掉旗標** | `map['a'] != 0` 代表初始化過 |
| **和 Fmt 整合** | `Str_fmt` 消耗三個參數，印出子字串不需要配置 |
| **注意可攜性** | `unsigned char` 轉型、`strncmp` 實作的錯誤 |

### Str vs. string.h

| | string.h | Str |
|---|---|---|
| 結果空間 | client 配置 | **函式配置** |
| 溢位風險 | **有** | 沒有 |
| 子字串 | 要自己算指標和長度 | **內建** `s[i:j]` |
| 從尾端存取 | 要先 `strlen` | **非正位置** |
| 釋放 | client | client |

---

## 7. 延伸閱讀重點

- **Plauger (1992)**：簡短批評 `string.h` 的函式，並說明怎麼實作它們。
- **Roberts (1995)**：一個以 `string.h` 為基礎、和 Str 類似的簡單字串介面。
- **⭐ Str 介面幾乎原封不動地取自 Icon 語言**（Griswold & Griswold, 1990）的字串處理功能。**用位置取代索引、用非正位置表示相對於尾端的位置，都源自 Icon。**
- Icon 的函式更強大，因為有**目標導向求值（goal-directed evaluation）**：例如 `find` 可以依呼叫的情境回傳**所有**出現的位置。Icon 還有**字串掃描（string scanning）**功能，搭配目標導向求值就是很強大的模式比對工具。
- **`Str_map` 的妙用**：若 s 是 7 個字元的字串，
  ```c
  Str_map("abcdefg", 1, 0, "gfedcba", s)
  ```
  會回傳 **s 的反轉**！（把 s 當成「對應表」，用位置重新排列。）Griswold (1980) 探討了這類對應的用法。

---

## 8. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 15.1 | 擴充 `ids.c`，忽略 C 的**註解、字串常值和關鍵字**；再加上用命令列參數指定要忽略的識別字 | 實際練習用位置寫掃描器 |
| 15.2 | 盡量用 `strncpy`、`memcpy` 等 string.h 函式重新實作 Str，量測效果 | 有些編譯器會把 string.h 呼叫展開成很快的內嵌程式碼；用字串長度描述各函式的改善程度 |
| 15.3 | 設計用**正規表示式**（如 AWK 的）搜尋子字串的函式 | 需要回傳兩個值：符合的開始位置和長度 |
| 15.4 | 研究 Icon 的**字串掃描**（`?` 運算子建立掃描環境），設計提供類似功能的介面 | 隱含的「目前字串和位置」 |
| 15.5 | 設計類似 `strtok`、但**不修改參數**的函式，能改進 `strtok` 的設計嗎？ | `strtok` 會覆寫原字串，而且用靜態狀態，不能重入 |
| 15.6 | 讓 Str 函式接受**選用的目的緩衝區**（例如 `Str_dup(dst, size, ...)`），dst 是 NULL 才配置 | `size` 太小時怎麼辦？比較兩種設計哪個比較簡單、比較不容易出錯 |
| 15.7 | 另一種提議：`Str_result(dst, size)` 指定**下一次**呼叫的結果緩衝區 | 討論優缺點，例如隱藏的全域狀態 |

---

## 9. 本章重點整理

1. **string.h 的缺點**：client 要自己配置結果空間，而且**不安全**（會溢位）。
2. **Str 自己配置結果**，用配置的成本換取安全；client 仍然要釋放。
3. **⭐ 位置是字元之間的位置**：正位置 1 到 len+1 從左邊算，非正位置 −len 到 0 從右邊算。`s[i:j]` 是兩個位置之間的子字串，**順序可以顛倒**；`s[1:0]` 是整個字串。
4. **函式分類**：建立（sub/dup/cat/catv/reverse/map）、資訊（pos/len/cmp）、搜尋（chr/upto/find 和它們的 r 版本）、跨越（any/many/rmany/match/rmatch）、轉換（`Str_fmt`）。
5. **搜尋和跨越成功時回傳正位置、失敗時回傳 0**；位置 0 剛好代表「最右邊」，讓很多寫法不需要特別處理失敗的情況。
6. **實作**：`idx`/`convert` 巨集把位置轉成索引；長度 0、1 特別處理；`Str_catv` 走訪兩次；`Str_map` 用 `map['a']` 判斷是否初始化過。
7. **`ids` 範例**：用位置掃描、用 `Str_fmt` 直接印出子字串，**完全不配置記憶體**。

> **一句話**：Str 借用 Icon 的「位置」概念，讓 C 字串可以安全、方便地操作子字串。結果自己配置所以不會溢位，失敗回傳 0 的設計讓很多邊界情況自然消失。
