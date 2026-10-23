# 05. 指標

> 程式練習：`CL03 用指標操作陣列`（之後每一題都會用到指標）
>
> 先備知識：第 03 課「傳值」、第 04 課「陣列」。

**這一課分成七個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 位址與指標 | 記憶體與位址、`&` 取位址、`*` 解參考、宣告的陷阱 |
| 第二部分 | 指標當參數與回傳值 | 讓函式修改呼叫者的變數、輸出參數、不能回傳區域變數的位址 |
| 第三部分 | 指標算術 | `p + 1` 移動幾個 byte、兩個指標相減、比較、走訪 |
| 第四部分 | 指標與陣列 | 陣列名稱會變成指標、`a[i]` 就是 `*(a + i)`、兩者的差別、`*p++` |
| 第五部分 | const 與指標 | `const int *` vs `int *const`、怎麼讀複雜的宣告 |
| 第六部分 | 指標的指標與 void * | `int **`、修改呼叫者的指標、通用指標 `void *` |
| 第七部分 | NULL 與指標錯誤大全 | 空指標、野指標、懸置指標，每一種的症狀與預防 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際用 `gcc -std=c11` 編譯執行過的結果（64 位元 Linux）。位址每次執行都不一樣，範例裡用「`0x7ffd...`」表示。標 🔍 的是深入內容。

---

# 第一部分：位址與指標

## 1.1 記憶體與位址

**是什麼**：記憶體可以想成一長排 **編了號的格子**，每一格 1 個 byte，號碼就是 **位址 (address)**。每個變數佔用其中連續的幾格。

```
位址：   1000  1001  1002  1003  1004  1005  1006  1007
       ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
       │      int x = 42       │      int y = 7        │
       └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

`x` 佔 4 個 byte（位址 1000 ~ 1003），我們說「`x` 的位址是 1000」（第一個 byte 的位址）。

**比喻**：記憶體是一條街，每一格是一間房子，位址就是門牌號碼。變數是住在裡面的東西。

## 1.2 & 取位址、指標變數

**是什麼**：
- `&x`：取得變數 `x` 的 **位址**。
- **指標 (pointer)**：一種變數，裡面存的是 **位址**。宣告時在名字前加 `*`。

```c
int x = 42;
int *p = &x;                     /* p 是「指向 int 的指標」，存著 x 的位址 */
printf("%p %p\n", (void *)&x, (void *)p);   // 輸出：0x7ffd... 0x7ffd...（兩個一樣）
printf("%zu\n", sizeof p);                  // 輸出：8（64 位元系統，所有指標都是 8 bytes）
```

`%p` 用來印位址，參數要轉成 `void *`。

```
   p                    x
┌──────────┐        ┌──────┐
│ 0x7ffd.. │ ─────▶ │  42  │
└──────────┘        └──────┘
```

**比喻**：`x` 是一間房子，`p` 是寫著那間房子門牌號碼的紙條。

## 1.3 * 解參考：透過指標存取

**是什麼**：`*p` 的意思是「**p 指向的那個變數**」。可以讀，也可以寫。

```c
int x = 42;
int *p = &x;
printf("%d\n", *p);              /* 讀：p 指向的值 → 輸出：42 */
*p = 100;                        /* 寫：把 p 指向的變數改成 100 */
printf("%d\n", x);               // 輸出：100（x 被改了！）
(*p)++;                          /* 透過指標遞增 */
printf("%d\n", x);               // 輸出：101
```

**`*` 有三種意思，看位置分辨**：

| 寫法 | 意思 |
|---|---|
| `int *p;` | 宣告：`p` 是指標 |
| `*p` | 運算式：解參考，取得 `p` 指向的東西 |
| `a * b` | 乘法 |

**指標可以換指向別的變數**：

```c
int a = 1, b = 2;
int *q = &a;
printf("%d ", *q);               /* 1 */
q = &b;                          /* q 改指向 b（注意：沒有 *，改的是 q 本身） */
printf("%d\n", *q);              // 輸出：1 2
```

| 寫法 | 改到什麼 |
|---|---|
| `q = &b;` | 改 **指標本身**（指向別的地方） |
| `*q = 5;` | 改 **指向的東西**（透過指標修改變數） |

## 1.4 指標的型別很重要

`int *` 只能指向 `int`，`double *` 指向 `double`。型別決定了：
1. 解參考時要讀幾個 byte、怎麼解讀它們。
2. 指標算術一次移動幾個 byte（第三部分）。

```c
double d = 3.5;
// int *bad = &d;                // ⚠️ warning: initialization of 'int *' from incompatible pointer type 'double *'
double *pd = &d;                 /* ✅ */
```

## 1.5 ⚠️ 宣告的陷阱：* 跟著變數名稱

```c
int *p1, p2;                     /* p1 是 int *，p2 是 int！ */
int *p3, *p4;                    /* 兩個都是指標要各寫一個 * */
```

`*` 屬於 **變數名稱**，不屬於型別。所以很多人習慣寫 `int *p`（星號靠變數）而不是 `int* p`，避免誤會。**一行只宣告一個指標** 最安全。

## 1.6 NULL：不指向任何東西

**是什麼**：`NULL`（定義在 `<stddef.h>`、`<stdio.h>`、`<stdlib.h>`）是一個特殊的指標值，表示「**目前沒有指向任何東西**」。

```c
int *p = NULL;                   /* 還沒有要指向誰：先設成 NULL */
if (p != NULL) printf("%d\n", *p);
else printf("p 是空的\n");        // 輸出：p 是空的
if (!p) printf("也可以這樣寫\n");  /* NULL 是「假」 */
```

**解參考 NULL 是未定義行為**，通常程式立刻當掉（Segmentation fault）。

**規則**：
- 指標宣告時就初始化：指向某個東西，或者 `NULL`。
- 可能是 `NULL` 的指標，使用前先檢查。

---

# 第二部分：指標當參數與回傳值

## 2.1 讓函式修改呼叫者的變數

第 03 課說過：C 只有傳值，函式改參數不會影響呼叫者。**傳指標** 就能解決：

```c
void add_ten(int *n) {           /* 參數是位址 */
    *n += 10;                    /* 透過位址修改呼叫者的變數 */
}
int score = 5;
add_ten(&score);                 /* 傳 score 的位址 */
printf("%d\n", score);           // 輸出：15
```

**其實還是傳值**：傳的值是「位址」，函式拿到位址的複製品，但兩個位址指向 **同一個變數**。

```c
void swap(int *a, int *b) {
    int t = *a;
    *a = *b;
    *b = t;
}
int x = 1, y = 2;
swap(&x, &y);
printf("%d %d\n", x, y);         // 輸出：2 1
```

## 2.2 輸出參數：一次回傳好幾個結果

```c
/* 回傳值表示成功或失敗；結果寫到 *lo、*hi */
int min_max(const int *a, int n, int *lo, int *hi) {
    if (n <= 0) return 0;
    *lo = *hi = a[0];
    for (int i = 1; i < n; i++) {
        if (a[i] < *lo) *lo = a[i];
        if (a[i] > *hi) *hi = a[i];
    }
    return 1;
}
int arr[] = {4, -2, 9, 0};
int lo, hi;
if (min_max(arr, 4, &lo, &hi)) printf("%d %d\n", lo, hi);   // 輸出：-2 9
```

這是 C 標準函式庫常見的設計：`scanf` 回傳成功讀到的個數，結果寫到你給的位址。

## 2.3 ⚠️ 不能回傳區域變數的位址

```c
int *bad(void) {
    int local = 42;
    return &local;               /* ❌ local 在函式結束時就消失了 */
}
```

GCC 會警告：`function returns address of local variable`（而且會故意回傳 `NULL`，讓錯誤更早出現）。

**懸置指標 (dangling pointer)**：指向「已經不存在」的變數的指標。讀寫它是未定義行為。

**要回傳一塊記憶體的位址，可以**：
- 回傳 `static` 區域變數的位址（它一直存在，但每次呼叫共用同一塊）。
- 回傳 `malloc` 配置的記憶體（第 07 課，呼叫者負責 `free`）。
- 回傳呼叫者傳進來的指標（例如 `strcpy` 回傳 `dst`）。

```c
int *counter_addr(void) {
    static int count = 0;        /* static：一直存在 */
    count++;
    return &count;               /* ✅ 合法 */
}
int *pc = counter_addr();
counter_addr();
printf("%d\n", *pc);             // 輸出：2（同一個 count）
```

---

# 第三部分：指標算術

## 3.1 p + 1 移動一個「元素」

**是什麼**：指標加減整數，移動的單位是 **它指向的型別的大小**，不是 1 個 byte。

```c
int a[4] = {10, 20, 30, 40};
int *p = a;                      /* 指向 a[0] */
printf("%d %d %d\n", *p, *(p + 1), *(p + 3));   // 輸出：10 20 40
printf("%td\n", (char *)(p + 1) - (char *)p);   // 實際差了幾個 byte → 輸出：4
```

`p + 1` 的位址 = `p` 的位址 + `sizeof(int)`。這就是為什麼指標一定要有型別。

```
    p       p+1      p+2      p+3
    ↓        ↓        ↓        ↓
  [ 10 ]  [ 20 ]  [ 30 ]  [ 40 ]
  1000    1004    1008    1012
```

## 3.2 指標的遞增、相減、比較

```c
int a[5] = {1, 2, 3, 4, 5};
int *begin = a, *end = a + 5;    /* end 指向「最後一個的下一個」 */

for (int *p = begin; p != end; p++)   /* 用指標走訪 */
    printf("%d ", *p);
printf("\n");                    // 輸出：1 2 3 4 5

int *q = &a[3];
printf("%td\n", q - begin);      /* 兩個指標相減：相差幾個元素（不是 byte）→ 輸出：3 */
printf("%d\n", q < end);         /* 同一個陣列裡的指標可以比較 → 輸出：1 */
```

| 運算 | 意思 | 結果型別 |
|---|---|---|
| `p + n`、`p - n` | 往後 / 往前移 `n` 個元素 | 指標 |
| `p++`、`p--` | 移動一個元素 | 指標 |
| `q - p` | 相差幾個元素 | `ptrdiff_t`（印的時候用 `%td`） |
| `p < q`、`p == q` | 比較位置 | `int` |

**不能做的**：兩個指標相加（`p + q` 沒有意義）、乘除。

## 3.3 [begin, end) 範圍的慣例

`end` 指向「最後一個元素的 **下一個** 位置」：
- 這個位置 **可以算出來、可以比較**，但 **不能解參考**。
- 元素個數 = `end - begin`；空範圍就是 `begin == end`。

`CL03` 的函式全部用這個慣例：`reverse_range(int *begin, int *end)`。C++ 的 STL 也是一樣的設計。

## 3.4 ⚠️ 指標算術只能在同一個陣列裡

```c
int x = 5, y = 6;
int *px = &x;
// *(px + 1) = 0;                 // ❌ 未定義行為：x 不是陣列，px + 1 不知道指向哪裡（不一定是 y）
int a[3];
int *pa = a;
// pa = pa + 10;                  // ❌ 指到陣列外面（連「算出來」都是未定義行為，除了 a + 3 這個結尾位置）
```

---

# 第四部分：指標與陣列

## 4.1 陣列名稱會變成指標（陣列退化）

**是什麼**：在大部分的運算式裡，陣列名稱 `a` 會 **自動轉換成指向第一個元素的指標** `&a[0]`。這叫 **陣列退化 (array decay)**。

```c
int a[3] = {7, 8, 9};
int *p = a;                      /* 等於 int *p = &a[0]; */
printf("%d %d\n", *p, *a);       // 輸出：7 7（*a 就是 a[0]）
printf("%d\n", p == &a[0]);      // 輸出：1
```

這就是為什麼：
- `scanf("%s", buf)` 的 `buf` 不用加 `&`（`buf` 本身就會變成位址）。
- 陣列傳給函式時，傳的是位址（第 04 課）：`void f(int arr[])` 就是 `void f(int *arr)`。

## 4.2 a[i] 就是 *(a + i)

**索引運算子的定義**：`a[i]` 的意思就是 `*(a + i)`。所以指標也可以用 `[]`，陣列也可以用 `*`：

```c
int a[4] = {10, 20, 30, 40};
int *p = a + 1;                  /* 指向 a[1] */
printf("%d %d %d\n", a[2], *(a + 2), p[1]);   // 三種寫法都是 a[2] → 輸出：30 30 30
printf("%d\n", p[-1]);           /* p[-1] = *(p - 1) = a[0] → 輸出：10 */
printf("%d\n", 2[a]);            /* 🔍 2[a] = *(2 + a) = a[2]，合法但千萬別這樣寫 → 輸出：30 */
```

## 4.3 陣列和指標的差別

雖然常常可以互換，但它們 **不是同一個東西**：

| | 陣列 `int a[5]` | 指標 `int *p` |
|---|---|---|
| 是什麼 | 5 個 `int` 的連續空間 | 一個存位址的變數 |
| `sizeof` | 20（整個陣列） | 8（指標本身） |
| 可以重新指定嗎 | ❌ `a = ...` 錯誤 | ✅ `p = ...` |
| `&` 取位址 | `&a` 的型別是 `int (*)[5]`（指向整個陣列） | `&p` 的型別是 `int **` |

```c
int a[5] = {0};
int *p = a;
printf("%zu %zu\n", sizeof a, sizeof p);   // 輸出：20 8
p++;                             /* ✅ 指標可以移動 */
// a++;                          // ❌ error: lvalue required as increment operand
```

## 4.4 🔍 *p++ 是什麼意思？

後置 `++` 的優先順序比 `*` 高，所以 `*p++` 是 `*(p++)`：**先取 `*p` 的值，然後 `p` 往後移**。這是 C 走訪陣列 / 字串最常見的寫法：

```c
int a[3] = {1, 2, 3};
int *p = a;
int x = *p++;                    /* x = a[0]，p 移到 a[1] */
int y = (*p)++;                  /* y = a[1]（2），然後 a[1] 變成 3；p 不動 */
printf("%d %d %d %d\n", x, y, a[1], *p);   // 輸出：1 2 3 3
```

| 寫法 | 意思 |
|---|---|
| `*p++` | 取值，指標往後移 |
| `(*p)++` | 取值，**指向的值** 加 1 |
| `*++p` | 指標先往後移，再取值 |
| `++*p` | 指向的值先加 1，再取值 |

**經典範例：複製字串**（第 06 課 `strcpy` 的實作）

```c
void copy_str(char *dst, const char *src) {
    while ((*dst++ = *src++) != '\0') { }   /* 複製一個字元，兩個指標都往後移，直到複製了 '\0' */
}
char buf[10];
copy_str(buf, "hi!");
printf("%s\n", buf);             // 輸出：hi!
```

## 4.5 用指標寫陣列函式

```c
/* 用 [begin, end) 範圍的版本 */
int sum_range(const int *begin, const int *end) {
    int s = 0;
    while (begin != end) s += *begin++;
    return s;
}
int data[] = {1, 2, 3, 4, 5};
printf("%d %d\n", sum_range(data, data + 5), sum_range(data + 1, data + 3));   // 輸出：15 5
```

用指標範圍的好處：可以很自然地處理「陣列的一部分」（`data + 1` 到 `data + 3`）。

---

# 第五部分：const 與指標

## 5.1 兩個不同的 const

指標牽涉到 **兩個東西**：指標本身、指向的資料。`const` 的位置決定了「哪一個不能改」：

| 宣告 | 能改指向的資料嗎 `*p = ...` | 能改指標本身嗎 `p = ...` |
|---|---|---|
| `int *p` | ✅ | ✅ |
| `const int *p`（= `int const *p`） | ❌ | ✅ |
| `int *const p` | ✅ | ❌ |
| `const int *const p` | ❌ | ❌ |

```c
int a = 1, b = 2;

const int *p1 = &a;              /* 指向「不能改的 int」 */
// *p1 = 10;                     // ❌ error: assignment of read-only location '*p1'
p1 = &b;                         /* ✅ 可以改指向別的地方 */

int *const p2 = &a;              /* 「不能改的指標」 */
*p2 = 10;                        /* ✅ 可以改指向的值 */
// p2 = &b;                      // ❌ error: assignment of read-only variable 'p2'

printf("%d %d\n", a, *p1);       // 輸出：10 2
```

**讀法**：**從變數名稱往左讀**，遇到 `*` 讀成「指向」：
- `const int *p`：p 是一個指標，指向 const int（指向的東西不能改）。
- `int *const p`：p 是一個 const 的指標，指向 int（指標本身不能改）。

## 5.2 const 指標參數：最常用的形式

函式只 **讀取** 指標指向的資料時，參數寫成 `const T *`：

```c
size_t my_strlen(const char *s);           /* 承諾不修改字串 */
int sum(const int *a, int n);              /* 承諾不修改陣列 */
void copy_str(char *dst, const char *src); /* dst 會被修改，src 不會 */
```

看到函式原型就知道哪些參數會被修改。`char *` 可以自動轉成 `const char *`（加上限制是安全的），反過來不行。

---

# 第六部分：指標的指標與 void *

## 6.1 指標的指標

**是什麼**：指標也是變數，也有位址。存「指標的位址」的變數，就是 **指標的指標** `int **`。

```c
int x = 5;
int *p = &x;
int **pp = &p;                   /* pp 指向 p，p 指向 x */
printf("%d %d %d\n", x, *p, **pp);   // 輸出：5 5 5
**pp = 9;                        /* 透過兩層找到 x */
printf("%d\n", x);               // 輸出：9
```

```
   pp               p               x
┌────────┐     ┌────────┐      ┌──────┐
│ &p     │ ──▶ │ &x     │ ──▶  │  9   │
└────────┘     └────────┘      └──────┘
```

## 6.2 為什麼需要：讓函式修改呼叫者的「指標」

和第二部分一樣的道理：函式要修改呼叫者的 `int`，要傳 `int *`；要修改呼叫者的 **`int *`**，就要傳 **`int **`**。

```c
#include <stdlib.h>
/* 錯誤版本：只改到複製品 */
void alloc_bad(int *p, int n) {
    p = malloc(n * sizeof(int));     /* 改的是參數 p（複製品），呼叫者的指標沒變；而且記憶體洩漏 */
}
/* 正確版本：傳指標的位址 */
void alloc_good(int **pp, int n) {
    *pp = malloc(n * sizeof(int));   /* 改的是呼叫者的指標 */
}
int *arr = NULL;
alloc_bad(arr, 10);
printf("%d\n", arr == NULL);         // 輸出：1（還是 NULL）
alloc_good(&arr, 10);
printf("%d\n", arr != NULL);         // 輸出：1
free(arr);
```

**其他常見的 `**`**：
- `int main(int argc, char **argv)`：`argv` 是「字串（`char *`）的陣列」。
- 鏈結串列刪除節點的 `Node **pp` 技巧（`CL05`、第 12 課）。
- 二維動態陣列 `long long **m`（`CL08`）。

## 6.3 void *：通用指標

**是什麼**：`void *` 可以存 **任何型別** 物件的位址，但 **不能直接解參考**（不知道要讀幾個 byte）、也不能做指標算術。要用的時候轉回原本的型別。

```c
int i = 42;
double d = 3.5;
void *vp = &i;                   /* 任何物件指標都能自動轉成 void * */
printf("%d\n", *(int *)vp);      /* 轉回 int * 再解參考 → 輸出：42 */
vp = &d;
printf("%.1f\n", *(double *)vp); // 輸出：3.5
// printf("%d\n", *vp);          // ❌ error: invalid use of void expression
```

**為什麼需要**：C 沒有模板，**通用的函式** 只能用 `void *` 接受任何型別：
- `malloc` 回傳 `void *`（不知道你要配置什麼型別）。
- `memcpy(void *dst, const void *src, size_t n)` 可以複製任何東西。
- `qsort` 能排序任何型別的陣列（第 09 課）。

在 C 裡，`void *` 和其他物件指標之間 **自動轉換**，不用寫轉型：`int *p = malloc(...)`（C++ 要寫 `(int *)`）。

**⚠️ 轉錯型別是未定義行為**：`void *` 不記得原本是什麼型別，轉成錯的型別編譯器不會發現。

---

# 第七部分：NULL 與指標錯誤大全

| 錯誤 | 是什麼 | 典型症狀 | 預防 |
|---|---|---|---|
| **解參考空指標** | `*p`，`p` 是 `NULL` | 立刻當掉（Segmentation fault） | 使用前檢查 `if (p)` |
| **野指標 (wild pointer)** | 沒有初始化的指標，指向隨機位置 | 隨機當掉或改壞資料 | 宣告時就初始化（至少設成 `NULL`） |
| **懸置指標 (dangling pointer)** | 指向的變數已經不存在（離開作用域、已經 `free`） | 有時候正常、有時候亂掉 | 不回傳區域變數的位址；`free` 後設成 `NULL` |
| **越界** | 指標算術超出陣列範圍 | 改壞其他變數、當掉 | 用 `[begin, end)` 範圍並仔細檢查邊界 |
| **型別不符** | 用錯誤的型別解讀記憶體 | 讀到奇怪的值 | 注意編譯器的 `incompatible pointer type` 警告 |

```c
int *wild;                       /* ❌ 野指標：值是垃圾 */
// *wild = 5;                    // ❌ 寫到隨機位置
int *safe = NULL;                /* ✅ */

int *dangling;
{
    int tmp = 10;
    dangling = &tmp;
}                                /* tmp 已經消失 */
// printf("%d\n", *dangling);    // ❌ 懸置指標
```

**偵測工具**：用 `--debug`（AddressSanitizer）執行，大部分的錯誤都會被抓到，並且告訴你是哪一行：

```bash
python3 judge.py test cl3 --debug
```

| ASan 的訊息 | 意思 |
|---|---|
| `SEGV on unknown address 0x000000000000` | 解參考空指標 |
| `stack-buffer-overflow`、`heap-buffer-overflow` | 越界 |
| `stack-use-after-return`、`stack-use-after-scope` | 用到已經消失的區域變數 |
| `heap-use-after-free` | 用到已經 `free` 的記憶體 |

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 位址 | Address | 記憶體格子的編號 | 1.1 |
| 指標 | Pointer | 存位址的變數 | 1.2 |
| 取位址 | Address-of `&` | 取得變數的位址 | 1.2 |
| 解參考 | Dereference `*` | 透過指標存取指向的變數 | 1.3 |
| 空指標 | Null Pointer | 不指向任何東西的指標 | 1.6 |
| 懸置指標 | Dangling Pointer | 指向已經不存在的東西 | 2.3、7 |
| 指標算術 | Pointer Arithmetic | `p + n` 移動 n 個元素 | 3.1 |
| 陣列退化 | Array Decay | 陣列名稱自動變成第一個元素的指標 | 4.1 |
| 指標的指標 | Pointer to Pointer | `int **`，存指標的位址 | 6.1 |
| 通用指標 | void Pointer | `void *`，可以存任何物件的位址 | 6.3 |
| 野指標 | Wild Pointer | 沒初始化的指標 | 7 |

---

# 習題

### 題 1：預測輸出

```c
int a = 3, b = 7;
int *p = &a, *q = &b;
*p = *q;
q = p;
*q = 10;
printf("%d %d %d %d\n", a, b, *p, *q);
```

### 題 2：預測輸出

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr + 1;
printf("%d %d %d %td\n", *p, p[2], *(arr + 4) - *p, &arr[4] - p);
```

### 題 3：下面的宣告中，哪些變數是指標？

```c
int *a, b, *c, **d, e[3];
```

### 題 4：找出錯誤

```c
int *make_array(void) {
    int arr[10];
    for (int i = 0; i < 10; i++) arr[i] = i;
    return arr;
}
```

### 題 5：預測輸出

```c
int a[4] = {1, 2, 3, 4};
int *p = a;
printf("%d ", *p++);
printf("%d ", *p);
printf("%d ", (*p)++);
printf("%d ", *++p);
printf("%d %d\n", a[1], a[2]);
```

### 題 6：哪幾行會編譯錯誤？

```c
int x = 1, y = 2;
const int *p = &x;
int *const q = &x;
*p = 5;          /* ① */
p = &y;          /* ② */
*q = 5;          /* ③ */
q = &y;          /* ④ */
```

### 題 7：寫一個函式 `void set_to_max(int **target, int *a, int *b)`，讓呼叫者的指標 `*target` 指向 `*a`、`*b` 中比較大的那個。

### 題 8：只用指標（不用 `[]`）寫出 `int count_zero(const int *begin, const int *end)`，計算範圍內 0 的個數。

---

# 習題解答

**題 1**：`10 7 10 10`。
- `*p = *q`：`a` 變成 7。
- `q = p`：`q` 改指向 `a`。
- `*q = 10`：`a` 變成 10。`b` 一直沒變。

**題 2**：`20 40 30 3`。`p` 指向 `arr[1]`（20）；`p[2]` 是 `arr[3]`（40）；`50 - 20 = 30`；`&arr[4] - p` 相差 3 個元素。

**題 3**：`a` 是 `int *`、`c` 是 `int *`、`d` 是 `int **`；`b` 是 `int`、`e` 是 `int` 的陣列（不是指標，但會退化成指標）。

**題 4**：回傳了 **區域陣列** 的位址，函式結束後 `arr` 就消失了 → 懸置指標（GCC 警告 `function returns address of local variable`）。修正：用 `malloc` 配置（呼叫者負責 `free`），或讓呼叫者傳陣列進來：`void fill(int *arr, int n)`。

**題 5**：`1 2 2 3 3 3`。
- `*p++`：印 `a[0]` = 1，然後 `p` 移到 `a[1]`。
- `*p`：印 `a[1]` = 2。
- `(*p)++`：印 2，然後 `a[1]` 變成 3（`p` 不動）。
- `*++p`：`p` 先移到 `a[2]`，印 3。
- 最後 `a[1]` 是 3（剛剛被加 1）、`a[2]` 是 3。

**題 6**：① 和 ④。`p` 是「指向 const int」，不能透過它修改（①）；`q` 是「const 指標」，不能改指向（④）。② 和 ③ 合法。

**題 7**：

```c
void set_to_max(int **target, int *a, int *b) {
    *target = (*a > *b) ? a : b;       /* 改的是呼叫者的指標本身 */
}
/* 使用：int x = 3, y = 8; int *m = NULL; set_to_max(&m, &x, &y);  // m 指向 y */
```

**題 8**：

```c
int count_zero(const int *begin, const int *end) {
    int c = 0;
    for (const int *p = begin; p != end; p++)
        if (*p == 0) c++;
    return c;
}
```
