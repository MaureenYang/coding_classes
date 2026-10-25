# C 語言總複習考卷

> 涵蓋 C 語言路線第 01 ~ 12 課。題型有預測輸出、找錯、寫程式、觀念說明；預測輸出的答案都是實際用 `gcc -std=c11`（x86-64 Linux）編譯執行的結果。
> 每一題先自己寫完，再按「看答案」對照。答錯的題目，回到該章重讀對應的段落。

@@@ 01 | 程式結構、型別與輸入輸出

??? 預測輸出
下面的程式會輸出什麼？（`[` `]` 是為了看清楚寬度）

```c
#include <stdio.h>

int main(void) {
    printf("[%5d][%-5d][%05.1f][%.3s]\n", 42, 42, 3.14159, "abcdef");
    printf("%x %o %e\n", 255, 8, 12345.678);
    printf("%c %d %d\n", 'A' + 2, 'A' + 2, '7' - '0');
    return 0;
}
```
!!!
```output
[   42][42   ][003.1][abc]
ff 10 1.234568e+04
C 67 7
```

- `%5d` 靠右補空白到寬度 5；`%-5d` 靠左。
- `%05.1f`：小數 1 位得到 `3.1`，寬度 5 不足的地方補 `0`。
- `%.3s`：字串只印前 3 個字元。
- `%x` 十六進位、`%o` 八進位、`%e` 科學記號（預設小數 6 位）。
- 字元就是整數：`'A' + 2` 是 67，用 `%c` 印出來是 `C`；`'7' - '0'` 是數字 7。

??? 找錯
下面的程式想讀入一個整數、一個 `double`、一個最多 9 個字元的單字。找出所有錯誤並改正。

```c
int n;
double d;
char word[10];
scanf("%d %f %s", n, &d, &word);
```
!!!
1. `n` 要傳位址：`&n`。`scanf` 要把讀到的值寫進變數，所以需要變數的位址。
2. 讀 `double` 要用 `%lf`。`%f` 是 `float *`，型別不符是未定義行為。（`printf` 印 `double` 用 `%f` 就可以，兩者不對稱。）
3. `word` 本身就會轉成指向第一個字元的指標，寫 `word` 就好。`&word` 的型別是 `char (*)[10]`，型別不對。
4. `%s` 沒有限制長度，輸入太長會溢位，應該寫 `%9s`，留一格給 `'\0'`。

```c
scanf("%d %lf %9s", &n, &d, word);
```

另外，應該檢查 `scanf` 的回傳值是不是 3。

??? 預測輸出
預測輸出，並說明第一行為什麼是這個數字。

```c
#include <stdio.h>

int main(void) {
    unsigned int u = 0;
    u = u - 1;
    printf("%u\n", u);
    int big = 2147483647;
    long long ll = big + 1LL;
    printf("%lld\n", ll);
    printf("%zu %zu\n", sizeof(int), sizeof(long long));
    return 0;
}
```
!!!
```output
4294967295
2147483648
4 8
```

- **無號整數溢位有定義**：結果會繞回，`0 - 1` 變成 2³² − 1 = 4294967295。
- `big + 1LL`：`1LL` 是 `long long`，`big` 先被轉成 `long long` 再相加，所以不會溢位。如果寫 `big + 1`，就是 `int` 溢位，屬於未定義行為。
- 在 x86-64 上 `int` 是 4 bytes、`long long` 是 8 bytes。

??? 觀念
1. 要存「全台灣的人口」和「全世界的人口（約 80 億）」，各應該用什麼型別？為什麼？
2. 為什麼 `main` 最後要 `return 0;`？回傳其他值代表什麼？
!!!
1. 台灣人口約 2300 萬，`int`（最大約 21 億）就夠。80 億超過 `int` 的範圍，要用 `long long`（最大約 9.2 × 10¹⁸）。印的時候用 `%lld`。
2. `main` 的回傳值是給作業系統（或呼叫它的程式）看的 **結束碼**：0 代表成功，非 0 代表發生錯誤。評測系統、shell 腳本都靠它判斷程式有沒有正常結束。（C99 起 `main` 沒寫 `return` 時會自動回傳 0，但明確寫出來比較清楚。）

@@@ 02 | 運算子與控制流程

??? 預測輸出
```c
#include <stdio.h>

int main(void) {
    printf("%d %d %d %d\n", 7 / 2, -7 / 2, 7 % -3, -7 % 3);
    printf("%.2f %.2f\n", 7 / 2 * 1.0, 7 / 2.0);
    int a = -1;
    unsigned int b = 1;
    printf("%s\n", a < b ? "a < b" : "a >= b");
    return 0;
}
```
!!!
```output
3 -3 1 -1
3.00 3.50
a >= b
```

- 整數除法 **往 0 截斷**：`-7 / 2` 是 -3（不是 -4）。
- `%` 的結果 **和被除數同號**：`7 % -3` 是 1、`-7 % 3` 是 -1。
- `7 / 2 * 1.0`：先算 `7 / 2` = 3（整數除法），再乘 1.0，已經來不及了；`7 / 2.0` 才是 3.5。
- `a < b`：`int` 和 `unsigned int` 比較時，`a` 會被轉成無號數，-1 變成 4294967295，所以「a 比較大」。這是 C 最經典的陷阱之一，用 `-Wall -Wextra` 編譯會有 `comparison of integer expressions of different signedness` 警告。

??? 預測輸出
```c
#include <stdio.h>

int main(void) {
    int a = 0, b = 0;
    if (a++ || b++) { }
    printf("%d %d\n", a, b);
    if (++a || b++) { }
    printf("%d %d\n", a, b);

    int x = 2, s = 0;
    switch (x) {
        case 1: s += 1;
        case 2: s += 10;
        case 3: s += 100; break;
        default: s += 1000;
    }
    printf("%d\n", s);
    return 0;
}
```
!!!
```output
1 1
2 1
110
```

- 第一個 `if`：`a++` 的值是 0（舊值），所以 `||` 還要算右邊，`b++` 也執行了 → `1 1`。
- 第二個 `if`：`++a` 的值是 2（真），**短路**，`b++` 不會執行 → `2 1`。
- `switch`：從 `case 2` 進入，沒有 `break` 會 **穿透** 到 `case 3`，加了 10 和 100 之後才遇到 `break` → 110。

??? 寫程式
用位元運算寫出下面五個運算式（`x` 是 `unsigned int`，`k` 介於 0 ~ 31）：

1. 第 `k` 位是不是 1
2. 把第 `k` 位設成 1
3. 把第 `k` 位清成 0
4. 把第 `k` 位反轉
5. `x`（`x > 0`）是不是 2 的冪次
!!!
1. `(x >> k) & 1u`，或 `(x & (1u << k)) != 0`
2. `x | (1u << k)`
3. `x & ~(1u << k)`
4. `x ^ (1u << k)`
5. `(x & (x - 1)) == 0`：2 的冪次只有一個位元是 1，減 1 之後那一位變 0、右邊全變 1，AND 起來是 0。

注意寫 `1u` 而不是 `1`：`1 << 31` 會讓有號整數溢位（未定義行為）。

??? 觀念
1. 下面這段程式有什麼問題？
```c
if (x = 5) printf("five\n");
```
2. `i != 0 && 10 / i > 1` 和 `10 / i > 1 && i != 0` 有什麼差別？
!!!
1. `=` 是指定，不是比較。`x = 5` 的值是 5（真），所以 **永遠** 印出 `five`，而且 `x` 被改成 5 了。應該寫 `x == 5`。用 `-Wall` 編譯會有 `suggest parentheses around assignment used as truth value` 警告。
2. `&&` 是 **短路求值**，由左到右，左邊是假就不算右邊。前者在 `i == 0` 時不會執行除法，是安全的；後者會先算 `10 / i`，`i == 0` 時就是除以 0（未定義行為，通常程式直接當掉）。

@@@ 03 | 函式與變數的生命

??? 找錯
下面的 `swap` 為什麼沒有效果？改正它，並寫出呼叫的方式。

```c
void swap(int a, int b) {
    int t = a;
    a = b;
    b = t;
}
```
!!!
C 的參數 **一律傳值**：`a`、`b` 是呼叫者變數的 **複本**，交換複本不影響原本的變數。要修改呼叫者的變數，必須傳 **位址**：

```c
void swap(int *a, int *b) {
    int t = *a;
    *a = *b;
    *b = t;
}

swap(&x, &y);
```

??? 預測輸出
```c
#include <stdio.h>

int x = 1;

int counter(void) {
    static int n = 0;
    n++;
    return n;
}

int main(void) {
    counter();
    counter();
    printf("%d\n", counter());
    int x = 2;
    {
        int x = 3;
        printf("%d\n", x);
    }
    printf("%d\n", x);
    return 0;
}
```
!!!
```output
3
3
2
```

- `static` 區域變數只初始化 **一次**，而且在呼叫之間 **保留它的值**，所以第三次呼叫回傳 3。
- 內層的 `x` **遮蔽 (shadow)** 了外層的 `x`；離開內層區塊後，看到的又是 `main` 裡的 `x = 2`。全域的 `x = 1` 在 `main` 裡完全被遮住了。

??? 預測輸出
`calls` 會被加幾次？先自己畫遞迴樹再看答案。

```c
#include <stdio.h>

int calls = 0;

int fib(int n) {
    calls++;
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

int main(void) {
    int r = fib(5);
    printf("%d %d\n", r, calls);
    return 0;
}
```
!!!
```output
5 15
```

呼叫次數 C(n) = 1 + C(n−1) + C(n−2)，C(0) = C(1) = 1：C(2) = 3、C(3) = 5、C(4) = 9、C(5) = 15。同樣的子問題被算了好多次（`fib(3)` 被算 2 次、`fib(2)` 被算 3 次），呼叫次數是指數成長的，這就是為什麼樸素的費氏遞迴很慢。

??? 觀念
1. 函式原型（prototype）是什麼？為什麼在 `main` 前面呼叫一個寫在後面的函式時需要它？
2. 全域變數前面加 `static` 是什麼意思？和區域變數前面加 `static` 有什麼不同？
!!!
1. 原型是 **只有函式的介面、沒有本體** 的宣告，例如 `int add(int a, int b);`。編譯器由上往下讀，呼叫函式時必須已經知道它的參數型別和回傳型別，才能檢查引數、做型別轉換。沒有原型就呼叫，C99 起是錯誤（舊編譯器會「隱式宣告」成回傳 `int`，型別不符時結果錯誤）。
2. `static` 用在兩個地方，意思完全不同：
   - **函式外面**（全域變數、函式）：限制 **連結性**，只有這個 `.c` 檔看得到，其他檔案用 `extern` 也拿不到。
   - **函式裡面**（區域變數）：改變 **生命週期**，變數存在整個程式執行期間，只初始化一次；但作用域仍然只在函式裡。

@@@ 04 | 陣列

??? 預測輸出
在 x86-64 上，下面的程式輸出什麼？為什麼 `f` 裡面印的不一樣？

```c
#include <stdio.h>

void f(int a[]) {
    printf("%zu\n", sizeof a);
}

int main(void) {
    int a[10];
    printf("%zu %zu\n", sizeof a, sizeof a / sizeof a[0]);
    f(a);
    return 0;
}
```
!!!
```output
40 10
8
```

在 `main` 裡，`a` 是真正的陣列，`sizeof a` 是 10 × 4 = 40 bytes。傳給函式時，陣列會 **退化成指向第一個元素的指標**，參數 `int a[]` 其實就是 `int *a`，`sizeof` 得到的是指標的大小（8）。所以陣列傳給函式時，**一定要另外傳長度**。（gcc 會警告 `'sizeof' on array function parameter 'a' will return size of 'int *'`。）

??? 預測輸出
```c
#include <stdio.h>

int main(void) {
    int a[5] = {1, 2};
    int b[] = {[3] = 7, [1] = 4};
    int m[3][4];
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 4; j++)
            m[i][j] = i * 10 + j;
    printf("%d %d %d\n", a[1], a[4], (int)(sizeof b / sizeof b[0]));
    printf("%d %d\n", b[0], b[1]);
    printf("%d %d\n", (int)(&m[1][2] - &m[0][0]), *(&m[0][0] + 7));
    return 0;
}
```
!!!
```output
2 0 4
0 4
6 13
```

- 初始化時只給部分元素，**其餘自動補 0**，所以 `a[4]` 是 0。
- 指定初始化 `[3] = 7` 決定了陣列至少有 4 個元素，沒指定的 `b[0]`、`b[2]` 是 0。
- 二維陣列是 **列優先 (row-major)** 連續存放：`m[i][j]` 在第 `i * 4 + j` 個位置。`m[1][2]` 是第 6 個；第 7 個是 `m[1][3]` = 13。

??? 找錯
找出下面程式的所有問題：

```c
int *make(int n) {
    int arr[100];
    for (int i = 0; i <= n; i++) arr[i] = i;
    return arr;
}
```
!!!
1. **回傳區域陣列的位址**：`arr` 在函式結束時就消失了，回傳的指標是懸空指標，之後使用是未定義行為。要嘛用 `malloc` 配置（呼叫者負責 `free`），要嘛由呼叫者傳入陣列。
2. `i <= n` 會寫到 `arr[n]`，多寫一格；如果 `n` 是 100 就越界了。通常應該是 `i < n`。
3. 沒有檢查 `n` 是否超過 100。

??? 觀念
用 VLA（`int a[n];`，`n` 是執行時才知道的值）有什麼風險？什麼情況應該改用 `malloc`？
!!!
VLA 配置在 **堆疊** 上，堆疊通常只有幾 MB（Linux 約 8 MB、Windows 約 1 MB）。`n` 很大（例如 10⁶ 個 `int` = 4 MB 以上）時，會 **堆疊溢位**，而且沒有任何辦法偵測失敗，程式直接當掉。另外 C11 起 VLA 是選配功能，有些編譯器（例如 MSVC）不支援。大小可能很大、或來自使用者輸入時，應該用 `malloc`（失敗會回傳 `NULL`，可以檢查）。

@@@ 05 | 指標

??? 預測輸出
```c
#include <stdio.h>

int main(void) {
    int a[] = {10, 20, 30, 40};
    int *p = a + 1;
    printf("%d %d %d\n", *p, *(p + 2), p[-1]);
    printf("%td\n", &a[3] - p);
    *p++ = 99;
    (*p)++;
    for (int i = 0; i < 4; i++) printf("%d ", a[i]);
    printf("\n");
    return 0;
}
```
!!!
```output
20 40 10
2
10 99 31 40 
```

- `p` 指向 `a[1]`；`p + 2` 指向 `a[3]`；`p[-1]` 就是 `*(p - 1)`，也就是 `a[0]`。
- 兩個指標相減得到 **相差幾個元素**（不是 byte 數）：3 − 1 = 2。
- `*p++ = 99`：後置 `++` 優先於 `*`，但用的是 **舊的** `p`，所以 `a[1] = 99`，然後 `p` 移到 `a[2]`。
- `(*p)++`：把 `p` 指向的值（`a[2]`）加 1 → 31。

??? 觀念
下面四個宣告，哪些操作是允許的？在每個空格填「可以」或「不行」。

```c
int x = 1, y = 2;
const int *p1 = &x;
int *const p2 = &x;
const int *const p3 = &x;
```

| | `*pN = 5;` | `pN = &y;` |
|---|---|---|
| `p1` | | |
| `p2` | | |
| `p3` | | |
!!!
| | `*pN = 5;`（改指向的值） | `pN = &y;`（改指標本身） |
|---|---|---|
| `p1`（指向 const int） | 不行 | 可以 |
| `p2`（const 指標） | 可以 | 不行 |
| `p3`（兩者都 const） | 不行 | 不行 |

讀法：從變數名稱往左讀。`const` 在 `*` **左邊** 修飾「指向的資料」，在 `*` **右邊** 修飾「指標本身」。函式參數寫 `const int *` 是在承諾「我不會修改你的資料」。

??? 寫程式
寫一個函式 `int alloc_array(int **out, int n)`：配置 `n` 個 `int`，全部設成 0，透過 `out` 把指標交給呼叫者；成功回傳 1、失敗回傳 0。再寫出呼叫和釋放的程式碼。為什麼參數要是 `int **`？
!!!
```c
int alloc_array(int **out, int n) {
    int *p = calloc(n, sizeof *p);        /* calloc 會清成 0 */
    if (p == NULL) return 0;
    *out = p;                             /* 修改呼叫者的指標變數 */
    return 1;
}

int *arr = NULL;
if (alloc_array(&arr, 100)) {
    /* 使用 arr[0] ~ arr[99] */
    free(arr);
}
```

要讓函式修改呼叫者的 `int`，要傳 `int *`；要讓函式修改呼叫者的 **指標**（`int *`），就要傳指標的位址，也就是 `int **`。如果參數只寫 `int *out`，函式裡 `out = p` 只改到複本，呼叫者的 `arr` 還是 `NULL`。

??? 觀念
1. 陣列名稱 `a` 和指標 `p`（`int *p = a;`）有哪三個不同？
2. `void *` 是什麼？為什麼不能直接 `*vp`？
!!!
1. - `sizeof a` 是整個陣列的大小，`sizeof p` 是指標的大小。
   - `a` 不能被指定（`a = p;` 是錯誤），`p` 可以指向別的地方。
   - `&a` 的型別是「指向整個陣列的指標」`int (*)[N]`，`&p` 是 `int **`。
2. `void *` 是「指向任何型別」的通用指標，任何物件指標都可以轉成 `void *` 再轉回來。因為不知道指向的資料是什麼型別、有多大，所以不能解參考，也不能做指標算術。要先轉回原本的型別：`*(int *)vp`。`malloc` 回傳 `void *`、`qsort` 的比較函式參數是 `const void *`，都是這個原因。

@@@ 06 | 字串

??? 預測輸出
在 x86-64 上：

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char s[] = "hello";
    const char *t = "hello";
    char u[10] = "hi";
    printf("%zu %zu %zu\n", sizeof s, strlen(s), sizeof t);
    printf("%zu %zu\n", sizeof u, strlen(u));
    s[2] = '\0';
    printf("%s %zu\n", s, strlen(s));
    printf("%d %d\n", strcmp("apple", "apricot") < 0, strcmp("abc", "abc"));
    return 0;
}
```
!!!
```output
6 5 8
10 2
he 2
1 0
```

- `char s[] = "hello"` 是 6 bytes 的陣列（包含結尾的 `'\0'`）；`strlen` 不算 `'\0'`，是 5。
- `t` 是指標，`sizeof t` 是 8，和字串長度無關。
- `u` 宣告了 10 個 char，`sizeof` 是 10，但字串內容只有 2 個字元。
- 在中間放一個 `'\0'`，字串就在那裡「結束」了。
- `strcmp` 依字典序比較：第 3 個字元 `'p'` < `'r'`，所以 `"apple"` 比較小，回傳負數；相等回傳 0。

??? 找錯
下面每一段都有錯，說明錯在哪裡、會發生什麼事、怎麼改。

```c
/* (a) */ char *s = "abc";  s[0] = 'X';
/* (b) */ char buf[5];      strcpy(buf, "hello");
/* (c) */ char a[] = "hi", b[] = "hi";  if (a == b) printf("same\n");
/* (d) */ char name[20];    name = "Amy";
```
!!!
- (a) `"abc"` 是 **字串字面值**，存在唯讀的記憶體，修改它是未定義行為（通常 segmentation fault）。要修改就宣告成陣列：`char s[] = "abc";`。
- (b) `"hello"` 需要 6 bytes（含 `'\0'`），`buf` 只有 5 → **緩衝區溢位**。陣列要開 `strlen + 1`，或用 `snprintf(buf, sizeof buf, "%s", "hello")` 安全地截斷。
- (c) `a == b` 比的是 **兩個陣列的位址**，永遠不相等。比較內容要用 `strcmp(a, b) == 0`。
- (d) 陣列不能被指定，編譯錯誤。要用 `strcpy(name, "Amy");`（或 `snprintf`）。

??? 寫程式
不使用 `<string.h>`，寫出 `void reverse(char *s)`：把字串原地反轉（例如 `"abc"` 變成 `"cba"`）。空字串也要能正確處理。
!!!
```c
void reverse(char *s) {
    size_t n = 0;
    while (s[n] != '\0') n++;             /* 自己算長度 */
    if (n == 0) return;                   /* 空字串：n - 1 會變成超大的無號數 */
    for (size_t i = 0, j = n - 1; i < j; i++, j--) {
        char t = s[i];
        s[i] = s[j];
        s[j] = t;
    }
}
```

重點：
- 用兩個索引從兩端往中間交換，`i < j` 時停止（奇數長度時中間那個不用動）。
- `size_t` 是無號數，`n == 0` 時 `n - 1` 會繞回成很大的數，所以要先處理空字串（或改用有號的索引）。
- 呼叫時不能傳字串字面值（`reverse("abc")` 會修改唯讀記憶體）。

??? 觀念
`strncpy(dst, src, n)` 有什麼陷阱？比較安全的替代方式是什麼？
!!!
`strncpy` 在 `src` 的長度 **大於等於 `n`** 時，**不會** 在 `dst` 結尾補 `'\0'`，之後把 `dst` 當字串用（`printf`、`strlen`）就會一直讀到記憶體別處。另外 `src` 很短時，它會把剩下的空間全部補 0，浪費時間。

比較安全的寫法：

```c
snprintf(dst, sizeof dst, "%s", src);     /* 一定會補 '\0'，太長就截斷 */
```

或者用 `strncpy` 之後手動補上：`dst[n - 1] = '\0';`。

@@@ 07 | 動態記憶體

??? 找錯
找出下面程式的所有錯誤（至少 5 個）：

```c
char *copy_upper(const char *src) {
    char *dst = malloc(strlen(src));
    for (int i = 0; src[i]; i++) dst[i] = toupper(src[i]);
    return dst;
}

int main(void) {
    int *a = malloc(10);
    a = realloc(a, 100 * sizeof(int));
    char *s = copy_upper("hello");
    printf("%s\n", s);
    free(a);
    free(a);
}
```
!!!
1. `malloc(strlen(src))` 少了結尾 `'\0'` 的空間，應該是 `strlen(src) + 1`。
2. 迴圈結束後 **沒有寫入 `'\0'`**：要補 `dst[i] = '\0';`，否則 `printf("%s")` 會一直讀下去（越界讀取）。
3. `malloc` 沒有檢查 `NULL`。
4. `malloc(10)` 是 10 個 **byte**，不是 10 個 `int`，應該寫 `10 * sizeof *a`。
5. `a = realloc(a, ...)`：如果 `realloc` 失敗回傳 `NULL`，原本的記憶體位址就遺失了（洩漏）。要先存到暫存指標。
6. `s` 沒有 `free` → 記憶體洩漏。
7. `free(a)` 兩次 → **double free**。
8. （小問題）`toupper` 的參數應該轉成 `unsigned char`：`toupper((unsigned char)src[i])`，否則遇到負的 `char` 是未定義行為。

??? 計算
動態陣列的容量從 0 開始，每次滿了就擴大：`cap = (cap == 0) ? 1 : cap * 2`。連續加入 1000 個元素：

1. 一共擴大（呼叫 `realloc`）幾次？最後容量是多少？
2. 擴大時總共複製了多少個元素？平均每次加入是幾次複製？
3. 如果改成「每次只多 10 格」，加入 n 個元素總共要複製多少個元素（用 Big-O 表示）？
!!!
1. 容量依序是 1、2、4、……、512、1024，一共 **11 次**，最後容量 **1024**。
2. 每次擴大要把舊的元素複製過去：1 + 2 + 4 + … + 512 = **1023** 個，平均每次加入約 1 次複製 → **攤銷 O(1)**。
3. 每 10 次加入就要複製一次全部：10 + 20 + 30 + … ≈ n² / 20，是 **O(n²)**。所以容量一定要「乘以倍數」成長，不能「加上固定值」。

??? 配對
下面四段程式各會讓 AddressSanitizer 回報哪一種錯誤？從 `heap-buffer-overflow`、`heap-use-after-free`、`double-free`、`detected memory leaks` 中選。

```c
/* (a) */ int *p = malloc(4 * sizeof *p);  p[4] = 1;  free(p);
/* (b) */ int *p = malloc(sizeof *p);  free(p);  *p = 1;
/* (c) */ int *p = malloc(sizeof *p);  p = malloc(sizeof *p);  free(p);
/* (d) */ int *p = malloc(sizeof *p);  int *q = p;  free(p);  free(q);
```
!!!
- (a) `heap-buffer-overflow`：合法的索引是 0 ~ 3，寫 `p[4]` 越界。
- (b) `heap-use-after-free`：釋放之後還寫入。
- (c) `detected memory leaks`：第一塊的位址被覆蓋，再也無法釋放。
- (d) `double-free`：`p` 和 `q` 指向同一塊，各 `free` 一次就是釋放兩次。解法是規定好「誰擁有、誰負責釋放」。

??? 寫程式
寫出配置 `rows × cols` 的 `double` 矩陣的函式 `double **mat_new(int rows, int cols)` 和釋放函式 `void mat_free(double **m)`，要求 **只呼叫 2 次 `malloc`**，而且可以用 `m[i][j]` 存取。
!!!
```c
double **mat_new(int rows, int cols) {
    double **m = malloc(rows * sizeof *m);              /* 列指標 */
    double *block = malloc((size_t)rows * cols * sizeof *block);   /* 所有元素，一整塊 */
    if (!m || !block) { free(m); free(block); return NULL; }
    for (int i = 0; i < rows; i++)
        m[i] = block + (size_t)i * cols;                /* 每一列指向 block 裡對應的位置 */
    return m;
}

void mat_free(double **m) {
    if (!m) return;
    free(m[0]);                                         /* m[0] 就是 block */
    free(m);
}
```

好處：資料連續（快取友善）、只要 2 次配置和 2 次釋放。注意 `rows` 是 0 時 `m[0]` 不能存取，實務上要另外處理。

@@@ 08 | struct、union、enum

??? 預測輸出
在 x86-64 上：

```c
#include <stdio.h>

struct A { char a; int b; char c; };
struct B { int b; char a; char c; };
struct C { char a; double d; };
union U { char c; int i; double d; };

int main(void) {
    printf("%zu %zu %zu %zu\n", sizeof(struct A), sizeof(struct B),
           sizeof(struct C), sizeof(union U));
    return 0;
}
```
!!!
```output
12 8 16 8
```

- `struct A`：`a` 在 0，`b` 要對齊 4 → 位移 4（中間填 3 bytes），`c` 在 8，總大小補到 4 的倍數 → 12。
- `struct B`：`b` 在 0，`a` 在 4，`c` 在 5，補到 8。成員 **由大排到小** 可以減少填充。
- `struct C`：`d` 要對齊 8 → 位移 8，總共 16。
- `union` 的大小是 **最大成員** 的大小（再補齊對齊）：8。

??? 預測輸出
```c
#include <stdio.h>

typedef struct { int v[3]; char *name; } Box;
enum Color { RED, GREEN = 5, BLUE, PINK = 2, GRAY };

int main(void) {
    char buf[] = "box";
    Box x = {{1, 2, 3}, buf};
    Box y = x;
    y.v[0] = 100;
    y.name[0] = 'B';
    printf("%d %d %s %s\n", x.v[0], y.v[0], x.name, y.name);
    printf("%d %d %d %d %d\n", RED, GREEN, BLUE, PINK, GRAY);
    return 0;
}
```
!!!
```output
1 100 Box Box
0 5 6 2 3
```

- 結構指定 `y = x` 會複製每個成員：陣列 `v` **整個被複製**，所以改 `y.v[0]` 不影響 `x`。
- 但 `name` 是指標，複製的只是位址（**淺複製**），`x.name` 和 `y.name` 指向同一個 `buf`，改一個兩個都變。
- enum 沒有指定值的成員是「前一個 + 1」：`BLUE = 6`、`GRAY = 3`。

??? 寫程式
用 **標記聯合 (tagged union)** 設計一個 `Shape`，可以是圓（半徑 `r`）或矩形（寬 `w`、高 `h`），並寫出 `double area(const Shape *s)`。為什麼需要那個「標記」？
!!!
```c
typedef enum { SHAPE_CIRCLE, SHAPE_RECT } ShapeKind;

typedef struct {
    ShapeKind kind;                       /* 標記：目前 union 裡放的是哪一種 */
    union {
        struct { double r; } circle;
        struct { double w, h; } rect;
    };                                    /* C11 匿名 union */
} Shape;

double area(const Shape *s) {
    switch (s->kind) {
        case SHAPE_CIRCLE: return 3.14159265 * s->circle.r * s->circle.r;
        case SHAPE_RECT:   return s->rect.w * s->rect.h;
    }
    return 0;
}
```

union 的所有成員 **共用同一塊記憶體**，union 自己不記得最後寫入的是哪一個成員。沒有標記的話，就沒辦法知道該用 `circle.r` 還是 `rect.w` 解讀資料；讀錯成員會得到沒有意義的值。

??? 觀念
1. 什麼時候用 `.`、什麼時候用 `->`？`*p.x` 為什麼是錯的？
2. 為什麼大的結構傳給函式時通常寫 `const T *` 而不是 `T`？
!!!
1. 左邊是 **結構本身** 用 `.`，左邊是 **指向結構的指標** 用 `->`。`p->x` 等於 `(*p).x`。`*p.x` 因為 `.` 的優先順序比 `*` 高，會被解讀成 `*(p.x)`，而 `p` 是指標，沒有 `.x` 成員，編譯錯誤。
2. 傳值會 **複製整個結構**，結構很大時很浪費時間和堆疊空間；傳指標只複製 8 bytes。加上 `const` 是告訴呼叫者「我只讀、不修改」，編譯器也會幫忙檢查。

@@@ 09 | 函式指標

??? 寫程式
學生結構如下。寫一個給 `qsort` 用的比較函式：**分數高的在前；分數相同時，名字字典序小的在前**。再寫出呼叫 `qsort` 的那一行。

```c
typedef struct { char name[21]; int score; } Student;
Student arr[100];
int n;
```
!!!
```c
int cmp_student(const void *a, const void *b) {
    const Student *x = a, *y = b;          /* void * 可以直接指定給 const Student * */
    if (x->score != y->score)
        return (y->score > x->score) - (y->score < x->score);   /* 分數高的在前 */
    return strcmp(x->name, y->name);       /* 名字小的在前 */
}

qsort(arr, n, sizeof arr[0], cmp_student);
```

重點：
- 比較函式收到的是 **元素的位址**，要先轉回 `const Student *`。
- 回傳負數代表 `a` 排在前面。由大到小只要把 `x`、`y` 對調。
- 第三個參數是 **一個元素** 的大小（`sizeof arr[0]`），不是整個陣列。
- 用 `(a > b) - (a < b)` 比較整數最安全；直接相減在數值很大時可能溢位。

??? 預測輸出
```c
#include <stdio.h>

int twice(int x) { return 2 * x; }
int plus3(int x) { return x + 3; }
int square(int x) { return x * x; }

int apply(int (*f)(int), int x, int times) {
    while (times-- > 0) x = f(x);
    return x;
}

int main(void) {
    int (*ops[])(int) = {twice, plus3, square};
    int v = 1;
    for (int i = 0; i < 3; i++) v = ops[i](v);
    printf("%d\n", v);
    printf("%d %d\n", apply(twice, 1, 10), apply(ops[1], 0, 4));
    return 0;
}
```
!!!
```output
25
1024 12
```

- `1 → twice → 2 → plus3 → 5 → square → 25`。
- `apply(twice, 1, 10)`：1 乘以 2 十次 = 2¹⁰ = 1024。
- `apply(plus3, 0, 4)`：0 加 3 四次 = 12。

??? 觀念
說出下面每個宣告的意思：

```c
int *f(int);
int (*g)(int);
int (*h[3])(void);
void (*signal(int sig, void (*fn)(int)))(int);
```
!!!
- `f`：**函式**，接收 `int`，回傳 `int *`。
- `g`：**指標**，指向「接收 `int`、回傳 `int`」的函式。
- `h`：3 個元素的 **陣列**，每個元素是指標，指向「不接收參數、回傳 `int`」的函式。
- `signal`：函式，接收一個 `int` 和一個函式指標（`void (*)(int)`），**回傳** 一個 `void (*)(int)` 型別的函式指標。

讀法是從名字開始，先往右、遇到右括號再往左。實務上用 `typedef void (*Handler)(int);` 拆開會好讀很多：`Handler signal(int sig, Handler fn);`。

??? 找錯
下面想排序字串陣列 `const char *words[]`，為什麼結果不對？

```c
int cmp(const void *a, const void *b) {
    return strcmp(a, b);
}
qsort(words, n, sizeof words[0], cmp);
```
!!!
比較函式收到的是 **元素的位址**：元素是 `const char *`，所以 `a`、`b` 其實是 `const char **`。直接把它們當字串傳給 `strcmp`，比的是「存放指標的那幾個 byte」，不是字串內容。要先解參考一次：

```c
int cmp(const void *a, const void *b) {
    const char *x = *(const char *const *)a;
    const char *y = *(const char *const *)b;
    return strcmp(x, y);
}
```

（如果陣列是 `char words[N][20]` 這種二維字元陣列，元素本身就是字元，`strcmp(a, b)` 反而是對的。）

@@@ 10 | 檔案與輸入輸出

??? 觀念
1. 為什麼 `getchar()` 的回傳值一定要存在 `int`，不能存在 `char`？
2. 下面的迴圈有什麼問題？檔案有 3 行時，`count` 是多少？
```c
while (!feof(fp)) {
    fgets(line, sizeof line, fp);
    count++;
}
```
!!!
1. `getchar` 要能回傳 257 種值：256 種位元組（0 ~ 255）加上 `EOF`（-1）。`char` 只有 256 種值，放不下。在 `char` 有號的平台上，位元組 `0xFF` 會被誤認成 `EOF`，讀到一半就停了；在 `char` 無號的平台上，`c` 永遠不會等於 -1，變成無窮迴圈。
2. `feof` 只有在 **讀取已經失敗之後** 才會變成真。讀完第 3 行時還沒「碰到」結尾，迴圈會再跑一次：第 4 次 `fgets` 失敗，但 `count` 還是加了，結果是 **4**（而且 `line` 還是上一行的內容）。正確寫法是用讀取函式的回傳值控制迴圈：`while (fgets(line, sizeof line, fp) != NULL)`。

??? 預測輸出
```c
#include <stdio.h>

int main(void) {
    int a = 0, b = 0;
    int r1 = sscanf("12 abc", "%d %d", &a, &b);
    int r2 = sscanf("", "%d", &a);
    int r3 = sscanf("7 8 9", "%d %d", &a, &b);
    printf("%d %d %d | %d %d\n", r1, r2, r3, a, b);
    return 0;
}
```
!!!
```output
1 -1 2 | 7 8
```

`scanf` 系列回傳 **成功讀入的項目數**：
- `"12 abc"`：讀到 12，`abc` 不是整數，停止 → 1。
- 空字串：還沒讀到任何項目就到結尾 → `EOF`（-1）。
- `"7 8 9"`：格式只要兩個，讀到 7 和 8 → 2，多的 `9` 不管。

所以讀資料的迴圈要寫 `while (scanf("%d", &x) == 1)`，而不是 `!= EOF`（遇到不是數字的輸入時會回傳 0，變成無窮迴圈）。

??? 預測輸出
`fgets(buf, 6, stdin)` 讀取輸入 `hello world` 加上換行。前三次呼叫分別讀到什麼字串？第幾次呼叫回傳 `NULL`？
!!!
每次最多讀 `6 - 1 = 5` 個字元，遇到換行就停（換行會被存進去）：

1. `"hello"`
2. `" worl"`
3. `"d\n"`
4. 第 4 次回傳 `NULL`（沒有資料了）

判斷「這一行讀完了沒」的方法：看字串最後一個字元是不是 `'\n'`。

??? 觀念
1. `fopen` 的 `"r"`、`"w"`、`"a"` 模式，檔案已經存在時各會怎樣？
2. 錯誤訊息為什麼應該寫到 `stderr`，而不是 `stdout`？
3. 程式當掉時，最後幾行 `printf` 沒有出現在輸出檔裡，可能的原因是什麼？
!!!
1. `"r"`：從頭讀；`"w"`：**清空** 原本的內容再寫；`"a"`：寫在檔案最後面。（檔案不存在時，`"r"` 會失敗回傳 `NULL`，另外兩個會建立新檔。）
2. `stdout` 常常被重新導向到檔案或另一個程式（評測系統就是拿 `stdout` 跟答案比對），錯誤訊息混進去會破壞輸出。`stderr` 是獨立的串流，預設還是顯示在螢幕上。
3. 輸出到檔案時 `stdout` 是 **全緩衝** 的，資料還在緩衝區裡，程式當掉就來不及寫出去。除錯訊息寫到 `stderr`（不緩衝），或必要時呼叫 `fflush(stdout)`。

@@@ 11 | 前置處理器與多檔案程式

??? 預測輸出
```c
#include <stdio.h>

#define SQ_BAD(x) x * x
#define SQ(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define SHOW(e) printf(#e " = %d\n", (e))

int main(void) {
    printf("%d %d\n", SQ_BAD(1 + 2), SQ(1 + 2));
    printf("%d\n", 100 / SQ(5));
    int i = 5, j = 3;
    int m = MAX(i++, j);
    printf("%d %d\n", m, i);
    SHOW(2 + 3 * 4);
    return 0;
}
```
!!!
```output
5 9
4
6 7
2 + 3 * 4 = 14
```

- `SQ_BAD(1 + 2)` 展開成 `1 + 2 * 1 + 2` = 5。巨集是 **文字替換**，參數和整個運算式都要加括號。
- `100 / SQ(5)` → `100 / ((5) * (5))` = 4。如果巨集外面沒有括號，會變成 `100 / 5 * 5` = 100。
- `MAX(i++, j)` 展開成 `((i++) > (j) ? (i++) : (j))`，`i++` 被執行 **兩次**：比較時 5 > 3，再取一次值得到 6，`i` 最後是 7。不要把有副作用的運算式傳給巨集。
- `#e` 把參數變成字串 `"2 + 3 * 4"`。

??? 觀念
`util.h` 的內容如下，`a.c` 和 `b.c` 都 `#include "util.h"`，執行 `gcc a.c b.c` 會得到什麼錯誤？引入防護 (include guard) 為什麼救不了？怎麼修正？

```c
#ifndef UTIL_H
#define UTIL_H
int counter = 0;
int twice(int x) { return 2 * x; }
#endif
```
!!!
連結錯誤：`multiple definition of 'counter'` 和 `multiple definition of 'twice'`。

`a.c` 和 `b.c` 是 **分開編譯** 的，各自都會得到一份 `counter` 和 `twice` 的 **定義**；連結時發現同一個名字有兩份。引入防護只防止「同一個 `.c` 檔」include 同一個標頭檔兩次，管不到不同的 `.c` 檔。

修正：標頭檔只放 **宣告**，定義放在 **一個** `.c` 檔裡：

```c
/* util.h */
#ifndef UTIL_H
#define UTIL_H
extern int counter;
int twice(int x);
#endif

/* util.c */
#include "util.h"
int counter = 0;
int twice(int x) { return 2 * x; }
```

編譯：`gcc a.c b.c util.c`。（小函式也可以在標頭檔寫成 `static inline`。）

??? 觀念
看到下面的錯誤訊息，各是編譯的哪一個步驟出錯？可能的原因是什麼？

1. `fatal error: lsit.h: No such file or directory`
2. `error: expected ';' before 'return'`
3. `undefined reference to 'list_push'`
4. `undefined reference to 'sqrt'`
!!!
1. **前置處理**：`#include` 找不到檔案，這裡是檔名拼錯（`lsit.h`），或標頭檔不在搜尋路徑裡。
2. **編譯**：語法錯誤，前一行少了分號。
3. **連結**：程式碼語法正確，但找不到 `list_push` 的 **定義**。通常是沒有一起編譯實作檔（`gcc main.c list.c`）、名字拼錯，或函式被宣告成 `static`。
4. **連結**：用了 `<math.h>` 的函式，但沒有連結數學函式庫，要加 `-lm`。

??? 寫程式
寫一個巨集 `SWAP(T, a, b)` 交換兩個型別為 `T` 的變數，要求下面的程式可以正確編譯並執行。為什麼要用 `do { ... } while (0)`？

```c
if (a > b) SWAP(int, a, b); else printf("ok\n");
```
!!!
```c
#define SWAP(T, a, b) do { T tmp_ = (a); (a) = (b); (b) = tmp_; } while (0)
```

如果只用 `{ ... }` 包起來，`if (a > b) { ... }; else ...` 裡那個分號會結束 `if` 敘述，後面的 `else` 找不到對應的 `if`，編譯錯誤。`do { ... } while (0)` 是 **一個完整的敘述**，後面剛好需要一個分號，用起來就像函式呼叫一樣。迴圈只執行一次，編譯器會把它最佳化掉。

@@@ 12 | 用 C 實作資料結構

??? 寫程式
用「指標的指標」的技巧，寫出 `int remove_all(Node **head, int x)`：刪除串列中所有值等於 `x` 的節點並釋放它們，回傳刪除的個數。**不可以** 對 head 做特別處理。

```c
typedef struct Node { int val; struct Node *next; } Node;
```
!!!
```c
int remove_all(Node **head, int x) {
    int removed = 0;
    Node **pp = head;                     /* pp 指向「指向目前節點的那個指標」 */
    while (*pp != NULL) {
        if ((*pp)->val == x) {
            Node *dead = *pp;
            *pp = dead->next;             /* 把指向它的指標改成指向下一個 */
            free(dead);
            removed++;                    /* pp 不動：*pp 已經是下一個節點 */
        } else {
            pp = &(*pp)->next;            /* 前進到目前節點的 next 欄位 */
        }
    }
    return removed;
}
```

`pp` 一開始指向 `head` 變數，之後指向前一個節點的 `next` 欄位。不管是哪一種，`*pp = ...` 都能把目前的節點「接掉」，所以刪除第一個節點不需要特別處理。

??? 預測輸出
下面的程式用到串列和 `Node **`，預測輸出。

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct Node { int val; struct Node *next; } Node;

void push_front(Node **head, int v) {
    Node *n = malloc(sizeof *n);
    n->val = v;
    n->next = *head;
    *head = n;
}

void insert_sorted(Node **head, int v) {
    Node **pp = head;
    while (*pp && (*pp)->val < v) pp = &(*pp)->next;
    Node *n = malloc(sizeof *n);
    n->val = v;
    n->next = *pp;
    *pp = n;
}

int main(void) {
    Node *a = NULL, *b = NULL;
    for (int i = 1; i <= 4; i++) push_front(&a, i);
    int in[] = {5, 1, 4, 9, 3};
    for (int i = 0; i < 5; i++) insert_sorted(&b, in[i]);
    for (Node *p = a; p; p = p->next) printf("%d ", p->val);
    printf("| ");
    for (Node *p = b; p; p = p->next) printf("%d ", p->val);
    printf("\n");
    while (a) { Node *t = a->next; free(a); a = t; }
    while (b) { Node *t = b->next; free(b); b = t; }
    return 0;
}
```
!!!
```output
4 3 2 1 | 1 3 4 5 9 
```

- `push_front` 每次都加在最前面，所以順序反過來。
- `insert_sorted` 找到第一個 `>= v` 的位置插入，結果是排好序的。
- 釋放串列時要 **先記住下一個節點** 再 `free`，否則 `free` 之後讀 `a->next` 是 use-after-free。

??? 觀念
第 12 課的泛型堆疊用 `void *` 加上 `elem_size` 存放任何型別：

1. 為什麼存放資料的指標宣告成 `char *data`，而不是 `void *data`？
2. `push` 為什麼要用 `memcpy`，不能寫 `data[size] = elem`？
3. 和 C++ 的 `std::stack<int>` 比起來，這種做法失去了什麼？
!!!
1. 要計算第 `i` 個元素的位址 `data + i * elem_size`，需要「以 byte 為單位」的指標算術。`void *` 不能做指標算術（不知道一步要走幾個 byte），`char` 剛好是 1 byte。
2. 容器不知道元素的型別，只知道每個元素有幾個 byte。`memcpy(data + size * elem_size, elem, elem_size)` 不管元素是什麼型別，都把那幾個 byte 原封不動地複製過去。
3. **型別檢查**：`stack_push(&s, &some_double)` 放進一個「存 `int`」的堆疊，編譯器不會發現，結果是錯的。另外每次都要 `memcpy`，比直接指定稍慢。C++ 的模板在編譯時就知道型別，兩個問題都沒有。

??? 觀念
不透明指標（opaque pointer）的寫法是：標頭檔只寫 `typedef struct Counter Counter;`，結構的內容寫在 `.c` 檔。

1. 使用者在自己的程式裡寫 `Counter c;` 或 `p->value = 5;` 會發生什麼事？為什麼？
2. 這樣做有什麼好處和代價？
!!!
1. **編譯錯誤**（`storage size of 'c' isn't known`、`invalid use of incomplete typedef 'Counter'`）。使用者那邊只看到 **不完整型別**：知道有這個型別，但不知道大小和成員，所以只能使用它的指標，不能建立變數、不能存取成員。
2. 好處：
   - 真正的 **封裝**，使用者不可能直接改內部的欄位，只能透過函式操作。
   - 修改結構的內容時，使用者的程式碼不用改，甚至不用重新編譯。

   代價：
   - 物件一定要用 `xxx_new()` 在堆積上配置（使用者不知道大小，無法放在堆疊上），用完要呼叫 `xxx_free()`。
   - 每次存取都要經過函式呼叫。

   C 標準函式庫的 `FILE` 就是這樣設計的。

??? 判斷
下面哪些是 **未定義行為**？說明理由。

```c
(a) unsigned int u = 0; u = u - 1;
(b) int i = 2147483647; i = i + 1;
(c) int a[3]; int *p = a + 3;
(d) int a[3]; int x = *(a + 3);
(e) char *s = malloc(4); strcpy(s, "abcd");
(f) int x; printf("%d\n", x);
(g) int k = 1 << 31;
```
!!!
- (a) **不是**：無號整數溢位有定義，繞回成 `UINT_MAX`。
- (b) **是**：有號整數溢位。
- (c) **不是**：指標可以指向「最後一個元素的下一個位置」（就像 C++ 的 `end()`），只是不能解參考。
- (d) **是**：解參考越界的位置。
- (e) **是**：`"abcd"` 需要 5 bytes（含 `'\0'`），只配置了 4 → 堆積越界。
- (f) **是**：讀取未初始化的區域變數。
- (g) **是**：`1` 是有號 `int`，左移到符號位元會溢位（應該寫 `1u << 31`）。

抓這些錯誤的工具：`gcc -Wall -Wextra` 的警告，以及執行時的 `-fsanitize=address,undefined`（本平台的 `--debug`）。
