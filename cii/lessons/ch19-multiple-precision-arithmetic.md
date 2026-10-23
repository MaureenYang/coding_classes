# 第 19 章　Multiple-Precision Arithmetic（多精度算術：MP）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.357–403

---

## 1. 本章定位

**MP** 是三個算術介面的最後一個，提供**無號**和**二補數有號**整數的多精度算術。

### 1.1 MP 和 XP、AP 的比較

| | XP（第 17 章） | AP（第 18 章） | **MP** |
|---|---|---|---|
| 長度單位 | 位元組（位數） | 自動 | **位元** |
| 長度 | 每次呼叫指定 | 任意、自動成長 | **用 `MP_set` 設定一次，全部共用** |
| 符號 | 無號 | 符號 + 大小 | **無號和二補數都有** |
| 型別 | 公開的 `unsigned char *` | 不透明 | **公開的 `unsigned char *`** |
| 錯誤檢查 | 幾乎沒有 | 完整 | **完整** |
| 溢位 | 回傳進位 | 不會溢位 | **丟出 `MP_Overflow`** |
| 配置 | 從不配置 | 每個運算都配置 | **幾乎不配置** |

- **和 XP 一樣**：公開表示方式，函式操作**指定大小**的整數。
- **和 XP 不同**：長度以**位元**為單位，而且**同時提供有號和無號**運算。
- **和 AP 一樣**：實作一般的 checked runtime error。

### 1.2 適用場合

> MP 適合需要擴展精度、但**想要更精細地控制配置**、**同時需要有號和無號運算**、或**必須模擬 n 位元二補數算術**的應用。

**範例**：
- **加密**：有些現代加密演算法要處理**幾百位數的固定精度整數**。
- **Cross compiler**：在平台 X 上執行、替平台 Y 產生程式碼。如果 Y 的整數比 X 大，編譯器可以用 MP 處理 Y 大小的整數，例如用 128 位元算術處理常數。
- **浮點常數轉換**：編譯器把浮點常數轉成最接近的浮點值時，必須使用多精度算術。

---

## 2. 介面（19.1 Interface）

MP 介面很大：**49 個函式和 2 個例外**，因為它要為 n 位元有號和無號整數提供完整的算術函式。

```c
/* mp.h（節錄）*/
#ifndef MP_INCLUDED
#define MP_INCLUDED
#include <stdarg.h>
#include <stddef.h>
#include "except.h"

#define T MP_T
typedef unsigned char *T;

extern const Except_T MP_Dividebyzero;
extern const Except_T MP_Overflow;

extern int MP_set(int n);
extern T   MP_new(unsigned long u);
/* ... 47 個其他函式 ... */

#undef T
#endif
```

### 2.1 表示方式

- n 位元整數用 **⌈n/8⌉ 個位元組**表示，**最低位元組在前**（和 XP 相同）。
- 有號整數用**二補數**表示，**第 n−1 位是符號位元**。
- 傳 NULL 的 MP_T 是 checked runtime error；但傳**太小**而放不下 n 位元整數的 MP_T 是 **unchecked** runtime error。

### 2.2 ⭐ `MP_set`：全域的精度設定

```c
extern int MP_set(int n);
```

- MP 一開始**自動初始化成 32 位元**算術。
- `MP_set(n)` 讓之後的呼叫都做 **n 位元**算術，並回傳之前的大小。n 小於 2 是 checked error。
- 可能丟出 `Mem_Failed`。

**為什麼用全域設定，而不是每次傳 n？**

> **一旦初始化之後，大多數應用只會用一種大小的擴展整數**，例如 cross compiler 一律用 128 位元算術處理常數。這個設計照顧了這類應用：
> 1. 簡化其他 MP 函式的使用方式，**參數比較少**。
> 2. **更重要的是：來源和目的參數沒有任何限制**，同一個 MP_T 永遠可以**同時**當來源和目的。
>
> 之所以能取消這些限制，是因為**某些函式需要的暫存空間只取決於 n**，所以可以**在 `MP_set` 裡一次配置好**。

> 和 XP 對比：`XP_mul` 的 z 不能等於 x 或 y，`XP_div` 的 q、r 不能是 x 或 y。MP 用預先配置的暫存空間，**完全消除了這些限制**。

**這個設計也避免了配置**：除了 `MP_set` 以外，48 個函式中**只有 4 個**會配置記憶體。

### 2.3 建立與整數轉換

```c
extern T MP_new     (unsigned long u);      /* 配置一個 MP_T，初始化成 u */
extern T MP_fromint (T z, long v);           /* z = v（有號）*/
extern T MP_fromintu(T z, unsigned long u);  /* z = u（無號）*/
```

`u` 或 `v` 放不進 n 位元時丟出 **`MP_Overflow`**：
- `MP_new` 和 `MP_fromintu`：u > 2ⁿ − 1 時。
- `MP_fromint`：v < −2ⁿ⁻¹ 或 v > 2ⁿ⁻¹ − 1 時。

### 2.4 ⭐ 先算出結果，再丟出例外

> **所有 MP 函式都會先計算並設定好結果，然後才丟出例外**，多出來的位元直接丟掉。

```c
MP_T z;
MP_set(8);
z = MP_new(0);
MP_fromintu(z, 0xFFF);    /* z 被設成 0xFF，然後丟出 MP_Overflow */
```

所以 client 可以用 TRY-EXCEPT **忽略溢位**，取得截斷後的結果：

```c
TRY
    MP_fromintu(z, 0xFFF);
EXCEPT(MP_Overflow) ;      /* 忽略溢位 */
END_TRY;
/* z == 0xFF */
```

> 這讓 MP 可以**同時**做到「偵測溢位」和「模擬 n 位元的截斷算術」（例如模擬機器的整數運算）。

**例外**：`MP_toint` 和 `MP_tointu` 回傳 C 的 long 或 unsigned long，放不下時丟出 `MP_Overflow`，而且**沒辦法取得結果**。

### 2.5 大小轉換

```c
extern unsigned long MP_tointu(T x);
extern long          MP_toint (T x);
extern T MP_cvt (int m, T z, T x);    /* x 轉成 m 位元有號，存進 z */
extern T MP_cvtu(int m, T z, T x);    /* x 轉成 m 位元無號，存進 z */
```

- `MP_cvt`/`MP_cvtu` 在放不下時會丟出 `MP_Overflow`，**但會先設定好 z**。
- m 大於 x 的位元數時，`MP_cvtu` **補 0**，`MP_cvt` 用 x 的**符號位元延伸**。
- 例如取得 x 最低的 `8*sizeof(unsigned)` 個位元，不管 x 多大：

```c
unsigned char z[sizeof (unsigned)];
TRY
    MP_cvtu(8*sizeof (unsigned), z, x);
EXCEPT(MP_Overflow) ;
END_TRY;
```

### 2.6 算術運算

```c
/* 有號（二補數）*/
extern T MP_add(T z, T x, T y);
extern T MP_sub(T z, T x, T y);
extern T MP_mul(T z, T x, T y);
extern T MP_div(T z, T x, T y);
extern T MP_mod(T z, T x, T y);
extern T MP_neg(T z, T x);

/* 無號（名稱以 u 結尾）*/
extern T MP_addu(T z, T x, T y);
extern T MP_subu(T z, T x, T y);
extern T MP_mulu(T z, T x, T y);
extern T MP_divu(T z, T x, T y);
extern T MP_modu(T z, T x, T y);

/* 雙倍長度乘積：不會溢位 */
extern T MP_mul2u(T z, T x, T y);
extern T MP_mul2 (T z, T x, T y);
```

- **有號和無號運算唯一的差別是溢位的語意。**
- x、y 異號時，`MP_div` 和 `MP_mod` **向負無限大截斷**，所以 x mod y **永遠是正數**（和 Arith、AP 一致）。
- **溢位規則**：

| 函式 | 何時丟出 `MP_Overflow` |
|---|---|
| 除了 `MP_divu`、`MP_modu` 以外的所有函式 | 結果放不下 |
| `MP_subu` | x < y |
| `MP_sub` | x、y 異號，而且結果的符號和 x 不同 |

- **除數是 0** 時，`MP_div`、`MP_divu`、`MP_mod`、`MP_modu` 丟出 **`MP_Dividebyzero`**。
- **`MP_mul2u`/`MP_mul2`**：z 有 **2n** 位元，**結果不可能溢位**。z 太小是 unchecked error；而且 z 要放 2n 位元，**不能用 `MP_new` 配置**。

### 2.7 便利函式

```c
extern T MP_addi (T z, T x, long y);
extern T MP_subi (T z, T x, long y);
extern T MP_muli (T z, T x, long y);
extern T MP_divi (T z, T x, long y);
extern T MP_addui(T z, T x, unsigned long y);
extern T MP_subui(T z, T x, unsigned long y);
extern T MP_mului(T z, T x, unsigned long y);
extern T MP_divui(T z, T x, unsigned long y);
extern long          MP_modi (T x, long y);
extern unsigned long MP_modui(T x, unsigned long y);
```

- 等同於把 y 先轉成 MP_T 再呼叫一般版本。
- **⭐ 有兩種溢位的可能**：**y 本身太大**，或**運算結果溢位**。y 太大時，**還是會先完成運算並設定 z，然後才丟出 `MP_Overflow`**。
- **這些便利函式不配置記憶體。**

### 2.8 比較

```c
extern int MP_cmp  (T x, T y);
extern int MP_cmpi (T x, long y);
extern int MP_cmpu (T x, T y);
extern int MP_cmpui(T x, unsigned long y);
```

`MP_cmpi` 和 `MP_cmpui` **不要求 y 放得進 MP_T**，它們只是單純比較 x 和 y 的值。

### 2.9 位元運算

```c
extern T MP_and (T z, T x, T y);
extern T MP_or  (T z, T x, T y);
extern T MP_xor (T z, T x, T y);
extern T MP_not (T z, T x);                    /* 一補數 */
extern T MP_andi(T z, T x, unsigned long y);
extern T MP_ori (T z, T x, unsigned long y);
extern T MP_xori(T z, T x, unsigned long y);
```

- 把輸入當成 **n 個位元的字串**處理。
- **這些函式從不丟出例外**；便利版本會**忽略** y 太大造成的溢位。

### 2.10 位移

```c
extern T MP_lshift(T z, T x, int s);   /* 邏輯左移，補 0 */
extern T MP_rshift(T z, T x, int s);   /* 邏輯右移，補 0 */
extern T MP_ashift(T z, T x, int s);   /* 算術右移，補符號位元 */
```

s 是負數是 checked error。

### 2.11 字串轉換

```c
extern T     MP_fromstr(T z, const char *str, int base, char **end);
extern char *MP_tostr  (char *str, int size, int base, T x);
extern void  MP_fmt    (int code, va_list *app, int put(int c, void *cl), void *cl,
                        unsigned char flags[], int width, int precision);
extern void  MP_fmtu   (int code, va_list *app, int put(int c, void *cl), void *cl,
                        unsigned char flags[], int width, int precision);
```

- **`MP_fromstr`**：像 `strtoul`，把字串解譯成**無號**整數；數字太大時丟出 `MP_Overflow`；不是合法數字時回傳 NULL。
- **`MP_tostr`**：str 是 NULL 時自動配置（client 負責釋放），可能丟出 `Mem_Failed`。
- **`MP_fmt`/`MP_fmtu`**：Fmt 的轉換函式，**消耗兩個參數：一個 MP_T 和一個 base**。`MP_fmt` 依 `%d` 的慣例格式化有號值，`MP_fmtu` 依 `%u` 的慣例格式化無號值。

---

## 3. 範例：另一個計算機 `mpcalc`（19.2）

### 3.1 功能

和第 18 章的 `calc` 類似，但對 **n 位元整數**做**有號和無號**運算。

| 運算子 | 功能 | 運算子 | 功能 |
|---|---|---|---|
| `~` | 取負 | `&` | AND |
| `+` | 加 | `\|` | OR |
| `-` | 減 | `^` | XOR |
| `*` | 乘 | `<` | 左移 |
| `/` | 除 | `>` | 右移 |
| `%` | 取餘數 | `!` | NOT |
| `i` | 設定**輸入**底數 | `o` | 設定**輸出**底數 |
| `k` | 設定**精度**（位元數） | `c` | 清空堆疊 |
| `d` | 複製頂端 | `p` | 印出頂端 |
| `f` | 印出全部 | `q` | 離開 |

- **`nk`**（n ≥ 2）設定整數的位元數，預設是 32；執行 `k` 時**堆疊必須是空的**。
- **`i`、`o`** 設定輸入和輸出的底數，預設都是 10。
- **⭐ 輸出底數是 2、8 或 16 時**，`+ - * / %` 做**無號**運算，`p`、`f` 印出無號值；**其他底數**則做**有號**運算。
- `~` 一律做有號運算；`& | ^ ! < >` 一律把運算元當成無號數。
- 溢位時宣告溢位，結果是值最低的 n 個位元；除以 0 時結果是 0。

### 3.2 ⭐ 改用 Seq 當堆疊

```c
#include "seq.h"
Seq_T sp;
sp = Seq_new(0);

MP_T pop(void) {
    if (Seq_length(sp) > 0)
        return Seq_remhi(sp);
    else {
        Fmt_fprint(stderr, "?stack underflow\n");
        return MP_new(0);
    }
}
```

> 回想第 18 章，calc 用 Stack 時，印出所有值要用暫時的堆疊倒來倒去。**改用 Seq_T 之後**：
> ```c
> case 'f': {
>     int n = Seq_length(sp);
>     while (--n >= 0)
>         Fmt_print(f->fmt, Seq_get(sp, n), obase);
>     break;
> }
> ```
> **用 Seq_T 表示堆疊時，印出所有值很容易。** 作者用這兩個範例的對比，示範**選對 ADT 有多重要**。

### 3.3 ⭐ 集中處理例外的主迴圈

```c
int main(int argc, char *argv[]) {
    int c;
    /* initialization */
    while ((c = getchar()) != EOF) {
        volatile MP_T x = NULL, y = NULL, z = NULL;   /* 注意 volatile！ */
        TRY
            switch (c) {
            /* cases */
            }
        EXCEPT(MP_Overflow)
            Fmt_fprint(stderr, "?overflow\n");
        EXCEPT(MP_Dividebyzero)
            Fmt_fprint(stderr, "?divide by 0\n");
        END_TRY;
        if (z)
            Seq_addhi(sp, z);      /* 結果推回堆疊 */
        FREE(x);                   /* 運算元釋放 */
        FREE(y);
    }
    /* clean up and exit */
}
```

**設計重點**：
- 每個運算子用 **x、y 存運算元**、**z 存結果**。
- switch 結束後：z 不是 NULL 就推入堆疊；x、y 不是 NULL 就釋放。
- **TRY-EXCEPT 只需要寫一次**，不用包住每個運算子。
- **因為 MP 會先設定結果再丟出例外**，溢位時 z 仍然有截斷後的值，會照常被推入堆疊。
- x、y、z 宣告成 **`volatile`**，因為它們在 TRY 裡被修改，之後又要使用（第 4 章的陷阱）。

### 3.4 用函式指標表切換有號和無號

```c
int ibase = 10;
int obase = 10;
struct {
    const char *fmt;
    MP_T (*add)(MP_T, MP_T, MP_T);
    MP_T (*sub)(MP_T, MP_T, MP_T);
    MP_T (*mul)(MP_T, MP_T, MP_T);
    MP_T (*div)(MP_T, MP_T, MP_T);
    MP_T (*mod)(MP_T, MP_T, MP_T);
} s = { "%D\n", MP_add,  MP_sub,  MP_mul,  MP_div,  MP_mod  },
  u = { "%U\n", MP_addu, MP_subu, MP_mulu, MP_divu, MP_modu },
 *f = &s;

/* 運算子 */
case '+': y = pop(); x = pop(); z = MP_new(0); (*f->add)(z, x, y); break;
case '&': y = pop(); x = pop(); z = MP_new(0); MP_and(z, x, y);    break;
case '~': z = pop(); MP_neg(z, z); break;     /* 原地運算：MP 允許 z == x */

/* 切換底數時也切換 f */
case 'i': case 'o': {
    long n;
    x = pop();
    n = MP_toint(x);
    if (n < 2 || n > 36)
        Fmt_fprint(stderr, "?%d is an illegal base\n", n);
    else if (c == 'i')
        ibase = n;
    else
        obase = n;
    if (obase == 2 || obase == 8 || obase == 16)
        f = &u;
    else
        f = &s;
    break;
}

/* 印出 */
Fmt_register('D', MP_fmt);
Fmt_register('U', MP_fmtu);
case 'p':
    Fmt_print(f->fmt, z = pop(), obase);   /* 傳 MP_T 和 base 兩個參數 */
    break;
```

**巧妙之處**：
- 用一個**函式指標結構**切換整組有號或無號運算，switch 裡完全不用 if-else。
- `MP_neg(z, z)` 這種**原地運算**之所以可行，正是 `MP_set` 預先配置暫存空間的好處。
- 判斷字元是不是合法數字的技巧：

```c
strchr(&"zyxwvutsrqponmlkjihgfedcba9876543210"[36-ibase], tolower(c))
```

把字串**倒過來排**，從第 `36-ibase` 個字元開始，剛好就是這個底數所有合法數字組成的字串。

### 3.5 其他運算子

```c
case 'k': {                          /* 設定精度 */
    long n;
    x = pop();
    n = MP_toint(x);
    if (n < 2 || n > INT_MAX)
        Fmt_fprint(stderr, "?%d is an illegal precision\n", n);
    else if (Seq_length(sp) > 0)
        Fmt_fprint(stderr, "?nonempty stack\n");  /* 舊的值大小不對了 */
    else
        MP_set(n);
    break;
}

case 'd': {                          /* 複製 */
    MP_T x = pop();
    z = MP_new(0);
    Seq_addhi(sp, x);
    MP_addui(z, x, 0);               /* 加 0 來複製 */
    break;
}
```

---

## 4. 實作（19.3 Implementation）

### 4.1 ⭐ 四個全域值

n 位元的數字用 nbytes = (n−1)/8 + 1 個位元組表示，最低位元組在前：

```
 byte (n−1)/8     ...      byte 1     byte 0
 [s·······]                [········] [········]
  ↑ bit n−1（符號位元），在最高位元組的第 shift 位
```

```c
static int nbits  = 32;
static int nbytes = (32-1)/8 + 1;      /* 需要的位元組數 */
static int shift  = (32-1)%8;          /* 最高位元組要右移幾位才能取出符號位元 */
static unsigned char msb = 0xFF;       /* shift+1 個 1：最高位元組的有效位元遮罩 */

#define sign(x) ((x)[nbytes-1]>>shift)
#define ones(n) (~(~0UL<<(((n)-1)%8+1)))
```

| 變數 | n = 32 | n = 13 |
|---|---|---|
| nbytes | 4 | 2 |
| shift | 7 | 4 |
| msb | 0xFF | 0x1F |

- **`msb`** 是最高位元組中**有效位元**的遮罩，用來**偵測溢位**和**清除多餘的位元**。
- **`ones(n)`**：`~0` 左移 `(n−1)%8+1` 位得到「一串 1 加上幾個 0」，取補數就得到最低的 `(n−1)%8+1` 個位元是 1。寫成巨集，是因為它也會用在 `MP_set` 以外的 n 值。

```c
int MP_set(int n) {
    int prev = nbits;
    assert(n > 1);
    nbits  = n;
    nbytes = (n-1)/8 + 1;
    shift  = (n-1)%8;
    msb    = ones(n);
    /* 配置暫存空間（見下）*/
    return prev;
}
```

### 4.2 ⭐ 預先配置的暫存空間

```c
static unsigned char temp[16 + 16 + 16 + 2*16+2];
static T tmp[] = {temp, temp+1*16, temp+2*16, temp+3*16};

/* MP_set 中 */
if (tmp[0] != temp)
    FREE(tmp[0]);                          /* 釋放之前配置的 */
if (nbytes <= 16)
    tmp[0] = temp;                         /* ≤ 128 位元：用靜態陣列 */
else
    tmp[0] = ALLOC(3*nbytes + 2*nbytes + 2);
tmp[1] = tmp[0] + 1*nbytes;
tmp[2] = tmp[0] + 2*nbytes;
tmp[3] = tmp[0] + 3*nbytes;                /* 2·nbytes+2：給乘法和除法用 */
```

- **三個 nbytes 的暫存，加上一個 2·nbytes+2 的暫存**（給 `XP_div` 的 tmp 和雙倍長度的乘積）。
- **n ≤ 128 時用靜態陣列 `temp`**，完全不配置。
- `temp` 是必要的，因為 MP 必須**像已經執行過 `MP_set(32)` 一樣**地初始化，不能要求 client 先呼叫 `MP_set`。
- **慣例**：`tmp[0]`、`tmp[1]` 用來存放取負或複製後的 x、y；`tmp[2]` 存放丟棄的餘數或商；`tmp[3]` 是 XP_div 的暫存或雙倍長度的乘積。

### 4.3 基本策略：XP 計算 + 溢位檢查

> **大多數 MP 函式都呼叫 XP 函式對 nbytes 位元組的數字做實際的運算，然後檢查結果是否超過 nbits 位元。**

```c
const Except_T MP_Dividebyzero = { "Division by zero" };
const Except_T MP_Overflow     = { "Overflow" };

T MP_new(unsigned long u) {
    return MP_fromintu(ALLOC(nbytes), u);
}

T MP_fromintu(T z, unsigned long u) {
    unsigned long carry;
    assert(z);
    /* set z to u */
    carry = XP_fromint(nbytes, z, u);     /* 放不進 nbytes 個位元組的部分 */
    carry |= z[nbytes-1]&~msb;            /* 最高位元組中超過 nbits 的部分 */
    z[nbytes-1] &= msb;                   /* 丟掉多餘的位元 */
    /* test for unsigned overflow */
    if (carry)
        RAISE(MP_Overflow);               /* ⭐ 先設定 z，再丟出例外 */
    return z;
}
```

**無號溢位偵測的慣用寫法（全章反覆出現）：**
1. XP 回傳的進位 → 放不進 nbytes。
2. `z[nbytes-1] & ~msb` → 雖然放得進 nbytes，但**超過 nbits**。
3. `z[nbytes-1] &= msb` → **丟掉多餘的位元**。
4. 有任何一種溢位就丟出例外，**但 z 已經設定好了**。

### 4.4 有號整數的設定

```c
T MP_fromint(T z, long v) {
    assert(z);
    /* set z to v */
    if (v == LONG_MIN) {
        XP_fromint(nbytes, z, LONG_MAX + 1UL);
        XP_neg(nbytes, z, z, 1);           /* 取二補數 */
    } else if (v < 0) {
        XP_fromint(nbytes, z, -v);
        XP_neg(nbytes, z, z, 1);
    } else
        XP_fromint(nbytes, z, v);
    z[nbytes-1] &= msb;
    if (/* v is too big */
        nbits < 8*(int)sizeof (v) &&
        (v < -(1L<<(nbits-1)) || v >= (1L<<(nbits-1))))
        RAISE(MP_Overflow);
    return z;
}
```

- 負數：先設成**絕對值**，再用 `XP_neg(..., 1)` 取**二補數**。
- 又是 `LONG_MIN` 的特別處理。
- `1L<<(nbits-1)` 算出 nbits 位元有號整數的範圍邊界。

### 4.5 大小轉換：窄化與加寬

```c
T MP_cvt(int m, T z, T x) {
    int fill, i, mbytes = (m - 1)/8 + 1;
    assert(m > 1);
    assert(x); assert(z);
    fill = sign(x) ? 0xFF : 0;
    if (m < nbits) {
        /* narrow signed x：多出來的位元必須全部等於符號位元 */
        int carry = (x[mbytes-1]^fill)&~ones(m);
        for (i = mbytes; i < nbytes; i++)
            carry |= x[i]^fill;
        memcpy(z, x, mbytes);
        z[mbytes-1] &= ones(m);
        if (carry)
            RAISE(MP_Overflow);
    } else {
        /* widen signed x：用符號位元延伸 */
        memcpy(z, x, nbytes);
        z[nbytes-1] |= fill&~msb;
        for (i = nbytes; i < mbytes; i++)
            z[i] = fill;
        z[mbytes-1] &= ones(m);
    }
    return z;
}
```

**⭐ 有號窄化的溢位判斷**：x 放得進 m 位元 ⇔ **第 m 到 nbits−1 位全部是 0 或全部是 1**，也就是全部等於 m 位元的符號位元。`fill` 是 0xFF（負數）或 0（正數），所以 **`x[i] ^ fill` 應該是 0**。

```c
long MP_toint(T x) {
    unsigned char d[sizeof (unsigned long)];   /* 在堆疊上的暫存 */
    assert(x);
    MP_cvt(8*sizeof d, d, x);                  /* 放不下就丟出例外 */
    return XP_toint(sizeof d, d);
}
```

`MP_cvtu` 的邏輯類似但比較簡單：窄化時只要檢查多出來的位元是否全部是 0；加寬時補 0。

### 4.6 無號算術

```c
T MP_addu(T z, T x, T y) {
    int carry;
    assert(x); assert(y); assert(z);
    carry = XP_add(nbytes, z, x, y, 0);
    carry |= z[nbytes-1]&~msb;
    z[nbytes-1] &= msb;
    if (carry)
        RAISE(MP_Overflow);
    return z;
}

T MP_subu(T z, T x, T y) {
    int borrow;
    assert(x); assert(y); assert(z);
    borrow = XP_sub(nbytes, z, x, y, 0);
    borrow |= z[nbytes-1]&~msb;
    z[nbytes-1] &= msb;
    if (borrow)
        RAISE(MP_Overflow);          /* x < y */
    return z;
}
```

**乘法：先算進暫存空間**

```c
T MP_mul2u(T z, T x, T y) {           /* 雙倍長度：不會溢位 */
    assert(x); assert(y); assert(z);
    memset(tmp[3], '\0', 2*nbytes);
    XP_mul(tmp[3], nbytes, x, nbytes, y);
    memcpy(z, tmp[3], (2*nbits - 1)/8 + 1);
    return z;
}

T MP_mulu(T z, T x, T y) {
    assert(x); assert(y); assert(z);
    memset(tmp[3], '\0', 2*nbytes);
    XP_mul(tmp[3], nbytes, x, nbytes, y);
    memcpy(z, tmp[3], nbytes);
    z[nbytes-1] &= msb;
    {   /* test for unsigned multiplication overflow */
        int i;
        if (tmp[3][nbytes-1]&~msb)
            RAISE(MP_Overflow);
        for (i = 0; i < nbytes; i++)
            if (tmp[3][i+nbytes] != 0)       /* 高 nbits 位元有任何 1 就是溢位 */
                RAISE(MP_Overflow);
    }
    return z;
}
```

> **為什麼先算進 `tmp[3]` 再複製？** `XP_mul` 不允許 z 是 x 或 y。先算進暫存空間再複製，**x 或 y 就可以當成 z 使用**。在 `MP_set` 配置暫存空間，**不但把配置集中在一處，也消除了對 x、y 的限制。**

**除法：複製 y 避開 XP_div 的限制**

```c
T MP_divu(T z, T x, T y) {
    assert(x); assert(y); assert(z);
    {   /* copy y to a temporary */
        memcpy(tmp[1], y, nbytes);
        y = tmp[1];
    }
    if (!XP_div(nbytes, z, x, nbytes, y, tmp[2], tmp[3]))   /* tmp[2] 存丟棄的餘數 */
        RAISE(MP_Dividebyzero);
    return z;
}
```

`MP_modu` 類似，但用 `tmp[2]` 存丟棄的商。

### 4.7 ⭐ 有號算術：二補數的好處

> AP 的**符號加大小**表示法，迫使 `AP_add` 依 x、y 的符號分情況處理。
> **二補數表示法的性質讓 `MP_add` 不需要分情況，不管 x、y 的符號，直接呼叫 `XP_add` 就好。** 有號加法和無號加法幾乎一模一樣，**唯一重要的差別是溢位檢查**。

```c
T MP_add(T z, T x, T y) {
    int sx, sy;
    assert(x); assert(y); assert(z);
    sx = sign(x);
    sy = sign(y);
    XP_add(nbytes, z, x, y, 0);        /* 不管符號，直接加 */
    z[nbytes-1] &= msb;
    if (sx == sy && sy != sign(z))     /* 同號相加，結果卻變號 → 溢位 */
        RAISE(MP_Overflow);
    return z;
}

T MP_sub(T z, T x, T y) {
    int sx, sy;
    assert(x); assert(y); assert(z);
    sx = sign(x);
    sy = sign(y);
    XP_sub(nbytes, z, x, y, 0);
    z[nbytes-1] &= msb;
    if (sx != sy && sy == sign(z))     /* 異號相減，結果和 y 同號 → 溢位 */
        RAISE(MP_Overflow);
    return z;
}
```

**二補數溢位判斷規則**：

| 運算 | 溢位條件 | 原因 |
|---|---|---|
| x + y | **x、y 同號**，而且結果符號**不同** | 正 + 正 不會變負，負 + 負 不會變正 |
| x − y | **x、y 異號**，而且結果符號**和 y 相同** | 正 − 負 應該是正，負 − 正 應該是負 |
| −x | **x 是負數**，而且結果**仍然是負數** | 只有最小的負數取負後還是自己 |

```c
T MP_neg(T z, T x) {
    int sx;
    assert(x); assert(z);
    sx = sign(x);
    XP_neg(nbytes, z, x, 1);
    z[nbytes-1] &= msb;                /* x 是正數時，取負後多出來的位元會是 1 */
    if (sx && sx == sign(z))
        RAISE(MP_Overflow);
    return z;
}
```

### 4.8 有號乘法：取絕對值後用無號乘法

> 實作有號乘法最簡單的方法：**把負的運算元取負**，做**無號乘法**，運算元**異號**時再把結果取負。

```c
/* tmp[3] ← x·y */
sx = sign(x);
sy = sign(y);
if (sx) {                              /* if x < 0, negate x */
    XP_neg(nbytes, tmp[0], x, 1);
    x = tmp[0];
    x[nbytes-1] &= msb;
}
if (sy) {                              /* if y < 0, negate y */
    XP_neg(nbytes, tmp[1], y, 1);
    y = tmp[1];
    y[nbytes-1] &= msb;
}
memset(tmp[3], '\0', 2*nbytes);
XP_mul(tmp[3], nbytes, x, nbytes, y);

T MP_mul(T z, T x, T y) {
    int sx, sy;
    assert(x); assert(y); assert(z);
    /* tmp[3] ← x·y */
    if (sx != sy)
        XP_neg(nbytes, z, tmp[3], 1);
    else
        memcpy(z, tmp[3], nbytes);
    z[nbytes-1] &= msb;
    /* test for unsigned multiplication overflow */
    if (sx == sy && sign(z))           /* 同號相乘結果卻是負數 → 溢位 */
        RAISE(MP_Overflow);
    return z;
}
```

### 4.9 有號除法

```c
T MP_div(T z, T x, T y) {
    int sx, sy;
    assert(x); assert(y); assert(z);
    sx = sign(x);
    sy = sign(y);
    /* if x < 0, negate x */
    /* if y < 0, negate y */ else /* copy y to a temporary */;
    if (!XP_div(nbytes, z, x, nbytes, y, tmp[2], tmp[3]))
        RAISE(MP_Dividebyzero);
    if (sx != sy) {
        /* adjust the quotient：取負，有餘數時再減 1（向負無限大）*/
        XP_neg(nbytes, z, z, 1);
        if (!iszero(tmp[2]))
            XP_diff(nbytes, z, z, 1);
        z[nbytes-1] &= msb;
    } else if (sx && sign(z))
        RAISE(MP_Overflow);            /* 最小負數 ÷ (−1) */
    return z;
}

#define iszero(x) (XP_length(nbytes,(x))==1 && (x)[0]==0)
```

- **同號**時商和餘數都是非負數，和無號除法一樣。
- **唯一可能溢位的情況**：被除數是**最小的 n 位元負數**、除數是 **−1**，結果應該是正數卻放不下。
- **異號**時的調整和 `AP_div`、`AP_mod` 相同：商取負，餘數不是 0 時商再減 1；餘數不是 0 時改成 y − 餘數。

```c
T MP_mod(T z, T x, T y) {
    /* ... 同樣先取絕對值 ... */
    if (!XP_div(nbytes, tmp[2], x, nbytes, y, z, tmp[3]))
        RAISE(MP_Dividebyzero);
    if (sx != sy) {
        if (!iszero(z))
            XP_sub(nbytes, z, y, z, 0);   /* 餘數 = |y| − 餘數 */
    } else if (sx && sign(tmp[2]))
        RAISE(MP_Overflow);
    return z;
}
```

### 4.10 便利函式：單一位數的捷徑

```c
#define BASE (1<<8)

T MP_addui(T z, T x, unsigned long y) {
    assert(x); assert(z);
    if (y < BASE) {                        /* y 只有一位數：用 XP_sum */
        int carry = XP_sum(nbytes, z, x, y);
        carry |= z[nbytes-1]&~msb;
        z[nbytes-1] &= msb;
        if (carry)
            RAISE(MP_Overflow);
    } else if (applyu(MP_addu, z, x, y))   /* 否則轉成 MP_T 再呼叫一般版本 */
        RAISE(MP_Overflow);
    return z;
}

static int applyu(T op(T, T, T), T z, T x, unsigned long u) {
    unsigned long carry;
    {   T z = tmp[2];                      /* 把 u 轉進 tmp[2] */
        carry = XP_fromint(nbytes, z, u);
        carry |= z[nbytes-1]&~msb;
        z[nbytes-1] &= msb;
    }
    op(z, x, tmp[2]);                      /* 先完成運算 */
    return carry != 0;                     /* 再回報 y 是否太大 */
}
```

- y 小於 256（**一個底數 2⁸ 的位數**）時，直接用 XP 的**單一位數函式**，最快。
- 否則用 `applyu`：把 y 轉進 `tmp[2]`、**記住轉換時是否溢位**、**先**呼叫一般函式完成運算，**最後**才回報 y 太大。這就實現了「先算出結果再丟出例外」的承諾。
- `op` 本身也可能丟出例外，但同樣會先設定好 z。

### 4.11 位移

```c
#define shft(fill, op) \
    assert(x); assert(z); assert(s >= 0); \
    if (s >= nbits) memset(z, fill, nbytes); \
    else op(nbytes, z, nbytes, x, s, fill); \
    z[nbytes-1] &= msb; \
    return z

T MP_lshift(T z, T x, int s) { shft(0, XP_lshift); }
T MP_rshift(T z, T x, int s) { shft(0, XP_rshift); }
T MP_ashift(T z, T x, int s) { shft(sign(x), XP_rshift); }   /* 填符號位元 */
```

- 用巨集統一三種位移；s ≥ nbits 時結果是全 0 或全 1。
- **算術右移**只是把**符號位元**當成 fill 傳給 `XP_rshift`。

### 4.12 字串轉換

```c
T MP_fromstr(T z, const char *str, int base, char **end) {
    int carry;
    assert(z);
    memset(z, '\0', nbytes);               /* XP_fromstr 不會清除，所以先清成 0 */
    carry = XP_fromstr(nbytes, z, str, base, end);
    carry |= z[nbytes-1]&~msb;
    z[nbytes-1] &= msb;
    if (carry)
        RAISE(MP_Overflow);
    return z;
}

char *MP_tostr(char *str, int size, int base, T x) {
    assert(x);
    assert(base >= 2 && base <= 36);
    assert(str == NULL || size > 1);
    if (str == NULL) {
        {   /* size ← 表示 x 需要的字元數（和 AP_tostr 同樣的技巧）*/
            int k;
            for (k = 5; (1<<k) > base; k--)
                ;
            size = nbits/k + 1 + 1;
        }
        str = ALLOC(size);
    }
    memcpy(tmp[1], x, nbytes);             /* 複製，因為 XP_tostr 會把輸入清成 0 */
    XP_tostr(str, size, base, nbytes, tmp[1]);
    return str;
}
```

**`MP_fmt`**：`MP_tostr` 只處理**無號**值，所以 `MP_fmt` 自己配置緩衝區，**負數先取絕對值，再在前面加上負號**，最後交給 `Fmt_putd` 處理對齊。

---

## 5. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **⭐ 全域精度設定** | `MP_set` 一次設定，參數變少；**暫存空間預先配置**，所以來源和目的參數沒有限制 |
| **先算出結果，再丟出例外** | 同時支援「偵測溢位」和「模擬截斷算術」 |
| **⭐ 二補數 vs. 符號加大小** | 加減法不用分情況；溢位只要看符號位元 |
| **統一的溢位偵測慣用寫法** | `carry \|= z[top] & ~msb; z[top] &= msb;` |
| **靜態暫存空間** | ≤ 128 位元時完全不配置 |
| **單一位數的捷徑** | 便利函式在 y < 256 時用 XP 的單一位數函式 |
| **再次分層** | MP = XP + 位元粒度 + 二補數 + 溢位檢查 + 解除別名限制 |
| **函式指標表** | mpcalc 用一個結構切換有號和無號運算 |
| **選對 ADT** | mpcalc 改用 Seq 後，印出整個堆疊變得很簡單 |

### 三個算術介面的總結

```
            ┌─────────────────────────────┐
  應用 ──→  │   AP（任意精度、有號）        │  符號 + 大小，自動配置
            ├─────────────────────────────┤
  應用 ──→  │   MP（n 位元、有號和無號）     │  二補數，溢位例外
            ├─────────────────────────────┤
            │   XP（無號、n 位數、不檢查）    │  直式算術，不配置
            └─────────────────────────────┘
```

---

## 6. 延伸閱讀重點

- 多精度算術常用在**編譯器**，有時候是**必須**的。例如 **Clinger (1990)** 證明了把浮點常數轉換成對應的 IEEE 表示法時，有時需要多精度算術才能達到最佳的精確度。
- **Schneier (1996)**：完整的密碼學綜述，很實用，包含部分演算法的 C 實作和大量參考文獻。
- **Press et al. (1992)** 第 20.6 節：用**快速傅立葉轉換（FFT）**實作乘法，時間是 **O(n lg n lg lg n)**；也說明了用「求倒數 1/y 再乘以 x」來實作除法，這需要帶小數部分的多精度數字。

---

## 7. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 19.1 | nbits 是 8 的倍數時，MP 做了很多不必要的工作（遮罩），修改實作避免這些工作並量測 | 特例最佳化的成本效益 |
| 19.2 | 很多應用的 nbits 選定後就不會變；寫一個**程式產生器**，針對特定 nbits 產生 `MP_nbits` 介面和實作 | 用程式碼產生取代執行期的參數 |
| 19.3 | 設計**定點**多精度數字（有整數和小數部分）的介面 | 一定要寫清楚捨入規則 |
| 19.4 | 設計可以指定**指數和尾數位元數**的浮點數介面 | 先讀 Goldberg (1991) |
| 19.5 | 用 `typedef unsigned char T[];` 或 `typedef unsigned char T;` 重新定義 XP_T、MP_T，讓 `const` 能正確運作，重新實作 XP、AP、MP、calc、mpcalc 並比較可讀性 | 陣列型別的參數會退化成指標；但陣列型別不能當回傳型別，也不能宣告變數 |

---

## 8. 本章重點整理

1. **MP = n 位元的無號和二補數有號整數**，表示方式公開（`unsigned char *`），長度以位元為單位。
2. **`MP_set(n)` 全域設定精度**，預設 32；同時預先配置暫存空間，所以**任何 MP_T 都可以同時當來源和目的**，而且幾乎不配置記憶體。
3. **先算出結果再丟出例外**：溢位時結果是截斷後的值，client 可以用 TRY-EXCEPT 忽略溢位。
4. **49 個函式**：轉換（new/fromint/toint/cvt）、有號和無號算術、雙倍長度乘法、便利函式、比較、位元運算、位移（邏輯和算術）、字串和 Fmt。
5. **實作核心**：XP 計算，加上用 `msb` 遮罩偵測並清除超過 nbits 的位元。
6. **二補數的好處**：有號加減法直接呼叫 XP；溢位只要比較運算元和結果的符號位元。有號乘除法則先取絕對值、做無號運算、再調整符號。
7. **mpcalc 範例**：Seq 當堆疊、TRY-EXCEPT 集中處理、`volatile` 變數、函式指標結構切換有號和無號運算。

> **一句話**：MP 用「全域精度 + 預先配置的暫存空間 + 二補數」，提供一組沒有參數別名限制、會偵測溢位但也能模擬截斷的固定位元數整數算術，完成了 XP、AP、MP 三層大數介面的設計。
