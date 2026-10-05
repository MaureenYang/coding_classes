# 12. 字串與輸入輸出 (Strings & I/O)

> 程式練習：`C12 成績單解析`、`C11 單字頻率統計`
>
> 先備知識：第 05 課「C 風格字串」、第 11 課「STL」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | std::string | 每個常用操作的範例、`npos`、數字與字串互轉、字元分類、trim / split、中文字的長度問題 |
| 第二部分 | string_view | 不複製的字串「視窗」，以及它的懸空陷阱 |
| 第三部分 | 串流的運作方式 | 緩衝區、`cout` / `cerr`、為什麼 `endl` 慢 |
| 第四部分 | 讀取輸入 | `>>` 的規則、讀到 EOF、串流狀態與恢復、`getline` 的陷阱、逐字元讀取 |
| 第五部分 | stringstream | 解析一行裡的資料、用分隔符號切字串、組出字串 |
| 第六部分 | 格式化輸出與檔案 | `iomanip` 每個操作子、`printf`、`ifstream` / `ofstream` |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際編譯執行過的結果。標 🔍 的是深入內容。

為了讓範例的輸入是固定的、可以重現，第四部分的很多範例用 `istringstream`（第五部分）代替 `cin` —— 兩者的讀取規則 **完全一樣**，因為它們都是 `istream`。

---

# 第一部分：std::string

## 1.1 string 是什麼

**是什麼**：C++ 標準函式庫的字串類別。自己管理記憶體、記得自己的長度、可以自動變長（本質上就是 `vector<char>` 加上字串專用的功能）。

**為什麼需要**：C 風格字串（`char[]` + `'\0'`，第 05 課）要自己算長度、自己配置記憶體、容易越界。`string` 把這些都處理好了。

| | C 風格字串 `char*` | `std::string` |
|---|---|---|
| 長度 | `strlen`：`O(n)`，一個一個數到 `'\0'` | `size()`：`O(1)` |
| 串接 | `strcat`：要自己確保空間夠 | `+`、`+=`：自動變長 |
| 複製 | `strcpy`：要自己配置 | `=`：自動深複製 |
| 比較 | `strcmp(a, b) == 0` | `a == b` |
| 越界 | 沒有保護 | `at()` 會檢查 |

```cpp
string s = "hello";
s += " world";                      // 自動變長
cout << s << ' ' << s.size() << '\n';   // 輸出：hello world 11
s[0] = 'H';                         // 可以修改
string t = s;                       // 深複製（第 06 課）
t[0] = 'J';
cout << s << " / " << t << '\n';    // 輸出：Hello world / Jello world（互不影響）
cout << (s == "Hello world") << (s < t) << '\n';   // 輸出：11（比較內容；字典序 'H' < 'J'）
```

### 建立字串的方式

```cpp
string a;                    // 空字串
string b = "abc";            // 從字面值
string c(5, '*');            // 5 個 '*'
string d(b, 1);              // 從 b 的索引 1 開始到結尾："bc"
string e("abcdef", 3);       // 字面值的前 3 個字元："abc"
string f = b + "-" + c;      // 串接
cout << '[' << a << "] " << c << ' ' << d << ' ' << e << ' ' << f << '\n';
// 輸出：[] ***** bc abc abc-*****
```

**常見錯誤**：`"abc" + "def"` 不能編譯 —— 兩邊都是 `const char*`，指標不能相加。至少要有一邊是 `string`：`string("abc") + "def"`。

```cpp
// string bad = "abc" + "def";        // ❌ error: invalid operands of types 'const char [4]' and 'const char [4]' to binary 'operator+'
string ok = string("abc") + "def";    // ✅
using namespace std::string_literals;
string ok2 = "abc"s + "def";          // ✅ "abc"s 是 string 字面值（C++14）
```

## 1.2 存取字元

```cpp
string s = "hello";
cout << s[1] << s.at(1) << s.front() << s.back() << '\n';   // 輸出：eeho
```

| 寫法 | 越界時 |
|---|---|
| `s[i]` | 未定義行為（不檢查，最快） |
| `s.at(i)` | 丟出 `out_of_range` |
| `s.front()` / `s.back()` | 空字串時未定義行為 |

```cpp
try { s.at(10); }
catch (const out_of_range& e) { cout << "越界\n"; }    // 輸出：越界
for (char& ch : s) ch = toupper((unsigned char)ch);   // 用參考修改每個字元
cout << s << '\n';                                    // 輸出：HELLO
```

## 1.3 常用操作（每一個都有範例）

| 操作 | 說明 | 複雜度 |
|---|---|---|
| `s.size()` / `s.length()` | 長度（兩個完全一樣） | `O(1)` |
| `s.empty()` | 是否為空字串 | `O(1)` |
| `s.substr(pos, len)` | 從 `pos` 開始取 `len` 個字元（**第二個參數是長度，不是結束位置**） | `O(len)` |
| `s.find(t)` / `s.find(t, pos)` | 找 `t` 第一次出現的位置；找不到回傳 `string::npos` | `O(n·m)` |
| `s.rfind(t)` | 從後面找 | |
| `s.find_first_of("abc")` | 第一個是 a、b、c **其中之一** 的位置 | |
| `s.find_first_not_of(" ")` | 第一個 **不是** 空白的位置（用來 trim） | |
| `s.find_last_not_of(" ")` | 最後一個不是空白的位置 | |
| `s.insert(pos, t)` / `s.erase(pos, len)` | 插入 / 刪除 | `O(n)` |
| `s.replace(pos, len, t)` | 把 `[pos, pos+len)` 換成 `t` | `O(n)` |
| `s.push_back(c)` / `s += t` / `s.append(t)` | 附加在後面 | 攤銷 `O(1)` / `O(len(t))` |
| `s.pop_back()` | 刪除最後一個字元 | `O(1)` |
| `s.compare(t)` | 比較：負數 / 0 / 正數 | `O(n)` |
| `s.c_str()` | 取得 C 風格字串 `const char*`（給舊的 C 函式用） | `O(1)` |

### substr

```cpp
string s = "programming";
//          0123456789A（A = 10）
cout << s.substr(3, 4) << '\n';     // 從 3 開始取 4 個 → 輸出：gram
cout << s.substr(7) << '\n';        // 省略長度：取到結尾 → 輸出：ming
cout << s.substr(8, 100) << '\n';   // 長度超過也沒關係，取到結尾為止 → 輸出：ing
try { s.substr(20); }               // 起點超過 size() → 丟例外
catch (const out_of_range&) { cout << "起點越界\n"; }   // 輸出：起點越界
```

**常見錯誤**：把 `substr(a, b)` 當成「從 a 到 b」。要取 `[a, b)` 這段，要寫 `substr(a, b - a)`。

### find 系列

```cpp
string s = "banana";
cout << s.find("an") << ' '          // 第一次出現 → 1
     << s.find("an", 2) << ' '       // 從索引 2 開始找 → 3
     << s.rfind("an") << ' '         // 最後一次出現 → 3
     << s.find('n') << '\n';         // 也可以找字元 → 2
// 輸出：1 3 3 2

string path = "/home/user/file.txt";
cout << path.substr(path.rfind('/') + 1) << '\n';        // 檔名 → 輸出：file.txt
cout << path.substr(path.rfind('.') + 1) << '\n';        // 副檔名 → 輸出：txt

string expr = "x = 3 + y4";
cout << expr.find_first_of("0123456789") << ' '          // 第一個數字的位置 → 4
     << expr.find_first_not_of("x =") << '\n';           // 第一個不是 'x'、' '、'=' 的位置 → 4
// 輸出：4 4
```

**找出所有出現的位置**：

```cpp
string text = "abcabcabc";
for (size_t p = text.find("bc"); p != string::npos; p = text.find("bc", p + 1))
    cout << p << ' ';
cout << '\n';                        // 輸出：1 4 7
```

### insert、erase、replace

```cpp
string s = "Hello World";
s.insert(5, ",");                    // 在位置 5 插入
cout << s << '\n';                   // 輸出：Hello, World
s.erase(5, 1);                       // 從位置 5 刪除 1 個字元
cout << s << '\n';                   // 輸出：Hello World
s.replace(6, 5, "C++");              // 把 [6, 11) 換成 "C++"
cout << s << '\n';                   // 輸出：Hello C++
s.erase(5);                          // 省略長度：刪到結尾
cout << s << '\n';                   // 輸出：Hello
```

**取代所有出現的子字串**（標準函式庫沒有內建）：

```cpp
string replace_all(string s, const string& from, const string& to) {
    for (size_t p = s.find(from); p != string::npos; p = s.find(from, p + to.size()))
        s.replace(p, from.size(), to);   // 注意下一次從 p + to.size() 開始，避免 to 裡面又含有 from 時無限迴圈
    return s;
}
cout << replace_all("a-b-c", "-", "::") << '\n';   // 輸出：a::b::c
```

### 附加與比較

```cpp
string s = "ab";
s.push_back('c');                    // 加一個字元
s += "de";                           // 加字串
s.append(3, '!');                    // 加 3 個 '!'
cout << s << '\n';                   // 輸出：abcde!!!
s.pop_back();
cout << s << ' ' << s.size() << '\n';     // 輸出：abcde!! 7

string a = "apple", b = "banana";
cout << a.compare(b) << ' ' << b.compare(a) << ' ' << a.compare("apple") << '\n';
// 輸出：-1 1 0（只保證「負 / 零 / 正」，實際數值依實作而定）
cout << (a < b) << (string("Z") < string("a")) << '\n';   // 輸出：11（字典序比較的是字元編碼：'Z' = 90 < 'a' = 97）
```

### c_str：給 C 函式用

```cpp
string name = "data.txt";
FILE* f = fopen(name.c_str(), "w");  // fopen 是 C 函式，只接受 const char*
if (f) fclose(f);
printf("%s\n", name.c_str());        // printf 的 %s 也要 const char* → 輸出：data.txt
```

`c_str()` 回傳的指標在 **字串被修改或銷毀後** 就失效了，不要存起來。

## 1.4 string::npos

**是什麼**：「**找不到**」的特殊值，等於 `size_t` 的最大值（`-1` 轉成無號數）。

```cpp
string s = "hello";
size_t p = s.find("xyz");
cout << (p == string::npos) << '\n';      // 輸出：1
cout << string::npos << '\n';             // 輸出：18446744073709551615
```

**常見錯誤**：

```cpp
int q = s.find("xyz");          // ❌ 存進 int 會變成 -1，看起來能用，但……
if (q == string::npos) { }      // 比較時 q 又被轉回無號數 → 碰巧成立。很脆弱，不要這樣寫

if (s.find("x") >= 0) { }       // ❌ 無號數永遠 >= 0，這個條件永遠成立
if (s.find("h")) { }            // ❌ 找到在位置 0 時是 false；找不到（npos）時反而是 true！
```

**規則**：用 `size_t`（或 `auto`）接 `find` 的回傳值，和 `string::npos` 比較。

```cpp
if (auto pos = s.find("ll"); pos != string::npos)    // C++17 if 初始化：pos 只在 if 裡面有效
    cout << "找到在 " << pos << '\n';                // 輸出：找到在 2
```

## 1.5 數字與字串互轉

### 數字 → 字串

```cpp
cout << to_string(42) << ' ' << to_string(-7) << ' ' << to_string(3.14) << '\n';
// 輸出：42 -7 3.140000
```

`to_string(double)` 固定印 6 位小數，通常不是你要的格式。要控制格式時用 `ostringstream`（5.3 節）。

### 字串 → 數字

| 函式 | 轉成 |
|---|---|
| `stoi(s)` | `int` |
| `stol(s)` / `stoll(s)` | `long` / `long long` |
| `stoul(s)` / `stoull(s)` | `unsigned long` / `unsigned long long` |
| `stof(s)` / `stod(s)` | `float` / `double` |

```cpp
cout << stoi("123") + 1 << ' '              // 輸出：124
     << stoll("-9000000000") << ' '         // 輸出：-9000000000
     << stod("2.5") * 2 << ' '              // 輸出：5
     << stoi("  42") << ' '                 // 開頭的空白會被跳過 → 輸出：42
     << stoi("12abc") << ' '                // 讀到不是數字的地方就停 → 輸出：12
     << stoi("ff", nullptr, 16) << '\n';    // 第三個參數是進位制 → 輸出：255
// 輸出：124 -9000000000 5 42 12 255
```

**失敗時丟例外**：

```cpp
try { stoi("abc"); }
catch (const invalid_argument& e) { cout << "不是數字\n"; }       // 輸出：不是數字
try { stoi("99999999999"); }
catch (const out_of_range& e) { cout << "超出 int 範圍\n"; }      // 輸出：超出 int 範圍
```

**檢查是否「整個字串」都是數字**：第二個參數可以拿到「讀到哪裡停下來」。

```cpp
size_t used;
int v = stoi("12abc", &used);
cout << v << ' ' << used << '\n';           // 輸出：12 2（只用了前 2 個字元）
bool all_digits = (used == string("12abc").size());
cout << all_digits << '\n';                 // 輸出：0
```

`C07` 的樣板用 `stoll` 解析分數。

### 字元和數字

```cpp
char c = '7';
int digit = c - '0';                        // 數字字元轉數字：'7' - '0' == 7
char back = '0' + 3;                        // 數字轉字元：'3'
cout << digit << ' ' << back << ' ' << ('d' - 'a') << '\n';   // 輸出：7 3 3（字母的位置）
```

**常見錯誤**：`int x = '7';` 得到的是 **55**（`'7'` 的 ASCII 編碼），不是 7。

## 1.6 字元的分類 (`<cctype>`)

| 函式 | 判斷 / 作用 |
|---|---|
| `isalpha(c)` | 英文字母 |
| `isdigit(c)` | 數字 `0`~`9` |
| `isalnum(c)` | 字母或數字 |
| `isspace(c)` | 空白（空格、`\t`、`\n`、`\r`……） |
| `isupper(c)` / `islower(c)` | 大寫 / 小寫字母 |
| `ispunct(c)` | 標點符號 |
| `toupper(c)` / `tolower(c)` | 轉大寫 / 小寫（不是字母就原樣回傳） |

```cpp
string s = "Hi, C++ 17!";
int letters = 0, digits = 0, spaces = 0, puncts = 0;
for (char ch : s) {
    unsigned char u = ch;                  // ⚠️ 先轉成 unsigned char（原因見下面）
    if (isalpha(u)) letters++;
    else if (isdigit(u)) digits++;
    else if (isspace(u)) spaces++;
    else if (ispunct(u)) puncts++;
}
cout << letters << ' ' << digits << ' ' << spaces << ' ' << puncts << '\n';   // 輸出：3 2 2 4
cout << (char)toupper('a') << (char)tolower('Q') << (char)toupper('3') << '\n';   // 輸出：Aq3
```

**注意**：`isalpha` 等函式回傳的是 `int`（非 0 代表真，**不一定是 1**），只能拿來當條件，不要寫 `isalpha(c) == 1`。`toupper` 回傳 `int`，印出來之前要轉回 `char`，否則會印出數字。

> ⚠️ 參數必須是 `unsigned char` 的範圍或 `EOF`。`char` 可能是負的（第 01 課：例如中文的 UTF-8 byte），直接傳進去是 **未定義行為**：寫 `isalpha((unsigned char)c)`。

## 1.7 常用的字串處理函式

標準函式庫沒有 `trim`、`split`、`to_lower`，以下是常見的寫法。

### trim：去掉前後空白

```cpp
string trim(const string& s) {
    size_t b = s.find_first_not_of(" \t\r\n");
    if (b == string::npos) return "";          // 全部都是空白
    size_t e = s.find_last_not_of(" \t\r\n");
    return s.substr(b, e - b + 1);
}
cout << '[' << trim("  hello world \n") << "] [" << trim("   ") << "]\n";   // 輸出：[hello world] []
```

### split：用分隔字元切開

```cpp
vector<string> split(const string& s, char delim) {
    vector<string> parts;
    size_t start = 0;
    while (true) {
        size_t p = s.find(delim, start);
        parts.push_back(s.substr(start, p - start));   // p 是 npos 時，取到結尾
        if (p == string::npos) break;
        start = p + 1;
    }
    return parts;
}
for (auto& part : split("a,,b,", ',')) cout << '[' << part << ']';
cout << '\n';                                   // 輸出：[a][][b][]（保留所有空欄位，包括結尾的）
```

（和 5.2 節 `getline` 的切法比較：`getline` 不會產生結尾那個空欄位。）

### 大小寫轉換、反轉、判斷前後綴

```cpp
string s = "Hello";
string lower = s;
transform(lower.begin(), lower.end(), lower.begin(), [](unsigned char ch) { return tolower(ch); });
string rev(s.rbegin(), s.rend());
cout << lower << ' ' << rev << '\n';            // 輸出：hello olleH

string file = "report.pdf";
bool is_pdf = file.size() >= 4 && file.compare(file.size() - 4, 4, ".pdf") == 0;   // 後綴
bool starts = file.rfind("rep", 0) == 0;        // 前綴：只在位置 0 找
cout << is_pdf << starts << '\n';               // 輸出：11
```

（C++20 有 `s.starts_with("rep")`、`s.ends_with(".pdf")`。）

## 1.8 🔍 中文字與 UTF-8

**是什麼**：`std::string` 存的是 **byte**，不是「字」。中文字在 UTF-8 編碼中通常佔 **3 個 byte**。

```cpp
string s = "你好";
cout << s.size() << '\n';               // 輸出：6，不是 2
cout << (int)(unsigned char)s[0] << '\n';   // 「你」的第一個 byte → 輸出：228
string half = s.substr(0, 1);           // 切到一半：只剩一個 byte，印出來是亂碼
string ni = s.substr(0, 3);             // 一個中文字 = 3 個 byte
cout << ni << '\n';                     // 輸出：你
```

**比喻**：用「格數」量一段文字，英文字母佔 1 格，中文字佔 3 格 —— `size()` 量的是格數，不是字數。

處理中文要用專門的函式庫（例如 ICU），或轉成 `u32string`（每個字元 4 bytes，一個字一個元素）。競賽和本平台的題目都只用 ASCII。

---

# 第二部分：string_view (C++17)

## 2.1 不擁有的字串視窗

**是什麼**：`string_view` 只記錄「**一個指標 + 一個長度**」，指向別人的字串資料，**不複製、不擁有**。

**比喻**：透過窗戶看外面的風景。你看得到，但風景不是你的；窗戶很便宜，換一扇不用搬動風景。

**為什麼需要**：函式參數寫 `const string&` 時，傳入字面值 `"hello"` 會 **建立一個暫時的 `string`**（配置記憶體、複製字元）。寫 `string_view` 就完全不用複製。

```cpp
size_t count_vowels(string_view sv) {        // 可以接受 string、"字面值"、char*，都不會複製
    size_t n = 0;
    for (char ch : sv) n += (string_view("aeiou").find(ch) != string_view::npos);
    return n;
}
string word = "education";
const char* cstr = "banana";
cout << count_vowels("hello") << ' ' << count_vowels(word) << ' ' << count_vowels(cstr) << '\n';
// 輸出：2 5 3
```

### string_view 的操作

`string_view` 有大部分 `string` 的 **唯讀** 操作：`size`、`[]`、`substr`、`find`、`compare`、`==`……而且 `substr` 是 `O(1)`（只是調整指標和長度，不複製）。

```cpp
string s = "Hello, World";
string_view sv = s;
string_view hello = sv.substr(0, 5);          // O(1)：不複製
cout << hello << ' ' << hello.size() << '\n'; // 輸出：Hello 5

sv.remove_prefix(7);                          // 視窗往右縮：O(1)
cout << sv << '\n';                           // 輸出：World
sv.remove_suffix(2);                          // 視窗右邊縮
cout << sv << '\n';                           // 輸出：Wor
cout << s << '\n';                            // 原本的字串完全沒變 → 輸出：Hello, World

string owned(hello);                          // 需要擁有一份時，明確轉成 string
```

**`string_view` 不能修改內容**，也 **不保證以 `'\0'` 結尾**（所以不能直接傳給需要 `const char*` 的 C 函式，`string_view` 也沒有 `c_str()`）。

## 2.2 懸空陷阱

`string_view` **不延長** 被指向的字串的生命。原始字串被銷毀後，`string_view` 就指向已經釋放的記憶體（第 05 課的懸置指標）。

```cpp
string_view sv = string("temp");     // ❌ 暫時的 string 在這一行結束時就銷毀了
cout << sv;                          // 懸空：讀到已經釋放的記憶體

string_view get_name() {
    string name = "Alice";
    return name;                     // ❌ 回傳指向區域變數的 view
}

string s = "hello";
string_view v = s;
s += " world, this is a long string";    // ❌ s 重新配置了記憶體，v 還指向舊的位置
```

這些都能編譯，但執行結果是未定義行為（用 `--debug` 執行，AddressSanitizer 會抓到 `heap-use-after-free` 或 `stack-use-after-return`）。

**規則**：
- `string_view` 適合當 **函式參數**（呼叫期間字串一定還活著）。
- **不要** 拿來當回傳值或存成成員變數，除非你確定原始字串活得比它久。
- 原始的 `string` 被修改後，之前的 `string_view` 都視為失效（跟第 11 課的迭代器失效一樣）。

---

# 第三部分：串流的運作方式

## 3.1 串流 (Stream)

**是什麼**：資料像 **水流** 一樣，一個字元一個字元地流進來（輸入）或流出去（輸出）。C++ 用 **同一套介面**（`<<`、`>>`、`getline`）處理鍵盤、螢幕、檔案、字串。

| 物件 | 型別 | 對應 |
|---|---|---|
| `cin` | `istream` | 標準輸入（鍵盤、或評測系統給的輸入檔） |
| `cout` | `ostream` | 標準輸出（有緩衝） |
| `cerr` | `ostream` | 標準錯誤（**沒有緩衝**，立刻輸出） |
| `clog` | `ostream` | 標準錯誤（有緩衝） |
| `ifstream` / `ofstream` | 檔案串流 | 讀 / 寫檔案（6.5 節） |
| `istringstream` / `ostringstream` / `stringstream` | 字串串流 | 從字串讀 / 寫到字串（第五部分） |

**同一個函式可以處理所有種類的串流**（第 08 課的多型）：

```cpp
void write_report(ostream& out) {         // 只依賴 ostream
    out << "total: " << 42 << '\n';
}
write_report(cout);                       // 寫到螢幕 → 輸出：total: 42
ostringstream oss;
write_report(oss);                        // 寫到字串
cout << "[" << oss.str().size() << "]\n"; // 輸出：[10]
// ofstream f("r.txt"); write_report(f);  // 寫到檔案
```

## 3.2 緩衝區 (Buffer) 與 flush

**是什麼**：`cout` 不會每個字元都立刻寫到螢幕，而是先放進 **緩衝區**，累積夠多了才一次送出（**flush**）。因為每次真正的輸出都要請作業系統幫忙（系統呼叫），很花時間。

**比喻**：寄信。每寫一封就跑一趟郵局很浪費時間，先放在信箱裡，滿了再一起寄。

**會觸發 flush 的情況**：
- 緩衝區滿了。
- 程式 **正常** 結束（`main` return 或呼叫 `exit`）。
- 輸出 `endl` 或 `flush`。
- 讀取 `cin` 之前（因為 `cin.tie(&cout)`：確保提示文字先顯示出來）。

```cpp
cout << x << endl;     // 換行 + flush：每一行都跑一趟郵局
cout << x << '\n';     // 只換行，累積起來
cout << flush;         // 只 flush，不換行
```

輸出 10 萬行時，`endl` 可能慢好幾倍到幾十倍。**一般情況用 `'\n'`**。

**程式當掉時，緩衝區的內容會遺失**：

```cpp
cout << "step 1 done";     // 還在緩衝區裡
int* p = nullptr;
*p = 1;                    // 程式當掉（segmentation fault）→ "step 1 done" 永遠不會出現
```

所以用 `cout` 印除錯訊息找當掉的位置，常常會誤判（以為還沒執行到那裡）。**除錯訊息用 `cerr`**（下一節）。

## 3.3 cout 與 cerr

🔍 **為什麼 `cerr` 沒有緩衝？** 錯誤訊息要 **立刻** 顯示 —— 如果程式接下來當掉了，緩衝區裡的訊息就永遠不會出現。

```cpp
cout << "答案：42\n";           // 標準輸出：評測系統比對的是這個
cerr << "debug: i = 3\n";       // 標準錯誤：不會被拿去比對答案
```

它們是 **兩個不同的輸出管道**。在終端機上看起來混在一起，但可以分開導向：`./a.out > out.txt` 只會把 `cout` 寫進檔案，`cerr` 還是顯示在螢幕上。評測系統只比對 `cout`（DS 路線第 11 課），所以除錯訊息用 `cerr` 就不怕忘記刪掉而 WA。

## 3.4 加速輸入輸出

```cpp
ios::sync_with_stdio(false);   // 不再和 C 的 printf / scanf 同步（之後不要混用 cout 和 printf）
cin.tie(nullptr);              // 讀 cin 之前不用先 flush cout
```

**為什麼預設比較慢？**
- `sync_with_stdio(true)`（預設）：為了讓 `cout` 和 `printf` 混用時順序正確，`cout` 的每次輸出都要跟 C 的輸出同步。關掉之後，`cout` 有自己的緩衝區，快很多。
- `cin.tie(&cout)`（預設）：每次讀 `cin` 前都 flush `cout`。互動式程式需要（先看到提示才輸入），但評測時輸入是檔案，不需要。

**關掉同步之後混用的後果**：

```cpp
ios::sync_with_stdio(false);
cout << "A";
printf("B");
cout << "C\n";
// 可能輸出 "BAC" 而不是 "ABC"：兩者各自有緩衝區，誰先 flush 不一定
```

---

# 第四部分：讀取輸入

## 4.1 `>>` 的規則

**是什麼**：`in >> x` 會：
1. **先跳過所有空白**（空格、Tab、換行）。
2. 讀「一個」符合型別的東西。
3. 讀到不符合的字元就停下來（**那個字元留在串流裡**，下一次讀取從它開始）。

```cpp
istringstream in("  3\n\n  4   Mary Ann");
int a, b;
string s1, s2;
in >> a >> b;                       // 空白、換行都被跳過
in >> s1 >> s2;                     // string 只讀到下一個空白之前
cout << a + b << ' ' << s1 << '|' << s2 << '\n';   // 輸出：7 Mary|Ann
```

**讀到不符合的字元就停下來**：

```cpp
istringstream in("12abc 3.5x");
int n; string rest; double d; char c;
in >> n;                            // 讀到 12，遇到 'a' 停下（'a' 留在串流裡）
in >> rest;                         // 從 'a' 開始讀到空白 → "abc"
in >> d >> c;                       // 3.5，然後 'x'
cout << n << ' ' << rest << ' ' << d << ' ' << c << '\n';   // 輸出：12 abc 3.5 x
```

**不同型別的讀法**：

| 型別 | `>>` 讀什麼 |
|---|---|
| `int`、`long long` | 可選的正負號 + 數字 |
| `double` | 數字、小數點、指數（`1e5`） |
| `char` | **一個** 非空白字元（會跳過空白） |
| `string` | 一串非空白字元 |

```cpp
istringstream in("a b  c");
char x, y, z;
in >> x >> y >> z;                  // char 也會跳過空白
cout << x << y << z << '\n';        // 輸出：abc
```

## 4.2 串流狀態 (Stream State)

| 狀態 | 意思 | 檢查 |
|---|---|---|
| good | 一切正常 | `in.good()` |
| eof | 讀到檔案結尾 | `in.eof()` |
| fail | 讀取失敗（格式不符，例如要讀 `int` 卻遇到 `abc`；或讀到 EOF 時沒讀到任何東西） | `in.fail()` |
| bad | 嚴重錯誤（硬體、串流損壞） | `in.bad()` |

**串流可以直接當成 `bool` 使用**：沒有 fail / bad 是 `true`，否則是 `false`。`in >> x` 這個運算式回傳串流本身，所以 `if (in >> x)` 就是「讀取成功了嗎」。

```cpp
istringstream in("10 abc 20");
int x;
in >> x;
cout << x << ' ' << (bool)in << '\n';      // 輸出：10 1
in >> x;                                   // 要讀 int 卻遇到 "abc" → fail
cout << x << ' ' << (bool)in << in.fail() << '\n';   // 輸出：0 01（C++11 起，讀取失敗時 x 被設成 0）
in >> x;                                   // ⚠️ 已經在 fail 狀態：直接失敗，什麼都不讀
cout << (bool)in << '\n';                  // 輸出：0
```

**一旦進入 fail 狀態，之後所有的讀取都會直接失敗**，直到呼叫 `clear()` 清除狀態。

### 從錯誤中恢復

```cpp
istringstream in("10 abc 20");
int x, sum = 0;
while (true) {
    if (in >> x) sum += x;                 // 讀到整數就加
    else if (in.eof()) break;              // 真的讀完了
    else {
        in.clear();                        // 1. 清除 fail 狀態
        string junk;
        in >> junk;                        // 2. 把造成錯誤的東西讀掉（不然下一次又在同一個地方失敗）
        cout << "跳過 " << junk << '\n';   // 輸出：跳過 abc
    }
}
cout << sum << '\n';                       // 輸出：30
```

**常見錯誤**：只 `clear()` 沒有讀掉錯誤的輸入 → 無限迴圈（每次都在 `abc` 那裡失敗）。

## 4.3 讀到 EOF：正確與錯誤的寫法

**正確**：用「讀取動作本身」當作迴圈條件。

```cpp
istringstream in("1 2 3\n");
int x, sum = 0;
while (in >> x) sum += x;          // ✅ 讀到 EOF 或格式錯誤時停止
cout << sum << '\n';               // 輸出：6
```

**經典錯誤**：用 `eof()` 當條件。

```cpp
istringstream in("1 2 3\n");       // 注意：結尾有換行（輸入檔通常都有）
int x, sum = 0;
while (!in.eof()) {                // ❌
    in >> x;                       // 最後一次讀取失敗時，x 沒有被更新（還是 3）
    sum += x;                      //    但還是被加進去了
}
cout << sum << '\n';               // 輸出：9   😱 最後一個數字被算了兩次
```

**為什麼？** `eof` 是在「**嘗試讀取時發現沒有東西了**」才被設定的，不是「下一次讀取會遇到結尾」的預告：

```
讀到 3 之後：串流還剩 "\n"，eof 還沒被設定 → 迴圈繼續
下一次 in >> x：跳過 "\n" 後發現沒東西了 → 設定 eof 和 fail，x 不變（3）
sum += x → 又加了一次 3
```

**規則：用「讀取動作本身」當作迴圈條件**：`while (in >> x)`、`while (getline(in, line))`、`while (in.get(c))`。

### 讀「先給數量」的輸入

```cpp
istringstream in("3\n10 20 30\n");
int n;
in >> n;
vector<int> v(n);
for (int& e : v) in >> e;          // 知道數量就用 for 迴圈
cout << v[2] << '\n';              // 輸出：30
```

## 4.4 getline：讀一整行

**是什麼**：`getline(in, line)` 讀到換行為止（**換行被讀掉，但不放進 `line`**），**不會跳過開頭的空白**。

```cpp
istringstream in("  Alice Smith  \nBob\n\nCarol");
string line;
int n = 0;
while (getline(in, line)) {        // 一行一行讀到 EOF
    cout << ++n << ":[" << line << "]\n";
}
// 輸出：
// 1:[  Alice Smith  ]          ← 前後的空白都保留
// 2:[Bob]
// 3:[]                         ← 空白行讀到空字串
// 4:[Carol]                    ← 最後一行沒有換行也能讀到
```

| | `in >> s` | `getline(in, s)` |
|---|---|---|
| 開頭的空白 | 跳過 | **保留** |
| 讀到哪裡 | 下一個空白之前 | 換行之前 |
| 換行字元 | 留在串流裡 | 讀掉（丟棄） |
| 空白行 | 跳過 | 讀到空字串 |

### 指定其他分隔字元

`getline` 的第三個參數可以指定「讀到哪個字元為止」（預設 `'\n'`）：

```cpp
istringstream in("key=value;next");
string k, v;
getline(in, k, '=');
getline(in, v, ';');
cout << k << " -> " << v << '\n';  // 輸出：key -> value
```

## 4.5 ⚠️ `>>` 和 getline 混用的陷阱

```cpp
istringstream in("3\nAlice Smith\n");
int n;
in >> n;
string name;
getline(in, name);
cout << n << " [" << name << "]\n";      // 輸出：3 []   😱 name 是空字串！
```

**原因**：`in >> n` 讀完 `3` 就停了，**換行字元還留在串流裡**。`getline` 一看到換行，就認為這一行結束了，回傳空字串。

```
串流內容：  3 \n A l i c e   S m i t h \n
in >> n 之後：  ↑ 停在這裡（\n 還沒被讀走）
getline 讀到 \n 就結束 → 空字串
```

**三種解法**（`C12` 的樣板用第一種）：

```cpp
// 解法 1：ignore 丟掉這一行剩下的所有字元（包括換行）
istringstream in1("3\nAlice Smith\n");
int n1; string s1;
in1 >> n1;
in1.ignore(numeric_limits<streamsize>::max(), '\n');   // 最多丟掉「無限多」個字元，直到丟掉一個 '\n'
getline(in1, s1);
cout << '[' << s1 << "]\n";                              // 輸出：[Alice Smith]

// 解法 2：多讀一次 getline，把那一行剩下的部分讀掉
istringstream in2("3\nAlice Smith\n");
int n2; string s2, dummy;
in2 >> n2;
getline(in2, dummy);
getline(in2, s2);
cout << '[' << s2 << "]\n";                              // 輸出：[Alice Smith]

// 解法 3：用 ws 跳過所有空白（包括換行）再 getline
istringstream in3("3\n\n   Alice Smith\n");
int n3; string s3;
in3 >> n3;
getline(in3 >> ws, s3);
cout << '[' << s3 << "]\n";                              // 輸出：[Alice Smith]
```

**解法 3 的副作用**：`ws` 會跳過 **所有** 空白，包括空白行和這一行開頭的空格。如果空白行或開頭空格是有意義的資料，就不能用。

## 4.6 一個字元一個字元讀

```cpp
istringstream in("a b\nc");
char c;
string by_op, by_get;
while (in >> c) by_op += c;              // >> 會跳過空白
cout << by_op << '\n';                   // 輸出：abc

istringstream in2("a b\nc");
while (in2.get(c)) by_get += (c == '\n' ? '/' : c);   // get 不跳過空白，連空格和換行都會讀到
cout << by_get << '\n';                  // 輸出：a b/c
```

`while (cin.get(c))` 是 `C11` 的標準解法：要逐字元處理整份輸入，包括標點和換行。

**其他逐字元操作**：

```cpp
istringstream in("xyz");
cout << (char)in.peek();                 // 偷看下一個字元，但不讀走 → x
in.get(c);                               // 讀走 x
cout << c;                               // x
in.unget();                              // 把剛讀的字元放回去
in.get(c);
cout << c << '\n';                       // 又讀到 x → 輸出：xxx
```

`peek` 常用在「看到下一個字元是什麼，再決定要用什麼方式讀」（例如解析運算式，`C01`）。

## 4.7 🔍 Windows 的換行

Windows 的文字檔換行是 `\r\n`，Linux 是 `\n`。在 Linux 上讀 Windows 產生的檔案，`getline` 讀到的每一行結尾會多一個 `\r`，造成「看起來一樣但比較不相等」的怪 bug：

```cpp
istringstream in("yes\r\nno\r\n");
string line;
getline(in, line);
cout << (line == "yes") << ' ' << line.size() << '\n';   // 輸出：0 4（多了一個看不見的 \r）
if (!line.empty() && line.back() == '\r') line.pop_back();
cout << (line == "yes") << '\n';                          // 輸出：1
```

---

# 第五部分：stringstream

`#include <sstream>`

## 5.1 從字串讀資料：istringstream

**是什麼**：把一個字串 **當成輸入串流**，就可以用 `>>`、`getline` 從裡面讀東西 —— 規則跟讀 `cin` 完全一樣。

**比喻**：把一張寫滿資料的紙條放進讀卡機，用讀鍵盤的方式來讀它。

**為什麼需要**：輸入是「一行一筆資料，但每行的欄位數不固定」時，先用 `getline` 讀一整行，再用 `istringstream` 解析這一行。

```cpp
string line = "3 apples 2.5";
istringstream iss(line);
int n; string what; double price;
iss >> n >> what >> price;
cout << what << ": " << n * price << '\n';      // 輸出：apples: 7.5
```

**每行的數字個數不固定**：

```cpp
istringstream input("1 2 3\n10\n4 5\n");
string row;
while (getline(input, row)) {                   // 先讀一行
    istringstream rs(row);                      // 再把這一行當成串流
    int x, sum = 0, cnt = 0;
    while (rs >> x) { sum += x; cnt++; }        // 讀到這一行結束
    cout << cnt << " 個數，總和 " << sum << '\n';
}
// 輸出：
// 3 個數，總和 6
// 1 個數，總和 10
// 2 個數，總和 9
```

**檢查字串是否「完整」是一個整數**：

```cpp
bool is_int(const string& s) {
    istringstream iss(s);
    int v;
    char extra;
    return (iss >> v) && !(iss >> extra);       // 讀得到整數，而且後面沒有其他非空白字元
}
cout << is_int("42") << is_int(" 42 ") << is_int("42x") << is_int("x") << '\n';   // 輸出：1100
```

## 5.2 用分隔符號切字串

```cpp
string csv = "amy, 90, , 80";
stringstream ss(csv);
string field;
while (getline(ss, field, ',')) {     // 第三個參數：分隔字元
    cout << '[' << field << ']';
}
cout << '\n';                         // 輸出：[amy][ 90][ ][ 80]
```

⚠️ 細節（`C12` 的 corner case）：
- 欄位前後的空白會 **保留**，要自己 trim（1.7 節）。
- 中間的空欄位會讀到空字串（或只有空白的字串）。
- **最後如果是分隔符號結尾**（`"a,b,"`），最後那個空欄位 **不會** 被讀到。

```cpp
for (string s : {"a,b,", ",a", ","}) {
    stringstream ss2(s);
    string f;
    int cnt = 0;
    while (getline(ss2, f, ',')) cnt++;
    cout << '"' << s << "\" → " << cnt << " 個欄位\n";
}
// 輸出：
// "a,b," → 2 個欄位
// ",a" → 2 個欄位
// "," → 1 個欄位
```

需要保留結尾空欄位時，用 1.7 節的 `split`。

## 5.3 組出字串：ostringstream

**是什麼**：把 `<<` 輸出的東西 **收集成一個字串**，而不是印到螢幕上。可以使用所有的格式化操作子（6.1 節）。

```cpp
double y = 2.0 / 3;
ostringstream oss;
oss << "x = " << 42 << ", y = " << fixed << setprecision(2) << y;
string result = oss.str();               // 取出組好的字串
cout << result << " (" << result.size() << " 字元)\n";   // 輸出：x = 42, y = 0.67 (16 字元)
```

**常見用途**：把數字格式化成字串（比 `to_string` 有彈性）。

```cpp
string format_money(long long cents) {
    ostringstream os;
    os << cents / 100 << '.' << setw(2) << setfill('0') << cents % 100;
    return os.str();
}
cout << format_money(12345) << ' ' << format_money(507) << '\n';   // 輸出：123.45 5.07
```

**重複使用 stringstream**：要清空內容用 `ss.str("")`，要清除狀態用 `ss.clear()`，兩個都要。

```cpp
stringstream ss;
ss << 1 << 2;
ss.str("");                              // 清空內容
ss << 3;
cout << ss.str() << '\n';                // 輸出：3
```

---

# 第六部分：格式化輸出與檔案

## 6.1 iomanip：每個操作子

`#include <iomanip>`

**操作子 (manipulator)**：放在 `<<` 中間、用來 **控制格式** 的東西，本身不會輸出任何字元。

### 小數：fixed 與 setprecision

```cpp
double pi = 3.14159265;
cout << pi << '\n';                               // 預設：6 位有效數字 → 輸出：3.14159
cout << setprecision(3) << pi << '\n';            // 沒有 fixed：「總共」3 位有效數字 → 輸出：3.14
cout << fixed << setprecision(3) << pi << '\n';   // 有 fixed：「小數點後」3 位 → 輸出：3.142
cout << 2.0 << '\n';                              // fixed 還在：輸出：2.000
cout << defaultfloat << 2.0 << '\n';              // 恢復預設格式 → 輸出：2
cout << scientific << 12345.678 << '\n';          // 科學記號（precision 還是 3）→ 輸出：1.235e+04
cout << defaultfloat << setprecision(6);          // 恢復
```

| 設定 | `setprecision(n)` 的意思 |
|---|---|
| 預設（`defaultfloat`） | 總共 n 位 **有效數字**（太大太小時自動用科學記號） |
| `fixed` | 小數點後 **n 位** |
| `scientific` | 科學記號，小數點後 n 位 |

**`fixed << setprecision(2)` 是「印到小數點後兩位」的標準寫法**（`C12`）。

### 寬度、對齊、填充

```cpp
cout << '[' << setw(6) << 42 << "]\n";                    // 寬度 6，預設靠右 → 輸出：[    42]
cout << '[' << left << setw(6) << 42 << "]\n";            // 靠左 → 輸出：[42    ]
cout << '[' << right << setw(6) << "ab" << "]\n";         // 字串也可以 → 輸出：[    ab]
cout << '[' << setw(6) << setfill('0') << 42 << "]\n";    // 填充字元 → 輸出：[000042]
cout << setfill(' ');                                     // 恢復
cout << '[' << setw(2) << 12345 << "]\n";                 // 寬度不夠時不會截斷 → 輸出：[12345]
```

**印出對齊的表格**：

```cpp
vector<pair<string, double>> rows = {{"apple", 1.5}, {"watermelon", 12.25}};
for (auto& [name, price] : rows)
    cout << left << setw(12) << name << right << setw(8) << fixed << setprecision(2) << price << '\n';
cout << defaultfloat;
// 輸出：
// apple           1.50
// watermelon     12.25
```

### 進位制、布林、正號

```cpp
cout << hex << 255 << ' ' << oct << 8 << ' ' << dec << 255 << '\n';   // 輸出：ff 10 255
cout << showbase << hex << 255 << dec << noshowbase << '\n';         // 輸出：0xff
cout << boolalpha << true << ' ' << (3 > 5) << noboolalpha << '\n'; // 輸出：true false
cout << showpos << 5 << ' ' << -5 << noshowpos << '\n';              // 輸出：+5 -5
```

### 哪些操作子會一直有效？

| 操作子 | 持續有效？ |
|---|---|
| `fixed`、`setprecision`、`left` / `right`、`setfill`、`hex` / `dec`、`boolalpha`、`showpos` | **持續**，直到被改掉 |
| `setw` | **只對下一個輸出有效** |

```cpp
cout << setw(4) << 1 << 2 << '\n';       // 只有 1 有寬度 → 輸出：   12
cout << hex << 10 << ' ' << 11 << dec << '\n';   // hex 一直有效 → 輸出：a b
```

**常見錯誤**：前面設了 `hex` 或 `fixed` 忘了改回來，後面的輸出全部變成十六進位 / 固定小數。

## 6.2 🔍 四捨五入的真相

`setprecision(2)` 會「四捨五入」，但浮點數本身不精確：

```cpp
cout << fixed << setprecision(2) << 2.675 << ' ' << 1.005 << '\n';   // 輸出：2.67 1.00（不是 2.68、1.01！）
cout << setprecision(20) << 2.675 << '\n';   // 輸出：2.67499999999999982236
cout << defaultfloat << setprecision(6);
```

因為 `2.675` 在二進位中無法精確表示，實際存的值是 `2.67499999999999982236431605997495353221893310546875`，比 2.675 小一點點，四捨五入就變成 2.67。

**需要精確的十進位（例如金額）時，用整數存「分」**，不要用浮點數（`C09` 用 `long long` 存金額，5.3 節的 `format_money`）。

## 6.3 printf

**是什麼**：C 語言的格式化輸出函式（`<cstdio>`）。用 **格式字串** 描述輸出的樣子，`%` 開頭的是「要填入值的位置」。

```cpp
int i = 42; long long ll = 9000000000LL; double d = 3.14159; string s = "hi"; char c = 'Z';
printf("%d %lld %.2f %s %c\n", i, ll, d, s.c_str(), c);   // 輸出：42 9000000000 3.14 hi Z
printf("%05d|%-5d|%5d|\n", 42, 42, 42);                   // 輸出：00042|42   |   42|
printf("%04d-%02d-%02d\n", 2024, 3, 9);                   // C03 的日期格式 → 輸出：2024-03-09
printf("%x %o %e\n", 255, 8, 12345.678);                  // 輸出：ff 10 1.234568e+04
printf("100%%\n");                                        // 印出 % 本身要寫 %% → 輸出：100%
```

| 格式 | 型別 |
|---|---|
| `%d` / `%lld` | `int` / `long long` |
| `%u` / `%llu` | `unsigned` / `unsigned long long` |
| `%zu` | `size_t` |
| `%f` / `%.3f` / `%e` | `double`（printf 的 `%f` 對 `float` 和 `double` 都可以） |
| `%s` | C 字串（`string` 要用 `.c_str()`） |
| `%c` | 字元 |
| `%x` / `%o` | 十六 / 八進位 |

| 修飾 | 意思 | 例子 |
|---|---|---|
| `%5d` | 寬度 5，靠右 | `   42` |
| `%-5d` | 寬度 5，靠左 | `42   ` |
| `%05d` | 寬度 5，補 0 | `00042` |
| `%.2f` | 小數點後 2 位 | `3.14` |

**格式和型別不符是未定義行為**：

```cpp
long long big = 9000000000LL;
// printf("%d\n", big);              // ❌ 用 %d 印 long long：印出錯誤的數字，-Wall 會警告 format '%d' expects argument of type 'int'
// printf("%s\n", s);                // ❌ 傳 string 給 %s：可能當掉。要寫 s.c_str()
```

**cout vs printf**：

| | `cout` | `printf` |
|---|---|---|
| 型別安全 | ✅ 編譯器自動選對的 `<<` | ❌ 格式寫錯是未定義行為 |
| 自訂型別 | ✅ 多載 `<<`（第 07 課） | ❌ |
| 格式化 | 囉唆（`setw`、`setprecision`） | 簡潔 |
| 速度 | 關掉同步後差不多 | 快 |

C++20 的 `std::format` 結合了兩者的優點：`cout << format("{:.2f} {:>5}", pi, 42);`（型別安全 + 簡潔的格式字串）。

## 6.4 scanf（讀取）

`printf` 的讀取版本，參數要傳 **位址**：

```cpp
int a; double b; char word[20];
sscanf("7 2.5 hello", "%d %lf %19s", &a, &b, word);   // sscanf 從字串讀（scanf 從標準輸入讀）
printf("%d %.1f %s\n", a, b, word);                   // 輸出：7 2.5 hello
```

**注意**：`scanf` 讀 `double` 要用 `%lf`（`printf` 用 `%f` 就可以）；讀字串時要限制長度（`%19s`），不然輸入太長會寫出陣列外面。

## 6.5 檔案輸入輸出

`#include <fstream>`

### 寫檔案

```cpp
{
    ofstream fout("/tmp/demo.txt");          // 開啟檔案（預設：覆蓋原本的內容）
    if (!fout) { cerr << "無法開啟\n"; return 1; }
    fout << "3\n";
    fout << "10 20 30\n";
}                                            // 離開作用域時解構子自動關檔（RAII，第 06 課）
```

### 讀檔案

```cpp
ifstream fin("/tmp/demo.txt");
if (!fin) { cerr << "無法開啟\n"; return 1; }   // ⚠️ 一定要檢查有沒有開成功（檔案不存在、沒有權限……）
int n, x, sum = 0;
fin >> n;
while (fin >> x) sum += x;                   // 讀檔案和讀 cin 的寫法完全一樣
cout << n << ' ' << sum << '\n';             // 輸出：3 60
```

**沒檢查就讀**：檔案開啟失敗時，串流一開始就在 fail 狀態，所有讀取都會失敗，變數保持原本的值 —— 程式不會當掉，只是結果莫名其妙，很難找到原因。

### 開啟模式

```cpp
{
    ofstream flog("/tmp/demo.txt", ios::app);    // app：附加在檔案結尾，不覆蓋
    flog << "40\n";
}
ifstream fin2("/tmp/demo.txt");
string line;
int lines = 0;
while (getline(fin2, line)) lines++;
cout << lines << '\n';                       // 輸出：3（原本 2 行 + 附加的 1 行）
```

| 模式 | 意思 |
|---|---|
| `ios::in` | 讀（`ifstream` 預設） |
| `ios::out` | 寫，會清空原本的內容（`ofstream` 預設） |
| `ios::app` | 寫，附加在結尾 |
| `ios::binary` | 二進位模式（不轉換換行字元） |

**不用手動 `close()`**：`fin`、`fout` 離開作用域時解構子會自動關檔。需要在作用域結束前就關掉（例如寫完要馬上讀同一個檔案），才呼叫 `fout.close()`。

### 把輸入導向檔案（除錯小技巧）

```cpp
int main() {
    // freopen("input.txt", "r", stdin);     // 除錯時打開：cin 改從檔案讀，不用每次手動輸入
    int x;
    cin >> x;
}
```

（記得提交前註解掉。本平台的 `judge.py run` 也可以直接指定輸入檔。）

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 字串 | std::string | 自己管理記憶體的字串類別 | 1.1 |
| 子字串 | substr | 取一段字串（參數是開頭和長度） | 1.3 |
| 找不到 | string::npos | find 失敗的回傳值，size_t 的最大值 | 1.4 |
| 字元分類 | Character Classification | isalpha、isdigit 等 | 1.6 |
| 去除空白 | Trim | 去掉前後的空白 | 1.7 |
| 字元編碼 | Character Encoding (UTF-8) | 字元怎麼存成 byte | 1.8 |
| 字串視窗 | string_view | 不擁有、不複製的字串參考 | 2.1 |
| 串流 | Stream | 統一的輸入輸出介面 | 3.1 |
| 緩衝區 | Buffer | 輸出先累積再一次送出 | 3.2 |
| 刷新 | Flush | 立刻送出緩衝區的內容 | 3.2 |
| 標準錯誤 | Standard Error (cerr) | 沒有緩衝、不被評測比對的輸出 | 3.3 |
| 串流狀態 | Stream State | good / eof / fail / bad | 4.2 |
| 檔案結尾 | EOF (End of File) | 沒有更多輸入了 | 4.3 |
| 字串串流 | stringstream | 把字串當成串流讀寫 | 5.1 |
| 操作子 | Manipulator | `setw`、`fixed` 等控制格式的東西 | 6.1 |
| 格式字串 | Format String | printf 的 `"%d %s"` | 6.3 |
| 檔案串流 | ifstream / ofstream | 讀 / 寫檔案的串流 | 6.5 |

---

# 習題

### 題 1：預測輸出

```cpp
string s = "programming";
cout << s.substr(3, 4) << ' ' << s.find('g') << ' ' << s.rfind('g') << ' ' << (s.find("xyz") == string::npos);
```

### 題 2：輸入是下面三行，`name` 讀到什麼？怎麼修？

```
2
Alice Smith
Bob Lee
```

```cpp
int n; cin >> n;
string name; getline(cin, name);
```

### 題 3：找 bug（輸入是 `1 2 3`，想算總和）

```cpp
int x, sum = 0;
while (!cin.eof()) { cin >> x; sum += x; }
cout << sum;
```

（提示：輸入的最後有沒有換行會影響結果。）

### 題 4：預測輸出

```cpp
cout << fixed << setprecision(1) << 2.25 << ' ' << 2.35 << ' ';
cout << setw(5) << 7 << '|' << 7 << '|';
cout << setfill('*') << setw(4) << 3;
```

### 題 5：這段程式有什麼問題？

```cpp
string_view first_word(const string& s) {
    return string_view(s).substr(0, s.find(' '));
}
string_view w = first_word("hello world");
cout << w;
```

### 題 6：`"a,,b,"` 用 `getline(ss, f, ',')` 會切出幾個欄位？各是什麼？

### 題 7：`string s = "台北"; cout << s.size();` 在 UTF-8 環境下印出多少？

### 題 8：預測輸出

```cpp
string s = "Hello World";
s.replace(0, 5, "Hi");
s.insert(s.size(), "!");
s.erase(2, 1);
cout << s << ' ' << s.size() << ' ' << s.find('o');
```

### 題 9：預測輸出

```cpp
istringstream in("5 x 7");
int a = -1, b = -1, c = -1;
in >> a >> b >> c;
cout << a << ' ' << b << ' ' << c << ' ' << in.fail();
```

### 題 10：寫一個函式 `int word_count(const string& line)`，回傳一行裡有幾個「以空白分隔的單字」（多個連續空白、前後空白都要正確處理）。

### 題 11：預測輸出

```cpp
cout << setw(3) << 7 << setw(3) << 8 << 9 << '\n';
cout << hex << 31 << ' ' << 16 << '\n';
cout << 10 << '\n';
```

---

# 習題解答

**題 1**：`gram 3 10 1`。`substr(3, 4)` 從索引 3 取 4 個字元 → `"gram"`；第一個 `g` 在索引 3；最後一個在索引 10；找不到 → `true`（印出 1）。

**題 2**：`name` 是 **空字串**。`cin >> n` 讀完 `2` 後，換行字元還在串流裡，`getline` 馬上讀到它就結束了。在 `getline` 前加上 `cin.ignore(numeric_limits<streamsize>::max(), '\n');`（4.5 節）。

**題 3**：輸入最後 **有換行** 時（通常都有）會印出 **9**：讀完 `3` 時還沒碰到檔案結尾，eof 還沒被設定，迴圈再跑一次；這次 `cin >> x` 跳過換行後遇到 EOF，**讀取失敗，`x` 沒有被修改**（還是 3），又被加了一次。輸入最後沒有換行時，讀 `3` 的同時就碰到 EOF，結果碰巧是正確的 6 —— 同一個程式，結果取決於輸入檔最後有沒有換行，這就是這種寫法危險的地方。改成 `while (cin >> x) sum += x;`。

**題 4**：`2.2 2.4     7|7|***3`。
- `2.25` 剛好可以精確表示，是真正的「一半」，採用四捨六入五成雙的結果是 `2.2`；`2.35` 實際是 `2.35000000000000008881784197001...`，比一半多一點，所以是 `2.4`。（浮點數的「四捨五入」不要靠直覺，見 6.2。）
- `setw(5)` 只對下一個輸出有效，所以第一個 7 前面有 4 個空格，第二個 7 沒有。
- `setfill('*')` 搭配 `setw(4)` → `***3`。

**題 5**：`"hello world"` 被轉成一個 **暫時的 `string`** 傳給 `first_word`，函式回傳後這個暫時物件就銷毀了，`w` 是 **懸空的 `string_view`**。修法：參數改成 `string_view`（字面值本身活到程式結束），或回傳 `string`。

**題 6**：**三個**：`"a"`、`""`、`"b"`。結尾的逗號後面那個空欄位不會被讀到。

**題 7**：`6`。每個中文字在 UTF-8 裡佔 3 個 byte，`size()` 計算的是 byte 數。

**題 8**：`HiWorld! 8 3`。一步一步算：
- `replace(0, 5, "Hi")`：`"Hello"` 換成 `"Hi"` → `"Hi World"`。
- `insert(s.size(), "!")`：加在結尾 → `"Hi World!"`。
- `erase(2, 1)`：刪掉索引 2 的空格 → `"HiWorld!"`。
- `size()` 是 8；`find('o')` 是 `"HiWorld!"` 裡 `o` 的位置 = 3。

**題 9**：`5 0 -1 1`。讀到 `5` 成功；讀 `b` 時遇到 `x` → 失敗，`b` 被設成 0（C++11 起），串流進入 fail 狀態；讀 `c` 時串流已經失敗，什麼都不做，`c` 保持 -1。

**題 10**：用 `istringstream` 讓 `>>` 處理所有空白：

```cpp
int word_count(const string& line) {
    istringstream iss(line);
    string w;
    int n = 0;
    while (iss >> w) n++;
    return n;
}
cout << word_count("  the  quick brown   fox ") << ' ' << word_count("   ") << '\n';   // 輸出：4 0
```

**題 11**：

```
  7  89
1f 10
a
```

- `setw` 只對下一個輸出有效：`7`、`8` 各佔 3 格，`9` 沒有寬度。
- `hex` 持續有效：31 → `1f`，16 → `10`；
- 下一行的 `10` 還是十六進位 → `a`（忘記改回 `dec` 的經典錯誤）。
