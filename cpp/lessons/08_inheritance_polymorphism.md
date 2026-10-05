# 08. 繼承與多型 (Inheritance & Polymorphism)

> 程式練習：`C08 圖形與多型`、`C09 銀行帳戶系統`
>
> 先備知識：第 07 課「類別、建構子、存取控制」、第 06 課「unique_ptr」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 繼承基礎 | is-a 關係、三種繼承方式、`protected` |
| 第二部分 | 建構與解構的順序 | 誰先建、誰先拆、怎麼呼叫父類別的建構子 |
| 第三部分 | 虛擬函式與多型 | 靜態繫結 vs 動態繫結、`override`、vtable 怎麼運作 |
| 第四部分 | 抽象類別與虛擬解構子 | 純虛擬函式、介面、為什麼解構子一定要 virtual |
| 第五部分 | 繼承的陷阱 | 物件切割、名稱隱藏、建構子裡呼叫虛擬函式、預設參數 |
| 第六部分 | 進階與設計 | `dynamic_cast`、多重繼承與菱形問題、組合 vs 繼承 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：繼承基礎

## 1.1 繼承 (Inheritance)

**白話**：以一個 **現有的類別** 為基礎，建立一個 **新的類別**。新類別自動擁有原本類別的成員，可以再 **增加** 新的成員，或 **改寫** 原有的行為。

- 原本的類別：**基底類別 (base class)** / 父類別 (parent) / 超類別 (superclass)
- 新的類別：**衍生類別 (derived class)** / 子類別 (child) / 次類別 (subclass)

```cpp
class Animal {
public:
    string name;
    void eat() { cout << name << " eats\n"; }
};
class Dog : public Animal {          // Dog 繼承 Animal
public:
    void bark() { cout << name << " barks\n"; }   // 新增的功能
};
Dog d;
d.name = "Rex";
d.eat();     // 繼承來的
d.bark();    // 自己的
```

## 1.2 is-a 關係

**白話**：公開繼承代表「**子類別 是一種 父類別**」。任何需要父類別的地方，都可以放子類別。

**比喻**：「狗 **是一種** 動物」，所以「動物園需要一隻動物」時，給一隻狗是合理的。反過來不行：「需要一隻狗」時不能隨便給一隻動物。

```cpp
void feed(Animal& a);
Dog d;
feed(d);                   // ✅ Dog 是一種 Animal
Animal* p = &d;            // ✅ 父類別指標可以指向子類別物件（向上轉型 upcast）
Dog* q = p;                // ❌ 反過來需要明確轉型（向下轉型 downcast）
```

**判斷要不要用繼承**：問「X 是一種 Y 嗎？」—— 如果答案是「X **有一個** Y」，應該用 **組合**（第 6.3 節）。

## 1.3 protected 與三種繼承方式

**`protected` 成員**：外部看不到，但 **子類別看得到**。

**繼承方式** 決定父類別的成員在子類別裡變成什麼權限：

| 父類別成員 | `public` 繼承 | `protected` 繼承 | `private` 繼承 |
|---|---|---|---|
| `public` | public | protected | private |
| `protected` | protected | protected | private |
| `private` | **看不到** | **看不到** | **看不到** |

**99% 的情況用 `public` 繼承**（表達 is-a）。`private` 繼承表示「用父類別來實作，但不是 is-a」，通常改用組合更清楚。

> ⚠️ `class D : B` 沒寫繼承方式時，**`class` 預設是 `private` 繼承**（`struct` 預設 `public`）。忘了寫 `public` 是常見錯誤：之後 `B* p = &d;` 會編譯失敗。

---

# 第二部分：建構與解構的順序

## 2.1 建構順序：由內而外

1. **父類別** 的建構子
2. **成員變數**（依宣告順序）
3. **子類別** 建構子的本體

## 2.2 解構順序：完全相反

1. **子類別** 解構子的本體
2. 成員變數（依宣告的相反順序）
3. **父類別** 的解構子

**比喻**：蓋房子先打地基（父類別），再蓋牆和裝潢（子類別）；拆房子則先拆裝潢，最後才拆地基。

```cpp
struct Base { Base() { cout << "B "; } ~Base() { cout << "~B "; } };
struct Member { Member() { cout << "M "; } ~Member() { cout << "~M "; } };
struct Derived : Base {
    Member m;
    Derived() { cout << "D "; }
    ~Derived() { cout << "~D "; }
};
{ Derived d; }    // 輸出：B M D ~D ~M ~B
```

## 2.3 呼叫父類別的建構子

父類別沒有預設建構子時，子類別 **必須在初始化串列裡呼叫** 它：

```cpp
class Rectangle : public Shape {
protected:
    double w_, h_;
public:
    Rectangle(double w, double h) : w_(w), h_(h) {}
};
class Square : public Rectangle {
public:
    explicit Square(double s) : Rectangle(s, s) {}   // C08 的寫法
};
```

**繼承建構子**：子類別沒有新增需要初始化的成員時，可以直接沿用父類別的建構子：

```cpp
class CalcError : public runtime_error {
public:
    using runtime_error::runtime_error;   // C13 的寫法
};
```

---

# 第三部分：虛擬函式與多型

## 3.1 問題：沒有 virtual 時會怎樣？

```cpp
class Animal {
public:
    void speak() { cout << "...\n"; }
};
class Dog : public Animal {
public:
    void speak() { cout << "Woof\n"; }
};
Animal* p = new Dog;
p->speak();     // 印出 "..."，不是 "Woof"！
```

## 3.2 靜態繫結 vs 動態繫結 (Static / Dynamic Binding)

- **靜態繫結**（早繫結）：**編譯時** 根據指標 / 參考的 **宣告型別** 決定呼叫哪個函式。`p` 的型別是 `Animal*`，所以呼叫 `Animal::speak`。
- **動態繫結**（晚繫結）：**執行時** 根據指標 / 參考 **實際指向的物件** 決定呼叫哪個函式。

加上 `virtual` 就變成動態繫結：

```cpp
class Animal {
public:
    virtual void speak() { cout << "...\n"; }
    virtual ~Animal() = default;
};
class Dog : public Animal {
public:
    void speak() override { cout << "Woof\n"; }
};
class Cat : public Animal {
public:
    void speak() override { cout << "Meow\n"; }
};

vector<unique_ptr<Animal>> zoo;
zoo.push_back(make_unique<Dog>());
zoo.push_back(make_unique<Cat>());
for (auto& a : zoo) a->speak();     // Woof、Meow
```

## 3.3 多型 (Polymorphism)

**白話**：**同一段程式碼**（`a->speak()`）面對 **不同型別的物件**，會執行 **各自的版本**。

**比喻**：老師對全班說「交作業」，每個同學交的是自己的作業。老師不需要知道每個人寫了什麼，只要說同一句話。

**多型的好處**：新增一種動物（例如 `Bird`）時，**完全不用修改** 走訪動物園的那段程式碼。這叫 **開放封閉原則**（對擴充開放、對修改封閉，第 09 課）。

**多型只透過指標或參考才會發生**。直接用物件呼叫（`Dog d; d.speak();`）一律是靜態繫結。

## 3.4 override 和 final

```cpp
class Dog : public Animal {
public:
    void speak() override;          // 明確說「我要覆寫父類別的虛擬函式」
    void speek() override;          // ❌ 編譯錯誤：父類別沒有 speek（打錯字被抓到了）
    void speak() const override;    // ❌ 編譯錯誤：簽章不同（多了 const）
};
class Puppy final : public Dog {};  // final：不能再被繼承
```

**沒有 `override` 的話**，打錯函式名稱或簽章不同，編譯器會以為你在定義一個 **新的** 函式，多型就默默失效了。**覆寫時一律加 `override`**。

## 3.5 🔍 虛擬函式怎麼運作：vtable

編譯器通常這樣實作虛擬函式：

1. 每個 **有虛擬函式的類別** 有一張 **虛擬函式表 (vtable)**：一個函式指標陣列，記錄這個類別每個虛擬函式的實際位址。
2. 每個 **物件** 多一個隱藏的指標 **vptr**，指向自己類別的 vtable。
3. 呼叫 `p->speak()` 時：透過 `p` 找到物件 → 讀 vptr → 找到 vtable → 取出 `speak` 的位址 → 呼叫。

```
Dog 物件                Dog 的 vtable
+--------+             +----------------+
| vptr ──┼───────────▶ | &Dog::speak    |
| name   |             | &Dog::~Dog     |
+--------+             +----------------+

Cat 物件                Cat 的 vtable
+--------+             +----------------+
| vptr ──┼───────────▶ | &Cat::speak    |
| name   |             | &Cat::~Cat     |
+--------+             +----------------+
```

**比喻**：每個員工身上帶著一張「我的部門的工作手冊」（vptr → vtable）。主管只要說「照手冊做」，每個人就照自己部門的手冊執行。

**成本**：
- 每個物件多一個指標（8 bytes）。
- 每次呼叫多一次間接存取，而且編譯器通常 **無法內聯 (inline)** 虛擬函式。
- 所以 C++ **預設不是虛擬的**：不需要多型的地方不用付這個代價。

---

# 第四部分：抽象類別與虛擬解構子

## 4.1 純虛擬函式與抽象類別 (Pure Virtual / Abstract Class)

**白話**：
- **純虛擬函式**：只宣告、**不提供實作**，寫成 `= 0`。表示「子類別 **一定要** 自己實作」。
- **抽象類別**：有至少一個純虛擬函式的類別。**不能建立物件**，只能當作父類別。

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;       // 純虛擬
    virtual string name() const = 0;
};
Shape s;                 // ❌ 編譯錯誤：抽象類別不能建立物件
unique_ptr<Shape> p = make_unique<Circle>(1.0);   // ✅ 可以用指標指向子類別
```

**比喻**：「交通工具」是一個抽象概念 —— 你不能買一台「交通工具」，只能買汽車、機車、腳踏車。但你可以說「我需要一台交通工具」。

子類別沒有實作全部的純虛擬函式時，它 **也是抽象類別**。

## 4.2 介面 (Interface)

**白話**：**只有** 純虛擬函式（加上虛擬解構子）、沒有資料成員的抽象類別。它只規定「**能做什麼**」，完全不管「怎麼做」。

C++ 沒有 `interface` 關鍵字，用全部都是純虛擬函式的類別來表達。第 09 課會用介面來設計 ADT。

## 4.3 虛擬解構子 (Virtual Destructor)

**規則：只要類別會被當作父類別、透過父類別指標刪除，解構子就必須是 `virtual`。**

```cpp
class Base {
public:
    ~Base() { }                 // ❌ 不是 virtual
};
class Derived : public Base {
    vector<int> data;           // 有資源
};
Base* p = new Derived;
delete p;                       // ❌ 只呼叫了 ~Base()，~Derived() 沒被呼叫
                                //    → data 沒有被釋放；而且這是未定義行為
```

加上 `virtual ~Base() = default;`，`delete p` 就會先呼叫 `~Derived()`，再呼叫 `~Base()`。

`unique_ptr<Base>` 也一樣：它內部就是 `delete` 一個 `Base*`，沒有虛擬解構子同樣出事。

**經驗法則**：有任何虛擬函式的類別，**解構子就要是 virtual**。

---

# 第五部分：繼承的陷阱

## 5.1 物件切割 (Object Slicing)

**白話**：把子類別物件 **以值複製** 給父類別變數時，**只有父類別的部分被複製**，子類別多出來的資料和行為全部被「切掉」。

```cpp
Dog d;
Animal a = d;            // 切割！a 只是一個 Animal
a.speak();               // "..."（就算 speak 是 virtual 也一樣）

void bad(Animal a) { a.speak(); }     // 傳值 → 切割
void good(Animal& a) { a.speak(); }   // 傳參考 → 多型正常

vector<Animal> zoo;      // 存進去的全部被切割成 Animal
zoo.push_back(Dog());
```

**比喻**：把一張全彩照片用黑白影印機印出來，顏色資訊就永遠不見了。

**規則**：多型的物件 **永遠用指標或參考傳遞**，存進容器時用 `vector<unique_ptr<Base>>`。把父類別設成抽象類別也能防止切割（抽象類別無法以值存在）。

## 5.2 名稱隱藏 (Name Hiding)

**白話**：子類別定義了一個跟父類別 **同名** 的函式，父類別 **所有同名的函式**（包括其他多載版本）都會被 **隱藏**。

```cpp
class Base {
public:
    void f(int x);
    void f(double x);
};
class Derived : public Base {
public:
    void f(string s);       // 隱藏了 Base 的兩個 f
};
Derived d;
d.f(1);       // ❌ 編譯錯誤：在 Derived 裡只找得到 f(string)

class Derived2 : public Base {
public:
    using Base::f;          // 把父類別的 f 都帶進來
    void f(string s);
};
```

## 5.3 建構子 / 解構子裡呼叫虛擬函式

**白話**：在 **父類別的建構子** 裡呼叫虛擬函式，**不會** 呼叫到子類別的版本。

```cpp
class Base {
public:
    Base() { init(); }                       // 呼叫的是 Base::init
    virtual void init() { cout << "Base\n"; }
};
class Derived : public Base {
    string s_ = "ready";
public:
    void init() override { cout << s_ << '\n'; }
};
Derived d;   // 印出 "Base"
```

**原因**：父類別建構子執行時，子類別的部分 **還沒建立**（`s_` 還沒初始化）。如果呼叫到子類別的版本，就會存取未初始化的成員。所以 C++ 規定：在建構 / 解構期間，物件的動態型別就是 **目前正在建構的那一層**。

**比喻**：房子還在打地基，就不能請住戶搬進來住。

## 5.4 🔍 虛擬函式的預設參數是靜態繫結的

```cpp
class Base { public: virtual void show(int x = 1) { cout << "B" << x; } };
class Derived : public Base { public: void show(int x = 2) override { cout << "D" << x; } };
Base* p = new Derived;
p->show();     // 印出 "D1"：函式是 Derived 的（動態），預設值是 Base 的（靜態）
```

**規則**：覆寫虛擬函式時，**不要改變預設參數**。

---

# 第六部分：進階與設計

## 6.1 dynamic_cast 與 RTTI

**白話**：把父類別指標 **安全地** 轉成子類別指標。執行時檢查實際型別：成功回傳指標，失敗回傳 `nullptr`（參考版本則丟出 `bad_cast`）。只能用在 **有虛擬函式** 的類別（多型類別）。

```cpp
Animal* a = get_animal();
if (Dog* d = dynamic_cast<Dog*>(a)) {
    d->bark();                 // 確定是 Dog 才呼叫
}
```

`static_cast<Dog*>(a)` 也能編譯，但 **不檢查**：`a` 其實是 `Cat` 時就是未定義行為。

**RTTI (Run-Time Type Information)**：執行期型別資訊，`dynamic_cast` 和 `typeid` 都靠它。

> 程式裡如果到處都是 `dynamic_cast` 判斷型別，通常代表 **設計有問題**：應該把行為寫成虛擬函式，讓多型自己處理。

## 6.2 多重繼承與菱形問題 (Multiple Inheritance / Diamond Problem)

C++ 允許一個類別有 **多個** 父類別：

```cpp
class Printable { public: virtual void print() const = 0; };
class Serializable { public: virtual string save() const = 0; };
class Document : public Printable, public Serializable { ... };   // 實作兩個介面：常見且安全
```

**菱形問題**：

```
        Animal
        /    \
    Mammal  WingedAnimal
        \    /
         Bat
```

`Bat` 裡會有 **兩份** `Animal` 的成員，`bat.name` 不知道是哪一份（模稜兩可）。

**虛擬繼承 (virtual inheritance)** 讓共同的祖先只保留一份：

```cpp
class Mammal : virtual public Animal { };
class WingedAnimal : virtual public Animal { };
class Bat : public Mammal, public WingedAnimal { };   // 只有一份 Animal
```

**建議**：多重繼承 **只用在繼承多個「介面」**（沒有資料的抽象類別），避免複雜的菱形結構。

## 6.3 組合優於繼承 (Composition over Inheritance)

**組合 (composition)**：類別 **擁有** 另一個類別的物件當成員（has-a）。

| | 繼承 (is-a) | 組合 (has-a) |
|---|---|---|
| 關係 | 狗 **是一種** 動物 | 汽車 **有一個** 引擎 |
| 耦合 | 緊：子類別依賴父類別的實作細節 | 鬆：只依賴對方的公開介面 |
| 彈性 | 編譯時就固定 | 可以在執行時替換成員 |

```cpp
class Car : public Engine { };      // ❌ 汽車不是一種引擎
class Car { Engine engine_; };      // ✅ 汽車有一個引擎
```

### 🔍 里氏替換原則 (Liskov Substitution Principle)

**白話**：**任何使用父類別的地方，換成子類別都必須能正確運作**。

經典反例：「正方形是一種長方形」在數學上對，但在程式裡 **如果長方形可以分別設定寬和高**，就會出問題：

```cpp
void stretch(Rectangle& r) {
    r.set_width(10);
    r.set_height(5);
    assert(r.area() == 50);    // 傳入 Square 時失敗：設高度時把寬度也改了
}
```

`C08` 的 `Square : Rectangle` 沒有問題，是因為圖形建立之後 **不能修改**（沒有 setter）。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 繼承 | Inheritance | 從現有類別延伸出新類別 | 1.1 |
| 基底 / 衍生類別 | Base / Derived Class | 父類別 / 子類別 | 1.1 |
| is-a 關係 | Is-a | 子類別是一種父類別 | 1.2 |
| 向上 / 向下轉型 | Upcast / Downcast | 子轉父（安全）/ 父轉子（要小心） | 1.2 |
| protected | protected | 子類別看得到、外部看不到 | 1.3 |
| 靜態 / 動態繫結 | Static / Dynamic Binding | 編譯時 / 執行時決定呼叫哪個函式 | 3.2 |
| 虛擬函式 | Virtual Function | 會動態繫結的成員函式 | 3.2 |
| 多型 | Polymorphism | 同一介面、各自的實作 | 3.3 |
| 覆寫 | Override | 子類別重新實作父類別的虛擬函式 | 3.4 |
| 虛擬函式表 | vtable / vptr | 實作動態繫結的函式指標表 | 3.5 |
| 純虛擬函式 | Pure Virtual Function `= 0` | 沒有實作，子類別必須實作 | 4.1 |
| 抽象類別 | Abstract Class | 不能建立物件的類別 | 4.1 |
| 介面 | Interface | 只有純虛擬函式的抽象類別 | 4.2 |
| 虛擬解構子 | Virtual Destructor | 透過父類別指標刪除時必須有 | 4.3 |
| 物件切割 | Object Slicing | 以值複製時子類別部分被切掉 | 5.1 |
| 名稱隱藏 | Name Hiding | 子類別同名函式蓋掉父類別所有同名函式 | 5.2 |
| 執行期型別資訊 | RTTI | dynamic_cast、typeid 的基礎 | 6.1 |
| 菱形問題 | Diamond Problem | 多重繼承時共同祖先出現兩份 | 6.2 |
| 虛擬繼承 | Virtual Inheritance | 讓共同祖先只有一份 | 6.2 |
| 組合 | Composition (has-a) | 擁有另一個物件當成員 | 6.3 |
| 里氏替換原則 | Liskov Substitution Principle | 子類別要能完全替代父類別 | 6.3 |

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

**題 6**：b、c、d 正確。a 錯：抽象類別可以（而且常常需要）有建構子，用來初始化自己的資料成員，由子類別的建構子呼叫。

**題 7**：
- a) **繼承**：老師是一種人。
- b) **組合**：圖書館有很多書（`vector<Book>`）。
- c) **組合**：Stack 不是一種 vector（如果繼承，使用者就能對 Stack 呼叫 `insert`、`v[3]` 等破壞堆疊規則的操作）；Stack **用** vector 來存資料。
- d) **繼承**：儲蓄帳戶是一種帳戶（`C09`）。

---

# 程式練習

- **`C08 圖形與多型`**：抽象類別 `Shape`、三層繼承（`Square : Rectangle : Shape`）、用 `vector<unique_ptr<Shape>>` 存不同的圖形。
- **`C09 銀行帳戶系統`**：用抽象類別定義帳戶的介面，兩種帳戶各自實作不同的規則。
