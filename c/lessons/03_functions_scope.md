# 03. 函式與變數的生命

> 程式練習：本課沒有獨立的評測題；之後每一題都要寫函式。
>
> 先備知識：第 01、02 課。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 定義與呼叫 | 函式的各部分、`void`、函式原型、為什麼要先宣告 |
| 第二部分 | 傳值 | 參數是複製品、為什麼 `swap` 寫不出來、怎麼「回傳好幾個值」 |
| 第三部分 | 遞迴 | 終止條件、呼叫堆疊、堆疊溢位、遞迴 vs 迴圈 |
| 第四部分 | 作用域與生命週期 | 區域 / 全域變數、遮蔽、`static` 區域變數、`static` 全域、`extern` |
| 第五部分 | 可變參數 | `printf` 怎麼接受任意個參數、`<stdarg.h>` |
| 第六部分 | 常用的標準函式 | `<math.h>`、`<stdlib.h>`、`main` 的參數與回傳值 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際用 `gcc -std=c11` 編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：定義與呼叫

## 1.1 函式的各部分

```c
int max_of(int a, int b) {       /* 回傳型別  名稱  (參數列) */
    if (a > b) return a;         /* return：結束函式，並把值交給呼叫者 */
    return b;
}

int main(void) {
    int m = max_of(3, 8);        /* 呼叫：引數 (argument) 3、8 被複製給參數 (parameter) a、b */
    printf("%d\n", m);           // 輸出：8
}
```

| 名詞 | 意思 |
|---|---|
| 回傳型別 | 函式交回來的值的型別；不回傳東西就寫 `void` |
| 參數 (parameter) | 函式定義裡的變數 `a`、`b` |
| 引數 (argument) | 呼叫時實際傳進去的值 `3`、`8` |
| `return` | 結束函式；非 `void` 函式要回傳一個值 |

**為什麼需要函式**：
- **重複使用**：同樣的邏輯寫一次，到處呼叫。
- **拆解問題**：一個大問題拆成好幾個小函式，每個只做一件事，容易讀也容易測試。
- **給邏輯取名字**：`is_prime(n)` 比一堆迴圈好懂。

## 1.2 void：沒有回傳值、沒有參數

```c
void print_line(int n) {         /* 不回傳值 */
    for (int i = 0; i < n; i++) putchar('-');
    putchar('\n');
    /* 走到結尾自動結束；也可以寫 return;（不帶值）提早結束 */
}

int read_positive(void) {        /* 沒有參數：寫 (void) */
    int x;
    while (scanf("%d", &x) == 1 && x <= 0) { }
    return x;
}
print_line(5);                   // 輸出：-----
```

**`f()` 和 `f(void)` 在 C 裡不一樣**（C++ 裡一樣）：
- `int f(void);` —— 明確說「沒有參數」，呼叫 `f(1)` 會編譯錯誤。
- `int f();` —— 舊式寫法，意思是「參數不確定」，呼叫 `f(1, 2, 3)` 編譯器不會檢查。（C23 改成和 `(void)` 相同。）

**規則：沒有參數就寫 `(void)`。**

## 1.3 ⚠️ 非 void 函式一定要回傳值

```c
int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    /* ❌ x == 0 時走到結尾沒有 return：回傳值是垃圾（未定義行為） */
}
```

`-Wall` 會警告：`control reaches end of non-void function`。

## 1.4 函式原型（宣告）：先宣告再使用

**問題**：C 編譯器 **由上往下** 讀程式。呼叫一個「還沒看過」的函式會怎樣？

```c
int main(void) {
    printf("%d\n", square(5));   /* ❌ 編譯器還不知道 square 是什麼 */
}
int square(int x) { return x * x; }
```

```
warning: implicit declaration of function 'square' [-Wimplicit-function-declaration]
```

GCC 13 只給 **警告**，而且程式可能「碰巧」能動 —— 編譯器 **猜** 它是「回傳 `int`、參數不檢查」的函式（這是 C89 的舊規則）。猜錯的話（例如函式其實回傳 `double`）結果就是垃圾。從 C99 起這種寫法已經不合法，**GCC 14 起直接是編譯錯誤**。看到這個警告一定要修。

**解法**：在使用前寫 **函式原型 (prototype)**：只有「回傳型別、名稱、參數型別」，用分號結尾。

```c
int square(int x);               /* 原型（宣告）：告訴編譯器「有這個函式，長這樣」 */

int main(void) {
    printf("%d\n", square(5));   // 輸出：25
}

int square(int x) {              /* 定義：真正的實作 */
    return x * x;
}
```

原型裡的參數名稱可以省略：`int square(int);`。

**為什麼需要原型？**
1. 函式之間互相呼叫（`a` 呼叫 `b`、`b` 又呼叫 `a`）時，不可能兩個都寫在前面。
2. 多檔案程式：標頭檔 `.h` 裡放的就是原型（第 11 課）。`#include <stdio.h>` 就是把 `printf` 的原型貼進來。
3. 編譯器靠原型 **檢查** 引數的個數和型別，必要時自動轉換。

---

# 第二部分：傳值 (Pass by Value)

## 2.1 參數是複製品

**是什麼**：C 的函式 **只有傳值**：呼叫時，引數的 **值** 被複製一份給參數。函式裡修改參數，**不會** 影響呼叫者的變數。

```c
void try_change(int x) {
    x = 100;                     /* 改的是複製品 */
    printf("函式裡 x = %d\n", x);
}
int main(void) {
    int a = 5;
    try_change(a);               // 輸出：函式裡 x = 100
    printf("a = %d\n", a);       // 輸出：a = 5（沒有改變）
}
```

**比喻**：影印一份文件給同事，同事在影印本上塗改，你的原稿不會變。

## 2.2 為什麼 swap 寫不出來？

```c
void bad_swap(int a, int b) {    /* a、b 是複製品 */
    int t = a; a = b; b = t;     /* 只交換了複製品 */
}
int x = 1, y = 2;
bad_swap(x, y);
printf("%d %d\n", x, y);         // 輸出：1 2（沒有交換）
```

**解法：傳指標**（第 05 課的主角）。把變數的 **位址** 傳進去，函式透過位址修改原本的變數：

```c
void swap(int *a, int *b) {      /* a、b 是「位址」 */
    int t = *a;                  /* *a：位址 a 上的那個變數 */
    *a = *b;
    *b = t;
}
swap(&x, &y);                    /* 傳 x、y 的位址 */
printf("%d %d\n", x, y);         // 輸出：2 1
```

這就是 `scanf("%d", &x)` 要加 `&` 的原因（第 01 課）。

## 2.3 怎麼「回傳好幾個值」？

`return` 只能回傳一個值。需要好幾個結果時有兩種做法：

**做法 1：輸出參數 (output parameter)** —— 傳指標進去，函式把結果寫進去：

```c
void div_mod(int a, int b, int *q, int *r) {
    *q = a / b;
    *r = a % b;
}
int q, r;
div_mod(17, 5, &q, &r);
printf("%d %d\n", q, r);         // 輸出：3 2
```

**做法 2：回傳 struct**（第 08 課）：

```c
typedef struct { int q, r; } DivResult;
DivResult div_mod2(int a, int b) {
    DivResult res = {a / b, a % b};
    return res;                  /* struct 可以整個回傳（會複製） */
}
DivResult d = div_mod2(17, 5);
printf("%d %d\n", d.q, d.r);     // 輸出：3 2
```

**常見的 C 慣例**：回傳值表示 **成功或失敗**，真正的結果用輸出參數傳回：

```c
int parse_age(const char *s, int *out) {   /* 成功回傳 1，失敗回傳 0 */
    int v;
    if (sscanf(s, "%d", &v) != 1 || v < 0) return 0;
    *out = v;
    return 1;
}
int age;
if (parse_age("25", &age)) printf("age = %d\n", age);   // 輸出：age = 25
if (!parse_age("abc", &age)) printf("格式錯誤\n");       // 輸出：格式錯誤
```

## 2.4 陣列參數例外：看起來像傳參考

陣列傳給函式時，傳的是 **第一個元素的位址**（第 04、05 課），所以函式 **可以** 修改呼叫者的陣列：

```c
void fill_zero(int arr[], int n) {
    for (int i = 0; i < n; i++) arr[i] = 0;
}
int a[3] = {1, 2, 3};
fill_zero(a, 3);
printf("%d %d %d\n", a[0], a[1], a[2]);   // 輸出：0 0 0
```

這其實還是「傳值」—— 傳的值是 **位址**。第 04 課詳細說明。

---

# 第三部分：遞迴 (Recursion)

## 3.1 函式呼叫自己

**是什麼**：函式在自己的本體裡呼叫自己。把問題拆成「**更小的同一個問題**」。

每個遞迴都需要：
1. **終止條件 (base case)**：最小的問題直接回答，不再遞迴。
2. **遞迴步驟**：把問題縮小，呼叫自己。

```c
long long factorial(int n) {
    if (n <= 1) return 1;                  /* 終止條件 */
    return n * factorial(n - 1);           /* n! = n × (n-1)! */
}
printf("%lld\n", factorial(20));           // 輸出：2432902008176640000
```

```c
/* 最大公因數：輾轉相除法 */
int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}
printf("%d\n", gcd(48, 18));               // 輸出：6

/* 把整數的每一位數字倒著印出來 */
void print_digits_reverse(int n) {
    printf("%d", n % 10);
    if (n >= 10) print_digits_reverse(n / 10);
}
print_digits_reverse(1234);                // 輸出：4321
```

## 3.2 🔍 呼叫堆疊 (Call Stack)

每次呼叫函式，系統會在 **堆疊 (stack)** 上配置一塊空間（**堆疊框架 stack frame**），放這次呼叫的參數、區域變數、返回位址。函式結束時這塊空間就被收回。

```
factorial(3) 的過程：

呼叫 factorial(3)          ┌────────────┐
  呼叫 factorial(2)        │ n = 1      │ ← 最上面：正在執行
    呼叫 factorial(1)      │ n = 2      │
    回傳 1                 │ n = 3      │
  回傳 2 × 1 = 2           │ main       │
回傳 3 × 2 = 6             └────────────┘
```

**遞迴的每一層都有自己的 `n`**，互不干擾。

## 3.3 ⚠️ 堆疊溢位 (Stack Overflow)

堆疊的大小有限（Linux 預設約 8 MB，Windows 1 MB）。遞迴太深、或忘了終止條件，堆疊會用完 → 程式當掉（Segmentation fault）。

```c
int forever(int n) { return forever(n + 1); }   /* ❌ 沒有終止條件 */

long long sum_to(int n) { return n == 0 ? 0 : n + sum_to(n - 1); }
// sum_to(100000) 沒問題；sum_to(100000000) 會堆疊溢位
```

**規則**：遞迴深度可能很大（例如 10⁶）時，改用迴圈。

## 3.4 遞迴 vs 迴圈

```c
/* 費氏數列的「天真」遞迴：每次呼叫分成兩個，總呼叫次數是指數級 */
long long fib_slow(int n) { return n < 2 ? n : fib_slow(n - 1) + fib_slow(n - 2); }

/* 迴圈版本：O(n) */
long long fib_fast(int n) {
    long long a = 0, b = 1;
    for (int i = 0; i < n; i++) { long long t = a + b; a = b; b = t; }
    return a;
}
printf("%lld %lld\n", fib_slow(30), fib_fast(90));   // 輸出：832040 2880067194370816120
```

`fib_slow(30)` 呼叫了一百多萬次；`fib_slow(50)` 要跑好幾分鐘。遞迴寫起來直覺，但要注意 **重複計算** 和 **深度**。

---

# 第四部分：作用域與生命週期

兩個不同的觀念：
- **作用域 (scope)**：程式碼的 **哪些地方** 看得到這個名字。
- **生命週期 (storage duration)**：變數 **什麼時候** 存在於記憶體中。

## 4.1 區域變數：區塊作用域、自動生命週期

**是什麼**：宣告在 `{ }` 裡面的變數。
- 只在那個區塊裡看得到。
- 進入區塊時建立、離開區塊時消失（**自動 automatic**）。
- 每次進入都是新的一份，**沒有初始化就是垃圾值**。

```c
void demo(void) {
    int x = 1;
    {
        int y = 2;                /* y 只在這個內層區塊裡 */
        printf("%d %d\n", x, y);  // 輸出：1 2
    }
    // printf("%d\n", y);         // ❌ error: 'y' undeclared
}
```

### 遮蔽 (Shadowing)

內層區塊宣告了和外層同名的變數，內層的會 **遮住** 外層的：

```c
int value = 1;
{
    int value = 2;                /* 新的變數，遮住外面的 value */
    printf("%d\n", value);        // 輸出：2
}
printf("%d\n", value);            // 輸出：1（外面的沒被改到）
```

這很容易造成「以為改了外面的變數，其實沒有」的 bug。`gcc -Wshadow` 會警告。

## 4.2 全域變數：檔案作用域、靜態生命週期

**是什麼**：宣告在所有函式外面的變數。
- 從宣告的地方到檔案結尾都看得到。
- 程式開始時就存在，直到程式結束（**靜態 static storage duration**）。
- **沒有初始化時自動是 0**。

```c
int counter;                      /* 全域：自動初始化為 0 */
void hit(void) { counter++; }
int main(void) {
    hit(); hit(); hit();
    printf("%d\n", counter);      // 輸出：3
}
```

**全域變數的問題**：任何函式都能修改它，程式一大就很難追蹤「是誰改的」。**能用參數傳就用參數傳**。

**例外：很大的陣列放全域**。區域變數放在堆疊上（只有幾 MB），`int arr[10000000];`（40 MB）放在函式裡會堆疊溢位；放在全域就沒問題（評測題常這樣做）。

## 4.3 static 區域變數：保留上次的值

**是什麼**：在函式裡的變數前面加 `static`：
- 作用域還是只在函式裡。
- 但生命週期變成 **整個程式**：函式結束後不會消失，**下次呼叫時還保留上次的值**。
- 只在 **第一次** 執行到時初始化（沒有初始值就是 0）。

```c
int next_id(void) {
    static int id = 0;            /* 只初始化一次 */
    id++;
    return id;
}
printf("%d %d %d\n", next_id(), next_id(), next_id());   /* 參數的計算順序沒有規定！ */
int a = next_id(), b = next_id();
printf("%d %d\n", a, b);          // 輸出：4 5（前面已經呼叫過 3 次）
```

（第一個 `printf` 印出的三個數字順序取決於編譯器，所以不要這樣寫 —— 第 02 課「求值順序」。）

**用途**：計數器、快取、「只做一次」的初始化。

## 4.4 static 全域變數 / 函式：只有這個檔案看得到

`static` 用在 **函式外面** 時，意思完全不同：**限制這個名字只在目前的 `.c` 檔案裡看得到**（內部連結 internal linkage）。

```c
static int helper_count = 0;      /* 其他 .c 檔看不到 */
static int helper(int x) {        /* 其他 .c 檔不能呼叫 */
    return x * 2;
}
```

**規則**：只在這個檔案裡用的輔助函式和全域變數，一律加 `static`，避免和其他檔案撞名（第 11 課）。

## 4.5 extern：使用別的檔案定義的變數

```c
/* a.c */
int shared = 42;                  /* 定義 */

/* b.c */
extern int shared;                /* 宣告：「shared 在別的地方定義」 */
void show(void) { printf("%d\n", shared); }
```

第 11 課會完整說明多檔案程式。

## 4.6 整理

| 寫在哪裡 | 寫法 | 作用域 | 生命週期 | 沒有初始化時 |
|---|---|---|---|---|
| 函式裡 | `int x;` | 區塊內 | 自動（離開區塊就消失） | 垃圾值 |
| 函式裡 | `static int x;` | 區塊內 | 整個程式 | 0 |
| 函式外 | `int x;` | 檔案（其他檔案用 `extern` 也看得到） | 整個程式 | 0 |
| 函式外 | `static int x;` | 只有這個檔案 | 整個程式 | 0 |

---

# 第五部分：可變參數 (Variadic Functions)

**是什麼**：參數個數不固定的函式，例如 `printf`。宣告時用 `...`：

```c
int printf(const char *format, ...);
```

**自己寫一個**：用 `<stdarg.h>`

```c
#include <stdarg.h>

int sum_ints(int count, ...) {       /* 第一個參數告訴我們後面有幾個 */
    va_list ap;
    va_start(ap, count);             /* 從 count 後面開始讀 */
    int total = 0;
    for (int i = 0; i < count; i++)
        total += va_arg(ap, int);    /* 讀下一個參數，型別是 int */
    va_end(ap);
    return total;
}
printf("%d %d\n", sum_ints(3, 10, 20, 30), sum_ints(0));   // 輸出：60 0
```

**為什麼 `printf` 需要格式字串？** 函式本身 **不知道** 傳進來幾個參數、各是什麼型別。`printf` 靠格式字串裡的 `%d`、`%s` 才知道要用 `va_arg(ap, int)` 還是 `va_arg(ap, char *)`。這也是為什麼格式寫錯就會讀到垃圾（第 01 課 3.5）。

**🔍 預設引數提升**：傳給 `...` 的 `char`、`short` 會被提升成 `int`，`float` 被提升成 `double`。所以 `va_arg` 只能寫 `int` 和 `double`，不能寫 `char` 或 `float`。這也是 `printf` 的 `%f` 同時能印 `float` 和 `double` 的原因。

---

# 第六部分：常用的標準函式

## 6.1 <math.h>

Linux 上用到 `<math.h>` 要加 `-lm` 連結（本平台會自動加）。

| 函式 | 意思 | 範例 | 結果 |
|---|---|---|---|
| `sqrt(x)` | 平方根 | `sqrt(2.0)` | `1.414214` |
| `pow(x, y)` | x 的 y 次方 | `pow(2, 10)` | `1024.000000` |
| `fabs(x)` | 浮點數的絕對值 | `fabs(-2.5)` | `2.5` |
| `floor(x)` / `ceil(x)` | 往下 / 往上取整 | `floor(-2.5)`、`ceil(-2.5)` | `-3`、`-2` |
| `round(x)` | 四捨五入（.5 遠離 0） | `round(-2.5)` | `-3` |
| `sin`、`cos`、`log`、`exp`…… | 三角、自然對數、指數 | `log(exp(1.0))` | `1` |

```c
#include <math.h>
printf("%f %f %.1f\n", sqrt(2.0), pow(2, 10), fabs(-2.5));   // 輸出：1.414214 1024.000000 2.5
printf("%.0f %.0f %.0f\n", floor(-2.5), ceil(-2.5), round(-2.5));   // 輸出：-3 -2 -3
```

**注意**：這些函式都是 `double`。整數的次方 **不要用 `pow`**：`pow` 用浮點數計算，結果可能是 `999.9999999` 轉成整數變成 999。整數次方自己用迴圈乘。

整數的絕對值用 `<stdlib.h>` 的 `abs`（`int`）、`llabs`（`long long`）。

## 6.2 <stdlib.h>

| 函式 | 意思 |
|---|---|
| `abs(x)`、`llabs(x)` | 整數絕對值 |
| `atoi(s)`、`strtol(s, &end, 10)` | 字串轉整數（`strtol` 能偵測錯誤，第 06 課） |
| `rand()`、`srand(seed)` | 亂數 |
| `exit(code)` | 立刻結束程式 |
| `malloc`、`free`…… | 動態記憶體（第 07 課） |
| `qsort`、`bsearch` | 排序、二分搜尋（第 09 課） |

```c
#include <stdlib.h>
srand(42);                         /* 設定亂數種子：同樣的種子，每次執行得到同樣的序列 */
int dice = rand() % 6 + 1;         /* 1 ~ 6（rand() % n 的分佈有一點點偏差，練習用沒問題） */
printf("%d\n", dice >= 1 && dice <= 6);   // 輸出：1
```

## 6.3 main 的參數與回傳值

```c
int main(int argc, char *argv[]) {   /* argc：參數個數（含程式名稱）；argv：參數字串的陣列 */
    for (int i = 0; i < argc; i++)
        printf("argv[%d] = %s\n", i, argv[i]);
    return 0;                        /* 0 代表成功；非 0 代表失敗 */
}
```

```bash
$ ./prog hello 42
argv[0] = ./prog
argv[1] = hello
argv[2] = 42
```

- `return` 的值會變成程式的 **結束碼 (exit code)**；評測系統看到非 0 會判定為 RE。
- 在任何地方呼叫 `exit(1);`（`<stdlib.h>`）也能立刻結束程式。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 參數 / 引數 | Parameter / Argument | 函式定義裡的變數 / 呼叫時給的值 | 1.1 |
| 函式原型 | Function Prototype | 只有宣告、沒有本體的函式，讓編譯器先認識它 | 1.4 |
| 傳值 | Pass by Value | 參數是引數的複製品 | 2.1 |
| 輸出參數 | Output Parameter | 傳指標進去，讓函式把結果寫回來 | 2.3 |
| 遞迴 | Recursion | 函式呼叫自己 | 3.1 |
| 終止條件 | Base Case | 遞迴不再呼叫自己的情況 | 3.1 |
| 呼叫堆疊 / 堆疊框架 | Call Stack / Stack Frame | 每次呼叫配置的空間 | 3.2 |
| 堆疊溢位 | Stack Overflow | 遞迴太深，堆疊用完 | 3.3 |
| 作用域 | Scope | 名字在哪裡看得到 | 4 |
| 生命週期 | Storage Duration | 變數什麼時候存在 | 4 |
| 遮蔽 | Shadowing | 內層同名變數遮住外層的 | 4.1 |
| 靜態區域變數 | static Local Variable | 函式結束後還保留值的變數 | 4.3 |
| 內部連結 | Internal Linkage | static 全域：只有這個檔案看得到 | 4.4 |
| 可變參數 | Variadic Function | 參數個數不固定，`...` | 5 |
| 結束碼 | Exit Code | main 的回傳值，0 代表成功 | 6.3 |

---

# 習題

### 題 1：預測輸出

```c
void f(int x) { x = x * 2; printf("%d ", x); }
int main(void) {
    int a = 5;
    f(a);
    f(a);
    printf("%d\n", a);
}
```

### 題 2：預測輸出

```c
int counter(void) {
    static int c = 10;
    int d = 10;
    c++; d++;
    return c * 100 + d;
}
int main(void) {
    int a = counter();
    int b = counter();
    printf("%d %d\n", a, b);
}
```

### 題 3：這個程式哪裡會出錯？

```c
#include <stdio.h>
int main(void) {
    printf("%d\n", triple(4));
}
int triple(int x) { return 3 * x; }
```

### 題 4：寫出遞迴函式 `int power(int b, int e)` 計算 bᵉ（e ≥ 0），並說明它的終止條件。

### 題 5：預測輸出

```c
int x = 1;
void show(void) { printf("%d ", x); }
int main(void) {
    int x = 2;
    show();
    {
        int x = 3;
        show();
        printf("%d ", x);
    }
    printf("%d\n", x);
}
```

### 題 6：寫一個函式 `void min_max(const int a[], int n, int *mn, int *mx)`，一次找出陣列的最小值和最大值。

### 題 7：下面的函式有什麼問題？

```c
int is_even(int n) {
    if (n % 2 == 0) return 1;
    else if (n % 2 == 1) return 0;
}
```

### 題 8：`sum_ints(3, 1, 2)`（第五部分的函式）會發生什麼事？

---

# 習題解答

**題 1**：`10 10 5`。每次呼叫 `f`，`x` 都是 `a` 的複製品（5），乘 2 是 10；`a` 本身沒有改變。

**題 2**：`1111 1211`。`c` 是 `static`，只初始化一次：第一次呼叫變成 11、第二次 12；`d` 是一般區域變數，每次都重新初始化為 10，再加 1 是 11。

**題 3**：`main` 呼叫 `triple` 時，編譯器還沒看過它的宣告 → `implicit declaration of function 'triple'`（GCC 13 是警告、GCC 14 起是錯誤）。這個例子碰巧能動（`triple` 剛好回傳 `int`），但這是不合法的寫法。修正：在 `main` 前面加上原型 `int triple(int x);`，或把 `triple` 的定義搬到 `main` 前面。

**題 4**：

```c
int power(int b, int e) {
    if (e == 0) return 1;              /* 終止條件：任何數的 0 次方是 1 */
    return b * power(b, e - 1);        /* bᵉ = b × bᵉ⁻¹ */
}
```

（更快的版本：`e` 是偶數時 `power(b*b, e/2)`，深度只有 `log e`。）

**題 5**：`1 1 3 2`。`show` 裡的 `x` 是 **全域** 的 `x`（1），不管呼叫它的地方有沒有同名的區域變數 —— 作用域是看「程式碼寫在哪裡」，不是「從哪裡被呼叫」。`main` 裡內層區塊的 `x` 是 3，外層是 2。

**題 6**：

```c
void min_max(const int a[], int n, int *mn, int *mx) {
    *mn = *mx = a[0];
    for (int i = 1; i < n; i++) {
        if (a[i] < *mn) *mn = a[i];
        if (a[i] > *mx) *mx = a[i];
    }
}
/* 使用：int lo, hi; min_max(arr, n, &lo, &hi); */
```

**題 7**：`n` 是負的奇數時，`n % 2` 是 **-1**（第 02 課），兩個條件都不成立，走到函式結尾沒有 `return` → 回傳垃圾值（未定義行為）。修正：`return n % 2 == 0;` 一行就好。

**題 8**：`count` 說有 3 個，但只傳了 2 個，`va_arg` 第三次會讀到不存在的參數 → **未定義行為**（讀到垃圾值）。可變參數函式 **沒辦法檢查** 參數的個數，所以呼叫者一定要給對。
