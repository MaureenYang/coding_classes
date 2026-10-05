# 11. STL 深入 (Standard Template Library)

> 程式練習：`C11 單字頻率統計`
>
> 先備知識：第 10 課「模板」、第 04 課「lambda」。資料結構路線的教學介紹過各容器的 **原理**，這一課著重在 **怎麼正確使用**。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | STL 的架構 | 容器、迭代器、演算法為什麼要分開 |
| 第二部分 | 容器的選擇 | 每種容器的特性與複雜度、`map` 的四種插入方式 |
| 第三部分 | 迭代器 | 半開區間、五種分類、迭代器失效的規則 |
| 第四部分 | 演算法 | 搜尋、排序、二分搜、數值、集合運算 |
| 第五部分 | 函式物件與自訂規則 | 比較器、自訂雜湊、`greater<>` |
| 第六部分 | 經典陷阱 | erase-remove、`accumulate` 溢位、`unique` 要先排序…… |

每個名詞都用同樣的格式說明：**英文名稱 → 白話解釋 → 生活比喻 → C++ 範例**。標 🔍 的是深入內容。

---

# 第一部分：STL 的架構

## 1.1 三大元件

| 元件 | 英文 | 角色 | 例子 |
|---|---|---|---|
| 容器 | Container | **存放** 資料 | `vector`、`map`、`set` |
| 迭代器 | Iterator | **走訪** 容器的「游標」 | `v.begin()`、`m.find(k)` |
| 演算法 | Algorithm | **處理** 資料 | `sort`、`find`、`count` |

## 1.2 為什麼要分開？

**白話**：演算法 **不直接操作容器**，而是操作 **迭代器指定的範圍**。所以一個演算法可以用在 **所有** 提供適當迭代器的容器上。

**比喻**：通用的插座規格。有 N 種電器、M 種插座，如果每種電器都要配每種插座，要做 N × M 種接頭；統一了插座規格（迭代器），只要 N + M 種就夠了。

```cpp
vector<int> v = {3, 1, 2};
list<int> l = {3, 1, 2};
int arr[] = {3, 1, 2};
find(v.begin(), v.end(), 2);      // 同一個 find
find(l.begin(), l.end(), 2);      // 用在不同的容器
find(arr, arr + 3, 2);            // 連普通陣列都可以（指標就是迭代器）
```

---

# 第二部分：容器的選擇

## 2.1 容器總覽

| 類別 | 容器 | 特色 |
|---|---|---|
| **序列容器** (sequence) | `vector` | 動態陣列，**預設首選** |
| | `deque` | 頭尾都能快速增刪 |
| | `list` / `forward_list` | 雙向 / 單向串列，已知位置時增刪 `O(1)` |
| | `array` | 固定大小，放在 stack 上 |
| **有序關聯容器** (ordered associative) | `set` / `multiset` | 自動排序的集合（紅黑樹） |
| | `map` / `multimap` | 自動依 key 排序的對照表 |
| **無序關聯容器** (unordered) | `unordered_set` / `unordered_map` | 雜湊表，平均 `O(1)` |
| **容器配接器** (adapter) | `stack`、`queue`、`priority_queue` | 包裝其他容器，只開放特定操作 |

## 2.2 複雜度速查

| 操作 | `vector` | `deque` | `list` | `set`/`map` | `unordered_*` |
|---|---|---|---|---|---|
| 隨機存取 `[i]` | `O(1)` | `O(1)` | ❌ | ❌ | ❌ |
| 尾端增刪 | 攤銷 `O(1)` | `O(1)` | `O(1)` | — | — |
| 頭端增刪 | `O(n)` | `O(1)` | `O(1)` | — | — |
| 中間增刪（已有位置） | `O(n)` | `O(n)` | `O(1)` | `O(log n)` | 平均 `O(1)` |
| 搜尋某個值 | `O(n)` | `O(n)` | `O(n)` | `O(log n)` | 平均 `O(1)` |
| 有序走訪 | 要先排序 | 要先排序 | 要先排序 | ✅ | ❌ |

**選擇口訣**：
1. **預設用 `vector`**：連續記憶體、快取友善，就算理論複雜度一樣，實際上通常最快。
2. 要用 key 查詢 → `unordered_map`；還需要 **有序** 或 **找前後 / 範圍** → `map`。
3. 要「去重複」→ `set` / `unordered_set`（或 `vector` 排序 + `unique`）。
4. 頭尾都要進出 → `deque`。
5. `list` 很少是最好的選擇，除非真的需要「在已知位置 `O(1)` 插入刪除」或「迭代器永遠不失效」（例如 LRU）。

## 2.3 emplace vs push / insert

```cpp
vector<pair<string, int>> v;
v.push_back(make_pair("a", 1));   // 先建立暫時的 pair，再移動進去
v.emplace_back("a", 1);           // 直接在 vector 裡建構 pair，參數直接轉給建構子
```

`emplace` 系列 **直接在容器的記憶體裡建構物件**，少一次暫時物件的建立與移動。對簡單型別沒差別，對大物件或不能移動的物件比較有用。

## 2.4 map 的四種存取 / 插入方式

| 寫法 | key 不存在時 | key 已存在時 | 回傳 |
|---|---|---|---|
| `m[k]` | **插入預設值**（0、空字串） | — | 值的參考 |
| `m.at(k)` | **丟出 `out_of_range`** | — | 值的參考 |
| `m.find(k)` | 回傳 `m.end()` | 回傳指向元素的迭代器 | 迭代器 |
| `m.insert({k, v})` / `m.emplace(k, v)` | 插入 | **不覆蓋**，什麼都不做 | `pair<迭代器, bool>` |
| `m.insert_or_assign(k, v)` | 插入 | 覆蓋 | 同上 |

```cpp
map<string, int> m;
if (m["x"] > 0) ...           // ❌ 只是想查詢，卻插入了 {"x", 0}
if (m.count("x") && m["x"] > 0) ...
if (auto it = m.find("x"); it != m.end() && it->second > 0) ...   // ✅ 只查一次
```

`const map` 不能用 `[]`（因為它可能會插入），要用 `at` 或 `find`。

## 2.5 set / map 的元素不能直接修改

`set` 的元素、`map` 的 **key** 是 `const` 的：修改它會破壞樹的排序。要改的話：先刪除、再插入新值。

---

# 第三部分：迭代器 (Iterator)

## 3.1 半開區間 (Half-open Range)

**白話**：STL 的範圍一律是 `[begin, end)`：**包含 begin，不包含 end**。`end()` 指向「**最後一個元素的下一個位置**」，不能解參考。

```
 begin()                    end()
   ↓                          ↓
 [ 10 | 20 | 30 | 40 | 50 ]  （這裡沒有元素）
```

**好處**：
- 元素個數 = `end - begin`。
- 空範圍就是 `begin == end`，不需要特別處理。
- 找不到時回傳 `end()`，很自然地代表「不在範圍裡」。

**比喻**：尺上量 3 公分到 7 公分，長度是 7 − 3 = 4，「7」是刻度不是一格。

## 3.2 迭代器分類 (Iterator Categories)

| 分類 | 能做什麼 | 例子 |
|---|---|---|
| 輸入 (input) | 讀一次、往前走 | `istream_iterator` |
| 輸出 (output) | 寫一次、往前走 | `back_inserter` |
| 前向 (forward) | 讀寫、往前走、可以走很多次 | `forward_list`、`unordered_*` |
| 雙向 (bidirectional) | 加上 **往回走** `--it` | `list`、`set`、`map` |
| 隨機存取 (random access) | 加上 **跳躍** `it + n`、`it[n]`、`it2 - it1` | `vector`、`deque`、陣列 |

演算法會要求最低的分類：`sort` 需要 **隨機存取** 迭代器，所以 **`list` 不能用 `std::sort`**，要用 `list.sort()` 成員函式。

```cpp
list<int> l = {3, 1, 2};
sort(l.begin(), l.end());     // ❌ 編譯錯誤（而且錯誤訊息很長）
l.sort();                     // ✅
```

## 3.3 反向迭代器

```cpp
for (auto it = v.rbegin(); it != v.rend(); ++it) cout << *it;   // 倒著走
sort(v.rbegin(), v.rend());                                     // 由大到小排序
```

## 3.4 迭代器失效 (Iterator Invalidation)

**白話**：容器被修改後，某些迭代器（以及指標、參考）**不再有效**，繼續使用是未定義行為。

| 容器 | 插入時 | 刪除時 |
|---|---|---|
| `vector` | 觸發擴容 → **全部失效**；沒擴容 → 插入點之後的失效 | 刪除點之後的失效 |
| `deque` | 頭尾插入：迭代器全部失效（但元素的參考仍有效） | 頭尾刪除只影響被刪的；中間刪除全部失效 |
| `list` / `set` / `map` | **都不失效** | 只有被刪除的那個失效 |
| `unordered_*` | 觸發 rehash → 迭代器全部失效 | 只有被刪除的那個失效 |

**邊走訪邊刪除** 的正確寫法：

```cpp
for (auto it = v.begin(); it != v.end(); ) {
    if (*it % 2 == 0) it = v.erase(it);    // erase 回傳下一個有效的迭代器
    else ++it;
}
// 或者更好的寫法：erase-remove（第 6.1 節），或 C++20 的 erase_if(v, pred)
```

---

# 第四部分：演算法 (Algorithms)

`#include <algorithm>`、`#include <numeric>`

## 4.1 搜尋與計數

| 演算法 | 作用 | 複雜度 |
|---|---|---|
| `find(b, e, x)` / `find_if(b, e, pred)` | 第一個等於 x / 符合條件的位置 | `O(n)` |
| `count(b, e, x)` / `count_if` | 等於 x / 符合條件的個數 | `O(n)` |
| `any_of` / `all_of` / `none_of` | 有任何 / 全部 / 沒有一個符合 | `O(n)` |
| `min_element` / `max_element` | 最小 / 最大值的 **位置** | `O(n)` |

```cpp
int evens = count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; });
auto it = max_element(v.begin(), v.end());
int maxv = *it, idx = it - v.begin();
```

## 4.2 排序相關

| 演算法 | 作用 | 複雜度 | 穩定？ |
|---|---|---|---|
| `sort` | 排序 | `O(n log n)` | ❌ |
| `stable_sort` | 排序，相等的元素 **保持原本順序** | `O(n log n)` | ✅ |
| `partial_sort(b, m, e)` | 只把最小的 `m - b` 個排好放在前面 | `O(n log k)` | ❌ |
| `nth_element(b, nth, e)` | 讓第 n 小的元素到正確位置，左邊都 ≤ 它、右邊都 ≥ 它 | 平均 `O(n)` | ❌ |
| `reverse` | 反轉 | `O(n)` | |

**穩定排序 (stable sort)**：相等的元素在排序後 **保持排序前的相對順序**。`C08` 的「面積相同時保持輸入順序」就需要它。

```cpp
nth_element(v.begin(), v.begin() + v.size() / 2, v.end());   // 平均 O(n) 找中位數
int median = v[v.size() / 2];
```

## 4.3 二分搜尋（範圍必須已排序）

| 演算法 | 回傳 |
|---|---|
| `binary_search(b, e, x)` | `bool`：有沒有 x |
| `lower_bound(b, e, x)` | 第一個 **≥ x** 的位置 |
| `upper_bound(b, e, x)` | 第一個 **> x** 的位置 |
| `equal_range(b, e, x)` | `[lower_bound, upper_bound)` 這個範圍，就是所有等於 x 的元素 |

```cpp
vector<int> v = {1, 3, 3, 3, 7};
lower_bound(v.begin(), v.end(), 3) - v.begin();   // 1
upper_bound(v.begin(), v.end(), 3) - v.begin();   // 4
upper_bound(...) - lower_bound(...);               // 3：x 出現幾次
lower_bound(v.begin(), v.end(), 5) - v.begin();   // 4：5 應該插入的位置
```

> `set` 和 `map` 要用 **成員函式** `s.lower_bound(x)`（`O(log n)`）。用 `std::lower_bound(s.begin(), s.end(), x)` 雖然能編譯，但因為迭代器不是隨機存取，會變成 `O(n)`。

## 4.4 修改序列

| 演算法 | 作用 |
|---|---|
| `copy(b, e, out)` | 複製到 `out` 開始的位置 |
| `transform(b, e, out, f)` | 每個元素套用 `f`，結果寫到 `out` |
| `fill(b, e, x)` | 全部設成 x |
| `replace(b, e, old, new)` | 把 old 換成 new |
| `remove(b, e, x)` / `remove_if` | 把 **不等於 x 的元素往前搬**，回傳新的結尾（**不會真的刪除**，見 6.1） |
| `unique(b, e)` | 把 **相鄰** 的重複元素移到後面，回傳新的結尾 |
| `rotate`、`shuffle`、`next_permutation` | 旋轉、隨機打亂、下一個排列 |

```cpp
string s = "Hello";
transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return tolower(c); });   // 轉小寫
vector<int> out;
copy_if(v.begin(), v.end(), back_inserter(out), [](int x) { return x > 0; });       // back_inserter 會自動 push_back
```

## 4.5 數值演算法 (`<numeric>`)

```cpp
long long total = accumulate(v.begin(), v.end(), 0LL);   // 總和（注意初值的型別！見 6.2）
iota(v.begin(), v.end(), 1);                             // 填入 1, 2, 3, ...
partial_sum(v.begin(), v.end(), prefix.begin());         // 前綴和
int g = gcd(12, 18);                                     // 6（C++17）
```

## 4.6 集合運算（範圍必須已排序）

```cpp
set_intersection(a.begin(), a.end(), b.begin(), b.end(), back_inserter(out));   // 交集
set_union(...);          // 聯集
set_difference(...);     // 差集
includes(...);           // a 是否包含 b 的全部
```

---

# 第五部分：函式物件與自訂規則

## 5.1 函式物件 (Function Object / Functor)

**白話**：**有 `operator()` 的物件**，可以像函式一樣被呼叫。lambda 其實就是編譯器幫你產生的函式物件。

```cpp
struct ByLength {
    bool operator()(const string& a, const string& b) const { return a.size() < b.size(); }
};
sort(words.begin(), words.end(), ByLength());
```

標準函式物件：`less<>`、`greater<>`、`plus<>`、`equal_to<>` ……

```cpp
sort(v.begin(), v.end(), greater<>());                   // 由大到小
priority_queue<int, vector<int>, greater<>> minpq;       // 最小堆積
set<int, greater<>> desc_set;                            // 由大到小排序的 set
```

## 5.2 容器的自訂比較

```cpp
auto cmp = [](const Point& a, const Point& b) { return tie(a.x, a.y) < tie(b.x, b.y); };
set<Point, decltype(cmp)> s(cmp);       // lambda 要用 decltype 取型別，並傳進建構子
```

或者直接幫 `Point` 定義 `operator<`，`set<Point>` 就能直接用。

## 5.3 自訂雜湊 (Custom Hash)

`unordered_map` 的 key 是自訂型別時，要提供 **雜湊函式** 和 **相等比較**：

```cpp
struct Point { int x, y; bool operator==(const Point& o) const { return x == o.x && y == o.y; } };
struct PointHash {
    size_t operator()(const Point& p) const {
        // 先轉成無號數再移位（對負數左移在 C++20 前是未定義行為）
        return hash<unsigned long long>()(((unsigned long long)(unsigned)p.x << 32) | (unsigned)p.y);
    }
};
unordered_map<Point, int, PointHash> m;
```

`pair<int, int>` 也沒有內建的雜湊，要自己寫（或改用 `map<pair<int,int>, int>`）。

---

# 第六部分：經典陷阱

## 6.1 remove 不會真的刪除：erase-remove 慣用法

**白話**：演算法只看得到迭代器，**沒辦法改變容器的大小**。`remove` 只是把「要保留的元素」**往前搬**，回傳新的邏輯結尾；後面剩下的元素還在，`size()` 沒變。

```cpp
vector<int> v = {1, 2, 3, 2, 4};
auto new_end = remove(v.begin(), v.end(), 2);
// v 現在是 {1, 3, 4, ?, ?}，size() 還是 5
v.erase(new_end, v.end());                    // 真的刪掉
// 合起來：erase-remove 慣用法
v.erase(remove(v.begin(), v.end(), 2), v.end());
// C++20：
erase(v, 2);
erase_if(v, [](int x) { return x % 2 == 0; });
```

**比喻**：`remove` 像是把要留的書往書架左邊推，右邊剩下的位置還沒清空；`erase` 才是真的把右邊的東西拿走。

## 6.2 accumulate 的初值決定了型別

```cpp
vector<int> v(100000, 100000);
accumulate(v.begin(), v.end(), 0);       // ❌ 初值 0 是 int，加總用 int 計算 → 溢位
accumulate(v.begin(), v.end(), 0LL);     // ✅ 用 long long 計算

vector<double> d = {0.5, 0.5};
accumulate(d.begin(), d.end(), 0);       // ❌ 結果是 0！每次加完都被截成 int
accumulate(d.begin(), d.end(), 0.0);     // ✅ 1.0
```

## 6.3 unique 只移除「相鄰」的重複

```cpp
vector<int> v = {3, 1, 3, 1};
v.erase(unique(v.begin(), v.end()), v.end());   // 沒有相鄰的重複 → 什麼都沒刪
sort(v.begin(), v.end());                       // 先排序，讓相同的值相鄰
v.erase(unique(v.begin(), v.end()), v.end());   // {1, 3}
```

## 6.4 其他常見陷阱

| 陷阱 | 說明 |
|---|---|
| `priority_queue` 預設是 **最大** 堆積 | 要最小堆積用 `greater<>` |
| `m[k]` 會插入 | 只查詢用 `find` / `count` / `contains`（C++20） |
| `v.size() - 1` 在空容器時 | 無號數繞回，變成超大的數 |
| `std::sort` 用在 `list` 上 | 編譯錯誤，要用 `l.sort()` |
| `std::lower_bound` 用在 `set` 上 | 能編譯但變成 `O(n)`，要用 `s.lower_bound` |
| 比較函式用 `<=` | 違反嚴格弱序，可能當掉（第 04 課） |
| 走訪時修改容器 | 迭代器失效（第 3.4 節） |
| `tolower(c)` 的 `c` 是負的 `char` | 未定義行為，先轉 `unsigned char` |
| `vector<bool>` | 是特化版本，`auto& b = v[0]` 不能編譯、行為和其他 vector 不同 |

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 標準模板函式庫 | STL | C++ 內建的容器與演算法 | 1.1 |
| 序列容器 | Sequence Container | 依插入順序存放 | 2.1 |
| 關聯容器 | Associative Container | 依 key 組織（有序或雜湊） | 2.1 |
| 容器配接器 | Container Adapter | 包裝其他容器、只開放部分操作 | 2.1 |
| 就地建構 | Emplace | 直接在容器裡建構物件 | 2.3 |
| 半開區間 | Half-open Range `[b, e)` | 包含開頭、不包含結尾 | 3.1 |
| 迭代器分類 | Iterator Category | 輸入 / 輸出 / 前向 / 雙向 / 隨機存取 | 3.2 |
| 迭代器失效 | Iterator Invalidation | 容器修改後迭代器不能再用 | 3.4 |
| 穩定排序 | Stable Sort | 相等元素保持原本順序 | 4.2 |
| 二分搜尋 | Binary Search | 在已排序範圍中每次砍一半 | 4.3 |
| 函式物件 | Function Object / Functor | 有 `operator()` 的物件 | 5.1 |
| erase-remove 慣用法 | Erase-remove Idiom | 先 remove 搬動、再 erase 刪除 | 6.1 |

---

# 習題

### 題 1：預測輸出

```cpp
vector<int> v = {5, 1, 4, 1, 5, 9, 2, 6};
sort(v.begin(), v.end());
cout << lower_bound(v.begin(), v.end(), 5) - v.begin() << ' '
     << upper_bound(v.begin(), v.end(), 5) - v.begin() << ' '
     << count(v.begin(), v.end(), 1);
```

### 題 2：預測輸出

```cpp
vector<int> v = {1, 2, 3, 2, 5};
remove(v.begin(), v.end(), 2);
cout << v.size();
```

### 題 3：找 bug（想刪掉所有負數）

```cpp
for (auto it = v.begin(); it != v.end(); ++it)
    if (*it < 0) v.erase(it);
```

### 題 4：預測輸出

```cpp
vector<double> d = {1.5, 2.5, 3.5};
cout << accumulate(d.begin(), d.end(), 0) << ' ' << accumulate(d.begin(), d.end(), 0.0);
```

### 題 5：選擇最適合的容器

```
a) 記錄網站目前線上的使用者 ID，常常要查詢某個 ID 是否在線
b) 排行榜：隨時插入新分數，隨時要查「比 X 分高的有幾個人」
c) 讀入 10^6 個數字，之後只會依序走訪和排序
d) 印表機的列印工作，先送出的先印
e) 瀏覽器的「上一頁」
```

### 題 6：為什麼下面這行不能編譯？怎麼改？

```cpp
list<int> l = {3, 1, 2};
sort(l.begin(), l.end());
```

### 題 7：用 STL 演算法（不寫迴圈）寫出：把 `vector<string> words` 去除重複後，依長度由短到長排序（長度相同依字典序）。

---

# 習題解答

**題 1**：排序後 `{1, 1, 2, 4, 5, 5, 6, 9}`。`lower_bound(5)` = 4，`upper_bound(5)` = 6，`count(1)` = 2。輸出 `4 6 2`。

**題 2**：`5`。`remove` 不改變容器大小，只是把 `{1, 3, 5}` 搬到前面（`v` 變成 `{1, 3, 5, 2, 5}` 之類，後面的值未指定）。要接著 `erase`。

**題 3**：`erase(it)` 之後 `it` **失效** 了，再 `++it` 是未定義行為（而且就算碰巧能跑，也會跳過被刪除元素的下一個）。改成：

```cpp
for (auto it = v.begin(); it != v.end(); )
    if (*it < 0) it = v.erase(it); else ++it;
// 或
v.erase(remove_if(v.begin(), v.end(), [](int x) { return x < 0; }), v.end());
```

**題 4**：`6 7.5`。初值 `0` 是 `int`，每次相加的結果都被截成 `int`：`0 + 1.5 → 1`，`1 + 2.5 → 3`，`3 + 3.5 → 6`。

**題 5**：
- a) `unordered_set`：只需要查詢存不存在。
- b) `multiset`（或有序結構）：要能依分數排序並查範圍。（`multiset` 查「比 X 高的有幾個」要用 `distance`，是 `O(n)`；真正 `O(log n)` 需要順序統計樹 / BIT，這是進階主題。）
- c) `vector`。
- d) `queue`。
- e) `stack`。

**題 6**：`std::sort` 需要 **隨機存取迭代器**，`list` 只有雙向迭代器。改用成員函式 `l.sort();`。

**題 7**：

```cpp
sort(words.begin(), words.end());
words.erase(unique(words.begin(), words.end()), words.end());
stable_sort(words.begin(), words.end(), [](const string& a, const string& b) { return a.size() < b.size(); });
```

先依字典序排序並去重；再用 **穩定排序** 依長度排，長度相同的保持字典序。

---

# 程式練習

- **`C11 單字頻率統計`**：`unordered_map` 計數、`vector<pair>` + `sort` + lambda 排序、`isalpha` / `tolower` 的正確用法、讀到 EOF。
