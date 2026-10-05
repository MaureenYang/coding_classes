# 10. 模板與泛型程式設計 (Templates & Generic Programming)

> 程式練習：`C10 泛型堆疊`
>
> 先備知識：第 04 課「函式多載」、第 07 課「類別」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 為什麼需要模板 | 重複程式碼的問題、泛型程式設計 |
| 第二部分 | 函式模板 | 型別推導的規則、推導失敗、明確指定、模板與多載 |
| 第三部分 | 類別模板 | 寫法、成員函式定義、只實例化用到的成員、預設引數、CTAD、別名模板 |
| 第四部分 | 非型別參數與特化 | `template <int N>`、完全特化、部分特化 |
| 第五部分 | 模板怎麼被編譯 | 實例化、為什麼要寫在標頭檔、`typename` 關鍵字 |
| 第六部分 | 約束與變長模板 | `static_assert`、type traits、`if constexpr`、C++20 concepts、參數包、完美轉發 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：為什麼需要模板

## 1.1 問題：同樣的邏輯，不同的型別

```cpp
int    max_int(int a, int b)          { return a < b ? b : a; }
double max_double(double a, double b) { return a < b ? b : a; }
string max_string(const string& a, const string& b) { return a < b ? b : a; }
// 每多一種型別就要再寫一次……
```

邏輯一模一樣，只有型別不同。用多載（第 04 課）可以讓名字相同，但 **還是要寫好幾份**，而且：
- 發現 bug 時，每一份都要改。
- 別人寫了一個新型別（例如 `Fraction`），你的函式不能用，除非再寫一份。

**其他「不好的」解法**：
- 用 `#define MAX(a, b) ((a) < (b) ? (b) : (a))`：巨集沒有型別檢查，`MAX(i++, j)` 會讓 `i` 加兩次（第 14 課）。
- 用 `void*`（C 語言的 `qsort` 就是這樣）：失去型別安全，要自己轉型，很容易出錯。

## 1.2 泛型程式設計 (Generic Programming)

**是什麼**：寫一份 **跟型別無關** 的程式碼，讓它可以用在 **很多種型別** 上。C++ 用 **模板 (template)** 來做到。

**比喻**：**餅乾模具**。同一個星星形狀的模具，可以壓出巧克力口味、抹茶口味、原味的餅乾 —— 模具（模板）只有一個，口味（型別）由你決定。

```cpp
template <class T>
T my_max(T a, T b) { return a < b ? b : a; }

cout << my_max(3, 5) << '\n';                        // T = int    → 輸出：5
cout << my_max(2.5, 1.5) << '\n';                    // T = double → 輸出：2.5
cout << my_max(string("apple"), string("pie")) << '\n';   // T = string → 輸出：pie（字典序比較）
cout << my_max('a', 'z') << '\n';                    // T = char   → 輸出：z
```

一份程式碼，四種型別都能用，而且每一種都有完整的型別檢查。

STL 整個就是建立在模板上：`vector<T>`、`map<K, V>`、`sort`、`find`、`max`……

---

# 第二部分：函式模板 (Function Template)

## 2.1 語法

```cpp
template <class T>              // 或 template <typename T>，兩者在這裡完全相同
void swap_values(T& a, T& b) {
    T tmp = a;                  // T 可以像一般型別一樣使用
    a = b;
    b = tmp;
}

int x = 1, y = 2;
swap_values(x, y);
cout << x << ' ' << y << '\n';            // 輸出：2 1
string s = "hi", t = "yo";
swap_values(s, t);
cout << s << ' ' << t << '\n';            // 輸出：yo hi
```

- `template <class T>`：宣告「接下來的函式是一個模板，`T` 是一個型別參數」。
- `T` 叫做 **模板參數 (template parameter)**，是一個「型別的佔位符」。名字可以隨便取，習慣用 `T`、`U`，或有意義的名字如 `Key`、`Value`。
- 可以有好幾個參數：`template <class K, class V>`。

**`class` 和 `typename` 的差別**：在 `template <...>` 裡完全相同。`class` 比較短；`typename` 意思比較清楚（`T` 不一定是類別，`int` 也可以）。只有 5.3 節的「依賴名稱」一定要用 `typename`。

## 2.2 模板引數推導 (Template Argument Deduction)

**是什麼**：呼叫時，編譯器 **根據引數的型別自動推導出 `T`**，不用自己寫。

```cpp
my_max(3, 5);              // 引數都是 int → T = int
my_max<double>(3, 5);      // 明確指定 T = double（3、5 會被轉成 double）
```

### 推導的規則：傳值會去掉 const 和參考

```cpp
template <class T> void by_value(T x)      { cout << is_const_v<T> << ' '; }
template <class T> void by_ref(T& x)       { cout << is_const_v<T> << ' '; }

const int c = 5;
by_value(c);              // T = int（傳值 = 複製一份，複製品不需要是 const）
by_ref(c);                // T = const int（參考綁定原本的 const 物件，const 必須保留）
cout << '\n';             // 輸出：0 1
```

| 參數寫法 | 引數 `const int c` | 推導出的 `T` | 原因 |
|---|---|---|---|
| `T x`（傳值） | `c` | `int` | 複製品可以修改，所以去掉 `const` |
| `T& x` | `c` | `const int` | 參考到原本的物件，`const` 不能去掉 |
| `const T& x` | `c` | `int` | `const` 已經寫在參數裡了 |

**陣列傳值會退化成指標**（第 05 課）：

```cpp
template <class T> void show_type(T x) { cout << is_pointer_v<T> << '\n'; }
int arr[3] = {1, 2, 3};
show_type(arr);           // T = int*（陣列退化成指標）→ 輸出：1
show_type("hello");       // T = const char* → 輸出：1
```

### 推導失敗 1：兩個引數推導出不同的型別

```cpp
// my_max(3, 2.5);        // ❌ error: no matching function for call to 'my_max(int, double)'
                          //    note: deduced conflicting types for parameter 'T' ('int' and 'double')
cout << my_max<double>(3, 2.5) << '\n';   // ✅ 明確指定 → 輸出：3
cout << my_max(3.0, 2.5) << '\n';         // ✅ 都是 double → 輸出：3
```

**模板推導時不做隱式轉換**：一般函式 `double f(double, double)` 會自動把 `3` 轉成 `3.0`；但模板推導要 **先決定 `T` 是什麼**，兩個引數給出矛盾的答案，編譯器不會幫你挑一個。

**解法：用兩個型別參數**

```cpp
template <class A, class B>
auto my_max2(A a, B b) { return a < b ? b : a; }   // auto：回傳型別自動推導（C++14）
auto r = my_max2(3, 2.5);
cout << r << ' ' << is_same_v<decltype(r), double> << '\n';   // 輸出：3 1（回傳 double）
```

`a < b ? b : a` 的型別是 `int` 和 `double` 的 **共同型別** `double`（第 02 課的算術轉換）。

### 推導失敗 2：型別只出現在回傳值

```cpp
template <class To, class From>
To convert(From x) { return static_cast<To>(x); }

// convert(3.7);                  // ❌ error: no matching function for call to 'convert(double)'
                                  //    note: couldn't deduce template parameter 'To'
cout << convert<int>(3.7) << '\n';       // ✅ To 明確指定、From 自動推導 → 輸出：3
```

編譯器 **只看引數** 推導，不看回傳值要給誰。所以「只出現在回傳型別」的參數一定要明確寫出來。把它放在 **第一個**，就可以只寫它、其他的讓編譯器推導（`static_cast<int>(x)`、`make_unique<T>(...)` 都是這樣設計的）。

## 2.3 隱含的要求

**是什麼**：模板對型別有「**隱含的要求**」—— 函式本體用到什麼操作，`T` 就必須支援。

```cpp
struct Point { int x, y; };          // 沒有定義 operator<
// my_max(Point{1, 2}, Point{3, 4});
// ❌ error: no match for 'operator<' (operand types are 'Point' and 'Point')
//    錯誤指向模板「內部」的 return a < b ? b : a; 那一行
```

`my_max` 的隱含要求：
1. `T` 能用 `<` 比較。
2. `T` 能複製（傳值參數、回傳值）。

只要滿足，任何型別都能用 —— 包括你自己寫的類別：

```cpp
struct Version {
    int major, minor;
    bool operator<(const Version& o) const { return major != o.major ? major < o.major : minor < o.minor; }
};
Version v = my_max(Version{1, 9}, Version{2, 0});
cout << v.major << '.' << v.minor << '\n';   // 輸出：2.0
```

這叫 **鴨子型別 (duck typing)**：「走起路來像鴨子、叫起來像鴨子，就是鴨子」—— 只要型別支援需要的操作，就能用（第 09 課 2.4）。

> 錯誤訊息常常很長很難讀，因為錯誤發生在模板 **內部**，而且會列出整個實例化的過程（`required from here`）。**讀模板錯誤的技巧**：找第一個 `error:` 看是什麼操作不支援，再找 `required from` 看是你哪一行呼叫造成的。C++20 的 concepts（6.4 節）就是為了解決這個問題。

## 2.4 模板與多載

函式模板也可以 **多載**：可以和其他模板、一般函式同名。編譯器挑選的規則：

1. 先找出所有 **可行** 的候選（一般函式 + 推導成功的模板）。
2. 比較每個候選需要的 **轉換**，選轉換最少的。
3. 一樣好的時候：**一般函式優先於模板**；**比較特定的模板優先於比較通用的模板**。

```cpp
template <class T> void print(const T& x) { cout << x; }
template <class A, class B> void print(const pair<A, B>& p) {     // 比較特定的版本
    cout << '(' << p.first << ',' << p.second << ')';
}
void print(bool b) { cout << (b ? "true" : "false"); }            // 一般函式

print(42);              cout << '\n';   // 第一個模板，T = int        → 輸出：42
print(make_pair(1, 2)); cout << '\n';   // pair 版本更特定              → 輸出：(1,2)
print(true);            cout << '\n';   // 一般函式（一樣好時優先）      → 輸出：true
print(string("s"));     cout << '\n';   // 第一個模板，T = string     → 輸出：s
```

**為什麼 `pair` 版本「比較特定」？** 第一個模板接受「任何 `T`」，第二個只接受「`pair<A, B>`」。能用第二個的一定能用第一個，反過來不行 —— 所以第二個比較特定。

`C10` 題就是用這個方法，讓 `pair` 有不同的輸出格式。

### 🔍 遞迴：讓 print 支援 vector

```cpp
template <class T> void show(const T& x) { cout << x; }
template <class T> void show(const vector<T>& v) {
    cout << '[';
    for (size_t i = 0; i < v.size(); i++) {
        if (i) cout << ", ";
        show(v[i]);                      // 元素可能也是 vector → 遞迴呼叫最適合的版本
    }
    cout << ']';
}
show(vector<vector<int>>{{1, 2}, {3}});
cout << '\n';                            // 輸出：[[1, 2], [3]]
```

---

# 第三部分：類別模板 (Class Template)

## 3.1 語法

```cpp
template <class T>
class Stack {
    vector<T> data_;
public:
    void push(const T& x) { data_.push_back(x); }
    void pop() { data_.pop_back(); }
    const T& top() const { return data_.back(); }
    bool empty() const { return data_.empty(); }
    size_t size() const { return data_.size(); }
};

Stack<int> si;                           // 類別模板要寫出型別參數
si.push(1); si.push(2);
cout << si.top() << ' ' << si.size() << '\n';   // 輸出：2 2

Stack<string> ss;
ss.push("hello");
cout << ss.top() << '\n';                // 輸出：hello

Stack<pair<int, string>> sp;
sp.push({7, "seven"});
cout << sp.top().second << '\n';         // 輸出：seven
```

`Stack` 本身 **不是一個型別**，是「產生型別的模具」；`Stack<int>`、`Stack<string>` 才是型別，而且 **是兩個完全不同、互不相關的型別**：

```cpp
cout << is_same_v<Stack<int>, Stack<long>> << '\n';   // 輸出：0
// Stack<long> b = si;                   // ❌ error: conversion from 'Stack<int>' to non-scalar type 'Stack<long int>' requested
```

在類別模板 **裡面**，可以直接寫 `Stack` 代表「目前這個 `Stack<T>`」：

```cpp
template <class T>
class Box {
    T v_;
public:
    Box(T v) : v_(v) {}
    Box bigger(const Box& o) const { return o.v_ < v_ ? *this : o; }   // Box 就是 Box<T>
    T get() const { return v_; }
};
cout << Box<int>(3).bigger(Box<int>(8)).get() << '\n';   // 輸出：8
```

## 3.2 在類別外定義成員函式

```cpp
template <class T>
class Queue2 {
    deque<T> d_;
public:
    void push(const T& x);
    T pop();
};

template <class T>                        // 每個成員函式前面都要重寫一次 template <class T>
void Queue2<T>::push(const T& x) {        // 類別名稱要寫 Queue2<T>，不是 Queue2
    d_.push_back(x);
}

template <class T>
T Queue2<T>::pop() {
    T front = d_.front();
    d_.pop_front();
    return front;
}

Queue2<int> q;
q.push(1); q.push(2);
cout << q.pop() << q.pop() << '\n';       // 輸出：12
```

**常見錯誤**：
- 忘了寫 `template <class T>` → `error: 'T' was not declared in this scope`。
- 寫成 `void Queue2::push(...)` → `error: 'template<class T> class Queue2' used without template arguments`。

## 3.3 只有用到的成員函式才會被實例化

**是什麼**：類別模板的成員函式，**只有在被呼叫時才會被產生**。所以一個型別就算不支援某個成員函式需要的操作，只要你不呼叫那個函式，就不會出錯。

```cpp
template <class T>
class Bag {
    vector<T> v_;
public:
    void add(const T& x) { v_.push_back(x); }
    size_t size() const { return v_.size(); }
    void sort_items() { sort(v_.begin(), v_.end()); }   // 需要 T 支援 <
};

struct NoLess { int x; };                // 不能比較大小
Bag<NoLess> b;
b.add({1}); b.add({2});
cout << b.size() << '\n';                // ✅ 輸出：2（沒呼叫 sort_items，所以沒問題）
// b.sort_items();                       // ❌ 這時才會編譯錯誤：no match for 'operator<'
```

`std::map<K, V>` 也是這樣：`V` 沒有預設建構子時，`map` 還是能用，只是不能呼叫 `operator[]`（它需要預設建構一個新值）。

## 3.4 每個實例化有自己的 static 成員

```cpp
template <class T>
struct Counter {
    inline static int created = 0;
    Counter() { created++; }
};
Counter<int> a, b, c;
Counter<double> d;
cout << Counter<int>::created << ' ' << Counter<double>::created << '\n';   // 輸出：3 1
```

`Counter<int>` 和 `Counter<double>` 是不同的類別，各自有一份 `created`。

## 3.5 預設模板引數

```cpp
template <class T, class Container = vector<T>>
class Stack2 {
    Container c_;
public:
    void push(const T& x) { c_.push_back(x); }
    const T& top() const { return c_.back(); }
};

Stack2<int> a;                  // Container 用預設的 vector<int>
Stack2<int, deque<int>> b;      // 指定用 deque<int>
a.push(1); b.push(2);
cout << a.top() << b.top() << '\n';    // 輸出：12
```

`std::stack`、`std::priority_queue`、`std::map`（比較函式）、`std::unordered_map`（雜湊函式）都是這樣設計的：

```cpp
priority_queue<int, vector<int>, greater<int>> min_heap;   // 第三個參數換成 greater → 最小堆積
for (int x : {5, 1, 3}) min_heap.push(x);
cout << min_heap.top() << '\n';         // 輸出：1
```

## 3.6 類別模板引數推導 (CTAD, C++17)

**是什麼**：C++17 起，建立物件時可以 **省略類別模板的參數**，由建構子的引數推導。

```cpp
pair p(1, 2.5);              // C++17：自動推導成 pair<int, double>
vector v{1, 2, 3};           // vector<int>
Box bx(3.5);                 // Box<double>（3.1 的 Box）
cout << is_same_v<decltype(p), pair<int, double>> << is_same_v<decltype(v), vector<int>> << '\n';   // 輸出：11
```

**常見陷阱**：

```cpp
vector v2{5, 1};             // vector<int>，內容是 {5, 1}（兩個元素）
vector v3(5, 1);             // vector<int>，內容是 5 個 1
auto s = vector{"a", "b"};   // ⚠️ vector<const char*>，不是 vector<string>！
```

## 3.7 別名模板 (Alias Template)

**是什麼**：用 `using` 為模板取一個比較短的別名，而且別名本身也可以有模板參數。

```cpp
template <class T>
using Matrix = vector<vector<T>>;              // Matrix<T> 就是 vector<vector<T>>

template <class V>
using StrMap = map<string, V>;                 // 只固定 key 的型別

Matrix<int> m(2, vector<int>(3, 0));
m[1][2] = 7;
StrMap<double> price{{"apple", 1.5}};
cout << m[1][2] << ' ' << price["apple"] << '\n';   // 輸出：7 1.5
```

---

# 第四部分：非型別參數與特化

## 4.1 非型別模板參數 (Non-type Template Parameter)

**是什麼**：模板參數不一定是型別，也可以是 **編譯期常數**（整數、`bool`、`char`、指標、`enum`；C++20 起還有更多）。

```cpp
template <class T, size_t N>
class FixedArray {
    T data_[N];                    // N 在編譯時就知道，可以當陣列大小
public:
    constexpr size_t size() const { return N; }
    T& operator[](size_t i) { return data_[i]; }
};

FixedArray<int, 10> a;
a[9] = 42;
cout << a.size() << ' ' << a[9] << ' ' << sizeof(a) << '\n';   // 輸出：10 42 40
cout << is_same_v<FixedArray<int, 10>, FixedArray<int, 20>> << '\n';   // 輸出：0（N 不同就是不同型別）
```

`sizeof(a)` 是 40 = 10 個 `int`：資料直接放在物件裡，**沒有任何動態配置**。

**標準函式庫的例子**：

```cpp
array<int, 5> arr = {1, 2, 3, 4, 5};      // std::array：固定大小的陣列
bitset<8> bits(0b10110);                  // bitset：固定位元數
cout << arr.size() << ' ' << bits << ' ' << bits.count() << '\n';   // 輸出：5 00010110 3
```

**非型別參數必須是編譯期常數**：

```cpp
int n = 5;
// FixedArray<int, n> bad;               // ❌ error: the value of 'n' is not usable in a constant expression
constexpr int M = 5;
FixedArray<int, M> ok;                   // ✅ constexpr 是編譯期常數（第 15 課）
```

### 用非型別參數推導陣列大小

```cpp
template <class T, size_t N>
constexpr size_t array_length(T (&)[N]) { return N; }    // 參數是「N 個 T 的陣列的參考」

int arr2[7];
double d[3];
cout << array_length(arr2) << ' ' << array_length(d) << '\n';   // 輸出：7 3
```

因為參數是 **參考**，陣列不會退化成指標，編譯器可以推導出 `N`。`std::size(arr)` 就是這樣實作的。

## 4.2 完全特化 (Full Specialization)

**是什麼**：為 **某個特定的型別**，提供一個 **完全不同的實作**。寫法是 `template <>`（空的角括號）加上指定的型別。

**比喻**：餅乾工廠大部分口味都用同一條生產線，但「無麩質」口味有專屬的生產線。

### 類別模板的完全特化

```cpp
template <class T>
struct TypeName { static string get() { return "unknown"; } };   // 通用版本（主模板 primary template）

template <>                                        // 空的角括號：完全特化
struct TypeName<int> { static string get() { return "int"; } };

template <>
struct TypeName<double> { static string get() { return "double"; } };

cout << TypeName<int>::get() << ' '
     << TypeName<double>::get() << ' '
     << TypeName<char>::get() << '\n';             // 輸出：int double unknown
```

**特化版本可以有完全不同的成員**：

```cpp
template <class T>
struct Storage { T value; string kind() const { return "一般"; } };

template <>
struct Storage<bool> {                             // bool 的特化：多了一個 flip()
    bool value;
    string kind() const { return "布林"; }
    void flip() { value = !value; }
};
Storage<int> si{5};
Storage<bool> sb{true};
sb.flip();
cout << si.kind() << ' ' << sb.kind() << ' ' << sb.value << '\n';   // 輸出：一般 布林 0
// si.flip();                                      // ❌ 一般版本沒有 flip
```

**STL 的例子**：`vector<bool>` 是特化版本，每個 `bool` 只用 1 bit 存（省 8 倍空間），但也因此行為怪異：

```cpp
vector<bool> vb = {true, false};
// bool& r = vb[0];                                // ❌ 不能取得 bool&：元素不是獨立的 bool 物件
auto r = vb[0];                                    // r 是一個「代理物件」，不是 bool
r = false;                                         // 透過代理修改了 vb[0]！
cout << vb[0] << '\n';                             // 輸出：0
```

### 函式模板的完全特化

函式模板也可以完全特化，但 **通常用多載比較好**（特化不參與多載選擇，規則容易混淆）：

```cpp
template <class T> string describe(T)        { return "something"; }
template <>        string describe<int>(int) { return "an int"; }   // 完全特化
string describe(double)                      { return "a double"; } // 一般函式多載（比較推薦）

cout << describe('x') << ", " << describe(1) << ", " << describe(1.5) << '\n';
// 輸出：something, an int, a double
```

## 4.3 部分特化 (Partial Specialization)

**是什麼**：為「**某一類**」型別提供特別的實作（只固定一部分、或固定型別的「形狀」）。**只有類別模板可以部分特化**，函式模板不行（用多載代替）。

### 例 1：所有指標型別

```cpp
template <class T>
struct IsPointer { static constexpr bool value = false; };

template <class T>
struct IsPointer<T*> { static constexpr bool value = true; };   // 「任何 T 的指標」

cout << IsPointer<int>::value << IsPointer<int*>::value
     << IsPointer<string*>::value << IsPointer<int**>::value << '\n';   // 輸出：0111
```

`int**` 也符合 `T*`（`T = int*`）。這就是標準函式庫 `std::is_pointer` 的實作原理。

### 例 2：固定一部分參數

```cpp
template <class A, class B>
struct Pair { string info() const { return "兩個不同型別"; } };

template <class T>
struct Pair<T, T> { string info() const { return "兩個相同型別"; } };    // A 和 B 相同時

template <class T>
struct Pair<T, int> { string info() const { return "第二個是 int"; } };  // B 固定是 int

cout << Pair<char, double>().info() << '\n';   // 輸出：兩個不同型別
cout << Pair<double, double>().info() << '\n'; // 輸出：兩個相同型別
cout << Pair<char, int>().info() << '\n';      // 輸出：第二個是 int
// Pair<int, int>：同時符合 <T, T> 和 <T, int>，兩個一樣特定 → ❌ error: ambiguous template instantiation
```

**選擇規則**：符合的特化裡選 **最特定** 的；一個都不符合就用主模板；有兩個一樣特定就是模稜兩可的錯誤。

### 例 3：所有 vector

```cpp
template <class T> struct ElemCount { static int get(const T&) { return 1; } };
template <class T> struct ElemCount<vector<T>> {
    static int get(const vector<T>& v) { return (int)v.size(); }
};
cout << ElemCount<int>::get(5) << ' ' << ElemCount<vector<int>>::get({1, 2, 3}) << '\n';   // 輸出：1 3
```

---

# 第五部分：模板怎麼被編譯

## 5.1 實例化 (Instantiation)

**是什麼**：模板本身 **不會產生任何機器碼**。編譯器看到 `my_max<int>` 被使用時，才 **照著模板產生一份 `int` 版本的程式碼**。這個過程叫實例化。

```cpp
my_max(1, 2);        // 產生 my_max<int>
my_max(1.0, 2.0);    // 產生 my_max<double>
my_max(3, 4);        // 已經有 my_max<int> 了，不會再產生
```

**比喻**：模具本身不能吃，要倒進麵糊、烤出來才是餅乾。

**親眼看到「每個實例化是不同的函式」**：

```cpp
template <class T>
int call_count() { static int n = 0; return ++n; }   // static 區域變數：每個實例化各有一份

call_count<int>(); call_count<int>();
call_count<double>();
cout << call_count<int>() << ' ' << call_count<double>() << '\n';   // 輸出：3 2
```

**結果**：
- 用到幾種型別，就有幾份程式碼（**程式碼膨脹 code bloat**），但每一份都能針對該型別完全最佳化 → 很快。`sort` 比 C 的 `qsort` 快，就是因為比較函式可以被內聯。
- 模板裡的錯誤，**要到實例化時才會被發現**（3.3 節）。

### 🔍 兩階段檢查

編譯器檢查模板分兩個階段：
1. **定義時**：只檢查「跟 `T` 無關」的部分（語法、不依賴 `T` 的名稱）。
2. **實例化時**：知道 `T` 是什麼了，才檢查跟 `T` 有關的部分。

```cpp
template <class T>
void f(T x) {
    x.whatever();            // 依賴 T：定義時不檢查（也許某個 T 真的有 whatever）
    // undefined_function(); // 不依賴 T：定義時就會報錯
}
// 只要沒有人呼叫 f，第一行就不會出錯
```

## 5.2 為什麼模板要寫在標頭檔？

一般的函式可以「宣告在 `.h`、定義在 `.cpp`」（第 09 課 2.2），但模板通常 **整個寫在標頭檔裡**。

**原因**：實例化需要 **看到完整的定義**。

```
stack.h      template <class T> class Stack { void push(const T&); };   ← 只有宣告
stack.cpp    template <class T> void Stack<T>::push(...) { ... }        ← 定義
main.cpp     Stack<int> s; s.push(1);
```

1. 編譯 `main.cpp`：需要 `Stack<int>::push`，但只看得到宣告，無法產生程式碼 → 先假設別的地方有。
2. 編譯 `stack.cpp`：有定義，但這個檔案裡沒有人用到 `Stack<int>` → 什麼都不產生。
3. 連結：找不到 `Stack<int>::push` → **`undefined reference to 'Stack<int>::push(int const&)'`**。

**解法**：
1. **（最常見）把定義寫在標頭檔裡**：所有 include 它的檔案都看得到定義。
2. 🔍 **明確實例化 (explicit instantiation)**：在 `stack.cpp` 最後寫 `template class Stack<int>;`，強迫產生 `int` 版本。缺點是只能用事先列出的型別。

## 5.3 🔍 typename 消除歧義

**問題**：在模板裡，`T::something` 可能是 **型別**（例如 `vector<int>::iterator`），也可能是 **靜態成員變數**（例如 `numeric_limits<int>::max` 是函式）。編譯器在實例化之前無法判斷，**預設當作「不是型別」**。

```cpp
template <class Container>
void print_first(const Container& c) {
    // Container::const_iterator it = c.begin();         // ❌ error: need 'typename' before 'Container::const_iterator' because 'Container' is a dependent scope
    typename Container::const_iterator it = c.begin();   // ✅ 告訴編譯器這是型別
    auto it2 = c.begin();                                 // ✅ 最簡單：用 auto
    cout << *it << ' ' << *it2 << '\n';
}
print_first(vector<int>{4, 5});                           // 輸出：4 4
print_first(string("hi"));                                // 輸出：h h
```

**規則**：**依賴模板參數的名稱**（dependent name，例如 `Container::xxx`、`T::xxx`）如果是型別，前面要加 `typename`。

**常見的例子**：

```cpp
template <class Container>
typename Container::value_type sum_all(const Container& c) {   // 回傳型別也要 typename
    typename Container::value_type total{};                   // value_type：容器裡元素的型別
    for (const auto& x : c) total += x;
    return total;
}
cout << sum_all(vector<int>{1, 2, 3}) << ' ' << sum_all(list<double>{0.5, 0.25}) << '\n';   // 輸出：6 0.75
```

---

# 第六部分：約束與變長模板

## 6.1 static_assert

**是什麼**：**編譯時** 檢查條件，不成立就 **編譯錯誤**，並顯示你寫的訊息。

**為什麼需要**：把模板的要求寫清楚，錯誤訊息從「一大串看不懂的模板內部錯誤」變成「你寫的一句話」。

```cpp
template <class T>
double average(const vector<T>& v) {
    static_assert(is_arithmetic_v<T>, "average() 只能用在數字型別");
    double s = 0;
    for (const T& x : v) s += x;
    return v.empty() ? 0 : s / v.size();
}
cout << average(vector<int>{1, 2, 4}) << '\n';   // 輸出：2.33333
// average(vector<string>{});
// ❌ error: static assertion failed: average() 只能用在數字型別
```

`static_assert` 也可以用在模板以外，檢查編譯環境的假設：

```cpp
static_assert(sizeof(int) == 4, "這個程式假設 int 是 4 bytes");
static_assert(sizeof(void*) == 8, "需要 64 位元系統");
```

## 6.2 型別特徵 (Type Traits)

**是什麼**：`<type_traits>` 提供很多「**在編譯時查詢或轉換型別**」的工具。結果是編譯期常數，可以用在 `static_assert`、`if constexpr`。

| 寫法 | 意思 | 例子 |
|---|---|---|
| `is_integral_v<T>` | 是整數型別嗎？（含 `bool`、`char`） | `is_integral_v<long>` → `true` |
| `is_floating_point_v<T>` | 是浮點數嗎？ | `is_floating_point_v<float>` → `true` |
| `is_arithmetic_v<T>` | 整數或浮點數？ | `is_arithmetic_v<string>` → `false` |
| `is_pointer_v<T>` | 是指標嗎？ | `is_pointer_v<int*>` → `true` |
| `is_same_v<T, U>` | 兩個型別完全一樣嗎？ | `is_same_v<int, int32_t>` → 通常 `true` |
| `is_const_v<T>` | 有 `const` 嗎？ | `is_const_v<const int>` → `true` |
| `is_base_of_v<B, D>` | `B` 是 `D` 的父類別嗎？ | 第 08 課的繼承關係 |
| `remove_reference_t<T>` | 去掉參考 | `int&` → `int` |
| `remove_const_t<T>` | 去掉 `const` | `const int` → `int` |
| `decay_t<T>` | 去掉參考和 `const`，陣列變指標 | 傳值時 `T` 會變成的型別 |

```cpp
cout << is_integral_v<long> << is_integral_v<double> << is_integral_v<bool>
     << is_arithmetic_v<string> << is_pointer_v<int*> << '\n';             // 輸出：10101
cout << is_same_v<remove_reference_t<int&>, int>
     << is_same_v<remove_const_t<const int>, int>
     << is_same_v<decay_t<const int&>, int> << '\n';                        // 輸出：111
struct Animal {}; struct Dog : Animal {};
cout << is_base_of_v<Animal, Dog> << is_base_of_v<Dog, Animal> << '\n';    // 輸出：10
```

`_v` 結尾的是值（C++17 的簡寫，等於 `is_integral<T>::value`）；`_t` 結尾的是型別（等於 `remove_reference<T>::type`）。

## 6.3 if constexpr：編譯期的 if

**是什麼**：C++17 的 `if constexpr (條件)`，條件必須是 **編譯期常數**，而且 **沒被選中的分支根本不會被編譯**。

**為什麼需要**：一般的 `if`，兩個分支都必須能編譯：

```cpp
template <class T>
string describe_bad(const T& x) {
    if (is_integral_v<T>) return "integer " + to_string(x);   // T = string 時：to_string(string) 不存在 → 編譯錯誤
    else return "other";                                       // 就算這個 if 執行時永遠不會走進去
}
```

改成 `if constexpr`：

```cpp
template <class T>
string describe(const T& x) {
    if constexpr (is_integral_v<T>) return "integer " + to_string(x);
    else if constexpr (is_floating_point_v<T>) return "float " + to_string(x);
    else if constexpr (is_same_v<T, string>) return "string \"" + x + "\"";
    else return "something else";
}
cout << describe(42) << '\n';                 // 輸出：integer 42
cout << describe(2.5) << '\n';                // 輸出：float 2.500000
cout << describe(string("hi")) << '\n';       // 輸出：string "hi"
cout << describe(vector<int>{}) << '\n';      // 輸出：something else
```

`T = string` 時，第一個分支 `to_string(x)` 根本不會被編譯，所以不會出錯。

**另一個例子：一個函式處理「指標或值」**

```cpp
template <class T>
auto get_value(const T& x) {
    if constexpr (is_pointer_v<T>) return *x;   // 指標：解參考
    else return x;                               // 值：直接回傳
}
int n = 7;
int* pn = &n;
cout << get_value(n) << ' ' << get_value(pn) << '\n';   // 輸出：7 7
```

## 6.4 C++20 Concepts

**是什麼**：**為模板參數加上具名的、明確的要求**。不符合要求時，錯誤訊息會直接告訴你「哪個要求沒滿足」，而不是一大串模板內部的錯誤。

**比喻**：餐廳門口貼著「**需穿著正式服裝**」—— 不符合的人在門口就被告知，而不是點完菜才發現被趕出來。

### 定義與使用 concept

```cpp
#include <concepts>
template <class T>
concept Comparable = requires(T a, T b) {       // requires：列出「這些運算式要能編譯」
    { a < b } -> std::convertible_to<bool>;     // 要求：能用 < 比較，結果能轉成 bool
};

template <Comparable T>                          // 用 concept 取代 class
T my_max3(T a, T b) { return a < b ? b : a; }

cout << my_max3(3, 9) << '\n';                   // 輸出：9
// my_max3(Point{}, Point{});
// ❌ error: no matching function for call to 'my_max3(Point, Point)'
//    note: constraints not satisfied
//    note: the required expression '(a < b)' is invalid
```

### 三種寫法

```cpp
template <Comparable T> T f1(T a, T b);                   // 1. 取代 class
template <class T> requires Comparable<T> T f2(T a, T b); // 2. requires 子句
auto f3(Comparable auto a, Comparable auto b);            // 3. 簡寫（參數用 auto）
```

### 標準函式庫內建的 concepts

| concept | 意思 |
|---|---|
| `std::integral<T>` | 整數型別 |
| `std::floating_point<T>` | 浮點數型別 |
| `std::same_as<T, U>` | 相同型別 |
| `std::convertible_to<From, To>` | 可以轉換 |
| `std::totally_ordered<T>` | 支援 `<`、`>`、`<=`、`>=`、`==`、`!=` |
| `std::copyable<T>` | 可以複製 |

```cpp
template <std::integral T>
T gcd2(T a, T b) { return b == 0 ? a : gcd2(b, a % b); }
cout << gcd2(12, 18) << '\n';                    // 輸出：6
// gcd2(1.5, 2.5);                               // ❌ note: constraints not satisfied
                                                 //    note: the expression 'is_integral_v<_Tp> [with _Tp = double]' evaluated to 'false'
```

**注意**：本平台用 C++17 編譯，concepts 需要 `-std=c++20`。在 C++17 裡用 `static_assert` 達到類似效果。

## 6.5 🔍 變長模板 (Variadic Template)

**是什麼**：接受 **任意數量** 模板參數的模板。`...` 叫 **參數包 (parameter pack)**。

```cpp
template <class... Args>              // Args 是「型別的包」：可能是 0 個、1 個、很多個型別
void count_args(const Args&... args) {    // args 是「值的包」
    cout << sizeof...(args) << '\n';  // sizeof...：包裡有幾個東西
}
count_args();                         // 輸出：0
count_args(1, "two", 3.0);            // 輸出：3
```

### 展開參數包：摺疊運算式 (Fold Expression, C++17)

```cpp
template <class... Args>
void print_all(const Args&... args) {
    ((cout << args << ' '), ...);     // 對每個參數都做一次 (cout << arg << ' ')
    cout << '\n';
}
print_all(1, "hi", 3.5, 'c');         // 輸出：1 hi 3.5 c

template <class... Args>
auto sum(Args... args) { return (args + ...); }   // 展開成 a1 + (a2 + (a3 + a4))
cout << sum(1, 2, 3, 4) << ' ' << sum(1.5, 2) << '\n';   // 輸出：10 3.5

template <class... Args>
bool all_positive(Args... args) { return ((args > 0) && ...); }
cout << all_positive(1, 2, 3) << all_positive(1, -2, 3) << '\n';   // 輸出：10
```

| 寫法 | 名稱 | 展開成 |
|---|---|---|
| `(args + ...)` | 一元右摺疊 | `a1 + (a2 + (a3 + a4))` |
| `(... + args)` | 一元左摺疊 | `((a1 + a2) + a3) + a4` |
| `(args + ... + 0)` | 二元右摺疊（有初值） | `a1 + (a2 + (a3 + 0))`，0 個參數時回傳 0 |
| `(expr, ...)` | 逗號摺疊 | 對每個參數各執行一次 `expr` |

**空的參數包**：`(args + ...)` 遇到 0 個參數會編譯錯誤（不知道 0 個東西相加是多少）；`&&` 是 `true`、`||` 是 `false`、`,` 是 `void()`。需要處理 0 個時，用二元摺疊給初值。

### C++17 之前的寫法：遞迴

```cpp
void print_rec() { cout << '\n'; }                 // 終止條件：沒有參數了
template <class First, class... Rest>
void print_rec(const First& f, const Rest&... rest) {
    cout << f << ' ';                              // 處理第一個
    print_rec(rest...);                            // 剩下的遞迴處理
}
print_rec(1, 2.5, "x");                            // 輸出：1 2.5 x
```

### 完美轉發 (Perfect Forwarding)

**是什麼**：把收到的引數 **原封不動**（左值還是左值、右值還是右值）轉交給另一個函式。寫法是 `T&&`（轉發參考 forwarding reference）+ `std::forward<T>`。

```cpp
template <class T, class... Args>
unique_ptr<T> my_make_unique(Args&&... args) {
    return unique_ptr<T>(new T(std::forward<Args>(args)...));   // 原樣轉交給 T 的建構子
}
auto p = my_make_unique<pair<string, int>>("age", 18);
cout << p->first << ' ' << p->second << '\n';                   // 輸出：age 18
```

`make_unique`、`make_shared`、`emplace_back` 都是這樣實作的：它們不知道 `T` 的建構子需要幾個、什麼型別的參數，就用變長模板全部收下，再用 `std::forward` 原樣轉交。`std::forward` 保留了右值性質，讓 `T` 的建構子能使用移動而不是複製（第 06 課）。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 泛型程式設計 | Generic Programming | 寫一份程式適用很多種型別 | 1.2 |
| 模板 | Template | 產生函式或類別的模具 | 1.2 |
| 模板參數 | Template Parameter | 型別（或常數）的佔位符 | 2.1 |
| 模板引數推導 | Template Argument Deduction | 根據引數自動決定 T | 2.2 |
| 鴨子型別 | Duck Typing | 支援需要的操作就能用 | 2.3 |
| 類別模板 | Class Template | 產生類別的模具 | 3.1 |
| 類別模板引數推導 | CTAD | C++17 自動推導類別模板參數 | 3.6 |
| 別名模板 | Alias Template | `template <class T> using X = ...;` | 3.7 |
| 非型別模板參數 | Non-type Template Parameter | 模板參數是編譯期常數 | 4.1 |
| 主模板 | Primary Template | 沒有特化的通用版本 | 4.2 |
| 完全 / 部分特化 | Full / Partial Specialization | 為特定型別 / 某類型別提供專門實作 | 4.2、4.3 |
| 實例化 | Instantiation | 照模板產生具體型別的程式碼 | 5.1 |
| 程式碼膨脹 | Code Bloat | 每種型別一份程式碼，執行檔變大 | 5.1 |
| 明確實例化 | Explicit Instantiation | `template class Stack<int>;` 強迫產生 | 5.2 |
| 依賴名稱 | Dependent Name | 依賴模板參數的名稱，型別要加 typename | 5.3 |
| 靜態斷言 | static_assert | 編譯時檢查條件 | 6.1 |
| 型別特徵 | Type Traits | 編譯時查詢型別性質 | 6.2 |
| 編譯期 if | if constexpr | 編譯時選擇分支，沒選中的不編譯 | 6.3 |
| 概念 | Concept | 對模板參數的明確要求，C++20 | 6.4 |
| 變長模板 / 參數包 | Variadic Template / Parameter Pack | 接受任意數量的參數 | 6.5 |
| 摺疊運算式 | Fold Expression | 對參數包的每個元素套用運算子 | 6.5 |
| 完美轉發 | Perfect Forwarding | 原封不動地轉交引數 | 6.5 |

---

# 習題

### 題 1：哪些呼叫可以編譯？T 是什麼？

```cpp
template <class T> T twice(T x) { return x + x; }

a) twice(3)
b) twice(2.5)
c) twice(string("ab"))
d) twice("ab")
e) twice<double>(3)
```

### 題 2：哪些可以編譯？

```cpp
template <class T> T add(T a, T b) { return a + b; }

a) add(1, 2)
b) add(1, 2.0)
c) add<long long>(1, 2)
d) add(1.0f, 2.0f)
```

### 題 3：預測輸出

```cpp
template <class T> void f(T)        { cout << "T "; }
template <class T> void f(T*)       { cout << "T* "; }
void f(int)                         { cout << "int "; }

int x = 0;
f(x); f(&x); f(3.0); f('c');
```

### 題 4：`Stack<int>` 和 `Stack<long>` 有什麼關係？下面這行可以編譯嗎？

```cpp
Stack<int> a;
Stack<long> b = a;
```

### 題 5：為什麼這段程式在連結時失敗？

```cpp
// stack.h
template <class T> class Stack { public: void push(const T&); ... };
// stack.cpp
#include "stack.h"
template <class T> void Stack<T>::push(const T& x) { ... }
// main.cpp
#include "stack.h"
int main() { Stack<int> s; s.push(1); }   // undefined reference to Stack<int>::push
```

### 題 6：預測輸出

```cpp
template <class T> struct Info { static const char* name() { return "other"; } };
template <> struct Info<int> { static const char* name() { return "int"; } };
template <class T> struct Info<T*> { static const char* name() { return "pointer"; } };

cout << Info<double>::name() << ' ' << Info<int>::name() << ' ' << Info<int*>::name() << ' ' << Info<int**>::name();
```

### 題 7：寫一個函式模板 `count_if_greater(const vector<T>& v, T x)`，回傳大於 `x` 的元素個數。它對 `T` 有什麼隱含的要求？

### 題 8：預測輸出

```cpp
template <class T>
struct Tally {
    inline static int n = 0;
    Tally() { n++; }
};
Tally<int> a, b;
Tally<char> c;
Tally<int> d;
cout << Tally<int>::n << Tally<char>::n << Tally<double>::n;
```

### 題 9：預測輸出

```cpp
template <class... Args>
int count_ints(Args... args) { return (0 + ... + (is_same_v<Args, int> ? 1 : 0)); }
cout << count_ints(1, 2.0, 3, 'c', 4) << ' ' << count_ints();
```

### 題 10：下面的函式模板為什麼對 `string` 會編譯失敗？用 `if constexpr` 修正它。

```cpp
template <class T>
void show(const T& x) {
    if (is_arithmetic_v<T>) cout << x * 2 << '\n';
    else cout << x << '\n';
}
show(5);
show(string("hi"));
```

### 題 11：用模板寫一個 `Pair<A, B>` 類別模板，以及一個函式模板 `swap_pair`，把 `Pair<A, B>` 轉成 `Pair<B, A>`。

---

# 習題解答

**題 1**：
- a) `int`，回傳 6。
- b) `double`，回傳 5.0。
- c) `string`，回傳 `"abab"`。
- d) **編譯錯誤**：`T` 被推導成 `const char*`（陣列退化成指標），兩個指標不能相加。
- e) `double`，`3` 被轉成 `3.0`，回傳 6.0。

**題 2**：a ✅（int）；b ❌（`int` 和 `double` 推導衝突）；c ✅（明確指定，`1`、`2` 轉成 `long long`）；d ✅（float）。

**題 3**：`int T* T T `。
- `f(x)`：一般函式 `f(int)` 和模板 `f<int>(int)` 一樣好，**優先選一般函式** → `int`。
- `f(&x)`：`f(T*)` 比 `f(T)` 更特定 → `T*`。
- `f(3.0)`：`f(int)` 需要轉換，模板 `f<double>` 完全符合 → `T`。
- `f('c')`：`f(int)` 需要提升，模板 `f<char>` 完全符合 → `T`。

**題 4**：**完全不同、互不相關的兩個型別**（雖然 `int` 可以轉成 `long`）。除非 `Stack` 自己寫了「從 `Stack<U>` 轉換」的建構子，否則 **不能編譯**。

**題 5**：編譯 `stack.cpp` 時，沒有人用到 `Stack<int>`，所以不會實例化 `Stack<int>::push`；編譯 `main.cpp` 時，只看得到宣告，看不到定義，無法實例化。連結時找不到 `Stack<int>::push` 的程式碼。**解法**：把成員函式的定義也放在標頭檔裡（或在 `stack.cpp` 加上明確實例化 `template class Stack<int>;`）。

**題 6**：`other int pointer pointer`。`int**` 符合 `T*`（`T = int*`），選部分特化版本。

**題 7**：

```cpp
template <class T>
size_t count_if_greater(const vector<T>& v, const T& x) {
    size_t c = 0;
    for (const T& e : v) if (x < e) c++;
    return c;
}
cout << count_if_greater(vector<int>{1, 5, 3, 8}, 3) << '\n';   // 輸出：2
```

隱含要求：`T` 要支援 `<` 比較（回傳能轉成 `bool` 的值）。用 C++20 可以寫成 `template <std::totally_ordered T>` 把要求寫清楚。（注意：用 `x < e` 而不是 `e > x`，這樣只需要 `T` 支援 `<` 一種運算子。）

**題 8**：`310`。`Tally<int>`、`Tally<char>`、`Tally<double>` 是三個不同的類別，各有一份 `n`。`Tally<int>` 建立了 `a`、`b`、`d` 三個；`Tally<char>` 一個；`Tally<double>` 一個都沒建立（但 `Tally<double>::n` 還是存在，值是 0）。

**題 9**：`3 0`。
- 二元左摺疊 `(0 + ... + expr)` 展開成 `((((0 + e1) + e2) + e3) + e4) + e5`，每一項在該參數的型別是 `int` 時為 1、否則為 0。
- 參數型別依序是 `int, double, int, char, int`（注意 `2.0` 是 `double`、`'c'` 是 `char`，都不是 `int`）→ 1 + 0 + 1 + 0 + 1 = 3。
- `count_ints()` 沒有參數：二元摺疊直接回傳初值 `0`（如果寫成沒有初值的 `(... + expr)`，0 個參數就會編譯錯誤）。

**題 10**：一般的 `if` 兩個分支都要能編譯。`T = string` 時，`x * 2` 不能編譯（字串不能乘以 2），就算執行時不會走進那個分支也一樣。改成 `if constexpr (is_arithmetic_v<T>)`，`T = string` 時第一個分支就不會被編譯。輸出：`10` 和 `hi`。

**題 11**：

```cpp
template <class A, class B>
struct Pair {
    A first;
    B second;
};
template <class A, class B>
Pair<B, A> swap_pair(const Pair<A, B>& p) {
    return {p.second, p.first};
}
Pair<int, string> p{1, "one"};
auto q = swap_pair(p);                       // Pair<string, int>，A、B 自動推導
cout << q.first << ' ' << q.second << '\n';  // 輸出：one 1
```
