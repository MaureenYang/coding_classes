# 第 17 章　Extended-Precision Arithmetic（擴展精度算術：XP）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.297–322

---

## 1. 本章定位

### 1.1 為什麼需要大數？

- 32 位元整數的範圍：有號 −2,147,483,648 到 +2,147,483,647（二補數），無號 0 到 4,294,967,295。對很多應用已經夠用，但**有些應用需要更大的範圍**。
- **整數**：在一個比較小的範圍內表示**每一個**整數值。
- **浮點數**：在一個很大的範圍內只表示**相對少數**的值。
  - 可以接受近似值時（例如很多科學計算）能用浮點數。
  - **需要一個很大範圍內的所有整數值時，浮點數就不能用了。**

### 1.2 三層算術介面

| 章 | 介面 | 層級 | 特性 |
|---|---|---|---|
| **17** | **XP** | **最低階** | 無號、**固定位數**、不配置記憶體、**幾乎不檢查錯誤** |
| 18 | AP | 高階 | 有號、**任意精度**、自動配置、完整檢查 |
| 19 | MP | 中階 | 有號和無號、**固定位元數**、二補數、檢查溢位 |

> **XP 的設計目的是當作 AP、MP 的基礎**，而不是讓一般應用直接使用。可以表示的值只受限於可用的記憶體。

---

## 2. 表示方式

### 2.1 多項式表示

一個 n 位數的無號整數 x 表示成：

```
x = x[n-1]·b^(n-1) + x[n-2]·b^(n-2) + … + x[1]·b + x[0]
```

其中 b 是**底數**，0 ≤ xᵢ < b。

- 32 位元的無號整數就是 n = 32、b = 2，每個係數是一個位元。
- 這個表示法可以推廣到任何底數。例如 b = 10 時，2,147,483,647 可以表示成：

```c
unsigned char x[] = { 7, 4, 6, 3, 8, 4, 7, 4, 1, 2 };   /* 最低位在前 */
```

**⭐ 最低位數（least significant digit）在前**：這是**實作算術運算最方便**的順序，因為加減乘都是從低位往高位進位。

### 2.2 底數的選擇

**底數越大，每一位能表示的值越大，可能越省記憶體**：

| 底數 | 2,147,483,647 的表示 | 大小 |
|---|---|---|
| 10 | `{7,4,6,3,8,4,7,4,1,2}` | 10 位數 |
| 2¹⁶ | `{65535, 32767}` | 4 位元組 |
| **2⁸** | **`{255, 255, 255, 127}`** | **4 位元組** |

**⭐ 為什麼 XP 選 b = 2⁸，每一位存在一個 `unsigned char`？**

- 底數是 2ᵏ、k 又剛好是某個 C 無號型別的大小時，**不會浪費空間**。
- **但大的底數會讓某些運算的實作變複雜**，主要是除法。
- 如果 **`unsigned long` 能存得下 b³ − 1**，這些複雜度就可以避免（見除法一節）。
- 標準 C 保證 `unsigned long` **至少 32 位元**，能存 b³ − 1 = 2²⁴ − 1。
- ⇒ **b = 2⁸ = 256 是同時符合「是 2 的冪」、「是內建型別的大小」、「b³ − 1 存得進 32 位元」的最大值。**

---

## 3. 介面（17.1 Interface）

```c
/* xp.h */
#ifndef XP_INCLUDED
#define XP_INCLUDED

#define T XP_T
typedef unsigned char *T;     /* 公開表示方式！ */

extern int XP_add     (int n, T z, T x, T y, int carry);
extern int XP_sub     (int n, T z, T x, T y, int borrow);
extern int XP_mul     (T z, int n, T x, int m, T y);
extern int XP_div     (int n, T q, T x, int m, T y, T r, T tmp);
extern int XP_sum     (int n, T z, T x, int y);
extern int XP_diff    (int n, T z, T x, int y);
extern int XP_product (int n, T z, T x, int y);
extern int XP_quotient(int n, T z, T x, int y);
extern int XP_neg     (int n, T z, T x, int carry);
extern int XP_cmp     (int n, T x, T y);
extern void XP_lshift (int n, T z, int m, T x, int s, int fill);
extern void XP_rshift (int n, T z, int m, T x, int s, int fill);
extern int           XP_length (int n, T x);
extern unsigned long XP_fromint(int n, T z, unsigned long u);
extern unsigned long XP_toint  (int n, T x);
extern int   XP_fromstr(int n, T z, const char *str, int base, char **end);
extern char *XP_tostr  (char *str, int size, int base, int n, T x);

#undef T
#endif
```

**`XP_T` 就是 `unsigned char *`**：一個存放 n 位數、底數 2⁸、**最低位在前**的陣列。

### 3.1 ⭐ 一個「危險」的介面

函式以 n 當輸入，XP_T 同時當輸入和輸出參數，陣列必須夠大，裝得下 n 位數。

**以下都是 unchecked runtime error**：傳入 NULL 的 XP_T、**太小**的 XP_T、或不是正數的長度。

> **XP 是一個危險的介面，因為它省略了大部分的 checked runtime error。** 理由有兩個：
> 1. **XP 的預期使用者是更高階的介面**（AP、MP），它們應該自己規定並實作必要的檢查。
> 2. **XP 的介面盡量簡單**，必要時某些函式可以**用組合語言實作**來追求效能。**這也是 XP 的函式都不配置記憶體的原因。**

> 這是第 2 章的「**分層**」思想：低階層追求速度和簡單，把安全性交給高階層。

### 3.2 加減法

```c
extern int XP_add(int n, T z, T x, T y, int carry);   /* z = x + y + carry  */
extern int XP_sub(int n, T z, T x, T y, int borrow);  /* z = x − y − borrow */
```

- x、y、z 都是 n 位數；`carry`/`borrow` 必須是 0 或 1。
- **回傳最高位的進位或借位**：`XP_add` 回傳 1 代表結果**放不進 n 位數**；`XP_sub` 回傳 1 代表 **y > x**。
- **只有這兩個函式**允許 x、y、z 是同一個 XP_T（例如 `XP_add(n, x, x, y, 0)` 就是 x += y）。

### 3.3 乘法

```c
extern int XP_mul(T z, int n, T x, int m, T y);   /* z = z + x·y */
```

- x 有 n 位、y 有 m 位，**z 必須能放 n+m 位**。
- **注意是 `z = z + x·y`**：把乘積**加到** z 上。z 先清成 0 的話就得到 x·y。
- 回傳擴增後 n+m 位乘積的最高位進位。
- **z 和 x 或 y 是同一個 XP_T 是 unchecked runtime error。**

**關於 `const` 的討論**：
```c
extern int XP_mul(T z, int n, const unsigned char *x, int m, const unsigned char *y);
```
這樣寫能明確表示 x、y 是輸入、z 是輸出，暗示 z 不應該和 x、y 相同。但是：
- **不能寫 `const T`**，因為那代表「常數指標」，而不是「指向常數的指標」（和第 2 章同樣的問題）。
- const **無法防止**把同一個 XP_T 同時當 x 和 z 傳入，因為 `unsigned char *` 可以自動轉成 `const unsigned char *`。
- 結論：**const 那一點點好處，抵不過它在 XP 裡造成的囉嗦。**

### 3.4 除法

```c
extern int XP_div(int n, T q, T x, int m, T y, T r, T tmp);
```

- 計算 **q = x / y** 和 **r = x mod y**。q 和 x 有 n 位，r 和 y 有 m 位。
- **y 是 0 時回傳 0**，q、r 不變；否則回傳 1。
- **`tmp` 至少要能放 n+m+2 位**，因為 XP 不配置記憶體，暫存空間要由呼叫端提供。
- q 或 r 是 x 或 y 之一、q 和 r 是同一個、或 tmp 太小，都是 unchecked error。

### 3.5 單一位數運算

```c
extern int XP_sum     (int n, T z, T x, int y);   /* z = x + y，回傳進位 */
extern int XP_diff    (int n, T z, T x, int y);   /* z = x − y，回傳借位 */
extern int XP_product (int n, T z, T x, int y);   /* z = x · y，回傳進位（可達 2⁸−1）*/
extern int XP_quotient(int n, T z, T x, int y);   /* z = x / y，回傳餘數 */
```

用 **一個底數 2⁸ 的位數 y** 對 n 位數的 XP_T 做加減乘除。
- `XP_sum`/`XP_diff`：y 必須是正數而且**不超過底數 2⁸**。
- `XP_product`/`XP_quotient`：y **不可超過 2⁸ − 1**。

### 3.6 其他

| 函式 | 功能 |
|---|---|
| `XP_neg(n, z, x, carry)` | z = ~x + carry。carry = 0 是**一補數**取負，carry = 1 是**二補數**取負 |
| `XP_cmp(n, x, y)` | 比較，回傳 `<0`、`0`、`>0` |
| `XP_lshift(n, z, m, x, s, fill)` | z = x 左移 s 位元；z 有 n 位、x 有 m 位；空出的位元填 fill（0 或 1） |
| `XP_rshift(n, z, m, x, s, fill)` | 右移。**fill = 0 是邏輯右移，fill = 1 可以用來實作算術右移** |
| `XP_length(n, x)` | 有效位數，也就是最高非零位數的索引 + 1 |
| `XP_fromint(n, z, u)` | z = u mod 2⁸ⁿ，**回傳放不進 z 的部分** u / 2⁸ⁿ |
| `XP_toint(n, x)` | 回傳 x mod (ULONG_MAX+1)，也就是最低的 8·sizeof(unsigned long) 個位元 |

### 3.7 字串轉換

```c
extern int   XP_fromstr(int n, T z, const char *str, int base, char **end);
extern char *XP_tostr  (char *str, int size, int base, int n, T x);
```

**`XP_fromstr`**：像 `strtoul`。
- 忽略開頭的空白，接受一個或多個 base 進位的數字；base 是 11 到 36 時，大小寫字母都可以當作大於 9 的數字。
- 用**乘加演算法**累積：`z ← base·z + 數字值`。
- **⚠ z 不會被清成 0，client 必須自己初始化。**
- 回傳乘法第一個非零的進位，**非零代表數字放不進 z**。
- `end` 不是 NULL 時，`*end` 指向停止解析的字元；不是合法數字時回傳 0，並把 `*end` 設成 `str`。
- base 不在 2 到 36、str 是 NULL，都是 checked error。

**`XP_tostr`**：把 x 轉成 base 進位的字串，用大寫字母表示大於 9 的數字。
- **⚠ x 會被設成 0！**（因為轉換過程是用除法把 x 一位一位剝掉的。）
- `size` 太小是 checked error。

---

## 4. 實作（17.2 Implementation）

```c
#define T XP_T
#define BASE (1<<8)
```

### 4.1 整數轉換

```c
unsigned long XP_fromint(int n, T z, unsigned long u) {
    int i = 0;
    do
        z[i++] = u%BASE;
    while ((u /= BASE) > 0 && i < n);
    for ( ; i < n; i++)
        z[i] = 0;
    return u;                   /* 剩下放不進去的部分 */
}

unsigned long XP_toint(int n, T x) {
    unsigned long u = 0;
    int i = (int)sizeof u;
    if (i > n)
        i = n;
    while (--i >= 0)
        u = BASE*u + x[i];      /* 從高位往低位累積 */
    return u;
}

int XP_length(int n, T x) {
    while (n > 1 && x[n-1] == 0)
        n--;
    return n;
}
```

> **風格說明**：`u%BASE` 其實不是必要的，因為指派給 `unsigned char` 本身就會取模。XP 的算術函式**刻意寫出這些明確的運算來說明演算法**。底數是 2 的常數冪次，大多數編譯器會把乘、除、取模轉成左移、右移、AND。

### 4.2 加法：小學的直式加法

```
       進位：   1   0   1   0
                 9   4   2   8
             +       7   3   2
             ─────────────────
         S： 1  10  11  06  10
```

從最低位到最高位，每一步：**S = carry + xᵢ + yᵢ；zᵢ = S mod b；新的 carry = S / b**。

```c
int XP_add(int n, T z, T x, T y, int carry) {
    int i;
    for (i = 0; i < n; i++) {
        carry += x[i] + y[i];      /* carry 暫時存放 S */
        z[i] = carry%BASE;
        carry /= BASE;             /* 然後只留下進位 */
    }
    return carry;
}
```

**範圍分析**：單一位數的和最大是 (b−1) + (b−1) + 1 = 2b − 1 = **511**，`int` 輕鬆放得下。

### 4.3 減法

每一步：**D = xᵢ + b − borrow − yᵢ；zᵢ = D mod b；新的 borrow = 1 − D/b**。

```c
int XP_sub(int n, T z, T x, T y, int borrow) {
    int i;
    for (i = 0; i < n; i++) {
        int d = (x[i] + BASE) - borrow - y[i];   /* 先加 b，避免負數 */
        z[i] = d%BASE;
        borrow = 1 - d/BASE;
    }
    return borrow;                 /* 非零代表 x < y */
}
```

**技巧**：先加上 BASE 確保 d **永遠不是負數**，避開有號數除法和取模的語意問題（第 2 章）。d 最大是 (b−1) + b = 511。

### 4.4 單一位數加減與取負

```c
int XP_sum(int n, T z, T x, int y) {     /* 把 y 當成初始進位 */
    int i;
    for (i = 0; i < n; i++) {
        y += x[i];
        z[i] = y%BASE;
        y /= BASE;
    }
    return y;
}

int XP_diff(int n, T z, T x, int y) {    /* 把 y 當成初始借位 */
    int i;
    for (i = 0; i < n; i++) {
        int d = (x[i] + BASE) - y;
        z[i] = d%BASE;
        y = 1 - d/BASE;
    }
    return y;
}

int XP_neg(int n, T z, T x, int carry) {
    int i;
    for (i = 0; i < n; i++) {
        carry += (unsigned char)~x[i];   /* 先取補數再加 */
        z[i] = carry%BASE;
        carry /= BASE;
    }
    return carry;
}
```

**巧妙之處**：單一位數運算**把第二個運算元直接當成進位或借位**，第一輪處理完它，之後就和一般的進位傳遞一樣。

`XP_neg` 的轉型確保 `~x[i]` 小於 b。`~` 會先把 `x[i]` 提升成 `int`，高位全部變成 1，所以要轉回 `unsigned char`。

### 4.5 乘法

x 有 n 位、y 有 m 位，z = x·y 由 **m 個 n 位數的部分積**相加，結果有 n+m 位。

```
                   7   3   2
         ×     9   4   2   8
         ─────────────────
               5   8   5   6     ← 8 × 732
           1   4   6   4         ← 2 × 732（左移 1 位）
       2   9   2   8             ← 4 × 732（左移 2 位）
 + 6   5   8   8                 ← 9 × 732（左移 3 位）
 ─────────────────────────
   6   9   0   1   2   9   6
```

**不需要明確計算部分積**：每算出一位就**直接加到 z 對應的位置**。涉及 xᵢ 的部分積，從 z 的第 i 位開始加。

```c
int XP_mul(T z, int n, T x, int m, T y) {
    int i, j, carryout = 0;
    for (i = 0; i < n; i++) {
        unsigned carry = 0;
        for (j = 0; j < m; j++) {             /* 部分積 x[i]·y 加到 z[i..] */
            carry += x[i]*y[j] + z[i+j];
            z[i+j] = carry%BASE;
            carry /= BASE;
        }
        for ( ; j < n + m - i; j++) {         /* 把進位傳遞到更高位 */
            carry += z[i+j];
            z[i+j] = carry%BASE;
            carry /= BASE;
        }
        carryout |= carry;                    /* 記錄是否溢出 z 的最高位 */
    }
    return carryout;
}
```

**範圍分析**：carry 最大是 (b−1)(b−1) + (b−1) = b² − b = **65,280**，`unsigned` 放得下（標準保證 `unsigned` 至少 16 位元）。

```c
int XP_product(int n, T z, T x, int y) {    /* 等於 m = 1、z 清成 0 的 XP_mul */
    int i;
    unsigned carry = 0;
    for (i = 0; i < n; i++) {
        carry += x[i]*y;
        z[i] = carry%BASE;
        carry /= BASE;
    }
    return carry;
}
```

### 4.6 ⭐ 除法：最複雜的運算

**簡單但不適用的遞迴演算法**：
```
if x < y then q ← 0, r ← x
else
    q′ ← x/2y, r′ ← x mod 2y
    if r′ < y then q ← 2q′, r ← r′
    else          q ← 2q′ + 1, r ← r′ − y
```
問題是 q′ 和 r′ 需要**配置記憶體**，遞迴深度可達 lg x，**而 XP 禁止隱含的配置**。

**XP_div 的結構：**

```c
int XP_div(int n, T q, T x, int m, T y, T r, T tmp) {
    int nx = n, my = m;
    n = XP_length(n, x);         /* 用有效位數 */
    m = XP_length(m, y);
    if (m == 1) {
        /* single-digit division（也處理除以 0）*/
    } else if (m > n) {          /* x < y：q = 0，r = x */
        memset(q, '\0', nx);
        memcpy(r, x, n);
        memset(r + n, '\0', my - n);
    } else {
        /* long division */
    }
    return 1;
}
```

**先檢查單一位數除法**，因為這個情況也處理了**除以 0**。

#### 單一位數除法

```
         1   3   4   6
     ┌──────────────────
   7 │ 09  24  32  48     餘 6
```

從**最高位**到最低位，每一步：**R = carry·b + xᵢ；qᵢ = R / y₀；新的 carry = R mod y₀**。

```c
int XP_quotient(int n, T z, T x, int y) {
    int i;
    unsigned carry = 0;
    for (i = n - 1; i >= 0; i--) {         /* 由高到低 */
        carry = carry*BASE + x[i];
        z[i] = carry/y;
        carry %= y;
    }
    return carry;                            /* 餘數 */
}

/* single-digit division */
if (y[0] == 0)
    return 0;                                /* 除以 0 */
r[0] = XP_quotient(nx, q, x, y[0]);
memset(r + 1, '\0', my - 1);
```

R 最大是 (b−1)b + (b−1) = b² − 1 = 65,535，`unsigned` 放得下。

#### ⭐ 長除法（m ≥ 2）

以 615,367 ÷ 296（十進位）為例，被除數前面**補一個 0**，讓 n 大於 m：

| k | rem | qₖ | dq = y·qₖ |
|---|---|---|---|
| 3 | 0**615**367 | 2 | 0592 |
| 2 | 0**233**67 | 0 | 0000 |
| 1 | **2336**7 | 7 | 2072 |
| 0 | **2647** | 8 | 2368 |
| | 279（餘數） | | |

```
rem ← 前面補 0 的 x
for (k = n - m; k >= 0; k--) {
    計算 qₖ
    dq ← y · qₖ
    q[k] = qₖ
    rem ← rem − dq · bᵏ
}
r ← rem
```

- 每一輪用 **m 位數的除數**去除 **rem 的 m+1 位數前綴**，算出一位商。
- 每輪結束時 rem 減去 qₖ·y，**長度減少一位**。
- **tmp 的用途**：rem 需要 n+1 位，dq 需要 m+1 位，**合計 n+m+2**，這就是 tmp 大小要求的由來。

```c
/* long division */
int k;
unsigned char *rem = tmp, *dq = tmp + n + 1;
assert(2 <= m && m <= n);
memcpy(rem, x, n);
rem[n] = 0;
for (k = n - m; k >= 0; k--) {
    int qk;
    /* compute qk, dq ← y·qk */
    q[k] = qk;
    /* rem ← rem − dq·bᵏ */
}
memcpy(r, rem, m);
/* fill out q and r with 0s */
```

#### ⭐ 估計商的每一位：Brinch-Hansen 的方法

**太慢的做法**：qₖ 從 b−1 開始，只要 y·qₖ 大於 rem 的前綴就減一，**最多要 b−1 次**，每次都要做 m 位數的乘法和比較。

**好方法**：
> **用 rem 的前 3 位除以 y 的前 2 位，得到的估計值要嘛正確，要嘛剛好大 1。**

所以只要**一次檢查、最多一次修正**：

```c
/* compute qk, dq ← y·qk */
{
    int i;
    assert(2 <= m && m <= k+m && k+m <= n);
    {   /* qk ← y[m-2..m-1] / rem[k+m-2..k+m] */
        int km = k + m;
        unsigned long y2 = y[m-1]*BASE + y[m-2];                         /* y 的前 2 位 */
        unsigned long r3 = rem[km]*(BASE*BASE) + rem[km-1]*BASE + rem[km-2];  /* rem 的前 3 位 */
        qk = r3/y2;
        if (qk >= BASE)
            qk = BASE - 1;
    }
    dq[m] = XP_product(m, dq, y, qk);
    for (i = m; i > 0; i--)                  /* 比較 rem[k..k+m] 和 dq */
        if (rem[i+k] != dq[i])
            break;
    if (rem[i+k] < dq[i])                    /* 估計大了 1 */
        dq[m] = XP_product(m, dq, y, --qk);
}
```

**⭐ 這就是限制 BASE 大小的原因**：
- r3 最大是 (b−1)b² + (b−1)b + (b−1) = **b³ − 1** = 16,777,215。
- r3 必須放得進 `unsigned long`（至少 32 位元），所以 b³ − 1 < 2³²，**b < 2^10.67 ≈ 1625**。
- **256 是不超過 1625、又剛好是內建型別大小的最大 2 的冪。**

**從 rem 減去 dq·bᵏ**：把指標指向 rem 適當的位置，直接重複使用 `XP_sub`：

```c
/* rem ← rem − dq·bᵏ */
{
    int borrow;
    assert(0 <= k && k <= k+m);
    borrow = XP_sub(m + 1, &rem[k], &rem[k], dq, 0);
    assert(borrow == 0);
}
```

「乘上 bᵏ」等於「位移 k 位」，傳 `&rem[k]` 就是位移，而 XP_sub 允許 z 和 x 相同。

### 4.7 比較

```c
int XP_cmp(int n, T x, T y) {
    int i = n - 1;
    while (i > 0 && x[i] == y[i])       /* 從最高位開始找第一個不同的位數 */
        i--;
    return x[i] - y[i];
}
```

### 4.8 位移：兩步驟

位移 s 個位元分成兩步：
1. **先以位元組為單位**位移 s/8 個位元組（搬陣列元素）。
2. **再位移剩下的 s mod 8 個位元**。

`fill` 先轉成全 1（0xFF）或全 0，才能一次填一整個位元組。

```c
void XP_lshift(int n, T z, int m, T x, int s, int fill) {
    fill = fill ? 0xFF : 0;
    {   /* shift left by s/8 bytes */
        int i, j = n - 1;
        if (n > m)
            i = m - 1;
        else
            i = n - s/8 - 1;
        for ( ; j >= m + s/8; j--)
            z[j] = 0;                       /* 超出 x 的高位清成 0 */
        for ( ; i >= 0; i--, j--)
            z[j] = x[i];                    /* 搬移（從高位開始）*/
        for ( ; j >= 0; j--)
            z[j] = fill;                    /* 低位填 fill */
    }
    s %= 8;
    if (s > 0) {
        /* shift z left by s bits */
        XP_product(n, z, z, 1<<s);          /* 左移 s 位 = 乘以 2ˢ */
        z[0] |= fill>>(8-s);                /* 最低的 s 個位元填 fill */
    }
}

void XP_rshift(int n, T z, int m, T x, int s, int fill) {
    fill = fill ? 0xFF : 0;
    {   /* shift right by s/8 bytes */
        int i, j = 0;
        for (i = s/8; i < m && j < n; i++, j++)
            z[j] = x[i];
        for ( ; j < n; j++)
            z[j] = fill;                    /* 空出來的和多出來的都填 fill */
    }
    s %= 8;
    if (s > 0) {
        /* shift z right by s bits */
        XP_quotient(n, z, z, 1<<s);         /* 右移 s 位 = 除以 2ˢ */
        z[n-1] |= fill<<(8-s);              /* 最高的 s 個位元填 fill */
    }
}
```

**巧妙之處**：**位元等級的位移直接重複使用乘法和除法**，因為左移 s 位就是乘以 2ˢ，右移就是除以 2ˢ。

### 4.9 字串轉換

```c
static char map[] = {
     0,  1,  2,  3,  4,  5,  6,  7,  8,  9,       /* '0'..'9' */
    36, 36, 36, 36, 36, 36, 36,                   /* ':'..'@'（非法）*/
    10, 11, ... , 35,                              /* 'A'..'Z' */
    36, 36, 36, 36, 36, 36,                       /* '['..'`'（非法）*/
    10, 11, ... , 35                               /* 'a'..'z' */
};

/* *p is a digit in base */
(*p && isalnum(*p) && map[*p-'0'] < base)

int XP_fromstr(int n, T z, const char *str, int base, char **end) {
    const char *p = str;
    assert(p);
    assert(base >= 2 && base <= 36);
    while (*p && isspace(*p))
        p++;
    if (/* *p is a digit in base */) {
        int carry;
        for ( ; /* *p is a digit in base */; p++) {
            carry = XP_product(n, z, z, base);     /* z ← base·z */
            if (carry)
                break;                             /* 溢位就停止 */
            XP_sum(n, z, z, map[*p-'0']);          /* z ← z + 數字值 */
        }
        if (end)
            *end = (char *)p;
        return carry;
    } else {
        if (end)
            *end = (char *)str;
        return 0;
    }
}
```

**`map` 的技巧**：`map[c - '0']` 是字元 c 的數字值。'0' 到 'z' 之間的非法字元對應到 **36**，這個值**一定 ≥ 任何合法的 base**，所以只要檢查 `map[c-'0'] < base` 就能判斷合法性。（假設是 ASCII 字元順序。）

```c
char *XP_tostr(char *str, int size, int base, int n, T x) {
    int i = 0;
    assert(str);
    assert(base >= 2 && base <= 36);
    do {
        int r = XP_quotient(n, x, x, base);    /* x ← x / base，r 是最低位 */
        assert(i < size);
        str[i++] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[r];
        while (n > 1 && x[n-1] == 0)           /* 縮短 n，加速後續的除法 */
            n--;
    } while (n > 1 || x[0] != 0);
    assert(i < size);
    str[i] = '\0';
    {   /* reverse str */
        int j;
        for (j = 0; j < --i; j++) {
            char c = str[j];
            str[j] = str[i];
            str[i] = c;
        }
    }
    return str;
}
```

- 標準演算法：**不斷除以 base，餘數就是從最低位開始的各個數字**。
- 數字是**反著**產生的，所以最後要反轉。
- **這就是 x 會被清成 0 的原因**：它被原地除到變成 0。
- 每輪都縮短 n，讓之後的除法越來越快。

---

## 5. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **⭐ 分層設計** | XP 是低階的基礎：快、簡單、不配置、不檢查；安全性交給 AP 和 MP |
| **公開表示方式** | `typedef unsigned char *XP_T`，讓高階層和組合語言實作能直接操作 |
| **呼叫端提供空間** | 所有輸出和暫存（例如 `tmp`）都由呼叫端配置 |
| **最低位在前** | 進位傳遞的方向和陣列索引一致 |
| **底數選擇的工程分析** | b³ − 1 必須放得進 unsigned long → b ≤ 256 |
| **範圍分析** | 每個中間值的最大值都算清楚，確認型別放得下 |
| **避免負數運算** | 減法先加 BASE |
| **重複使用** | 位移用乘除法實作；長除法用 `XP_sub` 加上指標位移；單一位數運算把運算元當進位 |
| **演算法選擇** | 不用需要配置的遞迴除法；用 Brinch-Hansen 估計商的位數 |
| **小學算術系統化** | 加減乘除都是直式計算的程式化版本 |
| **const 的取捨** | 好處太少、太囉嗦，所以不用 |

### 運算的位數規則

| 運算 | 輸入 | 輸出 |
|---|---|---|
| 加、減 | n 位 + n 位 | n 位 + 進位或借位 |
| 乘 | n 位 × m 位 | **n+m** 位 |
| 除 | n 位 ÷ m 位 | 商 n 位、餘數 m 位，tmp 要 **n+m+2** 位 |

---

## 6. 延伸閱讀重點

- XP 的大部分算術函式都是**每個人小學學過的演算法**的直接實作。
- **Hennessy & Patterson (1994)** 第 4 章、**Knuth (1981)** 第 4.3 節：經典的算術演算法，Knuth 也很好地整理了這些演算法的悠久歷史。
- **Brinch-Hansen (1994)**：XP_div 的演算法來源，包括「**估計的商最多大 1**」的**證明**；還說明了怎麼**縮放運算元**來避免大部分的修正，代價是多一次單一位數的乘法和除法。

---

## 7. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 17.1 | 實作遞迴除法，和 Brinch-Hansen 比較時間和空間；有沒有遞迴版本比較好的情況？ | 配置成本 vs. 簡單 |
| 17.2 | 實作 Hennessy & Patterson 第 4 章的「**位移減法**」除法並比較 | 逐位元的除法 |
| 17.3 | 改用**底數 2¹⁶**，大多數函式快一倍；但除法需要 (2¹⁶)³ − 1，在 32 位元機器上**超過 ULONG_MAX**。想辦法解決，並量測值不值得 | 底數和除法估計之間的權衡 |
| 17.4 | 同上，改用底數 2³² | |
| 17.5 | 用**組合語言**重新實作 XP | 很多機器有雙倍精度指令，也很容易取得進位和借位 |
| 17.6 | 實作在指定範圍內**均勻分布**的大數亂數產生器 | |

---

## 8. 本章重點整理

1. **XP 是三層算術介面的最底層**：無號、固定 n 位、底數 2⁸、最低位在前、`XP_T` 就是 `unsigned char *`。
2. **刻意危險**：幾乎沒有 checked error、不配置記憶體，因為使用者是 AP 和 MP，而且方便用組合語言實作。
3. **底數 256 的理由**：除法估計需要 b³ − 1 放得進 32 位元的 unsigned long，所以 b ≤ 1625，256 是其中最大、又剛好是內建型別大小的 2 的冪。
4. **加、減、乘就是直式計算**；加減法回傳進位或借位；乘法是 z += x·y，結果 n+m 位；減法先加 BASE 避免負數。
5. **除法**：單一位數直接用 C 除法；長除法用「rem 前 3 位 ÷ y 前 2 位」估計商（最多大 1，只要修正一次）；tmp 要 n+m+2 位。
6. **位移**先搬位元組，再用乘除 2ˢ 處理剩下的位元。
7. **字串轉換**：fromstr 用乘加，z 要先初始化；tostr 不斷除以 base 再反轉，**x 會被清成 0**。

> **一句話**：XP 把小學的直式算術系統化，做成一個不配置記憶體、不檢查錯誤、追求速度的大數底層，把安全和便利交給上面的 AP 和 MP。
