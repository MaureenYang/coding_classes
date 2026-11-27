# 18. 橢圓曲線與橢圓曲線離散對數（Elliptic Curves and the ECDLP）

> 對應課本：§5.1～§5.3
>
> 程式練習：`MC13 橢圓曲線運算`
>
> 先備知識：第 07 課（群、嬰兒步巨人步）、第 14 課（二次剩餘）。

**這一課分成四個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 實數上的橢圓曲線 | 曲線的方程式、用「畫直線」定義點的加法、無窮遠點 O |
| 第二部分 | 加法公式 | 課本定理 5.6 的演算法、為什麼這樣得到一個群 |
| 第三部分 | 有限體上的橢圓曲線 | E(F_p) 的點、Hasse 定理 |
| 第四部分 | ECDLP 與倍加法 | 給 P、Q = nP 求 n；用「倍加法」快速算 nP；有號二進位 |

---

# 第一部分：實數上的橢圓曲線

## 1.1 方程式

**橢圓曲線** 是滿足

```
E : Y² = X³ + AX + B
```

的點 (x, y) 全體，再加上一個額外的點 **O**（「無窮遠點」）。要求 `4A³ + 27B² ≠ 0`（判別式不為 0），保證曲線 **沒有尖點或自交點**——也就是右邊的三次式沒有重根。

（名字裡的「橢圓」和橢圓沒有直接關係，來自計算橢圓弧長時出現的積分。）

## 1.2 用直線定義加法

橢圓曲線最神奇的性質：**一條直線和曲線最多交三點**（代入後是三次方程式）。所以給兩個點 P、Q：

1. 畫過 P、Q 的直線 L，它和 E 交於第三個點 R。
2. 把 R 對 x 軸鏡射（y 變號），得到的點定義為 **P + Q**。

特殊情況：
- **P = Q**：用 P 點的 **切線**。
- **P 和 Q 上下對稱**（x 相同、y 相反）：直線是垂直的，和曲線沒有第三個交點——我們說它交於 **O**，定義 `P + Q = O`。所以 `−P` 就是 P 的鏡射點。
- **O 是單位元素**：`P + O = P`。可以想像 O 在「y 軸的最上方也是最下方」，每條垂直線都穿過它。

**定理 5.5**：這個加法讓 E 成為一個 **交換群**——有單位元素 O、反元素 −P、交換律、**結合律**。結合律用圖很難看出來，用公式驗證則是一段冗長的計算。

---

# 第二部分：加法公式

## 2.1 定理 5.6（橢圓曲線加法演算法）

`E : Y² = X³ + AX + B`，要算 `P₁ + P₂`：

1. 如果 P₁ = O，答案是 P₂；如果 P₂ = O，答案是 P₁。
2. 寫成 `P₁ = (x₁, y₁)`、`P₂ = (x₂, y₂)`。
3. 如果 `x₁ = x₂` 且 `y₁ = −y₂`，答案是 O。
4. 否則令

```
λ = (y₂ − y₁) / (x₂ − x₁)      如果 P₁ ≠ P₂（割線的斜率）
λ = (3x₁² + A) / (2y₁)         如果 P₁ = P₂（切線的斜率，隱函數微分）

x₃ = λ² − x₁ − x₂，  y₃ = λ(x₁ − x₃) − y₁
```

**推導**：把直線 `y = λx + ν` 代入 `y² = x³ + Ax + B`，得到 `x³ − λ²x² + ⋯ = 0`。三個根的和是 λ²（根與係數），已知其中兩個是 x₁、x₂，所以第三個是 `λ² − x₁ − x₂`。再算出直線上的 y，取負號（鏡射）。

```python
from fractions import Fraction as F

A, B = -15, 18                       # E : Y² = X³ − 15X + 18（課本 5.1 節的例子）
O = None

def add(P, Q):
    if P is O:
        return Q
    if Q is O:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and y1 == -y2:
        return O
    if P == Q:
        lam = (3 * x1 * x1 + A) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)

def on_curve(P):
    return P is O or P[1] ** 2 == P[0] ** 3 + A * P[0] + B

P, Q = (F(7), F(16)), (F(1), F(2))
S = add(P, Q)
print(S, on_curve(S))
print(add(P, P), on_curve(add(P, P)))
print(add(P, (P[0], -P[1])))
print(add(add(P, Q), (F(3), F(0))) == add(P, add(Q, (F(3), F(0)))))      # 結合律抽查
```
```output
(Fraction(-23, 9), Fraction(170, 27)) True
(Fraction(193, 64), Fraction(223, 512)) True
None
True
```
P + Q 和 2P 的座標都是分數，但仍然在曲線上。最後一行抽查結合律。

---

# 第三部分：有限體上的橢圓曲線

## 3.1 E(F_p)

密碼學用的是座標在 **有限體** F_p 中的點（p ≥ 3，F₂ 的情況在第 19 課）：

```
E(F_p) = {(x, y) : x, y ∈ F_p，y² ≡ x³ + Ax + B (mod p)} ∪ {O}
```

加法公式完全一樣，只是「除法」改成乘以模反元素（第 03 課）。**定理 5.9**：E(F_p) 是 **有限交換群**。

**列出所有點**（課本例 5.8，`Y² = X³ + 3X + 8` over F₁₃）：對每個 x，看右邊是不是二次剩餘（第 14 課），是的話有兩個 y（或 y = 0 時一個）。

```python
p, A, B = 13, 3, 8
points = [None] + [(x, y) for x in range(p) for y in range(p) if (y * y - x ** 3 - A * x - B) % p == 0]
print(len(points), points[1:])

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

print(add((9, 7), (1, 8)), add((9, 7), (9, 7)), add((1, 8), (1, 5)))   # 課本例 5.10
```
```output
9 [(1, 5), (1, 8), (2, 3), (2, 10), (9, 6), (9, 7), (12, 2), (12, 11)]
(2, 10) (9, 6) None
```
`(9, 7) + (1, 8) = (2, 10)`、`2·(9, 7) = (9, 6)`，和課本一致；`(1, 8) + (1, 5) = O`（y 相反）。

## 3.2 有幾個點：Hasse 定理

大約一半的 x 讓右邊是平方數，每個貢獻兩個點，再加上 O，所以點數大約 p + 1。

**定理 5.11（Hasse）**：

```
#E(F_p) = p + 1 − t_p，  |t_p| ≤ 2√p
```

`t_p` 叫 **Frobenius 跡**（trace of Frobenius）。

```python
import math

def count_points(A, B, p):
    sq = {}
    for y in range(p):
        sq[y * y % p] = sq.get(y * y % p, 0) + 1
    return 1 + sum(sq.get((x ** 3 + A * x + B) % p, 0) for x in range(p))

for p in (3, 5, 7, 11, 13, 17, 101, 1009):          # 課本例 5.12：Y² = X³ + 4X + 6
    n = count_points(4, 6, p)
    t = p + 1 - n
    print(p, n, t, round(2 * math.sqrt(p), 2))
```
```output
3 4 0 3.46
5 8 -2 4.47
7 11 -3 5.29
11 16 -4 6.63
13 14 0 7.21
17 15 3 8.25
101 117 -15 20.1
1009 1006 4 63.53
```
前六列和課本表 5.2 一致，`|t_p|` 永遠不超過 `2√p`。

**實務上怎麼算點數**：上面的方法要 O(p) 步，p ≈ 2²⁵⁶ 時不可能。Schoof（1985）找到 O((log p)⁶) 的多項式時間演算法，後來 Elkies、Atkin 改進成 SEA 演算法——所以我們能 **選出點數是大質數** 的曲線（這對安全很重要：見第四部分）。

---

# 第四部分：ECDLP 與倍加法

## 4.1 橢圓曲線離散對數問題

**定義**：給 E(F_p) 中的點 P 和 Q，找整數 n 使

```
Q = nP = P + P + ⋯ + P（n 個）
```

n 記作 `log_P(Q)`。和 F_p* 的 DLP 一樣，n 只決定到 **P 的階** 的倍數（Lagrange 定理：P 的階整除 #E(F_p)）。

課本例 5.15：`Y² = X³ + 8X + 7` over F₇₃，`P = (32, 53)`，`Q = (39, 17) = 11P`。

```python
p, A, B = 73, 8, 7

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

P = (32, 53)
R, n = P, 1
targets = {(39, 17): "Q", (35, 47): "R", (58, 4): "S"}
while R is not None:
    if R in targets:
        print(targets[R], "=", n, "P")
    R, n = add(R, P), n + 1
print("P 的階 =", n - 1)
```
```output
Q = 11 P
S = 28 P
R = 37 P
P 的階 = 40
```
## 4.2 倍加法（Double-and-Add）

要讓 ECDLP 能用在密碼學，**算 nP 必須很快**。和第 03 課的快速冪一模一樣，只是把「平方」換成「倍點」、「乘」換成「加」：

```
Q ← P，R ← O
while n > 0:
    if n 是奇數：R ← R + Q
    Q ← 2Q，n ← ⌊n/2⌋
回傳 R
```

最多 log₂ n 次倍點 + log₂ n 次加法。課本例 5.16：`Y² = X³ + 14X + 19` over F₃₆₂₃，`P = (6, 730)`，算 947P。

```python
p, A, B = 3623, 14, 19

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

def mul(n, P):
    R, Q = None, P
    doubles = adds = 0
    while n > 0:
        if n & 1:
            R = add(R, Q)
            adds += 1
        n >>= 1
        if n:
            Q = add(Q, Q)
            doubles += 1
    return R, doubles, adds

print(bin(947), mul(947, (6, 730)))
```
```output
0b1110110011 ((3492, 60), 9, 7)
```
9 次倍點、7 次加法（第一次是 O + P，課本不算，所以說 6 次），結果 `947P = (3492, 60)`。

## 4.3 有號二進位：更少的加法

**觀察**：橢圓曲線上 **減法和加法一樣便宜**（−P 只是 y 變號）。所以可以把 n 寫成係數是 {−1, 0, 1} 的「二進位」，非零項更少。

**命題 5.18**：每個 n 都能寫成 `Σ uᵢ 2^i`，`uᵢ ∈ {−1, 0, 1}`，且非零項 **最多約一半**（NAF，non-adjacent form：相鄰兩位不會都非零）。

例：`31 = 11111₂`（5 個 1）= `32 − 1`（2 項）。

```python
def naf(n):
    digits = []
    while n > 0:
        if n & 1:
            d = 2 - (n % 4)          # n ≡ 1 (mod 4) → 1；n ≡ 3 (mod 4) → −1
            n -= d
        else:
            d = 0
        digits.append(d)
        n //= 2
    return digits                    # 低位在前

for n in (31, 947, 2**20 - 1, 123456789):
    d = naf(n)
    assert sum(x * 2**i for i, x in enumerate(d)) == n
    print(n, bin(n).count("1"), sum(1 for x in d if x))
```
```output
31 5 2
947 7 5
1048575 20 2
123456789 16 11
```
## 4.4 ECDLP 有多難

**一般的演算法**：嬰兒步巨人步、碰撞法、Pollard ρ（第 07、16 課）都能直接用在 E(F_p) 上，花 **O(√N)** 步（N 是 P 的階）。

**沒有指標演算法**：F_p* 能用指標演算法（第 13 課）是因為整數能 **分解成小質數**；橢圓曲線上的點沒有這種結構。到目前為止，對 **一般的** 曲線，最好的 ECDLP 演算法仍是 O(√N)——**完全指數時間**。

**要避開的弱曲線**（第 19、20 課會再談）：
- 點數 N 有小質因數：Pohlig–Hellman 能拆小（所以選 **點數是大質數或大質數乘小餘因子** 的曲線）。
- **異常曲線**（`#E(F_p) = p`）：有多項式時間的攻擊。
- **嵌入度小** 的曲線（例如超奇異曲線）：MOV 攻擊用配對把 ECDLP 轉成 F_{p^k}* 的 DLP（第 20 課）。

| 安全度 | RSA / F_p* 的大小 | 橢圓曲線的 p |
|---|---|---|
| 80 位元 | 1024 位元 | 160 位元 |
| 128 位元 | 3072 位元 | 256 位元 |
| 256 位元 | 15360 位元 | 512 位元 |

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 橢圓曲線 | Elliptic Curve | `Y² = X³ + AX + B` 加上 O | 1.1 |
| 無窮遠點 | Point at Infinity O | 群的單位元素 | 1.2 |
| 判別式 | Discriminant | `4A³ + 27B²`，不能為 0 | 1.1 |
| 割線 / 切線 | Secant / Tangent Line | 加法 / 倍點用的直線 | 2.1 |
| E(F_p) | Points over F_p | 座標在 F_p 的點 | 3.1 |
| Hasse 定理 | Hasse's Theorem | 點數在 `p + 1 ± 2√p` 之間 | 3.2 |
| Frobenius 跡 | Trace of Frobenius | `t_p = p + 1 − #E(F_p)` | 3.2 |
| ECDLP | Elliptic Curve Discrete Logarithm Problem | 給 P、nP 求 n | 4.1 |
| 倍加法 | Double-and-Add | 橢圓曲線版的快速冪 | 4.2 |
| NAF | Non-Adjacent Form | 係數 {−1, 0, 1} 的二進位 | 4.3 |

---

# 習題

### 題 1：判別式

`Y² = X³ − 3X + 2` 是橢圓曲線嗎？為什麼？

### 題 2：手算加法

在 `Y² = X³ + 3X + 8` over F₁₃ 中，算 `(1, 5) + (2, 3)` 和 `2·(1, 5)`。

### 題 3：點數

列出 `Y² = X³ + X + 1` over F₅ 的所有點，並驗證 Hasse 定理。這個群是循環群嗎？

### 題 4：倍加法

在第 4.2 節的曲線上，算 `100P`，並說明用了幾次倍點、幾次加法。

### 題 5：觀念

為什麼同樣 128 位元的安全度，橢圓曲線只要 256 位元的 p，而 F_p* 的 DLP 要 3072 位元？

---

# 習題解答

**題 1**：`4(−3)³ + 27 · 2² = −108 + 108 = 0`，判別式是 0，不是橢圓曲線。事實上 `X³ − 3X + 2 = (X − 1)²(X + 2)` 有重根，曲線在 (1, 0) 自交。

**題 2**：

```python
p, A = 13, 3

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

print(add((1, 5), (2, 3)), add((1, 5), (1, 5)))
```
```output
(1, 8) (2, 10)
```
**題 3**：

```python
p, A, B = 5, 1, 1
pts = [None] + [(x, y) for x in range(p) for y in range(p) if (y * y - x ** 3 - A * x - B) % p == 0]
print(len(pts), pts[1:], abs(p + 1 - len(pts)) <= 2 * p ** 0.5)

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    lam = ((3 * x1 * x1 + A) * pow(2 * y1, -1, p) if P == Q else (y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

def order(P):
    R, k = P, 1
    while R is not None:
        R, k = add(R, P), k + 1
    return k

print({P: order(P) for P in pts[1:]})
```
```output
9 [(0, 1), (0, 4), (2, 1), (2, 4), (3, 1), (3, 4), (4, 2), (4, 3)] True
{(0, 1): 9, (0, 4): 9, (2, 1): 3, (2, 4): 3, (3, 1): 9, (3, 4): 9, (4, 2): 9, (4, 3): 9}
```
有 9 個點，`|6 − 9| = 3 ≤ 2√5 ≈ 4.47`。有階為 9 的點，所以是循環群。

**題 4**：100 = 1100100₂，6 次倍點、3 次加法（第一次加到 O 上）。

```python
p, A = 3623, 14

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    lam = ((3 * x1 * x1 + A) * pow(2 * y1, -1, p) if P == Q else (y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

R, Q, n = None, (6, 730), 100
while n:
    if n & 1:
        R = add(R, Q)
    n >>= 1
    Q = add(Q, Q)
print(R)
```
```output
(942, 3315)
```
**題 5**：F_p* 有次指數時間的指標演算法 / 數體篩法，要很大的 p 才能把 `L_{1/3}(p)` 推到 2¹²⁸；橢圓曲線目前只有 O(√N) 的通用攻擊，`√(2²⁵⁶) = 2¹²⁸` 就夠了。
