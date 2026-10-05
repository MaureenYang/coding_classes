# 13. 例外處理 (Exceptions)

> 程式練習：`C13 安全的計算機`（`C01`、`C07` 也用到了例外）
>
> 先備知識：第 06 課「RAII」、第 08 課「繼承」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 錯誤處理的選擇 | 回傳錯誤碼、assert、例外、`optional` 各適合什麼 |
| 第二部分 | throw / try / catch | 語法、為什麼要用參考捕捉、捕捉順序、重新拋出 |
| 第三部分 | 堆疊展開 | 例外發生時，中間的物件怎麼被清理 |
| 第四部分 | 例外安全保證 | 不丟、強、基本三種保證，怎麼做到 |
| 第五部分 | noexcept | 什麼時候該標、違反時會怎樣 |
| 第六部分 | 設計例外 | 標準例外階層、自訂例外、什麼時候不該用例外 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：錯誤處理的選擇

| 方式 | 例子 | 優點 | 缺點 |
|---|---|---|---|
| **回傳錯誤碼** | `bool withdraw(amt)`、`find` 回傳 `end()` | 簡單、快、流程清楚 | 呼叫者可能 **忘記檢查**；回傳值被錯誤碼佔用 |
| **`optional` / `expected`** | `optional<int> parse(s)` | 型別上就看得出「可能失敗」 | 每一層都要手動往上傳 |
| **assert** | `assert(i < n)` | 開發時抓 bug | 發布版本會被移除；只適合 **程式的 bug** |
| **例外** | `throw out_of_range(...)` | **不能被忽略**；錯誤可以跨越好幾層函式傳遞；建構子也能回報失敗 | 有效能成本（拋出時）；控制流程比較不明顯 |

**什麼時候用例外？**
- 錯誤 **不常發生**，而且 **呼叫者沒辦法在原地處理**，需要往上好幾層才知道怎麼辦（例如：深層的解析函式發現格式錯誤，要一路回到 `main` 告訴使用者）。
- **建構子失敗**：建構子沒有回傳值，例外是唯一能回報「物件建立失敗」的方法。

**比喻**：
- 錯誤碼像是 **回條**：對方回覆了「失敗」，但你可能根本沒看回條。
- 例外像是 **火災警報**：一響起來，所有人都會被強制處理，不可能假裝沒聽到。

---

# 第二部分：throw / try / catch

## 2.1 基本語法

```cpp
#include <stdexcept>

double safe_div(double a, double b) {
    if (b == 0) throw invalid_argument("division by zero");   // 拋出例外
    return a / b;
}

int main() {
    try {
        cout << safe_div(1, 0);           // 這裡拋出例外 → 下面的程式不會執行
        cout << "never printed";
    } catch (const invalid_argument& e) { // 捕捉
        cout << "error: " << e.what();    // what() 回傳錯誤訊息
    }
    cout << "continue";                   // catch 處理完之後從這裡繼續
}
```

- **`throw`**：拋出一個例外物件，**立刻離開** 目前的函式，往外找能處理它的 `catch`。
- **`try`**：包住「可能會拋出例外」的程式碼。
- **`catch`**：處理特定型別的例外。

**比喻**：工廠生產線上發現瑕疵品（`throw`），立刻拉下警報，產品被送到 **最近的、負責這類問題的品管站**（`catch`），中間的工作站全部跳過。

## 2.2 永遠用 const 參考捕捉

```cpp
catch (const exception& e)    // ✅
catch (exception e)           // ❌ 傳值：多一次複製，而且會發生「物件切割」
```

傳值捕捉時，如果拋出的是子類別（例如 `out_of_range`），會被 **切割** 成 `exception`，子類別的資訊就不見了（第 08 課）。

## 2.3 捕捉順序：由特殊到一般

**`catch` 由上往下比對，第一個符合的就處理**（不是挑「最符合」的）。所以 **子類別要寫在父類別前面**：

```cpp
try { ... }
catch (const out_of_range& e) { ... }     // 子類別
catch (const logic_error& e) { ... }      // 父類別
catch (const exception& e) { ... }        // 最一般
catch (...) { ... }                       // 捕捉「任何東西」（包括 throw 42 這種非 exception 的）
```

如果把 `catch (const exception&)` 寫在最前面，後面的都永遠不會被執行（編譯器會警告）。

## 2.4 重新拋出 (Rethrow)

在 `catch` 裡處理了一部分，但還要讓外層繼續處理：

```cpp
catch (const exception& e) {
    log(e.what());
    throw;          // ✅ 重新拋出「原本那個」例外物件，型別完整保留
    throw e;        // ❌ 拋出 e 的「複製品」，型別是 exception（被切割了）
}
```

## 2.5 沒有被捕捉的例外

例外一路往外傳，到了 `main` 都沒有人捕捉 → 呼叫 `std::terminate()` → 程式直接 **終止**（評測結果是 RE，訊息通常是 `terminate called after throwing an instance of ...`）。

---

# 第三部分：堆疊展開 (Stack Unwinding)

## 3.1 例外發生時，中間的物件怎麼辦？

**白話**：例外從 `throw` 往外傳到 `catch` 的過程中，**經過的每一層函式裡的區域物件，都會依照建立的相反順序被解構**。這叫堆疊展開。

```cpp
struct Guard {
    string name;
    Guard(string n) : name(n) { cout << "+" << name << ' '; }
    ~Guard() { cout << "-" << name << ' '; }
};
void inner() { Guard c("c"); throw runtime_error("boom"); }
void outer() { Guard b("b"); inner(); Guard never("x"); }
int main() {
    Guard a("a");
    try { outer(); }
    catch (const exception& e) { cout << "caught "; }
}
// 輸出：+a +b +c -c -b caught -a
```

**比喻**：從一棟大樓的頂樓緊急疏散到一樓的集合點（`catch`）。每經過一層樓，那一層的人都會 **關好門窗、關掉電源**（解構子）才離開。

## 3.2 RAII 是例外安全的基礎

因為堆疊展開會呼叫解構子，**用 RAII 管理的資源在例外發生時也會被正確釋放**：

```cpp
void bad() {
    int* p = new int[100];
    risky();               // 丟出例外 → delete[] 永遠不會執行 → 洩漏
    delete[] p;
}
void good() {
    vector<int> v(100);    // 或 unique_ptr
    risky();               // 丟出例外 → v 的解構子在堆疊展開時被呼叫 → 不洩漏
}
```

**這就是為什麼現代 C++ 不寫裸的 `new` / `delete`**：手動管理的資源，在每一個可能丟出例外的地方都會洩漏。

## 3.3 🔍 解構子不能拋出例外

如果在堆疊展開的過程中（已經有一個例外在傳遞），某個解構子 **又** 拋出例外，C++ 無法同時處理兩個例外，會直接呼叫 `std::terminate()`。

所以 C++11 起，解構子 **預設是 `noexcept`** 的。解構子裡可能失敗的操作（例如關檔失敗），要在解構子裡自己處理掉（記錄錯誤、忽略），**不能讓例外逃出解構子**。

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

## 4.1 怎麼做到強保證：先做會失敗的事，再修改狀態

**原則**：把「**可能失敗的步驟**」全部做完（在暫存的地方），確定沒問題了，再用「**不會失敗的操作**」（例如 `swap`、指標賦值）一口氣修改真正的狀態。

```cpp
// C13 的二元運算：強保證
void binary(const string& op) {
    if (st.size() < 2) throw StackUnderflow();     // ① 檢查（不修改任何東西）
    long long a = st[st.size() - 2], b = st.back();
    long long r = compute(a, b, op);                // ② 計算：可能拋出 Overflow / DivisionByZero
    st.pop_back();                                  // ③ 都沒問題了，才修改（這兩步不會失敗）
    st.back() = r;
}
```

如果寫成「先 `pop` 兩個，再計算」，計算失敗時兩個數字已經不見了 —— 只有基本保證（甚至更差）。

**copy-and-swap**（第 06 課）也是同樣的想法：先在複製品上做完所有可能失敗的事，最後 `swap`（不丟例外）。

## 4.2 🔍 vector::push_back 的強保證與 noexcept

`push_back` 提供 **強保證**：擴容時如果搬元素搬到一半失敗，`vector` 要回到原本的樣子。

- 如果元素的 **移動建構子是 `noexcept`**：移動不會失敗，放心用移動（快）。
- 否則：用 **複製**（舊的元素都還在，失敗時直接丟掉新空間就好）。

這就是第 06 課說「移動建構子一定要加 `noexcept`」的原因。

---

# 第五部分：noexcept

## 5.1 noexcept 的意思

**白話**：標記「**這個函式保證不會拋出例外**」。

```cpp
void swap(Buffer& a, Buffer& b) noexcept;
Buffer(Buffer&& other) noexcept;
int size() const noexcept { return n_; }
```

**好處**：
1. 讓使用者（和標準函式庫）知道可以放心依賴它（例如 `vector` 選擇移動）。
2. 編譯器可以做更多最佳化。

## 5.2 違反 noexcept 會怎樣？

如果標了 `noexcept` 的函式 **真的拋出了例外**，不會往外傳遞，而是 **直接呼叫 `std::terminate()`**，程式終止。

**比喻**：保證書上寫著「絕不故障」，如果真的故障了，不是送修，而是整台報廢。

## 5.3 該標 noexcept 的地方

- **移動建構子、移動指定運算子**（最重要）
- **`swap`**
- **解構子**（預設就是）
- 簡單的、明顯不會失敗的查詢函式（`size()`、`empty()`）

**不確定的就不要標** —— 標錯的代價（程式直接終止）比不標更嚴重。

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
└── ...
```

## 6.2 自訂例外

**繼承標準例外**，讓使用者可以用 `catch (const exception&)` 統一處理：

```cpp
class CalcError : public runtime_error {           // C13 的設計
public:
    using runtime_error::runtime_error;            // 繼承建構子
};
class DivisionByZero : public CalcError {
public:
    DivisionByZero() : CalcError("division by zero") {}
};
class Overflow : public CalcError {
public:
    Overflow() : CalcError("overflow") {}
};

try { calc.binary("div"); }
catch (const CalcError& e) { cout << "error: " << e.what() << '\n'; }   // 計算機的所有錯誤
```

建立 **例外的階層**，讓呼叫者可以選擇要捕捉「特定的錯誤」還是「這一類的所有錯誤」。

## 6.3 🔍 例外的成本

主流編譯器使用「**零成本例外 (zero-cost exceptions)**」：
- **沒有拋出例外時**：幾乎沒有額外的執行成本（`try` 區塊不會讓程式變慢）。
- **拋出例外時**：非常昂貴（要查表、展開堆疊），可能比一般函式呼叫慢上千倍。

所以 **例外只用在真正「例外」的情況**。

## 6.4 不要用例外的情況

| 情況 | 為什麼 | 改用 |
|---|---|---|
| 「失敗」是常見的正常結果（找不到、使用者取消） | 太慢、而且不是「例外」 | 回傳值、`optional`、`bool` |
| 控制流程（用例外跳出迴圈） | 難讀又慢 | `break`、`return` |
| 程式的 bug（不該發生的情況） | 應該修 bug，而不是處理它 | `assert` |
| 解構子裡 | 會導致 `terminate` | 在解構子裡自己處理掉 |
| 效能極度關鍵的迴圈 | 拋出成本太高 | 錯誤碼 |

`C09` 用回傳錯誤訊息（帳戶操作失敗是常見情況），`C13` 用例外（為了練習例外與強保證），兩種設計都合理。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 例外 | Exception | 用來回報錯誤、不能被忽略的機制 | 1 |
| 拋出 / 捕捉 | throw / catch | 發出錯誤 / 處理錯誤 | 2.1 |
| 重新拋出 | Rethrow (`throw;`) | 把同一個例外繼續往外丟 | 2.4 |
| 終止 | std::terminate | 沒被捕捉的例外會讓程式終止 | 2.5 |
| 堆疊展開 | Stack Unwinding | 例外往外傳時依序解構區域物件 | 3.1 |
| 例外安全 | Exception Safety | 例外發生時物件的狀態保證 | 4 |
| 不丟 / 強 / 基本保證 | No-throw / Strong / Basic Guarantee | 不會失敗 / 失敗時完全復原 / 失敗時不洩漏 | 4 |
| noexcept | noexcept | 保證不拋出例外 | 5.1 |
| 標準例外階層 | Standard Exception Hierarchy | logic_error、runtime_error 等 | 6.1 |
| 零成本例外 | Zero-cost Exceptions | 不拋出時沒有成本，拋出時很貴 | 6.3 |

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

---

# 習題解答

**題 1**：`C E`。`out_of_range` 是 `logic_error` 的子類別，**不是** `runtime_error`，內層的 `catch` 不符合，例外繼續往外傳（`B` 不會印出）；外層第一個符合的是 `logic_error` → `C`。

**題 2**：`abB!A`。建立 `a`、`b`；拋出例外時 `c` 還沒建立；堆疊展開解構 `b`（印 `B`）；捕捉到例外印 `!`；`main` 結束時解構 `a`（印 `A`）。

**題 3**：`out_of_range` 是 `exception` 的子類別，會被第一個 `catch` 攔下，第二個 `catch` **永遠不會執行**。要把子類別寫在前面。

**題 4**：`throw;` 重新拋出 **原本的例外物件**，型別完整保留（如果原本是 `out_of_range`，外層還是可以用 `catch (const out_of_range&)` 捕捉）。`throw e;` 拋出的是 `e` 的 **複製品**，型別是 `e` 的靜態型別 `exception`，子類別的資訊被 **切割** 掉了。

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

---

# 程式練習

- **`C13 安全的計算機`**：自訂例外階層、在計算之前檢查溢位、強例外保證（出錯時堆疊完全不變）、`LLONG_MIN % -1` 的陷阱。
