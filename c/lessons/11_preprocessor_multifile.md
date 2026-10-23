# 11. 前置處理器與多檔案程式

> 程式練習：本課沒有對應的練習題（評測系統一次只編譯一個檔案），但每一題樣板開頭的 `#include`、`#define`，以及 `CL02` 用 `#define strlen please_write_my_strlen` 禁止使用標準函式，都是這一課的內容。
>
> 先備知識：第 03 課「函式與變數的生命」（`static`、`extern`）、第 08 課「struct」。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 從原始碼到執行檔 | 前置處理 → 編譯 → 組譯 → 連結，每一步在做什麼 |
| 第二部分 | `#define` 巨集 | 常數巨集、函式巨集、括號陷阱、副作用陷阱、`#` 與 `##` |
| 第三部分 | 條件編譯 | `#ifdef`、`#if`、`-D` 參數、`assert` |
| 第四部分 | 多檔案程式 | 標頭檔放什麼、引入防護、`static` / `extern`、連結錯誤 |
| 第五部分 | 🔍 進階技巧 | `do { } while (0)`、可變參數巨集、X 巨集、`inline` |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 和錯誤訊息都是實際用 `gcc -std=c11` 產生的。標 🔍 的是深入內容。

---

# 第一部分：從原始碼到執行檔

## 1.1 四個步驟

`gcc main.c -o main` 這一行指令，其實做了四件事：

```
main.c ──[1. 前置處理]──▶ 展開後的 C 程式碼 ──[2. 編譯]──▶ 組合語言
       ──[3. 組譯]──▶ main.o（目的檔）──[4. 連結]──▶ main（執行檔）
                                             ▲
                         stack.o、標準函式庫 ─┘
```

| 步驟 | 做什麼 | 可以單獨執行 | 這一步的錯誤長什麼樣子 |
|---|---|---|---|
| 1. 前置處理 | 處理 `#` 開頭的指令：貼上 `#include` 的檔案、替換巨集、刪掉註解 | `gcc -E main.c` | `fatal error: stak.h: No such file or directory` |
| 2. 編譯 | 檢查語法和型別，翻譯成組合語言 | `gcc -S main.c` | `error: expected ';' before ...` |
| 3. 組譯 | 組合語言 → 機器碼（目的檔 `.o`） | `gcc -c main.c` | （很少出錯） |
| 4. 連結 | 把所有 `.o` 和函式庫接起來，找到每個函式的實際位置 | `gcc main.o stack.o` | `undefined reference to ...` |

**為什麼要知道這個？** 看到錯誤訊息時，先判斷是 **哪一步** 出錯，就知道去哪裡找原因：
- `undefined reference` 是 **連結** 錯誤：程式碼的語法完全沒問題，是「找不到函式的實作」（忘了編譯某個 `.c` 檔、函式名字打錯、或者忘了 `-lm`）。
- `implicit declaration of function` 是 **編譯** 錯誤 / 警告：忘了 `#include` 對應的標頭檔。

## 1.2 前置處理器只做「文字替換」

**是什麼**：前置處理器 (preprocessor) 在真正編譯 **之前** 執行，它 **完全不懂 C 語法**，只會依照 `#` 指令做文字的剪下、貼上、替換。

```c
#include <stdio.h>                        /* 把 stdio.h 的整個內容貼到這裡 */
#define MAX_N 100                         /* 之後所有的 MAX_N 都換成 100 */
```

用 `gcc -E prog.c` 可以看到前置處理之後的結果。遇到奇怪的巨集錯誤時，這是最好的除錯方法。

`#include` 的兩種寫法：

| 寫法 | 去哪裡找 | 用在 |
|---|---|---|
| `#include <stdio.h>` | 系統的標頭檔目錄 | 標準函式庫 |
| `#include "stack.h"` | **先找目前檔案所在的目錄**，找不到再找系統目錄 | 自己寫的標頭檔 |

---

# 第二部分：#define 巨集

## 2.1 常數巨集

```c
#define PI 3.14159
#define MAX_N 100

int arr[MAX_N];                           /* 前置處理後：int arr[100]; */
printf("%.2f\n", PI * 2);                 // 輸出：6.28
```

**慣例**：巨集名稱 **全部大寫**，一看就知道「這是巨集，不是變數」。

**常見錯誤**：

```c
#define MAX_N 100;                        /* ❌ 多了分號：int arr[MAX_N]; 變成 int arr[100;]; → 編譯錯誤 */
#define PI = 3.14                         /* ❌ 不需要 =：PI * 2 變成 = 3.14 * 2 */
```

**巨集 vs `const` 變數 vs `enum`**：

| | `#define N 100` | `const int N = 100;` | `enum { N = 100 };` |
|---|---|---|---|
| 有型別 | ❌ | ✅ | ✅（int） |
| 有作用域 | ❌（從定義處到檔案結尾） | ✅ | ✅ |
| 能當全域陣列大小 | ✅ | ❌（C 裡 `const` 變數不是常數運算式） | ✅ |
| 除錯器看得到名字 | ❌ | ✅ | ✅ |

C 和 C++ 不同：C 的 `const int` **不能** 用在 `case` 標籤或全域陣列的大小。所以 C 程式裡常數多半用 `#define` 或 `enum`。

## 2.2 函式巨集

```c
#define SQUARE(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

printf("%d\n", MAX(3, 7));                // 前置處理後：((3) > (7) ? (3) : (7))
```

**為什麼用巨集而不是函式**：
- 沒有函式呼叫的開銷（但現代編譯器的 `inline` 函式一樣快，見 5.4 節）。
- **不限型別**：`MAX` 可以用在 `int`、`double`、`long long` 上（C 沒有模板，也沒有函式多載）。

⚠️ **定義時，巨集名稱和 `(` 之間不能有空格**：`#define SQUARE (x) ...` 會被當成「常數巨集 `SQUARE`，內容是 `(x) ...`」。

## 2.3 ⚠️ 陷阱一：括號

巨集是 **文字替換**，不會先算參數的值：

```c
#define SQUARE_BAD(x) x * x
#define DOUBLE_BAD(x) (x) + (x)

printf("%d %d\n", SQUARE_BAD(1 + 2), SQUARE(1 + 2));   // 輸出：5 9
printf("%d\n", 10 * DOUBLE_BAD(3));                    // 輸出：33
```

展開後：
- `SQUARE_BAD(1 + 2)` → `1 + 2 * 1 + 2` = 1 + 2 + 2 = **5**（不是 9）。
- `10 * DOUBLE_BAD(3)` → `10 * (3) + (3)` = **33**（不是 60）。

**規則**：
1. **每個參數** 都用括號包起來：`(x)`。
2. **整個巨集** 也用括號包起來：`((x) * (x))`。

## 2.4 ⚠️ 陷阱二：參數被計算多次

```c
int i = 5;
int m = MAX(i++, 3);
printf("%d %d\n", m, i);                  // 輸出：6 7
```

展開成 `((i++) > (3) ? (i++) : (3))`：條件成立，`i++` **執行了兩次**。如果 `MAX` 是函式，`m` 會是 5、`i` 會是 6。

```c
int calls = 0;
int next(void) { return ++calls; }

int s = SQUARE(next());                   /* 展開成 ((next()) * (next())) */
printf("%d %d\n", s, calls);              // 輸出：2 2（next 被呼叫了兩次：1 * 2）

calls = 0;
s = square_fn(next());                    /* 一般函式：參數只計算一次 */
printf("%d %d\n", s, calls);              // 輸出：1 1
```

**規則**：**不要把有副作用的運算式**（`i++`、函式呼叫、`scanf`……）**傳給巨集**。這也是能用函式就用函式的原因。

## 2.5 🔍 `#` 與 `##`

**`#`（字串化）**：把參數變成字串：

```c
#define SHOW(expr) printf(#expr " = %d\n", (expr))
SHOW(3 + 4 * 2);                          // 輸出：3 + 4 * 2 = 11
```

`#expr` 變成 `"3 + 4 * 2"`，再和後面的字串字面值接在一起（相鄰的字串字面值會自動合併）。除錯時很好用。

```c
#define STR(x) #x
#define XSTR(x) STR(x)
printf("%s %s\n", STR(MAX_N), XSTR(MAX_N));   // 輸出：MAX_N 100
```

`STR(MAX_N)` 直接把 `MAX_N` 這幾個字變字串；`XSTR` 多繞一層，參數會 **先展開** 成 `100` 再字串化。

**`##`（拼接）**：把兩段文字接成一個名字：

```c
#define CONCAT(a, b) a##b
int CONCAT(var, 1) = 42;                  /* 變成 int var1 = 42; */
printf("%d\n", var1);                     // 輸出：42
```

## 2.6 實用的巨集

```c
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

int arr[] = {1, 2, 3, 4, 5, 6, 7};
printf("%zu\n", ARRAY_SIZE(arr));         // 輸出：7
```

⚠️ 只能用在 **真正的陣列**，用在指標（包括函式參數裡的「陣列」）會得到錯誤的結果（第 04 課）。

---

# 第三部分：條件編譯

## 3.1 #ifdef / #ifndef

**是什麼**：依照條件決定 **哪些程式碼要編譯**，沒選到的部分在前置處理時就被刪掉了。

```c
#ifdef DEBUG
    printf("debug on\n");                 /* 只有定義了 DEBUG 才會編譯這行 */
#else
    printf("debug off\n");
#endif
```

在命令列用 `-D` 定義巨集，**不用改程式碼** 就能切換：

```bash
gcc prog.c -o prog              # 輸出：debug off
gcc -DDEBUG prog.c -o prog      # 輸出：debug on（等於在檔案最前面寫了 #define DEBUG）
gcc -DMAX_N=500 prog.c          # 等於 #define MAX_N 500
```

**用途**：
- 除錯訊息：開發時打開、正式版關掉。
- 跨平台：`#ifdef _WIN32` 寫 Windows 專用的程式碼。
- 引入防護（4.2 節）。

## 3.2 #if：條件運算

```c
#if MAX_N > 50
    printf("big\n");                      // 輸出：big
#endif

#if __STDC_VERSION__ >= 201112L           /* 編譯器支援 C11 以上 */
    /* 使用 C11 的功能 */
#endif
```

`#if` 只能用 **整數常數運算式**（巨集、數字），不能用變數，也不能用 `sizeof`（前置處理器不懂型別）。

`#if 0 ... #endif` 是暫時停用一大段程式碼的好方法（比 `/* */` 好，因為裡面可以有 `/* */` 註解）。

## 3.3 預先定義的巨集

| 巨集 | 內容 |
|---|---|
| `__FILE__` | 目前的檔名（字串） |
| `__LINE__` | 目前的行號（整數） |
| `__func__` | 目前的函式名稱（C99，嚴格來說是變數不是巨集） |
| `__STDC_VERSION__` | C 標準版本：`-std=c11` 時是 `201112L` |
| `_WIN32` / `__linux__` | 作業系統（只有在那個平台上才會定義） |

## 3.4 assert

`<assert.h>` 的 `assert(條件)`：條件不成立時，印出錯誤訊息並 **中止程式**。

```c
#include <assert.h>

int stack_pop(Stack *s) {
    assert(s->size > 0);                  /* 「不可能發生」的情況：如果發生了，就是程式有 bug */
    return s->data[--s->size];
}
```

失敗時的訊息（然後程式被中止，結束碼不是 0）：

```
prog: prog.c:7: stack_pop: Assertion `s->size > 0' failed.
Aborted
```

- `assert` 是巨集，用 `-DNDEBUG` 編譯時 **整行會被刪掉**。所以 **不要在 `assert` 裡放有副作用的程式碼**，例如 `assert(fgets(buf, 100, fp) != NULL)`。
- `assert` 用來抓 **程式的 bug**，不是用來處理 **使用者的錯誤輸入**（那應該回傳錯誤碼或印出錯誤訊息）。

---

# 第四部分：多檔案程式

## 4.1 為什麼要分成多個檔案？

程式長到幾千行時，全部放在一個檔案裡很難管理。分檔案的好處：
- **模組化**：每個檔案負責一件事（例如 `stack.c` 只管堆疊）。
- **隱藏細節**：使用者只要看標頭檔就知道怎麼用。
- **加快編譯**：只改了一個檔案，只要重新編譯那一個。

**一個模組 = 兩個檔案**：

| 檔案 | 內容 | 比喻 |
|---|---|---|
| `stack.h`（標頭檔） | **宣告**：型別、函式原型、`extern` 變數 | 餐廳的 **菜單**：告訴客人有什麼 |
| `stack.c`（實作檔） | **定義**：函式的本體、全域變數 | **廚房**：實際怎麼做，客人看不到 |

## 4.2 完整的例子

**stack.h**：

```c
#ifndef STACK_H                           /* 引入防護 (include guard)，見下面說明 */
#define STACK_H

#include <stddef.h>                       /* 標頭檔用到 size_t，自己 include 需要的東西 */

typedef struct {
    int data[100];
    size_t size;
} Stack;

void stack_init(Stack *s);                /* 只有宣告（原型），沒有本體 */
int  stack_push(Stack *s, int x);         /* 成功回傳 1，滿了回傳 0 */
int  stack_pop(Stack *s, int *out);       /* 成功回傳 1，空了回傳 0 */

extern int stack_ops;                     /* 宣告：這個全域變數「定義在別的檔案」 */

#endif
```

**stack.c**：

```c
#include "stack.h"                        /* 實作檔也要 include 自己的標頭檔：讓編譯器檢查宣告和定義一致 */

int stack_ops = 0;                        /* 定義：真正配置記憶體的地方（只能有一個） */

static int is_full(const Stack *s) {      /* static：只有這個檔案看得到的輔助函式 */
    return s->size == 100;
}

void stack_init(Stack *s) { s->size = 0; }

int stack_push(Stack *s, int x) {
    if (is_full(s)) return 0;
    s->data[s->size++] = x;
    stack_ops++;
    return 1;
}

int stack_pop(Stack *s, int *out) {
    if (s->size == 0) return 0;
    *out = s->data[--s->size];
    stack_ops++;
    return 1;
}
```

**main.c**：

```c
#include <stdio.h>
#include "stack.h"

int main(void) {
    Stack s;
    stack_init(&s);
    for (int i = 1; i <= 3; i++) stack_push(&s, i * 10);
    int x;
    while (stack_pop(&s, &x)) printf("%d ", x);
    printf("\n%d\n", stack_ops);
    return 0;
}
```

**編譯**：

```bash
gcc -std=c11 -Wall main.c stack.c -o app      # 一次編譯兩個檔案
./app
# 輸出：
# 30 20 10
# 6

# 或者分開編譯，最後再連結：
gcc -std=c11 -c stack.c                       # 產生 stack.o
gcc -std=c11 -c main.c                        # 產生 main.o
gcc main.o stack.o -o app                     # 連結
```

**注意**：`.h` 檔 **不用** 寫在 `gcc` 指令裡，它已經被 `#include` 貼進 `.c` 檔了。

## 4.3 引入防護 (Include Guard)

**問題**：`main.c` include 了 `stack.h`，又 include 了另一個也 include `stack.h` 的檔案 → `stack.h` 被貼了兩次 → `Stack` 被定義兩次。拿掉引入防護、在 `main.c` 寫兩次 `#include "stack.h"` 試試：

```
error: conflicting types for 'Stack'; have 'struct <anonymous>'
```

**解法**：

```c
#ifndef STACK_H        /* 第一次：STACK_H 還沒定義 → 進入 */
#define STACK_H        /* 定義它 */
/* ... 內容 ... */
#endif                 /* 第二次：STACK_H 已經定義了 → 整段跳過 */
```

**每個標頭檔都要有引入防護**。巨集名字通常是檔名大寫，`.` 換成 `_`。

很多編譯器也支援 `#pragma once`（一行就搞定），但它不是 C 標準的一部分。

## 4.4 標頭檔放什麼、不放什麼

| ✅ 放在 .h | ❌ 不要放在 .h |
|---|---|
| 函式原型 `int f(int);` | 函式本體 `int f(int x) { ... }`（`static inline` 例外） |
| `typedef`、`struct` 定義、`enum` | 全域變數的定義 `int count = 0;` |
| `extern int count;`（宣告） | `static` 函式、`static` 變數 |
| `#define` 常數和巨集 | `using namespace` 之類（C 沒有，但 C++ 要注意） |

**為什麼不能把定義放在標頭檔**：標頭檔會被 **好幾個 `.c` 檔** include，每個 `.c` 都會得到一份定義 → 連結時發現有兩個同名的東西：

```c
/* counter.h */
#ifndef COUNTER_H
#define COUNTER_H
int counter = 0;                          /* ❌ 定義放在標頭檔 */
#endif
```

```bash
gcc a.c b.c          # a.c 和 b.c 都 include 了 counter.h
# multiple definition of `counter'; ... first defined here
```

**引入防護救不了這個問題**：它只防止「同一個 `.c` 檔」include 兩次；`a.c` 和 `b.c` 是 **分開編譯** 的，各自都會得到一份。

**正確做法**：`.h` 寫 `extern int counter;`（宣告），**只有一個** `.c` 寫 `int counter = 0;`（定義）。

## 4.5 static 與 extern：誰看得到？

（第 03 課介紹過，這裡從多檔案的角度整理。）

| 寫法（在函式外面） | 其他檔案看得到嗎 | 用途 |
|---|---|---|
| `int count = 0;` | ✅ 可以用 `extern int count;` 存取 | 要共用的全域變數（盡量少用） |
| `static int count = 0;` | ❌ 只有這個檔案 | 模組內部的狀態 |
| `void f(void) { }` | ✅ 有原型就能呼叫 | 公開的函式 |
| `static void f(void) { }` | ❌ 只有這個檔案 | 內部的輔助函式 |

**規則**：**不需要給別人用的，一律加 `static`**。好處：
- 不會和其他檔案的同名函式衝突（C 沒有命名空間，所有非 `static` 的函式名字都在同一個空間）。
- 別人不能依賴你的內部實作，以後可以放心修改。

例如 `stack.c` 的 `is_full` 是 `static`，在 `main.c` 裡就算自己寫了原型也呼叫不到：

```
undefined reference to `is_full'
```

**命名慣例**：因為所有公開的名字共用一個空間，C 函式庫都會加上 **模組名稱當前綴**：`stack_push`、`stack_pop`，而不是 `push`、`pop`。

## 4.6 常見的連結錯誤

| 錯誤訊息 | 原因 | 解法 |
|---|---|---|
| `undefined reference to 'stack_push'` | 沒有編譯 / 連結 `stack.c`；或名字拼錯；或函式是 `static` | `gcc main.c stack.c` |
| `undefined reference to 'sqrt'` | 用了 `<math.h>`，沒連結數學函式庫 | 加上 `-lm`（放在最後面） |
| `undefined reference to 'main'` | 沒有 `main` 函式（或拼錯，例如 `Main`） | |
| `multiple definition of 'counter'` | 同一個全域變數 / 函式在兩個 `.c` 檔都有定義 | 標頭檔只放宣告 |

只編譯 `main.c`、忘了 `stack.c` 時的實際錯誤：

```
main.c:(.text+0x29): undefined reference to `stack_init'
/usr/bin/ld: main.c:(.text+0x57): undefined reference to `stack_push'
...
collect2: error: ld returned 1 exit status
```

看到 `ld`（linker，連結器）就知道是 **連結** 錯誤，程式碼本身沒有語法問題。

## 4.7 🔍 Makefile

檔案一多，每次都打一長串 `gcc` 指令很麻煩。`make` 工具會讀取 `Makefile`，**只重新編譯有修改過的檔案**：

```makefile
CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -g

app: main.o stack.o
	$(CC) main.o stack.o -o app

main.o: main.c stack.h
	$(CC) $(CFLAGS) -c main.c

stack.o: stack.c stack.h
	$(CC) $(CFLAGS) -c stack.c

clean:
	rm -f *.o app
```

（指令前面必須是 **Tab**，不能是空格。）執行 `make` 就會建出 `app`；只改了 `stack.c` 時，`make` 只會重新編譯 `stack.o` 再連結。大型專案通常用 CMake 之類的工具產生建置設定。

---

# 第五部分：🔍 進階技巧

## 5.1 多行巨集：do { } while (0)

**問題**：巨集裡有好幾個敘述時，直接用 `{ }` 包起來，在 `if` / `else` 裡會出錯：

```c
#define SWAP_BAD(T, a, b) { T tmp_ = (a); (a) = (b); (b) = tmp_; }

if (a < b) SWAP_BAD(int, a, b); else printf("no\n");
/* 展開成：if (a < b) { ... }; else ...  ← 多出來的 ; 結束了 if，else 沒有對應的 if → 編譯錯誤 */
```

**解法**：用 `do { ... } while (0)` 包起來，它是 **一個完整的敘述**，後面剛好需要一個分號：

```c
#define SWAP(T, a, b) do { T tmp_ = (a); (a) = (b); (b) = tmp_; } while (0)

int a = 1, b = 2;
if (a < b) SWAP(int, a, b); else printf("no\n");
printf("%d %d\n", a, b);                  // 輸出：2 1
```

迴圈只會執行一次，編譯器會把它最佳化掉，沒有任何成本。這是 C 巨集的標準寫法。

## 5.2 可變參數巨集

```c
#define LOG(fmt, ...) fprintf(stderr, "[%s:%d] " fmt "\n", __FILE__, __LINE__, __VA_ARGS__)

LOG("x=%d y=%d", 3, 4);                   // stderr 輸出：[prog.c:35] x=3 y=4（35 是這一行的行號）
```

`...` 接收剩下的所有參數，`__VA_ARGS__` 代表它們。自動附上檔名和行號，是很常見的除錯巨集。

## 5.3 X 巨集：一份清單產生多個東西

**問題**：enum 和它的名字對照表（第 08 課 4.4 節）要分開寫，新增一個顏色時很容易只改了一邊。

**解法**：把清單寫 **一次**，用不同的巨集「套用」它：

```c
#define COLORS(X) X(RED) X(GREEN) X(BLUE)     /* 清單只寫一次 */

#define AS_ENUM(name) name,
#define AS_STRING(name) #name,

enum Color { COLORS(AS_ENUM) COLOR_COUNT };            /* → enum Color { RED, GREEN, BLUE, COLOR_COUNT }; */
static const char *COLOR_NAMES[] = { COLORS(AS_STRING) };   /* → { "RED", "GREEN", "BLUE", } */

printf("%d %s %s\n", COLOR_COUNT, COLOR_NAMES[GREEN], COLOR_NAMES[2]);   // 輸出：3 GREEN BLUE
```

新增顏色只要改 `COLORS` 那一行，enum 和字串表會自動同步。

## 5.4 inline 函式：取代函式巨集

```c
static inline int square_fn(int x) { return x * x; }
```

- 有型別檢查、參數只計算一次（2.4 節的陷阱都沒有）。
- 開了最佳化（`-O2`）時，編譯器會把呼叫直接展開，和巨集一樣快。
- 可以放在標頭檔裡（要加 `static`，否則會有 4.4 節的「多重定義」問題）。

**建議**：能寫成 `static inline` 函式的就不要用巨集。巨集只用在函式做不到的事：不限型別（`MAX`）、字串化（`SHOW`）、條件編譯、引入防護、X 巨集。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 前置處理器 | Preprocessor | 編譯前做文字替換的程式 | 1.2 |
| 目的檔 | Object File (`.o`) | 編譯好、還沒連結的機器碼 | 1.1 |
| 連結 | Linking | 把多個目的檔和函式庫接成執行檔 | 1.1 |
| 巨集 | Macro | `#define` 定義的文字替換規則 | 2.1 |
| 字串化 | Stringification (`#`) | 把巨集參數變成字串 | 2.5 |
| 記號拼接 | Token Pasting (`##`) | 把兩段文字接成一個名字 | 2.5 |
| 條件編譯 | Conditional Compilation | 依條件決定要編譯哪些程式碼 | 3.1 |
| 斷言 | Assertion | 檢查「不可能發生」的情況 | 3.4 |
| 標頭檔 | Header File (`.h`) | 放宣告、給別人 include 的檔案 | 4.1 |
| 引入防護 | Include Guard | 防止同一個標頭檔被貼兩次 | 4.3 |
| 內部連結 | Internal Linkage | `static`：只有自己的檔案看得到 | 4.5 |
| 外部連結 | External Linkage | 其他檔案可以用 `extern` 存取 | 4.5 |
| X 巨集 | X Macro | 一份清單套用不同巨集產生多種程式碼 | 5.3 |

---

# 習題

### 題 1：預測輸出

```c
#define ADD(a, b) a + b
#define MUL(a, b) a * b
printf("%d\n", 2 * ADD(3, 4));
printf("%d\n", MUL(1 + 1, 2 + 2));
```

把兩個巨集改成什麼樣子，才會得到「直覺上」的結果 14 和 8？

### 題 2：下面的巨集有什麼問題？

```c
#define ABS(x) ((x) < 0 ? -(x) : (x))
int i = -3;
int r = ABS(i--);
```

### 題 3：`gcc main.c -o main` 出現下面的錯誤，是哪一個步驟出錯？可能的原因是什麼？

```
/usr/bin/ld: /tmp/ccX.o: in function `main':
main.c:(.text+0x1e): undefined reference to `list_push'
```

### 題 4：`util.h` 的內容如下，被 `a.c` 和 `b.c` 同時 include，編譯 `gcc a.c b.c` 會發生什麼事？怎麼修正？

```c
#ifndef UTIL_H
#define UTIL_H
int verbose = 0;
int clamp(int x, int lo, int hi) { return x < lo ? lo : x > hi ? hi : x; }
#endif
```

### 題 5：下面的巨集用在 `if` / `else` 裡會出什麼問題？怎麼修正？

```c
#define RESET(p) free(p); p = NULL
if (done) RESET(buf);
```

### 題 6：在 `-DNDEBUG` 下，下面的程式會有什麼不同？

```c
assert((fp = fopen("data.txt", "r")) != NULL);
```

### 題 7：一個模組 `queue` 有公開函式 `queue_push`、`queue_pop`，以及只有自己用的輔助函式 `grow`。哪些要寫在 `queue.h`？`grow` 應該怎麼宣告？

---

# 習題解答

**題 1**：輸出 `10` 和 `5`。
- `2 * ADD(3, 4)` → `2 * 3 + 4` = 10。
- `MUL(1 + 1, 2 + 2)` → `1 + 1 * 2 + 2` = 5。

修正成 `#define ADD(a, b) ((a) + (b))`、`#define MUL(a, b) ((a) * (b))`，就會得到 14 和 8。

**題 2**：展開成 `((i--) < 0 ? -(i--) : (i--))`，`i--` 被執行 **兩次**：`r` 是 `-(-4)` = 4（不是 3），`i` 變成 -5（不是 -4）。不要把有副作用的運算式傳給巨集；改用 `static inline int abs_int(int x)`，或用標準函式 `abs`（`<stdlib.h>`）。

**題 3**：**連結** 步驟（訊息來自 `ld`）。程式碼語法正確，但找不到 `list_push` 的定義。可能的原因：`list_push` 寫在另一個 `.c` 檔（例如 `list.c`），但編譯時沒有一起編譯 —— 應該 `gcc main.c list.c -o main`；或者函式名字拼錯；或者 `list_push` 被宣告成 `static`。

**題 4**：連結錯誤 `multiple definition of 'verbose'` 和 `multiple definition of 'clamp'`：`a.c`、`b.c` 各自得到一份定義。引入防護只對單一 `.c` 檔有效。修正：

```c
/* util.h */
#ifndef UTIL_H
#define UTIL_H
extern int verbose;                                /* 宣告 */
static inline int clamp(int x, int lo, int hi) {   /* static inline：每個檔案各自一份，不衝突 */
    return x < lo ? lo : x > hi ? hi : x;
}
#endif

/* util.c */
#include "util.h"
int verbose = 0;                                   /* 定義：只有這裡 */
```

（`clamp` 也可以改成在 `.h` 只寫原型、本體放到 `util.c`。）

**題 5**：展開成 `if (done) free(buf); buf = NULL;`，只有 `free(buf)` 受 `if` 控制，`buf = NULL` **永遠** 會執行。如果後面還有 `else`，會變成編譯錯誤。修正：

```c
#define RESET(p) do { free(p); (p) = NULL; } while (0)
```

**題 6**：定義了 `NDEBUG` 時，整個 `assert(...)` 會被刪掉，**連 `fopen` 也不會執行**，`fp` 沒有被設定。正確寫法是分開：

```c
fp = fopen("data.txt", "r");
if (fp == NULL) { perror("data.txt"); return 1; }   /* 開檔失敗是「執行時的錯誤」，不該用 assert */
```

**題 7**：`queue.h` 放 `Queue` 型別、`queue_push`、`queue_pop` 的原型（和引入防護）。`grow` **不要** 寫在 `queue.h`，在 `queue.c` 裡定義成 `static void grow(Queue *q) { ... }`，其他檔案就看不到也呼叫不到它。
