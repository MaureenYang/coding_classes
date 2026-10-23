# 第 2 章　Interfaces and Implementations（介面與實作）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.15–32
> **全書方法論的核心章節**，後面每一章都套用這裡建立的慣例。

---

## 1. 本章定位

一個模組分成兩部分：

| | 介面（Interface） | 實作（Implementation） |
|---|---|---|
| 回答的問題 | 模組**做什麼**（what） | 模組**怎麼做**（how） |
| C 中的形式 | `.h` 標頭檔 | 一個或多個 `.c` 檔 |
| 數量 | 通常一個 | 可以有很多個，只要都符合介面規格 |
| 誰看得到 | 使用者（client） | 理想上只有實作者 |

- **Client**：使用模組的程式碼。Client *匯入（import）* 介面，實作 *匯出（export）* 介面。
- Client 只需要看介面，甚至可以只拿到實作的目的碼。
- 好處：避免重複的程式碼，也減少 bug，因為介面和實作**寫一次、除錯一次，但用很多次**。

---

## 2. 介面（2.1 Interfaces）

### 2.1 介面的職責

- 只宣告 client **可以用的**識別字，盡量隱藏表示方式和演算法。
- 目的是**降低耦合（coupling）**。Client 一旦依賴某個實作的細節，實作改變時就會出 bug，而且這種依賴常藏在隱含的假設裡，特別難抓。
- C 對介面和實作分離的支援很少，但**靠簡單的慣例就能得到大部分好處**。

### 2.2 命名前綴慣例

```c
/* arith.h */
extern int Arith_max(int x, int y);
extern int Arith_min(int x, int y);
extern int Arith_div(int x, int y);
extern int Arith_mod(int x, int y);
extern int Arith_ceiling(int x, int y);
extern int Arith_floor  (int x, int y);
```

- 介面名稱是 `Arith`，標頭檔是 `arith.h`，**每個識別字都加上 `Arith_` 前綴**。
- 原因：C 的檔案範圍識別字（變數、函式、typedef、列舉常數）全部共用**同一個名稱空間**，struct/union/enum 的 tag 則共用另一個。
- 大程式可能有上千個全域識別字，但模組通常只有幾百個，所以模組名稱很適合當前綴，**還能讓 client 的程式碼更容易看懂**。
- 作者也承認這「不好看，但 C 沒有其他更好的選擇」。

---

## 3. 範例一：`Arith`，填補語言的語意漏洞

### 3.1 問題：C 的整數除法定義不完整

C 標準只要求：若 `x/y` 可以表示，則 `(x/y)*y + x%y == x`。

當運算元**一正一負**時，除法可以**向零截斷**，也可以**向負無限大截斷**，由實作自己決定：

| `-13/5` 的結果 | 那麼 `-13%5` 必須是 |
|---|---|
| `-2`（向零） | `-13 - (-2)*5 = -3` |
| `-3`（向負無限大） | `-13 - (-3)*5 = 2` |

所以內建的 `/` 和 `%` **只有在運算元都是正數時才可靠**。標準函式庫的 `div`/`ldiv` 定義是清楚的，但固定向零截斷，`div(-13,5).quot` 永遠是 `-2`。

### 3.2 `Arith` 的精確定義

- **`Arith_div(x, y)`**：不超過實數 z（z·y = x）的最大整數，也就是一律**向數線左邊截斷**。
  - `Arith_div(-13, 5)`：z = −2.6，結果是 **−3**。
- **`Arith_mod(x, y)`** ≡ `x - y*Arith_div(x, y)`
  - `Arith_mod(-13, 5)` = −13 − 5·(−3) = **2**。
- **`Arith_floor`** / **`Arith_ceiling`**：

```
Arith_ceiling( 13,5) = ⌈ 2.6⌉ =  3
Arith_ceiling(-13,5) = ⌈-2.6⌉ = -2
Arith_floor  ( 13,5) = ⌊ 2.6⌋ =  2
Arith_floor  (-13,5) = ⌊-2.6⌋ = -3
```

- 除數為零時，行為和 `x/y`、`x%y` 相同（未定義）。

### 3.3 為什麼這很重要：模運算的實例

讓 `i` 在 `0..N-1` 之間循環遞增和遞減（例如雜湊表）：

```c
i = Arith_mod(i + 1, N);   // 正確
i = Arith_mod(i - 1, N);   // 正確，i 為 0 時得到 N-1

i = (i + 1) % N;           // 可以
i = (i - 1) % N;           // 錯！i 為 0 時可能得到 -1 或 N-1，依機器而定
i = (i - 1 + N) % N;       // 只在 i-1+N 不溢位時才正確
```

在 `(-1)%N == N-1` 的機器上寫的程式，移植到另一台機器就會壞掉。

### 3.4 核心觀念

> 這麼簡單的介面也需要這麼繁瑣的規格，**這很典型，而且是必要的**。
> 程式語言的語意都有漏洞，C 尤其多。**好的介面會補上這些漏洞**：替未定義的行為下定義，對「未定義」或「由實作決定」的行為做出明確的選擇。

---

## 4. 實作（2.2 Implementations）

### 4.1 實作的原則

- 實作揭露表示細節和演算法，但理想上 client 永遠不需要看。Client 通常透過函式庫共用目的碼。
- 只要遵守介面，**實作可以替換而不影響 client**，例如換成效能更好的版本。
- 好的介面避免機器相依，但可能**迫使實作必須機器相依**，所以不同機器可能需要不同的實作。
- 實作**一定要 `#include` 自己的 `.h`**，讓編譯器檢查定義和宣告是否一致。除此之外，C 沒有任何機制能檢查實作是否符合介面。

### 4.2 `arith.c` 的實作

```c
#include "arith.h"

int Arith_max(int x, int y) { return x > y ? x : y; }
int Arith_min(int x, int y) { return x > y ? y : x; }

int Arith_div(int x, int y) {
    if (-13/5 == -2                      /* 除法向零截斷？ */
    &&  (x < 0) != (y < 0)               /* x、y 異號？   */
    &&  x%y != 0)
        return x/y - 1;
    else
        return x/y;
}

int Arith_mod(int x, int y) {
    if (-13/5 == -2
    &&  (x < 0) != (y < 0)
    &&  x%y != 0)
        return x%y + y;
    else
        return x%y;
}

int Arith_floor(int x, int y)   { return Arith_div(x, y); }
int Arith_ceiling(int x, int y) { return Arith_div(x, y) + (x%y != 0); }
```

**巧妙之處**：

- 用 **`-13/5 == -2`** 在執行期（實際上編譯器通常會做常數折疊）偵測機器的截斷方向，**而不是用 `#if` 條件編譯**，呼應第 1 章「避免條件編譯」的主張。
- `(x < 0) != (y < 0)` 用比較兩個布林結果的方式判斷是否異號。
- `Arith_mod` 的推導：異號而且不整除時，
  `x - y*(x/y - 1)` = `x - y*(x/y) + y` = `x%y + y`。

---

## 5. 抽象資料型別（2.3 Abstract Data Types）

### 5.1 定義

**ADT** 是定義「一個資料型別」以及「對該型別的值的操作」的介面。之所以「抽象」，是因為介面**隱藏了表示方式**，只規定合法的操作。經典範例是**堆疊（stack）**。

### 5.2 不透明指標（Opaque Pointer）

```c
/* 初版 stack.h */
#ifndef STACK_INCLUDED
#define STACK_INCLUDED

typedef struct Stack_T *Stack_T;

extern Stack_T Stack_new  (void);
extern int     Stack_empty(Stack_T stk);
extern void    Stack_push (Stack_T stk, void *x);
extern void   *Stack_pop  (Stack_T stk);
extern void    Stack_free (Stack_T *stk);

#endif
```

**`typedef struct Stack_T *Stack_T;`** 是全書反覆使用的慣用寫法：

- 型別名稱和 struct tag 同名是合法的，因為 **tag 和一般識別字分屬不同的名稱空間**。用同一個名字可以避免多出一堆很少用到的名字。
- 介面只透露「堆疊是指向某個結構的指標」，**不透露結構長什麼樣子**。
- Client 可以自由傳遞這個指標，但**不能解參考（dereference）**，只有實作有這個權限。
- 額外好處是**型別檢查**：傳其他結構的指標進來會編譯錯誤（唯一的例外是 `void *`）。

### 5.3 Include Guard 慣例

- `#ifndef STACK_INCLUDED ... #endif` 讓標頭檔可以被重複引入（介面引用其他介面時就會發生）。
- 使用 **`_INCLUDED` 後綴**，而**不用前導底線**（`_STACK`），因為標準 C 把前導底線保留給實作者和未來的擴充。
- 作者比較過其他做法（禁止介面引用介面、把 guard 放在 client 端），認為這種做法「最不讓人反感」，讓編譯器去做髒活。

### 5.4 `T` 縮寫慣例

```c
/* 最終版 stack.h */
#ifndef STACK_INCLUDED
#define STACK_INCLUDED

#define T Stack_T
typedef struct T *T;

extern T     Stack_new  (void);
extern int   Stack_empty(T stk);
extern void  Stack_push (T stk, void *x);
extern void *Stack_pop  (T stk);
extern void  Stack_free (T *stk);

#undef T
#endif
```

- 介面 `X` 定義的 ADT 命名為 **`X_T`**。在介面內用巨集縮寫成 **`T`**，讓介面比較好讀。
- 結尾 **`#undef T`**，所以 client 必須寫完整的 `Stack_T`，不會污染 client 的名稱空間。
- 實作檔裡會再 `#define T Stack_T` 一次。
- 如果 ADT **公開表示方式**，而且以傳值方式傳遞結構（例如第 16 章的 `Text_T`），就用 `typedef struct T T;`（不是指標）。不論哪一種，`T` 都代表介面的主要型別。

### 5.5 `Stack_free(T *stk)`：傳指標的指標

```c
Stack_T names = Stack_new();
...
Stack_free(&names);   // 釋放後 names 會被設成 NULL
```

接受 `T *` 而不是 `T`，是為了在釋放後**把呼叫端的變數設成 NULL，避免懸空指標（dangling pointer）**。全書所有的 `_free` 函式都遵循這個設計。

---

## 6. Client 的責任（2.4 Client Responsibilities）

### 6.1 介面是一份合約

> "An interface is a contract between its implementations and its clients."

- 實作必須提供介面規定的功能；client 必須遵守介面裡明示和隱含的規則。
- C 的型別檢查能抓到型別錯誤和參數數目錯誤，**C 檢查不到的規則就必須寫在介面裡**。

### 6.2 三種錯誤分類（全書最重要的概念之一）

| 類別 | 定義 | 誰負責 | 可以復原嗎 | 範例 |
|---|---|---|---|---|
| **Unchecked runtime error** | 違反合約，但實作**不保證**偵測到 | Client 自己避免 | 否，結果不可預期 | `Arith` 除以零；傳入不是 `Stack_new` 產生的 `Stack_T` |
| **Checked runtime error** | 違反合約，實作**保證**偵測到（用 `assert`） | Client 有責任避免 | 否，這是程式 bug | 傳 NULL 的 `Stack_T`；對空堆疊 `pop` |
| **Exception** | 可能發生但很少見的情況 | Client **可以**處理 | **可以** | 記憶體用完（`Mem_Failed`） |

注意：runtime error **不是**「可預期的使用者錯誤」，例如開檔失敗。那種錯誤應該用回傳值處理。Runtime error 是**程式本身的 bug**。

**好的介面盡量避免 unchecked runtime error，但一定要寫明會出現哪些。**

> `Arith` 刻意把除以零留成 unchecked，為的是模仿 C 內建運算子的行為。作者也說改成 checked 是合理的替代方案。這是一個**設計選擇**。

### 6.3 `Stack` 介面的完整規格

**Checked runtime errors：**
1. 傳 NULL 的 `Stack_T` 給任何函式
2. 傳 NULL 的 `Stack_T *` 給 `Stack_free`
3. 對空堆疊呼叫 `Stack_pop`

**Exceptions：**
- `Stack_new`、`Stack_push` 可能丟出 `Mem_Failed`（來自它引用的 `Mem` 介面）
- 沒有被處理的 exception 會被視為 checked runtime error

### 6.4 `stack.c` 完整實作

```c
#include <stddef.h>
#include "assert.h"
#include "mem.h"
#include "stack.h"

#define T Stack_T

struct T {
    int count;
    struct elem {
        void *x;
        struct elem *link;
    } *head;
};

T Stack_new(void) {
    T stk;
    NEW(stk);              // Mem 介面的配置巨集
    stk->count = 0;
    stk->head = NULL;
    return stk;
}

int Stack_empty(T stk) {
    assert(stk);           // checked runtime error #1
    return stk->count == 0;
}

void Stack_push(T stk, void *x) {
    struct elem *t;
    assert(stk);
    NEW(t);
    t->x = x;
    t->link = stk->head;
    stk->head = t;
    stk->count++;
}

void *Stack_pop(T stk) {
    void *x;
    struct elem *t;
    assert(stk);
    assert(stk->count > 0);  // checked runtime error #3
    t = stk->head;
    stk->head = t->link;
    stk->count--;
    x = t->x;
    FREE(t);               // 釋放並把 t 設成 NULL
    return x;
}

void Stack_free(T *stk) {
    struct elem *t, *u;
    assert(stk && *stk);   // checked runtime error #1、#2
    for (t = (*stk)->head; t; t = u) {
        u = t->link;
        FREE(t);
    }
    FREE(*stk);
}
```

**要點**：
- `assert` 用來實作**所有** checked runtime error。這裡的 `assert` 是第 4 章自製的版本，能讓程式優雅地結束。
- `NEW(p)`：配置 `p` 所指型別大小的空間。`FREE(p)`：釋放後把 `p` 設成 NULL。兩者都來自第 5 章的 `Mem` 介面。
- 內部是**鏈結串列加上計數**，client 完全看不到。

### 6.5 全書 ADT 共通的 unchecked runtime errors（不另外寫明）

1. **傳入「外來的」ADT 值**：沒辦法保證傳進來的 `Stack_T` 真的是 `Stack_new` 產生的（見習題 2.3）。
2. **把函式指標存進 `void *`**：`void *` 可以存任何**物件**指標，但標準**不保證**能存函式指標。
3. **用 `void *` 繞過型別系統**：存進去的是 `S *`，卻用 `D *` 取出（S、D 是不同型別），結果未定義。不同型別的指標大小或表示方式可能不同，還可能違反對齊限制。

```c
S *p, *q; void *t;
t = p; q = t;     // OK：p == q

S *p; D *q; void *t;
t = p; q = t;     // 不保證 q == p，也不保證 q 是合法的 D*
```

### 6.6 陷阱：為什麼 ADT **不用 `const`**

看起來很合理，但其實是錯的：

```c
int Stack_empty(const T stk);   // ✗
```

- `T` 是 `struct T *` 的 typedef，`const T stk` 的意思是「**常數指標**指向 struct T」，而不是「指標指向**常數** struct T」。
- 指標本來就是傳值，加了 const 對呼叫端和函式**都沒有意義**。

就算改寫成 `const struct T *stk`，作者還是不用，因為：

> **`const` 會透露實作的資訊，因而限制了其他實作的可能性。**
> 例如某個實作想延後釋放元素以便重複使用，並在 `Stack_empty` 被呼叫時才釋放，它就需要修改 `*stk`，`const` 會讓這種實作做不到。

所以**全書所有 ADT 都不使用 `const`**。

---

## 7. 效率（2.5 Efficiency）

- 大多數實作的平均執行時間**不超過 N 的線性**，也能處理大量輸入。
- 處理不了大量輸入、或效能特別重要的介面，會**明確寫出效能標準**。實作必須達到，client 也只能期待這個程度，**不能期待更好**。效能也是合約的一部分。
- 使用簡單但有效率的演算法：陣列、鏈結串列、雜湊表、樹以及它們的組合。複雜演算法在 N 很大時比較好，但 **N 通常很小**。
- **不透明指標的成本**：用函式呼叫取代直接存取欄位，對實際應用的影響**幾乎都可以忽略**；換來的可靠性和偵錯機會**遠遠超過**那一點點效能損失。
- 真的需要提升效能時：
  1. **先嘗試不改介面**，例如改用巨集。
  2. 做不到的話，**另外建立一個新介面**並寫明它的效能優勢，**而不是修改現有介面**，否則所有既有的 client 都會失效。
  （第 10 章的 `Array` / `ArrayRep` 就是這種做法。）

---

## 8. 延伸閱讀重點

- **Parnas (1972)**：如何把程式切分成模組的經典論文，二十多年後仍然適用。
- **C 標準函式庫本身就是 15 個介面**；`stdio.h` 定義的 `FILE` 就是一個 ADT。Plauger (1992) 的寫法和本書類似。
- **Modula-3**：語言層級支援介面和實作分離。本書的術語、**checked/unchecked runtime error 的概念，以及 `T` 記法都來自 Modula-3**，部分介面也改編自 Modula-3 系統。
- **Assertion**：Modula-3、Eiffel（Meyer, 1992）內建 assertion 機制；Maguire (1993) 用了一整章談 C 的 assertion。
- **物件導向**：本書的介面設計原則同樣適用於 C++ 等物件導向語言；把書中的 ADT 改寫成 C++ 是很好的轉換練習。C++ 的 **STL** 提供類似的 ADT，並用 template 達成型別安全的泛型。

---

## 9. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 2.1 | 為什麼用 `-13/5 == -2` 測試比用 `#if` 巨集好？ | 避免條件編譯；測試的就是實際的編譯環境 |
| 2.2 | Cross compiler 的情況下這個測試可能出錯，不用條件編譯怎麼修？ | 編譯機器和執行機器的算術可能不同 |
| 2.3 | 修改 `stack.c` 以偵測部分「外來 `Stack_T`」 | 例如在結構裡加一個獨特的 magic number |
| 2.4 | 設計系統相關的 `isBadPtr(p)` 巨集 | 位址空間範圍、對齊限制 |
| 2.5 | 設計其他版本的 Stack 介面，例如 `Stack_new` 指定最大容量 | 介面設計沒有唯一解 |

---

## 10. 本章重點整理

1. **介面 = 做什麼，實作 = 怎麼做**。一個介面可以有多個實作，client 只依賴介面。
2. **命名前綴**（`Arith_`、`Stack_`）解決 C 只有單一全域名稱空間的問題。
3. **好的介面會補上語言的語意漏洞**，例如 `Arith` 把整數除法定義清楚。
4. **不透明指標** `typedef struct T *T;` 隱藏表示方式，同時取得型別檢查。
5. **介面慣例**：`_INCLUDED` include guard、`#define T X_T` / `#undef T`、`_free(T *)` 釋放後設成 NULL。
6. **介面是合約**，錯誤分三類：unchecked runtime error、checked runtime error（用 `assert`）、exception（可以復原）。
7. **ADT 不用 `const`**，因為它會洩漏並限制實作。
8. **效能也是合約的一部分**。需要更快時不要改既有介面，而是另開新介面。

> **一句話**：把每個模組都寫成一份精確的合約。介面說清楚能做什麼、怎樣算用錯、錯了會怎樣，實作則被完全藏起來、可以隨時替換。
