# 14. 編譯模型：前置處理、編譯、連結

> 程式練習：本課沒有評測題，建議照著第三部分自己建立一個多檔案的小專案。
>
> 先備知識：第 01 課「宣告與定義」、第 10 課「模板要寫在標頭檔」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 從原始碼到執行檔 | 前置處理 → 編譯 → 組譯 → 連結，每一步做了什麼 |
| 第二部分 | 前置處理器 | `#include`、巨集的陷阱、條件編譯、標頭檔防護 |
| 第三部分 | 多檔案專案 | 標頭檔放什麼、原始檔放什麼、怎麼編譯 |
| 第四部分 | 連結與 ODR | 「undefined reference」和「multiple definition」從哪來、內部 / 外部連結 |
| 第五部分 | 命名空間 | 為什麼需要、怎麼用、為什麼不要在標頭檔寫 `using namespace std` |
| 第六部分 | static 的多種意思與初始化順序 | 同一個關鍵字四種意思、靜態初始化順序問題 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

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
| ② 編譯 | Compilation | 檢查語法和型別，把 C++ 翻譯成組合語言 | `g++ -S main.cpp` |
| ③ 組譯 | Assembly | 把組合語言翻成機器碼，產生 **目的檔** `.o` | `g++ -c main.cpp` |
| ④ 連結 | Linking | 把所有 `.o` 和函式庫 **接起來**，填上函式之間的位址 | `g++ main.o math.o -o app` |

`g++ main.cpp -o app` 一行就把四步驟都做完了。

**比喻**：出版一本書。
- ① 前置處理：把「見附錄 A」的地方，直接把附錄 A 的內容貼進來。
- ② ③ 編譯組譯：每一章各自翻譯成外文（每一章獨立翻譯，翻譯第 3 章時不知道第 5 章寫了什麼）。
- ④ 連結：把所有章節裝訂成一本書，並填上「詳見第 128 頁」這類跨章節的頁碼。

## 1.2 編譯單元 (Translation Unit)

**白話**：一個 `.cpp` 檔 **經過前置處理之後**（所有 `#include` 都展開了）的完整內容。編譯器 **一次只處理一個編譯單元**，而且 **看不到其他編譯單元的內容**。

這就是為什麼：
- 要呼叫別的檔案裡的函式，必須先有 **宣告**（通常來自 `#include` 的標頭檔）—— 編譯器只要知道「有這個函式、它長什麼樣子」就能產生呼叫的程式碼，位址留給連結器填。
- 錯誤分成兩種：**編譯錯誤**（某個編譯單元本身有問題）和 **連結錯誤**（各個編譯單元之間對不起來）。

---

# 第二部分：前置處理器 (Preprocessor)

## 2.1 #include：複製貼上

**白話**：`#include` 就是把那個檔案的 **全部內容，原封不動貼在這裡**。

```cpp
#include <vector>       // 角括號：到系統 / 標準函式庫的目錄找
#include "math.h"       // 雙引號：先在目前的目錄找，找不到再去系統目錄
```

`#include <bits/stdc++.h>` 會引入 **整個標準函式庫**（GCC 專用，其他編譯器沒有），編譯會比較慢，競賽常用，正式專案不要用。

## 2.2 巨集 (Macro)

**白話**：`#define` 定義的 **文字替換規則**。前置處理器看到名稱就直接替換，**完全不懂 C++ 的語法和型別**。

```cpp
#define PI 3.14159
#define SQUARE(x) x * x
```

**陷阱 1：沒有括號**

```cpp
SQUARE(1 + 2)        // 展開成 1 + 2 * 1 + 2 = 5，不是 9
#define SQUARE(x) ((x) * (x))    // 每個參數和整體都要加括號
```

**陷阱 2：參數被計算很多次**

```cpp
#define MAX(a, b) ((a) > (b) ? (a) : (b))
int i = 5;
MAX(i++, 3);         // 展開成 ((i++) > (3) ? (i++) : (3))：i 被加了兩次！
```

**陷阱 3：沒有作用域、沒有型別檢查**，錯誤訊息很難懂。

**比喻**：巨集像是文書軟體的「全部取代」功能 —— 它不管你取代的是不是一個完整的詞，只要文字符合就換掉。

**現代 C++ 的替代品**：

| 用途 | 不要用 | 改用 |
|---|---|---|
| 常數 | `#define N 100` | `constexpr int N = 100;` |
| 小函式 | `#define SQUARE(x) ...` | `constexpr` / `inline` 函式或函式模板 |
| 型別別名 | `#define ll long long` | `using ll = long long;` |

## 2.3 條件編譯 (Conditional Compilation)

```cpp
#ifdef DEBUG
    cerr << "x = " << x << '\n';     // 只有定義了 DEBUG 才會被編譯
#endif

#if defined(_WIN32)
    // Windows 專用的程式碼
#elif defined(__linux__)
    // Linux 專用的程式碼
#endif
```

編譯時可以用 `-D` 定義巨集：`g++ -DDEBUG main.cpp`。`assert` 就是用 `NDEBUG` 這個巨集控制的：`g++ -DNDEBUG` 會移除所有 `assert`。

## 2.4 標頭檔防護 (Include Guard)

**問題**：`a.h` 和 `b.h` 都 `#include "point.h"`，`main.cpp` 又同時引入 `a.h` 和 `b.h` → `point.h` 被貼進來 **兩次** → `struct Point` 被定義兩次 → 編譯錯誤。

**解法**：

```cpp
// point.h
#ifndef POINT_H         // 如果還沒定義 POINT_H
#define POINT_H         // 就定義它，並且引入下面的內容

struct Point { int x, y; };

#endif                  // 第二次被引入時，POINT_H 已經定義了，整段被跳過
```

或者用幾乎所有編譯器都支援的簡寫：

```cpp
#pragma once
```

**每個標頭檔都要有標頭檔防護。**

---

# 第三部分：多檔案專案

## 3.1 一個小專案

```
project/
├── fraction.h      ← 介面：類別定義、函式宣告
├── fraction.cpp    ← 實作：成員函式的定義
└── main.cpp        ← 使用者
```

```cpp
// fraction.h
#pragma once
#include <iosfwd>          // 只需要 ostream 的宣告，不需要整個 <iostream>

class Fraction {
    long long num_, den_;
public:
    Fraction(long long n = 0, long long d = 1);
    Fraction operator+(const Fraction& o) const;
    long long num() const { return num_; }       // 寫在類別裡的函式自動是 inline，可以放標頭檔
    long long den() const { return den_; }
};
std::ostream& operator<<(std::ostream& os, const Fraction& f);
```

```cpp
// fraction.cpp
#include "fraction.h"
#include <numeric>
#include <ostream>

Fraction::Fraction(long long n, long long d) : num_(n), den_(d) { /* 正規化 */ }
Fraction Fraction::operator+(const Fraction& o) const { return Fraction(num_ * o.den_ + o.num_ * den_, den_ * o.den_); }
std::ostream& operator<<(std::ostream& os, const Fraction& f) { return os << f.num() << '/' << f.den(); }
```

```cpp
// main.cpp
#include "fraction.h"
#include <iostream>
int main() { std::cout << Fraction(1, 2) + Fraction(1, 3) << '\n'; }
```

編譯：

```bash
g++ -c fraction.cpp          # 產生 fraction.o
g++ -c main.cpp              # 產生 main.o
g++ fraction.o main.o -o app # 連結
# 或一次完成：g++ fraction.cpp main.cpp -o app
```

## 3.2 標頭檔放什麼、原始檔放什麼

| 放在標頭檔 `.h` | 放在原始檔 `.cpp` |
|---|---|
| 類別的定義（成員宣告） | 成員函式的定義（本體） |
| 函式的 **宣告** | 函式的 **定義** |
| `inline` 函式、`constexpr` 函式 | 只在這個檔案用的輔助函式（放在匿名命名空間） |
| **模板**（宣告和定義都要，第 10 課） | 全域變數的定義 |
| `extern` 變數宣告、`inline` 變數（C++17） | |

## 3.3 為什麼要分開？

1. **增量編譯 (incremental compilation)**：只改了 `fraction.cpp`，只要重新編譯 `fraction.cpp` 再連結，`main.cpp` 不用重編。大型專案可以從幾十分鐘縮短到幾秒。
2. **隱藏實作**：使用者只需要看標頭檔（介面），不用看實作細節（第 09 課）。
3. **減少相依**：標頭檔改了，所有 `#include` 它的檔案都要重新編譯，所以 **標頭檔越精簡越好**（能用前置宣告就不要 `#include`）。

**前置宣告 (forward declaration)**：只告訴編譯器「有這個類別」，不提供定義：

```cpp
class Engine;              // 前置宣告
class Car {
    Engine* engine_;       // 只用到指標或參考時，前置宣告就夠了（指標的大小是固定的）
};
```

實際的專案會用 **建置工具**（Make、CMake）自動追蹤哪些檔案需要重新編譯。

---

# 第四部分：連結與 ODR

## 4.1 單一定義規則 (One Definition Rule, ODR)

**白話**：
1. 在 **一個編譯單元** 裡，每個東西最多只能 **定義一次**。
2. 在 **整個程式** 裡，每個（非 inline 的）函式和變數 **只能定義一次**。
3. 類別、inline 函式、模板可以在多個編譯單元裡各定義一次（通常是透過標頭檔），但 **每一份都必須完全相同**。

## 4.2 兩種經典的連結錯誤

**undefined reference（未定義的參考）**：有宣告、有呼叫，但 **找不到定義**。

```
main.o: in function `main': undefined reference to `Fraction::operator+(Fraction const&) const'
```

常見原因：
- 忘了把 `fraction.cpp` 加進編譯指令。
- 宣告和定義的簽章不一樣（例如定義時少了 `const`）。
- 模板的定義放在 `.cpp` 裡（第 10 課）。
- 宣告了 `static` 成員變數，但忘了在 `.cpp` 裡定義它。

**multiple definition（重複定義）**：同一個東西在好幾個編譯單元裡都有 **定義**。

```cpp
// util.h
int counter = 0;                       // ❌ 定義放在標頭檔
int square(int x) { return x * x; }    // ❌ 非 inline 函式的定義放在標頭檔
```

`a.cpp` 和 `b.cpp` 都引入 `util.h` → 兩個編譯單元都有 `counter` 和 `square` 的定義 → 連結時重複定義。
（標頭檔防護 **救不了** 這個問題：防護只能防止「同一個編譯單元」重複引入。）

修法：

```cpp
// util.h
extern int counter;                           // 宣告
inline int square(int x) { return x * x; }    // inline：允許多份相同的定義
inline int counter2 = 0;                      // C++17 inline 變數
// util.cpp
int counter = 0;                              // 唯一的定義
```

## 4.3 連結性 (Linkage)

**白話**：一個名字能不能被 **其他編譯單元** 看到。

| 連結性 | 意思 | 怎麼產生 |
|---|---|---|
| 外部連結 (external) | 整個程式都看得到 | 一般的全域函式、全域變數（預設） |
| 內部連結 (internal) | 只有這個編譯單元看得到 | `static` 全域函式 / 變數、匿名命名空間、`const` 全域變數（預設） |
| 沒有連結 (none) | 只在作用域內 | 區域變數 |

**比喻**：外部連結是「公司的公開電話」，任何部門都能打；內部連結是「部門內的分機」，只有部門內部能用。

```cpp
// helper.cpp
static int helper_count = 0;        // 其他檔案看不到，也不會跟其他檔案的同名變數衝突
namespace {                         // 匿名命名空間：裡面的東西都是內部連結（現代 C++ 推薦的寫法）
    void log(const char* msg) { }
}
```

**規則**：只在一個 `.cpp` 裡用的輔助函式，放進 **匿名命名空間**，避免和別的檔案撞名。

---

# 第五部分：命名空間 (Namespace)

## 5.1 為什麼需要？

**白話**：大型專案（加上各種函式庫）裡，很容易有兩個東西取了 **一樣的名字**。命名空間把名字分組，`A::Point` 和 `B::Point` 就不會衝突。

**比喻**：兩個班級都有一個叫「小明」的同學，叫「三年一班的小明」和「三年二班的小明」就分得清楚了。

```cpp
namespace geometry {
    struct Point { double x, y; };
    double distance(Point a, Point b);
}
namespace graphics {
    struct Point { int x, y; };          // 不會衝突
}
geometry::Point p{1.0, 2.0};
geometry::distance(p, p);

namespace geometry::shapes { ... }      // C++17：巢狀命名空間的簡寫
```

標準函式庫的所有東西都在 `std` 命名空間裡。

## 5.2 using 宣告與 using 指示

```cpp
using std::cout;            // using 宣告：只引入 cout
using namespace std;        // using 指示：引入 std 裡的「所有」名字
```

**為什麼 `using namespace std;` 有風險**：`std` 裡有上千個名字（`count`、`distance`、`max`、`swap`、`size`……），很容易和你自己的名字撞在一起：

```cpp
using namespace std;
int count = 0;              // 和 std::count 衝突
int main() { count++; }     // ❌ 編譯錯誤：reference to 'count' is ambiguous
```

**規則**：
- **絕對不要在標頭檔裡寫 `using namespace std;`** —— 所有引入這個標頭檔的檔案都會被污染，而且使用者無法取消。
- 在 `.cpp` 檔裡、或是小程式 / 競賽中，寫在 `.cpp` 裡通常可以接受（本平台的樣板就這樣寫）。
- 正式專案中，寫 `std::` 或只 `using` 需要的名字。

## 5.3 🔍 引數相依查找 (ADL)

```cpp
std::vector<int> v;
sort(v.begin(), v.end());   // 沒寫 std:: 也能找到 std::sort？
```

**引數相依查找 (Argument-Dependent Lookup)**：呼叫函式時，編譯器除了在目前的作用域找，**也會到「引數型別所在的命名空間」去找**。`v.begin()` 的型別在 `std` 裡，所以會去 `std` 找 `sort`。`cout << x` 能找到 `std::operator<<` 也是因為 ADL。

---

# 第六部分：static 的多種意思與初始化順序

## 6.1 static 的四種意思

同一個關鍵字 `static`，在不同的地方意思完全不同：

| 位置 | 意思 | 第幾課 |
|---|---|---|
| 函式裡的區域變數 | **生命週期** 變成整個程式（值會保留到下次呼叫） | 第 01 課 |
| 全域變數 / 全域函式 | **內部連結**（只有這個檔案看得到） | 本課 |
| 類別的成員變數 | 屬於 **整個類別**，所有物件共用 | 第 07 課 |
| 類別的成員函式 | 屬於整個類別，**沒有 `this`** | 第 07 課 |

## 6.2 🔍 靜態初始化順序問題 (Static Initialization Order Fiasco)

**問題**：不同編譯單元裡的全域物件，**初始化的先後順序沒有規定**。

```cpp
// a.cpp
std::string greeting = "hello";
// b.cpp
extern std::string greeting;
std::string message = greeting + " world";   // 如果 b.cpp 先初始化，greeting 還是空的（甚至還沒建構）
```

**解法**：用函式裡的 `static` 區域變數（第一次呼叫時才初始化，而且 C++11 起保證執行緒安全）：

```cpp
std::string& greeting() {
    static std::string g = "hello";
    return g;
}
```

**比喻**：兩個人同時上台，誰先開口不知道。改成「需要的時候才請他上台」，就一定有人在台上。

## 6.3 main 函式

- 程式從 `main` 開始執行（但全域物件的建構子在 `main` **之前** 就執行了）。
- `main` 的回傳值是給作業系統的 **結束碼**：`0` 代表成功，非 0 代表失敗。評測系統看到非 0 的結束碼會判定為 RE。
- `main` 是唯一可以不寫 `return` 的回傳 `int` 的函式（預設回傳 0）。
- `int main(int argc, char* argv[])`：可以接收命令列參數。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 前置處理 | Preprocessing | 處理 #include、#define 的文字替換 | 1.1 |
| 目的檔 | Object File (.o) | 一個編譯單元的機器碼 | 1.1 |
| 連結 | Linking | 把目的檔接起來、填上位址 | 1.1 |
| 編譯單元 | Translation Unit | 一個 .cpp 展開所有 #include 之後的內容 | 1.2 |
| 巨集 | Macro | #define 定義的文字替換 | 2.2 |
| 條件編譯 | Conditional Compilation | #ifdef / #if 選擇要編譯的程式碼 | 2.3 |
| 標頭檔防護 | Include Guard / #pragma once | 防止同一個標頭檔被引入兩次 | 2.4 |
| 增量編譯 | Incremental Compilation | 只重新編譯有修改的檔案 | 3.3 |
| 前置宣告 | Forward Declaration | 只宣告類別存在，不提供定義 | 3.3 |
| 單一定義規則 | ODR | 每個東西只能定義一次 | 4.1 |
| 連結錯誤 | Linker Error | undefined reference / multiple definition | 4.2 |
| 外部 / 內部連結 | External / Internal Linkage | 整個程式 / 只有這個檔案看得到 | 4.3 |
| 匿名命名空間 | Anonymous Namespace | 讓裡面的東西變成內部連結 | 4.3 |
| 命名空間 | Namespace | 把名字分組避免衝突 | 5.1 |
| 引數相依查找 | ADL | 依引數型別所在的命名空間找函式 | 5.3 |
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

---

# 習題解答

**題 1**：`9 12`。`DOUBLE(a) * 2` 展開成 `a + a * 2` = `3 + 6` = 9（不是 12）；`TRIPLE(a + 1)` 有加括號，展開成 `((a + 1) * 3)` = 12。

**題 2**：
- a) **編譯錯誤**：編譯器在這個編譯單元裡找不到宣告。
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
