# 14. 編譯模型：前置處理、編譯、連結

> 程式練習：本課沒有評測題，建議照著第三部分自己建立一個多檔案的小專案。
>
> 先備知識：第 01 課「宣告與定義」、第 10 課「模板要寫在標頭檔」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 從原始碼到執行檔 | 前置處理 → 編譯 → 組譯 → 連結，每一步做了什麼、怎麼親眼看到 |
| 第二部分 | 前置處理器 | `#include`、巨集的每一種陷阱、`#` 與 `##`、預先定義的巨集、條件編譯、標頭檔防護 |
| 第三部分 | 多檔案專案 | 一個完整的專案、標頭檔放什麼、原始檔放什麼、前置宣告 |
| 第四部分 | 連結與 ODR | 「undefined reference」和「multiple definition」從哪來、`extern`、`inline` 變數、內部 / 外部連結 |
| 第五部分 | 命名空間 | 為什麼需要、怎麼定義和使用、別名、匿名命名空間、ADL、為什麼不要在標頭檔寫 `using namespace std` |
| 第六部分 | static 的多種意思與初始化順序 | 同一個關鍵字四種意思、靜態初始化順序問題、`main` 函式 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。本課的編譯錯誤、連結錯誤訊息都是實際用 `g++` 產生的（暫存檔名如 `/tmp/ccXXXX.o` 每次會不同）。標 🔍 的是深入內容。

---

# 第一部分：從原始碼到執行檔

## 1.1 四個步驟

```
main.cpp ──①前置處理──▶ 展開後的原始碼 ──②編譯──▶ 組合語言 ──③組譯──▶ main.o ─┐
math.cpp ──①──────────▶ ...              ──②────▶ ...      ──③────▶ math.o ─┼─④連結──▶ 執行檔
                                                                 標準函式庫 ─┘
```

| 步驟 | 英文 | 做什麼 | 想自己看 |
|---|---|---|---|
| ① 前置處理 | Preprocessing | 處理 `#include`、`#define`、`#if`：純粹的 **文字替換** | `g++ -E main.cpp` |
| ② 編譯 | Compilation | 檢查語法和型別，把 C++ 翻譯成組合語言 | `g++ -S main.cpp`（產生 `main.s`） |
| ③ 組譯 | Assembly | 把組合語言翻成機器碼，產生 **目的檔 (object file)** `.o` | `g++ -c main.cpp`（產生 `main.o`） |
| ④ 連結 | Linking | 把所有 `.o` 和函式庫 **接起來**，填上函式之間的位址 | `g++ main.o math.o -o app` |

`g++ main.cpp -o app` 一行就把四步驟都做完了（中間檔案放在暫存目錄、用完就刪掉）。

**比喻**：出版一本書。
- ① 前置處理：把「見附錄 A」的地方，直接把附錄 A 的內容貼進來。
- ② ③ 編譯組譯：每一章各自翻譯成外文（每一章獨立翻譯，翻譯第 3 章時不知道第 5 章寫了什麼）。
- ④ 連結：把所有章節裝訂成一本書，並填上「詳見第 128 頁」這類跨章節的頁碼。

### 親眼看到前置處理的結果

```cpp
// m.cpp
#define PI 3.14159
#define SQUARE(x) x * x
double area = PI * SQUARE(1 + 2);
```

```bash
$ g++ -E -P m.cpp          # -E：只做前置處理；-P：不要印出行號標記
double area = 3.14159 * 1 + 2 * 1 + 2;
```

巨集被 **逐字替換** 了，而且 `SQUARE(1 + 2)` 變成了 `1 + 2 * 1 + 2`（2.2 節的陷阱）。`#include <iostream>` 經過 `-E` 會展開成好幾萬行 —— 那就是編譯器真正看到的東西。

## 1.2 編譯單元 (Translation Unit)

**是什麼**：一個 `.cpp` 檔 **經過前置處理之後**（所有 `#include` 都展開了）的完整內容。編譯器 **一次只處理一個編譯單元**，而且 **看不到其他編譯單元的內容**。

這就是為什麼：
- 要呼叫別的檔案裡的函式，必須先有 **宣告**（通常來自 `#include` 的標頭檔）—— 編譯器只要知道「有這個函式、它長什麼樣子」就能產生呼叫的程式碼，位址留給連結器填。
- 錯誤分成兩種：
  - **編譯錯誤**：某個編譯單元本身有問題（語法、型別、沒宣告）。訊息格式是 `檔名:行:列: error: ...`。
  - **連結錯誤**：各個編譯單元之間對不起來（找不到定義、重複定義）。訊息來自 `ld`（連結器），通常 **沒有行號**，最後一行是 `collect2: error: ld returned 1 exit status`。

```
// 編譯錯誤：呼叫了沒宣告的函式
u.cpp:1:13: error: 'foo' was not declared in this scope

// 連結錯誤：有宣告、沒定義
/usr/bin/ld: ... undefined reference to `S::n'
collect2: error: ld returned 1 exit status
```

**看到 `ld returned 1 exit status` 就知道是連結錯誤**：程式碼本身的語法都對，問題在於「某個東西的定義找不到 / 有好幾個」。

## 1.3 🔍 目的檔裡有什麼：符號表

每個 `.o` 都有一張 **符號表 (symbol table)**，記錄「我定義了哪些東西」和「我需要哪些東西」。用 `nm -C` 可以看：

```bash
$ nm -C fraction.o | grep Fraction
0000000000000000 T Fraction::Fraction(long long, long long)
00000000000000be T Fraction::operator+(Fraction const&) const
000000000000014f T operator<<(std::ostream&, Fraction const&)

$ nm -C main.o | grep Fraction
                 U Fraction::Fraction(long long, long long)
                 U Fraction::operator+(Fraction const&) const
                 U operator<<(std::ostream&, Fraction const&)
```

- `T`（text）：**我定義了** 這個函式。
- `U`（undefined）：**我需要** 這個函式，但我沒有它的定義。

連結器的工作就是：把每個 `U` 對應到某個 `.o` 裡的 `T`。找不到 → `undefined reference`；找到兩個 → `multiple definition`。

---

# 第二部分：前置處理器 (Preprocessor)

以 `#` 開頭的那一行叫 **前置處理指令 (preprocessor directive)**，在編譯之前就被處理掉了。

## 2.1 #include：複製貼上

**是什麼**：`#include` 就是把那個檔案的 **全部內容，原封不動貼在這裡**。

```cpp
#include <vector>       // 角括號：到系統 / 標準函式庫的目錄找
#include "math.h"       // 雙引號：先在目前的目錄找，找不到再去系統目錄
```

**慣例**：標準函式庫和第三方函式庫用 `<>`，自己專案的檔案用 `""`。

`#include <bits/stdc++.h>` 會引入 **整個標準函式庫**（GCC 專用，其他編譯器沒有），編譯會比較慢，競賽常用，正式專案不要用。

**常見錯誤**：
- 檔名打錯或路徑不對：`fatal error: math.h: No such file or directory`。
- `#include` 了 `.cpp` 檔：會把整個實作貼進來，多個檔案都 include 時就會重複定義（4.2 節）。**只 include 標頭檔**。

## 2.2 巨集 (Macro)

**是什麼**：`#define` 定義的 **文字替換規則**。前置處理器看到名稱就直接替換，**完全不懂 C++ 的語法和型別**。

```cpp
#define PI 3.14159               // 物件式巨集 (object-like macro)
#define SQUARE(x) ((x) * (x))    // 函式式巨集 (function-like macro)

cout << PI * 2 << ' ' << SQUARE(5) << '\n';   // 輸出：6.28318 25
```

**比喻**：巨集像是文書軟體的「全部取代」功能 —— 它不管你取代的是不是一個完整的詞，只要文字符合就換掉。

### 陷阱 1：參數沒有括號

```cpp
#define BAD_SQUARE(x) x * x
cout << BAD_SQUARE(1 + 2) << '\n';     // 展開成 1 + 2 * 1 + 2 → 輸出：5（不是 9）
cout << SQUARE(1 + 2) << '\n';         // 展開成 ((1 + 2) * (1 + 2)) → 輸出：9
```

### 陷阱 2：整體沒有括號

```cpp
#define BAD_DOUBLE(x) (x) + (x)
cout << BAD_DOUBLE(3) * 10 << '\n';    // 展開成 (3) + (3) * 10 → 輸出：33（不是 60）
#define DOUBLE(x) ((x) + (x))
cout << DOUBLE(3) * 10 << '\n';        // 輸出：60
```

**規則**：每個參數加括號、整個運算式也加括號。

### 陷阱 3：參數被計算很多次

```cpp
#define MAX(a, b) ((a) > (b) ? (a) : (b))
int i = 5;
int m = MAX(i++, 3);         // 展開成 ((i++) > (3) ? (i++) : (3))：i 被加了兩次！
cout << m << ' ' << i << '\n';   // 輸出：6 7
```

加括號也救不了這個問題。用函式就沒有這個問題：`std::max(i++, 3)` 只會加一次。

### 陷阱 4：沒有作用域、沒有型別檢查

```cpp
#define SIZE 100
void f() {
    // int SIZE = 5;          // ❌ 展開成 int 100 = 5; → error: expected unqualified-id before numeric constant
}
```

巨集不屬於任何命名空間或作用域，一旦定義，後面 **所有地方** 的同名文字都會被替換，錯誤訊息指向替換後的結果，很難看懂。所以巨集名稱習慣 **全部大寫**，避免和一般名稱撞在一起。

### 現代 C++ 的替代品

| 用途 | 不要用 | 改用 | 好處 |
|---|---|---|---|
| 常數 | `#define N 100` | `constexpr int N = 100;` | 有型別、有作用域 |
| 小函式 | `#define SQUARE(x) ...` | `constexpr` / `inline` 函式或函式模板 | 參數只計算一次、有型別檢查 |
| 型別別名 | `#define ll long long` | `using ll = long long;` | 是真正的型別名稱 |

```cpp
constexpr int square(int x) { return x * x; }
int j = 5;
cout << square(j++) << ' ' << j << '\n';   // 輸出：25 6（只加一次）
```

**巨集仍然有用的地方**：條件編譯（2.5 節）、標頭檔防護（2.6 節）、需要 `__FILE__` / `__LINE__` 的除錯工具（下一節）。

## 2.3 🔍 # 和 ##：字串化與連接

```cpp
#define SHOW(expr) cout << #expr << " = " << (expr) << '\n'   // #expr：把參數變成字串
#define MAKE_VAR(name, n) int name##n = n                     // ##：把兩段文字黏成一個名字

int x = 7;
SHOW(x * 2 + 1);          // 輸出：x * 2 + 1 = 15
MAKE_VAR(value, 3);       // 展開成 int value3 = 3;
cout << value3 << '\n';   // 輸出：3
```

`SHOW` 這種巨集在除錯時很好用：同時印出「運算式本身」和「它的值」，這是一般函式做不到的。

## 2.4 預先定義的巨集

編譯器自動定義了一些巨集：

| 巨集 | 意思 |
|---|---|
| `__FILE__` | 目前的檔名（字串） |
| `__LINE__` | 目前的行號（整數） |
| `__func__` | 目前的函式名稱（嚴格來說不是巨集，是編譯器提供的變數） |
| `__cplusplus` | C++ 標準版本：C++17 是 `201703L`、C++20 是 `202002L` |
| `__GNUC__` | 是 GCC 編譯的嗎（值是主版本號） |
| `_WIN32` / `__linux__` / `__APPLE__` | 作業系統 |

```cpp
#define LOG(msg) cerr << "[" << __FILE__ << ":" << __LINE__ << " " << __func__ << "] " << msg << '\n'

void process() {
    LOG("開始處理");          // 輸出（到 cerr）：[main.cpp:4 process] 開始處理
}
cout << __cplusplus << '\n';  // 用 -std=c++17 編譯 → 輸出：201703
```

`assert`（第 09 課）就是用 `__FILE__`、`__LINE__` 印出失敗的位置。

## 2.5 條件編譯 (Conditional Compilation)

**是什麼**：依照條件決定 **哪些程式碼要被編譯**。沒被選中的程式碼在前置處理時就被刪掉，編譯器根本看不到。

```cpp
#ifdef DEBUG
    cerr << "x = " << x << '\n';     // 只有定義了 DEBUG 才會被編譯
#endif

#if defined(_WIN32)
    // Windows 專用的程式碼
#elif defined(__linux__)
    // Linux 專用的程式碼
#else
    // 其他
#endif
```

| 指令 | 意思 |
|---|---|
| `#ifdef X` | 如果定義了 X |
| `#ifndef X` | 如果 **沒有** 定義 X |
| `#if 運算式` | 如果運算式（整數常數）不是 0 |
| `#elif` / `#else` / `#endif` | 否則如果 / 否則 / 結束 |
| `#undef X` | 取消定義 X |

**編譯時用 `-D` 定義巨集**：

```cpp
// debug.cpp
#include <iostream>
int main() {
#ifdef DEBUG
    std::cout << "除錯模式\n";
#else
    std::cout << "正式模式\n";
#endif
}
```

```bash
$ g++ debug.cpp -o d && ./d
正式模式
$ g++ -DDEBUG debug.cpp -o d && ./d
除錯模式
```

`assert` 就是用 `NDEBUG` 這個巨集控制的：`g++ -DNDEBUG` 會移除所有 `assert`。本平台的 `--debug` 模式也是用 `-D_GLIBCXX_DEBUG` 讓標準函式庫進入「會檢查越界」的模式。

**暫時「註解掉」一大段程式碼**（裡面有 `/* */` 註解時，用 `/* */` 包會出問題）：

```cpp
#if 0
    ... 很多行程式碼，裡面還有 /* 註解 */ ...
#endif
```

## 2.6 標頭檔防護 (Include Guard)

**問題**：`a.h` 和 `b.h` 都 `#include "point.h"`，`main.cpp` 又同時引入 `a.h` 和 `b.h` → `point.h` 被貼進來 **兩次** → `struct Point` 被定義兩次 → 編譯錯誤。

```cpp
// point.h（沒有防護）
struct Point { int x, y; };

// g.cpp
#include "point.h"
#include "point.h"         // 實際情況通常是間接引入兩次
int main() {}
```

```
point.h:1:8: error: redefinition of 'struct Point'
```

**解法 1：#ifndef 防護**

```cpp
// point.h
#ifndef POINT_H         // 如果還沒定義 POINT_H
#define POINT_H         // 就定義它，並且引入下面的內容

struct Point { int x, y; };

#endif                  // 第二次被引入時，POINT_H 已經定義了，整段被跳過
```

巨集名稱要 **獨一無二**，習慣用「專案名_路徑_檔名_H」，例如 `MYPROJ_GEOMETRY_POINT_H`。

**解法 2：#pragma once**（幾乎所有編譯器都支援，比較簡潔）

```cpp
#pragma once
struct Point { int x, y; };
```

**每個標頭檔都要有標頭檔防護。**

---

# 第三部分：多檔案專案

## 3.1 一個完整的小專案

```
project/
├── fraction.h      ← 介面：類別定義、函式宣告
├── fraction.cpp    ← 實作：成員函式的定義
└── main.cpp        ← 使用者
```

```cpp
// fraction.h
#pragma once
#include <iosfwd>          // 只需要 ostream 的「宣告」，不需要整個 <iostream>

class Fraction {
    long long num_, den_;
public:
    Fraction(long long n = 0, long long d = 1);       // 宣告（預設引數寫在宣告這裡）
    Fraction operator+(const Fraction& o) const;
    long long num() const { return num_; }            // 寫在類別裡的函式自動是 inline，可以放標頭檔
    long long den() const { return den_; }
};
std::ostream& operator<<(std::ostream& os, const Fraction& f);
```

```cpp
// fraction.cpp
#include "fraction.h"      // 自己的標頭檔放第一個：確保它本身是完整的（沒有偷偷依賴別的 include）
#include <numeric>
#include <ostream>

Fraction::Fraction(long long n, long long d) : num_(n), den_(d) {   // 定義時「不要」再寫預設引數
    if (den_ < 0) { num_ = -num_; den_ = -den_; }
    long long g = std::gcd(num_, den_);
    if (g) { num_ /= g; den_ /= g; }
}
Fraction Fraction::operator+(const Fraction& o) const {
    return Fraction(num_ * o.den_ + o.num_ * den_, den_ * o.den_);
}
std::ostream& operator<<(std::ostream& os, const Fraction& f) {
    return os << f.num() << '/' << f.den();
}
```

```cpp
// main.cpp
#include "fraction.h"
#include <iostream>
int main() { std::cout << Fraction(1, 2) + Fraction(1, 3) << '\n'; }
```

編譯：

```bash
$ g++ -std=c++17 -c fraction.cpp          # 產生 fraction.o
$ g++ -std=c++17 -c main.cpp              # 產生 main.o
$ g++ fraction.o main.o -o app            # 連結
$ ./app
5/6
# 或一次完成：g++ -std=c++17 fraction.cpp main.cpp -o app
```

**忘了把 `fraction.cpp` 加進去**：

```bash
$ g++ main.cpp -o app
/usr/bin/ld: /tmp/cco7Mogg.o: in function `main':
main.cpp:(.text+0x2d): undefined reference to `Fraction::Fraction(long long, long long)'
main.cpp:(.text+0x56): undefined reference to `Fraction::operator+(Fraction const&) const'
main.cpp:(.text+0x74): undefined reference to `operator<<(std::ostream&, Fraction const&)'
collect2: error: ld returned 1 exit status
```

`main.cpp` 本身編譯成功了（有宣告），但連結時找不到這三個函式的定義。

**常見錯誤**：
- 預設引數在宣告和定義 **都寫** → `error: default argument given for parameter 1 of ...`。只寫在宣告（標頭檔）。
- 定義成員函式時忘了 `Fraction::` → 變成定義一個全域函式，連結時成員函式找不到定義。

## 3.2 標頭檔放什麼、原始檔放什麼

| 放在標頭檔 `.h` | 放在原始檔 `.cpp` |
|---|---|
| 類別的定義（成員宣告） | 成員函式的定義（本體） |
| 函式的 **宣告** | 函式的 **定義** |
| `inline` 函式、`constexpr` 函式 | 只在這個檔案用的輔助函式（放在匿名命名空間） |
| **模板**（宣告和定義都要，第 10 課） | 全域變數的定義 |
| `extern` 變數宣告、`inline` 變數（C++17）、`constexpr` 常數 | `static` 成員變數的定義（C++17 前） |
| 型別別名、`enum` | |

**判斷原則**：標頭檔會被 **很多個** `.cpp` 引入，所以只能放「出現很多份也沒關係」的東西（宣告、類別定義、inline 的東西、模板）；「只能有一份」的定義放 `.cpp`（4.1 節的 ODR）。

## 3.3 為什麼要分開？

1. **增量編譯 (incremental compilation)**：只改了 `fraction.cpp`，只要重新編譯 `fraction.cpp` 再連結，`main.cpp` 不用重編。大型專案可以從幾十分鐘縮短到幾秒。
2. **隱藏實作**：使用者只需要看標頭檔（介面），不用看實作細節（第 09 課）。
3. **減少相依**：標頭檔改了，所有 `#include` 它的檔案都要重新編譯，所以 **標頭檔越精簡越好**（能用前置宣告就不要 `#include`）。

## 3.4 前置宣告 (Forward Declaration)

**是什麼**：只告訴編譯器「**有這個類別**」，不提供定義。這時它是一個 **不完整型別 (incomplete type)**。

```cpp
class Engine;              // 前置宣告

class Car {
    Engine* engine_;       // ✅ 只用到指標或參考時，前置宣告就夠了（指標的大小是固定的）
    // Engine e_;          // ❌ error: field 'e_' has incomplete type 'Engine'（不知道 Engine 多大）
public:
    void start();          // 宣告可以用不完整型別
};
```

| 用 `class Engine;` 前置宣告之後 | 可以嗎？ |
|---|---|
| 宣告 `Engine*` / `Engine&` 變數、成員 | ✅ |
| 函式參數 / 回傳值是 `Engine`、`Engine&`（只是宣告） | ✅ |
| 建立 `Engine` 物件、`Engine` 型別的成員 | ❌ 要知道大小 |
| 呼叫 `engine_->start()`、存取成員 | ❌ 要知道有哪些成員 |
| `sizeof(Engine)`、繼承 `Engine` | ❌ |

**互相參考的類別** 一定要用前置宣告：

```cpp
class B;                   // 先宣告 B
class A { B* b; };         // A 用到 B 的指標
class B { A* a; };         // B 用到 A 的指標
```

實際的專案會用 **建置工具**（Make、CMake）自動追蹤哪些檔案需要重新編譯。

---

# 第四部分：連結與 ODR

## 4.1 單一定義規則 (One Definition Rule, ODR)

**是什麼**：
1. 在 **一個編譯單元** 裡，每個東西最多只能 **定義一次**。
2. 在 **整個程式** 裡，每個（非 inline 的）函式和變數 **只能定義一次**。
3. 類別、inline 函式、inline 變數、模板可以在多個編譯單元裡各定義一次（通常是透過標頭檔），但 **每一份都必須完全相同**。

**宣告 vs 定義**（第 01 課）：

| | 宣告（可以很多次） | 定義（只能一次） |
|---|---|---|
| 函式 | `int square(int x);` | `int square(int x) { return x * x; }` |
| 變數 | `extern int counter;` | `int counter = 0;` |
| 類別 | `class Engine;` | `class Engine { ... };` |

## 4.2 兩種經典的連結錯誤

### undefined reference（未定義的參考）

有宣告、有呼叫，但 **找不到定義**。

```
main.cpp:(.text+0x56): undefined reference to `Fraction::operator+(Fraction const&) const'
```

常見原因：
- 忘了把 `fraction.cpp` 加進編譯指令（3.1 節）。
- 宣告和定義的簽章不一樣（例如定義時少了 `const`、參數型別不同）。
- 模板的定義放在 `.cpp` 裡（第 10 課 5.2）。
- 宣告了 `static` 成員變數，但忘了定義它：

```cpp
struct S { static int n; };     // 只是宣告
int main() { return S::n; }
// /usr/bin/ld: s.cpp:(.text+0xa): undefined reference to `S::n'
// 修法：在 .cpp 加上 int S::n = 0;（或 C++17：inline static int n = 0;）
```

- 只宣告了函式、忘了寫定義（例如寫了解構子的宣告 `~Foo();` 卻沒有本體）。

### multiple definition（重複定義）

同一個東西在好幾個編譯單元裡都有 **定義**。

```cpp
// util.h
#pragma once
int counter = 0;                       // ❌ 定義放在標頭檔
int square(int x) { return x * x; }    // ❌ 非 inline 函式的定義放在標頭檔
```

```cpp
// a.cpp
#include "util.h"
int a() { return square(2) + counter; }
// b.cpp
#include "util.h"
int a();
int main() { return a() + square(3); }
```

```
$ g++ a.cpp b.cpp -o ab
/usr/bin/ld: /tmp/ccuPK3d6.o:(.bss+0x0): multiple definition of `counter'; /tmp/cct5LaUJ.o:(.bss+0x0): first defined here
/usr/bin/ld: /tmp/ccuPK3d6.o: in function `square(int)':
b.cpp:(.text+0x0): multiple definition of `square(int)'; /tmp/cct5LaUJ.o:a.cpp:(.text+0x0): first defined here
collect2: error: ld returned 1 exit status
```

`a.cpp` 和 `b.cpp` 都引入 `util.h` → 兩個編譯單元都有 `counter` 和 `square` 的定義 → 連結時重複定義。

**標頭檔防護救不了這個問題**：`#pragma once` 只能防止「同一個編譯單元」重複引入。`a.cpp` 和 `b.cpp` 是不同的編譯單元，各自引入一次，各自得到一份定義。

### 修法

```cpp
// util.h
#pragma once
extern int counter;                           // 1. 變數：標頭檔只放「宣告」
inline int square(int x) { return x * x; }    // 2. 函式：加 inline，允許多份相同的定義
inline int counter2 = 0;                      // 3. C++17 inline 變數：標頭檔裡直接定義，整個程式共用一份

// util.cpp
#include "util.h"
int counter = 0;                              // 變數唯一的定義
```

## 4.3 extern 與 inline 變數：跨檔案共用一個變數

**`extern`**：「這個變數 **在別的地方定義**，這裡只是宣告」。

**`inline` 變數（C++17）**：可以在多個編譯單元各寫一份定義，連結器會把它們 **合併成同一個**。

實驗：兩個檔案共用變數，各自修改，看看是不是同一份。

```cpp
// h1.cpp
#include <cstdio>
int counter = 0;                   // 定義
inline int counter2 = 0;           // inline 定義
void h1() { counter++; counter2++; }
```

```cpp
// h2.cpp
#include <cstdio>
extern int counter;                // 宣告：使用 h1.cpp 定義的那一個
inline int counter2 = 0;           // 另一份 inline 定義（和 h1.cpp 的合併成同一個）
void h1();
int main() {
    h1();
    counter++; counter2++;
    std::printf("counter=%d counter2=%d\n", counter, counter2);
}
```

```bash
$ g++ -std=c++17 h1.cpp h2.cpp -o hh && ./hh
counter=2 counter2=2               # 兩個檔案修改的是同一個變數
```

**全域變數的建議**：盡量少用（任何地方都能修改，很難追蹤）。真的需要時，`inline` 變數或 `constexpr` 常數放在標頭檔最簡單。

## 4.4 連結性 (Linkage)

**是什麼**：一個名字能不能被 **其他編譯單元** 看到。

| 連結性 | 意思 | 怎麼產生 |
|---|---|---|
| 外部連結 (external) | 整個程式都看得到 | 一般的全域函式、全域變數（預設） |
| 內部連結 (internal) | 只有這個編譯單元看得到 | `static` 全域函式 / 變數、匿名命名空間、`const` / `constexpr` 全域變數（預設） |
| 沒有連結 (none) | 只在作用域內 | 區域變數 |

**比喻**：外部連結是「公司的公開電話」，任何部門都能打；內部連結是「部門內的分機」，只有部門內部能用，所以不同部門可以有同號碼的分機。

**實驗：兩個檔案各有一個同名的內部連結變數和函式**

```cpp
// h1.cpp
static int helper_count = 1;                        // 內部連結
namespace { void log(const char* m) { std::printf("h1 log: %s\n", m); } }   // 匿名命名空間：內部連結
void h1() { log("hi"); helper_count++; std::printf("h1 sees helper_count=%d\n", helper_count); }

// h2.cpp
static int helper_count = 100;                      // 同名，但完全獨立
namespace { void log(const char* m) { std::printf("h2 log: %s\n", m); } }
void h1();
int main() { h1(); log("yo"); std::printf("h2 sees helper_count=%d\n", helper_count); }
```

```
h1 log: hi
h1 sees helper_count=2
h2 log: yo
h2 sees helper_count=100           # 各用各的，不會衝突，也不會出現 multiple definition
```

**規則**：只在一個 `.cpp` 裡用的輔助函式、變數，放進 **匿名命名空間**（現代 C++ 推薦）或加 `static`，避免和別的檔案撞名。

---

# 第五部分：命名空間 (Namespace)

## 5.1 為什麼需要？

**是什麼**：大型專案（加上各種函式庫）裡，很容易有兩個東西取了 **一樣的名字**。命名空間把名字分組，`geometry::Point` 和 `graphics::Point` 就不會衝突。

**比喻**：兩個班級都有一個叫「小明」的同學，叫「三年一班的小明」和「三年二班的小明」就分得清楚了。

```cpp
namespace geometry {
    struct Point { double x, y; };
    double distance(Point a, Point b) { return hypot(a.x - b.x, a.y - b.y); }
}
namespace graphics {
    struct Point { int x, y; };          // 同名，不會衝突
    void draw(Point p) { cout << "draw at " << p.x << ',' << p.y << '\n'; }
}

geometry::Point p{0, 0}, q{3, 4};
cout << geometry::distance(p, q) << '\n';     // 輸出：5
graphics::draw({1, 2});                       // 輸出：draw at 1,2
```

標準函式庫的所有東西都在 `std` 命名空間裡。

## 5.2 命名空間的寫法

### 可以分好幾段寫，甚至分在不同檔案

```cpp
namespace mylib { int a() { return 1; } }
namespace mylib { int b() { return a() + 1; } }   // 繼續往同一個命名空間加東西
cout << mylib::b() << '\n';                       // 輸出：2
```

（標頭檔裡寫 `namespace mylib { 宣告 }`，`.cpp` 裡寫 `namespace mylib { 定義 }`，就是這樣運作的。）

### 巢狀命名空間

```cpp
namespace company { namespace project { int version() { return 3; } } }
namespace company::project::util { int helper() { return 7; } }   // C++17 的簡寫
cout << company::project::version() << company::project::util::helper() << '\n';   // 輸出：37
```

### 命名空間別名

名字太長時取一個短的別名：

```cpp
namespace cpu = company::project::util;
cout << cpu::helper() << '\n';            // 輸出：7
namespace fs = std::filesystem;           // 常見用法（<filesystem>）
```

### 全域命名空間

不在任何命名空間裡的東西，在 **全域命名空間**，用 `::名稱` 明確指定：

```cpp
int value = 1;                            // 全域
namespace inner {
    int value = 2;
    int get_both() { return value * 10 + ::value; }   // value 是 inner::value，::value 是全域的
}
cout << inner::get_both() << '\n';        // 輸出：21
```

## 5.3 using 宣告與 using 指示

```cpp
using std::cout;            // using 宣告 (using-declaration)：只引入 cout 這一個名字
using namespace std;        // using 指示 (using-directive)：引入 std 裡的「所有」名字
```

```cpp
namespace tools {
    int add(int a, int b) { return a + b; }
    int mul(int a, int b) { return a * b; }
}
void f1() {
    using tools::add;                     // 只引入 add
    cout << add(2, 3) << '\n';            // 輸出：5
    // mul(2, 3);                         // ❌ mul 沒有被引入
}
void f2() {
    using namespace tools;                // 引入全部（只在這個函式裡有效）
    cout << mul(2, 3) << '\n';            // 輸出：6
}
```

**`using` 也有作用域**：寫在函式裡，只在那個函式裡有效。

### 為什麼 `using namespace std;` 有風險

`std` 裡有上千個名字（`count`、`distance`、`max`、`swap`、`size`、`data`……），很容易和你自己的名字撞在一起：

```cpp
#include <bits/stdc++.h>
using namespace std;
int count = 0;              // 和 std::count 衝突
int main() { count++; }
// error: reference to 'count' is ambiguous
```

**更隱密的情況**：沒有編譯錯誤，卻呼叫到不是你想要的函式（例如你的 `distance` 和 `std::distance` 參數剛好都能接受，多載解析挑了 `std` 的版本）。

**規則**：
- **絕對不要在標頭檔裡寫 `using namespace std;`** —— 所有引入這個標頭檔的檔案都會被污染，而且使用者無法取消。
- 在 `.cpp` 檔裡、或是小程式 / 競賽中，寫在 `.cpp` 裡通常可以接受（本平台的樣板就這樣寫）。
- 正式專案中，寫 `std::` 或只 `using` 需要的名字。

## 5.4 匿名命名空間 (Anonymous Namespace)

**是什麼**：沒有名字的命名空間。裡面的東西 **只有這個編譯單元看得到**（內部連結，4.4 節），但在這個檔案裡可以直接使用，不用加前綴。

```cpp
namespace {
    int call_count = 0;                   // 這個檔案私有的全域變數
    void bump() { call_count++; }         // 這個檔案私有的輔助函式
}
bump(); bump();
cout << call_count << '\n';               // 輸出：2
```

## 5.5 🔍 引數相依查找 (ADL)

```cpp
std::vector<int> v = {3, 1, 2};
sort(v.begin(), v.end());   // 沒寫 std::，也沒有 using namespace std，也能找到 std::sort？
```

**引數相依查找 (Argument-Dependent Lookup)**：呼叫一個 **沒有指定命名空間** 的函式時，編譯器除了在目前的作用域找，**也會到「引數型別所在的命名空間」去找**。`v.begin()` 的型別在 `std` 裡，所以會去 `std` 找 `sort`。

**自己的命名空間也一樣**：

```cpp
namespace shop {
    struct Item { string name; int price; };
    void print(const Item& it) { cout << it.name << " $" << it.price << '\n'; }
    Item operator+(const Item& a, const Item& b) { return {a.name + "+" + b.name, a.price + b.price}; }
}
shop::Item a{"pen", 10}, b{"ink", 5};
print(a);                  // 沒寫 shop::，但 a 的型別在 shop 裡 → ADL 找到 shop::print → 輸出：pen $10
print(a + b);              // operator+ 也是靠 ADL 找到的 → 輸出：pen+ink $15
```

**這就是為什麼運算子多載能運作**：`cout << x` 實際上是呼叫 `operator<<(cout, x)`，你不可能每次都寫 `std::operator<<(cout, x)`。ADL 讓編譯器自動到 `std`（`cout` 的型別所在）和 `x` 的型別所在的命名空間找 `operator<<`。所以 **自訂型別的運算子要定義在和型別相同的命名空間裡**。

---

# 第六部分：static 的多種意思與初始化順序

## 6.1 static 的四種意思

同一個關鍵字 `static`，在不同的地方意思完全不同：

| 位置 | 意思 | 第幾課 |
|---|---|---|
| 函式裡的區域變數 | **生命週期** 變成整個程式（值會保留到下次呼叫） | 第 01 課 |
| 全域變數 / 全域函式 | **內部連結**（只有這個檔案看得到） | 本課 4.4 |
| 類別的成員變數 | 屬於 **整個類別**，所有物件共用 | 第 07 課 |
| 類別的成員函式 | 屬於整個類別，**沒有 `this`** | 第 07 課 |

四種都放在一起看：

```cpp
static int file_private = 0;              // ② 內部連結：其他檔案看不到

int next_id() {
    static int id = 0;                    // ① 第一次呼叫時初始化，之後保留上次的值
    return ++id;
}

struct Widget {
    static int count;                     // ③ 所有 Widget 共用一份
    static Widget make() { count++; return Widget(); }   // ④ 沒有 this，用類別名稱呼叫
};
int Widget::count = 0;

cout << next_id() << next_id() << next_id() << '\n';   // 輸出：123
Widget::make(); Widget::make();
cout << Widget::count << ' ' << ++file_private << '\n';   // 輸出：2 1
```

## 6.2 🔍 靜態初始化順序問題 (Static Initialization Order Fiasco)

**問題**：
- **同一個** 編譯單元裡的全域物件：依照 **定義的順序** 初始化（有規定）。
- **不同** 編譯單元裡的全域物件：**初始化的先後順序沒有規定**。

```cpp
// ia.cpp
std::string greeting = "hello";

// ib.cpp
extern std::string greeting;
std::string message = greeting + " world";   // 如果 ib.cpp 先初始化，greeting 還沒建構
int main() { std::cout << "[" << message << "]\n"; }
```

實驗：改變連結的順序，結果就不一樣（GCC 通常依照命令列的順序初始化）：

```bash
$ g++ ia.cpp ib.cpp -o i1 && ./i1
[hello world]
$ g++ ib.cpp ia.cpp -o i2 && ./i2
[ world]                          # greeting 還沒初始化就被使用了（未定義行為，這次碰巧是空字串）
```

同一份程式碼，只是編譯指令的檔案順序不同，結果就不同 —— 這種 bug 非常難找。

**解法**：用函式裡的 `static` 區域變數（**第一次呼叫時** 才初始化，而且 C++11 起保證執行緒安全）：

```cpp
// ia.cpp
std::string& greeting() {
    static std::string g = "hello";   // 第一次呼叫 greeting() 時才建構
    return g;
}
// ib.cpp
std::string& greeting();
std::string message = greeting() + " world";   // 呼叫時一定會先初始化 → 永遠是 "hello world"
```

**比喻**：兩個人同時上台，誰先開口不知道。改成「需要的時候才請他上台」，就一定有人在台上。

**更好的做法**：避免讓全域物件的初始化依賴其他檔案的全域物件；常數用 `constexpr`（在編譯時就決定了，沒有順序問題）。

## 6.3 main 函式

- 程式從 `main` 開始執行（但全域物件的建構子在 `main` **之前** 就執行了，第 07 課 2.7 的實驗）。
- `main` 的回傳值是給作業系統的 **結束碼 (exit code)**：`0` 代表成功，非 0 代表失敗。評測系統看到非 0 的結束碼會判定為 RE。
- `main` 是唯一可以不寫 `return` 的回傳 `int` 的函式（預設回傳 0）。
- 在任何地方呼叫 `exit(n)` 也能結束程式（但區域物件的解構子不會執行）。

```cpp
// exitcode.cpp
int main() { return 3; }
```

```bash
$ g++ exitcode.cpp -o e && ./e; echo "結束碼 = $?"
結束碼 = 3
```

### 命令列參數

```cpp
// args.cpp
#include <iostream>
int main(int argc, char* argv[]) {          // argc：參數個數（含程式名稱）；argv：參數字串陣列
    for (int i = 0; i < argc; i++)
        std::cout << i << ": " << argv[i] << '\n';
}
```

```bash
$ ./args hello 42
0: ./args
1: hello
2: 42
```

`argv[0]` 是程式本身的名稱；參數都是 **字串**，要數字的話用 `stoi(argv[2])` 轉換（第 12 課）。`judge.py` 就是用命令列參數決定要執行哪一題（`python3 judge.py test 3`）。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 前置處理 | Preprocessing | 處理 #include、#define 的文字替換 | 1.1 |
| 目的檔 | Object File (.o) | 一個編譯單元的機器碼 | 1.1 |
| 連結 | Linking | 把目的檔接起來、填上位址 | 1.1 |
| 編譯單元 | Translation Unit | 一個 .cpp 展開所有 #include 之後的內容 | 1.2 |
| 符號表 | Symbol Table | 目的檔記錄「定義了什麼、需要什麼」 | 1.3 |
| 前置處理指令 | Preprocessor Directive | 以 # 開頭的那一行 | 2 |
| 巨集 | Macro | #define 定義的文字替換 | 2.2 |
| 字串化 / 連接 | Stringizing `#` / Token Pasting `##` | 巨集參數變字串 / 黏成一個名字 | 2.3 |
| 條件編譯 | Conditional Compilation | #ifdef / #if 選擇要編譯的程式碼 | 2.5 |
| 標頭檔防護 | Include Guard / #pragma once | 防止同一個標頭檔被引入兩次 | 2.6 |
| 增量編譯 | Incremental Compilation | 只重新編譯有修改的檔案 | 3.3 |
| 前置宣告 | Forward Declaration | 只宣告類別存在，不提供定義 | 3.4 |
| 不完整型別 | Incomplete Type | 只有宣告、還不知道大小的型別 | 3.4 |
| 單一定義規則 | ODR | 每個東西只能定義一次 | 4.1 |
| 連結錯誤 | Linker Error | undefined reference / multiple definition | 4.2 |
| inline 變數 | inline Variable | 標頭檔裡定義、整個程式共用一份（C++17） | 4.3 |
| 外部 / 內部連結 | External / Internal Linkage | 整個程式 / 只有這個檔案看得到 | 4.4 |
| 命名空間 | Namespace | 把名字分組避免衝突 | 5.1 |
| 命名空間別名 | Namespace Alias | `namespace fs = std::filesystem;` | 5.2 |
| using 宣告 / 指示 | using-declaration / using-directive | 引入一個名字 / 引入全部名字 | 5.3 |
| 匿名命名空間 | Anonymous Namespace | 讓裡面的東西變成內部連結 | 5.4 |
| 引數相依查找 | ADL | 依引數型別所在的命名空間找函式 | 5.5 |
| 靜態初始化順序問題 | Static Initialization Order Fiasco | 不同檔案的全域物件初始化順序不確定 | 6.2 |
| 結束碼 | Exit Code | main 的回傳值，0 代表成功 | 6.3 |

---

# 習題

### 題 1：預測輸出

```cpp
#define DOUBLE(x) x + x
#define TRIPLE(x) ((x) * 3)
int a = 3;
cout << DOUBLE(a) * 2 << ' ' << TRIPLE(a + 1);
```

### 題 2：這是編譯錯誤還是連結錯誤？

```
a) 呼叫了一個沒有宣告的函式
b) 呼叫了一個有宣告、但沒有任何地方定義的函式
c) 兩個 .cpp 檔都定義了同名的全域函式 int helper()
d) 型別錯誤：把 string 傳給需要 int 的函式
```

### 題 3：`util.h` 被 `a.cpp` 和 `b.cpp` 引入，哪幾行會造成連結錯誤？

```cpp
#pragma once
int g1 = 0;                              // ①
extern int g2;                           // ②
const int g3 = 0;                        // ③
int f1() { return 1; }                   // ④
inline int f2() { return 2; }            // ⑤
static int f3() { return 3; }            // ⑥
template <class T> T f4(T x) { return x; }   // ⑦
```

### 題 4：為什麼不能在標頭檔裡寫 `using namespace std;`？

### 題 5：只修改了 `fraction.cpp`（沒有改 `fraction.h`），哪些檔案需要重新編譯？如果改的是 `fraction.h` 呢？

### 題 6：`#pragma once` 能防止題 3 的連結錯誤嗎？為什麼？

### 題 7：預測輸出

```cpp
#define MIN(a, b) ((a) < (b) ? (a) : (b))
int x = 2, y = 5;
int m = MIN(x++, y);
cout << m << ' ' << x;
```

### 題 8：預測輸出

```cpp
int v = 1;
namespace A {
    int v = 10;
    namespace B {
        int v = 100;
        int f() { return v + A::v + ::v; }
    }
}
cout << A::B::f();
```

### 題 9：下面的標頭檔有什麼問題？怎麼改？

```cpp
// shape.h
#include <vector>
using namespace std;
class Canvas;
class Shape {
    Canvas c_;
public:
    double area() const;
};
```

### 題 10：`a.cpp` 有 `int total = 0;`，`b.cpp` 想使用同一個 `total`，應該怎麼寫？如果 `b.cpp` 也寫 `int total = 0;` 會發生什麼事？

---

# 習題解答

**題 1**：`9 12`。`DOUBLE(a) * 2` 展開成 `a + a * 2` = `3 + 6` = 9（不是 12）；`TRIPLE(a + 1)` 有加括號，展開成 `((a + 1) * 3)` = 12。

**題 2**：
- a) **編譯錯誤**：編譯器在這個編譯單元裡找不到宣告（`'foo' was not declared in this scope`）。
- b) **連結錯誤**（undefined reference）：編譯通過了，但連結時找不到定義。
- c) **連結錯誤**（multiple definition）。
- d) **編譯錯誤**。

**題 3**：① 和 ④。它們是外部連結的 **定義**，兩個編譯單元各有一份 → 重複定義。
- ② 只是宣告。
- ③ 全域 `const` 變數預設是內部連結，每個檔案各有一份，不衝突。
- ⑤ `inline` 允許多份相同的定義。
- ⑥ `static` 是內部連結，每個檔案各有一份（但會浪費空間，通常不該這樣寫）。
- ⑦ 模板可以在多個編譯單元定義。

**題 4**：所有 `#include` 這個標頭檔的檔案（以及它們再引入的檔案）都會被迫引入 `std` 的所有名字，使用者 **無法取消**，很容易造成名稱衝突，而且衝突發生的位置跟真正的原因相距很遠，很難除錯。

**題 5**：只改 `fraction.cpp`：只需要重新編譯 `fraction.cpp`，再重新連結。改了 `fraction.h`：**所有** `#include "fraction.h"` 的檔案（`fraction.cpp` 和 `main.cpp`）都要重新編譯 —— 這就是為什麼標頭檔要盡量精簡、少改動。

**題 6**：**不能**。`#pragma once` 只防止 **同一個編譯單元** 裡重複引入同一個標頭檔。`a.cpp` 和 `b.cpp` 是 **不同的編譯單元**，各自引入一次，各自得到一份定義，連結時就重複了。

**題 7**：`3 4`。展開成 `((x++) < (y) ? (x++) : (y))`：第一個 `x++` 比較 `2 < 5` 成立（x 變成 3），然後執行第二個 `x++`，回傳 3（x 變成 4）。本來想取 `min(2, 5) = 2`，結果得到 3，而且 `x` 被加了兩次。

**題 8**：`111`。在 `B::f` 裡，`v` 找到最近的 `A::B::v` = 100；`A::v` = 10；`::v` 是全域的 = 1。

**題 9**：兩個問題：
1. **標頭檔裡寫了 `using namespace std;`**：會污染所有引入它的檔案。拿掉，改寫 `std::vector`。
2. **`Canvas c_;` 是不完整型別**：只有前置宣告 `class Canvas;`，不知道 `Canvas` 有多大，不能當成員（`error: field 'c_' has incomplete type 'Canvas'`）。改成 `#include "canvas.h"`，或者成員改成指標 / 參考 `Canvas* c_;`（只需要前置宣告）。
另外還缺少標頭檔防護 `#pragma once`。

**題 10**：`b.cpp` 寫 `extern int total;`（宣告，使用 `a.cpp` 的定義）。如果 `b.cpp` 也寫 `int total = 0;`，兩個編譯單元都有 `total` 的定義 → 連結錯誤 `multiple definition of 'total'`。（如果兩邊都寫 `static int total = 0;`，就會變成 **兩個獨立的變數**，不會有錯誤，但也不是「共用」了。）
