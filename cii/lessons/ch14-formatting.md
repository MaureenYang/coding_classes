# 第 14 章　Formatting（格式化輸出）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.215–239

---

## 1. 本章定位

### 1.1 標準 `printf` 家族

`printf`、`fprintf`、`vprintf` 把資料格式化後輸出，`sprintf`、`vsprintf` 把資料格式化到字串。格式由 **`%c` 形式的轉換符號**控制：第 i 個轉換符號描述第 i 個參數的格式，其他字元原樣複製。

```c
sprintf(buf, "The %s interface has %d functions\n", name, count);
/* → "The Array interface has 8 functions\n" */
/* 用 %06d 則得到 "... has 000008 functions\n" */
```

### 1.2 ⭐ `printf` 的四個缺點

| # | 缺點 | `Fmt` 是否解決 |
|---|---|---|
| 1 | **轉換符號是固定的**，沒辦法加入 client 自訂的格式碼 | ✅ `Fmt_register` |
| 2 | **輸出只能印出來或存進字串**，沒辦法指定 client 自訂的輸出函式 | ✅ `put` 函式加上 `cl` |
| 3 | **最危險**：`sprintf`/`vsprintf` 可能寫入超過字串容量的字元，**沒辦法指定輸出字串的大小** | ✅ `Fmt_sfmt` 會丟出例外；`Fmt_string` 會自動配置 |
| 4 | 可變參數部分**沒有型別檢查** | ❌ 這是 C 語言本身的限制 |

> `Fmt` 解決了前三個問題。

---

## 2. 介面（14.1 Interface）

```c
/* fmt.h */
#ifndef FMT_INCLUDED
#define FMT_INCLUDED
#include <stdarg.h>
#include <stdio.h>
#include "except.h"

#define T Fmt_T
typedef void (*T)(int code, va_list *app,
    int put(int c, void *cl), void *cl,
    unsigned char flags[256], int width, int precision);

extern char *Fmt_flags;
extern const Except_T Fmt_Overflow;

extern void  Fmt_fmt    (int put(int c, void *cl), void *cl, const char *fmt, ...);
extern void  Fmt_vfmt   (int put(int c, void *cl), void *cl, const char *fmt, va_list ap);
extern void  Fmt_print  (const char *fmt, ...);
extern void  Fmt_fprint (FILE *stream, const char *fmt, ...);
extern int   Fmt_sfmt   (char *buf, int size, const char *fmt, ...);
extern int   Fmt_vsfmt  (char *buf, int size, const char *fmt, va_list ap);
extern char *Fmt_string (const char *fmt, ...);
extern char *Fmt_vstring(const char *fmt, va_list ap);
extern T     Fmt_register(int code, T cvt);
extern void  Fmt_putd(const char *str, int len,
                 int put(int c, void *cl), void *cl,
                 unsigned char flags[256], int width, int precision);
extern void  Fmt_puts(const char *str, int len,
                 int put(int c, void *cl), void *cl,
                 unsigned char flags[256], int width, int precision);

#undef T
#endif
```

匯出 **11 個函式、1 個型別、1 個變數、1 個例外**。

> 嚴格來說 **Fmt 不是 ADT**。它匯出的型別 `Fmt_T` 是**轉換函式的型別**，也就是每個格式碼對應的處理函式的簽名。

### 2.1 核心函式：`Fmt_fmt` / `Fmt_vfmt`

```c
extern void Fmt_fmt (int put(int c, void *cl), void *cl, const char *fmt, ...);
extern void Fmt_vfmt(int put(int c, void *cl), void *cl, const char *fmt, va_list ap);
```

- 依照 `fmt` 格式化參數，**每產生一個字元 c 就呼叫一次 `put(c, cl)`**。
- c 被當成 `unsigned char`，所以傳給 `put` 的值**一定是正數**。
- `cl` 是 client 的資料，**原封不動**地轉交給 `put`（又是閉包模式）。
- `put` 回傳一個整數，通常就是它的參數。Fmt 本身不用這個回傳值，但這樣設計讓 **`fputc` 可以直接當 `put` 用**：

```c
Fmt_fmt((int (*)(int, void *))fputc, stdout,
    "The %s interface has %d functions\n", name, count);
```

> 需要轉型，因為 `fputc` 的型別是 `int (*)(int, FILE*)`。**只有在 `FILE *` 和 `void *` 表示方式相同的機器上才正確。**

> **`put` + `cl` 的設計，讓輸出可以導向任何地方**：檔案、字串、網路、一個計算長度的函式……這解決了缺點 #2。

### 2.2 ⭐ 轉換符號的語法

```
%  [flags]  [width]  [. precision]  C
             ↑           ↑
          數字或 *     數字或 *
```

- **flags**：可以用的旗標字元是 **`Fmt_flags`** 字串裡的字元，預設是 `"-+ 0"`。旗標的**意義由格式碼決定**。同一個旗標在一個轉換符號裡出現超過 255 次是 checked runtime error。
- **width / precision**：可以是數字，或是 **`*`**，代表從下一個 `int` 參數取值。
  ⇒ 一個轉換符號可能消耗**零個或多個**參數。
- width 或 precision 的值是 **`INT_MIN`** 是 checked runtime error，因為 `INT_MIN` 被保留用來表示「沒有指定」。
- **C**：單一字元的格式碼。

### 2.3 預設旗標的意義

| 旗標 | 意義 |
|---|---|
| `-` | **靠左**對齊（預設靠右） |
| `+` | 有號轉換一律顯示 `+` 或 `-` |
| 空白 | 有號轉換是正數時前面加一個空白 |
| `0` | 數值轉換用**前導零**補滿寬度（預設用空白） |

- **負的寬度**等於 `-` 旗標加上對應的正寬度。
- **負的精確度**等於沒有指定精確度。

### 2.4 預設格式碼（printf 的子集）

| 碼 | 參數型別 | 說明 |
|---|---|---|
| `c` | `int` | 當成 unsigned char 輸出 |
| `d` | `int` | 有號十進位。precision 是**最少位數**（補前導零），預設 1。有 `-` 或有 precision 時忽略 `0`；同時有 `+` 和空白時忽略空白。**值和 precision 都是 0 時不輸出任何字元** |
| `o` `u` `x` | `unsigned` | 八進位、十進位、十六進位（小寫 abcdef）。旗標和 precision 同 `d` |
| `f` | `double` | `x.y` 形式。precision 是小數位數，預設 6；明確指定 0 時省略小數點。**precision 不可超過 99** |
| `e` | `double` | `x.ye±p`，x 一定是一位數，p 一定是兩位數 |
| `g` | `double` | 依值選擇 `f` 或 `e` 形式。precision 是有效位數，預設 1；去掉尾端的 0。**precision 不可超過 99** |
| `p` | `void *` | 指標的十六進位表示 |
| `s` | `char *` | 輸出字元直到 NUL，或輸出 precision 個字元；**除了 `-` 以外的旗標都忽略** |

### 2.5 對應標準函式庫的便利函式

| Fmt | 對應 | 說明 |
|---|---|---|
| `Fmt_print(fmt, ...)` | `printf` | 輸出到 stdout |
| `Fmt_fprint(stream, fmt, ...)` | `fprintf` | 輸出到指定的 stream |
| `Fmt_sfmt(buf, size, fmt, ...)` | `sprintf` | **有大小限制**，見下 |
| `Fmt_vsfmt(buf, size, fmt, ap)` | `vsprintf` | 同上，參數來自 `va_list` |
| `Fmt_string(fmt, ...)` | — | **自動配置**剛好夠大的字串 |
| `Fmt_vstring(fmt, ap)` | — | 同上 |

**⭐ `Fmt_sfmt` / `Fmt_vsfmt`：安全的 sprintf**
- 把結果存成以 NUL 結尾的字串，放在 `buf[0..size-1]`。
- 回傳存進去的字元數（**不含** NUL）。
- **輸出超過 `size` 個字元（含 NUL）時丟出 `Fmt_Overflow`**，而不是寫到緩衝區外面。
- `size` 不是正數是 checked runtime error。

**⭐ `Fmt_string` / `Fmt_vstring`：完全不用管大小**
- **自動配置**一個剛好裝得下結果的字串並回傳。
- **client 負責釋放**；可能丟出 `Mem_Failed`。

> 這兩組函式解決了缺點 #3，也就是 `sprintf` 的緩衝區溢位，這是 C 程式最常見的安全漏洞來源之一。

**通則**：傳 NULL 的 `put`、`buf` 或 `fmt` 給任何格式化函式都是 checked runtime error。

### 2.6 ⭐ 自訂轉換函式：`Fmt_register`

```c
extern T Fmt_register(int code, T cvt);
```

- 把 `cvt` 安裝成格式字元 `code` 的轉換函式，**回傳舊的函式**。
  ⇒ client 可以**暫時**覆蓋某個轉換函式，之後再恢復。
- `code` 不在 1 到 255 之間是 checked runtime error。
- 格式字串用到**沒有對應轉換函式**的格式碼，也是 checked runtime error。
- 使用的是**呼叫 `Fmt_fmt` 當時**已經註冊的函式。

> 這解決了缺點 #1：可以為自己的資料型別加入格式碼，例如用 `%T` 印出一個 Text、用 `%B` 印出一個位元向量（習題 14.4）。

### 2.7 轉換函式的簽名 `Fmt_T`

```c
typedef void (*Fmt_T)(int code, va_list *app,
    int put(int c, void *cl), void *cl,
    unsigned char flags[256], int width, int precision);
```

| 參數 | 意義 |
|---|---|
| `code` | 格式碼字元 |
| `app` | **指向** `va_list` 的指標，用來取得要格式化的參數 |
| `put`, `cl` | client 的輸出函式和它的資料 |
| `flags` | **256 個元素**的陣列，第 i 個元素是旗標字元 i 出現的**次數** |
| `width`, `precision` | 沒有明確指定時等於 **`INT_MIN`** |

**取得參數**：

```c
va_arg(*app, type)   /* 取值並讓 *app 指向下一個參數 */
```

**為什麼傳 `va_list *` 而不是 `va_list`？** 因為轉換函式取出參數後，`*app` 必須**前進**，讓呼叫端（`Fmt_vfmt`）接下來能取到**下一個**參數。傳值的話，前進的效果會遺失。

**轉換函式錯誤地前進 `*app`（例如型別不對、取太多或太少）是 unchecked runtime error。**

### 2.8 輔助函式：`Fmt_putd` 和 `Fmt_puts`

很多轉換函式只是 `%d` 和 `%s` 的變形，所以 Fmt 匯出兩個內部使用的工具：

| 函式 | 功能 |
|---|---|
| `Fmt_putd(str, len, put, cl, flags, width, precision)` | 假設 `str[0..len-1]` 是**有號數字的字串表示**，依 `%d` 的規則輸出（符號、補零、對齊） |
| `Fmt_puts(str, len, put, cl, flags, width, precision)` | 依 `%s` 的規則輸出（截斷、對齊） |

- 它們**本身不是轉換函式**，但轉換函式可以呼叫它們，**撰寫 client 自訂的轉換函式時最有用**。
- 傳 NULL 的 `str`、負的 `len`、NULL 的 `flags` 或 NULL 的 `put`，是 checked runtime error。

**範例：Fmt 內部 `%s` 的轉換函式**

```c
static void cvt_s(int code, va_list *app,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    char *str = va_arg(*app, char *);
    assert(str);
    Fmt_puts(str, strlen(str), put, cl, flags, width, precision);
}
```

**自訂轉換函式的典型寫法**：用 `va_arg` 取出自己的型別 → 轉成字串 → 交給 `Fmt_puts` 或 `Fmt_putd` 處理對齊和填充。

---

## 3. 實作（14.2 Implementation）

### 3.1 `Fmt_puts` 與正規化

```c
void Fmt_puts(const char *str, int len,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    assert(str);
    assert(len >= 0);
    assert(flags);
    /* normalize width and flags */
    if (width == INT_MIN)
        width = 0;                /* 沒指定寬度 = 寬度 0 */
    if (width < 0) {
        flags['-'] = 1;           /* 負寬度 = 靠左 + 正寬度 */
        width = -width;
    }
    if (precision >= 0)
        flags['0'] = 0;           /* 有 precision 就忽略 0 旗標 */

    if (precision >= 0 && precision < len)
        len = precision;          /* 截斷 */
    if (!flags['-'])
        pad(width - len, ' ');    /* 靠右：先補空白 */
    {
        int i;
        for (i = 0; i < len; i++)
            put((unsigned char)*str++, cl);   /* 轉 unsigned char，保證是正數 */
    }
    if (flags['-'])
        pad(width - len, ' ');    /* 靠左：後補空白 */
}

#define pad(n,c) do { int nn = (n); \
    while (nn-- > 0) \
        put((c), cl); } while (0)
```

- **介面很一般化**：轉換函式能區分「沒指定」、「明確指定」和「重複的旗標」。
- **預設轉換不需要這麼一般**，所以先**正規化**：沒指定寬度就當成 0、負寬度就當成 `-` 加上正寬度、負的 precision 當成沒指定、重複的旗標當成一次。
- `pad` 寫成**巨集**而不是函式，因為它要用到呼叫端的 `put` 和 `cl`。
- `nn` 先接收 `(n)` 的值，確保 `n` **只求值一次**。

### 3.2 所有格式化函式最後都呼叫 `Fmt_vfmt`

```c
void Fmt_fmt(int put(int c, void *), void *cl, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    Fmt_vfmt(put, cl, fmt, ap);
    va_end(ap);
}

static int outc(int c, void *cl) {
    FILE *f = cl;
    return putc(c, f);
}

void Fmt_print(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    Fmt_vfmt(outc, stdout, fmt, ap);
    va_end(ap);
}

void Fmt_fprint(FILE *stream, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    Fmt_vfmt(outc, stream, fmt, ap);
    va_end(ap);
}
```

**架構**：每一種輸出目的地都只是**一個不同的 `put` 函式**加上**不同的 `cl`**：

```
Fmt_print   ──→ Fmt_vfmt(outc,   stdout, ...)
Fmt_fprint  ──→ Fmt_vfmt(outc,   stream, ...)
Fmt_vsfmt   ──→ Fmt_vfmt(insert, &buf,   ...)   ← 固定大小，滿了丟例外
Fmt_vstring ──→ Fmt_vfmt(append, &buf,   ...)   ← 自動加倍
```

### 3.3 ⭐ 安全的字串輸出：`insert`

```c
struct buf {
    char *buf;    /* 緩衝區開頭 */
    char *bp;     /* 下一個寫入位置 */
    int size;     /* 容量 */
};

int Fmt_vsfmt(char *buf, int size, const char *fmt, va_list ap) {
    struct buf cl;
    assert(buf);
    assert(size > 0);
    assert(fmt);
    cl.buf = cl.bp = buf;
    cl.size = size;
    Fmt_vfmt(insert, &cl, fmt, ap);
    insert(0, &cl);                  /* 加上 NUL，滿了也會丟例外 */
    return cl.bp - cl.buf - 1;       /* 不算 NUL */
}

static int insert(int c, void *cl) {
    struct buf *p = cl;
    if (p->bp >= p->buf + p->size)
        RAISE(Fmt_Overflow);         /* 不會寫到緩衝區外面 */
    *p->bp++ = c;
    return c;
}
```

`cl` 就是指向一個區域變數 `struct buf` 的指標，`insert` 透過它知道要寫到哪裡、還剩多少空間。

### 3.4 ⭐ 自動加倍的字串輸出：`append`

```c
char *Fmt_vstring(const char *fmt, va_list ap) {
    struct buf cl;
    assert(fmt);
    cl.size = 256;                          /* 從 256 開始 */
    cl.buf = cl.bp = ALLOC(cl.size);
    Fmt_vfmt(append, &cl, fmt, ap);
    append(0, &cl);
    return RESIZE(cl.buf, cl.bp - cl.buf);  /* 縮小到剛好的大小 */
}

static int append(int c, void *cl) {
    struct buf *p = cl;
    if (p->bp >= p->buf + p->size) {
        RESIZE(p->buf, 2*p->size);          /* 滿了就加倍 */
        p->bp = p->buf + p->size;           /* RESIZE 可能搬移，要重設 bp */
        p->size *= 2;
    }
    *p->bp++ = c;
    return c;
}
```

- 滿了就**加倍**（攤銷常數時間）。
- `RESIZE` 可能**搬移**緩衝區，所以必須用新的 `p->buf` 重新計算 `bp`。
- 結束時用 `RESIZE` **縮小到剛好的大小**，釋放多餘的空間（習題 14.1 討論什麼時候值得這樣做）。

### 3.5 ⭐ 核心：`Fmt_vfmt`

```c
void Fmt_vfmt(int put(int c, void *cl), void *cl,
        const char *fmt, va_list ap) {
    assert(put);
    assert(fmt);
    while (*fmt)
        if (*fmt != '%' || *++fmt == '%')
            put((unsigned char)*fmt++, cl);     /* 一般字元，或 %% */
        else
        {   /* format an argument */
            unsigned char c, flags[256];
            int width = INT_MIN, precision = INT_MIN;
            memset(flags, '\0', sizeof flags);
            /* get optional flags */
            /* get optional field width */
            /* get optional precision */
            c = *fmt++;
            assert(cvt[c]);                     /* 沒有註冊的格式碼 → checked error */
            (*cvt[c])(c, &ap, put, cl, flags, width, precision);
        }
}
```

**`*fmt != '%' || *++fmt == '%'` 這個條件很精巧**：
- 不是 `%`：直接輸出。
- 是 `%`：**先前進一格**再看下一個字元；如果也是 `%`（`%%`），就輸出那個 `%`。
- 否則進入格式化流程，此時 `fmt` 已經指向 `%` 後面的字元。

`c` 宣告成 `unsigned char`，確保 `*fmt` 被當成 0 到 255 的整數，才能安全地當作 `cvt` 的索引。

### 3.6 轉換函式表

```c
static T cvt[256] = {
 /*   0-  7 */ 0, 0, 0, 0, 0, 0, 0, 0,
 /* ... */
 /*  96-103 */ 0,     0, 0, cvt_c, cvt_d, cvt_f, cvt_f, cvt_f,   /* c d e f g */
 /* 104-111 */ 0,     0, 0,     0,     0,     0,     0, cvt_o,   /* o */
 /* 112-119 */ cvt_p, 0, 0, cvt_s,     0, cvt_u,     0,     0,   /* p s u */
 /* 120-127 */ cvt_x, 0, 0,     0,     0,     0,     0,     0    /* x */
};

T Fmt_register(int code, T newcvt) {
    T old;
    assert(0 < code && code < (int)(sizeof (cvt)/sizeof (cvt[0])));
    old = cvt[code];
    cvt[code] = newcvt;
    return old;
}
```

- **以格式字元為索引的函式指標表**，這是典型的**表格驅動分派**。
- 初始化時假設 **ASCII** 字元順序。
- `e`、`f`、`g` 三個格式碼共用 `cvt_f`。

### 3.7 解析旗標、寬度、精確度

```c
char *Fmt_flags = "-+ 0";

/* get optional flags */
if (Fmt_flags) {
    unsigned char c = *fmt;
    for ( ; c && strchr(Fmt_flags, c); c = *++fmt) {
        assert(flags[c] < 255);
        flags[c]++;                     /* 計算每個旗標出現的次數 */
    }
}

/* get optional field width */
if (*fmt == '*' || isdigit(*fmt)) {
    int n;
    /* n ← next argument or scan digits */
    width = n;
}

/* n ← next argument or scan digits */
if (*fmt == '*') {
    n = va_arg(ap, int);
    assert(n != INT_MIN);               /* INT_MIN 保留給「沒指定」 */
    fmt++;
} else
    for (n = 0; isdigit(*fmt); fmt++) {
        int d = *fmt - '0';
        assert(n <= (INT_MAX - d)/10);  /* 檢查 10n + d 會不會溢位 */
        n = 10*n + d;
    }

/* get optional precision */
if (*fmt == '.' && (*++fmt == '*' || isdigit(*fmt))) {
    int n;
    /* n ← next argument or scan digits */
    precision = n;
}
```

**⭐ 不會溢位的溢位檢查**：
- 要確保 `10n + d ≤ INT_MAX`，但**不能真的去算 `10n + d`**，因為那本身就可能溢位。
- 所以**改寫不等式**：`n ≤ (INT_MAX − d) / 10`，這樣運算過程都不會超出範圍。

**細節**：一個 `.` 後面沒有接 `*` 或數字時，`.` 會被吃掉，並被解釋成「**明確省略** precision」。

### 3.8 `cvt_d` 和 `Fmt_putd`：數字格式化

```c
static void cvt_d(int code, va_list *app,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    int val = va_arg(*app, int);
    unsigned m;
    char buf[43];
    char *p = buf + sizeof buf;

    if (val == INT_MIN)
        m = INT_MAX + 1U;          /* 和 Atom_int 一樣處理二補數不對稱 */
    else if (val < 0)
        m = -val;
    else
        m = val;
    do
        *--p = m%10 + '0';         /* 從右往左產生數字 */
    while ((m /= 10) > 0);
    if (val < 0)
        *--p = '-';
    Fmt_putd(p, (buf + sizeof buf) - p, put, cl, flags, width, precision);
}
```

和第 3 章 `Atom_int` **完全相同的技巧**：用無號運算、特別處理 `INT_MIN`、43 個字元的緩衝區。

```c
void Fmt_putd(const char *str, int len,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    int sign;
    assert(str);
    assert(len >= 0);
    assert(flags);
    /* normalize width and flags */

    /* compute the sign */
    if (len > 0 && (*str == '-' || *str == '+')) {
        sign = *str++;
        len--;
    } else if (flags['+'])
        sign = '+';                /* + 優先於空白 */
    else if (flags[' '])
        sign = ' ';
    else
        sign = 0;

    {   /* emit str justified in width */
        int n;
        if (precision < 0)
            precision = 1;
        if (len < precision)
            n = precision;
        else if (precision == 0 && len == 1 && str[0] == '0')
            n = 0;                 /* 值 0 且 precision 0：不輸出任何數字 */
        else
            n = len;
        if (sign)
            n++;

        if (flags['-']) {                  /* 靠左：符號 */
            if (sign) put(sign, cl);
        } else if (flags['0']) {           /* 靠右補零：符號 + 零 */
            if (sign) put(sign, cl);
            pad(width - n, '0');
        } else {                           /* 靠右補空白：空白 + 符號 */
            pad(width - n, ' ');
            if (sign) put(sign, cl);
        }
        pad(precision - len, '0');         /* precision 要求的前導零 */
        /* emit str[0..len-1] */
        if (flags['-'])
            pad(width - n, ' ');           /* 靠左：後補空白 */
    }
}
```

**三種對齊方式的輸出順序**：

| 情況 | 輸出順序 | 例：-42，width 6 |
|---|---|---|
| 靠左（`-`） | 符號、數字、空白 | `-42   ` |
| 靠右補零（`0`） | 符號、**零**、數字 | `-00042` |
| 靠右補空白 | **空白**、符號、數字 | `   -42` |

注意**補零時符號在零的前面**，補空白時符號在空白的後面。

### 3.9 其他數值轉換

```c
static void cvt_u(...) {                   /* 無號十進位：不需要處理符號 */
    unsigned m = va_arg(*app, unsigned);
    /* declare buf and p */
    do *--p = m%10 + '0'; while ((m /= 10) > 0);
    Fmt_putd(p, (buf + sizeof buf) - p, put, cl, flags, width, precision);
}

static void cvt_o(...) {                   /* 八進位：用位移 */
    unsigned m = va_arg(*app, unsigned);
    /* declare buf and p */
    do *--p = (m&0x7) + '0'; while ((m >>= 3) != 0);
    Fmt_putd(...);
}

static void cvt_x(...) {                   /* 十六進位：查字串常值 */
    unsigned m = va_arg(*app, unsigned);
    /* declare buf and p */
    do *--p = "0123456789abcdef"[m&0xf]; while ((m >>= 4) != 0);
    Fmt_putd(...);
}

static void cvt_p(...) {                   /* 指標：轉成 unsigned long */
    unsigned long m = (unsigned long)va_arg(*app, void*);
    /* declare buf and p */
    precision = INT_MIN;                   /* 忽略 precision */
    /* emit m in hexadecimal */
}
```

- 八進位和十六進位的底數是 2 的冪，所以可以用**位移和遮罩**取代除法和取餘數。
- **`"0123456789abcdef"[m&0xf]`**：字串常值可以直接用索引存取。
- `cvt_p` 把指標轉成 **`unsigned long`**，因為 `unsigned` 可能**不夠大**，裝不下一個指標。

### 3.10 `cvt_c`：預設參數提升

```c
static void cvt_c(int code, va_list *app,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    /* normalize width */
    if (!flags['-'])
        pad(width - 1, ' ');
    put((unsigned char)va_arg(*app, int), cl);   /* 用 int 取，不是 char！ */
    if ( flags['-'])
        pad(width - 1, ' ');
}
```

> **為什麼用 `va_arg(*app, int)` 而不是 `char`？**
> 因為字元參數放在可變參數部分時，會經過**預設參數提升（default argument promotions）**，被轉成 `int` 傳遞。用 `char` 取是未定義行為。
> 再轉成 `unsigned char`，讓有號、無號和 plain char 都以相同方式輸出。

### 3.11 浮點數：借用 `sprintf`

```c
static void cvt_f(int code, va_list *app,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    char buf[DBL_MAX_10_EXP+1+1+99+1];
    if (precision < 0)
        precision = 6;
    if (code == 'g' && precision == 0)
        precision = 1;
    {   /* format a double argument into buf */
        static char fmt[] = "%.dd?";
        assert(precision <= 99);
        fmt[4] = code;                         /* e、f 或 g */
        fmt[3] =      precision%10 + '0';      /* 個位數 */
        fmt[2] = (precision/10)%10 + '0';      /* 十位數 */
        sprintf(buf, fmt, va_arg(*app, double));
    }
    Fmt_putd(buf, strlen(buf), put, cl, flags, width, precision);
}
```

- **把浮點數準確地轉成十進位、而且和機器無關，出乎意料地困難。** 和機器相關的演算法比較快也比較準，所以**直接借用 `sprintf`**。
- 動態組出 `"%.NNe"` 這樣的格式字串，例如 precision 12、code `f` 會得到 `"%.12f"`。
- **⭐ 為什麼 precision 限制在 99？為了讓緩衝區大小在編譯期就能確定：**
  - 最長的輸出是 `%.99f` 印 `DBL_MAX`：
  - 小數點前最多 `DBL_MAX_10_EXP + 1` 位（IEEE 754 雙精度是 308 + 1）
  - 加 1 個小數點、99 位小數、1 個 NUL。
  - ⇒ `buf[DBL_MAX_10_EXP+1+1+99+1]`。`%e` 和 `%g` 的結果都比 `%f` 短。
- 設定 `fmt[2]`、`fmt[3]` 的方式**假設是 ASCII** 字元順序。

---

## 4. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **輸出抽象化** | `put(c, cl)` 讓同一個格式化引擎能輸出到任何地方 |
| **可擴充性** | `Fmt_register` 加上以格式碼為索引的函式指標表 |
| **安全性** | `Fmt_sfmt` 滿了丟例外、`Fmt_string` 自動配置，消除 sprintf 溢位 |
| **單一核心** | 所有函式都匯流到 `Fmt_vfmt` |
| **提供積木** | 匯出 `Fmt_putd`/`Fmt_puts`，讓自訂轉換函式只需處理「轉成字串」 |
| **一般化的介面、正規化的實作** | 介面保留 `INT_MIN`、旗標次數等完整資訊；預設轉換先正規化再處理 |
| **傳 `va_list *`** | 讓轉換函式取參數後，呼叫端的 `va_list` 也跟著前進 |
| **不會溢位的溢位檢查** | `n ≤ (INT_MAX − d) / 10` |
| **預設參數提升** | `%c` 要用 `va_arg(ap, int)` |
| **務實地借用** | 浮點數交給 `sprintf`，並限制 precision 讓緩衝區大小固定 |
| **重複使用技巧** | `cvt_d` 沿用 `Atom_int` 的整數轉字串法 |

---

## 5. 延伸閱讀重點

- **Plauger (1992)**：C 函式庫 `printf` 家族的實作，包括字串和浮點數互相轉換的低階程式碼，以及其他 printf 旗標和格式碼的實作方式。
- **Hennessy & Patterson (1994)** 第 4.8 節：IEEE 754 浮點標準與浮點加法、乘法的實作。
- **Goldberg (1991)**：程式設計師最需要知道的浮點運算性質（〈What Every Computer Scientist Should Know About Floating-Point Arithmetic〉）。
- **浮點轉換的試金石**：給定浮點數 x，**輸出轉換產生的字串**，再經過**輸入轉換**後得到的 y，必須和 x **逐位元相同**。
  - **Clinger (1990)**：如何準確地做**輸入**轉換，並證明某些 x 需要**任意精度**運算。
  - **Steele & White (1990)**：如何準確地做**輸出**轉換。

---

## 6. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 14.1 | `Fmt_vstring` 用 `RESIZE` 釋放沒用到的部分，設計成**只在值得時**才做 | 釋放的空間值不值得那次重新配置的成本 |
| 14.2 | 用 Steele & White (1990) 的演算法實作 `e`、`f`、`g` | 擺脫對 `sprintf` 的依賴 |
| 14.3 | 寫一個 `%@` 轉換函式：**從下一個整數參數取得格式碼**再格式化，例如 `Fmt_string("... %@\n", x.format, x.value)` | 在轉換函式裡分派到別的轉換函式，注意 `va_list` 的處理 |
| 14.4 | 寫一個印出 `Bit_T` 的轉換函式，連續的 1 印成範圍，例如 `1 32–45 68 70–71` | 實際練習 `Fmt_register` 和 `Fmt_puts` |

---

## 7. 本章重點整理

1. **printf 的四個缺點**：格式碼固定、輸出目的地固定、**sprintf 會溢位**、沒有型別檢查。**Fmt 解決前三個。**
2. **核心** `Fmt_fmt(put, cl, fmt, ...)`：每個字元都呼叫 `put(c, cl)`，輸出可以導向任何地方。
3. **安全的字串格式化**：`Fmt_sfmt` 超過大小就丟出 `Fmt_Overflow`；`Fmt_string` 自動配置（client 負責釋放）。
4. **可擴充**：`Fmt_register(code, cvt)` 註冊自訂格式碼並回傳舊的函式；轉換函式的簽名是 `Fmt_T`，用 `va_arg(*app, type)` 取參數。
5. **輔助函式** `Fmt_putd`/`Fmt_puts` 處理數字和字串的對齊、補零、截斷。
6. **實作**：所有函式都匯流到 `Fmt_vfmt`；輸出目的地只是不同的 `put`（`outc`/`insert`/`append`）；以格式碼為索引的 `cvt[256]` 函式表。
7. **細節**：`INT_MIN` 代表沒指定；不會溢位的溢位檢查；`%c` 用 `int` 取參數；浮點數借用 `sprintf` 並限制 precision ≤ 99。

> **一句話**：Fmt 把 printf 拆成「解析格式字串的引擎」、「可替換的轉換函式表」和「可替換的輸出函式」三個部分，換來可擴充、可以導向任何地方、而且不會緩衝區溢位的格式化輸出。
