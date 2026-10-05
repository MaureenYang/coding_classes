# 11. STL 深入 (Standard Template Library)

> 程式練習：`C11 單字頻率統計`
>
> 先備知識：第 10 課「模板」、第 04 課「lambda」。資料結構路線的教學介紹過各容器的 **原理**，這一課著重在 **怎麼正確使用**。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | STL 的架構 | 容器、迭代器、演算法為什麼要分開 |
| 第二部分 | 容器 | 每種容器的常用操作（都有範例）、複雜度、怎麼選、`map` 的五種存取方式 |
| 第三部分 | 迭代器 | 半開區間、五種分類、`next`/`prev`/`distance`、插入迭代器、迭代器失效 |
| 第四部分 | 演算法 | 搜尋、排序、二分搜、修改序列、數值、集合運算、排列 |
| 第五部分 | 函式物件與自訂規則 | 比較器、`greater<>`、自訂雜湊 |
| 第六部分 | 經典陷阱 | erase-remove、`accumulate` 溢位、`unique` 要先排序…… |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際編譯執行過的結果。標 🔍 的是深入內容。

本課的範例常用這個小工具印出容器：

```cpp
template <class C>
void show(const C& c) {
    for (const auto& x : c) cout << x << ' ';
    cout << '\n';
}
```

---

# 第一部分：STL 的架構

## 1.1 三大元件

| 元件 | 英文 | 角色 | 例子 |
|---|---|---|---|
| 容器 | Container | **存放** 資料 | `vector`、`map`、`set` |
| 迭代器 | Iterator | **走訪** 容器的「游標」 | `v.begin()`、`m.find(k)` |
| 演算法 | Algorithm | **處理** 資料 | `sort`、`find`、`count` |

另外還有輔助的 **函式物件**（比較規則，第五部分）和 **配接器**（`stack`、`back_inserter`）。

## 1.2 為什麼要分開？

**是什麼**：演算法 **不直接操作容器**，而是操作 **迭代器指定的範圍**。所以一個演算法可以用在 **所有** 提供適當迭代器的容器上。

**比喻**：通用的插座規格。有 N 種電器、M 種插座，如果每種電器都要配每種插座，要做 N × M 種接頭；統一了插座規格（迭代器），只要 N + M 種就夠了。STL 有十幾種容器、上百個演算法，靠迭代器讓它們全部能互相搭配。

```cpp
vector<int> v = {3, 1, 2};
list<int> l = {3, 1, 2};
int arr[] = {3, 1, 2};
cout << (find(v.begin(), v.end(), 2) != v.end()) << ' '   // 同一個 find
     << (find(l.begin(), l.end(), 2) != l.end()) << ' '   // 用在不同的容器
     << (find(arr, arr + 3, 9) != arr + 3) << '\n';       // 連普通陣列都可以（指標就是迭代器）
// 輸出：1 1 0
```

演算法也可以只處理 **一部分**：

```cpp
vector<int> w = {5, 4, 3, 2, 1};
sort(w.begin(), w.begin() + 3);      // 只排前三個
show(w);                             // 輸出：3 4 5 2 1
```

---

# 第二部分：容器

## 2.1 容器總覽

| 類別 | 容器 | 特色 |
|---|---|---|
| **序列容器** (sequence) | `vector` | 動態陣列，**預設首選** |
| | `deque` | 頭尾都能快速增刪 |
| | `list` / `forward_list` | 雙向 / 單向串列，已知位置時增刪 `O(1)` |
| | `array` | 固定大小，資料直接放在物件裡 |
| **有序關聯容器** (ordered associative) | `set` / `multiset` | 自動排序的集合（紅黑樹） |
| | `map` / `multimap` | 自動依 key 排序的對照表 |
| **無序關聯容器** (unordered) | `unordered_set` / `unordered_map` | 雜湊表，平均 `O(1)` |
| **容器配接器** (adapter) | `stack`、`queue`、`priority_queue` | 包裝其他容器，只開放特定操作 |

**所有容器都有的操作**：`size()`、`empty()`、`clear()`、`begin()` / `end()`、`==` 比較、`swap`。

## 2.2 vector

**是什麼**：動態陣列。元素在記憶體中 **連續存放**，可以用 `[i]` 隨機存取，尾端增刪很快。

```cpp
vector<int> v;                 // 空的
vector<int> a(5);              // 5 個 0
vector<int> b(3, 7);           // 3 個 7
vector<int> c = {1, 2, 3};     // 初始化串列
vector<int> d(c.begin(), c.end());   // 從另一個範圍複製
show(a); show(b); show(d);
// 輸出：
// 0 0 0 0 0
// 7 7 7
// 1 2 3
```

**存取**：

```cpp
vector<int> v = {10, 20, 30};
cout << v[0] << ' ' << v.at(1) << ' ' << v.front() << ' ' << v.back() << '\n';   // 輸出：10 20 10 30
try { v.at(5); }
catch (const out_of_range& e) { cout << "越界\n"; }      // 輸出：越界（at 會檢查，[] 不會）
int* raw = v.data();                                     // 指向底層陣列的指標（給 C 函式用）
cout << raw[2] << '\n';                                  // 輸出：30
```

**增刪**：

```cpp
vector<int> v = {1, 2, 3};
v.push_back(4);                      // 尾端加入：攤銷 O(1)
v.pop_back();                        // 尾端刪除：O(1)
v.insert(v.begin() + 1, 99);         // 在位置 1 插入：O(n)，後面的元素都要往後搬
show(v);                             // 輸出：1 99 2 3
v.erase(v.begin());                  // 刪除位置 0：O(n)
show(v);                             // 輸出：99 2 3
v.insert(v.end(), {7, 8});           // 一次插入好幾個
v.erase(v.begin(), v.begin() + 2);   // 刪除範圍 [0, 2)
show(v);                             // 輸出：3 7 8
v.resize(5);                         // 變成 5 個，新的補 0
show(v);                             // 輸出：3 7 8 0 0
v.resize(2);                         // 變成 2 個，多的刪掉
show(v);                             // 輸出：3 7
```

**size 與 capacity**：

- `size()`：目前有幾個元素。
- `capacity()`：目前配置的空間能放幾個（不用重新配置的話）。
- 空間不夠時，`vector` 會配置一塊 **更大**（GCC 是 2 倍）的新空間、把元素搬過去 —— 這就是為什麼 `push_back` 是「攤銷」`O(1)`（DS 路線第 03 課）。

```cpp
vector<int> v;
for (int i = 0; i < 9; i++) {
    v.push_back(i);
    cout << v.capacity() << ' ';
}
cout << '\n';                        // 輸出（GCC）：1 2 4 4 8 8 8 8 16

vector<int> w;
w.reserve(100);                      // 事先配置空間：之後 100 次 push_back 都不會重新配置
cout << w.size() << ' ' << w.capacity() << '\n';   // 輸出：0 100
```

**`reserve` vs `resize`**：`reserve(n)` 只配置空間、`size` 不變；`resize(n)` 真的建立 n 個元素。

```cpp
vector<int> x;
x.reserve(3);
// x[0] = 1;                         // ❌ 未定義行為：size 還是 0，沒有元素可以存取
x.resize(3);
x[0] = 1;                            // ✅
```

## 2.3 deque

**是什麼**：double-ended queue（雙端佇列）。**頭尾** 增刪都是 `O(1)`，也能用 `[i]` 隨機存取。內部是好幾塊固定大小的陣列（不是一整塊連續記憶體）。

```cpp
deque<int> dq = {2, 3};
dq.push_front(1);                    // vector 沒有 push_front
dq.push_back(4);
show(dq);                            // 輸出：1 2 3 4
dq.pop_front();
cout << dq[0] << ' ' << dq.size() << '\n';   // 輸出：2 3
```

**什麼時候用**：需要從兩端進出（滑動視窗、BFS 的 0-1 變形）。只需要尾端時用 `vector`（比較快）。

## 2.4 list 與 forward_list

**是什麼**：`list` 是雙向鏈結串列、`forward_list` 是單向。**已知位置** 時插入刪除是 `O(1)`，而且 **插入刪除不會讓其他元素的迭代器失效**。不能用 `[i]`。

```cpp
list<int> l = {1, 2, 3};
l.push_front(0);
auto it = next(l.begin(), 2);        // 指向 2（list 不能寫 l.begin() + 2）
l.insert(it, 99);                    // 在 2 前面插入：O(1)
show(l);                             // 輸出：0 1 99 2 3
l.remove(99);                        // 成員函式 remove：真的刪除所有 99
show(l);                             // 輸出：0 1 2 3
```

**list 特有的成員函式**（比通用演算法更有效率）：

```cpp
list<int> a = {5, 1, 3}, b = {4, 2};
a.sort(); b.sort();                  // std::sort 不能用在 list 上（3.2 節）
a.merge(b);                          // 合併兩個已排序的 list：O(n)，b 變空的
show(a);                             // 輸出：1 2 3 4 5
cout << b.size() << '\n';            // 輸出：0
a.reverse();
show(a);                             // 輸出：5 4 3 2 1

list<int> src = {7, 8};
a.splice(a.begin(), src);            // 把 src 整個「接」到 a 的開頭：O(1)，不複製任何元素
show(a);                             // 輸出：7 8 5 4 3 2 1
```

**什麼時候用**：很少。LRU 快取（DS 路線第 10 題）就是典型例子：需要 `O(1)` 把某個節點搬到最前面（`splice`），而且雜湊表裡存的迭代器不能失效。

## 2.5 array

**是什麼**：固定大小的陣列，大小是模板參數（第 10 課 4.1）。跟 C 陣列一樣快，但多了 `size()`、`at()`、可以複製、可以比較、不會退化成指標。

```cpp
array<int, 4> a = {3, 1, 4, 1};
array<int, 4> b = a;                 // ✅ 可以整個複製（C 陣列不行）
sort(b.begin(), b.end());
cout << a.size() << ' ' << (a == b) << ' ' << b[0] << '\n';   // 輸出：4 0 1
```

## 2.6 set 與 multiset

**是什麼**：`set` 是 **自動排序、不重複** 的集合；`multiset` 允許重複。內部是平衡二元搜尋樹（紅黑樹），插入、刪除、搜尋都是 `O(log n)`。

```cpp
set<int> s = {5, 1, 3};
s.insert(3);                          // 已經有了，不會重複
s.insert(2);
show(s);                              // 輸出：1 2 3 5（自動排序）

auto [it, ok] = s.insert(4);          // insert 回傳 pair<迭代器, 是否真的插入>
auto [it2, ok2] = s.insert(4);
cout << ok << ' ' << ok2 << ' ' << *it2 << '\n';   // 輸出：1 0 4

cout << s.count(3) << ' ' << s.count(9) << '\n';   // 輸出：1 0（set 的 count 只會是 0 或 1）
s.erase(1);
cout << *s.begin() << ' ' << *s.rbegin() << '\n';  // 輸出：2 5（最小值、最大值）
```

**找前後的值**（`map` 也一樣）：

```cpp
set<int> s = {10, 20, 30, 40};
cout << *s.lower_bound(25) << ' '     // 第一個 >= 25 → 30
     << *s.upper_bound(30) << ' '     // 第一個 > 30  → 40
     << *prev(s.lower_bound(25)) << '\n';   // 小於 25 的最大值 → 20
// 輸出：30 40 20
```

**multiset：刪除一個 vs 刪除全部**

```cpp
multiset<int> ms = {1, 2, 2, 2, 3};
cout << ms.count(2) << '\n';          // 輸出：3
ms.erase(ms.find(2));                 // 只刪「一個」2
cout << ms.count(2) << '\n';          // 輸出：2
ms.erase(2);                          // ⚠️ 用值刪除：刪「所有」2
cout << ms.count(2) << ' ' << ms.size() << '\n';   // 輸出：0 2
```

**常見錯誤**：想從 `multiset` 刪掉一個元素，卻寫 `ms.erase(x)`，結果全部刪光。

## 2.7 map 與 multimap

**是什麼**：`map<K, V>` 是 **自動依 key 排序** 的「key → value」對照表，key 不重複。每個元素是一個 `pair<const K, V>`。

```cpp
map<string, int> age = {{"bob", 25}, {"amy", 30}};
age["cat"] = 20;                      // 插入
age["bob"] = 26;                      // 修改
for (const auto& [name, a] : age)     // 結構化綁定（第 15 課）：依 key 排序走訪
    cout << name << '=' << a << ' ';
cout << '\n';                         // 輸出：amy=30 bob=26 cat=20
cout << age.size() << '\n';           // 輸出：3
age.erase("amy");
cout << age.begin()->first << '\n';   // 輸出：bob
```

### map 的五種存取 / 插入方式

| 寫法 | key 不存在時 | key 已存在時 | 回傳 |
|---|---|---|---|
| `m[k]` | **插入預設值**（0、空字串） | — | 值的參考 |
| `m.at(k)` | **丟出 `out_of_range`** | — | 值的參考 |
| `m.find(k)` | 回傳 `m.end()` | 回傳指向元素的迭代器 | 迭代器 |
| `m.insert({k, v})` / `m.emplace(k, v)` | 插入 | **不覆蓋**，什麼都不做 | `pair<迭代器, bool>` |
| `m.insert_or_assign(k, v)` | 插入 | 覆蓋 | `pair<迭代器, bool>` |

每一種都用一次：

```cpp
map<string, int> m = {{"a", 1}};

// 1. operator[]：不存在就插入預設值
cout << m["zzz"] << ' ' << m.size() << '\n';     // 輸出：0 2（只是讀取，卻插入了 {"zzz", 0}！）

// 2. at：不存在就丟例外
try { m.at("nope"); }
catch (const out_of_range&) { cout << "沒有 nope\n"; }   // 輸出：沒有 nope

// 3. find：不存在就回傳 end()，不會插入
auto it = m.find("a");
if (it != m.end()) cout << it->first << ':' << it->second << '\n';   // 輸出：a:1
cout << (m.find("b") == m.end()) << '\n';        // 輸出：1

// 4. insert：已存在就不覆蓋
auto r1 = m.insert({"a", 100});
cout << r1.second << ' ' << m["a"] << '\n';      // 輸出：0 1（沒有插入，值還是 1）

// 5. insert_or_assign：已存在就覆蓋
m.insert_or_assign("a", 100);
cout << m["a"] << '\n';                          // 輸出：100
```

**只想查詢時不要用 `[]`**：

```cpp
if (m["x"] > 0) { }                                                // ❌ 只是想查詢，卻插入了 {"x", 0}
if (m.count("x") && m.at("x") > 0) { }                             // ✅ 但查了兩次
if (auto it = m.find("x"); it != m.end() && it->second > 0) { }    // ✅ 只查一次（C++17 if 初始化）
```

`const map` 不能用 `[]`（因為它可能會插入），要用 `at` 或 `find`：

```cpp
void print_age(const map<string, int>& m) {
    // cout << m["amy"];                          // ❌ error: passing 'const std::map<...>' as 'this' argument discards qualifiers
    cout << m.at("amy") << '\n';
}
```

**計數的慣用法**：`[]` 自動插入 0 的特性在計數時反而很方便。

```cpp
map<char, int> freq;
for (char c : string("banana")) freq[c]++;       // 第一次遇到時自動從 0 開始
for (auto [c, n] : freq) cout << c << n << ' ';
cout << '\n';                                    // 輸出：a3 b1 n2
```

**multimap**：一個 key 可以對應多個值，沒有 `[]`。

```cpp
multimap<string, string> phone;
phone.insert({"amy", "0911"});
phone.insert({"amy", "0922"});
phone.insert({"bob", "0933"});
auto [lo, hi] = phone.equal_range("amy");        // amy 的所有號碼
for (auto p = lo; p != hi; ++p) cout << p->second << ' ';
cout << '\n';                                    // 輸出：0911 0922
```

## 2.8 set / map 的 key 不能直接修改

`set` 的元素、`map` 的 **key** 是 `const` 的：修改它會破壞樹的排序。

```cpp
set<int> s = {1, 5, 9};
// *s.begin() = 100;                  // ❌ error: assignment of read-only location
s.erase(1);                           // 要改：先刪除
s.insert(100);                        // 再插入新值
show(s);                              // 輸出：5 9 100

map<string, int> m = {{"old", 1}};
auto node = m.extract("old");         // 🔍 C++17：拿出節點，改 key 再放回去（不重新配置記憶體）
node.key() = "new";
m.insert(std::move(node));
cout << m.begin()->first << '\n';     // 輸出：new
```

`map` 的 **value** 可以直接改：`m.begin()->second = 5;` 沒問題。

## 2.9 unordered_set 與 unordered_map

**是什麼**：用 **雜湊表** 實作（DS 路線第 09 課），插入、刪除、查詢 **平均 `O(1)`**。介面跟 `set` / `map` 幾乎一樣，但 **元素沒有順序**。

```cpp
unordered_map<string, int> stock;
stock["apple"] = 5;
stock["pear"] = 2;
stock["apple"] += 3;
cout << stock["apple"] << ' ' << stock.count("kiwi") << ' ' << stock.size() << '\n';   // 輸出：8 0 2

unordered_set<int> seen;
for (int x : {3, 1, 3, 2, 1}) seen.insert(x);
cout << seen.size() << ' ' << seen.count(2) << '\n';   // 輸出：3 1
```

**走訪的順序是不確定的**（取決於雜湊值、桶子數量，不同編譯器、甚至插入順序不同都會不一樣）。需要有序輸出時：改用 `map`，或複製到 `vector` 再排序。

```cpp
vector<pair<string, int>> items(stock.begin(), stock.end());
sort(items.begin(), items.end());
for (auto& [k, v] : items) cout << k << '=' << v << ' ';
cout << '\n';                         // 輸出：apple=8 pear=2
```

**`map` vs `unordered_map`**：

| | `map` | `unordered_map` |
|---|---|---|
| 實作 | 紅黑樹 | 雜湊表 |
| 查詢 | `O(log n)` | 平均 `O(1)`，最壞 `O(n)` |
| 有序 | ✅ 依 key 排序 | ❌ |
| `lower_bound`、找前後 | ✅ | ❌ |
| key 的要求 | 能用 `<` 比較 | 能雜湊 + 能用 `==` 比較（5.3 節） |

**🔍 效能小技巧**：已知大約要放多少元素時，先 `reserve(n)`，避免途中多次 rehash。

## 2.10 容器配接器：stack、queue、priority_queue

**是什麼**：包裝一個底層容器（預設 `deque` 或 `vector`），**只開放特定的操作**。沒有迭代器，不能走訪。

```cpp
stack<int> st;                        // 後進先出 LIFO
st.push(1); st.push(2); st.push(3);
cout << st.top() << ' ';              // 看頂端
st.pop();                             // 移除頂端（不回傳值！）
cout << st.top() << ' ' << st.size() << '\n';   // 輸出：3 2 2

queue<int> q;                         // 先進先出 FIFO
q.push(1); q.push(2); q.push(3);
cout << q.front() << ' ' << q.back() << ' ';
q.pop();
cout << q.front() << '\n';            // 輸出：1 3 2

priority_queue<int> pq;               // 預設：最大的在頂端
for (int x : {3, 1, 4, 1, 5}) pq.push(x);
while (!pq.empty()) { cout << pq.top() << ' '; pq.pop(); }
cout << '\n';                         // 輸出：5 4 3 1 1

priority_queue<int, vector<int>, greater<int>> minpq;   // 最小的在頂端
for (int x : {3, 1, 4}) minpq.push(x);
cout << minpq.top() << '\n';          // 輸出：1
```

**為什麼 `pop()` 不回傳值？** 歷史原因：如果 `pop()` 回傳被移除的元素，在複製這個元素時丟出例外，元素就已經被移除、又沒有成功回傳，資料就遺失了（第 13 課的例外安全）。所以拆成 `top()` 和 `pop()` 兩步。

**常見錯誤**：對空的 `stack` / `queue` / `priority_queue` 呼叫 `top()`、`front()`、`pop()` 是 **未定義行為**，先檢查 `empty()`。

## 2.11 複雜度速查與選擇

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
5. 只需要後進先出 / 先進先出 / 最大值 → `stack` / `queue` / `priority_queue`。
6. `list` 很少是最好的選擇，除非真的需要「在已知位置 `O(1)` 插入刪除」或「迭代器永遠不失效」（例如 LRU）。

## 2.12 emplace vs push / insert

**是什麼**：`emplace` 系列 **直接在容器的記憶體裡建構物件**，參數直接轉交給元素的建構子（第 10 課的完美轉發）；`push` / `insert` 則要先有一個完整的物件，再複製或移動進去。

```cpp
vector<pair<string, int>> v;
v.push_back(make_pair("a", 1));   // 先建立暫時的 pair，再移動進去
v.push_back({"b", 2});            // 同上
v.emplace_back("c", 3);           // 直接在 vector 裡用 ("c", 3) 建構 pair
cout << v.size() << ' ' << v[2].first << '\n';   // 輸出：3 c

map<string, int> m;
m.emplace("x", 1);                // map 也有 emplace
cout << m["x"] << '\n';           // 輸出：1
```

第 06 課用 `Tracer` 實際觀察過：`push_back(Tracer("tmp"))` 會「建立、移動、銷毀」，`emplace_back("direct")` 只有「建立」。

**什麼時候差別大**：元素很大、移動成本高，或元素根本不能移動 / 複製時。對 `int` 這類簡單型別沒有差別。

---

# 第三部分：迭代器 (Iterator)

## 3.1 迭代器是什麼

**是什麼**：指向容器中某個元素的「游標」，用法像指標：

| 操作 | 意思 |
|---|---|
| `*it` | 取得指向的元素 |
| `it->member` | 等於 `(*it).member` |
| `++it` | 移到下一個 |
| `it1 == it2` | 是不是指向同一個位置 |

```cpp
vector<string> v = {"aa", "bbb", "c"};
auto it = v.begin();                   // 型別是 vector<string>::iterator
cout << *it << ' ' << it->size() << '\n';   // 輸出：aa 2
++it;
cout << *it << '\n';                   // 輸出：bbb
*it = "B";                             // 可以透過迭代器修改
show(v);                               // 輸出：aa B c

auto cit = v.cbegin();                 // const_iterator：只能讀，不能改
// *cit = "x";                         // ❌ 編譯錯誤
```

## 3.2 半開區間 (Half-open Range)

**是什麼**：STL 的範圍一律是 `[begin, end)`：**包含 begin，不包含 end**。`end()` 指向「**最後一個元素的下一個位置**」，不能解參考。

```
 begin()                    end()
   ↓                          ↓
 [ 10 | 20 | 30 | 40 | 50 ]  （這裡沒有元素）
```

**好處**：
- 元素個數 = `end - begin`。
- 空範圍就是 `begin == end`，不需要特別處理。
- 找不到時回傳 `end()`，很自然地代表「不在範圍裡」。
- 把一個範圍切成兩半 `[b, m)`、`[m, e)` 很自然，不會重疊也不會漏掉。

**比喻**：尺上量 3 公分到 7 公分，長度是 7 − 3 = 4，「7」是刻度不是一格。

```cpp
vector<int> v = {10, 20, 30, 40, 50};
cout << v.end() - v.begin() << '\n';                      // 輸出：5
cout << accumulate(v.begin() + 1, v.begin() + 3, 0) << '\n';   // [1, 3) = 20 + 30 → 輸出：50
vector<int> empty_v;
cout << (empty_v.begin() == empty_v.end()) << '\n';       // 輸出：1
// cout << *v.end();                                      // ❌ 未定義行為
```

## 3.3 迭代器分類 (Iterator Categories)

| 分類 | 能做什麼 | 例子 |
|---|---|---|
| 輸入 (input) | 讀一次、往前走 | `istream_iterator` |
| 輸出 (output) | 寫一次、往前走 | `back_inserter`、`ostream_iterator` |
| 前向 (forward) | 讀寫、往前走、可以走很多次 | `forward_list`、`unordered_*` |
| 雙向 (bidirectional) | 加上 **往回走** `--it` | `list`、`set`、`map` |
| 隨機存取 (random access) | 加上 **跳躍** `it + n`、`it[n]`、`it2 - it1`、`<` | `vector`、`deque`、`array`、陣列 |

每一層都包含上一層的能力。演算法會要求最低的分類：`sort` 需要 **隨機存取** 迭代器，所以 **`list` 不能用 `std::sort`**：

```cpp
list<int> l = {3, 1, 2};
// sort(l.begin(), l.end());   // ❌ error: no match for 'operator-' (operand types are 'std::_List_iterator<int>' and 'std::_List_iterator<int>')
l.sort();                      // ✅ 用成員函式
show(l);                       // 輸出：1 2 3

set<int> s = {1, 2, 3};
auto it = s.begin();
// it + 2;                     // ❌ set 的迭代器是雙向的，不能跳
++it; ++it;                    // ✅ 只能一步一步走
cout << *it << '\n';           // 輸出：3
```

## 3.4 移動迭代器：next、prev、advance、distance

這幾個函式對 **任何** 迭代器都能用：隨機存取時是 `O(1)`，其他是 `O(n)`。

```cpp
list<int> l = {10, 20, 30, 40};
auto it = l.begin();
auto it2 = next(it, 2);              // 回傳往後 2 步的迭代器（it 本身不變）
cout << *it << ' ' << *it2 << '\n';  // 輸出：10 30
cout << *prev(l.end()) << '\n';      // 最後一個元素 → 輸出：40
advance(it, 3);                      // 直接移動 it 本身
cout << *it << '\n';                 // 輸出：40
cout << distance(l.begin(), it) << '\n';   // 兩個迭代器差幾步 → 輸出：3
```

| 函式 | 作用 | 修改原本的迭代器？ |
|---|---|---|
| `next(it, n)` | 回傳往後 n 步（預設 1） | ❌ |
| `prev(it, n)` | 回傳往前 n 步（需要雙向） | ❌ |
| `advance(it, n)` | 把 `it` 移動 n 步 | ✅ |
| `distance(a, b)` | 從 `a` 走到 `b` 要幾步 | ❌ |

## 3.5 反向迭代器

```cpp
vector<int> v = {1, 2, 3, 4};
for (auto it = v.rbegin(); it != v.rend(); ++it) cout << *it;   // 倒著走（++ 是往前）
cout << '\n';                                                   // 輸出：4321
sort(v.rbegin(), v.rend());                                     // 用反向迭代器排序 → 由大到小
show(v);                                                        // 輸出：4 3 2 1
vector<int> r(v.rbegin(), v.rend());                            // 反轉後的複製品
show(r);                                                        // 輸出：1 2 3 4
```

## 3.6 插入迭代器與串流迭代器

**問題**：演算法 **不能改變容器大小**，`copy` 到一個空的 `vector` 會寫到不存在的元素上。

```cpp
vector<int> src = {1, 2, 3};
vector<int> dst;
// copy(src.begin(), src.end(), dst.begin());     // ❌ 未定義行為：dst 是空的，沒有地方可以寫
```

**插入迭代器 (insert iterator)**：對它「寫入」時，會 **呼叫容器的插入函式**。

| 插入迭代器 | 寫入時呼叫 |
|---|---|
| `back_inserter(c)` | `c.push_back(x)` |
| `front_inserter(c)` | `c.push_front(x)` |
| `inserter(c, pos)` | `c.insert(pos, x)`（可以用在 `set`） |

```cpp
vector<int> dst;
copy(src.begin(), src.end(), back_inserter(dst));   // 每個元素都 push_back
show(dst);                                          // 輸出：1 2 3

deque<int> dq;
copy(src.begin(), src.end(), front_inserter(dq));   // 每個都 push_front → 順序相反
show(dq);                                           // 輸出：3 2 1

set<int> st;
copy(src.begin(), src.end(), inserter(st, st.end()));
cout << st.size() << '\n';                          // 輸出：3
```

**串流迭代器 (stream iterator)**：把輸入 / 輸出串流當成範圍。

```cpp
vector<int> v = {1, 2, 3};
copy(v.begin(), v.end(), ostream_iterator<int>(cout, ", "));   // 每個元素輸出後接 ", "
cout << '\n';                                                  // 輸出：1, 2, 3,

istringstream in("4 5 6");
vector<int> w(istream_iterator<int>(in), {});                  // 讀到串流結束
show(w);                                                       // 輸出：4 5 6
```

## 3.7 迭代器失效 (Iterator Invalidation)

**是什麼**：容器被修改後，某些迭代器（以及指向元素的指標、參考）**不再有效**，繼續使用是未定義行為。

**為什麼會失效？** 以 `vector` 為例：擴容時元素被搬到新的記憶體，舊的記憶體被釋放，指向舊位置的迭代器就變成懸置的了。

```cpp
vector<int> v = {1, 2, 3};
v.shrink_to_fit();                   // 讓 capacity 剛好等於 size（確保下一次 push_back 會擴容）
int* p = &v[0];
int* old_data = v.data();
v.push_back(4);                      // 擴容：元素被搬到新的記憶體
cout << (v.data() == old_data) << '\n';   // 輸出：0（記憶體位置變了，p 已經失效）
// cout << *p;                       // ❌ 未定義行為（用 --debug 執行會被 AddressSanitizer 抓到 heap-use-after-free）
```

| 容器 | 插入時 | 刪除時 |
|---|---|---|
| `vector` | 觸發擴容 → **全部失效**；沒擴容 → 插入點之後的失效 | 刪除點之後的失效 |
| `deque` | 頭尾插入：迭代器全部失效（但元素的參考仍有效）；中間插入：全部失效 | 頭尾刪除只影響被刪的；中間刪除全部失效 |
| `list` / `set` / `map` | **都不失效** | 只有被刪除的那個失效 |
| `unordered_*` | 觸發 rehash → 迭代器全部失效（參考仍有效） | 只有被刪除的那個失效 |

### 邊走訪邊刪除

```cpp
// ❌ 錯誤：erase 之後 it 失效，再 ++it 是未定義行為
// for (auto it = v.begin(); it != v.end(); ++it)
//     if (*it % 2 == 0) v.erase(it);

// ✅ 正確：erase 回傳「下一個有效的迭代器」
vector<int> v = {1, 2, 3, 4, 5, 6};
for (auto it = v.begin(); it != v.end(); ) {
    if (*it % 2 == 0) it = v.erase(it);   // 刪除後 it 指向下一個元素，不要再 ++
    else ++it;
}
show(v);                                  // 輸出：1 3 5

// map 也一樣
map<int, string> m = {{1, "a"}, {2, "b"}, {3, "c"}};
for (auto it = m.begin(); it != m.end(); ) {
    if (it->first != 2) it = m.erase(it);
    else ++it;
}
cout << m.size() << ' ' << m.begin()->second << '\n';   // 輸出：1 b
```

對 `vector` 更好的寫法是 erase-remove（6.1 節），或 C++20 的 `erase_if(v, pred)`。

### 邊走訪邊插入

```cpp
vector<int> v = {1, 2, 3};
// for (int x : v) if (x == 2) v.push_back(99);   // ❌ 範圍 for 內部用迭代器，push_back 可能讓它失效

size_t n = v.size();                     // ✅ 用索引，而且先記下原本的大小
for (size_t i = 0; i < n; i++) if (v[i] == 2) v.push_back(99);
show(v);                                 // 輸出：1 2 3 99
```

---

# 第四部分：演算法 (Algorithms)

`#include <algorithm>`、`#include <numeric>`

演算法的參數慣例：前兩個是範圍 `[first, last)`；結尾是 `_if` 的版本接受一個 **條件函式 (predicate)**（回傳 `bool` 的函式 / lambda）。

## 4.1 搜尋與計數

| 演算法 | 作用 | 複雜度 |
|---|---|---|
| `find(b, e, x)` / `find_if(b, e, pred)` | 第一個等於 x / 符合條件的位置（找不到回傳 `e`） | `O(n)` |
| `count(b, e, x)` / `count_if` | 等於 x / 符合條件的個數 | `O(n)` |
| `any_of` / `all_of` / `none_of` | 有任何 / 全部 / 沒有一個符合 | `O(n)` |
| `min_element` / `max_element` / `minmax_element` | 最小 / 最大值的 **位置** | `O(n)` |
| `search(b, e, sb, se)` | 子序列第一次出現的位置 | `O(n·m)` |
| `adjacent_find(b, e)` | 第一對相鄰相等元素的位置 | `O(n)` |

```cpp
vector<int> v = {4, 8, 15, 16, 23, 42};

auto it = find(v.begin(), v.end(), 15);
cout << (it - v.begin()) << '\n';                                   // 位置 → 輸出：2

auto odd = find_if(v.begin(), v.end(), [](int x) { return x % 2; });
cout << *odd << '\n';                                               // 第一個奇數 → 輸出：15

cout << count_if(v.begin(), v.end(), [](int x) { return x > 10; }) << '\n';   // 輸出：4

cout << all_of(v.begin(), v.end(), [](int x) { return x > 0; })
     << any_of(v.begin(), v.end(), [](int x) { return x > 40; })
     << none_of(v.begin(), v.end(), [](int x) { return x < 0; }) << '\n';    // 輸出：111

auto mx = max_element(v.begin(), v.end());
cout << *mx << " at " << (mx - v.begin()) << '\n';                  // 輸出：42 at 5
auto [mn, mx2] = minmax_element(v.begin(), v.end());
cout << *mn << ' ' << *mx2 << '\n';                                 // 輸出：4 42

vector<int> pat = {15, 16};
cout << (search(v.begin(), v.end(), pat.begin(), pat.end()) - v.begin()) << '\n';   // 輸出：2
vector<int> w = {1, 2, 2, 3};
cout << (adjacent_find(w.begin(), w.end()) - w.begin()) << '\n';    // 輸出：1
```

**注意**：`max_element` 回傳 **迭代器**，不是值。空範圍時回傳 `end()`，不能解參考。

## 4.2 排序相關

| 演算法 | 作用 | 複雜度 | 穩定？ |
|---|---|---|---|
| `sort` | 排序 | `O(n log n)` | ❌ |
| `stable_sort` | 排序，相等的元素 **保持原本順序** | `O(n log n)` | ✅ |
| `partial_sort(b, m, e)` | 只把最小的 `m - b` 個排好放在前面 | `O(n log k)` | ❌ |
| `nth_element(b, nth, e)` | 讓第 n 小的元素到正確位置，左邊都 ≤ 它、右邊都 ≥ 它 | 平均 `O(n)` | ❌ |
| `is_sorted` | 檢查是否已排序 | `O(n)` | |
| `reverse` | 反轉 | `O(n)` | |

```cpp
vector<int> v = {5, 2, 8, 1, 9, 3};

sort(v.begin(), v.end());                          // 由小到大
show(v);                                           // 輸出：1 2 3 5 8 9
sort(v.begin(), v.end(), greater<int>());          // 由大到小
show(v);                                           // 輸出：9 8 5 3 2 1
cout << is_sorted(v.begin(), v.end()) << '\n';     // 輸出：0（不是由小到大）

vector<int> p = {5, 2, 8, 1, 9, 3};
partial_sort(p.begin(), p.begin() + 3, p.end());   // 只要前 3 小，而且排好
cout << p[0] << p[1] << p[2] << '\n';              // 輸出：123（後面的順序不保證）

vector<int> q = {5, 2, 8, 1, 9, 3, 7};
nth_element(q.begin(), q.begin() + 3, q.end());    // 第 3 小（從 0 數）的放到位置 3
cout << q[3] << '\n';                              // 輸出：5（中位數；其他位置的順序不保證）

reverse(q.begin(), q.end());
```

### 穩定排序 (Stable Sort)

**是什麼**：相等的元素在排序後 **保持排序前的相對順序**。

```cpp
vector<pair<string, int>> people = {{"amy", 90}, {"bob", 80}, {"cat", 90}, {"dan", 80}};
stable_sort(people.begin(), people.end(),
            [](const auto& a, const auto& b) { return a.second > b.second; });   // 依分數由高到低
for (auto& [name, s] : people) cout << name << ' ';
cout << '\n';                        // 輸出：amy cat bob dan（同分的保持原本順序：amy 在 cat 前、bob 在 dan 前）
```

用 `sort` 的話，同分的 `amy` 和 `cat` 誰先誰後 **不保證**。`C08` 的「面積相同時保持輸入順序」就需要 `stable_sort`。

### 多重排序條件

```cpp
struct Student { string name; int score; int age; };
vector<Student> st = {{"amy", 90, 20}, {"bob", 90, 19}, {"cat", 85, 21}};
sort(st.begin(), st.end(), [](const Student& a, const Student& b) {
    if (a.score != b.score) return a.score > b.score;   // 1. 分數高的在前
    return a.age < b.age;                               // 2. 同分時年紀小的在前
});
for (auto& s : st) cout << s.name << ' ';
cout << '\n';                        // 輸出：bob amy cat

// 更短的寫法：用 tuple 比較（字典序）
sort(st.begin(), st.end(), [](const Student& a, const Student& b) {
    return make_tuple(-a.score, a.age) < make_tuple(-b.score, b.age);
});
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
//  索引：      0  1  2  3  4
cout << binary_search(v.begin(), v.end(), 3) << binary_search(v.begin(), v.end(), 4) << '\n';   // 輸出：10
auto lo = lower_bound(v.begin(), v.end(), 3);
auto hi = upper_bound(v.begin(), v.end(), 3);
cout << (lo - v.begin()) << ' ' << (hi - v.begin()) << ' ' << (hi - lo) << '\n';   // 輸出：1 4 3（3 出現 3 次）
cout << (lower_bound(v.begin(), v.end(), 5) - v.begin()) << '\n';   // 5 應該插入的位置 → 輸出：4
cout << (lower_bound(v.begin(), v.end(), 99) == v.end()) << '\n';   // 比全部都大 → 輸出：1
auto [a, b] = equal_range(v.begin(), v.end(), 3);
cout << (b - a) << '\n';                                            // 輸出：3
```

**常見用法：保持 vector 有序地插入**

```cpp
vector<int> sorted_v = {1, 4, 9};
sorted_v.insert(upper_bound(sorted_v.begin(), sorted_v.end(), 5), 5);
show(sorted_v);                      // 輸出：1 4 5 9
```

> **`set` 和 `map` 要用成員函式** `s.lower_bound(x)`（`O(log n)`）。用 `std::lower_bound(s.begin(), s.end(), x)` 雖然能編譯，但因為迭代器不是隨機存取，會變成 `O(n)`。

**沒排序就二分搜** → 結果沒有意義（不會報錯！）：

```cpp
vector<int> unsorted = {5, 1, 4};
cout << binary_search(unsorted.begin(), unsorted.end(), 5) << '\n';   // 輸出：0（明明有 5！）
```

## 4.4 修改序列

| 演算法 | 作用 |
|---|---|
| `copy(b, e, out)` / `copy_if` / `copy_n` | 複製到 `out` 開始的位置 |
| `transform(b, e, out, f)` | 每個元素套用 `f`，結果寫到 `out` |
| `fill(b, e, x)` / `fill_n` | 全部設成 x |
| `replace(b, e, old, new)` / `replace_if` | 把 old 換成 new |
| `remove(b, e, x)` / `remove_if` | 把 **要保留的元素往前搬**，回傳新的結尾（**不會真的刪除**，見 6.1） |
| `unique(b, e)` | 把 **相鄰** 的重複元素移到後面，回傳新的結尾 |
| `reverse`、`rotate` | 反轉、旋轉 |
| `shuffle(b, e, rng)` | 隨機打亂 |
| `swap(a, b)` / `iter_swap` | 交換 |

```cpp
vector<int> v = {1, 2, 3, 4, 5};

vector<int> sq(v.size());
transform(v.begin(), v.end(), sq.begin(), [](int x) { return x * x; });
show(sq);                                          // 輸出：1 4 9 16 25

vector<int> a = {1, 2, 3}, b = {10, 20, 30}, c(3);
transform(a.begin(), a.end(), b.begin(), c.begin(), plus<int>());   // 兩個範圍逐一相加
show(c);                                           // 輸出：11 22 33

vector<int> evens;
copy_if(v.begin(), v.end(), back_inserter(evens), [](int x) { return x % 2 == 0; });
show(evens);                                       // 輸出：2 4

vector<int> f(5);
fill(f.begin(), f.end(), 7);
fill_n(f.begin(), 2, 0);                           // 前 2 個設成 0
show(f);                                           // 輸出：0 0 7 7 7

replace(f.begin(), f.end(), 7, 1);
show(f);                                           // 輸出：0 0 1 1 1

vector<int> r = {1, 2, 3, 4, 5};
rotate(r.begin(), r.begin() + 2, r.end());         // 讓位置 2 的元素變成開頭
show(r);                                           // 輸出：3 4 5 1 2

string s = "Hello World";
transform(s.begin(), s.end(), s.begin(), [](unsigned char ch) { return toupper(ch); });
cout << s << '\n';                                 // 輸出：HELLO WORLD

mt19937 rng(42);                                   // 固定種子：每次執行結果相同
vector<int> deck = {1, 2, 3, 4, 5};
shuffle(deck.begin(), deck.end(), rng);            // 打亂（結果依種子而定）
sort(deck.begin(), deck.end());
show(deck);                                        // 輸出：1 2 3 4 5
```

## 4.5 數值演算法 (`<numeric>`)

| 演算法 | 作用 |
|---|---|
| `accumulate(b, e, init)` | 從 `init` 開始全部加起來（或用自訂運算） |
| `iota(b, e, x)` | 填入 x, x+1, x+2, ... |
| `partial_sum(b, e, out)` | 前綴和 |
| `adjacent_difference(b, e, out)` | 相鄰差（前綴和的反運算） |
| `inner_product(b1, e1, b2, init)` | 內積 |
| `gcd(a, b)` / `lcm(a, b)` | 最大公因數 / 最小公倍數（C++17） |

```cpp
vector<int> v(5);
iota(v.begin(), v.end(), 1);                               // 1 2 3 4 5
show(v);                                                   // 輸出：1 2 3 4 5

cout << accumulate(v.begin(), v.end(), 0) << '\n';         // 總和 → 輸出：15
cout << accumulate(v.begin(), v.end(), 1LL, multiplies<long long>()) << '\n';   // 乘積 → 輸出：120
string joined = accumulate(next(v.begin()), v.end(), to_string(v[0]),
                           [](string acc, int x) { return acc + "-" + to_string(x); });
cout << joined << '\n';                                    // 輸出：1-2-3-4-5

vector<int> pre(5);
partial_sum(v.begin(), v.end(), pre.begin());
show(pre);                                                 // 輸出：1 3 6 10 15

vector<int> diff(5);
adjacent_difference(pre.begin(), pre.end(), diff.begin());
show(diff);                                                // 輸出：1 2 3 4 5（還原了）

vector<int> w = {2, 0, 1, 0, 3};
cout << inner_product(v.begin(), v.end(), w.begin(), 0) << '\n';   // 1×2 + 3×1 + 5×3 → 輸出：20
cout << gcd(12, 18) << ' ' << lcm(4, 6) << '\n';           // 輸出：6 12
```

## 4.6 集合運算（範圍必須已排序）

```cpp
vector<int> a = {1, 2, 3, 4, 5}, b = {4, 5, 6, 7};
vector<int> out;

set_intersection(a.begin(), a.end(), b.begin(), b.end(), back_inserter(out));   // 交集
show(out);                                         // 輸出：4 5
out.clear();
set_union(a.begin(), a.end(), b.begin(), b.end(), back_inserter(out));          // 聯集
show(out);                                         // 輸出：1 2 3 4 5 6 7
out.clear();
set_difference(a.begin(), a.end(), b.begin(), b.end(), back_inserter(out));     // 差集 a − b
show(out);                                         // 輸出：1 2 3
out.clear();
set_symmetric_difference(a.begin(), a.end(), b.begin(), b.end(), back_inserter(out));   // 只在其中一邊
show(out);                                         // 輸出：1 2 3 6 7

vector<int> sub = {2, 4};
cout << includes(a.begin(), a.end(), sub.begin(), sub.end()) << '\n';   // a 包含 sub 的全部？ → 輸出：1
```

這些演算法可以直接用在 `set` 上（`set` 本來就是排序的）。

## 4.7 排列與比較

```cpp
vector<int> p = {1, 2, 3};
do {
    for (int x : p) cout << x;
    cout << ' ';
} while (next_permutation(p.begin(), p.end()));   // 依字典序產生下一個排列，沒有了就回傳 false
cout << '\n';                                    // 輸出：123 132 213 231 312 321

vector<int> x = {1, 2, 3}, y = {1, 2, 4};
cout << equal(x.begin(), x.end(), y.begin()) << ' '
     << lexicographical_compare(x.begin(), x.end(), y.begin(), y.end()) << '\n';   // 輸出：0 1
cout << (x < y) << '\n';                         // vector 的 < 就是字典序比較 → 輸出：1
```

**注意**：要列舉 **全部** 排列，起點必須是 **排序好的**（最小的排列）。DS 路線第 17 課的 N 皇后也可以用這個技巧。

---

# 第五部分：函式物件與自訂規則

## 5.1 函式物件 (Function Object / Functor)

**是什麼**：**有 `operator()` 的物件**，可以像函式一樣被呼叫（第 07 課 4.7）。lambda 其實就是編譯器幫你產生的函式物件。

三種寫比較規則的方式：

```cpp
// 1. 函式物件
struct ByLength {
    bool operator()(const string& a, const string& b) const { return a.size() < b.size(); }
};
// 2. 一般函式
bool by_length(const string& a, const string& b) { return a.size() < b.size(); }
// 3. lambda（最常用）
auto by_len = [](const string& a, const string& b) { return a.size() < b.size(); };

vector<string> w = {"ccc", "a", "bb"};
sort(w.begin(), w.end(), ByLength());   show(w);   // 輸出：a bb ccc
sort(w.begin(), w.end(), greater<>());  show(w);   // 輸出：ccc bb a（字典序反過來）
sort(w.begin(), w.end(), by_length);    show(w);   // 輸出：a bb ccc
```

### 標準函式物件 (`<functional>`)

| 函式物件 | 等於 |
|---|---|
| `less<T>` / `greater<T>` | `a < b` / `a > b` |
| `less_equal<T>` / `greater_equal<T>` | `a <= b` / `a >= b` |
| `equal_to<T>` / `not_equal_to<T>` | `a == b` / `a != b` |
| `plus<T>` / `minus<T>` / `multiplies<T>` | `a + b` / `a - b` / `a * b` |

寫成 `greater<>`（不寫型別）會自動推導，C++14 起可以用。

```cpp
vector<int> v = {3, 1, 2};
sort(v.begin(), v.end(), greater<>());           // 由大到小
show(v);                                         // 輸出：3 2 1

priority_queue<int, vector<int>, greater<>> minpq;   // 最小堆積
set<int, greater<>> desc = {1, 3, 2};            // 由大到小排序的 set
show(desc);                                      // 輸出：3 2 1
map<string, int, greater<>> rev_map = {{"a", 1}, {"b", 2}};
cout << rev_map.begin()->first << '\n';          // 輸出：b
```

## 5.2 容器的自訂比較

`set`、`map`、`priority_queue` 的比較規則是 **型別的一部分**（模板參數），所以寫法和 `sort` 不同。

```cpp
struct Point { int x, y; };

// 方法 1：函式物件（最簡單）
struct PointLess {
    bool operator()(const Point& a, const Point& b) const { return tie(a.x, a.y) < tie(b.x, b.y); }
};
set<Point, PointLess> s1 = {{2, 1}, {1, 5}, {1, 2}};
for (auto& p : s1) cout << '(' << p.x << ',' << p.y << ") ";
cout << '\n';                                    // 輸出：(1,2) (1,5) (2,1)

// 方法 2：lambda + decltype（lambda 的型別沒有名字，要用 decltype 取得，並傳進建構子）
auto by_y = [](const Point& a, const Point& b) { return a.y < b.y; };
set<Point, decltype(by_y)> s2(by_y);
s2.insert({{2, 1}, {1, 5}, {1, 2}});
for (auto& p : s2) cout << '(' << p.x << ',' << p.y << ") ";
cout << '\n';                                    // 輸出：(2,1) (1,2) (1,5)
```

**方法 3**：直接幫 `Point` 定義 `operator<`，`set<Point>` 就能直接用（第 07 課）。

`tie(a.x, a.y) < tie(b.x, b.y)`：把成員打包成 `tuple` 比較，就是「先比 x、x 相同再比 y」的字典序，不用自己寫一堆 `if`。

**⚠️ set 用比較規則判斷「相等」**：在 `set` 裡，`!(a < b) && !(b < a)` 就被當成「相同」。所以只比較部分欄位時，欄位相同的元素會被視為重複：

```cpp
set<Point, decltype(by_y)> s3(by_y);
s3.insert({1, 5});
s3.insert({9, 5});                               // y 相同 → 被當成「已存在」，不會插入！
cout << s3.size() << '\n';                       // 輸出：1
```

**priority_queue 的比較方向是反的**：比較規則說「`a < b`」時，`b` 的優先權 **比較高**（在頂端）。

```cpp
auto cmp = [](const pair<int, string>& a, const pair<int, string>& b) { return a.first > b.first; };
priority_queue<pair<int, string>, vector<pair<int, string>>, decltype(cmp)> tasks(cmp);
tasks.push({3, "c"}); tasks.push({1, "a"}); tasks.push({2, "b"});
cout << tasks.top().second << '\n';              // 用 > 比較 → 最小的在頂端 → 輸出：a
```

## 5.3 自訂雜湊 (Custom Hash)

**是什麼**：`unordered_map` / `unordered_set` 的 key 是自訂型別時，要提供：
1. **雜湊函式**：把 key 變成一個 `size_t`。
2. **相等比較**：`operator==`（雜湊值相同時用來確認是不是真的同一個 key）。

```cpp
struct Pt {
    int x, y;
    bool operator==(const Pt& o) const { return x == o.x && y == o.y; }
};
struct PtHash {
    size_t operator()(const Pt& p) const {
        // 把兩個 32 位元整數合成一個 64 位元整數再雜湊。
        // 先轉成無號數再移位（對負數左移在 C++20 前是未定義行為）
        return hash<unsigned long long>()(((unsigned long long)(unsigned)p.x << 32) | (unsigned)p.y);
    }
};

unordered_map<Pt, string, PtHash> grid;
grid[{0, 0}] = "origin";
grid[{-1, 2}] = "A";
cout << grid[{-1, 2}] << ' ' << grid.count({5, 5}) << '\n';   // 輸出：A 0
// unordered_map<Pt, string> bad;                 // ❌ 沒有給雜湊函式：error: use of deleted function 'std::unordered_map<...>::unordered_map() [with _Key = Pt; ... _Hash = std::hash<Pt>; ...]'
//                                                //    （標準函式庫沒有 std::hash<Pt>，所以連建構子都不能用）
```

**`pair` 和 `tuple` 也沒有內建的雜湊**：

```cpp
// unordered_set<pair<int, int>> s;               // ❌ 同樣的錯誤
set<pair<int, int>> s;                           // ✅ 最簡單的替代：用有序的 set（pair 有內建的 <）
s.insert({1, 2});
cout << s.count({1, 2}) << '\n';                 // 輸出：1
```

**好的雜湊函式**：不同的 key 盡量得到不同的值。`(x + y)` 這種寫法很差：`(1, 2)` 和 `(2, 1)` 會撞在一起；碰撞太多時，`unordered_map` 會退化成 `O(n)`。

---

# 第六部分：經典陷阱

## 6.1 remove 不會真的刪除：erase-remove 慣用法

**是什麼**：演算法只看得到迭代器，**沒辦法改變容器的大小**。`remove` 只是把「要保留的元素」**往前搬**，回傳新的邏輯結尾；後面剩下的元素還在，`size()` 沒變。

```cpp
vector<int> v = {1, 2, 3, 2, 4};
auto new_end = remove(v.begin(), v.end(), 2);
cout << v.size() << ' ' << (new_end - v.begin()) << '\n';   // 輸出：5 3
// v 的前 3 個是 {1, 3, 4}，後面 2 個的值「未指定」
v.erase(new_end, v.end());                    // 真的刪掉
show(v);                                      // 輸出：1 3 4
```

```
remove 之前： [1][2][3][2][4]
remove 之後： [1][3][4][?][?]
                       ↑ new_end
erase 之後：  [1][3][4]
```

**合起來寫：erase-remove 慣用法**

```cpp
vector<int> w = {5, -1, 3, -2, 0};
w.erase(remove_if(w.begin(), w.end(), [](int x) { return x < 0; }), w.end());
show(w);                                      // 輸出：5 3 0
```

**C++20 的簡化**：`erase(v, 2);`、`erase_if(v, pred);` 一步完成。

**比喻**：`remove` 像是把要留的書往書架左邊推，右邊剩下的位置還沒清空；`erase` 才是真的把右邊的東西拿走。

## 6.2 accumulate 的初值決定了型別

`accumulate` 的計算型別 **由初值決定**，不是由元素決定。

```cpp
vector<int> v(100000, 100000);                 // 總和是 10^10，超過 int
cout << accumulate(v.begin(), v.end(), 0LL) << '\n';    // ✅ 用 long long 計算 → 輸出：10000000000
// accumulate(v.begin(), v.end(), 0)           // ❌ 初值 0 是 int → 用 int 加總 → 溢位（未定義行為）

vector<double> d = {0.5, 0.5};
cout << accumulate(d.begin(), d.end(), 0) << ' '        // ❌ 初值是 int：每次加完都被截成 int
     << accumulate(d.begin(), d.end(), 0.0) << '\n';    // ✅
// 輸出：0 1
```

`0 + 0.5 = 0.5` 被截成 `0`，`0 + 0.5` 又是 `0`。

## 6.3 unique 只移除「相鄰」的重複

```cpp
vector<int> v = {3, 1, 3, 1};
v.erase(unique(v.begin(), v.end()), v.end());   // 沒有相鄰的重複 → 什麼都沒刪
show(v);                                        // 輸出：3 1 3 1
sort(v.begin(), v.end());                       // 先排序，讓相同的值相鄰：1 1 3 3
v.erase(unique(v.begin(), v.end()), v.end());
show(v);                                        // 輸出：1 3
```

**「排序 + unique + erase」是去重複的標準寫法**，常用於座標壓縮。

## 6.4 比較函式必須是「嚴格弱序」

`sort`、`set`、`map` 的比較函式必須像 `<` 一樣：`comp(a, a)` 一定是 `false`。

```cpp
vector<int> v(100, 5);
// sort(v.begin(), v.end(), [](int a, int b) { return a <= b; });   // ❌ 用 <=：comp(a, a) 是 true
//    → 違反嚴格弱序，sort 可能讀到陣列外面、當掉（第 04 課）
sort(v.begin(), v.end(), [](int a, int b) { return a < b; });       // ✅
```

## 6.5 size() 是無號數

```cpp
vector<int> v;
// for (int i = 0; i < v.size() - 1; i++)       // ❌ v 是空的：0 - 1 繞回成 18446744073709551615
cout << v.size() - 1 << '\n';                   // 輸出：18446744073709551615
for (int i = 0; i + 1 < (int)v.size(); i++) { } // ✅ 改寫成不會減到負數的形式
```

## 6.6 其他常見陷阱總整理

| 陷阱 | 說明 | 章節 |
|---|---|---|
| `priority_queue` 預設是 **最大** 堆積 | 要最小堆積用 `greater<>` | 2.10 |
| `m[k]` 會插入 | 只查詢用 `find` / `count` / `contains`（C++20） | 2.7 |
| `multiset::erase(x)` 刪除全部 | 只刪一個要用 `erase(find(x))` | 2.6 |
| `reserve` 不會建立元素 | 之後要用 `push_back`，不能直接 `v[i]` | 2.2 |
| 對空容器 `top()` / `front()` / `back()` | 未定義行為 | 2.10 |
| `std::sort` 用在 `list` 上 | 編譯錯誤，要用 `l.sort()` | 3.3 |
| `std::lower_bound` 用在 `set` 上 | 能編譯但變成 `O(n)`，要用 `s.lower_bound` | 4.3 |
| 沒排序就二分搜 | 結果錯誤，不會報錯 | 4.3 |
| `copy` 到空的容器 | 未定義行為，要用 `back_inserter` | 3.6 |
| 走訪時修改容器 | 迭代器失效 | 3.7 |
| `set` 的比較只看部分欄位 | 那些欄位相同的元素被當成重複 | 5.2 |
| `tolower(c)` 的 `c` 是負的 `char` | 未定義行為，先轉 `unsigned char` | 第 12 課 |
| `vector<bool>` | 是特化版本，`auto& b = v[0]` 不能編譯 | 第 10 課 |
| `unordered_map` 的走訪順序 | 不確定，需要有序就排序或改用 `map` | 2.9 |

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 標準模板函式庫 | STL | C++ 內建的容器與演算法 | 1.1 |
| 序列容器 | Sequence Container | 依插入順序存放 | 2.1 |
| 關聯容器 | Associative Container | 依 key 組織（有序或雜湊） | 2.1 |
| 容量 | Capacity | vector 不重新配置能放幾個 | 2.2 |
| 容器配接器 | Container Adapter | 包裝其他容器、只開放部分操作 | 2.10 |
| 就地建構 | Emplace | 直接在容器裡建構物件 | 2.12 |
| 迭代器 | Iterator | 指向元素的游標 | 3.1 |
| 半開區間 | Half-open Range `[b, e)` | 包含開頭、不包含結尾 | 3.2 |
| 迭代器分類 | Iterator Category | 輸入 / 輸出 / 前向 / 雙向 / 隨機存取 | 3.3 |
| 插入迭代器 | Insert Iterator | 寫入時呼叫 push_back / insert | 3.6 |
| 迭代器失效 | Iterator Invalidation | 容器修改後迭代器不能再用 | 3.7 |
| 條件函式 | Predicate | 回傳 bool 的函式，`_if` 演算法使用 | 4 |
| 穩定排序 | Stable Sort | 相等元素保持原本順序 | 4.2 |
| 二分搜尋 | Binary Search | 在已排序範圍中每次砍一半 | 4.3 |
| 前綴和 | Prefix Sum | 前 i 個元素的總和 | 4.5 |
| 函式物件 | Function Object / Functor | 有 `operator()` 的物件 | 5.1 |
| 雜湊函式 | Hash Function | 把 key 變成整數 | 5.3 |
| erase-remove 慣用法 | Erase-remove Idiom | 先 remove 搬動、再 erase 刪除 | 6.1 |
| 嚴格弱序 | Strict Weak Ordering | 比較函式必須像 `<` 一樣 | 6.4 |

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

### 題 8：預測輸出

```cpp
map<string, int> m;
m["a"];
m["b"] = 2;
m.insert({"b", 5});
m.emplace("c", 3);
cout << m.size() << ' ' << m["a"] << m["b"] << m["c"] << ' ' << m.count("d") << ' ' << m.size();
```

### 題 9：預測輸出

```cpp
multiset<int> ms = {4, 1, 4, 2, 4};
ms.erase(ms.find(4));
cout << ms.count(4) << ' ';
ms.erase(4);
for (int x : ms) cout << x;
```

### 題 10：預測輸出

```cpp
vector<int> v = {3, 7, 1, 8};
vector<int> out;
transform(v.begin(), v.end(), back_inserter(out), [](int x) { return x * 10; });
partial_sum(out.begin(), out.end(), out.begin());
cout << out.back() << ' ' << *max_element(v.begin(), v.end()) - *min_element(v.begin(), v.end());
```

### 題 11：用 `priority_queue` 找出 `vector<int> v` 中最大的 k 個數（由大到小輸出），只用 `O(k)` 的額外空間。

---

# 習題解答

**題 1**：排序後 `{1, 1, 2, 4, 5, 5, 6, 9}`。`lower_bound(5)` = 4，`upper_bound(5)` = 6，`count(1)` = 2。輸出 `4 6 2`。

**題 2**：`5`。`remove` 不改變容器大小，只是把 `{1, 3, 5}` 搬到前面（後面兩個位置的值未指定）。要接著 `erase`。

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

**題 6**：`std::sort` 需要 **隨機存取迭代器**（要計算 `last - first`），`list` 只有雙向迭代器。改用成員函式 `l.sort();`。

**題 7**：

```cpp
sort(words.begin(), words.end());
words.erase(unique(words.begin(), words.end()), words.end());
stable_sort(words.begin(), words.end(), [](const string& a, const string& b) { return a.size() < b.size(); });
```

先依字典序排序並去重；再用 **穩定排序** 依長度排，長度相同的保持字典序。

**題 8**：`3 023 0 3`。
- `m["a"];` 插入 `{"a", 0}`。
- `m["b"] = 2;` 插入。
- `m.insert({"b", 5})`：`b` 已存在，**不覆蓋**，還是 2。
- `m.emplace("c", 3)` 插入。此時 size 是 3。
- `m.count("d")` 不會插入 → 0；最後 size 還是 3。

**題 9**：`2 12`。`erase(find(4))` 只刪一個 4，剩兩個；`erase(4)` 刪除所有 4，剩下 `{1, 2}`。

**題 10**：`190 7`。`out` = `{30, 70, 10, 80}`，前綴和 `{30, 100, 110, 190}`，最後一個是 190；最大值 8 減最小值 1 是 7。

**題 11**：用 **最小堆積** 保留目前最大的 k 個：堆積超過 k 個時，把最小的丟掉。

```cpp
vector<int> top_k(const vector<int>& v, int k) {
    priority_queue<int, vector<int>, greater<int>> pq;   // 最小堆積
    for (int x : v) {
        pq.push(x);
        if ((int)pq.size() > k) pq.pop();                // 丟掉目前最小的
    }
    vector<int> res;
    while (!pq.empty()) { res.push_back(pq.top()); pq.pop(); }
    reverse(res.begin(), res.end());                     // 堆積吐出來是由小到大，反轉成由大到小
    return res;
}
show(top_k({5, 1, 9, 3, 7, 2}, 3));                      // 輸出：9 7 5
```

時間 `O(n log k)`，額外空間 `O(k)`。

---

# 程式練習

- **`C11 單字頻率統計`**：`unordered_map` 計數、`vector<pair>` + `sort` + lambda 排序、`isalpha` / `tolower` 的正確用法、讀到 EOF。
