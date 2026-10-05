# 15. 現代 C++ 工具箱與未定義行為總整理

> 程式練習：本課沒有獨立的評測題。建議回頭用本課的工具改寫 `C01` ~ `C14` 的解答。
>
> 先備知識：前面全部的課程。這一課是「總複習 + 補充」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | C++ 的版本 | C++11 / 14 / 17 / 20 / 23 各帶來了什麼 |
| 第二部分 | 讓程式更清楚的語法 | `enum class`、結構化綁定、`using` 別名、屬性、原始字串 |
| 第三部分 | 實用的標準型別 | `optional`、`variant`、`tuple`、`array`、`span`、`chrono` |
| 第四部分 | C++20 一瞥 | ranges、`format`、`<=>`、concepts |
| 第五部分 | 未定義行為總整理 | 這條路線提過的所有 UB，以及怎麼偵測 |
| 第六部分 | 寫好 C++ 的檢查清單 | 寫完程式之後逐項檢查 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：C++ 的版本

| 版本 | 重點 | 這條路線提過的 |
|---|---|---|
| C++98 / 03 | 「傳統 C++」：類別、模板、STL | 大部分基礎 |
| **C++11** | **現代 C++ 的起點** | `auto`、範圍 for、lambda、`nullptr`、移動語意、`unique_ptr` / `shared_ptr`、`constexpr`、`enum class`、`override`、大括號初始化、`unordered_map` |
| C++14 | 補強 C++11 | `make_unique`、泛型 lambda（`auto` 參數）、函式回傳型別推導、數字分隔符 `1'000'000` |
| **C++17** | 大量實用功能 | 結構化綁定、`if` 帶初始化、`optional`、`variant`、`string_view`、`if constexpr`、摺疊運算式、`inline` 變數、`std::gcd`、CTAD |
| **C++20** | 大改版 | concepts、ranges、`<=>`、`format`、`span`、modules、coroutines、`erase_if` |
| C++23 | 補強 | `std::expected`、`std::print`、`std::ranges::to` |

編譯時用 `-std=c++17` 或 `-std=c++20` 指定版本。本平台預設用 **C++17**。

---

# 第二部分：讓程式更清楚的語法

## 2.1 enum class（有範圍的列舉）

**白話**：傳統的 `enum` 有兩個問題：名字會「洩漏」到外面的作用域，而且會 **自動轉成整數**。`enum class` 解決了這兩個問題。

```cpp
enum Color { RED, GREEN };
enum Light { RED, YELLOW };     // ❌ 編譯錯誤：RED 重複了（都洩漏到同一個作用域）
int x = GREEN + 1;              // 可以：自動轉成整數，容易出錯

enum class Color2 { Red, Green };
enum class Light2 { Red, Yellow };   // ✅ 不衝突
Color2 c = Color2::Red;              // 要寫完整名稱
int y = c;                           // ❌ 不會自動轉成整數
int z = static_cast<int>(c);         // 要明確轉換
```

**比喻**：傳統 `enum` 像是把所有標籤都貼在公共佈告欄上，同名的會撞在一起；`enum class` 是每個列舉有自己的資料夾。

搭配 `switch` 時，編譯器（`-Wall`）會警告「有列舉值沒有被處理」，避免漏掉。

## 2.2 結構化綁定 (Structured Bindings, C++17)

**白話**：把 `pair`、`tuple`、`struct`、陣列 **一次拆開** 成好幾個變數。

```cpp
pair<string, int> p = {"amy", 90};
auto [name, score] = p;                  // name = "amy", score = 90

map<string, int> m;
for (const auto& [key, val] : m) { }     // 走訪 map 不用再寫 it->first、it->second

struct Point { int x, y; };
auto [x, y] = Point{3, 4};

if (auto [it, inserted] = m.insert({"bob", 70}); !inserted) { /* 已經存在 */ }
```

`auto&` 綁定參考（可以修改原物件），`const auto&` 唯讀不複製，`auto` 是複製。

## 2.3 using 型別別名

```cpp
typedef long long ll;                         // 舊寫法
using ll = long long;                         // 新寫法，比較好讀
using Graph = vector<vector<int>>;
template <class T> using Matrix = vector<vector<T>>;   // 模板別名：typedef 做不到
Matrix<double> m;
```

## 2.4 屬性 (Attributes)

| 屬性 | 意思 |
|---|---|
| `[[nodiscard]]` | 忽略回傳值時警告（第 04 課） |
| `[[maybe_unused]]` | 這個變數 / 參數可能沒用到，不要警告 |
| `[[fallthrough]]` | `switch` 的穿透是故意的（第 03 課） |
| `[[deprecated("原因")]]` | 已過時，使用時警告 |
| `[[likely]]` / `[[unlikely]]`（C++20） | 提示編譯器哪個分支比較常執行 |

## 2.5 原始字串字面值 (Raw String Literal)

**白話**：`R"(...)"` 裡面的內容 **完全照原樣**，反斜線不是跳脫字元。寫正規表示式、Windows 路徑、多行文字時很方便。

```cpp
string path = "C:\\Users\\amy\\file.txt";     // 一般字串：每個 \ 都要寫兩次
string path2 = R"(C:\Users\amy\file.txt)";    // 原始字串
string json = R"({
    "name": "amy",
    "score": 90
})";
```

## 2.6 使用者定義字面值 (User-defined Literals)

```cpp
using namespace std::literals;
auto s = "hello"s;         // std::string，不是 const char*
auto sv = "hello"sv;       // std::string_view
auto t = 500ms;            // std::chrono::milliseconds
```

---

# 第三部分：實用的標準型別

## 3.1 std::optional（C++17）

**白話**：「**可能有值，也可能沒有**」的型別。取代「用 -1 或特殊值表示失敗」的寫法。

**比喻**：一個可能是空的盒子。打開之前要先確認裡面有沒有東西。

```cpp
#include <optional>
optional<int> parse_int(const string& s) {
    try { return stoi(s); }
    catch (...) { return nullopt; }        // 沒有值
}

if (auto v = parse_int("42")) {            // 有值嗎？
    cout << *v;                            // 取值（沒有值時用 * 是 UB）
}
parse_int("abc").value_or(0);              // 沒有值就用 0
parse_int("abc").value();                  // 沒有值時丟出 bad_optional_access
```

**為什麼比特殊值好？** 如果用 `-1` 代表「找不到」，那 `-1` 本身是合法答案時就分不清了（資料結構路線 `08_next_greater` 的提示就提到這個問題）。

## 3.2 std::variant（C++17）

**白話**：「**幾種型別之一**」—— 同一時間只存其中一種，而且 **知道目前存的是哪一種**。型別安全版的 `union`。

```cpp
#include <variant>
variant<int, double, string> v = 42;
v = "hello"s;                              // 現在存的是 string
holds_alternative<string>(v);              // true
get<string>(v);                            // "hello"
get<int>(v);                               // ❌ 丟出 bad_variant_access

// visit：根據目前存的型別，呼叫對應的處理方式
visit([](const auto& x) { cout << x << '\n'; }, v);
```

**用途**：運算式的 token（數字或運算子）、解析結果（成功的值或錯誤訊息）、狀態機的狀態。
和第 08 課的繼承相比：`variant` 適合「**型別的種類固定**、但操作很多」的情況；繼承適合「**操作固定**、但型別會一直增加」的情況。

## 3.3 std::tuple

```cpp
tuple<string, int, double> t = {"amy", 20, 3.5};
get<0>(t);                                  // "amy"
auto [name, age, gpa] = t;                  // 結構化綁定
tie(a, b) = make_pair(1, 2);                // 一次指定好幾個變數
// 多條件比較的捷徑（第 04 課）
return tie(a.score, a.name) < tie(b.score, b.name);
```

## 3.4 std::array

**白話**：**固定大小** 的陣列，像內建陣列一樣放在 stack 上、沒有額外成本，但有 `size()`、可以複製、**不會退化成指標**、可以用在 STL 演算法。

```cpp
array<int, 5> a = {1, 2, 3, 4, 5};
a.size();                // 5
auto b = a;              // 可以整個複製（內建陣列不行）
sort(a.begin(), a.end());
void f(const array<int, 5>& arr);   // 大小是型別的一部分，不會遺失
```

## 3.5 std::span（C++20）

**白話**：「一段連續資料」的 **視窗**（就像 `string_view` 之於 `string`），可以接受 `vector`、`array`、內建陣列，解決「傳陣列給函式會遺失長度」的問題（第 05 課）。

```cpp
void print(span<const int> s) { for (int x : s) cout << x; }
vector<int> v = {1, 2, 3};
int arr[] = {4, 5};
print(v); print(arr);    // 都可以，而且知道長度
```

## 3.6 std::chrono：時間

```cpp
#include <chrono>
auto start = chrono::steady_clock::now();
do_work();
auto end = chrono::steady_clock::now();
auto ms = chrono::duration_cast<chrono::milliseconds>(end - start).count();
cout << "took " << ms << " ms\n";
```

測量程式執行時間用 `steady_clock`（不會因為系統調整時間而倒退）。

---

# 第四部分：C++20 一瞥

## 4.1 Ranges

**白話**：讓演算法直接接受 **整個容器**，而且可以用 `|` 把操作 **串起來**，像水管一樣。

```cpp
#include <ranges>
vector<int> v = {1, 2, 3, 4, 5, 6};
ranges::sort(v);                                   // 不用再寫 v.begin(), v.end()

auto evens_squared = v
    | views::filter([](int x) { return x % 2 == 0; })
    | views::transform([](int x) { return x * x; });
for (int x : evens_squared) cout << x << ' ';      // 4 16 36
```

`views` 是 **惰性求值 (lazy evaluation)** 的：不會建立中間的 vector，走訪時才一個一個計算。

## 4.2 std::format

```cpp
#include <format>
cout << format("{} scored {:.2f} ({:>5})\n", name, avg, rank);
// 結合 printf 的簡潔與 cout 的型別安全
```

## 4.3 其他

- **`<=>` 三向比較**（第 07 課）：`auto operator<=>(const T&) const = default;` 一次產生所有比較運算子。
- **Concepts**（第 10 課）：為模板參數加上清楚的要求。
- **Modules**：取代 `#include`，加快編譯、避免巨集污染（第 14 課的問題）。
- **Coroutines（協程）**：可以「暫停再繼續」的函式，用於非同步程式與產生器。

---

# 第五部分：未定義行為總整理

## 5.1 三種「不確定」

| 名稱 | 英文 | 意思 | 例子 |
|---|---|---|---|
| 實作定義 | Implementation-defined | 結果由編譯器決定，**而且要寫在文件裡** | `sizeof(long)`、`char` 有沒有號 |
| 未指定 | Unspecified | 幾種可能之一，編譯器不用說明是哪一種 | `f() + g()` 誰先呼叫 |
| **未定義** | **Undefined** | 標準 **完全沒有規定**，任何事都可能發生 | 陣列越界、有號整數溢位 |

**未定義行為 (UB) 為什麼這麼危險？**
- 不一定會當掉 —— 可能「看起來正常」，換一台電腦、換一個編譯選項、換一筆測資就出問題。
- 編譯器可以 **假設 UB 永遠不會發生**，並據此最佳化，把你的檢查程式碼刪掉（第 02 課的溢位例子）。

**比喻**：UB 就像合約上寫著「若發生某情況，後果 **不予規範**」—— 可能沒事，也可能損失慘重，而且你沒有立場抱怨。

## 5.2 UB 清單（這條路線提過的）

| 類別 | 未定義行為 | 哪一課 | 怎麼偵測 / 避免 |
|---|---|---|---|
| **記憶體** | 陣列 / vector 越界 | 05 | `--debug`（ASan、`_GLIBCXX_DEBUG`）、`at()` |
| | 解參考空指標 / 野指標 | 05 | 初始化指標、ASan |
| | 使用已釋放的記憶體（use-after-free） | 05、06 | 智慧指標、ASan |
| | 重複釋放（double free）、`new[]` 配 `delete` | 06 | RAII、ASan |
| | 回傳區域變數的參考 / 指標 | 04 | `-Wall` 會警告 |
| | 懸空的 `string_view` / lambda 參考捕獲 | 04、12 | 注意生命週期 |
| | 迭代器失效後繼續使用 | 11 | `_GLIBCXX_DEBUG` |
| **數值** | 有號整數溢位 | 02 | 先檢查再計算、`__builtin_*_overflow`、UBSan |
| | 整數除以 0、`% 0` | 02 | 先檢查 |
| | `LLONG_MIN / -1`、`LLONG_MIN % -1` | 02、`C13` | 特別處理 |
| | 移位量 ≥ 位元數或是負數 | 02、`C02` | 用無號數、檢查移位量、UBSan |
| | 浮點數轉整數時超出範圍 | 01 | 先檢查範圍 |
| **讀取** | 讀取未初始化的變數 | 01 | 宣告時就初始化、`-Wall` |
| | 對空的 `stack` / `vector` 呼叫 `top()` / `back()` | DS 05 | 先檢查 `empty()`、`_GLIBCXX_DEBUG` |
| **順序** | 同一個運算式裡修改同一個變數兩次 | 02 | 拆成多個敘述 |
| **其他** | 函式沒有 `return`（非 void） | 03 | `-Wall` |
| | 比較函式違反嚴格弱序 | 04 | 用 `<`，不要用 `<=` |
| | 修改 `const` 物件（透過 `const_cast`） | 01 | 不要這樣做 |
| | 透過沒有虛擬解構子的基底指標刪除衍生物件 | 08 | 虛擬解構子 |
| | 對負的 `char` 呼叫 `isalpha` 等函式 | 12 | 先轉 `unsigned char` |

## 5.3 偵測工具

```bash
# 開啟所有常用警告，並把警告當錯誤處理
g++ -std=c++17 -Wall -Wextra -Wshadow -Wconversion -Werror main.cpp

# 執行時檢查（本平台的 --debug 模式）
g++ -std=c++17 -g -fsanitize=address,undefined -D_GLIBCXX_DEBUG main.cpp
```

| 工具 | 抓什麼 |
|---|---|
| `-Wall -Wextra` | 未初始化、沒有 return、有號無號比較、`=` 寫成 `==`、初始化順序…… |
| `-Wshadow` | 變數遮蔽 |
| `-Wconversion` | 可能遺失資訊的隱式轉換 |
| AddressSanitizer (`address`) | 越界、use-after-free、double free、記憶體洩漏 |
| UndefinedBehaviorSanitizer (`undefined`) | 溢位、移位、空指標、未對齊存取 |
| `_GLIBCXX_DEBUG` | STL 容器的越界、迭代器失效、空容器操作 |
| Valgrind | 記憶體錯誤（不用重新編譯，但比較慢） |

---

# 第六部分：寫好 C++ 的檢查清單

寫完程式之後，逐項檢查：

**型別與數值**
- [ ] 數字會超過 `2 × 10⁹` 嗎？用 `long long` 了嗎？常數寫 `1LL << k` 了嗎？
- [ ] 有號 / 無號混在一起比較嗎？`v.size() - 1` 在空的時候會出事嗎？
- [ ] 整數除法的地方，想要的是小數嗎？
- [ ] 浮點數有用 `==` 比較嗎？

**記憶體與生命週期**
- [ ] 有裸的 `new` / `delete` 嗎？能換成容器或 `make_unique` 嗎？
- [ ] 有回傳區域變數的參考 / 指標 / `string_view` 嗎？
- [ ] lambda 的參考捕獲會比被捕獲的變數活得久嗎？
- [ ] 修改容器之後，還有在用舊的迭代器 / 指標嗎？

**類別**
- [ ] 不修改物件的成員函式都加 `const` 了嗎？
- [ ] 大型參數用 `const T&` 傳遞了嗎？
- [ ] 單一參數的建構子加 `explicit` 了嗎？
- [ ] 自己管理資源的類別，有遵守五法則（或 `= delete`）嗎？
- [ ] 複製指定能處理自我指定嗎？移動操作加 `noexcept` 了嗎？
- [ ] 有虛擬函式的類別，解構子是 `virtual` 嗎？覆寫的函式加 `override` 了嗎？

**控制流程與錯誤處理**
- [ ] `switch` 的每個 `case` 都有 `break`（或故意 `[[fallthrough]]`）嗎？
- [ ] 每條路徑都有 `return` 嗎？
- [ ] 比較函式用的是 `<` 而不是 `<=` 嗎？
- [ ] 例外用 `const&` 捕捉了嗎？出錯時物件的狀態還正確嗎？

**最後**
- [ ] 用 `-Wall -Wextra` 編譯，沒有任何警告？
- [ ] 用 `--debug` 跑過所有測資？

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 有範圍的列舉 | enum class | 名字不洩漏、不自動轉整數的列舉 | 2.1 |
| 結構化綁定 | Structured Bindings | 一次拆開 pair / tuple / struct | 2.2 |
| 型別別名 | Type Alias (`using`) | 幫型別取別名 | 2.3 |
| 屬性 | Attribute `[[...]]` | 給編譯器的額外提示 | 2.4 |
| 原始字串 | Raw String Literal `R"(...)"` | 反斜線不跳脫的字串 | 2.5 |
| 可選值 | std::optional | 可能有值也可能沒有 | 3.1 |
| 變體 | std::variant | 幾種型別之一，型別安全 | 3.2 |
| 元組 | std::tuple | 固定數量、不同型別的組合 | 3.3 |
| 視窗 | std::span | 連續資料的不擁有視窗 | 3.5 |
| 範圍 | Ranges | 直接操作整個容器、可串接的演算法 | 4.1 |
| 惰性求值 | Lazy Evaluation | 需要時才計算 | 4.1 |
| 實作定義 | Implementation-defined | 由編譯器決定並寫在文件裡 | 5.1 |
| 未指定行為 | Unspecified Behavior | 幾種可能之一 | 5.1 |
| 未定義行為 | Undefined Behavior | 標準沒有規定，任何事都可能發生 | 5.1 |
| 消毒器 | Sanitizer | 執行時偵測記憶體錯誤與 UB 的工具 | 5.3 |

---

# 習題

### 題 1：用 `optional` 改寫

```cpp
// 找不到時回傳 -1
int find_index(const vector<int>& v, int target);
```

為什麼 `optional` 版本比較好？

### 題 2：預測輸出

```cpp
map<string, int> m = {{"b", 2}, {"a", 1}};
for (auto& [k, v] : m) v *= 10;
for (const auto& [k, v] : m) cout << k << v << ' ';
```

### 題 3：下面每一項是「實作定義」、「未指定」還是「未定義」？

```
a) sizeof(int) 是多少
b) int x = INT_MAX; x++;
c) f(g(), h()) 中 g 和 h 誰先呼叫
d) char 是有號還是無號
e) int a[3]; a[3] = 0;
f) 1 << 40（int 是 32 位元）
```

### 題 4：下面的程式碼可以用本課的哪些工具改寫得更清楚？

```cpp
#define RED 0
#define GREEN 1
typedef vector<vector<int>> Grid;
pair<int, int> p = get_pos();
int row = p.first, col = p.second;
```

### 題 5：`variant<int, string> v = 5; cout << get<string>(v);` 會發生什麼事？

### 題 6：一個程式在你的電腦上正常，在評測系統上 WA。列出三個可能和「未定義行為」有關的原因。

---

# 習題解答

**題 1**：

```cpp
optional<size_t> find_index(const vector<int>& v, int target) {
    for (size_t i = 0; i < v.size(); i++) if (v[i] == target) return i;
    return nullopt;
}
if (auto i = find_index(v, 7)) cout << *i;
```

好處：「可能找不到」寫在 **型別** 上，呼叫者一看就知道要檢查；不用佔用一個特殊值（`-1` 也逼得回傳型別必須是有號整數）；忘了檢查直接當成數字用時，型別不符會編譯錯誤。

**題 2**：`a10 b20 `。`auto&` 綁定參考，修改的是 `map` 裡的值；`map` 依 key 排序走訪。

**題 3**：
- a) **實作定義**
- b) **未定義**（有號整數溢位）
- c) **未指定**
- d) **實作定義**
- e) **未定義**（越界）
- f) **未定義**（移位量 ≥ 位元數）

**題 4**：

```cpp
enum class Color { Red, Green };                 // 取代 #define
using Grid = vector<vector<int>>;                // 取代 typedef
auto [row, col] = get_pos();                     // 結構化綁定
```

**題 5**：`v` 目前存的是 `int`，用 `get<string>` 取值會丟出 `std::bad_variant_access` 例外（沒有捕捉的話程式終止）。應該先用 `holds_alternative<string>(v)` 檢查，或用 `get_if<string>(&v)`（不符合時回傳 `nullptr`）。

**題 6**（任選三個）：
- 使用了 **未初始化的變數**：在你的電腦上碰巧是 0，評測系統上是別的值。
- **陣列越界**：在你的電腦上碰巧讀到 0 或沒寫壞重要的東西。
- **有號整數溢位**：不同的最佳化等級（`-O0` vs `-O2`）結果不同。
- **求值順序**：`i++ + i++` 這類寫法在不同編譯器結果不同。
- 平台差異（實作定義）：`long` 在 Windows 是 32 位元、Linux 是 64 位元。

**解法**：用 `-Wall -Wextra` 編譯並修正所有警告，再用 `--debug`（sanitizer）跑一遍。
