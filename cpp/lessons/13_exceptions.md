# 13. 例外處理 (Exceptions)

> 程式練習：`C13 安全的計算機`（`C01`、`C07` 也用到了例外）
>
> 先備知識：第 06 課「RAII」、第 08 課「繼承」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 錯誤處理的選擇 | 回傳錯誤碼、`optional`、assert、例外 —— 同一個問題用四種方式寫 |
| 第二部分 | throw / try / catch | 語法與執行流程、能拋出什麼、為什麼要用參考捕捉、捕捉順序、`catch (...)`、重新拋出、沒被捕捉的例外 |
| 第三部分 | 堆疊展開 | 例外發生時，中間的物件怎麼被清理、建構子拋出例外時會怎樣 |
| 第四部分 | 例外安全保證 | 不丟、強、基本三種保證，各用一個例子看出差別 |
| 第五部分 | noexcept | 什麼時候該標、`noexcept` 運算子、違反時會怎樣 |
| 第六部分 | 設計例外 | 標準例外各在什麼時候被拋出、自訂例外階層、什麼時候不該用例外 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：錯誤處理的選擇

## 1.1 四種方式比較

| 方式 | 例子 | 優點 | 缺點 |
|---|---|---|---|
| **回傳錯誤碼** | `bool withdraw(amt)`、`find` 回傳 `end()` | 簡單、快、流程清楚 | 呼叫者可能 **忘記檢查**；回傳值被錯誤碼佔用 |
| **`optional` / `expected`** | `optional<int> parse(s)` | 型別上就看得出「可能失敗」 | 每一層都要手動往上傳 |
| **assert** | `assert(i < n)` | 開發時抓 bug | 發布版本會被移除；只適合 **程式的 bug** |
| **例外** | `throw out_of_range(...)` | **不能被忽略**；錯誤可以跨越好幾層函式傳遞；建構子也能回報失敗 | 有效能成本（拋出時）；控制流程比較不明顯 |

**比喻**：
- 錯誤碼像是 **回條**：對方回覆了「失敗」，但你可能根本沒看回條。
- 例外像是 **火災警報**：一響起來，所有人都會被強制處理，不可能假裝沒聽到。

## 1.2 同一個問題，四種寫法

問題：把字串轉成「正整數」，格式錯誤或不是正數都算失敗。

### 寫法 1：回傳錯誤碼

```cpp
// 回傳 true 表示成功，結果放在 out 裡
bool parse_code(const string& s, int& out) {
    if (s.empty() || !all_of(s.begin(), s.end(), [](unsigned char c) { return isdigit(c); })) return false;
    out = stoi(s);
    return out > 0;
}
int v;
if (parse_code("42", v)) cout << "ok " << v << '\n';     // 輸出：ok 42
if (!parse_code("abc", v)) cout << "失敗\n";             // 輸出：失敗
parse_code("x", v);                                       // ⚠️ 忘了檢查回傳值：v 是什麼？編譯器不會提醒你
```

**問題**：「忘了檢查」完全不會有任何提示（可以用 `[[nodiscard]]` 讓編譯器警告，第 15 課）；而且回傳值被拿去表示成功 / 失敗，真正的結果只能用參數傳出來。

### 寫法 2：optional

```cpp
optional<int> parse_opt(const string& s) {
    if (s.empty() || !all_of(s.begin(), s.end(), [](unsigned char c) { return isdigit(c); })) return nullopt;
    int x = stoi(s);
    if (x <= 0) return nullopt;
    return x;
}
auto r = parse_opt("42");
if (r) cout << "ok " << *r << '\n';                      // 輸出：ok 42
cout << parse_opt("0").value_or(-1) << '\n';             // 輸出：-1
```

**優點**：型別 `optional<int>` 本身就說明「可能沒有值」，使用者很難忘記檢查。**缺點**：不知道 **為什麼** 失敗（格式錯誤？還是 0？）。

### 寫法 3：assert（只適合「呼叫者保證不會發生」的情況）

```cpp
int parse_assert(const string& s) {
    assert(!s.empty() && "caller must not pass empty string");   // 這是呼叫者的 bug
    return stoi(s);
}
cout << parse_assert("7") << '\n';                        // 輸出：7
```

使用者輸入的資料 **不能** 用 assert 檢查：發布版本會把 assert 移除，錯誤的輸入就直接通過了。

### 寫法 4：例外

```cpp
int parse_throw(const string& s) {
    if (s.empty()) throw invalid_argument("empty string");
    for (unsigned char c : s)
        if (!isdigit(c)) throw invalid_argument("not a number: " + s);
    int x = stoi(s);
    if (x <= 0) throw out_of_range("not positive: " + s);
    return x;
}
for (string s : {"42", "4x2", "0"}) {
    try {
        int x = parse_throw(s);              // 先算出結果再輸出（寫成 cout << "ok " << parse_throw(s) 的話，
        cout << "ok " << x << '\n';          //   "ok " 會在拋出例外之前就先印出來）
    } catch (const invalid_argument& e) {
        cout << "格式錯誤：" << e.what() << '\n';
    } catch (const out_of_range& e) {
        cout << "範圍錯誤：" << e.what() << '\n';
    }
}
// 輸出：
// ok 42
// 格式錯誤：not a number: 4x2
// 範圍錯誤：not positive: 0
```

**優點**：可以區分不同的錯誤種類、帶詳細訊息；不處理的話程式會終止，不會帶著錯誤的值繼續跑。

## 1.3 什麼時候用例外？

- 錯誤 **不常發生**，而且 **呼叫者沒辦法在原地處理**，需要往上好幾層才知道怎麼辦（例如：深層的解析函式發現格式錯誤，要一路回到 `main` 告訴使用者）。
- **建構子失敗**：建構子沒有回傳值，例外是唯一能回報「物件建立失敗」的方法。
- **運算子失敗**：`a + b`、`v[i]` 沒有地方放錯誤碼。

**例外能跨越好幾層**：

```cpp
int level3(int x) { if (x < 0) throw runtime_error("negative at level 3"); return x * 2; }
int level2(int x) { return level3(x) + 1; }     // 不用寫任何錯誤處理的程式碼
int level1(int x) { return level2(x) * 10; }    // 這裡也不用

try {
    cout << level1(5) << '\n';                  // 輸出：110
    cout << level1(-1) << '\n';                 // level3 拋出，直接跳到 catch
} catch (const runtime_error& e) {
    cout << "main 收到：" << e.what() << '\n';   // 輸出：main 收到：negative at level 3
}
```

用錯誤碼的話，`level2`、`level1` 都要寫「檢查 level3 有沒有失敗、失敗就往上回傳」的程式碼。

---

# 第二部分：throw / try / catch

## 2.1 基本語法與執行流程

```cpp
double safe_div(double a, double b) {
    if (b == 0) throw invalid_argument("division by zero");   // 拋出例外
    return a / b;
}

try {
    cout << "A ";
    cout << safe_div(1, 0);              // 這裡拋出例外 → 下面的程式不會執行
    cout << "B ";
} catch (const invalid_argument& e) {    // 捕捉
    cout << "error: " << e.what() << ' ';   // what() 回傳錯誤訊息
}
cout << "C\n";                           // catch 處理完之後從這裡繼續
// 輸出：A error: division by zero C
```

- **`throw 運算式`**：建立一個例外物件，**立刻離開** 目前的函式，往外找能處理它的 `catch`。
- **`try { ... }`**：包住「可能會拋出例外」的程式碼。
- **`catch (型別 名稱) { ... }`**：處理特定型別的例外。處理完後，從 **整個 try-catch 之後** 繼續執行（不會回到 `throw` 的地方）。

**沒有例外時**，`catch` 區塊完全不會執行：

```cpp
try {
    cout << safe_div(6, 3) << ' ';
} catch (const invalid_argument& e) {
    cout << "不會執行 ";
}
cout << "done\n";                        // 輸出：2 done
```

**比喻**：工廠生產線上發現瑕疵品（`throw`），立刻拉下警報，產品被送到 **最近的、負責這類問題的品管站**（`catch`），中間的工作站全部跳過。

## 2.2 可以拋出什麼？

**任何型別** 都可以拋出：`int`、`string`、自訂類別……

```cpp
try { throw 42; }
catch (int code) { cout << "int " << code << '\n'; }                 // 輸出：int 42

try { throw string("oops"); }
catch (const string& s) { cout << "string " << s << '\n'; }          // 輸出：string oops

try { throw "C string"; }                                            // 型別是 const char*
catch (const char* s) { cout << "const char* " << s << '\n'; }       // 輸出：const char* C string
```

**但是應該拋出繼承 `std::exception` 的物件**，因為：
1. 呼叫者可以用 `catch (const exception& e)` 統一處理所有錯誤。
2. 有 `what()` 可以取得錯誤訊息。
3. 型別本身就說明了錯誤的種類（`out_of_range`、`invalid_argument`……）。

**型別要完全符合**（只允許「子類別 → 父類別」和少數指標轉換），不會做一般的隱式轉換：

```cpp
try {
    try { throw 42; }
    catch (long x) { cout << "long\n"; }       // ❌ int 不會被轉成 long 來符合
} catch (int x) { cout << "int\n"; }           // 輸出：int
```

## 2.3 永遠用 const 參考捕捉

```cpp
catch (const exception& e)    // ✅
catch (exception e)           // ❌ 傳值：多一次複製，而且會發生「物件切割」
```

傳值捕捉時，如果拋出的是子類別，會被 **切割** 成父類別，子類別的資訊（包括覆寫的 `what()`）就不見了（第 08 課）：

```cpp
struct MyError : exception {
    const char* what() const noexcept override { return "MyError 的詳細訊息"; }
};
try { throw MyError(); }
catch (exception e) { cout << e.what() << '\n'; }            // 輸出：std::exception（被切割了！）

try { throw MyError(); }
catch (const exception& e) { cout << e.what() << '\n'; }     // 輸出：MyError 的詳細訊息
```

（`-Wall` 會警告：`catching polymorphic type 'class std::exception' by value`。）

## 2.4 捕捉順序：由特殊到一般

**`catch` 由上往下比對，第一個符合的就處理**（不是挑「最符合」的）。所以 **子類別要寫在父類別前面**：

```cpp
void test(int which) {
    try {
        if (which == 1) throw out_of_range("index");
        if (which == 2) throw invalid_argument("arg");
        if (which == 3) throw runtime_error("runtime");
        if (which == 4) throw 3.14;
    }
    catch (const out_of_range& e)  { cout << "out_of_range\n"; }    // 子類別
    catch (const logic_error& e)   { cout << "logic_error\n"; }     // 父類別
    catch (const exception& e)     { cout << "exception\n"; }       // 最一般
    catch (...)                    { cout << "其他\n"; }            // 捕捉「任何東西」
}
test(1); test(2); test(3); test(4);
// 輸出：
// out_of_range
// logic_error          ← invalid_argument 是 logic_error 的子類別
// exception            ← runtime_error 不是 logic_error，往下找到 exception
// 其他                 ← double 不是 exception
```

**常見錯誤：父類別寫在前面**

```cpp
try { throw out_of_range("x"); }
catch (const exception& e) { cout << "general\n"; }          // 先符合 → 輸出：general
catch (const out_of_range& e) { cout << "index\n"; }         // 永遠不會執行
// -Wall 警告：exception of type 'std::out_of_range' will be caught by earlier handler（note: for type 'std::exception'）
```

## 2.5 catch (...)

**是什麼**：捕捉 **任何型別** 的例外。但因為不知道型別，拿不到例外的內容。

**用途**：
- 程式的最外層，確保任何錯誤都被處理（印出訊息、清理），而不是直接終止。
- 做完清理後 `throw;` 重新拋出（下一節）。

```cpp
int main() {
    try {
        // ... 整個程式 ...
        throw 42;
    } catch (const exception& e) {
        cerr << "錯誤：" << e.what() << '\n';
        return 1;
    } catch (...) {
        cerr << "未知的錯誤\n";            // 輸出（到 cerr）：未知的錯誤
        return 1;
    }
}
```

## 2.6 重新拋出 (Rethrow)

**是什麼**：在 `catch` 裡處理了一部分（例如記錄錯誤），但還要讓外層繼續處理。寫一個單獨的 `throw;`。

```cpp
void process() {
    try {
        throw out_of_range("index 10");
    } catch (const exception& e) {
        cout << "log: " << e.what() << '\n';
        throw;                         // ✅ 重新拋出「原本那個」例外物件，型別完整保留
    }
}
try { process(); }
catch (const out_of_range& e) { cout << "外層收到 out_of_range\n"; }
catch (const exception& e) { cout << "外層收到 exception\n"; }
// 輸出：
// log: index 10
// 外層收到 out_of_range
```

**`throw e;` 的問題**：拋出的是 `e` 的 **複製品**，型別是 `e` 的 **宣告型別** `exception`（被切割了）：

```cpp
void process_bad() {
    try {
        throw out_of_range("index 10");
    } catch (const exception& e) {
        throw e;                       // ❌ 拋出 exception 型別的複製品
    }
}
try { process_bad(); }
catch (const out_of_range& e) { cout << "外層收到 out_of_range\n"; }
catch (const exception& e) { cout << "外層收到 exception\n"; }   // 輸出：外層收到 exception
```

### 轉換成另一種例外

有時候要把底層的錯誤「翻譯」成這一層的錯誤：

```cpp
int read_config_port(const string& text) {
    try {
        return stoi(text);
    } catch (const invalid_argument&) {
        throw runtime_error("設定檔的 port 不是數字：" + text);   // 拋出新的、更有意義的例外
    }
}
try { read_config_port("http"); }
catch (const runtime_error& e) { cout << e.what() << '\n'; }   // 輸出：設定檔的 port 不是數字：http
```

## 2.7 沒有被捕捉的例外

例外一路往外傳，到了 `main` 都沒有人捕捉 → 呼叫 `std::terminate()` → 程式直接 **終止**。

```cpp
int main() {
    vector<int> v(3);
    v.at(10);           // 拋出 out_of_range，沒有人捕捉
}
// 執行結果（stderr）：
// terminate called after throwing an instance of 'std::out_of_range'
//   what():  vector::_M_range_check: __n (which is 10) >= this->size() (which is 3)
// Aborted
```

評測結果是 **RE**（執行期錯誤）。看到 `terminate called after throwing` 就知道是哪一種例外沒被處理，`what()` 告訴你原因。

---

# 第三部分：堆疊展開 (Stack Unwinding)

## 3.1 例外發生時，中間的物件怎麼辦？

**是什麼**：例外從 `throw` 往外傳到 `catch` 的過程中，**經過的每一層函式裡的區域物件，都會依照建立的相反順序被解構**。這叫堆疊展開。

```cpp
struct Guard {
    string name;
    Guard(string n) : name(n) { cout << "+" << name << ' '; }
    ~Guard() { cout << "-" << name << ' '; }
};
void inner() { Guard c("c"); throw runtime_error("boom"); }
void outer() { Guard b("b"); inner(); Guard never("x"); }

Guard a("a");
try { outer(); }
catch (const exception& e) { cout << "caught "; }
cout << '\n';
// 輸出：+a +b +c -c -b caught
// （a 在 main 結束時才解構）
```

**一步一步看**：
1. `a`、`b`、`c` 依序建立。
2. `inner` 拋出例外 → 離開 `inner`：解構 `c`。
3. 離開 `outer`：解構 `b`（`never` 還沒建立，不用解構）。
4. 到達 `catch`，印出 `caught`。

**比喻**：從一棟大樓的頂樓緊急疏散到一樓的集合點（`catch`）。每經過一層樓，那一層的人都會 **關好門窗、關掉電源**（解構子）才離開。

## 3.2 RAII 是例外安全的基礎

因為堆疊展開會呼叫解構子，**用 RAII 管理的資源在例外發生時也會被正確釋放**：

```cpp
int live = 0;                                     // 目前還沒釋放的配置數量
struct Tracked { Tracked() { live++; } ~Tracked() { live--; } };
void risky() { throw runtime_error("fail"); }

void bad() {
    Tracked* p = new Tracked;
    risky();                // 丟出例外 → 下一行永遠不會執行
    delete p;
}
void good() {
    auto p = make_unique<Tracked>();
    risky();                // 丟出例外 → p 的解構子在堆疊展開時被呼叫 → delete
}

try { bad(); } catch (...) {}
cout << "bad 之後 live = " << live << '\n';       // 輸出：bad 之後 live = 1（洩漏了一個）
try { good(); } catch (...) {}
cout << "good 之後 live = " << live << '\n';      // 輸出：good 之後 live = 1（沒有增加）
```

**這就是為什麼現代 C++ 不寫裸的 `new` / `delete`**：手動管理的資源，在每一個可能丟出例外的地方都會洩漏。

## 3.3 建構子拋出例外時會怎樣？

**規則**：
- 建構子拋出例外 → 物件 **沒有建立成功** → 它的 **解構子不會被呼叫**。
- 但 **已經建立好的成員和父類別** 會被正確解構。

```cpp
struct Part { string n; Part(string s) : n(s) { cout << "+" << n << ' '; } ~Part() { cout << "-" << n << ' '; } };
struct Machine {
    Part a{"a"};
    Part b{"b"};
    Machine() {
        cout << "建構中 ";
        throw runtime_error("零件不良");
    }
    ~Machine() { cout << "~Machine "; }        // 不會被呼叫
};
try { Machine m; }
catch (const exception& e) { cout << "| " << e.what() << '\n'; }
// 輸出：+a +b 建構中 -b -a | 零件不良
```

`~Machine` 沒有被呼叫，但成員 `a`、`b` 都被解構了。

**這對手動管理資源的影響**：

```cpp
struct TwoBuffers {
    int* p1;
    int* p2;
    TwoBuffers() : p1(new int[100]), p2(new int[1000000000000]) {}   // p2 配置失敗 → bad_alloc
    ~TwoBuffers() { delete[] p1; delete[] p2; }                      // 不會被呼叫 → p1 洩漏！
};
```

用 `vector<int>` 或 `unique_ptr<int[]>` 當成員就沒有這個問題：已經建立好的成員一定會被解構。**又一次證明 RAII 的重要**。

## 3.4 🔍 解構子不能拋出例外

如果在堆疊展開的過程中（已經有一個例外在傳遞），某個解構子 **又** 拋出例外，C++ 無法同時處理兩個例外，會直接呼叫 `std::terminate()`。

所以 C++11 起，解構子 **預設是 `noexcept`** 的（第五部分）。就算沒有其他例外在傳遞，從解構子拋出的例外也會直接 `terminate`：

```cpp
struct Bad {
    ~Bad() { throw runtime_error("from destructor"); }   // -Wall 警告：'throw' will always call 'terminate'
};
// { Bad b; }   // 執行時：terminate called after throwing an instance of 'std::runtime_error'
```

**規則**：解構子裡可能失敗的操作（例如關檔失敗、網路斷線），要在解構子裡自己處理掉（記錄錯誤、忽略），**不能讓例外逃出解構子**。

```cpp
struct SafeClose {
    ~SafeClose() {
        try {
            might_fail();
        } catch (...) {
            // 記錄錯誤，但不往外丟
        }
    }
    static void might_fail() { throw runtime_error("close failed"); }
};
{ SafeClose s; }
cout << "沒事\n";                              // 輸出：沒事
```

---

# 第四部分：例外安全保證 (Exception Safety Guarantees)

當一個函式拋出例外時，物件會處於什麼狀態？有四個等級：

| 等級 | 英文 | 承諾 | 比喻（網路轉帳） |
|---|---|---|---|
| **不丟保證** | No-throw / Nothrow | **絕對不會** 拋出例外 | 查詢餘額：一定成功 |
| **強保證** | Strong | 失敗時，狀態 **完全回到呼叫前**（像沒發生過一樣） | 轉帳失敗，兩邊的錢都沒變 |
| **基本保證** | Basic | 失敗時，**不洩漏資源、不變量仍成立**，但狀態可能改變了 | 轉帳失敗，錢沒有不見，但可能產生了一筆「待處理」紀錄 |
| **沒有保證** | No guarantee | 失敗時什麼都可能發生 | 錢可能憑空消失 |

**每個函式至少要提供基本保證**。能提供強保證就更好。

## 4.1 用同一個例子看三種保證

情境：一個「堆疊計算機」，`apply_div()` 要把頂端兩個數相除，結果放回堆疊。除以 0 時拋出例外。

```cpp
void print_stack(const vector<long long>& st) {
    cout << '[';
    for (size_t i = 0; i < st.size(); i++) cout << (i ? " " : "") << st[i];
    cout << "]\n";
}
long long checked_div(long long a, long long b) {
    if (b == 0) throw runtime_error("division by zero");
    return a / b;
}
```

### 沒有保證 / 只有基本保證：先修改，再做可能失敗的事

```cpp
void apply_div_weak(vector<long long>& st) {
    long long b = st.back(); st.pop_back();       // ① 先拿出兩個（修改了狀態）
    long long a = st.back(); st.pop_back();
    st.push_back(checked_div(a, b));              // ② 計算可能失敗
}
vector<long long> s1 = {7, 10, 0};
try { apply_div_weak(s1); } catch (const exception& e) { cout << e.what() << ": "; }
print_stack(s1);                                  // 輸出：division by zero: [7]   😱 10 和 0 不見了
```

物件還是合法的（不洩漏、`vector` 本身沒壞）→ **基本保證**。但使用者的資料遺失了。

### 強保證：先做完所有可能失敗的事，最後才修改

```cpp
void apply_div_strong(vector<long long>& st) {
    if (st.size() < 2) throw runtime_error("stack underflow");   // ① 檢查（不修改）
    long long a = st[st.size() - 2], b = st.back();              // ② 只讀取
    long long r = checked_div(a, b);                             // ③ 可能失敗的計算（還沒修改任何東西）
    st.pop_back();                                               // ④ 確定成功了，才修改（這兩步不會失敗）
    st.back() = r;
}
vector<long long> s2 = {7, 10, 0};
try { apply_div_strong(s2); } catch (const exception& e) { cout << e.what() << ": "; }
print_stack(s2);                                  // 輸出：division by zero: [7 10 0]（完全沒變）

vector<long long> s3 = {7, 10, 3};
apply_div_strong(s3);
print_stack(s3);                                  // 輸出：[7 3]（成功時正常運作）
```

這就是 `C13` 要求的寫法。

### 不丟保證：不可能失敗的操作

```cpp
size_t depth(const vector<long long>& st) noexcept { return st.size(); }   // 只讀取一個數字，不會失敗
```

## 4.2 怎麼做到強保證：兩個技巧

**原則**：把「**可能失敗的步驟**」全部做完（在暫存的地方），確定沒問題了，再用「**不會失敗的操作**」（例如 `swap`、指標賦值、`pop_back`）一口氣修改真正的狀態。

### 技巧 1：先檢查、先計算，最後修改（4.1 的寫法）

### 技巧 2：在複製品上修改，成功後 swap

當修改很複雜、步驟很多時，直接在一份 **複製品** 上做，全部成功了再和原本的交換：

```cpp
void normalize_all(vector<int>& data) {
    vector<int> tmp = data;                      // ① 複製（可能失敗，但原資料沒被動到）
    for (int& x : tmp) {
        if (x < 0) throw invalid_argument("negative value");   // ② 在複製品上做，中途失敗也沒關係
        x = x * 100 / 255;
    }
    data.swap(tmp);                              // ③ 全部成功：交換（不會失敗）
}
vector<int> d1 = {255, 51, -1, 102};
try { normalize_all(d1); } catch (const exception& e) { cout << e.what() << ": "; }
cout << d1[0] << ' ' << d1[1] << '\n';           // 輸出：negative value: 255 51（原資料沒有被改到一半）
vector<int> d2 = {255, 51};
normalize_all(d2);
cout << d2[0] << ' ' << d2[1] << '\n';           // 輸出：100 20
```

如果直接在 `data` 上改，遇到 `-1` 時前兩個已經被改掉了，資料變成「一半新一半舊」。

**copy-and-swap**（第 06 課 3.5）就是這個技巧用在指定運算子上。

**代價**：多一次複製。所以標準函式庫不是每個操作都提供強保證，會在文件中註明。

## 4.3 🔍 vector::push_back 的強保證與 noexcept

`push_back` 提供 **強保證**：擴容時如果搬元素搬到一半失敗，`vector` 要回到原本的樣子。

- 如果元素的 **移動建構子是 `noexcept`**：移動不會失敗，放心用移動（快）。
- 否則：用 **複製**（舊的元素都還在，失敗時直接丟掉新空間就好）。

這就是第 06 課 4.6 說「移動建構子一定要加 `noexcept`」的原因（那裡有實驗：`MMMMM` vs `MCCCC`）。

---

# 第五部分：noexcept

## 5.1 noexcept 的意思

**是什麼**：標記「**這個函式保證不會拋出例外**」。

```cpp
class Buffer {
    int* data_ = nullptr;
    size_t n_ = 0;
public:
    Buffer(Buffer&& other) noexcept : data_(other.data_), n_(other.n_) { other.data_ = nullptr; other.n_ = 0; }
    void swap(Buffer& other) noexcept { std::swap(data_, other.data_); std::swap(n_, other.n_); }
    size_t size() const noexcept { return n_; }
    ~Buffer() { delete[] data_; }               // 解構子：不寫也是 noexcept
};
```

**好處**：
1. 讓使用者（和標準函式庫）知道可以放心依賴它（例如 `vector` 選擇移動）。
2. 編譯器可以做更多最佳化（不需要為這個函式準備例外處理的資料）。

## 5.2 noexcept 運算子：在編譯時查詢

`noexcept(運算式)` 是一個 **編譯期** 的 `bool`：這個運算式會不會拋出例外？（運算式不會真的被執行。）

```cpp
void may_throw() {}
void never_throw() noexcept {}
struct Plain { ~Plain() {} };

cout << noexcept(may_throw()) << ' '                    // 沒標 noexcept → 0
     << noexcept(never_throw()) << ' '                  // → 1
     << noexcept(1 + 2) << ' '                          // 內建運算不會拋出 → 1
     << noexcept(Plain().~Plain()) << ' '               // 解構子預設 noexcept → 1
     << noexcept(vector<int>().push_back(1)) << '\n';   // 可能配置記憶體失敗 → 0
// 輸出：0 1 1 1 0

cout << is_nothrow_move_constructible_v<Buffer> << ' '
     << is_nothrow_move_constructible_v<string> << '\n';   // 輸出：1 1
```

`vector` 擴容時就是用 `is_nothrow_move_constructible` 決定要移動還是複製。

## 5.3 違反 noexcept 會怎樣？

如果標了 `noexcept` 的函式 **真的拋出了例外**，不會往外傳遞，而是 **直接呼叫 `std::terminate()`**，程式終止 —— 外面的 `catch` 完全沒有機會處理。

```cpp
void liar() noexcept { throw runtime_error("x"); }   // -Wall 警告：'throw' will always call 'terminate'
int main() {
    try { liar(); }
    catch (...) { cout << "caught"; }                 // 不會執行
}
// 執行結果：terminate called after throwing an instance of 'std::runtime_error'
```

**例外是從 noexcept 函式「呼叫的其他函式」裡拋出的也一樣**：

```cpp
void helper() { throw runtime_error("deep"); }
void wrapper() noexcept { helper(); }                 // 編譯器不會警告，但執行時一樣 terminate
```

**比喻**：保證書上寫著「絕不故障」，如果真的故障了，不是送修，而是整台報廢。

## 5.4 該標 noexcept 的地方

- **移動建構子、移動指定運算子**（最重要）
- **`swap`**
- **解構子**（預設就是，不用寫）
- 簡單的、明顯不會失敗的查詢函式（`size()`、`empty()`）

**不確定的就不要標** —— 標錯的代價（程式直接終止）比不標更嚴重。

**常見錯誤**：在 `noexcept` 函式裡呼叫了會配置記憶體的操作（`push_back`、建立 `string`）。記憶體不足時拋出 `bad_alloc` → 程式終止。

---

# 第六部分：設計例外

## 6.1 標準例外階層

```
std::exception
├── std::logic_error           「程式邏輯錯誤」：理論上檢查參數就能避免
│   ├── std::invalid_argument      參數不合法（stoi("abc")）
│   ├── std::domain_error          數學定義域錯誤
│   ├── std::length_error          長度超過上限
│   └── std::out_of_range          索引越界（vector::at、string::substr）
├── std::runtime_error         「執行期錯誤」：無法事先預測
│   ├── std::range_error
│   ├── std::overflow_error        算術溢位
│   └── std::underflow_error
├── std::bad_alloc             new 配置記憶體失敗
├── std::bad_cast              dynamic_cast 參考版本失敗
├── std::bad_optional_access   對空的 optional 呼叫 value()
└── ...
```

**`logic_error` vs `runtime_error`**：
- `logic_error`：**呼叫者寫錯了**（傳了不合法的參數）。理論上呼叫前檢查就能避免。
- `runtime_error`：**外部環境造成的**，無法事先預測（檔案損毀、網路中斷、計算溢位）。

## 6.2 標準函式庫什麼時候拋出哪一種？

```cpp
auto report = [](const char* what_happened, auto&& action) {
    try { action(); cout << what_happened << "：沒有例外\n"; }
    catch (const out_of_range&)          { cout << what_happened << "：out_of_range\n"; }
    catch (const invalid_argument&)      { cout << what_happened << "：invalid_argument\n"; }
    catch (const length_error&)          { cout << what_happened << "：length_error\n"; }
    catch (const bad_alloc&)             { cout << what_happened << "：bad_alloc\n"; }
    catch (const bad_cast&)              { cout << what_happened << "：bad_cast\n"; }
    catch (const bad_optional_access&)   { cout << what_happened << "：bad_optional_access\n"; }
};

struct Base { virtual ~Base() = default; };
struct Derived : Base {};

vector<int> v(3);
string s = "abc";
optional<int> empty_opt;
Base b;

report("v.at(5)",            [&] { v.at(5); });
report("v[5]",               [&] { /* v[5] 是未定義行為，不檢查也不拋出 */ });
report("s.substr(10)",       [&] { s.substr(10); });
report("stoi(\"abc\")",      [&] { stoi("abc"); });
report("stoi(\"9999999999\")", [&] { stoi("9999999999"); });
report("v.reserve(極大)",     [&] { v.reserve(v.max_size() + 1); });
report("new 8TB",            [&] { delete[] new long long[1000000000000LL]; });
report("dynamic_cast<&>",    [&] { (void)dynamic_cast<Derived&>(b); });
report("empty_opt.value()",  [&] { (void)empty_opt.value(); });
// 輸出：
// v.at(5)：out_of_range
// v[5]：沒有例外
// s.substr(10)：out_of_range
// stoi("abc")：invalid_argument
// stoi("9999999999")：out_of_range
// v.reserve(極大)：length_error
// new 8TB：bad_alloc
// dynamic_cast<&>：bad_cast
// empty_opt.value()：bad_optional_access
```

**注意**：同一種錯誤可能有「檢查版」和「不檢查版」：`v.at(i)` vs `v[i]`、`opt.value()` vs `*opt`、`dynamic_cast` vs `static_cast`。不檢查的版本比較快，但出錯時是未定義行為。

## 6.3 自訂例外

**繼承標準例外**，讓使用者可以用 `catch (const exception&)` 統一處理：

```cpp
class CalcError : public runtime_error {           // C13 的設計：計算機所有錯誤的父類別
public:
    using runtime_error::runtime_error;            // 繼承建構子（第 08 課 2.4）
};
class DivisionByZero : public CalcError {
public:
    DivisionByZero() : CalcError("division by zero") {}
};
class Overflow : public CalcError {
public:
    Overflow() : CalcError("overflow") {}
};
```

建立 **例外的階層**，讓呼叫者可以選擇要捕捉「特定的錯誤」還是「這一類的所有錯誤」：

```cpp
void calc(int kind) {
    if (kind == 1) throw DivisionByZero();
    if (kind == 2) throw Overflow();
    if (kind == 3) throw CalcError("unknown op");
}
for (int k = 1; k <= 3; k++) {
    try { calc(k); }
    catch (const DivisionByZero& e) { cout << "特別處理除以零\n"; }       // 只想特別處理這一種
    catch (const CalcError& e) { cout << "計算錯誤：" << e.what() << '\n'; }   // 其他計算錯誤
}
// 輸出：
// 特別處理除以零
// 計算錯誤：overflow
// 計算錯誤：unknown op
```

### 帶額外資訊的例外

例外是普通的類別，可以有自己的成員：

```cpp
class ParseError : public runtime_error {
    int line_;
public:
    ParseError(const string& msg, int line)
        : runtime_error("line " + to_string(line) + ": " + msg), line_(line) {}
    int line() const noexcept { return line_; }
};

try {
    throw ParseError("unexpected ')'", 7);
} catch (const ParseError& e) {
    cout << e.what() << " (行號 " << e.line() << ")\n";   // 輸出：line 7: unexpected ')' (行號 7)
}
```

**設計建議**：
- 繼承 `runtime_error` 或 `logic_error`（它們已經幫你存好訊息、實作好 `what()`）。
- 例外類別的成員函式（尤其是 `what()`）標 `noexcept`。
- 例外的複製建構子不應該拋出例外 —— 所以訊息用 `runtime_error` 存，不要自己存一個 `string` 成員（`runtime_error` 內部用了不會在複製時拋出例外的方式儲存）。

## 6.4 🔍 例外的成本

主流編譯器使用「**零成本例外 (zero-cost exceptions)**」：
- **沒有拋出例外時**：幾乎沒有額外的執行成本（`try` 區塊不會讓程式變慢）。
- **拋出例外時**：非常昂貴（要查表、展開堆疊、配置例外物件），可能比一般函式呼叫慢上千倍。

所以 **例外只用在真正「例外」的情況**。

## 6.5 不要用例外的情況

| 情況 | 為什麼 | 改用 |
|---|---|---|
| 「失敗」是常見的正常結果（找不到、使用者取消、餘額不足） | 太慢、而且不是「例外」 | 回傳值、`optional`、`bool` |
| 控制流程（用例外跳出迴圈） | 難讀又慢 | `break`、`return` |
| 程式的 bug（不該發生的情況） | 應該修 bug，而不是處理它 | `assert` |
| 解構子裡 | 會導致 `terminate` | 在解構子裡自己處理掉 |
| 效能極度關鍵的迴圈 | 拋出成本太高 | 錯誤碼 |

**反例：用例外控制流程**

```cpp
// ❌ 用例外跳出巢狀迴圈
try {
    for (int i = 0; i < 10; i++)
        for (int j = 0; j < 10; j++)
            if (i * j == 42) throw make_pair(i, j);
} catch (pair<int, int> p) {
    cout << p.first << ' ' << p.second << '\n';   // 輸出：6 7
}

// ✅ 寫成函式，用 return
auto find_pair = []() -> optional<pair<int, int>> {
    for (int i = 0; i < 10; i++)
        for (int j = 0; j < 10; j++)
            if (i * j == 42) return make_pair(i, j);
    return nullopt;
};
if (auto p = find_pair()) cout << p->first << ' ' << p->second << '\n';   // 輸出：6 7
```

`C09` 用回傳錯誤訊息（帳戶操作失敗是常見情況），`C13` 用例外（為了練習例外與強保證），兩種設計都合理。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 例外 | Exception | 用來回報錯誤、不能被忽略的機制 | 1 |
| 拋出 / 捕捉 | throw / catch | 發出錯誤 / 處理錯誤 | 2.1 |
| 捕捉所有 | catch (...) | 捕捉任何型別的例外 | 2.5 |
| 重新拋出 | Rethrow (`throw;`) | 把同一個例外繼續往外丟 | 2.6 |
| 終止 | std::terminate | 沒被捕捉的例外會讓程式終止 | 2.7 |
| 堆疊展開 | Stack Unwinding | 例外往外傳時依序解構區域物件 | 3.1 |
| 例外安全 | Exception Safety | 例外發生時物件的狀態保證 | 4 |
| 不丟 / 強 / 基本保證 | No-throw / Strong / Basic Guarantee | 不會失敗 / 失敗時完全復原 / 失敗時不洩漏 | 4 |
| noexcept | noexcept | 保證不拋出例外 | 5.1 |
| noexcept 運算子 | noexcept operator | 編譯時查詢運算式會不會拋出 | 5.2 |
| 標準例外階層 | Standard Exception Hierarchy | logic_error、runtime_error 等 | 6.1 |
| 零成本例外 | Zero-cost Exceptions | 不拋出時沒有成本，拋出時很貴 | 6.4 |

---

# 習題

### 題 1：預測輸出

```cpp
try {
    try {
        throw out_of_range("oops");
    } catch (const runtime_error& e) {
        cout << "A ";
    }
    cout << "B ";
} catch (const logic_error& e) {
    cout << "C ";
} catch (const exception& e) {
    cout << "D ";
}
cout << "E";
```

### 題 2：預測輸出

```cpp
struct T { char c; T(char x) : c(x) { cout << c; } ~T() { cout << (char)toupper(c); } };
void f() { T b('b'); throw 1; T c('c'); }
int main() {
    T a('a');
    try { f(); } catch (int) { cout << '!'; }
}
```

### 題 3：下面的捕捉順序有什麼問題？

```cpp
try { ... }
catch (const exception& e) { cout << "general"; }
catch (const out_of_range& e) { cout << "index"; }
```

### 題 4：`throw;` 和 `throw e;` 有什麼差別？

```cpp
catch (const exception& e) { throw e; }
```

### 題 5：這個函式提供哪一種例外安全保證？怎麼改成強保證？

```cpp
void Account::transfer(Account& to, long long amt) {
    balance_ -= amt;
    to.deposit(amt);        // 可能拋出例外（例如超過存款上限）
}
```

### 題 6：下面這段程式會發生什麼事？

```cpp
void f() noexcept { throw runtime_error("x"); }
int main() {
    try { f(); } catch (...) { cout << "caught"; }
}
```

### 題 7：下列情況適合用例外嗎？

```
a) 在 vector 中找不到某個值
b) 設定檔的格式錯誤，程式無法繼續
c) 建構一個 Matrix 時，傳入的列數是負數
d) 迴圈中想提早結束
```

### 題 8：預測輸出

```cpp
struct M { string n; M(string s) : n(s) { cout << '+' << n; } ~M() { cout << '-' << n; } };
struct W {
    M x{"x"};
    M y;
    W() : y("y") { throw 1; }
    ~W() { cout << "~W"; }
};
int main() {
    try { W w; } catch (int) { cout << '!'; }
}
```

### 題 9：預測輸出

```cpp
void g(int k) {
    try {
        if (k == 0) throw string("zero");
        if (k == 1) throw 1;
        cout << "ok ";
    } catch (const string& s) {
        cout << "s:" << s << ' ';
        throw;
    }
}
int main() {
    for (int k : {2, 0, 1}) {
        try { g(k); }
        catch (const string&) { cout << "outer-s "; }
        catch (int) { cout << "outer-i "; }
    }
}
```

### 題 10：下面的 `push_all` 提供哪一種例外安全保證？把它改成強保證。

```cpp
void push_all(vector<int>& v, const vector<string>& items) {
    for (const string& s : items) v.push_back(stoi(s));   // stoi 可能拋出例外
}
```

---

# 習題解答

**題 1**：`C E`。`out_of_range` 是 `logic_error` 的子類別，**不是** `runtime_error`，內層的 `catch` 不符合，例外繼續往外傳（`B` 不會印出）；外層第一個符合的是 `logic_error` → `C`。

**題 2**：`abB!A`。建立 `a`、`b`；拋出例外時 `c` 還沒建立；堆疊展開解構 `b`（印 `B`）；捕捉到例外印 `!`；`main` 結束時解構 `a`（印 `A`）。

**題 3**：`out_of_range` 是 `exception` 的子類別，會被第一個 `catch` 攔下，第二個 `catch` **永遠不會執行**。要把子類別寫在前面。

**題 4**：`throw;` 重新拋出 **原本的例外物件**，型別完整保留（如果原本是 `out_of_range`，外層還是可以用 `catch (const out_of_range&)` 捕捉）。`throw e;` 拋出的是 `e` 的 **複製品**，型別是 `e` 的靜態型別 `exception`，子類別的資訊被 **切割** 掉了（2.6 節的實驗）。

**題 5**：**沒有保證（或最多只有基本保證）**：`deposit` 失敗時，錢已經從自己扣掉了，但沒有存進對方 —— 錢消失了，破壞了「總金額不變」的不變量。改成先做可能失敗的操作：

```cpp
void Account::transfer(Account& to, long long amt) {
    if (balance_ < amt) throw insufficient_funds();
    to.deposit(amt);        // 可能失敗：失敗時自己的餘額還沒動
    balance_ -= amt;        // 不會失敗
}
```

**題 6**：例外不能逃出 `noexcept` 函式，**直接呼叫 `std::terminate()`**，程式終止，`catch (...)` 捕捉不到，`caught` 不會印出。

**題 7**：
- a) **不適合**：找不到是正常結果，回傳 `end()` 或 `optional`。
- b) **適合**：不常發生、需要回報到上層（通常是 `main`）告訴使用者。
- c) **適合**：建構子失敗只能用例外回報（`invalid_argument`）。
- d) **不適合**：用 `break` 或 `return`。

**題 8**：`+x+y-y-x!`。成員 `x`、`y` 依宣告順序建立；建構子本體拋出例外 → 物件沒有建立成功，**`~W` 不會被呼叫**，但已經建立好的成員以相反順序解構（`-y-x`）；最後 `catch` 印出 `!`。

**題 9**：`ok s:zero outer-s outer-i `。
- `k = 2`：沒有例外 → `ok`。
- `k = 0`：拋出 `string`，內層捕捉印 `s:zero`，`throw;` 重新拋出，外層捕捉印 `outer-s`。
- `k = 1`：拋出 `int`，內層只捕捉 `string`，不符合 → 直接傳到外層 → `outer-i`。

**題 10**：**基本保證**：中途 `stoi` 失敗時，前面的元素已經被加進 `v` 了（`v` 是合法的 vector，但內容是「加了一半」）。強保證的寫法：先全部轉換好，再一次加進去。

```cpp
void push_all(vector<int>& v, const vector<string>& items) {
    vector<int> converted;
    converted.reserve(items.size());
    for (const string& s : items) converted.push_back(stoi(s));   // 可能失敗：v 還沒被動到
    v.insert(v.end(), converted.begin(), converted.end());        // 最後才修改 v
}
vector<int> v = {1};
try { push_all(v, {"2", "x", "4"}); } catch (...) {}
cout << v.size() << '\n';               // 輸出：1（失敗時 v 完全沒變）
push_all(v, {"2", "3"});
cout << v.size() << '\n';               // 輸出：3
```

（嚴格來說，最後的 `insert` 本身也可能因為記憶體不足而失敗，但 `vector::insert` 在元素是 `int` 時提供強保證，所以整個函式仍然是強保證。）

---

# 程式練習

- **`C13 安全的計算機`**：自訂例外階層、在計算之前檢查溢位、強例外保證（出錯時堆疊完全不變）、`LLONG_MIN % -1` 的陷阱。
