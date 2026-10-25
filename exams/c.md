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

??? 預測輸出
```c
#include <stdio.h>

int main(void) {
    printf("%+d %+d|%8.3f|%-6s|%%|%c\n", 5, -5, 3.14159, "ab", 65);
    printf("%.2e|%g|%g\n", 1234.5, 0.0001, 100000000.0);
    int x = 3.99;
    double d = 7 / 2;
    double e = (double)7 / 2;
    printf("%d %.1f %.1f\n", x, d, e);
    return 0;
}
```
!!!
```output
+5 -5|   3.142|ab    |%|A
1.23e+03|0.0001|1e+08
3 3.0 3.5
```

- `%+d` 一定印出正負號；`%8.3f` 寬度 8、小數 3 位（四捨五入成 3.142）；`%-6s` 靠左補到 6 格；`%%` 印出一個 `%`；`%c` 把 65 當成字元 `A`。
- `%.2e` 是科學記號、小數 2 位；`%g` 自動選擇比較短的表示法，並去掉多餘的 0。
- `int x = 3.99` 會 **截斷**（不是四捨五入）成 3。
- `7 / 2` 兩邊都是 `int`，結果是 3，存進 `double` 才變成 3.0；要先把其中一邊轉成 `double`，才會做浮點數除法。

??? 找錯
下面的程式想讀入兩個整數並印出平均（要有小數），找出所有問題：

```c
int a, b;
scanf("%d%d", &a, &b);
double avg = (a + b) / 2;
printf("%d\n", avg);
```
!!!
1. `(a + b) / 2` 是 **整數除法**，小數部分已經被丟掉了，之後才轉成 `double`。應該寫 `(a + b) / 2.0`。
2. `printf("%d", avg)`：`avg` 是 `double`，卻用 `%d` 印，型別不符是 **未定義行為**（通常印出亂七八糟的數字）。應該用 `%f`（例如 `%.2f`）。
3. `a + b` 在兩個數都很大時可能 **溢位**，可以寫成 `((double)a + b) / 2`。
4. 沒有檢查 `scanf` 的回傳值是否為 2。

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

??? 預測輸出
```c
#include <stdio.h>

int main(void) {
    int i, s = 0;
    for (i = 0; i < 10; i += 3) s += i;
    printf("%d %d\n", i, s);

    int n = 0;
    do { n++; } while (n < 0);
    printf("%d\n", n);

    int k = 5;
    while (k-- > 0) printf("%d", k);
    printf(" %d\n", k);
    return 0;
}
```
!!!
```output
12 18
1
43210 -1
```

- `for`：i 依序是 0、3、6、9 時執行迴圈本體（s = 18），i 變成 12 時條件不成立才離開，所以離開後 i 是 **12**。
- `do-while` **至少執行一次**，條件在最後才檢查。
- `k-- > 0`：先用舊值比較、再減 1。k = 5 時比較成立，進迴圈時已經是 4；最後一次比較 `0 > 0` 不成立，但 `--` 還是執行了，所以離開時 k 是 **-1**。

??? 預測輸出
```c
#include <stdio.h>

int main(void) {
    unsigned int x = 0xF0;
    printf("%u %u %u %u\n", x >> 4, x & 0x3C, x | 0x0F, x ^ 0xFF);
    printf("%d %d %d\n", 5 & 3, 5 | 3, 5 ^ 3);
    printf("%u %d\n", ~0u, !5);
    int a = 10;
    a <<= 2;
    a |= 1;
    printf("%d\n", a);
    return 0;
}
```
!!!
```output
15 48 255 15
1 7 6
4294967295 0
41
```

- `0xF0` = 1111 0000₂：右移 4 位是 1111₂ = 15；`& 0x3C`（0011 1100₂）= 0011 0000₂ = 48；`| 0x0F` = 1111 1111₂ = 255；`^ 0xFF` 把 8 個位元全部反轉 = 0000 1111₂ = 15。
- 5 = 101₂、3 = 011₂：AND = 001₂、OR = 111₂、XOR = 110₂。
- `~0u` 是 32 個 1；`!` 是 **邏輯** 非，非 0 的值都變成 0（不要和位元的 `~` 搞混）。
- `a <<= 2` 是 a × 4 = 40，再 `|= 1` 把最低位設成 1 → 41。

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

??? 預測輸出
```c
#include <stdio.h>

void f(int n) {
    if (n == 0) return;
    printf("%d ", n);
    f(n - 1);
    printf("%d ", n);
}

int sum_digits(int n) {
    return n < 10 ? n : n % 10 + sum_digits(n / 10);
}

int main(void) {
    f(3);
    printf("\n%d\n", sum_digits(9875));
    return 0;
}
```
!!!
```output
3 2 1 1 2 3 
29
```

- 每一層在 **遞迴之前** 印一次（往下走時：3 2 1），**遞迴回來之後** 再印一次（往回走時：1 2 3）。這就是呼叫堆疊「後進先出」的效果。
- `sum_digits`：9875 → 5 + sum_digits(987) → 5 + 7 + sum_digits(98) → 5 + 7 + 8 + 9 = 29。

??? 寫程式
用遞迴寫出 `long long power(long long b, int e)`（`e ≥ 0`），要求遞迴深度是 O(log e)。說明為什麼比「`b * power(b, e - 1)`」快。
!!!
```c
long long power(long long b, int e) {
    if (e == 0) return 1;                 /* 終止條件 */
    long long half = power(b, e / 2);     /* 只遞迴一次，結果存起來 */
    if (e % 2 == 0) return half * half;
    else return half * half * b;
}
```

每次把指數 **減半**，遞迴深度和乘法次數都是 O(log e)。`b * power(b, e - 1)` 每次只減 1，要 e 層遞迴、e 次乘法。

常見錯誤：寫成 `power(b, e / 2) * power(b, e / 2)`，同一個子問題算了兩次，又變回 O(e) 次呼叫。

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

??? 預測輸出
下面的程式對陣列做 **一輪** 氣泡排序（相鄰兩個比較，前面比較大就交換），預測輸出：

```c
#include <stdio.h>

int main(void) {
    int a[5] = {5, 1, 4, 2, 3};
    int swaps = 0;
    for (int i = 0; i + 1 < 5; i++) {
        if (a[i] > a[i + 1]) {
            int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;
            swaps++;
        }
    }
    for (int i = 0; i < 5; i++) printf("%d ", a[i]);
    printf("| %d\n", swaps);
    return 0;
}
```
!!!
```output
1 4 2 3 5 | 4
```

5 在每一次比較都比右邊大，一路被交換到最後面：
- 比較 5、1 → 交換：`1 5 4 2 3`
- 比較 5、4 → 交換：`1 4 5 2 3`
- 比較 5、2 → 交換：`1 4 2 5 3`
- 比較 5、3 → 交換：`1 4 2 3 5`

一輪之後 **最大的元素一定到了最後面**，n 個元素最多 n − 1 輪就排好了，O(n²)。迴圈條件寫成 `i + 1 < 5`，避免存取 `a[5]` 越界。

??? 寫程式
寫一個函式，計算 `rows × 4` 的二維陣列每一列的總和，存到 `sums` 陣列。函式參數要怎麼宣告？為什麼第二維的大小一定要寫出來？
!!!
```c
void row_sums(int m[][4], int rows, int sums[]) {
    for (int i = 0; i < rows; i++) {
        sums[i] = 0;
        for (int j = 0; j < 4; j++) sums[i] += m[i][j];
    }
}
```

（C99 也可以用 VLA 參數：`void row_sums(int rows, int cols, int m[rows][cols], int sums[])`，注意 `rows`、`cols` 要寫在 `m` 前面。）

二維陣列傳給函式時會退化成「指向第一列的指標」，型別是 `int (*)[4]`。編譯器要計算 `m[i][j]` 的位址 `m + i * 4 + j`，必須知道 **一列有幾個元素**；第一維（列數）不影響位址計算，所以可以省略。

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

??? 預測輸出
```c
#include <stdio.h>

int main(void) {
    int x = 1, y = 2;
    int *p = &x;
    int **pp = &p;
    **pp = 10;
    *pp = &y;
    **pp += 5;
    printf("%d %d %d\n", x, y, *p);

    int arr[] = {1, 2, 3, 4, 5};
    int *b = arr, *e = arr + 5;
    int sum = 0;
    while (b != e) sum += *b++;
    printf("%d %d\n", sum, (int)(e - arr));
    return 0;
}
```
!!!
```output
10 7 7
15 5
```

- `**pp = 10`：`*pp` 就是 `p`，`**pp` 就是 `*p`，也就是 x → x = 10。
- `*pp = &y`：修改的是 `p` 本身，現在 `p` 指向 y。
- `**pp += 5`：y = 7，`*p` 也是 7。
- `[b, e)` 半開區間的走訪：`e` 指向最後一個元素的 **下一個位置**，不能解參考，但可以拿來比較。`*b++` 先取值、再讓 b 前進。

??? 找錯
下面三段程式各有什麼問題？會發生什麼事？

```c
/* (a) */ int *p;  *p = 5;
/* (b) */ int *q = NULL;  if (*q == 0) printf("zero\n");
/* (c) */ int *r = malloc(sizeof *r);  free(r);  if (r != NULL) *r = 3;
```
!!!
- (a) **野指標 (wild pointer)**：`p` 沒有初始化，裡面是隨機的位址，寫入它是未定義行為（可能當掉，也可能悄悄改壞別的資料）。指標宣告時就要初始化（`= NULL` 或一個有效的位址）。
- (b) **解參考空指標**：未定義行為，通常是 segmentation fault。使用前要先檢查 `q != NULL`。
- (c) **懸空指標**：`free(r)` 不會把 `r` 設成 NULL，`r` 還是舊的位址，所以 `r != NULL` 檢查 **擋不住**，寫入就是 use-after-free。好習慣是 `free(r); r = NULL;`。

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

??? 預測輸出
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    const char *s = "banana";
    printf("%td %td\n", strchr(s, 'n') - s, strrchr(s, 'a') - s);
    printf("%s\n", strstr(s, "nan"));
    printf("%d %d\n", strncmp("apple", "apply", 4), atoi("123abc"));
    char buf[20];
    snprintf(buf, sizeof buf, "%s-%03d", "id", 7);
    printf("%s %zu\n", buf, strlen(buf));
    char small[5];
    int need = snprintf(small, sizeof small, "%s", "hello world");
    printf("%s %d\n", small, need);
    return 0;
}
```
!!!
```output
2 5
nana
0 123
id-007 6
hell 11
```

- `strchr` 找 **第一個**、`strrchr` 找 **最後一個**，回傳指標，減掉開頭得到索引。
- `strstr` 回傳子字串第一次出現的位置，從那裡印到結尾。
- `strncmp` 只比前 4 個字元（"appl" 相同 → 0）；`atoi` 讀到不是數字的字元就停。
- `%03d` 寬度 3、補 0。
- `snprintf` **最多寫 size − 1 個字元並補上 `'\0'`**，不會溢位；回傳值是「如果空間足夠會寫幾個字元」（11），比 size 大就代表被截斷了。

??? 寫程式
不使用 `<string.h>`，寫出 `int my_strcmp(const char *a, const char *b)`：行為和 `strcmp` 一樣（a 比較小回傳負數、相等回傳 0、比較大回傳正數）。為什麼比較字元時要轉成 `unsigned char`？
!!!
```c
int my_strcmp(const char *a, const char *b) {
    while (*a != '\0' && *a == *b) {
        a++;
        b++;
    }
    return (unsigned char)*a - (unsigned char)*b;
}
```

- 一直往前走，直到遇到不同的字元，或其中一個字串結束（較短的字串結尾的 `'\0'` 是 0，比任何字元都小，所以 `"app"` < `"apple"`）。
- `strcmp` 規定以 `unsigned char` 比較。`char` 可能是有號的，`0xE4`（例如 UTF-8 中文的第一個位元組）會變成負數，結果就和標準不一致。
- 兩個 `unsigned char` 相減會先提升成 `int`，不會溢位。

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

??? 預測輸出
```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *a = calloc(3, sizeof *a);
    a[1] = 5;
    int *t = realloc(a, 5 * sizeof *a);
    if (t == NULL) { free(a); return 1; }
    a = t;
    a[3] = a[4] = 9;
    for (int i = 0; i < 5; i++) printf("%d ", a[i]);
    printf("\n");
    t = realloc(a, 2 * sizeof *a);
    if (t) a = t;
    printf("%d %d\n", a[0], a[1]);
    free(a);
    free(NULL);
    printf("done\n");
    return 0;
}
```
!!!
```output
0 5 0 9 9 
0 5
done
```

- `calloc` 把配置的空間 **清成 0**。
- `realloc` 擴大時會 **保留原本的資料**（前 3 個元素），新增的空間內容未定（這裡馬上被設成 9）。
- `realloc` 縮小時只保留前面的元素。
- `free(NULL)` 是合法的，什麼都不做。

??? 觀念
1. 下面兩個函式，哪一個是正確的？為什麼？
```c
int *make1(int n) { int a[100]; for (int i = 0; i < n; i++) a[i] = i; return a; }
int *make2(int n) { int *a = malloc(n * sizeof *a); for (int i = 0; a && i < n; i++) a[i] = i; return a; }
```
2. `make2` 的說明文件應該寫清楚什麼？
!!!
1. **`make2` 正確**。`make1` 的 `a` 是 **區域陣列**，放在堆疊上，函式結束就失效了，回傳的是懸空指標。`make2` 的記憶體在 **堆積** 上，會一直存在到有人呼叫 `free` 為止，回傳它的位址是合法的（而且 `make2` 也沒有 100 個元素的上限）。
2. 要寫清楚 **所有權**：「回傳的陣列由呼叫者負責 `free`」，以及「配置失敗時回傳 NULL」。C 沒有自動釋放，每塊記憶體都要有一個明確的擁有者。

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

??? 預測輸出
```c
#include <stdio.h>
typedef struct { char name[8]; int age; } P;
int main(void) {
    P ps[] = {{"amy", 20}, {"bob", 31}, {"cat", 25}};
    P *p = ps;
    p++;
    printf("%s %d\n", p->name, (p + 1)->age);
    printf("%zu\n", sizeof ps / sizeof ps[0]);
    printf("%c\n", ps[2].name[0] - 32);
    P q = ps[0];
    q.age = 99;
    p = &ps[0];
    p->age += 1;
    printf("%d %d\n", q.age, ps[0].age);
    return 0;
}
```
!!!
```output
bob 25
3
C
99 21
```

- `p++` 讓指標前進 **一整個結構**（`sizeof(P)` 個 byte），指向 `ps[1]`，所以 `p->name` 是 bob；`(p + 1)` 指向 `ps[2]`，年齡是 25。
- `sizeof ps / sizeof ps[0]` 是陣列的元素個數。
- 小寫字母減 32 就是對應的大寫字母（ASCII 中 `'c'` 是 99、`'C'` 是 67）。實務上用 `toupper` 比較清楚。
- `P q = ps[0]` 是 **複製**，改 `q` 不影響 `ps[0]`；透過指標 `p->age += 1` 才會改到 `ps[0]` 本身。

??? 寫程式
檔案權限用位元旗標表示：讀 = 4、寫 = 2、執行 = 1。用 `enum` 定義這三個旗標，並寫出 `void perm_str(int perm, char out[4])`，把權限轉成 `"rwx"` 這樣的字串，沒有的權限用 `-`（例如 5 → `"r-x"`）。
!!!
```c
enum { PERM_READ = 4, PERM_WRITE = 2, PERM_EXEC = 1 };

void perm_str(int perm, char out[4]) {
    out[0] = (perm & PERM_READ)  ? 'r' : '-';
    out[1] = (perm & PERM_WRITE) ? 'w' : '-';
    out[2] = (perm & PERM_EXEC)  ? 'x' : '-';
    out[3] = '\0';
}

/* 組合權限：PERM_READ | PERM_EXEC 就是 5 */
```

- 每個旗標佔 **一個位元**（4 = 100₂、2 = 010₂、1 = 001₂），所以可以用 `|` 組合、用 `&` 檢查，互不干擾。
- 用 `enum` 給這些數字取名字，比在程式裡到處寫 4、2、1（魔術數字）清楚得多。
- `out` 要有 4 格：3 個字元加上結尾的 `'\0'`。

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

??? 預測輸出
C 沒有 lambda，回呼函式需要額外資料時，用一個 `void *ctx` 參數轉交：

```c
#include <stdio.h>
void for_each(const int *a, int n, void (*f)(int, void *), void *ctx) {
    for (int i = 0; i < n; i++) f(a[i], ctx);
}
void find_max(int v, void *ctx) { int *m = ctx; if (v > *m) *m = v; }
void count_even(int v, void *ctx) { if (v % 2 == 0) ++*(int *)ctx; }
typedef struct { long long sum; int n; } Avg;
void add_avg(int v, void *ctx) { Avg *s = ctx; s->sum += v; s->n++; }
int main(void) {
    int a[] = {3, 8, -2, 7, 10};
    int mx = a[0], ev = 0;
    Avg s = {0, 0};
    for_each(a, 5, find_max, &mx);
    for_each(a, 5, count_even, &ev);
    for_each(a, 5, add_avg, &s);
    printf("%d %d %.1f\n", mx, ev, (double)s.sum / s.n);
    return 0;
}
```
!!!
```output
10 3 5.2
```

- `find_max`：`ctx` 指向目前的最大值（初始值用第一個元素，不要用 0，陣列可能全是負數）→ 10。
- `count_even`：8、-2、10 是偶數（-2 % 2 是 0）→ 3。
- `add_avg`：需要好幾個資料時，包成一個 `struct` 再傳它的位址；總和 26、個數 5，平均 5.2。

`for_each` 完全不知道 `ctx` 是什麼，只負責原封不動地轉交；回呼函式自己知道該把它轉回什麼型別。這是 C 函式庫最常見的設計（`qsort_r`、`pthread_create`、GUI 的事件回呼）。

??? 寫程式
有一個 **依 `id` 排序好** 的陣列 `Item items[n]`（`typedef struct { int id; char name[20]; } Item;`）。用 `bsearch` 寫出 `Item *find_item(Item *items, int n, int id)`，找不到回傳 NULL。比較函式的兩個參數各是什麼型別？
!!!
```c
int cmp_key_item(const void *key, const void *elem) {
    int k = *(const int *)key;                 /* 第一個參數是 key */
    const Item *it = elem;                     /* 第二個參數是陣列元素 */
    return (k > it->id) - (k < it->id);
}

Item *find_item(Item *items, int n, int id) {
    return bsearch(&id, items, n, sizeof items[0], cmp_key_item);
}
```

`bsearch` 呼叫比較函式時，**第一個參數一定是 key 的位址**，第二個是陣列元素的位址，兩者的型別 **可以不同**：這裡 key 是 `int *`、元素是 `Item *`。這樣就不用為了搜尋特地建立一個假的 `Item`。陣列必須是用「同樣的順序」（依 `id` 遞增）排序過的，否則結果沒有意義。

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

??? 預測輸出
下面的程式用第 10 課 `wc` 的狀態機，統計一個字串的行數、單字數、字元數：

```c
#include <ctype.h>
#include <stdio.h>
int main(void) {
    const char *text = "  hello  world\tfoo \n bar\n\nend";
    long chars = 0, lines = 0, words = 0;
    int in_word = 0;
    for (const char *p = text; *p; p++) {
        int c = (unsigned char)*p;
        chars++;
        if (c == '\n') lines++;
        if (isspace(c)) in_word = 0;
        else if (!in_word) { in_word = 1; words++; }
    }
    printf("%ld %ld %ld\n", lines, words, chars);
    return 0;
}
```
!!!
```output
3 5 29
```

- **行數** 是 `'\n'` 的個數：3 個（中間有一個空行，最後的 `end` 後面沒有換行，不算）。
- **單字** 是連續的非空白字元：hello、world、foo、bar、end，共 5 個。連續的空白、tab、換行都只是「離開單字」，不會多算。
- **字元數** 包含所有空白和換行：29。

讀檔版本只要把 `for` 迴圈改成 `while ((c = getchar()) != EOF)`，邏輯完全一樣。

??? 寫程式
寫出 `int sum_file(const char *path, long long *sum)`：開啟文字檔，讀出所有整數加總，透過 `sum` 回傳結果。檔案打不開回傳 -1，檔案裡有不是整數的內容回傳 -2，成功回傳讀到的整數個數。不能有資源洩漏。
!!!
```c
int sum_file(const char *path, long long *sum) {
    FILE *fp = fopen(path, "r");
    if (fp == NULL) return -1;               /* 打不開：直接回傳，沒有東西要關 */
    long long total = 0, x;
    int count = 0, r;
    while ((r = fscanf(fp, "%lld", &x)) == 1) {
        total += x;
        count++;
    }
    int bad = (r != EOF);                    /* 迴圈因為格式錯誤（回傳 0）而停止 */
    fclose(fp);                              /* 每一條路徑都要關檔 */
    if (bad) return -2;
    *sum = total;
    return count;
}
```

重點：
- `fopen` 一定要檢查 `NULL`。
- 用 **`fscanf` 的回傳值** 控制迴圈（不要用 `feof`）：回傳 1 代表讀到一個整數；回傳 `EOF` 代表正常讀完；回傳 0 代表遇到不是整數的內容。
- 不管成功或失敗，打開的檔案都要 `fclose`；先記下結果、關檔，再回傳。

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

??? 預測輸出
```c
#include <stdio.h>
#define DEBUG 1
#define LOG(x) printf("log: %s = %d\n", #x, (x))
#define A 2
#define B A + 1
#define B2 (A + 1)
int main(void) {
#if DEBUG
    LOG(2 * 3);
#endif
#ifdef UNDEFINED_THING
    printf("yes\n");
#else
    printf("no\n");
#endif
    printf("%d %d\n", B * 2, B2 * 2);
    return 0;
}
```
!!!
```output
log: 2 * 3 = 6
no
4 6
```

- `#x` 把參數 **原樣** 變成字串 `"2 * 3"`，`(x)` 則是計算出來的值。
- `UNDEFINED_THING` 沒有定義，走 `#else`。
- `B * 2` 展開成 `2 + 1 * 2` = 4；`B2` 的定義有括號，`(2 + 1) * 2` = 6。**巨集的內容如果是運算式，整個都要加括號。**

??? 觀念
你要寫一個計數器模組，讓 `main.c` 可以呼叫 `counter_add(int)` 和 `counter_get()`，計數器的值 **不能** 被其他檔案直接修改，模組裡還有一個只給自己用的 `check_range()` 函式。寫出 `counter.h` 和 `counter.c` 的內容（函式本體可以簡單寫），以及編譯指令。
!!!
```c
/* counter.h：只放公開的宣告 */
#ifndef COUNTER_H
#define COUNTER_H

void counter_add(int x);
int counter_get(void);

#endif
```

```c
/* counter.c */
#include "counter.h"

static int value = 0;                    /* static：其他檔案看不到，無法直接修改 */

static int check_range(int x) {          /* static：只有這個檔案能呼叫 */
    return x >= -1000 && x <= 1000;
}

void counter_add(int x) {
    if (check_range(x)) value += x;
}

int counter_get(void) {
    return value;
}
```

編譯：`gcc -std=c11 -Wall main.c counter.c -o app`（`.h` 不用寫在指令裡）。

- 計數器的值放在 `.c` 檔、加上 `static`，就只能透過公開的函式存取（封裝）。
- 標頭檔要有 **引入防護**，而且只放宣告，不放變數或函式的定義。
- 函式名稱加上模組前綴 `counter_`，避免和其他檔案的函式撞名（C 沒有命名空間）。

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

??? 手動模擬
雜湊表有 8 個桶子，`h(k) = k % 8`，用分離鏈結法，**新元素加在串列的最前面**。

1. 依序插入 3、11、19、4、12，每個桶子的串列長什麼樣子？
2. 用第 12 課的 `Node **pp` 技巧刪除 11：`pp` 一開始指向哪裡、最後停在哪裡？哪一個指標被改掉了？
3. 再插入 27，桶子 3 變成什麼樣子？
!!!
1. 3、11、19 都落在桶子 3，4、12 落在桶子 4。每次加在最前面：
   - 桶子 3：`19 → 11 → 3`
   - 桶子 4：`12 → 4`
2. `pp` 一開始指向 **`buckets[3]` 這個指標本身**。`*pp` 是 19，不是要刪的，`pp` 前進到 **19 這個節點的 `next` 欄位**；這時 `*pp` 是 11，找到了。執行 `*pp = dead->next`，**被改掉的是 19 的 `next`**，改成指向 3，然後 `free` 掉 11。結果：`19 → 3`。（如果刪的是 19，被改掉的就是 `buckets[3]` 本身，程式完全一樣，不用特別處理。）
3. 27 % 8 = 3，加在最前面：`27 → 19 → 3`。

??? 寫程式
為一個 **不透明** 的整數佇列寫出 `queue.h`：使用者只能透過函式建立、加入、取出、查詢是否為空、釋放，看不到內部的表示方式。取出空佇列時要讓呼叫者知道失敗。
!!!
```c
#ifndef QUEUE_H
#define QUEUE_H

#include <stdbool.h>

typedef struct Queue Queue;            /* 不完整型別：使用者不知道內容 */

Queue *queue_new(void);                /* 失敗回傳 NULL */
void   queue_free(Queue *q);           /* q 可以是 NULL */
bool   queue_push(Queue *q, int x);    /* 記憶體不足時回傳 false */
bool   queue_pop(Queue *q, int *out);  /* 空的時候回傳 false，不修改 *out */
bool   queue_empty(const Queue *q);

#endif
```

- `struct Queue` 的內容寫在 `queue.c` 裡（可以是環狀陣列或串列），以後換實作，使用者的程式不用改。
- 使用者只能拿到 `Queue *`，所以一定要用 `queue_new` / `queue_free` 成對地建立和釋放。
- C 沒有例外，失敗用 **回傳值** 表示；取出的值透過指標參數交給呼叫者。
- 只讀取的函式參數用 `const Queue *`。
