# C05. 用指標做矩陣 (Dynamic 2D Array with Pointers)

> 主題：指標、動態配置、二維陣列　難度：★★☆　時間限制：1 秒　相關教學：`cpp/lessons/05_pointers_references.md`

## 題目

請 **不要使用 `vector`**，用 `long long**`（指標的指標）和 `new` / `delete` 實作一個矩陣類別 `Matrix`，
讀入兩個矩陣 `A`（`r1 × c1`）和 `B`（`r2 × c2`），依序輸出：

1. `A + B`：大小不同時輸出 `A+B: size mismatch`
2. `A × B`（矩陣乘法）：`c1 ≠ r2` 時輸出 `A*B: size mismatch`
3. `A` 的轉置 `Aᵀ`（`c1 × r1`）

每個結果先輸出一行標題（`A+B:`、`A*B:`、`T(A):`），接著每一列一行，數字用空白分隔。

**矩陣乘法**：`(A × B)[i][j] = Σ A[i][k] × B[k][j]`（`k` 從 0 到 `c1 - 1`）。

## 輸入

```
r1 c1
A 的 r1 列，每列 c1 個整數
r2 c2
B 的 r2 列，每列 c2 個整數
```

## 輸出

如上所述。

## 限制

- `1 ≤ r1, c1, r2, c2 ≤ 200`
- 矩陣元素 `|x| ≤ 10^4`（乘法結果最多 `200 × 10^8`，需要 `long long`）

## 範例

輸入
```
2 3
1 2 3
4 5 6
3 2
1 0
0 1
1 1
```
輸出
```
A+B: size mismatch
A*B:
4 5
10 11
T(A):
1 4
2 5
3 6
```

## 提示

```cpp
long long** a = new long long*[rows];      // 先配置「每一列的指標」
for (int i = 0; i < rows; i++)
    a[i] = new long long[cols]();          // 再配置每一列；() 代表全部初始化成 0
// 釋放時順序相反
for (int i = 0; i < rows; i++) delete[] a[i];
delete[] a;
```

- 讓 `Matrix` 的 **解構子** 負責釋放記憶體，就不會忘記（RAII，第 06 課）。
- 如果你的 `Matrix` 會被 **複製**（例如函式回傳 `Matrix`），要注意第 06 課的「三法則 / 五法則」，
  否則兩個物件會共用同一塊記憶體，解構時 `delete` 兩次 → 當掉。用 `--debug` 模式可以抓到這類錯誤。
- 1 × 1 的矩陣、只有一列、只有一行都是很好的 corner case。
