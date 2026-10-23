# 12. 用 C 實作資料結構

> 程式練習：`CL04 動態陣列`、`CL05 鏈結串列`、`CL10 字串雜湊表`
>
> 先備知識：第 05 ~ 11 課全部。這一課是 C 路線的總整理：把指標、動態記憶體、struct、函式指標、多檔案組合起來。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 在 C 裡設計資料結構 | 抽象資料型別 (ADT)、介面慣例、錯誤處理 |
| 第二部分 | 鏈結串列 | 節點、走訪、釋放、為什麼需要 `Node **` |
| 第三部分 | 泛型容器 | 用 `void *` + 元素大小，寫一個能放任何型別的堆疊 |
| 第四部分 | 雜湊表 | 雜湊函式、桶子、分離鏈結法、擴容 |
| 第五部分 | 不透明指標 | 把結構的內容藏起來：真正的封裝 |
| 第六部分 | 未定義行為總整理 | C 最危險的地方，以及怎麼抓到它們 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際用 `gcc -std=c11` 編譯執行過的結果。標 🔍 的是深入內容。

> 為了讓範例短一點，這一課的範例直接用 `malloc` / `free`。做練習題時請用樣板提供的 `xmalloc` / `xfree`（它們會檢查記憶體洩漏）。

---

# 第一部分：在 C 裡設計資料結構

## 1.1 抽象資料型別 (ADT)

**是什麼**：**抽象資料型別 (Abstract Data Type)** 是「一組資料 + 一組操作它的函式」。使用者只透過函式操作，不直接碰內部的欄位。

C++ 用 `class` 把資料和函式綁在一起；C 沒有 `class`，所以用 **命名慣例** 來做同一件事：

| C++ | C |
|---|---|
| `class Stack { ... };` | `typedef struct { ... } Stack;` |
| 建構子 `Stack s;` | `stack_init(&s)` 或 `Stack *s = stack_new()` |
| 解構子（自動呼叫） | `stack_free(&s)`（**一定要自己呼叫**） |
| 成員函式 `s.push(3)` | `stack_push(&s, 3)`：第一個參數是「物件」的指標 |
| `private:` | 不透明指標（第五部分）或「說好不要碰」 |
| 例外 | 回傳值表示成功 / 失敗 |

## 1.2 介面的慣例

**1. 所有函式都加上模組名稱當前綴**：`list_push`、`hm_get`。C 沒有命名空間，`push`、`get` 這種名字一定會和別的東西衝突。

**2. 第一個參數是物件的指標**：

```c
void list_push(List *l, int x);           /* 會修改 → List * */
size_t list_size(const List *l);          /* 只讀取 → const List * */
```

**3. 成對的建立 / 釋放函式**（第 07 課 7.1 節）。

| 風格 | 寫法 | 結構放在哪 |
|---|---|---|
| init / free | `List l; list_init(&l); ... list_free(&l);` | 呼叫者決定（通常在堆疊上） |
| new / delete | `List *l = list_new(); ... list_delete(l);` | 一定在堆積上 |

`CL04`、`CL05`、`CL10` 都用 init / free 風格；第五部分的不透明指標一定要用 new / delete 風格。

**4. 用回傳值表示錯誤**：

```c
int  stack_pop(Stack *s, int *out);       /* 成功回傳 1，空的回傳 0；結果寫到 *out */
int *hm_get(HashMap *m, const char *key); /* 找不到回傳 NULL */
```

C 沒有例外，**呼叫者一定要檢查回傳值**。

---

# 第二部分：鏈結串列

## 2.1 節點與走訪

```c
typedef struct Node {
    int val;
    struct Node *next;                    /* 下一個節點；最後一個是 NULL */
} Node;

Node *node_new(int val, Node *next) {
    Node *n = malloc(sizeof *n);
    if (!n) { fprintf(stderr, "out of memory\n"); exit(1); }
    n->val = val;
    n->next = next;
    return n;
}

void print_list(const Node *head) {
    for (const Node *p = head; p != NULL; p = p->next)   /* 走訪的標準寫法 */
        printf("%d ", p->val);
    printf("\n");
}
```

```
head ──▶ [ 3 | ●─]──▶ [ 2 | ●─]──▶ [ 1 | NULL ]
```

## 2.2 釋放整條串列

```c
void free_list(Node *head) {
    while (head != NULL) {
        Node *next = head->next;          /* ⚠️ 先記住下一個 */
        free(head);                       /* 再釋放目前這個 */
        head = next;
    }
}
```

**常見錯誤**：

```c
for (Node *p = head; p != NULL; p = p->next)
    free(p);                              /* ❌ free(p) 之後才執行 p = p->next：use-after-free */
```

## 2.3 為什麼要傳 `Node **`？

**問題**：寫一個「在最前面插入」的函式。新節點會變成新的 `head`，所以函式要 **修改呼叫者的 `head` 變數**。

```c
void push_front_bad(Node *head, int val) {
    head = node_new(val, head);           /* ❌ 改的是參數（複本），呼叫者的 head 沒變 */
}

void push_front(Node **head, int val) {
    *head = node_new(val, *head);         /* ✅ 透過指標修改呼叫者的 head */
}

Node *head = NULL;
for (int i = 1; i <= 3; i++) push_front(&head, i);
print_list(head);                         // 輸出：3 2 1
push_front_bad(head, 99);
print_list(head);                         // 輸出：3 2 1（99 沒有加進去，而且那個節點洩漏了）
```

**規則和第 05 課一樣**：想讓函式修改一個 `int`，要傳 `int *`；想讓函式修改一個 `Node *`，就要傳 `Node **`。

（`CL05` 的做法是把 `head`、`tail`、`size` 包進 `List` 結構，傳 `List *`。這樣修改 `l->head` 就會改到呼叫者的結構，是另一種解法。）

## 2.4 🔍 用 `Node **` 刪除節點：不用特別處理 head

**問題**：刪除串列中所有值等於 `x` 的節點。一般的寫法要記住「前一個節點」，而且刪除 head 時要特別處理（因為 head 沒有「前一個」）。

**技巧**：用 `Node **pp` 指向「**指向目前節點的那個指標**」：一開始指向 `head` 變數，之後指向前一個節點的 `next` 欄位。不管是哪一種，`*pp = ...` 都能把目前的節點「接掉」。

```c
int remove_all(Node **head, int x) {
    int removed = 0;
    Node **pp = head;                     /* pp 指向「指向目前節點的指標」 */
    while (*pp != NULL) {
        if ((*pp)->val == x) {
            Node *dead = *pp;
            *pp = dead->next;             /* 讓指向它的指標改指向下一個（head 或前一個的 next 都一樣） */
            free(dead);
            removed++;                    /* pp 不動：*pp 現在已經是下一個節點了 */
        } else {
            pp = &(*pp)->next;            /* 前進：指向目前節點的 next 欄位 */
        }
    }
    return removed;
}

/* 串列：2 5 2 2 7 2 */
int r = remove_all(&head, 2);
printf("%d: ", r);
print_list(head);                         // 輸出：4: 5 7
```

```
一開始：  pp ──▶ head ──▶ [2]──▶ [5]──▶ ...
刪掉第一個 2 後：*pp（也就是 head）直接改成指向 [5]

pp 前進到 [5] 的 next 欄位：
          head ──▶ [5 | next]──▶ [2]──▶ ...
                        ▲
                        pp
```

同樣的技巧也能寫出「插入到排序好的位置」：

```c
void insert_sorted(Node **head, int val) {
    Node **pp = head;
    while (*pp != NULL && (*pp)->val < val)
        pp = &(*pp)->next;                /* 找到第一個 >= val 的位置 */
    *pp = node_new(val, *pp);             /* 插在那裡（可能是 head、中間或最後） */
}

/* 依序插入 5 1 4 9 3 */
// 結果：1 3 4 5 9
```

`CL05` 的 `remove_first` 就可以用這個技巧寫。

---

# 第三部分：泛型容器

## 3.1 問題

`IntVec`（`CL04`）只能放 `int`。要放 `double`、`Point`、`char *` 時，C 沒有模板，難道每種型別都要寫一份？

**解法**：學 `qsort` 的設計（第 09 課）：容器 **不知道元素的型別，只知道每個元素有幾個 byte**，用 `memcpy` 搬資料。

## 3.2 泛型堆疊

```c
typedef struct {
    char *data;                           /* 用 char *：可以做「以 byte 為單位」的指標算術 */
    size_t elem_size;                     /* 每個元素幾個 byte */
    size_t size, cap;
} Stack;

void stack_init(Stack *s, size_t elem_size) {
    s->data = NULL;
    s->elem_size = elem_size;
    s->size = s->cap = 0;
}

void stack_free(Stack *s) {
    free(s->data);
    s->data = NULL;
    s->size = s->cap = 0;
}

int stack_push(Stack *s, const void *elem) {        /* 傳「元素的位址」 */
    if (s->size == s->cap) {
        size_t nc = s->cap == 0 ? 4 : s->cap * 2;
        char *tmp = realloc(s->data, nc * s->elem_size);
        if (!tmp) return 0;
        s->data = tmp;
        s->cap = nc;
    }
    memcpy(s->data + s->size * s->elem_size, elem, s->elem_size);   /* 第 size 個元素的位置 */
    s->size++;
    return 1;
}

int stack_pop(Stack *s, void *out) {                /* 結果複製到 out 指向的地方 */
    if (s->size == 0) return 0;
    s->size--;
    memcpy(out, s->data + s->size * s->elem_size, s->elem_size);
    return 1;
}
```

**使用**：

```c
Stack si;
stack_init(&si, sizeof(int));             /* 放 int */
for (int i = 1; i <= 5; i++) stack_push(&si, &i);
int x;
while (stack_pop(&si, &x)) printf("%d ", x);
printf("\n");                             // 輸出：5 4 3 2 1
stack_free(&si);

typedef struct { double x, y; } Point;
Stack sp;
stack_init(&sp, sizeof(Point));           /* 同一份程式碼，放 Point */
stack_push(&sp, &(Point){1.5, 2.0});      /* 複合字面值（第 08 課） */
stack_push(&sp, &(Point){3.0, 4.5});
Point p;
stack_pop(&sp, &p);
printf("%.1f %.1f %zu\n", p.x, p.y, sp.size);   // 輸出：3.0 4.5 1
stack_free(&sp);
```

**為什麼 `data` 是 `char *` 而不是 `void *`**：`void *` 不能做指標算術（不知道一步要走幾個 byte）；`char` 剛好是 1 byte，`data + k` 就是往後 `k` 個 byte。

**代價**：

| | C++ 模板 `stack<int>` | C 的 `void *` 泛型 |
|---|---|---|
| 型別檢查 | ✅ 放錯型別是編譯錯誤 | ❌ `stack_push(&si, &some_double)` 編譯得過，結果是錯的 |
| 速度 | 快（`int` 直接複製） | 稍慢（每次都 `memcpy`） |
| 程式碼 | 每種型別各產生一份 | 只有一份 |

**常見錯誤**：
- `stack_push(&si, i)`：要傳 **位址** `&i`。
- 元素是指標（例如 `char *`）時，`elem_size` 是 `sizeof(char *)`，存進去的是 **指標本身**，不是字串的內容。字串的記憶體由誰負責釋放，要另外規定清楚。

---

# 第四部分：雜湊表

## 4.1 為什麼需要雜湊表？

**問題**：存「單字 → 出現次數」。用陣列存，每次查詢都要從頭找一遍：`O(n)`。排序後二分搜尋是 `O(log n)`，但插入要搬資料。

**雜湊表 (hash table)**：平均 `O(1)` 的查詢、插入、刪除。C++ 的 `unordered_map`、Python 的 `dict` 都是雜湊表。

## 4.2 雜湊函式

**是什麼**：把 key（例如字串）轉成一個整數的函式。要求：
1. **同一個 key 永遠得到同一個值**。
2. 不同的 key 盡量得到不同的值（分散得越均勻越好）。

**djb2**：簡單又好用的字串雜湊函式：

```c
unsigned long djb2(const char *s) {
    unsigned long h = 5381;
    for (; *s; s++)
        h = h * 33 + (unsigned char)*s;   /* 每個字元都會影響結果 */
    return h;
}

printf("%lu %lu %lu\n", djb2("a"), djb2("ab"), djb2("ba"));   // 輸出：177670 5863208 5863240
```

- 用 `unsigned long`：溢位時自動繞回（無號整數溢位有定義，有號的是未定義行為，見第六部分）。
- `(unsigned char)*s`：`char` 可能是負的，先轉成無號。
- 注意 `"ab"` 和 `"ba"` 的值不同：**字元的順序** 也會影響結果。（如果只是把字元加起來，兩者會一樣，分散效果很差。）

## 4.3 桶子與分離鏈結法

雜湊值很大，所以用 `雜湊值 % 桶子數` 決定放在 **哪個桶子 (bucket)**。不同的 key 可能落在同一個桶子（**碰撞 collision**），所以每個桶子是一條 **鏈結串列**：

```c
#define NB 4                              /* 桶子數 */

typedef struct WC {
    char *word;                           /* 自己複製的一份 */
    int count;
    struct WC *next;                      /* 同一個桶子裡的下一個 */
} WC;

WC *table[NB];                            /* 全域陣列：一開始全部是 NULL */

void add_word(const char *w) {
    size_t b = djb2(w) % NB;              /* 1. 算出在哪個桶子 */
    for (WC *e = table[b]; e; e = e->next)   /* 2. 只要在這一條串列裡找 */
        if (strcmp(e->word, w) == 0) { e->count++; return; }
    WC *e = malloc(sizeof *e);            /* 3. 找不到：新增到串列最前面 */
    size_t n = strlen(w) + 1;
    e->word = malloc(n);
    memcpy(e->word, w, n);                /* 複製 key（第 07 課 5.1 節） */
    e->count = 1;
    e->next = table[b];
    table[b] = e;
}
```

（為了簡短，這裡省略了 `malloc` 的 `NULL` 檢查。）

加入 `the cat sat on the mat the cat` 之後：

```
[0]
[1] sat:1 cat:2
[2] on:1 the:3
[3] mat:1
```

**查詢 `"the"`**：算出桶子 2，只要比較桶子 2 裡的 2 個項目，不用看全部 5 個。

**釋放**：每個桶子的每個項目，都要先 `free(e->word)` 再 `free(e)`（第 07 課：先釋放成員，再釋放自己）。

## 4.4 擴容 (Rehash)

**問題**：桶子數固定的話，項目越來越多，每條串列越來越長，最後又變成 `O(n)`。

**解法**：記錄 **負載因子 (load factor)** = 項目數 ÷ 桶子數。超過某個門檻（例如 2）時：
1. 配置一個 **兩倍大** 的桶子陣列。
2. 把每個項目 **重新計算桶子**（`% 新的桶子數`，結果會不一樣！）並移過去。
3. 釋放舊的桶子陣列。

**重點**：
- 第 2 步只要 **搬移節點**（改 `next` 指標），不用重新配置節點、也不用重新複製 key。
- 和動態陣列的「容量倍增」一樣，平均每次插入仍然是 `O(1)`。

`CL10` 要你把這一節的內容完整實作出來：`hm_put`、`hm_get`、`hm_del`、擴容和釋放。

---

# 第五部分：不透明指標

## 5.1 問題

`CL04` 的 `IntVec` 定義在標頭檔裡，使用者看得到 `data`、`size`、`cap`，就可能直接修改 `v.size = 100`，破壞資料結構。C 沒有 `private`，怎麼辦？

## 5.2 解法：只在 .h 宣告，在 .c 定義

利用 **不完整型別**（第 08 課 2.6 節）：標頭檔只告訴使用者「有這個型別」，不告訴他裡面有什麼。

**counter.h**（使用者看到的）：

```c
#ifndef COUNTER_H
#define COUNTER_H

typedef struct Counter Counter;           /* 只有宣告：使用者不知道裡面有什麼 */

Counter *counter_new(int start);
void counter_free(Counter *c);
void counter_inc(Counter *c);
int counter_get(const Counter *c);

#endif
```

**counter.c**（只有實作者看得到）：

```c
#include <stdlib.h>
#include "counter.h"

struct Counter {                          /* 真正的定義藏在 .c 裡 */
    int value;
    int times;
};

Counter *counter_new(int start) {
    Counter *c = malloc(sizeof *c);       /* 只有這個檔案知道 sizeof(Counter) */
    if (c) { c->value = start; c->times = 0; }
    return c;
}
void counter_free(Counter *c) { free(c); }
void counter_inc(Counter *c) { c->value++; c->times++; }
int counter_get(const Counter *c) { return c->value; }
```

**main.c**：

```c
#include <stdio.h>
#include "counter.h"

int main(void) {
    Counter *c = counter_new(10);
    counter_inc(c);
    counter_inc(c);
    printf("%d\n", counter_get(c));       // 輸出：12
    counter_free(c);
    return 0;
}
```

使用者試圖碰內部的話，**編譯錯誤**：

```c
c->value = 5;                             /* error: invalid use of incomplete typedef 'Counter' */
Counter d;                                /* error: storage size of 'd' isn't known */
```

**好處**：
- 真正的封裝：使用者 **不可能** 直接改內部欄位。
- 以後修改 `struct Counter` 的內容（例如加一個欄位），使用者的程式 **不用改、甚至不用重新編譯**，只要重新連結。

**代價**：結構一定要用 `malloc` 配置（使用者不知道大小，不能放在堆疊上），每次存取都要呼叫函式。

C 標準函式庫的 `FILE` 就是這樣：你只拿得到 `FILE *`，從來不會直接碰 `FILE` 裡面的欄位。

---

# 第六部分：未定義行為總整理

## 6.1 什麼是未定義行為？

**未定義行為 (Undefined Behavior, UB)**：C 標準說「這種情況，**程式做什麼都可以**」。可能當掉、可能看起來正常、可能今天正常明天出錯、可能開了 `-O2` 才出錯。

**為什麼 C 要有 UB**：C 為了速度，不做任何執行時檢查。例如陣列存取不檢查索引，編譯器也可以 **假設 UB 永遠不會發生**，依此做更積極的最佳化。

**最危險的地方**：UB 常常 **不會立刻出錯**。程式在你的電腦上「跑得很好」，不代表它是對的。

## 6.2 C 最常見的 UB

| 未定義行為 | 例子 | 課 | 怎麼抓 |
|---|---|---|---|
| 陣列 / 指標越界 | `int a[5]; a[5] = 1;` | 04、05 | ASan：`stack-buffer-overflow` / `heap-buffer-overflow` |
| 解參考空指標 | `int *p = NULL; *p = 1;` | 05 | ASan：`SEGV on unknown address 0x000000000000` |
| 使用已釋放的記憶體 | `free(p); *p = 1;` | 07 | ASan：`heap-use-after-free` |
| 重複釋放 | `free(p); free(p);` | 07 | ASan：`double-free` |
| 回傳區域變數的位址 | `int x; return &x;` | 05 | gcc 警告 `function returns address of local variable` |
| 使用未初始化的變數 | `int x; printf("%d", x);` | 01 | gcc 警告 `-Wuninitialized`（開最佳化時較準） |
| 有號整數溢位 | `INT_MAX + 1` | 02 | UBSan：`signed integer overflow` |
| 除以 0 | `x / 0`、`x % 0` | 02 | UBSan：`division by zero` |
| 位移超過位元數 | `1 << 32`（`int` 是 32 位元） | 02 | UBSan：`shift exponent 32 is too large` |
| 修改字串字面值 | `char *s = "hi"; s[0] = 'H';` | 06 | 通常直接 segmentation fault |
| 字串沒有 `'\0'` 結尾 | `char s[3] = "abc"; strlen(s);` | 06 | ASan：越界讀取 |
| `printf` 格式和型別不符 | `printf("%d", 3.14);` | 01 | gcc 警告 `-Wformat` |
| 同一個運算式中修改同一個變數兩次 | `i = i++ + 1;` | 02 | gcc 警告 `-Wsequence-point` |
| 用錯誤型別的函式指標呼叫 | 第 09 課題 4 | 09 | 很難抓，靠 `-Wall` 的轉型警告 |

## 6.3 防禦的工具

1. **編譯警告全開**：`gcc -std=c11 -Wall -Wextra`。把每個警告都當成錯誤處理。
2. **AddressSanitizer + UndefinedBehaviorSanitizer**：`gcc -g -fsanitize=address,undefined`，也就是本平台的 `--debug`。**每一題送出前都用 `--debug` 跑一次**。
3. **小心的習慣**：
   - 變數宣告時就初始化。
   - `malloc` 後檢查 `NULL`；`free` 後設成 `NULL`。
   - 字串配置 `strlen + 1`；用 `snprintf`、`fgets` 這些有長度限制的函式。
   - 迴圈邊界想清楚是 `<` 還是 `<=`。
   - 每塊記憶體都有明確的擁有者。

---

# 結語：C 和 C++ 的對照

學完 C 之後回頭看 C++，就會知道每個功能是 **為了解決 C 的哪個問題**：

| C 的痛點 | C 的寫法 | C++ 的解法 |
|---|---|---|
| 忘了 `free` | 手動呼叫 `xxx_free` | 解構子、RAII、`unique_ptr` |
| 字串長度和 `'\0'` | `char[]` + `strlen + 1` | `std::string` |
| 動態陣列要自己擴容 | `realloc` + 容量倍增 | `std::vector` |
| 容器只能放一種型別 | `void *` + `elem_size` + `memcpy` | 模板 `template <class T>` |
| 比較函式要轉型 | `qsort` + `const void *` | `std::sort` + lambda |
| 回呼函式拿不到外部變數 | `void *ctx` | lambda 捕捉 |
| 函式名字衝突 | `stack_push` 前綴 | 命名空間、成員函式、多載 |
| 沒辦法封裝 | 不透明指標 | `private` |
| 錯誤要逐層回傳 | 回傳錯誤碼 | 例外 |

C++ 給了你更方便的工具，但底層發生的事情和 C 完全一樣。懂了 C，你就知道 `vector::push_back` 為什麼有時候很慢、迭代器為什麼會失效、`string` 為什麼複製很花時間 —— 這就是學 C 最大的收穫。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 抽象資料型別 | Abstract Data Type (ADT) | 資料 + 操作它的函式，使用者只透過函式操作 | 1.1 |
| 節點 | Node | 串列中的一個元素：資料 + 指向下一個的指標 | 2.1 |
| 指標的指標 | Pointer to Pointer | `Node **`：讓函式能修改呼叫者的指標 | 2.3 |
| 泛型 | Generic | 一份程式碼能用在多種型別上 | 3.1 |
| 雜湊函式 | Hash Function | 把 key 轉成整數的函式 | 4.2 |
| 桶子 | Bucket | 雜湊表陣列中的一格 | 4.3 |
| 碰撞 | Collision | 不同的 key 落在同一個桶子 | 4.3 |
| 分離鏈結法 | Separate Chaining | 每個桶子用一條串列存放碰撞的項目 | 4.3 |
| 負載因子 | Load Factor | 項目數 ÷ 桶子數 | 4.4 |
| 重新雜湊 | Rehash | 桶子變多時，把每個項目重新分配 | 4.4 |
| 不透明指標 | Opaque Pointer | 使用者只拿得到指標，看不到結構內容 | 5.2 |
| 未定義行為 | Undefined Behavior (UB) | 標準不規定結果，什麼都可能發生 | 6.1 |

---

# 習題

### 題 1：找出錯誤

```c
void free_list(Node *head) {
    Node *p = head;
    while (p != NULL) {
        free(p);
        p = p->next;
    }
}
```

### 題 2：下面的 `pop_front` 想刪除串列的第一個節點並回傳它的值，有什麼問題？怎麼修正？

```c
int pop_front(Node *head) {
    int v = head->val;
    Node *old = head;
    head = head->next;
    free(old);
    return v;
}
```

### 題 3：用泛型堆疊（3.2 節）存放 `double`，寫出初始化、放入 `1.5` 和 `2.5`、取出並印出的程式碼。

### 題 4：雜湊函式如果寫成「把所有字元的值加起來」，會有什麼問題？舉一個例子。

### 題 5：雜湊表有 8 個桶子、目前有 20 個項目，負載因子是多少？如果門檻是「超過 2 就擴容成兩倍」，擴容後的負載因子是多少？

### 題 6：用 `Node **pp` 的技巧，寫出 `void append(Node **head, int val)`：把新節點加到串列 **最後面**（串列可能是空的）。

### 題 7：下面哪些是未定義行為？

```c
(a) unsigned int u = UINT_MAX; u = u + 1;
(b) int i = INT_MAX; i = i + 1;
(c) int a[3]; int *p = a + 3;
(d) int a[3]; int x = *(a + 3);
(e) char *s = malloc(4); strcpy(s, "abcd");
```

---

# 習題解答

**題 1**：`free(p)` 之後又讀取 `p->next`：**use-after-free**。要先存下一個節點：

```c
while (p != NULL) {
    Node *next = p->next;
    free(p);
    p = next;
}
```

**題 2**：
- `head = head->next` 只改了參數（複本），呼叫者的 `head` 還是指向 **已經被釋放** 的節點 → 之後使用就是 use-after-free。
- 沒有處理空串列：`head` 是 `NULL` 時 `head->val` 會當掉。

修正：傳 `Node **`，並處理空串列：

```c
int pop_front(Node **head, int *out) {
    if (*head == NULL) return 0;          /* 空的：回傳失敗 */
    Node *old = *head;
    *out = old->val;
    *head = old->next;                    /* 修改呼叫者的 head */
    free(old);
    return 1;
}
```

**題 3**：

```c
Stack sd;
stack_init(&sd, sizeof(double));
double a = 1.5, b = 2.5;
stack_push(&sd, &a);
stack_push(&sd, &b);
double v;
while (stack_pop(&sd, &v)) printf("%.1f\n", v);   /* 先印 2.5，再印 1.5 */
stack_free(&sd);
```

注意不能寫 `stack_push(&sd, &1.5)`（常數沒有位址）；可以用複合字面值 `stack_push(&sd, &(double){1.5})`。

**題 4**：字元相同、順序不同的字串（例如 `"listen"` 和 `"silent"`、`"ab"` 和 `"ba"`）會得到 **一樣的** 雜湊值，全部擠在同一個桶子。而且英文單字的字元和通常只在幾百到幾千之間，桶子很多時，大部分桶子都用不到。djb2 的 `h * 33` 讓每個字元的「位置」也影響結果。

**題 5**：負載因子 = 20 ÷ 8 = **2.5**，超過 2，擴容成 16 個桶子，新的負載因子 = 20 ÷ 16 = **1.25**。

**題 6**：

```c
void append(Node **head, int val) {
    Node **pp = head;
    while (*pp != NULL)                   /* 走到最後一個指標（最後一個節點的 next，或空串列時的 head） */
        pp = &(*pp)->next;
    *pp = node_new(val, NULL);
}
```

空串列時迴圈一次都不執行，`*pp` 就是 `*head`，新節點直接變成 head，不用特別處理。（每次都要走完整條串列，是 `O(n)`；`CL05` 用 `tail` 指標做到 `O(1)`。）

**題 7**：
- (a) **不是** UB：無號整數溢位有定義，繞回 0。
- (b) **是** UB：有號整數溢位。
- (c) **不是** UB：指標可以指向「陣列最後一個元素的下一個位置」（這就是 `end` 的概念），只是不能解參考。
- (d) **是** UB：解參考了越界的位置。
- (e) **是** UB：`"abcd"` 需要 5 個 byte（含 `'\0'`），只配置了 4 個 → 堆積越界。
