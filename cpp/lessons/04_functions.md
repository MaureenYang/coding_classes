# 04. 函式 (Functions)

> 程式練習：`C04 多條件排序`
>
> 先備知識：第 01 課「參考」的基本概念、第 03 課「return」。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 函式的組成 | 宣告、定義、簽章、參數與引數 |
| 第二部分 | 參數傳遞與回傳 | 傳值 / 傳參考 / 傳 const 參考 / 傳指標怎麼選；不能回傳區域變數的參考 |
| 第三部分 | 多載與預設參數 | 編譯器怎麼挑函式、什麼時候會「模稜兩可」 |
| 第四部分 | 函式的修飾 | `inline`、`constexpr`、`[[nodiscard]]`、`static` |
| 第五部分 | 函式也是值 | 函式指標、lambda、捕獲、`std::function`、比較函式的規則 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：函式的組成

## 1.1 函式 (Function)

**白話**：一段 **有名字、可以重複使用** 的程式碼，接收輸入（參數），產生輸出（回傳值）。

**比喻**：果汁機。放進水果（參數），按下按鈕（呼叫），得到果汁（回傳值）。你不需要知道裡面的刀片怎麼轉。

```cpp
//  回傳型別  名稱   參數列
    int       add(int a, int b) {
        return a + b;        // 函式本體
    }
```

## 1.2 參數 vs 引數 (Parameter vs Argument)

- **參數 (parameter)**：函式 **定義** 裡的變數名稱，`add(int a, int b)` 的 `a`、`b`。
- **引數 (argument)**：**呼叫** 時實際傳進去的值，`add(3, x)` 的 `3`、`x`。

**比喻**：表格上的欄位名稱「姓名：____」是參數；你填進去的「王小明」是引數。

## 1.3 宣告、定義、簽章

```cpp
int add(int a, int b);                    // 宣告（原型 prototype）：只說「有這個函式」
int add(int a, int b) { return a + b; }   // 定義：提供本體
```

- **宣告** 可以有很多次，**定義** 只能有一次。
- 函式要 **先宣告才能呼叫**。兩個函式互相呼叫時，至少要先寫一個的宣告。
- **簽章 (signature)**：函式名稱 + 參數的型別列表。**不包含回傳型別**。編譯器用簽章來區分不同的函式。

---

# 第二部分：參數傳遞與回傳

## 2.1 傳值 (Pass by Value)

**白話**：參數是引數的 **複製品**。函式裡怎麼改，都不影響外面的變數。

```cpp
void inc(int x) { x++; }
int a = 5;
inc(a);           // a 還是 5
```

**比喻**：影印一份文件給別人，他在影本上塗改，你的正本不受影響。

**成本**：要複製整個物件。`int` 很便宜，但 `vector<int>`（一百萬個元素）每次呼叫都複製一百萬個數字。

## 2.2 傳參考 (Pass by Reference)

**白話**：參數是引數的 **別名**。函式裡改它，就是改外面的變數。不會複製。

```cpp
void inc(int& x) { x++; }
int a = 5;
inc(a);           // a 變成 6
inc(5);           // ❌ 編譯錯誤：5 是右值，不能綁定到 int&
```

**比喻**：把文件 **正本** 交給對方，他改了就是真的改了。

## 2.3 傳 const 參考 (Pass by const Reference)

**白話**：**不複製**，也 **保證不會修改**。讀取大型物件的最佳選擇。

```cpp
double average(const vector<int>& v) {   // 不複製、不能改
    long long s = 0;
    for (int x : v) s += x;
    return v.empty() ? 0 : (double)s / v.size();
}
average({1, 2, 3});   // ✅ const 參考可以綁定到暫時物件
```

**比喻**：把正本放在玻璃櫃裡給對方看，看得到但摸不到。

## 2.4 傳指標 (Pass by Pointer)

**白話**：傳入物件的 **位址**。可以修改，而且 **可以傳 `nullptr` 表示「沒有」**。

```cpp
void reset(int* p) {
    if (p) *p = 0;    // 要先檢查是不是空指標
}
reset(&a);
reset(nullptr);       // 合法
```

## 2.5 怎麼選？

| 情況 | 寫法 |
|---|---|
| 小型別（`int`、`double`、`char`、指標），只讀 | **傳值** `int x` |
| 大型物件（`string`、`vector`、自訂類別），只讀 | **const 參考** `const T& x` |
| 要修改呼叫者的變數 | **參考** `T& x` |
| 參數「可以沒有」 | **指標** `T* x`（或 C++17 的 `std::optional`） |
| 函式內部本來就要複製一份來存 | 傳值，再 `std::move`（第 06 課） |

## 2.6 回傳值 (Return Value)

**回傳一個值**：直接回傳物件就好，不用擔心複製的成本。

```cpp
vector<int> make_list(int n) {
    vector<int> v(n);
    ...
    return v;         // 不會真的複製一百萬個元素
}
```

🔍 這是因為 **複製省略 (copy elision) / 回傳值最佳化 (RVO)**：編譯器直接在呼叫者準備好的位置建立 `v`，根本沒有複製。C++17 起某些情況是 **保證** 的。就算沒有省略，也會用 **移動**（第 06 課），成本很低。

**回傳多個值**：用 `pair`、`tuple` 或自訂 `struct`，搭配結構化綁定：

```cpp
pair<int, int> min_max(const vector<int>& v) { ... }
auto [lo, hi] = min_max(v);
```

## 2.7 懸空參考：絕對不能回傳區域變數的參考或指標

```cpp
int& bad() {
    int x = 42;
    return x;          // ❌ x 在函式結束時就被銷毀了
}
int* bad2() {
    int x = 42;
    return &x;         // ❌ 同樣的問題
}
int& r = bad();        // r 指向已經不存在的記憶體 → 懸空參考 (dangling reference)
```

**比喻**：退房之後還把飯店的房卡給朋友，朋友拿著房卡去開門 —— 房間可能已經是別人的了。

編譯器通常會警告 `reference to local variable returned`。**回傳參考只在「被參考的東西在函式結束後還活著」時才安全**，例如回傳成員變數、回傳傳進來的參考。

---

# 第三部分：多載與預設參數

## 3.1 函式多載 (Function Overloading)

**白話**：**同一個名字**，**參數列不同**，就是不同的函式。呼叫時編譯器依照引數的型別挑一個。

```cpp
int    area(int side)            { return side * side; }
int    area(int w, int h)        { return w * h; }
double area(double r)            { return 3.14159 * r * r; }

area(3);       // 第一個
area(3, 4);    // 第二個
area(2.0);     // 第三個
```

**比喻**：「開」這個字：開門、開車、開會 —— 同一個字，根據後面接的東西決定意思。

**不能只靠回傳型別區分**：

```cpp
int    f(int x);
double f(int x);     // ❌ 編譯錯誤：簽章一樣
```

## 3.2 🔍 多載解析 (Overload Resolution)

編譯器挑選的優先順序（簡化版）：

1. **完全符合**（包括加上 `const`、陣列轉指標這類小調整）
2. **提升 (promotion)**：`char`、`short`、`bool` → `int`；`float` → `double`
3. **標準轉換 (conversion)**：`int` → `double`、`double` → `int`、`long` → `int`……
4. 使用者定義的轉換（建構子、轉換運算子）

如果在 **同一個等級** 有兩個以上的候選，就是 **模稜兩可 (ambiguous)**，編譯錯誤：

```cpp
void f(int x);
void f(double x);
f(5);        // f(int)：完全符合
f(5.0f);     // f(double)：float → double 是提升
f(5L);       // ❌ 模稜兩可：long → int 和 long → double 都是「轉換」
f('a');      // f(int)：char → int 是提升
```

## 3.3 預設參數 (Default Argument)

```cpp
void print(const string& s, int times = 1, char end = '\n');
print("hi");           // times = 1, end = '\n'
print("hi", 3);        // end = '\n'
print("hi", 3, ' ');
```

規則：
- 預設值只能放在 **最右邊** 的參數（有預設值的參數右邊，全部都要有預設值）。
- 預設值寫在 **宣告** 裡，只寫一次（標頭檔裡寫了，定義就不要再寫）。
- 和多載混用容易模稜兩可：`void g(int a);` 和 `void g(int a, int b = 0);` → `g(1)` 不知道要呼叫哪個。

---

# 第四部分：函式的修飾

## 4.1 inline

**白話**：原本的意思是「建議編譯器把函式本體直接展開在呼叫處」，省掉呼叫的成本。

現代編譯器 **自己會決定要不要展開**，不太理會這個建議。`inline` 現在主要的作用是：**允許函式定義出現在多個編譯單元**（寫在標頭檔裡不會發生重複定義的錯誤，第 14 課）。

類別裡直接寫本體的成員函式，自動就是 `inline`。

## 4.2 constexpr 函式

**白話**：如果參數是編譯期常數，**整個函式在編譯時就算完**。

```cpp
constexpr long long fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }
constexpr long long F10 = fact(10);    // 編譯時就算好 3628800
int x; cin >> x;
long long y = fact(x);                 // 參數不是常數時，就跟普通函式一樣在執行時算
```

## 4.3 [[nodiscard]]

**白話**：標記「**呼叫這個函式卻不使用回傳值，很可能是 bug**」，編譯器會警告。

```cpp
[[nodiscard]] bool try_withdraw(long long amt);
try_withdraw(100);              // ⚠️ 警告：忽略了回傳值（提款失敗了你都不知道）
if (!try_withdraw(100)) ...     // ✅
```

`std::vector::empty()` 在 C++20 就是 `[[nodiscard]]`：寫 `v.empty();` 想清空 vector 是常見的錯誤（應該寫 `v.clear()`）。

## 4.4 static 函式（檔案內部）

**白話**：在 **全域** 函式前面加 `static`，代表「這個函式只有這個 `.cpp` 檔看得到」（內部連結，第 14 課）。和類別裡的 `static` 成員函式（第 07 課）是不同的意思。

---

# 第五部分：函式也是值

## 5.1 函式指標 (Function Pointer)

**白話**：存放「**函式位址**」的變數。可以把函式當成參數傳給別的函式。

```cpp
bool desc(int a, int b) { return a > b; }

bool (*cmp)(int, int) = desc;    // 宣告一個函式指標，語法很難讀
sort(v.begin(), v.end(), desc);  // 把函式傳給 sort
```

**比喻**：把「做事的方法」寫在紙條上交給別人，讓他照著做。

## 5.2 Lambda 運算式

**白話**：**就地定義的匿名函式**。不用另外取名字，寫在要用的地方。

```cpp
sort(v.begin(), v.end(), [](int a, int b) { return a > b; });
//                       ↑捕獲 ↑參數          ↑本體
```

完整語法：`[捕獲](參數) -> 回傳型別 { 本體 }`，回傳型別通常可以省略（自動推導）。

```cpp
auto square = [](int x) { return x * x; };
square(5);                                       // 25
auto add = [](auto a, auto b) { return a + b; }; // C++14 泛型 lambda：參數可以是任何型別
```

## 5.3 捕獲 (Capture)

**白話**：lambda 預設 **看不到** 外面的區域變數，要在 `[ ]` 裡寫出來，才能使用。

| 寫法 | 意思 |
|---|---|
| `[]` | 不捕獲任何東西 |
| `[x]` | 複製一份 `x`（**值捕獲**） |
| `[&x]` | 參考 `x`（**參考捕獲**） |
| `[=]` | 用到的外部變數全部值捕獲 |
| `[&]` | 用到的外部變數全部參考捕獲 |
| `[=, &y]` | 預設值捕獲，但 `y` 用參考 |
| `[this]` | 捕獲目前物件的指標（在成員函式裡） |

```cpp
int threshold = 10, count = 0;
auto big = [threshold](int x) { return x > threshold; };   // 複製 threshold
for_each(v.begin(), v.end(), [&count](int x) { if (x > 0) count++; });   // 修改外面的 count
```

**比喻**：
- **值捕獲**：出門前拍一張照片帶著走，之後外面怎麼變，照片都不會變。
- **參考捕獲**：帶著一支能即時看到現場的監視器畫面。

**值捕獲是在「建立 lambda 時」拍照**：

```cpp
int x = 1;
auto f = [x]() { return x; };
auto g = [&x]() { return x; };
x = 100;
f();   // 1
g();   // 100
```

值捕獲的變數預設是 **唯讀** 的；要修改那份複製品，lambda 要加 `mutable`：`[x]() mutable { x++; }`。

### 懸空捕獲

```cpp
function<int()> make_counter() {
    int count = 0;
    return [&count]() { return ++count; };   // ❌ count 在函式結束時銷毀了
}
```

參考捕獲的 lambda **活得比被捕獲的變數久** → 懸空參考。改成值捕獲 + `mutable`：`[count]() mutable { return ++count; }`。

## 5.4 std::function

**白話**：一個能裝 **任何「可以被呼叫的東西」**（函式、函式指標、lambda、函式物件）的容器，只要參數和回傳型別符合。

```cpp
#include <functional>
function<int(int, int)> op;
op = [](int a, int b) { return a + b; };
op = [](int a, int b) { return a * b; };
map<char, function<int(int, int)>> ops = {
    {'+', [](int a, int b) { return a + b; }},
    {'*', [](int a, int b) { return a * b; }},
};
ops['+'](3, 4);   // 7
```

代價：比直接呼叫 lambda 稍慢（有一層間接呼叫）。傳給 `sort` 這類模板函式時，直接傳 lambda 就好，不用包成 `function`。

## 5.5 比較函式的規則：嚴格弱序 (Strict Weak Ordering)

`sort`、`set`、`map`、`priority_queue` 的比較函式 `comp(a, b)` 代表「**a 要排在 b 前面**」，必須滿足：

1. **反自反**：`comp(a, a)` 一定是 `false`。
2. **反對稱**：`comp(a, b)` 是 `true` 時，`comp(b, a)` 一定是 `false`。
3. **遞移**：`comp(a, b)` 且 `comp(b, c)` → `comp(a, c)`。

```cpp
sort(v.begin(), v.end(), [](int a, int b) { return a >= b; });   // ❌ 違反第 1 條
```

用 `>=` 或 `<=` 的後果：`std::sort` 可能 **讀到陣列外面**、程式當掉，或排出錯的結果（未定義行為）。資料裡有很多相同的值時特別容易發生。

**多條件比較的標準寫法**（`C04`）：

```cpp
[](const Student& a, const Student& b) {
    if (a.score != b.score) return a.score > b.score;   // 第一條件
    if (a.age != b.age) return a.age < b.age;           // 第二條件
    return a.name < b.name;                             // 最後一個條件直接回傳
}
// 或用 tuple：tie 會依序比較
return tie(b.score, a.age, a.name) < tie(a.score, b.age, b.name);
```

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 函式 | Function | 有名字、可重複使用的程式碼 | 1.1 |
| 參數 / 引數 | Parameter / Argument | 定義裡的名字 / 呼叫時給的值 | 1.2 |
| 原型 | Prototype | 函式的宣告 | 1.3 |
| 簽章 | Signature | 名稱 + 參數型別，不含回傳型別 | 1.3 |
| 傳值 / 傳參考 | Pass by Value / Reference | 給複製品 / 給本人 | 2.1、2.2 |
| 複製省略 | Copy Elision / RVO | 回傳物件時直接建在目的地 | 2.6 |
| 懸空參考 | Dangling Reference | 參考到已經銷毀的物件 | 2.7 |
| 函式多載 | Function Overloading | 同名、參數不同 | 3.1 |
| 多載解析 | Overload Resolution | 編譯器挑選函式的規則 | 3.2 |
| 模稜兩可 | Ambiguous | 有兩個一樣好的候選，編譯錯誤 | 3.2 |
| 預設參數 | Default Argument | 沒給的參數用預設值 | 3.3 |
| 函式指標 | Function Pointer | 存放函式位址的變數 | 5.1 |
| Lambda | Lambda Expression | 就地定義的匿名函式 | 5.2 |
| 捕獲 | Capture | lambda 取用外部變數的方式 | 5.3 |
| 嚴格弱序 | Strict Weak Ordering | 比較函式必須遵守的規則 | 5.5 |

---

# 習題

### 題 1：預測輸出

```cpp
void f(int a, int& b, const int& c) { a++; b++; }
int main() {
    int x = 1, y = 1, z = 1;
    f(x, y, z);
    cout << x << y << z;
}
```

### 題 2：哪些呼叫可以編譯？呼叫的是哪個版本？

```cpp
void g(int x);
void g(double x);
void g(const string& s);

a) g(1);   b) g(1.5f);   c) g('c');   d) g(2LL);   e) g("hi");
```

### 題 3：找 bug

```cpp
const string& longer(const string& a, const string& b) {
    string result = a.size() > b.size() ? a : b;
    return result;
}
```

### 題 4：預測輸出

```cpp
int n = 1;
auto a = [n]() { return n * 10; };
auto b = [&n]() { return n * 10; };
n = 5;
cout << a() << ' ' << b();
```

### 題 5：這個 swap 為什麼沒效？怎麼改？

```cpp
void my_swap(int a, int b) { int t = a; a = b; b = t; }
```

### 題 6：下面的比較函式有什麼問題？

```cpp
sort(v.begin(), v.end(), [](const Point& p, const Point& q) {
    return p.x <= q.x;
});
```

### 題 7：預測輸出

```cpp
int counter = 0;
auto inc = [counter]() mutable { return ++counter; };
inc(); inc();
cout << inc() << ' ' << counter;
```

### 題 8：選擇最適合的參數寫法

```
a) 計算 vector<double> 的平均值
b) 把 string 轉成大寫（直接修改傳進來的字串）
c) 計算兩個 int 的最大公因數
d) 在樹中尋找節點，找不到時回傳「沒有」
```

---

# 習題解答

**題 1**：`121`。`a` 是傳值（外面的 x 不變）；`b` 是參考（y 變成 2）；`c` 是 const 參考（不能改，也沒改）。

**題 2**：
- a) `g(int)`：完全符合。
- b) `g(double)`：`float → double` 是提升。
- c) `g(int)`：`char → int` 是提升。
- d) **模稜兩可**：`long long → int` 和 `long long → double` 都是轉換。
- e) `g(const string&)`：`"hi"` 透過 `string` 的建構子轉換（使用者定義的轉換）。

**題 3**：`result` 是 **區域變數**，函式結束時就銷毀了，回傳它的參考是 **懸空參考**。改法：回傳值 `string longer(...)`，或直接回傳參數 `return a.size() > b.size() ? a : b;`（參數本來就是外面的物件，還活著）。

**題 4**：`10 50`。`a` 在建立時複製了 `n = 1`；`b` 參考 `n`，呼叫時 `n` 已經是 5。

**題 5**：參數是 **傳值**，交換的是複製品。改成 `void my_swap(int& a, int& b)`。（或直接用 `std::swap`。）

**題 6**：用了 `<=`，違反 **嚴格弱序**（`comp(p, p)` 是 `true`）。`x` 相同的點很多時，`std::sort` 可能當掉或排錯。改成 `p.x < q.x`。

**題 7**：`3 0`。`mutable` 讓 lambda 可以修改 **自己那份複製品**，複製品在呼叫之間會保留（1 → 2 → 3）；外面的 `counter` 完全沒被改到。

**題 8**：
- a) `const vector<double>&`：大型物件、只讀。
- b) `string&`：要修改呼叫者的字串。
- c) `int`：小型別、只讀，傳值最簡單也最快。
- d) 回傳 `Node*`（找不到回傳 `nullptr`），或 `std::optional`。

---

# 程式練習

- **`C04 多條件排序`**：用 lambda 寫多條件比較函式；測資有大量完全相同的資料，用 `<=` 寫的比較函式會出問題。
