# 08. 二元搜尋樹 (Binary Search Tree)

> 練習題：`13_bst`

## 1. 樹的名詞

```
            8          ← 根 (root)，深度 0
          /   \
         3     10      ← 3 是 1、6 的父親 (parent)
        / \      \
       1   6      14
          / \     /
         4   7   13    ← 沒有小孩的叫葉節點 (leaf)
```

- **高度 (height)**：根到最深葉子的節點數（本平台定義：空樹 0、只有根 1）。上圖高度 4。
- **子樹 (subtree)**：某個節點和它所有後代。

## 2. BST 性質

對每個節點 `x`：**左子樹所有值 < x < 右子樹所有值**。

所以 **中序走訪（左 → 自己 → 右）會得到排序好的結果**：上圖是 `1 3 4 6 7 8 10 13 14`。

## 3. 三種走訪

```cpp
void preorder(Node* t)  { if (!t) return; visit(t); preorder(t->left); preorder(t->right); }  // 根左右
void inorder(Node* t)   { if (!t) return; inorder(t->left); visit(t); inorder(t->right); }    // 左根右
void postorder(Node* t) { if (!t) return; postorder(t->left); postorder(t->right); visit(t); } // 左右根
```

上圖：
- 前序：`8 3 1 6 4 7 10 14 13`（可以用來 **重建** 同一棵 BST）
- 中序：`1 3 4 6 7 8 10 13 14`
- 後序：`1 4 7 6 3 13 14 10 8`（釋放記憶體時用：先刪小孩再刪自己）

## 4. 搜尋與插入

從根開始，比較大小決定往左還是往右，每一步往下一層 → `O(h)`。

```cpp
void insert(Node*& t, int x) {     // Node*& ：可以直接改到父親的 left/right 指標
    if (!t) { t = new Node(x); return; }
    if (x < t->key) insert(t->left, x);
    else if (x > t->key) insert(t->right, x);
    // 相等：已存在，忽略
}
```

> 如果參數是 `Node* t`（沒有 `&`），`t = new Node(x)` 只會改到區域變數，樹完全不會變！

## 5. 刪除（三種情況）

```cpp
bool erase(Node*& t, int x) {
    if (!t) return false;                         // 找不到
    if (x < t->key) return erase(t->left, x);
    if (x > t->key) return erase(t->right, x);
    // 找到了
    if (t->left && t->right) {                    // 情況 3：兩個小孩
        Node* s = t->right;
        while (s->left) s = s->left;              // 右子樹最小 = 中序後繼
        t->key = s->key;                          // 拿後繼的值取代自己
        return erase(t->right, s->key);           // 再去右子樹刪掉後繼（它最多只有右小孩）
    }
    Node* child = t->left ? t->left : t->right;   // 情況 1、2：0 或 1 個小孩
    delete t;
    t = child;                                    // 父親直接指向小孩（可能是 nullptr）
    return true;
}
```

範例：刪除上圖的 `3`（兩個小孩）→ 右子樹最小是 `4` → `3` 換成 `4`，再刪掉原本的 `4`：

```
            8                      8
          /   \                  /   \
         3     10      →        4     10
        / \      \             / \      \
       1   6      14          1   6      14
          / \     /                \     /
         4   7   13                 7   13
```

## 6. BST 的弱點：退化

依序插入 `1, 2, 3, 4, 5`：

```
1
 \
  2
   \
    3
     \
      4
       \
        5
```

變成一條串列，高度 `n`，所有操作 `O(n)`！而且遞迴深度也是 `n`，`n` 很大時會 stack overflow。

**平衡樹**（AVL、紅黑樹、Treap、Splay）會在插入 / 刪除時透過「旋轉」保持高度 `O(log n)`。
`std::set` / `std::map` 就是紅黑樹，保證 `O(log n)`。

```cpp
set<int> s;
s.insert(5); s.erase(5); s.count(5);
auto it = s.lower_bound(x);   // 第一個 >= x 的元素
auto it2 = s.upper_bound(x);  // 第一個 > x 的元素
for (int v : s) ...           // 依序（中序）走訪
```

## 7. Corner case checklist

- 空樹的所有操作（走訪輸出 `empty`、高度 0）。
- 插入重複的值。
- 刪除 **根**（尤其是只剩一個節點時）。
- 刪除的節點是兩個小孩，而且中序後繼 **有右小孩**。
- 刪除不存在的值、同一個值刪兩次。
- 遞增 / 遞減插入造成的退化樹。
