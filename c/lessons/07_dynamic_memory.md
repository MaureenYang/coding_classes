# 07. 動態記憶體

> 程式練習：`CL04 動態陣列`、`CL08 動態二維矩陣`（`CL05`、`CL10` 也大量使用）
>
> 先備知識：第 05 課「指標」、第 06 課「字串」。

**這一課分成七個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 為什麼需要動態記憶體 | 堆疊 vs 堆積、三種情況一定要用 `malloc` |
| 第二部分 | malloc / calloc / free | 標準寫法、檢查 `NULL`、`sizeof *p` 的慣用法 |
| 第三部分 | realloc | 擴大 / 縮小、為什麼要用暫存指標、容量倍增 |
| 第四部分 | 記憶體錯誤大全 | 洩漏、use-after-free、double free、越界……每一種的真實錯誤訊息 |
| 第五部分 | 動態字串 | 複製字串、讀取長度未知的一行 |
| 第六部分 | 動態二維陣列 | 三種配置方式的比較 |
| 第七部分 | 所有權 | 誰負責 `free`？設計函式介面的慣例 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際用 `gcc -std=c11` 編譯執行過的結果；錯誤訊息是用 AddressSanitizer（`-fsanitize=address`）實際產生的。標 🔍 的是深入內容。

---

# 第一部分：為什麼需要動態記憶體

## 1.1 堆疊 (Stack) 與堆積 (Heap)

| | 堆疊 (stack) | 堆積 (heap) |
|---|---|---|
| 放什麼 | 區域變數、函式參數 | `malloc` 配置的記憶體 |
| 誰管理 | **自動**：進入函式配置、離開時釋放 | **你自己**：`malloc` 配置、`free` 釋放 |
| 大小 | 小（Linux 約 8 MB、Windows 1 MB） | 大（整台電腦可用的記憶體） |
| 大小何時決定 | 編譯時（VLA 例外） | **執行時** |
| 生命週期 | 到區塊結束 | 到你呼叫 `free` 為止 |
| 速度 | 非常快 | 比較慢（要找空間） |

**比喻**：
- 堆疊像 **餐廳的托盤**：拿了就用，吃完自動收走，又快又方便，但不能疊太高。
- 堆積像 **租倉庫**：要多大有多大、想用多久就用多久，但 **不用了要自己去退租**，忘了就一直付錢（記憶體洩漏）。

## 1.2 三種一定要用動態記憶體的情況

**1. 大小要到執行時才知道**

```c
int n;
scanf("%d", &n);
int *arr = malloc(n * sizeof *arr);       /* n 是使用者輸入的 */
```

**2. 資料很大，放在堆疊會溢位**

```c
void f(void) {
    // int big[10000000];                  // ❌ 40 MB 放堆疊 → 堆疊溢位（程式直接當掉）
    int *big = malloc(10000000 * sizeof *big);   /* ✅ 放堆積 */
    free(big);
}
```

**3. 資料要活得比函式久**

```c
int *make_squares(int n) {
    int *a = malloc(n * sizeof *a);       /* 函式結束後還存在 */
    for (int i = 0; i < n; i++) a[i] = i * i;
    return a;                             /* ✅ 回傳 heap 的位址是合法的（第 05 課：不能回傳區域變數的位址） */
}
```

另外，**鏈結串列、樹、雜湊表** 這些「節點數量會變」的資料結構，每個節點都要動態配置（第 12 課）。

---

# 第二部分：malloc / calloc / free

`#include <stdlib.h>`

## 2.1 malloc：配置記憶體

**是什麼**：`malloc(size)` 在堆積上配置 **`size` 個 byte**，回傳指向那塊記憶體的指標（`void *`）；失敗時回傳 `NULL`。

```c
int n = 5;
int *a = malloc(n * sizeof *a);           /* 配置 n 個 int */
if (a == NULL) {                          /* 一定要檢查 */
    fprintf(stderr, "記憶體不足\n");
    return 1;
}
for (int i = 0; i < n; i++) a[i] = i * 10;   /* 用起來就像陣列 */
printf("%d %d\n", a[0], a[4]);            // 輸出：0 40
free(a);                                  /* 用完一定要釋放 */
```

### 標準寫法的每一個細節

```c
int *a = malloc(n * sizeof *a);
```

| 部分 | 為什麼這樣寫 |
|---|---|
| `malloc(...)` 回傳 `void *` | C 會自動轉成 `int *`，**不用寫 `(int *)`**（C++ 才需要） |
| `n * sizeof *a` | 大小的單位是 **byte**：n 個元素 × 每個元素的大小 |
| `sizeof *a` 而不是 `sizeof(int)` | `*a` 的型別就是元素的型別；以後把 `int` 改成 `long long`，這裡不用跟著改，不會忘記 |

**常見錯誤**：

```c
int *p1 = malloc(n);                      /* ❌ 只配置了 n 個 byte，不是 n 個 int */
int *p2 = malloc(n * sizeof p2);          /* ❌ sizeof p2 是「指標」的大小（通常 8），不是 int 的大小；這裡碰巧配多了，元素換成大的 struct 就不夠 */
int *p3 = malloc(n * sizeof *p3);         /* ✅ */
```

### malloc 給的記憶體內容是垃圾值

```c
int *g = malloc(3 * sizeof *g);
/* g[0]、g[1]、g[2] 的值是不確定的，使用前要先設定 */
free(g);
```

## 2.2 calloc：配置並清成 0

```c
int *z = calloc(5, sizeof *z);            /* 5 個元素，每個 sizeof *z bytes，全部設成 0 */
printf("%d %d\n", z[0], z[4]);            // 輸出：0 0
free(z);
```

| | `malloc(n * size)` | `calloc(n, size)` |
|---|---|---|
| 內容 | 垃圾值 | 全部是 0 |
| 參數 | 總 byte 數 | 個數、每個的大小 |
| 🔍 溢位檢查 | `n * size` 太大會溢位，配置到比預期小的空間 | 會檢查乘法溢位，太大就回傳 `NULL` |

## 2.3 free：釋放記憶體

**是什麼**：`free(p)` 把 `malloc` / `calloc` / `realloc` 配置的記憶體 **還給系統**。

```c
int *p = malloc(sizeof *p);
*p = 42;
free(p);                                  /* 釋放：p 本身的值沒有變，但它指向的記憶體已經不屬於你了 */
p = NULL;                                 /* 好習慣：避免之後不小心使用（懸置指標） */
free(NULL);                               /* free(NULL) 是合法的，什麼都不做 */
```

**規則**：
1. **每個 `malloc` 都要剛好對應一個 `free`**。
2. 只能 `free` **`malloc` 系列回傳的指標**，不能 `free` 區域變數的位址、也不能 `free` 陣列中間的位置。
3. `free` 之後就 **不能再使用** 那塊記憶體。
4. 不能 `free` 兩次。

## 2.4 🔍 malloc 失敗

`malloc` 失敗（記憶體不足、要求的大小太大）時回傳 `NULL`。不檢查就使用 → 解參考空指標 → 當掉。

```c
size_t huge = (size_t)1 << 50;            /* 1 PB */
void *p = malloc(huge);
printf("%d\n", p == NULL);                // 輸出：1
```

練習題的範圍內 `malloc` 幾乎不會失敗，但正式程式一定要檢查。`CL04` 等題目的 `xmalloc` 就是「失敗時直接結束程式」的包裝。

---

# 第三部分：realloc

## 3.1 改變已配置記憶體的大小

**是什麼**：`realloc(p, new_size)` 把 `p` 指向的記憶體調整成 `new_size` 個 byte，**回傳新的位址**：
- 原地就能擴大：回傳同一個位址。
- 原地放不下：配置一塊新的、**把舊資料複製過去**、釋放舊的，回傳新的位址。
- 失敗：回傳 `NULL`，**舊的記憶體保持不變**（沒有被釋放）。

```c
int *a = malloc(3 * sizeof *a);
for (int i = 0; i < 3; i++) a[i] = i + 1;

int *tmp = realloc(a, 6 * sizeof *a);     /* 擴大成 6 個 */
if (tmp == NULL) { free(a); return 1; }   /* 失敗：a 還是有效的，要記得釋放 */
a = tmp;
for (int i = 3; i < 6; i++) a[i] = (i + 1) * 10;
for (int i = 0; i < 6; i++) printf("%d ", a[i]);
printf("\n");                             // 輸出：1 2 3 40 50 60（前 3 個被保留了）
free(a);
```

### ⚠️ 為什麼要用暫存指標？

```c
a = realloc(a, new_size);                 /* ❌ 如果失敗回傳 NULL，a 被蓋成 NULL —— 原本的記憶體再也找不到了（洩漏） */
```

### ⚠️ realloc 之後，舊的指標都失效了

```c
int *arr = malloc(2 * sizeof *arr);
int *second = &arr[1];                    /* 指向陣列中的元素 */
arr = realloc(arr, 1000 * sizeof *arr);   /* 可能搬到新的位置 */
// *second = 5;                           // ❌ second 可能指向已經釋放的舊記憶體
free(arr);
```

（C++ 的 `vector` 擴容後迭代器失效，原因完全一樣。）

### 特殊情況

| 呼叫 | 效果 |
|---|---|
| `realloc(NULL, n)` | 等於 `malloc(n)` |
| `realloc(p, 較小的大小)` | 縮小，保留前面的資料 |

## 3.2 動態陣列：容量倍增

**問題**：一筆一筆讀入資料，事先不知道有幾筆。每加一筆就 `realloc` 一次會很慢（每次都可能整個複製，總共 `O(n²)`）。

**解法**：記錄 **容量 (capacity)**，空間不夠時 **一次擴大成兩倍**。總複製量是 `n + n/2 + n/4 + ... < 2n`，平均每次加入是 `O(1)`（攤銷分析）。

```c
int *data = NULL;
size_t size = 0, cap = 0;
int x;
while (scanf("%d", &x) == 1) {
    if (size == cap) {                                 /* 滿了 */
        size_t new_cap = cap == 0 ? 4 : cap * 2;
        int *tmp = realloc(data, new_cap * sizeof *data);
        if (!tmp) { free(data); return 1; }
        data = tmp;
        cap = new_cap;
    }
    data[size++] = x;
}
printf("%zu %zu\n", size, cap);           // 輸入 10 個數 → 輸出：10 16
free(data);
```

`CL04` 就是把這個邏輯包成 `IntVec` 型別。C++ 的 `std::vector` 內部也是這樣做的。

---

# 第四部分：記憶體錯誤大全

C 不會幫你管理記憶體，以下每一種錯誤都 **不會有編譯錯誤**，而且常常 **不會立刻當掉**。唯一可靠的方法是用 **AddressSanitizer** 檢查（本平台的 `--debug`）：

```bash
gcc -g -fsanitize=address prog.c -o prog && ./prog
python3 judge.py test cl4 --debug
```

## 4.1 記憶體洩漏 (Memory Leak)

**是什麼**：配置了，卻沒有釋放，而且已經 **沒有任何指標指向它**（再也沒辦法釋放）。

```c
int *p = malloc(10 * sizeof *p);
p = malloc(20 * sizeof *p);               /* ❌ 第一塊的位址被蓋掉了 → 洩漏 40 bytes */
free(p);
```

```
==8634==ERROR: LeakSanitizer: detected memory leaks
Direct leak of 40 byte(s) in 1 object(s) allocated from:
SUMMARY: AddressSanitizer: 40 byte(s) leaked in 1 allocation(s).
```

**後果**：短時間執行的程式看不出來（程式結束時作業系統會收回所有記憶體），但 **長時間執行的程式**（伺服器、遊戲）記憶體會一直增加，最後用光。

**常見原因**：
- 提早 `return` 時忘了釋放。
- `realloc` 失敗時直接覆蓋原本的指標（3.1 節）。
- 釋放「結構」時，忘了先釋放它裡面的指標（例如鏈結串列只 `free(head)`，或 `struct` 裡的字串）。

## 4.2 使用已釋放的記憶體 (Use After Free)

```c
int *p = malloc(4 * sizeof *p);
free(p);
printf("%d\n", p[0]);                     /* ❌ 那塊記憶體已經不屬於你 */
```

```
==8638==ERROR: AddressSanitizer: heap-use-after-free on address 0x502000000010 ...
READ of size 4 at 0x502000000010 thread T0
    #0 0x... in main prog.c:7
```

**後果**：沒有偵測工具時，常常「看起來正常」（資料還沒被覆蓋），之後某次 `malloc` 把那塊記憶體分配給別人，兩邊互相覆蓋，產生極難追蹤的 bug。

**預防**：`free(p); p = NULL;`，之後誤用會變成「解參考空指標」，立刻當掉、容易發現。

## 4.3 重複釋放 (Double Free)

```c
int *p = malloc(4 * sizeof *p);
free(p);
free(p);                                  /* ❌ */
```

```
==8641==ERROR: AddressSanitizer: attempting double-free on 0x502000000010 in thread T0:
```

沒有 ASan 時，glibc 通常會偵測到並中止程式：`free(): double free detected in tcache 2`。更糟的情況是破壞記憶體配置器的內部結構，之後的 `malloc` 出現詭異的行為。

**常見原因**：兩個指標指向同一塊記憶體，各自 `free` 了一次。**解法**：清楚地規定「誰擁有、誰負責釋放」（第七部分）。

## 4.4 堆積越界 (Heap Buffer Overflow)

```c
int *p = malloc(4 * sizeof *p);
p[4] = 1;                                 /* ❌ 合法的索引是 0 ~ 3 */
```

```
==8644==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x502000000020 ...
WRITE of size 4 at 0x502000000020 thread T0
```

### 經典版本：字串忘了 + 1

```c
const char *src = "hello";
char *s = malloc(strlen(src));            /* ❌ 5 個 byte，放不下結尾的 '\0' */
strcpy(s, src);                           /* 寫了 6 個 byte → 越界 1 個 */
```

```
==8647==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x502000000015 ...
WRITE of size 6 at 0x502000000015 thread T0
```

**規則：配置字串一定是 `strlen(s) + 1`。**

## 4.5 釋放不是 malloc 來的記憶體

```c
int x = 5;
int *p = &x;
free(p);                                  /* ❌ x 在堆疊上 */

int *arr = malloc(10 * sizeof *arr);
free(arr + 2);                            /* ❌ 只能 free「malloc 回傳的那個指標」，不能 free 中間 */
```

```
==8650==ERROR: AddressSanitizer: attempting free on address which was not malloc()-ed: 0x7f48f4d00020 in thread T0
```

## 4.6 整理

| 錯誤 | ASan 的關鍵字 | 預防 |
|---|---|---|
| 記憶體洩漏 | `detected memory leaks` | 每個 `malloc` 對應一個 `free`；釋放結構前先釋放成員 |
| 使用已釋放的記憶體 | `heap-use-after-free` | `free` 後設成 `NULL` |
| 重複釋放 | `double-free` | 釐清所有權，只有一個擁有者負責 `free` |
| 堆積越界 | `heap-buffer-overflow` | 注意 `+ 1`、`<` vs `<=` |
| 釋放非 heap 記憶體 | `not malloc()-ed`、`bad-free` | 只 `free` malloc 回傳的指標 |
| 忘了檢查 NULL | `SEGV on unknown address 0x000000000000` | `malloc` 後檢查 |

`--debug` 模式除了越界和 use-after-free，**程式結束時也會檢查洩漏**（LeakSanitizer），有洩漏就會判定為 RE 並列出是哪裡配置的。

---

# 第五部分：動態字串

## 5.1 複製一份字串

```c
char *dup_str(const char *s) {
    size_t n = strlen(s) + 1;             /* + 1：結尾的 '\0' */
    char *copy = malloc(n);
    if (copy) memcpy(copy, s, n);
    return copy;                          /* 呼叫者負責 free */
}
char *name = dup_str("Amy");
name[0] = 'a';                            /* 是自己的一份，可以修改 */
printf("%s\n", name);                     // 輸出：amy
free(name);
```

（POSIX 和 C23 有內建的 `strdup`，功能一樣；嚴格的 C11 沒有。）

**為什麼需要複製？** 例如雜湊表要存使用者給的 key（`CL10`）：如果只存指標，使用者之後修改或釋放了那個字串，表裡的 key 就跟著壞了。

## 5.2 讀取長度未知的一行

`fgets` 需要固定大小的緩衝區。行的長度不確定時，用動態陣列的技巧：

```c
/* 讀一整行（不含換行），回傳 malloc 的字串；檔案結束時回傳 NULL */
char *read_line(FILE *in) {
    size_t cap = 16, len = 0;
    char *buf = malloc(cap);
    if (!buf) return NULL;
    int c;
    while ((c = fgetc(in)) != EOF && c != '\n') {
        if (len + 1 == cap) {                     /* 留一格給 '\0' */
            char *tmp = realloc(buf, cap * 2);
            if (!tmp) { free(buf); return NULL; }
            buf = tmp;
            cap *= 2;
        }
        buf[len++] = (char)c;
    }
    if (c == EOF && len == 0) { free(buf); return NULL; }
    buf[len] = '\0';
    return buf;
}

char *line;
while ((line = read_line(stdin)) != NULL) {       /* 每一行都要 free */
    printf("%zu: %s\n", strlen(line), line);
    free(line);
}
// 輸入兩行：「hello」「a much longer line here」
// 輸出：
// 5: hello
// 23: a much longer line here
```

---

# 第六部分：動態二維陣列

行列數要到執行時才知道時，有三種做法：

## 6.1 做法一：列指標陣列，每列各配置一次

```c
int rows = 3, cols = 4;
int **m = malloc(rows * sizeof *m);       /* rows 個「int *」 */
for (int i = 0; i < rows; i++)
    m[i] = malloc(cols * sizeof *m[i]);   /* 每一列 cols 個 int */

m[2][3] = 7;                              /* 用法和二維陣列一樣 */
printf("%d\n", m[2][3]);                  // 輸出：7

for (int i = 0; i < rows; i++) free(m[i]);   /* 釋放：先釋放每一列 */
free(m);                                  /* 再釋放列指標陣列（順序反過來就找不到每一列了） */
```

```
m ──▶ [ m[0] ] ──▶ [ . . . . ]
      [ m[1] ] ──▶ [ . . . . ]     每一列在記憶體中不一定相鄰
      [ m[2] ] ──▶ [ . . . 7 ]
```

- ✅ 寫法直覺；每一列可以有不同的長度（鋸齒狀陣列）。
- ❌ 配置 `rows + 1` 次；列和列不相鄰，比較慢。

## 6.2 做法二：一整塊，自己算索引

```c
int *flat = malloc(rows * cols * sizeof *flat);
int r = 2, c = 3;
flat[r * cols + c] = 7;                   /* m[r][c] 在第 r * cols + c 個位置 */
printf("%d\n", flat[2 * cols + 3]);       // 輸出：7
free(flat);
```

- ✅ 只配置一次、記憶體連續、最快。
- ❌ 每次存取都要寫 `r * cols + c`，容易寫錯。

## 6.3 做法三：一整塊 + 列指標（兩者的優點）

```c
int **g = malloc(rows * sizeof *g);
int *block = malloc(rows * cols * sizeof *block);
for (int i = 0; i < rows; i++) g[i] = block + i * cols;   /* 每個列指標指向 block 中對應的位置 */
g[2][3] = 7;
printf("%d %d\n", g[2][3], block[11]);    /* 同一個元素 → 輸出：7 7 */
free(g[0]);                               /* g[0] 就是 block */
free(g);
```

- ✅ 只配置兩次、資料連續、可以用 `g[i][j]`。
- `CL08` 的參考解就是這個做法。

## 6.4 🔍 做法四：指向陣列的指標（C99）

```c
int (*v)[cols] = malloc(rows * sizeof *v);   /* v 是「指向 cols 個 int 的陣列」的指標 */
v[2][3] = 7;
printf("%d\n", v[2][3]);                     // 輸出：7
free(v);                                     /* 只配置了一次，也只要 free 一次 */
```

語法比較少見，但很簡潔。需要 VLA 型別的支援（C11 起是選配功能）。

---

# 第七部分：所有權 (Ownership)

## 7.1 誰負責 free？

C 沒有自動釋放，所以每一塊記憶體都要有一個明確的 **擁有者 (owner)**：負責在最後 `free` 它的那一段程式碼。

**常見的慣例**：

| 情況 | 誰負責 free |
|---|---|
| 函式回傳 `malloc` 的指標（例如 `dup_str`、`read_line`） | **呼叫者**（要在說明裡寫清楚） |
| 函式接收呼叫者準備好的緩衝區（例如 `snprintf`、`fgets`） | 呼叫者（函式完全不管配置與釋放） |
| 資料結構內部的記憶體（串列的節點、雜湊表的 key） | 資料結構自己：提供 `xxx_free()` 函式 |
| 函式只是「借用」指標來讀取 | 不負責，**不能** free |

```c
/* 好的介面：成對的建立 / 銷毀函式 */
typedef struct { int *data; size_t size; } Buffer;

Buffer *buffer_new(size_t n) {
    Buffer *b = malloc(sizeof *b);
    if (!b) return NULL;
    b->data = calloc(n, sizeof *b->data);
    if (!b->data) { free(b); return NULL; }   /* 部分失敗：已經配置的要釋放 */
    b->size = n;
    return b;
}

void buffer_free(Buffer *b) {
    if (!b) return;
    free(b->data);                            /* 先釋放成員 */
    free(b);                                  /* 再釋放自己 */
}

Buffer *buf = buffer_new(100);
buf->data[99] = 5;
printf("%zu %d\n", buf->size, buf->data[99]); // 輸出：100 5
buffer_free(buf);
```

C 標準函式庫也是這樣設計的：`fopen` / `fclose`、`malloc` / `free`。

## 7.2 錯誤處理與清理

函式中途失敗時，要釋放 **到目前為止配置的所有東西**。用 `goto` 集中清理是 C 的慣用寫法（第 02 課）：

```c
int process(int n) {
    int ret = -1;
    int *a = NULL, *b = NULL;
    a = malloc(n * sizeof *a);
    if (!a) goto cleanup;
    b = malloc(n * sizeof *b);
    if (!b) goto cleanup;
    /* ... 使用 a、b ... */
    ret = 0;
cleanup:
    free(b);                                  /* free(NULL) 是安全的，所以不用分別判斷 */
    free(a);
    return ret;
}
```

C++ 的解構子和 `unique_ptr` 就是為了自動完成這件事而設計的（C++ 深入第 06 課 RAII）。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 堆疊 / 堆積 | Stack / Heap | 自動管理的小空間 / 手動管理的大空間 | 1.1 |
| 動態配置 | Dynamic Allocation | 執行時用 malloc 配置記憶體 | 2.1 |
| 釋放 | Free / Deallocate | 把記憶體還給系統 | 2.3 |
| 容量 | Capacity | 已配置的空間能放幾個元素 | 3.2 |
| 攤銷分析 | Amortized Analysis | 平均每次操作的成本 | 3.2 |
| 記憶體洩漏 | Memory Leak | 配置了卻無法釋放 | 4.1 |
| 使用已釋放的記憶體 | Use After Free | free 之後還在用 | 4.2 |
| 重複釋放 | Double Free | 同一塊記憶體 free 兩次 | 4.3 |
| 鋸齒狀陣列 | Jagged Array | 每一列長度不同的二維陣列 | 6.1 |
| 所有權 | Ownership | 誰負責釋放這塊記憶體 | 7.1 |

---

# 習題

### 題 1：找出所有錯誤

```c
int *arr = malloc(10);
for (int i = 0; i <= 10; i++) arr[i] = i;
free(arr);
printf("%d\n", arr[0]);
free(arr);
```

### 題 2：下面的函式有什麼問題？

```c
char *greet(const char *name) {
    char buf[64];
    snprintf(buf, sizeof buf, "Hello, %s!", name);
    return buf;
}
```

把它改成回傳 `malloc` 的字串。呼叫者要注意什麼？

### 題 3：這段程式洩漏了多少 byte？（`int` 是 4 bytes）

```c
for (int i = 0; i < 3; i++) {
    int *p = malloc(5 * sizeof *p);
    if (i == 2) free(p);
}
```

### 題 4：下面的 realloc 有什麼問題？

```c
int *data = malloc(4 * sizeof *data);
data = realloc(data, 1000000 * sizeof *data);
```

### 題 5：一個結構如下，寫出正確的釋放函式

```c
typedef struct {
    char *name;       /* malloc 的字串 */
    int *scores;      /* malloc 的陣列 */
    int count;
} Student;
```

### 題 6：用「容量倍增」從 0 開始，每次滿了就變成兩倍（初始容量 1），連續加入 100 個元素，`realloc` 一共被呼叫幾次？最後的容量是多少？

### 題 7：用做法一（每列各配置一次）配置 `rows × cols` 的矩陣時，`malloc` 和 `free` 各要呼叫幾次？做法三呢？

---

# 習題解答

**題 1**：
- `malloc(10)` 只配置了 10 個 **byte**，應該是 `malloc(10 * sizeof *arr)`。
- `i <= 10` 會寫到 `arr[10]`，越界（就算配置正確，合法索引也只有 0 ~ 9）。
- `free` 之後讀 `arr[0]`：use-after-free。
- 第二次 `free(arr)`：double free。

**題 2**：回傳了區域陣列 `buf` 的位址，函式結束後就失效了（懸置指標）。修正：

```c
char *greet(const char *name) {
    size_t n = strlen(name) + sizeof "Hello, !";   /* sizeof 字面值已經包含 '\0' */
    char *buf = malloc(n);
    if (buf) snprintf(buf, n, "Hello, %s!", name);
    return buf;
}
```

呼叫者必須在用完之後 `free` 回傳的字串，而且要檢查是不是 `NULL`。

**題 3**：40 bytes。前兩次迴圈配置的 5 個 `int`（20 bytes）都沒有釋放，而且離開迴圈本體後 `p` 就消失了，再也找不到那兩塊記憶體。

**題 4**：直接把 `realloc` 的結果指定回 `data`：如果 `realloc` 失敗回傳 `NULL`，原本那塊記憶體的位址就遺失了（洩漏），而且 `data` 變成 `NULL`。應該先存到暫存指標，確定成功再指定。

**題 5**：

```c
void student_free(Student *s) {
    if (!s) return;
    free(s->name);
    free(s->scores);
    s->name = NULL;
    s->scores = NULL;
    s->count = 0;
}
```

（如果 `Student` 本身也是 `malloc` 的，最後還要 `free(s)`，而且要 **先釋放成員再釋放自己**。）

**題 6**：容量依序變成 1、2、4、8、16、32、64、128，一共擴大 **8 次**（從 0 → 1 也算一次），最後容量是 **128**。每次擴大要複製舊資料，總共複製 1 + 2 + 4 + ... + 64 = 127 個元素，平均每個元素不到 2 次。

**題 7**：做法一：`malloc` 呼叫 `rows + 1` 次（列指標陣列 1 次 + 每列 1 次），`free` 也是 `rows + 1` 次。做法三：`malloc` 和 `free` 都只要 2 次。
