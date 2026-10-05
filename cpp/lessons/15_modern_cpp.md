# 15. 現代 C++ 工具箱與未定義行為總整理

> 程式練習：本課沒有獨立的評測題。建議回頭用本課的工具改寫 `C01` ~ `C14` 的解答。
>
> 先備知識：前面全部的課程。這一課是「總複習 + 補充」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | C++ 的版本 | C++11 / 14 / 17 / 20 / 23 各帶來了什麼 |
| 第二部分 | 讓程式更清楚的語法 | `auto` / `decltype`、`enum class`、結構化綁定、帶初始化的 `if` / `switch`、`using` 別名、`constexpr`、屬性、原始字串、使用者定義字面值 |
| 第三部分 | 實用的標準型別 | `optional`、`variant`、`any`、`tuple`、`pair`、`array`、`function`、`span`、`chrono`、亂數 |
| 第四部分 | C++20 一瞥 | ranges、`format`、`<=>`、concepts、其他小功能 |
| 第五部分 | 未定義行為總整理 | 這條路線提過的所有 UB，以及怎麼用工具偵測（附真實的偵測訊息） |
| 第六部分 | 寫好 C++ 的檢查清單 | 寫完程式之後逐項檢查 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際編譯執行過的結果；標示「C++20」的範例要用 `-std=c++20` 編譯。標 🔍 的是深入內容。

---

# 第一部分：C++ 的版本

| 版本 | 重點 | 這條路線提過的 |
|---|---|---|
| C++98 / 03 | 「傳統 C++」：類別、模板、STL | 大部分基礎 |
| **C++11** | **現代 C++ 的起點** | `auto`、範圍 for、lambda、`nullptr`、移動語意、`unique_ptr` / `shared_ptr`、`constexpr`、`enum class`、`override`、大括號初始化、`unordered_map`、變長模板 |
| C++14 | 補強 C++11 | `make_unique`、泛型 lambda（`auto` 參數）、函式回傳型別推導、數字分隔符 `1'000'000`、二進位字面值 `0b1010` |
| **C++17** | 大量實用功能 | 結構化綁定、`if` 帶初始化、`optional`、`variant`、`any`、`string_view`、`if constexpr`、摺疊運算式、`inline` 變數、`std::gcd`、CTAD |
| **C++20** | 大改版 | concepts、ranges、`<=>`、`format`、`span`、modules、coroutines、`erase_if`、`contains`、`starts_with` |
| C++23 | 補強 | `std::expected`、`std::print`、`std::ranges::to` |

編譯時用 `-std=c++17` 或 `-std=c++20` 指定版本。本平台預設用 **C++17**。

**怎麼知道目前用的是哪一版？**

```cpp
cout << __cplusplus << '\n';     // 輸出：201703（-std=c++17）；C++20 是 202002
```

---

# 第二部分：讓程式更清楚的語法

## 2.1 auto 與 decltype

**`auto`**：讓編譯器 **從初始值推導型別**（第 01 課）。

```cpp
auto a = 42;                 // int
auto b = 3.0;                // double
auto c = 'x';                // char
auto d = "hi";               // const char*（不是 string！）
auto e = string("hi");       // string
auto f = {1, 2, 3};          // initializer_list<int>（大括號的特例）
vector<int> v = {1, 2, 3};
auto it = v.begin();         // vector<int>::iterator：不用寫出又長又難記的型別
cout << is_same_v<decltype(d), const char*> << is_same_v<decltype(it), vector<int>::iterator> << '\n';   // 輸出：11
```

**`auto` 會去掉參考和頂層 const**（跟模板推導一樣，第 10 課 2.2）：

```cpp
const int ci = 5;
int& ref = a;
auto x1 = ci;                // int（const 被去掉）
auto x2 = ref;               // int（是複製品，不是參考）
auto& x3 = ref;              // int&（要參考就寫 auto&）
const auto& x4 = ci;         // const int&
x2 = 100;                    // 不影響 a
x3 = 200;                    // 修改了 a
cout << a << '\n';           // 輸出：200
```

**`decltype(運算式)`**：取得運算式的 **型別**（不會去掉參考和 const，運算式也不會被執行）。

```cpp
int n = 0;
decltype(n) m = 5;           // int
decltype(v.size()) sz = 0;   // size_t：不用記住 size() 回傳什麼型別
cout << is_same_v<decltype(ci), const int> << is_same_v<decltype(ref), int&> << '\n';   // 輸出：11
```

**什麼時候用 `auto`？**
- ✅ 型別很長、或從右邊就看得出來：迭代器、`make_unique<...>()`、lambda、`static_cast<T>(...)`。
- ⚠️ 型別很重要、而且右邊看不出來時，寫出來比較清楚：`int total = compute();`。
- ❌ 注意陷阱：`auto s = "hi";` 是 `const char*`；`auto n = v.size() - 1;` 是無號數。

## 2.2 enum class（有範圍的列舉）

**是什麼**：傳統的 `enum` 有兩個問題：名字會「洩漏」到外面的作用域，而且會 **自動轉成整數**。`enum class` 解決了這兩個問題。

```cpp
enum Color { RED, GREEN };
// enum Light { RED, YELLOW };     // ❌ error: 'RED' conflicts with a previous declaration（都洩漏到同一個作用域）
int x = GREEN + 1;                 // 可以：自動轉成整數，容易出錯
cout << x << '\n';                 // 輸出：2

enum class Color2 { Red, Green };
enum class Light2 { Red, Yellow }; // ✅ 不衝突
Color2 c = Color2::Red;            // 要寫完整名稱
// int y = c;                      // ❌ error: cannot convert 'Color2' to 'int' in initialization
int z = static_cast<int>(c);       // 要明確轉換
cout << z << '\n';                 // 輸出：0
// if (c == Light2::Red) {}        // ❌ 不同的 enum class 不能比較：型別安全
```

**比喻**：傳統 `enum` 像是把所有標籤都貼在公共佈告欄上，同名的會撞在一起；`enum class` 是每個列舉有自己的資料夾。

### 指定數值與底層型別

```cpp
enum class Status : uint8_t {      // 底層型別：只佔 1 byte
    Ok = 0,
    NotFound = 404,                // ❌ error: enumerator value '404' is outside the range of underlying type 'uint8_t'
};
```

```cpp
enum class HttpStatus : int { Ok = 200, NotFound = 404, Error = 500 };
cout << static_cast<int>(HttpStatus::NotFound) << ' ' << sizeof(HttpStatus) << '\n';   // 輸出：404 4
```

### 搭配 switch

```cpp
enum class Op { Add, Sub, Mul };
int apply(Op op, int a, int b) {
    switch (op) {
        case Op::Add: return a + b;
        case Op::Sub: return a - b;
        case Op::Mul: return a * b;
    }
    return 0;
}
cout << apply(Op::Mul, 6, 7) << '\n';   // 輸出：42
```

`-Wall` 會在 `switch` **漏掉某個列舉值** 時警告（`enumeration value 'Mul' not handled in switch`），新增列舉值時不會忘記改。

### 把 enum class 印出來

`enum class` 不能直接 `cout`（不會自動轉成整數），通常寫一個轉換函式：

```cpp
string to_string(Op op) {
    switch (op) {
        case Op::Add: return "+";
        case Op::Sub: return "-";
        case Op::Mul: return "*";
    }
    return "?";
}
cout << to_string(Op::Sub) << '\n';     // 輸出：-
```

## 2.3 結構化綁定 (Structured Bindings, C++17)

**是什麼**：把 `pair`、`tuple`、`struct`、陣列 **一次拆開** 成好幾個變數。

```cpp
pair<string, int> p = {"amy", 90};
auto [name, score] = p;                  // name = "amy", score = 90
cout << name << ' ' << score << '\n';    // 輸出：amy 90

struct Point { int x, y; };
auto [px, py] = Point{3, 4};
cout << px + py << '\n';                 // 輸出：7

int arr[3] = {1, 2, 3};
auto [a1, a2, a3] = arr;
cout << a1 + a2 + a3 << '\n';            // 輸出：6

tuple<int, string, double> t = {1, "x", 2.5};
auto [ti, ts, td] = t;
cout << ts << td << '\n';                // 輸出：x2.5
```

**最常見的用途：走訪 map**

```cpp
map<string, int> m = {{"a", 1}, {"b", 2}};
for (const auto& [key, val] : m)         // 不用再寫 it->first、it->second
    cout << key << '=' << val << ' ';
cout << '\n';                            // 輸出：a=1 b=2
```

**接收函式的多個回傳值**

```cpp
pair<int, int> div_mod(int a, int b) { return {a / b, a % b}; }
auto [q, r] = div_mod(17, 5);
cout << q << ' ' << r << '\n';           // 輸出：3 2

auto [it2, inserted] = m.insert({"c", 3});   // insert 回傳 pair<迭代器, bool>
cout << inserted << ' ' << it2->first << '\n';   // 輸出：1 c
```

**`auto` / `auto&` / `const auto&` 的差別**：

```cpp
map<string, int> scores = {{"amy", 1}, {"bob", 2}};
for (auto [k, v] : scores) v *= 10;          // auto：複製品，修改不影響 map
cout << scores["amy"] << ' ';                // 1
for (auto& [k, v] : scores) v *= 10;         // auto&：綁定參考，修改的是 map 裡的值
cout << scores["amy"] << '\n';               // 10
// 輸出：1 10
```

**限制**：名字的個數必須 **剛好等於** 成員的個數；不能只取一部分（不需要的可以取名 `_` 或 `unused`，再加 `[[maybe_unused]]`）。

## 2.4 帶初始化的 if / switch（C++17）

**是什麼**：`if (初始化; 條件)`。初始化的變數 **只在 if / else 裡面有效**，不會洩漏到外面。

```cpp
map<string, int> stock = {{"apple", 5}};

// 舊寫法：it 在 if 之後還存在，容易被誤用，也佔用了名字
auto it = stock.find("apple");
if (it != stock.end()) cout << it->second << '\n';

// 新寫法：it 只在 if 裡面有效
if (auto it2 = stock.find("apple"); it2 != stock.end())
    cout << "有 " << it2->second << " 個\n";        // 輸出：有 5 個
else
    cout << "沒有\n";

if (auto pos = string("hello").find('l'); pos != string::npos)
    cout << "l 在 " << pos << '\n';                 // 輸出：l 在 2

switch (int code = 404; code / 100) {
    case 2: cout << "成功\n"; break;
    case 4: cout << "用戶端錯誤 " << code << '\n'; break;   // 輸出：用戶端錯誤 404
    default: cout << "其他\n";
}
```

## 2.5 using 型別別名

```cpp
typedef long long ll;                         // 舊寫法：名字在中間，難讀
using ll = long long;                         // 新寫法：「名字 = 型別」，比較好讀
using Graph = vector<vector<int>>;
using Callback = void (*)(int);               // 函式指標：typedef void (*Callback)(int); 更難讀
template <class T> using Matrix = vector<vector<T>>;   // 模板別名：typedef 做不到（第 10 課 3.7）

Graph g(3);
g[0].push_back(1);
Matrix<double> mat(2, vector<double>(2, 0.5));
cout << g[0][0] << ' ' << mat[1][1] << '\n';  // 輸出：1 0.5
```

## 2.6 constexpr：編譯期計算

**是什麼**：`constexpr` 變數的值 **在編譯時就決定**；`constexpr` 函式 **可以在編譯時執行**（引數是編譯期常數時）。

```cpp
constexpr int MAXN = 100005;                  // 編譯期常數：可以當陣列大小、模板參數
int buf[MAXN];

constexpr long long factorial(int n) {        // constexpr 函式
    long long r = 1;
    for (int i = 2; i <= n; i++) r *= i;
    return r;
}
constexpr long long f10 = factorial(10);      // 在「編譯時」就算好了，執行時不用計算
static_assert(f10 == 3628800);                // 編譯時檢查（第 10 課 6.1）
int k = 5;
cout << f10 << ' ' << factorial(k) << '\n';   // 輸出：3628800 120（引數不是常數時，就在執行時計算）
```

| | `const` | `constexpr` |
|---|---|---|
| 意思 | 初始化之後不能修改 | 值在 **編譯時** 就知道 |
| `const int n = read_input();` | ✅（執行時才知道值） | ❌ |
| 可以當陣列大小 / 模板參數 | 只有當初始值是常數時 | ✅ 一定可以 |

**`constexpr` 取代 `#define` 常數**（第 14 課）：有型別、有作用域、偵錯器看得到。

## 2.7 屬性 (Attributes)

**是什麼**：寫在 `[[ ]]` 裡、給編譯器的 **額外提示**。不改變程式的意思，但可以讓編譯器給出更好的警告或最佳化。

| 屬性 | 意思 |
|---|---|
| `[[nodiscard]]` | 忽略回傳值時警告（第 04 課） |
| `[[maybe_unused]]` | 這個變數 / 參數可能沒用到，不要警告 |
| `[[fallthrough]]` | `switch` 的穿透是故意的（第 03 課） |
| `[[deprecated("原因")]]` | 已過時，使用時警告 |
| `[[noreturn]]` | 這個函式永遠不會返回（例如一定會丟例外或 `exit`） |
| `[[likely]]` / `[[unlikely]]`（C++20） | 提示編譯器哪個分支比較常執行 |

```cpp
[[nodiscard]] bool save(const string& path) { return !path.empty(); }
[[deprecated("改用 save")]] void old_save() {}

void demo([[maybe_unused]] int debug_level) {
    // save("a.txt");                  // ⚠️ warning: ignoring return value of 'bool save(const std::string&)', declared with attribute 'nodiscard'
    if (!save("a.txt")) cerr << "失敗\n";
    // old_save();                     // ⚠️ warning: 'void old_save()' is deprecated: 改用 save
    int level = 2;
    switch (level) {
        case 2: cout << "二";
            [[fallthrough]];           // 故意穿透：-Wimplicit-fallthrough 不會警告
        case 1: cout << "一\n";
    }
}
demo(0);                               // 輸出：二一
```

## 2.8 原始字串字面值 (Raw String Literal)

**是什麼**：`R"(...)"` 裡面的內容 **完全照原樣**，反斜線不是跳脫字元，換行也會保留。寫正規表示式、Windows 路徑、多行文字時很方便。

```cpp
string path = "C:\\Users\\amy\\file.txt";     // 一般字串：每個 \ 都要寫兩次
string path2 = R"(C:\Users\amy\file.txt)";    // 原始字串：照原樣
cout << (path == path2) << '\n';              // 輸出：1

string json = R"({
  "name": "amy",
  "score": 90
})";
cout << json << '\n';
// 輸出：
// {
//   "name": "amy",
//   "score": 90
// }

string tricky = R"x(內容裡有 )" 也沒關係)x";  // 自訂分隔符號 x：遇到 )x" 才結束
cout << tricky << '\n';                       // 輸出：內容裡有 )" 也沒關係
```

## 2.9 使用者定義字面值 (User-defined Literals)

**是什麼**：數字或字串後面加上 **後綴**，產生特定型別的值。

```cpp
using namespace std::literals;
auto s = "hello"s;          // std::string，不是 const char*
auto sv = "hello"sv;        // std::string_view
auto t = 500ms;             // std::chrono::milliseconds
auto h = 2h + 30min;        // 時間可以直接相加
cout << s.size() + sv.size() << ' ' << chrono::duration_cast<chrono::minutes>(h).count() << '\n';   // 輸出：10 150
cout << is_same_v<decltype(s), string> << '\n';   // 輸出：1
```

**數字的寫法**（C++14）：

```cpp
long long big = 1'000'000'007;      // 數字分隔符 '：只是為了好讀
int mask = 0b1011;                  // 二進位
int hexv = 0xFF;                    // 十六進位
cout << big << ' ' << mask << ' ' << hexv << '\n';   // 輸出：1000000007 11 255
```

---

# 第三部分：實用的標準型別

## 3.1 std::optional（C++17）

**是什麼**：「**可能有值，也可能沒有**」的型別。取代「用 -1 或特殊值表示失敗」的寫法。

**比喻**：一個可能是空的盒子。打開之前要先確認裡面有沒有東西。

```cpp
#include <optional>
optional<int> parse_int(const string& s) {
    try { return stoi(s); }
    catch (...) { return nullopt; }        // nullopt：沒有值
}

auto r1 = parse_int("42"), r2 = parse_int("abc");
if (r1) cout << "有值：" << *r1 << '\n';                    // 輸出：有值：42
cout << r1.has_value() << r2.has_value() << '\n';          // 輸出：10
cout << r2.value_or(0) << '\n';                            // 沒有值就用 0 → 輸出：0
try { r2.value(); }                                        // value()：沒有值時丟出例外
catch (const bad_optional_access&) { cout << "空的\n"; }   // 輸出：空的
// *r2;                                                    // ❌ * 不檢查：沒有值時是未定義行為
```

| 操作 | 有值 | 沒有值 |
|---|---|---|
| `if (opt)` / `opt.has_value()` | `true` | `false` |
| `*opt` / `opt->member` | 取值 | **未定義行為** |
| `opt.value()` | 取值 | 丟出 `bad_optional_access` |
| `opt.value_or(預設)` | 取值 | 回傳預設值 |
| `opt = nullopt;` / `opt.reset()` | 變成沒有值 | |

**為什麼比特殊值好？** 如果用 `-1` 代表「找不到」，那 `-1` 本身是合法答案時就分不清了（資料結構路線 `08_next_greater` 的提示就提到這個問題）。

**optional 也可以當成員**：表示「這個欄位可以沒有填」。

```cpp
struct Person {
    string name;
    optional<string> nickname;          // 不一定有暱稱
};
Person p1{"amy", "A"}, p2{"bob", nullopt};
for (auto& p : {p1, p2})
    cout << p.name << ": " << p.nickname.value_or("(無)") << '\n';
// 輸出：
// amy: A
// bob: (無)
```

## 3.2 std::variant（C++17）

**是什麼**：「**幾種型別之一**」—— 同一時間只存其中一種，而且 **知道目前存的是哪一種**。型別安全版的 `union`。

```cpp
#include <variant>
variant<int, double, string> v = 42;        // 現在存的是 int
cout << v.index() << ' ' << get<int>(v) << '\n';   // 第幾種型別（從 0 開始）→ 輸出：0 42
v = "hello"s;                               // 現在存的是 string
cout << v.index() << ' ' << holds_alternative<string>(v) << ' ' << get<string>(v) << '\n';   // 輸出：2 1 hello
try { get<int>(v); }                        // 型別不符
catch (const bad_variant_access&) { cout << "現在不是 int\n"; }   // 輸出：現在不是 int
if (auto* ps = get_if<string>(&v)) cout << ps->size() << '\n';    // get_if：不符合時回傳 nullptr → 輸出：5
```

### visit：根據目前的型別做不同的事

```cpp
vector<variant<int, double, string>> items = {1, 2.5, "three"s};
for (auto& item : items)
    visit([](const auto& x) { cout << x << ' '; }, item);   // 泛型 lambda：每種型別都能處理
cout << '\n';                                               // 輸出：1 2.5 three

// 對不同型別做不同的事：用 if constexpr（第 10 課 6.3）
for (auto& item : items) {
    visit([](const auto& x) {
        using T = decay_t<decltype(x)>;
        if constexpr (is_same_v<T, int>) cout << "整數 ";
        else if constexpr (is_same_v<T, double>) cout << "小數 ";
        else cout << "字串 ";
    }, item);
}
cout << '\n';                                               // 輸出：整數 小數 字串
```

**用途**：運算式的 token（數字或運算子）、解析結果（成功的值或錯誤訊息）、狀態機的狀態。

```cpp
using Token = variant<long long, char>;      // 數字或運算子
vector<Token> tokens = {3LL, '+', 4LL};
long long total = 0;
char pending = '+';
for (auto& tk : tokens) {
    if (auto* num = get_if<long long>(&tk)) total = (pending == '+') ? total + *num : total - *num;
    else pending = get<char>(tk);
}
cout << total << '\n';                       // 輸出：7
```

**和第 08 課的繼承相比**：

| | `variant` | 繼承 + 虛擬函式 |
|---|---|---|
| 適合 | **型別的種類固定**、但操作很多 | **操作固定**、但型別會一直增加 |
| 新增一種型別 | 要改所有 `visit` 的地方 | 只新增一個子類別 |
| 新增一種操作 | 寫一個新的 `visit` | 要改每個子類別 |
| 記憶體 | 直接存值，不需要 heap 配置 | 通常要 `unique_ptr` |

## 3.3 std::any（C++17）

**是什麼**：可以存 **任何型別** 的值，取出時要 **指定正確的型別**。比 `variant` 更有彈性，但編譯器幫不上忙（型別錯了要到執行時才知道）。

```cpp
#include <any>
any a = 42;
cout << any_cast<int>(a) << '\n';           // 輸出：42
a = string("text");
cout << a.type().name() << '\n';            // 型別名稱（GCC 的編碼格式，可讀性差）
try { any_cast<int>(a); }
catch (const bad_any_cast&) { cout << "型別不對\n"; }   // 輸出：型別不對
```

**很少需要**：大部分情況下 `variant`（知道可能是哪幾種型別）或模板是更好的選擇。

## 3.4 std::pair 與 std::tuple

**`pair`**：兩個值的組合；**`tuple`**：任意數量、不同型別的值的組合。

```cpp
pair<string, int> p = make_pair("amy", 20);
cout << p.first << ' ' << p.second << '\n';    // 輸出：amy 20

tuple<string, int, double> t = {"bob", 21, 3.5};
cout << get<0>(t) << ' ' << get<2>(t) << '\n'; // 用索引取值（索引必須是編譯期常數）→ 輸出：bob 3.5
get<1>(t) = 22;                                // 可以修改
auto [name, age, gpa] = t;                     // 結構化綁定（2.3 節）
cout << age << ' ' << tuple_size_v<decltype(t)> << '\n';   // 輸出：22 3
```

### tie：一次指定好幾個變數

```cpp
int a, b;
tie(a, b) = make_pair(1, 2);                   // a = 1, b = 2
tie(a, b) = make_tuple(b, a);                  // 交換
cout << a << b << '\n';                        // 輸出：21
string nm;
tie(nm, ignore, ignore) = t;                   // 只取第一個，其他的忽略
cout << nm << '\n';                            // 輸出：bob
```

### 多條件比較的捷徑（第 04 課）

`pair` 和 `tuple` 的比較是 **字典序**：先比第一個，相同再比第二個……

```cpp
struct Student { string name; int score; int age; };
vector<Student> st = {{"amy", 90, 20}, {"bob", 95, 22}, {"cat", 90, 19}};
sort(st.begin(), st.end(), [](const Student& x, const Student& y) {
    return tie(y.score, x.age) < tie(x.score, y.age);   // 分數由高到低；同分時年紀由小到大
});
for (auto& s : st) cout << s.name << ' ';
cout << '\n';                                  // 輸出：bob cat amy
```

（`tie(y.score, ...)` 把 `x`、`y` 對調，就是由大到小。）

## 3.5 std::array

**是什麼**：**固定大小** 的陣列，像內建陣列一樣沒有額外成本，但有 `size()`、可以複製、**不會退化成指標**、可以用在 STL 演算法（第 11 課 2.5）。

```cpp
array<int, 5> a = {5, 3, 1, 4, 2};
auto b = a;                          // 可以整個複製（內建陣列不行）
sort(a.begin(), a.end());
cout << a.size() << ' ' << a[0] << ' ' << b[0] << ' ' << (a == b) << '\n';   // 輸出：5 1 5 0

void show(const array<int, 5>& arr);   // 大小是型別的一部分，傳進函式不會遺失
array<array<int, 3>, 2> grid{};        // 2×3 的二維陣列，全部是 0
grid[1][2] = 9;
cout << grid[1][2] << '\n';            // 輸出：9
```

## 3.6 std::function：存放任何「可以呼叫的東西」

**是什麼**：可以存放 **函式、lambda、函式物件**，只要「參數和回傳型別」符合。

```cpp
#include <functional>
int add(int a, int b) { return a + b; }
struct Mul { int operator()(int a, int b) const { return a * b; } };

function<int(int, int)> op;          // 「接受兩個 int、回傳 int」的任何可呼叫物件
op = add;               cout << op(3, 4) << ' ';      // 一般函式
op = Mul();             cout << op(3, 4) << ' ';      // 函式物件
op = [](int a, int b) { return a - b; };
                        cout << op(3, 4) << '\n';     // lambda
// 輸出：7 12 -1

map<string, function<int(int, int)>> ops = {
    {"+", add}, {"*", Mul()}, {"max", [](int a, int b) { return max(a, b); }}
};
cout << ops["max"](3, 9) << '\n';    // 輸出：9（指令表：用字串找到對應的運算）

function<void()> empty_fn;
try { empty_fn(); }                  // 空的 function 被呼叫
catch (const bad_function_call&) { cout << "空的 function\n"; }   // 輸出：空的 function
```

**代價**：比直接呼叫 lambda 慢一點（類似虛擬函式的間接呼叫），也可能配置記憶體。只有在「需要把不同的可呼叫物件存在同一個變數 / 容器裡」時才用；傳給演算法時直接用模板或 `auto` 就好。

## 3.7 std::span（C++20）

**是什麼**：「一段連續資料」的 **視窗**（就像 `string_view` 之於 `string`），可以接受 `vector`、`array`、內建陣列，解決「傳陣列給函式會遺失長度」的問題（第 05 課）。

```cpp
#include <span>          // C++20
int sum(span<const int> s) {
    int total = 0;
    for (int x : s) total += x;
    return total;
}
vector<int> v = {1, 2, 3};
int arr[] = {4, 5};
array<int, 3> a = {6, 7, 8};
cout << sum(v) << ' ' << sum(arr) << ' ' << sum(a) << '\n';     // 都可以，而且知道長度 → 輸出：6 9 21
cout << sum(span(v).subspan(1)) << '\n';                        // 子範圍：{2, 3} → 輸出：5
```

和 `string_view` 一樣：`span` **不擁有** 資料，原本的資料被銷毀後就不能再用。

## 3.8 std::chrono：時間

```cpp
#include <chrono>
auto start = chrono::steady_clock::now();
long long s = 0;
for (int i = 0; i < 10000000; i++) s += i;
auto end = chrono::steady_clock::now();
auto ms = chrono::duration_cast<chrono::milliseconds>(end - start).count();
cout << "took " << ms << " ms\n";        // 輸出：took 9 ms（數字依電腦而定）
```

**測量程式執行時間用 `steady_clock`**（不會因為系統調整時間而倒退）；`system_clock` 是「牆上的時間」，可能被校時調整。

**時間單位可以安全地換算**：

```cpp
using namespace std::chrono;
auto d = 2min + 30s;                               // 型別會自動選擇能精確表示的單位
cout << duration_cast<seconds>(d).count() << ' '   // 輸出：150
     << duration<double, ratio<60>>(d).count() << '\n';   // 換算成分鐘（小數）→ 輸出：2.5
```

## 3.9 亂數 (`<random>`)

**是什麼**：C++11 的亂數工具，分成 **產生器**（產生隨機的位元）和 **分佈**（把隨機位元轉成想要的範圍與分佈）。

```cpp
#include <random>
mt19937 rng(12345);                              // 梅森旋轉產生器，固定種子 → 每次執行結果相同
uniform_int_distribution<int> dice(1, 6);        // 1 到 6 的均勻分佈（兩端都包含）
uniform_real_distribution<double> unit(0.0, 1.0);
int counts[7] = {};
for (int i = 0; i < 60000; i++) counts[dice(rng)]++;
bool all_close = true;
for (int f = 1; f <= 6; f++) all_close &= abs(counts[f] - 10000) < 500;
cout << all_close << '\n';                       // 每個點數出現約 10000 次 → 輸出：1
double u = unit(rng);
cout << (0.0 <= u && u < 1.0) << '\n';           // 輸出：1
```

| | `rand() % 6 + 1`（C 的寫法） | `mt19937` + `uniform_int_distribution` |
|---|---|---|
| 品質 | 差（`RAND_MAX` 可能只有 32767） | 好 |
| 分佈 | 取餘數會讓小的數字機率稍高 | 精確的均勻分佈 |
| 執行緒安全 | 全域狀態 | 各自的產生器物件 |

**種子**：固定種子（例如 `12345`）每次結果相同，方便除錯與重現（本平台的 `gen.py` 產生測資也是這樣）；要每次不同就用 `random_device{}()` 或時間當種子。

---

# 第四部分：C++20 一瞥

> 本部分的範例要用 `-std=c++20` 編譯（GCC 13 以上）。

## 4.1 Ranges

**是什麼**：讓演算法直接接受 **整個容器**，而且可以用 `|` 把操作 **串起來**，像水管一樣。

```cpp
#include <ranges>
vector<int> v = {5, 2, 6, 1, 4, 3};
ranges::sort(v);                                   // 不用再寫 v.begin(), v.end()
for (int x : v) cout << x;                         // 輸出：123456
cout << '\n';

auto evens_squared = v
    | views::filter([](int x) { return x % 2 == 0; })   // 只留偶數
    | views::transform([](int x) { return x * x; });    // 平方
for (int x : evens_squared) cout << x << ' ';      // 輸出：4 16 36
cout << '\n';

for (int x : views::iota(1, 6) | views::reverse) cout << x;   // 1~5 反過來 → 輸出：54321
cout << '\n';
for (int x : v | views::take(3)) cout << x;        // 前 3 個 → 輸出：123
cout << '\n';
```

**`views` 是惰性求值 (lazy evaluation) 的**：不會建立中間的 vector，走訪時才一個一個計算。

| view | 作用 |
|---|---|
| `views::filter(pred)` | 只留下符合條件的 |
| `views::transform(f)` | 每個元素套用 `f` |
| `views::take(n)` / `views::drop(n)` | 前 n 個 / 跳過前 n 個 |
| `views::reverse` | 反轉 |
| `views::iota(a, b)` | `a, a+1, ..., b-1` |
| `views::keys` / `views::values` | map 的 key / value |

## 4.2 std::format

**是什麼**：用 `{}` 當佔位符的格式化，結合 `printf` 的簡潔與 `cout` 的型別安全（第 12 課 6.3）。

```cpp
#include <format>
string name = "amy";
double avg = 87.456;
int rank = 3;
cout << format("{} scored {:.2f} (rank {:>3})\n", name, avg, rank);   // 輸出：amy scored 87.46 (rank   3)
cout << format("{:08.3f}|{:<6}|{:^7}|{:x}\n", 3.14159, "ab", "mid", 255);
// 輸出：0003.142|ab    |  mid  |ff
cout << format("{1} {0}\n", "world", "hello");                       // 指定順序 → 輸出：hello world
```

| 格式 | 意思 |
|---|---|
| `{}` | 預設格式 |
| `{:.2f}` | 小數點後 2 位 |
| `{:>5}` / `{:<5}` / `{:^5}` | 寬度 5，靠右 / 靠左 / 置中 |
| `{:08.3f}` | 寬度 8、補 0、小數 3 位 |
| `{:x}` / `{:b}` | 十六進位 / 二進位 |

## 4.3 其他

- **`<=>` 三向比較**（第 07 課 4.5）：`auto operator<=>(const T&) const = default;` 一次產生所有比較運算子。
- **Concepts**（第 10 課 6.4）：為模板參數加上清楚的要求。
- **容器的小幫手**：

```cpp
map<string, int> m = {{"a", 1}};
cout << m.contains("a") << m.contains("z") << '\n';       // C++20：取代 count / find → 輸出：10
string s = "report.pdf";
cout << s.starts_with("rep") << s.ends_with(".pdf") << '\n';   // 輸出：11
vector<int> v = {1, 2, 3, 4, 5, 6};
erase_if(v, [](int x) { return x % 2 == 0; });            // 取代 erase-remove（第 11 課 6.1）
cout << v.size() << '\n';                                 // 輸出：3
```

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

```cpp
cout << sizeof(long) << '\n';             // 實作定義：Linux 64 位元是 8，Windows 是 4
int f_calls = 0;
auto f = [&] { return ++f_calls * 10; };
auto g = [&] { return ++f_calls; };
int r = f() + g();                        // 未指定：誰先呼叫不一定 → 21 或 12
cout << (r == 21 || r == 12) << '\n';     // 輸出：1（兩種都是「正確」的結果）
```

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
| | 對空的 `optional` 用 `*` | 15 | 先檢查，或用 `value()` |
| **順序** | 同一個運算式裡修改同一個變數兩次 | 02 | 拆成多個敘述 |
| **其他** | 函式沒有 `return`（非 void） | 03 | `-Wall` |
| | 比較函式違反嚴格弱序 | 04、11 | 用 `<`，不要用 `<=` |
| | 修改 `const` 物件（透過 `const_cast`） | 01 | 不要這樣做 |
| | 透過沒有虛擬解構子的基底指標刪除衍生物件 | 08 | 虛擬解構子 |
| | 對負的 `char` 呼叫 `isalpha` 等函式 | 12 | 先轉 `unsigned char` |
| | 靜態初始化順序（跨檔案的全域物件互相依賴） | 14 | 函式內的 `static` 區域變數 |

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

### 偵測工具的真實訊息

**有號整數溢位**（UBSan）：

```cpp
int x = INT_MAX;
x += argc;                // argc 是 1
```

```
ub1.cpp:3:49: runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
```

**移位量太大**（UBSan）：

```
ub4.cpp:1:58: runtime error: shift exponent 32 is too large for 32-bit type 'int'
```

**用指標讀到陣列外面**（ASan）：

```cpp
vector<int> v(3);
int* p = v.data();
return p[3];
```

```
==2008==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x50200000001c ...
READ of size 4 at 0x50200000001c thread T0
```

**使用已經 delete 的記憶體**（ASan）：

```
==2033==ERROR: AddressSanitizer: heap-use-after-free on address 0x502000000010 ...
```

**vector 的 `[]` 越界**（`_GLIBCXX_DEBUG`）：

```cpp
vector<int> v(3);
return v[3];
```

```
Error: attempt to subscript container with out-of-bounds index 3, but
container only holds 3 elements.
```

**怎麼讀這些訊息**：
1. 找 `runtime error:` 或 `ERROR:` 那一行：說明是 **哪一種** 錯誤。
2. UBSan 的訊息開頭就是 `檔名:行:列`。ASan 的訊息往下看，找第一個 **你自己的檔案名稱**（堆疊追蹤 `#0 #1 ...` 裡），那就是出錯的位置（編譯時要加 `-g` 才有行號）。
3. 沒有偵測工具時，這些程式可能「看起來正常」地印出錯誤的結果 —— 這就是為什麼提交前要用 `--debug` 跑一次。

---

# 第六部分：寫好 C++ 的檢查清單

寫完程式之後，逐項檢查：

**型別與數值**
- [ ] 數字會超過 `2 × 10⁹` 嗎？用 `long long` 了嗎？常數寫 `1LL << k` 了嗎？
- [ ] 有號 / 無號混在一起比較嗎？`v.size() - 1` 在空的時候會出事嗎？
- [ ] 整數除法的地方，想要的是小數嗎？
- [ ] 浮點數有用 `==` 比較嗎？
- [ ] 常數用 `constexpr` 而不是 `#define` 了嗎？列舉用 `enum class` 了嗎？

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
- [ ] 「可能沒有結果」用 `optional` 表達了嗎（而不是特殊值）？
- [ ] 例外用 `const&` 捕捉了嗎？出錯時物件的狀態還正確嗎？

**最後**
- [ ] 用 `-Wall -Wextra` 編譯，沒有任何警告？
- [ ] 用 `--debug` 跑過所有測資？

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 型別推導 | auto / decltype | 讓編譯器推導型別 / 取得運算式的型別 | 2.1 |
| 有範圍的列舉 | enum class | 名字不洩漏、不自動轉整數的列舉 | 2.2 |
| 結構化綁定 | Structured Bindings | 一次拆開 pair / tuple / struct | 2.3 |
| 帶初始化的 if | if with initializer | `if (init; cond)`，變數只在 if 裡有效 | 2.4 |
| 型別別名 | Type Alias (`using`) | 幫型別取別名 | 2.5 |
| 編譯期常數 | constexpr | 編譯時就算好的值 / 可以在編譯時執行的函式 | 2.6 |
| 屬性 | Attribute `[[...]]` | 給編譯器的額外提示 | 2.7 |
| 原始字串 | Raw String Literal `R"(...)"` | 反斜線不跳脫的字串 | 2.8 |
| 使用者定義字面值 | User-defined Literal | `"hi"s`、`500ms` 這類後綴 | 2.9 |
| 可選值 | std::optional | 可能有值也可能沒有 | 3.1 |
| 變體 | std::variant | 幾種型別之一，型別安全 | 3.2 |
| 任意值 | std::any | 可以存任何型別 | 3.3 |
| 元組 | std::tuple | 固定數量、不同型別的組合 | 3.4 |
| 可呼叫物件包裝 | std::function | 存放任何符合簽名的可呼叫物件 | 3.6 |
| 視窗 | std::span | 連續資料的不擁有視窗 | 3.7 |
| 亂數產生器 / 分佈 | Engine / Distribution | 產生隨機位元 / 轉成想要的範圍 | 3.9 |
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

### 題 7：預測輸出

```cpp
auto a = 5;
auto& b = a;
auto c = b;
c += 10;
b += 1;
const auto d = a;
cout << a << ' ' << b << ' ' << c << ' ' << d;
```

### 題 8：預測輸出

```cpp
optional<int> x;
optional<int> y = 7;
cout << x.value_or(-1) << ' ' << y.value_or(-1) << ' ';
x = y;
y.reset();
cout << x.has_value() << y.has_value() << ' ' << *x;
```

### 題 9：用 `variant<int, string>` 和 `visit`，寫一段程式把 `{3, "ab", 5}` 中的整數加總、字串長度也加總，輸出 `8 2`。

### 題 10：下面的 `switch` 用 `-Wall` 編譯會得到什麼警告？怎麼修？

```cpp
enum class Dir { Up, Down, Left, Right };
int dx(Dir d) {
    switch (d) {
        case Dir::Left: return -1;
        case Dir::Right: return 1;
    }
    return 0;
}
```

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

**題 7**：`6 6 15 6`。`b` 是 `a` 的參考；`c` 是 `b` 的 **複製品**（`auto` 去掉參考），`c += 10` 不影響 `a`，`c` = 15；`b += 1` 讓 `a` 變成 6；`d` 複製了 6。

**題 8**：`-1 7 10 7`。`x` 一開始沒有值 → `-1`；`y` 有 7。`x = y` 複製了值，`y.reset()` 只清空 `y`，所以 `x` 有值、`y` 沒有 → `10`；`*x` 是 7。

**題 9**：

```cpp
vector<variant<int, string>> items = {3, "ab", 5};
int num_sum = 0, len_sum = 0;
for (auto& it : items) {
    visit([&](const auto& x) {
        if constexpr (is_same_v<decay_t<decltype(x)>, int>) num_sum += x;
        else len_sum += (int)x.size();
    }, it);
}
cout << num_sum << ' ' << len_sum << '\n';    // 輸出：8 2
```

**題 10**：警告 `enumeration value 'Up' not handled in switch` 和 `enumeration value 'Down' not handled in switch`。這正是 `enum class` + `switch` + `-Wall` 的好處：漏掉的情況被找出來了。修法：補上 `case Dir::Up: case Dir::Down: return 0;`（上下移動時 x 不變），之後新增列舉值時編譯器也會再提醒。
