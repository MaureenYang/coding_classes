# 01. 型別、變數與型別轉換

> 程式練習：本課沒有獨立的程式題，觀念會在 `C01`、`C02`、`C13` 中反覆用到。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 型別系統 | 各種型別的大小與範圍「保證」是什麼、字面值的型別 |
| 第二部分 | 宣告、定義、初始化 | 五種初始化寫法的差別、未初始化的危險、`auto` |
| 第三部分 | `const` 與 `constexpr` | 「不能改」和「編譯期就知道」的差別 |
| 第四部分 | 作用域與生命週期 | 變數「在哪裡看得到」和「活多久」是兩件事 |
| 第五部分 | 型別轉換 | 隱式轉換的陷阱、四種 C++ 轉型 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：型別系統

## 1.1 靜態型別 (Static Typing)

**白話**：C++ 的每個變數、每個運算式，在 **編譯時** 就確定了型別，而且之後不能變。編譯器會根據型別決定：要用多少記憶體、能做哪些運算、運算的規則是什麼。

**比喻**：容器上貼了標籤「醬油」，就只能裝醬油。Python 像是沒貼標籤的瓶子，什麼都能裝，但打開之前不知道裡面是什麼。

好處：很多錯誤在 **編譯時** 就被抓到，而且編譯器能產生很快的機器碼。

## 1.2 基本型別的「保證」

C++ 標準 **只保證最小範圍**，實際大小看平台：

| 型別 | 標準保證 | 常見的 64 位元 Linux | 64 位元 Windows |
|---|---|---|---|
| `char` | 至少 8 bits | 8 bits | 8 bits |
| `short` | 至少 16 bits | 16 | 16 |
| `int` | 至少 16 bits | 32 | 32 |
| `long` | 至少 32 bits | **64** | **32** |
| `long long` | 至少 64 bits | 64 | 64 |
| `float` / `double` | — | 32 / 64 bits（IEEE 754） | 同左 |

> ⚠️ `long` 在 Linux 是 64 位元、在 Windows 是 32 位元。**要確定大小時，用 `long long` 或 `<cstdint>` 的固定寬度型別**：

```cpp
#include <cstdint>
int32_t a;    // 剛好 32 位元
int64_t b;    // 剛好 64 位元
uint8_t c;    // 剛好 8 位元、無號
```

**`sizeof`**：回傳型別或物件佔幾個 byte，型別是 `size_t`（無號）。`sizeof(char)` 永遠是 1。

## 1.3 char 的正負號

**白話**：`char` 到底是有號還是無號，**由編譯器決定**（x86 上通常有號，ARM 上通常無號）。

```cpp
char c = 200;          // 有號的 char 存不下 200，變成 -56
if (c > 100) ...       // 在 x86 上是 false！
```

所以把 `char` 傳給 `isalpha`、`tolower` 這類函式時，要先轉成 `unsigned char`（`C11` 題的提示）。
`char`、`signed char`、`unsigned char` 是 **三個不同的型別**。

## 1.4 字面值 (Literal) 的型別

**白話**：直接寫在程式裡的值，例如 `42`、`3.14`、`'a'`，也有型別。

| 寫法 | 型別 | 說明 |
|---|---|---|
| `42` | `int` | 太大放不下時會自動變成 `long` 或 `long long` |
| `42u` / `42U` | `unsigned int` | |
| `42LL` | `long long` | |
| `42ULL` | `unsigned long long` | |
| `0x2A` / `052` / `0b101010` | `int` | 十六進位 / **八進位（開頭是 0）** / 二進位 |
| `3.14` | `double` | |
| `3.14f` | `float` | |
| `1e9` | **`double`** | 科學記號一律是浮點數！ |
| `'a'` | `char` | 單引號 |
| `"a"` | `const char[2]` | 雙引號：字串，結尾有 `'\0'`，所以長度 2 |
| `1'000'000` | `int` | C++14 起可以用 `'` 分隔數字，方便閱讀 |

**常見陷阱**：

```cpp
int x = 010;               // 是 8，不是 10！開頭的 0 代表八進位
long long y = 1 << 40;     // 1 是 int，先在 int 裡溢位，才轉成 long long → 錯
long long z = 1LL << 40;   // 正確
long long w = 1e18 + 1;    // 1e18 是 double，+1 的精度不夠，結果是 1e18
```

---

# 第二部分：宣告、定義、初始化

## 2.1 宣告 vs 定義 (Declaration vs Definition)

- **宣告**：告訴編譯器「有這個名字，它是什麼型別」。可以宣告很多次。
- **定義**：真正 **配置記憶體**（變數）或 **提供本體**（函式）。整個程式只能定義一次（第 14 課的 ODR）。

```cpp
extern int counter;        // 宣告：counter 在別的地方定義
int counter = 0;           // 定義
int add(int a, int b);     // 函式宣告（原型）
int add(int a, int b) { return a + b; }   // 函式定義
```

**比喻**：宣告是「名片」（告訴你這個人存在、怎麼聯絡）；定義是「這個人本身」。

## 2.2 未初始化 (Uninitialized)

**白話**：**區域變數** 宣告時沒給初值，裡面的值是 **不確定的**（垃圾值），讀取它是未定義行為。

```cpp
int main() {
    int sum;                 // 垃圾值！
    for (int i = 0; i < 3; i++) sum += i;   // 結果無法預測
}
```

**全域變數** 和 **`static` 變數** 則會自動初始化成 0。

**比喻**：租到一間沒打掃過的房間，抽屜裡可能有前一個房客留下的東西。區域變數用的記憶體，可能剛被別的函式用過。

## 2.3 五種初始化寫法

| 寫法 | 名稱 | 說明 |
|---|---|---|
| `int a;` | 預設初始化 (default) | 區域變數是垃圾值 |
| `int a = 5;` | 複製初始化 (copy) | 最常見 |
| `int a(5);` | 直接初始化 (direct) | |
| `int a{5};` | 列表初始化 (list / brace) | C++11，**禁止窄化轉換** |
| `int a{};` | 值初始化 (value) | 一定是 0 |

**窄化轉換 (Narrowing Conversion)**：可能 **遺失資訊** 的轉換，例如 `double → int`、`long long → int`。大括號會擋下來：

```cpp
int a = 3.7;      // 可以編譯，a == 3（小數被截掉，可能只有警告）
int b{3.7};       // 編譯錯誤！大括號不允許窄化
int c{};          // 0，保證有初值
```

**建議**：不確定時用 **大括號**，讓編譯器幫你抓錯。

### 🔍 最令人困擾的解析 (Most Vexing Parse)

```cpp
Widget w();       // 你以為：建立一個 Widget 物件
                  // 實際上：宣告一個「沒有參數、回傳 Widget 的函式」叫 w！
Widget w2{};      // 用大括號就沒有這個問題
Widget w3;        // 或乾脆不要括號
```

C++ 的規則是「能被解讀成宣告的，就是宣告」。

## 2.4 auto：讓編譯器推導型別

**白話**：`auto` 讓編譯器根據 **初始值** 決定型別。

```cpp
auto a = 42;          // int
auto b = 42LL;        // long long
auto c = 1e9;         // double！
auto d = v.begin();   // vector<int>::iterator，不用寫一長串
auto e = "hi";        // const char*，不是 std::string！
```

**陷阱**：`auto` 會 **丟掉** 參考和頂層 `const`：

```cpp
const int& r = x;
auto y = r;           // y 是 int（複製品），不是 const int&
auto& z = r;          // z 是 const int&
```

**比喻**：`auto` 像是「照著樣品做一個新的」，做出來的是 **複製品**，不是樣品本身。

---

# 第三部分：const 與 constexpr

## 3.1 const：唯讀

**白話**：`const` 變數 **初始化之後不能修改**。違反的話編譯錯誤。

```cpp
const int MAX = 100;
MAX = 200;            // 編譯錯誤
const int n = read(); // 可以：值在執行時才知道，但之後不能改
```

**為什麼要用？** 讓編譯器幫你檢查「這個不應該被改」，也讓讀程式的人一眼就知道。這叫 **const 正確性 (const correctness)**，第 05、07 課會再看到。

## 3.2 constexpr：編譯期常數

**白話**：`constexpr` 要求值在 **編譯時** 就能算出來。

```cpp
constexpr int N = 1000;          // 編譯時就知道
int arr[N];                      // 可以當陣列大小
constexpr int sq(int x) { return x * x; }
constexpr int K = sq(12);        // 編譯時就算好 144，執行時完全不花時間
```

| | `const` | `constexpr` |
|---|---|---|
| 意思 | 執行期間不能改 | 編譯時就要知道值 |
| 初始值 | 可以是執行時才知道的 | 必須是編譯期常數 |
| 可以當陣列大小 / 模板參數 | 只有初始值是常數時 | ✅ |

**比喻**：`const` 是「印好之後不能修改的考卷」；`constexpr` 是「出題時就已經印好的考卷」。

---

# 第四部分：作用域與生命週期

這是兩個 **不同** 的概念，常被搞混。

## 4.1 作用域 (Scope)：在哪裡「看得到」這個名字

| 作用域 | 範圍 |
|---|---|
| 區塊作用域 (block) | 從宣告處到所在的 `}` |
| 函式參數 | 整個函式本體 |
| 命名空間 / 全域 (namespace / global) | 從宣告處到檔案結尾 |
| 類別作用域 (class) | 類別的所有成員函式裡 |

**遮蔽 (Shadowing)**：內層宣告了 **同名** 的變數，會蓋住外層的。

```cpp
int x = 1;
void f() {
    int x = 2;            // 遮蔽了全域的 x
    {
        int x = 3;        // 又遮蔽了外面的 x
        cout << x;        // 3
    }
    cout << x << ::x;     // 2 1（::x 指定全域的 x）
}
```

遮蔽很容易造成 bug（以為在改外面的變數，其實改的是自己的），編譯時加 `-Wshadow` 會警告。

## 4.2 生命週期 (Lifetime) / 儲存期 (Storage Duration)：變數「活多久」

| 儲存期 | 什麼時候建立 | 什麼時候銷毀 | 例子 |
|---|---|---|---|
| 自動 (automatic) | 執行到宣告的地方 | 離開所在的區塊 | 區域變數 |
| 靜態 (static) | 程式開始（或第一次執行到） | 程式結束 | 全域變數、`static` 變數 |
| 動態 (dynamic) | `new` | `delete` | heap 上的物件 |
| 執行緒 (thread) | 執行緒開始 | 執行緒結束 | `thread_local` |

## 4.3 static 區域變數

**白話**：在函式裡加 `static` 的變數，**作用域** 只在函式裡（外面看不到），但 **生命週期** 是整個程式 —— 函式結束後它還活著，值會保留到下一次呼叫。

```cpp
int next_id() {
    static int id = 0;    // 只在第一次執行到這行時初始化
    return ++id;
}
next_id();  // 1
next_id();  // 2
```

**比喻**：辦公室裡你的抽屜（作用域：只有你能開），下班之後東西還在（生命週期：一直存在）。普通區域變數則像是會議室的白板，開完會就擦掉。

---

# 第五部分：型別轉換

## 5.1 隱式轉換 (Implicit Conversion)

**白話**：編譯器 **自動** 幫你做的轉換。方便，但也是很多 bug 的來源。

### 整數提升 (Integral Promotion)

比 `int` 小的型別（`char`、`short`、`bool`）參與運算時，**先被轉成 `int`**。

```cpp
char a = 100, b = 100;
auto c = a + b;     // c 是 int，值 200（不會在 char 裡溢位）
```

### 一般算術轉換 (Usual Arithmetic Conversions)

兩邊型別不同時，**轉成「比較大」的那一邊**：`int + long long → long long`、`int + double → double`。

**最危險的情況：有號 和 無號 混在一起**，有號的會被轉成 **無號**：

```cpp
int a = -1;
unsigned int b = 0;
if (a < b) cout << "yes";      // 不會印！-1 變成 4294967295，比 0 大

vector<int> v;
if (-1 < v.size()) ...         // false！同樣的原因
```

編譯時加 `-Wall -Wextra` 會出現 `comparison of integer expressions of different signedness` 警告 —— **不要忽略它**。

### 浮點數轉整數

**白話**：小數部分直接 **截掉**（向 0 取整），不是四捨五入。超出整數範圍是未定義行為。

```cpp
int a = 3.99;        // 3
int b = -3.99;       // -3
int c = 1e20;        // 未定義行為！
int d = (int)(x + 0.5);   // 正數的四捨五入；負數要另外處理，或用 std::lround
```

## 5.2 顯式轉換：四種 C++ 轉型

C 語言的 `(int)x` 什麼都能轉，太危險。C++ 把它拆成四種，**各自只做一件事**，而且在程式碼裡很好搜尋。

| 轉型 | 用途 | 安全性 |
|---|---|---|
| `static_cast<T>(x)` | 一般的轉換：數值型別互轉、`void*` 轉回原本的指標、往下轉型（不檢查） | 編譯期檢查 |
| `dynamic_cast<T>(x)` | 多型類別的 **往下轉型**，執行時檢查是否正確（第 08 課） | 執行期檢查 |
| `const_cast<T>(x)` | 加上或 **拿掉** `const` | 拿掉後去修改原本是 `const` 的物件 → 未定義行為 |
| `reinterpret_cast<T>(x)` | 把位元 **重新解讀** 成別的型別（指標 ↔ 整數等） | 非常危險，幾乎用不到 |

```cpp
int total = 7, cnt = 2;
double avg = static_cast<double>(total) / cnt;   // 3.5（先轉再除）
double bad = static_cast<double>(total / cnt);   // 3.0（先整數除法再轉，太晚了）
```

**比喻**：C 的轉型像萬能鑰匙，什麼門都能開，但開錯門也不會有人阻止你。C++ 的四種轉型像是四把專用鑰匙，用錯了編譯器會告訴你。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 靜態型別 | Static Typing | 型別在編譯時決定，之後不變 | 1.1 |
| 固定寬度整數 | Fixed-width Integer | `int32_t`、`int64_t` 等保證大小的型別 | 1.2 |
| 字面值 | Literal | 直接寫在程式裡的值 | 1.4 |
| 宣告 / 定義 | Declaration / Definition | 告訴編譯器有這個名字 / 真正配置或實作 | 2.1 |
| 未初始化 | Uninitialized | 沒給初值，內容不確定 | 2.2 |
| 列表初始化 | List Initialization | 大括號初始化，禁止窄化 | 2.3 |
| 窄化轉換 | Narrowing Conversion | 可能遺失資訊的轉換 | 2.3 |
| 最令人困擾的解析 | Most Vexing Parse | `T x();` 被當成函式宣告 | 2.3 |
| 型別推導 | Type Deduction (`auto`) | 讓編譯器依初始值決定型別 | 2.4 |
| 編譯期常數 | constexpr | 編譯時就算好的值 | 3.2 |
| const 正確性 | Const Correctness | 不該改的東西都標成 const | 3.1 |
| 作用域 | Scope | 名字在哪裡看得到 | 4.1 |
| 遮蔽 | Shadowing | 內層同名變數蓋住外層 | 4.1 |
| 生命週期 / 儲存期 | Lifetime / Storage Duration | 變數活多久 | 4.2 |
| 整數提升 | Integral Promotion | 小型別運算時先轉成 int | 5.1 |
| 一般算術轉換 | Usual Arithmetic Conversions | 兩邊型別不同時轉成較大的 | 5.1 |
| 靜態轉型 | static_cast | 一般用途的明確轉型 | 5.2 |

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

### 題 5：`auto` 推導出什麼型別？

```cpp
auto a = 'x';
auto b = 10 / 4;
auto c = 10 / 4.0;
auto d = "text";
const int k = 5;
auto e = k;
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

---

# 習題解答

**題 1**：印出 `1` 和 `4294967295`。`a + b` 中 `b` 被轉成 `unsigned int`，`-2` 變成 `4294967294`，加 1 得到 `4294967295`（就是 -1 的無號表示），當然 `> 0`。

**題 2**：
- `a`：可以，`a == 2`（截掉小數，可能有警告）。
- `b`：**編譯錯誤**，大括號禁止 `double → int` 的窄化。
- `c`：可以，`c == 2`。
- `d`：可以，`int → long long` 不是窄化。
- `e`：`5LL` 是 **常數** 而且放得進 `int`，所以 **可以**（窄化規則對常數會檢查實際值）。

**題 3**：三個 bug：
1. `sum` 沒有初始化，是垃圾值 → `int sum = 0;`
2. `sum / v.size()`：整數除法（而且 `int` 會被轉成無號的 `size_t`），小數不見了 → `static_cast<double>(sum) / v.size()`。
3. `v` 是空的時候除以 0 → 要先檢查。
（`sum` 也可能溢位，大量資料時用 `long long`。）

**題 4**：`101112`。`c` 只在第一次初始化成 10，之後保留上次的值；`c++` 回傳的是加 1 之前的值。

**題 5**：`a` 是 `char`；`b` 是 `int`（值 2，整數除法）；`c` 是 `double`（2.5）；`d` 是 `const char*`；`e` 是 `int`（`auto` 丟掉頂層 `const`）。

**題 6**：**不一樣**。Linux 64 位元的 `long` 是 64 位元，印出 `3000000000`；Windows 的 `long` 是 32 位元，放不下，結果不同。要用 `long long`。

**題 7**：只能用 `const`。`n` 是執行時才讀入的，`n * 2` 不是編譯期常數，不能用 `constexpr`。
