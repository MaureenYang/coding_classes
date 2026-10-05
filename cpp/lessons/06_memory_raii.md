# 06. 記憶體管理、RAII 與移動語意

> 程式練習：`C06 自己做一個字串類別`、`C14 智慧指標串列`
>
> 先備知識：第 05 課「指標錯誤大全」、第 07 課的「建構子 / 解構子」基本概念（也可以先讀第 07 課第一、二部分）。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 物件的生命 | 記憶體的四個區域、`new` / `delete` 到底做了什麼 |
| 第二部分 | RAII | C++ 最重要的設計慣例：讓物件自己管理資源 |
| 第三部分 | 複製語意 | 淺複製的災難、三法則、自我指定、copy-and-swap |
| 第四部分 | 移動語意 | 右值參考、`std::move`、五法則、零法則、`noexcept` |
| 第五部分 | 智慧指標 | `unique_ptr`、`shared_ptr`、`weak_ptr`、循環參考 |
| 第六部分 | 所有權的設計 | 什麼時候用什麼、解構的遞迴陷阱 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：物件的生命

## 1.1 記憶體的四個區域

| 區域 | 放什麼 | 誰管理 | 大小 |
|---|---|---|---|
| **程式碼區 (text)** | 編譯好的機器碼 | 系統 | 固定 |
| **靜態區 (static / data)** | 全域變數、`static` 變數、字串字面值 | 程式開始時建立、結束時銷毀 | 固定 |
| **堆疊區 (stack)** | 區域變數、函式參數、返回位址 | **自動**：進入區塊時建立、離開時銷毀 | 小（通常 1 ~ 8 MB） |
| **堆積區 (heap / free store)** | `new` 出來的東西 | **程式設計師** 負責 `delete` | 大 |

**比喻**：
- **堆疊區** 像是餐廳托盤：拿了就用，吃完自動收走，但不能疊太高。
- **堆積區** 像是租倉庫：要多大有多大，但不用了要自己去退租。

## 1.2 new 和 delete 做了什麼

```cpp
Widget* p = new Widget(1, 2);
```

1. 跟系統要一塊 `sizeof(Widget)` 大小的記憶體（`operator new`）。
2. 在那塊記憶體上 **呼叫建構子** `Widget(1, 2)`。
3. 回傳指標。

```cpp
delete p;
```

1. **呼叫解構子** `~Widget()`。
2. 把記憶體還給系統（`operator delete`）。

| 配置 | 釋放 | |
|---|---|---|
| `new T` | `delete p` | 單一物件 |
| `new T[n]` | `delete[] p` | 陣列：每個元素都要呼叫解構子，所以要用 `[]` |

配錯（`new[]` 配 `delete`）是未定義行為。記憶體不夠時，`new` 會丟出 `std::bad_alloc` 例外。

## 1.3 手動管理為什麼很容易出錯

```cpp
void process() {
    int* buf = new int[1000];
    if (!load(buf)) return;           // ❌ 提早 return，忘了 delete → 洩漏
    compute(buf);                     // ❌ 如果 compute 丟出例外，也不會 delete
    delete[] buf;
}
```

每一條離開函式的路徑（`return`、例外、`break`……）都要記得釋放，**人一定會忘記**。

---

# 第二部分：RAII

## 2.1 RAII (Resource Acquisition Is Initialization)

**白話**：直譯是「取得資源就是初始化」，意思是：**把資源綁在一個物件上** ——
- **建構子** 取得資源（配置記憶體、開檔案、上鎖）；
- **解構子** 釋放資源。

因為 C++ **保證區域物件離開作用域時一定會呼叫解構子**（不管是正常結束、`return`、還是例外），資源 **一定會被釋放**。

**比喻**：飯店房卡。退房（物件被銷毀）時，房卡自動失效、房間自動回收，你不需要另外記得去「歸還房間」。

```cpp
class Buffer {
    int* data_;
public:
    Buffer(size_t n) : data_(new int[n]) {}   // 建構子：取得
    ~Buffer() { delete[] data_; }              // 解構子：釋放
    int* get() { return data_; }
};

void process() {
    Buffer buf(1000);
    if (!load(buf.get())) return;   // ✅ buf 的解構子自動執行
    compute(buf.get());             // ✅ 就算丟出例外也一樣
}                                   // ✅ 正常結束也一樣
```

## 2.2 你已經在用 RAII 了

| 類別 | 管理的資源 |
|---|---|
| `std::vector`、`std::string` | heap 記憶體 |
| `std::ifstream` / `ofstream` | 檔案（解構時自動關檔） |
| `std::lock_guard` | 互斥鎖（解構時自動解鎖） |
| `std::unique_ptr` / `shared_ptr` | 任意 heap 物件 |

**現代 C++ 的原則**：程式裡 **幾乎不應該出現裸的 `new` / `delete`**，交給 RAII 類別處理。

## 2.3 🔍 解構的順序

- 同一個區塊裡的區域變數：**建立的相反順序** 銷毀（後建立的先銷毀）。
- 類別的成員：**宣告的相反順序** 銷毀；解構子本體先執行，然後才銷毀成員。
- 繼承：先執行子類別的解構子，再執行父類別的（第 08 課）。

---

# 第三部分：複製語意 (Copy Semantics)

## 3.1 預設的複製是「淺複製」

**白話**：如果你沒有自己寫，編譯器產生的複製建構子會 **一個成員一個成員地複製**。對指標成員來說，**只複製位址，不複製指向的內容**。

```cpp
Buffer a(10);
Buffer b = a;     // 預設複製：b.data_ = a.data_，兩個指向同一塊記憶體！
}                 // b 解構：delete[] data_
                  // a 解構：delete[] data_ 同一塊 → 重複釋放 (double free) → 當掉
```

```
淺複製：               深複製：
a.data_ ──┐            a.data_ ──▶ [1 2 3]
          ├──▶ [1 2 3]
b.data_ ──┘            b.data_ ──▶ [1 2 3]（另一份）
```

**比喻**：淺複製是「給朋友一把你家的備份鑰匙」—— 同一間房子，他亂丟東西你家也亂；你把房子賣了，他的鑰匙也沒用了。深複製是「幫朋友蓋一間一模一樣的房子」。

## 3.2 三法則 (Rule of Three)

**白話**：如果你的類別需要自己寫 **以下任何一個**，通常 **三個都要寫**：

1. **解構子** `~T()`
2. **複製建構子** `T(const T& other)`：用另一個物件 **建立** 新物件
3. **複製指定運算子** `T& operator=(const T& other)`：把另一個物件 **指定給已存在的** 物件

原因：需要自己寫解構子，代表類別管理了某種資源；那麼預設的「淺複製」一定是錯的。

```cpp
Buffer b = a;     // 複製建構子（b 是新建立的）
Buffer c(5);
c = a;            // 複製指定（c 已經存在，要先處理 c 原本的資源）
```

## 3.3 自我指定 (Self-assignment)

**白話**：`a = a;`。看起來很蠢，但在 `v[i] = v[j]`（`i == j`）、`*p = *q`（指向同一個物件）時會不知不覺發生。

錯誤的寫法：

```cpp
Buffer& operator=(const Buffer& o) {
    delete[] data_;                     // ① 先釋放自己的
    data_ = new int[o.n_];              // 
    copy(o.data_, o.data_ + o.n_, data_);   // ② o 就是自己，o.data_ 已經被釋放了！
    return *this;
}
```

這就是 `C06` 測資 `corner_self_copy` 在測的陷阱。

## 3.4 copy-and-swap 慣用法

**白話**：先用複製建構子 **做一份複製品**，再把自己的內容和複製品 **交換**，舊的內容會隨著複製品一起被銷毀。

```cpp
Buffer& operator=(Buffer other) {   // ① 參數是「傳值」：已經複製好了
    swap(data_, other.data_);       // ② 交換
    swap(n_, other.n_);
    return *this;
}                                   // ③ other 帶著舊資料被解構
```

優點：
- **自我指定自動安全**（複製品是獨立的）。
- **例外安全**：如果複製時記憶體不夠丟出例外，自己的資料完全沒被動到（第 13 課的「強保證」）。

**比喻**：要重新裝潢房子，先在旁邊蓋好一間新的，搬進去，再把舊的拆掉。蓋到一半失敗了，你還有舊房子可以住。

---

# 第四部分：移動語意 (Move Semantics)

## 4.1 為什麼需要移動？

```cpp
vector<string> v;
string s = make_huge_string();   // 一百萬個字元
v.push_back(s);                  // 複製一百萬個字元：s 之後還要用，合理
v.push_back(make_huge_string()); // 暫時物件馬上就要消失了，為什麼還要複製？
```

**移動**：對於「**馬上就要消失**」的物件，不用複製它的資源，直接 **偷過來**。

**比喻**：朋友要搬家，把舊公寓的家具送給你。
- **複製**：照著每件家具買一件新的，搬進你家（舊的再被丟掉）。
- **移動**：直接把舊家具搬過來。

## 4.2 右值參考 (Rvalue Reference)

**白話**：`T&&` 只能綁定 **右值**（暫時物件、快消失的東西）。用它來 **多載** 出「移動版本」的函式：

```cpp
void push_back(const T& x);   // 左值（還要用的）→ 複製
void push_back(T&& x);        // 右值（快消失的）→ 移動
```

編譯器根據引數是左值還是右值，自動挑選版本。

## 4.3 移動建構子與移動指定

```cpp
class Buffer {
    int* data_; size_t n_;
public:
    // 移動建構子：偷走 other 的資源
    Buffer(Buffer&& other) noexcept : data_(other.data_), n_(other.n_) {
        other.data_ = nullptr;     // ← 關鍵：讓 other 不再擁有它
        other.n_ = 0;
    }
    // 移動指定
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;        // 釋放自己原本的
            data_ = other.data_;   // 偷過來
            n_ = other.n_;
            other.data_ = nullptr;
            other.n_ = 0;
        }
        return *this;
    }
};
```

**一定要把對方的指標設成 `nullptr`**，不然兩個物件都以為自己擁有那塊記憶體，解構時 double free。

**被移動之後的物件 (moved-from object)**：處於「**有效但未指定**」的狀態 —— 可以安全地解構、重新指定，但不要假設它的內容。（`C06` 題規定移動後必須是空字串，這是我們自己的規格。）

## 4.4 std::move：其實什麼都沒移動

**白話**：`std::move(x)` **只是把 `x` 轉型成右值**，告訴編譯器「我不再需要 x 了，可以偷它」。真正的「偷」是移動建構子 / 移動指定做的。

```cpp
string a = "hello";
string b = std::move(a);   // 呼叫 string 的移動建構子
// a 現在是有效但未指定的狀態（實際上通常是空字串），不要再使用它的值
```

**比喻**：`std::move` 是在東西上貼一張「可以拿走」的標籤，它自己沒有搬任何東西。

**陷阱**：
```cpp
const string c = "hi";
string d = std::move(c);   // 還是「複製」！const 物件不能被偷（不能修改），只能退回複製版本
return std::move(local);   // ❌ 多此一舉，反而會妨礙複製省略 (RVO)
```

## 4.5 五法則與零法則 (Rule of Five / Rule of Zero)

**五法則**：C++11 之後，如果要自己管理資源，五個特殊成員函式都要考慮：
解構子、複製建構子、複製指定、**移動建構子**、**移動指定**。

**零法則**：**最好的做法是一個都不寫**。把資源交給 `vector`、`string`、`unique_ptr` 這些已經寫好五法則的類別管理，編譯器產生的預設版本就是對的。

```cpp
class Student {
    string name_;              // string 自己會正確複製 / 移動
    vector<int> scores_;       // vector 也是
    unique_ptr<Photo> photo_;  // unique_ptr 會讓 Student 自動變成「只能移動」
    // 不用寫任何解構子、複製、移動 → 零法則
};
```

**`= default` 和 `= delete`**：

```cpp
Matrix(const Matrix&) = delete;              // 禁止複製（C05 題的做法）
Matrix& operator=(const Matrix&) = delete;
Widget(Widget&&) = default;                  // 明確要求編譯器產生預設版本
```

## 4.6 🔍 為什麼移動要加 noexcept？

`vector` 擴容時要把舊元素搬到新空間。如果搬到一半出錯，`vector` 要能 **恢復原狀**（強例外保證）：
- **複製**：出錯了沒關係，舊的元素都還在。
- **移動**：舊的元素已經被偷走了，無法恢復。

所以 `vector` 只在 **移動建構子保證不丟例外（`noexcept`）** 時才會用移動，否則退回用複製。
**忘記加 `noexcept`，`vector<你的類別>` 擴容時會變成複製，效能大幅下降。**

---

# 第五部分：智慧指標 (Smart Pointers)

`#include <memory>`

## 5.1 所有權 (Ownership)

**白話**：誰 **負責** 在用完之後釋放這個物件。裸指標 `T*` 看不出來它是不是擁有者；智慧指標把所有權寫進型別裡。

## 5.2 unique_ptr：獨占所有權

**白話**：**只有一個** 擁有者。`unique_ptr` 被銷毀時，自動 `delete` 它擁有的物件。

```cpp
auto p = make_unique<Widget>(1, 2);    // 建立（推薦用 make_unique，不要自己 new）
p->method();                           // 用法跟指標一樣
unique_ptr<Widget> q = p;              // ❌ 編譯錯誤：不能複製（不能有兩個擁有者）
unique_ptr<Widget> q = std::move(p);   // ✅ 轉移所有權，p 變成 nullptr
Widget* raw = q.get();                 // 拿到裸指標（不轉移所有權，只是借看）
q.reset();                             // 立刻釋放
```

**比喻**：一把 **獨一無二的鑰匙**。不能複製，只能交給別人（交出去之後自己就沒有了）。最後拿著鑰匙的人離開時，房子就被回收。

成本：**跟裸指標一樣**（沒有額外的記憶體或時間）。**預設就用 `unique_ptr`**。

```cpp
vector<unique_ptr<Shape>> shapes;      // C08：用基底類別指標存不同的子類別
shapes.push_back(make_unique<Circle>(1.0));
```

## 5.3 shared_ptr：共享所有權

**白話**：**多個** 擁有者共享同一個物件。內部有一個 **參考計數 (reference count)**，記錄目前有幾個 `shared_ptr` 指向它；**最後一個** 被銷毀時才 `delete`。

```cpp
auto a = make_shared<Widget>();   // 計數 = 1
{
    shared_ptr<Widget> b = a;     // 可以複製，計數 = 2
}                                 // b 銷毀，計數 = 1
a.use_count();                    // 1
a.reset();                        // 計數 = 0 → delete Widget
```

**比喻**：圖書館的書。每借出一本就記一筆（計數 +1），歸還就劃掉（計數 −1）。最後一個人歸還、沒有人借了，書才可以下架。

成本：多一塊 **控制區塊 (control block)** 存計數；複製 / 銷毀時要 **原子地** 增減計數（為了多執行緒安全），比 `unique_ptr` 慢。

## 5.4 循環參考與 weak_ptr

**問題**：兩個物件用 `shared_ptr` **互相指著**，計數永遠不會變成 0 → **記憶體洩漏**。

```cpp
struct Person {
    shared_ptr<Person> partner;
};
auto a = make_shared<Person>(), b = make_shared<Person>();
a->partner = b;     // b 的計數 = 2
b->partner = a;     // a 的計數 = 2
}                   // a、b 這兩個區域變數銷毀，計數都變成 1，永遠不會到 0 → 洩漏
```

**weak_ptr**：**不擁有** 物件、**不增加計數** 的觀察者。要使用時先 `lock()`，如果物件還活著就拿到一個 `shared_ptr`，否則拿到空的。

```cpp
struct Person {
    weak_ptr<Person> partner;     // 改成 weak_ptr，打破循環
};
if (auto p = a->partner.lock()) { /* 對方還活著 */ }
```

**比喻**：`weak_ptr` 是「知道書在哪一個書架」，但沒有借書。要看的時候去書架找，書可能已經被下架了。

## 5.5 三種指標的選擇

| 情況 | 用什麼 |
|---|---|
| 這個物件只有一個擁有者（絕大多數情況） | `unique_ptr` |
| 真的有好幾個擁有者，不知道誰最後結束 | `shared_ptr` |
| 想觀察 `shared_ptr` 管理的物件，但不想延長它的生命 / 要打破循環 | `weak_ptr` |
| 只是 **借用**，不負責釋放（函式參數、走訪串列） | 裸指標 `T*` 或參考 `T&` |

**函式參數**：只是要使用物件時，傳 `T&` 或 `T*`，**不要傳智慧指標**。只有要轉移或共享所有權時才傳 `unique_ptr<T>`（傳值 + `move`）或 `shared_ptr<T>`。

---

# 第六部分：所有權的設計

## 6.1 用 unique_ptr 做資料結構

```cpp
struct Node {
    int val;
    unique_ptr<Node> next;   // 每個節點「擁有」下一個節點
};
// 樹也一樣：
struct TreeNode {
    int key;
    unique_ptr<TreeNode> left, right;
};
```

好處：不用寫任何 `delete`，不可能洩漏、不可能 double free。

## 6.2 🔍 解構的遞迴陷阱（C14 題）

銷毀串列的 `head` 時：
`~unique_ptr<Node>` → `delete` 第 1 個節點 → 第 1 個節點的成員 `next` 被銷毀 → `delete` 第 2 個節點 → ……

**這是遞迴**，深度等於串列長度。一百萬個節點 → 遞迴一百萬層 → **堆疊溢位**，程式在 **結束的時候** 當掉。

解法：自己寫解構子，用 **迴圈** 一個一個拆：

```cpp
~List() {
    while (head) head = std::move(head->next);
}
```

`head = std::move(head->next)` 的過程：
1. `head->next` 的所有權先被轉移到一個暫時的位置，`head->next` 變成空的。
2. `head` 原本擁有的節點被銷毀 —— 它的 `next` 已經是空的，**不會繼續遞迴**。
3. `head` 接收原本的第 2 個節點。

退化成一條鏈的二元樹（第 08 課 DS 路線）也有同樣的問題。

## 6.3 檢查清單

- [ ] 程式裡還有裸的 `new` / `delete` 嗎？能不能換成 `make_unique` 或容器？
- [ ] 自己寫了解構子的類別，有處理複製和移動嗎（或明確 `= delete`）？
- [ ] 複製指定能處理自我指定嗎？
- [ ] 移動建構子 / 移動指定有標 `noexcept` 嗎？有把對方設成空的嗎？
- [ ] 有 `shared_ptr` 互相指著的循環嗎？
- [ ] 很長的鏈狀結構，解構時會不會遞迴太深？
- [ ] 用 `--debug` 跑過一次了嗎？

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 堆疊區 / 堆積區 | Stack / Heap | 自動管理的小空間 / 手動管理的大空間 | 1.1 |
| 資源取得即初始化 | RAII | 建構時取得資源、解構時釋放 | 2.1 |
| 淺複製 / 深複製 | Shallow / Deep Copy | 只複製指標 / 複製指向的內容 | 3.1 |
| 複製建構子 | Copy Constructor | 用另一個物件建立新物件 | 3.2 |
| 複製指定運算子 | Copy Assignment Operator | 把另一個物件指定給已存在的物件 | 3.2 |
| 三法則 | Rule of Three | 解構、複製建構、複製指定要一起寫 | 3.2 |
| 自我指定 | Self-assignment | `a = a` | 3.3 |
| 複製並交換 | Copy-and-swap | 先複製再交換，自動處理自我指定與例外 | 3.4 |
| 移動語意 | Move Semantics | 偷走暫時物件的資源，不複製 | 4.1 |
| 右值參考 | Rvalue Reference `T&&` | 只綁定暫時物件 | 4.2 |
| 移動建構子 / 移動指定 | Move Constructor / Assignment | 偷資源的建構 / 指定 | 4.3 |
| 被移動後的物件 | Moved-from Object | 有效但未指定的狀態 | 4.3 |
| 五法則 / 零法則 | Rule of Five / Zero | 五個都要寫 / 最好一個都不用寫 | 4.5 |
| 所有權 | Ownership | 誰負責釋放 | 5.1 |
| 獨占指標 | unique_ptr | 唯一擁有者，不能複製 | 5.2 |
| 共享指標 | shared_ptr | 多個擁有者，參考計數 | 5.3 |
| 參考計數 | Reference Count | 記錄有幾個擁有者 | 5.3 |
| 循環參考 | Reference Cycle | 互相持有，計數永遠不歸零 | 5.4 |
| 弱指標 | weak_ptr | 觀察但不擁有 | 5.4 |

---

# 習題

### 題 1：預測輸出

```cpp
struct T {
    string name;
    T(string n) : name(n) { cout << "+" << name << ' '; }
    ~T() { cout << "-" << name << ' '; }
};
int main() {
    T a("a");
    {
        T b("b");
        T c("c");
    }
    T d("d");
}
```

### 題 2：這個類別有什麼問題？會在什麼時候出事？

```cpp
class IntArray {
    int* data; int n;
public:
    IntArray(int n) : data(new int[n]), n(n) {}
    ~IntArray() { delete[] data; }
};
void f(IntArray arr) { }
int main() {
    IntArray a(10);
    f(a);
}
```

### 題 3：下面每一行呼叫的是複製還是移動？

```cpp
string a = "x";
string b = a;                 // ①
string c = std::move(a);      // ②
string d = a + b;             // ③
const string e = "y";
string f = std::move(e);      // ④
vector<string> v;
v.push_back(b);               // ⑤
v.push_back(std::move(b));    // ⑥
```

### 題 4：哪幾行會編譯錯誤？

```cpp
auto p = make_unique<int>(5);
auto q = p;                       // ①
auto r = std::move(p);            // ②
unique_ptr<int> s(r.get());       // ③
cout << *p;                       // ④
```

另外，哪一行雖然能編譯，但會造成嚴重的執行期錯誤？

### 題 5：預測 `use_count` 的輸出

```cpp
auto a = make_shared<int>(1);
auto b = a;
{
    auto c = b;
    cout << a.use_count() << ' ';
}
weak_ptr<int> w = a;
cout << a.use_count() << ' ';
b.reset();
cout << a.use_count();
```

### 題 6：為什麼這段程式會洩漏記憶體？怎麼修？

```cpp
struct Node {
    shared_ptr<Node> parent;
    vector<shared_ptr<Node>> children;
};
```

### 題 7：移動建構子忘了寫 `other.data_ = nullptr;` 會發生什麼事？

### 題 8：一個類別只有 `string name; vector<int> v;` 兩個成員，需要自己寫解構子和複製建構子嗎？

---

# 習題解答

**題 1**：`+a +b +c -c -b +d -d -a`。區塊結束時，`b`、`c` 以 **相反順序** 銷毀；`main` 結束時 `d`、`a` 也以相反順序銷毀。

**題 2**：違反 **三法則**：有解構子，但沒有複製建構子 / 複製指定。`f(a)` **傳值** 會用預設的淺複製建立參數 `arr`，`arr.data` 和 `a.data` 指向同一塊記憶體。`f` 結束時 `arr` 解構，`delete[]` 一次；`main` 結束時 `a` 解構，又 `delete[]` 同一塊 → **double free**。修法：寫深複製的複製建構子和複製指定（或 `= delete` 禁止複製，或直接改用 `vector<int>`）。

**題 3**：① 複製；② 移動；③ 移動（`a + b` 是暫時物件，右值）—— 其實更可能是複製省略，連移動都沒有；④ **複製**（`const` 物件不能被偷）；⑤ 複製；⑥ 移動。

**題 4**：① 編譯錯誤（`unique_ptr` 不能複製）。
③ 能編譯，但讓 **兩個** `unique_ptr`（`r` 和 `s`）擁有同一個物件 → 兩個都會 `delete` 它 → **double free**。
④ 能編譯，但 `p` 已經被移動走了，是 `nullptr` → **解參考空指標**（題目問的「嚴重的執行期錯誤」③ 和 ④ 都是）。

**題 5**：`3 2 1`。`a`、`b`、`c` 共三個；`c` 銷毀後剩 2 個；`weak_ptr` **不增加計數**，仍然是 2；`b.reset()` 後剩 1 個。

**題 6**：父節點用 `shared_ptr` 擁有子節點，子節點又用 `shared_ptr` 指回父節點 → **循環參考**，計數永遠不會歸零。修法：`parent` 改成 `weak_ptr<Node>`（子節點不擁有父節點）。更簡單的設計：`children` 用 `unique_ptr`，`parent` 用裸指標 `Node*`（只是借用）。

**題 7**：`other` 和新物件都指向同一塊記憶體，兩個都以為自己是擁有者。`other` 解構時會 `delete` 那塊記憶體，新物件之後再用就是 use-after-free，解構時又 double free。

**題 8**：**不需要**（零法則）。`string` 和 `vector` 都已經正確實作了複製、移動、解構，編譯器產生的預設版本會一個成員一個成員地呼叫它們，結果就是對的。

---

# 程式練習

- **`C06 自己做一個字串類別`**：完整實作五法則。測資專門測自我指定、自我附加（`s += s`）、移動之後的狀態，最後還會檢查有沒有記憶體洩漏。
- **`C14 智慧指標串列`**：用 `unique_ptr` 實作串列，不准寫 `new` / `delete`。一百萬個節點的測資會抓出「解構的遞迴陷阱」。
