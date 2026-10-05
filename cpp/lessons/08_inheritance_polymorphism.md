# 08. 繼承與多型 (Inheritance & Polymorphism)

> 程式練習：`C08 圖形與多型`、`C09 銀行帳戶系統`
>
> 先備知識：第 07 課「類別、建構子、存取控制」、第 06 課「unique_ptr」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 繼承基礎 | is-a 關係、繼承到了什麼、`protected`、三種繼承方式 |
| 第二部分 | 建構與解構的順序 | 誰先建、誰先拆、怎麼呼叫父類別的建構子、繼承建構子 |
| 第三部分 | 虛擬函式與多型 | 靜態繫結 vs 動態繫結、`override`、`final`、呼叫父類別版本、vtable |
| 第四部分 | 抽象類別與虛擬解構子 | 純虛擬函式、介面、為什麼解構子一定要 virtual、多型的複製 `clone` |
| 第五部分 | 繼承的陷阱 | 物件切割、名稱隱藏、建構子裡呼叫虛擬函式、預設參數 |
| 第六部分 | 進階與設計 | `dynamic_cast`、`typeid`、多重繼承與菱形問題、組合 vs 繼承、里氏替換原則 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：繼承基礎

## 1.1 繼承 (Inheritance)

**是什麼**：以一個 **現有的類別** 為基礎，建立一個 **新的類別**。新類別自動擁有原本類別的成員，可以再 **增加** 新的成員，或 **改寫** 原有的行為。

- 原本的類別：**基底類別 (base class)** / 父類別 (parent) / 超類別 (superclass)
- 新的類別：**衍生類別 (derived class)** / 子類別 (child) / 次類別 (subclass)

**語法**：`class 子類別 : public 父類別 { ... };`

**為什麼需要**：好幾個類別有 **共同的部分** 時，不用每個都重寫一次。

```cpp
// 沒有繼承：重複的程式碼
class Dog { public: string name; void eat() { cout << name << " eats\n"; } void bark(); };
class Cat { public: string name; void eat() { cout << name << " eats\n"; } void meow(); };
// name 和 eat() 寫了兩次。要改 eat() 的行為，兩個地方都要改。
```

```cpp
// 有繼承：共同的部分寫在父類別
class Animal {
public:
    string name;
    void eat() { cout << name << " eats\n"; }
};
class Dog : public Animal {                            // Dog 繼承 Animal
public:
    void bark() { cout << name << " barks\n"; }        // 新增的功能；可以直接用繼承來的 name
};
class Cat : public Animal {
public:
    void meow() { cout << name << " meows\n"; }
};

Dog d;
d.name = "Rex";       // 繼承來的成員變數
d.eat();              // 繼承來的成員函式 → 輸出：Rex eats
d.bark();             // 自己的 → 輸出：Rex barks
Cat c;
c.name = "Tom";
c.eat();              // 輸出：Tom eats
c.meow();             // 輸出：Tom meows
// c.bark();          // ❌ error: 'class Cat' has no member named 'bark'
```

**子類別物件裡面包含了一個完整的父類別物件**（叫做 **基底子物件 (base subobject)**），再加上子類別自己的成員：

```
Dog 物件
+------------------+
| Animal 的部分    |  ← name
+------------------+
| Dog 自己的部分   |  （這裡 Dog 沒有新的資料成員）
+------------------+
```

### 什麼東西 *不會* 被繼承？

| 不會繼承 | 說明 |
|---|---|
| 建構子 | 子類別要自己寫（或用 `using` 繼承建構子，2.4） |
| 解構子 | 子類別有自己的（編譯器自動產生），會自動呼叫父類別的 |
| 複製 / 移動指定運算子 | 子類別有自己的（編譯器自動產生），會自動呼叫父類別的 |
| `friend` 關係 | 父類別的朋友不是子類別的朋友 |
| `private` 成員的 **存取權** | `private` 成員 **確實存在** 於子類別物件裡，但子類別的程式碼 **不能直接存取** |

```cpp
class Base {
    int secret_ = 42;                     // private
public:
    int secret() const { return secret_; }
};
class Derived : public Base {
public:
    // int peek() { return secret_; }     // ❌ error: 'int Base::secret_' is private within this context
    int peek() const { return secret(); } // ✅ 透過父類別的公開函式
};
cout << Derived().peek() << ' ' << sizeof(Derived) << '\n';   // 輸出：42 4（secret_ 確實在 Derived 物件裡）
```

### 改寫父類別的函式，並呼叫父類別的版本

子類別可以定義一個 **同名** 的函式改寫父類別的行為。在子類別裡要呼叫父類別的版本，寫 `父類別名::函式名()`：

```cpp
class Logger {
public:
    void log(const string& msg) { cout << msg << '\n'; }
};
class TimeLogger : public Logger {
public:
    void log(const string& msg) {
        cout << "[12:00] ";
        Logger::log(msg);                 // 呼叫父類別的版本（不寫 Logger:: 就會無限遞迴呼叫自己！）
    }
};
TimeLogger t;
t.log("start");                           // 輸出：[12:00] start
t.Logger::log("raw");                     // 也可以從外面明確指定 → 輸出：raw
```

（這裡的 `log` 不是虛擬函式，所以這只是「隱藏」父類別的版本，不是多型。第三部分會講兩者的差別。）

## 1.2 is-a 關係

**是什麼**：公開繼承代表「**子類別 是一種 父類別**」。所以 **任何需要父類別的地方，都可以放子類別**。

**比喻**：「狗 **是一種** 動物」，所以「動物園需要一隻動物」時，給一隻狗是合理的。反過來不行：「需要一隻狗」時不能隨便給一隻動物（牠可能是貓）。

```cpp
void feed(Animal& a) { cout << "餵 " << a.name << '\n'; }

Dog d; d.name = "Rex";
feed(d);                   // ✅ Dog 是一種 Animal → 輸出：餵 Rex
Animal* p = &d;            // ✅ 父類別指標可以指向子類別物件 —— 向上轉型 (upcast)，自動、安全
Animal& r = d;             // ✅ 父類別參考也可以
cout << p->name << ' ' << r.name << '\n';   // 輸出：Rex Rex
// p->bark();              // ❌ 透過 Animal* 只看得到 Animal 有的成員
// Dog* q = p;             // ❌ error: invalid conversion from 'Animal*' to 'Dog*'
Dog* q = static_cast<Dog*>(p);   // 向下轉型 (downcast)：要明確轉型，而且要你自己確定它真的是 Dog（6.1）
q->bark();                 // 輸出：Rex barks
```

| 轉換方向 | 名稱 | 自動？ | 安全？ |
|---|---|---|---|
| 子類別 → 父類別（`Dog*` → `Animal*`） | 向上轉型 upcast | ✅ 自動 | ✅ 一定安全（狗一定是動物） |
| 父類別 → 子類別（`Animal*` → `Dog*`） | 向下轉型 downcast | ❌ 要明確寫 | ⚠️ 不一定（動物不一定是狗） |

**判斷要不要用繼承**：問「X 是一種 Y 嗎？」
- 「老師是一種人」→ 繼承。
- 「汽車 **有一個** 引擎」→ 不是 is-a，應該用 **組合**（6.4 節）。

## 1.3 protected

**是什麼**：介於 `public` 和 `private` 之間 —— **外部看不到，但子類別看得到**。

| 存取權限 | 自己的成員函式 | 子類別的成員函式 | 外部程式碼 |
|---|---|---|---|
| `public` | ✅ | ✅ | ✅ |
| `protected` | ✅ | ✅ | ❌ |
| `private` | ✅ | ❌ | ❌ |

**比喻**：家族企業的「內部帳本」：家族成員（子類別）可以看，外人（使用者）不能看。

```cpp
class Shape {
protected:
    string label_;                              // 子類別可以直接用
    Shape(string l) : label_(l) {}              // protected 建構子：只有子類別能呼叫
public:
    string label() const { return label_; }
};
class Circle : public Shape {
    double r_;
public:
    Circle(double r) : Shape("circle"), r_(r) {}
    string describe() const { return label_ + " r=" + to_string((int)r_); }   // ✅ 子類別直接存取 protected
};

Circle c(3);
cout << c.describe() << '\n';     // 輸出：circle r=3
cout << c.label() << '\n';        // 輸出：circle
// cout << c.label_;              // ❌ error: 'std::string Shape::label_' is protected within this context
// Shape s("x");                  // ❌ 建構子是 protected：外部不能直接建立 Shape
```

**設計建議**：**資料成員還是盡量用 `private`**，提供 `protected` 的成員函式給子類別用。理由：`protected` 的資料等於對「所有可能的子類別」公開，任何子類別都可以破壞不變量，而你無法控制別人會寫什麼子類別。

## 1.4 三種繼承方式

**是什麼**：`: public Base`、`: protected Base`、`: private Base` 決定 **父類別的成員在子類別裡變成什麼權限**（影響的是「子類別的使用者」和「孫類別」能看到什麼）。

| 父類別成員 | `public` 繼承 | `protected` 繼承 | `private` 繼承 |
|---|---|---|---|
| `public` | public | protected | private |
| `protected` | protected | protected | private |
| `private` | **看不到** | **看不到** | **看不到** |

**記法**：繼承方式是一個「**上限**」，比它寬鬆的權限都會被降到它。

```cpp
class Base { public: void hi() { cout << "hi\n"; } };
class Pub  : public Base    {};
class Prot : protected Base { public: void call() { hi(); } };   // 子類別內部仍然可以用
class Priv : private Base   { public: void call() { hi(); } };

Pub a;  a.hi();                    // ✅ 輸出：hi
Prot b; b.call();                  // ✅ 輸出：hi
// b.hi();                         // ❌ hi 在 Prot 裡變成 protected
Priv c; c.call();                  // ✅ 輸出：hi
// c.hi();                         // ❌ hi 在 Priv 裡變成 private
Base* p1 = &a;                     // ✅ public 繼承才是 is-a
// Base* p2 = &c;                  // ❌ error: 'Base' is an inaccessible base of 'Priv'
```

**99% 的情況用 `public` 繼承**（表達 is-a）。`private` 繼承的意思是「**用** 父類別來實作，但 **不是** 一種父類別」，這種情況改用組合（成員變數）通常更清楚。

> ⚠️ **常見錯誤**：`class D : B` 沒寫繼承方式時，**`class` 預設是 `private` 繼承**（`struct` 預設 `public`）。之後 `B* p = &d;` 會出現 `'B' is an inaccessible base of 'D'` 的錯誤。**永遠明確寫 `public`**。

---

# 第二部分：建構與解構的順序

## 2.1 建構順序：由內而外

1. **父類別** 的建構子（有好幾層就從最上層開始）
2. **子類別的成員變數**（依宣告順序）
3. **子類別** 建構子的本體

## 2.2 解構順序：完全相反

1. **子類別** 解構子的本體
2. 子類別的成員變數（依宣告的 **相反** 順序）
3. **父類別** 的解構子

**比喻**：蓋房子先打地基（父類別），再蓋牆（成員）、最後裝潢（子類別本體）；拆房子則先拆裝潢，最後才拆地基。

**為什麼是這個順序？** 子類別的建構子可能會用到父類別的成員，所以父類別要先準備好；解構時子類別可能還在用父類別的東西，所以子類別要先拆。

```cpp
struct Base   { Base()   { cout << "B ";  } ~Base()   { cout << "~B "; } };
struct Member { Member() { cout << "M ";  } ~Member() { cout << "~M "; } };
struct Derived : Base {
    Member m;
    Derived()  { cout << "D ";  }
    ~Derived() { cout << "~D "; }
};
{ Derived d; }
cout << '\n';         // 輸出：B M D ~D ~M ~B
```

**多層繼承 + 每層都有成員**：

```cpp
struct Tag { string s; Tag(string x) : s(x) { cout << "+" << s << ' '; } ~Tag() { cout << "-" << s << ' '; } };
struct L1 { Tag t{"L1成員"}; L1() { cout << "L1 "; } ~L1() { cout << "~L1 "; } };
struct L2 : L1 { Tag t{"L2成員"}; L2() { cout << "L2 "; } ~L2() { cout << "~L2 "; } };
struct L3 : L2 { Tag t{"L3成員"}; L3() { cout << "L3 "; } ~L3() { cout << "~L3 "; } };
{ L3 x; cout << "| "; }
cout << '\n';
// 輸出：+L1成員 L1 +L2成員 L2 +L3成員 L3 | ~L3 -L3成員 ~L2 -L2成員 ~L1 -L1成員
```

每一層都是「成員 → 本體」，然後下一層；拆的時候每一層都是「本體 → 成員」，從最下層開始。

## 2.3 呼叫父類別的建構子

**規則**：子類別的建構子 **一定會** 先呼叫父類別的建構子。
- 沒有特別寫 → 呼叫父類別的 **預設建構子**。
- 父類別 **沒有預設建構子**（或你想用別的）→ **必須在初始化串列裡寫出來**。

```cpp
class Person {
protected:
    string name_;
public:
    Person(string n) : name_(n) { cout << "Person(" << name_ << ")\n"; }   // 沒有預設建構子
};
class Student : public Person {
    int id_;
public:
    Student(string n, int id) : Person(n), id_(id) {   // ✅ 在初始化串列呼叫父類別建構子
        cout << "Student(" << id_ << ")\n";
    }
    // Student(string n, int id) : id_(id) {}          // ❌ error: no matching function for call to 'Person::Person()'
    void show() const { cout << name_ << " #" << id_ << '\n'; }
};

Student s("amy", 7);
s.show();
// 輸出：
// Person(amy)
// Student(7)
// amy #7
```

**注意**：初始化串列裡，**父類別永遠最先初始化**，不管你寫在哪個位置（跟第 07 課成員初始化順序的規則一樣）。

**三層的例子**（`C08` 的寫法）：

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
};
class Rectangle : public Shape {
protected:
    double w_, h_;
public:
    Rectangle(double w, double h) : w_(w), h_(h) {}
    double area() const override { return w_ * h_; }
};
class Square : public Rectangle {
public:
    explicit Square(double s) : Rectangle(s, s) {}   // 只能呼叫「直接」的父類別 Rectangle
};
cout << Square(3).area() << '\n';                     // 輸出：9
```

## 2.4 繼承建構子 (Inheriting Constructors)

**是什麼**：子類別 **沒有新增需要初始化的成員** 時，用 `using 父類別::父類別;` 直接沿用父類別的 **所有** 建構子。

**為什麼需要**：不然每個建構子都要寫一個「原封不動轉交」的版本，很囉唆。

```cpp
class CalcError : public runtime_error {
public:
    using runtime_error::runtime_error;    // 沿用 runtime_error(const string&)、runtime_error(const char*)
};
// 不寫 using 的話要這樣：
// CalcError(const string& msg) : runtime_error(msg) {}
// CalcError(const char* msg) : runtime_error(msg) {}

try {
    throw CalcError("division by zero");
} catch (const runtime_error& e) {
    cout << e.what() << '\n';               // 輸出：division by zero
}
```

`C13` 的自訂例外就是這樣寫的。

---

# 第三部分：虛擬函式與多型

## 3.1 問題：沒有 virtual 時會怎樣？

```cpp
class Animal {
public:
    void speak() const { cout << "...\n"; }
};
class Dog : public Animal {
public:
    void speak() const { cout << "Woof\n"; }
};

Dog d;
d.speak();                 // 輸出：Woof
Animal* p = &d;
p->speak();                // 輸出：...   ← 指向的明明是 Dog，卻呼叫了 Animal 的版本！
Animal& r = d;
r.speak();                 // 輸出：...
```

**問題**：我們想寫一段「不管是什麼動物都能處理」的程式（例如 `vector<Animal*>` 走訪呼叫 `speak`），但呼叫的永遠是 `Animal::speak`。

## 3.2 靜態繫結 vs 動態繫結 (Static / Dynamic Binding)

**繫結 (binding)**：決定「這一行函式呼叫，到底要執行哪一個函式」。

| | 靜態繫結（早繫結） | 動態繫結（晚繫結） |
|---|---|---|
| 什麼時候決定 | **編譯時** | **執行時** |
| 根據什麼 | 指標 / 參考的 **宣告型別** | 指標 / 參考 **實際指向的物件** |
| 怎麼得到 | 預設 | 函式加上 `virtual` |
| 速度 | 快（可以內聯） | 多一次間接查表（3.6） |

3.1 的例子：`p` 的宣告型別是 `Animal*`，`speak` 不是虛擬函式 → 靜態繫結 → `Animal::speak`。

**加上 `virtual` 就變成動態繫結**：

```cpp
class Animal {
public:
    virtual void speak() const { cout << "...\n"; }   // ← virtual
    virtual ~Animal() = default;                      // 有虛擬函式就要有虛擬解構子（4.3）
};
class Dog : public Animal {
public:
    void speak() const override { cout << "Woof\n"; }  // override：覆寫父類別的虛擬函式（3.4）
};
class Cat : public Animal {
public:
    void speak() const override { cout << "Meow\n"; }
};

Dog d;
Animal* p = &d;
p->speak();                // 輸出：Woof   ← 執行時查看 p 實際指向 Dog
Animal& r = d;
r.speak();                 // 輸出：Woof
```

**虛擬函式的「虛擬」會被繼承**：父類別宣告了 `virtual`，子類別同名同簽章的函式 **自動** 也是虛擬的（寫不寫 `virtual` 都一樣），孫類別也是。

## 3.3 多型 (Polymorphism)

**是什麼**：**同一段程式碼**（`a->speak()`）面對 **不同型別的物件**，會執行 **各自的版本**。希臘文的意思是「多種形態」。

**比喻**：老師對全班說「交作業」，每個同學交的是自己的作業。老師不需要知道每個人寫了什麼，只要說同一句話。

### 例 1：用容器存不同的子類別

```cpp
vector<unique_ptr<Animal>> zoo;
zoo.push_back(make_unique<Dog>());
zoo.push_back(make_unique<Cat>());
zoo.push_back(make_unique<Dog>());
for (const auto& a : zoo) a->speak();
// 輸出：
// Woof
// Meow
// Woof
```

### 例 2：函式參數用父類別的參考

```cpp
void make_noise(const Animal& a, int times) {
    for (int i = 0; i < times; i++) a.speak();    // 不知道、也不需要知道 a 實際是什麼
}
make_noise(Cat(), 2);
// 輸出：
// Meow
// Meow
```

### 為什麼多型這麼重要？

**沒有多型的寫法**：

```cpp
enum Kind { DOG, CAT };
void speak(Kind k) {
    switch (k) {
        case DOG: cout << "Woof\n"; break;
        case CAT: cout << "Meow\n"; break;
    }
}
// 新增 Bird：要找出程式裡「每一個」switch(kind) 加上 case BIRD。漏改一個就是 bug。
```

**有多型的寫法**：新增 `Bird` 只需要 **寫一個新類別**，走訪動物園、`make_noise` 等既有的程式碼 **一行都不用改**：

```cpp
class Bird : public Animal {
public:
    void speak() const override { cout << "Tweet\n"; }
};
zoo.push_back(make_unique<Bird>());       // 原本的 for 迴圈直接就能處理 Bird
```

這叫 **開放封閉原則 (Open-Closed Principle)**：對擴充開放、對修改封閉（第 09 課）。

### 多型只透過指標或參考才會發生

```cpp
Dog d;
d.speak();                 // 直接用物件：編譯時就知道是 Dog → 靜態繫結（結果剛好也是 Woof）
Animal a = d;              // ⚠️ 複製成一個 Animal 物件（物件切割，5.1）
a.speak();                 // 輸出：...   a 就是一個 Animal，跟 Dog 沒關係了
```

## 3.4 override 和 final

### override

**是什麼**：寫在子類別函式後面，明確告訴編譯器「**我要覆寫父類別的虛擬函式**」。如果父類別 **沒有** 對應的虛擬函式可以覆寫，就編譯錯誤。

**為什麼需要**：覆寫的條件很嚴格 —— **名稱、參數、`const`** 都要完全一樣。差一點點，編譯器就會以為你在定義一個 **新的** 函式，多型默默失效，而且 **不會有任何錯誤訊息**。

```cpp
class Base {
public:
    virtual void draw() const { cout << "Base::draw\n"; }
    virtual ~Base() = default;
};
class NoOverride : public Base {
public:
    void draw() { cout << "NoOverride::draw\n"; }   // 忘了 const → 這是一個「新的」函式，沒有覆寫！
};
NoOverride n;
Base& b = n;
b.draw();                  // 輸出：Base::draw   😱 沒有任何警告，多型失效了
```

加上 `override`，編譯器就會抓到：

```cpp
class WithOverride : public Base {
public:
    // void draw() override;          // ❌ error: 'void WithOverride::draw()' marked 'override', but does not override
    // void drow() const override;    // ❌ 打錯字也會被抓到
    void draw() const override { cout << "WithOverride::draw\n"; }   // ✅
};
```

**規則：覆寫虛擬函式時，一律加 `override`**（`-Wall` 不一定會警告你漏了，`-Wsuggest-override` 才會）。

### final

**是什麼**：
- 寫在 **類別** 後面：這個類別 **不能再被繼承**。
- 寫在 **虛擬函式** 後面：這個函式 **不能再被子類別覆寫**。

```cpp
class Dog2 : public Animal {
public:
    void speak() const final { cout << "Woof\n"; }      // 子類別不能再覆寫 speak
};
// class Puppy : public Dog2 {
//     void speak() const override {}                   // ❌ error: virtual function 'virtual void Puppy::speak() const' overriding final function
// };

class Leaf final : public Animal {};                    // Leaf 不能被繼承
// class Sub : public Leaf {};                          // ❌ error: cannot derive from 'final' base 'Leaf' in derived type 'Sub'
```

**什麼時候用**：確定設計上不該再被延伸時。另外編譯器知道「不會再有子類別覆寫」，有機會把虛擬呼叫最佳化成直接呼叫（去虛擬化 devirtualization）。

## 3.5 覆寫時呼叫父類別的版本

**是什麼**：子類別的覆寫版本常常是「父類別做的事 + 一些額外的事」，用 `父類別::函式()` 呼叫父類別的版本。

```cpp
class Account {
protected:
    long long balance_ = 0;
public:
    virtual ~Account() = default;
    virtual void report() const { cout << "餘額 " << balance_; }
    void deposit(long long x) { balance_ += x; }
};
class SavingsAccount : public Account {
    double rate_;
public:
    SavingsAccount(double r) : rate_(r) {}
    void report() const override {
        Account::report();                        // 先做父類別的部分
        cout << "，利率 " << rate_ * 100 << "%";   // 再加上自己的
    }
};

SavingsAccount s(0.02);
s.deposit(1000);
const Account& a = s;
a.report();
cout << '\n';               // 輸出：餘額 1000，利率 2%
```

**常見錯誤**：寫成 `report();`（少了 `Account::`）→ 呼叫的是自己 → **無限遞迴** → stack overflow。

## 3.6 🔍 虛擬函式怎麼運作：vtable

編譯器通常這樣實作虛擬函式：

1. 每個 **有虛擬函式的類別** 有一張 **虛擬函式表 (vtable)**：一個函式指標陣列，記錄這個類別每個虛擬函式的實際位址。整個類別 **共用一張**。
2. 每個 **物件** 多一個隱藏的指標 **vptr**，指向自己類別的 vtable。vptr 在建構子裡被設定。
3. 呼叫 `p->speak()` 時：透過 `p` 找到物件 → 讀 vptr → 找到 vtable → 取出 `speak` 那一格的位址 → 呼叫。

```
Dog 物件                Dog 的 vtable
+--------+             +----------------+
| vptr ──┼───────────▶ | &Dog::speak    |
| ...    |             | &Dog::~Dog     |
+--------+             +----------------+

Cat 物件                Cat 的 vtable
+--------+             +----------------+
| vptr ──┼───────────▶ | &Cat::speak    |
| ...    |             | &Cat::~Cat     |
+--------+             +----------------+
```

**比喻**：每個員工身上帶著一張「我的部門的工作手冊」（vptr → vtable）。主管只要說「照手冊第 1 頁做」，每個人就照自己部門的手冊執行。

**親眼看到 vptr 的存在**：

```cpp
struct NoVirtual   { int x; void f() {} };
struct WithVirtual { int x; virtual void f() {} };
cout << sizeof(NoVirtual) << ' ' << sizeof(WithVirtual) << '\n';   // 輸出：4 16（64 位元系統）
```

`WithVirtual` 多了 8 bytes 的 vptr，再加上對齊（第 01 課），從 4 bytes 變成 16 bytes。

**成本**：
- 每個物件多一個指標（8 bytes）。
- 每次呼叫多兩次間接存取（讀 vptr、讀 vtable），而且編譯器通常 **無法內聯 (inline)** 虛擬函式。
- 所以 C++ **預設不是虛擬的**：不需要多型的地方不用付這個代價（「不用的東西不付錢」是 C++ 的設計哲學）。

---

# 第四部分：抽象類別與虛擬解構子

## 4.1 純虛擬函式與抽象類別 (Pure Virtual / Abstract Class)

**是什麼**：
- **純虛擬函式**：只宣告、**不提供實作**，寫成 `= 0`。表示「子類別 **一定要** 自己實作」。
- **抽象類別**：有 **至少一個** 純虛擬函式的類別。**不能建立物件**，只能當作父類別。
- **具體類別 (concrete class)**：所有純虛擬函式都實作了、可以建立物件的類別。

**為什麼需要**：3.2 的 `Animal::speak` 印 `"..."` 其實沒什麼意義 —— 「一隻抽象的動物」該怎麼叫？根本沒有合理的預設行為。用純虛擬函式表達「**每種動物都必須會叫，但 Animal 本身不知道怎麼叫**」。

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;          // 純虛擬：Shape 不知道怎麼算面積
    virtual string name() const = 0;
    void print() const {                       // 一般函式：可以呼叫純虛擬函式！
        cout << name() << " 面積 " << area() << '\n';
    }
};
class Circle : public Shape {
    double r_;
public:
    explicit Circle(double r) : r_(r) {}
    double area() const override { return 3.14 * r_ * r_; }
    string name() const override { return "圓形"; }
};
class Rect : public Shape {
    double w_, h_;
public:
    Rect(double w, double h) : w_(w), h_(h) {}
    double area() const override { return w_ * h_; }
    string name() const override { return "矩形"; }
};

// Shape s;                                   // ❌ error: cannot declare variable 's' to be of abstract type 'Shape'
Circle c(1);
Rect r(2, 3);
c.print();                                     // 輸出：圓形 面積 3.14
r.print();                                     // 輸出：矩形 面積 6
Shape& sr = r;                                 // ✅ 抽象類別的參考和指標都可以
unique_ptr<Shape> p = make_unique<Circle>(2);  // ✅
cout << p->area() << '\n';                     // 輸出：12.56
```

注意 `Shape::print()`：父類別的一般函式 **呼叫了純虛擬函式**，執行時會呼叫到子類別的實作。這叫 **樣板方法模式 (Template Method Pattern)**：父類別定好「流程」，子類別填入「細節」。

**比喻**：「交通工具」是一個抽象概念 —— 你不能買一台「交通工具」，只能買汽車、機車、腳踏車。但你可以說「我需要一台交通工具」（抽象類別的參考 / 指標）。

### 子類別沒有實作全部的純虛擬函式 → 子類別也是抽象的

```cpp
class HalfDone : public Shape {
public:
    double area() const override { return 0; }    // 只實作了 area，沒有實作 name
};
// HalfDone h;      // ❌ error: cannot declare variable 'h' to be of abstract type 'HalfDone'
//                  //    note: because the following virtual functions are pure within 'HalfDone': 'virtual std::string Shape::name() const'
```

錯誤訊息的 note 會告訴你 **還缺哪些函式沒實作**。

### 抽象類別可以有建構子、資料成員和實作好的函式

```cpp
class Employee {
    string name_;                                  // 資料成員
public:
    Employee(string n) : name_(n) {}               // 建構子（由子類別呼叫）
    virtual ~Employee() = default;
    virtual long long salary() const = 0;          // 純虛擬
    string name() const { return name_; }          // 實作好的函式
};
class Engineer : public Employee {
public:
    using Employee::Employee;
    long long salary() const override { return 80000; }
};
Engineer e("amy");
cout << e.name() << ' ' << e.salary() << '\n';    // 輸出：amy 80000
```

## 4.2 介面 (Interface)

**是什麼**：**只有** 純虛擬函式（加上虛擬解構子）、**沒有資料成員** 的抽象類別。它只規定「**能做什麼**」，完全不管「怎麼做」。

C++ 沒有 `interface` 關鍵字，用「全部都是純虛擬函式的類別」來表達。

**為什麼需要**：使用者只依賴介面，背後的實作可以 **隨時替換**。

```cpp
class Storage {                                    // 介面：「能存、能讀」
public:
    virtual ~Storage() = default;
    virtual void save(const string& key, int value) = 0;
    virtual int load(const string& key) const = 0;
};

class MemoryStorage : public Storage {             // 實作 1：存在記憶體
    map<string, int> data_;
public:
    void save(const string& k, int v) override { data_[k] = v; }
    int load(const string& k) const override { auto it = data_.find(k); return it == data_.end() ? -1 : it->second; }
};

class LoggingStorage : public Storage {            // 實作 2：每次操作都印出紀錄（包裝另一個 Storage）
    unique_ptr<Storage> inner_;
public:
    LoggingStorage(unique_ptr<Storage> s) : inner_(std::move(s)) {}
    void save(const string& k, int v) override { cout << "save " << k << '\n'; inner_->save(k, v); }
    int load(const string& k) const override { cout << "load " << k << '\n'; return inner_->load(k); }
};

void run(Storage& st) {                            // 只依賴介面
    st.save("score", 95);
    cout << st.load("score") << '\n';
}

MemoryStorage m;
run(m);
// 輸出：95
LoggingStorage lg(make_unique<MemoryStorage>());
run(lg);
// 輸出：
// save score
// load score
// 95
```

`run` 完全不用改，就能搭配不同的實作。第 09 課會用介面來設計 ADT。

## 4.3 虛擬解構子 (Virtual Destructor)

**規則：只要類別會被當作父類別、而且可能透過父類別指標刪除子類別物件，解構子就必須是 `virtual`。**

**為什麼**：`delete p;` 也是一次「函式呼叫」（呼叫解構子）。如果解構子不是虛擬的，就是 **靜態繫結**，只會呼叫 `p` 宣告型別的解構子。

### 錯誤示範

```cpp
struct BadBase {
    ~BadBase() { cout << "~BadBase\n"; }              // ❌ 不是 virtual
};
struct BadDerived : BadBase {
    vector<int> data = vector<int>(1000);            // 有資源
    ~BadDerived() { cout << "~BadDerived\n"; }
};
BadBase* p = new BadDerived;
delete p;
// 實際輸出（GCC）：
// ~BadBase
// ~BadDerived 沒被呼叫 → data 的 1000 個 int 沒有被釋放（洩漏）
// 而且依照標準，這是「未定義行為」，什麼事都可能發生
```

`-Wall` 會警告：`deleting object of polymorphic class type ... which has non-virtual destructor might cause undefined behavior`（類別有其他虛擬函式時）。用 `--debug`（AddressSanitizer）執行會直接報錯。

### 正確寫法

```cpp
struct GoodBase {
    virtual ~GoodBase() { cout << "~GoodBase\n"; }   // ✅ virtual
};
struct GoodDerived : GoodBase {
    ~GoodDerived() override { cout << "~GoodDerived\n"; }
};
GoodBase* q = new GoodDerived;
delete q;
// 輸出：
// ~GoodDerived
// ~GoodBase
```

`unique_ptr<Base>` 和 `shared_ptr<Base>`（用 `new` 給的時候）也一樣：它們內部就是 `delete` 一個 `Base*`，沒有虛擬解構子同樣出事。

**經驗法則**：
- 有任何虛擬函式的類別，**解構子就要是 virtual**：寫 `virtual ~Base() = default;` 就好。
- 不打算被繼承的類別：不用 virtual（可以加 `final` 表明）。

## 4.4 🔍 多型的複製：clone

**問題**：手上只有一個 `Shape*`，要怎麼「複製一份一模一樣的圖形」？`Shape copy = *p;` 不行（抽象類別、而且會切割），也不知道實際型別是什麼。

**解法**：讓每個子類別自己提供一個虛擬的 `clone()`：

```cpp
class Shape2 {
public:
    virtual ~Shape2() = default;
    virtual unique_ptr<Shape2> clone() const = 0;
    virtual string name() const = 0;
};
class Circle2 : public Shape2 {
    double r_;
public:
    explicit Circle2(double r) : r_(r) {}
    unique_ptr<Shape2> clone() const override { return make_unique<Circle2>(*this); }   // 用自己的複製建構子
    string name() const override { return "Circle r=" + to_string((int)r_); }
};

vector<unique_ptr<Shape2>> a;
a.push_back(make_unique<Circle2>(5));
vector<unique_ptr<Shape2>> b;
for (auto& s : a) b.push_back(s->clone());     // 深複製整個容器
cout << b[0]->name() << ' ' << (a[0].get() != b[0].get()) << '\n';   // 輸出：Circle r=5 1
```

---

# 第五部分：繼承的陷阱

## 5.1 物件切割 (Object Slicing)

**是什麼**：把子類別物件 **以值複製** 給父類別變數時，**只有父類別的部分被複製**，子類別多出來的資料和行為全部被「切掉」。

**比喻**：把一張全彩照片用黑白影印機印出來，顏色資訊就永遠不見了。

```cpp
struct Pet {
    string name = "pet";
    virtual ~Pet() = default;
    virtual string sound() const { return "..."; }
};
struct Parrot : Pet {
    string word = "hello";
    string sound() const override { return word; }
};

Parrot pr;
Pet a = pr;                                   // 切割！只複製了 Pet 的部分
cout << a.sound() << '\n';                    // 輸出：...（就算 sound 是 virtual 也一樣：a 就是一個 Pet）
// cout << a.word;                            // ❌ Pet 沒有 word
```

### 切割發生的三種常見情境

```cpp
void by_value(Pet p)      { cout << p.sound() << '\n'; }   // ❌ 傳值 → 切割
void by_ref(const Pet& p) { cout << p.sound() << '\n'; }   // ✅ 傳參考 → 多型正常
void by_ptr(const Pet* p) { cout << p->sound() << '\n'; }  // ✅ 傳指標 → 多型正常

by_value(pr);                 // 輸出：...
by_ref(pr);                   // 輸出：hello
by_ptr(&pr);                  // 輸出：hello

vector<Pet> pets;             // ❌ 存進去的全部被切割成 Pet
pets.push_back(Parrot());
cout << pets[0].sound() << '\n';              // 輸出：...

vector<unique_ptr<Pet>> good;                 // ✅
good.push_back(make_unique<Parrot>());
cout << good[0]->sound() << '\n';             // 輸出：hello
```

**還有一種：`catch` 例外時用值接收**（第 13 課）：`catch (exception e)` 會切割，要寫 `catch (const exception& e)`。

**規則**：
- 多型的物件 **永遠用指標或參考傳遞**。
- 存進容器時用 `vector<unique_ptr<Base>>`。
- 把父類別設成 **抽象類別** 也能防止切割：抽象類別無法以值存在，`Shape s = circle;` 直接編譯錯誤。

## 5.2 名稱隱藏 (Name Hiding)

**是什麼**：子類別定義了一個跟父類別 **同名** 的函式（不管參數一不一樣），父類別 **所有同名的函式**（包括其他多載版本）在子類別裡都會被 **隱藏**。

**為什麼會這樣？** 編譯器找名字的規則是：**先在最內層的作用域找，找到這個名字就停止**，不會再往外（父類別）找，然後才在找到的那一層做多載選擇。

```cpp
struct Base {
    void f(int x)    { cout << "Base::f(int)\n"; }
    void f(double x) { cout << "Base::f(double)\n"; }
};
struct Derived : Base {
    void f(string s) { cout << "Derived::f(string)\n"; }   // 隱藏了 Base 的兩個 f
};

Derived d;
d.f(string("hi"));        // 輸出：Derived::f(string)
// d.f(1);                // ❌ error: cannot convert 'int' to 'std::string'
                          //    在 Derived 找到 f 就停了，只有 f(string) 可以選，int 轉不成 string
d.Base::f(1);             // ✅ 明確指定 → 輸出：Base::f(int)
```

**修法：用 `using` 把父類別的同名函式帶進來**

```cpp
struct Derived2 : Base {
    using Base::f;                                          // 把 Base 的所有 f 帶進 Derived2 的作用域
    void f(string s) { cout << "Derived2::f(string)\n"; }
};
Derived2 d2;
d2.f(1);                  // 輸出：Base::f(int)
d2.f(2.5);                // 輸出：Base::f(double)
d2.f(string("x"));        // 輸出：Derived2::f(string)
```

**虛擬函式也會被隱藏**：父類別有 `virtual void g(int)` 和 `virtual void g(double)`，子類別只覆寫 `g(int)`，那麼透過 **子類別** 物件呼叫 `g(2.5)` 時，2.5 會被轉成 int 呼叫 `g(int)`！（`-Woverloaded-virtual` 會警告。）同樣用 `using Base::g;` 解決。

## 5.3 建構子 / 解構子裡呼叫虛擬函式

**是什麼**：在 **父類別的建構子 / 解構子** 裡呼叫虛擬函式，**不會** 呼叫到子類別的版本。

```cpp
struct Base {
    Base()          { cout << "建構中："; who(); }
    virtual ~Base() { cout << "解構中："; who(); }
    virtual void who() const { cout << "Base\n"; }
};
struct Derived : Base {
    string s_ = "Derived";
    void who() const override { cout << s_ << '\n'; }
};

{
    Derived d;
    cout << "建構完成："; d.who();
}
// 輸出：
// 建構中：Base
// 建構完成：Derived
// 解構中：Base
```

**原因**：父類別建構子執行時，子類別的部分 **還沒建立**（`s_` 還沒初始化）。如果呼叫到子類別的版本，就會存取一個還不存在的字串。所以 C++ 規定：**在建構 / 解構期間，物件的動態型別就是「目前正在建構 / 解構的那一層」**（vptr 在每一層建構子開始時才設成那一層的 vtable）。

解構時也一樣：`~Base()` 執行時，`~Derived()` 已經跑完、`s_` 已經被銷毀了。

**比喻**：房子還在打地基，就不能請住戶搬進來住；房子拆到只剩地基時，住戶也早就搬走了。

**更危險的情況**：在建構子裡呼叫 **純虛擬** 函式 → 呼叫一個沒有實作的函式 → 程式當掉（`pure virtual method called`）。

## 5.4 🔍 虛擬函式的預設參數是靜態繫結的

```cpp
struct B { virtual ~B() = default; virtual void show(int x = 1) const { cout << "B" << x << '\n'; } };
struct D : B { void show(int x = 2) const override { cout << "D" << x << '\n'; } };

D d;
B& rb = d;
rb.show();     // 輸出：D1   ← 函式是 D 的（動態繫結），預設值卻是 B 的（靜態繫結）
d.show();      // 輸出：D2
```

**原因**：預設參數是 **編譯時** 由編譯器填進呼叫處的，編譯器只知道 `rb` 的宣告型別是 `B&`，所以填入 `B` 的預設值 `1`；而要呼叫哪個函式是 **執行時** 才查 vtable 決定的。

**規則**：覆寫虛擬函式時，**不要改變預設參數**（最好虛擬函式乾脆不要用預設參數）。

---

# 第六部分：進階與設計

## 6.1 dynamic_cast 與 RTTI

**是什麼**：把父類別指標 / 參考 **安全地** 轉成子類別。**執行時檢查** 物件的實際型別：
- 指標版本：成功回傳指標，失敗回傳 `nullptr`。
- 參考版本：失敗時丟出 `std::bad_cast` 例外（參考不能是空的）。

只能用在 **多型類別**（至少有一個虛擬函式的類別），因為它要靠 vtable 裡的型別資訊。

```cpp
struct Animal { virtual ~Animal() = default; };
struct Dog : Animal { void fetch() const { cout << "撿球\n"; } };
struct Cat : Animal { void climb() const { cout << "爬樹\n"; } };

vector<unique_ptr<Animal>> zoo;
zoo.push_back(make_unique<Dog>());
zoo.push_back(make_unique<Cat>());

for (auto& a : zoo) {
    if (auto* d = dynamic_cast<Dog*>(a.get()))      d->fetch();   // 是 Dog 才成功
    else if (auto* c = dynamic_cast<Cat*>(a.get())) c->climb();
}
// 輸出：
// 撿球
// 爬樹

Cat cat;
Animal& ref = cat;
try {
    Dog& dg = dynamic_cast<Dog&>(ref);              // 參考版本：失敗丟例外
    dg.fetch();
} catch (const bad_cast& e) {
    cout << "不是 Dog\n";                           // 輸出：不是 Dog
}
```

**和 `static_cast` 的差別**：

```cpp
Animal* pa = zoo[1].get();                          // 實際上是 Cat
Dog* bad = static_cast<Dog*>(pa);                   // 能編譯，不檢查 → 拿 Cat 當 Dog 用是未定義行為
Dog* safe = dynamic_cast<Dog*>(pa);
cout << (safe == nullptr) << '\n';                  // 輸出：1（安全地失敗）
```

| | `static_cast` | `dynamic_cast` |
|---|---|---|
| 檢查時機 | 只在編譯時檢查「有沒有繼承關係」 | **執行時** 檢查實際型別 |
| 轉錯了 | 未定義行為 | 回傳 `nullptr` / 丟出 `bad_cast` |
| 成本 | 零 | 要查型別資訊，比較慢 |
| 需要虛擬函式 | 不用 | 要（多型類別） |

### typeid

**是什麼**：取得物件的 **執行期型別資訊**（回傳 `type_info`），可以拿來比較型別。

```cpp
#include <typeinfo>
Animal& r2 = *zoo[0];
cout << (typeid(r2) == typeid(Dog)) << ' ' << (typeid(r2) == typeid(Cat)) << '\n';   // 輸出：1 0
```

（`typeid(x).name()` 也能印出型別名稱，但格式由編譯器決定，GCC 印出的是 `3Dog` 這種編碼過的名字。）

**RTTI (Run-Time Type Information)**：執行期型別資訊，`dynamic_cast` 和 `typeid` 都靠它。

> **設計提醒**：程式裡如果到處都是 `dynamic_cast` / `typeid` 判斷型別再分別處理，通常代表 **設計有問題**：應該把「分別處理」寫成虛擬函式，讓多型自己處理（3.3 的 switch 對比）。

## 6.2 多重繼承 (Multiple Inheritance)

**是什麼**：C++ 允許一個類別有 **多個** 父類別。

**最常見、也最安全的用法：實作多個介面**

```cpp
class Printable {
public:
    virtual ~Printable() = default;
    virtual void print() const = 0;
};
class Serializable {
public:
    virtual ~Serializable() = default;
    virtual string save() const = 0;
};
class Document : public Printable, public Serializable {   // 同時是「可列印的」和「可存檔的」
    string text_;
public:
    Document(string t) : text_(t) {}
    void print() const override { cout << "列印：" << text_ << '\n'; }
    string save() const override { return "DOC:" + text_; }
};

Document doc("hello");
Printable& p = doc;
Serializable& s = doc;
p.print();                         // 輸出：列印：hello
cout << s.save() << '\n';          // 輸出：DOC:hello
```

**兩個父類別有同名成員時**：直接使用會 **模稜兩可**，要指定是哪一個。

```cpp
struct Camera { string name() const { return "camera"; } };
struct Phone  { string name() const { return "phone"; } };
struct SmartPhone : Camera, Phone {};

SmartPhone sp;
// sp.name();                      // ❌ error: request for member 'name' is ambiguous
cout << sp.Camera::name() << ' ' << sp.Phone::name() << '\n';   // 輸出：camera phone
```

## 6.3 🔍 菱形問題與虛擬繼承 (Diamond Problem / Virtual Inheritance)

**菱形問題**：兩個父類別有 **共同的祖先**。

```
        Animal
        /    \
    Mammal  WingedAnimal
        \    /
         Bat
```

```cpp
struct Animal1 { int age = 0; Animal1() { cout << "Animal1 建構\n"; } };
struct Mammal1 : Animal1 {};
struct Winged1 : Animal1 {};
struct Bat1 : Mammal1, Winged1 {};

Bat1 b;
// 輸出：
// Animal1 建構
// Animal1 建構          ← Animal1 被建構了兩次！Bat1 裡有兩份 Animal1
// b.age = 3;            // ❌ error: request for member 'age' is ambiguous（哪一份？）
b.Mammal1::age = 3;      // 要指定經過哪一條路
cout << b.Mammal1::age << ' ' << b.Winged1::age << '\n';   // 輸出：3 0（兩份是獨立的）
```

**虛擬繼承 (virtual inheritance)** 讓共同的祖先只保留 **一份**：

```cpp
struct Animal2 { int age = 0; Animal2() { cout << "Animal2 建構\n"; } };
struct Mammal2 : virtual Animal2 {};      // ← virtual 繼承
struct Winged2 : virtual Animal2 {};
struct Bat2 : Mammal2, Winged2 {};

Bat2 b2;
// 輸出：
// Animal2 建構          ← 只建構一次
b2.age = 3;              // ✅ 只有一份，不再模稜兩可
cout << b2.Mammal2::age << ' ' << b2.Winged2::age << '\n';   // 輸出：3 3（是同一份）
```

`std::iostream` 就是這樣：它同時繼承 `istream` 和 `ostream`，兩者都虛擬繼承 `ios_base`。

**建議**：多重繼承 **只用在繼承多個「介面」**（沒有資料的抽象類別），避免複雜的菱形結構。虛擬繼承有額外的成本，而且建構規則很複雜（最底層的類別要負責建構虛擬基底）。

## 6.4 組合優於繼承 (Composition over Inheritance)

**組合 (composition)**：類別 **擁有** 另一個類別的物件當成員（has-a）。

| | 繼承 (is-a) | 組合 (has-a) |
|---|---|---|
| 關係 | 狗 **是一種** 動物 | 汽車 **有一個** 引擎 |
| 耦合 | 緊：子類別依賴父類別的實作細節，父類別一改子類別可能壞掉 | 鬆：只依賴對方的公開介面 |
| 暴露 | 父類別的公開成員全部變成子類別的公開成員 | 只開放你想開放的 |
| 彈性 | 編譯時就固定 | 可以在執行時替換成員（例如換成另一個實作） |

### 反例：用繼承做 Stack

```cpp
class BadStack : public vector<int> {      // ❌ Stack 不是一種 vector
public:
    void push(int x) { push_back(x); }
    int pop() { int t = back(); pop_back(); return t; }
};
BadStack bs;
bs.push(1); bs.push(2); bs.push(3);
bs.insert(bs.begin(), 99);                 // 😱 使用者可以從底部插入，破壞「只能從頂端操作」的規則
bs[1] = -1;                                // 😱 也可以直接改中間的元素
cout << bs.pop() << ' ' << bs.size() << '\n';   // 輸出：3 3
```

### 正確：用組合

```cpp
class Stack {
    vector<int> data_;                     // ✅ Stack「有一個」vector 來存資料
public:
    void push(int x) { data_.push_back(x); }
    int pop() { int t = data_.back(); data_.pop_back(); return t; }
    bool empty() const { return data_.empty(); }
    size_t size() const { return data_.size(); }
};
Stack st;
st.push(1); st.push(2);
// st.insert(...);                         // ❌ 沒有這個操作：只開放了堆疊該有的操作
cout << st.pop() << ' ' << st.size() << '\n';   // 輸出：2 1
```

標準函式庫的 `std::stack` 就是用組合實作的（內部有一個 `deque`）。

### 組合 + 介面：執行時替換行為

```cpp
class Engine { public: virtual ~Engine() = default; virtual string start() const = 0; };
class GasEngine : public Engine { public: string start() const override { return "轟轟"; } };
class ElectricEngine : public Engine { public: string start() const override { return "嗡~"; } };

class Car {
    unique_ptr<Engine> engine_;            // 組合：Car 有一個 Engine
public:
    Car(unique_ptr<Engine> e) : engine_(std::move(e)) {}
    void start() const { cout << "發動：" << engine_->start() << '\n'; }
    void swap_engine(unique_ptr<Engine> e) { engine_ = std::move(e); }   // 執行時換引擎
};
Car car(make_unique<GasEngine>());
car.start();                               // 輸出：發動：轟轟
car.swap_engine(make_unique<ElectricEngine>());
car.start();                               // 輸出：發動：嗡~
```

如果寫成 `class GasCar : public GasEngine`，就不可能在執行時換引擎了。

## 6.5 🔍 里氏替換原則 (Liskov Substitution Principle, LSP)

**是什麼**：**任何使用父類別的地方，換成子類別都必須能正確運作**。子類別不能違反父類別給使用者的「承諾」。

經典反例：「正方形是一種長方形」在數學上對，但在程式裡 **如果長方形可以分別設定寬和高**，就會出問題：

```cpp
class Rectangle {
protected:
    int w_ = 0, h_ = 0;
public:
    virtual ~Rectangle() = default;
    virtual void set_width(int w)  { w_ = w; }
    virtual void set_height(int h) { h_ = h; }
    int area() const { return w_ * h_; }
};
class Square : public Rectangle {
public:
    void set_width(int w) override  { w_ = h_ = w; }   // 正方形：寬高要一樣
    void set_height(int h) override { w_ = h_ = h; }
};

void stretch(Rectangle& r) {
    r.set_width(10);
    r.set_height(5);
    cout << r.area() << '\n';      // 使用者預期：10 × 5 = 50
}
Rectangle rect; stretch(rect);     // 輸出：50
Square sq;      stretch(sq);       // 輸出：25   😱 設高度時把寬度也改了，違反了 Rectangle 的承諾
```

`Square` 違反了 `Rectangle` 的承諾：「設定寬度不會影響高度」。所以在這個設計下，`Square` **不應該** 繼承 `Rectangle`。

`C08` 的 `Square : Rectangle` 沒有問題，是因為圖形建立之後 **不能修改**（沒有 setter），就不存在這個承諾。

**判斷方法**：is-a 不只是「概念上是一種」，而是「**行為上** 能完全替代」。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 繼承 | Inheritance | 從現有類別延伸出新類別 | 1.1 |
| 基底 / 衍生類別 | Base / Derived Class | 父類別 / 子類別 | 1.1 |
| 基底子物件 | Base Subobject | 子類別物件裡面那份完整的父類別 | 1.1 |
| is-a 關係 | Is-a | 子類別是一種父類別 | 1.2 |
| 向上 / 向下轉型 | Upcast / Downcast | 子轉父（安全、自動）/ 父轉子（要小心） | 1.2 |
| protected | protected | 子類別看得到、外部看不到 | 1.3 |
| 繼承方式 | public / protected / private Inheritance | 決定繼承來的成員權限的上限 | 1.4 |
| 繼承建構子 | Inheriting Constructor | `using Base::Base;` 沿用父類別建構子 | 2.4 |
| 靜態 / 動態繫結 | Static / Dynamic Binding | 編譯時 / 執行時決定呼叫哪個函式 | 3.2 |
| 虛擬函式 | Virtual Function | 會動態繫結的成員函式 | 3.2 |
| 多型 | Polymorphism | 同一介面、各自的實作 | 3.3 |
| 開放封閉原則 | Open-Closed Principle | 新增功能時不用修改舊程式碼 | 3.3 |
| 覆寫 | Override | 子類別重新實作父類別的虛擬函式 | 3.4 |
| final | final | 不能再被繼承 / 覆寫 | 3.4 |
| 虛擬函式表 | vtable / vptr | 實作動態繫結的函式指標表 | 3.6 |
| 純虛擬函式 | Pure Virtual Function `= 0` | 沒有實作，子類別必須實作 | 4.1 |
| 抽象 / 具體類別 | Abstract / Concrete Class | 不能 / 可以建立物件的類別 | 4.1 |
| 樣板方法模式 | Template Method Pattern | 父類別定流程、子類別填細節 | 4.1 |
| 介面 | Interface | 只有純虛擬函式的抽象類別 | 4.2 |
| 虛擬解構子 | Virtual Destructor | 透過父類別指標刪除時必須有 | 4.3 |
| 物件切割 | Object Slicing | 以值複製時子類別部分被切掉 | 5.1 |
| 名稱隱藏 | Name Hiding | 子類別同名函式蓋掉父類別所有同名函式 | 5.2 |
| 執行期型別資訊 | RTTI | dynamic_cast、typeid 的基礎 | 6.1 |
| 多重繼承 | Multiple Inheritance | 一個類別有多個父類別 | 6.2 |
| 菱形問題 | Diamond Problem | 多重繼承時共同祖先出現兩份 | 6.3 |
| 虛擬繼承 | Virtual Inheritance | 讓共同祖先只有一份 | 6.3 |
| 組合 | Composition (has-a) | 擁有另一個物件當成員 | 6.4 |
| 里氏替換原則 | Liskov Substitution Principle | 子類別在行為上要能完全替代父類別 | 6.5 |

---

# 習題

### 題 1：預測輸出

```cpp
struct A { A() { cout << "A"; } ~A() { cout << "a"; } };
struct B : A { B() { cout << "B"; } ~B() { cout << "b"; } };
struct C : B { C() { cout << "C"; } ~C() { cout << "c"; } };
int main() { C x; }
```

### 題 2：預測輸出

```cpp
struct Base {
    void f() { cout << "Bf "; }
    virtual void g() { cout << "Bg "; }
};
struct Derived : Base {
    void f() { cout << "Df "; }
    void g() override { cout << "Dg "; }
};
int main() {
    Derived d;
    Base& r = d;
    Base b = d;
    r.f(); r.g(); b.g(); d.f();
}
```

### 題 3：這段程式有什麼問題？

```cpp
class Logger {
public:
    ~Logger() { }
    virtual void log(const string& s) = 0;
};
class FileLogger : public Logger {
    ofstream file_;
public:
    void log(const string& s) override { file_ << s; }
};
unique_ptr<Logger> lg = make_unique<FileLogger>();
```

### 題 4：為什麼 `d.f(1)` 編譯失敗？

```cpp
struct Base { void f(int) {} };
struct Derived : Base { void f(const char*) {} };
Derived d;
d.f(1);
```

### 題 5：預測輸出

```cpp
struct Base {
    Base() { hello(); }
    virtual void hello() { cout << "Base "; }
};
struct Derived : Base {
    void hello() override { cout << "Derived "; }
};
int main() { Derived d; d.hello(); }
```

### 題 6：下面哪些敘述正確？

```
a) 抽象類別不能有建構子。
b) 抽象類別可以有資料成員和已實作的函式。
c) 子類別沒有實作全部的純虛擬函式時，子類別也不能建立物件。
d) 可以宣告抽象類別的指標和參考。
```

### 題 7：用繼承還是組合？

```
a) Teacher 和 Person
b) Library 和 Book
c) Stack 和 vector（Stack 用 vector 存資料）
d) SavingsAccount 和 Account
```

### 題 8：預測輸出

```cpp
struct P { virtual ~P() = default; virtual void f() const { cout << "P"; } };
struct Q : P { void f() const override { cout << "Q"; } };
struct R : Q { void f() const override { cout << "R"; Q::f(); } };
int main() {
    R r;
    P& a = r;
    Q& b = r;
    a.f(); b.f();
    Q q = r;
    q.f();
}
```

### 題 9：這段程式碼本來想讓 `Derived` 覆寫 `area`，為什麼印出 `0`？加上什麼關鍵字就能讓編譯器抓到錯誤？

```cpp
struct Shape { virtual ~Shape() = default; virtual double area() const { return 0; } };
struct Sq : Shape {
    double s = 2;
    double area() { return s * s; }
};
Sq sq;
const Shape& r = sq;
cout << r.area();
```

### 題 10：預測輸出

```cpp
struct B { virtual ~B() = default; virtual void show(int x = 10) const { cout << "B" << x << ' '; } };
struct D : B { void show(int x = 20) const override { cout << "D" << x << ' '; } };
int main() {
    D d;
    B* pb = &d;
    pb->show();
    d.show();
    pb->show(5);
}
```

### 題 11：下面的程式碼會印出什麼？`dynamic_cast` 換成 `static_cast` 會發生什麼事？

```cpp
struct A { virtual ~A() = default; };
struct B : A { int x = 7; };
struct C : A {};
A* p = new C;
B* q = dynamic_cast<B*>(p);
cout << (q ? "B" : "not B");
delete p;
```

### 題 12：預測輸出

```cpp
struct Item { Item(const char* s) { cout << s; } };
struct Base { Item i{"1"}; Base() { cout << "2"; } };
struct Derived : Base {
    Item j{"3"};
    Item k;
    Derived() : k("4") { cout << "5"; }
};
int main() { Derived d; }
```

---

# 習題解答

**題 1**：`ABCcba`。建構由父到子（A → B → C），解構完全相反（C → B → A）。

**題 2**：`Bf Dg Bg Df`。
- `r.f()`：`f` 不是虛擬函式，依 `r` 的宣告型別 `Base&` → `Bf`。
- `r.g()`：`g` 是虛擬函式，`r` 實際參考 `Derived` → `Dg`。
- `b.g()`：`b` 是 **切割** 後的 `Base` 物件（以值複製），不是透過指標 / 參考 → `Bg`。
- `d.f()`：直接用 `Derived` 物件 → `Df`。

**題 3**：`Logger` 的解構子 **不是 virtual**。`unique_ptr<Logger>` 銷毀時是透過 `Logger*` 刪除，`~FileLogger()` 不會被呼叫，`file_` 不會被正確關閉（而且是未定義行為）。改成 `virtual ~Logger() = default;`。

**題 4**：**名稱隱藏**。`Derived` 定義了 `f`，`Base` 的所有 `f` 都被隱藏，在 `Derived` 的作用域裡只找得到 `f(const char*)`，而 `1` 不能轉成 `const char*`。在 `Derived` 裡加上 `using Base::f;`。

**題 5**：`Base Derived `。建構 `Base` 的部分時，物件還不是 `Derived`，所以建構子裡的 `hello()` 呼叫 `Base::hello`；建構完成後 `d.hello()` 呼叫 `Derived::hello`。

**題 6**：b、c、d 正確。a 錯：抽象類別可以（而且常常需要）有建構子，用來初始化自己的資料成員，由子類別的建構子呼叫（4.1 的 `Employee`）。

**題 7**：
- a) **繼承**：老師是一種人。
- b) **組合**：圖書館有很多書（`vector<Book>`）。
- c) **組合**：Stack 不是一種 vector（如果繼承，使用者就能對 Stack 呼叫 `insert`、`v[3]` 等破壞堆疊規則的操作，6.4 的 `BadStack`）；Stack **用** vector 來存資料。
- d) **繼承**：儲蓄帳戶是一種帳戶（`C09`）。

**題 8**：`RQRQQ`。
- `a.f()`：`a` 實際參考 `R` → `R::f` 印 `R`，再呼叫 `Q::f` 印 `Q`。
- `b.f()`：同上，印 `RQ`。
- `Q q = r;`：**切割** 成一個 `Q` 物件 → `q.f()` 印 `Q`。

**題 9**：`Sq::area()` **少了 `const`**，跟 `Shape::area() const` 的簽章不同，所以它 **沒有覆寫**，只是一個新的函式。透過 `const Shape&` 呼叫的是 `Shape::area`，回傳 `0`。在 `Sq::area` 加上 `override`：`double area() override` 會編譯錯誤 `marked 'override', but does not override`，提醒你補上 `const`。

**題 10**：`D10 D20 D5 `。
- `pb->show()`：函式動態繫結到 `D::show`，但預設參數靜態繫結用 `B` 的 `10`。
- `d.show()`：宣告型別是 `D`，用 `D` 的預設值 `20`。
- `pb->show(5)`：有給引數，沒有預設參數的問題。

**題 11**：印出 `not B`。`p` 實際指向 `C`，不是 `B`，`dynamic_cast` 在執行時發現了，回傳 `nullptr`。換成 `static_cast` 的話，**編譯會通過、而且不會檢查**，`q` 會指向一個其實是 `C` 的物件，之後使用 `q->x` 就是 **未定義行為**（讀到不屬於這個物件的記憶體）。

**題 12**：`12345`。順序：父類別 `Base`（它的成員 `i` → `1`，本體 → `2`）→ 子類別的成員依宣告順序（`j` → `3`、`k` → `4`）→ 子類別本體 → `5`。
