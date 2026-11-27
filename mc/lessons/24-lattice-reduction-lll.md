# 24. 格基約化與 LLL 演算法（Lattice Reduction）

> 對應課本：§6.12、§6.13
>
> 程式練習：`MC14 二維格基約化`
>
> 先備知識：第 22 課（Gram–Schmidt、SVP、Babai）、第 21、23 課（要攻擊的系統）。

**這一課分成四個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 二維：Gauss 格基約化 | 一直扣掉另一個向量的倍數，直到不能再短；課本例 6.64 |
| 第二部分 | LLL 演算法 | 大小條件、Lovász 條件、演算法、保證找到的向量最多是最短的 2^((n−1)/2) 倍 |
| 第三部分 | LLL 的變形 | 搭配 Babai 解 apprCVP、深插入、BKZ |
| 第四部分 | 用 LLL 做密碼分析 | 破解同餘密碼、背包密碼、玩具 NTRU、GGH |

---

# 第一部分：二維：Gauss 格基約化

## 1.1 想法

二維格有基底 v₁、v₂，假設 `‖v₁‖ ≤ ‖v₂‖`。想讓 v₂ 變短：最理想是扣掉它在 v₁ 方向的投影（Gram–Schmidt），但係數必須是 **整數**，所以取最接近的整數：

```
m = round( v₁ · v₂ / ‖v₁‖² )，  v₂ ← v₂ − m v₁
```

如果扣完之後 v₂ 比 v₁ 還短，就交換，繼續做。

**命題 6.63（Gauss 格基約化）**：

```
loop:
    if ‖v₂‖ < ‖v₁‖: 交換 v₁、v₂
    m = round(v₁ · v₂ / ‖v₁‖²)
    if m == 0: 回傳 v₁, v₂
    v₂ ← v₂ − m v₁
```

結束時 **v₁ 就是格中的最短非零向量**，而 v₂ 是在「和 v₁ 獨立」的向量中最短的。條件 m = 0 等價於 `|v₁ · v₂| ≤ ‖v₁‖²/2`——兩個向量夾角在 60° 到 120° 之間。

（這就是第 21 課破解同餘密碼時偷用的函數，也就是程式練習 MC14。）

## 1.2 課本例 6.64

```python
def gauss_reduce(v1, v2, verbose=False):
    dot = lambda a, b: a[0] * b[0] + a[1] * b[1]
    while True:
        if dot(v2, v2) < dot(v1, v1):
            v1, v2 = v2, v1
        num, den = dot(v1, v2), dot(v1, v1)
        m = (2 * num + den) // (2 * den)          # 用整數算 round(num / den)，避免浮點誤差
        if verbose:
            print(v1, v2, "m =", m)
        if m == 0:
            return v1, v2
        v2 = (v2[0] - m * v1[0], v2[1] - m * v1[1])

v1, v2 = gauss_reduce((66586820, 65354729), (6513996, 6393464), verbose=True)
print(v1, v2)
det = abs(66586820 * 6393464 - 65354729 * 6513996)
print(det, abs(v1[0] * v2[1] - v1[1] * v2[0]))
```
```output
(6513996, 6393464) (66586820, 65354729) m = 10
(1446860, 1420089) (6513996, 6393464) m = 5
(-720304, -706981) (1446860, 1420089) m = -2
(6252, 6127) (-720304, -706981) m = -115
(-1324, -2376) (6252, 6127) m = -3
(2280, -1001) (-1324, -2376) m = 0
(2280, -1001) (-1324, -2376)
6742604 6742604
```
原本兩個基底向量長度約 9 × 10⁷ 和 9 × 10⁶，約化後是 (2280, −1001) 和 (−1324, −2376)，長度只有 2490 和 2720 左右——同一個格（行列式都是 6742604），但基底好得多。

> ⚠️ 實作提醒：`round(num / den)` 在數字很大時用浮點數會出錯，上面改用整數運算 `(2·num + den) // (2·den)`。寫 C 程式時（MC14）也要用整數，並注意 64 位元溢位。

---

# 第二部分：LLL 演算法

## 2.1 什麼是「好」的基底

1982 年 A. K. Lenstra、H. W. Lenstra、L. Lovász 把 Gauss 的方法推廣到任意維度。

設 v₁*, …, vₙ* 是 Gram–Schmidt 正交化（第 22 課），`μᵢⱼ = vᵢ · vⱼ* / ‖vⱼ*‖²`。注意 **`det L = ‖v₁*‖ ⋯ ‖vₙ*‖`**（命題 6.65）。

**LLL 約化基底** 的兩個條件：

| 條件 | 式子 | 意思 |
|---|---|---|
| **大小條件** | `|μᵢⱼ| ≤ 1/2`（所有 j < i） | 每個向量都已經盡量扣掉前面向量的整數倍（像 Gauss 的 m = 0） |
| **Lovász 條件** | `‖vᵢ*‖² ≥ (3/4 − μ²_{i,i−1}) ‖v*_{i−1}‖²` | 正交化後的長度不會突然變得太短——向量大致由短到長排好 |

## 2.2 LLL 約化基底有多好（定理 6.66）

```
‖v₁‖ ≤ 2^((n−1)/2) · (最短非零向量的長度)
‖v₁‖ ≤ 2^((n−1)/4) · (det L)^(1/n)
```

也就是 LLL 在 **多項式時間** 內解決 **近似因子 2^((n−1)/2)** 的 apprSVP。這個因子是指數級的，但實務上 LLL 的表現比理論保證好得多；維度小（例如 < 100）時常常直接找到最短向量。

## 2.3 演算法（課本圖 6.7）

```
k = 2
while k ≤ n:
    for j = k−1 down to 1:                    # 大小約化
        vₖ ← vₖ − round(μₖⱼ) vⱼ
    if Lovász 條件對 k 成立:
        k ← k + 1
    else:
        交換 vₖ、v_{k−1}；k ← max(k − 1, 2)
```

**定理 6.68**：迴圈最多執行 `O(n² log n + n² log B)` 次（B 是基底向量的最大長度），所以 LLL 是 **多項式時間** 演算法。為什麼會停：每次交換都讓一個正的量 `D = Π ‖vᵢ*‖^(2(n−i+1))` 至少縮小成 3/4 倍，而 D 對整數格有正的下界。

```python
from fractions import Fraction as F

def lll(B, delta=F(3, 4)):
    B = [list(map(F, v)) for v in B]
    n = len(B)
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))

    def gso():
        Bs, mu = [], [[F(0)] * n for _ in range(n)]
        for i in range(n):
            w = B[i][:]
            for j in range(i):
                mu[i][j] = dot(B[i], Bs[j]) / dot(Bs[j], Bs[j])
                w = [a - mu[i][j] * b for a, b in zip(w, Bs[j])]
            Bs.append(w)
        return Bs, mu

    Bs, mu = gso()
    k = 1
    while k < n:
        for j in range(k - 1, -1, -1):
            q = round(mu[k][j])
            if q:
                B[k] = [a - q * b for a, b in zip(B[k], B[j])]
                Bs, mu = gso()
        if dot(Bs[k], Bs[k]) >= (delta - mu[k][k - 1] ** 2) * dot(Bs[k - 1], Bs[k - 1]):
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            Bs, mu = gso()
            k = max(k - 1, 1)
    return [[int(x) for x in v] for v in B]

M = [[19, 2, 32, 46, 3, 33], [15, 42, 11, 0, 3, 24], [43, 15, 0, 24, 4, 16],
     [20, 44, 44, 0, 18, 15], [0, 48, 35, 16, 31, 31], [48, 33, 32, 9, 1, 29]]   # 課本例 6.72
R = lll(M)
for v in R:
    print(v, round(sum(x * x for x in v) ** 0.5, 2))
```
```output
[7, -12, -8, 4, 19, 9] 26.74
[-20, 4, -9, 16, 13, 16] 34.32
[5, 2, 33, 0, 15, -9] 37.74
[-6, -7, -20, -21, 8, -12] 33.67
[-10, -24, 21, -15, -6, -11] 38.72
[7, 4, -9, -11, 1, 31] 35.06
```
（這是為了清楚而寫的簡單版本：每次修改都重算整個 Gram–Schmidt，用分數保證精確。實務上的實作只更新需要的部分、用浮點數並小心控制誤差，例如 fplll 函式庫。）

原本的基底向量長度在 52～76 之間，約化後全部在 27～39 之間，而且第一個向量最短（約 26.7）。課本例 6.72 用的是同一個格。

---

# 第三部分：LLL 的變形

## 3.1 LLL + Babai 解 apprCVP

**定理 6.73**：先用 LLL 把基底約化成「近乎正交」，再跑 Babai 演算法，就能在多項式時間內解近似因子 Cⁿ 的 apprCVP。——這正是攻擊 GGH 的方法：Eve 把公開的壞基底丟進 LLL，維度不夠高時就能得到夠好的基底來解密。

## 3.2 更強但更慢：深插入與 BKZ

| 方法 | 做法 | 代價 |
|---|---|---|
| **深插入**（deep insertion） | 交換時不只和前一個交換，而是插到更前面最划算的位置 | 實務上更好，最壞情況可能不是多項式時間 |
| **BKZ**（block Korkin–Zolotarev） | 把基底切成大小 β 的區塊，每個區塊 **精確** 解 SVP | 近似因子隨 β 變好，時間隨 β 指數成長 |

**格密碼的安全性** 就是用「BKZ 需要多大的區塊才能找到秘密向量、那要花多少時間」來估計的。

---

# 第四部分：用 LLL 做密碼分析（§6.13）

## 4.1 同餘密碼（第 21 課）

二維格 `(1, h), (0, q)`，Gauss 約化一步到位找出 (f, g)。

## 4.2 背包密碼

第 21 課的背包格：`vᵢ = (2eᵢ, Mᵢ)`、`v_{n+1} = (1, …, 1, S)`，目標向量 `t = (2x₁ − 1, …, 2xₙ − 1, 0)`，所有分量都是 ±1。

```python
from fractions import Fraction as F
import random

def lll(B, delta=F(99, 100)):
    B = [list(map(F, v)) for v in B]
    n = len(B)
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    def gso():
        Bs, mu = [], [[F(0)] * n for _ in range(n)]
        for i in range(n):
            w = B[i][:]
            for j in range(i):
                mu[i][j] = dot(B[i], Bs[j]) / dot(Bs[j], Bs[j])
                w = [a - mu[i][j] * b for a, b in zip(w, Bs[j])]
            Bs.append(w)
        return Bs, mu
    Bs, mu = gso()
    k = 1
    while k < n:
        for j in range(k - 1, -1, -1):
            q = round(mu[k][j])
            if q:
                B[k] = [a - q * b for a, b in zip(B[k], B[j])]
                Bs, mu = gso()
        if dot(Bs[k], Bs[k]) >= (delta - mu[k][k - 1] ** 2) * dot(Bs[k - 1], Bs[k - 1]):
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            Bs, mu = gso()
            k = max(k - 1, 1)
    return [[int(x) for x in v] for v in B]

random.seed(3)
n = 12
r, total = [], 0
for _ in range(n):                                  # 秘密的超遞增序列
    nxt = total + random.randint(1, 20)
    r.append(nxt)
    total += nxt
B = 2 * r[-1] + random.randint(1, 50)
A = random.randrange(2, B)
while __import__("math").gcd(A, B) != 1:
    A += 1
M = [A * x % B for x in r]                          # 公鑰
x = [random.randint(0, 1) for _ in range(n)]
S = sum(a * b for a, b in zip(x, M))                # 密文

rows = [[2 if j == i else 0 for j in range(n)] + [M[i]] for i in range(n)] + [[1] * n + [S]]
for v in lll(rows):
    if v[-1] == 0 and all(c in (1, -1) for c in v[:-1]):
        guess = [(c + 1) // 2 for c in v[:-1]]
        if sum(a * b for a, b in zip(guess, M)) != S:
            guess = [1 - g for g in guess]
        print("LLL 找到", guess)
        break
print("真正的   ", x)
```
```output
LLL 找到 [0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0]
真正的    [0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0]
```
完全沒有用到私鑰（r、A、B），只靠公鑰 M 和密文 S 就解出明文。（Lagarias–Odlyzko 證明「密度」低的背包問題幾乎都能這樣解；後來 Coster 等人改良的格把可破解的範圍再擴大。）

## 4.3 玩具 NTRU：從公鑰找回私鑰

第 23 課的 NTRU 格 `(I H; 0 qI)`，N = 7，維度 14。私鑰 (f, g) 是格中的最短向量（以及它的旋轉）：

```python
from fractions import Fraction as F

def lll(B, delta=F(99, 100)):
    B = [list(map(F, v)) for v in B]
    n = len(B)
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    def gso():
        Bs, mu = [], [[F(0)] * n for _ in range(n)]
        for i in range(n):
            w = B[i][:]
            for j in range(i):
                mu[i][j] = dot(B[i], Bs[j]) / dot(Bs[j], Bs[j])
                w = [a - mu[i][j] * b for a, b in zip(w, Bs[j])]
            Bs.append(w)
        return Bs, mu
    Bs, mu = gso()
    k = 1
    while k < n:
        for j in range(k - 1, -1, -1):
            q = round(mu[k][j])
            if q:
                B[k] = [a - q * b for a, b in zip(B[k], B[j])]
                Bs, mu = gso()
        if dot(Bs[k], Bs[k]) >= (delta - mu[k][k - 1] ** 2) * dot(Bs[k - 1], Bs[k - 1]):
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            Bs, mu = gso()
            k = max(k - 1, 1)
    return [[int(x) for x in v] for v in B]

def conv(a, b, N, q):
    c = [0] * N
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            c[(i + j) % N] += ai * bj
    return [x % q for x in c]

N, q = 7, 41
h = [30, 26, 8, 38, 2, 40, 20]                     # 只有公鑰
H = [[h[(j - i) % N] for j in range(N)] for i in range(N)]
Mh = [[1 if j == i else 0 for j in range(N)] + H[i] for i in range(N)] + \
     [[0] * N + [q if j == i else 0 for j in range(N)] for i in range(N)]
for v in lll(Mh)[:3]:
    F_, G_ = v[:N], v[N:]
    ok = conv(F_, h, N, q) == [x % q for x in G_]
    print(F_, G_, ok)
```
```output
[-1, -1, -1, -1, -1, -1, -1] [0, 0, 0, 0, 0, 0, 0] True
[1, 0, -1, 1, 0, -1, -1] [-1, 0, -1, 0, 1, 1, 0] True
[-1, 1, 0, -1, -1, 1, 0] [-1, 0, 1, 1, 0, -1, 0] True
```
三個短向量都滿足 `F ⋆ h ≡ G (mod q)`。第一個 `(−1, …, −1, 0, …, 0)` 是一個「平凡」的短向量：因為 `g ∈ T(d, d)` 的係數和是 0，`h(1) ≡ 0 (mod q)`，所以全 1 的向量乘上 h 會得到 0——但它在 R_p 中不可逆，不能拿來解密。後面兩個正是私鑰 f 的 **旋轉**（`±x^k ⋆ f`），都能拿來解密（Remark 6.54）。真實的 NTRU 用 N ≈ 500～800，格的維度 1000 以上，LLL 和 BKZ 都找不到。

## 4.4 GGH

GGH 原始論文建議的參數維度到 400 左右。Nguyen（1999）利用密文中擾動 r 的特殊形式，把問題化成維度較低、間隙較大的 CVP，用 LLL / BKZ 在建議的參數下全部破解。這說明格密碼的 **參數選擇** 和 **結構細節** 和底層問題同樣重要。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 格基約化 | Lattice Reduction | 把基底變得又短又正交 | 1.1 |
| Gauss 格基約化 | Gaussian Lattice Reduction | 二維時找出最短向量 | 1.1 |
| LLL 演算法 | LLL Algorithm | 任意維度的多項式時間約化 | 2.3 |
| 大小條件 / Lovász 條件 | Size / Lovász Condition | LLL 約化基底的兩個條件 | 2.1 |
| 近似因子 | Approximation Factor | 找到的向量最多是最短的幾倍 | 2.2 |
| BKZ | Block Korkin–Zolotarev | 區塊內精確解 SVP 的強化版 | 3.2 |
| 背包密度 | Knapsack Density | n / log₂ max Mᵢ，低密度易被格破解 | 4.2 |

---

# 習題

### 題 1：Gauss 約化

約化基底 `(31, 59)`、`(37, 70)`，求最短向量。

### 題 2：大小條件

基底 `(1, 0)`、`(7, 1)` 滿足大小條件嗎？約化後是什麼？

### 題 3：同餘密碼

q = 918293817、h = 767748560（第 21 課題 1 的公鑰）。用 Gauss 約化找出私鑰 (f, g)。

### 題 4：觀念

LLL 只保證近似因子 2^((n−1)/2)，為什麼格密碼要用很高的維度（幾百以上）？

---

# 習題解答

**題 1**：

```python
def gauss_reduce(v1, v2):
    dot = lambda a, b: a[0] * b[0] + a[1] * b[1]
    while True:
        if dot(v2, v2) < dot(v1, v1):
            v1, v2 = v2, v1
        num, den = dot(v1, v2), dot(v1, v1)
        m = (2 * num + den) // (2 * den)
        if m == 0:
            return v1, v2
        v2 = (v2[0] - m * v1[0], v2[1] - m * v1[1])

print(gauss_reduce((31, 59), (37, 70)))
print(abs(31 * 70 - 59 * 37))
```
```output
((3, -1), (1, 4))
13
```
行列式的絕對值是 13，最短向量是 ±(3, −1)，長度 √10；另一個約化後的基底向量是 (1, 4)。檢查：`3·4 − (−1)·1 = 13`，行列式不變。

**題 2**：`μ = (7, 1)·(1, 0) / 1 = 7`，`|μ| > 1/2`，不滿足。扣掉 7 倍：`(7, 1) − 7(1, 0) = (0, 1)`。

**題 3**：

```python
def gauss_reduce(v1, v2):
    dot = lambda a, b: a[0] * b[0] + a[1] * b[1]
    while True:
        if dot(v2, v2) < dot(v1, v1):
            v1, v2 = v2, v1
        num, den = dot(v1, v2), dot(v1, v1)
        m = (2 * num + den) // (2 * den)
        if m == 0:
            return v1, v2
        v2 = (v2[0] - m * v1[0], v2[1] - m * v1[1])

q, h = 918293817, 767748560
print(gauss_reduce((1, h), (0, q)))
```
```output
((19928, 18643), (-14243, 32756))
```
最短向量就是 ±(19928, 18643)，也就是私鑰 (f, g)。

**題 4**：近似因子 `2^((n−1)/2)` 是 **最壞情況的保證**，實際上 LLL 在低維度常常直接找到最短向量；只有在高維度時，LLL（甚至 BKZ）找到的向量才會明顯長於秘密向量。格密碼的安全性就是要讓維度高到：要找到私鑰那麼短的向量，BKZ 需要的區塊大小 β 太大、計算量超過 2¹²⁸ 之類的門檻。
