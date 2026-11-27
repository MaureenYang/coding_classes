# 21. 同餘密碼與背包密碼（Congruential and Knapsack Cryptosystems）

> 對應課本：§6.1、§6.2
>
> 先備知識：第 03 課（模反元素）、第 17 課（NP 完全）。
>
> 這一課是格密碼的「序章」：兩個看起來和「格」毫無關係的密碼系統，最後都被 **在格裡找短向量** 給破解了。

**這一課分成三個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 同餘密碼 | 用「小的數」當私鑰的玩具系統、為什麼解密會成功、它和二維格的關係 |
| 第二部分 | 子集合和問題與超遞增序列 | 子集合和問題、碰撞演算法 O(2^(n/2))、超遞增序列為什麼好解 |
| 第三部分 | Merkle–Hellman 背包密碼 | 用模乘法偽裝超遞增序列、加密解密、它怎麼被格攻擊 |

---

# 第一部分：同餘密碼

## 1.1 系統

這是一個 **玩具** 系統，但它是第 23 課 NTRU 的一維版本。

| | 做什麼 |
|---|---|
| **Alice 建金鑰** | 公開大模數 q；選秘密的 **小** 整數 f、g：`f < √(q/2)`，`√(q/4) < g < √(q/2)`，`gcd(f, q) = 1`；公鑰 `h ≡ f⁻¹ g (mod q)` |
| **Bob 加密** | 明文 `m < √(q/4)`，隨機 `r < √(q/2)`，送 `e ≡ r h + m (mod q)` |
| **Alice 解密** | `a ≡ f e (mod q)`（取 0 ≤ a < q），再算 `b ≡ f⁻¹ a (mod g)`，b 就是 m |

**為什麼解得開**：`a ≡ f(rh + m) = r g + f m (mod q)`。因為 f、g、r、m 都很小，

```
r g + f m < √(q/2)·√(q/2) + √(q/2)·√(q/4) < q
```

所以 a **就等於** 整數 `rg + fm`，不只是同餘！再 mod g 就消掉 rg：`f⁻¹ a ≡ m (mod g)`，而 m < g，所以 b = m。

**關鍵想法**：私鑰是「小」的數，運算後結果仍然「小」，取模 **沒有繞圈**，所以等式在整數上成立。這個「小 → 模 q 的運算沒有繞圈」的技巧是格密碼（NTRU、GGH）的核心。

課本例 6.1：

```python
q, f, g = 122430513841, 231231, 195698
h = pow(f, -1, q) * g % q
print("公鑰 h =", h)

m, r = 123456, 101010
e = (r * h + m) % q
print("密文 e =", e)

a = f * e % q
b = pow(f, -1, g) * a % g
print(a, a == r * g + f * m, b)
```
```output
公鑰 h = 39245579300
密文 e = 18357558717
48314309316 True 123456
```
## 1.2 Eve 的攻擊：找一個二維格裡的短向量

Eve 想找 **任何** 一對小的 (F, G) 滿足 `F h ≡ G (mod q)`——這樣的 (F, G) 通常也能當解密金鑰。改寫成 `F h = G + qR`：

```
F · (1, h) − R · (0, q) = (F, G)
```

左邊是兩個已知向量 `v₁ = (1, h)`、`v₂ = (0, q)` 的 **整數** 線性組合，右邊是一個 **很短** 的向量。所有整數組合的集合 `L = {a₁v₁ + a₂v₂ : a₁, a₂ ∈ Z}` 叫做 **格**（lattice）。Eve 要做的就是 **在格 L 中找一個短向量**。

而二維格的最短向量，高斯在 1801 年就會找了（第 24 課的 Gauss 格基約化）——所以這個系統一碰就碎。下面先看一眼結果：

```python
q, h = 122430513841, 39245579300

def gauss_reduce(v1, v2):                    # 第 24 課會詳細解釋
    dot = lambda a, b: a[0] * b[0] + a[1] * b[1]
    while True:
        if dot(v2, v2) < dot(v1, v1):
            v1, v2 = v2, v1
        m = round(dot(v1, v2) / dot(v1, v1))
        if m == 0:
            return v1, v2
        v2 = (v2[0] - m * v1[0], v2[1] - m * v1[1])

v1, v2 = gauss_reduce((1, h), (0, q))
print(v1, v2)
F, G = abs(v1[0]), abs(v1[1])
e = 18357558717
a = F * e % q
print("Eve 解出", pow(F, -1, G) * a % G)
```
```output
(-231231, -195698) (-368222, 217835)
Eve 解出 123456
```
最短向量就是 (f, g) = (231231, 195698)（差一個正負號），Eve 直接拿到私鑰。

---

# 第二部分：子集合和問題與超遞增序列

## 2.1 子集合和問題

給一串正整數 `M = (M₁, …, Mₙ)` 和目標 S，找一個子集合，總和是 S。等價地：找 **0/1 向量** x 使 `x · M = Σ xᵢMᵢ = S`。

課本例 6.2：`M = (2, 3, 4, 9, 14, 23)`。S = 27 只有 {4, 9, 14}；S = 29 有兩組：{2, 4, 23} 和 {2, 4, 9, 14}。

子集合和是 **NP 完全** 問題（第 17 課）。最直接的解法要試 2ⁿ 種。

## 2.2 碰撞演算法：O(2^(n/2))

**命題 6.3**：把 M 分成前後兩半，前半所有子集合的和存進表格（2^(n/2) 個），再對後半每個子集合算 `S − (後半的和)` 去查表。這又是中間相遇（第 16 課）——時間和空間都是 O(2^(n/2))。

```python
from itertools import product

def subset_sum_mitm(M, S):
    n = len(M)
    left, right = M[: n // 2], M[n // 2 :]
    table = {}
    for bits in product([0, 1], repeat=len(left)):
        table.setdefault(sum(b * m for b, m in zip(bits, left)), bits)
    for bits in product([0, 1], repeat=len(right)):
        rest = S - sum(b * m for b, m in zip(bits, right))
        if rest in table:
            return table[rest] + bits
    return None

M = (2, 3, 4, 9, 14, 23)
print(subset_sum_mitm(M, 27), subset_sum_mitm(M, 29))
```
```output
(0, 0, 1, 0, 0, 1) (1, 0, 1, 0, 0, 1)
```
所以要有 2^k 的安全度，n 至少要 2k（例如 2⁸⁰ 安全度要 n > 160）。

## 2.3 超遞增序列

**定義**：`r = (r₁, …, rₙ)` 叫 **超遞增**（superincreasing），如果每一項都大於前面所有項的和：`r_{i+1} ≥ 2rᵢ`（課本用的定義），因此 `r_k > r₁ + ⋯ + r_{k−1}`（引理 6.4）。

**命題 6.5**：超遞增序列的子集合和問題 **非常容易**：從最大的開始，能放就放（貪婪法）。

**為什麼**：如果 `S ≥ rₙ`，那 rₙ 一定要選——因為前面所有項加起來都不到 rₙ。選了之後 `S ← S − rₙ`，再看 r_{n−1}，以此類推。

課本例 6.6：`r = (3, 11, 24, 50, 115)`，S = 142。

```python
def solve_superincreasing(r, S):
    x = [0] * len(r)
    for i in reversed(range(len(r))):
        if S >= r[i]:
            x[i] = 1
            S -= r[i]
    return x if S == 0 else None

print(solve_superincreasing((3, 11, 24, 50, 115), 142))
```
```output
[1, 0, 1, 0, 1]
```
`x = (1, 0, 1, 0, 1)`：3 + 24 + 115 = 142。

---

# 第三部分：Merkle–Hellman 背包密碼

## 3.1 系統（1978）

**想法**：用容易的超遞增問題當 **陷門**，再用模乘法把它 **偽裝** 成看起來隨機的子集合和問題。

| | 做什麼 |
|---|---|
| **Alice 建金鑰** | 秘密的超遞增序列 r；秘密的 A、B，`B > 2rₙ`、`gcd(A, B) = 1`；公鑰 `Mᵢ ≡ A rᵢ (mod B)` |
| **Bob 加密** | 明文是 0/1 向量 x，送 `S = x · M` |
| **Alice 解密** | `S' ≡ A⁻¹ S (mod B)`，用超遞增的貪婪法解 `S' = x · r` |

**為什麼對**：`S' ≡ A⁻¹ Σ xᵢ A rᵢ = Σ xᵢ rᵢ (mod B)`，而 `Σ xᵢ rᵢ ≤ Σ rᵢ < 2rₙ < B`，所以模 B 沒有繞圈——又是「小 → 沒有繞圈 → 等式」的技巧。

課本例 6.7：`r = (3, 11, 24, 50, 115)`、A = 113、B = 250。

```python
def solve_superincreasing(r, S):
    x = [0] * len(r)
    for i in reversed(range(len(r))):
        if S >= r[i]:
            x[i] = 1
            S -= r[i]
    return x if S == 0 else None

r, A, B = (3, 11, 24, 50, 115), 113, 250
M = [A * ri % B for ri in r]
print("公鑰", M)
x = (1, 0, 1, 0, 1)
S = sum(xi * mi for xi, mi in zip(x, M))
print("密文", S)
S2 = pow(A, -1, B) * S % B
print(pow(A, -1, B), S2, solve_superincreasing(r, S2))
```
```output
公鑰 [89, 243, 212, 150, 245]
密文 546
177 142 [1, 0, 1, 0, 1]
```
## 3.2 它怎麼被破的

**實際尺寸的問題**：為了抵抗碰撞攻擊 n 要夠大，又為了避免其他攻擊，r₁ 要大於 2ⁿ，結果 Mᵢ 大約 2²ⁿ 位元。公鑰是 n 個 2n 位元的數，**約 2n² 位元**；n = 300 時就是 176 KB——太大了。

**更致命的是格攻擊**（Shamir 1982 首先破解；LLL 演算法 1985 年發表後，所有背包變體幾乎全滅）。Eve 用下面這些向量（課本 (6.4) 式）當格的基底：

```
v₁   = (2, 0, 0, …, 0, M₁)
v₂   = (0, 2, 0, …, 0, M₂)
  ⋮
vₙ   = (0, 0, 0, …, 2, Mₙ)
vₙ₊₁ = (1, 1, 1, …, 1, S)
```

如果 x 是解，那

```
t = Σ xᵢ vᵢ − vₙ₊₁ = (2x₁ − 1, 2x₂ − 1, …, 2xₙ − 1, 0)
```

每個分量都是 ±1，**長度只有 √n**；而基底向量的長度大約是 2²ⁿ。所以 t 幾乎一定是格中最短的向量——找到最短向量就找到明文。

```python
import math
M = [89, 243, 212, 150, 245]
S = 546
x = (1, 0, 1, 0, 1)
n = len(M)
rows = [[2 if j == i else 0 for j in range(n)] + [M[i]] for i in range(n)] + [[1] * n + [S]]
t = [sum(x[i] * rows[i][k] for i in range(n)) - rows[n][k] for k in range(n + 1)]
print(t, round(math.sqrt(sum(c * c for c in t)), 3))
print([round(math.sqrt(sum(c * c for c in row)), 1) for row in rows])
```
```output
[1, -1, 1, -1, 1, 0] 2.236
[89.0, 243.0, 212.0, 150.0, 245.0, 546.0]
```
第 24 課會真的用 LLL 演算法從這個格中把 t 找出來。

> **歷史教訓**（呼應第 17 課）：子集合和是 NP 完全問題，但 Merkle–Hellman 用的是 **有陷門的特殊實例**，而這個特殊結構正好可以被格方法利用。**建立在 NP 完全問題上 ≠ 安全。**

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 同餘密碼 | Congruential Cryptosystem | 用小的 f、g 當私鑰的玩具系統 | 1.1 |
| 格 | Lattice | 一組向量的所有整數線性組合 | 1.2 |
| 子集合和問題 | Subset-Sum Problem | 找子集合使總和為 S | 2.1 |
| 超遞增序列 | Superincreasing Sequence | 每一項大於前面所有項的和 | 2.3 |
| 背包密碼 | Knapsack Cryptosystem | 用偽裝的子集合和問題加密 | 3.1 |

---

# 習題

### 題 1：同餘密碼

q = 918293817、f = 19928、g = 18643。算 h；用 m = 10220、r = 19564 加密，再解密。

### 題 2：超遞增

`r = (2, 5, 9, 18, 37, 80)` 是超遞增嗎？解 S = 133。

### 題 3：背包密碼

用 `r = (2, 5, 9, 18, 37, 80)`、A = 77、B = 200 建公鑰，加密 x = (0, 1, 1, 0, 0, 1)，再解密。

### 題 4：觀念

同餘密碼和背包密碼的解密都靠「某個數小於模數，所以沒有繞圈」。各指出是哪個不等式。

---

# 習題解答

**題 1**：

```python
q, f, g = 918293817, 19928, 18643
h = pow(f, -1, q) * g % q
m, r = 10220, 19564
e = (r * h + m) % q
a = f * e % q
print(h, e, a, pow(f, -1, g) * a % g)
```
```output
767748560 619167208 568395812 10220
```
**題 2**：每一項都大於前面總和（5 > 2、9 > 7、18 > 16、37 > 34、80 > 71），是超遞增。貪婪法：133 ≥ 80 選、53 ≥ 37 選、16 < 18 不選、16 ≥ 9 選、7 ≥ 5 選、2 ≥ 2 選。

```python
def solve_superincreasing(r, S):
    x = [0] * len(r)
    for i in reversed(range(len(r))):
        if S >= r[i]:
            x[i] = 1
            S -= r[i]
    return x if S == 0 else None
print(solve_superincreasing((2, 5, 9, 18, 37, 80), 133))
```
```output
[1, 1, 1, 0, 1, 1]
```
**題 3**：

```python
def solve_superincreasing(r, S):
    x = [0] * len(r)
    for i in reversed(range(len(r))):
        if S >= r[i]:
            x[i] = 1
            S -= r[i]
    return x if S == 0 else None

r, A, B = (2, 5, 9, 18, 37, 80), 77, 200
M = [A * ri % B for ri in r]
x = (0, 1, 1, 0, 0, 1)
S = sum(a * b for a, b in zip(x, M))
print(M, S, solve_superincreasing(r, pow(A, -1, B) * S % B))
```
```output
[154, 185, 93, 186, 49, 160] 438 [0, 1, 1, 0, 0, 1]
```
**題 4**：同餘密碼：`rg + fm < q`，所以 `a ≡ fe (mod q)` 就等於整數 `rg + fm`。背包密碼：`Σ xᵢrᵢ ≤ Σ rᵢ < 2rₙ < B`，所以 `S' ≡ A⁻¹S (mod B)` 就等於整數 `x · r`。
