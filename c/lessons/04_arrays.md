# 04. 陣列

> 程式練習：`CL03 用指標操作陣列`（陣列 + 指標）、`CL08 動態二維矩陣`
>
> 先備知識：第 01 ~ 03 課。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 宣告與初始化 | 各種初始化寫法、沒寫到的元素是多少、算出陣列長度 |
| 第二部分 | 存取與越界 | 索引從 0 開始、越界是未定義行為、怎麼抓到越界 |
| 第三部分 | 陣列不是一般的變數 | 不能整個指定、不能用 `==` 比較、怎麼複製 |
| 第四部分 | 常見的陣列操作 | 總和 / 最大值、反轉、搜尋、插入刪除、計數陣列 |
| 第五部分 | 陣列傳給函式 | 傳的其實是位址、函式裡 `sizeof` 失效、一定要傳長度、`const` |
| 第六部分 | 二維陣列與 VLA | 列優先的記憶體配置、二維陣列當參數、可變長度陣列 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際用 `gcc -std=c11` 編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：宣告與初始化

## 1.1 陣列是什麼

**是什麼**：**同樣型別** 的元素，在記憶體中 **連續排列**。用一個名字 + 索引存取。

```c
int scores[5];                   /* 5 個 int，連續排在記憶體中 */
```

```
scores:  [ scores[0] | scores[1] | scores[2] | scores[3] | scores[4] ]
位址：     1000        1004        1008        1012        1016     （每個 int 4 bytes）
```

**為什麼需要**：要存 100 個學生的成績，不可能宣告 100 個變數 `s1, s2, ..., s100`。陣列讓你用迴圈處理所有元素。

**大小必須是正整數**，而且在 C89 / 一般情況下必須是 **編譯期常數**（C99 的 VLA 例外，見 6.4 節）：

```c
#define N 100
int a[N];                        /* ✅ 巨集常數 */
int b[10 * 2];                   /* ✅ 常數運算式 */
enum { SIZE = 8 };
int c[SIZE];                     /* ✅ enum 常數 */
```

## 1.2 初始化的各種寫法

```c
int a[5] = {1, 2, 3, 4, 5};      /* 全部給值 */
int b[5] = {1, 2};               /* 只給前兩個：其他自動是 0 → {1, 2, 0, 0, 0} */
int c[5] = {0};                  /* 全部是 0 的慣用寫法 */
int d[] = {7, 8, 9};             /* 省略大小：由初始值的個數決定 → 3 個元素 */
int e[5] = {[2] = 50, [4] = 70}; /* C99 指定初始化：{0, 0, 50, 0, 70} */

printf("%d %d %d\n", b[1], b[4], c[3]);      // 輸出：2 0 0
printf("%zu\n", sizeof d / sizeof d[0]);     // 輸出：3
printf("%d %d %d\n", e[0], e[2], e[4]);      // 輸出：0 50 70
```

**規則**：只要寫了 `= { ... }`，沒寫到的元素就是 0。

### ⚠️ 沒有初始化的區域陣列是垃圾值

```c
void f(void) {
    int x[5];                    /* ❌ 內容是垃圾值 */
    int y[5] = {0};              /* ✅ 全部是 0 */
}
int g[5];                        /* 全域陣列：自動全部是 0 */
```

### 初始值太多

```c
// int z[3] = {1, 2, 3, 4};      // ⚠️ warning: excess elements in array initializer（多的被丟掉）
```

## 1.3 算出陣列的長度

```c
int arr[] = {3, 1, 4, 1, 5, 9, 2, 6};
size_t n = sizeof arr / sizeof arr[0];       /* 整個陣列的 byte 數 ÷ 一個元素的 byte 數 */
printf("%zu %zu %zu\n", sizeof arr, sizeof arr[0], n);   // 輸出：32 4 8
```

習慣定義一個巨集：

```c
#define ARRAY_LEN(a) (sizeof(a) / sizeof((a)[0]))
```

**⚠️ 只對「真正的陣列」有效**：陣列傳進函式之後就變成指標，`sizeof` 會得到指標的大小（第五部分）。

---

# 第二部分：存取與越界

## 2.1 索引從 0 開始

長度 `n` 的陣列，合法的索引是 `0` 到 `n - 1`。

```c
int a[5] = {10, 20, 30, 40, 50};
printf("%d %d\n", a[0], a[4]);   // 第一個和最後一個 → 輸出：10 50
a[2] = 99;                        // 修改
for (int i = 0; i < 5; i++) printf("%d ", a[i]);
printf("\n");                    // 輸出：10 20 99 40 50
```

**迴圈的慣用寫法**：`for (int i = 0; i < n; i++)`，用 `<` 不用 `<=`。

## 2.2 ⚠️ 越界存取：C 不會幫你檢查

**是什麼**：讀寫 `a[-1]`、`a[n]` 或更遠的位置。C **不會檢查** 索引是否合法，直接去讀寫那個位址的記憶體 → **未定義行為**。

```c
int a[5] = {0};
a[5] = 123;                      /* ❌ 寫到陣列外面：可能改到別的變數、可能當掉、可能「看起來沒事」 */
for (int i = 0; i <= 5; i++)     /* ❌ 經典錯誤：<= 讓 i 跑到 5 */
    a[i] = 0;
```

**最可怕的是「看起來沒事」**：程式可能正常跑完、輸出正確，換一筆測資或換一台電腦才出錯。

**怎麼抓到越界**：用 **AddressSanitizer** 編譯（本平台的 `--debug`）：

```bash
gcc -g -fsanitize=address prog.c -o prog && ./prog
# ==12345==ERROR: AddressSanitizer: stack-buffer-overflow on address ...
# WRITE of size 4 at ... thread T0
#     #0 0x... in main prog.c:4       ← 出錯的行號
```

```bash
python3 judge.py test cl3 --debug
```

**規則**：寫完陣列相關的程式，一定要用 `--debug` 跑一次。

---

# 第三部分：陣列不是一般的變數

## 3.1 不能整個指定

```c
int a[3] = {1, 2, 3};
int b[3];
// b = a;                        // ❌ error: assignment to expression with array type
```

**複製陣列**：用迴圈，或 `<string.h>` 的 `memcpy`：

```c
#include <string.h>
for (int i = 0; i < 3; i++) b[i] = a[i];      /* 方法一：迴圈 */
memcpy(b, a, sizeof a);                        /* 方法二：複製 sizeof a 個 byte */
printf("%d %d %d\n", b[0], b[1], b[2]);        // 輸出：1 2 3
```

## 3.2 不能用 == 比較內容

```c
int x[3] = {1, 2, 3}, y[3] = {1, 2, 3};
printf("%d\n", x == y);                        // 輸出：0   比較的是「兩個陣列的位址」，當然不同
printf("%d\n", memcmp(x, y, sizeof x) == 0);   // 比較內容 → 輸出：1
```

`-Wall` 會警告：`comparison between two arrays`。

## 3.3 函式不能回傳陣列

```c
// int[3] make(void);             // ❌ 語法上就不允許
```

要「回傳」陣列，有三種做法：
1. 呼叫者準備好陣列，傳進去讓函式填（最常見，5.1 節）。
2. 把陣列包在 `struct` 裡回傳（第 08 課）。
3. 用 `malloc` 配置，回傳指標（第 07 課）。

---

# 第四部分：常見的陣列操作

## 4.1 總和、最大值、平均

```c
int a[] = {3, 8, 1, 9, 4};
int n = 5, sum = 0, mx = a[0], mx_idx = 0;
for (int i = 0; i < n; i++) {
    sum += a[i];
    if (a[i] > mx) { mx = a[i]; mx_idx = i; }
}
printf("%d %d %d %.2f\n", sum, mx, mx_idx, (double)sum / n);   // 輸出：25 9 3 5.00
```

**常見錯誤**：最大值的初值設成 0。陣列全是負數時答案就錯了。**用第一個元素當初值。**

## 4.2 反轉

```c
int r[] = {1, 2, 3, 4, 5};
int len = 5;
for (int i = 0, j = len - 1; i < j; i++, j--) {   /* 兩個索引往中間走 */
    int t = r[i]; r[i] = r[j]; r[j] = t;
}
for (int i = 0; i < len; i++) printf("%d ", r[i]);
printf("\n");                                     // 輸出：5 4 3 2 1
```

## 4.3 搜尋

```c
int find(const int a[], int n, int x) {
    for (int i = 0; i < n; i++)
        if (a[i] == x) return i;
    return -1;                                    /* 找不到：回傳一個不可能的索引 */
}
int data[] = {5, 3, 8, 3};
printf("%d %d\n", find(data, 4, 3), find(data, 4, 7));   // 輸出：1 -1
```

## 4.4 插入與刪除：要搬移元素

陣列的大小是固定的，「插入」其實是 **把後面的元素往後搬一格**：

```c
int a[10] = {10, 20, 30, 40};
int n = 4;                                /* 目前使用了 4 格 */
int pos = 1, val = 15;
for (int i = n; i > pos; i--) a[i] = a[i - 1];   /* 從最後面開始往後搬（反過來會覆蓋掉資料！） */
a[pos] = val;
n++;
for (int i = 0; i < n; i++) printf("%d ", a[i]);
printf("\n");                             // 輸出：10 15 20 30 40

/* 刪除位置 2：後面的往前搬 */
for (int i = 2; i < n - 1; i++) a[i] = a[i + 1];
n--;
for (int i = 0; i < n; i++) printf("%d ", a[i]);
printf("\n");                             // 輸出：10 15 30 40
```

插入和刪除都是 `O(n)`。需要大小可變的陣列，第 07 課會用 `realloc` 做出「動態陣列」（`CL04`）。

## 4.5 計數陣列 (Counting Array)

**是什麼**：用 **值當索引**，統計每個值出現幾次。值的範圍不大時非常好用。

```c
int votes[] = {2, 0, 2, 1, 2, 0};
int count[3] = {0};                       /* count[k]：k 號候選人的票數 */
for (int i = 0; i < 6; i++) count[votes[i]]++;
printf("%d %d %d\n", count[0], count[1], count[2]);   // 輸出：2 1 3

/* 字母頻率 */
const char *s = "banana";
int freq[26] = {0};
for (int i = 0; s[i] != '\0'; i++) freq[s[i] - 'a']++;
printf("a=%d n=%d b=%d\n", freq[0], freq['n' - 'a'], freq[1]);   // 輸出：a=3 n=2 b=1
```

---

# 第五部分：陣列傳給函式

## 5.1 傳的其實是位址

**是什麼**：陣列當參數時，**不會複製整個陣列**，而是傳 **第一個元素的位址**。所以：
- 函式 **可以修改** 呼叫者的陣列。
- 函式 **不知道** 陣列有多長，一定要另外傳長度。

```c
void double_all(int arr[], int n) {       /* int arr[] 其實就是 int *arr（第 05 課） */
    for (int i = 0; i < n; i++) arr[i] *= 2;
}
int v[3] = {1, 2, 3};
double_all(v, 3);
printf("%d %d %d\n", v[0], v[1], v[2]);   // 輸出：2 4 6（呼叫者的陣列被改了）
```

**為什麼這樣設計？** 陣列可能很大（例如一百萬個元素），每次呼叫都複製一份太浪費。

## 5.2 ⚠️ 函式裡的 sizeof 失效

```c
void print_size(int arr[]) {
    printf("%zu\n", sizeof arr);          /* arr 其實是指標 → 指標的大小 */
}
int big[100];
printf("%zu\n", sizeof big);              // 輸出：400
print_size(big);                          // 輸出：8（64 位元系統的指標大小）
```

GCC 會警告：`'sizeof' on array function parameter 'arr' will return size of 'int *'`。

**規則**：**陣列一定要和長度一起傳**：`void f(int arr[], int n)`。

`int arr[100]` 寫成參數時，那個 100 會被 **完全忽略**：`void f(int arr[100])` 和 `void f(int *arr)` 完全一樣。

## 5.3 const：保證不修改

只讀取、不修改陣列的函式，參數加上 `const`：

```c
int sum(const int arr[], int n) {
    int s = 0;
    for (int i = 0; i < n; i++) s += arr[i];
    // arr[0] = 0;                         // ❌ error: assignment of read-only location '*arr'
    return s;
}
```

**好處**：
1. 呼叫者一看就知道「這個函式不會改我的陣列」。
2. 不小心修改時，編譯器會擋下來。

---

# 第六部分：二維陣列與 VLA

## 6.1 二維陣列

```c
int m[2][3] = {
    {1, 2, 3},                            /* 第 0 列 */
    {4, 5, 6},                            /* 第 1 列 */
};
printf("%d %d\n", m[0][2], m[1][0]);      // 輸出：3 4
for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 3; j++) printf("%d ", m[i][j]);
    printf("\n");
}
// 輸出：
// 1 2 3
// 4 5 6
```

`int m[2][3]` 是「**2 個元素的陣列，每個元素是 3 個 int 的陣列**」。

## 6.2 🔍 列優先 (Row-major) 的記憶體配置

二維陣列在記憶體中還是 **一整條連續的空間**，一列接著一列：

```
m[0][0] m[0][1] m[0][2] m[1][0] m[1][1] m[1][2]
   1       2       3       4       5       6
```

```c
int *flat = &m[0][0];
for (int k = 0; k < 6; k++) printf("%d ", flat[k]);
printf("\n");                             // 輸出：1 2 3 4 5 6
printf("%zu %zu\n", sizeof m, sizeof m[0]);   // 整個陣列、一列 → 輸出：24 12
```

`m[i][j]` 在第 `i * 3 + j` 個位置。所以 **走訪時外層迴圈跑列、內層跑行**，記憶體是依序存取的，比較快（快取友善）。

## 6.3 二維陣列當參數：一定要寫行數

```c
int total(int mat[][3], int rows) {       /* 第二維（行數）不能省略 */
    int s = 0;
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < 3; j++) s += mat[i][j];
    return s;
}
printf("%d\n", total(m, 2));              // 輸出：21
```

**為什麼第二維不能省略？** 編譯器要算 `mat[i][j]` 的位置 = `i * 行數 + j`，所以一定要知道行數。

這很不方便（行數被寫死了）。行數要到執行時才知道的話，用 VLA 參數（下一節）或動態配置（第 07 課、`CL08`）。

## 6.4 VLA：可變長度陣列 (C99)

**是什麼**：陣列的大小可以是 **執行時才知道的變數**。

```c
int n;
scanf("%d", &n);                          // 輸入：4
int sq[n];                                /* 大小由 n 決定 */
for (int i = 0; i < n; i++) sq[i] = i * i;
printf("%d %zu\n", sq[n - 1], sizeof sq);   // 輸出：9 16（VLA 的 sizeof 在執行時計算）
```

**VLA 參數**讓二維陣列的函式更通用：

```c
int total2(int rows, int cols, int mat[rows][cols]) {   /* rows、cols 要寫在 mat 前面 */
    int s = 0;
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++) s += mat[i][j];
    return s;
}
printf("%d\n", total2(2, 3, m));          // 輸出：21
```

**⚠️ VLA 的限制與風險**：
- 放在 **堆疊** 上：`n` 是一百萬就會堆疊溢位，而且 **沒有任何錯誤回報**。
- 不能用 `= {0}` 初始化。
- C11 把 VLA 改成「編譯器可以選擇不支援」的功能（MSVC 就不支援）。

**規則**：大小不確定、或可能很大的陣列，用 `malloc`（第 07 課）。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 陣列 | Array | 同型別元素連續排列 | 1.1 |
| 索引 | Index | 從 0 開始的位置編號 | 2.1 |
| 指定初始化 | Designated Initializer | `[2] = 50` 指定某個元素的初值（C99） | 1.2 |
| 越界 | Out of Bounds | 存取 `[0, n)` 以外的元素，未定義行為 | 2.2 |
| AddressSanitizer | ASan | 執行時偵測越界、記憶體錯誤的工具 | 2.2 |
| 計數陣列 | Counting Array | 用值當索引統計次數 | 4.5 |
| 陣列退化 | Array Decay | 陣列傳給函式時變成指向第一個元素的指標 | 5.1 |
| 列優先 | Row-major | 二維陣列一列接一列存放 | 6.2 |
| 可變長度陣列 | VLA (Variable Length Array) | 大小是執行時變數的陣列（C99） | 6.4 |

---

# 習題

### 題 1：預測輸出

```c
int a[6] = {4, [3] = 7, 1};
for (int i = 0; i < 6; i++) printf("%d ", a[i]);
```

### 題 2：找出所有錯誤

```c
int main(void) {
    int a[5] = {1, 2, 3, 4, 5};
    int b[5];
    b = a;
    for (int i = 1; i <= 5; i++) printf("%d\n", b[i]);
}
```

### 題 3：預測輸出（64 位元系統）

```c
void f(int x[10]) { printf("%zu ", sizeof x); }
int main(void) {
    int arr[10];
    printf("%zu ", sizeof arr);
    f(arr);
    printf("%zu\n", sizeof arr / sizeof arr[0]);
}
```

### 題 4：寫一個函式 `int count_greater(const int a[], int n, int x)`，回傳陣列中大於 `x` 的元素個數。

### 題 5：預測輸出

```c
int m[3][2] = {{1, 2}, {3, 4}, {5, 6}};
int *p = &m[0][0];
printf("%d %d %d\n", m[1][1], p[3], p[2 * 2 + 1]);
```

### 題 6：下面的插入程式有什麼問題？

```c
/* 在 pos 插入 val，n 是目前的元素個數 */
for (int i = pos; i < n; i++) a[i + 1] = a[i];
a[pos] = val;
n++;
```

### 題 7：寫一個函式，把長度 `n` 的陣列中所有的 0 移到最後面，其他元素保持原本的順序（例如 `0 1 0 3 12` → `1 3 12 0 0`），只能用 `O(1)` 的額外空間。

---

# 習題解答

**題 1**：`4 0 0 7 1 0`。`a[0] = 4`；`[3] = 7` 指定 `a[3]`；之後的 `1` 接著指定 `a[4]`；其他沒寫到的是 0。

**題 2**：
- `b = a;` 不能整個指定陣列（編譯錯誤）。用迴圈或 `memcpy(b, a, sizeof a);`。
- 迴圈 `i = 1; i <= 5` 跳過了 `b[0]`，而且 `b[5]` 越界。應該是 `for (int i = 0; i < 5; i++)`。

**題 3**：`40 8 10`。`main` 裡的 `arr` 是真正的陣列（40 bytes）；`f` 的參數 `x` 雖然寫成 `int x[10]`，其實是指標（8 bytes）。

**題 4**：

```c
int count_greater(const int a[], int n, int x) {
    int c = 0;
    for (int i = 0; i < n; i++)
        if (a[i] > x) c++;
    return c;
}
```

**題 5**：`4 4 6`。列優先：`m[1][1]` 是第 `1 * 2 + 1 = 3` 個 → 4；`p[3]` 也是第 3 個 → 4；`p[5]` 是最後一個 → 6。

**題 6**：從前面往後搬會 **覆蓋** 資料：`a[pos+1] = a[pos]` 之後，下一輪 `a[pos+2] = a[pos+1]` 拿到的已經是被覆蓋的值，結果後面全部變成 `a[pos]`。要 **從最後面往前** 搬：`for (int i = n; i > pos; i--) a[i] = a[i - 1];`。另外要確定陣列還有空間（`n < 陣列大小`）。

**題 7**：用一個「寫入位置」`w`，把非 0 的元素依序往前寫，最後把剩下的位置補 0：

```c
void move_zeros(int a[], int n) {
    int w = 0;
    for (int i = 0; i < n; i++)
        if (a[i] != 0) a[w++] = a[i];
    while (w < n) a[w++] = 0;
}
```

時間 `O(n)`，額外空間 `O(1)`。這個「讀寫兩個索引」的技巧在 `CL09` 的 `filter_keep` 也會用到。
