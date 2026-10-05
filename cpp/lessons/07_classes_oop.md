# 07. 類別與物件導向 (Classes & OOP)

> 程式練習：`C07 分數類別`
>
> 先備知識：第 04 課「函式」、第 05 課「參考」。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 類別與封裝 | 類別、物件、存取控制、不變量 |
| 第二部分 | 建構子全攻略 | 成員初始化串列、初始化順序的陷阱、`explicit`、委派建構子 |
| 第三部分 | 成員的種類 | `this`、`const` 成員函式、`static` 成員、`friend` |
| 第四部分 | 運算子多載 | 成員 vs 非成員、該回傳什麼、`++` 的前置與後置 |
| 第五部分 | 物件導向的四大概念 | 封裝、抽象、繼承、多型的整體地圖 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：類別與封裝

## 1.1 類別與物件 (Class / Object)

**白話**：
- **類別**：一種 **自訂的型別**，把「**資料**」和「**操作這些資料的函式**」包在一起。
- **物件 / 實例 (instance)**：用類別建立出來的一個具體的東西。

**比喻**：類別是 **設計圖**，物件是照著設計圖蓋出來的 **房子**。一張設計圖可以蓋很多間房子，每間房子有自己的家具（資料），但格局（結構和功能）都一樣。

```cpp
class Account {
private:
    string owner_;           // 成員變數 (data member)
    long long balance_ = 0;
public:
    void deposit(long long amt) { balance_ += amt; }   // 成員函式 (member function)
    long long balance() const { return balance_; }
};

Account a, b;        // 兩個物件，各自有自己的 balance_
a.deposit(100);      // 只改 a 的
```

## 1.2 存取控制 (Access Specifiers)

| 關鍵字 | 誰可以存取 |
|---|---|
| `public` | 所有人 |
| `private` | 只有這個類別自己的成員函式（和 `friend`） |
| `protected` | 自己 + 子類別（第 08 課） |

**`class` vs `struct`**：唯一的差別是 **預設的存取權限**。`class` 預設 `private`，`struct` 預設 `public`。
慣例：單純的資料包（沒有不變量）用 `struct`；有不變量、要保護的用 `class`。

## 1.3 封裝 (Encapsulation)

**白話**：把資料 **藏起來**（`private`），只透過 **公開的函式** 讓外界操作。

**比喻**：自動販賣機。你只能投錢、按按鈕（公開介面），不能直接打開機器拿飲料或改變裡面的價格（私有資料）。

為什麼要藏？為了保護 **不變量**。

## 1.4 不變量 (Invariant)

**白話**：一個物件 **在任何時候都應該成立** 的條件。

例子：
- `Fraction`（`C07`）：分母永遠是正的，而且分子分母互質。
- `Account`：儲蓄帳戶的餘額永遠 ≥ 0。
- `vector`：`size() <= capacity()`。

如果資料是 `public`，任何人都可以寫 `f.den_ = 0;` 破壞不變量。設成 `private`，只有類別自己的函式能修改，**只要每個成員函式都維持不變量，不變量就永遠成立**。

```cpp
class Fraction {
    long long num_, den_;    // private
public:
    Fraction(long long n, long long d) : num_(n), den_(d) { normalize(); }   // 建構時建立不變量
    Fraction operator+(const Fraction& o) const { ... }                      // 每個操作都回傳正規化的結果
};
```

### 🔍 getter / setter 的迷思

替每個成員都寫 `getX()` / `setX()`，其實 **等於沒有封裝**（任何人都能隨便設定）。
好的介面提供 **有意義的操作**（`deposit`、`withdraw`），而不是暴露資料本身（`setBalance`）。

---

# 第二部分：建構子全攻略

## 2.1 建構子 (Constructor)

**白話**：物件 **被建立時自動呼叫** 的特殊函式，名稱和類別相同，**沒有回傳型別**。負責讓物件處於合法的初始狀態（建立不變量）。

## 2.2 預設建構子 (Default Constructor)

**白話**：**不需要任何參數** 的建構子。

```cpp
class A { public: int x; };       // 沒寫任何建構子 → 編譯器自動產生預設建構子
A a;                              // ✅ 但 a.x 是垃圾值！
A b{};                            // ✅ 值初始化，b.x 是 0

class B { public: B(int v) {} };  // 自己寫了任何建構子 → 編譯器 **不再** 自動產生預設建構子
B b;                              // ❌ 編譯錯誤
```

**預設成員初始值 (default member initializer)**：直接在宣告時給初值，最簡單也最不容易忘：

```cpp
class Counter {
    int count_ = 0;               // 每個建構子都會用這個初值（除非建構子另外指定）
    string name_ = "unnamed";
};
```

## 2.3 成員初始化串列 (Member Initializer List)

```cpp
class Point {
    int x_, y_;
public:
    Point(int x, int y) : x_(x), y_(y) {}   // 初始化串列
};
```

**和在本體裡賦值的差別**：

```cpp
Point(int x, int y) { x_ = x; y_ = y; }   // 先「預設初始化」成員，再「賦值」
```

**一定要用初始化串列的情況**：
1. **`const` 成員**：建立之後就不能賦值。
2. **參考成員**：一定要在建立時綁定。
3. **沒有預設建構子的成員**（例如成員是上一節的 `B`）。
4. **基底類別** 需要參數時（第 08 課）。

而且對 `string`、`vector` 這類成員，初始化串列比「先預設建構再賦值」更有效率。

**比喻**：初始化串列是「出廠時就裝好零件」；在本體裡賦值是「先裝一個預設零件，出廠後再拆下來換」。

## 2.4 🔍 初始化順序的陷阱

**成員的初始化順序是「在類別裡宣告的順序」，不是初始化串列裡寫的順序！**

```cpp
class Range {
    int size_;        // 先宣告 → 先初始化
    int end_;
    int begin_;
public:
    Range(int b, int e) : begin_(b), end_(e), size_(end_ - begin_) {}
    // 實際順序：size_ 先初始化，這時 end_ 和 begin_ 都還是垃圾值！
};
```

`-Wall` 會警告 `will be initialized after`。**規則：初始化串列的順序寫得跟宣告順序一樣，並且不要讓成員互相依賴。**

## 2.5 委派建構子 (Delegating Constructor)

**白話**：一個建構子 **呼叫同一個類別的另一個建構子**，避免重複的程式碼。

```cpp
class Fraction {
public:
    Fraction(long long n, long long d) : num_(n), den_(d) { normalize(); }
    Fraction(long long n) : Fraction(n, 1) {}     // 委派給上面那個
    Fraction() : Fraction(0) {}
};
```

## 2.6 explicit：禁止隱式轉換

**白話**：**只有一個參數** 的建構子，會被編譯器拿來做 **自動型別轉換**。有時候這會造成意外。

```cpp
class Buffer {
public:
    Buffer(int size);              // 可以用 int 建立 Buffer
};
void send(const Buffer& b);
send(42);                          // 😱 編譯通過！自動建立一個大小 42 的 Buffer

class SafeBuffer {
public:
    explicit SafeBuffer(int size);
};
void send2(const SafeBuffer& b);
send2(42);                         // ❌ 編譯錯誤，好
send2(SafeBuffer(42));             // ✅ 必須明確寫出來
```

**比喻**：沒有 `explicit` 就像餐廳服務生「自動幫你升級套餐」；有 `explicit` 則是「要升級請自己說」。

**規則**：單一參數的建構子 **預設加上 `explicit`**，除非你真的想要自動轉換（例如 `Fraction(5)` 讓 `f + 5` 能運作，這是有意的）。

## 2.7 解構子 (Destructor)

**白話**：物件 **被銷毀時自動呼叫**，寫成 `~類別名()`，負責釋放資源（第 06 課 RAII）。沒有參數、沒有回傳值、不能多載。

---

# 第三部分：成員的種類

## 3.1 this 指標

**白話**：在成員函式裡，`this` 是 **指向「呼叫這個函式的那個物件」** 的指標。

```cpp
class Account {
    long long balance_;
public:
    Account& deposit(long long amt) {
        this->balance_ += amt;    // 等於 balance_ += amt
        return *this;             // 回傳自己 → 可以串接呼叫
    }
};
a.deposit(10).deposit(20);        // 方法串接 (method chaining)
```

🔍 **成員函式的本質**：`a.deposit(10)` 在底層大約等於 `Account::deposit(&a, 10)`，`this` 就是那個隱藏的第一個參數。

## 3.2 const 成員函式

**白話**：在參數列後面加 `const`，承諾「**這個函式不會修改物件**」。

```cpp
class Account {
public:
    long long balance() const { return balance_; }    // 不修改
    void deposit(long long amt) { balance_ += amt; }  // 會修改
};

const Account c;
c.balance();     // ✅
c.deposit(5);    // ❌ 編譯錯誤：const 物件只能呼叫 const 成員函式

void print(const Account& a) {
    cout << a.balance();    // 這裡的 a 是 const 參考，所以 balance() 必須是 const！
}
```

**最常見的錯誤**：忘了把「只是讀取」的函式標成 `const`，結果傳 `const T&` 的函式都無法呼叫它。

**規則：不會修改物件的成員函式，一律加 `const`。**

🔍 `mutable` 成員：即使在 `const` 函式裡也可以修改，用於「不影響物件邏輯狀態」的東西，例如快取、統計呼叫次數。

## 3.3 static 成員

**白話**：屬於 **整個類別**，而不是屬於某個物件。所有物件 **共用同一份**。

```cpp
class Student {
    static int count_;              // 宣告：所有 Student 共用
public:
    Student() { count_++; }
    ~Student() { count_--; }
    static int count() { return count_; }   // static 成員函式：沒有 this
};
int Student::count_ = 0;            // 定義（C++17 起可以在類別裡寫 inline static int count_ = 0;）

Student::count();                   // 不需要物件就能呼叫
```

**比喻**：班上每個同學有自己的座號（一般成員），但「全班人數」只有一個，寫在教室門口（static 成員）。

`static` 成員函式 **沒有 `this`**，所以不能存取一般的成員變數。

## 3.4 friend

**白話**：讓 **某個外部函式或類別** 可以存取這個類別的 `private` 成員。

```cpp
class Fraction {
    long long num_, den_;
    friend ostream& operator<<(ostream& os, const Fraction& f);   // 允許它存取 num_、den_
};
ostream& operator<<(ostream& os, const Fraction& f) {
    return os << f.num_ << '/' << f.den_;
}
```

**比喻**：把家裡的鑰匙給 **特定的好朋友**，他可以直接進來，其他人不行。

`friend` 會破壞封裝，**謹慎使用**。如果類別已經有公開的 `num()`、`den()`，就不需要 `friend`（`C07` 的樣板就是這樣設計的）。

---

# 第四部分：運算子多載 (Operator Overloading)

## 4.1 基本概念

**白話**：讓自訂的類別也能使用 `+`、`==`、`<<` 這些運算子，用起來跟內建型別一樣自然。

```cpp
Fraction a(1, 2), b(1, 3);
Fraction c = a + b;      // 比 Fraction c = a.add(b); 自然多了
```

運算子其實就是名字特別的函式：`a + b` 就是 `operator+(a, b)` 或 `a.operator+(b)`。

**規則**：
- 只能多載 **已存在** 的運算子，不能發明新的（例如 `**`）。
- **不能改變** 優先順序、結合性、運算元的個數。
- 不能多載：`::`、`.`、`.*`、`?:`、`sizeof`。
- **語意要符合直覺**：`+` 就該是「加」，不要拿來做奇怪的事。

## 4.2 成員函式 vs 非成員函式

```cpp
class Fraction {
public:
    Fraction operator+(const Fraction& o) const;   // 成員：左邊必須是 Fraction
};
Fraction operator+(const Fraction& a, const Fraction& b);   // 非成員：兩邊對等
```

差別在 **隱式轉換**（假設 `Fraction(long long)` 沒有 `explicit`）：

```cpp
Fraction f(1, 2);
f + 1;     // 兩種寫法都可以：1 被轉成 Fraction(1)
1 + f;     // 成員版本 ❌（1 不是 Fraction，沒有 operator+ 成員）；非成員版本 ✅
```

| 運算子 | 建議 |
|---|---|
| `=`、`[]`、`()`、`->` | **必須** 是成員 |
| `+=`、`-=`、`++`、`--` 等修改自己的 | 成員 |
| `+`、`-`、`==`、`<` 等對稱的二元運算子 | 非成員（兩邊都能轉換） |
| `<<`、`>>`（輸出入） | **必須** 是非成員（左邊是 `ostream`） |

## 4.3 該回傳什麼？

| 運算子 | 回傳 | 原因 |
|---|---|---|
| `a + b` | **新物件（傳值）** | 結果是新的值，`a`、`b` 都不變 |
| `a += b` | **`*this` 的參考** `T&` | 修改自己，回傳自己才能串接 `a += b += c` |
| `a = b` | `*this` 的參考 | 同上，`a = b = c` |
| `a == b`、`a < b` | `bool` | |
| `os << a` | `ostream&` | 才能串接 `cout << a << b` |
| `a[i]` | 元素的參考 `T&`（再寫一個 `const` 版本回傳 `const T&`） | 才能寫 `a[i] = x` |

**慣用寫法：用 `+=` 實作 `+`**，避免重複：

```cpp
class Fraction {
public:
    Fraction& operator+=(const Fraction& o) { /* 修改自己 */ return *this; }
};
Fraction operator+(Fraction a, const Fraction& b) {   // a 傳值 = 複製一份
    a += b;
    return a;
}
```

## 4.4 前置與後置 ++

```cpp
class Counter {
    int n_ = 0;
public:
    Counter& operator++() { ++n_; return *this; }         // 前置 ++c：回傳自己（左值）
    Counter operator++(int) {                              // 後置 c++：int 只是用來區分的假參數
        Counter old = *this;                               // 先存舊值
        ++n_;
        return old;                                        // 回傳舊值的複製品
    }
};
```

後置版本要複製一份舊值，這就是為什麼迭代器用 `++it` 比較好（第 02 課）。

## 4.5 輸出運算子

```cpp
ostream& operator<<(ostream& os, const Fraction& f) {
    os << f.num();
    if (f.den() != 1) os << '/' << f.den();
    return os;                  // 回傳 os 才能串接
}
cout << f << '\n';
```

## 4.6 🔍 比較運算子與 C++20 的 <=>

C++20 之前要寫 `==`、`!=`、`<`、`<=`、`>`、`>=` 六個。C++20 的 **三向比較運算子**（太空船運算子）`<=>` 可以一次產生全部：

```cpp
struct Version {
    int major, minor, patch;
    auto operator<=>(const Version&) const = default;   // 依成員順序逐一比較
};
```

## 4.7 轉換運算子

```cpp
class Fraction {
public:
    explicit operator double() const { return (double)num_ / den_; }
};
double d = static_cast<double>(f);   // 有 explicit 時要明確轉換
```

最常見的是 `explicit operator bool()`：讓物件可以用在 `if (obj)` 裡（例如 `if (cin)`、`if (ptr)`），但不會被意外當成整數相加。

---

# 第五部分：物件導向的四大概念

| 概念 | 英文 | 白話 | C++ 怎麼做 | 在哪一課 |
|---|---|---|---|---|
| 封裝 | Encapsulation | 把資料藏起來，只開放必要的操作 | `private` + 公開成員函式 | 本課 |
| 抽象 | Abstraction | 只關心「能做什麼」，不關心「怎麼做」 | 抽象類別、介面、ADT | 第 09 課 |
| 繼承 | Inheritance | 從現有類別延伸出新類別，重用並擴充 | `class B : public A` | 第 08 課 |
| 多型 | Polymorphism | 同一個介面，不同的實作，執行時決定 | 虛擬函式 | 第 08 課 |

**比喻**（以「交通工具」為例）：
- **封裝**：開車不用知道引擎怎麼運作，只要會用方向盤、油門、煞車。
- **抽象**：「交通工具」就是一個抽象概念 —— 能移動、能載人。
- **繼承**：汽車、機車都 **是一種** 交通工具，繼承了「能移動」的特性，再加上自己的特色。
- **多型**：叫每台交通工具「移動」，汽車用四個輪子跑，船在水上開，飛機在天上飛 —— 同一個指令，各自用自己的方式完成。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 類別 / 物件 | Class / Object | 設計圖 / 照設計圖做出來的東西 | 1.1 |
| 成員變數 / 成員函式 | Data Member / Member Function | 類別裡的資料 / 操作 | 1.1 |
| 存取控制 | Access Specifier | public / private / protected | 1.2 |
| 封裝 | Encapsulation | 資料藏起來，只開放操作 | 1.3 |
| 不變量 | Invariant | 物件永遠成立的條件 | 1.4 |
| 建構子 / 解構子 | Constructor / Destructor | 建立時 / 銷毀時自動呼叫 | 2.1、2.7 |
| 預設建構子 | Default Constructor | 不需要參數的建構子 | 2.2 |
| 成員初始化串列 | Member Initializer List | `: x_(x), y_(y)` | 2.3 |
| 委派建構子 | Delegating Constructor | 呼叫同類別的另一個建構子 | 2.5 |
| explicit | explicit | 禁止用這個建構子做隱式轉換 | 2.6 |
| this 指標 | this | 指向目前物件 | 3.1 |
| const 成員函式 | const Member Function | 承諾不修改物件 | 3.2 |
| 靜態成員 | static Member | 整個類別共用一份 | 3.3 |
| 朋友 | friend | 允許外部存取 private | 3.4 |
| 運算子多載 | Operator Overloading | 讓自訂型別也能用運算子 | 4.1 |
| 三向比較 | Three-way Comparison `<=>` | 一次定義所有比較，C++20 | 4.6 |
| 多型 | Polymorphism | 同一介面、不同實作 | 5 |

---

# 習題

### 題 1：預測輸出

```cpp
class A {
    int b_, a_;
public:
    A(int x) : a_(x), b_(a_ * 2) {}
    void show() const { cout << a_ << ' ' << b_; }
};
A obj(5); obj.show();
```

### 題 2：哪幾行會編譯錯誤？

```cpp
class Box {
    int w_;
public:
    explicit Box(int w) : w_(w) {}
    int width() { return w_; }
};
void show(const Box& b) { cout << b.width(); }   // ①
Box b1(3);                                        // ②
Box b2 = 3;                                       // ③
show(Box(4));                                     // ④
```

### 題 3：預測輸出

```cpp
class Obj {
public:
    static int alive;
    Obj() { alive++; }
    ~Obj() { alive--; }
};
int Obj::alive = 0;
int main() {
    Obj a;
    { Obj b, c; cout << Obj::alive; }
    Obj* p = new Obj;
    cout << Obj::alive;
    delete p;
    cout << Obj::alive;
}
```

### 題 4：預測輸出

```cpp
class Counter {
    int n_ = 0;
public:
    Counter& operator++() { ++n_; return *this; }
    Counter operator++(int) { Counter t = *this; ++n_; return t; }
    int get() const { return n_; }
};
Counter c;
Counter a = c++;
Counter b = ++c;
cout << a.get() << b.get() << c.get();
```

### 題 5：為什麼 `1 + f` 編譯失敗，`f + 1` 可以？怎麼讓兩個都能編譯？

```cpp
class Fraction {
public:
    Fraction(long long n, long long d = 1);
    Fraction operator+(const Fraction& o) const;
};
Fraction f(1, 2);
f + 1;
1 + f;
```

### 題 6：這個類別的設計有什麼問題？

```cpp
class Temperature {
public:
    double kelvin;    // 不能小於 0
};
```

### 題 7：`operator+=` 應該回傳 `Fraction`、`Fraction&` 還是 `void`？為什麼？

---

# 習題解答

**題 1**：`5` 和一個 **垃圾值**（實際輸出可能是 `5 0` 或其他）。成員依照 **宣告順序** 初始化：`b_` 先宣告，所以先執行 `b_(a_ * 2)`，這時 `a_` 還沒初始化。`-Wall` 會警告。

**題 2**：① 和 ③。
- ①：`width()` 不是 `const` 成員函式，不能對 `const Box&` 呼叫。改成 `int width() const`。
- ③：`Box b2 = 3;` 是複製初始化，需要隱式轉換，但建構子是 `explicit`。

**題 3**：`321`。`a` 建立 → 1；區塊裡建立 `b`、`c` → 3，印出 `3`；區塊結束 `b`、`c` 銷毀 → 1；`new` 一個 → 2，印出 `2`；`delete p` → 1，印出 `1`。

**題 4**：`022`。`c++` 回傳舊值（0）給 `a`，c 變成 1；`++c` 讓 c 變成 2，回傳 c 本身，`b` 複製到 2。

**題 5**：`operator+` 是 **成員函式**，左邊的運算元必須已經是 `Fraction`。`f + 1` 的 `1` 可以透過非 `explicit` 的建構子轉成 `Fraction`；但 `1 + f` 的左邊 `1` 是 `int`，不會為了呼叫成員函式而被轉換。改成 **非成員函式**：`Fraction operator+(const Fraction& a, const Fraction& b);`，兩邊都能轉換。

**題 6**：`kelvin` 是 `public`，任何人都可以設成負數，破壞「不小於 0」的 **不變量**。應該設成 `private`，透過建構子和成員函式（例如 `set_kelvin`、`add`）檢查並維持不變量，違反時丟出例外。

**題 7**：回傳 **`Fraction&`**（`*this`）。`+=` 修改的是自己，回傳自己的參考可以支援串接（`a += b += c`）和 `(a += b).method()`，也跟內建型別的行為一致。回傳 `Fraction`（傳值）會多一次複製，而且 `(a += b) += c` 會改到複製品而不是 `a`。
