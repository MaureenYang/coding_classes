# 03. 敘述與控制流程 (Statements & Control Flow)

> 程式練習：`C03 日期計算`
>
> 先備知識：第 02 課的運算式、短路求值。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 敘述的種類 | 運算式敘述、空敘述、區塊，以及「多一個分號」的災難 |
| 第二部分 | if / else | 懸空 else、`=` 和 `==`、C++17 的 if 初始化 |
| 第三部分 | switch | fall-through、case 裡宣告變數的限制 |
| 第四部分 | 迴圈 | 四種迴圈的選擇、範圍 for 的陷阱、無號數倒數 |
| 第五部分 | 跳躍敘述 | break / continue / return / goto，怎麼跳出多層迴圈 |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：敘述的種類

## 1.1 敘述 (Statement)

**白話**：程式裡 **一個完整的動作 / 指令**，是程式執行的基本單位。運算式「算出一個值」；敘述「做一件事」。

**比喻**：運算式像是句子裡的片語（「三加四」）；敘述像是一個完整的句子（「把三加四的結果存起來。」）。

| 種類 | 例子 |
|---|---|
| 運算式敘述 (expression statement) | `x = 5;`、`f();`、`i++;` |
| 宣告敘述 (declaration statement) | `int x = 5;` |
| 複合敘述 / 區塊 (compound / block) | `{ ... }` |
| 選擇敘述 (selection) | `if`、`switch` |
| 迴圈敘述 (iteration) | `while`、`do-while`、`for` |
| 跳躍敘述 (jump) | `break`、`continue`、`return`、`goto` |
| 空敘述 (null statement) | `;` |

## 1.2 區塊 (Block / Compound Statement)

**白話**：用 `{ }` 把好幾個敘述包起來，**當作一個敘述** 使用。區塊也會開啟一個新的 **作用域**：在裡面宣告的變數，出了 `}` 就消失。

```cpp
if (x > 0) {          // if 只能控制「一個敘述」，用區塊把多個敘述包成一個
    int y = x * 2;
    cout << y;
}                     // y 在這裡被銷毀
```

🔍 區塊結束時，裡面的物件會 **依照建立的相反順序** 被解構。這是 RAII（第 06 課）的基礎。

## 1.3 空敘述 (Null Statement) 與多餘的分號

**白話**：只有一個分號 `;` 的敘述，什麼都不做。

最危險的 bug：

```cpp
if (x > 100);              // ← 多了一個分號！if 控制的是「空敘述」
{
    cout << "too big";     // 這個區塊跟 if 無關，永遠會執行
}

for (int i = 0; i < n; i++);   // ← 迴圈本體是空敘述，跑 n 次什麼都沒做
    sum += a[i];               // 只執行一次，而且 i 已經不存在 → 編譯錯誤（幸好）
```

編譯時加 `-Wall -Wextra` 會出現 `suggest braces around empty body` 之類的警告。

---

# 第二部分：if / else

## 2.1 if 的條件

條件會被轉成 `bool`：0、`nullptr` 是 `false`，其他是 `true`（第 02 課）。

### 經典 bug：`=` 寫成 `==`

```cpp
if (x = 5) { ... }    // 不是比較！是把 5 指定給 x，結果是 5 → 永遠是 true
```

`-Wall` 會警告 `suggest parentheses around assignment used as truth value`。
有人會寫成 `if (5 == x)`（叫 Yoda 條件），寫錯成 `5 = x` 就會編譯錯誤 —— 但開警告就夠了。

## 2.2 懸空 else (Dangling Else)

**白話**：`else` 永遠跟 **最近的、還沒配對的 `if`** 配對，**跟縮排無關**。

```cpp
if (a > 0)
    if (b > 0)
        cout << "both positive";
else                              // 縮排看起來屬於外層的 if
    cout << "a is not positive";  // 實際上屬於內層的 if！
```

實際的意思是：`a > 0` 而且 `b <= 0` 時印出 "a is not positive"。

**比喻**：文章裡的「他」指的是 **最近提到的那個人**，不管你心裡想的是誰。

**解法**：**永遠加大括號**。

## 2.3 else if 鏈

```cpp
if (score >= 90) grade = 'A';
else if (score >= 80) grade = 'B';   // 其實是 else { if (...) ... } 的簡寫
else if (score >= 70) grade = 'C';
else grade = 'F';
```

條件 **由上往下檢查**，第一個成立的就執行，後面的都不看。所以 **範圍要從嚴格到寬鬆排**；把 `score >= 70` 放在第一個，90 分的人也會拿到 C。

## 2.4 C++17：if 帶初始化 (if with Initializer)

```cpp
if (auto it = m.find(key); it != m.end()) {
    cout << it->second;
} else {
    cout << "not found";
}
// it 在這裡已經不存在了
```

**好處**：`it` 只在 `if` / `else` 裡面看得到，不會污染外面的作用域。`switch` 也可以這樣寫。

---

# 第三部分：switch

## 3.1 switch 的基本規則

**白話**：根據一個 **整數（或列舉、字元）** 的值，跳到對應的 `case` 開始執行。

```cpp
switch (op) {
    case '+': r = a + b; break;
    case '-': r = a - b; break;
    default:  cout << "unknown"; break;
}
```

| 規則 | 說明 |
|---|---|
| 條件的型別 | 整數、`char`、`enum`。**不能是 `string`、`double`** |
| `case` 的值 | 必須是 **編譯期常數**，而且不能重複 |
| `default` | 沒有任何 case 符合時執行（可以省略，也可以放在任何位置） |

**比喻**：大樓的電梯。按下樓層號碼（`case`），電梯直接跳到那一層。

## 3.2 穿透 (Fall-through)

**白話**：`case` 只是 **進入點**，不是邊界。執行完一個 `case` 如果 **沒有 `break`**，會 **繼續往下執行下一個 case 的程式碼**。

**比喻**：電梯停在 5 樓之後，如果你沒有出電梯（`break`），它會繼續往下一層一層停。

```cpp
switch (level) {
    case 3: cout << "gold ";      // 沒有 break
    case 2: cout << "silver ";    // 沒有 break
    case 1: cout << "bronze";     // 
}
// level = 3 → 印出 "gold silver bronze"
```

**有時候是故意的**（`C03` 的標準解）：

```cpp
switch (month) {
    case 2: return is_leap(y) ? 29 : 28;
    case 4: case 6: case 9: case 11: return 30;   // 多個 case 共用同一段程式
    default: return 31;
}
```

故意穿透時加上 `[[fallthrough]];`（C++17），告訴讀者和編譯器「我是故意的」，`-Wimplicit-fallthrough` 就不會警告。

## 3.3 🔍 case 裡宣告變數

```cpp
switch (x) {
    case 1:
        int y = 10;      // 
        break;
    case 2:              // ❌ 編譯錯誤：jump to case label crosses initialization of 'int y'
        cout << y;
        break;
}
```

原因：所有 `case` 共用 **同一個作用域**。跳到 `case 2` 時，`y` 已經在作用域內，但它的初始化被跳過了。
**解法**：用大括號把 case 的內容包起來：

```cpp
case 1: {
    int y = 10;
    break;
}
```

## 3.4 switch vs if-else

| | `switch` | `if-else` 鏈 |
|---|---|---|
| 適合 | 一個值對應很多個 **固定** 的選項 | 範圍判斷、複雜條件 |
| 速度 | 編譯器可能做成 **跳躍表**，`O(1)` | 一個一個檢查 |
| 能比較 | 整數、字元、列舉 | 任何條件 |

---

# 第四部分：迴圈

## 4.1 四種迴圈

| 迴圈 | 什麼時候用 | 至少執行一次？ |
|---|---|---|
| `while (條件) { }` | 不知道要跑幾次，條件滿足就繼續 | 否 |
| `do { } while (條件);` | **至少要做一次**，例如「先讀輸入再檢查」 | **是** |
| `for (初始化; 條件; 更新) { }` | 計數、已知範圍 | 否 |
| `for (宣告 : 範圍) { }` | 走過容器的每個元素 | 否 |

```cpp
// do-while：至少問一次
int x;
do {
    cout << "請輸入 1~10：";
    cin >> x;
} while (x < 1 || x > 10);     // 注意結尾的分號
```

## 4.2 for 迴圈的三個部分

```cpp
for (int i = 0; i < n; i++) { ... }
//   ① 初始化    ② 條件   ③ 更新
```

執行順序：① → ② →（本體）→ ③ → ② →（本體）→ ③ → …… → ② 不成立就結束。

- 三個部分 **都可以省略**：`for (;;)` 是無窮迴圈。
- ① 宣告的變數只在迴圈裡有效。
- ③ 可以用逗號做多件事：`for (int i = 0, j = n - 1; i < j; i++, j--)`。

## 4.3 範圍 for (Range-based for)

```cpp
vector<int> v = {1, 2, 3};
for (int x : v) x *= 2;          // ❌ 沒效果：x 是複製品
for (int& x : v) x *= 2;         // ✅ x 是參考，真的改到 v
for (const auto& s : names) ...  // ✅ 唯讀，而且不會複製（大物件時很重要）
for (auto& [key, val] : m) ...   // ✅ C++17 結構化綁定，走訪 map
```

**選擇口訣**：
- 要修改 → `auto&`
- 只讀、元素很大（`string`、`vector`）→ `const auto&`
- 只讀、元素很小（`int`、`char`）→ `auto`

> ⚠️ **範圍 for 的迴圈中，不要對同一個容器 `push_back` / `erase`**。範圍 for 內部用的是迭代器，容器改變後迭代器會失效（未定義行為）。

## 4.4 迴圈常見的陷阱

### 差一錯誤 (Off-by-one Error)

```cpp
for (int i = 0; i <= n; i++) a[i] = 0;   // 多跑一次：a[n] 越界
for (int i = 1; i < n; i++) sum += a[i]; // 少算 a[0]
```

寫迴圈前先問：**第一次是多少？最後一次是多少？總共幾次？**

### 無號數倒數 → 無窮迴圈

```cpp
for (size_t i = v.size() - 1; i >= 0; i--)   // ❌ i 是無號數，永遠 >= 0
    ...                                       // i 減到 0 再減 → 變成超大的數，繼續跑

for (int i = (int)v.size() - 1; i >= 0; i--)  // ✅ 用有號數
for (size_t i = v.size(); i-- > 0; )          // ✅ 慣用寫法：先比較再減
```

而且 `v` 是空的時候，`v.size() - 1` 已經是超大的數了。

### 用浮點數當計數器

```cpp
for (double x = 0; x != 1.0; x += 0.1)   // ❌ 0.1 加 10 次不會剛好等於 1.0 → 無窮迴圈
for (int i = 0; i <= 10; i++) { double x = i * 0.1; ... }   // ✅
```

### 迴圈條件每次都重算

```cpp
for (int i = 0; i < strlen(s); i++)   // strlen 是 O(n)，整個迴圈變 O(n²)
int len = strlen(s);
for (int i = 0; i < len; i++)          // ✅
```

## 4.5 🔍 迴圈不變量 (Loop Invariant)

**白話**：一個在 **每次迴圈開始時都成立** 的條件。用它來確認迴圈是對的。

```cpp
// 不變量：sum 是 a[0] ~ a[i-1] 的總和
int sum = 0;
for (int i = 0; i < n; i++) sum += a[i];
// 迴圈結束時 i == n → sum 是 a[0] ~ a[n-1] 的總和 ✓
```

**比喻**：爬樓梯時，每一階開始前都確認「我腳下踩的是第 i 階」。只要一開始成立、每一步之後還成立，最後一定在正確的位置。

寫二分搜尋、雙指標這類容易寫錯的迴圈時，先想清楚不變量，可以少掉大部分的 bug。

---

# 第五部分：跳躍敘述

## 5.1 break / continue

- `break`：**立刻離開** 最內層的迴圈（或 `switch`）。
- `continue`：**跳過這一次** 剩下的部分，直接進行下一次（`for` 會先執行更新 ③）。

```cpp
for (int x : v) {
    if (x < 0) continue;     // 負數跳過
    if (x == 0) break;       // 遇到 0 就停
    sum += x;
}
```

**比喻**：`continue` 是「這一題不會，跳到下一題」；`break` 是「不寫了，交卷」。

## 5.2 跳出多層迴圈

`break` **只能跳出一層**。要跳出好幾層，常見的方法：

```cpp
// 方法 1：寫成函式，用 return（最推薦）
bool find(const vector<vector<int>>& g, int target) {
    for (auto& row : g)
        for (int x : row)
            if (x == target) return true;
    return false;
}

// 方法 2：旗標
bool found = false;
for (int i = 0; i < n && !found; i++)
    for (int j = 0; j < m && !found; j++)
        if (g[i][j] == target) found = true;

// 方法 3：goto（C++ 中少數合理的用法）
for (...) for (...) if (...) goto done;
done:
```

## 5.3 goto

**白話**：直接跳到程式裡的某個 **標籤 (label)**。

`goto` 讓程式的流程很難追蹤（「義大利麵程式碼」），**一般不要用**。唯一比較被接受的用途是上面的「跳出多層迴圈」。

而且 `goto` 不能跳過變數的初始化（跟 `switch` 的 case 一樣的限制）。

## 5.4 return

**白話**：結束函式，回到呼叫的地方。函式宣告有回傳型別（不是 `void`）時，**每一條執行路徑都要 `return` 一個值**。

```cpp
int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
}   // ❌ x == 0 時沒有 return → 未定義行為（-Wall 會警告 control reaches end of non-void function）
```

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 敘述 | Statement | 一個完整的動作 | 1.1 |
| 區塊 / 複合敘述 | Block / Compound Statement | `{ }` 把多個敘述包成一個 | 1.2 |
| 空敘述 | Null Statement | 只有 `;`，什麼都不做 | 1.3 |
| 懸空 else | Dangling Else | else 跟最近的 if 配對 | 2.2 |
| if 帶初始化 | If with Initializer | `if (init; cond)`，C++17 | 2.4 |
| 穿透 | Fall-through | case 沒有 break，繼續往下執行 | 3.2 |
| 跳躍表 | Jump Table | switch 用陣列直接跳到對應位置 | 3.4 |
| 範圍 for | Range-based for | `for (x : 容器)` | 4.3 |
| 結構化綁定 | Structured Binding | `auto [a, b] = pair;`，C++17 | 4.3 |
| 差一錯誤 | Off-by-one Error | 多跑或少跑一次 | 4.4 |
| 迴圈不變量 | Loop Invariant | 每次迴圈開始時都成立的條件 | 4.5 |
| 標籤 | Label | goto 跳躍的目的地 | 5.3 |

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

---

# 習題解答

**題 1**：只印出 `C`。`else` 跟 **內層** 的 `if (b > 0)` 配對，外層 `a > 0` 不成立，整個內層（包括 else）都不執行。

**題 2**：`two three other `。從 `case 2` 進入，沒有 `break`，一路穿透到最後。

**題 3**：`i` 是 `size_t`（無號），`i >= 0` 永遠成立。`i` 從 0 再減 1 會變成超大的數，`v[i]` 越界 → 未定義行為（很可能當掉）。改成 `for (int i = (int)v.size() - 1; i >= 0; i--)`。

**題 4**：**一次**。`for` 後面多了分號，迴圈本體是空敘述；後面的區塊是獨立的，只執行一次。

**題 5**：`auto x` 是 **複製品**，改的是複製品。改成 `for (auto& x : v) x *= 2;`。

**題 6**：只有 **B** 可以。A：跳到 `case 2` 會跳過 `t` 的初始化，編譯錯誤。C：`switch` 不能用 `string`。

**題 7**：`8 19`。i = 1、2 加入（sum = 3）；3 是 3 的倍數，`continue` 跳過；4、5 加入（sum = 12）；6 跳過；7 加入（sum = 19）；i = 8 時 `break`，8 沒有被加入，迴圈結束時 i = 8。

**題 8**：第一個條件 `score >= 60` 也會攔下 90 分以上的人，`excellent` 永遠不會出現。條件要 **從嚴格到寬鬆**：

```cpp
if (score >= 90) grade = "excellent";
else if (score >= 60) grade = "pass";
else grade = "fail";
```

---

# 程式練習

- **`C03 日期計算`**：閏年規則（巢狀條件）、每月天數（`switch` 的刻意穿透）、日期轉換（迴圈）。測資專門檢查 1900 / 2000 年、2 月 29 日、跨年等邊界。
