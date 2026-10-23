# 09. 函式指標

> 程式練習：`CL06 學生成績排名`（`qsort` / `bsearch`）、`CL09 函式指標與指令表`
>
> 先備知識：第 05 課「指標」（特別是 `void *`）、第 08 課「struct」。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 函式指標是什麼 | 宣告、指定、呼叫、用 `typedef` 簡化 |
| 第二部分 | 回呼函式 | 把「要做什麼」當參數傳進去：`apply_all`、`count_if` |
| 第三部分 | qsort 與 bsearch | 比較函式的寫法、整數溢位陷阱、排序字串與結構 |
| 第四部分 | 查表分派 | 函式指標陣列、指令名稱 → 函式的對照表 |
| 第五部分 | 🔍 進階 | 用 `void *ctx` 傳額外資料、回傳函式指標、讀懂複雜的宣告 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際用 `gcc -std=c11` 編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：函式指標是什麼

## 1.1 函式也有位址

程式執行時，函式的機器碼也放在記憶體裡，所以 **函式也有位址**。存放函式位址的變數，就是 **函式指標 (function pointer)**。

**為什麼需要**：讓「要呼叫哪個函式」可以 **在執行時決定**，或 **當參數傳給另一個函式**。例如：
- `qsort` 會排序，但它不知道你要「由小到大」還是「依分數排」：你把 **比較函式** 傳給它。
- 計算機程式依照使用者輸入的 `+`、`*` 選擇要呼叫的函式。

C++ 的 lambda、`std::function`、虛擬函式，在 C 裡都是用函式指標做的。

## 1.2 宣告與使用

```c
int add(int a, int b) { return a + b; }
int mul(int a, int b) { return a * b; }

int (*fp)(int, int) = add;                /* fp：指向「接收兩個 int、回傳 int」的函式 */
printf("%d\n", fp(2, 3));                 // 輸出：5

fp = mul;                                 /* 換成指向另一個函式 */
printf("%d %d\n", fp(2, 3), (*fp)(4, 5)); // 輸出：6 20
```

**怎麼讀 `int (*fp)(int, int)`**：
1. 從名字 `fp` 開始。
2. `(*fp)`：fp 是一個 **指標**。
3. 往右看 `(int, int)`：指向一個 **接收兩個 int 的函式**。
4. 往左看 `int`：那個函式 **回傳 int**。

**寫法的小規則**：
- `fp = add` 和 `fp = &add` 一樣：函式名稱會自動轉成它的位址（就像陣列名稱轉成指標）。
- `fp(2, 3)` 和 `(*fp)(2, 3)` 一樣：兩種呼叫方式都可以，一般寫前者。

### ⚠️ 括號不能少

```c
int (*fp)(int, int);                      /* ✅ fp 是「指向函式的指標」 */
int *fp(int, int);                        /* ❌ 這是「宣告一個函式 fp，回傳 int *」，完全不同 */
```

### 型別要完全相符

```c
double half(double x) { return x / 2; }
int (*fp)(int, int) = half;               /* ❌ 型別不符：gcc 警告 incompatible pointer type */
```

函式指標的型別包含 **回傳型別和每個參數的型別**。用錯誤的型別呼叫函式是 **未定義行為**，就算強制轉型讓它編譯通過，結果也是錯的。

## 1.3 用 typedef 簡化

函式指標的語法很難讀，幾乎都會用 `typedef` 取一個名字：

```c
typedef int (*BinOp)(int, int);           /* BinOp 就是「指向 int f(int, int) 的指標」型別 */

BinOp ops[3] = {add, sub, mul};           /* 函式指標陣列，一目了然 */
for (int i = 0; i < 3; i++) printf("%d ", ops[i](10, 3));
printf("\n");                             // 輸出：13 7 30
```

沒有 `typedef` 的話，這個陣列要寫成 `int (*ops[3])(int, int)`。

---

# 第二部分：回呼函式

## 2.1 是什麼

**回呼函式 (callback)**：把一個函式當參數傳給另一個函式，由對方在適當的時候「回頭呼叫」它。

**比喻**：你去餐廳排隊，留下電話號碼（函式指標）。餐廳不用知道你是誰，有位子時「打電話給你」（呼叫回呼函式）就好。

## 2.2 例子：對每個元素做某件事

```c
void apply_all(int *a, int n, int (*f)(int)) {
    for (int i = 0; i < n; i++) a[i] = f(a[i]);   /* 要做什麼由呼叫者決定 */
}

int square(int x) { return x * x; }
int negate(int x) { return -x; }

int a[] = {1, -2, 3, -4, 5};
apply_all(a, 5, square);
for (int i = 0; i < 5; i++) printf("%d ", a[i]);
printf("\n");                             // 輸出：1 4 9 16 25
```

**為什麼這樣設計**：「走過陣列」的迴圈只寫一次，「對元素做什麼」可以任意替換。要改成取負號，傳 `negate` 就好，不用再寫一個迴圈。

## 2.3 例子：數符合條件的元素

回傳「真 / 假」的函式叫 **述詞 (predicate)**：

```c
int count_if(const int *a, int n, int (*pred)(int)) {
    int c = 0;
    for (int i = 0; i < n; i++)
        if (pred(a[i])) c++;
    return c;
}

int is_even(int x)     { return x % 2 == 0; }
int is_positive(int x) { return x > 0; }

int b[] = {1, -2, 3, -4, 6};
printf("%d %d\n", count_if(b, 5, is_even), count_if(b, 5, is_positive));   // 輸出：3 3
```

`CL09` 的 `map_all`、`filter_keep`、`fold` 就是這個概念的延伸（對應 C++ 的 `transform`、`remove_if`、`accumulate`）。

---

# 第三部分：qsort 與 bsearch

## 3.1 qsort 的介面

`<stdlib.h>` 的 `qsort` 可以排序 **任何型別** 的陣列：

```c
void qsort(void *base, size_t n, size_t size,
           int (*cmp)(const void *, const void *));
```

| 參數 | 意義 |
|---|---|
| `base` | 陣列的開頭（`void *`：什麼型別都可以） |
| `n` | 元素個數 |
| `size` | **每個元素** 的大小（byte），通常寫 `sizeof arr[0]` |
| `cmp` | 比較函式：收到 **兩個元素的位址** |

**為什麼要傳 `size`**：`qsort` 不知道元素是什麼型別，只能把陣列當成「一堆每塊 `size` bytes 的資料」來搬動。

**比較函式的規則**：`cmp(a, b)` 回傳
- **負數**：`a` 應該排在 `b` **前面**；
- **0**：一樣；
- **正數**：`a` 應該排在 `b` **後面**。

## 3.2 排序整數

```c
int cmp_int(const void *a, const void *b) {
    int x = *(const int *)a;              /* 1. 把 void * 轉回原本的型別，取出值 */
    int y = *(const int *)b;
    return (x > y) - (x < y);             /* 2. x<y → -1，x==y → 0，x>y → 1 */
}

int c[] = {5, 2, 9, 1, 7};
qsort(c, 5, sizeof c[0], cmp_int);        /* 傳函式名稱，不要加 () */
// c 變成：1 2 5 7 9
```

**由大到小**：把參數對調就好：

```c
int cmp_int_desc(const void *a, const void *b) { return cmp_int(b, a); }
// c 變成：9 7 5 2 1
```

### ⚠️ 經典錯誤：用減法比較

```c
int cmp_bad(const void *a, const void *b) {
    return *(const int *)a - *(const int *)b;     /* ❌ 可能溢位 */
}

int d[] = {INT_MAX, -2, 0};
qsort(d, 3, sizeof d[0], cmp_bad);
// d 變成：2147483647 -2 0（排錯了！）
```

`INT_MAX - (-2)` 超過 `int` 的範圍，溢位成負數（有號整數溢位是未定義行為，這裡實際得到負數），`qsort` 就以為 `INT_MAX < -2`。數值範圍小（例如分數 0 ~ 100）時減法沒問題，但 **`(x > y) - (x < y)` 永遠是安全的**，養成習慣比較好。`CL09` 的測資就會抓這個錯誤。

### 其他常見錯誤

```c
qsort(c, 5, sizeof c, cmp_int);           /* ❌ sizeof c 是整個陣列（20），不是一個元素 */
qsort(c, 5, sizeof c[0], cmp_int());      /* ❌ 加了 () 變成「呼叫」cmp_int，編譯錯誤 */
```

## 3.3 排序字串

**陷阱**：比較函式收到的是 **元素的位址**。陣列元素是 `char *` 時，收到的是 `char **`：

```c
int cmp_str(const void *a, const void *b) {
    const char *x = *(const char *const *)a;      /* a 指向一個 char *，先解參考一次 */
    const char *y = *(const char *const *)b;
    return strcmp(x, y);
}

const char *words[] = {"pear", "apple", "fig", "banana"};
qsort(words, 4, sizeof words[0], cmp_str);
// words 變成：apple banana fig pear
```

```c
int cmp_str_wrong(const void *a, const void *b) {
    return strcmp(a, b);                  /* ❌ a 是「指向指標的指標」，把指標的位元組當成字元在比 */
}
```

但如果是 **二維字元陣列**，每個元素本身就是字元，`strcmp(a, b)` 反而是對的：

```c
int cmp_row(const void *a, const void *b) { return strcmp(a, b); }   /* 元素就是 char[10] */

char rows[4][10] = {"pear", "apple", "fig", "banana"};
qsort(rows, 4, sizeof rows[0], cmp_row);  /* sizeof rows[0] 是 10 */
// rows 變成：apple banana fig pear
```

| 陣列 | 元素型別 | 比較函式收到 | 取出字串 |
|---|---|---|---|
| `const char *words[]` | `char *` | `char **`（以 `void *` 傳入） | `*(const char *const *)a` |
| `char rows[4][10]` | `char[10]` | `char *`（以 `void *` 傳入） | `(const char *)a` |

## 3.4 排序結構：多個條件

```c
typedef struct { char name[21]; int score; } Stu;

int cmp_stu(const void *a, const void *b) {
    const Stu *x = a, *y = b;             /* C 裡 void * 可以直接指定給 const Stu *，不用轉型 */
    if (x->score != y->score)
        return y->score - x->score;       /* 1. 分數高的在前（0~100 不會溢位） */
    return strcmp(x->name, y->name);      /* 2. 分數一樣，名字字典序小的在前 */
}

Stu ss[] = {{"cat", 90}, {"amy", 85}, {"bob", 90}};
qsort(ss, 3, sizeof ss[0], cmp_stu);
// 結果：bob:90 cat:90 amy:85
```

**模式**：依序比較每個條件，**不相等就直接回傳**，相等才看下一個條件。`CL06` 的 `cmp_rank` 有三個條件，寫法完全一樣。

🔍 **`qsort` 不是穩定排序**：比較結果為 0 的元素，排序後的相對順序不保證。要穩定的話，就把「原本的位置」也加進比較條件。

## 3.5 bsearch：二分搜尋

```c
void *bsearch(const void *key, const void *base, size_t n, size_t size,
              int (*cmp)(const void *, const void *));
```

在 **已經排序好** 的陣列中找 `key`，找到回傳 **指向那個元素的指標**，找不到回傳 `NULL`。

```c
int sorted[] = {1, 3, 5, 7, 9, 11};
int key = 7;
int *hit = bsearch(&key, sorted, 6, sizeof sorted[0], cmp_int);   /* key 也要傳「位址」 */
if (hit) printf("%td\n", hit - sorted);   // 輸出：3（索引 = 指標相減）

key = 4;
hit = bsearch(&key, sorted, 6, sizeof sorted[0], cmp_int);
printf("%s\n", hit ? "found" : "not found");   // 輸出：not found
```

**注意**：
- 陣列必須用 **同一個比較函式** 排序過，否則結果沒有意義。
- 比較函式的 **第一個參數是 key**、第二個是陣列元素。兩者型別可以不同（`CL06` 的 `find_by_name` 就是用名字字串去找 `Student`）。

在字串陣列中找字串時，key 也要和元素同一個「層級」：

```c
/* words 已經排好：apple banana fig pear */
const char *k = "fig";
const char **w = bsearch(&k, words, 4, sizeof words[0], cmp_str);   /* 傳 &k（char **） */
if (w) printf("%td\n", w - words);        // 輸出：2
```

---

# 第四部分：查表分派

## 4.1 用陣列取代一長串 if-else

**問題**：命令列計算機，依照輸入的指令名稱呼叫對應的函式：

```c
if (strcmp(cmd, "add") == 0) r = add(x, y);
else if (strcmp(cmd, "sub") == 0) r = sub(x, y);
else if (strcmp(cmd, "mul") == 0) r = mul(x, y);
/* ……每加一個指令就多一個分支 */
```

**解法**：把「名稱 → 函式」做成一張表：

```c
typedef struct {
    const char *name;
    BinOp fn;
} Command;

static const Command COMMANDS[] = {
    {"add", add},
    {"sub", sub},
    {"mul", mul},
};

BinOp find_op(const char *name) {
    for (size_t i = 0; i < sizeof COMMANDS / sizeof COMMANDS[0]; i++)
        if (strcmp(COMMANDS[i].name, name) == 0) return COMMANDS[i].fn;
    return NULL;                          /* 找不到 */
}

BinOp f = find_op("sub");
if (f) printf("%d\n", f(10, 4));          // 輸出：6
printf("%s\n", find_op("div") ? "yes" : "unknown command");   // 輸出：unknown command
```

**好處**：新增指令只要在表裡加一行；指令清單（例如 `help` 要列出所有指令）也可以直接從表產生。`CL09` 的 `main` 就是用這種表，把 `square`、`is_even` 這些名字對應到函式。

**常見錯誤**：呼叫之前沒檢查 `NULL`。呼叫空的函式指標 → 程式當掉（`SEGV on unknown address 0x000000000000`）。

---

# 第五部分：🔍 進階

## 5.1 用 `void *ctx` 傳額外資料

**問題**：C 沒有 lambda，回呼函式「拿不到」呼叫者的區域變數。例如想用 `for_each` 加總，總和要存在哪裡？

**解法**：多傳一個 `void *` 參數（常叫 `ctx`、`user_data`），原封不動地轉交給回呼函式：

```c
typedef void (*Visit)(int value, void *ctx);

void for_each(const int *a, int n, Visit f, void *ctx) {
    for (int i = 0; i < n; i++) f(a[i], ctx);    /* for_each 不知道 ctx 是什麼，只負責轉交 */
}

void sum_up(int v, void *ctx) {
    *(long long *)ctx += v;               /* 回呼函式知道 ctx 其實是 long long * */
}

typedef struct { int threshold; int count; } Above;
void count_above(int v, void *ctx) {
    Above *s = ctx;                       /* 需要好幾個資料時，包成一個 struct */
    if (v > s->threshold) s->count++;
}

int b[] = {1, -2, 3, -4, 6};
long long total = 0;
for_each(b, 5, sum_up, &total);
printf("%lld\n", total);                  // 輸出：4

Above st = {2, 0};
for_each(b, 5, count_above, &st);
printf("%d\n", st.count);                 // 輸出：2（3 和 6）
```

這是 C 函式庫最常見的設計（例如 `pthread_create` 的 `void *arg`、GUI 函式庫的事件回呼）。C++ 的 lambda 捕捉變數，背後做的就是這件事。

## 5.2 回傳函式指標的函式

```c
BinOp pick(char op) {                     /* 用 typedef：很好讀 */
    switch (op) {
        case '+': return add;
        case '*': return mul;
        default:  return NULL;
    }
}

int (*pick_raw(char op))(int, int) {      /* 不用 typedef：同一個函式，難讀很多 */
    return pick(op);
}

printf("%d %d\n", pick('+')(3, 4), pick_raw('*')(3, 4));   // 輸出：7 12
```

## 5.3 讀懂複雜的宣告：由內往外

規則：**從名字開始，先往右讀，遇到右括號再往左讀**，一層一層往外。

| 宣告 | 讀法 |
|---|---|
| `int *f(int)` | f 是函式（接收 int），回傳 `int *` |
| `int (*f)(int)` | f 是指標，指向函式（接收 int），回傳 int |
| `int (*f[4])(int)` | f 是 4 個元素的陣列，每個是指標，指向函式…… |
| `int (*pick_raw(char))(int, int)` | pick_raw 是函式（接收 char），回傳指標，指向函式（接收兩個 int）回傳 int |
| `void (*signal(int, void (*)(int)))(int)` | 標準函式 `signal`：接收 int 和一個函式指標，回傳函式指標 |

看到這種宣告時，最好的做法是 **用 typedef 拆開**：

```c
typedef void (*Handler)(int);
Handler signal(int sig, Handler h);       /* 和上表最後一行一模一樣，但好讀多了 */
```

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 函式指標 | Function Pointer | 存放函式位址的變數 | 1.1 |
| 回呼函式 | Callback | 當參數傳進去、由對方呼叫的函式 | 2.1 |
| 述詞 | Predicate | 回傳真 / 假的函式 | 2.3 |
| 比較函式 | Comparator | 告訴排序「誰該排前面」的函式 | 3.1 |
| 穩定排序 | Stable Sort | 相等的元素保持原本的順序 | 3.4 |
| 二分搜尋 | Binary Search | 在排序好的資料中每次刪去一半 | 3.5 |
| 查表分派 | Dispatch Table | 用表格把名稱 / 代碼對應到函式 | 4.1 |
| 上下文指標 | Context Pointer | 轉交給回呼函式的 `void *` 額外資料 | 5.1 |

---

# 習題

### 題 1：下面每一行宣告的是什麼？

```c
int *a(void);
int (*b)(void);
int (*c[3])(double);
```

### 題 2：找出錯誤

```c
int cmp(const void *a, const void *b) {
    return *(int *)a > *(int *)b;
}
int arr[] = {3, 1, 2};
qsort(arr, 3, sizeof arr, cmp);
```

### 題 3：寫一個比較函式，把 `double` 陣列由小到大排序。

### 題 4：下面的程式想排序字串陣列，為什麼結果不對？

```c
const char *names[] = {"tom", "amy", "joe"};
qsort(names, 3, sizeof names[0], (int (*)(const void *, const void *))strcmp);
```

### 題 5：預測輸出

```c
int twice(int x) { return 2 * x; }
int plus1(int x) { return x + 1; }

int (*fs[])(int) = {twice, plus1, twice};
int v = 3;
for (int i = 0; i < 3; i++) v = fs[i](v);
printf("%d\n", v);
```

### 題 6：用第 5.1 節的 `for_each` 和一個新的回呼函式，找出陣列的最大值（陣列至少一個元素）。

### 題 7：`bsearch` 回傳 `int *hit`，要怎麼得到它在陣列中的索引？如果陣列有好幾個相同的值，`bsearch` 會回傳哪一個？

---

# 習題解答

**題 1**：
- `a`：函式，不接收參數，回傳 `int *`。
- `b`：指標，指向「不接收參數、回傳 int」的函式。
- `c`：3 個元素的陣列，每個元素是指標，指向「接收 double、回傳 int」的函式。

**題 2**：
- 比較函式只回傳 0 或 1，**從來不回傳負數**：`a < b` 時它說「一樣」，違反了比較函式的規則。結果正不正確要看 `qsort` 內部怎麼實作：在某些系統上碰巧排對（作者用 Linux glibc 測試時就排對了），換一個系統或一組資料就可能排錯。不要依賴碰巧，應該寫 `(x > y) - (x < y)`。
- `sizeof arr` 是整個陣列（12），應該是 `sizeof arr[0]`。

**題 3**：

```c
int cmp_double(const void *a, const void *b) {
    double x = *(const double *)a;
    double y = *(const double *)b;
    return (x > y) - (x < y);             /* 不能寫 (int)(x - y)：0.3 會被截斷成 0 */
}
```

**題 4**：比較函式收到的是 **元素的位址**，也就是 `char **`；`strcmp` 卻把它當成 `char *`，比的是 **指標本身的位元組**，不是字串內容。而且把 `strcmp` 強制轉成不同型別的函式指標再呼叫，本身就是未定義行為。要寫一個像 3.3 節 `cmp_str` 的包裝函式。

**題 5**：`14`。`3 → twice → 6 → plus1 → 7 → twice → 14`。

**題 6**：

```c
void find_max(int v, void *ctx) {
    int *best = ctx;
    if (v > *best) *best = v;
}

int best = b[0];                          /* 用第一個元素當初始值，不要用 0（陣列可能全是負數） */
for_each(b, 5, find_max, &best);
```

**題 7**：索引是 `hit - arr`（指標相減，型別是 `ptrdiff_t`，用 `%td` 印）。有多個相同值時，標準 **不保證** 回傳哪一個；要找「第一個」的話，要自己寫二分搜尋（類似 C++ 的 `lower_bound`）。
