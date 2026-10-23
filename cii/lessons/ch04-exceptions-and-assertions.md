# 第 4 章　Exceptions and Assertions（例外與斷言）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.45–65

---

## 1. 本章定位：程式中的三種錯誤

| 類別 | 性質 | 處理方式 | 範例 |
|---|---|---|---|
| **使用者錯誤**（user error） | **可以預期**，是正常計算的一部分 | 函式**回傳錯誤碼** | 檔案不存在、試算表數字格式錯誤、原始碼有語法錯誤 |
| **例外**（exception） | 少見、可能出乎意料，但**可能可以復原** | **丟出例外**，由處理程式復原 | 記憶體用完、算術溢位、使用者按下中斷鍵、寫檔錯誤 |
| **執行期錯誤**（checked runtime error） | **永遠不該發生**，代表程式有 bug | **assert**，優雅地結束程式 | 傳 NULL 給 `Stack_push` |

**為什麼例外不用錯誤碼？**
例外很少發生，如果每個函式都回傳錯誤碼，處理少數情況的程式碼會**淹沒常見情況的程式碼**。

**例外的範圍是動態的**：丟出例外時，由**最近建立的**處理程式接手。控制權的轉移就像一個 **nonlocal goto**，處理程式可能在離丟出點很遠的函式裡。

本章提供兩個介面：
- **`Except`**：結構化的例外處理（TRY / EXCEPT / FINALLY / RAISE）
- **`Assert`**：取代標準的 `assert.h`，失敗時丟出例外

---

## 2. 基礎：`setjmp` / `longjmp`

- **`setjmp`** 建立處理程式，**`longjmp`** 丟出例外。
- `setjmp` 的特別之處：**它可以回傳兩次**。
  - 第一次直接呼叫時回傳 **0**。
  - 之後有人呼叫 `longjmp(env, v)` 時，**再回傳一次**，這次的值是 `v`。

### 2.1 原始的寫法（有問題）

```c
#include <setjmp.h>
int Allocation_handled = 0;
jmp_buf Allocate_Failed;

void *allocate(unsigned n) {
    void *new = malloc(n);
    if (new)
        return new;
    if (Allocation_handled)
        longjmp(Allocate_Failed, 1);
    assert(0);   /* 沒有處理程式 → checked runtime error */
}

/* client */
char *buf;
Allocation_handled = 1;
if (setjmp(Allocate_Failed)) {
    fprintf(stderr, "couldn't allocate the buffer\n");
    exit(EXIT_FAILURE);
}
buf = allocate(4096);
Allocation_handled = 0;
```

### 2.2 問題

1. **不支援巢狀處理程式**：client 不可能知道它呼叫的實作內部自己建立了哪些處理程式。
2. **`Allocation_handled` 旗標很笨拙**：沒在正確的時間設定或清除，就會一團亂。

`Except` 介面就是要解決這兩個問題。

---

## 3. `Except` 介面（4.1 Interface）

### 3.1 例外的型別

```c
/* except.h */
#ifndef EXCEPT_INCLUDED
#define EXCEPT_INCLUDED
#include <setjmp.h>

#define T Except_T
typedef struct T {
    const char *reason;
} T;
/* ... exported types / variables / functions / macros ... */
#undef T
#endif
```

- `Except_T` 只有一個欄位 `reason`，是描述例外的字串，**沒有被處理時會印出來**。
- **處理程式用例外的「位址」來辨識它**，所以例外**必須是全域或 static 變數**。
- 把例外宣告成**區域變數或參數**是 **unchecked runtime error**。
- 注意這裡用的是 `typedef struct T T;`，**不是**不透明指標。這是第 2 章提到的「公開表示方式」的例外情況。

### 3.2 丟出例外

```c
#define RAISE(e) Except_raise(&(e), __FILE__, __LINE__)
void Except_raise(const T *e, const char *file, int line);
```

- `RAISE` 會自動帶入**檔名和行號**，也就是例外的「座標」。
- 傳 NULL 的 `e` 給 `Except_raise` 是 checked runtime error。

### 3.3 TRY-EXCEPT 敘述

```c
TRY
    S
EXCEPT(e1)
    S1
EXCEPT(e2)
    S2
...
ELSE
    S0
END_TRY;
```

| 情況 | 行為 |
|---|---|
| S 沒有丟出例外 | 拆除處理程式，繼續執行 `END_TRY` 之後的程式 |
| S 丟出 `ei` | 中斷 S，跳到對應的 `Si`，執行完後繼續 `END_TRY` 之後的程式 |
| S 丟出不在清單中的例外 | 執行 `ELSE` 的 `S0`（`ELSE` 可省略） |
| 沒有任何子句處理 | 例外傳給**外層**（先前建立的）TRY 處理 |

`TRY ... END_TRY` 在語法上等同於**一個敘述**，`TRY` 會開啟一個新的作用域。

**改寫後的範例：**

```c
Except_T Allocate_Failed = { "Allocation failed" };

void *allocate(unsigned n) {
    void *new = malloc(n);
    if (new)
        return new;
    RAISE(Allocate_Failed);
    assert(0);
}

/* client */
extern Except_T Allocate_Failed;
char *buf;
TRY
    buf = allocate(4096);
EXCEPT(Allocate_Failed)
    fprintf(stderr, "couldn't allocate the buffer\n");
    exit(EXIT_FAILURE);
END_TRY;
```

### 3.4 ⚠ `volatile` 陷阱

因為底層是 `setjmp`/`longjmp`，標準 C 的限制同樣適用：

```c
static Except_T e;
int i = 0;
TRY
    i++;
    RAISE(e);
EXCEPT(e)
    ;
END_TRY;
printf("%d\n", i);   /* 可能印出 0 或 1！ */
```

在 S 裡修改的**自動（區域）變數**，經過 `longjmp` 之後，值**不保證**保留下來，因為它可能被放在暫存器裡。

**解法**：宣告成 `volatile int i = 0;`，這樣保證印出 1。

### 3.5 TRY-FINALLY 敘述

```c
TRY
    S
FINALLY
    S1
END_TRY;
```

- **不管 S 有沒有丟出例外，S1 都會執行。**
- 如果 S 丟出例外，S1 執行完後會**重新丟出**同一個例外，交給外層處理。
- 用途：**清理資源**。

```c
FILE *fp = fopen(...);
char *buf;
TRY
    buf = allocate(4096);
    ...
FINALLY
    fclose(fp);        /* 不論成功或失敗都會關檔 */
END_TRY;
```

TRY-FINALLY 等同於：

```c
TRY
    S
ELSE
    S1
    RERAISE;
END_TRY;
S1
```

另外，`TRY S END_TRY` 等同於 `TRY S FINALLY ; END_TRY`。

### 3.6 RERAISE 與 RETURN

```c
#define RERAISE Except_raise(Except_frame.exception, \
                Except_frame.file, Except_frame.line)

#define RETURN switch (Except_stack = Except_stack->prev, 0) default: return
```

- **`RERAISE`**：在處理程式裡把例外再丟出去。
- **`RETURN`**：在 TRY 敘述裡**必須用 `RETURN` 取代 `return`**。直接用 C 的 `return` 是 **unchecked runtime error**，因為例外框架沒有從堆疊彈出，會留下指向已失效堆疊框架的懸空指標。
  - 用 `switch` 的技巧是為了讓 `RETURN;` 和 `RETURN e;` 都能展開成**一個語法正確的 C 敘述**。

### 3.7 作者的自我評價

> 這些巨集**確實粗糙，也有點脆弱**。它們的 unchecked runtime error 特別麻煩，造成的 bug 很難找。
> 但對大多數應用已經夠用，因為**例外應該少用**，一個大型應用裡也只有少數幾個。
> **如果例外大量出現，通常代表有更嚴重的設計錯誤。**

---

## 4. 實作（4.2 Implementation）

### 4.1 例外堆疊

```c
typedef struct Except_Frame Except_Frame;
struct Except_Frame {
    Except_Frame *prev;        /* 指向前一個框架 */
    jmp_buf env;               /* 給 setjmp/longjmp 用 */
    const char *file;          /* 例外座標 */
    int line;
    const T *exception;        /* 被丟出的例外 */
};

extern Except_Frame *Except_stack;   /* 堆疊頂端 */
```

- 每個 TRY 都會**推入**一個 `Except_Frame`，多個框架串成一個**鏈結串列形式的堆疊**，這就是支援巢狀的方式。
- **框架的空間就是 TRY 區塊裡的一個區域變數**，不需要動態配置。

### 4.2 四種狀態

```c
enum { Except_entered = 0, Except_raised,
       Except_handled,     Except_finalized };
```

| 狀態 | 意義 |
|---|---|
| `Except_entered` | 進入 TRY，框架已推入。**必須是 0**，因為 `setjmp` 第一次回傳 0 |
| `Except_raised` | 有例外發生（`longjmp` 傳回的值） |
| `Except_handled` | 某個處理程式已經處理了這個例外 |
| `Except_finalized` | 沒有例外，但執行了 FINALLY 子句 |

### 4.3 巨集展開

```c
#define TRY do { \
    volatile int Except_flag; \
    Except_Frame Except_frame; \
    Except_frame.prev = Except_stack;   /* push */ \
    Except_stack = &Except_frame; \
    Except_flag = setjmp(Except_frame.env); \
    if (Except_flag == Except_entered) {

#define EXCEPT(e) \
        if (Except_flag == Except_entered) Except_stack = Except_stack->prev; \
    } else if (Except_frame.exception == &(e)) { \
        Except_flag = Except_handled;

#define ELSE \
        if (Except_flag == Except_entered) Except_stack = Except_stack->prev; \
    } else { \
        Except_flag = Except_handled;

#define FINALLY \
        if (Except_flag == Except_entered) Except_stack = Except_stack->prev; \
    } { \
        if (Except_flag == Except_entered) \
            Except_flag = Except_finalized;

#define END_TRY \
        if (Except_flag == Except_entered) Except_stack = Except_stack->prev; \
    } if (Except_flag == Except_raised) RERAISE; \
} while (0)
```

**TRY-EXCEPT 展開後的邏輯骨架：**

```c
do {
    建立並推入 Except_Frame
    if (setjmp 第一次回傳) {
        S
    } else if (例外是 e1) {
        S1
    } ... else {
        S0
    }
    if (有例外而且沒被處理)
        RERAISE;
} while (0)
```

**設計細節：**
- **`do { ... } while (0)`**：讓整個 TRY 在語法上等同於一個敘述，例如可以直接放在 `if` 後面。
- **`Except_flag` 宣告成 `volatile`**：因為它在 `setjmp` 之後會被修改。
- **「只在第一個 EXCEPT 前彈出」**：每個子句開頭都有 `if (Except_flag == Except_entered) pop;`。S 正常結束時旗標仍是 `entered`，第一個子句前就會彈出框架；之後的子句前面是處理程式，旗標已經變成 `handled`，這個 `if` 能避免重複彈出。作者承認「用巨集實作例外會產生一些扭曲的程式碼」。
- **FINALLY** 像是沒有 `else` 的 ELSE，控制流程直接落入清理程式碼。有例外時旗標保持 `raised`，所以 `END_TRY` 會重新丟出。

### 4.4 `Except_raise`

```c
Except_Frame *Except_stack = NULL;

void Except_raise(const T *e, const char *file, int line) {
    Except_Frame *p = Except_stack;

    assert(e);
    if (p == NULL) {
        /* 沒有任何處理程式 → 宣告未捕捉的例外並中止 */
        fprintf(stderr, "Uncaught exception");
        if (e->reason)
            fprintf(stderr, " %s", e->reason);
        else
            fprintf(stderr, " at 0x%p", e);
        if (file && line > 0)
            fprintf(stderr, " raised at %s:%d\n", file, line);
        fprintf(stderr, "aborting...\n");
        fflush(stderr);
        abort();
    }
    p->exception = e;          /* 填入例外資訊 */
    p->file = file;
    p->line = line;
    Except_stack = Except_stack->prev;   /* 先 pop */
    longjmp(p->env, Except_raised);      /* 跳回 setjmp */
}
```

**為什麼先 pop 再 longjmp？**
這樣處理程式裡如果**又**丟出例外，就會由**外層**的 TRY 處理，因為外層框架現在在堆疊頂端。

---

## 5. 斷言（4.3 Assertions）

### 5.1 標準 `assert.h` 回顧

- `assert(e)`：`e` 為 0 時，把失敗的運算式文字和檔名、行號寫到 stderr，然後呼叫 `abort()`。
- 定義了 **`NDEBUG`** 時，`assert(e)` 等同於 `((void)0)`。
  ⇒ **`e` 絕對不可以有必要的副作用**（例如賦值），因為它可能根本不會被執行。
- 慣用寫法：
  - `assert(0)`：標示不可能發生的情況。
  - `assert(!"ptr==NULL -- can't happen")`：診斷訊息更有意義。字串字面值是非零指標，取 `!` 後等於 0。

典型實作：

```c
#define assert(e) ((void)((e)|| \
    (fprintf(stderr, "%s:%d: Assertion failed: %s\n", \
     __FILE__, (int)__LINE__, #e), abort(), 0)))
```

- 用 `e1 || e2` 是因為 `assert` **必須展開成運算式**，不能是敘述，效果等同於 `if (!(e1)) e2;`。
- `e2` 是逗號運算式，最後的 `0` 讓它有一個值，符合 `||` 的要求。
- 整個運算式轉型成 `void`，因為標準規定 `assert` 沒有回傳值。
- `#e` 會把運算式變成字串字面值。

### 5.2 `Assert` 介面

```c
/* assert.h */
#undef assert
#ifdef NDEBUG
#define assert(e) ((void)0)
#else
#include "except.h"
extern void assert(int e);
#define assert(e) ((void)((e)||(RAISE(Assert_Failed),0)))
#endif
```

```c
/* except.h 中 */
extern const Except_T Assert_Failed;
```

```c
/* assert.c */
#include "assert.h"
const Except_T Assert_Failed = { "Assertion failed" };
void (assert)(int e) {
    assert(e);
}
```

**重點：**
- 和標準版的差別：失敗時**丟出 `Assert_Failed` 例外**，而不是直接 `abort`；也**不提供**運算式的文字。
- 刻意模仿標準的定義，讓兩個 `assert.h` **可以互換**。這也是 `Assert_Failed` 宣告在 `except.h` 的原因。
- **`void (assert)(int e)`**：函式名稱加上括號，可以**阻止巨集展開**，這樣才能定義出介面要求的同名函式。這是 C 的經典技巧。
- 沒有處理時，輸出會是：
  ```
  Uncaught exception Assertion failed raised at stmt.c:201
  aborting...
  ```
  功能上等同於標準 assert 的診斷訊息。

### 5.3 正式版程式該不該保留 assertion？

這是本節最重要的論點。反對保留的兩個常見理由，以及作者的反駁：

**理由一：效率**
- assertion 確實要花時間，但差異**可以量測，而且通常很小**。
- 和其他效能修改一樣，**只有客觀量測支持時才拿掉**。
- 就算真的太貴，通常也可以**移動** assertion 來降低成本。例如 `h` 裡的檢查太貴，而大部分成本來自 `g` 在迴圈裡呼叫 `h`，那就把檢查移到 `f` 和 `g` 裡，並放在 `g` 的迴圈之前。

**理由二：診斷訊息讓使用者看不懂**
- 拿掉 assertion 只會換來**更糟的結果**。assertion 失敗代表程式已經錯了，繼續執行的結果不可預期，最後多半還是會當掉：
  ```
  General protection fault at 3F60:40EA
  Segmentation fault -- core dumped
  ```
  這些訊息並沒有比 assertion 訊息好懂。
- **更糟的是：繼續執行可能破壞使用者的資料**，例如編輯器毀掉使用者的檔案。作者的評語是 **"This behavior is inexcusable."**

**解法：在最上層包一個 TRY-ELSE**

```c
int main(int argc, char *argv[]) {
    TRY
        edit(argc, argv);
    ELSE
        fprintf(stderr,
            "An internal error has occurred from which there is "
            "no recovery.\nPlease report this error to "
            "Technical Support at 800-777-1234.\nNote the "
            "following message, which will help our support "
            "staff\nfind the cause of this error.\n\n");
        RERAISE;
    END_TRY;
    return EXIT_SUCCESS;
}
```

捕捉所有未處理的例外，先印出友善的回報說明，再重新丟出，讓原本的診斷訊息接著印出來。

> 正是因為 assertion 被包裝成**例外**，才能用這種方式在正式版程式裡優雅地處理。這是 `Assert` 介面存在的真正理由。

---

## 6. 延伸閱讀重點

- 內建例外機制的語言：Ada、**Modula-3**、Eiffel、C++。**`Except` 的 TRY-EXCEPT 是仿照 Modula-3 設計的。**
- **Roberts (1989)** 提出等價的 C 例外介面，但丟出例外時**效率更好**：
  - `Except` 的問題是，如果處理程式在 N 層之下，`Except_raise` 和 `longjmp` 會被呼叫 N 次，一層層重新丟出。
  - Roberts 的版本只呼叫一次就直接到達正確的處理程式或第一個 FINALLY，代價是要限制一個 TRY 裡處理程式的數量上限。
- Microsoft 等編譯器提供結構化例外處理（SEH）作為語言擴充。
- Maguire (1993) 用一整章談 assertion。

---

## 7. 習題摘要

| 題號 | 內容 | 提示 |
|---|---|---|
| 4.1 | 同時有 EXCEPT 和 FINALLY 會怎樣？ | 照巨集展開推演：FINALLY 區塊接在 else-if 鏈之後，所以有沒有匹配都會執行；匹配的例外已經被處理，不會再丟出；沒匹配的例外在 FINALLY 之後重新丟出 |
| 4.2 | 讓 `Except_raise` 只呼叫一次 `longjmp` | 參考 Roberts (1989) |
| 4.3 | 設計把 UNIX signal 轉成例外的介面 | signal handler 和 longjmp 的互動 |
| 4.4 | 未捕捉的例外印出 stack trace | 依賴平台的呼叫慣例 |
| 4.5 | 未捕捉的例外自動啟動除錯器，並在執行期判斷是否要啟動 | 開發和正式版共用 |
| 4.6 | 修改 lcc 原生支援 TRY/RAISE，不靠 setjmp/longjmp | **大型專案** |

---

## 8. 本章重點整理

1. **三種錯誤**：使用者錯誤（回傳錯誤碼）、例外（RAISE，可以復原）、執行期錯誤（assert，代表 bug）。
2. **`setjmp` 回傳兩次**：0 代表建立處理程式，非 0 代表例外發生。這是 C 例外機制的基礎。
3. **`Except` 介面**：`TRY / EXCEPT / ELSE / FINALLY / END_TRY`、`RAISE`、`RERAISE`、`RETURN`。
4. **例外以位址辨識**，必須是全域或 static 變數。
5. **兩大陷阱**：TRY 裡修改的區域變數要宣告 `volatile`；TRY 裡要用 `RETURN`，不能用 `return`。
6. **實作**：用鏈結串列組成的例外框架堆疊、四種狀態旗標、`do-while(0)` 包裝；丟出例外時先 pop 再 longjmp。
7. **`Assert`**：失敗時丟出 `Assert_Failed`，和標準 `assert.h` 可以互換；用 `void (assert)(int)` 阻止巨集展開。
8. **正式版要保留 assertion**：拿掉不會更安全，只會讓錯誤更隱蔽、甚至破壞資料。在最上層用 TRY-ELSE 提供友善的訊息。
9. **例外要少用**，大量出現代表設計有問題。

> **一句話**：用巨集把 `setjmp`/`longjmp` 包成結構化的例外處理，再把 assertion 改成丟出例外，讓「程式有 bug」的情況在正式版裡也能被安全地發現和處理。
