# 12. 字串與輸入輸出 (Strings & I/O)

> 程式練習：`C12 成績單解析`、`C11 單字頻率統計`
>
> 先備知識：第 05 課「C 風格字串」、第 11 課「STL」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | std::string | 常用操作、`npos`、數字與字串互轉、中文字的長度問題 |
| 第二部分 | string_view | 不複製的字串「視窗」，以及它的懸空陷阱 |
| 第三部分 | 串流的運作方式 | 緩衝區、`cout` / `cerr`、為什麼 `endl` 慢 |
| 第四部分 | 讀取輸入 | `>>` 的規則、讀到 EOF、串流狀態、`getline` 的陷阱 |
| 第五部分 | stringstream | 切字串、解析一行裡的資料 |
| 第六部分 | 格式化輸出與檔案 | `iomanip`、`printf`、`ifstream` / `ofstream` |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：std::string

## 1.1 string 是什麼

**白話**：C++ 標準函式庫的字串類別，自己管理記憶體、記得自己的長度，可以自動變長（本質上就是 `vector<char>` 加上字串專用的功能）。

```cpp
string s = "hello";
s += " world";            // 自動變長
s.size();                 // 11（O(1)，不像 strlen 要一個一個數）
s[0] = 'H';               // 可以修改
string t = s;             // 深複製（第 06 課）
s == t;                   // 比較內容，不是比較位址
```

## 1.2 常用操作

| 操作 | 說明 | 複雜度 |
|---|---|---|
| `s.size()` / `s.length()` | 長度（一樣） | `O(1)` |
| `s.substr(pos, len)` | 從 `pos` 開始取 `len` 個字元（**第二個參數是長度，不是結束位置**） | `O(len)` |
| `s.find(t)` / `s.find(t, pos)` | 找 `t` 第一次出現的位置；找不到回傳 `string::npos` | `O(n·m)` |
| `s.rfind(t)` | 從後面找 | |
| `s.find_first_of("abc")` | 第一個是 a、b、c 其中之一的位置 | |
| `s.find_first_not_of(' ')` | 第一個不是空白的位置（用來 trim） | |
| `s.insert(pos, t)` / `s.erase(pos, len)` | 插入 / 刪除 | `O(n)` |
| `s.replace(pos, len, t)` | 取代 | `O(n)` |
| `s.push_back(c)` / `s += t` | 附加在後面 | 攤銷 `O(1)` / `O(len(t))` |
| `s.c_str()` | 取得 C 風格字串 `const char*`（給舊的 C 函式用） | `O(1)` |

## 1.3 string::npos

**白話**：「**找不到**」的特殊值，等於 `size_t` 的最大值（`-1` 轉成無號數）。

```cpp
size_t p = s.find("xyz");
if (p == string::npos) cout << "not found";

int q = s.find("xyz");          // ❌ 存進 int 會變成 -1，看起來能用，但……
if (q == string::npos) ...      // 比較時 q 又被轉回無號數 → 碰巧成立。很脆弱，不要這樣寫
if (s.find("x") >= 0) ...       // ❌ 無號數永遠 >= 0，這個條件永遠成立
```

**用 `size_t`（或 `auto`）接 `find` 的回傳值，和 `string::npos` 比較。**

## 1.4 數字與字串互轉

```cpp
string a = to_string(42);          // "42"
string b = to_string(3.14);        // "3.140000"（固定 6 位小數，通常不是你要的格式）

int x = stoi("123");               // 123
long long y = stoll("-9000000000");
double z = stod("2.5");
stoi("12abc");                     // 12：讀到不是數字的地方就停
stoi("abc");                       // ❌ 丟出 invalid_argument 例外
stoi("99999999999");               // ❌ 丟出 out_of_range 例外
```

`C07` 的樣板用 `stoll` 解析分數。

## 1.5 字元的分類 (`<cctype>`)

```cpp
isalpha(c) isdigit(c) isspace(c) isupper(c) islower(c) isalnum(c)
toupper(c) tolower(c)
```

> ⚠️ 參數必須是 `unsigned char` 的範圍或 `EOF`。`char` 可能是負的（第 01 課），直接傳進去是未定義行為：寫 `isalpha((unsigned char)c)`。

數字字元轉數字：`c - '0'`（`'7' - '0' == 7`）；字母的位置：`c - 'a'`。

## 1.6 🔍 中文字與 UTF-8

**白話**：`std::string` 存的是 **byte**，不是「字」。中文字在 UTF-8 編碼中通常佔 **3 個 byte**。

```cpp
string s = "你好";
s.size();          // 6，不是 2
s[0];              // 「你」的第一個 byte，單獨印出來是亂碼
s.substr(0, 1);    // 切到一半，變成亂碼
```

**比喻**：用「格數」量一段文字，英文字母佔 1 格，中文字佔 3 格 —— `size()` 量的是格數，不是字數。

處理中文要用專門的函式庫（例如 ICU），或轉成 `u32string`（每個字元 4 bytes，一個字一個元素）。競賽和本平台的題目都只用 ASCII。

---

# 第二部分：string_view (C++17)

## 2.1 不擁有的字串視窗

**白話**：`string_view` 只記錄「**一個指標 + 一個長度**」，指向別人的字串資料，**不複製、不擁有**。

**比喻**：透過窗戶看外面的風景。你看得到，但風景不是你的；窗戶很便宜，換一扇不用搬動風景。

```cpp
void print_upper(string_view sv) {          // 可以接受 string、"字面值"、char*，都不會複製
    for (char c : sv) cout << (char)toupper((unsigned char)c);
}
print_upper("hello");                        // 不會建立暫時的 string
string s = "world";
print_upper(s);
string_view part = string_view(s).substr(1, 3);   // substr 是 O(1)，不複製
```

## 2.2 懸空陷阱

`string_view` **不延長** 被指向的字串的生命：

```cpp
string_view sv = string("temp");     // ❌ 暫時的 string 在這一行結束時就銷毀了
cout << sv;                          // 懸空：讀到已經釋放的記憶體

string_view get_name() {
    string name = "Alice";
    return name;                     // ❌ 回傳指向區域變數的 view
}
```

**規則**：`string_view` 適合當 **函式參數**（呼叫期間字串一定還活著）；**不要** 拿來當回傳值或存起來，除非你確定原始字串活得比它久。

---

# 第三部分：串流的運作方式

## 3.1 串流 (Stream)

**白話**：資料像 **水流** 一樣，一個字元一個字元地流進來（輸入）或流出去（輸出）。C++ 用同一套介面處理鍵盤、螢幕、檔案、字串。

| 物件 | 型別 | 對應 |
|---|---|---|
| `cin` | `istream` | 標準輸入 |
| `cout` | `ostream` | 標準輸出（有緩衝） |
| `cerr` | `ostream` | 標準錯誤（**沒有緩衝**，立刻輸出） |
| `clog` | `ostream` | 標準錯誤（有緩衝） |
| `ifstream` / `ofstream` | 檔案串流 | 讀 / 寫檔案 |
| `istringstream` / `ostringstream` / `stringstream` | 字串串流 | 從字串讀 / 寫到字串 |

## 3.2 緩衝區 (Buffer) 與 flush

**白話**：`cout` 不會每個字元都立刻寫到螢幕，而是先放進 **緩衝區**，累積夠多了才一次送出（**flush**）。因為每次真正的輸出都很花時間（系統呼叫）。

**比喻**：寄信。每寫一封就跑一趟郵局很浪費時間，先放在信箱裡，滿了再一起寄。

會觸發 flush 的情況：緩衝區滿了、程式正常結束、`endl`、`flush`、讀取 `cin` 之前（因為 `cin.tie(&cout)`）。

```cpp
cout << x << endl;     // 換行 + flush：每一行都跑一趟郵局
cout << x << '\n';     // 只換行，累積起來
```

輸出 10 萬行時，`endl` 可能慢好幾倍到幾十倍。

## 3.3 加速輸入輸出

```cpp
ios::sync_with_stdio(false);   // 不再和 C 的 printf / scanf 同步（之後不要混用 cout 和 printf）
cin.tie(nullptr);              // 讀 cin 之前不用先 flush cout
```

🔍 為什麼 `cerr` 沒有緩衝？錯誤訊息要 **立刻** 顯示 —— 如果程式接下來當掉了，緩衝區裡的訊息就永遠不會出現。所以除錯訊息用 `cerr`（而且評測只比對 `cout`，見 DS 路線第 11 課）。

---

# 第四部分：讀取輸入

## 4.1 `>>` 的規則

**白話**：`cin >> x` 會 **先跳過所有空白**（空格、Tab、換行），然後讀「一個」符合型別的東西，讀到不符合的字元就停下來（那個字元留在串流裡）。

```cpp
int a, b;
cin >> a >> b;      // 輸入 "  3\n\n  4" 也能正確讀到 3 和 4
string s;
cin >> s;           // 只讀到第一個空白之前："Mary Ann" 只會讀到 "Mary"
```

## 4.2 串流狀態 (Stream State)

| 狀態 | 意思 | 檢查 |
|---|---|---|
| good | 一切正常 | `cin.good()` |
| eof | 讀到檔案結尾 | `cin.eof()` |
| fail | 讀取失敗（格式不符，例如要讀 `int` 卻遇到 `abc`） | `cin.fail()` |
| bad | 嚴重錯誤（硬體、串流損壞） | `cin.bad()` |

**一旦進入 fail 狀態，之後所有的讀取都會直接失敗**，直到呼叫 `cin.clear()` 清除狀態。

串流可以直接當成 `bool` 使用：成功是 `true`，失敗是 `false`。

```cpp
int x;
while (cin >> x) sum += x;     // ✅ 讀到 EOF 或格式錯誤時停止

while (!cin.eof()) {           // ❌ 經典錯誤
    cin >> x;                  // 最後一次讀取失敗時，x 沒有被更新，但還是會被加進去
    sum += x;                  //    → 最後一個數字被算兩次
}
```

**規則：用「讀取動作本身」當作迴圈條件。**

## 4.3 getline：讀一整行

```cpp
string line;
getline(cin, line);            // 讀到換行為止（換行被讀掉但不放進 line）
while (getline(cin, line)) { } // 一行一行讀到 EOF
```

## 4.4 ⚠️ `>>` 和 getline 混用的陷阱

```cpp
int n;
cin >> n;                // 輸入 "3\nAlice Smith\n"
string name;
getline(cin, name);      // 😱 name 是空字串！
```

**原因**：`cin >> n` 讀完 `3` 就停了，**換行字元還留在串流裡**。`getline` 一看到換行，就認為這一行結束了，回傳空字串。

```
串流內容：  3 \n A l i c e   S m i t h \n
cin >> n 之後：  ↑ 停在這裡（\n 還沒被讀走）
getline 讀到 \n 就結束 → 空字串
```

**解法**（`C12` 的樣板就是這樣做的）：

```cpp
cin >> n;
cin.ignore(numeric_limits<streamsize>::max(), '\n');   // 丟掉這一行剩下的所有字元（包括換行）
// 或者
string dummy; getline(cin, dummy);
// 或者在 getline 前用 ws 跳過空白（但會連空白行也跳過）
getline(cin >> ws, name);
```

## 4.5 一個字元一個字元讀

```cpp
char c;
cin >> c;              // 會跳過空白
cin.get(c);            // 不跳過空白，連空格和換行都會讀到
while (cin.get(c)) { } // 讀到 EOF（C11 的標準解）
```

## 4.6 🔍 Windows 的換行

Windows 的文字檔換行是 `\r\n`，Linux 是 `\n`。在 Linux 上讀 Windows 產生的檔案，`getline` 讀到的每一行結尾會多一個 `\r`，造成「看起來一樣但比較不相等」的怪 bug。必要時手動去掉：

```cpp
if (!line.empty() && line.back() == '\r') line.pop_back();
```

---

# 第五部分：stringstream

## 5.1 從字串讀資料

**白話**：把一個字串 **當成輸入串流**，就可以用 `>>`、`getline` 從裡面讀東西。

**比喻**：把一張寫滿資料的紙條放進讀卡機，用讀鍵盤的方式來讀它。

```cpp
#include <sstream>
string line = "3 apples 2.5";
istringstream iss(line);
int n; string what; double price;
iss >> n >> what >> price;
```

## 5.2 用分隔符號切字串

```cpp
string csv = "amy, 90, , 80";
stringstream ss(csv);
string field;
while (getline(ss, field, ',')) {     // 第三個參數：分隔字元
    // field 依序是 "amy"、" 90"、" "、" 80"
}
```

⚠️ 細節（`C12` 的 corner case）：
- 欄位前後的空白會保留，要自己 trim。
- 中間的空欄位會讀到空字串。
- **最後如果是分隔符號結尾**（`"a,b,"`），最後那個空欄位 **不會** 被讀到。

## 5.3 組出字串

```cpp
ostringstream oss;
oss << "x = " << x << ", y = " << fixed << setprecision(2) << y;
string result = oss.str();
```

---

# 第六部分：格式化輸出與檔案

## 6.1 iomanip

```cpp
#include <iomanip>
double pi = 3.14159265;
cout << fixed << setprecision(2) << pi;        // 3.14：fixed 時 precision 是「小數點後幾位」
cout << setprecision(3) << pi;                 // 沒有 fixed 時是「總共幾位有效數字」：3.14
cout << setw(8) << 42;                         // "      42"：寬度 8，預設靠右
cout << setw(8) << left << 42;                 // "42      "
cout << setw(5) << setfill('0') << 42;         // "00042"
cout << hex << 255;                            // ff
cout << boolalpha << true;                     // true（而不是 1）
```

| 操作子 | 持續有效？ |
|---|---|
| `fixed`、`setprecision`、`left`、`setfill`、`hex`、`boolalpha` | **持續**，直到被改掉 |
| `setw` | **只對下一個輸出有效** |

## 6.2 🔍 四捨五入的真相

`setprecision(2)` 會「四捨五入」，但浮點數本身不精確：

```cpp
cout << fixed << setprecision(2) << 2.675;   // 2.67，不是 2.68！
```

因為 `2.675` 在二進位中其實是 `2.67499999999999982236431605997495353221893310546875`。
需要精確的十進位（例如金額）時，**用整數存「分」**，不要用浮點數（`C09` 用 `long long` 存金額）。

## 6.3 printf

```cpp
printf("%d %lld %.2f %s %c\n", i, ll, d, s.c_str(), c);
printf("%05d|%-5d|%5d\n", 42, 42, 42);      // 00042|42   |   42
printf("%04d-%02d-%02d\n", y, m, d);         // C03 的日期格式
```

| 格式 | 型別 |
|---|---|
| `%d` / `%lld` | `int` / `long long` |
| `%u` / `%llu` | `unsigned` / `unsigned long long` |
| `%f` / `%.3f` / `%e` | `double`（printf 的 `%f` 對 `float` 和 `double` 都可以） |
| `%s` | C 字串（`string` 要用 `.c_str()`） |
| `%c` | 字元 |

格式和型別不符是 **未定義行為**（例如用 `%d` 印 `long long`）。`-Wall` 會檢查。

C++20 的 `std::format` 結合了兩者的優點：`cout << format("{:.2f} {:>5}", pi, 42);`。

## 6.4 檔案輸入輸出

```cpp
#include <fstream>
ifstream fin("input.txt");
if (!fin) { cerr << "cannot open\n"; return 1; }   // 一定要檢查有沒有開成功
int x;
while (fin >> x) { ... }

ofstream fout("output.txt");             // 預設：覆蓋原本的內容
ofstream flog("log.txt", ios::app);      // 附加在檔案結尾
fout << "result: " << x << '\n';
// 不用手動 close()：fin、fout 離開作用域時解構子會自動關檔（RAII）
```

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 字串 | std::string | 自己管理記憶體的字串類別 | 1.1 |
| 子字串 | substr | 取一段字串（參數是開頭和長度） | 1.2 |
| 找不到 | string::npos | find 失敗的回傳值，size_t 的最大值 | 1.3 |
| 字元編碼 | Character Encoding (UTF-8) | 字元怎麼存成 byte | 1.6 |
| 字串視窗 | string_view | 不擁有、不複製的字串參考 | 2.1 |
| 串流 | Stream | 統一的輸入輸出介面 | 3.1 |
| 緩衝區 | Buffer | 輸出先累積再一次送出 | 3.2 |
| 刷新 | Flush | 立刻送出緩衝區的內容 | 3.2 |
| 串流狀態 | Stream State | good / eof / fail / bad | 4.2 |
| 檔案結尾 | EOF (End of File) | 沒有更多輸入了 | 4.2 |
| 字串串流 | stringstream | 把字串當成串流讀寫 | 5.1 |
| 操作子 | Manipulator | `setw`、`fixed` 等控制格式的東西 | 6.1 |
| 檔案串流 | ifstream / ofstream | 讀 / 寫檔案的串流 | 6.4 |

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

---

# 習題解答

**題 1**：`gram 3 10 1`。`substr(3, 4)` 從索引 3 取 4 個字元 → `"gram"`；第一個 `g` 在索引 3；最後一個在索引 10；找不到 → `true`（印出 1）。

**題 2**：`name` 是 **空字串**。`cin >> n` 讀完 `2` 後，換行字元還在串流裡，`getline` 馬上讀到它就結束了。在 `getline` 前加上 `cin.ignore(numeric_limits<streamsize>::max(), '\n');`。

**題 3**：輸入最後 **有換行** 時（通常都有）會印出 **9**：讀完 `3` 時還沒碰到檔案結尾，eof 還沒被設定，迴圈再跑一次；這次 `cin >> x` 跳過換行後遇到 EOF，**讀取失敗，`x` 沒有被修改**（還是 3），又被加了一次。輸入最後沒有換行時，讀 `3` 的同時就碰到 EOF，結果碰巧是正確的 6 —— 同一個程式，結果取決於輸入檔最後有沒有換行，這就是這種寫法危險的地方。改成 `while (cin >> x) sum += x;`。

**題 4**：`2.2 2.4     7|7|***3`。
- `2.25` 和 `2.35` 的二進位都不精確：`2.25` 剛好可以精確表示，四捨六入五成雙的結果是 `2.2`；`2.35` 實際是 `2.35000000000000008881784197001...`，所以是 `2.4`。（浮點數的「四捨五入」不要靠直覺，見 6.2。）
- `setw(5)` 只對下一個輸出有效，所以第一個 7 前面有 4 個空格，第二個 7 沒有。
- `setfill('*')` 搭配 `setw(4)` → `***3`。

**題 5**：`"hello world"` 被轉成一個 **暫時的 `string`** 傳給 `first_word`，函式回傳後這個暫時物件就銷毀了，`w` 是 **懸空的 `string_view`**。

**題 6**：**三個**：`"a"`、`""`、`"b"`。結尾的逗號後面那個空欄位不會被讀到。

**題 7**：`6`。每個中文字在 UTF-8 裡佔 3 個 byte，`size()` 計算的是 byte 數。

---

# 程式練習

- **`C12 成績單解析`**：`cin >>` 和 `getline` 混用、`getline(ss, field, ',')` 切欄位、trim、空欄位、`fixed << setprecision(2)`。
- **`C11 單字頻率統計`**：`cin.get(c)` 讀到 EOF、`isalpha` / `tolower` 的正確用法。
