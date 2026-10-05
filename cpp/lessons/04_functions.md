# 04. 函式 (Functions)

> 程式練習：`C04 多條件排序`
>
> 先備知識：第 01 課「參考」的基本概念、第 03 課「return」。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 函式的組成 | 宣告、定義、簽章、參數與引數、呼叫時發生了什麼 |
| 第二部分 | 參數傳遞與回傳 | 傳值 / 傳參考 / 傳 const 參考 / 傳指標怎麼選；回傳多個值；懸空參考 |
| 第三部分 | 多載與預設參數 | 編譯器怎麼挑函式、什麼時候會「模稜兩可」 |
| 第四部分 | 函式的修飾 | `inline`、`constexpr`、`[[nodiscard]]`、`static`、遞迴 |
| 第五部分 | 函式也是值 | 函式指標、lambda、捕獲、`std::function`、比較函式的規則 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：...` 是實際執行的結果。標 🔍 的是深入內容。

---

# 第一部分：函式的組成

## 1.1 函式 (Function)

**是什麼**：一段 **有名字、可以重複使用** 的程式碼。接收輸入（參數），產生輸出（回傳值）。

**為什麼需要**：
1. **重複使用**：同樣的邏輯寫一次，到處呼叫。
2. **分解問題**：把大問題拆成小函式，每個函式只做一件事。
3. **好讀、好測試**：看到 `is_leap(year)` 就知道在做什麼，不用讀裡面的細節。

**比喻**：果汁機。放進水果（參數），按下按鈕（呼叫），得到果汁（回傳值）。你不需要知道裡面的刀片怎麼轉。

```cpp
//  回傳型別   名稱      參數列
    int       add      (int a, int b) {
        return a + b;                 // 函式本體
    }

int main() {
    int r = add(3, 4);                // 呼叫：引數是 3 和 4
    cout << r << '\n';                // 輸出：7
    cout << add(r, 10) << '\n';       // 引數可以是任何運算式 → 輸出：17
}
```

**沒有回傳值** 的函式，回傳型別寫 `void`：

```cpp
void greet(const string& name) {
    cout << "Hello, " << name << "!\n";
}
greet("Amy");                         // 輸出：Hello, Amy!
```

**沒有參數** 的函式，參數列留空：

```cpp
int roll_dice() { return rand() % 6 + 1; }
```

## 1.2 參數 vs 引數 (Parameter vs Argument)

| | 參數 (parameter) | 引數 (argument) |
|---|---|---|
| 在哪裡 | 函式 **定義** 裡 | 函式 **呼叫** 時 |
| 是什麼 | 一個變數名稱 | 實際傳進去的值 |
| 例子 | `int add(int a, int b)` 的 `a`、`b` | `add(3, x)` 的 `3`、`x` |

**比喻**：表格上的欄位「姓名：____」是參數；你填進去的「王小明」是引數。

## 1.3 呼叫時發生了什麼

```cpp
int square(int x) {
    int r = x * x;
    return r;
}
int main() {
    int a = 5;
    int b = square(a + 1);
    cout << b << '\n';                // 輸出：36
}
```

逐步拆解：
1. 計算引數 `a + 1` → `6`。
2. 建立參數 `x`，用 `6` 初始化（**複製**）。
3. 跳到 `square` 的本體執行，建立區域變數 `r = 36`。
4. `return r;` 把 `36` 帶回呼叫的地方，`x` 和 `r` 被銷毀。
5. `b` 被初始化成 `36`。

每次呼叫，參數和區域變數都存在 **呼叫堆疊 (call stack)** 上一個新的「框架」裡，函式結束時框架就被拿掉（DS 路線第 02 課有詳細的圖）。

## 1.4 宣告、定義、簽章

**宣告（原型 prototype）**：只說「有這個函式、它長什麼樣子」。
**定義**：提供函式的本體。

```cpp
int add(int a, int b);                    // 宣告：參數名稱可以省略 → int add(int, int);
int add(int a, int b) { return a + b; }   // 定義
```

**規則**：
- **呼叫之前，編譯器必須先看過宣告**（或定義）。
- **宣告可以有很多次，定義只能有一次**。

**為什麼需要分開宣告？**

**情況 1：函式定義寫在 main 後面**

```cpp
double area(double r);                    // 先宣告
int main() {
    cout << area(2.0) << '\n';            // 輸出：12.5664
}
double area(double r) { return 3.14159265 * r * r; }
```

**情況 2：兩個函式互相呼叫**

```cpp
bool is_odd(int n);                       // 必須先宣告其中一個
bool is_even(int n) { return n == 0 ? true : is_odd(n - 1); }
bool is_odd(int n)  { return n == 0 ? false : is_even(n - 1); }
cout << is_even(10) << is_odd(7) << '\n'; // 輸出：11
```

**情況 3：多檔案專案**（第 14 課）：宣告放在 `.h`，定義放在 `.cpp`。

**簽章 (signature)**：函式名稱 + **參數的型別列表**。**不包含回傳型別、也不包含參數名稱**。編譯器用簽章來區分不同的函式（第三部分的多載）。

| 宣告 | 簽章 |
|---|---|
| `int add(int a, int b)` | `add(int, int)` |
| `double add(double x, double y)` | `add(double, double)` |
| `long add(int p, int q)` | `add(int, int)` ← 和第一個一樣！不能同時存在 |

---

# 第二部分：參數傳遞與回傳

## 2.1 傳值 (Pass by Value)

**是什麼**：參數是引數的 **複製品**。函式裡怎麼改參數，都 **不影響** 外面的變數。

```cpp
void try_change(int x) {
    x = 100;                          // 改的是複製品
    cout << "inside: " << x << '\n';
}
int a = 5;
try_change(a);                        // 輸出：inside: 100
cout << "outside: " << a << '\n';     // 輸出：outside: 5（沒變）
```

**比喻**：影印一份文件給別人，他在影本上塗改，你的正本完全不受影響。

**成本**：要複製整個物件。`int`、`double`、`char` 很便宜；但 `string`、`vector` 每次呼叫都要複製全部的內容：

```cpp
long long sum_bad(vector<int> v) {        // 每次呼叫都複製整個 vector
    long long s = 0;
    for (int x : v) s += x;
    return s;
}
vector<int> big(1000000, 1);
for (int i = 0; i < 1000; i++) sum_bad(big);   // 複製了 1000 次 × 100 萬個元素 → 很慢
```

## 2.2 傳參考 (Pass by Reference)

**是什麼**：參數是引數的 **別名**。函式裡改參數，**就是改外面的變數**。而且 **不會複製**。

```cpp
void change(int& x) {
    x = 100;                          // 改的就是外面的變數
}
int a = 5;
change(a);
cout << a << '\n';                    // 輸出：100
```

**比喻**：把文件 **正本** 交給對方，他改了就是真的改了。

**經典例子：交換兩個變數**

```cpp
void swap_bad(int a, int b) { int t = a; a = b; b = t; }   // 傳值：交換的是複製品
void swap_ok(int& a, int& b) { int t = a; a = b; b = t; }  // 傳參考：交換的是本人

int x = 1, y = 2;
swap_bad(x, y);
cout << x << y << '\n';               // 輸出：12（沒變）
swap_ok(x, y);
cout << x << y << '\n';               // 輸出：21
```

**用參考「回傳」多個結果**（舊式寫法，現在比較常用 2.6 的方式）：

```cpp
void min_max(const vector<int>& v, int& mn, int& mx) {
    mn = mx = v[0];
    for (int x : v) { mn = min(mn, x); mx = max(mx, x); }
}
int lo, hi;
min_max({3, 9, 1, 7}, lo, hi);
cout << lo << ' ' << hi << '\n';      // 輸出：1 9
```

**限制**：非 const 的參考 **不能綁定到暫時的值（右值）**：

```cpp
// change(5);                         // ❌ error: cannot bind non-const lvalue reference to an rvalue
// change(a + 1);                     // ❌ a + 1 是暫時的值
```

道理很簡單：函式說「我要修改你給我的東西」，但 `5` 或 `a + 1` 是暫時的值，改了也沒有意義。

## 2.3 傳 const 參考 (Pass by const Reference)

**是什麼**：**不複製**，而且 **保證不會修改**。讀取大型物件的最佳選擇。

```cpp
long long sum_good(const vector<int>& v) {    // 不複製、也不能改
    long long s = 0;
    for (int x : v) s += x;
    // v.push_back(1);                        // ❌ 編譯錯誤：v 是 const
    return s;
}
```

**const 參考可以接受暫時的值**：

```cpp
void print(const string& s) { cout << s << '\n'; }
string name = "Amy";
print(name);                  // ✅ 左值
print("Bob");                 // ✅ "Bob" 先轉成暫時的 string，再綁定到 s → 輸出：Bob
print(name + "!");            // ✅ 暫時的 string → 輸出：Amy!
```

**比喻**：把正本放在玻璃櫃裡給對方看，看得到但摸不到。

## 2.4 傳指標 (Pass by Pointer)

**是什麼**：傳入物件的 **位址**。可以修改，而且 **可以傳 `nullptr` 表示「沒有」**。

```cpp
void reset(int* p) {
    if (p != nullptr) *p = 0;         // 一定要先檢查是不是空指標
}
int a = 5;
reset(&a);                            // 傳位址要用 &
cout << a << '\n';                    // 輸出：0
reset(nullptr);                       // 合法：什麼都不做
```

**什麼時候用指標而不是參考？** 當參數 **可以不存在** 的時候：

```cpp
// 找到就把位置寫進 *pos；呼叫者不在乎位置時可以傳 nullptr
bool find_value(const vector<int>& v, int target, int* pos) {
    for (int i = 0; i < (int)v.size(); i++)
        if (v[i] == target) {
            if (pos) *pos = i;
            return true;
        }
    return false;
}
int where;
cout << find_value({5, 7, 9}, 7, &where) << ' ' << where << '\n';   // 輸出：1 1
cout << find_value({5, 7, 9}, 8, nullptr) << '\n';                  // 輸出：0
```

## 2.5 怎麼選？

| 情況 | 寫法 | 範例 |
|---|---|---|
| 小型別（`int`、`double`、`char`、指標），只讀 | **傳值** `T x` | `bool is_prime(int n)` |
| 大型物件（`string`、`vector`、類別），只讀 | **const 參考** `const T& x` | `double average(const vector<int>& v)` |
| 要修改呼叫者的變數 | **參考** `T& x` | `void to_upper(string& s)` |
| 參數「可以沒有」 | **指標** `T* x`（或 `std::optional`） | `void log(const char* msg, int* code)` |
| 函式內部本來就要複製一份存起來 | 傳值，再 `std::move`（第 06 課） | `Person(string name) : name_(std::move(name))` |

每一列的完整範例：

```cpp
bool is_prime(int n) {                                // 小型別：傳值
    if (n < 2) return false;
    for (int d = 2; d * d <= n; d++) if (n % d == 0) return false;
    return true;
}
double average(const vector<int>& v) {                // 大型、只讀：const 參考
    if (v.empty()) return 0;
    long long s = 0;
    for (int x : v) s += x;
    return (double)s / v.size();
}
void to_upper(string& s) {                            // 要修改：參考
    for (char& c : s) c = toupper((unsigned char)c);
}

cout << is_prime(97) << '\n';                         // 輸出：1
cout << average({1, 2, 3, 4}) << '\n';                // 輸出：2.5
string word = "hello";
to_upper(word);
cout << word << '\n';                                 // 輸出：HELLO
```

**為什麼小型別不用 const 參考？** 參考在底層通常是用指標實作的（8 bytes），傳 `int`（4 bytes）的複製品反而更小、更快，而且不用透過指標間接存取。

## 2.6 回傳值 (Return Value)

### 回傳一個物件：直接回傳，不用擔心成本

```cpp
vector<int> make_squares(int n) {
    vector<int> v(n);
    for (int i = 0; i < n; i++) v[i] = i * i;
    return v;                         // 不會真的複製整個 vector
}
vector<int> sq = make_squares(5);
for (int x : sq) cout << x << ' ';    // 輸出：0 1 4 9 16
cout << '\n';
```

🔍 **複製省略 (copy elision) / 回傳值最佳化 (RVO)**：編譯器直接在「呼叫者準備好的位置」建立 `v`，根本沒有複製。用一個會印出建構和複製的類別觀察：

```cpp
struct Big {
    Big() { cout << "construct "; }
    Big(const Big&) { cout << "copy "; }
};
Big make() { Big b; return b; }
Big x = make();
cout << '\n';                         // 輸出：construct（沒有 copy！）
```

C++17 起，`return Big();` 這種直接回傳暫時物件的情況是 **保證** 省略的。就算編譯器沒有省略，也會用 **移動**（第 06 課），成本很低。

### 回傳多個值

**方法 1：pair（兩個值）**

```cpp
pair<int, int> divmod(int a, int b) { return {a / b, a % b}; }
auto [q, r] = divmod(17, 5);          // C++17 結構化綁定
cout << q << ' ' << r << '\n';        // 輸出：3 2
```

**方法 2：tuple（三個以上）**

```cpp
tuple<int, int, double> stats(const vector<int>& v) {
    int mn = *min_element(v.begin(), v.end());
    int mx = *max_element(v.begin(), v.end());
    double avg = accumulate(v.begin(), v.end(), 0.0) / v.size();
    return {mn, mx, avg};
}
auto [mn, mx, avg] = stats({4, 8, 6});
cout << mn << ' ' << mx << ' ' << avg << '\n';   // 輸出：4 8 6
```

**方法 3：自訂 struct（最清楚：每個欄位有名字）**

```cpp
struct Stats { int min, max; double avg; };
Stats stats2(const vector<int>& v) { /* ... */ return {4, 8, 6.0}; }
Stats s = stats2({4, 8, 6});
cout << s.max << '\n';                // 輸出：8（看名字就知道是什麼，不用記第幾個）
```

**方法 4：optional（可能沒有結果，C++17，第 15 課）**

```cpp
optional<int> find_index(const vector<int>& v, int target) {
    for (int i = 0; i < (int)v.size(); i++) if (v[i] == target) return i;
    return nullopt;                   // 找不到
}
if (auto idx = find_index({5, 7, 9}, 9)) cout << *idx << '\n';   // 輸出：2
```

## 2.7 懸空參考：絕對不能回傳區域變數的參考或指標

**是什麼**：函式回傳了 **指向區域變數** 的參考或指標。但區域變數在函式結束時就被銷毀了，呼叫者拿到的參考 / 指標指向 **已經不存在的東西**。

```cpp
int& bad_ref() {
    int x = 42;
    return x;          // ❌ warning: reference to local variable 'x' returned
}
int* bad_ptr() {
    int x = 42;
    return &x;         // ❌ warning: address of local variable 'x' returned
}
const string& bad_str() {
    string s = "temp";
    return s;          // ❌ 同樣的問題
}
// int& r = bad_ref();    → r 是懸空參考，使用它是未定義行為：可能印出 42、垃圾值，或當掉
```

**比喻**：退房之後還把飯店的房卡給朋友，朋友拿著房卡去開門 —— 房間可能已經是別人的了。

**什麼時候回傳參考是安全的？** 被參考的東西 **在函式結束後還活著**：

```cpp
// 1. 回傳參數（參數本來就是外面的物件）
const string& longer(const string& a, const string& b) {
    return a.size() >= b.size() ? a : b;      // ✅ a、b 是呼叫者的物件
}
string s1 = "hi", s2 = "hello";
cout << longer(s1, s2) << '\n';               // 輸出：hello

// 2. 回傳成員變數（物件還活著）
class Box {
    vector<int> items_;
public:
    vector<int>& items() { return items_; }   // ✅ items_ 跟著物件一起活著
};

// 3. 回傳 static 或全域變數
int& counter() {
    static int c = 0;                         // ✅ static：活到程式結束
    return c;
}
counter()++;
counter()++;
cout << counter() << '\n';                    // 輸出：2
```

**還是有陷阱**：上面的 `longer`，如果傳入 **暫時的值**：

```cpp
const string& r = longer("abc", "de");        // "abc" 和 "de" 轉成的暫時 string 在這一行結束就銷毀
// cout << r;                                 // ❌ r 懸空了
```

**最安全的做法：不確定的時候，回傳值（`string`）而不是參考（`const string&`）**。

---

# 第三部分：多載與預設參數

## 3.1 函式多載 (Function Overloading)

**是什麼**：**同一個名字**、**參數列不同**（個數或型別不同）的函式，可以同時存在。呼叫時，編譯器依照 **引數的型別** 挑選要呼叫哪一個。

**為什麼需要**：同一個概念（例如「印出」、「面積」、「最大值」）作用在不同型別上，用同一個名字比較自然，不用取 `print_int`、`print_double`、`print_string` 這種名字。

**比喻**：「開」這個字 —— 開門、開車、開會，同一個字，根據後面接的東西決定意思。

```cpp
int    area(int side)          { return side * side; }           // 正方形
int    area(int w, int h)      { return w * h; }                 // 長方形（個數不同）
double area(double r)          { return 3.14159 * r * r; }       // 圓（型別不同）

cout << area(3) << '\n';           // 呼叫 area(int)        → 輸出：9
cout << area(3, 4) << '\n';        // 呼叫 area(int, int)   → 輸出：12
cout << area(2.0) << '\n';         // 呼叫 area(double)     → 輸出：12.5664
```

```cpp
void print(int x)            { cout << "int: " << x << '\n'; }
void print(double x)         { cout << "double: " << x << '\n'; }
void print(const string& s)  { cout << "string: " << s << '\n'; }
void print(const vector<int>& v) { cout << "vector of " << v.size() << '\n'; }

print(42);                         // 輸出：int: 42
print(3.5);                        // 輸出：double: 3.5
print(string("hi"));               // 輸出：string: hi
print(vector<int>{1, 2, 3});       // 輸出：vector of 3
```

**不能只靠回傳型別區分**（簽章不包含回傳型別）：

```cpp
int    parse(const string& s);
// double parse(const string& s);  // ❌ error: ambiguating new declaration（簽章一樣）
```

原因：呼叫 `parse("3")` 時，編譯器只看引數，不知道你想要哪一個回傳型別。

**參數名稱不同也不算**：`void f(int a)` 和 `void f(int b)` 是同一個函式。

## 3.2 🔍 多載解析 (Overload Resolution)

**是什麼**：編譯器挑選函式的規則。它會把每個候選函式的「**轉換成本**」分等級，挑成本最低的：

| 等級 | 名稱 | 包含哪些轉換 |
|---|---|---|
| 1（最好） | **完全符合 (exact match)** | 型別一模一樣；或只加上 `const`；陣列 → 指標 |
| 2 | **提升 (promotion)** | `char`、`short`、`bool` → `int`；`float` → `double` |
| 3 | **標準轉換 (conversion)** | `int` ↔ `double`、`long` → `int`、`int` → `long long`、`double` → `float`、指標 → `bool` …… |
| 4 | 使用者定義的轉換 | 透過建構子或轉換運算子（例如 `const char*` → `string`） |

每個等級的範例（有 `f(int)` 和 `f(double)` 兩個版本）：

```cpp
void f(int x)    { cout << "f(int) "; }
void f(double x) { cout << "f(double) "; }

f(5);          // 等級 1：int 完全符合 f(int)                    → f(int)
f(5.0);        // 等級 1：double 完全符合 f(double)              → f(double)
f('a');        // char → int 是提升（等級 2）；char → double 是轉換（等級 3）→ f(int)
f(true);       // bool → int 是提升                               → f(int)
f(5.0f);       // float → double 是提升；float → int 是轉換      → f(double)
short s = 1;
f(s);          // short → int 是提升                              → f(int)
cout << '\n';
// 輸出：f(int) f(double) f(int) f(int) f(double) f(int)
```

### 模稜兩可 (Ambiguous)

**是什麼**：最好的候選 **不只一個**（同等級），編譯器無法決定 → **編譯錯誤**。

```cpp
f(5L);         // ❌ long → int 是轉換、long → double 也是轉換，同等級
               // error: call of overloaded 'f(long int)' is ambiguous
f(5LL);        // ❌ 同樣的原因
f(5u);         // ❌ unsigned → int、unsigned → double 都是轉換
f(static_cast<int>(5L));   // ✅ 明確轉型解決
```

**另一種模稜兩可：多個參數的取捨**

```cpp
void g(int a, double b)  { cout << "g1\n"; }
void g(double a, int b)  { cout << "g2\n"; }
// g(1, 2);    // ❌ g1 第一個參數比較好、g2 第二個參數比較好 → 沒有一個「全面勝出」
g(1, 2.0);     // ✅ g1 兩個都完全符合 → 輸出：g1
```

### 使用者定義的轉換（等級 4）

```cpp
void h(const string& s) { cout << "string\n"; }
void h(bool b)          { cout << "bool\n"; }
h("hello");    // 😱 輸出：bool
// 原因："hello" 是 const char*，指標 → bool 是「標準轉換」（等級 3），
//       比 const char* → string（使用者定義的轉換，等級 4）更好
h(string("hello"));   // ✅ 輸出：string
```

這是多載最有名的陷阱之一。設計 API 時，避免同時有 `bool` 和 `string` 版本的多載。

## 3.3 預設參數 (Default Argument)

**是什麼**：參數有 **預設值**，呼叫時可以省略，省略的就用預設值。

```cpp
void print_line(const string& text, int times = 1, char end = '\n') {
    for (int i = 0; i < times; i++) cout << text << end;
}
print_line("hi");              // times = 1, end = '\n'   → 輸出：hi
print_line("ab", 3);           // end = '\n'              → 輸出 3 行 ab
print_line("x", 3, ' ');       //                         → 輸出：x x x
cout << '\n';
```

**規則**：

**規則 1：預設值只能放在最右邊**（有預設值的參數，右邊的參數全部都要有預設值）

```cpp
void a1(int x, int y = 0, int z = 0);     // ✅
// void a2(int x = 0, int y, int z = 0);  // ❌ y 沒有預設值，卻在有預設值的 x 右邊
```

原因：呼叫時引數是 **從左到右** 對應的，`a2(5, 6)` 不知道 5 是給 x 還是給 y。

**規則 2：不能跳過中間的參數**

```cpp
// print_line("x", , ' ');     // ❌ 想用預設的 times，但指定 end —— 做不到
print_line("x", 1, ' ');       // ✅ 只能把 times 也寫出來
```

**規則 3：預設值只寫一次，通常寫在宣告裡**

```cpp
// util.h
void connect(const string& host, int port = 80);
// util.cpp
void connect(const string& host, int port) { /* ... */ }      // ✅ 定義不再寫預設值
// void connect(const string& host, int port = 80) { }        // ❌ error: default argument given for parameter 2
```

**規則 4：和多載混用容易模稜兩可**

```cpp
void k(int a) { }
void k(int a, int b = 0) { }
// k(1);       // ❌ 兩個版本都能接受 k(1) → 模稜兩可
k(1, 2);       // ✅ 只有第二個版本可以
```

---

# 第四部分：函式的修飾

## 4.1 inline

**原本的意思**：建議編譯器把函式本體 **直接展開在呼叫的地方**，省掉函式呼叫的成本（跳躍、建立堆疊框架）。

```cpp
inline int square(int x) { return x * x; }
int y = square(5);     // 編譯器可能直接展開成 int y = 5 * 5;
```

**現在的意思**：現代編譯器 **自己會決定** 要不要展開（`-O2` 下，小函式就算沒寫 `inline` 也會被展開；大函式寫了也可能不展開）。所以 `inline` 現在主要的作用是：

**允許同一個函式的定義出現在多個 `.cpp` 檔裡**（寫在標頭檔裡，被很多檔案引入也不會「重複定義」，第 14 課）。

```cpp
// math_util.h
inline int clamp_to_byte(int x) { return x < 0 ? 0 : x > 255 ? 255 : x; }   // ✅ 可以放標頭檔
// int bad(int x) { return x; }   // ❌ 沒有 inline，被兩個 .cpp 引入時連結會出錯
```

**類別裡直接寫本體的成員函式，自動就是 `inline`**。

## 4.2 constexpr 函式

**是什麼**：參數是編譯期常數時，**整個函式在編譯時就算完**；參數不是常數時，就跟一般函式一樣在執行時計算。

```cpp
constexpr long long fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }
constexpr int pow2(int k) { return 1 << k; }

constexpr long long F10 = fact(10);    // 編譯時算好 3628800
int arr[pow2(4)];                      // 陣列大小 16，編譯時算好
static_assert(fact(5) == 120);         // 編譯時檢查

int n;
cin >> n;
cout << fact(n) << '\n';               // n 是執行時才知道的 → 在執行時計算
```

## 4.3 [[nodiscard]]

**是什麼**：標記「**呼叫這個函式卻不使用回傳值，很可能是 bug**」，忽略回傳值時編譯器會警告。

```cpp
[[nodiscard]] bool try_withdraw(long long& balance, long long amt) {
    if (amt > balance) return false;
    balance -= amt;
    return true;
}
long long bal = 100;
try_withdraw(bal, 500);              // ⚠️ warning: ignoring return value（提款失敗了你都不知道）
if (!try_withdraw(bal, 500)) cout << "insufficient\n";   // ✅ 輸出：insufficient
```

**標準函式庫的例子**：C++20 的 `vector::empty()` 是 `[[nodiscard]]`。常見的錯誤是想清空 vector 卻寫成 `v.empty();`（這只是「查詢是否為空」），應該寫 `v.clear()`。

## 4.4 static 函式（檔案內部）

**是什麼**：在 **全域** 函式前面加 `static`，代表「**這個函式只有這個 `.cpp` 檔看得到**」（內部連結，第 14 課）。

```cpp
// a.cpp
static int helper() { return 1; }     // 只有 a.cpp 能用
// b.cpp
static int helper() { return 2; }     // 不會和 a.cpp 的 helper 衝突
```

這和 **類別裡的 `static` 成員函式**（第 07 課）是 **完全不同的意思**。現代 C++ 更推薦用 **匿名命名空間** 達到同樣的效果。

## 4.5 遞迴 (Recursion)

函式可以呼叫自己。DS 路線第 02 課有完整的說明（河內塔、回溯法），這裡只複習三個要素：

```cpp
long long power(long long base, int exp) {
    if (exp == 0) return 1;                        // 1. 終止條件
    long long half = power(base, exp / 2);         // 2. 問題變小（exp 減半）
    return exp % 2 == 0 ? half * half : half * half * base;   // 3. 用小問題組出答案
}
cout << power(2, 10) << ' ' << power(3, 5) << '\n';   // 輸出：1024 243
```

---

# 第五部分：函式也是值

在 C++ 裡，函式可以被 **存在變數裡**、**當成參數傳給別的函式**。這讓我們可以寫出「行為可以替換」的程式，例如讓 `sort` 照我們自訂的規則排序。

## 5.1 函式指標 (Function Pointer)

**是什麼**：存放「**函式位址**」的變數。

**語法**（有點難讀）：`回傳型別 (*變數名稱)(參數型別列表)`

```cpp
int add(int a, int b) { return a + b; }
int mul(int a, int b) { return a * b; }

int (*op)(int, int);         // op 是「指向『接收兩個 int、回傳 int』的函式」的指標
op = add;                    // 函式名稱會自動轉成函式指標
cout << op(3, 4) << '\n';    // 輸出：7
op = mul;
cout << op(3, 4) << '\n';    // 輸出：12
```

**用 `using` 取別名，比較好讀**：

```cpp
using BinaryOp = int (*)(int, int);
BinaryOp ops[] = {add, mul};                 // 函式指標的陣列
for (BinaryOp f : ops) cout << f(5, 6) << ' ';   // 輸出：11 30
cout << '\n';
```

**當成參數傳給別的函式（回呼 callback）**：

```cpp
int apply_all(const vector<int>& v, int init, BinaryOp f) {
    int r = init;
    for (int x : v) r = f(r, x);
    return r;
}
vector<int> nums = {1, 2, 3, 4};
cout << apply_all(nums, 0, add) << ' ' << apply_all(nums, 1, mul) << '\n';   // 輸出：10 24
```

**比喻**：把「做事的方法」寫在紙條上交給別人，讓他照著做。`apply_all` 負責「走過每個元素」，至於「怎麼合併」由你交給它的函式決定。

**傳給 STL**：

```cpp
bool descending(int a, int b) { return a > b; }
vector<int> v = {3, 1, 4, 1, 5};
sort(v.begin(), v.end(), descending);
for (int x : v) cout << x;                   // 輸出：54311
cout << '\n';
```

## 5.2 Lambda 運算式

**是什麼**：**就地定義的匿名函式**。不用另外取名字、不用寫在別的地方，直接寫在要用的位置。

**完整語法**：

```
[捕獲](參數列) -> 回傳型別 { 本體 }
```

回傳型別通常可以省略（編譯器會從 `return` 推導）。

**各種寫法的範例**：

```cpp
// 1. 最簡單：存在變數裡，像函式一樣呼叫
auto square = [](int x) { return x * x; };
cout << square(5) << '\n';                          // 輸出：25

// 2. 沒有參數
auto hello = []() { cout << "hello\n"; };
hello();                                            // 輸出：hello

// 3. 明確寫出回傳型別（兩個 return 型別不同時需要）
auto safe_div = [](int a, int b) -> double {
    if (b == 0) return 0;                           // 0 是 int，沒寫 -> double 會編譯錯誤
    return (double)a / b;
};
cout << safe_div(7, 2) << '\n';                     // 輸出：3.5

// 4. 定義完立刻呼叫
int result = [](int a, int b) { return a + b; }(10, 20);
cout << result << '\n';                             // 輸出：30

// 5. 泛型 lambda（C++14）：參數寫 auto，可以接受任何型別
auto add_any = [](auto a, auto b) { return a + b; };
cout << add_any(1, 2) << ' ' << add_any(1.5, 2.25) << ' ' << add_any(string("ab"), string("cd")) << '\n';
// 輸出：3 3.75 abcd
```

**最常見的用途：傳給 STL 演算法**

```cpp
vector<int> v = {5, 2, 8, 1, 9, 3};

sort(v.begin(), v.end(), [](int a, int b) { return a > b; });      // 由大到小
// v = {9, 8, 5, 3, 2, 1}

int evens = count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; });
cout << evens << '\n';                              // 輸出：2（8 和 2）

auto it = find_if(v.begin(), v.end(), [](int x) { return x < 4; });
cout << *it << '\n';                                // 輸出：3（第一個 < 4 的）

for_each(v.begin(), v.end(), [](int& x) { x *= 10; });
cout << v[0] << '\n';                               // 輸出：90
```

## 5.3 捕獲 (Capture)

**是什麼**：lambda 預設 **看不到外面的區域變數**。要在 `[ ]` 裡寫出來，才能在 lambda 裡使用。這叫「捕獲」。

```cpp
int threshold = 5;
// auto big = [](int x) { return x > threshold; };   // ❌ error: 'threshold' is not captured
auto big = [threshold](int x) { return x > threshold; };   // ✅
cout << big(7) << '\n';                              // 輸出：1
```

**比喻**：
- **值捕獲 `[x]`**：出門前 **拍一張照片** 帶著走。之後外面的 `x` 怎麼變，照片都不會變。
- **參考捕獲 `[&x]`**：帶著一支 **即時監視器**，看到的永遠是現在的 `x`；也能透過它修改 `x`。

**每一種捕獲寫法的範例**：

| 寫法 | 意思 |
|---|---|
| `[]` | 不捕獲任何東西 |
| `[x]` | 複製一份 `x`（值捕獲） |
| `[&x]` | 參考 `x`（參考捕獲） |
| `[x, &y]` | `x` 值捕獲、`y` 參考捕獲 |
| `[=]` | 用到的外部變數 **全部** 值捕獲 |
| `[&]` | 用到的外部變數 **全部** 參考捕獲 |
| `[=, &y]` | 預設值捕獲，但 `y` 用參考 |
| `[&, x]` | 預設參考捕獲，但 `x` 用值 |
| `[this]` | 捕獲目前物件的指標（在成員函式裡） |
| `[v = expr]` | C++14 初始化捕獲：建立一個新的變數 `v` |

```cpp
int a = 1, b = 2, c = 3;

auto f1 = [a]() { return a; };                 // 值捕獲 a
auto f2 = [&a]() { return a; };                // 參考捕獲 a
auto f3 = [a, &b]() { b += a; };               // a 值捕獲、b 參考捕獲（可以修改 b）
auto f4 = [=]() { return a + b + c; };         // 全部值捕獲
auto f5 = [&]() { c = a + b; };                // 全部參考捕獲（可以修改 c）
auto f6 = [=, &c]() { c = a * 100; };          // 預設值捕獲，c 用參考
auto f7 = [s = string("x") + "y"]() { return s; };   // 初始化捕獲：s 是新建立的

a = 10;                                         // 改變 a 之後才呼叫
cout << f1() << ' ' << f2() << '\n';            // 輸出：1 10（f1 拍照時 a 是 1；f2 看到現在的 10）
f3(); cout << b << '\n';                        // 輸出：3（b += 1，f3 捕獲的 a 是當時的 1）
cout << f4() << '\n';                           // 輸出：6（建立時 a=1, b=2, c=3）
f5(); cout << c << '\n';                        // 輸出：13（現在 a=10, b=3）
f6(); cout << c << '\n';                        // 輸出：100（f6 的 a 是建立時的 1）
cout << f7() << '\n';                           // 輸出：xy
```

**重點：值捕獲是在「建立 lambda 的那一刻」拍照**，不是呼叫的時候。

**`[this]`：在成員函式裡使用成員變數**

```cpp
class Counter {
    int count_ = 0;
public:
    void add_all(const vector<int>& v) {
        for_each(v.begin(), v.end(), [this](int x) { count_ += x; });   // 透過 this 存取成員
    }
    int count() const { return count_; }
};
Counter cnt;
cnt.add_all({1, 2, 3});
cout << cnt.count() << '\n';                    // 輸出：6
```

### mutable：修改值捕獲的複製品

值捕獲的變數預設是 **唯讀** 的。要修改那份複製品，lambda 要加 `mutable`：

```cpp
int n = 0;
// auto bad = [n]() { n++; };                   // ❌ error: increment of read-only variable 'n'
auto counter = [n]() mutable { return ++n; };   // ✅ 修改的是自己的複製品
cout << counter() << counter() << counter() << '\n';   // 輸出：123（複製品在呼叫之間會保留）
cout << n << '\n';                              // 輸出：0（外面的 n 完全沒變）
```

### 懸空捕獲

**問題**：參考捕獲的 lambda **活得比被捕獲的變數還久** → 參考指向已經銷毀的變數。

```cpp
function<int()> make_counter_bad() {
    int count = 0;
    return [&count]() { return ++count; };      // ❌ count 在函式結束時就銷毀了
}
function<int()> make_counter_ok() {
    int count = 0;
    return [count]() mutable { return ++count; };   // ✅ 值捕獲：lambda 自己有一份
}
auto c = make_counter_ok();
cout << c() << c() << c() << '\n';              // 輸出：123
```

**規則**：lambda 如果會 **被存起來、回傳、或交給別的執行緒**，用值捕獲；只在當下馬上用完（傳給 `sort`、`for_each`），參考捕獲沒問題。

## 5.4 std::function

**是什麼**：一個能裝 **任何「可以被呼叫的東西」** 的容器 —— 一般函式、函式指標、lambda（包括有捕獲的）、函式物件 —— 只要 **參數和回傳型別符合**。

**為什麼需要**：每個 lambda 都有自己獨一無二的型別，沒辦法直接放進同一個 `vector` 或 `map`。`std::function` 把它們統一成同一個型別。

```cpp
#include <functional>
int add(int a, int b) { return a + b; }

function<int(int, int)> op;          // 「接收兩個 int、回傳 int」的任何東西
op = add;                            // 一般函式
cout << op(2, 3) << ' ';             // 輸出：5
op = [](int a, int b) { return a * b; };   // lambda
cout << op(2, 3) << ' ';             // 輸出：6
int base = 100;
op = [base](int a, int b) { return base + a - b; };   // 有捕獲的 lambda
cout << op(2, 3) << '\n';            // 輸出：99
```

**應用：用 map 做「指令 → 動作」的對照表**

```cpp
map<string, function<double(double, double)>> calc = {
    {"add", [](double a, double b) { return a + b; }},
    {"sub", [](double a, double b) { return a - b; }},
    {"pow", [](double a, double b) { return pow(a, b); }},
};
cout << calc["add"](2, 3) << ' ' << calc["pow"](2, 10) << '\n';   // 輸出：5 1024
```

**空的 function**：

```cpp
function<void()> empty_fn;
if (!empty_fn) cout << "empty\n";    // 輸出：empty
// empty_fn();                       // ❌ 丟出 std::bad_function_call
```

**代價**：比直接呼叫 lambda 稍慢（多一層間接呼叫，而且可能要配置記憶體）。傳給 `sort` 這類模板函式時，**直接傳 lambda 就好**，不用包成 `function`。

## 5.5 比較函式的規則：嚴格弱序 (Strict Weak Ordering)

`sort`、`set`、`map`、`priority_queue` 的比較函式 `comp(a, b)` 代表「**a 要排在 b 前面**」，必須滿足：

| 規則 | 意思 | 違反的例子 |
|---|---|---|
| **反自反** | `comp(a, a)` 一定是 `false` | `a <= a` 是 `true` ❌ |
| **反對稱** | `comp(a, b)` 是 `true` 時，`comp(b, a)` 一定是 `false` | |
| **遞移** | `comp(a, b)` 且 `comp(b, c)` → `comp(a, c)` | |
| **等價的遞移** | a 和 b 等價、b 和 c 等價 → a 和 c 等價 | 用 `abs(a - b) < 0.5` 判斷「相等」 |

**錯誤的比較函式**：

```cpp
vector<int> v(100, 7);                                     // 100 個相同的值
// sort(v.begin(), v.end(), [](int a, int b) { return a <= b; });   // ❌ 違反反自反
```

用 `<=` 或 `>=` 的後果：`std::sort` 可能 **讀到陣列外面**、程式當掉，或排出錯的結果（未定義行為）。資料裡有很多相同的值時特別容易發生，`C04` 的 `corner_all_identical_200000` 就是在測這個。

**正確的寫法：用 `<` 或 `>`**

```cpp
sort(v.begin(), v.end(), [](int a, int b) { return a > b; });      // ✅ 由大到小
```

**多條件比較的標準寫法**（`C04`）：

```cpp
struct Student { string name; int score; int age; };
vector<Student> st = {{"amy", 90, 20}, {"bob", 95, 22}, {"cat", 90, 19}, {"dan", 90, 19}};

// 寫法 1：一個條件一個條件比，相同才看下一個
sort(st.begin(), st.end(), [](const Student& a, const Student& b) {
    if (a.score != b.score) return a.score > b.score;     // 1. 分數高的在前
    if (a.age != b.age) return a.age < b.age;             // 2. 年齡小的在前
    return a.name < b.name;                               // 3. 名字字典序
});
for (auto& s : st) cout << s.name << ' ';                 // 輸出：bob cat dan amy
cout << '\n';

// 寫法 2：用 tie 一次比較（依序比較每個欄位）
sort(st.begin(), st.end(), [](const Student& a, const Student& b) {
    return tie(b.score, a.age, a.name) < tie(a.score, b.age, b.name);
    //         ↑ 分數由大到小：把 a、b 對調
});
```

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 函式 | Function | 有名字、可重複使用的程式碼 | 1.1 |
| 參數 / 引數 | Parameter / Argument | 定義裡的名字 / 呼叫時給的值 | 1.2 |
| 呼叫堆疊 | Call Stack | 存放每次呼叫的參數與區域變數 | 1.3 |
| 原型 | Prototype | 函式的宣告 | 1.4 |
| 簽章 | Signature | 名稱 + 參數型別，不含回傳型別 | 1.4 |
| 傳值 / 傳參考 | Pass by Value / Reference | 給複製品 / 給本人 | 2.1、2.2 |
| 複製省略 | Copy Elision / RVO | 回傳物件時直接建在目的地 | 2.6 |
| 懸空參考 | Dangling Reference | 參考到已經銷毀的物件 | 2.7 |
| 函式多載 | Function Overloading | 同名、參數不同 | 3.1 |
| 多載解析 | Overload Resolution | 編譯器挑選函式的規則 | 3.2 |
| 提升 / 轉換 | Promotion / Conversion | 小型別變大 / 型別互轉 | 3.2 |
| 模稜兩可 | Ambiguous | 有兩個一樣好的候選，編譯錯誤 | 3.2 |
| 預設參數 | Default Argument | 沒給的參數用預設值 | 3.3 |
| 內聯 | inline | 允許定義出現在多個檔案 | 4.1 |
| 函式指標 | Function Pointer | 存放函式位址的變數 | 5.1 |
| 回呼 | Callback | 當成參數傳給別人呼叫的函式 | 5.1 |
| Lambda | Lambda Expression | 就地定義的匿名函式 | 5.2 |
| 泛型 lambda | Generic Lambda | 參數寫 auto 的 lambda | 5.2 |
| 捕獲 | Capture | lambda 取用外部變數的方式 | 5.3 |
| mutable | mutable | 允許修改值捕獲的複製品 | 5.3 |
| 可呼叫物件包裝 | std::function | 能裝任何可呼叫的東西 | 5.4 |
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

### 題 9：哪幾行會編譯錯誤？

```cpp
void p(int a, int b = 2, int c = 3);
p(1);          // ①
p(1, 5);       // ②
p();           // ③
p(1, , 4);     // ④
```

### 題 10：預測輸出

```cpp
void h(const string& s) { cout << "string"; }
void h(bool b) { cout << "bool"; }
h("text");
```

---

# 習題解答

**題 1**：`121`。`a` 是傳值（外面的 x 不變）；`b` 是參考（y 變成 2）；`c` 是 const 參考（不能改，也沒改）。

**題 2**：
- a) `g(int)`：完全符合。
- b) `g(double)`：`float → double` 是提升。
- c) `g(int)`：`char → int` 是提升。
- d) **模稜兩可**：`long long → int` 和 `long long → double` 都是轉換。
- e) `g(const string&)`：`"hi"` 透過 `string` 的建構子轉換（使用者定義的轉換）。這裡沒有 `bool` 版本，所以不會發生題 10 的問題。

**題 3**：`result` 是 **區域變數**，函式結束時就銷毀了，回傳它的參考是 **懸空參考**。改法：回傳值 `string longer(...)`，或直接回傳參數 `return a.size() > b.size() ? a : b;`（參數本來就是外面的物件）。

**題 4**：`10 50`。`a` 在建立時複製了 `n = 1`；`b` 參考 `n`，呼叫時 `n` 已經是 5。

**題 5**：參數是 **傳值**，交換的是複製品。改成 `void my_swap(int& a, int& b)`。（或直接用 `std::swap`。）

**題 6**：用了 `<=`，違反 **嚴格弱序**（`comp(p, p)` 是 `true`）。`x` 相同的點很多時，`std::sort` 可能當掉或排錯。改成 `p.x < q.x`。

**題 7**：`3 0`。`mutable` 讓 lambda 可以修改 **自己那份複製品**，複製品在呼叫之間會保留（1 → 2 → 3）；外面的 `counter` 完全沒被改到。

**題 8**：
- a) `const vector<double>&`：大型物件、只讀。
- b) `string&`：要修改呼叫者的字串。
- c) `int`：小型別、只讀，傳值最簡單也最快。
- d) 回傳 `Node*`（找不到回傳 `nullptr`），或 `std::optional`。

**題 9**：③ 和 ④。③ 第一個參數沒有預設值，一定要給；④ 不能跳過中間的參數。

**題 10**：印出 `bool`。`"text"` 的型別是 `const char*`，指標轉 `bool` 是標準轉換（等級 3），比轉成 `string`（使用者定義的轉換，等級 4）優先。

---

# 程式練習

- **`C04 多條件排序`**：用 lambda 寫多條件比較函式；測資有大量完全相同的資料，用 `<=` 寫的比較函式會出問題。
