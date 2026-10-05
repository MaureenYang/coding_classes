# 06. 記憶體管理、RAII 與移動語意

> 程式練習：`C06 自己做一個字串類別`、`C14 智慧指標串列`
>
> 先備知識：第 05 課「指標錯誤大全」、第 07 課的「建構子 / 解構子」基本概念（也可以先讀第 07 課第一、二部分）。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 物件的生命 | 記憶體的四個區域、`new` / `delete` 到底做了什麼 |
| 第二部分 | RAII | C++ 最重要的設計慣例：讓物件自己管理資源 |
| 第三部分 | 複製語意 | 什麼時候會複製、淺複製的災難、三法則、自我指定、copy-and-swap |
| 第四部分 | 移動語意 | 右值參考、`std::move`、五法則、零法則、`noexcept` 為什麼重要 |
| 第五部分 | 智慧指標 | `unique_ptr`、`shared_ptr`、`weak_ptr` 的每一個操作、循環參考 |
| 第六部分 | 所有權的設計 | 什麼時候用什麼、解構的遞迴陷阱 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。這一課的很多範例會用一個「**會印出自己被建立、複製、移動、銷毀**」的類別，讓你親眼看到每一步發生了什麼。標 🔍 的是深入內容。

本課反覆使用的觀察工具：

```cpp
struct Tracer {
    string name;
    Tracer(string n) : name(n)            { cout << "建立 " << name << '\n'; }
    Tracer(const Tracer& o) : name(o.name + "'") { cout << "複製 " << name << '\n'; }
    Tracer(Tracer&& o) noexcept : name(o.name + "*") { cout << "移動 " << name << '\n'; }
    ~Tracer()                             { cout << "銷毀 " << name << '\n'; }
};
```

（複製出來的名字後面加 `'`、移動出來的加 `*`，方便分辨。）

---

# 第一部分：物件的生命

## 1.1 記憶體的四個區域

一個執行中的程式，記憶體大致分成四個區域：

| 區域 | 放什麼 | 誰管理 | 大小 | 生命週期 |
|---|---|---|---|---|
| **程式碼區 (text)** | 編譯好的機器碼 | 系統 | 固定 | 整個程式 |
| **靜態區 (static / data)** | 全域變數、`static` 變數、字串字面值 | 系統 | 固定 | 整個程式 |
| **堆疊區 (stack)** | 區域變數、函式參數、返回位址 | **自動** | 小（通常 1 ~ 8 MB） | 進入區塊時建立、離開時銷毀 |
| **堆積區 (heap / free store)** | `new` 出來的東西 | **程式設計師** | 大（整台電腦的記憶體） | `new` 到 `delete` |

每個區域的變數範例：

```cpp
int global_count = 0;                   // 靜態區
const char* msg = "hello";              // msg 本身在靜態區；"hello" 也在靜態區（唯讀）

void demo() {
    static int calls = 0;               // 靜態區（第一次執行到時初始化）
    int local = 5;                      // 堆疊區：demo 結束就消失
    int* p = new int(42);               // p 本身在堆疊區；new 出來的 int 在堆積區
    vector<int> v(1000);                // v 這個物件在堆疊區；那 1000 個 int 在堆積區
    delete p;                           // 堆積區的 int 要手動釋放
}                                       // local、p、v 被銷毀；v 的解構子自動釋放那 1000 個 int
```

**比喻**：
- **堆疊區** 像是餐廳的托盤：拿了就用，吃完自動收走，又快又方便，但不能疊太高（太大的陣列或太深的遞迴會 stack overflow）。
- **堆積區** 像是租倉庫：要多大有多大、想用多久就用多久，但 **不用了要自己去退租**，忘了就一直付錢（記憶體洩漏）。

**為什麼大陣列要放在堆積區？**

```cpp
void bad() {
    int huge[10000000];                 // ❌ 40 MB 放在堆疊區 → stack overflow → 當掉
}
void good() {
    vector<int> huge(10000000);         // ✅ vector 把資料放在堆積區
}
int big_global[10000000];               // ✅ 全域陣列放在靜態區，也沒問題
```

## 1.2 new 和 delete 做了什麼

```cpp
Tracer* p = new Tracer("A");
```

`new` 做了三件事：
1. 跟系統要一塊 `sizeof(Tracer)` 大小的記憶體（呼叫 `operator new`）。
2. 在那塊記憶體上 **呼叫建構子** `Tracer("A")`。
3. 回傳指向它的指標。

```cpp
delete p;
```

`delete` 做了兩件事：
1. **呼叫解構子** `~Tracer()`。
2. 把記憶體還給系統（呼叫 `operator delete`）。

```cpp
Tracer* p = new Tracer("A");     // 輸出：建立 A
delete p;                        // 輸出：銷毀 A
```

### 單一物件 vs 陣列

| 配置 | 釋放 | 說明 |
|---|---|---|
| `new T` / `new T(args)` | `delete p` | 單一物件 |
| `new T[n]` | `delete[] p` | 陣列：每個元素都要呼叫建構子 / 解構子 |

```cpp
struct Item { Item() { cout << "+"; } ~Item() { cout << "-"; } };
Item* arr = new Item[3];         // 輸出：+++（呼叫 3 次建構子）
delete[] arr;                    // 輸出：---（呼叫 3 次解構子）
cout << '\n';
```

`delete[]` 怎麼知道要解構幾個？`new[]` 會在陣列前面偷偷記下元素個數。如果用 `delete`（沒有 `[]`）釋放，就不會讀這個數字 → **未定義行為**（可能只解構第一個、可能當掉）。

### 初始化

```cpp
int* a = new int;          // 沒有初始化：垃圾值
int* b = new int();        // 值初始化：0
int* c = new int(7);       // 7
int* d = new int[5];       // 5 個垃圾值
int* e = new int[5]();     // 5 個 0
int* f = new int[3]{1, 2, 3};
cout << *b << ' ' << *c << ' ' << e[4] << ' ' << f[2] << '\n';   // 輸出：0 7 0 3
delete a; delete b; delete c;
delete[] d; delete[] e; delete[] f;
```

### 記憶體不夠

`new` 配置失敗時會丟出 `std::bad_alloc` 例外：

```cpp
try {
    long long* huge = new long long[1000000000000LL];   // 8 TB
    delete[] huge;
} catch (const bad_alloc& e) {
    cout << "記憶體不足\n";       // 輸出：記憶體不足
}
```

## 1.3 手動管理為什麼很容易出錯

```cpp
bool load(int* buf);
void compute(int* buf);       // 可能丟出例外

void process() {
    int* buf = new int[1000];
    if (!load(buf)) return;   // ❌ 提早 return，忘了 delete[] → 洩漏
    compute(buf);             // ❌ 如果 compute 丟出例外，下一行不會執行 → 洩漏
    delete[] buf;
}
```

函式每多一條離開的路徑（`return`、例外、`break`、`goto`），就要多記得一次 `delete`。**人一定會忘記**。下一部分的 RAII 就是為了解決這個問題。

---

# 第二部分：RAII

## 2.1 RAII (Resource Acquisition Is Initialization)

**是什麼**：直譯是「取得資源就是初始化」，意思是 —— **把資源的生命綁在一個物件的生命上**：
- **建構子** 取得資源（配置記憶體、開檔案、上鎖、建立網路連線）。
- **解構子** 釋放資源。

**為什麼有效？** C++ **保證**：區域物件離開作用域時，**一定** 會呼叫解構子 —— 不管是正常走到 `}`、`return`、`break`，還是丟出例外。所以資源 **一定** 會被釋放。

**比喻**：飯店房卡。退房（物件被銷毀）時，房卡自動失效、房間自動回收，你不需要另外記得「去櫃台歸還房間」。

### 例 1：管理記憶體

```cpp
class Buffer {
    int* data_;
public:
    explicit Buffer(size_t n) : data_(new int[n]()) { cout << "配置\n"; }   // 取得
    ~Buffer() { delete[] data_; cout << "釋放\n"; }                         // 釋放
    int* get() { return data_; }
    Buffer(const Buffer&) = delete;              // 先禁止複製（第三部分再說明）
    Buffer& operator=(const Buffer&) = delete;
};

bool process(bool fail_early) {
    Buffer buf(1000);
    if (fail_early) return false;   // ✅ buf 的解構子自動執行
    buf.get()[0] = 42;
    return true;                    // ✅ 正常結束也一樣
}
process(true);
process(false);
// 輸出：
// 配置
// 釋放
// 配置
// 釋放
```

### 例 2：就算丟出例外也會釋放

```cpp
void risky() { throw runtime_error("boom"); }
try {
    Buffer b(10);
    risky();                         // 丟出例外，離開這個區塊
    cout << "不會執行到這裡\n";
} catch (const exception& e) {
    cout << "捕捉到：" << e.what() << '\n';
}
// 輸出：
// 配置
// 釋放                ← 例外往外傳的途中，b 的解構子已經被呼叫了
// 捕捉到：boom
```

### 例 3：管理檔案（C 語言的 FILE*）

```cpp
class File {
    FILE* f_;
public:
    File(const char* path, const char* mode) : f_(fopen(path, mode)) {
        if (!f_) throw runtime_error("cannot open file");
    }
    ~File() { if (f_) fclose(f_); }     // 保證關檔
    FILE* get() { return f_; }
    File(const File&) = delete;
    File& operator=(const File&) = delete;
};
{
    File out("/tmp/raii_demo.txt", "w");
    fprintf(out.get(), "hello\n");
}   // 離開區塊時自動 fclose，不會忘記
```

### 例 4：計時器（建構時開始、解構時印出經過的時間）

```cpp
class ScopeTimer {
    string label_;
    chrono::steady_clock::time_point start_ = chrono::steady_clock::now();
public:
    explicit ScopeTimer(string label) : label_(move(label)) {}
    ~ScopeTimer() {
        auto ms = chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now() - start_).count();
        cout << label_ << " took " << ms << " ms\n";
    }
};
{
    ScopeTimer t("sorting");
    vector<int> v(1000000);
    sort(v.begin(), v.end());
}   // 輸出：sorting took 3 ms（數字依電腦而定）
```

RAII 不只能管理記憶體，**任何「開始之後一定要結束」的事** 都可以這樣做。

## 2.2 你已經在用 RAII 了

標準函式庫裡到處都是 RAII 類別：

| 類別 | 管理的資源 | 建構時 | 解構時 |
|---|---|---|---|
| `std::vector`、`std::string` | heap 記憶體 | 配置 | 釋放 |
| `std::ifstream` / `ofstream` | 檔案 | 開檔 | 關檔 |
| `std::lock_guard` | 互斥鎖 (mutex) | 上鎖 | 解鎖 |
| `std::unique_ptr` / `shared_ptr` | 任意 heap 物件 | 接收擁有權 | `delete` |

```cpp
// 檔案：不用手動 close
{
    ofstream fout("/tmp/raii2.txt");
    fout << "data\n";
}   // fout 的解構子自動關檔

// 鎖：不用手動 unlock，就算中間 return 或丟出例外也會解鎖
mutex m;
int shared_counter = 0;
void safe_increment() {
    lock_guard<mutex> lock(m);      // 建構時上鎖
    shared_counter++;
}                                   // 解構時解鎖
```

**現代 C++ 的原則**：程式裡 **幾乎不應該出現裸的 `new` / `delete`**，交給 RAII 類別（容器、智慧指標）處理。

## 2.3 🔍 解構的順序

**規則**：
- 同一個區塊裡的區域變數：**建立的相反順序** 銷毀（後建立的先銷毀）。
- 類別的成員：**宣告的相反順序** 銷毀；而且 **解構子本體先執行**，然後才銷毀成員。
- 繼承：先執行子類別的解構子，再執行父類別的（第 08 課）。

**區域變數**：

```cpp
{
    Tracer a("a");
    Tracer b("b");
    Tracer c("c");
}
// 輸出：建立 a、建立 b、建立 c、銷毀 c、銷毀 b、銷毀 a
```

**為什麼要反過來？** 後建立的物件可能 **依賴** 先建立的（例如 `b` 的建構子用到了 `a`）。所以要先拆掉 `b`，`a` 才能安全地被拆掉。

**成員**：

```cpp
struct Car {
    Tracer engine{"engine"};
    Tracer wheels{"wheels"};
    Car() { cout << "Car 建構完成\n"; }
    ~Car() { cout << "Car 解構子本體\n"; }
};
{ Car car; }
// 輸出：
// 建立 engine
// 建立 wheels
// Car 建構完成
// Car 解構子本體
// 銷毀 wheels
// 銷毀 engine
```

---

# 第三部分：複製語意 (Copy Semantics)

## 3.1 什麼時候會複製？

**複製建構子** 會在「**用一個現有的物件，建立一個新的物件**」時被呼叫：

| 情況 | 範例 |
|---|---|
| 用另一個物件初始化 | `Tracer b = a;` 或 `Tracer b(a);` |
| 傳值給函式 | `void f(Tracer t); f(a);` |
| 放進容器 | `v.push_back(a);` |
| 從函式回傳（沒有被省略時） | 通常會被複製省略或改成移動 |

**複製指定運算子** 則是在「**把一個物件指定給另一個已經存在的物件**」時被呼叫：`b = a;`

```cpp
void by_value(Tracer t) { }

Tracer a("a");                 // 輸出：建立 a
Tracer b = a;                  // 複製建構 → 輸出：複製 a'
by_value(a);                   // 傳值 → 輸出：複製 a'、銷毀 a'（參數在函式結束時銷毀）
vector<Tracer> v;
v.reserve(10);
v.push_back(a);                // 放進容器 → 輸出：複製 a'
```

## 3.2 預設的複製是「淺複製」

**是什麼**：如果你沒有自己寫複製建構子，編譯器會產生一個「**一個成員一個成員地複製**」的版本。對 `int`、`string`、`vector` 這些成員來說沒問題（它們自己知道怎麼正確地複製）；但對 **指標成員** 來說，**只複製了位址，沒有複製指向的內容**。這叫 **淺複製 (shallow copy)**。

```cpp
class BadArray {
public:
    int* data;
    int n;
    BadArray(int n) : data(new int[n]()), n(n) {}
    ~BadArray() { delete[] data; }
    // 沒有寫複製建構子 → 編譯器產生的版本只複製 data 這個指標
};

BadArray a(3);
BadArray b = a;                          // 淺複製
cout << (a.data == b.data) << '\n';      // 輸出：1（兩個指向同一塊記憶體！）
b.data[0] = 99;
cout << a.data[0] << '\n';               // 輸出：99（改 b 也改到了 a）
}   // b 解構：delete[] data
    // a 解構：delete[] data 同一塊 → 重複釋放 (double free) → 當掉
```

```
淺複製：                    深複製：
a.data ──┐                  a.data ──▶ [0 0 0]
         ├──▶ [99 0 0]
b.data ──┘                  b.data ──▶ [0 0 0]（另一份）
```

**比喻**：淺複製是「給朋友一把你家的備份鑰匙」—— 同一間房子，他亂丟東西你家也亂；你把房子賣了，他的鑰匙也沒用了。深複製是「幫朋友蓋一間一模一樣的房子」。

## 3.3 三法則 (Rule of Three)

**規則**：如果你的類別需要自己寫 **以下任何一個**，通常 **三個都要寫**：

1. **解構子** `~T()`
2. **複製建構子** `T(const T& other)`：用另一個物件 **建立** 新物件
3. **複製指定運算子** `T& operator=(const T& other)`：把另一個物件 **指定給已存在的** 物件

**原因**：需要自己寫解構子，代表這個類別管理了某種資源（例如用 `new` 配置的記憶體）；那麼預設的「淺複製」一定是錯的。

**完整的正確版本**：

```cpp
class IntArray {
    int* data_;
    int n_;
public:
    explicit IntArray(int n) : data_(new int[n]()), n_(n) {}

    ~IntArray() { delete[] data_; }                         // 1. 解構子

    IntArray(const IntArray& o) : data_(new int[o.n_]), n_(o.n_) {   // 2. 複製建構子：深複製
        copy(o.data_, o.data_ + n_, data_);
    }

    IntArray& operator=(const IntArray& o) {                // 3. 複製指定
        if (this == &o) return *this;                       //    處理自我指定（3.4）
        int* nd = new int[o.n_];                            //    先配置新的（可能丟出例外）
        copy(o.data_, o.data_ + o.n_, nd);
        delete[] data_;                                     //    成功了才釋放舊的
        data_ = nd;
        n_ = o.n_;
        return *this;
    }

    int& operator[](int i) { return data_[i]; }
    int size() const { return n_; }
};

IntArray a(3);
a[0] = 5;
IntArray b = a;            // 複製建構：b 有自己的一份
b[0] = 99;
cout << a[0] << ' ' << b[0] << '\n';   // 輸出：5 99（互不影響）

IntArray c(10);
c = a;                     // 複製指定：c 原本的 10 個元素被釋放，換成 a 的複製品
cout << c.size() << ' ' << c[0] << '\n';   // 輸出：3 5
```

**複製建構 vs 複製指定的差別**：

```cpp
IntArray x = a;    // 複製建構：x 是「新出生」的，沒有舊資源要處理
IntArray y(5);
y = a;             // 複製指定：y 已經存在，要先處理 y 原本的資源（釋放那 5 個 int）
```

## 3.4 自我指定 (Self-assignment)

**是什麼**：`a = a;`。看起來很蠢，但在 `v[i] = v[j]`（`i == j`）、`*p = *q`（`p` 和 `q` 指向同一個物件）時會不知不覺發生。

**錯誤的寫法**：

```cpp
IntArray& operator=(const IntArray& o) {
    delete[] data_;                       // ① 先釋放自己的
    data_ = new int[o.n_];                // ② 配置新的
    copy(o.data_, o.data_ + o.n_, data_); // ③ 從 o 複製 —— 但 o 就是自己，o.data_ 已經在 ① 被釋放了！
    n_ = o.n_;
    return *this;
}
```

自我指定時：`o` 和 `*this` 是同一個物件，① 釋放了資料，③ 從已經釋放的記憶體讀資料 → **use-after-free**。這就是 `C06` 測資 `corner_self_copy` 在測的陷阱。

**兩種解法**：
1. 開頭檢查 `if (this == &o) return *this;`（3.3 的寫法）。
2. 使用 copy-and-swap（下一節）。

## 3.5 copy-and-swap 慣用法

**是什麼**：先用複製建構子 **做一份複製品**，再把自己的內容和複製品 **交換**，舊的內容會跟著複製品一起被銷毀。

```cpp
class IntArray2 {
    int* data_; int n_;
public:
    explicit IntArray2(int n) : data_(new int[n]()), n_(n) {}
    ~IntArray2() { delete[] data_; }
    IntArray2(const IntArray2& o) : data_(new int[o.n_]), n_(o.n_) { copy(o.data_, o.data_ + n_, data_); }

    IntArray2& operator=(IntArray2 other) {   // ① 參數是「傳值」：呼叫時就已經複製好了
        swap(data_, other.data_);             // ② 和複製品交換內容（只交換指標，不會失敗）
        swap(n_, other.n_);
        return *this;
    }                                         // ③ other 帶著「舊的資料」被解構
};
```

**優點**：
- **自我指定自動安全**：複製品是獨立的一份。
- **例外安全**：如果複製時記憶體不夠丟出例外，例外發生在 ① 參數建立的時候，**自己的資料完全沒被動到**（第 13 課的「強保證」）。
- **程式碼最少**：重用了複製建構子和解構子。

**比喻**：要重新裝潢房子，先在旁邊蓋好一間新的，搬進去，再把舊的拆掉。蓋到一半失敗了，你還有舊房子可以住。

---

# 第四部分：移動語意 (Move Semantics)

## 4.1 為什麼需要移動？

```cpp
vector<string> names;
string s = string(1000000, 'x');    // 一百萬個字元
names.push_back(s);                 // 複製一百萬個字元：合理，s 之後還要用
names.push_back(string(1000000, 'y'));   // 暫時物件，這一行結束就要被丟掉了 —— 為什麼還要複製？
```

**移動**：對於「**馬上就要消失**」的物件，不用複製它的資源，直接 **把資源偷過來**。對 `string` 來說，就是把內部指向字元陣列的指標拿過來，原本的 `string` 變成空的。複製一百萬個字元變成複製一個指標。

**比喻**：朋友要搬家，把舊公寓的家具送給你。
- **複製**：照著每件家具買一件一模一樣的新的，搬進你家，然後朋友的舊家具被丟掉。
- **移動**：直接把舊家具搬到你家。

## 4.2 右值參考 (Rvalue Reference)

**是什麼**：`T&&` 只能綁定 **右值**（暫時物件、快要消失的東西）。用它來多載出「**移動版本**」的函式：

```cpp
void store(const string& s) { cout << "複製版本\n"; }   // 接受左值（還要用的東西）
void store(string&& s)      { cout << "移動版本\n"; }   // 接受右值（快消失的東西）

string name = "amy";
store(name);                       // name 有名字、之後還可能用 → 輸出：複製版本
store(string("bob"));              // 暫時物件 → 輸出：移動版本
store(name + "!");                 // 暫時物件 → 輸出：移動版本
store(std::move(name));            // 明確說「name 我不要了」→ 輸出：移動版本
```

編譯器根據引數是左值還是右值，**自動挑選** 版本。`vector::push_back` 就是這樣，有 `push_back(const T&)` 和 `push_back(T&&)` 兩個版本。

## 4.3 移動建構子與移動指定

```cpp
class IntArray3 {
    int* data_; int n_;
public:
    explicit IntArray3(int n) : data_(new int[n]()), n_(n) {}
    ~IntArray3() { delete[] data_; }

    // 移動建構子：偷走 other 的資源
    IntArray3(IntArray3&& other) noexcept : data_(other.data_), n_(other.n_) {
        other.data_ = nullptr;     // ← 關鍵：讓 other 不再擁有它
        other.n_ = 0;
    }

    // 移動指定
    IntArray3& operator=(IntArray3&& other) noexcept {
        if (this != &other) {
            delete[] data_;        // 釋放自己原本的
            data_ = other.data_;   // 偷過來
            n_ = other.n_;
            other.data_ = nullptr;
            other.n_ = 0;
        }
        return *this;
    }
    int size() const { return n_; }
};

IntArray3 a(1000);
IntArray3 b = std::move(a);              // 移動建構：只搬了一個指標
cout << a.size() << ' ' << b.size() << '\n';   // 輸出：0 1000
```

**一定要把對方的指標設成 `nullptr`**：不然兩個物件都以為自己擁有那塊記憶體，解構時 double free。（`delete[] nullptr` 是安全的，什麼都不做。）

### 被移動之後的物件 (Moved-from Object)

**規則**：被移動之後，物件處於「**有效但未指定 (valid but unspecified)**」的狀態：
- ✅ 可以安全地 **解構**。
- ✅ 可以 **重新指定** 新的值。
- ❌ 不要假設它的內容（標準函式庫的 `string`、`vector` 實際上通常是空的，但標準不保證）。

```cpp
string s1 = "hello";
string s2 = std::move(s1);
cout << s2 << " [" << s1 << "]\n";       // 輸出：hello []（GCC 的實作：s1 變成空字串）
s1 = "reuse";                            // ✅ 重新指定是安全的
cout << s1 << '\n';                      // 輸出：reuse

vector<int> v1 = {1, 2, 3};
vector<int> v2 = std::move(v1);
cout << v1.size() << ' ' << v2.size() << '\n';   // 輸出：0 3
```

（`C06` 題規定移動後必須是空字串，這是我們自己的規格。）

## 4.4 std::move：其實什麼都沒移動

**是什麼**：`std::move(x)` **只是把 `x` 轉型成右值**（`static_cast<T&&>(x)`），告訴編譯器「我不再需要 x 了，可以偷它」。**真正的「偷」是移動建構子 / 移動指定做的**。

**比喻**：`std::move` 是在東西上貼一張「可以拿走」的標籤。它自己什麼都沒搬，但看到標籤的人（移動建構子）就會把它拿走。

```cpp
string a = "data";
std::move(a);                      // 只是轉型，沒有人接收 → 什麼都沒發生
cout << a << '\n';                 // 輸出：data（a 完全沒變）
string b = std::move(a);           // 這次有人「接收」了：string 的移動建構子把資料偷走
cout << "[" << a << "]\n";         // 輸出：[]
```

### 什麼時候會發生移動？

| 情況 | 會移動嗎？ | 範例 |
|---|---|---|
| 用暫時物件初始化 | ✅ 自動（或直接省略） | `string s = string("x") + "y";` |
| 把暫時物件放進容器 | ✅ 自動 | `v.push_back(string("x"));` |
| 用 `std::move` 標記 | ✅ | `v.push_back(std::move(s));` |
| `return` 區域變數 | ✅ 自動（或複製省略） | `return local;` |
| 用有名字的變數初始化 | ❌ 複製 | `string t = s;` |
| `const` 物件 + `std::move` | ❌ **還是複製** | `const string c; string d = std::move(c);` |

用 Tracer 觀察：

```cpp
vector<Tracer> v;
v.reserve(10);
Tracer t("t");                    // 輸出：建立 t
v.push_back(t);                   // 輸出：複製 t'
v.push_back(std::move(t));        // 輸出：移動 t*
v.push_back(Tracer("tmp"));       // 輸出：建立 tmp、移動 tmp*、銷毀 tmp（暫時物件被移動後銷毀）
v.emplace_back("direct");         // 輸出：建立 direct（直接在 vector 裡建構，連移動都不用）
```

### 兩個常見的錯誤

**錯誤 1：對 const 物件 std::move**

```cpp
const string c = "constant";
string d = std::move(c);   // 還是「複製」！const 物件不能被修改，所以不能被偷，只能退回複製版本
cout << c << '\n';         // 輸出：constant（c 沒變）
```

**錯誤 2：return std::move(local)**

```cpp
string make() {
    string local = "result";
    return std::move(local);   // ❌ 多此一舉，反而妨礙了「複製省略」
    // return local;           // ✅ 編譯器會自動省略複製，或至少自動移動
}
```

GCC 加 `-Wall` 會警告 `moving a local object in a return statement prevents copy elision`。

## 4.5 五法則與零法則 (Rule of Five / Rule of Zero)

**五法則**：C++11 之後，如果要自己管理資源，五個特殊成員函式都要考慮：

| # | 成員函式 | 什麼時候被呼叫 |
|---|---|---|
| 1 | 解構子 `~T()` | 物件被銷毀 |
| 2 | 複製建構子 `T(const T&)` | 用左值建立新物件 |
| 3 | 複製指定 `T& operator=(const T&)` | 把左值指定給現有物件 |
| 4 | 移動建構子 `T(T&&) noexcept` | 用右值建立新物件 |
| 5 | 移動指定 `T& operator=(T&&) noexcept` | 把右值指定給現有物件 |

**🔍 只寫了其中幾個，其他的會怎樣？**
- 自己寫了 **解構子、複製建構子或複製指定** 任何一個 → 編譯器 **不會** 自動產生移動操作 → 移動會退回用 **複製**（能用，但慢）。
- 自己寫了 **移動建構子或移動指定** → 編譯器把複製操作設成 **刪除 (deleted)** → 物件不能被複製。

**零法則**：**最好的做法是一個都不寫**。把資源交給 `vector`、`string`、`unique_ptr` 這些已經正確實作五法則的類別管理，編譯器自動產生的版本就是對的。

```cpp
class Student {
    string name_;               // string 自己會正確地複製 / 移動 / 解構
    vector<int> scores_;        // vector 也是
public:
    Student(string n) : name_(std::move(n)) {}
    // 不用寫任何解構子、複製、移動 → 零法則
};
Student s1("amy");
Student s2 = s1;                // ✅ 自動深複製（name_ 和 scores_ 各自複製）
Student s3 = std::move(s1);     // ✅ 自動移動
```

### = default 和 = delete

```cpp
class NonCopyable {
public:
    NonCopyable() = default;                           // 明確要求編譯器產生預設版本
    NonCopyable(const NonCopyable&) = delete;          // 禁止複製
    NonCopyable& operator=(const NonCopyable&) = delete;
    NonCopyable(NonCopyable&&) = default;              // 但允許移動
    NonCopyable& operator=(NonCopyable&&) = default;
};
NonCopyable x;
// NonCopyable y = x;           // ❌ error: use of deleted function
NonCopyable z = std::move(x);   // ✅
```

`C05` 的 `Matrix` 就用 `= delete` 禁止複製，避免淺複製的問題。

## 4.6 🔍 為什麼移動建構子要加 noexcept？

`vector` 擴容時，要把舊空間的元素搬到新空間。`vector::push_back` 承諾「**強例外保證**」：如果搬到一半出錯，`vector` 要回到原本的樣子（第 13 課）。

- **用複製搬**：出錯了沒關係，舊空間的元素都還在，直接丟掉新空間就好。
- **用移動搬**：舊空間的元素已經被偷走了，出錯時 **無法恢復**。

所以 `vector` 的策略是：**只有在移動建構子保證不會丟例外（`noexcept`）時，才用移動；否則退回用複製**。

**實驗**：

```cpp
struct WithNoexcept {
    WithNoexcept() = default;
    WithNoexcept(const WithNoexcept&) { cout << "C"; }
    WithNoexcept(WithNoexcept&&) noexcept { cout << "M"; }
};
struct WithoutNoexcept {
    WithoutNoexcept() = default;
    WithoutNoexcept(const WithoutNoexcept&) { cout << "C"; }
    WithoutNoexcept(WithoutNoexcept&&) { cout << "M"; }       // 忘了 noexcept
};

vector<WithNoexcept> v1(4);
v1.push_back(WithNoexcept());      // 擴容：舊的 4 個元素用「移動」搬過去
cout << '\n';                       // 輸出：MMMMM（新元素 1 次 + 舊元素 4 次）

vector<WithoutNoexcept> v2(4);
v2.push_back(WithoutNoexcept());   // 擴容：舊的 4 個元素用「複製」搬過去！
cout << '\n';                       // 輸出：MCCCC
```

**忘記加 `noexcept`，`vector<你的類別>` 擴容時就會變成複製**。如果元素是很大的字串或陣列，效能會大幅下降。

---

# 第五部分：智慧指標 (Smart Pointers)

`#include <memory>`

## 5.1 所有權 (Ownership)

**是什麼**：誰 **負責** 在用完之後釋放這個物件。

裸指標 `T*` 最大的問題是 **看不出所有權**：

```cpp
Widget* get_widget();   // 回傳的指標要不要 delete？是誰負責？看宣告完全不知道
```

智慧指標把所有權 **寫進型別** 裡，而且自動負責釋放（RAII）。

## 5.2 unique_ptr：獨占所有權

**是什麼**：**只有一個** 擁有者。`unique_ptr` 被銷毀時，自動 `delete` 它擁有的物件。

**比喻**：一把 **獨一無二的鑰匙**。不能複製，只能交給別人（交出去之後自己就沒有了）。最後拿著鑰匙的人離開時，房子就被回收。

**成本**：**跟裸指標一樣**（沒有額外的記憶體或時間）。**預設就用 `unique_ptr`**。

### unique_ptr 的每一個操作

```cpp
// 1. 建立：用 make_unique（不要自己寫 new）
auto p = make_unique<Tracer>("A");        // 輸出：建立 A

// 2. 使用：跟指標一樣
cout << p->name << ' ' << (*p).name << '\n';   // 輸出：A A

// 3. 檢查是否為空
if (p) cout << "p 有東西\n";              // 輸出：p 有東西

// 4. 不能複製
// unique_ptr<Tracer> q = p;              // ❌ error: use of deleted function（不能有兩個擁有者）

// 5. 可以移動：轉移所有權
unique_ptr<Tracer> q = std::move(p);      // 所有權從 p 轉移到 q，物件本身沒有被複製或移動
cout << (p == nullptr) << '\n';           // 輸出：1（p 變成空的）

// 6. get()：拿到裸指標（只是借看，不轉移所有權）
Tracer* raw = q.get();
cout << raw->name << '\n';                // 輸出：A

// 7. reset()：立刻釋放（或換成新的物件）
q.reset();                                // 輸出：銷毀 A
q.reset(new Tracer("B"));                 // 輸出：建立 B
// 8. release()：放棄所有權，回傳裸指標（之後要自己 delete！很少用）
Tracer* manual = q.release();
delete manual;                            // 輸出：銷毀 B
```

### 離開作用域時自動釋放

```cpp
{
    auto x = make_unique<Tracer>("X");    // 輸出：建立 X
    cout << "使用中\n";                    // 輸出：使用中
}                                          // 輸出：銷毀 X（自動 delete）
```

### 放進容器

```cpp
vector<unique_ptr<Tracer>> v;
v.push_back(make_unique<Tracer>("v1"));   // 輸出：建立 v1
v.push_back(make_unique<Tracer>("v2"));   // 輸出：建立 v2
v.clear();                                // 輸出：銷毀 v1、銷毀 v2
```

`C08` 的 `vector<unique_ptr<Shape>>` 就是這樣：用基底類別的指標存不同的子類別，`vector` 銷毀時自動 `delete` 每一個。

### 傳給函式

| 函式想要…… | 參數寫法 | 呼叫方式 |
|---|---|---|
| 只是 **使用** 物件 | `void use(Tracer& t)` 或 `void use(Tracer* t)` | `use(*p);` / `use(p.get());` |
| **接收所有權**（之後由函式負責） | `void take(unique_ptr<Tracer> t)` | `take(std::move(p));` |

```cpp
void use(const Tracer& t) { cout << "使用 " << t.name << '\n'; }
void take(unique_ptr<Tracer> t) { cout << "接收 " << t->name << '\n'; }   // 函式結束時 t 被銷毀

auto u = make_unique<Tracer>("U");   // 輸出：建立 U
use(*u);                             // 輸出：使用 U（u 還是擁有者）
take(std::move(u));                  // 輸出：接收 U、銷毀 U（所有權交給 take，take 結束就銷毀了）
cout << (u == nullptr) << '\n';      // 輸出：1
```

**原則**：**只是使用的話，不要傳智慧指標**，傳參考或裸指標就好。

### 陣列版本

```cpp
auto arr = make_unique<int[]>(5);    // 5 個 int，全部是 0
arr[2] = 7;
cout << arr[2] << '\n';              // 輸出：7
// 離開作用域時自動 delete[]（但一般直接用 vector 更好）
```

## 5.3 shared_ptr：共享所有權

**是什麼**：**多個** 擁有者共享同一個物件。內部有一個 **參考計數 (reference count)**，記錄目前有幾個 `shared_ptr` 指向它；**最後一個** 被銷毀時才 `delete`。

**比喻**：圖書館的書。每借出一本就記一筆（計數 +1），歸還就劃掉（計數 −1）。最後一個人歸還、沒有人借了，書才可以下架。

```cpp
auto a = make_shared<Tracer>("S");      // 輸出：建立 S
cout << a.use_count() << '\n';          // 輸出：1
{
    shared_ptr<Tracer> b = a;           // 可以複製：計數 +1
    shared_ptr<Tracer> c = b;           // 計數 +1
    cout << a.use_count() << '\n';      // 輸出：3
}                                        // b、c 被銷毀：計數 −2
cout << a.use_count() << '\n';          // 輸出：1
shared_ptr<Tracer> d = std::move(a);    // 移動：所有權轉移，計數不變
cout << d.use_count() << ' ' << (a == nullptr) << '\n';   // 輸出：1 1
d.reset();                              // 計數變成 0 → 輸出：銷毀 S
```

**什麼時候真的需要 shared_ptr？** 物件有 **好幾個擁有者**，而且 **不知道誰會最後結束**。例如：好幾個視窗共用同一份設定、圖形編輯器中好幾個圖層共用同一張圖片。大部分情況其實有明確的擁有者，用 `unique_ptr` 就好。

**成本**：
- 多一塊 **控制區塊 (control block)** 存計數（`make_shared` 會把它和物件放在同一塊記憶體）。
- 複製 / 銷毀時要 **原子地 (atomically)** 增減計數（為了多執行緒安全），比 `unique_ptr` 慢。

## 5.4 循環參考與 weak_ptr

**問題**：兩個物件用 `shared_ptr` **互相指著**，計數永遠不會變成 0 → **記憶體洩漏**。

```cpp
struct Person {
    string name;
    shared_ptr<Person> partner;
    Person(string n) : name(n) { cout << "建立 " << name << '\n'; }
    ~Person() { cout << "銷毀 " << name << '\n'; }
};
{
    auto amy = make_shared<Person>("amy");    // amy 的計數 = 1
    auto bob = make_shared<Person>("bob");    // bob 的計數 = 1
    amy->partner = bob;                        // bob 的計數 = 2
    bob->partner = amy;                        // amy 的計數 = 2
}
// 輸出：建立 amy、建立 bob
// 區塊結束時，區域變數 amy、bob 被銷毀，兩個計數都變成 1
// 但它們互相持有對方，計數永遠不會到 0 → 「銷毀」永遠不會印出來 → 洩漏
```

```
amy 物件 ──partner──▶ bob 物件
    ▲                    │
    └──────partner───────┘    互相持有，誰都放不掉
```

**weak_ptr**：**不擁有** 物件、**不增加計數** 的觀察者。

| 操作 | 意思 |
|---|---|
| `weak_ptr<T> w = sp;` | 觀察 `sp` 管理的物件（計數不變） |
| `w.expired()` | 物件已經被銷毀了嗎？ |
| `w.lock()` | 物件還活著 → 回傳一個 `shared_ptr`（暫時延長生命）；已經銷毀 → 回傳空的 |
| `w.use_count()` | 目前有幾個 `shared_ptr` 擁有它 |

```cpp
struct Person2 {
    string name;
    weak_ptr<Person2> partner;                // 改成 weak_ptr：觀察但不擁有
    Person2(string n) : name(n) {}
    ~Person2() { cout << "銷毀 " << name << '\n'; }
};
{
    auto amy = make_shared<Person2>("amy");
    auto bob = make_shared<Person2>("bob");
    amy->partner = bob;                        // 計數不變，還是 1
    bob->partner = amy;
    if (auto p = amy->partner.lock())          // 要用的時候 lock() 拿到 shared_ptr
        cout << amy->name << " 的伴侶是 " << p->name << '\n';
}
// 輸出：
// amy 的伴侶是 bob
// 銷毀 bob
// 銷毀 amy        ← 正確地被釋放了
```

**weak_ptr 觀察到物件消失**：

```cpp
weak_ptr<int> w;
{
    auto sp = make_shared<int>(42);
    w = sp;
    cout << w.expired() << ' ' << *w.lock() << '\n';   // 輸出：0 42
}                                                       // sp 被銷毀，物件也被銷毀
cout << w.expired() << ' ' << (w.lock() == nullptr) << '\n';   // 輸出：1 1
```

**比喻**：`weak_ptr` 是「知道書在哪一個書架」，但沒有借書。要看的時候去書架找（`lock`），書可能已經被下架了。

## 5.5 三種指標的選擇

| 情況 | 用什麼 | 範例 |
|---|---|---|
| 物件只有一個擁有者（**絕大多數情況**） | `unique_ptr` | 樹的子節點、`vector<unique_ptr<Shape>>` |
| 真的有好幾個擁有者，不知道誰最後結束 | `shared_ptr` | 多個視窗共用的設定物件 |
| 觀察 `shared_ptr` 管理的物件，但不想延長它的生命 / 打破循環 | `weak_ptr` | 子節點指回父節點、快取 |
| 只是 **借用**，不負責釋放（函式參數、走訪） | 裸指標 `T*` 或參考 `T&` | `void draw(const Shape& s)`、`for (Node* p = head.get(); ...)` |

**一個樹的例子**，同時用到三種：

```cpp
struct TreeNode {
    int val;
    vector<unique_ptr<TreeNode>> children;   // 父節點「擁有」子節點
    TreeNode* parent = nullptr;              // 子節點只是「知道」父節點在哪（借用）
    TreeNode(int v) : val(v) {}
};
auto root = make_unique<TreeNode>(1);
root->children.push_back(make_unique<TreeNode>(2));
root->children[0]->parent = root.get();
cout << root->children[0]->parent->val << '\n';   // 輸出：1
// root 被銷毀時，所有子節點自動被銷毀；parent 是裸指標，不會造成循環
```

---

# 第六部分：所有權的設計

## 6.1 用 unique_ptr 做資料結構

```cpp
struct Node {
    int val;
    unique_ptr<Node> next;   // 每個節點「擁有」下一個節點
};
// 插入到最前面
unique_ptr<Node> head;
for (int x : {3, 2, 1}) {
    auto nd = make_unique<Node>();
    nd->val = x;
    nd->next = std::move(head);      // 新節點接收舊的串列
    head = std::move(nd);            // head 改成新節點
}
for (Node* p = head.get(); p; p = p->next.get()) cout << p->val;   // 走訪用裸指標（借用）
cout << '\n';                        // 輸出：123
```

好處：不用寫任何 `delete`，不可能洩漏、不可能 double free。

## 6.2 🔍 解構的遞迴陷阱（C14 題）

銷毀串列的 `head` 時：
`~unique_ptr<Node>` → `delete` 第 1 個節點 → 第 1 個節點的成員 `next` 被銷毀 → `delete` 第 2 個節點 → 第 2 個節點的 `next` 被銷毀 → ……

**這是遞迴**，深度等於串列長度。

```cpp
{
    unique_ptr<Node> big;
    for (int i = 0; i < 1000000; i++) {
        auto nd = make_unique<Node>();
        nd->next = std::move(big);
        big = std::move(nd);
    }
}   // ❌ 這裡解構時遞迴一百萬層 → 堆疊溢位 → 程式在「結束的時候」當掉（我們實測：10 萬個沒事，100 萬個當掉）
```

**解法**：自己寫解構子（或 `clear`），用 **迴圈** 一個一個拆：

```cpp
class List {
    unique_ptr<Node> head;
public:
    ~List() {
        while (head) head = std::move(head->next);
    }
};
```

`head = std::move(head->next)` 的過程：
1. `head->next` 的所有權先被移到一個暫時的位置，`head->next` 變成空的。
2. `head` 原本擁有的節點被銷毀 —— 它的 `next` 已經是空的，**不會繼續遞迴**。
3. `head` 接收原本的第 2 個節點。

每次只銷毀一個節點，堆疊深度永遠是常數。退化成一條鏈的二元樹（DS 路線第 08 課）也有同樣的問題。

## 6.3 檢查清單

| 檢查項目 | 為什麼 | 對應章節 |
|---|---|---|
| 程式裡還有裸的 `new` / `delete` 嗎？ | 能換成容器或 `make_unique` 就換 | 2.2、5.2 |
| 自己寫了解構子的類別，有處理複製和移動嗎？ | 否則預設的淺複製會造成 double free | 3.2、3.3 |
| 複製指定能處理自我指定嗎？ | `a = a` 時不能先釋放再複製 | 3.4 |
| 移動建構子 / 移動指定有標 `noexcept` 嗎？ | 否則 `vector` 擴容時會改用複製 | 4.6 |
| 移動之後有把對方設成空的嗎？ | 否則兩個物件都會釋放同一塊記憶體 | 4.3 |
| 有對 `const` 物件用 `std::move` 嗎？ | 不會移動，只會複製 | 4.4 |
| 有 `shared_ptr` 互相指著的循環嗎？ | 會洩漏，改用 `weak_ptr` 或裸指標 | 5.4 |
| 函式參數只是要「使用」物件，卻傳了智慧指標？ | 改傳參考或裸指標 | 5.2 |
| 很長的鏈狀結構，解構時會不會遞迴太深？ | 自己寫迴圈版的解構子 | 6.2 |
| 用 `--debug` 跑過一次了嗎？ | AddressSanitizer 會抓到洩漏、double free、use-after-free | 第 05 課 |

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 堆疊區 / 堆積區 | Stack / Heap | 自動管理的小空間 / 手動管理的大空間 | 1.1 |
| 資源取得即初始化 | RAII | 建構時取得資源、解構時釋放 | 2.1 |
| 互斥鎖 | Mutex | 多執行緒時保護共用資料的鎖 | 2.2 |
| 淺複製 / 深複製 | Shallow / Deep Copy | 只複製指標 / 複製指向的內容 | 3.2 |
| 重複釋放 | Double Free | 同一塊記憶體 delete 兩次 | 3.2 |
| 複製建構子 | Copy Constructor | 用另一個物件建立新物件 | 3.3 |
| 複製指定運算子 | Copy Assignment Operator | 把另一個物件指定給已存在的物件 | 3.3 |
| 三法則 | Rule of Three | 解構、複製建構、複製指定要一起寫 | 3.3 |
| 自我指定 | Self-assignment | `a = a` | 3.4 |
| 複製並交換 | Copy-and-swap | 先複製再交換，自動處理自我指定與例外 | 3.5 |
| 移動語意 | Move Semantics | 偷走暫時物件的資源，不複製 | 4.1 |
| 右值參考 | Rvalue Reference `T&&` | 只綁定暫時物件 | 4.2 |
| 移動建構子 / 移動指定 | Move Constructor / Assignment | 偷資源的建構 / 指定 | 4.3 |
| 被移動後的物件 | Moved-from Object | 有效但未指定的狀態 | 4.3 |
| 五法則 / 零法則 | Rule of Five / Zero | 五個都要考慮 / 最好一個都不用寫 | 4.5 |
| 刪除的函式 | Deleted Function `= delete` | 禁止使用的函式（例如禁止複製） | 4.5 |
| 所有權 | Ownership | 誰負責釋放 | 5.1 |
| 獨占指標 | unique_ptr | 唯一擁有者，不能複製 | 5.2 |
| 共享指標 | shared_ptr | 多個擁有者，參考計數 | 5.3 |
| 參考計數 | Reference Count | 記錄有幾個擁有者 | 5.3 |
| 控制區塊 | Control Block | shared_ptr 存放計數的地方 | 5.3 |
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

### 題 4：哪幾行會編譯錯誤？哪幾行能編譯但會造成嚴重的執行期錯誤？

```cpp
auto p = make_unique<int>(5);
auto q = p;                       // ①
auto r = std::move(p);            // ②
unique_ptr<int> s(r.get());       // ③
cout << *p;                       // ④
```

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

### 題 9：預測輸出（使用本課的 Tracer）

```cpp
vector<Tracer> v;
v.reserve(5);
Tracer x("x");
v.push_back(x);
v.push_back(std::move(x));
v.emplace_back("y");
```

### 題 10：這個類別的移動建構子沒有標 `noexcept`，會有什麼影響？

```cpp
struct Data {
    vector<int> big;
    Data(Data&& o) : big(std::move(o.big)) {}
    Data(const Data& o) = default;
    Data() = default;
};
```

---

# 習題解答

**題 1**：`+a +b +c -c -b +d -d -a`。區塊結束時，`b`、`c` 以 **相反順序** 銷毀；`main` 結束時 `d`、`a` 也以相反順序銷毀。

**題 2**：違反 **三法則**：有解構子，但沒有複製建構子 / 複製指定。`f(a)` **傳值** 會用預設的淺複製建立參數 `arr`，`arr.data` 和 `a.data` 指向同一塊記憶體。`f` 結束時 `arr` 解構，`delete[]` 一次；`main` 結束時 `a` 解構，又 `delete[]` 同一塊 → **double free**。修法：寫深複製的複製建構子和複製指定（或 `= delete` 禁止複製，或直接改用 `vector<int>`）。

**題 3**：① 複製；② 移動；③ 移動（`a + b` 是暫時物件）—— 實際上通常是複製省略，連移動都沒有；④ **複製**（`const` 物件不能被偷）；⑤ 複製；⑥ 移動。

**題 4**：① **編譯錯誤**（`unique_ptr` 不能複製）。
③ 能編譯，但讓 **兩個** `unique_ptr`（`r` 和 `s`）擁有同一個物件 → 兩個都會 `delete` 它 → **double free**。
④ 能編譯，但 `p` 已經被移動走了，是 `nullptr` → **解參考空指標**。

**題 5**：`3 2 1`。`a`、`b`、`c` 共三個；`c` 銷毀後剩 2 個；`weak_ptr` **不增加計數**，仍然是 2；`b.reset()` 後剩 1 個。

**題 6**：父節點用 `shared_ptr` 擁有子節點，子節點又用 `shared_ptr` 指回父節點 → **循環參考**，計數永遠不會歸零。修法：`parent` 改成 `weak_ptr<Node>`（子節點不擁有父節點）。更簡單的設計：`children` 用 `unique_ptr`，`parent` 用裸指標 `Node*`（只是借用，5.5 的樹範例）。

**題 7**：`other` 和新物件都指向同一塊記憶體，兩個都以為自己是擁有者。`other` 解構時會 `delete` 那塊記憶體，新物件之後再用就是 use-after-free，解構時又 double free。

**題 8**：**不需要**（零法則）。`string` 和 `vector` 都已經正確實作了複製、移動、解構，編譯器產生的預設版本會一個成員一個成員地呼叫它們，結果就是對的。

**題 9**：

```
建立 x
複製 x'
移動 x*
建立 y
```

（`emplace_back("y")` 直接在 vector 裡建構，不需要移動。程式結束時還會依序銷毀 `x`（已被移動的原物件）和 vector 裡的三個元素。）

**題 10**：`vector<Data>` 擴容時，因為移動建構子 **可能丟例外**，為了維持強例外保證，`vector` 會改用 **複製建構子** 搬移舊元素 —— 每次擴容都要複製每個 `Data` 裡的整個 `big` vector，效能大幅下降。加上 `noexcept` 就能用移動（只搬指標）。
