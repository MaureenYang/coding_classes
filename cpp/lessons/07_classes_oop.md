# 07. 類別與物件導向 (Classes & OOP)

> 程式練習：`C07 分數類別`、`C09 銀行帳戶 ADT`
>
> 先備知識：第 04 課「函式」、第 05 課「參考」。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 類別與封裝 | 類別、物件、存取控制、封裝、不變量、成員函式寫在類別外 |
| 第二部分 | 建構子全攻略 | 各種建構子、成員初始化串列、初始化順序的陷阱、`explicit`、委派建構子、解構子 |
| 第三部分 | 成員的種類 | `this`、`const` 成員函式、`mutable`、`static` 成員、`friend`、巢狀型別 |
| 第四部分 | 運算子多載 | 每一種常用運算子的寫法：算術、複合指定、比較、輸出入、`[]`、`()`、`++`、轉換 |
| 第五部分 | 物件導向的四大概念 | 封裝、抽象、繼承、多型的整體地圖 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：類別與封裝

## 1.1 類別與物件 (Class / Object)

**是什麼**：
- **類別 (class)**：一種 **自訂的型別**，把「**資料**」和「**操作這些資料的函式**」包在一起。
- **物件 / 實例 (object / instance)**：用類別建立出來的一個具體的東西。
- **成員 (member)**：類別裡面的東西。資料叫 **成員變數 (data member)**，函式叫 **成員函式 (member function)**，也常被叫做 **方法 (method)**。

**比喻**：類別是 **設計圖**，物件是照著設計圖蓋出來的 **房子**。一張設計圖可以蓋很多間房子，每間房子有自己的家具（資料），但格局（結構和功能）都一樣。

**為什麼需要**：沒有類別的時候，資料和處理資料的函式是分開的：

```cpp
// 沒有類別：資料和函式散落各處
string owner;
long long balance = 0;
void deposit(long long& bal, long long amt) { bal += amt; }
deposit(balance, 100);
// 問題：要管理兩個帳戶，就要兩組變數；任何人都可以直接寫 balance = -999;
```

用類別把它們綁在一起：

```cpp
class Account {
private:
    string owner_;                 // 成員變數
    long long balance_ = 0;
public:
    Account(string owner) : owner_(owner) {}             // 建構子（第二部分）
    void deposit(long long amt) { balance_ += amt; }     // 成員函式
    long long balance() const { return balance_; }
    string owner() const { return owner_; }
};

Account a("amy"), b("bob");       // 兩個物件，各自有自己的 owner_ 和 balance_
a.deposit(100);                   // 用「.」呼叫成員函式：只改 a 的
b.deposit(30);
b.deposit(20);
cout << a.owner() << ' ' << a.balance() << '\n';   // 輸出：amy 100
cout << b.owner() << ' ' << b.balance() << '\n';   // 輸出：bob 50
```

透過指標存取成員用 `->`：

```cpp
Account* p = &a;
p->deposit(5);                    // 等於 (*p).deposit(5)
cout << p->balance() << '\n';     // 輸出：105
```

**命名慣例**：本課的私有成員變數後面加底線（`balance_`），一眼就能分出「成員」和「參數 / 區域變數」。也有人用 `m_balance` 的寫法，選一種一致就好。

## 1.2 成員函式寫在類別外面

**是什麼**：成員函式可以在類別裡只寫 **宣告**，**定義** 寫在外面，用 `類別名::函式名` 表示「這是哪個類別的函式」。`::` 叫做 **範圍解析運算子 (scope resolution operator)**。

**為什麼需要**：類別定義只放宣告，看起來就是一份清楚的「介面說明」；大專案裡宣告放 `.h`、定義放 `.cpp`（第 14 課）。

```cpp
class Rect {
    int w_, h_;
public:
    Rect(int w, int h);              // 只有宣告
    int area() const;
    void scale(int k);
};

Rect::Rect(int w, int h) : w_(w), h_(h) {}             // 建構子的定義
int Rect::area() const { return w_ * h_; }             // 注意 const 也要寫
void Rect::scale(int k) { w_ *= k; h_ *= k; }

Rect r(3, 4);
r.scale(2);
cout << r.area() << '\n';            // 輸出：48
```

**常見錯誤**：
- 忘了寫 `Rect::` → 變成定義了一個「普通的全域函式 `area`」，它看不到 `w_`、`h_`，編譯錯誤 `'w_' was not declared in this scope`。
- 宣告有 `const`、定義沒寫 → 編譯器認為是兩個不同的函式，錯誤 `no declaration matches`。

🔍 寫在類別 **裡面** 的成員函式自動是 `inline`（第 14 課），放在標頭檔被多個 `.cpp` include 也不會重複定義；寫在 **外面** 又放在標頭檔的話，要自己加 `inline`。

## 1.3 存取控制 (Access Specifiers)

| 關鍵字 | 誰可以存取 | 比喻 |
|---|---|---|
| `public` | 所有人 | 店面的櫃台：誰都可以來 |
| `private` | 只有這個類別自己的成員函式（和 `friend`） | 老闆的保險箱 |
| `protected` | 自己 + 子類別（第 08 課） | 家族成員才能進的後台 |

```cpp
class Safe {
    int secret_ = 42;             // class 預設是 private
public:
    int peek() const { return secret_; }   // 自己的成員函式可以存取 private
private:
    void reset() { secret_ = 0; }          // private 成員函式：只能在類別內部使用
};

Safe s;
cout << s.peek() << '\n';         // ✅ 輸出：42
// s.secret_ = 0;                 // ❌ error: 'int Safe::secret_' is private within this context
// s.reset();                     // ❌ error: 'void Safe::reset()' is private within this context
```

🔍 **存取控制是「以類別為單位」，不是以物件為單位**：同一個類別的成員函式，可以存取 **另一個同類物件** 的 `private` 成員。

```cpp
class Money {
    long long cents_;
public:
    Money(long long c) : cents_(c) {}
    bool richer_than(const Money& other) const {
        return cents_ > other.cents_;      // ✅ 可以直接讀 other 的 private 成員
    }
};
cout << Money(500).richer_than(Money(300)) << '\n';   // 輸出：1
```

### class vs struct

**唯一的差別是預設的存取權限**：`class` 預設 `private`，`struct` 預設 `public`（繼承的預設也一樣，第 08 課）。

```cpp
struct P { int x; };      // x 是 public
class Q { int x; };       // x 是 private
P p; p.x = 1;             // ✅
Q q; // q.x = 1;          // ❌ private
```

**慣例**：
- 單純的資料包、**沒有不變量**（每個欄位都可以是任何值）→ 用 `struct`，例如 `struct Point { int x, y; };`。
- 有 **不變量要保護** → 用 `class`，資料設成 `private`。

## 1.4 封裝 (Encapsulation)

**是什麼**：把資料 **藏起來**（`private`），只透過 **公開的成員函式** 讓外界操作。

**比喻**：自動販賣機。你只能投錢、按按鈕（公開介面），不能直接打開機器拿飲料或改裡面的價格（私有資料）。

**為什麼需要**：有兩個好處。

**好處 1：保護資料，讓它永遠合法**（下一節的不變量）。

**好處 2：可以修改內部實作，而不影響使用者**。

```cpp
// 版本 1：用「元」存餘額
class Wallet {
    double yuan_ = 0;
public:
    void add(double y) { yuan_ += y; }
    double total() const { return yuan_; }
};

// 版本 2：發現 double 有誤差，改成用「分」存（整數）
class Wallet2 {
    long long cents_ = 0;
public:
    void add(double y) { cents_ += llround(y * 100); }
    double total() const { return cents_ / 100.0; }
};
// 使用者的程式碼 w.add(0.1); w.total(); 完全不用改！
```

如果資料是 `public`，使用者會直接寫 `w.yuan_ += 0.1;`，內部改成 `cents_` 之後，**所有使用者的程式都要改**。

```cpp
Wallet w1; Wallet2 w2;
for (int i = 0; i < 10; i++) { w1.add(0.1); w2.add(0.1); }
cout << (w1.total() == 1.0) << ' ' << (w2.total() == 1.0) << '\n';   // 輸出：0 1
```

（0.1 加十次用 `double` 不會剛好等於 1.0，第 01 課浮點數誤差。改成用整數的「分」存，結果就精確了，而使用者程式一行都不用改。）

## 1.5 不變量 (Invariant)

**是什麼**：一個物件 **在任何時候都應該成立** 的條件。

例子：
- `Fraction`（`C07`）：分母永遠是正的，而且分子分母互質（最簡分數）。
- `Account`（`C09`）：餘額永遠 ≥ 0。
- `vector`：`size() <= capacity()`。
- 日期：月份在 1 ~ 12、日期不超過那個月的天數。

**為什麼需要**：如果資料是 `public`，任何人都可以寫 `f.den_ = 0;` 破壞不變量。設成 `private` 之後，只有類別自己的函式能修改，所以：

> **只要「建構子建立不變量」並且「每個公開的成員函式都維持不變量」，不變量就永遠成立。**

使用這個類別的人，再也不用檢查「分母是不是 0」「是不是最簡分數」。

### 例 1：建構子建立不變量

```cpp
class Fraction {
    long long num_, den_;
    void normalize() {                         // private 輔助函式
        if (den_ == 0) throw invalid_argument("denominator is zero");
        if (den_ < 0) { num_ = -num_; den_ = -den_; }   // 分母變成正的
        long long g = gcd(num_ < 0 ? -num_ : num_, den_);
        if (g) { num_ /= g; den_ /= g; }       // 約分
    }
public:
    Fraction(long long n, long long d) : num_(n), den_(d) { normalize(); }
    long long num() const { return num_; }
    long long den() const { return den_; }
};

Fraction f(6, -8);
cout << f.num() << '/' << f.den() << '\n';     // 輸出：-3/4（負號移到分子、約分）
Fraction g(0, 5);
cout << g.num() << '/' << g.den() << '\n';     // 輸出：0/1
try {
    Fraction bad(1, 0);
} catch (const invalid_argument& e) {
    cout << "錯誤：" << e.what() << '\n';      // 輸出：錯誤：denominator is zero
}
```

### 例 2：每個操作都維持不變量

```cpp
class SavingAccount {
    long long balance_ = 0;                    // 不變量：balance_ >= 0
public:
    void deposit(long long amt) {
        if (amt <= 0) throw invalid_argument("amount must be positive");
        balance_ += amt;
    }
    bool withdraw(long long amt) {
        if (amt <= 0 || amt > balance_) return false;   // 會破壞不變量 → 拒絕
        balance_ -= amt;
        return true;
    }
    long long balance() const { return balance_; }
};

SavingAccount acc;
acc.deposit(100);
cout << acc.withdraw(30) << ' ' << acc.balance() << '\n';    // 輸出：1 70
cout << acc.withdraw(500) << ' ' << acc.balance() << '\n';   // 輸出：0 70（拒絕，餘額不變）
```

**怎麼處理「會破壞不變量的要求」？** 兩種常見做法：
- **回傳 `bool` 或錯誤碼**：失敗是「正常會發生的事」時（例如餘額不足）。
- **丟出例外**：失敗代表「呼叫者寫錯了」時（例如存負數、分母是 0）。第 13 課詳談。

### 🔍 getter / setter 的迷思

替每個成員都寫 `getX()` / `setX()`，其實 **等於沒有封裝**：

```cpp
class BadAccount {
    long long balance_;
public:
    long long getBalance() const { return balance_; }
    void setBalance(long long b) { balance_ = b; }   // 任何人都能設成 -999，跟 public 沒兩樣
};
```

好的介面提供 **有意義的操作**（`deposit`、`withdraw`，裡面會檢查），而不是暴露資料本身（`setBalance`）。

**判斷方法**：想一下「使用者想做什麼事？」（存錢、提款），而不是「物件裡有什麼資料？」（餘額）。

---

# 第二部分：建構子全攻略

## 2.1 建構子 (Constructor)

**是什麼**：物件 **被建立時自動呼叫** 的特殊成員函式。
- 名稱和類別 **相同**。
- **沒有回傳型別**（連 `void` 都不寫）。
- 可以 **多載**（好幾個參數列不同的建構子）。

**為什麼需要**：讓物件一出生就處於 **合法的初始狀態**（建立不變量）。沒有建構子的話，使用者可能忘記初始化。

```cpp
class Point {
    int x_, y_;
public:
    Point() : x_(0), y_(0)                { cout << "Point()\n"; }
    Point(int x, int y) : x_(x), y_(y)    { cout << "Point(int, int)\n"; }
    Point(int v) : x_(v), y_(v)           { cout << "Point(int)\n"; }
    void print() const { cout << '(' << x_ << ", " << y_ << ")\n"; }
};

Point a;            // 輸出：Point()
Point b(1, 2);      // 輸出：Point(int, int)
Point c{3, 4};      // 輸出：Point(int, int)（大括號初始化，C++11）
Point d(7);         // 輸出：Point(int)
Point e = 8;        // 輸出：Point(int)（複製初始化：隱式轉換，見 2.6）
b.print();          // 輸出：(1, 2)
d.print();          // 輸出：(7, 7)
```

### 建立物件的各種寫法

| 寫法 | 名稱 | 說明 |
|---|---|---|
| `Point a;` | 預設初始化 | 呼叫預設建構子 |
| `Point a{};` | 值初始化 | 有預設建構子就呼叫它；沒有自訂建構子的話，成員設成 0 |
| `Point a(1, 2);` | 直接初始化 | 呼叫對應的建構子 |
| `Point a{1, 2};` | 列表初始化 | 同上，但 **禁止窄化轉換**（第 01 課） |
| `Point a = 8;` | 複製初始化 | 需要隱式轉換，`explicit` 建構子不能用 |
| `Point a = {1, 2};` | 複製列表初始化 | 同上 |
| `auto p = new Point(1, 2);` | 動態配置 | 在 heap 上建立（第 06 課） |

**🔍 最惱人的解析 (most vexing parse)**：

```cpp
Point a();          // ⚠️ 這不是建立物件！這是「宣告一個叫 a、沒有參數、回傳 Point 的函式」
Point b{};          // ✅ 用大括號就不會有這個問題
```

## 2.2 預設建構子 (Default Constructor)

**是什麼**：**不需要任何參數** 就能呼叫的建構子（沒有參數，或所有參數都有預設值）。

**什麼時候需要它**：`Point a;`、`Point arr[10];`、`vector<Point> v(10);` 都需要預設建構子。

### 規則 1：完全沒寫建構子 → 編譯器自動產生一個

```cpp
class A { public: int x; string s; };
A a;              // ✅ 編譯器產生的預設建構子：s 是空字串，但 a.x 是垃圾值！
A b{};            // ✅ 值初始化：b.x 是 0
cout << b.x << " [" << b.s << "]\n";   // 輸出：0 []
```

編譯器產生的預設建構子 **不會初始化 `int`、`double`、指標這些內建型別**（跟區域變數一樣，第 01 課），但會呼叫 `string`、`vector` 等類別成員的預設建構子。

### 規則 2：自己寫了任何一個建構子 → 編譯器 **不再** 自動產生

```cpp
class B { public: B(int v) {} };
// B b;           // ❌ error: no matching function for call to 'B::B()'
// B arr[3];      // ❌ 同樣的錯誤
// vector<B> v(3);// ❌ 同樣的錯誤
B ok(5);          // ✅
```

### 規則 3：用 `= default` 要回來

```cpp
class C {
public:
    C() = default;          // 「請幫我產生預設版本」
    C(int v) : x(v) {}
    int x = -1;
};
C c1;                       // ✅ x 用預設成員初始值 -1
C c2(9);
cout << c1.x << ' ' << c2.x << '\n';   // 輸出：-1 9
```

### 預設成員初始值 (Default Member Initializer)

**是什麼**：直接在成員宣告時給初值。每個建構子如果 **沒有在初始化串列裡另外指定**，就用這個值。

```cpp
class Counter {
    int count_ = 0;
    string name_ = "unnamed";
    vector<int> history_;            // 沒寫初值：用 vector 的預設建構子（空的）
public:
    Counter() {}                                   // 全部用預設初始值
    Counter(string n) : name_(n) {}                // name_ 用參數；count_ 仍然是 0
    void show() const { cout << name_ << ':' << count_ << '\n'; }
};
Counter().show();                // 輸出：unnamed:0
Counter("clicks").show();        // 輸出：clicks:0
```

**建議**：**每個內建型別的成員都給一個預設初值**，就永遠不會有垃圾值。

## 2.3 成員初始化串列 (Member Initializer List)

**是什麼**：建構子參數列後面、本體 `{` 前面，用冒號開頭的那一段：

```cpp
class Point {
    int x_, y_;
public:
    Point(int x, int y) : x_(x), y_(y) {}   // ← 「: x_(x), y_(y)」就是初始化串列
};
```

### 和「在本體裡賦值」的差別

```cpp
Point(int x, int y) { x_ = x; y_ = y; }   // 先「預設初始化」成員，進入本體後再「賦值」
```

成員在 **進入建構子本體之前** 就已經被建立好了。寫在本體裡的是「**建立好之後再改值**」，不是初始化。用一個會印出動作的類別觀察：

```cpp
struct Loud {
    Loud()                     { cout << "  預設建構\n"; }
    Loud(int)                  { cout << "  用 int 建構\n"; }
    Loud& operator=(int)       { cout << "  賦值\n"; return *this; }
};
struct UseList  { Loud m; UseList()  : m(5) {} };
struct UseBody  { Loud m; UseBody()  { m = 5; } };

cout << "初始化串列：\n";  UseList x;
cout << "本體賦值：\n";    UseBody y;
// 輸出：
// 初始化串列：
//   用 int 建構
// 本體賦值：
//   預設建構
//   賦值
```

本體賦值多做了一次預設建構。對 `int` 沒差，對 `string`、`vector` 就是白白浪費。

**比喻**：初始化串列是「**出廠時就裝好零件**」；在本體裡賦值是「先裝一個預設零件，出廠後再拆下來換」。

### 一定要用初始化串列的四種情況

**情況 1：`const` 成員** —— 建立之後就不能再賦值。

```cpp
class Circle {
    const double radius_;
public:
    Circle(double r) : radius_(r) {}          // ✅
    // Circle(double r) { radius_ = r; }      // ❌ error: assignment of read-only member
    double area() const { return 3.14 * radius_ * radius_; }
};
cout << Circle(2).area() << '\n';             // 輸出：12.56
```

**情況 2：參考成員** —— 參考一定要在建立時綁定（第 05 課）。

```cpp
class Logger {
    ostream& out_;
public:
    Logger(ostream& o) : out_(o) {}           // ✅ 參考成員只能這樣綁定
    void log(const string& s) { out_ << "[log] " << s << '\n'; }
};
Logger lg(cout);
lg.log("hello");                              // 輸出：[log] hello
```

**情況 3：成員的型別沒有預設建構子**

```cpp
class Engine { public: Engine(int hp) : hp_(hp) {} int hp_; };
class Car {
    Engine engine_;
public:
    Car() : engine_(150) {}                   // ✅
    // Car() { engine_ = Engine(150); }       // ❌ error: no matching function for call to 'Engine::Engine()'
    int hp() const { return engine_.hp_; }
};
cout << Car().hp() << '\n';                   // 輸出：150
```

**情況 4：基底類別的建構子需要參數**（第 08 課）。

### 參數和成員同名

```cpp
class Pt {
    int x, y;
public:
    Pt(int x, int y) : x(x), y(y) {}   // ✅ 合法：括號外的 x 是成員，括號內的 x 是參數
    int sum() const { return x + y; }
};
cout << Pt(3, 4).sum() << '\n';        // 輸出：7
```

這是合法的，但容易混淆；用 `x_` 這種命名就不會有問題。**在本體裡** 同名就要寫 `this->x = x;`（3.1）。

## 2.4 🔍 初始化順序的陷阱

**規則：成員的初始化順序是「在類別裡宣告的順序」，不是初始化串列裡寫的順序！**

```cpp
struct Tag {
    Tag(const char* s) { cout << s << ' '; }
};
struct Order {
    Tag a, b, c;                                      // 宣告順序：a, b, c
    Order() : c("c"), b("b"), a("a") {}               // 串列寫的順序：c, b, a
};
Order o;
cout << '\n';                                         // 輸出：a b c（按照宣告順序！）
```

**陷阱**：成員之間有依賴時就會出錯。

```cpp
class Range {
    int size_;        // 先宣告 → 先初始化
    int end_;
    int begin_;
public:
    Range(int b, int e) : begin_(b), end_(e), size_(end_ - begin_) {}
    // 實際順序：size_ 先初始化，這時 end_ 和 begin_ 都還沒初始化 → size_ 是垃圾值！
};
```

`-Wall` 會警告：`'Range::begin_' will be initialized after 'int Range::size_'`。

**修法**（任一種）：
1. 調整宣告順序，讓被依賴的成員先宣告。
2. 不要讓成員互相依賴：`size_(e - b)` 直接用 **參數** 計算。

**規則：初始化串列的順序寫得跟宣告順序一樣，並且盡量不要讓成員互相依賴。**

## 2.5 委派建構子 (Delegating Constructor)

**是什麼**：一個建構子在初始化串列裡 **呼叫同一個類別的另一個建構子**。

**為什麼需要**：好幾個建構子做的事情差不多時，把共同的邏輯寫在一個地方，避免重複（重複的程式碼改一處忘一處就會出 bug）。

```cpp
class Frac {
    long long n_, d_;
public:
    Frac(long long n, long long d) : n_(n), d_(d) {
        cout << "主建構子 " << n_ << '/' << d_ << '\n';
        // ……檢查分母、約分等共同邏輯只寫在這裡
    }
    Frac(long long n) : Frac(n, 1) { cout << "  整數版\n"; }   // 委派給主建構子
    Frac() : Frac(0) { cout << "  預設版\n"; }                 // 委派給整數版
};

Frac a(3, 4);
// 輸出：
// 主建構子 3/4
Frac b;
// 輸出：
// 主建構子 0/1
//   整數版
//   預設版
```

**執行順序**：先完整執行被委派的建構子（包含它的本體），再執行自己的本體。

**限制**：委派建構子的初始化串列裡 **只能有** 那一個委派呼叫，不能再初始化其他成員：

```cpp
// Frac(long long n) : Frac(n, 1), n_(n) {}   // ❌ error: mem-initializer for 'Frac::n_' follows constructor delegation
```

**另一個選擇：預設引數**

```cpp
Frac(long long n = 0, long long d = 1);   // 一個建構子就能處理 Frac()、Frac(5)、Frac(3, 4)
```

## 2.6 explicit：禁止隱式轉換

**是什麼**：可以 **只用一個引數呼叫** 的建構子，叫做 **轉換建構子 (converting constructor)**：編譯器會在需要時，**自動** 用它把那個引數轉成這個類別。加上 `explicit` 就禁止這種自動轉換。

**為什麼需要**：自動轉換有時候很方便，有時候會造成意外。

```cpp
class Buffer {
public:
    Buffer(int size) { cout << "建立大小 " << size << " 的 Buffer\n"; }
};
void send(const Buffer& b) { cout << "送出\n"; }

send(42);
// 輸出：
// 建立大小 42 的 Buffer     😱 本來可能只是想送數字 42，結果編譯器自動幫你建了一個 Buffer
// 送出
```

加上 `explicit`：

```cpp
class SafeBuffer {
public:
    explicit SafeBuffer(int size) { cout << "SafeBuffer " << size << '\n'; }
};
void send2(const SafeBuffer& b) { }

// send2(42);                 // ❌ error: invalid initialization of reference of type 'const SafeBuffer&'
send2(SafeBuffer(42));        // ✅ 必須明確寫出來 → 輸出：SafeBuffer 42
SafeBuffer s1(10);            // ✅ 直接初始化可以 → 輸出：SafeBuffer 10
// SafeBuffer s2 = 10;        // ❌ 複製初始化需要隱式轉換
SafeBuffer s3{10};            // ✅ → 輸出：SafeBuffer 10
```

**`explicit` 影響的情況整理**：

| 寫法 | 沒有 `explicit` | 有 `explicit` |
|---|---|---|
| `T x(10);` / `T x{10};` | ✅ | ✅ |
| `T x = 10;` | ✅ | ❌ |
| `f(10);`（`f` 的參數是 `T` 或 `const T&`） | ✅ 自動轉換 | ❌ |
| `return 10;`（函式回傳 `T`） | ✅ | ❌ |
| `T x = {10};` | ✅ | ❌ |

**比喻**：沒有 `explicit` 就像餐廳服務生「自動幫你升級套餐」；有 `explicit` 則是「要升級請自己說」。

**什麼時候 *不* 加 `explicit`？** 當「自動轉換」在語意上完全合理時。例如 `Fraction(long long n)`：整數 5 本來就是分數 5/1，讓 `f + 5` 能運作是有意的設計。`std::string` 能從 `"hello"` 自動轉換也是同樣的道理。

**規則**：單一引數的建構子 **預設加上 `explicit`**，除非你確定想要自動轉換。

**常見錯誤：`vector<int> v = 10;`** —— `vector` 的「大小」建構子是 `explicit` 的，所以這行編譯失敗（正是為了避免意外）。

## 2.7 解構子 (Destructor)

**是什麼**：物件 **被銷毀時自動呼叫** 的成員函式，寫成 `~類別名()`。
- 沒有參數、沒有回傳值、**不能多載**（一個類別只有一個）。
- 沒寫的話，編譯器會自動產生一個（會依序銷毀每個成員）。

**為什麼需要**：釋放物件持有的資源（記憶體、檔案、鎖），這就是第 06 課的 RAII。

### 什麼時候會被呼叫？

| 物件種類 | 何時銷毀 |
|---|---|
| 區域變數 | 離開它所在的區塊 `}`（包含 `return`、`break`、例外） |
| `new` 出來的物件 | `delete` 的時候 |
| 暫時物件 | 那一整個運算式（到分號）結束時 |
| 全域變數、`static` 變數 | 程式結束時（`main` 結束之後） |
| 成員 | 擁有它的物件被銷毀時（在擁有者的解構子本體之後） |
| 容器裡的元素 | 從容器移除、或容器被銷毀時 |

```cpp
struct Noisy {
    string n;
    Noisy(string s) : n(s) { cout << "建立 " << n << '\n'; }
    ~Noisy() { cout << "銷毀 " << n << '\n'; }
};
Noisy global_obj("global");               // 全域：main 之前建立，main 之後銷毀

int main() {
    cout << "main 開始\n";
    Noisy a("a");
    {
        Noisy b("b");
    }                                     // b 在這裡銷毀
    Noisy* p = new Noisy("heap");
    Noisy("temp");                        // 暫時物件：這一行結束就銷毀
    delete p;                             // heap 物件在 delete 時銷毀
    static Noisy s("static");             // static：程式結束時銷毀
    cout << "main 結束\n";
}                                         // a 在這裡銷毀
// 輸出：
// 建立 global
// main 開始
// 建立 a
// 建立 b
// 銷毀 b
// 建立 heap
// 建立 temp
// 銷毀 temp
// 銷毀 heap
// 建立 static
// main 結束
// 銷毀 a
// 銷毀 static
// 銷毀 global
```

**常見錯誤**：
- 自己呼叫解構子 `a.~Noisy();` → 離開區塊時又會自動呼叫一次 → 銷毀兩次（未定義行為）。**不要自己呼叫解構子**。
- 解構子丟出例外 → 預設會直接呼叫 `std::terminate` 讓程式終止（第 13 課）。**解構子不要丟例外**。

## 2.8 🔍 聚合 (Aggregate) 與指定初始化

**是什麼**：沒有自訂建構子、沒有 `private` 資料、沒有虛擬函式的簡單 `struct`，叫做 **聚合 (aggregate)**。可以直接用大括號依照成員順序初始化。

```cpp
struct Student {
    string name;
    int age;
    double gpa = 0.0;              // 可以有預設成員初始值
};
Student s1{"amy", 20, 3.8};
Student s2{"bob", 21};             // 少給的用預設值（gpa = 0.0）
Student s3{};                      // 全部值初始化："" 0 0.0
cout << s1.name << ' ' << s2.gpa << ' ' << s3.age << '\n';   // 輸出：amy 0 0
```

C++20 還可以寫 **指定初始化 (designated initializer)**，指名欄位（順序要跟宣告一樣）：

```cpp
Student s4{.name = "cat", .gpa = 3.5};   // C++20：age 用值初始化 = 0
```

---

# 第三部分：成員的種類

## 3.1 this 指標

**是什麼**：在成員函式裡，`this` 是 **指向「呼叫這個函式的那個物件」** 的指標。型別是 `類別名*`（在 `const` 成員函式裡是 `const 類別名*`）。

🔍 **成員函式的本質**：`a.deposit(10)` 在底層大約等於 `Account::deposit(&a, 10)`，`this` 就是那個 **隱藏的第一個參數**。所以同一個 `deposit` 函式，被 `a` 呼叫時改 `a` 的餘額，被 `b` 呼叫時改 `b` 的。

```cpp
struct Who {
    void show() { cout << (this == &w1 ? "w1" : "w2") << '\n'; }
    static Who w1, w2;
};
Who Who::w1, Who::w2;
Who::w1.show();    // 輸出：w1
Who::w2.show();    // 輸出：w2
```

### 用途 1：參數和成員同名時區分

```cpp
class Person {
    string name;
public:
    void set_name(const string& name) {
        this->name = name;      // this->name 是成員，name 是參數
        // name = name;         // ❌ 兩個都是參數：自己指定給自己，成員沒變！（-Wall 不一定警告）
    }
    string get() const { return name; }
};
Person p; p.set_name("amy");
cout << p.get() << '\n';        // 輸出：amy
```

### 用途 2：回傳自己，讓呼叫可以串接 (method chaining)

```cpp
class Builder {
    string s_;
public:
    Builder& add(const string& x) { s_ += x; return *this; }   // 回傳自己的參考
    Builder& space() { s_ += ' '; return *this; }
    string build() const { return s_; }
};
cout << Builder().add("hello").space().add("world").build() << '\n';   // 輸出：hello world
```

**注意回傳型別一定要是參考 `Builder&`**。如果寫成 `Builder`（傳值），每次都回傳一個 **複製品**，後面的呼叫改的是複製品：

```cpp
class BadBuilder {
public:
    string s_;
    BadBuilder add(const string& x) { s_ += x; return *this; }   // ❌ 回傳複製品
};
BadBuilder b;
b.add("a").add("b");            // 第二個 add 改到的是第一個 add 回傳的暫時複製品
cout << b.s_ << '\n';           // 輸出：a
```

### 用途 3：檢查是不是同一個物件（自我指定，第 06 課）

```cpp
if (this == &other) return *this;
```

## 3.2 const 成員函式

**是什麼**：在參數列後面加 `const`，承諾「**這個函式不會修改物件的任何成員**」。編譯器會檢查：在 `const` 成員函式裡修改成員就編譯錯誤。

```cpp
class Account {
    long long balance_ = 0;
public:
    long long balance() const { return balance_; }      // 只讀取 → 標 const
    void deposit(long long amt) { balance_ += amt; }    // 會修改 → 不能標 const
    // void bad() const { balance_ = 0; }               // ❌ error: assignment of member 'Account::balance_' in read-only object
};
```

**為什麼需要**：`const` 物件（和 `const` 參考）**只能呼叫 `const` 成員函式**。而函式參數幾乎都用 `const T&` 傳遞（第 04 課），所以忘記標 `const` 會導致一堆函式無法使用：

```cpp
void print(const Account& a) {
    cout << a.balance() << '\n';    // a 是 const 參考 → balance() 必須是 const，否則編譯錯誤
}

const Account c;
c.balance();                        // ✅
// c.deposit(5);                    // ❌ error: passing 'const Account' as 'this' argument discards qualifiers
```

那個錯誤訊息 `passing 'const X' as 'this' argument discards qualifiers` 就是「你對 const 物件呼叫了非 const 成員函式」的意思，**看到它就去檢查是不是忘了標 `const`**。

**規則：不會修改物件的成員函式，一律加 `const`。**

### const 多載：同一個函式的 const 版本與非 const 版本

`const` 也是函式簽名的一部分，所以可以多載。最常見的是 `operator[]`：

```cpp
class IntList {
    vector<int> v_{10, 20, 30};
public:
    int& operator[](size_t i)             { cout << "(非 const) "; return v_[i]; }
    const int& operator[](size_t i) const { cout << "(const) ";    return v_[i]; }
};

IntList a;
a[0] = 99;                     // 非 const 物件 → 呼叫非 const 版本，回傳 int& 可以修改
cout << a[0] << '\n';          // 輸出：(非 const) (非 const) 99
const IntList b;
cout << b[1] << '\n';          // 輸出：(const) 20
// b[1] = 5;                   // ❌ const 版本回傳 const int&，不能修改
```

`vector`、`string`、`map::at` 都是這樣設計的。

### mutable：const 函式裡也可以改的成員

**是什麼**：標成 `mutable` 的成員，即使在 `const` 成員函式裡也可以修改。

**什麼時候用**：這個成員 **不屬於物件的「邏輯狀態」**，例如快取、統計呼叫次數。從使用者的角度看，物件沒有被改變。

```cpp
class Report {
    vector<int> data_;
    mutable long long cached_sum_ = -1;     // 快取：-1 代表還沒算過
    mutable int compute_count_ = 0;         // 統計真的計算了幾次
public:
    Report(vector<int> d) : data_(d) {}
    long long sum() const {                 // 邏輯上是「讀取」，所以標 const
        if (cached_sum_ < 0) {
            compute_count_++;
            cached_sum_ = 0;
            for (int x : data_) cached_sum_ += x;
        }
        return cached_sum_;
    }
    int computed() const { return compute_count_; }
};

const Report r({1, 2, 3, 4});
cout << r.sum() << ' ' << r.sum() << ' ' << r.sum() << '\n';   // 輸出：10 10 10
cout << r.computed() << '\n';                                  // 輸出：1（只真正算了一次）
```

## 3.3 static 成員

**是什麼**：屬於 **整個類別**，而不是屬於某個物件。所有物件 **共用同一份**。

**比喻**：班上每個同學有自己的座號（一般成員），但「全班人數」只有一個，寫在教室門口（static 成員）。

### static 成員變數

```cpp
class Student {
    string name_;
    static int count_;                      // 宣告：所有 Student 共用這一份
public:
    Student(string n) : name_(n) { count_++; }
    ~Student() { count_--; }
    static int count() { return count_; }   // static 成員函式
};
int Student::count_ = 0;                    // 定義（在類別外，而且只能定義一次）

cout << Student::count() << '\n';           // 輸出：0（不需要任何物件就能呼叫）
Student a("amy");
{
    Student b("bob"), c("cat");
    cout << Student::count() << '\n';       // 輸出：3
}
cout << Student::count() << '\n';           // 輸出：1（b、c 被銷毀了）
cout << a.count() << '\n';                  // 輸出：1（也可以透過物件呼叫，但不建議，容易誤會）
```

**C++17 的簡化寫法**：`inline static` 可以直接在類別裡定義，不用另外寫在外面。

```cpp
class Config {
public:
    inline static int verbose = 0;                  // C++17
    static constexpr int MAX_USERS = 100;           // 常數：constexpr static 也可以直接寫在類別裡
};
Config::verbose = 2;
cout << Config::verbose << ' ' << Config::MAX_USERS << '\n';   // 輸出：2 100
```

**常見錯誤**：C++17 之前只宣告 `static int count_;` 而忘了在類別外定義 → **連結錯誤** `undefined reference to 'Student::count_'`（第 14 課）。

### static 成員函式

**是什麼**：**沒有 `this`** 的成員函式。因為沒有 `this`，所以 **不能存取一般的（非 static）成員**，只能存取 static 成員。

```cpp
class Temperature {
    double celsius_;
    explicit Temperature(double c) : celsius_(c) {}    // 建構子設成 private
public:
    // 具名建構函式 (named constructor)：用名字說清楚單位
    static Temperature from_celsius(double c)    { return Temperature(c); }
    static Temperature from_fahrenheit(double f) { return Temperature((f - 32) * 5 / 9); }
    double celsius() const { return celsius_; }
    // static void bad() { cout << celsius_; }  // ❌ error: invalid use of member 'celsius_' in static member function
};

auto t1 = Temperature::from_celsius(100);
auto t2 = Temperature::from_fahrenheit(212);
cout << t1.celsius() << ' ' << t2.celsius() << '\n';   // 輸出：100 100
```

**常見用途**：
- 計數器、全域設定（如上）。
- **具名建構函式 / 工廠函式**：`Temperature::from_fahrenheit(212)` 比 `Temperature(212, true)` 清楚得多。
- 跟類別相關、但不需要某個特定物件的工具函式。

🔍 **函式裡的 `static` 區域變數**（第 04 課）和 **類別的 `static` 成員** 是同一個關鍵字、不同的用途：前者是「離開函式不會消失的變數」，後者是「全類別共用的成員」。

## 3.4 friend

**是什麼**：讓 **某個外部函式或類別** 可以存取這個類別的 `private` 成員。

**比喻**：把家裡的鑰匙給 **特定的好朋友**，他可以直接進來，其他人不行。

### friend 函式

```cpp
class Vec2 {
    double x_, y_;
public:
    Vec2(double x, double y) : x_(x), y_(y) {}
    friend double dot(const Vec2& a, const Vec2& b);            // 宣告 dot 是朋友
    friend ostream& operator<<(ostream& os, const Vec2& v);     // 輸出運算子常常是 friend
};
double dot(const Vec2& a, const Vec2& b) {           // 不是成員函式（沒有 Vec2::）
    return a.x_ * b.x_ + a.y_ * b.y_;                // 但可以存取 private 的 x_、y_
}
ostream& operator<<(ostream& os, const Vec2& v) {
    return os << '(' << v.x_ << ", " << v.y_ << ')';
}

Vec2 a(1, 2), b(3, 4);
cout << dot(a, b) << ' ' << a << '\n';               // 輸出：11 (1, 2)
```

### friend 類別

```cpp
class Engine {
    int rpm_ = 0;
    friend class Mechanic;           // Mechanic 的所有成員函式都可以存取 Engine 的 private
};
class Mechanic {
public:
    void tune(Engine& e) { e.rpm_ = 3000; }
    int check(const Engine& e) { return e.rpm_; }
};
Engine e; Mechanic m;
m.tune(e);
cout << m.check(e) << '\n';          // 輸出：3000
```

**friend 的特性**：
- **單向**：`Engine` 說 `Mechanic` 是朋友，不代表 `Mechanic` 把 `Engine` 當朋友。
- **不會傳遞**：朋友的朋友不是朋友。
- **不會繼承**：父類別的朋友，不能存取子類別的 `private`。

**什麼時候用**：`friend` 會破壞封裝，**謹慎使用**。最常見的合理用途是 `operator<<` 和對稱的二元運算子。如果類別已經有公開的 `num()`、`den()`，就不需要 `friend`（`C07` 的樣板就是這樣設計的）。

## 3.5 🔍 巢狀型別與型別別名

**是什麼**：類別裡面可以定義 **型別**：巢狀類別、`enum`、`using` 別名。用 `類別名::型別名` 存取。

```cpp
class Inventory {
public:
    using Id = int;                                // 型別別名
    enum class Status { InStock, SoldOut };        // 巢狀列舉
    struct Item { Id id; string name; Status st; };// 巢狀類別
    void add(Item it) { items_.push_back(it); }
    size_t size() const { return items_.size(); }
private:
    vector<Item> items_;
};

Inventory inv;
Inventory::Item pen{1, "pen", Inventory::Status::InStock};
inv.add(pen);
inv.add({2, "ink", Inventory::Status::SoldOut});
cout << inv.size() << '\n';                        // 輸出：2
```

標準函式庫大量使用這個技巧：`vector<int>::iterator`、`vector<int>::size_type`、`map<K,V>::value_type` 都是巢狀型別。

---

# 第四部分：運算子多載 (Operator Overloading)

## 4.1 基本概念

**是什麼**：讓自訂的類別也能使用 `+`、`==`、`<<` 這些運算子，用起來跟內建型別一樣自然。

**運算子其實就是名字特別的函式**：函式名稱是 `operator` 加上運算子符號。

```cpp
Fraction a(1, 2), b(1, 3);
Fraction c = a + b;            // 編譯器把它翻譯成 operator+(a, b) 或 a.operator+(b)
Fraction d = a.add(b);         // 沒有運算子多載的話只能這樣寫，比較不自然
```

**規則**：
- 只能多載 **已存在** 的運算子，不能發明新的（例如 `**`）。
- **不能改變** 優先順序、結合性、運算元的個數。`a + b * c` 永遠是先乘後加。
- 至少一個運算元是自訂型別（不能改變 `int + int` 的意思）。
- 不能多載：`::`、`.`、`.*`、`?:`、`sizeof`。
- 🔍 可以但 **不應該** 多載 `&&`、`||`、`,`：多載後會失去短路求值 / 求值順序的特性（第 02 課）。
- **語意要符合直覺**：`+` 就該是「加」，不要拿來做奇怪的事。

本部分用一個完整的 `Frac`（分數）類別示範各種運算子。完整程式碼在 4.9。

## 4.2 成員函式 vs 非成員函式

同一個運算子可以寫成兩種形式：

```cpp
class Frac {
public:
    Frac operator-(const Frac& o) const;          // 成員：左運算元是 *this，只寫右運算元
};
Frac operator+(const Frac& a, const Frac& b);     // 非成員：兩個運算元都寫出來
```

**差別在隱式轉換**（假設 `Frac(long long)` 沒有 `explicit`）：

```cpp
Frac f(1, 2);
f + 1;     // 非成員版本 ✅：1 被轉成 Frac(1)
1 + f;     // 非成員版本 ✅：兩邊都可以轉換
f - 1;     // 成員版本 ✅：右邊的 1 可以轉換
// 1 - f;  // 成員版本 ❌：左邊的 1 是 int，編譯器不會為了呼叫「成員函式」而轉換左邊
           // error: no match for 'operator-' (operand types are 'int' and 'Frac')
```

| 運算子 | 建議 | 原因 |
|---|---|---|
| `=`、`[]`、`()`、`->` | **必須** 是成員 | 語言規定 |
| `+=`、`-=`、`*=`、`++`、`--` | 成員 | 修改自己，左邊一定是這個類別 |
| 一元 `-`、`!` | 成員 | 只有一個運算元 |
| `+`、`-`、`*`、`==`、`<` 等對稱的二元運算子 | **非成員** | 兩邊都能隱式轉換 |
| `<<`、`>>`（輸出入） | **必須** 是非成員 | 左邊是 `ostream` / `istream`，不是你的類別 |

## 4.3 該回傳什麼？

| 運算子 | 回傳 | 原因 |
|---|---|---|
| `a + b`、`a - b`、`-a` | **新物件（傳值）** `T` | 結果是新的值，`a`、`b` 都不變 |
| `a += b`、`a = b` | **`*this` 的參考** `T&` | 修改自己，回傳自己才能串接 `a = b = c` |
| `++a` | `T&` | 前置：回傳改過的自己 |
| `a++` | `T`（傳值） | 後置：回傳 **舊值的複製品** |
| `a == b`、`a < b` | `bool` | |
| `os << a` | `ostream&` | 才能串接 `cout << a << b` |
| `is >> a` | `istream&` | 才能串接 `cin >> a >> b`，也能放在 `while (cin >> a)` |
| `a[i]` | `T&` 和 `const T&` 兩個版本 | 才能寫 `a[i] = x`，const 物件也能讀 |

**常見錯誤：`operator+` 回傳參考**

```cpp
Frac& operator+(const Frac& a, const Frac& b) {
    Frac result = ...;
    return result;      // ❌ 回傳區域變數的參考 → 懸置參考（第 05 課）
}
```

## 4.4 算術與複合指定：用 += 實作 +

**慣用寫法**：先寫會修改自己的 `+=`（成員），再用它實作 `+`（非成員）。這樣運算邏輯只寫一次。

```cpp
class Frac {
    long long n_, d_;
    void normalize() {
        if (d_ < 0) { n_ = -n_; d_ = -d_; }
        long long g = gcd(n_ < 0 ? -n_ : n_, d_);
        if (g) { n_ /= g; d_ /= g; }
    }
public:
    Frac(long long n = 0, long long d = 1) : n_(n), d_(d) { normalize(); }   // 不加 explicit：允許 int → Frac
    long long num() const { return n_; }
    long long den() const { return d_; }

    Frac& operator+=(const Frac& o) { n_ = n_ * o.d_ + o.n_ * d_; d_ *= o.d_; normalize(); return *this; }
    Frac& operator-=(const Frac& o) { n_ = n_ * o.d_ - o.n_ * d_; d_ *= o.d_; normalize(); return *this; }
    Frac& operator*=(const Frac& o) { n_ *= o.n_; d_ *= o.d_; normalize(); return *this; }
    Frac operator-() const { return Frac(-n_, d_); }        // 一元負號：回傳新物件
};

Frac operator+(Frac a, const Frac& b) { a += b; return a; }   // a 傳值 = 先複製一份，再對複製品 +=
Frac operator-(Frac a, const Frac& b) { a -= b; return a; }
Frac operator*(Frac a, const Frac& b) { a *= b; return a; }
```

使用（`<<` 的寫法見 4.6）：

```cpp
Frac a(1, 2), b(1, 3);
cout << a + b << '\n';       // 輸出：5/6
cout << a - b << '\n';       // 輸出：1/6
cout << a * b << '\n';       // 輸出：1/6
cout << -a << '\n';          // 輸出：-1/2
cout << a + 1 << '\n';       // 輸出：3/2（1 自動轉成 Frac(1)）
cout << 2 * a << '\n';       // 輸出：1（非成員版本：左邊的 2 也能轉換）
a += b;                      // a 變成 5/6
a += a;                      // 自己加自己：5/3
cout << a << '\n';           // 輸出：5/3
```

## 4.5 比較運算子

**慣用寫法**：只真正實作 `==` 和 `<`，其他的用它們推出來。

```cpp
bool operator==(const Frac& a, const Frac& b) { return a.num() == b.num() && a.den() == b.den(); }
bool operator!=(const Frac& a, const Frac& b) { return !(a == b); }
bool operator<(const Frac& a, const Frac& b)  { return a.num() * b.den() < b.num() * a.den(); }   // 分母都是正的才能這樣交叉相乘
bool operator>(const Frac& a, const Frac& b)  { return b < a; }
bool operator<=(const Frac& a, const Frac& b) { return !(b < a); }
bool operator>=(const Frac& a, const Frac& b) { return !(a < b); }

cout << (Frac(1, 2) == Frac(2, 4)) << '\n';   // 輸出：1（因為都正規化成 1/2）
cout << (Frac(1, 3) < Frac(1, 2)) << '\n';    // 輸出：1
cout << (Frac(-1, 2) > 0) << '\n';            // 輸出：0
```

**為什麼 `==` 這麼簡單就對了？** 因為不變量保證「每個分數都是最簡、分母為正」，相同的值一定有相同的表示法。**不變量讓其他操作變簡單**，這就是封裝的回報。

**有了 `<`，標準函式庫的 `sort`、`set`、`map` 就能直接用**：

```cpp
vector<Frac> v = {Frac(1, 2), Frac(1, 3), Frac(3, 4), Frac(-1, 5)};
sort(v.begin(), v.end());                    // sort 預設用 operator<
for (auto& f : v) cout << f << ' ';
cout << '\n';                                // 輸出：-1/5 1/3 1/2 3/4
```

### 🔍 C++20 的三向比較 <=>

C++20 之前要寫 `==`、`!=`、`<`、`<=`、`>`、`>=` 六個。C++20 的 **三向比較運算子**（太空船運算子）`<=>` 可以一次產生全部：

```cpp
struct Version {
    int major, minor, patch;
    auto operator<=>(const Version&) const = default;   // C++20：依成員宣告順序逐一比較
};
Version a{1, 2, 3}, b{1, 10, 0};
cout << (a < b) << (a == b) << (a != b) << '\n';      // 輸出：101（需要 -std=c++20）
```

`= default` 的比較方式是 **字典序**：先比 `major`，相同再比 `minor`，再比 `patch`。本平台用 C++17 編譯，所以練習題裡還是要自己寫。

## 4.6 輸出與輸入運算子 << 和 >>

```cpp
ostream& operator<<(ostream& os, const Frac& f) {
    os << f.num();
    if (f.den() != 1) os << '/' << f.den();     // 整數就不印分母
    return os;                                  // 回傳 os 才能串接
}

istream& operator>>(istream& is, Frac& f) {     // 讀入格式：a/b
    long long n, d; char slash;
    if (is >> n >> slash >> d) {
        if (slash == '/' && d != 0) f = Frac(n, d);
        else is.setstate(ios::failbit);         // 格式錯誤：讓串流進入失敗狀態（第 12 課）
    }
    return is;
}
```

**為什麼參數這樣寫**：
- `os` 是 **非 const 參考**：輸出會改變串流的狀態；而且串流不能複製。
- `<<` 的 `f` 是 `const Frac&`：輸出不會改變分數。
- `>>` 的 `f` 是 `Frac&`（非 const）：要把讀到的值寫進去。

```cpp
istringstream in("3/6 -2/4 1/0");
Frac x, y, z;
in >> x >> y;
cout << x << ' ' << y << '\n';           // 輸出：1/2 -1/2
if (!(in >> z)) cout << "讀取失敗\n";    // 輸出：讀取失敗（分母是 0）
cout << z << '\n';                       // 輸出：0（z 沒有被修改）
```

**常見錯誤：寫成成員函式**

```cpp
class Frac {
    ostream& operator<<(ostream& os) const;   // 這樣寫的話，左運算元是 Frac
};
f << cout;                                    // 😵 要這樣用才行，完全反了
```

## 4.7 下標運算子 [] 與函式呼叫運算子 ()

### operator[]

```cpp
class Matrix {
    int r_, c_;
    vector<double> a_;
public:
    Matrix(int r, int c) : r_(r), c_(c), a_(r * c, 0) {}
    // 讓 m[i][j] 可以用：m[i] 回傳第 i 列的開頭指標，再用指標的 [j]
    double* operator[](int i)             { return &a_[i * c_]; }
    const double* operator[](int i) const { return &a_[i * c_]; }
    // 另一種常見寫法：用 () 接兩個參數
    double& operator()(int i, int j)       { return a_[i * c_ + j]; }
    double operator()(int i, int j) const  { return a_[i * c_ + j]; }
};

Matrix m(2, 3);
m[1][2] = 5;
m(0, 1) = 7;
cout << m(1, 2) << ' ' << m[0][1] << '\n';   // 輸出：5 7
```

### operator()：函式物件 (Functor)

**是什麼**：多載了 `()` 的物件，可以 **像函式一樣被呼叫**。比普通函式多了一個能力：**可以帶狀態**（成員變數）。

```cpp
class Multiplier {
    int factor_;
public:
    explicit Multiplier(int f) : factor_(f) {}
    int operator()(int x) const { return x * factor_; }
};
Multiplier times3(3);
cout << times3(10) << '\n';                  // 輸出：30（看起來像函式呼叫）

vector<int> v = {1, 2, 3};
transform(v.begin(), v.end(), v.begin(), Multiplier(10));
for (int x : v) cout << x << ' ';
cout << '\n';                                // 輸出：10 20 30
```

**帶狀態的函式物件**：

```cpp
class CountCalls {
public:
    int count = 0;
    bool operator()(int a, int b) { count++; return a < b; }
};
vector<int> w = {5, 3, 1, 4, 2};
CountCalls cmp;
sort(w.begin(), w.end(), ref(cmp));          // ref：傳參考進去，才看得到 count 的變化
cout << (cmp.count > 0) << '\n';             // 輸出：1（sort 呼叫了比較函式好幾次）
```

第 11 課的 `priority_queue<int, vector<int>, greater<int>>`、`sort(..., greater<int>())`，`greater<int>` 就是標準函式庫內建的函式物件；第 15 課的 lambda 其實就是編譯器幫你產生的函式物件。

## 4.8 遞增 ++ 與遞減 --

```cpp
class Counter {
    int n_ = 0;
public:
    Counter& operator++() { ++n_; return *this; }    // 前置 ++c：加完回傳自己（參考）
    Counter operator++(int) {                         // 後置 c++：int 只是用來區分的「假參數」
        Counter old = *this;                          // 1. 先存舊值
        ++*this;                                      // 2. 用前置版本加一（邏輯只寫一次）
        return old;                                   // 3. 回傳舊值的複製品
    }
    int get() const { return n_; }
};

Counter c;
Counter a = c++;                 // a 拿到舊值 0，c 變成 1
Counter& r = ++c;                // c 變成 2，r 就是 c 本身
cout << a.get() << ' ' << c.get() << ' ' << (&r == &c) << '\n';   // 輸出：0 2 1
++++c;                           // 前置回傳參考，可以連續：c 變成 4
cout << c.get() << '\n';         // 輸出：4
```

**為什麼後置版本要假參數 `int`？** 因為兩個都叫 `operator++`、都沒有真正的參數，編譯器需要某種方式區分。這是語言規定的特殊記號，那個 `int` 永遠不會被用到。

**效能**：後置版本要多複製一份舊值。對 `int` 沒差（編譯器會最佳化），對迭代器這種類別就是額外的成本，所以 **迴圈裡習慣寫 `++it`**（第 02 課）。

## 4.9 轉換運算子

**是什麼**：讓物件可以 **轉換成其他型別**。寫法是 `operator 目標型別() const`，**不寫回傳型別**（名字本身就是回傳型別）。

```cpp
class Frac2 {
    long long n_, d_;
public:
    Frac2(long long n, long long d) : n_(n), d_(d) {}
    explicit operator double() const { return (double)n_ / d_; }   // 明確轉換才能用
    explicit operator bool() const { return n_ != 0; }             // 是不是非零
};

Frac2 f(1, 4), z(0, 1);
double d = static_cast<double>(f);     // ✅ 明確轉換
cout << d << '\n';                     // 輸出：0.25
// double e = f;                       // ❌ explicit：不能隱式轉換
if (f) cout << "f 不是 0\n";           // ✅ 輸出：f 不是 0（if 條件是特例，允許 explicit bool）
if (!z) cout << "z 是 0\n";            // ✅ 輸出：z 是 0
// int k = f + 1;                      // ❌ explicit bool 不會被偷偷當成整數 1 來加
```

**為什麼 `operator bool` 一定要 `explicit`？** 沒有 `explicit` 的話，`bool` 可以再自動轉成 `int`，於是 `f + 1`、`f < 3` 這種沒有意義的運算式都會編譯通過，而且結果很詭異。`explicit operator bool()` 讓物件 **只能** 用在 `if`、`while`、`!`、`&&`、`||`、`?:` 這些需要「真假」的地方。

`if (cin)`、`if (ptr)`（智慧指標）、`if (opt)`（`optional`，第 15 課）都是用 `explicit operator bool` 做的。

## 4.10 🔍 運算子多載總整理：完整的 Frac

```cpp
class Frac {
    long long n_, d_;
    void normalize();
public:
    Frac(long long n = 0, long long d = 1);           // 非 explicit：允許 int → Frac
    long long num() const;
    long long den() const;
    Frac& operator+=(const Frac& o);                  // 成員：修改自己，回傳 *this
    Frac& operator-=(const Frac& o);
    Frac& operator*=(const Frac& o);
    Frac operator-() const;                           // 成員：一元負號，回傳新物件
    explicit operator double() const;                 // 明確轉換
};
Frac operator+(Frac a, const Frac& b);                // 非成員：對稱、兩邊都能轉換
Frac operator-(Frac a, const Frac& b);
Frac operator*(Frac a, const Frac& b);
bool operator==(const Frac& a, const Frac& b);        // 非成員：回傳 bool
bool operator<(const Frac& a, const Frac& b);
ostream& operator<<(ostream& os, const Frac& f);      // 非成員：回傳串流參考
istream& operator>>(istream& is, Frac& f);
```

`C07 分數類別` 就是要你把這些實作出來。

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

**四個概念在一段程式碼裡**（繼承、多型的細節在第 08 課）：

```cpp
class Vehicle {                                    // 抽象：只描述「能做什麼」
public:
    virtual string move() const = 0;               // 純虛擬函式：沒有實作
    virtual ~Vehicle() = default;
};
class Car : public Vehicle {                       // 繼承：Car 是一種 Vehicle
    int fuel_ = 100;                               // 封裝：油量是私有的
public:
    string move() const override { return "四輪行駛"; }   // 多型：自己的實作
};
class Boat : public Vehicle {
public:
    string move() const override { return "水上航行"; }
};

vector<unique_ptr<Vehicle>> fleet;
fleet.push_back(make_unique<Car>());
fleet.push_back(make_unique<Boat>());
for (auto& v : fleet) cout << v->move() << '\n';   // 同一個呼叫，不同的行為
// 輸出：
// 四輪行駛
// 水上航行
```

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 類別 / 物件 | Class / Object | 設計圖 / 照設計圖做出來的東西 | 1.1 |
| 成員變數 / 成員函式 | Data Member / Member Function | 類別裡的資料 / 操作 | 1.1 |
| 範圍解析運算子 | Scope Resolution `::` | `Rect::area` 指定是哪個類別的成員 | 1.2 |
| 存取控制 | Access Specifier | public / private / protected | 1.3 |
| 封裝 | Encapsulation | 資料藏起來，只開放操作 | 1.4 |
| 不變量 | Invariant | 物件永遠成立的條件 | 1.5 |
| 建構子 / 解構子 | Constructor / Destructor | 建立時 / 銷毀時自動呼叫 | 2.1、2.7 |
| 預設建構子 | Default Constructor | 不需要參數的建構子 | 2.2 |
| 預設成員初始值 | Default Member Initializer | 宣告時直接給的初值 | 2.2 |
| 成員初始化串列 | Member Initializer List | `: x_(x), y_(y)` | 2.3 |
| 委派建構子 | Delegating Constructor | 呼叫同類別的另一個建構子 | 2.5 |
| 轉換建構子 | Converting Constructor | 能用一個引數呼叫、會被用來自動轉換的建構子 | 2.6 |
| explicit | explicit | 禁止用這個建構子 / 轉換運算子做隱式轉換 | 2.6、4.9 |
| 聚合 | Aggregate | 可以直接用 `{...}` 依序初始化的簡單 struct | 2.8 |
| this 指標 | this | 指向目前物件 | 3.1 |
| 方法串接 | Method Chaining | `a.f().g().h()`，靠回傳 `*this` | 3.1 |
| const 成員函式 | const Member Function | 承諾不修改物件 | 3.2 |
| mutable | mutable | const 函式裡也能改的成員（快取） | 3.2 |
| 靜態成員 | static Member | 整個類別共用一份 | 3.3 |
| 具名建構函式 | Named Constructor | 用 static 函式取代意義不清的建構子 | 3.3 |
| 朋友 | friend | 允許外部存取 private | 3.4 |
| 運算子多載 | Operator Overloading | 讓自訂型別也能用運算子 | 4.1 |
| 三向比較 | Three-way Comparison `<=>` | 一次定義所有比較，C++20 | 4.5 |
| 函式物件 | Functor / Function Object | 多載了 `()`、可以像函式一樣呼叫的物件 | 4.7 |
| 轉換運算子 | Conversion Operator | `operator double()`，物件轉成其他型別 | 4.9 |
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

### 題 8：預測輸出

```cpp
struct Tag { Tag(const char* s) { cout << s; } };
struct M {
    Tag z{"z"};
    Tag y;
    Tag x;
    M() : x("x"), y("y") { cout << "!"; }
};
M m;
```

### 題 9：這段程式碼為什麼印出 `0`？怎麼修？

```cpp
class Box {
    int w = 0;
public:
    void set(int w) { w = w; }
    int get() const { return w; }
};
Box b; b.set(5); cout << b.get();
```

### 題 10：預測輸出

```cpp
class Acc {
    int v_ = 0;
public:
    Acc& add(int x) { v_ += x; return *this; }
    Acc  add2(int x) { v_ += x; return *this; }
    int get() const { return v_; }
};
Acc a;
a.add(1).add(2).add2(3).add2(4);
cout << a.get();
```

### 題 11：下面的類別，哪幾行會編譯錯誤？

```cpp
class Shape {
    double area_ = 1.0;
    static int created_;
public:
    double area() const { return area_; }
    void grow() const { area_ *= 2; }                // ①
    static int created() { return created_; }        // ②
    static double twice() { return area_ * 2; }      // ③
};
```

### 題 12：寫一個函式物件 `InRange`，建構時給定 `lo`、`hi`，呼叫 `r(x)` 時回傳 `lo <= x && x <= hi`。用它配合 `count_if` 算出 `{1, 5, 8, 10, 3}` 裡有幾個數在 `[3, 8]` 之間。

---

# 習題解答

**題 1**：`5` 和一個 **垃圾值**（實際輸出可能是 `5 0` 或其他）。成員依照 **宣告順序** 初始化：`b_` 先宣告，所以先執行 `b_(a_ * 2)`，這時 `a_` 還沒初始化。`-Wall` 會警告。修法：把 `b_(a_ * 2)` 改成 `b_(x * 2)`，直接用參數。

**題 2**：① 和 ③。
- ①：`width()` 不是 `const` 成員函式，不能對 `const Box&` 呼叫（錯誤訊息：`passing 'const Box' as 'this' argument discards qualifiers`）。改成 `int width() const`。
- ③：`Box b2 = 3;` 是複製初始化，需要隱式轉換，但建構子是 `explicit`。
- ② 是直接初始化，④ 明確寫出了 `Box(4)`，都沒問題。

**題 3**：`321`。`a` 建立 → 1；區塊裡建立 `b`、`c` → 3，印出 `3`；區塊結束 `b`、`c` 銷毀 → 1；`new` 一個 → 2，印出 `2`；`delete p` → 1，印出 `1`。

**題 4**：`022`。`c++` 回傳舊值（0）給 `a`，c 變成 1；`++c` 讓 c 變成 2，回傳 c 本身，`b` 複製到 2。

**題 5**：`operator+` 是 **成員函式**，左邊的運算元必須已經是 `Fraction`。`f + 1` 的 `1` 可以透過非 `explicit` 的建構子轉成 `Fraction`；但 `1 + f` 的左邊 `1` 是 `int`，不會為了呼叫成員函式而被轉換。改成 **非成員函式**：`Fraction operator+(const Fraction& a, const Fraction& b);`，兩邊都能轉換。

**題 6**：`kelvin` 是 `public`，任何人都可以設成負數，破壞「不小於 0」的 **不變量**。應該設成 `private`，透過建構子和成員函式（例如 `set_kelvin`、`add`）檢查並維持不變量，違反時丟出例外。

**題 7**：回傳 **`Fraction&`**（`*this`）。`+=` 修改的是自己，回傳自己的參考可以支援串接（`a += b += c`）和 `(a += b).method()`，也跟內建型別的行為一致。回傳 `Fraction`（傳值）會多一次複製，而且 `(a += b) += c` 會改到複製品而不是 `a`。

**題 8**：`zyx!`。成員按照 **宣告順序** `z`、`y`、`x` 初始化（`z` 用預設成員初始值，`y`、`x` 用初始化串列，串列裡寫的順序不影響），全部成員建好之後才執行建構子本體印出 `!`。

**題 9**：`set` 裡的 `w = w;` 兩個 `w` 都是 **參數**（參數遮蔽了成員），等於參數自己指定給自己，成員 `w` 完全沒變。修法：`this->w = w;`，或把參數改名（例如 `int new_w`），或成員改名為 `w_`。

**題 10**：`6`。`add` 回傳 **參考**，所以 `add(1)`、`add(2)` 都改到 `a`，`a` 變成 3。`add2(3)` 也作用在 `a` 上（因為它是對 `add(2)` 回傳的參考 —— 也就是 `a` 本身 —— 呼叫的），`a` 變成 6，但它 **回傳的是複製品**；最後的 `add2(4)` 改的是那個暫時複製品，不影響 `a`。

**題 11**：① 和 ③。
- ①：`grow()` 是 `const` 成員函式，不能修改 `area_`（除非 `area_` 宣告成 `mutable`，但它在邏輯上屬於物件狀態，不應該這樣做 —— 應該把 `const` 拿掉）。
- ③：`static` 成員函式沒有 `this`，不能存取非 static 的 `area_`。
- ② 沒問題：static 成員函式存取 static 成員變數。（但要記得在類別外定義 `int Shape::created_ = 0;`，否則使用時會連結錯誤。）

**題 12**：

```cpp
class InRange {
    int lo_, hi_;
public:
    InRange(int lo, int hi) : lo_(lo), hi_(hi) {}
    bool operator()(int x) const { return lo_ <= x && x <= hi_; }
};
vector<int> v = {1, 5, 8, 10, 3};
cout << count_if(v.begin(), v.end(), InRange(3, 8)) << '\n';   // 輸出：3（5、8、3）
```
