# 03. 敘述與控制流程 (Statements & Control Flow)

> 程式練習：`C03 日期計算`
>
> 先備知識：第 02 課的運算式、短路求值。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 敘述的種類 | 運算式敘述、空敘述、區塊，以及「多一個分號」的災難 |
| 第二部分 | if / else | 懸空 else、`=` 和 `==`、else if 的順序、C++17 的 if 初始化 |
| 第三部分 | switch | 跳躍的原理、穿透、case 裡宣告變數的限制 |
| 第四部分 | 迴圈 | 四種迴圈怎麼選、範圍 for 的三種寫法、常見陷阱、迴圈不變量 |
| 第五部分 | 跳躍敘述 | break / continue / return / goto，怎麼跳出多層迴圈 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：...` 是實際執行的結果。標 🔍 的是深入內容。

---

# 第一部分：敘述的種類

## 1.1 敘述 (Statement)

**是什麼**：程式裡 **一個完整的動作 / 指令**，是程式執行的基本單位。

**和運算式的差別**：
- **運算式** 會「**算出一個值**」（`3 + 4`、`x = 5`）。
- **敘述** 是「**做一件事**」，本身沒有值。程式就是一連串的敘述，由上往下執行。

**比喻**：運算式像句子裡的片語（「三加四」）；敘述像一個完整的句子（「把三加四的結果存起來。」），句號就是分號。

C++ 的敘述分成這幾種，每一種的範例：

| 種類 | 說明 | 例子 |
|---|---|---|
| 運算式敘述 | 運算式 + 分號 | `x = 5;`、`f();`、`i++;` |
| 宣告敘述 | 宣告變數 | `int x = 5;`、`string s;` |
| 複合敘述 / 區塊 | 用 `{ }` 包起來的一群敘述 | `{ int t = a; a = b; b = t; }` |
| 選擇敘述 | 依條件選擇要執行的程式碼 | `if`、`switch` |
| 迴圈敘述 | 重複執行 | `while`、`do-while`、`for` |
| 跳躍敘述 | 改變執行的位置 | `break`、`continue`、`return`、`goto` |
| 空敘述 | 只有分號，什麼都不做 | `;` |

```cpp
int a = 3, b = 7;                 // 宣告敘述
a = a + b;                        // 運算式敘述
{                                 // 區塊：把三個敘述包成一個
    int t = a;
    a = b;
    b = t;
}
if (a > b) cout << "a\n";         // 選擇敘述
else cout << "b\n";               // 輸出：b（交換後 a = 7、b = 10）
for (int i = 0; i < 2; i++)       // 迴圈敘述
    cout << i;                    // 輸出：01
cout << '\n';
```

## 1.2 區塊 (Block / Compound Statement)

**是什麼**：用 `{ }` 把好幾個敘述包起來，**在語法上當作一個敘述**。

**為什麼需要**：`if`、`for`、`while` 的語法規定後面 **只能接一個敘述**。要做好幾件事，就要用區塊把它們包成一個：

```cpp
int score = 95;
// ❌ 沒有大括號：if 只控制「下一個敘述」
if (score >= 90)
    cout << "Excellent! ";
    cout << "Bonus!\n";           // 這行不屬於 if，永遠會執行（縮排會騙人）

// ✅ 有大括號：兩行都受 if 控制
if (score >= 90) {
    cout << "Excellent! ";
    cout << "Bonus!\n";
}
```

**區塊也是一個新的作用域**：在裡面宣告的變數，出了 `}` 就消失了（第 01 課 4.1）。

```cpp
int x = 1;
{
    int y = 2;                    // y 只在這個區塊裡
    cout << x + y << '\n';        // 輸出：3
}
// cout << y;                     // ❌ 編譯錯誤：y 已經不存在
```

🔍 **區塊結束時，裡面的物件會依照「建立的相反順序」被解構**。這是 RAII（第 06 課）的基礎：

```cpp
struct T { char c; T(char x) : c(x) { cout << "+" << c << ' '; } ~T() { cout << "-" << c << ' '; } };
{
    T a('a');
    T b('b');
}                                 // 輸出：+a +b -b -a
```

**建議**：`if`、`for`、`while` 後面 **永遠加大括號**，就算只有一行。之後要加第二行時不會出錯。

## 1.3 空敘述 (Null Statement) 與多餘的分號

**是什麼**：只有一個分號 `;` 的敘述，什麼都不做。

**合理的用途**（很少）：迴圈的工作全部在條件裡做完了。

```cpp
const char* s = "hello";
int len = 0;
while (s[len] != '\0') len++;     // 一般寫法
int len2 = 0;
while (s[len2++] != '\0');        // 空敘述當迴圈本體：所有工作都在條件裡（不好讀，不推薦）
cout << len << ' ' << len2 - 1 << '\n';   // 輸出：5 5
```

**最危險的 bug：多打一個分號**

**例 1：if 後面多了分號**

```cpp
int x = 5;
if (x > 100);                     // ← 多了一個分號！if 控制的是「空敘述」
{
    cout << "too big\n";          // 這個區塊跟 if 無關，永遠會執行
}
// 輸出：too big（x 明明只有 5）
```

**例 2：for 後面多了分號**

```cpp
int sum = 0;
for (int i = 1; i <= 3; i++);     // ← 迴圈本體是空敘述，跑 3 次什麼都沒做
{
    sum += 10;                    // 只執行一次
}
cout << sum << '\n';              // 輸出：10（以為是 30）
```

**例 3：while 後面多了分號 → 無窮迴圈**

```cpp
int n = 3;
while (n > 0);                    // ← 空敘述，n 永遠不會變，程式卡住（TLE）
{
    n--;
}
```

**怎麼避免**：編譯時加 `-Wall -Wextra`，會出現 `suggest braces around empty body in an 'if' statement` 之類的警告。另外，左大括號 `{` 和 `if` / `for` 寫在同一行，比較不容易出這種錯。

---

# 第二部分：if / else

## 2.1 if 的三種形式

```cpp
int t = 28;

// 形式 1：只有 if
if (t > 30) cout << "hot\n";

// 形式 2：if-else
if (t > 25) cout << "warm\n";     // 輸出：warm
else cout << "cool\n";

// 形式 3：else if 鏈
if (t > 30) cout << "hot\n";
else if (t > 20) cout << "nice\n";   // 輸出：nice
else if (t > 10) cout << "cool\n";
else cout << "cold\n";
```

**條件會被轉成 `bool`**：0、`nullptr` 是 `false`，其他是 `true`（第 02 課 5.3）。

## 2.2 經典 bug：`=` 寫成 `==`

```cpp
int x = 0;
if (x = 5) cout << "x is 5\n";    // ❌ 不是比較！是把 5 指定給 x，運算式的值是 5 → true
cout << x << '\n';                // 輸出：x is 5 和 5（x 被改掉了）

int y = 0;
if (y = 0) cout << "never\n";     // ❌ 指定成 0，值是 0 → false，永遠不會執行
```

**怎麼避免**：
- `-Wall` 會警告 `suggest parentheses around assignment used as truth value`。
- 如果是故意的（例如 `while ((c = getchar()) != EOF)`），加上括號並和某個值比較，意圖會更清楚。

## 2.3 懸空 else (Dangling Else)

**規則**：`else` 永遠跟 **最近的、還沒配對的 `if`** 配對，**跟縮排完全無關**。

```cpp
int a = 5, b = -1;
if (a > 0)
    if (b > 0)
        cout << "both positive\n";
else                                  // 縮排看起來屬於外層的 if (a > 0)
    cout << "a is not positive\n";    // 實際上屬於內層的 if (b > 0)！
// 輸出：a is not positive（但 a 明明是 5）
```

編譯器的理解：

```cpp
if (a > 0) {
    if (b > 0) cout << "both positive\n";
    else cout << "a is not positive\n";    // a > 0 而且 b <= 0 時執行
}
```

**比喻**：文章裡的「他」指的是 **最近提到的那個人**，不管你心裡想的是誰。

**解法**：**加大括號** 讓配對明確：

```cpp
if (a > 0) {
    if (b > 0) cout << "both positive\n";
} else {
    cout << "a is not positive\n";          // 現在真的屬於外層
}
// 輸出：（什麼都不印）
```

`-Wall` 會警告 `suggest explicit braces to avoid ambiguous 'else'`。

## 2.4 else if 鏈的順序

**規則**：條件 **由上往下** 檢查，**第一個成立的就執行，後面的全部跳過**。

所以範圍判斷時，**條件要從嚴格排到寬鬆**：

```cpp
int score = 95;

// ❌ 順序錯誤：第一個條件太寬鬆，攔下了所有 >= 60 的人
if (score >= 60) cout << "pass\n";            // 輸出：pass
else if (score >= 90) cout << "excellent\n";  // 永遠不會執行到
else cout << "fail\n";

// ✅ 從嚴格到寬鬆
if (score >= 90) cout << "excellent\n";       // 輸出：excellent
else if (score >= 60) cout << "pass\n";
else cout << "fail\n";
```

🔍 `else if` 其實不是特殊語法，它是「`else` 後面接了一個 `if` 敘述」：

```cpp
if (A) x();
else if (B) y();
else z();
// 等同於
if (A) x();
else {
    if (B) y();
    else z();
}
```

## 2.5 用 && 合併條件，減少巢狀

```cpp
int age = 25;
bool has_ticket = true, is_vip = false;

// 巢狀：越來越往右縮，不好讀
if (age >= 18) {
    if (has_ticket) {
        if (!is_vip) cout << "general admission\n";
    }
}
// 合併：一行看完
if (age >= 18 && has_ticket && !is_vip) cout << "general admission\n";   // 輸出：general admission
```

**提早返回 (early return)**：在函式開頭先處理「不合格」的情況，主要邏輯就不用縮排好幾層：

```cpp
string check(int age, bool ticket) {
    if (age < 18) return "too young";
    if (!ticket) return "no ticket";
    return "welcome";                       // 主要邏輯在最外層
}
cout << check(15, true) << ' ' << check(20, false) << ' ' << check(20, true) << '\n';
// 輸出：too young no ticket welcome
```

## 2.6 C++17：if 帶初始化 (if with Initializer)

**語法**：`if (初始化; 條件)`

**為什麼需要**：有些變數 **只為了這個 if 而存在**，用完就不需要了。放在 if 裡面，它的作用域就只在 `if` / `else` 裡，不會污染外面。

**例 1：map 查詢**（最常見）

```cpp
map<string, int> ages = {{"amy", 20}, {"bob", 25}};

// 舊寫法：it 在 if 之後還存在
auto it = ages.find("amy");
if (it != ages.end()) cout << it->second << '\n';

// C++17：it2 只在 if / else 裡
if (auto it2 = ages.find("bob"); it2 != ages.end()) {
    cout << "found " << it2->second << '\n';     // 輸出：found 25
} else {
    cout << "not found\n";                       // else 裡也能用 it2
}
// cout << it2->second;                          // ❌ 編譯錯誤：it2 已經不存在
```

**例 2：計算一次、用兩次**

```cpp
int a = 17, b = 5;
if (int r = a % b; r != 0) cout << "餘數 " << r << '\n';   // 輸出：餘數 2
```

**例 3：switch 也可以**

```cpp
switch (int d = a / b; d) {
    case 3: cout << "three\n"; break;              // 輸出：three
    default: cout << d << '\n';
}
```

---

# 第三部分：switch

## 3.1 switch 的基本規則

**是什麼**：根據一個 **整數（或字元、列舉）** 的值，**直接跳到** 對應的 `case` 開始執行。

```cpp
char op = '*';
int a = 6, b = 3, r = 0;
switch (op) {
    case '+': r = a + b; break;
    case '-': r = a - b; break;
    case '*': r = a * b; break;
    case '/': r = a / b; break;
    default:  cout << "unknown op\n"; break;
}
cout << r << '\n';               // 輸出：18
```

**比喻**：大樓的電梯。按下樓層號碼（`case`），電梯 **直接** 到那一層，不會一層一層停下來問「是這層嗎？」

| 規則 | 說明 | 範例 |
|---|---|---|
| 條件的型別 | 整數、`char`、`bool`、`enum` | ✅ `switch (n)`、`switch (c)` |
| 不能用的型別 | `string`、`double`、指標 | ❌ `switch (s)`、`switch (3.5)` |
| `case` 的值 | 必須是 **編譯期常數** | ✅ `case 3:`、`case 'a':`、`case MAX:`（`constexpr`） |
| `case` 不能重複 | 同一個值只能出現一次 | ❌ 兩個 `case 1:` |
| `default` | 沒有任何 case 符合時執行 | 可以省略；可以放在任何位置 |

不能用的情況的範例：

```cpp
string cmd = "add";
// switch (cmd) { case "add": ... }   // ❌ error: switch quantity not an integer

int limit = 10;
// switch (x) { case limit: ... }     // ❌ limit 不是編譯期常數
constexpr int LIMIT = 10;
switch (10) { case LIMIT: cout << "ok\n"; break; }   // ✅ constexpr 可以 → 輸出：ok
```

**字串怎麼辦？** 用 `if-else` 鏈，或用 `map` 把字串對應到動作：

```cpp
map<string, int> code = {{"add", 1}, {"sub", 2}};
switch (code[cmd]) {               // 先把字串轉成整數
    case 1: cout << "adding\n"; break;     // 輸出：adding
    case 2: cout << "subtracting\n"; break;
    default: cout << "unknown\n";
}
```

## 3.2 穿透 (Fall-through)

**規則**：`case` 只是一個 **進入點（標籤）**，不是邊界。執行完一個 case 的程式碼，如果 **沒有 `break`**，會 **繼續往下執行下一個 case 的程式碼**，直到遇到 `break` 或 switch 結束。

**比喻**：電梯停在 5 樓之後，如果你沒有出電梯（`break`），它會繼續往下一層一層停，每一層的東西都會被執行。

**例 1：忘記 break（bug）**

```cpp
int level = 2;
switch (level) {
    case 1: cout << "easy ";
    case 2: cout << "medium ";        // 從這裡進入
    case 3: cout << "hard ";          // 沒有 break → 繼續執行
    default: cout << "?";              // 沒有 break → 繼續執行
}
cout << '\n';
// 輸出：medium hard ?
```

**例 2：故意穿透 —— 多個 case 共用同一段程式碼**（`C03` 的標準解）

```cpp
int days_in_month(int m, bool leap) {
    switch (m) {
        case 2:
            return leap ? 29 : 28;
        case 4: case 6: case 9: case 11:   // 四個 case 都穿透到同一行
            return 30;
        default:
            return 31;
    }
}
cout << days_in_month(2, true) << ' ' << days_in_month(9, false) << ' ' << days_in_month(12, false) << '\n';
// 輸出：29 30 31
```

這裡用 `return` 代替 `break`（`return` 直接離開整個函式，當然也離開了 switch）。

**例 3：故意穿透 —— 累積的效果**

```cpp
int membership = 3;      // 3 = 金卡、2 = 銀卡、1 = 普卡
cout << "優惠：";
switch (membership) {
    case 3: cout << "貴賓室 ";
        [[fallthrough]];               // C++17：告訴讀者和編譯器「這是故意的」
    case 2: cout << "免運費 ";
        [[fallthrough]];
    case 1: cout << "生日禮";
}
cout << '\n';
// 輸出：優惠：貴賓室 免運費 生日禮
```

加上 `[[fallthrough]];`，編譯時的 `-Wimplicit-fallthrough` 就不會警告；而且讀程式的人一看就知道不是忘了寫 `break`。

## 3.3 🔍 case 裡宣告變數

**問題**：所有的 `case` 共用 **同一個作用域**（整個 switch 的大括號）。如果在某個 case 裡宣告並初始化一個變數，跳到 **後面的 case** 時，這個變數「已經在作用域裡，但初始化被跳過了」—— C++ 禁止這種情況。

```cpp
int x = 2;
switch (x) {
    case 1:
        int y = 10;             // y 的作用域延伸到 switch 結尾
        cout << y;
        break;
    case 2:                     // ❌ error: jump to case label crosses initialization of 'int y'
        cout << "two";
        break;
}
```

**解法**：用大括號把 case 的內容包成一個區塊，`y` 的作用域就只在那個區塊裡：

```cpp
switch (x) {
    case 1: {
        int y = 10;
        cout << y << '\n';
        break;
    }
    case 2: {
        cout << "two\n";         // 輸出：two
        break;
    }
}
```

## 3.4 switch vs if-else

| | `switch` | `if-else` 鏈 |
|---|---|---|
| 適合 | 一個值對應 **很多個固定的選項** | 範圍判斷、複雜條件、字串 |
| 速度 | 編譯器可能做成 **跳躍表**，`O(1)` 直接跳 | 一個一個檢查 |
| 能比較 | 整數、字元、列舉的 **相等** | 任何條件 |
| 可讀性 | 選項很多時很清楚 | 選項很多時很長 |

同一個需求的兩種寫法：

```cpp
int day = 6;
// switch：適合「一個值對應一個結果」
switch (day) {
    case 0: case 6: cout << "weekend\n"; break;     // 輸出：weekend
    default: cout << "weekday\n";
}
// if-else：適合範圍
int hour = 14;
if (hour < 12) cout << "morning\n";
else if (hour < 18) cout << "afternoon\n";          // 輸出：afternoon
else cout << "evening\n";
```

🔍 **跳躍表 (jump table)**：當 case 的值很密集（例如 0 ~ 10），編譯器會建立一個陣列，存放每個 case 的程式碼位址，直接用 `表[x]` 跳過去，不需要一個一個比較。

---

# 第四部分：迴圈

## 4.1 四種迴圈

| 迴圈 | 什麼時候用 | 至少執行一次？ |
|---|---|---|
| `while (條件) { }` | 不知道要跑幾次，條件滿足就繼續 | 否 |
| `do { } while (條件);` | **至少要做一次**，做完再檢查 | **是** |
| `for (初始化; 條件; 更新) { }` | 計數、已知的範圍 | 否 |
| `for (宣告 : 範圍) { }` | 走過容器 / 陣列的每個元素 | 否 |

**while：不知道要跑幾次**

```cpp
// 計算一個數是 2 的幾次方以內
int n = 100, k = 0;
while ((1 << k) < n) k++;       // 條件一開始就不成立的話，一次都不會執行
cout << k << '\n';              // 輸出：7（2⁷ = 128 >= 100）

// 數字的各位數字和
int num = 9472, digit_sum = 0;
while (num > 0) {
    digit_sum += num % 10;      // 取最後一位
    num /= 10;                  // 去掉最後一位
}
cout << digit_sum << '\n';      // 輸出：22（9 + 4 + 7 + 2）
```

**do-while：至少執行一次**

```cpp
// 把數字反過來：就算 n 是 0，也要處理一次（印出 0）
int n2 = 0, rev = 0;
do {
    rev = rev * 10 + n2 % 10;
    n2 /= 10;
} while (n2 > 0);
cout << rev << '\n';            // 輸出：0
// 如果用 while (n2 > 0)，n2 是 0 時迴圈一次都不執行 —— 這時剛好也是 0，但處理「位數」時就會差一位
```

```cpp
// 典型用途：先讀輸入再檢查
int x;
do {
    cout << "請輸入 1~10：";
    cin >> x;
} while (x < 1 || x > 10);      // 注意結尾的分號
```

**for：已知範圍的計數**

```cpp
for (int i = 1; i <= 5; i++) cout << i * i << ' ';    // 輸出：1 4 9 16 25
cout << '\n';
for (int i = 10; i > 0; i -= 3) cout << i << ' ';     // 輸出：10 7 4 1
cout << '\n';
```

**範圍 for：走過每個元素**

```cpp
vector<string> fruits = {"apple", "banana", "cherry"};
for (const string& f : fruits) cout << f[0];          // 輸出：abc
cout << '\n';
int arr[] = {3, 1, 4};
for (int x : arr) cout << x;                          // 內建陣列也可以 → 輸出：314
cout << '\n';
for (int x : {2, 7, 1, 8}) cout << x;                 // 直接寫一串值 → 輸出：2718
cout << '\n';
```

## 4.2 for 迴圈的三個部分

```cpp
for (int i = 0; i < n; i++) { 本體 }
//   ① 初始化    ② 條件   ③ 更新
```

**執行順序**：① → ② →（本體）→ ③ → ② →（本體）→ ③ → …… → ② 不成立就結束。

用一個會印出每一步的程式觀察：

```cpp
int i;
for (i = 0, cout << "init "; cout << "check(" << i << ") ", i < 2; cout << "update ", i++)
    cout << "body ";
cout << '\n';
// 輸出：init check(0) body update check(1) body update check(2)
```

注意：最後一次 `check(2)` 失敗後就離開了，**更新部分總共執行 2 次、條件檢查執行 3 次**。

**三個部分的各種寫法**：

```cpp
// 1. 三個部分都可以省略：無窮迴圈（要在裡面 break）
int cnt = 0;
for (;;) {
    if (++cnt == 3) break;
}
cout << cnt << '\n';                                   // 輸出：3

// 2. 用逗號宣告多個變數、做多個更新：雙指標
string s = "racecar";
bool palindrome = true;
for (int i = 0, j = (int)s.size() - 1; i < j; i++, j--) {
    if (s[i] != s[j]) { palindrome = false; break; }
}
cout << palindrome << '\n';                            // 輸出：1

// 3. 初始化的變數只在迴圈裡有效
for (int k = 0; k < 1; k++) { }
// cout << k;                                          // ❌ k 已經不存在

// 4. 迴圈結束後還要用計數器：宣告在外面
int idx;
vector<int> v = {5, 8, 2, 9};
for (idx = 0; idx < (int)v.size(); idx++)
    if (v[idx] == 2) break;
cout << idx << '\n';                                   // 輸出：2（找到的位置）
```

## 4.3 範圍 for (Range-based for)

**三種寫法，效果完全不同**：

| 寫法 | 迴圈變數是 | 能修改原本的元素？ | 會複製元素？ |
|---|---|---|---|
| `for (auto x : v)` | 複製品 | ❌（改的是複製品） | ✅ 每個都複製 |
| `for (auto& x : v)` | 參考 | ✅ | ❌ |
| `for (const auto& x : v)` | 唯讀參考 | ❌（編譯錯誤） | ❌ |

```cpp
vector<int> v = {1, 2, 3};

for (auto x : v) x *= 10;          // 改的是複製品
for (int x : v) cout << x << ' ';  // 輸出：1 2 3（沒變）
cout << '\n';

for (auto& x : v) x *= 10;         // 改的是 v 裡的元素
for (int x : v) cout << x << ' ';  // 輸出：10 20 30
cout << '\n';

for (const auto& x : v) {
    // x *= 2;                     // ❌ 編譯錯誤：x 是 const
    cout << x << ' ';              // 輸出：10 20 30
}
cout << '\n';
```

**為什麼大物件要用 `const auto&`**：

```cpp
vector<string> names(100000, string(1000, 'a'));   // 十萬個、每個 1000 字元的字串
for (auto s : names) { }           // 每次都複製一個 1000 字元的字串：總共複製 1 億個字元
for (const auto& s : names) { }    // 完全不複製
```

**選擇口訣**：
- 要修改元素 → `auto&`
- 只讀、元素很大（`string`、`vector`、自訂類別）→ `const auto&`
- 只讀、元素很小（`int`、`char`、`double`）→ `auto`（複製很便宜）

**搭配結構化綁定（C++17）走訪 map**：

```cpp
map<string, int> stock = {{"apple", 5}, {"pear", 0}};
for (auto& [name, qty] : stock) qty += 10;            // 修改數量
for (const auto& [name, qty] : stock) cout << name << '=' << qty << ' ';
cout << '\n';                                          // 輸出：apple=15 pear=10
```

> ⚠️ **範圍 for 的迴圈中，不要對同一個容器 `push_back` / `erase` / `insert`**。範圍 for 內部用的是迭代器，容器改變大小後迭代器會失效（未定義行為，第 11 課）。

```cpp
vector<int> w = {1, 2, 3};
// for (int x : w) w.push_back(x);   // ❌ 未定義行為：可能當掉、可能跑不停
```

## 4.4 迴圈常見的陷阱

### 陷阱 1：差一錯誤 (Off-by-one Error)

**是什麼**：迴圈多跑一次或少跑一次。最常見的迴圈 bug。

```cpp
int a[5] = {1, 2, 3, 4, 5};
int s1 = 0;
for (int i = 0; i <= 5; i++) s1 += a[i];   // ❌ 多跑一次：a[5] 越界（未定義行為）

int s2 = 0;
for (int i = 1; i < 5; i++) s2 += a[i];    // ❌ 少算了 a[0]
cout << s2 << '\n';                        // 輸出：14（應該是 15）

int s3 = 0;
for (int i = 0; i < 5; i++) s3 += a[i];    // ✅
cout << s3 << '\n';                        // 輸出：15
```

**檢查方法**：寫迴圈前先問三個問題：**第一次是多少？最後一次是多少？總共幾次？**
- `for (int i = 0; i < n; i++)`：0 到 n-1，共 n 次。
- `for (int i = 1; i <= n; i++)`：1 到 n，共 n 次。
- `for (int i = a; i < b; i++)`：共 b - a 次。

### 陷阱 2：無號數倒數 → 無窮迴圈

```cpp
vector<int> v = {1, 2, 3};
// for (size_t i = v.size() - 1; i >= 0; i--)   // ❌ i 是無號數，永遠 >= 0
//     cout << v[i];                           //    i 從 0 再減 1 → 變成超大的數 → v[i] 越界

for (int i = (int)v.size() - 1; i >= 0; i--)   // ✅ 方法 1：用有號數
    cout << v[i];
cout << '\n';                                   // 輸出：321

for (size_t i = v.size(); i-- > 0; )            // ✅ 方法 2：先比較、再減（慣用寫法）
    cout << v[i];
cout << '\n';                                   // 輸出：321

for (auto it = v.rbegin(); it != v.rend(); ++it)   // ✅ 方法 3：反向迭代器
    cout << *it;
cout << '\n';                                   // 輸出：321
```

而且 `v` 是空的時候，`v.size() - 1` 本身就已經是超大的數了。

### 陷阱 3：用浮點數當計數器

```cpp
int count = 0;
for (double x = 0; x != 1.0; x += 0.1) {        // ❌ 0.1 加 10 次不會剛好等於 1.0
    if (++count > 20) break;                    //    → 沒有這行就是無窮迴圈
}
cout << count << '\n';                          // 輸出：21（停不下來，被強制 break）

for (int i = 0; i <= 10; i++) {                 // ✅ 用整數計數，再換算成小數
    double x = i * 0.1;
    (void)x;
}
```

### 陷阱 4：迴圈條件裡有昂貴的計算

```cpp
const char* text = "hello world";
for (size_t i = 0; i < strlen(text); i++) { }   // ❌ strlen 每次都從頭數一遍，整個迴圈變 O(n²)
size_t len = strlen(text);
for (size_t i = 0; i < len; i++) { }            // ✅ 只算一次
```

（`v.size()`、`s.size()` 是 `O(1)`，放在條件裡沒關係。）

### 陷阱 5：在迴圈裡修改迴圈變數

```cpp
for (int i = 0; i < 10; i++) {
    if (i % 2 == 0) i++;          // ⚠️ 迴圈變數被改了兩次，很難看出實際跑了哪些 i
    cout << i << ' ';
}
cout << '\n';                     // 輸出：1 3 5 7 9
```

能跑，但讀的人很容易搞錯。需要跳著走時，直接寫在更新部分：`for (int i = 1; i < 10; i += 2)`。

## 4.5 🔍 迴圈不變量 (Loop Invariant)

**是什麼**：一個在 **每一次迴圈開始時都成立** 的條件。用它來確認迴圈寫得對。

**證明迴圈正確的三步驟**：
1. **初始化**：第一次進入迴圈前，不變量成立。
2. **保持**：如果某一次開始時成立，執行完本體後（下一次開始時）還是成立。
3. **結束**：迴圈結束時，不變量 + 結束條件 = 我們想要的結果。

**例 1：求和**

```cpp
// 不變量：每次迴圈開始時，sum == a[0] + a[1] + ... + a[i-1]
int a[] = {3, 1, 4, 1, 5};
int n = 5, sum = 0;
for (int i = 0; i < n; i++) sum += a[i];
// 初始化：i = 0，sum = 0 = 空的和 ✓
// 保持：加上 a[i] 之後，sum 是 a[0..i] 的和，下一次 i 變成 i+1 ✓
// 結束：i == n → sum 是 a[0..n-1] 的和 ✓
cout << sum << '\n';                      // 輸出：14
```

**例 2：二分搜尋**（最容易寫錯的迴圈之一）

```cpp
// 在排序好的陣列中找第一個 >= target 的位置
// 不變量：答案一定在 [lo, hi] 這個範圍裡
//         a[0..lo-1] 全部 < target；a[hi..n-1] 全部 >= target
vector<int> a2 = {1, 3, 3, 5, 8, 13};
int target = 4;
int lo = 0, hi = (int)a2.size();          // 初始化：整個範圍，答案可能是 n（都比 target 小）
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;         // 寫成 (lo + hi) / 2 在 lo + hi 很大時會溢位
    if (a2[mid] < target) lo = mid + 1;   // mid 和左邊都 < target → 答案在 mid 右邊
    else hi = mid;                        // mid >= target → 答案是 mid 或在 mid 左邊
}
cout << lo << '\n';                       // 輸出：3（a2[3] = 5 是第一個 >= 4 的）
```

每一步都檢查「不變量還成立嗎？」，就不會寫出 `lo = mid`（可能無窮迴圈）或 `hi = mid - 1`（可能錯過答案）這類錯誤。

**比喻**：爬樓梯時，每一階開始前都確認「我腳下踩的是第 i 階」。只要一開始成立、每一步之後還成立，最後一定在正確的位置。

---

# 第五部分：跳躍敘述

## 5.1 break 和 continue

| 敘述 | 效果 |
|---|---|
| `break` | **立刻離開** 最內層的迴圈（或 `switch`） |
| `continue` | **跳過這一次** 剩下的部分，直接進行下一次（`for` 會先執行更新部分 ③） |

**比喻**：寫考卷時，`continue` 是「這一題不會，跳到下一題」；`break` 是「不寫了，直接交卷」。

**break 的例子：找到就停**

```cpp
vector<int> v = {4, 8, 15, 16, 23, 42};
int found = -1;
for (int i = 0; i < (int)v.size(); i++) {
    if (v[i] > 10) { found = i; break; }   // 找到第一個 > 10 的就停，後面不看了
}
cout << found << '\n';                      // 輸出：2
```

**continue 的例子：跳過不需要處理的**

```cpp
int sum_odd = 0;
for (int i = 1; i <= 10; i++) {
    if (i % 2 == 0) continue;               // 偶數跳過，直接進行下一次（i++ 還是會執行）
    sum_odd += i;
}
cout << sum_odd << '\n';                    // 輸出：25（1 + 3 + 5 + 7 + 9）
```

**兩個一起用，追蹤每一步**：

```cpp
for (int x : {3, -1, 5, 0, 7}) {
    if (x < 0) { cout << "skip "; continue; }
    if (x == 0) { cout << "stop"; break; }
    cout << x << ' ';
}
cout << '\n';
// 輸出：3 skip 5 stop
```

**`while` 裡的 continue 要小心**：`while` 沒有「更新部分」，`continue` 會直接跳回條件檢查。如果更新寫在 `continue` 後面，就會變成無窮迴圈：

```cpp
int i = 0;
while (i < 5) {
    if (i == 2) { i++; continue; }          // ✅ continue 之前先更新
    // if (i == 2) continue;                // ❌ i 永遠停在 2 → 無窮迴圈
    cout << i;
    i++;
}
cout << '\n';                               // 輸出：0134
```

## 5.2 跳出多層迴圈

**`break` 只能跳出一層**：

```cpp
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (j == 1) break;                  // 只跳出內層的 j 迴圈
        cout << i << j << ' ';
    }
}
cout << '\n';                               // 輸出：00 10 20（外層還是跑完了 3 次）
```

要 **一次跳出好幾層**，常見的三種方法。以「在二維陣列中找某個值的位置」為例：

```cpp
vector<vector<int>> g = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
int target = 5;
```

**方法 1：寫成函式，用 return（最推薦）**

```cpp
pair<int, int> find_pos(const vector<vector<int>>& g, int target) {
    for (int i = 0; i < (int)g.size(); i++)
        for (int j = 0; j < (int)g[i].size(); j++)
            if (g[i][j] == target) return {i, j};    // 直接離開整個函式
    return {-1, -1};
}
auto [r, c] = find_pos(g, target);
cout << r << ' ' << c << '\n';               // 輸出：1 1
```

**方法 2：旗標 (flag)**

```cpp
bool found = false;
int fr = -1, fc = -1;
for (int i = 0; i < 3 && !found; i++)       // 外層條件也檢查旗標
    for (int j = 0; j < 3 && !found; j++)
        if (g[i][j] == target) { found = true; fr = i; fc = j; }
cout << fr << ' ' << fc << '\n';             // 輸出：1 1
```

**方法 3：goto（C++ 中少數合理的用法）**

```cpp
int gr = -1, gc = -1;
for (int i = 0; i < 3; i++)
    for (int j = 0; j < 3; j++)
        if (g[i][j] == target) { gr = i; gc = j; goto done; }
done:
cout << gr << ' ' << gc << '\n';             // 輸出：1 1
```

## 5.3 goto

**是什麼**：直接跳到程式裡的某個 **標籤 (label)**（`名稱:`）。

**為什麼一般不要用**：可以跳到任何地方，讓程式的流程變得很難追蹤（被稱為「義大利麵程式碼 spaghetti code」—— 執行流程像一盤義大利麵一樣糾纏在一起）。

**限制**：`goto` 不能跳過變數的初始化（和 `switch` 的 case 一樣的限制）：

```cpp
// goto skip;
// int x = 5;          // ❌ error: jump to label 'skip' crosses initialization of 'int x'
// skip:
```

唯一比較被接受的用途是 5.2 的「跳出多層迴圈」，而且大部分情況改寫成函式 + `return` 更好。

## 5.4 return

**是什麼**：結束目前的函式，回到呼叫的地方，並（如果不是 `void`）帶回一個值。

**規則 1：非 `void` 的函式，每一條執行路徑都要 `return` 一個值**

```cpp
int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
}   // ❌ x == 0 時沒有 return → 未定義行為
    //    -Wall 會警告：control reaches end of non-void function

int sign_ok(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;                       // ✅ 每條路徑都有 return
}
cout << sign_ok(-7) << sign_ok(0) << sign_ok(3) << '\n';   // 輸出：-101
```

**規則 2：`void` 函式可以用 `return;` 提早結束**

```cpp
void print_positive(int x) {
    if (x <= 0) return;             // 不合格就提早離開
    cout << x << '\n';
}
print_positive(-3);                 // 什麼都不印
print_positive(8);                  // 輸出：8
```

**規則 3：`main` 的 return 值是給作業系統的「結束碼」**

`main` 回傳 `0` 代表成功，非 0 代表失敗。`main` 是唯一可以不寫 `return` 的非 void 函式（預設回傳 0）。評測系統看到非 0 的結束碼會判定為 RE。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 敘述 | Statement | 一個完整的動作 | 1.1 |
| 區塊 / 複合敘述 | Block / Compound Statement | `{ }` 把多個敘述包成一個 | 1.2 |
| 空敘述 | Null Statement | 只有 `;`，什麼都不做 | 1.3 |
| 懸空 else | Dangling Else | else 跟最近的 if 配對 | 2.3 |
| 提早返回 | Early Return | 先處理不合格的情況並返回 | 2.5 |
| if 帶初始化 | If with Initializer | `if (init; cond)`，C++17 | 2.6 |
| 標籤 | Label | `case 3:`、`done:` 這類跳躍目標 | 3.1、5.3 |
| 穿透 | Fall-through | case 沒有 break，繼續往下執行 | 3.2 |
| 跳躍表 | Jump Table | switch 用陣列直接跳到對應位置 | 3.4 |
| 範圍 for | Range-based for | `for (x : 容器)` | 4.3 |
| 結構化綁定 | Structured Binding | `auto [a, b] = ...`，C++17 | 4.3 |
| 差一錯誤 | Off-by-one Error | 多跑或少跑一次 | 4.4 |
| 迴圈不變量 | Loop Invariant | 每次迴圈開始時都成立的條件 | 4.5 |
| 旗標 | Flag | 記錄某件事是否發生的 bool 變數 | 5.2 |
| 義大利麵程式碼 | Spaghetti Code | 流程糾纏、難以追蹤的程式 | 5.3 |
| 結束碼 | Exit Code | main 的回傳值 | 5.4 |

---

# 習題

### 題 1：預測輸出

```cpp
int a = 0, b = 5;
if (a > 0)
    if (b > 0) cout << "A";
else
    cout << "B";
cout << "C";
```

### 題 2：預測輸出

```cpp
int x = 2;
switch (x) {
    case 1: cout << "one ";
    case 2: cout << "two ";
    case 3: cout << "three ";
    default: cout << "other ";
}
```

### 題 3：找 bug（這個程式想印出 v 的元素，從最後一個到第一個）

```cpp
vector<int> v = {1, 2, 3};
for (size_t i = v.size() - 1; i >= 0; i--)
    cout << v[i] << ' ';
```

### 題 4：下面的程式會執行幾次 `cout`？

```cpp
for (int i = 0; i < 10; i++);
{
    cout << "hi\n";
}
```

### 題 5：這段程式想把 v 的每個元素加倍，為什麼沒效？

```cpp
for (auto x : v) x *= 2;
```

### 題 6：哪一段可以編譯？

```cpp
// A
switch (cmd) { case 1: int t = 5; cout << t; break; case 2: break; }
// B
switch (cmd) { case 1: { int t = 5; cout << t; break; } case 2: break; }
// C
string s = "add";
switch (s) { case "add": break; }
```

### 題 7：預測輸出

```cpp
int i = 0, sum = 0;
while (i < 10) {
    i++;
    if (i % 3 == 0) continue;
    if (i == 8) break;
    sum += i;
}
cout << i << ' ' << sum;
```

### 題 8：把下面的分數判斷改正

```cpp
if (score >= 60) grade = "pass";
else if (score >= 90) grade = "excellent";
else grade = "fail";
```

### 題 9：預測輸出

```cpp
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (j > i) break;
        cout << j;
    }
    cout << '|';
}
```

### 題 10：這個迴圈會停嗎？為什麼？

```cpp
int n = 10;
while (n != 0) n -= 3;
```

---

# 習題解答

**題 1**：只印出 `C`。`else` 跟 **內層** 的 `if (b > 0)` 配對；外層 `a > 0` 不成立，整個內層（包括 else）都不執行。

**題 2**：`two three other `。從 `case 2` 進入，沒有 `break`，一路穿透到最後。

**題 3**：`i` 是 `size_t`（無號），`i >= 0` 永遠成立。`i` 從 0 再減 1 會變成 `18446744073709551615`，`v[i]` 越界 → 未定義行為（很可能當掉）。改成 `for (int i = (int)v.size() - 1; i >= 0; i--)`。

**題 4**：**一次**。`for` 後面多了分號，迴圈本體是空敘述（跑了 10 次什麼都沒做）；後面的區塊是獨立的，只執行一次。

**題 5**：`auto x` 是 **複製品**，改的是複製品。改成 `for (auto& x : v) x *= 2;`。

**題 6**：只有 **B** 可以。A：跳到 `case 2` 會跳過 `t` 的初始化，編譯錯誤。C：`switch` 不能用 `string`。

**題 7**：`8 19`。i = 1、2 加入（sum = 3）；3 是 3 的倍數，`continue` 跳過；4、5 加入（sum = 12）；6 跳過；7 加入（sum = 19）；i = 8 時 `break`，8 沒有被加入，迴圈結束時 i = 8。

**題 8**：第一個條件 `score >= 60` 也會攔下 90 分以上的人，`excellent` 永遠不會出現。條件要 **從嚴格到寬鬆**：

```cpp
if (score >= 90) grade = "excellent";
else if (score >= 60) grade = "pass";
else grade = "fail";
```

**題 9**：`0|01|012|`。`break` 只跳出內層迴圈：i = 0 時印 `0`；i = 1 時印 `01`；i = 2 時印 `012`；每次內層結束後外層印 `|`。

**題 10**：**不會停**（無窮迴圈）。n 依序是 10、7、4、1、-2、-5……永遠不會剛好等於 0。條件應該寫成 `while (n > 0)`。用 `!=` 當迴圈條件時，要確定變數一定會「剛好」碰到那個值。
