# 04. 鏈結串列 (Linked List)

> 練習題：`04_linked_list`、`11_lru_cache`

## 1. 結構

每個節點存「值」和「指向下一個節點的指標」，節點在記憶體中 **不必連續**。

```
head                                   tail
 │                                      │
 ▼                                      ▼
+---+---+    +---+---+    +---+---+    +---+------+
| 3 | ●─┼──▶ | 8 | ●─┼──▶ | 1 | ●─┼──▶ | 6 | null |
+---+---+    +---+---+    +---+---+    +---+------+
```

```cpp
struct Node {
    int val;
    Node* next;
    Node(int v) : val(v), next(nullptr) {}
};
```

| 操作 | 陣列 | 單向串列 |
|---|---|---|
| 存取第 `i` 個 | `O(1)` | `O(i)` |
| 頭部插入 / 刪除 | `O(n)` | `O(1)` |
| 尾部插入（有 tail） | 攤銷 `O(1)` | `O(1)` |
| 尾部刪除 | `O(1)` | `O(n)`（要找倒數第二個）|
| 已知節點後插入 / 刪除 | `O(n)` | `O(1)` |

## 2. 基本操作

### 頭部插入

```cpp
void push_front(int x) {
    Node* nd = new Node(x);
    nd->next = head;
    head = nd;
    if (!tail) tail = nd;   // 原本是空的 → 新節點也是 tail
}
```

### 在第 i 個位置插入

先走到第 `i-1` 個節點（`prev`），然後：

```
before:  prev ──▶ A
after:   prev ──▶ nd ──▶ A
```

```cpp
nd->next = prev->next;  // 順序很重要！先接後面
prev->next = nd;        // 再改前面
```

### 刪除第 i 個

```cpp
Node* t = prev->next;
prev->next = t->next;
if (t == tail) tail = prev;   // ← 最常忘記的一行
delete t;
```

## 3. 反轉串列（面試超常考）

用三個指標 `prev / cur / nx`，一個一個把箭頭反過來：

```
null ◀── 3    8 ──▶ 1 ──▶ null
         ▲    ▲
       prev  cur
```

```cpp
Node *prev = nullptr, *cur = head;
tail = head;                 // 反轉後原本的 head 變成 tail
while (cur) {
    Node* nx = cur->next;    // 1. 先記住下一個
    cur->next = prev;        // 2. 反轉箭頭
    prev = cur;              // 3. 往前走
    cur = nx;
}
head = prev;
```

## 4. 技巧：dummy head（哨兵節點）

在最前面放一個不存資料的假節點，`head` 永遠不會是 `nullptr`，
「插在最前面」和「插在中間」就變成同一種情況，少寫很多 `if`。

```cpp
Node dummy(0);
dummy.next = head;
Node* prev = &dummy;
for (int k = 0; k < i; k++) prev = prev->next;
// 在 prev 後面插入 / 刪除
head = dummy.next;
```

## 5. 雙向串列 (Doubly Linked List)

每個節點多一個 `prev` 指標，可以 `O(1)` 刪除 **任何已知節點**、`O(1)` 刪尾巴。
C++ 的 `std::list` 就是雙向串列。

```
null ◀──┐   ┌──▶ ◀──┐   ┌──▶ null
      [ A ]          [ B ]
```

### 應用：LRU Cache

LRU（Least Recently Used）快取需要：
- 用 key 快速找到資料 → **雜湊表**
- 快速把某筆資料移到「最新」、快速刪掉「最舊」→ **雙向串列**

兩個合在一起：`unordered_map<key, list::iterator>`。
`std::list::splice` 可以 `O(1)` 把一個節點搬到串列最前面，而且 iterator 不會失效。

```cpp
list<pair<int,int>> items;                         // 前面 = 最近使用
unordered_map<int, list<pair<int,int>>::iterator> pos;

// 把 key 的節點移到最前面
items.splice(items.begin(), items, pos[key]);
```

## 6. Corner case checklist

- 空串列的 `pop_front` / `pop_back` / `reverse` / `print`。
- 只有一個節點時刪除它：`head` 和 `tail` 都要變 `nullptr`。
- 刪掉最後一個節點：`tail` 要往前移。
- `reverse` 後 `tail` 有沒有更新？
- `insert(size, x)` 是合法的（等於 push_back）。
- 刪除節點後還使用它（use-after-free）→ 用 `--debug` 會被抓到。
- 解構子要釋放所有節點，避免 memory leak。
