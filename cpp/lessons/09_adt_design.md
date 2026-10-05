# 09. 抽象資料型別與程式設計 (ADT & Design)

> 程式練習：`C09 銀行帳戶系統`
>
> 先備知識：第 07 課「封裝、不變量」、第 08 課「抽象類別、多型」。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | ADT 是什麼 | 「規格」和「實作」為什麼要分開、規格怎麼寫、怎麼照規格寫測試 |
| 第二部分 | 介面與實作分離 | 標頭檔 / 原始檔、抽象類別、同一個 ADT 的多種實作、靜態多型 vs 動態多型、pimpl |
| 第三部分 | 契約式設計 | 前置條件、後置條件、不變量；違反時的四種處理方式各怎麼寫 |
| 第四部分 | 設計原則 | 高內聚低耦合、SOLID 每一條的反例與修正、DRY / KISS / YAGNI |
| 第五部分 | 案例：設計銀行系統 | 從需求一步一步設計出 `C09` 的類別 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：ADT 是什麼

## 1.1 抽象資料型別 (Abstract Data Type, ADT)

**是什麼**：用 **「能做哪些操作、每個操作的效果是什麼」** 來定義一種資料型別，**完全不提** 它內部怎麼存、怎麼實作。

- **抽象 (abstract)**：只看「能做什麼」，把「怎麼做」藏起來。
- **資料型別 (data type)**：一組值 + 可以對這些值做的操作。

**比喻**：電視遙控器的說明書寫著「按 + 音量變大、按 CH▲ 換下一台」，但不會告訴你遙控器裡的電路怎麼設計。只要符合說明書，用紅外線還是藍牙實作都可以；你換了一支新遙控器，也不用重新學怎麼用。

**你其實一直在用 ADT**：

| 你用的東西 | 你知道的（規格） | 你不需要知道的（實作） |
|---|---|---|
| `int` | 加減乘除、比較 | CPU 用二補數、32 個位元 |
| `std::string` | `+`、`size()`、`substr()` | 短字串最佳化 (SSO)、記憶體怎麼配置 |
| `std::map` | `insert`、`find`、依 key 排序、`O(log n)` | 紅黑樹、旋轉、節點顏色 |
| `std::priority_queue` | `push`、`top` 是最大值、`pop` | 二元堆積、上浮下沉（DS 路線第 07 課） |

## 1.2 一個 ADT 的規格長什麼樣子

以 **Stack ADT** 為例，一份完整的規格包含四部分：

**① 操作清單**（名稱、參數、回傳值）

**② 每個操作的前置條件與效果**

| 操作 | 前置條件 | 效果（後置條件） | 複雜度要求 |
|---|---|---|---|
| `push(x)` | 無 | `x` 成為頂端元素，`size` 加 1 | `O(1)` 攤銷 |
| `pop()` | **非空** | 移除頂端元素，`size` 減 1 | `O(1)` |
| `top()` | **非空** | 回傳頂端元素，不改變 stack | `O(1)` |
| `size()` | 無 | 回傳元素個數 | `O(1)` |
| `empty()` | 無 | 回傳 `size() == 0` | `O(1)` |

**③ 公理 (axioms)**：用其他操作描述某個操作的效果，精確定義「行為」。

- `push(x)` 之後，`top()` 等於 `x`。
- `push(x)` 之後，`size()` 比原本多 1。
- `push(x)` 之後再 `pop()`，stack 回到原本的狀態。
- 新建立的 stack，`empty()` 是 `true`。

**④ 錯誤情況**：前置條件不成立時會怎樣（3.2 節）。

**注意規格裡沒有提到** 陣列、指標、節點、容量 —— 這些都是 **實作** 的事。

### 另一個例子：Set ADT（集合）

| 操作 | 前置條件 | 效果 |
|---|---|---|
| `insert(x)` | 無 | 之後 `contains(x)` 為真；`x` 原本就在的話什麼都不變 |
| `erase(x)` | 無 | 之後 `contains(x)` 為假 |
| `contains(x)` | 無 | 回傳 `x` 在不在集合裡 |
| `size()` | 無 | 不同元素的個數 |

公理：`insert(x); insert(x);` 和只 `insert(x)` 一次效果相同（集合沒有重複元素）。

這份規格可以用 **排序陣列**、**二元搜尋樹**、**雜湊表** 實作，複雜度不同，但行為都一樣。

## 1.3 為什麼要分開規格和實作？

1. **使用者不需要懂實作**：用 `std::map` 不需要懂紅黑樹。
2. **實作可以替換**：發現用陣列太慢，改成別的實作，**使用者的程式碼一行都不用改**（第 07 課 1.4 的 `Wallet` 例子）。
3. **可以分工**：一個人寫實作，其他人照著規格寫使用它的程式。
4. **容易測試**：照著規格寫測試，**任何實作都要通過同一套測試**（下一節）。
5. **容易推理**：看程式時只要記得規格，不用同時記住所有細節。

**資料結構路線** 的每一題（`03_my_vector`、`12_binary_heap`……）其實就是：「題目給你 ADT 的規格，請你寫出實作」；而評測系統拿來比對的 `solution.cpp`，是同一份規格的另一個實作。

## 1.4 照著規格寫測試

**是什麼**：把 1.2 的公理直接寫成程式碼檢查。只要實作符合規格，這些檢查 **一定** 會通過。

```cpp
// 一個「任何 Stack 實作」都要通過的測試
template <class Stack>
bool test_stack_axioms() {
    Stack s;
    if (!s.empty()) return false;                    // 公理：新的 stack 是空的
    s.push(1);
    if (s.top() != 1 || s.size() != 1) return false; // 公理：push(x) 後 top() == x、size 加 1
    s.push(2);
    s.pop();
    if (s.top() != 1 || s.size() != 1) return false; // 公理：push 再 pop 回到原狀
    s.pop();
    return s.empty();
}

cout << test_stack_axioms<stack<int>>() << '\n';     // 輸出：1（std::stack 符合規格）
```

（`template` 的寫法在第 10 課詳細說明，這裡先知道「同一個測試可以套用到不同的型別」就好。）

這正是 `judge.py stress` 在做的事：用隨機資料比較你的實作和參考實作，兩者都符合同一份規格，輸出就必須一樣。

---

# 第二部分：介面與實作分離

## 2.1 介面 (Interface) vs 實作 (Implementation)

- **介面**：外界看得到、可以使用的部分（公開的函式宣告、它們的規格）。
- **實作**：內部怎麼做到的（私有成員、函式本體）。

**比喻**：餐廳的 **菜單** 是介面，**廚房** 是實作。客人只看菜單點菜；廚房換了廚師、換了爐子，只要菜一樣，客人不會察覺。

C++ 有好幾種層次的分離：

| 方式 | 分離了什麼 | 在哪裡 |
|---|---|---|
| `public` / `private` | 同一個類別裡，哪些能用、哪些不能碰 | 第 07 課 |
| 標頭檔 `.h` / 原始檔 `.cpp` | 宣告和定義放在不同檔案 | 2.2、第 14 課 |
| 抽象類別（純虛擬函式） | 規格和 **多種** 實作，**執行時** 決定用哪一種 | 2.3 |
| 模板 | 規格和多種實作，**編譯時** 決定 | 2.4、第 10 課 |
| 🔍 pimpl | 連私有成員都藏起來 | 2.5 |

## 2.2 標頭檔與原始檔

**是什麼**：
- **標頭檔 (`.h` / `.hpp`)**：放 **介面** —— 類別定義、函式宣告。使用者 `#include` 它。
- **原始檔 (`.cpp`)**：放 **實作** —— 成員函式的本體。單獨編譯。

```cpp
// ===== stack.h：介面（使用者只需要看這個檔案）=====
#pragma once                       // 防止同一個標頭檔被 include 兩次（第 14 課）
#include <vector>

class IntStack {
public:
    void push(int x);              // 只有宣告
    void pop();                    // 前置條件：!empty()
    int top() const;               // 前置條件：!empty()
    bool empty() const;
private:
    std::vector<int> data_;        // 私有成員還是得寫在這裡（2.5 的 pimpl 可以藏起來）
};
```

```cpp
// ===== stack.cpp：實作 =====
#include "stack.h"

void IntStack::push(int x) { data_.push_back(x); }
void IntStack::pop() { data_.pop_back(); }
int IntStack::top() const { return data_.back(); }
bool IntStack::empty() const { return data_.empty(); }
```

```cpp
// ===== main.cpp：使用者 =====
#include "stack.h"
#include <iostream>
int main() {
    IntStack s;
    s.push(3); s.push(4);
    std::cout << s.top() << '\n';  // 輸出：4
}
```

編譯：`g++ main.cpp stack.cpp -o app`。

**好處**：
- 使用者看 `stack.h` 就知道怎麼用，不會被實作細節干擾。
- 改了 `stack.cpp` 的實作，只需要重新編譯 `stack.cpp`，`main.cpp` 不用重編（大專案可以省下很多時間）。

**注意**：標頭檔裡不要寫 `using namespace std;`（會污染所有 include 它的檔案），所以要寫 `std::vector`。完整的編譯模型在第 14 課。

本平台的練習題都是單一檔案，所以介面和實作寫在一起，但「類別定義 = 介面、成員函式本體 = 實作」的觀念是一樣的。

## 2.3 用抽象類別表達 ADT

**是什麼**：把 ADT 的每個操作寫成 **純虛擬函式**，每種實作是一個子類別。使用者只透過抽象類別的參考 / 指標操作。

```cpp
// 規格：任何 Stack 都要能做這些事
class AbstractStack {
public:
    virtual ~AbstractStack() = default;
    virtual void push(int x) = 0;
    virtual void pop() = 0;               // 前置條件：!empty()
    virtual int top() const = 0;          // 前置條件：!empty()
    virtual size_t size() const = 0;
    bool empty() const { return size() == 0; }   // 可以用其他操作組合出來的，直接實作
    virtual string impl_name() const = 0;
};

// 實作一：用 vector（陣列）
class ArrayStack : public AbstractStack {
    vector<int> v_;
public:
    void push(int x) override { v_.push_back(x); }
    void pop() override { v_.pop_back(); }
    int top() const override { return v_.back(); }
    size_t size() const override { return v_.size(); }
    string impl_name() const override { return "陣列"; }
};

// 實作二：用鏈結串列
class ListStack : public AbstractStack {
    struct Node { int val; unique_ptr<Node> next; };
    unique_ptr<Node> head_;
    size_t n_ = 0;
public:
    void push(int x) override { head_ = make_unique<Node>(Node{x, std::move(head_)}); n_++; }
    void pop() override { head_ = std::move(head_->next); n_--; }
    int top() const override { return head_->val; }
    size_t size() const override { return n_; }
    string impl_name() const override { return "鏈結串列"; }
};

// 使用者只依賴「規格」
int sum_and_clear(AbstractStack& s) {
    int total = 0;
    while (!s.empty()) { total += s.top(); s.pop(); }
    return total;
}
```

```cpp
ArrayStack a;
ListStack b;
for (int i = 1; i <= 4; i++) { a.push(i); b.push(i * 10); }
cout << sum_and_clear(a) << ' ' << a.empty() << '\n';   // 輸出：10 1
cout << sum_and_clear(b) << ' ' << b.empty() << '\n';   // 輸出：100 1
```

`sum_and_clear` 不知道、也不在乎傳進來的是 `ArrayStack` 還是 `ListStack`。

### 執行時才決定用哪個實作

抽象類別最大的威力：**選擇實作的時機可以延後到執行時**（例如依照設定檔、使用者輸入）。

```cpp
unique_ptr<AbstractStack> make_stack(const string& kind) {     // 工廠函式 (factory)
    if (kind == "list") return make_unique<ListStack>();
    return make_unique<ArrayStack>();
}

for (string kind : {"array", "list"}) {
    auto s = make_stack(kind);                 // 使用者的程式只拿到 AbstractStack
    s->push(5); s->push(7);
    cout << s->impl_name() << ": top=" << s->top() << " size=" << s->size() << '\n';
}
// 輸出：
// 陣列: top=7 size=2
// 鏈結串列: top=7 size=2
```

**兩個實作，相同的行為**：這就是「符合同一份規格」的意思。

## 2.4 🔍 靜態多型 vs 動態多型

同樣的事情也可以用 **模板** 做，不需要繼承同一個父類別：

```cpp
template <class Stack>
int sum_and_clear_t(Stack& s) {          // 任何有 top / pop / empty 的型別都可以
    int total = 0;
    while (!s.empty()) { total += s.top(); s.pop(); }
    return total;
}

stack<int> st;                            // std::stack 跟 AbstractStack 沒有任何繼承關係
st.push(1); st.push(2);
cout << sum_and_clear_t(st) << '\n';      // 輸出：3
ArrayStack as;
as.push(5);
cout << sum_and_clear_t(as) << '\n';      // 輸出：5（模板版本也能用在 ArrayStack 上）
```

這種「**只要有這些操作就能用**」的方式叫做 **鴨子型別 (duck typing)**：「走起來像鴨子、叫起來像鴨子，就當牠是鴨子」。

| | 動態多型（虛擬函式） | 靜態多型（模板） |
|---|---|---|
| 決定時機 | 執行時 | 編譯時 |
| 需要共同的父類別 | ✅ 要 | ❌ 不用 |
| 速度 | 有虛擬呼叫的成本 | 可以內聯，最快 |
| 能放進同一個容器 | ✅ `vector<unique_ptr<Base>>` | ❌ 每種型別是不同的實例 |
| 規格檢查 | 抽象類別（漏了實作就編譯錯誤） | C++20 concepts，或沒寫對時噴出很長的錯誤 |
| 程式碼大小 | 一份 | 每種型別各產生一份 |

**選擇**：
- 要在 **執行時** 混用不同型別（例如讀檔決定要建立哪種帳戶）→ 虛擬函式。
- 型別在編譯時就確定、要求效能 → 模板。STL 選擇了模板。

## 2.5 🔍 pimpl：連私有成員都藏起來

**問題**：2.2 的 `stack.h` 裡還是看得到 `private: std::vector<int> data_;`。這有兩個缺點：
1. 使用者看得到實作細節（雖然不能用）。
2. 改了私有成員（例如換成 `deque`），**所有 include 它的檔案都要重新編譯**（因為物件大小變了）。

**pimpl (pointer to implementation)**：類別裡只放一個指向「實作物件」的指標，實作物件的定義藏在 `.cpp` 裡。

```cpp
// ===== widget.h =====
class Widget {
public:
    Widget();
    ~Widget();                           // 必須在 .cpp 裡定義（那裡才看得到 Impl 的完整定義）
    void add(int x);
    int total() const;
private:
    struct Impl;                         // 只宣告，不定義：使用者完全看不到裡面有什麼
    std::unique_ptr<Impl> p_;
};

// ===== widget.cpp =====
struct Widget::Impl {                    // 真正的資料在這裡
    std::vector<int> items;
};
Widget::Widget() : p_(std::make_unique<Impl>()) {}
Widget::~Widget() = default;
void Widget::add(int x) { p_->items.push_back(x); }
int Widget::total() const { int s = 0; for (int x : p_->items) s += x; return s; }
```

```cpp
Widget w;
w.add(3); w.add(4);
cout << w.total() << '\n';               // 輸出：7
```

**代價**：每個物件多一次 heap 配置、每次存取多一次間接。用在大型專案的公開介面、需要穩定的二進位介面 (ABI) 時。

---

# 第三部分：契約式設計 (Design by Contract)

## 3.1 三種契約

**是什麼**：把函式想成「**呼叫者** 和 **函式** 之間的契約」，雙方各有責任。

| 契約 | 英文 | 誰負責 | 例子（`pop()`） |
|---|---|---|---|
| **前置條件** | Precondition | **呼叫者** 要保證 | stack 不是空的 |
| **後置條件** | Postcondition | **函式** 要保證 | 頂端元素被移除，size 減 1 |
| **不變量** | Class Invariant | **類別** 在每個公開函式前後都要保證 | `0 ≤ size ≤ capacity` |

**比喻**：租車契約。**你** 要保證有駕照、會還車（前置條件）；**租車公司** 要保證車子能開、有加滿油（後置條件）；這台車 **任何時候** 都要有保險（不變量）。

**為什麼需要**：責任清楚了，就知道 **出錯時是誰的錯**：
- 前置條件不成立 → **呼叫者** 的 bug。
- 前置條件成立、後置條件卻不成立 → **函式** 的 bug。

### 把契約寫在註解裡

```cpp
// 在排序好的陣列 a 中二分搜尋 x
// 前置條件：a 依遞增排序
// 後置條件：回傳 i 使得 a[i] == x；找不到則回傳 -1
// 複雜度：O(log n)
int binary_search(const vector<int>& a, int x);
```

**常見錯誤**：前置條件沒寫清楚，呼叫者不知道陣列要先排序，就會得到莫名其妙的結果。

## 3.2 違反前置條件時怎麼辦？四種做法

| 做法 | 什麼時候用 | 標準函式庫的例子 |
|---|---|---|
| **未定義行為**（不檢查） | 追求效能，而且呼叫者「應該知道」的條件 | `vector::operator[]`、空 `stack` 的 `top()` |
| **assert** | 開發時抓 bug；發布版本關掉 | — |
| **丟出例外** | 錯誤可能在正常使用中發生，呼叫者需要處理 | `vector::at()` 越界丟 `out_of_range`、`stoi("abc")` |
| **回傳錯誤碼 / `optional` / `bool`** | 「失敗」是常見的正常結果 | `map::find` 回傳 `end()`、`string::find` 回傳 `npos` |

用同一個「安全除法」各寫一次：

### 做法 1：不檢查（未定義行為）

```cpp
int divide_ub(int a, int b) { return a / b; }      // 前置條件：b != 0（呼叫者負責）
cout << divide_ub(7, 2) << '\n';                   // 輸出：3
// divide_ub(7, 0);                                // 💥 除以 0：未定義行為，通常程式直接當掉
```

最快，但違反時後果完全無法預測。

### 做法 2：assert

```cpp
#include <cassert>
int divide_assert(int a, int b) {
    assert(b != 0 && "divisor must not be zero");  // 字串常值永遠為真，只是用來讓錯誤訊息更清楚
    return a / b;
}
cout << divide_assert(9, 3) << '\n';               // 輸出：3
// divide_assert(9, 0);
// 執行時印出類似：main.cpp:4: int divide_assert(int, int): Assertion `b != 0 && "divisor must not be zero"' failed.
// 然後程式立刻中止（abort）
```

**`assert` 的特性**：
- 條件為假時印出 **檔名、行號、條件**，然後中止程式 —— 很容易找到 bug 在哪。
- 定義了 `NDEBUG` 時（編譯加 `-DNDEBUG`，通常是發布版本），`assert` **整行被移除**，完全沒有成本。
- 所以 **不要在 `assert` 裡寫有副作用的程式碼**：`assert(v.pop_back(), ...)` 在發布版本就不會執行了！

### 做法 3：丟出例外

```cpp
int divide_throw(int a, int b) {
    if (b == 0) throw invalid_argument("divide by zero");
    return a / b;
}
try {
    cout << divide_throw(8, 4) << '\n';            // 輸出：2
    cout << divide_throw(8, 0) << '\n';            // 丟出例外，這行的輸出不會發生
} catch (const invalid_argument& e) {
    cout << "錯誤：" << e.what() << '\n';          // 輸出：錯誤：divide by zero
}
```

呼叫者 **不能忽略** 例外（沒有 catch 的話程式會終止），適合「一定要處理」的錯誤。第 13 課詳談。

### 做法 4：回傳值表示成功或失敗

```cpp
optional<int> divide_opt(int a, int b) {
    if (b == 0) return nullopt;                    // 「沒有結果」
    return a / b;
}
auto r1 = divide_opt(10, 5), r2 = divide_opt(10, 0);
cout << r1.has_value() << ' ' << *r1 << '\n';      // 輸出：1 2
cout << r2.has_value() << ' ' << r2.value_or(-1) << '\n';   // 輸出：0 -1
```

`optional`（第 15 課）比「回傳 -1 代表錯誤」好：-1 可能本來就是合法的答案。

### 判斷原則

- 這個錯誤是 **程式寫錯了**（bug，正確的程式永遠不會發生）→ `assert` 或 UB。
- 這個錯誤是 **外部世界造成的**（使用者輸入錯誤、檔案不存在、餘額不足）→ 例外或錯誤回傳值。
  - 很常發生、是「正常結果」之一（找不到、餘額不足）→ 回傳值。
  - 很少發生、呼叫者可能沒辦法在原地處理（記憶體不足、檔案損毀）→ 例外。

## 3.3 後置條件的檢查

後置條件通常在 **開發時** 用 `assert` 檢查，確認函式本身沒寫錯：

```cpp
int my_abs(int x) {
    int result = x < 0 ? -x : x;
    assert(result >= 0);                 // 後置條件：結果非負
    return result;
}
cout << my_abs(-5) << ' ' << my_abs(3) << '\n';   // 輸出：5 3
// my_abs(INT_MIN) 會讓 assert 失敗：-INT_MIN 溢位（第 02 課），結果仍然是負數
//   → assert 幫你抓到了一個邊界情況的 bug
```

## 3.4 維護不變量

**規則**：
1. **建構子** 建立不變量（建構失敗就丟例外，**不要產生一個不合法的物件**）。
2. **每個公開的成員函式**：進入時可以假設不變量成立，**離開時必須讓不變量成立**。
3. 資料成員設為 `private`，外界無法破壞不變量。
4. 私有的輔助函式 **執行到一半** 時可以暫時破壞不變量，只要公開函式結束前恢復就好。

### 用 check_invariant 在開發時抓 bug

```cpp
class BoundedCounter {
    int value_, lo_, hi_;                      // 不變量：lo_ <= value_ <= hi_
    void check_invariant() const { assert(lo_ <= value_ && value_ <= hi_); }
public:
    BoundedCounter(int lo, int hi) : value_(lo), lo_(lo), hi_(hi) {
        if (lo > hi) throw invalid_argument("lo > hi");   // 1. 建構時建立不變量
        check_invariant();
    }
    bool increment() {
        if (value_ == hi_) return false;      // 會破壞不變量 → 拒絕，狀態不變
        value_++;
        check_invariant();                    // 2. 每個公開函式結束前檢查
        return true;
    }
    int value() const { return value_; }
};

BoundedCounter c(0, 2);
cout << c.increment() << c.increment() << c.increment() << ' ' << c.value() << '\n';   // 輸出：110 2
try { BoundedCounter bad(5, 1); }
catch (const invalid_argument& e) { cout << e.what() << '\n'; }                        // 輸出：lo > hi
```

`increment` 回傳 `1`、`1`、`0`：第三次會超過上限，被拒絕，值停在 2。

**常見錯誤：失敗時「改到一半」**

```cpp
bool bad_withdraw(long long amt) {
    balance_ -= amt;                           // ❌ 先改了
    if (balance_ < 0) return false;            // 才發現不合法 → 回傳 false，但餘額已經變成負的了！
    return true;
}
```

**正確的順序：先檢查，全部通過才修改**。失敗時狀態完全不變。

---

# 第四部分：設計原則

## 4.1 高內聚、低耦合 (High Cohesion, Low Coupling)

- **內聚 (cohesion)**：一個類別 **內部** 的東西是否都在做 **同一件事**。越高越好。
- **耦合 (coupling)**：不同類別之間 **互相依賴** 的程度。越低越好。

**比喻**：好的公司部門：每個部門專注於自己的工作（高內聚），部門之間只透過正式的窗口溝通（低耦合）。一個部門改組，不會讓其他部門跟著大亂。

**低內聚的例子**：

```cpp
class Utils {                       // ❌ 什麼都放：字串處理、數學、檔案、網路……
public:
    static string trim(string s);
    static int gcd(int a, int b);
    static string read_file(const string& path);
    static void send_http(const string& url);
};
```

**高耦合的例子**：

```cpp
class Report {
public:
    void make(Database& db) {
        // ❌ 直接操作 Database 的內部資料結構
        for (auto& row : db.internal_rows_) { /* ... */ }
        // Database 一改內部結構，Report 就壞了
    }
};
```

降低耦合的方法：只透過 **公開的介面** 溝通（`db.query(...)`），更進一步是依賴 **抽象介面**（4.2 的 D）。

## 4.2 SOLID 原則

五個物件導向設計原則的英文字首：

| 原則 | 英文 | 一句話 |
|---|---|---|
| **S** 單一職責 | Single Responsibility | 一個類別只有 **一個** 改變的理由 |
| **O** 開放封閉 | Open/Closed | 對 **擴充** 開放，對 **修改** 封閉 |
| **L** 里氏替換 | Liskov Substitution | 子類別要能 **完全替代** 父類別 |
| **I** 介面隔離 | Interface Segregation | 不要強迫使用者依賴 **用不到** 的函式 |
| **D** 依賴反轉 | Dependency Inversion | 依賴 **抽象**（介面），不要依賴 **具體實作** |

下面每一條都給一個 **違反的例子** 和 **修正的方式**。

### S：單一職責原則 (Single Responsibility Principle)

**「改變的理由」是什麼意思？** 想像未來可能的需求變更：「報表要改成 HTML 格式」「要改存到雲端」「要換一種計算方式」。如果這些不同的變更都要改 **同一個類別**，它的職責就太多了。

```cpp
// ❌ 違反：計算、格式化、存檔都在同一個類別
class GradeBook {
    vector<int> scores_;
public:
    void add(int s) { scores_.push_back(s); }
    double average() const;                       // 計算（理由 1：計算規則改變）
    string to_html() const;                       // 格式化（理由 2：顯示格式改變）
    void save(const string& path) const;          // 存檔（理由 3：儲存方式改變）
};
```

```cpp
// ✅ 符合：拆成各司其職的類別
class GradeBook {                                 // 只負責「成績資料與計算」
    vector<int> scores_;
public:
    void add(int s) { scores_.push_back(s); }
    double average() const {
        if (scores_.empty()) return 0;
        return accumulate(scores_.begin(), scores_.end(), 0.0) / scores_.size();
    }
    const vector<int>& scores() const { return scores_; }
};
class TextFormatter {                             // 只負責「怎麼顯示」
public:
    string format(const GradeBook& g) const {
        ostringstream os;
        os << "共 " << g.scores().size() << " 筆，平均 " << g.average();
        return os.str();
    }
};

GradeBook g;
g.add(80); g.add(90); g.add(70);
cout << TextFormatter().format(g) << '\n';        // 輸出：共 3 筆，平均 80
```

要加 HTML 格式？新增一個 `HtmlFormatter` 就好，`GradeBook` 完全不用動。

### O：開放封閉原則 (Open/Closed Principle)

**意思**：加新功能時，應該是 **新增** 程式碼，而不是 **修改** 已經寫好、測試過的程式碼。

```cpp
// ❌ 違反：每加一種圖形就要改這個函式（而且同樣的 switch 可能散落在很多地方）
enum Kind { CIRCLE, RECT };
struct ShapeData { Kind kind; double a, b; };
double area(const ShapeData& s) {
    switch (s.kind) {
        case CIRCLE: return 3.14 * s.a * s.a;
        case RECT:   return s.a * s.b;
    }
    return 0;     // 加三角形要回來改這裡，還有 perimeter()、draw()……
}
```

```cpp
// ✅ 符合：加新圖形只要新增一個類別，現有的程式碼不用動
class Shape { public: virtual ~Shape() = default; virtual double area() const = 0; };
class Circle : public Shape { double r_; public: Circle(double r) : r_(r) {} double area() const override { return 3.14 * r_ * r_; } };
class Rect : public Shape { double w_, h_; public: Rect(double w, double h) : w_(w), h_(h) {} double area() const override { return w_ * h_; } };
// 新增的：
class Triangle : public Shape { double b_, h_; public: Triangle(double b, double h) : b_(b), h_(h) {} double area() const override { return b_ * h_ / 2; } };

double total_area(const vector<unique_ptr<Shape>>& v) {    // 這個函式永遠不用改
    double s = 0;
    for (auto& p : v) s += p->area();
    return s;
}
vector<unique_ptr<Shape>> shapes;
shapes.push_back(make_unique<Circle>(1));
shapes.push_back(make_unique<Rect>(2, 3));
shapes.push_back(make_unique<Triangle>(4, 5));
cout << total_area(shapes) << '\n';               // 輸出：19.14
```

### L：里氏替換原則 (Liskov Substitution Principle)

**意思**：任何使用父類別的地方，換成子類別都必須能正確運作（第 08 課 6.5 的 `Square : Rectangle` 反例）。

另一個常見的違反方式：**子類別讓某個操作「不能用」**。

```cpp
class Bird {
public:
    virtual ~Bird() = default;
    virtual string fly() const { return "飛起來了"; }
};
class Penguin : public Bird {
public:
    string fly() const override { throw logic_error("企鵝不會飛"); }   // ❌ 違反 Bird 的承諾
};
// 任何「拿到 Bird 就呼叫 fly()」的程式碼，遇到 Penguin 就會出錯
```

**修正**：重新思考繼承結構 —— 「會飛」不是所有鳥的共同行為，就不該放在 `Bird` 裡。

```cpp
class Bird2 { public: virtual ~Bird2() = default; virtual string name() const = 0; };
class FlyingBird : public Bird2 { public: virtual string fly() const { return "飛起來了"; } };
class Sparrow : public FlyingBird { public: string name() const override { return "麻雀"; } };
class Penguin2 : public Bird2 { public: string name() const override { return "企鵝"; } };
// 需要「會飛」的函式就收 FlyingBird&，企鵝根本傳不進去 —— 錯誤在編譯時就被擋下來了
```

### I：介面隔離原則 (Interface Segregation Principle)

**意思**：介面要小而專注。不要做一個大而全的介面，逼實作者實作用不到的函式。

```cpp
// ❌ 違反：一個巨大的介面
class Machine {
public:
    virtual ~Machine() = default;
    virtual void print(const string&) = 0;
    virtual void scan() = 0;
    virtual void fax(const string&) = 0;
};
class SimplePrinter : public Machine {
public:
    void print(const string& s) override { cout << "列印 " << s << '\n'; }
    void scan() override { throw logic_error("不支援"); }      // 被迫實作用不到的功能
    void fax(const string&) override { throw logic_error("不支援"); }
};
```

```cpp
// ✅ 符合：拆成小介面，需要什麼就實作什麼
class Printer { public: virtual ~Printer() = default; virtual void print(const string&) = 0; };
class Scanner { public: virtual ~Scanner() = default; virtual string scan() = 0; };

class BasicPrinter : public Printer {
public:
    void print(const string& s) override { cout << "列印 " << s << '\n'; }
};
class AllInOne : public Printer, public Scanner {       // 多功能事務機：兩個都實作（第 08 課多重繼承）
public:
    void print(const string& s) override { cout << "列印 " << s << '\n'; }
    string scan() override { return "掃描結果"; }
};

void print_report(Printer& p) { p.print("報表"); }      // 只需要列印功能 → 只依賴 Printer
BasicPrinter bp; AllInOne aio;
print_report(bp);                                        // 輸出：列印 報表
print_report(aio);                                       // 輸出：列印 報表
cout << aio.scan() << '\n';                              // 輸出：掃描結果
```

### D：依賴反轉原則 (Dependency Inversion Principle)

**意思**：高層的邏輯（「做什麼」）不應該直接依賴低層的細節（「用什麼工具做」），兩者都應該依賴 **抽象介面**。

```cpp
// ❌ 違反：通知服務直接寫死用 Email
class EmailSender { public: void send(const string& to, const string& msg) { /* ... */ } };
class OrderService {
    EmailSender email_;                    // 寫死了具體的類別
public:
    void place_order() { email_.send("user", "訂單成立"); }
    // 想改成簡訊通知？要改 OrderService 的程式碼
    // 想寫測試？每次跑測試都會真的寄信
};
```

```cpp
// ✅ 符合：依賴抽象介面，具體實作從外面「注入」
class Notifier {
public:
    virtual ~Notifier() = default;
    virtual void notify(const string& msg) = 0;
};
class SmsNotifier : public Notifier {
public:
    void notify(const string& msg) override { cout << "[簡訊] " << msg << '\n'; }
};
class FakeNotifier : public Notifier {     // 測試用：只記錄，不真的發送
public:
    vector<string> sent;
    void notify(const string& msg) override { sent.push_back(msg); }
};

class OrderService2 {
    Notifier& notifier_;                   // 只知道「有一個能通知的東西」
public:
    explicit OrderService2(Notifier& n) : notifier_(n) {}    // 從外面傳進來：依賴注入 (dependency injection)
    void place_order(int id) { notifier_.notify("訂單 " + to_string(id) + " 成立"); }
};

SmsNotifier sms;
OrderService2 real(sms);
real.place_order(1);                       // 輸出：[簡訊] 訂單 1 成立

FakeNotifier fake;
OrderService2 test(fake);
test.place_order(2);
cout << fake.sent.size() << ' ' << fake.sent[0] << '\n';   // 輸出：1 訂單 2 成立（測試時不會真的發簡訊）
```

## 4.3 其他常見原則

| 原則 | 一句話 | 例子 |
|---|---|---|
| **DRY** (Don't Repeat Yourself) | 同樣的邏輯只寫一次 | 用 `+=` 實作 `+`（第 07 課）、委派建構子 |
| **KISS** (Keep It Simple, Stupid) | 能簡單就不要複雜 | 用 `vector` 就夠了，不要自己寫記憶體池 |
| **YAGNI** (You Aren't Gonna Need It) | 不要為了「以後可能會用到」而寫現在用不到的功能 | 只有一種帳戶時，不用先設計十層抽象 |
| **最少驚訝原則** (Least Astonishment) | 介面的行為要符合使用者的直覺 | `+` 就該是加法；`size()` 不該修改物件 |

**DRY 的例子**：

```cpp
// ❌ 同樣的驗證邏輯寫了兩次，改一處忘一處
void deposit(long long amt)  { if (amt <= 0 || amt > 1000000000) throw invalid_argument("bad"); /*...*/ }
void withdraw(long long amt) { if (amt <= 0 || amt > 1000000000) throw invalid_argument("bad"); /*...*/ }

// ✅ 抽出來
void check_amount(long long amt) { if (amt <= 0 || amt > 1000000000) throw invalid_argument("bad"); }
void deposit2(long long amt)  { check_amount(amt); /*...*/ }
void withdraw2(long long amt) { check_amount(amt); /*...*/ }
```

> 原則是 **指引**，不是法律。過度設計（為了一個小程式寫十層抽象）和完全不設計一樣糟。**先寫出簡單、正確的程式，等真的需要擴充時再重構**。

---

# 第五部分：案例：設計銀行系統（C09）

這一部分示範「從需求到類別設計」的思考過程。

## 5.1 第一步：找出名詞和動詞

需求：「銀行有 **儲蓄帳戶** 和 **支票帳戶**。可以 **開戶**、**存款**、**提款**、**轉帳**、**月底結算**、**查詢餘額**。儲蓄帳戶不能透支、月底有利息；支票帳戶可以透支到額度、負餘額時月底扣手續費。」

- **名詞 → 類別候選**：銀行、帳戶、儲蓄帳戶、支票帳戶。
- **動詞 → 操作候選**：開戶、存款、提款、轉帳、結算、查詢。

## 5.2 第二步：找出 is-a 和 has-a

- 儲蓄帳戶 **是一種** 帳戶 → 繼承。
- 支票帳戶 **是一種** 帳戶 → 繼承。
- 銀行 **有很多** 帳戶 → 組合：`map<string, unique_ptr<Account>>`。

```
        Bank ◆──────── 多個 ──────▶ Account（抽象）
                                     ▲         ▲
                                     │         │
                          SavingsAccount   CheckingAccount
```

（◆ 表示「擁有」：銀行被銷毀時，帳戶跟著被銷毀 —— 用 `unique_ptr` 正好表達這個關係。）

## 5.3 第三步：哪些行為相同、哪些不同？

| 操作 | 兩種帳戶相同？ | 放在哪裡 |
|---|---|---|
| 存款 | 相同 | `Account` 的一般成員函式 |
| 查詢餘額 | 相同 | `Account` 的一般成員函式 |
| **能不能提款** | **不同**（不變量不同） | `Account` 的 **純虛擬函式** `canWithdraw` |
| **月底結算** | **不同** | 純虛擬函式 `monthEnd` |
| 型別名稱 | 不同 | 純虛擬函式 `type` |
| 轉帳 | 涉及兩個帳戶 | **銀行** 的責任（單一職責：帳戶不應該知道其他帳戶） |
| 檢查帳號存不存在 | 跟帳戶本身無關 | **銀行** 的責任 |

## 5.4 第四步：決定錯誤處理

- 帳號不存在、金額不合法、餘額不足：是 **正常使用中會發生的錯誤** → 回傳錯誤訊息，**狀態不變**（3.2 的「回傳值」做法）。
- 題目規定了 **檢查順序**：同時有好幾個錯誤時，要回報最前面的那一個。所以檢查要照順序寫，一發現錯誤就回傳。
- 轉帳要 **原子性 (atomicity)**：要嘛完整成功，要嘛完全沒發生。做法是 **先檢查所有條件，全部通過才修改**（第 13 課的「強例外保證」也是同樣的想法）。

**為什麼原子性重要？** 看這個錯誤的寫法：

```cpp
// ❌ 先提款，再發現不能存 → 錢憑空消失
bool bad_transfer(Account& from, Account& to, long long amt) {
    from.withdraw(amt);                  // 已經扣了
    if (!to.can_receive(amt)) return false;   // 才發現不行 —— 但 from 的錢已經不見了
    to.deposit(amt);
    return true;
}
```

**正確的模式**：

```cpp
// ✅ 先檢查全部，再一次修改
bool transfer(Account& from, Account& to, long long amt) {
    if (!from.canWithdraw(amt)) return false;   // 所有的檢查都在前面
    // （如果還有其他條件，也都在這裡檢查）
    from.withdraw(amt);                         // 走到這裡就保證不會失敗
    to.deposit(amt);
    return true;
}
```

## 5.5 結果：Account 的介面

```cpp
class Account {                          // 抽象：定義所有帳戶的共同介面
protected:
    long long balance_ = 0;
public:
    virtual ~Account() = default;
    long long balance() const { return balance_; }
    void deposit(long long amt) { balance_ += amt; }         // 前置條件：amt > 0（由 Bank 檢查）
    void withdraw(long long amt) { balance_ -= amt; }        // 前置條件：canWithdraw(amt)
    virtual bool canWithdraw(long long amt) const = 0;       // 不同帳戶的不變量
    virtual void monthEnd() = 0;
    virtual string type() const = 0;
};
```

一個子類別的範例（另一個留給你在 `C09` 實作）：

```cpp
class SavingsAccount : public Account {
    long long rate_;                     // 利率（百分比）
public:
    explicit SavingsAccount(long long rate) : rate_(rate) {}
    bool canWithdraw(long long amt) const override { return balance_ - amt >= 0; }   // 不變量：餘額 >= 0
    void monthEnd() override { balance_ += balance_ * rate_ / 100; }
    string type() const override { return "savings"; }
};

SavingsAccount s(10);
s.deposit(140);
cout << s.canWithdraw(200) << ' ' << s.canWithdraw(140) << '\n';   // 輸出：0 1
s.monthEnd();
cout << s.type() << ' ' << s.balance() << '\n';                    // 輸出：savings 154
```

**新增第三種帳戶**（例如定期存款：結算前不能提款）時，只要新增一個類別實作這三個虛擬函式，**銀行的程式碼完全不用改** —— 這就是開放封閉原則。

## 5.6 設計檢查清單

| 問題 | 本案例的答案 |
|---|---|
| 每個類別的職責是什麼？能用一句話說完嗎？ | `Account`：管理一個帳戶的餘額與規則；`Bank`：管理帳號與跨帳戶的操作 |
| 不變量是什麼？誰負責維護？ | 每種帳戶的餘額下限；`canWithdraw` 檢查、`Bank` 在修改前呼叫 |
| 哪些地方會變？變的時候要改哪裡？ | 新增帳戶種類 → 只新增子類別 |
| 錯誤怎麼回報？失敗時狀態會不會改到一半？ | 回傳錯誤訊息；先檢查再修改 |
| 誰擁有誰？誰負責釋放？ | `Bank` 用 `unique_ptr` 擁有所有帳戶 |

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 抽象資料型別 | ADT | 用操作來定義的資料型別，不管實作 | 1.1 |
| 公理 | Axiom | 描述操作之間關係的規則 | 1.2 |
| 介面 / 實作 | Interface / Implementation | 外界看得到的 / 內部怎麼做 | 2.1 |
| 標頭檔 / 原始檔 | Header / Source File | 放宣告 / 放定義 | 2.2 |
| 工廠函式 | Factory Function | 依參數決定建立哪種實作的函式 | 2.3 |
| 靜態 / 動態多型 | Static / Dynamic Polymorphism | 模板（編譯時）/ 虛擬函式（執行時） | 2.4 |
| 鴨子型別 | Duck Typing | 只要有這些操作就能用，不需要共同的父類別 | 2.4 |
| 指向實作的指標 | pimpl | 把私有成員藏到 .cpp 裡 | 2.5 |
| 契約式設計 | Design by Contract | 用前置、後置條件和不變量描述函式 | 3.1 |
| 前置條件 | Precondition | 呼叫者要保證的條件 | 3.1 |
| 後置條件 | Postcondition | 函式要保證的結果 | 3.1 |
| 類別不變量 | Class Invariant | 物件隨時都要成立的條件 | 3.1 |
| 斷言 | Assertion | 開發時檢查條件，不成立就停止 | 3.2 |
| 內聚 / 耦合 | Cohesion / Coupling | 內部專注程度 / 互相依賴程度 | 4.1 |
| SOLID | SOLID | 五個物件導向設計原則 | 4.2 |
| 單一職責原則 | Single Responsibility | 一個類別只有一個改變的理由 | 4.2 |
| 開放封閉原則 | Open/Closed Principle | 擴充不用修改現有程式 | 4.2 |
| 介面隔離原則 | Interface Segregation | 介面要小，不強迫實作用不到的函式 | 4.2 |
| 依賴反轉原則 | Dependency Inversion | 依賴抽象而不是具體實作 | 4.2 |
| 依賴注入 | Dependency Injection | 依賴的物件從外面傳進來 | 4.2 |
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

### 題 7：下面的程式碼在「發布版本」（加了 `-DNDEBUG`）會出什麼問題？

```cpp
vector<int> v = {1, 2, 3};
assert(!v.empty());
int last = v.back();
assert(v.size() == 3 && (v.pop_back(), true));
cout << v.size();
```

### 題 8：寫一個 Set ADT 的抽象類別 `IntSet`（`insert`、`contains`、`size`），並用 `vector<int>`（不排序，線性搜尋）和 `std::set<int>` 各寫一個實作。寫一個函式 `count_unique(IntSet& s, const vector<int>& a)` 回傳陣列中不同元素的個數。

### 題 9：這個介面違反了哪個原則？

```cpp
class Shape {
public:
    virtual double area() const = 0;
    virtual double volume() const = 0;    // 平面圖形的體積？
};
class Circle : public Shape {
    double volume() const override { return 0; }   // ???
};
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

**題 7**：開發版本印出 `2`，發布版本印出 `3`。第二個 `assert` 裡面有 **副作用**（`v.pop_back()`）。定義 `NDEBUG` 後，整個 `assert` 被移除，`pop_back` 就不會執行了 —— 程式在兩種版本的行為不同。**規則：`assert` 裡只能放沒有副作用的檢查**。

**題 8**：

```cpp
class IntSet {
public:
    virtual ~IntSet() = default;
    virtual void insert(int x) = 0;
    virtual bool contains(int x) const = 0;
    virtual size_t size() const = 0;
};
class VectorSet : public IntSet {           // insert O(n)、contains O(n)
    vector<int> v_;
public:
    void insert(int x) override { if (!contains(x)) v_.push_back(x); }
    bool contains(int x) const override { return find(v_.begin(), v_.end(), x) != v_.end(); }
    size_t size() const override { return v_.size(); }
};
class TreeSet : public IntSet {             // insert O(log n)、contains O(log n)
    set<int> s_;
public:
    void insert(int x) override { s_.insert(x); }
    bool contains(int x) const override { return s_.count(x) > 0; }
    size_t size() const override { return s_.size(); }
};
size_t count_unique(IntSet& s, const vector<int>& a) {
    for (int x : a) s.insert(x);
    return s.size();
}
VectorSet vs; TreeSet ts;
vector<int> a = {3, 1, 3, 2, 1};
cout << count_unique(vs, a) << ' ' << count_unique(ts, a) << '\n';   // 輸出：3 3
```

兩個實作的 **行為** 相同（都符合「集合沒有重複元素」的公理），**效率** 不同。

**題 9**：違反 **介面隔離原則**（也違反里氏替換原則的精神）：不是每種圖形都有體積，卻強迫所有子類別實作 `volume()`，只好回傳一個沒有意義的 `0`。應該拆成 `Shape2D`（`area`）和 `Shape3D`（`area`、`volume`）兩個介面。
