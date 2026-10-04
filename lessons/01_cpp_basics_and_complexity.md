# 01. C++ 基礎與時間複雜度

## 1. 為什麼要學資料結構？

資料結構 = **資料怎麼存** + **能做哪些操作、多快**。
同一個問題，選對資料結構可以讓程式從「跑一小時」變成「跑 0.1 秒」。

| 需求 | 好的選擇 | 操作複雜度 |
|---|---|---|
| 用索引快速存取 | 陣列 / `vector` | `O(1)` |
| 在頭尾快速加入刪除 | `deque`、鏈結串列 | `O(1)` |
| 後進先出（復原、括號、遞迴） | stack | `O(1)` |
| 先進先出（排隊、BFS） | queue | `O(1)` |
| 用 key 快速查詢 | 雜湊表 `unordered_map` | 平均 `O(1)` |
| 隨時拿出最小 / 最大值 | heap `priority_queue` | `O(log n)` |
| 有序、還要能查前後、範圍 | 平衡 BST `set` / `map` | `O(log n)` |
| 動態合併集合、判斷連通 | 併查集 | 近似 `O(1)` |

## 2. 時間複雜度 Big-O

Big-O 描述「輸入變大時，執行時間怎麼成長」，忽略常數。

```cpp
// O(1)
int x = a[5];

// O(n)
for (int i = 0; i < n; i++) sum += a[i];

// O(n^2)
for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++) ...

// O(log n)：每次範圍減半
while (lo < hi) { int mid = (lo + hi) / 2; ... }

// O(2^n)：河內塔、列舉所有子集合
```

### 估算能不能過：每秒大約 `10^8` 個簡單運算

| n 的範圍 | 可以接受的複雜度 |
|---|---|
| `n ≤ 12` | `O(n!)` |
| `n ≤ 25` | `O(2^n)` |
| `n ≤ 500` | `O(n^3)` |
| `n ≤ 5000` | `O(n^2)` |
| `n ≤ 10^6` | `O(n log n)` 或 `O(n)` |
| `n ≤ 10^18` | `O(log n)` 或 `O(1)` |

**讀題目時先看限制**：`n ≤ 3×10^5` 就是在告訴你「`O(n^2)` 會 TLE」。

### 攤銷分析 (amortized)

有些操作「偶爾很慢，平均很快」。例如 `vector::push_back` 容量滿了要搬全部資料（`O(n)`），
但因為容量每次加倍，`n` 次 push 的總成本是 `O(n)`，**平均每次 `O(1)`**。詳見 `03_dynamic_array.md`。

## 3. 競程 / 解題的 C++ 樣板

```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);  // 讓 cin/cout 變快
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> a(n);
    for (auto& x : a) cin >> x;

    // ...

    cout << answer << '\n';       // 用 '\n'，不要用 endl（endl 每次都會 flush，很慢）
    return 0;
}
```

### 常見陷阱

1. **整數溢位**：`int` 最大約 `2.1×10^9`。兩個 `10^9` 相加、或 `1 << 40`，都會溢位。
   用 `long long`，寫 `1LL << 40`。
2. **`size()` 是無號數**：`v.size() - 1` 在 `v` 為空時會變成超大的數字。
   ```cpp
   for (int i = 0; i < v.size() - 1; i++)  // v 是空的 → 災難
   for (int i = 0; i + 1 < (int)v.size(); i++)  // 安全
   ```
3. **負數取餘數**：C++ 中 `-7 % 3 == -1`，不是 `2`。要非負：`((x % m) + m) % m`。
4. **未定義行為 (UB)**：越界存取、對空的 `stack` 呼叫 `top()`，程式可能「看起來正常」，
   換一筆測資就當掉。用 `--debug` 模式（sanitizer）可以抓出來。
5. **遞迴太深**：預設 stack 通常只有 8MB，遞迴深度 `10^5 ~ 10^6` 層就可能 stack overflow (RE)。

## 4. 指標與動態記憶體（實作資料結構的基本功）

```cpp
struct Node {
    int val;
    Node* next;
};

Node* p = new Node{5, nullptr};  // 在 heap 上配置
p->val = 7;                      // 等同 (*p).val = 7
delete p;                        // 用完要釋放
p = nullptr;                     // 好習慣：避免 dangling pointer

int* arr = new int[n];           // 配置陣列
delete[] arr;                    // 陣列要用 delete[]
```

**參考 (reference)** 可以讓函式修改呼叫者的變數，在樹的遞迴裡非常好用：

```cpp
void insert(Node*& t, int x) {   // t 是「指標的參考」
    if (!t) { t = new Node{x, nullptr}; return; }  // 直接改到父親的指標
    ...
}
```

## 5. STL 速查

| 容器 | 用途 | 主要操作 |
|---|---|---|
| `vector<T>` | 動態陣列 | `push_back`, `pop_back`, `[i]`, `size` |
| `deque<T>` | 雙端佇列 | `push_front/back`, `pop_front/back` |
| `list<T>` | 雙向串列 | `insert`, `erase`, `splice`（`O(1)`） |
| `stack<T>` | 堆疊 | `push`, `pop`, `top` |
| `queue<T>` | 佇列 | `push`, `pop`, `front` |
| `priority_queue<T>` | 最大堆積 | `push`, `pop`, `top` |
| `set<T>` / `map<K,V>` | 平衡 BST，有序 | `insert`, `erase`, `find`, `lower_bound` |
| `unordered_map<K,V>` | 雜湊表 | `[]`, `find`, `erase`, `count` |

這個平台的很多題目會要求你 **不要用 STL 的對應容器**，自己實作一次 —— 這是理解原理最好的方法。
寫過一次之後，平常解題就放心用 STL。
