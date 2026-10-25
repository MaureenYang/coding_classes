# C++ 深入總複習考卷

> 涵蓋 C++ 深入路線第 01 ~ 15 課。題型有預測輸出、找錯、判斷能不能編譯、寫程式、觀念說明；預測輸出的答案都是實際用 `g++ -std=c++17`（x86-64 Linux）編譯執行的結果。
> 每一題寫完再看答案；答錯的題目，回到該課對應的段落重讀。

@@@ 01 | 型別、變數與型別轉換

??? 預測輸出
在 x86-64 Linux 上：

```cpp
#include <iostream>
using namespace std;

int main() {
    char c = 200;
    cout << (int)c << "\n";
    cout << sizeof(3.0f) << sizeof(3.0) << sizeof('a') << sizeof(3LL) << "\n";
    auto x = 5 / 2;
    auto y = 5 / 2.0;
    cout << x << " " << y << "\n";
    unsigned int u = -1;
    cout << u << "\n";
    return 0;
}
```
!!!
```output
-56
4818
2 2.5
4294967295
```

- `char` 在 x86 上是 **有號** 的（這是實作定義的，ARM 上通常是無號），200 存不下，變成 200 − 256 = -56。
- 字面值的型別：`3.0f` 是 `float`（4）、`3.0` 是 `double`（8）、`'a'` 在 C++ 是 `char`（1，在 C 裡是 `int`！）、`3LL` 是 `long long`（8）。
- `auto` 依照初始值推導：`5 / 2` 是 `int` 除法得到 2；`5 / 2.0` 是 `double`。
- -1 轉成 `unsigned int` 是 2³² − 1。

??? 判斷能不能編譯
下面每一行能不能編譯？能的話 `a` ~ `e` 的值是多少？

```cpp
int a = 3.7;
int b(3.7);
int c{3.7};
int d = {3};
double e{3};
```
!!!
- `int a = 3.7;`：可以，**截斷** 成 3（編譯器可能警告）。
- `int b(3.7);`：可以，一樣是 3。
- `int c{3.7};`：**編譯錯誤**。大括號初始化 **禁止窄化轉換 (narrowing)**：`double` → `int` 會遺失資料。
- `int d = {3};`：可以，3。
- `double e{3};`：可以，3.0。`int` 常數 3 轉成 `double` 不會遺失資料，不算窄化。

這就是推薦用 `{}` 初始化的原因：不小心遺失資料時，編譯器會擋下來。

??? 觀念
1. `const` 和 `constexpr` 有什麼不同？下面哪一行會編譯錯誤？
```cpp
int n;
cin >> n;
const int a = n;
constexpr int b = n;
constexpr int c = 10 * 10;
int arr[c];
```
2. C++ 有哪四種具名轉型？各用在什麼情況？
!!!
1. - `const`：**執行時** 不能再修改，但初始值可以是執行時才知道的值。
   - `constexpr`：值必須在 **編譯時** 就算得出來，可以用在陣列大小、模板參數等需要常數的地方。

   `constexpr int b = n;` **編譯錯誤**，因為 `n` 是執行時才讀進來的。其他都可以。
2. - `static_cast`：一般的、有意義的轉換（`int` ↔ `double`、`void*` → `T*`、往下轉型但自己保證正確）。最常用。
   - `dynamic_cast`：多型類別之間 **安全的** 往下轉型，執行時檢查，失敗回傳 `nullptr`（參考則丟出 `bad_cast`）。
   - `const_cast`：加上或移除 `const`。只能用在原本不是 `const` 的物件上，否則修改它是未定義行為。
   - `reinterpret_cast`：把位元重新解讀成不相關的型別（指標 ↔ 整數等），非常危險，幾乎用不到。

   C 風格的 `(int)x` 會依序嘗試上面幾種，看不出意圖，C++ 裡應該避免。

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

int x = 1;

int next_id() {
    static int id = 100;
    return id++;
}

int main() {
    int x = 2;
    {
        int x = 3;
        cout << x << " " << ::x << "\n";
    }
    next_id();
    next_id();
    cout << next_id() << " " << x << "\n";
    return 0;
}
```
!!!
```output
3 1
102 2
```

- 內層的 `x` 遮蔽了外層；`::x` 指的是 **全域** 的 `x`。
- `static` 區域變數只初始化一次，呼叫之間保留值：100、101、102。`id++` 回傳舊值，所以第三次回傳 102。

@@@ 02 | 運算式

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

int main() {
    int x = 6;
    cout << (1 << 2 + 1) << " " << (x & 1 == 0) << " " << ((x & 1) == 0) << "\n";
    cout << -7 / 2 << " " << -7 % 2 << " " << 7 % -2 << "\n";
    cout << (0.1 + 0.2 == 0.3) << "\n";
    int a, b;
    a = b = 3;
    a += b *= 2;
    cout << a << " " << b << "\n";
    return 0;
}
```
!!!
```output
8 0 1
-3 -1 1
0
9 6
```

- `+` 的優先順序比 `<<` 高：`1 << (2 + 1)` = 8。
- `==` 的優先順序比 `&` 高：`x & (1 == 0)` = `6 & 0` = 0。位元運算一定要加括號。
- 整數除法往 0 截斷；`%` 的結果和 **被除數** 同號。
- 0.1、0.2、0.3 都不能用二進位精確表示，`0.1 + 0.2` 是 0.30000000000000004。浮點數要用「差的絕對值小於 ε」比較。
- 指定運算子是 **右結合**：`b *= 2` 先算（b = 6），再 `a += 6`（a = 9）。

??? 判斷
下面每一行，是 **定義良好**、**未指定行為 (unspecified)**，還是 **未定義行為 (UB)**？（C++17）

```cpp
(a) i = i++ + 1;
(b) i = ++i + i++;
(c) cout << f() << g();          // f、g 都會印東西
(d) int r = f() + g();           // f、g 都會印東西
(e) a[i] = i++;
(f) i = i + 1;
```
!!!
- (a) **定義良好**（C++17 起）：`=` 右邊會在指定之前完全算完。（C++14 以前是 UB。）
- (b) **UB**：同一個運算式裡，`i` 被兩個沒有先後順序的副作用修改。
- (c) **定義良好**（C++17 起）：`<<` 由左到右求值，先 `f()` 再 `g()`。
- (d) **未指定**：`+` 的兩個運算元誰先算沒有規定，可能先印 f 的也可能先印 g 的，但一定是其中一種，不會壞掉。
- (e) **定義良好**（C++17 起）：`=` 的右邊先求值（包括 `i++` 的副作用），才算左邊的 `a[i]`，所以寫入的是 `a[新的 i]`。這種寫法很難讀，不要這樣寫。
- (f) **定義良好**。

實務原則：**同一個運算式裡，不要對同一個變數修改超過一次，也不要一邊修改一邊讀取**。

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

int calls = 0;
bool check(bool v) { calls++; return v; }

int main() {
    bool r1 = check(false) && check(true);
    bool r2 = check(true) || check(false);
    bool r3 = check(true) && check(false) || check(true);
    cout << r1 << r2 << r3 << " " << calls << "\n";
    int n = 12;
    cout << (n & -n) << " " << __builtin_popcount(n) << " " << (n >> 1) << "\n";
    return 0;
}
```
!!!
```output
011 5
4 2 6
```

- `r1`：左邊是 false，`&&` 短路，只呼叫 1 次。
- `r2`：左邊是 true，`||` 短路，只呼叫 1 次。
- `r3`：`&&` 優先於 `||`，是 `(true && false) || true`，三個都要算，呼叫 3 次。合計 5 次。
- `n & -n` 取出 **最低位的 1**：12 = 1100₂ → 100₂ = 4。
- 12 有 2 個位元是 1；右移一位等於除以 2。

??? 觀念
1. `1 << 31`（`int` 是 32 位元）有什麼問題？`1 << 32` 呢？
2. 怎麼判斷 `a + b`（兩個 `int`）會不會溢位，**而且判斷的過程本身不能溢位**？
!!!
1. - `1 << 31`：結果超出 `int` 能表示的正數範圍（C++20 以前是 UB，C++20 起定義為 `INT_MIN`），應該寫 `1u << 31` 或 `1LL << 31`。
   - `1 << 32`：位移量 **大於等於型別的位元數** 永遠是 UB（x86 上實際會變成 `1 << 0`，得到 1，非常隱密的 bug）。
2. 在相加 **之前** 檢查：

   ```cpp
   if (b > 0 && a > INT_MAX - b) /* 會往上溢位 */;
   if (b < 0 && a < INT_MIN - b) /* 會往下溢位 */;
   ```

   `INT_MAX - b`（b > 0 時）和 `INT_MIN - b`（b < 0 時）都不會溢位。或者用更大的型別：`(long long)a + b` 再和範圍比較；GCC 也有 `__builtin_add_overflow`。

@@@ 03 | 敘述與控制流程

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

int main() {
    int a = 5, b = 0;
    if (a > 3)
        if (b > 0)
            cout << "A\n";
    else
        cout << "B\n";

    for (int i = 0; i < 5; i++) {
        if (i == 1) continue;
        if (i == 4) break;
        cout << i;
    }
    cout << "\n";

    int k = 0;
    for (int i = 0; i < 3; i++);
    {
        k++;
    }
    cout << k << "\n";
    return 0;
}
```
!!!
```output
B
023
1
```

- **懸空 else**：`else` 永遠跟 **最近的** 那個 `if` 配對，縮排騙人。這裡 `else` 屬於 `if (b > 0)`，`b > 0` 為假，所以印 `B`。要讓 `else` 跟外層的 `if`，必須加大括號。
- `continue` 跳過 i = 1，`break` 在 i = 4 時離開：印 `0 2 3`。
- `for (...);` 後面多了一個分號，迴圈本體是 **空敘述**，空轉 3 次就結束了。下面的 `{ k++; }` 只是一個普通的區塊，不屬於迴圈，只執行一次，所以 `k` 是 1。如果寫成 `while (k < 3);`，就會變成無窮迴圈。

??? 判斷能不能編譯
下面的程式能不能編譯？不能的話怎麼改？

```cpp
switch (op) {
    case 1:
        int x = 10;
        cout << x;
        break;
    case 2:
        cout << "two";
        break;
}
```
!!!
**不能**：`error: jump to case label` / `crosses initialization of 'int x'`。

`case` 只是 **標籤**，整個 `switch` 是同一個作用域。跳到 `case 2` 時會「跳過」`x` 的初始化，但 `x` 在 `case 2` 裡仍然看得到（作用域還沒結束），所以編譯器禁止。

改法：用大括號把 `case 1` 的內容包成自己的區塊：

```cpp
case 1: {
    int x = 10;
    cout << x;
    break;
}
```

??? 找錯
下面每一個迴圈都有問題，說明會發生什麼事：

```cpp
// (a) 想由大到小走訪
for (unsigned i = n - 1; i >= 0; i--) cout << a[i];

// (b)
for (double t = 0; t != 1.0; t += 0.1) cout << t << " ";

// (c) 想刪除所有偶數
for (auto it = v.begin(); it != v.end(); it++)
    if (*it % 2 == 0) v.erase(it);
```
!!!
- (a) `unsigned` 永遠 `>= 0`，條件永遠成立。i 從 0 再減 1 會繞回成 4294967295，**無窮迴圈加上越界存取**。改用 `int`，或寫成 `for (size_t i = n; i-- > 0; )`。
- (b) 0.1 不能精確表示，加 10 次之後是 0.9999999999999999，**永遠不會剛好等於 1.0**，無窮迴圈。浮點數不要用 `!=` 當迴圈條件，改成 `t < 1.0 - 1e-9`，或用整數計數再除。
- (c) `erase(it)` 之後 `it` **失效** 了，再 `it++` 是未定義行為。正確寫法：`it = v.erase(it);`（不刪時才 `++it`），或直接用 `v.erase(remove_if(...), v.end())`。

??? 觀念
1. 要跳出 **兩層** 迴圈，有哪些寫法？
2. C++17 的 `if (auto it = m.find(k); it != m.end())` 有什麼好處？
!!!
1. - 用一個 `bool found` 旗標，內層 `break` 後外層檢查旗標再 `break`。
   - 把兩層迴圈包成一個 **函式**，找到時直接 `return`（最乾淨）。
   - 用 `goto` 跳到迴圈外面（C++ 裡少用，但這是少數合理的場合）。
   - 用 lambda 包起來立即呼叫，裡面 `return`。
2. `it` 的 **作用域只在這個 `if`（和它的 `else`）裡面**，不會汙染外面的作用域，也不會在後面被誤用。同時把「宣告」和「條件」寫在一起，意圖更清楚。

@@@ 04 | 函式

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

void f(int)    { cout << "int "; }
void f(double) { cout << "double "; }
void f(long)   { cout << "long "; }
void g(int a, int b = 10, int c = 20) { cout << a + b + c << " "; }

int main() {
    f(3);
    f(3.0f);
    f('a');
    f(3L);
    cout << "\n";
    g(1);
    g(1, 2);
    g(1, 2, 3);
    cout << "\n";
    return 0;
}
```
!!!
```output
int double int long 
31 23 6 
```

多載解析的優先順序：**完全符合** > **提升 (promotion)** > **一般轉換**。
- `3.0f` 是 `float`，`float → double` 是「提升」，比轉成 `int` / `long` 好。
- `'a'` 是 `char`，`char → int` 是「提升」。
- 預設參數從右邊開始補：`g(1)` 是 1 + 10 + 20。

（注意 `f(3u)` 會 **模稜兩可**：`unsigned → int`、`→ long`、`→ double` 都是一般轉換，編譯錯誤。）

??? 找錯
下面兩個函式都有嚴重的錯誤，說明原因：

```cpp
const string& greet(const string& name) {
    string s = "Hello, " + name;
    return s;
}

int& biggest(vector<int> v) {
    return *max_element(v.begin(), v.end());
}
```
!!!
兩個都是 **回傳懸空參考**：
- `greet`：`s` 是區域變數，函式結束就解構了，回傳的參考指向已經不存在的物件。應該 **回傳值** `string`（有回傳值最佳化 / 移動，不會慢）。
- `biggest`：參數 `v` 是 **傳值**，是呼叫者 vector 的複本，函式結束時就銷毀了；回傳的參考指向複本裡的元素。應該改成 `int& biggest(vector<int>& v)`，才會指向呼叫者的元素。

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

int main() {
    int x = 1;
    auto byval = [x]() { return x; };
    auto byref = [&x]() { return x; };
    x = 5;
    cout << byval() << " " << byref() << "\n";

    int c = 0;
    auto inc = [c]() mutable { return ++c; };
    inc();
    inc();
    cout << inc() << " " << c << "\n";

    auto add = [](int a, int b) { return a + b; };
    cout << add(2, 3) << "\n";
    return 0;
}
```
!!!
```output
1 5
3 0
5
```

- `[x]` **按值捕獲**：建立 lambda 的那一刻複製 x（= 1），之後改 x 不影響。
- `[&x]` **按參考捕獲**：每次呼叫時讀的是現在的 x。
- `mutable` 讓 lambda 可以修改 **自己那份複本**；複本會在呼叫之間保留，所以是 1、2、3，但外面的 `c` 仍然是 0。

??? 找錯
下面的比較函式用在 `sort` 上，可能讓程式 **當掉或結果錯誤**，為什麼？

```cpp
sort(v.begin(), v.end(), [](int a, int b) { return a <= b; });
```
!!!
`sort` 要求比較函式是 **嚴格弱序 (strict weak ordering)**，其中一條是 **非自反性**：`comp(a, a)` 必須是 `false`。`a <= b` 在 `a == b` 時回傳 `true`，違反規則，是 **未定義行為**：有很多相同元素時，`sort` 內部的迴圈可能跑出陣列範圍而當掉。

改成 `a < b`（遞減就用 `a > b`）。多個條件時，「相等」一定要回傳 `false`。

@@@ 05 | 指標與參考

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

void set1(int* p) { p = nullptr; }
void set2(int*& p) { p = nullptr; }

int main() {
    int a = 1, b = 2;
    int& r = a;
    r = b;
    b = 3;
    cout << a << " " << b << "\n";

    int arr[] = {10, 20, 30};
    int* p = arr;
    int* q = p;
    set1(p);
    cout << (p == nullptr) << " ";
    set2(q);
    cout << (q == nullptr) << "\n";
    cout << *(arr + 2) << " " << 2[arr] << "\n";
    return 0;
}
```
!!!
```output
2 3
0 1
30 30
```

- 參考 **一旦綁定就不能改綁**：`r = b` 是「把 b 的值指定給 r 所代表的 a」，所以 a = 2；之後改 b 不影響 a。
- `set1` 收到的是指標的 **複本**，改複本不影響 `p`；`set2` 收到指標的 **參考**，真的改到 `q`。
- `arr[i]` 就是 `*(arr + i)`，加法可以交換，所以 `2[arr]` 也合法（但不要這樣寫）。

??? 判斷能不能編譯
下面每一行能不能編譯？

```cpp
int x = 1, y = 2;
const int* p1 = &x;    *p1 = 5;    // (a)
const int* p2 = &x;    p2 = &y;    // (b)
int* const p3 = &x;    *p3 = 5;    // (c)
int* const p4 = &x;    p4 = &y;    // (d)
int& r1 = 5;                       // (e)
const int& r2 = 5;                 // (f)
int& r3;                           // (g)
```
!!!
- (a) **不行**：`p1` 指向 `const int`，不能透過它修改。
- (b) 可以：指標本身不是 const，可以改指向。
- (c) 可以：指標本身是 const，但指向的資料可以改。
- (d) **不行**：`p3`/`p4` 這種 `* const` 指標不能改指向。
- (e) **不行**：非 const 的左值參考不能綁定到暫時物件（字面值 5）。
- (f) 可以：**const 參考可以綁定暫時物件**，而且會延長暫時物件的生命週期到參考的作用域結束。
- (g) **不行**：參考一定要在宣告時初始化。

??? 觀念
什麼時候用指標、什麼時候用參考？列出兩者的三個差別。
!!!
| | 指標 | 參考 |
|---|---|---|
| 可以是「空的」 | 可以（`nullptr`） | 不行，一定綁定某個物件 |
| 可以改指向別的物件 | 可以 | 不行 |
| 需要初始化 | 不一定 | 一定 |
| 使用語法 | `*p`、`p->x` | 跟一般變數一樣 |
| 可以做算術、陣列走訪 | 可以 | 不行 |

原則：
- 函式參數「一定有一個物件、要修改或避免複製」→ **參考**（`T&` 或 `const T&`）。
- 「可能沒有」（選擇性參數）、需要改指向、需要走訪陣列、或用於資料結構的連結 → **指標**。
- 擁有資源 → 智慧指標（第 06 課）。

??? 預測輸出
`int m[2][3] = {{1,2,3},{4,5,6}};`，下面的程式輸出什麼？

```cpp
#include <iostream>
using namespace std;

int main() {
    int m[2][3] = {{1, 2, 3}, {4, 5, 6}};
    int* flat = &m[0][0];
    int (*row)[3] = m;
    cout << flat[4] << " " << *(*(row + 1) + 2) << " " << sizeof(m) / sizeof(m[0]) << "\n";
    const char* s = "hello";
    cout << *(s + 1) << " " << s + 2 << "\n";
    return 0;
}
```
!!!
```output
5 6 2
e llo
```

- 二維陣列連續存放（列優先），`flat[4]` 是第二列第二個 = 5。
- `row` 是「指向 3 個 int 的陣列」的指標，`row + 1` 跳過一整列；`*(row + 1) + 2` 是第二列第三個元素的位址 → 6。
- `sizeof(m) / sizeof(m[0])` = 24 / 12 = 2（列數）。
- `s + 2` 是指向 `'l'` 的 `const char*`，`cout` 會把它當字串印出 `llo`。

@@@ 06 | 記憶體管理、RAII 與移動語意

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

struct Tracer {
    const char* name;
    Tracer(const char* n) : name(n) { cout << "+" << name << " "; }
    ~Tracer() { cout << "-" << name << " "; }
};

Tracer g("G");

int main() {
    cout << "| ";
    Tracer a("A");
    {
        Tracer b("B");
        Tracer c("C");
    }
    Tracer* d = new Tracer("D");
    delete d;
    Tracer e("E");
    cout << "| ";
    return 0;
}
```
!!!
```output
+G | +A +B +C -C -B +D -D +E | -E -A -G 
```

- 全域物件在 `main` 之前建構、在 `main` 結束之後解構。
- 區域物件在離開作用域時，以 **建構的相反順序** 解構（C 先於 B）。
- `new` 出來的物件只有在 `delete` 時才解構；忘了 `delete` 就永遠不會解構（洩漏）。
- `main` 結束時：先解構 E、A（相反順序），最後才是全域的 G。

??? 找錯
下面的類別有什麼問題？寫出至少兩種修正方式。

```cpp
class Buffer {
    int* data;
    int n;
public:
    Buffer(int n) : data(new int[n]), n(n) {}
    ~Buffer() { delete[] data; }
};

void f() {
    Buffer a(10);
    Buffer b = a;
}
```
!!!
類別自己管理資源（寫了解構子），卻 **沒有寫複製建構子和複製指定**。編譯器產生的版本是 **淺複製**：`b.data` 和 `a.data` 指向同一塊記憶體，`f` 結束時兩個解構子各 `delete[]` 一次 → **double free**。這違反了 **三法則**。

修正方式：
1. **三法則 / 五法則**：自己寫複製建構子（配置新的陣列並複製內容）、複製指定（處理自我指定，或用 copy-and-swap），最好再加上移動建構子和移動指定。
2. **禁止複製**：`Buffer(const Buffer&) = delete; Buffer& operator=(const Buffer&) = delete;`（不需要複製時）。
3. **零法則**（最好）：不要自己管理記憶體，把 `int* data` 換成 `vector<int> data`（或 `unique_ptr<int[]>`），編譯器產生的複製 / 移動 / 解構就全部正確了，一個都不用寫。

??? 預測輸出
```cpp
#include <iostream>
#include <memory>
using namespace std;

int main() {
    auto p1 = make_unique<int>(42);
    auto p2 = std::move(p1);
    cout << (p1 == nullptr) << " " << *p2 << "\n";

    shared_ptr<int> s1 = make_shared<int>(7);
    cout << s1.use_count() << " ";
    {
        shared_ptr<int> s2 = s1;
        auto s3 = s1;
        cout << s1.use_count() << " ";
    }
    cout << s1.use_count() << "\n";

    weak_ptr<int> w = s1;
    cout << w.use_count() << " " << w.expired() << " ";
    s1.reset();
    cout << w.expired() << "\n";
    return 0;
}
```
!!!
```output
1 42
1 3 1
1 0 1
```

- `unique_ptr` **不能複製、只能移動**；移動之後原本的 `p1` 變成空的。
- `shared_ptr` 用 **參考計數**：複製一次加 1，離開作用域減 1。
- `weak_ptr` **不增加** 計數；最後一個 `shared_ptr` 放開之後，`weak_ptr` 就 `expired()` 了。這就是打破 `shared_ptr` **循環參考**（互相指向導致永遠不會釋放）的方法。

??? 觀念
1. `std::move(x)` 本身做了什麼？
2. 移動建構子為什麼通常要標 `noexcept`？不標的話 `vector` 擴容時會怎樣？
3. 用 `unique_ptr<Node>` 串起一條 10⁶ 個節點的串列，程式結束時為什麼可能當掉？
!!!
1. **什麼都沒移動**。它只是一個轉型：把 `x` 轉成右值參考（`T&&`），讓多載解析選到 **移動** 建構子 / 移動指定。真正「搬走資源」的是那些函式。被移動之後的物件處於「有效但未指定」的狀態，只能重新指定或解構。
2. `vector` 擴容時要把舊元素搬到新空間，而且要提供 **強例外保證**（失敗時原本的 vector 不變）。如果移動建構子可能丟例外，搬到一半失敗就無法復原，所以 `vector` 會改用 **複製**（慢）。標了 `noexcept`，`vector` 才敢用移動。
3. 第一個節點解構時，會解構它的 `unique_ptr<Node> next`，觸發第二個節點的解構……形成 **深度 10⁶ 的遞迴**，堆疊溢位。解法：在串列的解構子裡用迴圈一個一個釋放（每次把 `next` 搬出來，讓目前節點的 `next` 是空的再釋放）。

@@@ 07 | 類別與物件導向

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

struct M { M(const char* s) { cout << s << " "; } };

struct X {
    M b;
    M a;
    X() : a("a"), b("b") { cout << "body "; }
};

struct Counter {
    static int alive;
    Counter() { alive++; }
    ~Counter() { alive--; }
};
int Counter::alive = 0;

int main() {
    X x;
    cout << "\n";
    Counter c1, c2;
    {
        Counter c3;
        cout << Counter::alive << " ";
    }
    cout << Counter::alive << "\n";
    return 0;
}
```
!!!
```output
b a body 
3 2
```

- 成員初始化的順序是 **成員在類別裡宣告的順序**（先 `b` 再 `a`），**跟初始化串列寫的順序無關**。如果 `a` 的初始值用到 `b`，或反過來，順序錯了就會用到未初始化的值。gcc 的 `-Wall` 會給 `-Wreorder` 警告。
- 成員初始化完成之後，才執行建構子的本體。
- `static` 成員屬於 **整個類別**，所有物件共用一份。

??? 判斷能不能編譯
```cpp
class Meter {
    double v;
public:
    explicit Meter(double x) : v(x) {}
    double get() const { return v; }
    void set(double x) { v = x; }
};

void show(Meter m);

Meter a(3.0);          // (a)
Meter b = 3.0;         // (b)
show(4.0);             // (c)
show(Meter(4.0));      // (d)
const Meter c(1.0);
c.get();               // (e)
c.set(2.0);            // (f)
```
!!!
- (a) 可以：直接呼叫建構子。
- (b) **不行**：`explicit` 禁止「用 `=` 從 `double` 隱式轉換」。
- (c) **不行**：一樣是隱式轉換。
- (d) 可以：明確建構。
- (e) 可以：`get` 是 **const 成員函式**，const 物件可以呼叫。
- (f) **不行**：`set` 不是 const 成員函式，const 物件不能呼叫（它可能修改物件）。

單一參數的建構子預設應該加 `explicit`，避免意外的轉換（例如 `show(4.0)` 這種看不出單位的寫法）。

??? 寫程式
為分數類別 `Frac`（成員 `long long num, den`，建構時已經約分、`den > 0`）寫出：

1. `operator+=`（成員函式）
2. 用 `+=` 實作的 `operator+`（非成員函式）
3. `operator==`
4. `operator<<`

說明 `+=` 和 `+` 的回傳型別為什麼不同。
!!!
```cpp
class Frac {
    long long num, den;
    void normalize();              // 約分、讓分母為正
public:
    Frac(long long n = 0, long long d = 1) : num(n), den(d) { normalize(); }

    Frac& operator+=(const Frac& o) {
        num = num * o.den + o.num * den;
        den = den * o.den;
        normalize();
        return *this;                          // 回傳自己的參考
    }
    friend bool operator==(const Frac& a, const Frac& b) {
        return a.num == b.num && a.den == b.den;   // 都已約分，直接比
    }
    friend ostream& operator<<(ostream& os, const Frac& f) {
        return os << f.num << "/" << f.den;
    }
};

Frac operator+(Frac a, const Frac& b) {        // a 是複本
    a += b;
    return a;                                  // 回傳新的值
}
```

- `+=` 修改的是 **左邊的物件本身**，回傳它的 **參考**（`Frac&`），讓 `(a += b) += c` 這種連鎖可以運作，也不用複製。
- `+` 產生一個 **新的值**，左右兩邊都不改，所以 **回傳值**（`Frac`）。絕對不能回傳區域變數的參考。
- `+` 寫成非成員函式，`1 + f` 這種「左邊不是 `Frac`」的寫法才能透過隱式轉換運作。
- `operator<<` 的左邊是 `ostream`，不可能是 `Frac` 的成員；要回傳 `ostream&` 才能連續 `<<`。

??? 觀念
1. 什麼是類別的 **不變量 (invariant)**？用 `Frac` 舉例。
2. 為什麼成員資料通常設成 `private`？
!!!
1. 不變量是 **在任何公開函式執行前後都必須成立的條件**。例如 `Frac`：分母永遠 > 0、分子分母永遠互質（已約分）。建構子負責建立不變量，每個會修改狀態的公開函式負責維持它。有了不變量，其他函式就可以依賴它（例如 `==` 直接比較分子分母）。
2. **封裝**：如果成員是 `public`，任何人都可以寫 `f.den = 0;`，直接破壞不變量，類別無法保證自己的正確性。設成 `private` 之後，只能透過公開函式修改，所有的修改都經過檢查。另外也能自由地修改內部表示方式，不影響使用者的程式。

@@@ 08 | 繼承與多型

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

struct Base {
    void hello() { cout << "Base::hello "; }
    virtual void who() { cout << "Base::who "; }
    virtual ~Base() = default;
};
struct Derived : Base {
    void hello() { cout << "Derived::hello "; }
    void who() override { cout << "Derived::who "; }
};

void by_value(Base b) { b.who(); }
void by_ref(Base& b) { b.who(); }

int main() {
    Derived d;
    Base* p = &d;
    p->hello();
    p->who();
    cout << "\n";
    by_value(d);
    by_ref(d);
    cout << "\n";
    return 0;
}
```
!!!
```output
Base::hello Derived::who 
Base::who Derived::who 
```

- `hello` 不是 `virtual`：依照 **指標的型別**（`Base*`）在編譯時決定，叫到 `Base::hello`（**靜態繫結**）。
- `who` 是 `virtual`：依照 **物件真正的型別**（`Derived`）在執行時決定（**動態繫結**）。
- `by_value(d)`：傳值時只複製了 `Derived` 裡的 `Base` 部分，物件被 **切割 (slicing)** 成一個真正的 `Base`，所以叫到 `Base::who`。多型一定要透過 **指標或參考**。

??? 預測輸出
```cpp
#include <iostream>
using namespace std;

struct Part {
    const char* n;
    Part(const char* s) : n(s) { cout << "+" << n << " "; }
    ~Part() { cout << "-" << n << " "; }
};

struct Base {
    Part p{"BasePart"};
    Base() { cout << "Base() "; show(); }
    virtual void show() { cout << "[Base::show] "; }
    virtual ~Base() { cout << "~Base() "; }
};

struct Derived : Base {
    Part q{"DerivedPart"};
    Derived() { cout << "Derived() "; show(); }
    void show() override { cout << "[Derived::show] "; }
    ~Derived() override { cout << "~Derived() "; }
};

int main() {
    Base* b = new Derived;
    cout << "\n";
    delete b;
    cout << "\n";
    return 0;
}
```
!!!
```output
+BasePart Base() [Base::show] +DerivedPart Derived() [Derived::show] 
~Derived() -DerivedPart ~Base() -BasePart 
```

- **建構順序由內而外**：先建構父類別（父類別的成員 → 父類別建構子本體），再建構子類別的成員，最後是子類別建構子本體。
- **解構順序完全相反**。
- 在 **父類別的建構子裡** 呼叫虛擬函式，叫到的是 **父類別的版本**：這時子類別的部分還沒建構，物件「目前還只是 Base」。
- 因為 `~Base()` 是 `virtual`，`delete b`（`Base*`）才會正確地呼叫 `~Derived()`。

??? 觀念
如果上一題的 `~Base()` **不是** `virtual`，`delete b;` 會發生什麼事？什麼時候解構子一定要是 `virtual`？
!!!
透過父類別指標刪除子類別物件，而父類別的解構子不是 `virtual`，是 **未定義行為**。實際上通常只會呼叫 `~Base()`：`~Derived()` 不會執行，子類別的成員（`DerivedPart`）也不會解構，子類別擁有的資源就洩漏了。

規則：**只要一個類別打算被當成多型的父類別使用**（有任何虛擬函式、或會透過父類別指標刪除子類別物件），它的解構子就要是 `virtual`（或者是 `protected` 而且非虛擬，禁止透過父類別指標刪除）。

??? 觀念
1. 抽象類別是什麼？`class Shape { public: virtual double area() const = 0; };` 可以 `Shape s;` 嗎？
2. 「組合優於繼承」是什麼意思？什麼時候該用繼承？
!!!
1. 有至少一個 **純虛擬函式**（`= 0`）的類別是抽象類別，**不能建立物件**（`Shape s;` 是編譯錯誤），只能當父類別，由子類別實作所有純虛擬函式後才能建立。它用來定義 **介面**：「所有圖形都能算面積」。
2. - **繼承** 表示 **is-a**（「圓形是一種圖形」），子類別必須在任何使用父類別的地方都能正確替代（里氏替換原則）。
   - **組合** 表示 **has-a**（「車子有一個引擎」），把其他物件當成員。

   組合的耦合比較低、比較有彈性（可以在執行時替換成員）。只為了「重用程式碼」而繼承，常常會繼承到不該有的介面（例如 `Stack` 繼承 `vector` 之後，使用者可以從中間插入，破壞堆疊的性質）。只有真的需要 **多型**（用父類別指標操作不同的子類別）時才用公開繼承。

@@@ 09 | 抽象資料型別與程式設計

??? 寫程式
為一個 **有界堆疊 (BoundedStack)**（最多放 `capacity` 個 `int`）寫出規格：每個操作的 **前置條件**、**後置條件**，以及類別的 **不變量**。操作有 `push(x)`、`pop()`、`top()`、`size()`、`empty()`、`full()`。
!!!
**不變量**：`0 ≤ size() ≤ capacity`；`empty() == (size() == 0)`；`full() == (size() == capacity)`。

| 操作 | 前置條件 | 後置條件 |
|---|---|---|
| `push(x)` | `!full()` | `size()` 加 1；`top() == x`；其他元素不變 |
| `pop()` | `!empty()` | `size()` 減 1；移除的是原本的 `top()`；其他元素不變 |
| `top()` | `!empty()` | 回傳最後放入、還沒移除的元素；堆疊不變 |
| `size()` / `empty()` / `full()` | 無 | 堆疊不變 |

規格只說「做什麼」，不說「怎麼做」（陣列或串列都可以實作）。測試就是照著這些條件寫：例如「push 之後 top 一定是剛放的值」、「滿了之後 push 必須被拒絕」。

??? 觀念
呼叫者違反前置條件時（例如對空堆疊 `pop()`），函式有四種處理方式。列出來並說明各自適合的情況。
!!!
1. **不檢查（未定義行為）**：前置條件寫在文件裡，由呼叫者負責。最快，適合效能要求高、呼叫者可信任的底層函式（例如 `vector::operator[]`）。
2. **`assert` 檢查**：除錯版會中止並指出錯誤位置，正式版（`NDEBUG`）不檢查。適合「違反了就是程式有 bug」的情況。
3. **丟出例外**：例如 `vector::at` 丟 `out_of_range`。適合呼叫者有機會、也有理由處理的錯誤，而且無法事先輕易檢查的情況。
4. **回傳錯誤碼 / 特殊值**（`bool`、`optional`、`expected`）：呼叫者必須檢查。適合「失敗是正常的、預期中的情況」（例如查詢找不到）。

重點是 **在規格裡寫清楚** 選了哪一種，讓呼叫者知道該負什麼責任。

??? 找錯
下面的設計違反了 SOLID 的哪一個原則？怎麼改？

```cpp
double area(const Shape& s) {
    switch (s.kind) {
        case CIRCLE: return 3.14159 * s.r * s.r;
        case RECT:   return s.w * s.h;
        // 每新增一種圖形，就要回來改這裡，還有 perimeter()、draw()……
    }
    return 0;
}
```
!!!
違反 **開放封閉原則 (Open-Closed Principle)**：程式應該「對擴充開放、對修改封閉」。這裡每新增一種圖形，就要修改所有用到 `switch (s.kind)` 的函式，容易漏改，而且要重新測試舊的程式碼。

改法：用 **多型**，讓每種圖形自己實作行為：

```cpp
struct Shape {
    virtual double area() const = 0;
    virtual ~Shape() = default;
};
struct Circle : Shape { double r; double area() const override { return 3.14159 * r * r; } };
struct Rect   : Shape { double w, h; double area() const override { return w * h; } };
```

新增圖形只要新增一個類別，舊的程式碼完全不用動。（如果種類固定、而操作常常增加，`variant` + `visit` 反而比較合適，這是取捨。）

??? 觀念
1. 「高內聚、低耦合」是什麼意思？
2. pimpl 慣用法解決了什麼問題？代價是什麼？
!!!
1. - **高內聚**：一個模組 / 類別裡的東西都是為了 **同一個目的**，關係很緊密（例如 `Account` 只管帳戶餘額和交易，不管畫面顯示）。
   - **低耦合**：模組之間的依賴 **越少越好、越窄越好**，只透過清楚的介面溝通；一個模組改了實作，其他模組不需要跟著改。

   兩者合起來讓程式容易理解、測試和修改。
2. **pimpl（pointer to implementation）**：類別只放一個指向實作結構的指標 `unique_ptr<Impl> p;`，所有私有成員都放在 `.cpp` 檔的 `Impl` 裡。

   解決的問題：
   - 修改私有成員時，標頭檔不用改，**使用這個類別的檔案不用重新編譯**，大型專案的編譯時間大幅縮短；
   - 也真正隱藏了實作細節（ABI 穩定）。

   代價：
   - 多一次堆積配置和一層間接存取（比較慢）；
   - 要自己處理複製（`unique_ptr` 不能複製）；
   - 解構子必須寫在 `.cpp` 裡（`Impl` 在那裡才是完整型別）。

@@@ 10 | 模板與泛型程式設計

??? 判斷能不能編譯
```cpp
template <typename T>
T my_max(T a, T b) { return a > b ? a : b; }

my_max(3, 7);              // (a)
my_max(3, 4.5);            // (b)
my_max<double>(3, 4.5);    // (c)
my_max(string("a"), "b");  // (d)
```
!!!
- (a) 可以，`T` 推導成 `int`。
- (b) **不行**：第一個參數推導出 `T = int`，第二個推導出 `T = double`，**互相衝突**，模板引數推導失敗。（推導時不考慮隱式轉換。）
- (c) 可以：明確指定 `T = double`，3 會被轉成 3.0。
- (d) **不行**：`string` 和 `const char*` 衝突。要寫 `my_max<string>(...)` 或兩個都用 `string`。

??? 預測輸出
```cpp
#include <iostream>
#include <type_traits>
using namespace std;

template <typename T>
struct Counter {
    static int count;
    Counter() { count++; }
};
template <typename T> int Counter<T>::count = 0;

template <typename T> const char* kind() { return "general"; }
template <> const char* kind<int>() { return "int"; }

template <typename T>
const char* describe(T) {
    if constexpr (is_integral_v<T>) return "integral";
    else if constexpr (is_floating_point_v<T>) return "floating";
    else return "other";
}

int main() {
    Counter<int> a, b;
    Counter<double> c;
    cout << Counter<int>::count << " " << Counter<double>::count << "\n";
    cout << kind<int>() << " " << kind<char>() << "\n";
    cout << describe(1) << " " << describe(2.5) << " " << describe("x") << "\n";
    return 0;
}
```
!!!
```output
2 1
int general
integral floating other
```

- `Counter<int>` 和 `Counter<double>` 是 **兩個不同的類別**，各有自己的 `static` 成員。
- `kind<int>` 有 **完全特化** 的版本，其他型別用一般版本。
- `if constexpr` 在 **編譯時** 依照型別選擇分支，沒選到的分支根本不會被編譯（所以裡面可以寫對其他型別不合法的程式碼）。`"x"` 的型別是 `const char*`，不是整數也不是浮點數。

??? 觀念
1. 為什麼模板的定義通常要寫在 **標頭檔** 裡？把定義寫在 `.cpp`、標頭檔只放宣告，會發生什麼錯誤？
2. `template <typename T> void f(T x) { x.foo(); }`：寫這個模板時有沒有錯？什麼時候才會發現錯誤？
!!!
1. 模板本身不是程式碼，而是「產生程式碼的藍圖」。編譯器要在 **使用的地方**（例如 `main.cpp` 呼叫 `f<int>`）看到完整的定義，才能 **實例化** 出 `f<int>` 的程式碼。如果定義只在 `f.cpp` 裡，編譯 `main.cpp` 時看不到定義，只能留下一個呼叫；而 `f.cpp` 裡從來沒有人用 `f<int>`，所以也沒有產生它 → 連結錯誤 `undefined reference to 'void f<int>(int)'`。
2. 模板本身沒有錯；它對 `T` 有一個 **隱含的要求**：「`T` 要有成員函式 `foo()`」。只有在用某個型別 **實例化** 時（例如 `f(3)`），才會檢查並報錯（`request for member 'foo' in 'x', which is of non-class type 'int'`），錯誤訊息常常又長又難懂。C++20 的 **concepts** 可以把要求寫成明確的條件，錯誤訊息會直接說「`int` 不滿足某個 concept」。

??? 寫程式
寫一個函式模板 `sum_all`，用 **變長模板 (variadic template)** 加上 **摺疊運算式 (fold expression)**，回傳所有參數的總和：`sum_all(1, 2, 3)` 是 6，`sum_all(1.5, 2)` 是 3.5。
!!!
```cpp
template <typename... Ts>
auto sum_all(Ts... xs) {
    return (xs + ...);           // 右摺疊：x1 + (x2 + (x3 + ...))
}
```

- `typename... Ts` 是 **型別參數包**，`Ts... xs` 是 **函式參數包**，可以接收任意個數、任意型別的參數。
- `(xs + ...)` 是 C++17 的摺疊運算式，把 `+` 套用在所有參數之間。
- 回傳型別用 `auto`，由運算結果決定（`1.5 + 2` 是 `double`）。
- 沒有參數時 `(xs + ...)` 會編譯錯誤；要支援的話寫成 `(0 + ... + xs)`（帶初始值的左摺疊）。

@@@ 11 | STL 深入

??? 預測輸出
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <vector>
using namespace std;

void show(const vector<int>& v) { for (int x : v) cout << x << " "; cout << "| "; }

int main() {
    vector<int> v = {1, 2, 3, 2, 4, 2};
    auto it = remove(v.begin(), v.end(), 2);
    cout << v.size() << " " << (it - v.begin()) << " ";
    v.erase(it, v.end());
    show(v);
    cout << "\n";

    vector<int> w = {1, 1, 2, 2, 1, 3, 3};
    w.erase(unique(w.begin(), w.end()), w.end());
    show(w);
    cout << "\n";

    vector<double> d = {0.5, 0.5, 0.5};
    cout << accumulate(d.begin(), d.end(), 0) << " " << accumulate(d.begin(), d.end(), 0.0) << "\n";
    return 0;
}
```
!!!
```output
6 3 1 3 4 | 
1 2 1 3 | 
0 1.5
```

- `remove` **不會真的刪除**：它把「要保留的」元素往前搬，回傳新的結尾，`size()` 還是 6。要再呼叫 `erase` 才會真的縮小（**erase-remove 慣用法**）。C++20 可以直接用 `std::erase(v, 2)`。
- `unique` 只移除 **相鄰** 的重複，所以兩個 1 之間隔了 2 時，後面的 1 還在。要移除全部重複，先 `sort`。
- `accumulate` 的回傳型別由 **初始值** 決定：`0` 是 `int`，每一步都截斷成整數（0 + 0.5 → 0）；要寫 `0.0`。

??? 預測輸出
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <vector>
using namespace std;

int main() {
    map<string, int> m;
    m["apple"] = 3;
    if (m["banana"] == 0) cout << "zero ";
    cout << m.size() << " " << m.count("cherry") << " " << m.size() << "\n";

    vector<int> v = {1, 3, 3, 3, 5, 7};
    auto lo = lower_bound(v.begin(), v.end(), 3);
    auto hi = upper_bound(v.begin(), v.end(), 3);
    auto x = lower_bound(v.begin(), v.end(), 4);
    cout << (lo - v.begin()) << " " << (hi - v.begin()) << " " << (hi - lo) << " " << *x << "\n";
    return 0;
}
```
!!!
```output
zero 2 0 2
1 4 3 5
```

- `m["banana"]` 在 key 不存在時會 **自動插入**（值初始化成 0），所以 `size()` 變成 2。只想查詢的話用 `count`、`find` 或 `contains`（C++20），它們不會插入。
- `lower_bound`：第一個 **≥** 值的位置；`upper_bound`：第一個 **>** 值的位置；兩者相減就是該值出現的次數。找 4 時第一個 ≥ 4 的是 5。範圍必須已經排序。

??? 觀念
1. `vector`、`deque`、`list` 在 **中間插入** 和 **隨機存取** 的複雜度各是多少？
2. `set` 和 `unordered_set` 該怎麼選？
3. `push_back(Obj(1, 2))` 和 `emplace_back(1, 2)` 差在哪裡？
!!!
1. | | 中間插入 | 隨機存取 `[i]` | 尾端插入 |
   |---|---|---|---|
   | `vector` | O(n) | O(1) | 攤銷 O(1) |
   | `deque` | O(n) | O(1) | O(1)（頭尾都是） |
   | `list` | O(1)（已有迭代器時） | 不支援（O(n) 走過去） | O(1) |

   實務上 `vector` 因為記憶體連續、快取友善，通常是最快的預設選擇。
2. - `set`：平衡樹，O(log n)，**有排序**，可以 `lower_bound`、依序走訪。
   - `unordered_set`：雜湊表，平均 O(1) 但最壞 O(n)，**沒有順序**，key 需要雜湊函數。

   只需要「有沒有這個元素」而且很在乎速度時用 `unordered_set`；需要順序、範圍查詢、或要保證最壞情況時用 `set`。
3. `push_back(Obj(1, 2))` 先建構一個 **暫時物件**，再把它移動（或複製）進容器；`emplace_back(1, 2)` 把參數 **直接轉交給建構子，在容器的空間裡就地建構**，省掉暫時物件。對簡單型別差別不大。

??? 找錯
下面的程式想刪除 `map` 中所有值為 0 的項目，哪裡有問題？

```cpp
for (auto it = m.begin(); it != m.end(); ++it)
    if (it->second == 0) m.erase(it);
```
!!!
`erase(it)` 之後 `it` 就 **失效** 了（它指向的節點已經被刪除），接著 `++it` 是未定義行為。

正確寫法：用 `erase` 的回傳值（指向下一個元素的迭代器）：

```cpp
for (auto it = m.begin(); it != m.end(); ) {
    if (it->second == 0) it = m.erase(it);
    else ++it;
}
```

C++20 可以直接寫 `std::erase_if(m, [](const auto& p) { return p.second == 0; });`。

@@@ 12 | 字串與輸入輸出

??? 預測輸出
```cpp
#include <iostream>
#include <sstream>
#include <string>
#include <iomanip>
using namespace std;

int main() {
    string s = "hello world";
    cout << s.find("o") << " " << s.rfind("o") << " " << (s.find("xyz") == string::npos) << "\n";
    cout << s.substr(6) << "|" << s.substr(0, 4) << "|" << s.substr(3, 100) << "\n";

    istringstream in("10,20,,30");
    string tok;
    int cnt = 0;
    while (getline(in, tok, ',')) { cout << "[" << tok << "]"; cnt++; }
    cout << " " << cnt << "\n";

    cout << fixed << setprecision(2) << 3.14159 << " " << setw(6) << 2.5 << "|" << "\n";
    return 0;
}
```
!!!
```output
4 7 1
world|hell|lo world
[10][20][][30] 4
3.14   2.50|
```

- `find` 回傳第一次出現的位置，`rfind` 從後面找；找不到回傳 `string::npos`。
- `substr(pos, len)`：`len` 超過字串尾端時只取到結尾，不會出錯（但 `pos` 超過長度會丟出 `out_of_range`）。
- `getline` 用 `,` 切割時，兩個逗號之間會得到 **空字串**。
- `fixed` + `setprecision(2)`：小數點後固定 2 位；`setw(6)` 只影響 **下一個** 輸出，寬度 6 靠右。

??? 找錯
下面的程式想先讀一個整數 n，再讀一整行的名字。輸入是：
```
3
Amy Chen
```
但 `name` 讀到的是空字串。為什麼？怎麼改？

```cpp
int n;
string name;
cin >> n;
getline(cin, name);
```
!!!
`cin >> n` 讀完 `3` 之後，**換行字元還留在輸入緩衝區裡**。`getline` 讀到這個換行就認為「這一行結束了」，所以得到空字串。

改法：在 `getline` 之前把那一行剩下的部分丟掉：

```cpp
cin >> n;
cin.ignore(numeric_limits<streamsize>::max(), '\n');   // 丟到換行為止
getline(cin, name);
```

或者用 `getline(cin >> ws, name);`（`ws` 會吃掉前面的空白和換行，但也會吃掉名字前面的空白）。

??? 觀念
1. `string_view` 是什麼？下面的程式有什麼問題？
```cpp
string_view first_word(const string& s) { return string_view(s).substr(0, s.find(' ')); }
string_view w = first_word("hello world");
cout << w;
```
2. 讀入直到檔案結尾，`while (!cin.eof()) { cin >> x; sum += x; }` 有什麼問題？
!!!
1. `string_view` 是 **不擁有資料** 的字串「視窗」（一個指標 + 長度），複製和取子字串都不配置記憶體，很快。問題是：`"hello world"` 先被轉成一個 **暫時的 `string`** 傳給 `first_word`，這個暫時物件在那一行結束時就銷毀了，`w` 指向已經被釋放的記憶體 → **懸空**，`cout << w` 是未定義行為。`string_view` 絕對不能比它看的那個字串活得久。
2. `eof()` 只有在 **讀取失敗之後** 才會變成真。讀完最後一個數字時還沒碰到結尾，迴圈會多跑一次：`cin >> x` 失敗，`x` 的值沒有被更新（C++11 起會設成 0），但 `sum += x` 還是執行了。另外如果輸入有不是數字的東西，`cin` 進入失敗狀態但 `eof()` 永遠是假，**無窮迴圈**。正確寫法：`while (cin >> x) sum += x;`。

??? 寫程式
用 `istringstream` 寫一個函式，把一行 `"name score1 score2 ..."`（分數個數不固定）解析出名字和平均分數。分數一個都沒有時平均是 0。
!!!
```cpp
#include <sstream>
#include <string>
using namespace std;

bool parse(const string& line, string& name, double& avg) {
    istringstream in(line);
    if (!(in >> name)) return false;        // 空行
    double sum = 0, x;
    int cnt = 0;
    while (in >> x) { sum += x; cnt++; }    // 讀到失敗（行尾或非數字）為止
    avg = cnt ? sum / cnt : 0;
    return true;
}
```

`istringstream` 把一個字串當成輸入串流，`>>` 會自動跳過空白，用起來和讀 `cin` 一樣。每一行用一個新的串流解析，一行格式錯誤也不會影響下一行。

@@@ 13 | 例外處理

??? 預測輸出
```cpp
#include <iostream>
#include <stdexcept>
using namespace std;

struct Guard {
    const char* n;
    Guard(const char* s) : n(s) {}
    ~Guard() { cout << "~" << n << " "; }
};

void level2() {
    Guard g("L2");
    throw out_of_range("bad index");
}

void level1() {
    Guard g("L1");
    level2();
    cout << "unreachable ";
}

int main() {
    try {
        level1();
    } catch (const logic_error& e) {
        cout << "logic: " << e.what() << "\n";
    } catch (const out_of_range& e) {
        cout << "range: " << e.what() << "\n";
    }
    try {
        throw 42;
    } catch (double) {
        cout << "double\n";
    } catch (...) {
        cout << "other\n";
    }
    return 0;
}
```
!!!
```output
~L2 ~L1 logic: bad index
other
```

- 例外往外傳時，沿途的區域物件會 **依序解構**（**堆疊回溯 stack unwinding**），所以 `~L2`、`~L1` 先印出來。這就是 RAII 在例外發生時仍然能釋放資源的原因。
- `out_of_range` 是 `logic_error` 的子類別，`catch` 由上往下找 **第一個符合的**，所以被 `logic_error` 接走了。**子類別要寫在前面**（gcc 會警告後面的 catch 永遠不會被執行）。
- 例外的型別比對 **不做一般的型別轉換**：`int` 不會被 `catch (double)` 接住，最後由 `catch (...)` 接住。

??? 觀念
說明 **基本保證**、**強保證**、**不丟保證** 的意思。下面的函式提供哪一種？怎麼改成強保證？

```cpp
void Roster::add(const string& name, int score) {
    names.push_back(name);      // 可能丟出 bad_alloc
    scores.push_back(score);    // 可能丟出 bad_alloc
}
```
!!!
- **不丟保證 (nothrow)**：保證不會丟出例外（例如解構子、`swap`、移動建構子）。
- **強保證 (strong)**：如果丟出例外，物件的狀態 **和呼叫前完全一樣**（像交易一樣，要嘛全部成功、要嘛什麼都沒發生）。
- **基本保證 (basic)**：如果丟出例外，不會洩漏資源，物件仍然處於 **有效**（不變量成立）但可能被改變的狀態。

這個函式只有 **基本保證**（甚至可能連不變量都破壞）：如果第一個 `push_back` 成功、第二個失敗，`names` 多了一個名字而 `scores` 沒有，兩個 vector 長度不一致。

改成強保證：

```cpp
void Roster::add(const string& name, int score) {
    names.push_back(name);
    try {
        scores.push_back(score);
    } catch (...) {
        names.pop_back();       // 復原第一步（pop_back 不會丟例外）
        throw;                  // 重新丟出
    }
}
```

另一種技巧是「先在複本上做完所有可能失敗的事，最後用不會丟例外的 `swap` 交換」（copy-and-swap）。

??? 觀念
1. 為什麼要用 `catch (const exception& e)` 而不是 `catch (exception e)`？
2. 解構子為什麼不應該丟出例外？
3. 一個標了 `noexcept` 的函式裡丟出了例外（沒有在函式裡被接住），會發生什麼事？
!!!
1. **傳值會切割**：子類別的例外物件被複製成一個基底類別 `exception`，`what()` 回傳的就不是原本的訊息了（多型失效），而且多了一次複製。用 `const` 參考才能保留真正的型別。
2. 解構子常常在 **堆疊回溯的過程中** 被呼叫（已經有一個例外在傳遞）。如果這時解構子又丟出第二個例外，C++ 沒辦法同時處理兩個，會直接呼叫 `std::terminate` 結束程式。所以 C++11 起解構子預設就是 `noexcept`。
3. 直接呼叫 **`std::terminate`**，程式立刻中止，**不會** 往外傳給呼叫者的 `catch`（堆疊回溯也不保證會發生）。`noexcept` 是一個承諾，違反它就是致命錯誤。

??? 觀念
什麼情況 **應該** 用例外？什麼情況 **不應該**？各舉兩個例子。
!!!
**應該用例外**：
- **錯誤無法在發生的地方處理**，需要往上傳好幾層才有人知道怎麼辦（例如解析設定檔時深層的函式發現格式錯誤）。
- **建構子失敗**（建構子沒有回傳值，只能丟例外）。
- 違反前置條件、但呼叫者有理由處理的情況（例如 `vector::at` 的越界）。

**不應該用例外**：
- **正常的、預期中的情況**：例如「在 map 裡找不到 key」、「使用者輸入了錯誤的密碼」，應該用回傳值（`optional`、`bool`）。
- **程式的 bug**（不可能發生的情況）：用 `assert`，讓它在除錯時立刻停下來。
- 效能極度敏感的迴圈裡（丟出例外的成本很高）。
- 解構子裡。

@@@ 14 | 編譯模型與程式組織

??? 觀念
`util.h` 裡寫了下面的內容，被 `a.cpp` 和 `b.cpp` 同時 include。連結時會出什麼錯？C++ 有哪些方法可以修正（至少三種）？

```cpp
#pragma once
int counter = 0;
int twice(int x) { return 2 * x; }
```
!!!
`multiple definition of 'counter'` 和 `multiple definition of 'twice'`：違反 **單一定義規則 (ODR)**。`a.cpp`、`b.cpp` 是兩個獨立的 **編譯單元**，各自都有一份定義；`#pragma once`（引入防護）只防止同一個編譯單元 include 兩次。

修正方式：
1. 標頭檔只放 **宣告**：`extern int counter;`、`int twice(int x);`，定義放在 **一個** `.cpp` 檔裡。
2. 用 **`inline`**：`inline int twice(int x) { ... }`、C++17 的 `inline int counter = 0;`。`inline` 允許在多個編譯單元裡出現相同的定義，連結器會只保留一份。
3. 用 **`static`** 或 **匿名命名空間**：每個編譯單元各有一份 **獨立的** `counter` 和 `twice`（內部連結）。注意這樣 `a.cpp` 和 `b.cpp` 的 `counter` 是 **兩個不同的變數**，不是共用的。
4. 函式也可以寫成 `constexpr`（隱含 `inline`）。

??? 觀念
`static` 在 C++ 裡有四種意思，分別說明：

```cpp
static int a = 0;                         // (1) 在檔案層級
void f() { static int b = 0; }            // (2) 在函式裡
struct S { static int c; };               // (3) 在類別裡（資料）
struct T { static void g(); };            // (4) 在類別裡（函式）
```
!!!
1. **內部連結**：`a` 只有這個 `.cpp` 檔看得到，其他檔案用 `extern` 也拿不到。（C++ 比較推薦用匿名命名空間。）
2. **靜態儲存期**：`b` 在第一次執行到這一行時初始化（C++11 起是執行緒安全的），之後一直存在到程式結束，呼叫之間保留值；作用域仍然只在函式裡。
3. **類別共用的成員**：`c` 屬於整個類別，所有物件共用一份，不佔物件的空間；需要在一個 `.cpp` 裡定義（或在類別裡寫 `inline static int c = 0;`）。
4. **靜態成員函式**：不屬於任何物件，沒有 `this` 指標，只能存取靜態成員；呼叫時寫 `T::g()`。

??? 觀念
1. `using namespace std;` 寫在 **標頭檔** 裡有什麼問題？
2. 什麼是「靜態初始化順序問題」？怎麼避免？
!!!
1. 所有 include 這個標頭檔的檔案都會被迫把 `std` 的所有名字拉進全域，使用者 **沒辦法取消**。結果容易和使用者自己的名字衝突（例如自己定義了 `count`、`distance`、`max`），產生模稜兩可或悄悄呼叫錯函式的問題。標頭檔裡應該寫完整的 `std::string`；`using namespace` 最多只在 `.cpp` 檔裡、或函式裡使用。
2. 不同編譯單元的 **全域（靜態儲存期）物件**，誰先初始化是 **沒有規定的**。如果 `a.cpp` 的全域物件在建構時用到 `b.cpp` 的全域物件，而後者還沒初始化，就會用到未初始化的值。解法：把全域物件改成 **函式裡的 static 區域變數**，透過函式取得（第一次呼叫時才初始化，保證用的時候已經建好）：

   ```cpp
   Config& config() {
       static Config c;
       return c;
   }
   ```

??? 預測輸出
```cpp
#include <iostream>

#define SQUARE(x) x * x
#define STR(x) #x
#define CAT(a, b) a##b

namespace math {
    int value = 1;
    namespace detail { int value = 2; }
}

namespace {
    int hidden = 3;
}

int main() {
    std::cout << SQUARE(2 + 1) << " " << STR(1 + 2) << "\n";
    int CAT(var, 7) = 70;
    std::cout << var7 << " " << math::value << " " << math::detail::value << " " << hidden << "\n";
#ifdef NDEBUG
    std::cout << "release\n";
#else
    std::cout << "debug\n";
#endif
    return 0;
}
```
（用 `g++ -std=c++17 prog.cpp` 編譯，沒有加 `-DNDEBUG`。）
!!!
```output
5 1 + 2
70 1 2 3
debug
```

- `SQUARE(2 + 1)` 展開成 `2 + 1 * 2 + 1` = 5。巨集是文字替換，參數要加括號（C++ 裡應該改用 `constexpr` 函式）。
- `#x` 把參數變成字串；`a##b` 把兩段接成一個名字 `var7`。
- 巢狀命名空間用 `::` 存取；匿名命名空間裡的名字在這個檔案裡可以直接用（但其他檔案看不到）。
- 沒有定義 `NDEBUG`，走 `#else` 分支。

@@@ 15 | 現代 C++ 與總整理

??? 預測輸出
```cpp
#include <iostream>
#include <map>
#include <optional>
#include <string>
#include <tuple>
#include <variant>
using namespace std;

optional<int> parse(const string& s) {
    if (s.empty() || s.find_first_not_of("0123456789") != string::npos) return nullopt;
    return stoi(s);
}

int main() {
    map<string, int> m = {{"b", 2}, {"a", 1}};
    for (const auto& [k, v] : m) cout << k << "=" << v << " ";
    cout << "\n";

    auto [x, y, z] = make_tuple(1, 2.5, string("s"));
    cout << x + y << " " << z << "\n";

    cout << parse("123").value_or(-1) << " " << parse("12a").value_or(-1) << " "
         << parse("").has_value() << "\n";

    variant<int, string> v = 10;
    cout << v.index() << " ";
    v = string("hi");
    cout << v.index() << " " << get<string>(v) << " " << holds_alternative<int>(v) << "\n";
    return 0;
}
```
!!!
```output
a=1 b=2 
3.5 s
123 -1 0
0 1 hi 0
```

- **結構化綁定** `auto [k, v]` 把 pair / tuple / struct 拆成幾個名字；`map` 依 key 排序走訪。
- `optional<int>` 表示「可能沒有值」：`value_or(-1)` 沒有值時回傳預設值，比用 -1 當特殊值更清楚、也不會和合法的值混淆。
- `variant<int, string>` 是型別安全的標記聯合：`index()` 是目前存放的是第幾個型別；`get<string>` 取值（型別不對會丟出 `bad_variant_access`）。

??? 觀念
`enum class` 和傳統的 `enum` 有哪些差別？下面哪幾行會編譯錯誤？

```cpp
enum Color { RED, GREEN };
enum class Light { RED, YELLOW, GREEN };     // (1)
enum class Dir { UP, DOWN };
int a = RED;                                 // (2)
int b = Dir::UP;                             // (3)
int c = static_cast<int>(Dir::DOWN);         // (4)
Dir d = UP;                                  // (5)
if (Dir::UP == 0) {}                         // (6)
```
!!!
- (1) 可以：`enum class` 的成員 **有自己的作用域**（`Light::RED`），不會和 `Color` 的 `RED` 衝突。如果兩個都是傳統 `enum`，`RED` 會重複定義。
- (2) 可以：傳統 `enum` 會 **隱式轉換** 成整數。
- (3) **錯誤**：`enum class` 不會隱式轉換成整數。
- (4) 可以：要明確轉型。
- (5) **錯誤**：要寫 `Dir::UP`。
- (6) **錯誤**：不能直接和整數比較。

`enum class` 的好處：名字不會汙染外層作用域、不會意外地和整數混用，型別更安全。

??? 分類
下面每一項是 **未定義行為 (UB)**、**未指定行為 (unspecified)**、還是 **實作定義行為 (implementation-defined)**？

1. `sizeof(int)` 是多少
2. `f() + g()` 誰先被呼叫
3. 有號整數溢位
4. `char` 是有號還是無號
5. 解參考空指標
6. 讀取未初始化的區域變數
7. 對負數右移 `-8 >> 1` 的結果（C++20 以前）
8. 修改字串字面值
!!!
1. **實作定義**：標準只規定最小範圍，實際大小由編譯器決定，而且 **必須寫在文件裡**（x86-64 上是 4）。
2. **未指定**：一定是其中一種順序，但標準不規定、編譯器也不用說明，甚至每次都可以不同。
3. **UB**。
4. **實作定義**（x86 上有號、ARM 上通常無號）。
5. **UB**。
6. **UB**。
7. **實作定義**（實際上幾乎都是算術右移，得到 -4；C++20 起規定為算術右移）。
8. **UB**（通常是 segmentation fault）。

差別：**UB** 的程式完全沒有保證，編譯器可以假設它不會發生並做出意想不到的最佳化；另外兩種都會得到某個合理的結果。

??? 觀念
1. `constexpr` 函式和一般函式有什麼不同？`constexpr int sq(int x) { return x * x; }`，`int a[sq(3)];` 可以嗎？`sq(n)`（`n` 是執行時讀入的）可以嗎？
2. 寫完程式後，有哪些工具可以幫忙抓出 UB 和記憶體錯誤？
!!!
1. `constexpr` 函式 **可以在編譯時計算**（只要參數都是編譯時常數），結果可以用在陣列大小、模板參數、`static_assert` 等需要常數的地方。
   - `int a[sq(3)];` **可以**：`sq(3)` 在編譯時算出 9。
   - `sq(n)` **也可以呼叫**，只是會在執行時計算，就像一般函式。（要強制只能在編譯時計算，C++20 用 `consteval`。）
2. - **編譯器警告**：`-Wall -Wextra`（未初始化、有號無號比較、格式字串、優先順序……），並把警告當錯誤看待。
   - **AddressSanitizer**（`-fsanitize=address`）：越界、use-after-free、double free、記憶體洩漏。
   - **UndefinedBehaviorSanitizer**（`-fsanitize=undefined`）：有號溢位、位移過量、除以 0、空指標存取……
   - **`_GLIBCXX_DEBUG`**：STL 容器的越界和迭代器檢查。
   - 本平台的 `--debug` 就是把這些全部打開。另外還有 Valgrind、靜態分析工具（clang-tidy）等。
