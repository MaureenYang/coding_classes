# 資料結構總複習考卷

> 涵蓋資料結構路線第 01 ~ 11 課（含 01b 複雜度考題）。題型有預測輸出、手動模擬、找錯、複雜度分析、寫程式、觀念說明；預測輸出的答案都是實際用 `g++ -std=c++17` 編譯執行的結果。
> 「手動模擬」的題目請真的拿紙筆畫出來，這是確認你懂一個資料結構最好的方法。

@@@ 01 | C++ 基礎與時間複雜度

??? 預測輸出
```cpp
#include <iostream>
#include <vector>
using namespace std;

int main() {
    vector<int> v;
    cout << (v.size() - 1 > 5) << "\n";
    int a = 100000;
    long long b = 1LL * a * a;
    cout << b << "\n";
    int x = 7;
    int &r = x;
    int *p = &x;
    r = 10;
    *p += 1;
    cout << x << "\n";
    return 0;
}
```
!!!
```output
1
10000000000
11
```

- `v.size()` 是 **無號數**（`size_t`），空的 vector `size() - 1` 不會變成 -1，而是繞回成一個超大的數，所以比 5 大。寫 `for (int i = 0; i < v.size() - 1; i++)` 遇到空 vector 就會出事；改寫成 `i + 1 < v.size()`。
- `a * a` 是兩個 `int` 相乘，10¹⁰ 會溢位；先乘 `1LL` 讓運算變成 `long long`。
- `r` 是 `x` 的 **參考（別名）**，`p` 指向 `x`，改它們就是改 `x`：10 再加 1 = 11。

??? 複雜度
寫出每段程式的時間複雜度（用 n 表示），並說明理由。

```cpp
// (a)
for (int i = 1; i < n; i *= 2)
    for (int j = 0; j < i; j++) cnt++;

// (b)
for (int i = 1; i <= n; i++)
    for (int j = i; j <= n; j += i) cnt++;

// (c)
for (int i = 0; i < n; i++)
    for (int j = i; j < n; j++) cnt++;

// (d)
int i = n;
while (i > 0) i /= 3;
```
!!!
- (a) **O(n)**：內層依序跑 1 + 2 + 4 + … + (小於 n 的最大 2 的冪次) < 2n 次。外層雖然是 log n 次，但不能直接相乘。
- (b) **O(n log n)**：內層跑 n/i 次，總共 n/1 + n/2 + … + n/n = n × (1 + 1/2 + … + 1/n) ≈ n ln n（調和級數）。
- (c) **O(n²)**：n + (n−1) + … + 1 = n(n+1)/2。
- (d) **O(log n)**：每次除以 3，log₃ n 次就到 0。

??? 找錯
下面的程式不管輸入的 n 是多少，一執行就當掉（Segmentation fault）。為什麼？怎麼改？

```cpp
int main() {
    int n;
    cin >> n;
    int cnt[10000000];
    // ...
}
```
!!!
`cnt` 是 **區域變數**，放在 **堆疊 (stack)** 上。10⁷ 個 `int` 是 40 MB，遠超過堆疊的大小（Linux 預設約 8 MB），所以 **堆疊溢位**。陣列的大小在編譯時就固定了，進入 `main` 時整個 40 MB 都要放在堆疊上，和實際用到多少（n）無關。

改法（任選一種）：
- 改成 **全域變數**（放在靜態資料區，不佔堆疊）：在 `main` 外面宣告 `int cnt[10000000];`。
- 用 `vector<int> cnt(n);`（資料放在 **堆積 heap** 上，而且大小剛好）。

??? 觀念
1. 題目限制 n ≤ 2 × 10⁵，時間限制 1 秒。O(n²)、O(n log n)、O(n√n) 哪些來得及？（以每秒約 10⁸ 次基本運算估計）
2. 為什麼大量輸入時要寫 `ios::sync_with_stdio(false); cin.tie(nullptr);`？
!!!
1. - O(n²) = 4 × 10¹⁰ → **來不及**（大約要 400 秒）。
   - O(n log n) ≈ 2 × 10⁵ × 18 ≈ 3.6 × 10⁶ → 輕鬆。
   - O(n√n) ≈ 2 × 10⁵ × 450 ≈ 9 × 10⁷ → 勉強可以（約 1 秒，看常數）。
2. 預設 `cin`/`cout` 要和 C 的 `scanf`/`printf` 同步，而且每次讀 `cin` 之前會先 flush `cout`，大量輸入輸出時很慢。關掉同步、解除綁定後速度可以快好幾倍。（關掉之後就 **不能** 再混用 `printf` 和 `cout`。）另外換行用 `"\n"` 而不是 `endl`，因為 `endl` 每次都會 flush。

??? 預測輸出
```cpp
#include <iostream>
#include <vector>
using namespace std;

struct P { int x, y; };

void f(vector<int> v) { v.push_back(1); }
void g(vector<int>& v) { v.push_back(2); }

int main() {
    vector<int> a;
    f(a);
    g(a);
    g(a);
    cout << a.size() << " " << a[0] << "\n";
    P p{1, 2};
    P q = p;
    q.x = 9;
    cout << p.x << " " << q.x << "\n";
    int* h = new int[3]{4, 5, 6};
    cout << h[1] + *(h + 2) << "\n";
    delete[] h;
    return 0;
}
```
!!!
```output
2 2
1 9
11
```

- `f` 是 **傳值**：收到的是 vector 的複本，`push_back` 加在複本上，函式結束複本就消失了。`g` 是 **傳參考**，真的改到 `a`。所以 `a` 只有兩個元素（都是 2）。
- 結構的 `=` 會複製每個成員，`q` 是獨立的一份。
- `new int[3]{4, 5, 6}` 在堆積配置陣列；`h[1]` 和 `*(h + 2)` 是 5 和 6。用 `new[]` 配置的要用 `delete[]` 釋放。

傳值會複製整個 vector（O(n)），大的容器只讀不改時要用 `const vector<int>&`。

??? 複雜度
寫出每段程式的時間複雜度（v 是排好序、有 n 個元素的 vector）：

```cpp
// (a)
for (int i = 0; i < n; i++)
    if (binary_search(v.begin(), v.end(), q[i])) cnt++;

// (b) 雙指標
int i = 0, j = 0;
while (i < n && j < n) {
    if (a[i] < b[j]) i++;
    else j++;
}

// (c) cnt 是 map<int,int>
for (int i = 0; i < n; i++) cnt[a[i]]++;

// (d)
for (int i = 0; i * i < n; i++) work();
```
!!!
- (a) **O(n log n)**：n 次二分搜尋，每次 O(log n)。
- (b) **O(n)**：每一輪 i 或 j 一定有一個加 1，兩個都最多加到 n，所以迴圈最多跑 2n 次。不要看到兩個指標就以為是 O(n²)。
- (c) **O(n log n)**：`map` 是平衡樹，每次 `[]` 是 O(log n)。換成 `unordered_map` 是平均 O(n)。
- (d) **O(√n)**：i 只跑到 √n。

@@@ 01b | 時間複雜度考題

??? 複雜度
下面每段程式的時間複雜度是多少？陷阱在哪裡？

```cpp
// (a) v 有 n 個元素
while (!v.empty()) v.erase(v.begin());

// (b) s 是長度 n 的 string
for (int i = 0; i < n; i++) t = t + s[i];

// (c) st 是有 n 個元素的 set<int>
for (int x : queries) if (st.count(x)) ans++;   // 共 q 個查詢

// (d)
for (int i = 0; i < (int)s.size(); i++)
    if (s.find('x') != string::npos) cnt++;
```
!!!
- (a) **O(n²)**：`erase(begin())` 要把後面所有元素往前搬一格，每次 O(n)。改成從尾端刪（`pop_back`）或直接 `clear()`。
- (b) **O(n²)**：`t = t + s[i]` 每次都建立一個新字串並複製整個 `t`。改成 `t += s[i]`（攤銷 O(1)）。
- (c) **O(q log n)**：`set` 是平衡樹，每次查詢 O(log n)。
- (d) **O(n²)**：`find` 本身是 O(n)，放在迴圈裡又跑 n 次。應該在迴圈外面算一次。

??? 複雜度
寫出下面遞迴的時間複雜度：

```cpp
int f(int n) { if (n <= 1) return 1; return f(n - 1) + 1; }              // (a)
int g(int n) { if (n <= 1) return 1; return g(n - 1) + g(n - 1); }       // (b)
void h(int l, int r) {                                                     // (c)
    if (r - l <= 1) return;
    int m = (l + r) / 2;
    h(l, m); h(m, r);
    for (int i = l; i < r; i++) work();                                    // O(1)
}
int k(int n) { if (n <= 1) return 1; return k(n / 2) + 1; }               // (d)
```
!!!
- (a) **O(n)**：T(n) = T(n−1) + O(1)，一條長度 n 的呼叫鏈。
- (b) **O(2ⁿ)**：T(n) = 2T(n−1) + O(1)，每層呼叫數加倍。（把兩次 `g(n-1)` 改成算一次再乘 2，就變 O(n)。）
- (c) **O(n log n)**：T(n) = 2T(n/2) + O(n)，跟合併排序一樣：log n 層，每層總共 O(n)。
- (d) **O(log n)**：T(n) = T(n/2) + O(1)。

??? 觀念
1. `vector::push_back` 的時間複雜度是「攤銷 O(1)」。這和「最壞情況 O(1)」有什麼不同？
2. n = 10⁵ 個點的圖，用 `int adj[n][n]` 的鄰接矩陣需要多少記憶體？記憶體限制 256 MB 時可以嗎？
!!!
1. **攤銷 O(1)**：把很多次操作的總成本平均分攤，每次平均是 O(1)；但 **單獨某一次** 可能很慢（擴容時要複製全部，O(n)）。**最壞情況 O(1)** 則保證每一次都是常數時間。對「總時間」來說兩者一樣；但如果每一次操作都有嚴格的時間要求（例如即時系統），攤銷就不夠了。
2. 10⁵ × 10⁵ × 4 bytes = 4 × 10¹⁰ bytes = **40 GB**，遠超過 256 MB，不行。稀疏的圖要用 **鄰接串列**（`vector<vector<int>>`），記憶體是 O(n + m)。

??? 計算
記憶體限制 256 MB，下面每一項大約要多少記憶體？可不可以？

1. `vector<long long> a(10000000);`
2. `bool vis[1000000000];`
3. 有 n = 10⁵ 個點、m = 10⁶ 條無向邊的鄰接串列 `vector<vector<int>>`
4. 長度 10⁸ 的 `string`
!!!
1. 10⁷ × 8 bytes = **80 MB**，可以。
2. 10⁹ × 1 byte = **1 GB**，不行。（通常代表演算法要換，例如改用雜湊表或座標壓縮。）
3. 無向邊每條存兩次，共 2 × 10⁶ 個 `int` = **8 MB**，加上 10⁵ 個 vector 本身的開銷（每個約 24 bytes ≈ 2.4 MB），約 **10 MB 多**，可以。
4. 10⁸ bytes ≈ **100 MB**，勉強可以，但如果又複製一份（例如傳值、`s + t`）就超過了。

估算方法：**個數 × 每個元素的大小**。`int` 4、`long long` 8、`double` 8、`bool`/`char` 1、指標 8 bytes。

??? 複雜度
用遞迴樹或展開法，求出下面遞迴關係式的複雜度：

1. T(n) = T(n/2) + O(n)
2. T(n) = 2T(n/2) + O(1)
3. T(n) = T(n − 1) + O(n)
4. T(n) = T(n − 1) + T(n − 2) + O(1)
!!!
1. **O(n)**：n + n/2 + n/4 + … < 2n。
2. **O(n)**：遞迴樹的節點總數是 1 + 2 + 4 + … + n ≈ 2n，每個節點 O(1)。（例如遞迴求陣列的最大值）
3. **O(n²)**：n + (n − 1) + … + 1。（例如選擇排序的遞迴寫法）
4. **O(φⁿ)**，φ ≈ 1.618，也就是指數級（樸素的費氏遞迴）；常常寫成 O(2ⁿ) 當上界。

@@@ 02 | 遞迴：河內塔與回溯法

??? 計算
1. n 個盤子的河內塔最少要移動幾次？寫出遞迴關係式並解出來。n = 10 是多少？
2. 遞迴的三個要素是什麼？用河內塔說明。
!!!
1. T(n) = 2T(n−1) + 1，T(1) = 1（先把上面 n−1 個移到中間柱、移最大的一個、再把 n−1 個移上去）。解得 **T(n) = 2ⁿ − 1**，n = 10 是 **1023** 次。
2. - **終止條件 (base case)**：n = 1（或 n = 0）時直接移動（或什麼都不做）。
   - **縮小問題**：每次遞迴處理 n − 1 個盤子，越來越接近終止條件。
   - **相信遞迴**：假設 `hanoi(n-1, ...)` 會正確地搬好 n−1 個盤子，只要想「怎麼用它組合出 n 個的解」。

??? 預測輸出
```cpp
#include <iostream>
#include <vector>
using namespace std;

int n = 3;
vector<int> cur;
vector<bool> used(4, false);
int cnt = 0;

void dfs() {
    if ((int)cur.size() == n) {
        cnt++;
        if (cnt <= 3) {
            for (int x : cur) cout << x;
            cout << "\n";
        }
        return;
    }
    for (int i = 1; i <= n; i++) {
        if (used[i]) continue;
        used[i] = true;
        cur.push_back(i);
        dfs();
        cur.pop_back();
        used[i] = false;
    }
}

int main() {
    dfs();
    cout << cnt << "\n";
    return 0;
}
```
!!!
```output
123
132
213
6
```

這是列出所有排列的回溯法：每一層選一個還沒用過的數字，遞迴結束後 **撤銷選擇**（`pop_back`、`used[i] = false`）。排列依字典序產生，n = 3 共 3! = 6 個。

??? 找錯
下面的回溯法想列出 1 ~ n 的所有排列，但輸出完全不對。錯在哪裡？

```cpp
void dfs(vector<int>& cur, vector<bool>& used, int n) {
    if ((int)cur.size() == n) { print(cur); return; }
    for (int i = 1; i <= n; i++) {
        if (used[i]) continue;
        used[i] = true;
        cur.push_back(i);
        dfs(cur, used, n);
    }
}
```
!!!
遞迴回來之後 **沒有撤銷選擇**：少了 `cur.pop_back();` 和 `used[i] = false;`。結果 `cur` 越來越長、`used` 全部變成 `true`，只會印出第一個排列（`1 2 3 …`），之後的分支都被跳過了。

回溯法的模板：**做選擇 → 遞迴 → 撤銷選擇**，三步缺一不可。

??? 觀念
1. 樸素遞迴的費氏數列 `fib(n) = fib(n-1) + fib(n-2)` 為什麼很慢？怎麼改成 O(n)？
2. 一個遞迴函式在 n = 10⁶ 時當掉了，n = 10⁴ 時正常。最可能的原因是什麼？怎麼解決？
!!!
1. 同一個子問題被重複算了很多次（**重疊子問題**），呼叫次數是指數級的。改法：
   - **記憶化 (memoization)**：用陣列記住算過的結果，再遇到就直接回傳；
   - 或改成迴圈由小算到大（只需要前兩項）。

   兩者都是 O(n)。
2. **堆疊溢位**：遞迴深度 10⁶ 層，每層都佔一些堆疊空間，超過了堆疊的上限（Linux 約 8 MB）。解法：
   - 改寫成迴圈；
   - 或用自己的 `stack` 模擬遞迴（資料放在 heap）；
   - 本機測試時可以調大堆疊（`ulimit -s`），但不能依賴這個。

??? 預測輸出
下面的回溯法列出 {1, 2, 3} 的所有子集合，每一層決定「不選」或「選」`a[i]`：

```cpp
#include <iostream>
#include <vector>
using namespace std;

int a[] = {1, 2, 3};
int n = 3;
vector<int> cur;

void dfs(int i) {
    if (i == n) {
        cout << "[";
        for (size_t k = 0; k < cur.size(); k++) cout << (k ? " " : "") << cur[k];
        cout << "] ";
        return;
    }
    dfs(i + 1);              // 不選 a[i]
    cur.push_back(a[i]);     // 選 a[i]
    dfs(i + 1);
    cur.pop_back();          // 撤銷
}

int main() {
    dfs(0);
    cout << "\n";
    return 0;
}
```
!!!
```output
[] [3] [2] [2 3] [1] [1 3] [1 2] [1 2 3] 
```

每個元素都有「不選 / 選」兩種分支，n 個元素共 2ⁿ 個子集合，遞迴樹有 2ⁿ 個葉子。程式 **先走「不選」的分支**，所以第一個印出的是空集合；最後一層（i = 2，決定要不要選 3）變化最快，所以 `[]` 後面緊接著 `[3]`。

??? 觀念
N 皇后問題（每一列放一個皇后，任兩個皇后不能在同一行、同一條斜線上）：

1. 用回溯法時，「剪枝」剪掉的是什麼？
2. 怎麼用陣列在 O(1) 時間判斷位置 (r, c) 能不能放？兩條斜線的編號各是什麼？
!!!
1. 一放下皇后就檢查衝突，只要 **目前這一列** 和前面已經放好的皇后衝突，就 **不再往下遞迴**，整棵子樹都不用走。沒有剪枝的話要檢查 nⁿ 種放法，剪枝後實際走過的狀態少很多。
2. 用三個布林陣列記錄已經被佔用的：
   - `col[c]`：第 c 行。
   - `diag1[r + c]`：「/」方向的斜線，同一條線上 r + c 相同，範圍 0 ~ 2n − 2。
   - `diag2[r - c + n - 1]`：「\」方向的斜線，同一條線上 r − c 相同，加上 n − 1 讓索引不是負的。

   三個都沒被佔用才能放；放下時三個都設成 true，**回溯時記得改回 false**。

@@@ 03 | 動態陣列

??? 計算
自己實作的動態陣列，容量從 1 開始、滿了就 **加倍**。連續 `push_back` 17 個元素：

1. 最後的 size 和 capacity 是多少？
2. 一共發生幾次擴容？總共複製了幾個元素？
3. 如果改成每次容量 **+1**，總共複製幾個元素？
!!!
1. size = **17**，capacity = **32**（1 → 2 → 4 → 8 → 16 → 32）。
2. 擴容 **5 次**（在放第 2、3、5、9、17 個元素時），複製 1 + 2 + 4 + 8 + 16 = **31** 個元素，平均每次 push_back 不到 2 次複製 → 攤銷 O(1)。
3. 每次都要複製全部：0 + 1 + 2 + … + 16 = **136** 個。n 個元素時是 n(n−1)/2，O(n²)。

??? 找錯
下面的程式有時候會印出奇怪的數字，有時候正常。為什麼？

```cpp
vector<int> v = {1, 2, 3};
int &first = v[0];
int *last = &v.back();
for (int i = 0; i < 100; i++) v.push_back(i);
first = 10;
cout << *last << "\n";
```
!!!
**指標 / 參考失效**：`push_back` 時如果容量不夠，vector 會 **配置一塊新的記憶體、把資料搬過去、釋放舊的**。之後 `first` 和 `last` 還指向舊的那塊（已經被釋放），讀寫它們是未定義行為（use-after-free）。

「有時候正常」是因為只有在真的擴容時才會搬家。解法：擴容之後重新取得參考，或改存 **索引**（`v[0]`）而不是指標；如果事先知道大小，可以先 `reserve`。

??? 觀念
自己寫的 `MyVector` 用 `int *data` 指向 `new` 出來的陣列，解構子裡 `delete[] data`。如果沒有寫複製建構子和複製指定運算子，下面的程式會發生什麼事？什麼是「三法則」？

```cpp
MyVector a;
a.push_back(1);
MyVector b = a;
b.push_back(2);
```
!!!
預設的複製是 **淺複製**：`b.data` 和 `a.data` 指向 **同一塊** 記憶體。

- 修改 `b` 會影響 `a`（甚至 `b` 擴容時會 `delete[]` 那塊共用的記憶體，`a.data` 就變成懸空指標）。
- 程式結束時 `a`、`b` 的解構子各 `delete[]` 一次 → **double free**。

**三法則**：如果類別需要自己寫 **解構子**、**複製建構子**、**複製指定運算子** 其中一個（通常是因為它管理資源），那三個都要寫。複製時要配置新的記憶體並複製內容（**深複製**），複製指定還要處理自我指定。

??? 寫程式
在一個 **不在乎順序** 的 `vector<int> v` 中，寫出 O(1) 刪除第 `i` 個元素的程式碼。為什麼 `v.erase(v.begin() + i)` 是 O(n)？
!!!
```cpp
v[i] = v.back();      // 用最後一個元素蓋掉要刪的
v.pop_back();         // 刪掉最後一個（O(1)）
```

`erase` 要保持其他元素的順序，必須把 `i` 後面的所有元素往前搬一格，最壞要搬 n − 1 個。

??? 預測輸出
```cpp
#include <iostream>
#include <vector>
using namespace std;

int main() {
    vector<int> v = {1, 2, 3, 4, 5, 6};
    for (auto it = v.begin(); it != v.end(); ) {
        if (*it % 2 == 0) it = v.erase(it);
        else ++it;
    }
    v.insert(v.begin() + 1, 9);
    for (int x : v) cout << x << " ";
    cout << "| " << v.size() << " " << v.front() << " " << v.back() << "\n";
    return 0;
}
```
!!!
```output
1 9 3 5 | 4 1 5
```

- 在走訪時刪除元素，要用 **`erase` 的回傳值**（指向被刪元素的下一個）更新迭代器；刪除時 **不要** 再 `++it`，否則會跳過下一個元素，甚至越過 `end()`。
- 刪掉偶數後是 `1 3 5`，再在索引 1 插入 9 → `1 9 3 5`。
- `insert` 和 `erase` 在中間操作都是 O(n)（後面的元素要搬動）。

??? 觀念
自己實作的動態陣列在 `pop_back` 時也想縮小容量以節省記憶體。

1. 如果規則是「size 降到 capacity 的 **1/2** 時，容量減半」，會有什麼問題？舉一個操作序列。
2. 比較好的規則是什麼？為什麼？
!!!
1. 會 **反覆抖動 (thrashing)**。假設容量 8、size 是 5，`pop_back` 到 4（剛好一半）→ 縮成容量 4；接著 `push_back` 一次，size 5 > 4 → 又擴成 8；再 `pop_back` → 又縮……每次操作都觸發 O(n) 的重新配置，攤銷 O(1) 的保證就消失了。
2. **size 降到 capacity 的 1/4 才減半**。縮小之後 size 是新容量的 1/2，離「要擴大」和「要縮小」都還有一段距離，中間至少要做 Θ(n) 次操作才會再觸發重新配置，攤銷成本仍然是 O(1)。（STL 的 `vector` 乾脆不自動縮小，要縮小時呼叫 `shrink_to_fit`。）

@@@ 04 | 鏈結串列

??? 找錯
想在節點 `cur` 後面插入新節點 `node`，下面的寫法有什麼問題？畫圖說明。

```cpp
cur->next = node;
node->next = cur->next;
```
!!!
第一行執行後，`cur->next` 已經變成 `node`，原本後面那個節點的位址 **遺失了**。第二行的 `cur->next` 就是 `node` 自己，結果 `node->next = node`，形成 **自己指向自己的環**，後面的節點全部斷掉（而且洩漏）。

順序要反過來：**先接後面、再接前面**：

```cpp
node->next = cur->next;
cur->next = node;
```

??? 寫程式
寫出反轉單向串列的函式 `Node* reverse(Node* head)`，要求 O(n) 時間、O(1) 額外空間。

```cpp
struct Node { int val; Node* next; };
```
!!!
```cpp
Node* reverse(Node* head) {
    Node* prev = nullptr;
    Node* cur = head;
    while (cur) {
        Node* nxt = cur->next;   // 1. 先記住下一個
        cur->next = prev;        // 2. 反轉指標
        prev = cur;              // 3. 兩個指標往前走
        cur = nxt;
    }
    return prev;                 // prev 是新的頭
}
```

空串列（`head == nullptr`）和只有一個節點的串列都能正確處理。

??? 觀念
1. 快慢指標怎麼找到串列的 **中間節點**？怎麼判斷串列 **有沒有環**？
2. 「虛擬頭節點 (dummy head)」解決了什麼問題？
!!!
1. - **中間節點**：慢指標一次走 1 步、快指標一次走 2 步；快指標走到尾端時，慢指標剛好在中間。
   - **判斷有環**：同樣一快一慢；如果有環，快指標會在環裡追上慢指標（兩者相遇）；如果沒有環，快指標會先走到 `nullptr`。時間 O(n)、空間 O(1)。
2. 很多操作在處理 **第一個節點** 時要特別判斷（例如刪除 head、在 head 前插入，要修改 `head` 變數本身）。在最前面放一個不存資料的 dummy 節點，所有真正的節點都「有前一個節點」，就可以用同一套程式處理，最後回傳 `dummy.next`。

??? 觀念
LRU 快取需要做到 `get` 和 `put` 都是 O(1)。為什麼要用「**雙向** 串列 + 雜湊表」？只用其中一個、或改用單向串列，會卡在哪一步？
!!!
- **雜湊表**：key → 串列節點的位置，讓「找到某個 key」是 O(1)。只用串列的話，要從頭找，O(n)。
- **串列**：維持「最近使用」的順序，把一個節點移到最前面、刪掉最後一個都是 O(1)。只用雜湊表的話，沒辦法 O(1) 找出「最久沒用的那個」。
- **雙向**：從中間刪除一個節點時，需要修改它 **前一個節點** 的 `next`。單向串列只能從頭走才找得到前一個，O(n)；雙向串列有 `prev` 指標，直接 O(1)。

??? 預測輸出
建立 1 ~ 6 的串列，用虛擬頭節點刪除所有偶數，再反轉：

```cpp
#include <iostream>
using namespace std;

struct Node { int val; Node* next; };

int main() {
    Node* head = nullptr;
    Node* tail = nullptr;
    for (int i = 1; i <= 6; i++) {               // 用 tail 加到尾端
        Node* n = new Node{i, nullptr};
        if (!head) head = tail = n;
        else { tail->next = n; tail = n; }
    }
    Node dummy{0, head};                        // 虛擬頭節點
    for (Node* p = &dummy; p->next; ) {
        if (p->next->val % 2 == 0) {
            Node* dead = p->next;
            p->next = dead->next;
            delete dead;
        } else {
            p = p->next;
        }
    }
    head = dummy.next;
    Node* prev = nullptr;                       // 反轉
    while (head) { Node* nx = head->next; head->next = prev; prev = head; head = nx; }
    head = prev;
    int len = 0;
    for (Node* p = head; p; p = p->next) { cout << p->val << " "; len++; }
    cout << "| " << len << "\n";
    while (head) { Node* nx = head->next; delete head; head = nx; }
    return 0;
}
```
!!!
```output
5 3 1 | 3
```

- 用 `tail` 指標加到尾端是 O(1)；第一個節點時 `head` 和 `tail` 都要設定。
- **虛擬頭節點** `dummy` 讓第一個節點也「有前一個節點」，刪除 head 不用特別處理。刪除後 `p` **不前進**，因為 `p->next` 已經換成下一個節點，還要再檢查一次。
- 反轉後 `1 3 5` 變成 `5 3 1`。

??? 觀念
什麼情況下鏈結串列比陣列（`vector`）好？什麼情況下比較差？為什麼實務上大部分時候 `vector` 都比較快？
!!!
| 操作 | 陣列（vector） | 鏈結串列 |
|---|---|---|
| 存取第 i 個元素 | **O(1)** | O(n)，要從頭走 |
| 在已知位置插入 / 刪除 | O(n)，要搬動 | **O(1)**，只改指標 |
| 尾端加入 | 攤銷 O(1) | O(1)（有 tail 指標時） |
| 額外記憶體 | 少 | 每個節點多一個（或兩個）指標 |

串列適合 **頻繁在中間插入、刪除，而且手上已經有節點位置** 的情況（例如 LRU 快取把節點移到最前面），以及需要「插入後其他元素的位址不變」的情況。

`vector` 通常比較快，因為元素 **在記憶體中連續**，CPU 快取一次會載入相鄰的好幾個元素；串列的節點散落在記憶體各處，每走一步都可能 cache miss。另外每個節點都要 `new` 一次，配置的成本也很高。所以就算理論上串列的插入是 O(1)，n 不大時 `vector` 的 O(n) 搬動往往還是比較快。

@@@ 05 | 堆疊、佇列、雙端佇列

??? 預測輸出
```cpp
#include <iostream>
#include <stack>
#include <string>
using namespace std;

bool valid(const string& s) {
    stack<char> st;
    for (char c : s) {
        if (c == '(' || c == '[' || c == '{') st.push(c);
        else {
            if (st.empty()) return false;
            char t = st.top(); st.pop();
            if ((c == ')' && t != '(') || (c == ']' && t != '[') || (c == '}' && t != '{')) return false;
        }
    }
    return st.empty();
}

int main() {
    for (string s : {"([]{})", "([)]", "((", "())", ""})
        cout << valid(s);
    cout << "\n";
    return 0;
}
```
!!!
```output
10001
```

- `([]{})`：合法。
- `([)]`：`)` 遇到的堆疊頂端是 `[`，不配對。
- `((`：最後堆疊不是空的（有沒關的括號）。
- `())`：第三個 `)` 時堆疊已經空了。
- 空字串：合法。

三種錯誤（不配對、右括號多、左括號多）都要檢查，最後一個最容易漏掉。

??? 手動模擬
容量 K = 4 的環狀佇列，用 `head`（隊首的索引）和 `count`（元素個數）實作，新元素放在 `(head + count) % K`。一開始 `head = 0, count = 0`。依序執行：

`push 1, push 2, push 3, pop, pop, push 4, push 5, push 6`

1. 每次操作後 `head` 和 `count` 是多少？
2. 最後陣列 `a[0..3]` 的內容是什麼？從隊首到隊尾依序是哪些數？
3. 再 `push 7` 會怎樣？
!!!
| 操作 | head | count | 放在哪一格 |
|---|---|---|---|
| push 1 | 0 | 1 | a[0] |
| push 2 | 0 | 2 | a[1] |
| push 3 | 0 | 3 | a[2] |
| pop（取出 1） | 1 | 2 | |
| pop（取出 2） | 2 | 1 | |
| push 4 | 2 | 2 | a[3] |
| push 5 | 2 | 3 | a[(2+3)%4] = a[0] |
| push 6 | 2 | 4 | a[1] |

1. 見上表。
2. `a = {5, 6, 3, 4}`；從 `head = 2` 開始依序是 **3, 4, 5, 6**。
3. `count == K`，佇列 **滿了**，push 要拒絕（或回報錯誤）。

用 `count` 判斷空（`count == 0`）和滿（`count == K`）最清楚；如果只用 `head` 和 `tail` 兩個索引，空和滿都是 `head == tail`，分不出來。

??? 預測輸出
用單調堆疊找「下一個更大的元素」（右邊第一個比自己大的數，沒有就是 -1）：

```cpp
#include <iostream>
#include <stack>
#include <vector>
using namespace std;

int main() {
    vector<int> a = {2, 1, 5, 3, 6, 4};
    int n = a.size();
    vector<int> ans(n, -1);
    stack<int> st;                       // 存索引，對應的值由底到頂遞減
    for (int i = 0; i < n; i++) {
        while (!st.empty() && a[st.top()] < a[i]) {
            ans[st.top()] = a[i];
            st.pop();
        }
        st.push(i);
    }
    for (int x : ans) cout << x << " ";
    cout << "\n";
    return 0;
}
```
!!!
```output
5 5 6 6 -1 -1 
```

堆疊裡放的是「還沒找到答案」的索引。遇到 `a[i]` 時，所有比它小的都在這一刻找到答案，於是彈出。

??? 觀念
1. 上一題的程式有兩層迴圈，為什麼時間複雜度是 O(n) 而不是 O(n²)？
2. 陣列 `[1, 3, -1, -3, 5, 3, 6, 7]`、視窗大小 k = 3，滑動視窗最大值是什麼？單調 deque 裡存的是什麼、要維持什麼性質？
!!!
1. 每個索引 **最多被 push 一次、pop 一次**，所以 `while` 迴圈在整個程式中總共最多執行 n 次。總成本 = 外層 n 次 + 所有 pop 合計 n 次 = O(n)（攤銷分析）。
2. 答案是 **3 3 5 5 6 7**。
   - deque 存 **索引**，對應的值 **由前到後遞減**。
   - 新元素進來時，從尾端彈出所有比它小的（它們以後不可能是最大值）；
   - 隊首的索引如果已經滑出視窗（`<= i - k`）就從前端彈出；
   - 隊首永遠是目前視窗的最大值。

   每個元素最多進出 deque 各一次，O(n)。

??? 預測輸出
用堆疊計算 **後序表示法 (postfix)** 的運算式：

```cpp
#include <iostream>
#include <sstream>
#include <stack>
#include <string>
using namespace std;

long long eval_postfix(const string& expr) {
    stack<long long> st;
    istringstream in(expr);
    string tok;
    while (in >> tok) {
        if (tok == "+" || tok == "-" || tok == "*" || tok == "/") {
            long long b = st.top(); st.pop();     // 注意：先取出的是右運算元
            long long a = st.top(); st.pop();
            if (tok == "+") st.push(a + b);
            else if (tok == "-") st.push(a - b);
            else if (tok == "*") st.push(a * b);
            else st.push(a / b);
        } else {
            st.push(stoll(tok));
        }
    }
    return st.top();
}

int main() {
    cout << eval_postfix("3 4 + 2 * 7 -") << " "
         << eval_postfix("5 1 2 + 4 * + 3 -") << " "
         << eval_postfix("8 2 /") << "\n";
    return 0;
}
```
!!!
```output
7 14 4
```

- `3 4 + 2 * 7 -`：3、4 入堆疊；`+` 取出兩個算 7；2 入堆疊；`*` 算 14；7 入堆疊；`-` 算 14 − 7 = **7**。也就是 (3 + 4) × 2 − 7。
- `5 1 2 + 4 * + 3 -` = 5 + (1 + 2) × 4 − 3 = **14**。
- `8 2 /`：**先取出的是右運算元**（2），所以是 8 / 2 = 4，不是 2 / 8。減法和除法的順序弄反是最常見的錯誤。

後序表示法不需要括號和優先順序，用一個堆疊由左到右掃一次就算完了，O(n)。

??? 觀念
只用兩個堆疊（`in` 和 `out`）實作一個佇列：

1. `push` 和 `pop` 要怎麼做？
2. 為什麼每個操作是 **攤銷 O(1)**，雖然有時候 `pop` 要搬 n 個元素？
!!!
1. - `push(x)`：直接放進 `in`。
   - `pop()`：如果 `out` 是空的，就把 `in` 的元素 **全部** 一個一個彈出、放進 `out`（順序剛好反過來，最早放進去的到了 `out` 的頂端）；然後從 `out` 彈出。
   - `front()` 同理。
2. 每個元素在一生中 **最多被搬動一次**：放進 `in`、搬到 `out`、從 `out` 彈出，每一步都是 O(1)。n 個操作的總成本是 O(n)，平均每個 O(1)。雖然某一次 `pop` 可能要搬很多元素，但那些元素之後就不會再搬了。

@@@ 06 | 雜湊表

??? 手動模擬
雜湊表有 m = 7 個桶子，雜湊函數 `h(k) = k % 7`，用 **分離鏈結法**，新元素加在串列 **尾端**。依序插入 `10, 17, 3, 24, 5, 14`：

1. 每個桶子裡有哪些 key？
2. 負載因子是多少？
3. 查詢 `31` 需要比較幾次才知道不存在？
!!!
1. `10 % 7 = 3`、`17 % 7 = 3`、`3 % 7 = 3`、`24 % 7 = 3`、`5 % 7 = 5`、`14 % 7 = 0`：
   - 桶子 0：14
   - 桶子 3：10 → 17 → 3 → 24
   - 桶子 5：5
   - 其他桶子空的
2. 負載因子 = 元素數 / 桶子數 = 6 / 7 ≈ 0.86。
3. `31 % 7 = 3`，要把桶子 3 的 **4 個** key 都比過一次才知道不存在。

這組 key 刻意讓很多元素擠在同一個桶子，說明雜湊函數「分散得好不好」直接決定效率；最壞情況（全部在同一桶）會退化成 O(n)。

??? 找錯
下面的雜湊表在測資有 **負數** key 時當掉，為什麼？怎麼改？

```cpp
int bucket_of(long long key) { return key % M; }
// ...
buckets[bucket_of(key)].push_back(key);
```
!!!
C++ 的 `%` 結果和被除數同號：`(-13) % 10 == -3`。負的索引會讓 `buckets[-3]` **越界**。

改法：
```cpp
int bucket_of(long long key) { return ((key % M) + M) % M; }
// 或
int bucket_of(long long key) { return (unsigned long long)key % M; }
```

??? 觀念
1. 什麼是負載因子？為什麼負載因子太高時要 **重新雜湊 (rehash)**？
2. rehash 時為什麼每個元素都要重新計算桶子，不能直接複製到新陣列的同一個位置？
3. 每次 rehash 都是 O(n)，為什麼插入仍然是平均 O(1)？
!!!
1. 負載因子 = 元素數 ÷ 桶子數，代表每個桶子平均有幾個元素。負載因子越高，每條串列越長，查詢越慢；超過門檻（例如 1）時把桶子數加倍，讓平均長度回到常數。
2. 桶子是用 `hash(key) % m` 算的，**m 改變了，同一個 key 算出來的桶子也不同**。直接複製的話，之後用新的 m 去查就找不到了。
3. 和動態陣列一樣：桶子數 **加倍** 成長，rehash 的總成本是 n + n/2 + n/4 + … < 2n，平均分攤到每次插入是 O(1)（攤銷分析）。

??? 觀念
1. `unordered_map` 和 `map` 各是用什麼資料結構實作的？各操作的複雜度？什麼時候選 `map`？
2. 什麼是雜湊攻擊 (Hash DoS)？
!!!
1. - `unordered_map`：**雜湊表**，平均 O(1)、最壞 O(n)，**沒有順序**。
   - `map`：**平衡二元搜尋樹**（紅黑樹），每個操作 **保證 O(log n)**，key **有排序**。

   需要「依序走訪」、「找第一個 ≥ x 的 key」（`lower_bound`）、或要保證最壞情況時，選 `map`。
2. 攻擊者知道雜湊函數（例如對整數 key 很簡單的 `k % m`），刻意構造一大堆 **落在同一個桶子** 的 key，讓每次操作都退化成 O(n)，n 個操作變成 O(n²)，程式超時（伺服器被拖垮）。解法是用把位元充分打亂、加上隨機種子的雜湊函數（例如 splitmix64 加上執行時決定的亂數）。

??? 手動模擬
雜湊表有 m = 7 格，`h(k) = k % 7`，用 **線性探測 (linear probing)**：位置被佔用就往下一格找（超過結尾繞回 0）。依序插入 `10, 3, 17, 24, 6`：

1. 每個 key 最後放在哪一格？
2. 查詢 31 時要檢查哪幾格才知道不存在？
3. 如果把 17 刪除時直接把那格清空，查詢 24 會發生什麼事？要怎麼解決？
!!!
1. - 10 % 7 = 3 → 格 **3**
   - 3 % 7 = 3，被佔 → 格 **4**
   - 17 % 7 = 3，3、4 被佔 → 格 **5**
   - 24 % 7 = 3，3、4、5 被佔 → 格 **6**
   - 6 % 7 = 6，被佔 → 繞回格 **0**

   結果：`[6, -, -, 10, 3, 17, 24]`
2. 31 % 7 = 3，從格 3 開始：3、4、5、6、0 都有別的 key，**格 1 是空的** 才能確定不存在，共檢查 6 格。這就是線性探測的 **群聚 (clustering)** 問題：連續被佔用的區段越長，查詢越慢。
3. 查詢 24 從格 3 開始往下找，走到格 5 發現是空的，就會 **誤以為 24 不存在**（其實它在格 6）。解法：刪除時不清空，而是放一個 **墓碑 (tombstone)** 標記「這裡曾經有東西」：查詢時遇到墓碑要繼續往下找，插入時可以重複使用墓碑的位置。

??? 寫程式
給一個整數陣列和目標值 target，找出兩個 **不同位置** 的元素，使它們的和等於 target，回傳兩個索引（保證有解）。要求平均 O(n)。
!!!
```cpp
pair<int, int> two_sum(const vector<int>& a, int target) {
    unordered_map<int, int> pos;               // 值 → 索引
    for (int i = 0; i < (int)a.size(); i++) {
        auto it = pos.find(target - a[i]);     // 之前有沒有出現過「需要的另一半」？
        if (it != pos.end()) return {it->second, i};
        pos[a[i]] = i;                          // 查完再放入，避免和自己配對
    }
    return {-1, -1};
}
```

一邊走一邊把看過的值放進雜湊表，每個元素只要查一次「`target - a[i]` 出現過沒有」。每次查詢和插入平均 O(1)，總共 **平均 O(n)**。暴力法（兩層迴圈）是 O(n²)；先排序再用雙指標是 O(n log n)，但會打亂原本的索引。

**先查詢、再插入** 很重要：例如 target = 6、a[i] = 3 時，如果先插入，就會找到自己。

@@@ 07 | 堆積與優先佇列

??? 預測輸出
下面的程式用陣列實作 **最小堆積**（索引從 0 開始），依序插入 `5 3 8 1 9 2`，然後取出一次最小值。預測每一步的陣列內容。

```cpp
#include <iostream>
#include <vector>
#include <utility>
using namespace std;

vector<int> h;

void push(int x) {
    h.push_back(x);
    int i = h.size() - 1;
    while (i > 0 && h[(i - 1) / 2] > h[i]) {
        swap(h[(i - 1) / 2], h[i]);
        i = (i - 1) / 2;
    }
}

int pop() {
    int top = h[0];
    h[0] = h.back();
    h.pop_back();
    int i = 0, n = h.size();
    while (true) {
        int l = 2 * i + 1, r = 2 * i + 2, m = i;
        if (l < n && h[l] < h[m]) m = l;
        if (r < n && h[r] < h[m]) m = r;
        if (m == i) break;
        swap(h[i], h[m]);
        i = m;
    }
    return top;
}

void show() { for (int x : h) cout << x << " "; cout << "\n"; }

int main() {
    for (int x : {5, 3, 8, 1, 9, 2}) push(x);
    show();
    cout << pop() << "\n";
    show();
    return 0;
}
```
!!!
```output
1 3 2 5 9 8 
1
2 3 8 5 9 
```

插入過程（上浮）：
- 5 → `5`
- 3 → `3 5`（3 比父節點 5 小，交換）
- 8 → `3 5 8`
- 1 → 放在索引 3，父節點是 5 → 交換；再和 3 比 → 交換 → `1 3 8 5`
- 9 → `1 3 8 5 9`
- 2 → 放在索引 5，父節點 8 → 交換；再和 1 比，不動 → `1 3 2 5 9 8`

取出：把最後一個 8 移到根，往下沉：8 和小孩 3、2 比，和 2 交換 → `2 3 8 5 9`。

??? 觀念
1. 用陣列存完全二元樹（索引從 0 開始），節點 `i` 的父節點、左小孩、右小孩的索引各是多少？
2. 為什麼堆積的插入和刪除是 O(log n)？
3. 把 n 個數「建成堆積」可以 O(n) 完成，用的是什麼方法？
!!!
1. 父節點 `(i - 1) / 2`，左小孩 `2i + 1`，右小孩 `2i + 2`。（索引從 1 開始時是 `i / 2`、`2i`、`2i + 1`。）
2. 堆積是 **完全二元樹**，高度是 ⌊log₂ n⌋。上浮和下沉每次往上或往下一層，最多走樹高那麼多步。
3. **由下往上建堆 (bottom-up heapify)**：從最後一個非葉節點（索引 `n/2 - 1`）開始，往前對每個節點做 **下沉**。大部分節點都在樹的底部，下沉的距離很短：高度 h 的節點約有 n / 2^(h+1) 個，總成本 Σ h × n / 2^(h+1) = O(n)。（一個一個 push 則是 O(n log n)。）

??? 預測輸出
```cpp
#include <iostream>
#include <queue>
#include <vector>
using namespace std;

int main() {
    priority_queue<int> maxpq;
    priority_queue<int, vector<int>, greater<int>> minpq;
    for (int x : {4, 1, 7, 3}) { maxpq.push(x); minpq.push(x); }
    cout << maxpq.top() << " " << minpq.top() << "\n";

    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<>> pq;
    pq.push({3, 2}); pq.push({1, 5}); pq.push({3, 1}); pq.push({1, 9});
    while (!pq.empty()) {
        cout << pq.top().first << "," << pq.top().second << " ";
        pq.pop();
    }
    cout << "\n";
    return 0;
}
```
!!!
```output
7 1
1,5 1,9 3,1 3,2 
```

- `priority_queue` **預設是最大堆積**；加上 `greater<int>` 反而變成 **最小** 堆積。
- `pair` 比較時 **先比 first，相同再比 second**，所以最小堆積依序取出 `(1,5) (1,9) (3,1) (3,2)`。

??? 寫程式
有 n 個數（n 可能是 10⁷，記憶體放不下全部排序的額外空間也沒關係，但希望比 O(n log n) 快），要找出 **最小的 k 個**（k 很小，例如 100）。用 `priority_queue` 寫出做法，並分析複雜度。
!!!
維護一個大小為 k 的 **最大堆積**，裡面放「目前看到最小的 k 個」：

```cpp
priority_queue<int> pq;                 // 最大堆積
for (int x : a) {
    if ((int)pq.size() < k) pq.push(x);
    else if (x < pq.top()) {            // 比目前第 k 小的還小
        pq.pop();
        pq.push(x);
    }
}
// pq 裡就是最小的 k 個（堆頂是其中最大的）
```

時間 **O(n log k)**、額外空間 **O(k)**。k = 100 時 log k ≈ 7，比 O(n log n) 的排序快很多。

為什麼用 **最大** 堆積：要能快速知道「這 k 個裡最大的是誰」，新的數比它小才替換掉它。

??? 預測輸出
用「由下往上建堆」把陣列變成 **最小堆積**：

```cpp
#include <iostream>
#include <utility>
#include <vector>
using namespace std;

void sift_down(vector<int>& h, int i) {
    int n = h.size();
    while (true) {
        int l = 2 * i + 1, r = 2 * i + 2, m = i;
        if (l < n && h[l] < h[m]) m = l;
        if (r < n && h[r] < h[m]) m = r;
        if (m == i) return;
        swap(h[i], h[m]);
        i = m;
    }
}

int main() {
    vector<int> h = {9, 4, 7, 1, 8, 2, 6};
    for (int i = (int)h.size() / 2 - 1; i >= 0; i--) sift_down(h, i);
    for (int x : h) cout << x << " ";
    cout << "\n";
    return 0;
}
```
!!!
```output
1 4 2 9 8 7 6 
```

從最後一個非葉節點（索引 n/2 − 1 = 2）往前，對每個節點做下沉：
- i = 2（值 7，小孩 2、6）：和 2 交換 → `9 4 2 1 8 7 6`
- i = 1（值 4，小孩 1、8）：和 1 交換 → `9 1 2 4 8 7 6`（4 換到索引 3，沒有小孩，停）
- i = 0（值 9，小孩 1、2）：和 1 交換 → `1 9 2 4 8 7 6`；9 到了索引 1，小孩 4、8，再和 4 交換 → `1 4 2 9 8 7 6`

總成本是 O(n)，比一個一個插入的 O(n log n) 快。

??? 觀念
有 k 個已經排好序的串列，總共 N 個元素，要把它們合併成一個排好序的串列。

1. 用堆積怎麼做？複雜度是多少？
2. 為什麼比「全部放在一起再排序」好？
!!!
1. 把每個串列的 **第一個元素**（連同它屬於哪個串列、在第幾個位置）放進一個 **最小堆積**。每次取出堆頂（目前所有串列中最小的）放進結果，再把 **同一個串列的下一個元素** 放進堆積。堆積裡最多 k 個元素，每次操作 O(log k)，總共 **O(N log k)**。
2. 全部放在一起再排序是 O(N log N)。k 通常遠小於 N（例如 k = 10 個檔案、N = 10⁹ 筆資料），log k 比 log N 小很多；而且堆積只需要 O(k) 的記憶體，可以 **一邊讀一邊輸出**，資料大到放不進記憶體時也能用（外部排序就是這樣做的）。

@@@ 08 | 二元搜尋樹

??? 預測輸出
依序插入 `50 30 70 20 40 60 80 35` 到 BST，輸出三種走訪：

```cpp
#include <iostream>
using namespace std;

struct Node { int key; Node *left = nullptr, *right = nullptr; Node(int k) : key(k) {} };

void insert(Node*& t, int k) {
    if (!t) { t = new Node(k); return; }
    if (k < t->key) insert(t->left, k);
    else insert(t->right, k);
}
void pre(Node* t)  { if (!t) return; cout << t->key << " "; pre(t->left); pre(t->right); }
void in(Node* t)   { if (!t) return; in(t->left); cout << t->key << " "; in(t->right); }
void post(Node* t) { if (!t) return; post(t->left); post(t->right); cout << t->key << " "; }

int main() {
    Node* root = nullptr;
    for (int k : {50, 30, 70, 20, 40, 60, 80, 35}) insert(root, k);
    pre(root);  cout << "\n";
    in(root);   cout << "\n";
    post(root); cout << "\n";
    return 0;
}
```
!!!
```output
50 30 20 40 35 70 60 80 
20 30 35 40 50 60 70 80 
20 35 40 30 60 80 70 50 
```

樹的形狀：

```
        50
      /    \
    30      70
   /  \    /  \
  20  40  60  80
      /
     35
```

**中序走訪一定是由小到大**，這是 BST 最重要的性質，可以用來檢查 BST 是否正確。

??? 手動模擬
接續上一題的樹，刪除 **50**（用 **中序後繼** 取代）。刪除後的前序走訪是什麼？再刪除 **30** 呢？
!!!
1. **刪除 50**：50 有兩個小孩，找中序後繼 = 右子樹的最小值 = **60**。把根的值換成 60，再刪掉原本的 60（它是葉節點）。
   ```
           60
         /    \
       30      70
      /  \       \
     20  40       80
         /
        35
   ```
   前序：**60 30 20 40 35 70 80**
2. **再刪除 30**：30 有兩個小孩，中序後繼 = 右子樹（40, 35）的最小值 = **35**。把 30 換成 35，再刪掉原本的 35（葉節點）。
   前序：**60 35 20 40 70 80**

??? 觀念
插入函式的參數為什麼寫成 `Node*& t`（指標的參考）？如果寫成 `Node* t` 會怎樣？
!!!
插入到空的位置時要執行 `t = new Node(k);`，這必須修改 **呼叫者那邊的指標**（父節點的 `left` 或 `right`，或是 `root` 本身）。

- `Node*& t`：`t` 是那個指標的 **別名**，指定給 `t` 就是改到父節點的欄位。
- `Node* t`：`t` 只是指標的 **複本**，`t = new Node(k)` 只改了複本，新節點沒有接到樹上（而且洩漏），樹永遠是空的。

（C 沒有參考，要寫成 `Node **t`，道理一樣。）

??? 觀念
1. 依序插入 `1, 2, 3, …, n` 到一般的 BST，樹會長什麼樣子？搜尋的複雜度變成多少？
2. `std::set` / `std::map` 怎麼避免這個問題？
!!!
1. 每個新節點都比前面的大，全部接在右邊，樹 **退化成一條鏈**（像串列），高度是 n，搜尋、插入、刪除都變成 **O(n)**。
2. 它們是 **平衡二元搜尋樹**（通常是紅黑樹），每次插入或刪除後會用 **旋轉** 調整形狀，保證樹高是 O(log n)，所以每個操作 **最壞也是 O(log n)**。

??? 預測輸出
`set` 是平衡二元搜尋樹，可以做「找第一個 ≥ x」這類查詢：

```cpp
#include <iostream>
#include <iterator>
#include <set>
using namespace std;

int main() {
    set<int> s = {40, 10, 30, 20};
    cout << *s.lower_bound(25) << " " << *s.upper_bound(30) << " "
         << *prev(s.lower_bound(25)) << " " << (s.lower_bound(50) == s.end()) << "\n";
    s.insert(20);
    s.erase(10);
    for (int x : s) cout << x << " ";
    cout << "| " << s.size() << " " << *s.begin() << " " << *s.rbegin() << "\n";
    return 0;
}
```
!!!
```output
30 40 20 1
20 30 40 | 3 20 40
```

- `lower_bound(25)`：第一個 **≥ 25** 的元素 → 30。
- `upper_bound(30)`：第一個 **> 30** 的元素 → 40。
- `prev(lower_bound(25))`：**比 25 小的最大元素**（floor）→ 20。使用前要確認 `lower_bound` 不是 `begin()`。
- 找不到時回傳 `end()`，不能解參考。
- `set` 不存重複的元素，再插入 20 沒有作用；走訪時依序由小到大；`rbegin()` 是最大值。

這些查詢都是 O(log n)，在 BST 上沿著一條路徑往下走就能找到。

??? 手動模擬
1. 要把 1 ~ 7 插入一棵空的 BST，得到 **高度最小**（完全平衡）的樹，插入順序可以是什麼？畫出結果。
2. 如果依序插入 `4, 2, 6, 1, 3, 5, 7` 之後刪除 **4**（用中序後繼取代），樹會變成什麼樣子？
!!!
1. 先插入 **中間** 的值當根，再遞迴地插入左右兩半的中間值，例如 **4, 2, 6, 1, 3, 5, 7**（同一層之間的順序可以換）：
   ```
         4
       /   \
      2     6
     / \   / \
    1   3 5   7
   ```
   高度是 2（3 層），是 7 個節點能達到的最小高度。依序插入 1 ~ 7 則會退化成一條鏈，高度 6。
2. 4 有兩個小孩，中序後繼是右子樹的最小值 **5**。把根換成 5，再刪掉原本的 5（葉節點）：
   ```
         5
       /   \
      2     6
     / \     \
    1   3     7
   ```

@@@ 09 | 圖：BFS、DFS 與拓撲排序

??? 預測輸出
```cpp
#include <iostream>
#include <queue>
#include <vector>
using namespace std;

int main() {
    int n = 6;
    vector<vector<int>> adj(n + 1);
    int edges[][2] = {{1, 2}, {1, 3}, {2, 4}, {3, 4}, {4, 5}, {5, 6}, {3, 6}};
    for (auto& e : edges) { adj[e[0]].push_back(e[1]); adj[e[1]].push_back(e[0]); }

    vector<int> dist(n + 1, -1);
    queue<int> q;
    dist[1] = 0; q.push(1);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        cout << u << " ";
        for (int v : adj[u])
            if (dist[v] == -1) { dist[v] = dist[u] + 1; q.push(v); }
    }
    cout << "\n";
    for (int i = 1; i <= n; i++) cout << dist[i] << " ";
    cout << "\n";
    return 0;
}
```
!!!
```output
1 2 3 4 6 5 
0 1 1 2 3 2 
```

- 走訪順序：1 → 鄰居 2、3 → 2 的鄰居 4 → 3 的鄰居 6（4 已經有距離了）→ 4 的鄰居 5 → …
- 距離（依序是點 1 ~ 6）：4 經過 1-2-4 是 2；5 是 4 再走一步 = 3；6 經過 1-3-6 是 2。

注意 **加入佇列時就標記**（設定 `dist`），不是取出時才標記；否則同一個點可能被加入佇列很多次。

??? 觀念
1. 為什麼 BFS 求得的是 **無權重圖** 的最短距離？為什麼 DFS 不行？
2. 有權重（都是正數）的圖要求最短路徑，BFS 為什麼不能用？要用什麼？
!!!
1. BFS 用 **佇列**，一層一層往外擴張：先處理所有距離 0 的點，再處理所有距離 1 的點……一個點第一次被走到時，一定是經由最少的邊數。DFS 沿著一條路一直走到底，第一次走到某個點時，走的可能是一條繞遠路的路徑。
2. BFS 只算「邊數」，不考慮權重：經過 2 條權重 1 的邊（總和 2），比經過 1 條權重 10 的邊好，但 BFS 會先找到後者。要用 **Dijkstra 演算法**：每次從還沒確定的點中，挑目前距離最小的確定下來（用 `priority_queue`），O((n + m) log n)。

??? 觀念
1. n = 10⁵ 個點、m = 2 × 10⁵ 條邊的圖，用鄰接矩陣和鄰接串列各需要多少記憶體（以 `int` / `bool` 估計即可）？該用哪一個？
2. 迷宮（R × C 的網格）的 BFS，「圖」的點和邊是什麼？
!!!
1. - 鄰接矩陣：n² = 10¹⁰ 格，就算用 `bool` 也要 10 GB，不行。
   - 鄰接串列：O(n + m)，大約 (10⁵ + 2 × 2 × 10⁵) 個 `int`，幾 MB 而已。

   **稀疏圖用鄰接串列**；鄰接矩陣只適合點很少（n 幾千以內）、或需要 O(1) 查詢「兩點之間有沒有邊」的情況。
2. 每個 **格子** 是一個點；相鄰（上下左右）而且不是牆的兩個格子之間有一條邊。不需要真的建出鄰接串列，用方向陣列 `dr[] = {-1, 1, 0, 0}`、`dc[] = {0, 0, -1, 1}` 直接枚舉鄰居，並檢查是否越界、是否是牆。

??? 預測輸出
用 Kahn 演算法（搭配最小堆積）求 **字典序最小** 的拓撲排序：

```cpp
#include <iostream>
#include <queue>
#include <vector>
using namespace std;

int main() {
    int n = 6;
    vector<vector<int>> adj(n + 1);
    vector<int> indeg(n + 1, 0);
    int edges[][2] = {{5, 2}, {5, 1}, {4, 1}, {2, 3}, {3, 1}, {6, 3}};
    for (auto& e : edges) { adj[e[0]].push_back(e[1]); indeg[e[1]]++; }

    priority_queue<int, vector<int>, greater<int>> pq;
    for (int i = 1; i <= n; i++) if (indeg[i] == 0) pq.push(i);
    vector<int> order;
    while (!pq.empty()) {
        int u = pq.top(); pq.pop();
        order.push_back(u);
        for (int v : adj[u]) if (--indeg[v] == 0) pq.push(v);
    }
    for (int x : order) cout << x << " ";
    cout << "\n" << (order.size() == (size_t)n ? "DAG" : "has cycle") << "\n";
    return 0;
}
```
!!!
```output
4 5 2 6 3 1 
DAG
```

一開始的入度：點 1 是 3（來自 5、4、3），點 2 是 1，點 3 是 2（來自 2、6），點 4、5、6 是 0。

| 取出 | 更新入度 | 堆積裡剩下 |
|---|---|---|
| **4**（4、5、6 中最小） | 點 1：3 → 2 | 5, 6 |
| **5** | 點 2：1 → 0（加入）；點 1：2 → 1 | 2, 6 |
| **2** | 點 3：2 → 1 | 6 |
| **6** | 點 3：1 → 0（加入） | 3 |
| **3** | 點 1：1 → 0（加入） | 1 |
| **1** | | （空） |

**判斷有環**：如果最後輸出的點數少於 n，表示有些點的入度永遠降不到 0，它們在環上。

??? 預測輸出
和前面 BFS 題目相同的圖（邊依序是 1-2、1-3、2-4、3-4、4-5、5-6、3-6），改用 **遞迴 DFS** 從 1 出發：

```cpp
#include <iostream>
#include <vector>
using namespace std;

vector<vector<int>> adj;
vector<bool> seen;

void dfs(int u) {
    seen[u] = true;
    cout << u << " ";
    for (int v : adj[u])
        if (!seen[v]) dfs(v);
}

int main() {
    int n = 6;
    adj.assign(n + 1, {});
    seen.assign(n + 1, false);
    int edges[][2] = {{1, 2}, {1, 3}, {2, 4}, {3, 4}, {4, 5}, {5, 6}, {3, 6}};
    for (auto& e : edges) { adj[e[0]].push_back(e[1]); adj[e[1]].push_back(e[0]); }
    dfs(1);
    cout << "\n";
    return 0;
}
```
!!!
```output
1 2 4 3 6 5 
```

DFS 沿著一條路一直走到底才回頭：1 → 2（1 的第一個鄰居）→ 4（2 的鄰居中第一個沒走過的）→ 3（4 的鄰居 2 走過了，下一個是 3）→ 6（3 的鄰居 1、4 都走過了）→ 5（6 的鄰居）。然後一路回溯，所有點都走過了。

BFS 的順序是 `1 2 3 4 6 5`，一層一層往外；DFS 是 `1 2 4 3 6 5`，先往深處走。兩者都是 O(n + m)。

??? 觀念
1. 一個 R × C 的網格，`.` 是空地、`#` 是牆。怎麼算出有幾個「互相連通的空地區域」？複雜度是多少？
2. 用遞迴 DFS 做這件事，在 1000 × 1000 全是空地的網格上可能會發生什麼事？怎麼避免？
!!!
1. 走訪每一個格子；遇到 **還沒拜訪過的空地**，區域數加 1，然後從它開始做 BFS 或 DFS（**flood fill**），把整個區域都標記成拜訪過。每個格子只會被拜訪一次、檢查 4 個鄰居，總共 **O(R × C)**。
2. 整個網格是一個區域，遞迴深度可能達到 10⁶ 層，**堆疊溢位**。改用 BFS（佇列放在堆積上），或用自己的 `stack` 寫成迴圈版本的 DFS。

@@@ 10 | 併查集

??? 預測輸出
```cpp
#include <iostream>
#include <numeric>
#include <utility>
#include <vector>
using namespace std;

vector<int> parent, sz;

int find(int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); }

bool unite(int a, int b) {
    a = find(a); b = find(b);
    if (a == b) return false;
    if (sz[a] < sz[b]) swap(a, b);
    parent[b] = a;
    sz[a] += sz[b];
    return true;
}

int main() {
    int n = 8;
    parent.resize(n); sz.assign(n, 1);
    iota(parent.begin(), parent.end(), 0);
    int ops[][2] = {{0, 1}, {2, 3}, {1, 3}, {4, 5}, {3, 0}, {6, 7}, {5, 6}};
    int groups = n;
    for (auto& o : ops) {
        bool merged = unite(o[0], o[1]);
        if (merged) groups--;
        cout << merged;
    }
    cout << "\n" << groups << " " << (find(2) == find(0)) << " " << (find(4) == find(0))
         << " " << sz[find(7)] << "\n";
    return 0;
}
```
!!!
```output
1111011
2 1 0 4
```

- `unite(3, 0)` 回傳 `false`：此時 0、1、2、3 已經在同一組了（**這條邊會形成環**）。
- 最後剩兩組：{0, 1, 2, 3} 和 {4, 5, 6, 7}，第二組大小 4。

??? 觀念
1. 不做任何優化的併查集，最壞情況下 `find` 是多少？什麼操作序列會造成這種情況？
2. 「按大小合併」和「路徑壓縮」各做了什麼？兩個一起用時，複雜度是多少？
!!!
1. **O(n)**。例如依序 `union(1,2)`、`union(2,3)`、…，每次都把舊的根接到新的點下面，樹變成一條長鏈，`find` 最底下的點要走 n 步。
2. - **按大小合併 (union by size)**：把 **小的樹接到大的樹下面**，樹高最多 O(log n)。
   - **路徑壓縮 (path compression)**：`find` 的時候把路上每個節點直接接到根，下次就一步到位。
   - 兩個一起用：每個操作攤銷 **O(α(n))**，α 是反阿克曼函數，在任何實際的 n 下都 ≤ 4，可以視為常數。

??? 寫程式
用併查集寫出：給一個 n 個點、m 條邊的 **無向圖**，判斷它有沒有環。說明為什麼這樣判斷是對的，以及 Kruskal 最小生成樹怎麼用到同樣的想法。
!!!
```cpp
bool has_cycle(int n, const vector<pair<int,int>>& edges) {
    DSU d(n);                          // 前一題的 parent / sz / find / unite
    for (auto [u, v] : edges)
        if (!d.unite(u, v)) return true;   // 兩端已經連通，再加這條邊就形成環
    return false;
}
```

加入邊 (u, v) 之前，如果 u 和 v **已經在同一組**，表示它們之間本來就有一條路徑，再加上這條邊就會形成環。

**Kruskal**：把邊依權重由小到大排序，依序考慮每條邊；兩端不在同一組就加入生成樹並合併，已經在同一組就跳過（加了會形成環）。總共 O(m log m)（排序是瓶頸）。

??? 找錯
下面的 `unite` 有什麼問題？

```cpp
void unite(int a, int b) {
    parent[a] = b;
}
```
!!!
它把 **`a` 本身** 接到 `b` 底下，而不是把 **`a` 的根** 接到 **`b` 的根** 底下。如果 `a` 不是根，`a` 原本所在的那棵樹會被拆開：`a` 和它的子樹跑到 `b` 那邊，但 `a` 的祖先們還留在原地，兩組都只合併了一部分，結果錯誤。

正確寫法：

```cpp
void unite(int a, int b) {
    a = find(a);
    b = find(b);
    if (a != b) parent[a] = b;   // 再加上按大小合併更好
}
```

??? 預測輸出
用 Kruskal 演算法求最小生成樹：

```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <tuple>
#include <vector>
using namespace std;

vector<int> parent;
int find(int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); }

int main() {
    int n = 5;
    vector<tuple<int, int, int>> edges = {   // (權重, u, v)
        {1, 1, 2}, {3, 2, 3}, {4, 1, 3}, {2, 3, 4}, {5, 4, 5}, {7, 3, 5}, {6, 2, 5}};
    sort(edges.begin(), edges.end());
    parent.resize(n + 1);
    iota(parent.begin(), parent.end(), 0);
    int total = 0, used = 0;
    for (auto [w, u, v] : edges) {
        int a = find(u), b = find(v);
        if (a == b) continue;               // 加了會形成環
        parent[a] = b;
        total += w;
        used++;
        cout << u << "-" << v << " ";
    }
    cout << "| " << total << " " << used << "\n";
    return 0;
}
```
!!!
```output
1-2 3-4 2-3 4-5 | 11 4
```

邊依權重由小到大考慮：
- 權重 1（1-2）：不同組 → 選。
- 權重 2（3-4）：不同組 → 選。
- 權重 3（2-3）：{1,2} 和 {3,4} 不同組 → 選，合併成 {1,2,3,4}。
- 權重 4（1-3）：已經在同一組，加了會形成環 → **跳過**。
- 權重 5（4-5）：選。
- 已經選了 n − 1 = 4 條邊，生成樹完成。總權重 1 + 2 + 3 + 5 = 11。

??? 觀念
1. 併查集可以很快地「合併」兩組，但不支援「把一條邊拿掉、讓一組分裂」。為什麼？
2. 如果題目是「依序刪除圖中的邊，每次刪除後問有幾個連通分量」，怎麼還是能用併查集？
!!!
1. 併查集只記錄每個點的 **代表元素（根）**，合併時把兩棵樹接起來，而且路徑壓縮還會改變樹的形狀。它 **沒有記錄是哪一條邊造成了連通**，所以拿掉一條邊時，無法知道這兩個點是否還有別的路徑相連，也就無法正確地分裂。
2. **倒過來做（離線處理）**：先讀完所有的刪除操作，從「所有要刪的邊都已經刪掉」的最終狀態開始，把操作 **反過來** 變成「依序加入邊」，用併查集計算每一步的連通分量數，最後把答案反轉輸出。「刪除」變成「加入」之後，併查集就能處理了。

@@@ 11 | Corner Case、自己產生測資、對拍

??? 觀念
題目：「給 n 個整數，輸出 **最大連續子陣列和**」（n ≥ 1，|aᵢ| ≤ 10⁹，n ≤ 2 × 10⁵）。列出至少 6 個應該測試的 corner case，並說明每個要抓什麼錯誤。
!!!
1. **n = 1**：最小的輸入，迴圈邊界、初始值。
2. **全部是負數**（例如 `-5 -2 -9`）：答案是最大的那個負數（-2）。如果把答案初始化成 0、或允許「空子陣列」，就會錯輸出 0。
3. **全部是正數**：答案是整個陣列的和。
4. **總和超過 int**：2 × 10⁵ 個 10⁹ 加起來是 2 × 10¹⁴，要用 `long long`。
5. **全部是 0**：答案 0。
6. **最大值在最開頭 / 最尾端**：檢查迴圈有沒有漏掉第一個或最後一個元素。
7. **n 最大而且是隨機數**：檢查時間複雜度（O(n²) 會超時）。
8. **最大子陣列中間夾著負數**（例如 `5 -1 5`，答案 9）：檢查是不是太早「重新開始」。

??? 觀念
1. 「對拍」是什麼？需要準備哪三個程式？
2. 對拍時為什麼要用 **很小** 的隨機測資（例如 n ≤ 8），而不是大的？
3. 找到反例之後，為什麼要記下 **亂數種子 (seed)**？
!!!
1. 用 **隨機測資** 比較「要測試的解法」和「一定正確的解法」的輸出，找出兩者不同的輸入（反例）。需要：
   - **產生器**：產生隨機的小測資；
   - **暴力解**：慢但簡單、一定正確（例如枚舉所有子陣列）；
   - **待測解**：你的正式解法。
2. - 小的測資 **跑得快**，可以在短時間內試幾千、幾萬組；
   - 暴力解通常是指數或 O(n³)，大測資根本跑不完；
   - 最重要的是：反例很小，**人可以手動追蹤**，很快看出錯在哪裡。

   大部分的 bug 在小測資就會出現。
3. 同樣的種子會產生同樣的測資，可以 **重現** 那個反例：修改程式後用同一個種子再跑一次，確認真的修好了。

??? 配對
下面每一種錯誤訊息（來自 `--debug` 的 sanitizer 或執行結果），最可能是什麼 bug？

1. `heap-buffer-overflow ... READ of size 4`
2. `stack-overflow`
3. `runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'`
4. `heap-use-after-free`
5. 判定 TLE，但小測資都 AC
!!!
1. 讀取 `vector` 或 `new` 出來的陣列時 **越界**（例如 `v[v.size()]`、迴圈寫成 `<=`）。`size 4` 表示讀的是一個 `int`。
2. 遞迴太深（沒有終止條件、或深度真的達到 10⁵ ~ 10⁶），或在函式裡宣告了很大的區域陣列。
3. 運算結果超過 `int` 範圍，要改用 `long long`（或在運算前先轉型）。
4. 使用已經 `delete`/`free` 的記憶體，或使用 `vector` 擴容後失效的指標、參考、迭代器。
5. 演算法的 **時間複雜度太高**（例如 O(n²) 而 n = 10⁵），或有隱藏的成本（在迴圈裡 `erase(begin())`、字串 `+` 串接、`endl` 太多次）。

??? 觀念
什麼是 **anti-test（卡掉錯誤解法的測資）**？舉兩個例子：一個卡「快排選第一個元素當 pivot」，一個卡「BST 沒有平衡」。
!!!
anti-test 是針對某個 **錯誤或太慢的解法** 刻意構造的測資，讓它出錯或超時。隨機測資常常抓不到這些情況，所以好的測資一定要包含它們。

- **快排固定選第一個元素當 pivot**：給一個 **已經排好序**（或完全相反）的陣列，每次切分都極度不平均，退化成 O(n²)。
- **沒有平衡的 BST**：依序插入 **1, 2, 3, …, n**，樹變成一條鏈，n = 10⁵ 時每次操作 O(n)，總共 O(n²)，而且遞迴實作還可能堆疊溢位。

??? 寫程式
你寫了一個二分搜尋 `int lower_bound_idx(const vector<int>& a, int x)`（回傳第一個 ≥ x 的索引，都比 x 小時回傳 n）。

1. 迴圈裡應該維持什麼 **不變量**？可以用 `assert` 檢查什麼？
2. 寫出完整的函式。
!!!
1. 用半開區間 `[lo, hi)`，不變量是：
   - `a[0 .. lo-1]` 都 **< x**；
   - `a[hi .. n-1]` 都 **≥ x**；
   - `0 ≤ lo ≤ hi ≤ n`。

   迴圈結束時 `lo == hi`，就是答案。可以 `assert(0 <= lo && lo <= hi && hi <= n)`，也可以檢查每一輪區間都有縮小（避免無窮迴圈）。
2. 完整的函式：

   ```cpp
   int lower_bound_idx(const vector<int>& a, int x) {
       int lo = 0, hi = a.size();              // 答案在 [lo, hi] 之間
       while (lo < hi) {
           int mid = lo + (hi - lo) / 2;       // 不會溢位；lo <= mid < hi
           if (a[mid] < x) lo = mid + 1;       // a[0..mid] 都 < x
           else hi = mid;                      // a[mid..] 都 >= x
           assert(0 <= lo && lo <= hi && hi <= (int)a.size());
       }
       return lo;
   }
   ```
   測試時要包含：空陣列、x 比全部小、x 比全部大、x 有重複、只有一個元素。也可以和 `std::lower_bound` 對拍。

??? 寫程式
你想對拍「最大連續子陣列和」的 O(n) 解法。寫出產生器 `gen.cpp` 的核心（用 seed 產生 n ≤ 8、值在 −10 ~ 10 的陣列）和暴力解 `brute.cpp` 的核心，並說明對拍的迴圈怎麼寫。
!!!
**產生器**（seed 從命令列傳入，同一個 seed 產生同一組測資）：

```cpp
int main(int argc, char* argv[]) {
    mt19937 rng(atoi(argv[1]));
    int n = rng() % 8 + 1;                              // 1 ~ 8
    cout << n << "\n";
    for (int i = 0; i < n; i++) cout << (int)(rng() % 21) - 10 << " ";
    cout << "\n";
}
```

**暴力解**（枚舉所有子陣列，O(n²)，簡單到不會錯）：

```cpp
long long best = LLONG_MIN;
for (int l = 0; l < n; l++) {
    long long s = 0;
    for (int r = l; r < n; r++) { s += a[r]; best = max(best, s); }
}
cout << best << "\n";
```

**對拍迴圈**（bash）：

```bash
for i in $(seq 1 1000); do
    ./gen $i > in.txt
    ./mine < in.txt > out1.txt
    ./brute < in.txt > out2.txt
    if ! cmp -s out1.txt out2.txt; then echo "seed $i 不同"; cat in.txt; break; fi
done
```

找到反例後，`in.txt` 就是一組很小的、可以手動追蹤的輸入；記下 seed，修好之後用同一個 seed 再跑一次確認。（本平台的 `python3 judge.py stress` 就是在做這件事。）
