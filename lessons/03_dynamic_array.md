# 03. 動態陣列 (Dynamic Array / vector)

> 練習題：`03_my_vector`

## 1. 陣列的特性

陣列在記憶體中是 **連續** 的一塊：

```
索引:    0    1    2    3    4
       +----+----+----+----+----+
data → | 12 |  7 | 33 | -4 |  9 |
       +----+----+----+----+----+
位址:  1000 1004 1008 1012 1016     (int 佔 4 bytes)
```

`a[i]` 的位址 = `起點 + i × 元素大小` → **`O(1)` 隨機存取**。
缺點：大小固定；在中間插入 / 刪除要搬移後面的元素（`O(n)`）。

## 2. 動態陣列：不夠就換一塊更大的

`std::vector` 內部有三個東西：

- `data`：指向一塊用 `new[]` 配置的記憶體
- `size`：目前放了幾個元素
- `capacity`：這塊記憶體最多可以放幾個

```
size = 3, capacity = 4
+----+----+----+----+
|  5 |  7 |  9 |  ? |
+----+----+----+----+
```

`push_back(x)` 時：

1. 如果 `size < capacity`：直接放進 `data[size]`，`size++`。
2. 如果滿了：配置一塊 **兩倍大** 的新記憶體，把舊資料複製過去，釋放舊記憶體，再放入。

```cpp
void push_back(int x) {
    if (size_ == cap_) {
        int ncap = max(1, cap_ * 2);
        int* nd = new int[ncap];
        for (int i = 0; i < size_; i++) nd[i] = data_[i];
        delete[] data_;
        data_ = nd;
        cap_ = ncap;
    }
    data_[size_++] = x;
}
```

## 3. 為什麼要「加倍」？攤銷分析

假設 push `n` 個元素：

- **每次 +1**：第 `k` 次要搬 `k-1` 個 → 總共 `1+2+...+n = O(n^2)`。太慢！
- **每次 ×2**：搬移發生在容量是 `1, 2, 4, 8, ..., n` 時 → 總共 `1+2+4+...+n < 2n = O(n)`。

所以 `n` 次 push 總成本 `O(n)`，**平均每次 `O(1)`**，這就叫 **攤銷 (amortized) `O(1)`**。

> 小知識：GCC 的 `vector` 用 2 倍，MSVC 用 1.5 倍。只要是乘以一個 > 1 的常數，攤銷就是 `O(1)`。

## 4. pop_back 要不要縮小？

`pop_back` 只要 `size--` 就好。如果每次 `size < capacity / 2` 就縮小一半，
在剛好邊界上反覆 push / pop 會造成每次都搬移（thrashing）。
常見的做法是 `size < capacity / 4` 才縮小，或乾脆不縮（`std::vector` 就不會自動縮）。

## 5. 記憶體管理三大規則 (Rule of Three)

如果你的 class 自己管理記憶體（有 `new`），通常要寫：

1. **解構子**：`~MyVector() { delete[] data_; }`
2. **複製建構子**：深複製，否則兩個物件會指向同一塊記憶體，解構時 double free。
3. **複製指定運算子** `operator=`

練習題只用到一個物件，寫解構子就夠了；但寫正式程式時要注意。

## 6. 邊界條件 checklist

- 空陣列 `pop` / `get`。
- 索引是 **負數**：如果你用 `size_t`（無號數）接，`-1` 會變成 `18446744073709551615`；
  用 `int` 接要檢查 `i < 0`。
- `capacity` 從 `0` 開始，第一次 push 要變成 `1`（`0 × 2 = 0`！）。
- 搬移後要 `delete[]` 舊記憶體（不然會 memory leak），而且不能再使用舊指標。

## 7. vector 常用技巧

```cpp
vector<int> v(n, 0);          // n 個 0
v.reserve(1000000);           // 預先配置，避免多次搬移
v.emplace_back(x);            // 直接在尾端建構
v.back();                     // 最後一個元素
v.insert(v.begin() + i, x);   // O(n)
v.erase(v.begin() + i);       // O(n)
sort(v.begin(), v.end());
vector<vector<int>> g(n);     // 二維：圖的鄰接串列
```

> ⚠️ `push_back` 造成重新配置之後，**所有指向舊元素的指標、參考、iterator 都會失效**。
