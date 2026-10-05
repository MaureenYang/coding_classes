# 09. 抽象資料型別與程式設計 (ADT & Design)

> 程式練習：`C09 銀行帳戶系統`
>
> 先備知識：第 07 課「封裝、不變量」、第 08 課「抽象類別、多型」。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | ADT 是什麼 | 「規格」和「實作」為什麼要分開 |
| 第二部分 | 介面與實作分離 | 標頭檔 / 原始檔、抽象類別、同一個 ADT 的多種實作 |
| 第三部分 | 契約式設計 | 前置條件、後置條件、不變量，違反時怎麼辦 |
| 第四部分 | 設計原則 | SOLID、高內聚低耦合，各用一句話說明 |
| 第五部分 | 案例：設計銀行系統 | 從需求一步一步設計出 `C09` 的類別 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：ADT 是什麼

## 1.1 抽象資料型別 (Abstract Data Type, ADT)

**白話**：用 **「能做哪些操作、每個操作的效果是什麼」** 來定義一種資料型別，**完全不提** 它內部怎麼存、怎麼實作。

**比喻**：電視遙控器的說明書寫著「按 + 音量變大、按 CH▲ 換下一台」，但不會告訴你遙控器裡的電路怎麼設計。只要符合說明書，用紅外線還是藍牙實作都可以。

## 1.2 一個 ADT 的規格長什麼樣子

以 **Stack ADT** 為例：

| 操作 | 前置條件 | 效果（後置條件） | 複雜度要求 |
|---|---|---|---|
| `push(x)` | 無 | `x` 成為頂端元素，`size` 加 1 | `O(1)` 攤銷 |
| `pop()` | **非空** | 移除頂端元素，`size` 減 1 | `O(1)` |
| `top()` | **非空** | 回傳頂端元素，不改變 stack | `O(1)` |
| `size()` | 無 | 回傳元素個數 | `O(1)` |
| `empty()` | 無 | `size() == 0` | `O(1)` |

**公理 (axioms)**（描述操作之間的關係）：
- `push(x)` 之後 `top()` 等於 `x`。
- `push(x)` 之後再 `pop()`，stack 回到原本的狀態。

注意規格裡 **沒有提到** 陣列、指標、節點 —— 這些都是 **實作** 的事。

## 1.3 為什麼要分開規格和實作？

1. **使用者不需要懂實作**：用 `std::map` 不需要懂紅黑樹。
2. **實作可以替換**：發現用陣列太慢，改成別的實作，**使用者的程式碼一行都不用改**。
3. **可以分工**：一個人寫實作，其他人照著規格寫使用它的程式。
4. **容易測試**：照著規格寫測試，任何實作都要通過同一套測試。

**資料結構路線** 的每一題（`03_my_vector`、`12_binary_heap`……）其實就是：「題目給你 ADT 的規格，請你寫出實作」。

---

# 第二部分：介面與實作分離

## 2.1 介面 (Interface) vs 實作 (Implementation)

- **介面**：外界看得到、可以使用的部分（公開的函式宣告）。
- **實作**：內部怎麼做到的（私有成員、函式本體）。

C++ 有好幾種層次的分離：

| 方式 | 分離了什麼 |
|---|---|
| `public` / `private` | 同一個類別裡，哪些能用、哪些不能碰 |
| 標頭檔 `.h` / 原始檔 `.cpp` | 宣告和定義放在不同檔案（第 14 課） |
| 抽象類別（純虛擬函式） | 規格和 **多種** 實作，執行時決定用哪一種 |
| 模板 + 概念 (concepts) | 規格和多種實作，**編譯時** 決定（第 10 課） |

## 2.2 用抽象類別表達 ADT

```cpp
// 規格：任何 Stack 都要能做這些事
class IntStack {
public:
    virtual ~IntStack() = default;
    virtual void push(int x) = 0;
    virtual void pop() = 0;           // 前置條件：!empty()
    virtual int top() const = 0;      // 前置條件：!empty()
    virtual size_t size() const = 0;
    bool empty() const { return size() == 0; }   // 可以用其他操作組合出來的，直接實作
};

// 實作一：陣列
class ArrayStack : public IntStack {
    vector<int> v_;
public:
    void push(int x) override { v_.push_back(x); }
    void pop() override { v_.pop_back(); }
    int top() const override { return v_.back(); }
    size_t size() const override { return v_.size(); }
};

// 實作二：鏈結串列
class ListStack : public IntStack {
    struct Node { int val; unique_ptr<Node> next; };
    unique_ptr<Node> head_;
    size_t n_ = 0;
public:
    void push(int x) override { head_ = make_unique<Node>(Node{x, std::move(head_)}); n_++; }
    void pop() override { head_ = std::move(head_->next); n_--; }
    int top() const override { return head_->val; }
    size_t size() const override { return n_; }
};

// 使用者只依賴「規格」
int sum_and_clear(IntStack& s) {
    int total = 0;
    while (!s.empty()) { total += s.top(); s.pop(); }
    return total;
}
```

`sum_and_clear` 不知道、也不在乎傳進來的是 `ArrayStack` 還是 `ListStack`。

## 2.3 🔍 靜態多型 vs 動態多型

同樣的事情也可以用 **模板** 做：

```cpp
template <class Stack>
int sum_and_clear(Stack& s) { ... }   // 任何有 top / pop / empty 的型別都可以
```

| | 動態多型（虛擬函式） | 靜態多型（模板） |
|---|---|---|
| 決定時機 | 執行時 | 編譯時 |
| 速度 | 有虛擬呼叫的成本 | 可以內聯，最快 |
| 能放進同一個容器 | ✅ `vector<unique_ptr<Base>>` | ❌ 每種型別是不同的實例 |
| 規格檢查 | 抽象類別（編譯器強制） | C++20 concepts，或沒寫對時噴出很長的錯誤 |

**選擇**：要在 **執行時** 混用不同型別（例如讀檔決定要建立哪種帳戶）→ 虛擬函式；型別在編譯時就確定、要求效能 → 模板。STL 選擇了模板。

---

# 第三部分：契約式設計 (Design by Contract)

## 3.1 三種契約

**白話**：把函式想成「**呼叫者** 和 **函式** 之間的契約」。

| 契約 | 英文 | 誰負責 | 例子（`pop()`） |
|---|---|---|---|
| **前置條件** | Precondition | **呼叫者** 要保證 | stack 不是空的 |
| **後置條件** | Postcondition | **函式** 要保證 | 頂端元素被移除，size 減 1 |
| **不變量** | Class Invariant | **類別** 在每個公開函式前後都要保證 | `0 ≤ size ≤ capacity` |

**比喻**：租車契約。**你** 要保證有駕照、會還車（前置條件）；**租車公司** 要保證車子能開、有加滿油（後置條件）；這台車 **任何時候** 都要有保險（不變量）。

## 3.2 違反前置條件時怎麼辦？

| 做法 | 什麼時候用 | 例子 |
|---|---|---|
| **未定義行為**（不檢查） | 追求效能、而且呼叫者「應該知道」的條件 | `vector::operator[]`、`stack::top()` 空的時候 |
| **assert** | 開發時抓 bug；發布版本關掉 | 內部函式的參數檢查 |
| **丟出例外** | 錯誤可能在正常使用中發生，呼叫者需要處理 | `vector::at()` 越界丟 `out_of_range` |
| **回傳錯誤碼 / `optional` / `bool`** | 「失敗」是常見的正常情況 | `map::find` 回傳 `end()`、`C09` 的提款失敗 |

**判斷原則**：
- 這個錯誤是 **程式寫錯了**（bug）→ `assert` 或 UB。
- 這個錯誤是 **外部世界造成的**（使用者輸入錯誤、檔案不存在、餘額不足）→ 例外或錯誤回傳值。

```cpp
#include <cassert>
void ArrayStack::pop() {
    assert(!v_.empty() && "pop on empty stack");   // 開發時抓 bug
    v_.pop_back();
}
```

`assert` 在定義了 `NDEBUG` 時（通常是發布版本）會被完全移除。

## 3.3 維護不變量

**規則**：
1. **建構子** 建立不變量（建構失敗就丟例外，不要產生一個不合法的物件）。
2. **每個公開的成員函式**：進入時可以假設不變量成立，**離開時必須讓不變量成立**。
3. 資料成員設為 `private`，外界無法破壞不變量。

```cpp
class SavingsAccount {
    long long balance_ = 0;    // 不變量：balance_ >= 0
public:
    bool withdraw(long long amt) {
        if (amt <= 0 || balance_ - amt < 0) return false;   // 會破壞不變量 → 拒絕，狀態不變
        balance_ -= amt;
        return true;
    }
};
```

開發時可以寫一個 `check_invariant()`，在每個成員函式結尾 `assert` 它，很快就能抓到破壞不變量的 bug。

---

# 第四部分：設計原則

## 4.1 高內聚、低耦合 (High Cohesion, Low Coupling)

- **內聚 (cohesion)**：一個類別 **內部** 的東西是否都在做 **同一件事**。越高越好。
- **耦合 (coupling)**：不同類別之間 **互相依賴** 的程度。越低越好。

**比喻**：好的公司部門：每個部門專注於自己的工作（高內聚），部門之間只透過正式的窗口溝通（低耦合）。一個部門改組，不會讓其他部門跟著大亂。

## 4.2 SOLID 原則

| 原則 | 英文 | 一句話 | 違反的例子 |
|---|---|---|---|
| **S** 單一職責 | Single Responsibility | 一個類別只有 **一個** 改變的理由 | `Account` 同時負責計算利息、寫入資料庫、產生 PDF 報表 |
| **O** 開放封閉 | Open/Closed | 對 **擴充** 開放，對 **修改** 封閉 | 每加一種圖形，就要去改 `switch (type)` 的計算面積函式 |
| **L** 里氏替換 | Liskov Substitution | 子類別要能 **完全替代** 父類別 | 可以分別設寬高的 `Square : Rectangle`（第 08 課） |
| **I** 介面隔離 | Interface Segregation | 不要強迫使用者依賴 **用不到** 的函式 | 一個巨大的 `Device` 介面同時有 `print()`、`scan()`、`fax()`，只會印的印表機也要實作 `fax()` |
| **D** 依賴反轉 | Dependency Inversion | 依賴 **抽象**（介面），不要依賴 **具體實作** | 報表類別直接 `new MySQLDatabase()`，換成 PostgreSQL 就要改報表的程式碼 |

**開放封閉原則的例子**：

```cpp
// ❌ 違反：每加一種圖形就要改這個函式
double area(const ShapeData& s) {
    switch (s.type) {
        case CIRCLE: return PI * s.r * s.r;
        case RECT: return s.w * s.h;
        // 加三角形要回來改這裡
    }
}
// ✅ 符合：加新圖形只要新增一個類別，現有的程式碼不用動
class Shape { public: virtual double area() const = 0; };
class Triangle : public Shape { double area() const override { ... } };
```

## 4.3 其他常見原則

| 原則 | 一句話 |
|---|---|
| **DRY** (Don't Repeat Yourself) | 同樣的邏輯只寫一次（例如用 `+=` 實作 `+`，第 07 課） |
| **KISS** (Keep It Simple, Stupid) | 能簡單就不要複雜 |
| **YAGNI** (You Aren't Gonna Need It) | 不要為了「以後可能會用到」而寫現在用不到的功能 |
| **最少驚訝原則** (Least Astonishment) | 介面的行為要符合使用者的直覺（`+` 就該是加法） |

> 原則是 **指引**，不是法律。過度設計（為了一個小程式寫十層抽象）和完全不設計一樣糟。

---

# 第五部分：案例：設計銀行系統（C09）

## 5.1 第一步：找出名詞和動詞

需求：「銀行有 **儲蓄帳戶** 和 **支票帳戶**。可以 **開戶**、**存款**、**提款**、**轉帳**、**月底結算**、**查詢餘額**。儲蓄帳戶不能透支、月底有利息；支票帳戶可以透支到額度、負餘額時月底扣手續費。」

- **名詞 → 類別候選**：銀行、帳戶、儲蓄帳戶、支票帳戶。
- **動詞 → 操作候選**：開戶、存款、提款、轉帳、結算、查詢。

## 5.2 第二步：找出 is-a 和 has-a

- 儲蓄帳戶 **是一種** 帳戶 → 繼承。
- 支票帳戶 **是一種** 帳戶 → 繼承。
- 銀行 **有很多** 帳戶 → 組合：`map<string, unique_ptr<Account>>`。

## 5.3 第三步：哪些行為相同、哪些不同？

| 操作 | 兩種帳戶相同？ | 放在哪裡 |
|---|---|---|
| 存款 | 相同 | `Account` 的一般成員函式 |
| 查詢餘額 | 相同 | `Account` 的一般成員函式 |
| **能不能提款** | **不同**（不變量不同） | `Account` 的 **純虛擬函式** `canWithdraw` |
| **月底結算** | **不同** | 純虛擬函式 `monthEnd` |
| 型別名稱 | 不同 | 純虛擬函式 `type` |
| 轉帳 | 涉及兩個帳戶 | **銀行** 的責任（單一職責：帳戶不應該知道其他帳戶） |

## 5.4 第四步：決定錯誤處理

- 帳號不存在、金額不合法、餘額不足：是 **正常使用中會發生的錯誤** → 回傳錯誤訊息，狀態不變。
- 轉帳要 **原子性**：先檢查所有條件，全部通過才修改（第 13 課的「強例外保證」也是同樣的想法）。

## 5.5 結果

```cpp
class Account {                          // 抽象：定義所有帳戶的共同介面
protected:
    long long balance_ = 0;
public:
    virtual ~Account() = default;
    long long balance() const { return balance_; }
    void deposit(long long amt) { balance_ += amt; }
    void withdraw(long long amt) { balance_ -= amt; }        // 前置條件：canWithdraw(amt)
    virtual bool canWithdraw(long long amt) const = 0;       // 不同帳戶的不變量
    virtual void monthEnd() = 0;
    virtual string type() const = 0;
};
```

**新增第三種帳戶**（例如定期存款：結算前不能提款）時，只要新增一個類別實作這三個虛擬函式，**銀行的程式碼完全不用改** —— 這就是開放封閉原則。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 抽象資料型別 | ADT | 用操作來定義的資料型別，不管實作 | 1.1 |
| 公理 | Axiom | 描述操作之間關係的規則 | 1.2 |
| 介面 / 實作 | Interface / Implementation | 外界看得到的 / 內部怎麼做 | 2.1 |
| 靜態 / 動態多型 | Static / Dynamic Polymorphism | 模板（編譯時）/ 虛擬函式（執行時） | 2.3 |
| 契約式設計 | Design by Contract | 用前置、後置條件和不變量描述函式 | 3.1 |
| 前置條件 | Precondition | 呼叫者要保證的條件 | 3.1 |
| 後置條件 | Postcondition | 函式要保證的結果 | 3.1 |
| 類別不變量 | Class Invariant | 物件隨時都要成立的條件 | 3.1 |
| 斷言 | Assertion | 開發時檢查條件，不成立就停止 | 3.2 |
| 內聚 / 耦合 | Cohesion / Coupling | 內部專注程度 / 互相依賴程度 | 4.1 |
| SOLID | SOLID | 五個物件導向設計原則 | 4.2 |
| 開放封閉原則 | Open/Closed Principle | 擴充不用修改現有程式 | 4.2 |
| 依賴反轉原則 | Dependency Inversion | 依賴抽象而不是具體實作 | 4.2 |
| DRY / KISS / YAGNI | — | 不重複 / 保持簡單 / 不做用不到的 | 4.3 |
| 原子性 | Atomicity | 要嘛全部成功，要嘛完全沒發生 | 5.4 |

---

# 習題

### 題 1：寫出 Queue ADT 的規格

列出操作、前置條件、後置條件，以及至少兩條公理。

### 題 2：下面哪些是「實作細節」，不應該出現在 ADT 規格裡？

```
a) push 之後 size 加 1
b) 內部用環狀陣列存資料
c) top() 的時間複雜度是 O(1)
d) 容量滿了會配置兩倍的空間
e) 對空的 stack 呼叫 pop 是前置條件違反
```

### 題 3：選擇錯誤處理方式（UB / assert / 例外 / 回傳值）

```
a) 使用者輸入的日期格式錯誤
b) 內部函式收到負數長度（呼叫它的程式應該保證不會發生）
c) 開啟的設定檔不存在
d) 在 hash table 裡查詢不存在的 key
e) 高效能矩陣運算中的索引越界
```

### 題 4：這個類別違反了哪個 SOLID 原則？怎麼改？

```cpp
class Report {
public:
    void calculate();
    void print_to_console();
    void save_to_file(const string& path);
    void send_email(const string& to);
};
```

### 題 5：這段程式違反了哪個原則？怎麼改？

```cpp
double pay(const Employee& e) {
    if (e.type == "fulltime") return e.salary;
    if (e.type == "parttime") return e.hours * e.rate;
    if (e.type == "intern") return 1000;
    return 0;
}
```

### 題 6：`transfer(a, b, amt)` 為什麼不能寫成下面這樣？

```cpp
void transfer(Account& a, Account& b, long long amt) {
    a.withdraw(amt);               // 會檢查並在失敗時丟出例外
    b.deposit(amt);                // 假設 b 有存款上限，超過會丟出例外
}
```

---

# 習題解答

**題 1**（參考答案）：

| 操作 | 前置條件 | 後置條件 |
|---|---|---|
| `enqueue(x)` | 無 | `x` 加到尾端，`size` 加 1 |
| `dequeue()` | 非空 | 移除最前面的元素，`size` 減 1 |
| `front()` | 非空 | 回傳最前面的元素，不改變 queue |
| `size()` / `empty()` | 無 | 回傳元素個數 / 是否為空 |

公理：
- 對空的 queue `enqueue(x)` 之後，`front()` 等於 `x`。
- 非空的 queue `enqueue(x)` 之後，`front()` 不變。
- 依序 `enqueue(a)`、`enqueue(b)` 之後，`dequeue()` 會先移除 `a`（先進先出）。

**題 2**：b 和 d 是實作細節。a、e 是行為規格；c（複雜度要求）**可以** 是規格的一部分 —— 例如 C++ 標準就規定了 `vector::push_back` 必須是攤銷 `O(1)`，這會限制可行的實作方式。

**題 3**：
- a) **例外或回傳值**：外部輸入錯誤，是正常會發生的情況。
- b) **assert**：這是程式的 bug。
- c) **例外**（或回傳值）：外部環境造成的錯誤。
- d) **回傳值**：「找不到」是正常結果（`find` 回傳 `end()` 或 `optional`）。
- e) **UB**（不檢查）或開發時的 `assert`：為了效能，呼叫者負責保證。

**題 4**：違反 **單一職責原則**：計算、顯示、存檔、寄信是四個不同的改變理由（換一種輸出格式、換存檔位置、換郵件伺服器都要改這個類別）。拆成 `Report`（只負責資料與計算）、`ReportPrinter`、`ReportSaver`、`ReportMailer`。

**題 5**：違反 **開放封閉原則**：每加一種員工都要修改 `pay`（而且同樣的 `if` 可能散落在很多函式裡）。改成抽象類別 `Employee` 有純虛擬函式 `pay()`，每種員工各自實作，新增員工類型時只要新增類別。

**題 6**：不是 **原子操作**。如果 `withdraw` 成功、`deposit` 丟出例外，錢已經從 `a` 扣掉卻沒有存進 `b` —— 錢憑空消失了。應該 **先檢查所有條件**（`a` 能提款、`b` 能存款），全部通過才修改兩邊；或是在 `deposit` 失敗時把錢存回 `a`（回滾 rollback）。

---

# 程式練習

- **`C09 銀行帳戶系統`**：照著第五部分的設計實作。注意錯誤的檢查順序和轉帳的原子性。
