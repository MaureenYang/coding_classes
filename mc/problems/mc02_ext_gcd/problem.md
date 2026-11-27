# MC02. 擴展歐幾里得與模反元素 (Extended Euclidean Algorithm)

> 主題：擴展歐幾里得演算法、模反元素、線性同餘方程　難度：★★　時間限制：1 秒　相關教學：`mc/lessons/02-divisibility-gcd.md`、`mc/lessons/03-modular-arithmetic.md`

## 題目

處理 q 個指令：

| 指令 | 輸出 |
|---|---|
| `GCD a b` | `gcd(a, b)` |
| `INV a m` | a 模 m 的反元素（`0 ≤ x < m` 且 `a·x ≡ 1 (mod m)`）；不存在時輸出 `none` |
| `LIN a b m` | 解 `a·x ≡ b (mod m)`：無解輸出 `none`；有解輸出兩個數 `g x₀`，g 是模 m 下 **解的個數**，x₀ 是 **最小的非負解** |

**提示**：令 `g = gcd(a, m)`。`a·x ≡ b (mod m)` 有解 ⇔ `g | b`；有解時，模 m 恰好有 g 個解，它們模 `m/g` 都相同：`x₀ ≡ (b/g) · (a/g)⁻¹ (mod m/g)`。

## 輸入

第一行是 q，接下來 q 行，每行一個指令。

## 限制

- `1 ≤ q ≤ 10⁵`
- `GCD`：`0 ≤ a, b ≤ 10¹⁸`，不會兩個都是 0
- `INV`、`LIN`：`1 ≤ m ≤ 10¹⁸`，`0 ≤ a, b < m`
- `m = 1` 時每個整數都 ≡ 0 ≡ 1，所以反元素是 0

## 範例

輸入
```
6
GCD 2024 748
INV 3 7
INV 6 9
LIN 6 3 9
LIN 6 4 9
INV 5 1
```
輸出
```
44
5
none
3 2
none
0
```

`6x ≡ 3 (mod 9)`：g = 3 整除 3，三個解是 2、5、8，最小的是 2。

## 提示

- 擴展歐幾里得用迴圈寫：同時維護 `(r, u, v)` 兩組，每次 `q = r₀ / r₁`，三個數都做 `新 = 舊₀ − q·舊₁`。係數不會超過 m，`long long` 放得下。
- 但 `(b/g) · u` 可能到 10³⁶：先轉成 `__int128` 再取模。
- u 可能是負的：`((u % mm) + mm) % mm`。
