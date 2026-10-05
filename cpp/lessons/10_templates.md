# 10. 模板與泛型程式設計 (Templates & Generic Programming)

> 程式練習：`C10 泛型堆疊`
>
> 先備知識：第 04 課「函式多載」、第 07 課「類別」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 為什麼需要模板 | 重複程式碼的問題、泛型程式設計 |
| 第二部分 | 函式模板 | 型別推導、推導失敗、模板與多載 |
| 第三部分 | 類別模板 | 寫法、成員函式定義、C++17 的類別模板推導 |
| 第四部分 | 非型別參數與特化 | `template <int N>`、完全特化、部分特化 |
| 第五部分 | 模板怎麼被編譯 | 實例化、為什麼要寫在標頭檔、`typename` 關鍵字 |
| 第六部分 | 約束與變長模板 | `static_assert`、type traits、C++20 concepts、參數包 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：為什麼需要模板

## 1.1 問題：同樣的邏輯，不同的型別

```cpp
int    max_int(int a, int b)          { return a < b ? b : a; }
double max_double(double a, double b) { return a < b ? b : a; }
string max_string(const string& a, const string& b) { return a < b ? b : a; }
// 每多一種型別就要再寫一次……
```

邏輯一模一樣，只有型別不同。多載可以讓名字相同，但還是要寫好幾份。

## 1.2 泛型程式設計 (Generic Programming)

**白話**：寫一份 **跟型別無關** 的程式碼，讓它可以用在 **很多種型別** 上。C++ 用 **模板 (template)** 來做到。

**比喻**：**餅乾模具**。同一個星星形狀的模具，可以壓出巧克力口味、抹茶口味、原味的餅乾 —— 模具（模板）只有一個，口味（型別）由你決定。

```cpp
template <class T>
T my_max(T a, T b) { return a < b ? b : a; }

my_max(3, 5);                          // T = int
my_max(2.5, 1.5);                      // T = double
my_max(string("a"), string("b"));      // T = string
```

STL 整個就是建立在模板上：`vector<T>`、`map<K, V>`、`sort`、`find`……

---

# 第二部分：函式模板 (Function Template)

## 2.1 語法

```cpp
template <class T>              // 或 template <typename T>，兩者在這裡完全相同
void swap_values(T& a, T& b) {
    T tmp = a;
    a = b;
    b = tmp;
}
```

`T` 叫做 **模板參數 (template parameter)**，是一個「型別的佔位符」。

## 2.2 模板引數推導 (Template Argument Deduction)

**白話**：呼叫時，編譯器 **根據引數的型別自動推導出 `T`**，不用自己寫。

```cpp
my_max(3, 5);            // 推導 T = int
my_max<double>(3, 5);    // 明確指定 T = double（3、5 會被轉成 double）
```

### 推導失敗

```cpp
my_max(3, 2.5);          // ❌ 編譯錯誤：第一個引數說 T = int，第二個說 T = double，矛盾
my_max<double>(3, 2.5);  // ✅ 明確指定
my_max(3.0, 2.5);        // ✅
```

**模板推導時不做隱式轉換**（一般函式會把 `int` 轉成 `double`，但模板推導不會）。

**用兩個型別參數** 也可以解決：

```cpp
template <class A, class B>
auto my_max2(A a, B b) { return a < b ? b : a; }   // 回傳型別自動推導（C++14）
my_max2(3, 2.5);   // 回傳 double 3.0
```

## 2.3 隱含的要求

**白話**：模板對型別有「**隱含的要求**」—— 函式本體用到什麼操作，`T` 就必須支援。

```cpp
my_max(Point{1, 2}, Point{3, 4});   // ❌ 如果 Point 沒有 operator<，編譯錯誤
```

這有點像「**鴨子型別 (duck typing)**」：「走起路來像鴨子、叫起來像鴨子，就是鴨子」—— 只要型別支援需要的操作，就能用。

> 錯誤訊息常常很長很難讀，因為錯誤發生在模板 **內部**。C++20 的 concepts（第 6.3 節）就是為了解決這個問題。

## 2.4 模板與多載

函式模板也可以 **多載**，編譯器會挑「**最特定 (most specialized)**」的版本：

```cpp
template <class T> void print(const T& x) { cout << x; }
template <class A, class B> void print(const pair<A, B>& p) {     // 比較特定的版本
    cout << '(' << p.first << ',' << p.second << ')';
}
void print(bool b) { cout << (b ? "true" : "false"); }            // 一般函式

print(42);              // 第一個模板，T = int
print(make_pair(1, 2)); // 第二個模板（pair 版本更特定）
print(true);            // 一般函式（一般函式和模板一樣好時，優先選一般函式）
```

`C10` 題就是用這個方法，讓 `pair` 有不同的輸出格式。

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
};

Stack<int> si;          // 類別模板一定要寫出型別（C++17 前）
Stack<string> ss;
```

`Stack` 本身 **不是一個型別**，是「產生型別的模具」；`Stack<int>`、`Stack<string>` 才是型別，而且 **是兩個完全不同、互不相關的型別**。

## 3.2 在類別外定義成員函式

```cpp
template <class T>
class Stack {
public:
    void push(const T& x);
};

template <class T>                        // 每個成員函式前面都要重寫一次
void Stack<T>::push(const T& x) {         // 類別名稱要寫 Stack<T>
    data_.push_back(x);
}
```

## 3.3 預設模板引數

```cpp
template <class T, class Container = vector<T>>
class Stack { Container c_; ... };

Stack<int> a;                  // 用 vector<int>
Stack<int, deque<int>> b;      // 用 deque<int>
```

`std::stack`、`std::priority_queue` 就是這樣設計的。

## 3.4 類別模板引數推導 (CTAD, C++17)

```cpp
pair p(1, 2.5);        // C++17：自動推導成 pair<int, double>
vector v{1, 2, 3};     // vector<int>
```

---

# 第四部分：非型別參數與特化

## 4.1 非型別模板參數 (Non-type Template Parameter)

**白話**：模板參數不一定是型別，也可以是 **編譯期常數**（整數、指標、C++20 起還有更多）。

```cpp
template <class T, size_t N>
class FixedArray {
    T data_[N];                    // N 在編譯時就知道，可以當陣列大小
public:
    constexpr size_t size() const { return N; }
    T& operator[](size_t i) { return data_[i]; }
};
FixedArray<int, 10> a;            // FixedArray<int, 10> 和 FixedArray<int, 20> 是不同的型別

std::array<int, 5> arr;           // STL 的 std::array 就是這樣
bitset<64> bits;                  // bitset 也是
```

**好處**：大小在編譯時就固定，不需要動態配置，而且編譯器可以做更多最佳化。

## 4.2 完全特化 (Full Specialization)

**白話**：為 **某個特定的型別**，提供一個 **完全不同的實作**。

```cpp
template <class T>
struct TypeName { static string get() { return "unknown"; } };

template <>                                        // 空的角括號：完全特化
struct TypeName<int> { static string get() { return "int"; } };

template <>
struct TypeName<double> { static string get() { return "double"; } };

TypeName<int>::get();       // "int"
TypeName<char>::get();      // "unknown"
```

**比喻**：餅乾工廠大部分口味都用同一條生產線，但「無麩質」口味有專屬的生產線。

STL 的例子：`vector<bool>` 是特化版本，每個 `bool` 只用 1 bit 存（省空間，但也因此行為怪異，例如不能取得元素的 `bool&`）。

## 4.3 部分特化 (Partial Specialization)

**白話**：為「**某一類**」型別提供特別的實作（只固定一部分參數）。**只有類別模板可以部分特化**，函式模板不行（用多載代替）。

```cpp
template <class T>
struct IsPointer { static constexpr bool value = false; };

template <class T>
struct IsPointer<T*> { static constexpr bool value = true; };   // 所有指標型別

IsPointer<int>::value;       // false
IsPointer<int*>::value;      // true
IsPointer<string*>::value;   // true
```

這就是標準函式庫 `std::is_pointer` 的實作原理。

---

# 第五部分：模板怎麼被編譯

## 5.1 實例化 (Instantiation)

**白話**：模板本身 **不會產生任何機器碼**。編譯器看到 `my_max<int>` 被使用時，才 **照著模板產生一份 `int` 版本的程式碼**。這個過程叫實例化。

```cpp
my_max(1, 2);        // 產生 my_max<int>
my_max(1.0, 2.0);    // 產生 my_max<double>
my_max(3, 4);        // 已經有 my_max<int> 了，不會再產生
```

**比喻**：模具本身不能吃，要倒進麵糊、烤出來才是餅乾。

**結果**：
- 用到幾種型別，就有幾份程式碼（**程式碼膨脹 code bloat**），但每一份都能針對該型別完全最佳化 → 很快。
- 模板裡的錯誤，**要到實例化時才會被發現**。沒被用到的成員函式甚至不會被檢查。

## 5.2 為什麼模板要寫在標頭檔？

一般的函式可以「宣告在 `.h`、定義在 `.cpp`」，但模板通常 **整個寫在標頭檔裡**。

原因：實例化需要 **看到完整的定義**。如果 `Stack<T>::push` 的定義放在 `stack.cpp`，`main.cpp` 用到 `Stack<int>` 時，編譯器只看得到宣告，無法產生 `Stack<int>::push` 的程式碼；而編譯 `stack.cpp` 時又不知道有人需要 `int` 版本。結果是 **連結錯誤**（undefined reference）。

## 5.3 🔍 typename 消除歧義

在模板裡，`T::something` 可能是 **型別**，也可能是 **靜態成員變數**，編譯器無法判斷。預設當作 **變數**：

```cpp
template <class Container>
void print_first(const Container& c) {
    Container::const_iterator it = c.begin();            // ❌ 編譯錯誤
    typename Container::const_iterator it = c.begin();   // ✅ 告訴編譯器這是型別
    auto it2 = c.begin();                                 // ✅ 最簡單：用 auto
}
```

規則：**依賴模板參數的名稱**（dependent name）如果是型別，前面要加 `typename`。

---

# 第六部分：約束與變長模板

## 6.1 static_assert

**白話**：編譯時檢查條件，不成立就 **編譯錯誤**，並顯示你寫的訊息。

```cpp
template <class T>
T average(const vector<T>& v) {
    static_assert(is_arithmetic_v<T>, "average() 只能用在數字型別");
    ...
}
average(vector<string>{});   // 編譯錯誤：average() 只能用在數字型別
```

## 6.2 型別特徵 (Type Traits)

`<type_traits>` 提供很多「**在編譯時查詢型別性質**」的工具：

| 寫法 | 意思 |
|---|---|
| `is_integral_v<T>` | 是整數型別嗎？ |
| `is_floating_point_v<T>` | 是浮點數嗎？ |
| `is_pointer_v<T>` | 是指標嗎？ |
| `is_same_v<T, U>` | 兩個型別一樣嗎？ |
| `remove_reference_t<T>` | 去掉參考（`int&` → `int`） |

搭配 C++17 的 `if constexpr`，可以在 **編譯時** 依型別選擇不同的程式碼：

```cpp
template <class T>
string describe(const T& x) {
    if constexpr (is_integral_v<T>) return "integer " + to_string(x);
    else if constexpr (is_floating_point_v<T>) return "float " + to_string(x);
    else return "something else";     // 沒被選中的分支不會被編譯（所以 to_string(string) 不會出錯）
}
```

## 6.3 C++20 Concepts

**白話**：**為模板參數加上明確的要求**。不符合要求時，錯誤訊息會直接告訴你「哪個要求沒滿足」，而不是一大串模板內部的錯誤。

```cpp
#include <concepts>
template <class T>
concept Comparable = requires(T a, T b) {
    { a < b } -> std::convertible_to<bool>;    // 要求：能用 < 比較
};

template <Comparable T>
T my_max(T a, T b) { return a < b ? b : a; }

my_max(Point{}, Point{});
// 錯誤訊息：the constraint 'Comparable<Point>' was not satisfied
```

**比喻**：餐廳門口貼著「**需穿著正式服裝**」—— 不符合的人在門口就被告知，而不是點完菜才發現被趕出來。

## 6.4 🔍 變長模板 (Variadic Template)

**白話**：接受 **任意數量** 模板參數的模板。`...` 叫 **參數包 (parameter pack)**。

```cpp
template <class... Args>
void print_all(const Args&... args) {
    ((cout << args << ' '), ...);     // C++17 摺疊運算式 (fold expression)：對每個參數都做一次
    cout << '\n';
}
print_all(1, "hi", 3.5, 'c');          // 1 hi 3.5 c

template <class... Args>
auto sum(Args... args) { return (args + ...); }   // 右摺疊：a1 + (a2 + (a3 + ...))
sum(1, 2, 3, 4);   // 10
```

`make_unique<T>(args...)`、`emplace_back(args...)`、`printf` 風格的格式化函式都是用變長模板實作的。

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
| 類別模板引數推導 | CTAD | C++17 自動推導類別模板參數 | 3.4 |
| 非型別模板參數 | Non-type Template Parameter | 模板參數是編譯期常數 | 4.1 |
| 完全 / 部分特化 | Full / Partial Specialization | 為特定型別 / 某類型別提供專門實作 | 4.2、4.3 |
| 實例化 | Instantiation | 照模板產生具體型別的程式碼 | 5.1 |
| 程式碼膨脹 | Code Bloat | 每種型別一份程式碼，執行檔變大 | 5.1 |
| 依賴名稱 | Dependent Name | 依賴模板參數的名稱，型別要加 typename | 5.3 |
| 型別特徵 | Type Traits | 編譯時查詢型別性質 | 6.2 |
| 編譯期 if | if constexpr | 編譯時選擇分支 | 6.2 |
| 概念 | Concept | 對模板參數的明確要求，C++20 | 6.3 |
| 變長模板 / 參數包 | Variadic Template / Parameter Pack | 接受任意數量的參數 | 6.4 |
| 摺疊運算式 | Fold Expression | 對參數包的每個元素套用運算子 | 6.4 |

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

---

# 習題解答

**題 1**：
- a) `int`，回傳 6。
- b) `double`，回傳 5.0。
- c) `string`，回傳 `"abab"`。
- d) **編譯錯誤**：`T` 被推導成 `const char*`，兩個指標不能相加。
- e) `double`，`3` 被轉成 `3.0`，回傳 6.0。

**題 2**：a ✅（int）；b ❌（`int` 和 `double` 推導衝突）；c ✅（明確指定，`1`、`2` 轉成 `long long`）；d ✅（float）。

**題 3**：`int T* T T `。
- `f(x)`：一般函式 `f(int)` 和模板 `f<int>(int)` 一樣好，**優先選一般函式** → `int`。
- `f(&x)`：`f(T*)` 比 `f(T)` 更特定 → `T*`。
- `f(3.0)`：`f(int)` 需要轉換，模板 `f<double>` 完全符合 → `T`。
- `f('c')`：`f(int)` 需要提升，模板 `f<char>` 完全符合 → `T`。

**題 4**：**完全不同、互不相關的兩個型別**（雖然 `int` 可以轉成 `long`）。除非 `Stack` 自己寫了「從 `Stack<U>` 轉換」的建構子，否則 **不能編譯**。

**題 5**：編譯 `stack.cpp` 時，沒有人用到 `Stack<int>`，所以不會實例化 `Stack<int>::push`；編譯 `main.cpp` 時，只看得到宣告，看不到定義，無法實例化。連結時找不到 `Stack<int>::push` 的程式碼。**解法**：把成員函式的定義也放在標頭檔裡。

**題 6**：`other int pointer pointer`。`int**` 符合 `T*`（`T = int*`），選部分特化版本。

**題 7**：

```cpp
template <class T>
size_t count_if_greater(const vector<T>& v, const T& x) {
    size_t c = 0;
    for (const T& e : v) if (x < e) c++;
    return c;
}
```

隱含要求：`T` 要支援 `<` 比較（回傳能轉成 `bool` 的值）。用 C++20 可以寫成 `template <std::totally_ordered T>` 把要求寫清楚。（注意：用 `x < e` 而不是 `e > x`，這樣只需要 `T` 支援 `<` 一種運算子。）

---

# 程式練習

- **`C10 泛型堆疊`**：一個 `Stack<T>` 同時存 `int`、`string`、`pair<int, string>`；用函式模板處理三種型別共通的指令，用模板多載處理 `pair` 的特殊輸出格式。
