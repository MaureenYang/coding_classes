# 第 18 章　Arbitrary-Precision Arithmetic（任意精度算術：AP）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.323–355

---

## 1. 本章定位

**AP** 提供**任意精度的有號整數**和它們的算術運算：
- 和 XP_T 不同，AP 的整數**可以是負數**，而且**位數任意**。
- 可以表示的值只受限於可用的記憶體。

**應用範例**：有些共同基金公司把股價追蹤到 **centicent（1/10,000 美元）**，所有計算都以 centicent 為單位。32 位元無號整數只能表示 **$429,496.7295**，對管理數十億美元的基金來說遠遠不夠。

### 1.1 AP 和 XP 的關係

| | XP（第 17 章） | **AP** |
|---|---|---|
| 層級 | 低階 | **高階** |
| 符號 | 無號 | **有號** |
| 位數 | 固定 n，呼叫端指定 | **自動、任意** |
| 型別 | 公開的 `unsigned char *` | **不透明指標** |
| 記憶體 | 呼叫端提供 | **AP 自己配置** |
| 錯誤檢查 | 幾乎沒有 | **完整的 checked runtime error** |

> AP **當然使用 XP**，但它是一個**高階介面**：只公開一個不透明型別、提供配置和釋放函式、提供一般的算術運算，**並實作 XP 省略的 checked runtime error**。
> **大多數應用應該使用 AP 或下一章的 MP**，而不是直接用 XP。

---

## 2. 介面（18.1 Interface）

```c
/* ap.h */
#ifndef AP_INCLUDED
#define AP_INCLUDED
#include <stdarg.h>

#define T AP_T
typedef struct T *T;

/* 建立 */
extern T    AP_new    (long int n);
extern T    AP_fromstr(const char *str, int base, char **end);

/* 轉換與輸出 */
extern long int AP_toint(T x);
extern char    *AP_tostr(char *str, int size, int base, T x);
extern void     AP_fmt  (int code, va_list *app,
                    int put(int c, void *cl), void *cl,
                    unsigned char flags[], int width, int precision);

/* 釋放 */
extern void AP_free(T *z);

/* 算術 */
extern T AP_neg(T x);
extern T AP_add(T x, T y);
extern T AP_sub(T x, T y);
extern T AP_mul(T x, T y);
extern T AP_div(T x, T y);
extern T AP_mod(T x, T y);
extern T AP_pow(T x, T y, T p);

/* 便利函式（第二個運算元是 long）*/
extern T    AP_addi(T x, long int y);
extern T    AP_subi(T x, long int y);
extern T    AP_muli(T x, long int y);
extern T    AP_divi(T x, long int y);
extern long AP_modi(T x, long int y);

/* 位移 */
extern T AP_lshift(T x, int s);
extern T AP_rshift(T x, int s);

/* 比較 */
extern int AP_cmp (T x, T y);
extern int AP_cmpi(T x, long int y);

#undef T
#endif
```

**通則**：傳 NULL 的 `AP_T` 給任何函式都是 checked runtime error（另有說明的除外）。

### 2.1 建立

| 函式 | 功能 |
|---|---|
| `AP_new(n)` | 建立 AP_T，初始化成 long 值 n |
| `AP_fromstr(str, base, &end)` | 像 `strtol`：忽略開頭空白，接受**選用的正負號**加上一個或多個 base 進位的數字；不是合法數字時**回傳 NULL**，並把 `*end` 設成 `str` |

兩者都可能丟出 `Mem_Failed`。base 不在 2 到 36、str 是 NULL，都是 checked error。

### 2.2 轉換與輸出

- **`AP_toint(x)`**：回傳和 x **同號**、大小為 **|x| mod (LONG_MAX+1)** 的 long。（x 是 LONG_MIN 時回傳 0。）
- **`AP_tostr(str, size, base, x)`**：轉成 base 進位的字串，大於 9 的數字用大寫字母。
  - str 不是 NULL：填入最多 size 個字元，**size 太小是 checked error**。
  - **str 是 NULL：忽略 size，自動配置剛好夠大的字串**，client 負責釋放。
- **`AP_fmt`**：Fmt 的轉換函式，像 `%d` 一樣格式化 AP_T，可能丟出 `Mem_Failed`。

```c
Fmt_register('D', AP_fmt);
Fmt_print("%D\n", x);
```

> 注意 `AP_fmt` 消耗的是 **`AP_T` 本身**（它就是指標），不像第 16 章的 `Text_fmt` 必須傳結構的指標。

### 2.3 釋放

**`AP_free(&z)`**：釋放並把 `*z` 設成 NULL。

> ⚠ **每個 AP 函式都回傳一個新配置的 AP_T**，client 要負責釋放所有中間結果，否則就會洩漏。

### 2.4 算術

所有函式都**回傳新的 AP_T**，也都可能丟出 `Mem_Failed`。

| 函式 | 結果 |
|---|---|
| `AP_neg(x)` | −x |
| `AP_add(x, y)` | x + y |
| `AP_sub(x, y)` | x − y |
| `AP_mul(x, y)` | x · y |
| `AP_div(x, y)` | x / y |
| `AP_mod(x, y)` | x mod y |
| `AP_pow(x, y, p)` | p 是 NULL 時算 **xʸ**；否則算 **(xʸ) mod p** |

**⭐ 除法的截斷規則**：
- **向左截斷**：任一方是負數時向負無限大截斷，否則向零截斷，**所以餘數永遠是正數**。
- 精確定義：商 q 是**不超過實數 w（w·y = x）的最大整數**，餘數是 x − y·q。
- **這和第 2 章的 `Arith` 介面完全相同。**
- `AP_div`、`AP_mod` 的 y 是 0 是 checked runtime error。

**`AP_pow`**：y 是負數，或 p 不是 NULL 而且小於 2，都是 checked runtime error。

### 2.5 便利函式

```c
AP_addi(x, y)   /* 等同於 AP_add(x, AP_new(y))，但不會洩漏那個暫時物件 */
```

`AP_addi`、`subi`、`muli`、`divi`、`modi`、`cmpi`：第二個運算元是 `long`。除法和取餘數的規則同上。**`AP_modi` 回傳 `long`**，因為餘數一定比 y 小。

### 2.6 位移與比較

- **`AP_lshift(x, s)`**：x 左移 s 位元，也就是乘以 2ˢ。
- **`AP_rshift(x, s)`**：x 右移 s 位元，也就是除以 2ˢ。
- 結果和 x **同號**（除非結果是 0），空出的位元填 0。s 是負數是 checked error。
- **`AP_cmp(x, y)`**、**`AP_cmpi(x, y)`**：回傳 `<0`、`0`、`>0`。

---

## 3. 範例：任意精度計算機 `calc`（18.2）

### 3.1 功能

**逆波蘭表示法**（Polish suffix notation）：值推入堆疊，運算子從堆疊彈出運算元，再把結果推回去。

| 運算子 | 功能 |
|---|---|
| `~` | 取負 |
| `+` `-` `*` `/` `%` | 加、減、乘、除、取餘數 |
| `^` | 次方 |
| `d` | 複製堆疊頂端的值 |
| `p` | 印出堆疊頂端的值 |
| `f` | 從頂端往下印出堆疊所有的值 |
| `c` | 清空堆疊 |
| `q` | 離開 |

一個值是一個或多個連續的十進位數字；空白字元用來分隔，其他字元會被報告為無法辨識的運算子。

### 3.2 結構

```c
#include "stack.h"     /* 第 2 章的 Stack！ */
#include "ap.h"
#include "fmt.h"

Stack_T sp;

AP_T pop(void) {
    if (!Stack_empty(sp))
        return Stack_pop(sp);
    else {
        Fmt_fprint(stderr, "?stack underflow\n");
        return AP_new(0);           /* 永遠回傳一個 AP_T，簡化其他地方的錯誤檢查 */
    }
}

int main(int argc, char *argv[]) {
    int c;
    sp = Stack_new();
    Fmt_register('D', AP_fmt);
    while ((c = getchar()) != EOF)
        switch (c) {
        case ' ': case '\t': case '\n': case '\f': case '\r':
            break;
        case '0': case '1': /* ... */ case '9': {
            char buf[512];
            /* gather up digits into buf */
            Stack_push(sp, AP_fromstr(buf, 10, NULL));
            break;
        }
        case '+': {
            AP_T y = pop(), x = pop();      /* 注意彈出順序 */
            Stack_push(sp, AP_add(x, y));
            AP_free(&x);
            AP_free(&y);
            break;
        }
        /* ... 其他運算子 ... */
        default:
            if (isprint(c))
                Fmt_fprint(stderr, "?'%c'", c);
            else
                Fmt_fprint(stderr, "?'\\%03o'", c);
            Fmt_fprint(stderr, " is unimplemented\n");
            break;
        }
    /* clear the stack */
    Stack_free(&sp);
    return EXIT_SUCCESS;
}
```

> **這個範例把全書的模組串在一起**：第 2 章的 Stack、第 14 章的 Fmt、本章的 AP。

### 3.3 ⭐ 記憶體管理協定

> 很容易犯的錯誤是**在堆疊上放兩份同一個 AP_T**，這樣就沒辦法知道哪些 AP_T 該釋放。
>
> **簡單的協定：唯一「永久」的 AP_T 是堆疊上的那些；其他的一律用 `AP_free` 釋放。**

所以每個二元運算子都是：**彈出 x、y → 推入新結果 → 釋放 x、y**。

### 3.4 防禦性檢查

```c
case '/': {
    AP_T y = pop(), x = pop();
    if (AP_cmpi(y, 0) == 0) {           /* AP 會 assert，所以 calc 要先檢查 */
        Fmt_fprint(stderr, "?/ by 0\n");
        Stack_push(sp, AP_new(0));
    } else
        Stack_push(sp, AP_div(x, y));
    AP_free(&x);
    AP_free(&y);
    break;
}

case '^': {
    AP_T y = pop(), x = pop();
    if (AP_cmpi(y, 0) <= 0) {           /* 非正的次方 */
        Fmt_fprint(stderr, "?nonpositive power\n");
        Stack_push(sp, AP_new(0));
    } else
        Stack_push(sp, AP_pow(x, y, NULL));
    AP_free(&x);
    AP_free(&y);
    break;
}
```

> AP 把除以 0 定義成 **checked runtime error**（程式的 bug）。但對 calc 來說，使用者輸入除以 0 是**使用者錯誤**，所以 **calc 必須在呼叫 AP 之前自己檢查**。這正是第 4 章三種錯誤分類的實際應用。

### 3.5 複製與印出

```c
case 'd': {
    AP_T x = pop();
    Stack_push(sp, x);
    Stack_push(sp, AP_addi(x, 0));      /* 複製 AP_T 唯一的方法：加 0 */
    break;
}

case 'p': {
    AP_T x = pop();
    Fmt_print("%D\n", x);
    Stack_push(sp, x);
    break;
}
```

**觀察**：AP 介面**沒有複製函式**，「加 0」是唯一的方法。

### 3.6 ⭐ 暴露 Stack 介面的弱點

```c
case 'f':
    if (!Stack_empty(sp)) {
        Stack_T tmp = Stack_new();
        while (!Stack_empty(sp)) {
            AP_T x = pop();
            Fmt_print("%D\n", x);
            Stack_push(tmp, x);         /* 倒到暫時的堆疊 */
        }
        while (!Stack_empty(tmp))
            Stack_push(sp, Stack_pop(tmp));   /* 再倒回來 */
        Stack_free(&tmp);
    }
    break;
```

> 印出所有值暴露了 **Stack 介面的弱點**：**沒辦法存取頂端以下的值，也沒辦法知道堆疊上有幾個值**。比較好的堆疊介面可以有類似 `Table_length` 和 `Table_map` 的函式。沒有它們，calc 只好用一個暫時的堆疊來回倒。

> **作者用自己書裡的介面當反例**，示範介面設計不周時，client 要付出多少代價。

### 3.7 讀取數字

```c
/* gather up digits into buf */
{
    int i = 0;
    for ( ; c != EOF && isdigit(c); c = getchar(), i++)
        if (i < (int)sizeof (buf) - 1)
            buf[i] = c;
    if (i > (int)sizeof (buf) - 1) {
        i = (int)sizeof (buf) - 1;
        Fmt_fprint(stderr, "?integer constant exceeds %d digits\n", i);
    }
    buf[i] = 0;
    if (c != EOF)
        ungetc(c, stdin);
}
```

數字太長時會報告並截斷。

---

## 4. 實作（18.3 Implementation）

### 4.1 ⭐ 符號 + 大小（sign-magnitude）表示

```c
struct T {
    int sign;       /* 1 或 -1 */
    int ndigits;    /* 使用中的位數 */
    int size;       /* 配置的位數 */
    XP_T digits;    /* 絕對值，用 XP_T 表示 */
};
```

- **sign** 是 1 或 −1。
- **size** 是配置的位數，可以**大於** ndigits。
- AP_T 代表的值就是 `digits[0..ndigits-1]` 這個 XP_T。
- **AP_T 永遠是正規化的**：最高位數不是 0（除非值是 0）。所以 ndigits 常常小於 size。

```
751,702,468,129 的 AP_T（11 位數，只用了 5 位）：

  sign     1
  ndigits  5
  size     11
  digits ──→ [33][102][245][4][175][ ][ ][ ][ ][ ][ ]
              ↑ 最低位                ↑ 沒用到的部分
```

### 4.2 建立：`mk` 和 `set`

```c
T AP_new(long int n) {
    return set(mk(sizeof (long int)), n);
}

static T mk(int size) {
    T z = CALLOC(1, sizeof (*z) + size);   /* 結構和位數一起配置，清成 0 */
    assert(size > 0);
    z->sign = 1;
    z->size = size;
    z->ndigits = 1;
    z->digits = (XP_T)(z + 1);
    return z;
}
```

**⭐ 零的唯一表示**：符號加大小的表示法有**兩種零**（+0 和 −0），AP 的慣例是**只用正的那種**，這點從 `mk` 就看得出來。

```c
static T set(T z, long int n) {
    if (n == LONG_MIN)
        XP_fromint(z->size, z->digits, LONG_MAX + 1UL);   /* 又是二補數不對稱 */
    else if (n < 0)
        XP_fromint(z->size, z->digits, -n);
    else
        XP_fromint(z->size, z->digits, n);
    z->sign = n < 0 ? -1 : 1;          /* 保證是 ±1，而且 0 的符號是 1 */
    return normalize(z, z->size);
}

static T normalize(T z, int n) {
    z->ndigits = XP_length(n, z->digits);    /* 去掉前導的 0 */
    return z;
}

void AP_free(T *z) {
    assert(z && *z);
    FREE(*z);         /* 結構和位數是一起配置的，一次釋放 */
}
```

`AP_new` 是配置 AP_T **唯一**的方式，所以 `AP_free` 可以放心地「知道」結構和位數陣列是一次配置的。

### 4.3 輔助巨集

```c
#define iszero(x)  ((x)->ndigits==1 && (x)->digits[0]==0)
#define isone(x)   ((x)->ndigits==1 && (x)->digits[0]==1)
#define maxdigits(x,y) ((x)->ndigits > (y)->ndigits ? (x)->ndigits : (y)->ndigits)

/* x and y have the same sign */
((x->sign^y->sign) == 0)
```

- `iszero` 利用**正規化**的保證：零只有一位數。
- **同號判斷用 XOR**：sign 只會是 1 或 −1，兩者相同時 XOR 為 0。

### 4.4 取負與乘法

```c
T AP_neg(T x) {
    T z;
    assert(x);
    z = mk(x->ndigits);
    memcpy(z->digits, x->digits, x->ndigits);
    z->ndigits = x->ndigits;
    z->sign = iszero(z) ? 1 : -x->sign;    /* ⚠ 零的符號必須維持是 1 */
    return z;
}
```

> 取負是最簡單的運算，但它展示了**符號加大小表示法反覆出現的問題**：**每次設定符號都要特別處理零**。

```c
T AP_mul(T x, T y) {
    T z;
    assert(x);
    assert(y);
    z = mk(x->ndigits + y->ndigits);       /* 乘積最多 n+m 位 */
    XP_mul(z->digits, x->ndigits, x->digits, y->ndigits, y->digits);
    normalize(z, z->size);
    z->sign = iszero(z) || /* same sign */ ((x->sign^y->sign) == 0) ? 1 : -1;
    return z;
}
```

- |x·y| = |x|·|y|，**XP_mul 計算大小，AP 自己計算符號**。
- `mk` 已經把 z 清成 0，而 XP_mul 做的是 z += x·y，剛好就是 x·y。

### 4.5 ⭐ 加法：依符號分情況

**加法比較複雜，因為可能需要做減法**：

|  | y < 0 | y ≥ 0 |
|---|---|---|
| **x < 0** | −(\|x\| + \|y\|) | \|y\| − \|x\|（若 \|y\| ≥ \|x\|）<br>−(\|x\| − \|y\|)（若 \|y\| < \|x\|） |
| **x ≥ 0** | \|x\| − \|y\|（若 \|x\| > \|y\|）<br>−(\|y\| − \|x\|)（若 \|x\| ≤ \|y\|） | \|x\| + \|y\| |

```c
T AP_add(T x, T y) {
    T z;
    assert(x);
    assert(y);
    if (/* same sign */) {                          /* 對角線：大小相加 */
        z = add(mk(maxdigits(x,y) + 1), x, y);     /* 可能多一位 */
        z->sign = iszero(z) ? 1 : x->sign;
    } else                                          /* 異號：大小相減 */
        if (cmp(x, y) > 0) {                        /* |x| > |y| */
            z = sub(mk(x->ndigits), x, y);
            z->sign = iszero(z) ? 1 : x->sign;      /* 和 x 同號 */
        } else {                                    /* |x| ≤ |y| */
            z = sub(mk(y->ndigits), y, x);
            z->sign = iszero(z) ? 1 : -x->sign;     /* 和 x 反號 */
        }
    return z;
}
```

**⭐ 減法只要把表格「轉一下」**：

|  | y < 0 | y ≥ 0 |
|---|---|---|
| **x < 0** | 比較大小後相減 | −(\|x\| + \|y\|) |
| **x ≥ 0** | \|x\| + \|y\| | 比較大小後相減 |

```c
T AP_sub(T x, T y) {
    T z;
    assert(x);
    assert(y);
    if (!/* same sign */) {                         /* 非對角線：大小相加 */
        z = add(mk(maxdigits(x,y) + 1), x, y);
        z->sign = iszero(z) ? 1 : x->sign;
    } else                                          /* 對角線：大小相減 */
        if (cmp(x, y) > 0) {
            z = sub(mk(x->ndigits), x, y);
            z->sign = iszero(z) ? 1 : x->sign;
        } else {
            z = sub(mk(y->ndigits), y, x);
            z->sign = iszero(z) ? 1 : -x->sign;
        }
    return z;
}
```

> **加法的「同號」情況就是減法的「異號」情況**，反之亦然。所以兩個函式的程式碼幾乎一樣，只差在第一個 `if` 有沒有 `!`。

### 4.6 大小的加減：`add` 和 `sub`

```c
static T add(T z, T x, T y) {          /* |z| = |x| + |y| */
    int n = y->ndigits;
    if (x->ndigits < n)
        return add(z, y, x);           /* 確保 x 比較長 */
    else if (x->ndigits > n) {
        int carry = XP_add(n, z->digits, x->digits, y->digits, 0);
        z->digits[z->size-1] = XP_sum(x->ndigits - n,
            &z->digits[n], &x->digits[n], carry);   /* x 剩下的高位加上進位 */
    } else
        z->digits[n] = XP_add(n, z->digits, x->digits, y->digits, 0);
    return normalize(z, z->size);
}

static T sub(T z, T x, T y) {          /* |z| = |x| − |y|，前提是 |x| ≥ |y| */
    int borrow, n = y->ndigits;
    borrow = XP_sub(n, z->digits, x->digits, y->digits, 0);
    if (x->ndigits > n)
        borrow = XP_diff(x->ndigits - n, &z->digits[n],
            &x->digits[n], borrow);
    assert(borrow == 0);               /* 因為 |x| ≥ |y| */
    return normalize(z, z->size);
}

static int cmp(T x, T y) {             /* 比較大小 */
    if (x->ndigits != y->ndigits)
        return x->ndigits - y->ndigits;          /* 位數多的比較大（因為有正規化）*/
    else
        return XP_cmp(x->ndigits, x->digits, y->digits);
}
```

**技巧**：
- 兩個數字長度不同時，**先處理共同長度的部分**（`XP_add`/`XP_sub`），**再把進位或借位傳到比較長的那個數字的高位**，這時就用**單一位數**的 `XP_sum`/`XP_diff`，把進位或借位當成那一位數。
- `cmp` 利用**正規化**：位數多的數字一定比較大。

### 4.7 ⭐ 除法：調整到「向左截斷」

XP_div 只處理**無號數**。AP 必須自己處理符號，並依照「向左截斷」調整：

| x、y 的符號 | 商 | 餘數 |
|---|---|---|
| **同號** | ⌊\|x\|/\|y\|⌋，正數 | \|x\| mod \|y\| |
| **異號**，而且 \|x\| mod \|y\| = 0 | −(\|x\|/\|y\|) | 0 |
| **異號**，而且 \|x\| mod \|y\| ≠ 0 | −(⌊\|x\|/\|y\|⌋ **+ 1**) | \|y\| **−** (\|x\| mod \|y\|) |

⇒ **餘數永遠是正數。**

```c
/* q ← x/y, r ← x mod y */
assert(x);
assert(y);
assert(!iszero(y));                    /* AP 實作 XP 沒有的 checked error */
q = mk(x->ndigits);
r = mk(y->ndigits);
{
    XP_T tmp = ALLOC(x->ndigits + y->ndigits + 2);   /* AP 替 XP 配置暫存空間 */
    XP_div(x->ndigits, q->digits, x->digits,
           y->ndigits, y->digits, r->digits, tmp);
    FREE(tmp);
}
normalize(q, q->size);
normalize(r, r->size);
q->sign = iszero(q) || /* same sign */ ? 1 : -1;

T AP_div(T x, T y) {
    T q, r;
    /* q ← x/y, r ← x mod y */
    if (!/* same sign */ && !iszero(r)) {
        int carry = XP_sum(q->size, q->digits, q->digits, 1);   /* |q| + 1 */
        assert(carry == 0);
        normalize(q, q->size);
    }
    AP_free(&r);           /* 只要商，丟掉餘數 */
    return q;
}

T AP_mod(T x, T y) {
    T q, r;
    /* q ← x/y, r ← x mod y */
    if (!/* same sign */ && !iszero(r)) {
        int borrow = XP_sub(r->size, r->digits, y->digits, r->digits, 0);  /* |y| − r */
        assert(borrow == 0);
        normalize(r, r->size);
    }
    AP_free(&q);           /* 只要餘數，丟掉商 */
    return r;
}
```

**觀察**：`AP_div` 只調整商（因為它丟掉餘數），`AP_mod` 只調整餘數（因為它丟掉商）。

> 這裡可以看到 XP 和 AP 的分工：**AP 檢查除以 0、替 XP 配置 tmp、處理符號和截斷規則**；XP 只負責無號的計算。

### 4.8 ⭐ 次方：快速冪

**天真的做法**：把 1 乘以 x，乘 y 次。如果 y 很大，例如 200 位十進位數字，**花的時間比宇宙的年齡還久**。

**用數學規則簡化：**

```
x^y = (x^(y/2))²          若 y 是偶數
x^y = x · (x^⌊y/2⌋)²      若 y 是奇數
```

遞迴深度，也就是運算次數，**和 lg y 成正比**。

```c
T AP_pow(T x, T y, T p) {
    T z;
    assert(x);
    assert(y);
    assert(y->sign == 1);                                   /* y ≥ 0 */
    assert(!p || p->sign==1 && !iszero(p) && !isone(p));    /* p ≥ 2 */
    /* special cases */
    if (iszero(x))
        return AP_new(0);                  /* 0ʸ = 0 */
    if (iszero(y))
        return AP_new(1);                  /* x⁰ = 1 */
    if (isone(x))
        return AP_new(/* y is even */ (((y)->digits[0]&1) == 0) ? 1 : x->sign);
                                           /* 1ʸ = 1；(−1)ʸ 依 y 的奇偶而定 */
    if (p)
        /* z ← xʸ mod p */
    else
        /* z ← xʸ */
    return z;
}
```

**不取模的情況：**

```c
/* z ← xʸ */
if (isone(y))
    z = AP_addi(x, 0);                     /* x¹ = x（複製一份）*/
else {
    T y2 = AP_rshift(y, 1), t = AP_pow(x, y2, NULL);   /* t = x^⌊y/2⌋ */
    z = AP_mul(t, t);                                   /* z = t² */
    AP_free(&y2);
    AP_free(&t);
    if (!/* y is even */) {
        z = AP_mul(x, t = z);                           /* z = x · t² */
        AP_free(&t);
    }
}
```

- y 是正數，所以右移一位就是 ⌊y/2⌋。
- **每一個中間結果都要釋放**，避免產生無法存取的記憶體。

**⭐ 取模的情況：模乘法**

p 不是 NULL 時，**不能真的算出 xʸ**，因為它可能太大了。例如 x 是 10 位數、y 是 200，**xʸ 的位數比宇宙中的原子還多**。但 xʸ mod p 小得多。

利用模運算的性質：

```
(x · y) mod p = ((x mod p) · (y mod p)) mod p
```

```c
static T mulmod(T x, T y, T p) {
    T z, xy = AP_mul(x, y);
    z = AP_mod(xy, p);
    AP_free(&xy);                          /* 釋放暫時的乘積 */
    return z;
}

/* z ← xʸ mod p */
if (isone(y))
    z = AP_mod(x, p);
else {
    T y2 = AP_rshift(y, 1), t = AP_pow(x, y2, p);   /* 遞迴時也帶著 p */
    z = mulmod(t, t, p);
    AP_free(&y2);
    AP_free(&t);
    if (!/* y is even */) {
        z = mulmod(y2 = AP_mod(x, p), t = z, p);    /* y 是奇數時先把 x mod p */
        AP_free(&y2);
        AP_free(&t);
    }
}
```

和不取模的版本幾乎一樣，差別只在**乘法改用 `mulmod`**、**遞迴時傳入 p**、**y 是奇數時先把 x 對 p 取模**。這樣每個中間結果都不會超過 p²。

> 模冪運算是 **RSA 等公開金鑰加密**的核心運算。

### 4.9 比較

```c
int AP_cmp(T x, T y) {
    assert(x);
    assert(y);
    if (!/* same sign */)
        return x->sign;            /* 異號：直接看 x 的符號 */
    else if (x->sign == 1)
        return cmp(x, y);          /* 都是正數：比較大小 */
    else
        return cmp(y, x);          /* 都是負數：大小比較大的反而比較小，所以參數對調 */
}
```

### 4.10 ⭐ 便利函式：在堆疊上建立暫時的 AP_T

```c
/* declare and initialize t */
unsigned char d[sizeof (unsigned long)];   /* 位數陣列放在堆疊上 */
struct T t;                                 /* 結構也放在堆疊上 */
t.size = sizeof d;
t.digits = d;

T AP_addi(T x, long int y) {
    /* declare and initialize t */
    return AP_add(x, set(&t, y));
}

T AP_subi(T x, long int y) { /* ... */ return AP_sub(x, set(&t, y)); }
T AP_muli(T x, long int y) { /* ... */ return AP_mul(x, set(&t, y)); }
T AP_divi(T x, long int y) { /* ... */ return AP_div(x, set(&t, y)); }
int AP_cmpi(T x, long int y) { /* ... */ return AP_cmp(x, set(&t, y)); }

long int AP_modi(T x, long int y) {
    long int rem;
    T r;
    /* declare and initialize t */
    r = AP_mod(x, set(&t, y));
    rem = XP_toint(r->ndigits, r->digits);
    AP_free(&r);
    return rem;
}
```

**巧妙之處**：暫時的 AP_T 和它的位數陣列**都配置在堆疊上**（區域變數），**完全不需要 malloc 和 free**。之所以可行，是因為 long 轉換的位數**上限是已知的**，就是 `sizeof(unsigned long)` 個位元組。

> 介面說 `AP_addi(x, y)` 「等同於」`AP_add(x, AP_new(y))`，但後者會**洩漏** `AP_new(y)` 配置的物件；實作用堆疊上的暫時物件避免了這個問題。

### 4.11 位移

```c
T AP_lshift(T x, int s) {
    T z;
    assert(x);
    assert(s >= 0);
    z = mk(x->ndigits + ((s+7)&~7)/8);     /* 多 ⌈s/8⌉ 位 */
    XP_lshift(z->size, z->digits, x->ndigits, x->digits, s, 0);
    z->sign = x->sign;
    return normalize(z, z->size);
}

T AP_rshift(T x, int s) {
    assert(x);
    assert(s >= 0);
    if (s >= 8*x->ndigits)
        return AP_new(0);                  /* 全部移出去了 */
    else {
        T z = mk(x->ndigits - s/8);
        XP_rshift(z->size, z->digits, x->ndigits, x->digits, s, 0);
        normalize(z, z->size);
        z->sign = iszero(z) ? 1 : x->sign; /* 結果可能是 0 */
        return z;
    }
}
```

### 4.12 字串轉換

```c
long int AP_toint(T x) {
    unsigned long u;
    assert(x);
    u = XP_toint(x->ndigits, x->digits)%(LONG_MAX + 1UL);
    if (x->sign == -1)
        return -(long)u;
    else
        return (long)u;
}
```

**`AP_fromstr`** 接受的語法：`{ 空白 } [ - | + ] { 空白 } 數字 { 數字 }`

```c
T AP_fromstr(const char *str, int base, char **end) {
    T z;
    const char *p = str;
    char *endp, sign = '\0';
    int carry;
    assert(p);
    assert(base >= 2 && base <= 36);
    while (*p && isspace(*p))
        p++;
    if (*p == '-' || *p == '+')
        sign = *p++;
    /* z ← 0（配置足夠的空間）*/
    carry = XP_fromstr(z->size, z->digits, p, base, &endp);
    assert(carry == 0);                    /* 空間保證夠，所以不會溢位 */
    normalize(z, z->size);
    if (endp == p) {                       /* 沒有讀到任何數字 */
        endp = (char *)str;
        z = AP_new(0);
    } else
        z->sign = iszero(z) || sign != '-' ? 1 : -1;
    if (end)
        *end = (char *)endp;
    return z;
}
```

**⭐ 估計需要多少位元組：**
- n 個 base 進位的數字需要 **n · lg base** 個位元，也就是 (n · lg base)/8 個位元組。
- 取 k 使 **2ᵏ 是 ≥ base 的最小 2 的冪**，k 就是每個數字位元數的**保守高估**。
- 例如 base 10：每個數字實際上是 lg 10 ≈ 3.32 個位元，k = 4。
- k 的範圍從 1（base 2）到 6（base 36）。

```c
/* z ← 0 */
{
    const char *start;
    int k, n = 0;
    for ( ; *p == '0' && p[1] == '0'; p++)  /* 跳過前導的 0 */
        ;
    start = p;
    for ( ; /* *p is a digit in base */; p++)
        n++;                                /* 計算數字的個數 */
    for (k = 1; (1<<k) < base; k++)          /* 2ᵏ ≥ base */
        ;
    z = mk(((k*n + 7)&~7)/8);               /* ⌈k·n / 8⌉ 個位元組 */
    p = start;
}
```

**`AP_tostr`** 用類似的技巧，但方向**反過來**：
- 取 k 使 **2ᵏ 是 ≤ base 的最大 2 的冪**，k 是每個數字位元數的**低估**，所以估計出的字元數 8·m/k 是**保守的（偏大）**。
- 例如 base 10：k = 3，每個位元組配置 8/3 ≈ 3 個十進位數字的空間（實際上是 8/lg 10 ≈ 2.41）。
- k 的範圍從 5（base 36）到 1（base 2）。

```c
/* size ← number of characters in str */
{
    int k;
    for (k = 5; (1<<k) > base; k--)          /* 2ᵏ ≤ base */
        ;
    size = (8*x->ndigits)/k + 1 + 1;        /* 數字 + NUL + 1 */
    if (x->sign == -1)
        size++;                             /* 負號 */
}

char *AP_tostr(char *str, int size, int base, T x) {
    XP_T q;
    assert(x);
    assert(base >= 2 && base <= 36);
    assert(str == NULL || size > 1);
    if (str == NULL) {
        /* size ← number of characters in str */
        str = ALLOC(size);
    }
    q = ALLOC(x->ndigits);
    memcpy(q, x->digits, x->ndigits);       /* ⭐ 複製一份，因為 XP_tostr 會把它清成 0 */
    if (x->sign == -1) {
        str[0] = '-';
        XP_tostr(str + 1, size - 1, base, x->ndigits, q);
    } else
        XP_tostr(str, size, base, x->ndigits, q);
    FREE(q);
    return str;
}

void AP_fmt(int code, va_list *app,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    T x;
    char *buf;
    assert(app && flags);
    x = va_arg(*app, T);
    assert(x);
    buf = AP_tostr(NULL, 0, 10, x);
    Fmt_putd(buf, strlen(buf), put, cl, flags, width, precision);   /* 交給 Fmt 處理對齊 */
    FREE(buf);
}
```

**注意**：`XP_tostr` **會破壞輸入**（把它清成 0），所以 AP 必須**先複製一份**。這又是一個「高階層保護 client 不受低階層副作用影響」的例子。

---

## 5. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **⭐ 高階包裝低階** | AP = XP + 符號 + 自動配置 + checked error + 不破壞輸入 |
| **符號加大小** | 直覺，但每次都要特別處理零的符號；只用 +0 |
| **正規化不變式** | 最高位數非零 → `iszero` 簡單、`cmp` 先比位數 |
| **結構和位數一次配置** | `mk` 用一次 `CALLOC`，`AP_free` 一次 `FREE` |
| **用表格分析情況** | 加法和減法的符號 × 大小表格，兩者互為轉置 |
| **XOR 判斷同號** | `(x->sign ^ y->sign) == 0` |
| **一致的除法語意** | 向左截斷、餘數為正，和 `Arith` 相同 |
| **快速冪 + 模乘法** | O(lg y) 次乘法；中間結果不超過 p² |
| **堆疊上的暫時物件** | 便利函式不配置記憶體 |
| **保守的大小估計** | 用 2 的冪近似 lg base，確保空間夠 |
| **每個中間結果都要釋放** | AP 回傳新物件，client 和實作都要小心洩漏 |

### 從 calc 學到的

| 教訓 | 說明 |
|---|---|
| **所有權協定** | 只有堆疊上的值是永久的，其他一律釋放 |
| **使用者錯誤 vs. 程式 bug** | AP 把除以 0 當成 bug（assert），calc 把它當成使用者錯誤（先檢查） |
| **介面缺陷的代價** | Stack 沒有 length/map，印出所有值時只能倒來倒去 |
| **模組組合** | Stack + AP + Fmt 組成完整的應用 |

---

## 6. 延伸閱讀重點

- AP_T 類似某些程式語言的 **bignum**。例如新版的 **Icon** 只有一種整數型別，必要時自動改用任意精度運算，程式設計師**不需要區分**機器整數和任意精度整數。（Python 的 int 也是這樣。）
- 任意精度算術常以**標準函式庫或套件**的形式提供：**LISP** 系統很早就有 bignum 套件，**ML** 也有類似的套件。
- **符號運算系統**：**Mathematica**（Wolfram, 1988）提供任意長度的整數，以及分子分母都是任意長度整數的有理數；**Maple V** 也有類似功能。

---

## 7. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 18.1 | `AP_div`/`AP_mod` 每次都配置和釋放 tmp，改成**共用**一塊、記住大小、需要時才擴大 | 減少配置次數 |
| 18.2 | 把遞迴的 `AP_pow` 改寫成**迭代**的「平方再乘」演算法（Knuth 4.6.3） | 迭代通常比較快，但真正的好處是**中間值配置的空間比較少**；x、y 要多大才看得出差別？ |
| 18.3 | 實作 `AP_ceil(x, y)` 和 `AP_floor(x, y)` | 一定要寫清楚 x、y 異號時的行為 |
| 18.4 | AP 介面很「**吵**」（參數多、輸入輸出容易搞混），設計一個用 **Seq_T 當堆疊**取運算元、存結果的介面 | 介面要乾淨，但不能少了重要的功能 |
| 18.5 | 實作在指定範圍內均勻分布的 AP 亂數產生器 | |
| 18.6 | 設計**模 n 運算**的介面，值域是 0 到 n−1 | 除法只有在這個集合是**有限體**時才有定義，也就是 n 是**質數**時 |
| 18.7 | 用 **Karatsuba 演算法**實作遞迴的 `AP_mul`：O(n^1.58) 取代 O(n²) | xy = acBⁿ + (ad+bc)B^(n/2) + bd，而 ad+bc = ac + bd + (a−b)(d−c)，**4 次乘法變 3 次**；n 多大時明顯比較快？ |

---

## 8. 本章重點整理

1. **AP = 有號、任意精度、不透明的大整數**，建立在 XP 之上，並補上 XP 省略的配置和檢查。
2. **每個運算都回傳新的 AP_T**，client 要負責釋放，`calc` 示範了「只有堆疊上的值是永久的」這個協定。
3. **除法向左截斷、餘數為正**，和第 2 章的 `Arith` 一致。
4. **表示方式**：`{sign, ndigits, size, digits}`，用符號加大小；**零只用 +0**；**永遠正規化**。
5. **加減法依符號分情況**：同號（加法）或異號（減法）時大小相加，否則比較大小後相減；結果的符號依情況決定，而且每次都要特別處理零。
6. **除法**：XP_div 計算大小，異號而且有餘數時，商的大小 +1、餘數改成 |y| − r。
7. **次方**：快速冪 O(lg y)；取模時用 `mulmod` 讓中間值保持在 p² 以下。
8. **便利函式**用堆疊上的暫時 AP_T，不配置記憶體；`AP_tostr` 先複製再呼叫會破壞輸入的 `XP_tostr`。

> **一句話**：AP 在 XP 的無號大數上加了符號、自動配置和完整的錯誤檢查，變成一個應用可以直接使用的任意精度整數；`calc` 範例則把全書的 Stack、Fmt、AP 串起來，同時示範了所有權協定和介面缺陷的代價。
