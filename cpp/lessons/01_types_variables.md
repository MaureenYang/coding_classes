# 01. 型別、變數與型別轉換

> 程式練習：本課沒有獨立的程式題，觀念會在 `C01`、`C02`、`C13` 中反覆用到。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 型別系統 | 各種型別的大小與範圍「保證」是什麼、字面值的型別 |
| 第二部分 | 宣告、定義、初始化 | 五種初始化寫法的差別、未初始化的危險、`auto` |
| 第三部分 | `const` 與 `constexpr` | 「不能改」和「編譯期就知道」的差別 |
| 第四部分 | 作用域與生命週期 | 變數「在哪裡看得到」和「活多久」是兩件事 |
| 第五部分 | 型別轉換 | 隱式轉換的陷阱、四種 C++ 轉型各自怎麼用 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：...` 是實際執行的結果。標 🔍 的是深入內容，第一次讀可以先跳過。

---

# 第一部分：型別系統

## 1.1 靜態型別 (Static Typing)

**是什麼**：C++ 的每個變數、每個運算式，在 **編譯時** 就確定了型別，而且之後 **不能改變**。

**型別決定了三件事**：

1. **佔多少記憶體**：`int` 通常 4 bytes、`double` 8 bytes。
2. **能做哪些運算**：`int` 可以 `%`，`double` 不行；`string` 可以 `+` 串接，但不能 `-`。
3. **運算的規則**：同樣寫 `7 / 2`，整數和浮點數的結果不同。

```cpp
int a = 7, b = 2;
double c = 7, d = 2;
cout << a / b << '\n';     // 輸出：3      （整數除法，小數被丟掉）
cout << c / d << '\n';     // 輸出：3.5    （浮點數除法）
cout << a % b << '\n';     // 輸出：1
// cout << c % d;          // ❌ 編譯錯誤：double 不能用 %（要用 fmod）

int x = 5;
// x = "hello";            // ❌ 編譯錯誤：不能把字串放進 int
```

**為什麼要這樣設計？**
- 很多錯誤在 **編譯時** 就被抓到，不用等到執行才當掉。
- 編譯器知道每個變數的確切型別，可以產生非常快的機器碼。

**比喻**：容器上貼了標籤「醬油」，就只能裝醬油，倒錯東西在工廠就會被擋下來。Python 像是沒貼標籤的瓶子，什麼都能裝，但要打開才知道裡面是什麼（執行時才發現型別錯誤）。

## 1.2 基本型別的大小與範圍

C++ 標準 **只保證「最小範圍」**，實際大小由平台決定：

| 型別 | 標準保證 | 64 位元 Linux / macOS | 64 位元 Windows | 範圍（Linux） |
|---|---|---|---|---|
| `bool` | — | 1 byte | 1 byte | `true` / `false` |
| `char` | 剛好 1 byte、至少 8 bits | 8 bits | 8 bits | -128 ~ 127（通常） |
| `short` | 至少 16 bits | 16 | 16 | -32768 ~ 32767 |
| `int` | 至少 16 bits | 32 | 32 | 約 ±2.1 × 10⁹ |
| `long` | 至少 32 bits | **64** | **32** | 約 ±9.2 × 10¹⁸ |
| `long long` | 至少 64 bits | 64 | 64 | 約 ±9.2 × 10¹⁸ |
| `float` | — | 32 bits | 32 bits | 約 7 位有效數字 |
| `double` | — | 64 bits | 64 bits | 約 15~16 位有效數字 |

**用程式查詢實際的大小和範圍**：

```cpp
#include <climits>
#include <limits>
cout << sizeof(int) << '\n';                       // 輸出：4
cout << sizeof(long) << '\n';                      // 輸出：8（Linux）/ 4（Windows）
cout << INT_MAX << '\n';                           // 輸出：2147483647
cout << INT_MIN << '\n';                           // 輸出：-2147483648
cout << LLONG_MAX << '\n';                         // 輸出：9223372036854775807
cout << numeric_limits<int>::max() << '\n';        // 輸出：2147483647（C++ 風格的寫法）
cout << numeric_limits<double>::digits10 << '\n';  // 輸出：15（保證精確的十進位位數）
```

- **`sizeof(T)`**：回傳型別或物件佔幾個 byte。結果的型別是 `size_t`（無號整數）。`sizeof(char)` 永遠是 1。
- **`<climits>`**：C 風格的常數 `INT_MAX`、`LLONG_MIN`……
- **`numeric_limits<T>`**：C++ 風格，對任何數值型別都能用。

### 固定寬度整數 (Fixed-width Integer)

因為 `long` 在不同平台大小不同，**需要確定大小時** 用 `<cstdint>`：

```cpp
#include <cstdint>
int8_t   a = -100;          // 剛好 8 位元、有號
uint8_t  b = 200;           // 剛好 8 位元、無號（0 ~ 255）
int32_t  c = 2000000000;    // 剛好 32 位元
int64_t  d = 9000000000;    // 剛好 64 位元
uint64_t e = 18000000000000000000ULL;   // 剛好 64 位元、無號
cout << sizeof(c) << ' ' << sizeof(d) << '\n';   // 輸出：4 8（在任何平台都一樣）
```

> ⚠️ `int8_t` / `uint8_t` 其實是 `signed char` / `unsigned char` 的別名，`cout << b` 會印出 **字元** 而不是數字。要印數字寫 `cout << (int)b`。

### size_t

**是什麼**：用來表示「大小」和「索引」的 **無號** 整數型別，64 位元系統上是 64 位元。`sizeof`、`v.size()`、`s.length()` 回傳的都是 `size_t`。

```cpp
vector<int> v = {1, 2, 3};
size_t n = v.size();        // 3
// 無號數不會是負的：0 減 1 會繞回最大值（第五部分會詳細說明）
size_t z = 0;
cout << z - 1 << '\n';      // 輸出：18446744073709551615
```

## 1.3 char 的正負號

**是什麼**：`char` 到底是 **有號**（-128 ~ 127）還是 **無號**（0 ~ 255），C++ **沒有規定**，由編譯器和平台決定。x86 電腦上通常是有號，ARM（手機、新款 Mac）上常常是無號。

`char`、`signed char`、`unsigned char` 是 **三個不同的型別**。

```cpp
char c = 200;                    // x86：200 超出 -128~127，變成 -56
cout << (int)c << '\n';          // 輸出：-56（x86 Linux）；ARM 上會是 200
if (c > 100) cout << "big\n";    // x86 上不會印！因為 c 是 -56

signed char sc = -1;             // 明確指定有號
unsigned char uc = 255;          // 明確指定無號
cout << (int)sc << ' ' << (int)uc << '\n';   // 輸出：-1 255
```

**為什麼這很重要？** `isalpha`、`toupper` 這類函式要求參數是 `unsigned char` 的範圍（0 ~ 255）。如果字串裡有 128 以上的字元（例如中文的 UTF-8 編碼），`char` 會是負數，直接傳進去是未定義行為：

```cpp
string s = "中";
isalpha(s[0]);                   // ❌ s[0] 是負數，未定義行為
isalpha((unsigned char)s[0]);    // ✅
```

## 1.4 字面值 (Literal) 的型別

**是什麼**：直接寫在程式裡的值（`42`、`3.14`、`'a'`、`"hi"`）叫字面值。**字面值也有型別**，而且型別會影響計算結果。

### 整數字面值

| 寫法 | 型別 | 範例 |
|---|---|---|
| `42` | `int`（放不下時自動變大成 `long` / `long long`） | `auto a = 42;` → `int` |
| `42u` / `42U` | `unsigned int` | `auto b = 42u;` |
| `42L` | `long` | |
| `42LL` | `long long` | `auto c = 42LL;` |
| `42ULL` | `unsigned long long` | `auto d = 42ULL;` |
| `0x2A` | 十六進位，值是 42 | `0xFF` = 255 |
| `052` | **八進位**（開頭是 0），值是 42 | `010` = 8 |
| `0b101010` | 二進位（C++14），值是 42 | `0b1111` = 15 |
| `1'000'000` | 數字分隔符（C++14），值是 1000000 | 只是方便閱讀 |

```cpp
cout << 0x2A << ' ' << 052 << ' ' << 0b101010 << '\n';   // 輸出：42 42 42
cout << 010 << '\n';                                    // 輸出：8（不是 10！）
cout << 1'000'000 + 1 << '\n';                           // 輸出：1000001
cout << sizeof(42) << ' ' << sizeof(42LL) << '\n';       // 輸出：4 8
```

### 浮點數、字元、字串字面值

| 寫法 | 型別 | 說明 |
|---|---|---|
| `3.14` | `double` | 有小數點就是 `double` |
| `3.14f` | `float` | 加 `f` 才是 `float` |
| `1e9` | **`double`** | 科學記號一律是浮點數，即使看起來是整數 |
| `'a'` | `char` | 單引號：一個字元，值是 ASCII 碼 97 |
| `"a"` | `const char[2]` | 雙引號：字串，結尾自動加 `'\0'`，所以佔 2 個 char |
| `"a"s` | `std::string` | C++14，要 `using namespace std::literals;` |

```cpp
cout << sizeof(3.14) << ' ' << sizeof(3.14f) << '\n';  // 輸出：8 4
cout << 'a' << ' ' << (int)'a' << '\n';                // 輸出：a 97
cout << sizeof('a') << ' ' << sizeof("a") << '\n';     // 輸出：1 2
cout << 'a' + 1 << '\n';                               // 輸出：98（char 在運算時變成 int）
cout << (char)('a' + 1) << '\n';                       // 輸出：b
```

### 字面值的陷阱

```cpp
long long y = 1 << 40;      // ❌ 1 是 int，在 int 裡先溢位（未定義行為），之後才轉成 long long
long long z = 1LL << 40;    // ✅ 1099511627776

long long big = 2000000000 * 2;     // ❌ 兩個都是 int，乘完就溢位了
long long ok  = 2000000000LL * 2;   // ✅ 4000000000

int n = 1e9;                // ✅ 可以，1e9 是 double，剛好能精確轉成 int
long long w = 1e18 + 1;     // ❌ 1e18 是 double，double 只有 15~16 位精度，+1 消失了
cout << w << '\n';          // 輸出：1000000000000000000
```

**規則**：運算的型別是由 **運算元** 決定的，跟「結果要存進哪個變數」無關。所以要在 **運算之前** 就讓運算元變成夠大的型別。

---

# 第二部分：宣告、定義、初始化

## 2.1 宣告 vs 定義 (Declaration vs Definition)

**是什麼**：
- **宣告**：告訴編譯器「**有這個名字，它是什麼型別**」。可以宣告很多次。
- **定義**：真正 **配置記憶體**（變數）或 **提供內容**（函式本體、類別成員）。整個程式 **只能定義一次**（第 14 課的單一定義規則 ODR）。

| 東西 | 只有宣告 | 定義 |
|---|---|---|
| 變數 | `extern int counter;` | `int counter = 0;` 或 `int counter;` |
| 函式 | `int add(int a, int b);` | `int add(int a, int b) { return a + b; }` |
| 類別 | `class Engine;`（前置宣告） | `class Engine { int hp; };` |

```cpp
int add(int a, int b);        // 宣告：先告訴編譯器有 add 這個函式
int main() {
    cout << add(2, 3);        // ✅ 可以呼叫：編譯器已經知道 add 的參數和回傳型別
}                             // 輸出：5
int add(int a, int b) {       // 定義：放在後面也沒關係
    return a + b;
}
```

如果把 `int add(int a, int b);` 這行拿掉，`main` 裡呼叫 `add` 時編譯器還不認識它 → 編譯錯誤 `'add' was not declared in this scope`。

**比喻**：宣告是「名片」—— 告訴你這個人存在、怎麼聯絡他；定義是「這個人本身」。你可以發很多張名片，但人只有一個。

## 2.2 未初始化 (Uninitialized)

**是什麼**：宣告變數時沒有給初值。

**規則取決於變數住在哪裡**：

| 變數種類 | 沒給初值時 |
|---|---|
| **區域變數**（函式裡的） | **不確定的值**（垃圾值），讀取它是 **未定義行為** |
| **全域變數** | 自動設成 0 |
| **`static` 變數** | 自動設成 0 |
| `string`、`vector` 等類別物件 | 呼叫預設建構子（空字串、空 vector） |

```cpp
int g;                     // 全域：自動是 0
int main() {
    static int s;          // static：自動是 0
    int local;             // 區域：垃圾值！
    string str;            // 類別：空字串 ""
    vector<int> v;         // 類別：空 vector
    cout << g << ' ' << s << '\n';        // 輸出：0 0
    cout << str.size() << ' ' << v.size() << '\n';   // 輸出：0 0
    // cout << local;      // ❌ 未定義行為：可能是 0、可能是 32767、可能是任何數
}
```

**最常見的 bug**：

```cpp
int sum;                              // 忘了 = 0
for (int i = 1; i <= 3; i++) sum += i;
cout << sum;                          // 可能是 6，也可能是 21845 之類的怪數字
```

在你的電腦上碰巧是 0、結果碰巧對；換到評測系統上就錯了 —— 這種「時好時壞」的 bug 最難找。

**比喻**：租到一間沒打掃過的房間，抽屜裡可能有前一個房客留下的東西。區域變數使用的記憶體，可能剛剛才被別的函式用過，裡面留著舊資料。

**怎麼避免**：宣告時一律給初值；編譯時加 `-Wall`，編譯器會警告 `'sum' is used uninitialized`。

## 2.3 五種初始化寫法

| 寫法 | 名稱 | 效果 |
|---|---|---|
| `int a;` | 預設初始化 (default) | 區域變數是垃圾值 |
| `int a = 5;` | 複製初始化 (copy) | `a` 是 5，最常見的寫法 |
| `int a(5);` | 直接初始化 (direct) | `a` 是 5 |
| `int a{5};` | 列表初始化 (list / brace)，C++11 | `a` 是 5，**禁止窄化轉換** |
| `int a{};` | 值初始化 (value) | `a` **一定是 0** |

每一種的範例：

```cpp
int a;                // 預設初始化：垃圾值
int b = 5;            // 複製初始化
int c(5);             // 直接初始化
int d{5};             // 列表初始化
int e{};              // 值初始化：0
double f{};           // 0.0
string s{};           // ""
int* p{};             // nullptr
cout << b << c << d << e << '\n';   // 輸出：5550
```

### 窄化轉換 (Narrowing Conversion)

**是什麼**：可能 **遺失資訊** 的轉換。大括號初始化會 **直接編譯錯誤**，其他寫法只會默默地截掉：

| 轉換 | 為什麼會遺失資訊 | `=` 的結果 | `{}` 的結果 |
|---|---|---|---|
| `double → int` | 小數被截掉 | `int a = 3.7;` → 3 | `int a{3.7};` ❌ 編譯錯誤 |
| `long long → int` | 大數放不下 | `int b = 5000000000LL;` → 705032704 | ❌ 編譯錯誤 |
| `int → char` | 超過 127 放不下 | `char c = 300;` → 44 | ❌ 編譯錯誤 |
| `double → float` | 精度變差 | `float f = 0.1;` → 精度降低 | `float f{0.1};` ❌ 編譯錯誤 |
| `int → unsigned` | 負數放不下 | `unsigned u = -1;` → 4294967295 | ❌ 編譯錯誤 |

```cpp
int a = 3.7;          // 可以編譯，a == 3（-Wall 可能只有警告）
int b{3.7};           // ❌ error: narrowing conversion of '3.7e+0' from 'double' to 'int'
int c{7};             // ✅
int d{5LL};           // ✅ 例外：常數而且放得下，不算窄化
long long e{5};       // ✅ int → long long 不會遺失資訊
```

**建議**：不確定時用 **大括號**，讓編譯器幫你抓錯。

### 大括號的特殊情況：vector

對 **有 `initializer_list` 建構子的類別**（例如 `vector`），小括號和大括號的意思 **不一樣**：

```cpp
vector<int> v1(3, 5);     // 小括號：3 個 5        → {5, 5, 5}
vector<int> v2{3, 5};     // 大括號：元素是 3 和 5   → {3, 5}
vector<int> v3(3);        // 3 個 0               → {0, 0, 0}
vector<int> v4{3};        // 一個元素 3            → {3}
cout << v1.size() << ' ' << v2.size() << ' ' << v3.size() << ' ' << v4.size() << '\n';
// 輸出：3 2 3 1
```

### 🔍 最令人困擾的解析 (Most Vexing Parse)

```cpp
struct Widget { int x = 7; };
Widget w1();          // 你以為：建立一個 Widget 物件
                      // 實際上：宣告一個「沒有參數、回傳 Widget 的函式」叫 w1！
// cout << w1.x;      // ❌ 編譯錯誤：w1 是函式，沒有 .x
Widget w2{};          // ✅ 用大括號就沒有這個問題
Widget w3;            // ✅ 或乾脆不寫括號
cout << w2.x << w3.x; // 輸出：77
```

原因：C++ 的規則是「**能被解讀成宣告的，就是宣告**」，而 `Widget w1();` 剛好符合函式宣告的格式。

## 2.4 auto：讓編譯器推導型別

**是什麼**：`auto` 讓編譯器根據 **初始值** 自動決定變數的型別。

**為什麼需要**：有些型別很長（`map<string, vector<int>>::iterator`），寫出來又長又容易錯。

| 初始值 | `auto` 推導出的型別 |
|---|---|
| `auto a = 42;` | `int` |
| `auto b = 42LL;` | `long long` |
| `auto c = 3.0;` | `double` |
| `auto d = 1e9;` | **`double`**（不是 `int`！） |
| `auto e = 'x';` | `char` |
| `auto f = "hi";` | **`const char*`**（不是 `string`！） |
| `auto g = string("hi");` | `string` |
| `auto h = v.begin();` | `vector<int>::iterator` |
| `auto i = 10 / 4;` | `int`，值是 2 |
| `auto j = m.find(k);` | `map<...>::iterator` |

```cpp
map<string, vector<int>> m;
map<string, vector<int>>::iterator it1 = m.begin();   // 不用 auto：又長又難讀
auto it2 = m.begin();                                  // 用 auto：簡潔

auto f = "hi";
// f.size();                 // ❌ 編譯錯誤：const char* 沒有 size()
auto g = string("hi");
cout << g.size() << '\n';    // 輸出：2
```

### auto 會丟掉參考和頂層 const

```cpp
int x = 10;
const int cx = 20;
int& rx = x;

auto a = cx;     // a 是 int（不是 const int）→ 可以修改 a
a = 99;          // ✅
auto b = rx;     // b 是 int（不是 int&）→ 是複製品
b = 0;           // x 不受影響
cout << x << '\n';   // 輸出：10

auto& c = rx;    // c 是 int& → 參考到 x
c = 0;
cout << x << '\n';   // 輸出：0

const auto& d = x;   // d 是 const int& → 唯讀參考，不複製
```

**比喻**：`auto` 像是「照著樣品做一個新的」，做出來的是 **複製品**，不是樣品本身，也不會繼承樣品上「禁止修改」的標籤。要參考原本那一個，就要寫 `auto&`。

**什麼時候用 auto**：
- ✅ 型別很長、而且從右邊就看得出來（迭代器、`make_unique<...>`）。
- ✅ 範圍 for：`for (const auto& x : v)`。
- ⚠️ 數字：`auto n = 0;` 是 `int`，如果之後要存很大的數，應該明確寫 `long long n = 0;`。

---

# 第三部分：const 與 constexpr

## 3.1 const：唯讀

**是什麼**：`const` 變數 **初始化之後就不能修改**，違反的話 **編譯錯誤**。

**為什麼需要**：
1. 讓編譯器幫你檢查「這個不應該被改」。
2. 讓讀程式的人一眼就知道這個值是固定的。
3. 函式參數加 `const`，代表「我保證不會改你傳進來的東西」。

這種「**不該改的都標成 const**」的習慣叫 **const 正確性 (const correctness)**。

```cpp
const int MAX_N = 100;
// MAX_N = 200;            // ❌ error: assignment of read-only variable 'MAX_N'

// const int k;            // ❌ const 變數一定要初始化（之後就不能改了）

int n;
cin >> n;
const int doubled = n * 2;  // ✅ 值可以在「執行時」才決定，只是之後不能再改
```

### const 用在函式參數

```cpp
void print(const vector<int>& v) {   // const 參考：不複製、也不能改
    for (int x : v) cout << x << ' ';
    // v.push_back(1);               // ❌ 編譯錯誤：v 是 const
}
void fill_zero(vector<int>& v) {     // 沒有 const：表示會修改
    for (int& x : v) x = 0;
}
```

看函式的宣告就知道誰會修改你的資料、誰不會。

### const 用在成員函式（第 07 課詳細說明）

```cpp
class Account {
    long long balance_ = 0;
public:
    long long balance() const { return balance_; }   // 承諾不修改物件
};
```

## 3.2 constexpr：編譯期常數

**是什麼**：`constexpr` 要求值必須在 **編譯時** 就能算出來。

**為什麼需要**：
1. 有些地方 **必須** 是編譯期常數：內建陣列的大小、模板參數、`switch` 的 `case`。
2. 在編譯時算好，執行時完全不花時間。

```cpp
constexpr int N = 1000;              // 編譯時就知道是 1000
int arr[N];                          // ✅ 可以當陣列大小
std::array<int, N> a2;               // ✅ 可以當模板參數

int n;
cin >> n;
// constexpr int M = n;              // ❌ n 要執行時才知道
const int M = n;                     // ✅ const 可以
// int arr2[M];                      // ❌（標準 C++）：M 不是編譯期常數
```

### constexpr 函式

```cpp
constexpr long long square(long long x) { return x * x; }
constexpr long long fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }

constexpr long long A = square(12);       // 編譯時就算好 144
constexpr long long F = fact(10);         // 編譯時就算好 3628800
static_assert(F == 3628800, "fact 算錯了");   // 編譯時檢查，失敗就編譯錯誤

int k;
cin >> k;
long long B = square(k);                  // 參數不是常數：跟普通函式一樣在執行時算
```

`constexpr` 函式是「**可以** 在編譯時算」，不是「**一定** 在編譯時算」。

### const vs constexpr

| | `const` | `constexpr` |
|---|---|---|
| 意思 | 執行期間不能改 | 編譯時就要知道值（也不能改） |
| 初始值 | 可以是執行時才知道的（`cin` 讀進來的） | 必須是編譯期常數 |
| 可以當陣列大小 / 模板參數 | 只有初始值剛好是常數時 | ✅ 一定可以 |
| 能修飾函式 | 成員函式後面加 `const`（不同意思） | `constexpr` 函式 |

**比喻**：`const` 是「印好之後不能修改的考卷」；`constexpr` 是「出題時就已經印好的考卷」—— 後者一定也不能修改，而且考試前就準備好了。

**選擇**：值在寫程式時就知道（例如 `MAXN = 200005`）→ `constexpr`；值要執行時才知道，但之後不會變 → `const`。

---

# 第四部分：作用域與生命週期

這是兩個 **不同** 的概念：
- **作用域 (scope)**：在程式碼的 **哪些地方** 可以用這個名字。這是「空間」上的概念。
- **生命週期 (lifetime)**：這個變數在 **哪段時間** 實際存在於記憶體中。這是「時間」上的概念。

## 4.1 作用域 (Scope)：在哪裡「看得到」這個名字

| 作用域 | 範圍 | 範例 |
|---|---|---|
| 區塊作用域 (block) | 從宣告處到所在的 `}` | `if`、`for`、`{ }` 裡宣告的變數 |
| 函式參數 | 整個函式本體 | `void f(int x)` 的 `x` |
| for / if 的初始化部分 | 整個 for / if（包括 else） | `for (int i = 0; ...)` 的 `i` |
| 命名空間 / 全域 (namespace / global) | 從宣告處到檔案結尾 | 函式外面宣告的變數 |
| 類別作用域 (class) | 類別的所有成員函式裡 | 成員變數 |

每一種的範例：

```cpp
int g = 1;                         // 全域：這行之後，整個檔案都能用

void f(int param) {                // 函式參數：整個函式裡都能用
    int local = param + g;         // 區塊作用域：從這裡到函式結尾
    if (local > 0) {
        int inner = local * 2;     // 區塊作用域：只在這個 if 裡
        cout << inner << '\n';
    }
    // cout << inner;              // ❌ 編譯錯誤：inner 已經超出作用域

    for (int i = 0; i < 3; i++) { }
    // cout << i;                  // ❌ i 只在 for 迴圈裡

    if (int t = param * 10; t > 5) cout << t << '\n';   // C++17：t 在 if / else 裡都能用
    // cout << t;                  // ❌ 出了 if 就沒了
}

class Counter {
    int count_ = 0;                // 類別作用域
public:
    void inc() { count_++; }       // 所有成員函式都能用 count_
};
```

**為什麼要盡量縮小作用域？** 變數只在需要的地方存在，比較不會被不小心改到，程式也比較好讀。

### 遮蔽 (Shadowing)

**是什麼**：內層宣告了 **同名** 的變數，會 **蓋住** 外層的。內層裡用這個名字，指的都是內層的那個。

```cpp
int x = 1;                       // 全域的 x
int main() {
    int x = 2;                   // 遮蔽了全域的 x
    {
        int x = 3;               // 又遮蔽了 main 裡的 x
        cout << x << '\n';       // 輸出：3
    }
    cout << x << '\n';           // 輸出：2
    cout << ::x << '\n';         // 輸出：1（:: 開頭代表全域）
}
```

**遮蔽造成的 bug**：

```cpp
int total = 0;
for (int i = 0; i < 3; i++) {
    int total = 0;               // 😱 不小心又宣告了一次，遮蔽了外面的 total
    total += i;
}
cout << total << '\n';           // 輸出：0（外面的 total 從來沒被改過）
```

編譯時加 `-Wshadow`，編譯器會警告 `declaration of 'total' shadows a previous local`。

## 4.2 生命週期 / 儲存期 (Storage Duration)：變數「活多久」

| 儲存期 | 什麼時候建立 | 什麼時候銷毀 | 例子 |
|---|---|---|---|
| 自動 (automatic) | 執行到宣告的那一行 | 離開所在的區塊 `}` | 一般的區域變數、函式參數 |
| 靜態 (static) | 程式開始時（區域 static：第一次執行到時） | 程式結束 | 全域變數、`static` 變數 |
| 動態 (dynamic) | `new` 的時候 | `delete` 的時候 | heap 上的物件 |
| 執行緒 (thread) | 執行緒開始 | 執行緒結束 | `thread_local` 變數 |

用一個會印出「建立」和「銷毀」的類別，觀察各種儲存期：

```cpp
struct Tracer {
    string name;
    Tracer(string n) : name(n) { cout << "建立 " << name << '\n'; }
    ~Tracer() { cout << "銷毀 " << name << '\n'; }
};

Tracer global("全域");                 // 靜態儲存期：main 開始之前就建立

void func() {
    Tracer a("自動");                  // 自動：每次呼叫都建立、結束時銷毀
    static Tracer s("static區域");     // 靜態：只在第一次呼叫時建立，程式結束才銷毀
}

int main() {
    cout << "main 開始\n";
    func();
    func();                            // 第二次呼叫：「static區域」不會再建立
    Tracer* p = new Tracer("動態");    // 動態：new 的時候建立
    delete p;                          // delete 的時候銷毀
    cout << "main 結束\n";
}
```

輸出：

```
建立 全域
main 開始
建立 自動
建立 static區域
銷毀 自動
建立 自動
銷毀 自動
建立 動態
銷毀 動態
main 結束
銷毀 static區域
銷毀 全域
```

**觀察重點**：
- 「全域」在 `main` 開始之前就建立了。
- 「自動」每次呼叫 `func` 都建立一次、銷毀一次。
- 「static區域」只建立一次，而且一直活到程式結束（比 `main` 裡的東西還晚銷毀）。
- 「動態」的生命完全由 `new` / `delete` 控制；如果忘了 `delete`，它就永遠不會被銷毀（記憶體洩漏，第 06 課）。

## 4.3 static 區域變數

**是什麼**：在函式裡加 `static` 的變數：
- **作用域** 只在函式裡（外面看不到）。
- **生命週期** 是整個程式 —— 函式結束後它還活著，**值會保留到下一次呼叫**。
- 初始化 **只發生一次**（第一次執行到那一行時）。

```cpp
int next_id() {
    static int id = 0;      // 這行只在第一次呼叫時執行
    return ++id;
}
int main() {
    cout << next_id() << '\n';   // 輸出：1
    cout << next_id() << '\n';   // 輸出：2
    cout << next_id() << '\n';   // 輸出：3
    // cout << id;               // ❌ 編譯錯誤：id 的作用域只在 next_id 裡
}
```

**和全域變數的差別**：效果類似（值會一直保留），但 `static` 區域變數 **只有這個函式能用**，不會被其他程式碼不小心改到。

**比喻**：辦公室裡你的抽屜 —— 只有你能開（作用域：只在函式裡），下班之後東西還在，明天上班還看得到（生命週期：一直存在）。普通區域變數則像是會議室的白板，每次開完會就擦掉。

---

# 第五部分：型別轉換

## 5.1 隱式轉換 (Implicit Conversion)

**是什麼**：編譯器 **自動** 幫你做的型別轉換，你沒有寫任何轉型的程式碼。

**為什麼要了解**：它讓程式寫起來方便（`double d = 5;` 不用特別轉），但也是很多「看起來對、結果錯」的 bug 的來源。

### (1) 整數提升 (Integral Promotion)

**規則**：比 `int` 小的型別（`bool`、`char`、`short`）參與 **算術運算** 時，會 **先被轉成 `int`**。

```cpp
char a = 100, b = 100;
auto c = a + b;                  // 先轉成 int 再相加 → c 是 int
cout << c << '\n';               // 輸出：200（不會在 char 裡溢位）

char ch = 'A';
cout << ch + 1 << '\n';          // 輸出：66（是 int，不是字元 'B'）
cout << (char)(ch + 1) << '\n';  // 輸出：B

bool t = true, f = false;
cout << t + t + f << '\n';       // 輸出：2（true 變成 1，false 變成 0）

short s1 = 30000, s2 = 30000;
int product = s1 * s2;           // 先轉成 int 再相乘
cout << product << '\n';         // 輸出：900000000
```

### (2) 一般算術轉換 (Usual Arithmetic Conversions)

**規則**：二元運算子（`+ - * / < ==` ……）兩邊的型別不同時，會 **先轉成同一個型別**，通常是「**比較大 / 比較能表示**」的那一邊。

| 左邊 | 右邊 | 轉成 | 範例 | 結果 |
|---|---|---|---|---|
| `int` | `long long` | `long long` | `2000000000 + 2000000000LL` | `4000000000` ✅ |
| `int` | `double` | `double` | `7 / 2.0` | `3.5` |
| `float` | `double` | `double` | `1.5f + 2.0` | `3.5`（double） |
| `int` | `unsigned int` | **`unsigned int`** | `-1 < 0u` | **`false`** 😱 |
| `int` | `size_t` | **`size_t`** | `-1 < v.size()` | **`false`** 😱 |

```cpp
cout << 2000000000 + 2000000000LL << '\n';   // 輸出：4000000000
cout << 7 / 2 << ' ' << 7 / 2.0 << '\n';      // 輸出：3 3.5
```

**最危險的情況：有號和無號混在一起**。有號的會被轉成 **無號**，負數會變成一個超大的正數：

```cpp
int a = -1;
unsigned int b = 0;
if (a < b) cout << "a 比較小\n";
else cout << "a 比較大??\n";         // 輸出：a 比較大??
// 原因：-1 被轉成 unsigned int，變成 4294967295

vector<int> v;                      // 空的 vector
for (int i = 0; i < v.size() - 1; i++) { }   // 😱 v.size() - 1 是 0 - 1 = 18446744073709551615
                                             //    這個迴圈會跑非常非常久（而且 v[i] 越界）
for (int i = 0; i + 1 < (int)v.size(); i++) { }   // ✅ 先轉成 int，或改寫成不需要減法的形式
```

編譯時加 `-Wall -Wextra` 會出現 `comparison of integer expressions of different signedness` 警告 —— **不要忽略它**。

### (3) 賦值時的轉換

把值存進另一個型別的變數時，也會自動轉換。**存不下時會默默出錯**：

```cpp
int big = 300;
char c = big;                 // char 最大 127：300 變成 44（300 - 256）
cout << (int)c << '\n';       // 輸出：44

long long huge = 5000000000LL;
int i = huge;                 // int 放不下：變成 705032704
cout << i << '\n';            // 輸出：705032704

double d = 3.99;
int n = d;                    // 小數被截掉
cout << n << '\n';            // 輸出：3

int neg = -1;
unsigned int u = neg;         // 負數存進無號：繞回最大值
cout << u << '\n';            // 輸出：4294967295
```

### (4) 浮點數轉整數：截斷，不是四捨五入

**規則**：浮點數轉成整數時，小數部分 **直接丟掉**（向 0 取整）。超出整數範圍是 **未定義行為**。

要其他的取整方式，用 `<cmath>` 的函式：

| 函式 | 意思 | `3.7` | `3.2` | `-3.7` | `-3.2` |
|---|---|---|---|---|---|
| `(int)x` | 截斷（向 0） | 3 | 3 | -3 | -3 |
| `trunc(x)` | 截斷（向 0） | 3 | 3 | -3 | -3 |
| `floor(x)` | 向下取整（往負無限大） | 3 | 3 | **-4** | **-4** |
| `ceil(x)` | 向上取整（往正無限大） | **4** | **4** | -3 | -3 |
| `round(x)` | 四捨五入（.5 遠離 0） | 4 | 3 | -4 | -3 |

```cpp
#include <cmath>
double x = -3.7;
cout << (int)x << ' ' << floor(x) << ' ' << ceil(x) << ' ' << round(x) << '\n';
// 輸出：-3 -4 -3 -4
cout << round(2.5) << ' ' << round(-2.5) << '\n';   // 輸出：3 -3
long long r = llround(2.5);                          // 回傳 long long 的四捨五入：3
// int bad = 1e20;                                   // ❌ 未定義行為：int 放不下 10^20
```

**常見寫法**：`(int)(x + 0.5)` 對正數是四捨五入，**對負數是錯的**（`-3.7 + 0.5 = -3.2` → `-3`），直接用 `round` / `llround`。

## 5.2 顯式轉換：四種 C++ 轉型

**為什麼需要四種？** C 語言的轉型 `(int)x` **什麼都能轉**：數值轉換、拿掉 const、把指標當成整數……一個寫法做了好幾種意思完全不同的事，寫錯了也不會有任何警告。C++ 把它拆成四種，**每一種只做一類事**，用錯了編譯器會告訴你，而且在程式碼裡很容易搜尋（搜尋 `_cast` 就能找到所有轉型的地方）。

| 轉型 | 用途 | 檢查時機 | 危險程度 |
|---|---|---|---|
| `static_cast<T>(x)` | 一般的、「合理」的轉換 | 編譯時 | 低 |
| `dynamic_cast<T>(x)` | 繼承體系裡的 **向下轉型**，執行時確認真的是那個型別 | **執行時** | 低（會檢查） |
| `const_cast<T>(x)` | 加上或 **拿掉** `const` | 編譯時 | 中（拿掉後修改原本就是 const 的東西 → UB） |
| `reinterpret_cast<T>(x)` | 把記憶體的位元 **原封不動地當成另一種型別** | 不檢查 | 高 |

**比喻**：C 的轉型像一把萬能鑰匙，什麼門都能開，但開錯門也沒人阻止你。C++ 的四種轉型像是四把專用鑰匙：要開辦公室用辦公室的鑰匙，拿錯鑰匙門根本插不進去（編譯錯誤）。

### (1) static_cast：一般用途

**用途**：所有「**有道理、編譯器知道怎麼做**」的轉換。這是最常用的一種。

**例 1：數值型別之間的轉換**（最常見）

```cpp
int total = 7, cnt = 2;
double avg1 = total / cnt;                        // ❌ 先做整數除法得到 3，再轉成 3.0
double avg2 = static_cast<double>(total) / cnt;   // ✅ 先把 total 轉成 7.0，再除 → 3.5
double avg3 = static_cast<double>(total / cnt);   // ❌ 轉得太晚：total / cnt 已經是 3
cout << avg1 << ' ' << avg2 << ' ' << avg3 << '\n';   // 輸出：3 3.5 3

double price = 19.99;
int dollars = static_cast<int>(price);            // 明確表示「我知道會截掉小數」
cout << dollars << '\n';                          // 輸出：19

long long big = 1LL << 40;
int low = static_cast<int>(big & 0xFFFFFFFF);     // 明確取低 32 位元
```

和隱式轉換的結果一樣，但 **寫出來讓讀程式的人知道「這是故意的」**，編譯器也不會再發出警告。

**例 2：字元和整數**

```cpp
char c = 'A';
int code = static_cast<int>(c);           // 65
char next = static_cast<char>(code + 1);  // 'B'
cout << code << ' ' << next << '\n';      // 輸出：65 B
```

**例 3：列舉 (enum class) 和整數**（第 15 課）

```cpp
enum class Color { Red, Green, Blue };
Color col = Color::Blue;
// int k = col;                           // ❌ enum class 不會自動轉成整數
int k = static_cast<int>(col);            // ✅ 2
Color back = static_cast<Color>(1);       // ✅ Color::Green
cout << k << ' ' << static_cast<int>(back) << '\n';   // 輸出：2 1
```

**例 4：`void*` 轉回原本的指標型別**

```cpp
int value = 42;
void* vp = &value;                        // 任何指標都能自動轉成 void*
// int* ip = vp;                          // ❌ void* 不會自動轉回來
int* ip = static_cast<int*>(vp);          // ✅ 轉回原本的型別
cout << *ip << '\n';                      // 輸出：42
```

**例 5：繼承體系裡的轉型（不檢查）**

```cpp
struct Animal { virtual ~Animal() = default; };
struct Dog : Animal { void bark() { cout << "Woof\n"; } };

Dog d;
Animal* a = &d;                           // 向上轉型（子 → 父）：自動、安全
Dog* d2 = static_cast<Dog*>(a);           // 向下轉型（父 → 子）：可以，但「不檢查」
d2->bark();                               // 輸出：Woof（因為 a 真的指向 Dog）
```

如果 `a` 其實指向的是 `Cat`，`static_cast<Dog*>` **還是會成功**，之後使用就是未定義行為。不確定實際型別時，要用 `dynamic_cast`。

**static_cast 做不到的事**（會編譯錯誤，這正是它的價值）：

```cpp
const int ci = 5;
// int* p = static_cast<int*>(&ci);       // ❌ 不能拿掉 const（要用 const_cast）
double dd = 3.14;
// int* q = static_cast<int*>(&dd);       // ❌ 不能把 double* 當成 int*（要用 reinterpret_cast）
```

### (2) dynamic_cast：安全的向下轉型

**用途**：把「**父類別的指標 / 參考**」轉成「**子類別的指標 / 參考**」，而且會在 **執行時檢查** 物件實際上是不是那個子類別。（詳細的繼承與多型見第 08 課。）

**條件**：父類別必須是 **多型類別**（至少有一個虛擬函式）。

**例 1：指標版本 —— 失敗時回傳 `nullptr`**

```cpp
struct Animal { virtual ~Animal() = default; };
struct Dog : Animal { void bark() { cout << "Woof\n"; } };
struct Cat : Animal { void meow() { cout << "Meow\n"; } };

void react(Animal* a) {
    if (Dog* d = dynamic_cast<Dog*>(a)) {        // a 真的是 Dog 嗎？
        d->bark();
    } else if (Cat* c = dynamic_cast<Cat*>(a)) { // a 真的是 Cat 嗎？
        c->meow();
    } else {
        cout << "不認識的動物\n";
    }
}

Dog dog; Cat cat; Animal generic;
react(&dog);       // 輸出：Woof
react(&cat);       // 輸出：Meow
react(&generic);   // 輸出：不認識的動物
```

**例 2：參考版本 —— 失敗時丟出 `std::bad_cast` 例外**

```cpp
#include <typeinfo>
Cat cat2;
Animal& ref = cat2;
try {
    Dog& d = dynamic_cast<Dog&>(ref);    // ref 其實是 Cat → 失敗
    d.bark();
} catch (const bad_cast& e) {
    cout << "轉型失敗\n";                 // 輸出：轉型失敗
}
```

參考不能是「空的」，所以沒辦法回傳 `nullptr`，只好丟出例外。

**例 3：和 static_cast 的比較**

```cpp
Animal* a = &cat;
Dog* s = static_cast<Dog*>(a);    // ⚠️ 編譯通過，不檢查：s 指向一隻貓，但型別說它是狗
Dog* d = dynamic_cast<Dog*>(a);   // ✅ 檢查後發現不是狗 → nullptr
cout << (d == nullptr) << '\n';   // 輸出：1
// s->bark();                     // ❌ 未定義行為
```

**代價**：`dynamic_cast` 要在執行時查詢型別資訊，比 `static_cast` 慢。程式裡如果到處都需要 `dynamic_cast` 判斷型別，通常代表應該改用 **虛擬函式**（第 08 課）。

### (3) const_cast：加上或拿掉 const

**用途**：**唯一** 能改變 `const` 屬性的轉型。

**例 1：呼叫舊的、沒有寫 const 的函式**（最主要的合理用途）

```cpp
// 一個舊的 C 函式庫函式：明明不會修改字串，但參數忘了寫 const
int legacy_length(char* s) { int n = 0; while (s[n]) n++; return n; }

const string name = "Alice";
// legacy_length(name.c_str());                         // ❌ 不能把 const char* 傳給 char*
int len = legacy_length(const_cast<char*>(name.c_str())); // ✅ 我們確定它不會修改
cout << len << '\n';                                      // 輸出：5
```

**例 2：原本不是 const 的物件，可以安全地拿掉 const 再修改**

```cpp
int x = 10;                         // x 本身不是 const
const int& cref = x;                // 透過 const 參考看它
int& r = const_cast<int&>(cref);    // 拿掉 const
r = 20;                             // ✅ 合法：x 本來就可以修改
cout << x << '\n';                  // 輸出：20
```

**例 3：⚠️ 原本就是 const 的物件，拿掉 const 再修改 → 未定義行為**

```cpp
const int y = 10;                   // y 本身就是 const
int& ry = const_cast<int&>(y);      // 可以編譯
ry = 20;                            // ❌ 未定義行為！
cout << y << '\n';                  // 可能印出 10（編譯器已經把 y 當成常數 10 替換掉了）
                                    // 也可能印出 20，或發生其他事
```

**例 4：加上 const**（很少需要，因為加 const 本來就會自動發生）

```cpp
int z = 1;
const int* cp = const_cast<const int*>(&z);   // 等同於 const int* cp = &z;
```

**規則**：`const_cast` 只用在「**我確定那個東西其實可以修改，只是型別上多了 const**」的情況。看到 `const_cast` 時要特別小心。

### (4) reinterpret_cast：重新解讀位元

**用途**：不做任何轉換，**把同一塊記憶體的位元直接當成另一種型別來看**。主要用在很底層的程式（硬體、網路封包、序列化）。

**例 1：把指標變成整數（例如印出或計算位址）**

```cpp
#include <cstdint>
int value = 42;
uintptr_t addr = reinterpret_cast<uintptr_t>(&value);   // 位址變成一個整數
cout << hex << addr << dec << '\n';                      // 輸出：7ffd...（每次執行不同）
int* back = reinterpret_cast<int*>(addr);                 // 再轉回指標
cout << *back << '\n';                                    // 輸出：42
```

`uintptr_t`（`<cstdint>`）是「剛好能放下一個指標」的無號整數型別。

**例 2：逐 byte 查看一個整數的記憶體內容**

```cpp
int n = 0x12345678;
unsigned char* bytes = reinterpret_cast<unsigned char*>(&n);
for (int i = 0; i < 4; i++) cout << hex << (int)bytes[i] << ' ';
cout << dec << '\n';
// 輸出：78 56 34 12（x86 是「小端序 little-endian」：低位的 byte 放在前面）
```

透過 `char*` / `unsigned char*` 查看任何物件的 byte 是 **合法** 的。

**例 3：⚠️ 把一種型別的物件當成另一種型別來讀 → 未定義行為**

```cpp
float f = 1.0f;
int* ip = reinterpret_cast<int*>(&f);
// cout << *ip;     // ❌ 未定義行為（違反「嚴格別名規則 strict aliasing」）

int bits;
memcpy(&bits, &f, sizeof f);        // ✅ 想看 float 的位元，用 memcpy
cout << hex << bits << dec << '\n'; // 輸出：3f800000
// C++20 可以用 std::bit_cast<int>(f)
```

**規則**：一般的應用程式 **幾乎用不到** `reinterpret_cast`。如果你覺得需要它，先想想有沒有別的寫法。

### (5) C 風格轉型：為什麼不建議用

```cpp
double d = 3.7;
int a = (int)d;      // C 風格
int b = int(d);      // 函式風格（意思和 C 風格一樣）
```

C 風格轉型會 **依序嘗試** `const_cast`、`static_cast`、`static_cast + const_cast`、`reinterpret_cast`、`reinterpret_cast + const_cast`，**用第一個成功的**。問題是你看不出它實際做了哪一種：

```cpp
const int secret = 5;
int* p1 = (int*)&secret;            // C 風格：默默地拿掉了 const，沒有任何警告
// int* p2 = static_cast<int*>(&secret);   // C++ 風格：編譯錯誤，提醒你這樣做有問題

double dd = 2.5;
int* p3 = (int*)&dd;                // C 風格：默默地做了 reinterpret_cast，非常危險
```

**例外**：簡單的數值轉換（`(int)x`、`(double)y`）用 C 風格很常見、也很清楚，競賽程式和本平台的範例也常這樣寫。但 **涉及指標的轉換，一定要用 C++ 的四種轉型**。

### 總整理：我想要……該用哪一個？

| 我想要…… | 用 |
|---|---|
| 把 `int` 轉成 `double`（讓除法有小數） | `static_cast<double>(x)` |
| 把 `double` 截斷成 `int` | `static_cast<int>(x)`（四捨五入用 `llround`） |
| `enum class` ↔ 整數 | `static_cast` |
| `void*` 轉回原本的指標 | `static_cast` |
| 父類別指標 → 子類別指標，**確定** 是那個子類別 | `static_cast`（或用 `dynamic_cast` 更安全） |
| 父類別指標 → 子類別指標，**不確定** 是哪個子類別 | `dynamic_cast` |
| 傳 `const` 字串給沒寫 `const` 的舊函式 | `const_cast` |
| 指標 ↔ 整數、查看物件的原始 byte | `reinterpret_cast` |
| 查看 `float` 的位元表示 | `memcpy` 或 C++20 的 `bit_cast` |

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 靜態型別 | Static Typing | 型別在編譯時決定，之後不變 | 1.1 |
| 固定寬度整數 | Fixed-width Integer | `int32_t`、`int64_t` 等保證大小的型別 | 1.2 |
| 大小型別 | size_t | 表示大小與索引的無號整數 | 1.2 |
| 字面值 | Literal | 直接寫在程式裡的值 | 1.4 |
| 宣告 / 定義 | Declaration / Definition | 告訴編譯器有這個名字 / 真正配置或實作 | 2.1 |
| 未初始化 | Uninitialized | 沒給初值，區域變數的內容不確定 | 2.2 |
| 列表初始化 | List Initialization | 大括號初始化，禁止窄化 | 2.3 |
| 值初始化 | Value Initialization | `T x{};`，數值一定是 0 | 2.3 |
| 窄化轉換 | Narrowing Conversion | 可能遺失資訊的轉換 | 2.3 |
| 最令人困擾的解析 | Most Vexing Parse | `T x();` 被當成函式宣告 | 2.3 |
| 型別推導 | Type Deduction (`auto`) | 讓編譯器依初始值決定型別 | 2.4 |
| const 正確性 | Const Correctness | 不該改的東西都標成 const | 3.1 |
| 編譯期常數 | constexpr | 編譯時就算好的值 | 3.2 |
| 靜態斷言 | static_assert | 編譯時檢查條件 | 3.2 |
| 作用域 | Scope | 名字在程式碼的哪裡看得到 | 4.1 |
| 遮蔽 | Shadowing | 內層同名變數蓋住外層 | 4.1 |
| 生命週期 / 儲存期 | Lifetime / Storage Duration | 變數在什麼時間存在 | 4.2 |
| 整數提升 | Integral Promotion | 小型別運算時先轉成 int | 5.1 |
| 一般算術轉換 | Usual Arithmetic Conversions | 兩邊型別不同時轉成同一型別 | 5.1 |
| 截斷 | Truncation | 浮點數轉整數時丟掉小數 | 5.1 |
| 靜態轉型 | static_cast | 一般用途的明確轉型 | 5.2 |
| 動態轉型 | dynamic_cast | 執行時檢查的向下轉型 | 5.2 |
| 常數轉型 | const_cast | 加上或拿掉 const | 5.2 |
| 重新解讀轉型 | reinterpret_cast | 把位元當成另一種型別 | 5.2 |
| 小端序 | Little-endian | 低位 byte 存在低位址 | 5.2 |

---

# 習題

### 題 1：預測輸出

```cpp
unsigned int a = 1;
int b = -2;
cout << (a + b > 0) << '\n';
cout << a + b << '\n';
```

### 題 2：哪些可以編譯？

```cpp
int a = 2.5;
int b{2.5};
int c(2.5);
long long d{5};
int e{5LL};
char f{300};
```

### 題 3：找 bug

```cpp
double average(const vector<int>& v) {
    int sum;
    for (int x : v) sum += x;
    return sum / v.size();
}
```

### 題 4：預測輸出

```cpp
int counter() {
    static int c = 10;
    return c++;
}
int main() {
    cout << counter() << counter() << counter();
}
```

（提示：C++17 起 `<<` 串接的求值順序是由左到右。）

### 題 5：`auto` 推導出什麼型別？值是多少？

```cpp
auto a = 'x';
auto b = 10 / 4;
auto c = 10 / 4.0;
auto d = "text";
const int k = 5;
auto e = k;
auto f = 1e3;
```

### 題 6：這段程式在 Linux 和 Windows 上結果一樣嗎？

```cpp
long x = 3000000000;
cout << x;
```

### 題 7：`const` 和 `constexpr` 哪個可以用在這裡？

```cpp
int n;
cin >> n;
??? int limit = n * 2;
```

### 題 8：預測輸出

```cpp
double x = -2.5;
cout << (int)x << ' ' << floor(x) << ' ' << ceil(x) << ' ' << round(x);
```

### 題 9：預測輸出

```cpp
vector<int> a(4, 1);
vector<int> b{4, 1};
cout << a.size() << ' ' << b.size() << ' ' << a[0] << ' ' << b[0];
```

### 題 10：選出正確的轉型

```
a) 把 int sum 轉成 double，讓 sum / n 有小數
b) Animal* 指向的可能是 Dog 也可能是 Cat，想在是 Dog 時呼叫 bark()
c) 呼叫 void old_api(char* s)，手上只有 const string& name，而且確定 old_api 不會修改字串
d) 印出一個指標代表的位址數值
```

---

# 習題解答

**題 1**：印出 `1` 和 `4294967295`。`a + b` 中 `b` 被轉成 `unsigned int`：`-2` 變成 `4294967294`，加 1 得到 `4294967295`（就是 -1 的無號表示），當然 `> 0`。

**題 2**：
- `a`：可以，`a == 2`（截掉小數，可能有警告）。
- `b`：**編譯錯誤**，大括號禁止 `double → int` 的窄化。
- `c`：可以，`c == 2`。
- `d`：可以，`int → long long` 不會遺失資訊。
- `e`：**可以**。`5LL` 是常數而且放得進 `int`，窄化規則對常數會檢查實際的值。
- `f`：**編譯錯誤**。`300` 是常數，但放不進 `char`（最大 127）。

**題 3**：三個 bug：
1. `sum` 沒有初始化，是垃圾值 → `int sum = 0;`（大量資料時用 `long long`）。
2. `sum / v.size()`：整數除法（而且 `int` 會被轉成無號的 `size_t`），小數不見了 → `static_cast<double>(sum) / v.size()`。
3. `v` 是空的時候除以 0 → 要先檢查 `if (v.empty()) return 0;`。

**題 4**：`101112`。`c` 只在第一次呼叫時初始化成 10，之後保留上一次的值；`c++` 回傳的是加 1 **之前** 的值。

**題 5**：
- `a`：`char`，值 `'x'`。
- `b`：`int`，值 `2`（整數除法）。
- `c`：`double`，值 `2.5`。
- `d`：`const char*`（不是 `string`）。
- `e`：`int`，值 `5`（`auto` 丟掉頂層 `const`）。
- `f`：`double`，值 `1000.0`（科學記號一律是浮點數）。

**題 6**：**不一樣**。Linux 64 位元的 `long` 是 64 位元，印出 `3000000000`；Windows 的 `long` 是 32 位元，放不下（最大約 21 億），結果是錯的。要用 `long long`。

**題 7**：只能用 `const`。`n` 是執行時才讀入的，`n * 2` 不是編譯期常數，不能用 `constexpr`。

**題 8**：`-2 -3 -2 -3`。截斷向 0 → `-2`；`floor` 往負無限大 → `-3`；`ceil` 往正無限大 → `-2`；`round` 的 .5 遠離 0 → `-3`。

**題 9**：`4 2 1 4`。小括號 `(4, 1)` 是「4 個 1」；大括號 `{4, 1}` 是「兩個元素：4 和 1」。

**題 10**：
- a) `static_cast<double>(sum) / n`
- b) `if (Dog* d = dynamic_cast<Dog*>(a)) d->bark();`
- c) `old_api(const_cast<char*>(name.c_str()));`
- d) `reinterpret_cast<uintptr_t>(ptr)`（或直接 `cout << ptr;`，指標本身就能印出位址）
