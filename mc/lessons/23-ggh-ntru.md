# 23. GGH 與 NTRU：建立在格上的密碼系統

> 對應課本：§6.7～§6.11
>
> 程式練習：`MC15 NTRU 加解密`
>
> 先備知識：第 09 課（多項式環、擴展歐幾里得）、第 21 課（同餘密碼）、第 22 課（Babai 演算法）。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 格密碼的動機 | 為什麼要建立在 SVP / CVP 上：速度、量子電腦 |
| 第二部分 | GGH 密碼系統 | 好基底當私鑰、壞基底當公鑰、Babai 解密；課本例 6.36 |
| 第三部分 | 卷積多項式環 | `Z[x]/(x^N − 1)`、卷積乘法、中心提升、求反元素 |
| 第四部分 | NTRU 密碼系統 | 金鑰、加密、解密、為什麼解密會成功；課本例 6.53 |
| 第五部分 | NTRU 作為格密碼 | NTRU 格、私鑰是格中的短向量、安全參數 |

---

# 第一部分：格密碼的動機

1990 年代中期出現了幾個以 **格中的 SVP / CVP** 為基礎的密碼系統：Ajtai–Dwork、**GGH**（Goldreich–Goldwasser–Halevi）、**NTRU**（Hoffstein–Pipher–Silverman，也就是本書三位作者）。

| 優點 | 說明 |
|---|---|
| **速度** | 加解密只需要加法和小整數的乘法，O(N²) 甚至 O(N log N)，比 RSA、ECC 快很多 |
| **抗量子** | Shor 演算法能在量子電腦上有效分解整數、解離散對數（RSA、DH、ECC 全滅）；但目前 **沒有** 已知能有效解 SVP / CVP 的量子演算法 |
| **最壞情況到平均情況的歸約** | Ajtai 證明某些格問題的 **平均** 難度等價於 **最壞** 難度——這是其他密碼難題沒有的保證（第 17 課說過密碼需要平均情況的困難） |

2024 年 NIST 公布的後量子密碼標準 **ML-KEM（Kyber）**、**ML-DSA（Dilithium）** 都建立在格上，NTRU 也是重要的候選之一。

---

# 第二部分：GGH 密碼系統

## 2.1 系統

| | 做什麼 |
|---|---|
| **Alice 建金鑰** | 選一組 **好基底**（近乎正交）v₁, …, vₙ 當私鑰 V；選一個行列式 ±1 的整數矩陣 U，算 **壞基底** `W = UV` 當公鑰 |
| **Bob 加密** | 明文是一個小整數向量 m；選小的隨機擾動 r；送 `e = mW + r`（一個格點加一點雜訊） |
| **Alice 解密** | 用 **好基底** 跑 Babai 演算法找到離 e 最近的格點 v（= mW）；再算 `m = vW⁻¹` |

Eve 只有壞基底，Babai 演算法失效（第 22 課）。

## 2.2 課本例 6.36

```python
from fractions import Fraction as F

def solve(B, e):                      # 解 e = t·B（B 是 3×3，列向量是基底）
    n = len(B)
    A = [[F(B[j][i]) for j in range(n)] + [F(e[i])] for i in range(n)]   # 轉置後的增廣矩陣
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        A[c] = [x / A[c][c] for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                A[r] = [x - A[r][c] * y for x, y in zip(A[r], A[c])]
    return [A[i][n] for i in range(n)]

def combo(coeffs, B):
    return [sum(c * B[i][k] for i, c in enumerate(coeffs)) for k in range(len(B[0]))]

V = [[-97, 19, 19], [-36, 30, 86], [-184, -64, 78]]                 # 私鑰：好基底
U = [[4327, -15447, 23454], [3297, -11770, 17871], [5464, -19506, 29617]]
W = [combo(U[i], V) for i in range(3)]                              # 公鑰：壞基底
print(W)

m, r = [86, -35, -32], [-4, -3, 2]
e = [a + b for a, b in zip(combo(m, W), r)]
print("密文", e)

t = solve(V, e)                                                     # Alice 用好基底
v = combo([round(x) for x in t], V)
print([float(round(x, 2)) for x in t], v)
print("Alice 解出", [int(x) for x in solve(W, v)])

t2 = solve(W, e)                                                    # Eve 只有壞基底
v2 = combo([round(x) for x in t2], W)
print([float(round(x, 2)) for x in t2], "Eve 解出", [int(x) for x in solve(W, v2)])
```
```output
[[-4179163, -1882253, 583183], [-3184353, -1434201, 444361], [-5277320, -2376852, 736426]]
密文 [-79081427, -35617462, 11035473]
[81878.97, -292300.0, 443815.04] [-79081423, -35617459, 11035471]
Alice 解出 [86, -35, -32]
[75.76, -34.52, -24.18] Eve 解出 [76, -35, -24]
```
Alice 用好基底，四捨五入後得到正確的格點，解出 m = (86, −35, −32)；Eve 用壞基底，得到錯誤的 (76, −35, −24)（和課本一致）。

## 2.3 GGH 的問題

- **公鑰太大**：n × n 的矩陣，n 要好幾百維才安全，公鑰動輒幾百 KB 到 MB。
- **被破解**：Nguyen（1999）發現 GGH 的密文結構洩漏資訊（擾動 r 的分量是 ±σ），把問題降成較容易的 CVP，在建議的參數下破解。
- **機率式加密的陷阱**（Remark 6.37）：同一個 m 用兩個 r 加密、或兩個 m 用同一個 r 加密，都會洩漏資訊——實務上 r 由 m 的雜湊產生。

NTRU 用 **特殊結構的格**（循環結構）解決了公鑰太大的問題。

---

# 第三部分：卷積多項式環

## 3.1 定義

```
R = Z[x] / (x^N − 1)，  R_q = (Z/qZ)[x] / (x^N − 1)
```

每個元素都能寫成 `a₀ + a₁x + ⋯ + a_{N−1}x^(N−1)`，也就是一個長度 N 的向量。因為 `x^N = 1`，乘法時次方 **繞圈**：

**命題 6.39（卷積）**：`(a ⋆ b)_k = Σ_{i + j ≡ k (mod N)} aᵢ bⱼ`

課本例 6.40：N = 5，`a = 1 − 2x + 4x³ − x⁴`、`b = 3 + 4x − 2x² + 5x³ + 2x⁴`。

```python
def conv(a, b, N, q=None):
    c = [0] * N
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            c[(i + j) % N] += ai * bj
    return [x % q for x in c] if q else c

a = [1, -2, 0, 4, -1]
b = [3, 4, -2, 5, 2]
print(conv(a, b, 5), conv(a, b, 5, 11))
```
```output
[-13, 20, -7, 19, 5] [9, 9, 4, 8, 5]
```
## 3.2 中心提升

從 R_q 回到 R 時，把每個係數取在 **−q/2 < aᵢ ≤ q/2**，叫 **中心提升**（centered lift）。注意：提升 **不保持** 乘法——「提升後再乘」和「乘了再提升」一般不同（只是模 q 同餘）。NTRU 解密正是要小心這一點。

```python
def lift(a, q):
    return [x - q if x > q // 2 else x for x in (y % q for y in a)]

print(lift([5, 3, -6, 2, 4], 7))            # 課本例 6.43
```
```output
[-2, 3, 1, 2, -3]
```
## 3.3 求反元素

**命題 6.45**：q 是質數時，`a(x)` 在 R_q 中可逆 ⟺ `gcd(a(x), x^N − 1) = 1`（在 F_q[x] 中），反元素用擴展歐幾里得算（第 09 課）。

```python
def trim(a):
    while a and a[-1] == 0:
        a = a[:-1]
    return a

def pdivmod(a, b, p):
    a, b = trim([x % p for x in a]), trim([x % p for x in b])
    q = [0] * max(len(a) - len(b) + 1, 1)
    inv = pow(b[-1], -1, p)
    r = a[:]
    while r and len(r) >= len(b):
        s, c = len(r) - len(b), r[-1] * inv % p
        q[s] = c
        for i, bc in enumerate(b):
            r[i + s] = (r[i + s] - c * bc) % p
        r = trim(r)
    return trim(q), r

def pmul(a, b, p):
    if not a or not b:
        return []
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] = (c[i + j] + x * y) % p
    return trim(c)

def psub(a, b, p):
    n = max(len(a), len(b))
    return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p for i in range(n)])

def inverse_mod(a, N, p):                     # a(x)⁻¹ 在 (Z/pZ)[x]/(x^N − 1)，p 是質數
    m = [-1] + [0] * (N - 1) + [1]            # x^N − 1
    r0, r1 = trim([x % p for x in m]), trim([x % p for x in a])
    s0, s1 = [], [1]                          # 只追蹤 a 的係數
    while r1:
        q, r = pdivmod(r0, r1, p)
        r0, r1 = r1, r
        s0, s1 = s1, psub(s0, pmul(q, s1, p), p)
    if len(r0) != 1:
        return None                           # gcd 不是常數：不可逆
    c = pow(r0[0], -1, p)
    s = [x * c % p for x in s0]
    return s + [0] * (N - len(s))

print(inverse_mod([1, 1, 0, 0, 1], 5, 2))     # 課本例 6.46：(1 + x + x⁴)⁻¹ = 1 + x² + x³
```
```output
[1, 0, 1, 1, 0]
```
---

# 第四部分：NTRU 密碼系統

## 4.1 系統（課本表 6.4）

公開參數 (N, p, q, d)：N、p 是質數，`gcd(p, q) = gcd(N, q) = 1`，`q > (6d + 1)p`。`T(d₁, d₂)` 表示「有 d₁ 個 +1、d₂ 個 −1、其餘為 0」的 **三元多項式**。

| | 做什麼 |
|---|---|
| **Alice 建金鑰** | 私鑰 `f ∈ T(d + 1, d)`（要在 R_q、R_p 都可逆）、`g ∈ T(d, d)`；算 `F_q = f⁻¹ (mod q)`、`F_p = f⁻¹ (mod p)`；**公鑰 `h = F_q ⋆ g (mod q)`** |
| **Bob 加密** | 明文 m 的係數在 −p/2 到 p/2 之間；隨機 `r ∈ T(d, d)`；送 `e ≡ p · h ⋆ r + m (mod q)` |
| **Alice 解密** | `a ≡ f ⋆ e (mod q)`，**中心提升** 到 R；再算 `b ≡ F_p ⋆ a (mod p)`，中心提升後就是 m |

## 4.2 為什麼解密會成功（命題 6.48）

```
a ≡ f ⋆ (p h ⋆ r + m) = p f ⋆ F_q ⋆ g ⋆ r + f ⋆ m ≡ p g ⋆ r + f ⋆ m (mod q)
```

f、g、r、m 的係數都很小，所以 `p g ⋆ r + f ⋆ m` 的每個係數絕對值最多約 `(6d + 1)p/2 < q/2`——中心提升後 **a 就等於整數多項式** `p g ⋆ r + f ⋆ m`，不只是同餘。（又是第 21 課「小 → 沒有繞圈」的技巧！）然後模 p：

```
F_p ⋆ a ≡ F_p ⋆ (p g ⋆ r + f ⋆ m) ≡ F_p ⋆ f ⋆ m ≡ m (mod p)
```

## 4.3 課本例 6.53：(N, p, q, d) = (7, 3, 41, 2)

```python
def trim(a):
    while a and a[-1] == 0:
        a = a[:-1]
    return a

def pdivmod(a, b, p):
    a, b = trim([x % p for x in a]), trim([x % p for x in b])
    q = [0] * max(len(a) - len(b) + 1, 1)
    inv = pow(b[-1], -1, p)
    r = a[:]
    while r and len(r) >= len(b):
        s, c = len(r) - len(b), r[-1] * inv % p
        q[s] = c
        for i, bc in enumerate(b):
            r[i + s] = (r[i + s] - c * bc) % p
        r = trim(r)
    return trim(q), r

def pmul(a, b, p):
    if not a or not b:
        return []
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] = (c[i + j] + x * y) % p
    return trim(c)

def psub(a, b, p):
    n = max(len(a), len(b))
    return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p for i in range(n)])

def inverse_mod(a, N, p):
    m = [-1] + [0] * (N - 1) + [1]
    r0, r1 = trim([x % p for x in m]), trim([x % p for x in a])
    s0, s1 = [], [1]
    while r1:
        q, r = pdivmod(r0, r1, p)
        r0, r1 = r1, r
        s0, s1 = s1, psub(s0, pmul(q, s1, p), p)
    if len(r0) != 1:
        return None
    c = pow(r0[0], -1, p)
    s = [x * c % p for x in s0]
    return s + [0] * (N - len(s))

def conv(a, b, N, q):
    c = [0] * N
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            c[(i + j) % N] += ai * bj
    return [x % q for x in c]

def lift(a, q):
    return [x - q if x > q // 2 else x for x in (y % q for y in a)]

N, p, q, d = 7, 3, 41, 2
f = [-1, 0, 1, 1, -1, 0, 1]          # x⁶ − x⁴ + x³ + x² − 1   ∈ T(3, 2)
g = [0, -1, -1, 0, 1, 0, 1]          # x⁶ + x⁴ − x² − x        ∈ T(2, 2)
Fq, Fp = inverse_mod(f, N, q), inverse_mod(f, N, p)
h = conv(Fq, g, N, q)
print("Fq =", Fq)
print("Fp =", Fp)
print("h  =", h)

m = [1, -1, 1, 1, 0, -1, 0]          # −x⁵ + x³ + x² − x + 1
r = [-1, 1, 0, 0, 0, -1, 1]          # x⁶ − x⁵ + x − 1
e = [(p * x + y) % q for x, y in zip(conv(h, r, N, q), m)]
print("e  =", e)

a = lift(conv(f, e, N, q), q)
print("a  =", a)
print("解密", lift(conv(Fp, a, N, p), p), "原文", m)
```
```output
Fq = [37, 2, 40, 21, 31, 26, 8]
Fp = [1, 1, 1, 1, 0, 2, 1]
h  = [30, 26, 8, 38, 2, 40, 20]
e  = [25, 3, 40, 2, 4, 19, 31]
a  = [-1, 1, -1, -1, -8, 10, 1]
解密 [1, -1, 1, 1, 0, -1, 0] 原文 [1, -1, 1, 1, 0, -1, 0]
```
係數由低次到高次排列。`F_q`、`h`、`e`、`a` 都和課本一致（課本由高次寫到低次），最後解出 Bob 的明文。

## 4.4 速度

NTRU 的運算都是卷積：`r ⋆ h`、`f ⋆ e`、`F_p ⋆ a`，其中 r、f 是三元多項式（係數 0、±1），所以 **不用乘法**，只要大約 `2N²/3` 次加減。整個加解密是 O(N²)，用 FFT 還能更快。N = 509 時的安全度大約相當於 RSA 3072，但快上百倍。

---

# 第五部分：NTRU 作為格密碼

## 5.1 NTRU 格

給公鑰 h，用下面這個 2N × 2N 矩陣的列生成 **NTRU 格** `L_h`（每個區塊是 N × N）：

```
M_h = ( I   H  )        H 的第 i 列是 h 的係數循環右移 i 格
      ( 0   qI )
```

**命題 6.59**：如果 `f ⋆ h = g + q u`，則 `(f, −u) M_h = (f, g)`——**私鑰 (f, g) 是 NTRU 格中的一個向量**。

**為什麼它很特別**：`det L_h = q^N`，高斯啟發式預期的最短長度約 `√(2N/(2πe)) · √q`（隨 √q 成長）；但 (f, g) 的係數只有 0、±1，長度只有大約 `√(4d)`——**遠遠短於** 隨機格的最短向量。所以 (f, g)（以及它的循環旋轉 `x^k ⋆ f`）就是格中的最短向量，**找到最短向量 = 找到私鑰**（命題 6.61）。

```python
import math
N, q, d = 7, 41, 2
f = [-1, 0, 1, 1, -1, 0, 1]
g = [0, -1, -1, 0, 1, 0, 1]
h = [30, 26, 8, 38, 2, 40, 20]                 # 第 4.3 節的公鑰

H = [[h[(j - i) % N] for j in range(N)] for i in range(N)]
M = [[1 if j == i else 0 for j in range(N)] + H[i] for i in range(N)] + \
    [[0] * N + [q if j == i else 0 for j in range(N)] for i in range(N)]

fh = [sum(f[i] * h[(k - i) % N] for i in range(N)) for k in range(N)]
u = [(x - y) // q for x, y in zip(fh, g)]          # f ⋆ h = g + q·u
coef = f + [-x for x in u]
vec = [sum(coef[i] * M[i][k] for i in range(2 * N)) for k in range(2 * N)]
print(vec == f + g, vec)
print(round(math.sqrt(sum(x * x for x in f + g)), 3),
      round(math.sqrt(2 * N / (2 * math.pi * math.e)) * math.sqrt(q), 3))
```
```output
True [-1, 0, 1, 1, -1, 0, 1, 0, -1, -1, 0, 1, 0, 1]
3.0 5.797
```
私鑰向量長度是 3，而高斯預期的最短長度約 5.8——私鑰明顯比較短，所以它就是最短向量；而 N 這麼小，格只有 14 維，這個玩具例子很容易被格約化破解（第 24 課）。真實參數下 N 是幾百，差距大到能讓私鑰「顯得特別」，但格的維度 2N 太高，約化演算法找不到它。

## 5.2 安全參數

LLL 演算法（第 24 課）在多項式時間內能找到長度最多是最短向量 `2^(n/2)` 倍的向量；更強的 BKZ 演算法在高維時的時間隨維度指數成長。NTRU 的安全性就落在「**2N 維的格中，最短向量雖然特別短，但仍然找不到**」。

課本也提到：解密失敗（係數超過 q/2）可能洩漏私鑰資訊，所以要選讓失敗機率極小（例如 < 2⁻⁸⁰）的參數；而且臨時金鑰 r 應由明文的雜湊產生，避免重複使用。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 後量子密碼 | Post-Quantum Cryptography | 量子電腦也破不了的公鑰密碼 | 1 |
| GGH 密碼系統 | GGH Cryptosystem | 好基底私鑰、壞基底公鑰 | 2.1 |
| 卷積多項式環 | Convolution Polynomial Ring | `Z[x]/(x^N − 1)`，乘法會繞圈 | 3.1 |
| 中心提升 | Centered Lift | 係數取在 (−q/2, q/2] | 3.2 |
| 三元多項式 | Ternary Polynomial | 係數只有 0、±1 | 4.1 |
| NTRU 密碼系統 | NTRUEncrypt | `e = p h ⋆ r + m (mod q)` | 4.1 |
| NTRU 格 | NTRU Lattice | `(I H; 0 qI)` 生成的 2N 維格 | 5.1 |

---

# 習題

### 題 1：卷積

在 `Z[x]/(x³ − 1)` 中算 `(1 + 2x) ⋆ (3 + x + x²)`。

### 題 2：反元素

在 R₃（N = 5）中求 `1 − x + x³` 的反元素，並驗算。

### 題 3：NTRU

用第 4.3 節的金鑰，加密 `m = [0, 1, −1, 0, 1, 0, −1]`（隨機 r 用 `[1, 0, −1, 1, 0, −1, 0]`），再解密。

### 題 4：觀念

NTRU 解密為什麼要求 `q > (6d + 1)p`？如果 q 太小會怎樣？

### 題 5：觀念

GGH 和 NTRU 的「陷門」各是什麼？為什麼都和「找格中的短向量」有關？

---

# 習題解答

**題 1**：

```python
def conv(a, b, N):
    c = [0] * N
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            c[(i + j) % N] += ai * bj
    return c

print(conv([1, 2, 0], [3, 1, 1], 3))
```
```output
[5, 7, 3]
```
`(1 + 2x)(3 + x + x²) = 3 + 7x + 3x² + 2x³`，`x³ = 1`，所以是 `5 + 7x + 3x²`。

**題 2**：

```python
def trim(a):
    while a and a[-1] == 0:
        a = a[:-1]
    return a

def pdivmod(a, b, p):
    a, b = trim([x % p for x in a]), trim([x % p for x in b])
    q = [0] * max(len(a) - len(b) + 1, 1)
    inv = pow(b[-1], -1, p)
    r = a[:]
    while r and len(r) >= len(b):
        s, c = len(r) - len(b), r[-1] * inv % p
        q[s] = c
        for i, bc in enumerate(b):
            r[i + s] = (r[i + s] - c * bc) % p
        r = trim(r)
    return trim(q), r

def pmul(a, b, p):
    if not a or not b:
        return []
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] = (c[i + j] + x * y) % p
    return trim(c)

def psub(a, b, p):
    n = max(len(a), len(b))
    return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p for i in range(n)])

def inverse_mod(a, N, p):
    m = [-1] + [0] * (N - 1) + [1]
    r0, r1 = trim([x % p for x in m]), trim([x % p for x in a])
    s0, s1 = [], [1]
    while r1:
        q, r = pdivmod(r0, r1, p)
        r0, r1 = r1, r
        s0, s1 = s1, psub(s0, pmul(q, s1, p), p)
    if len(r0) != 1:
        return None
    c = pow(r0[0], -1, p)
    s = [x * c % p for x in s0]
    return s + [0] * (N - len(s))

def conv(a, b, N, q):
    c = [0] * N
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            c[(i + j) % N] += ai * bj
    return [x % q for x in c]

a = [1, -1, 0, 1, 0]
inv = inverse_mod(a, 5, 3)
print(inv, conv(a, inv, 5, 3))
```
```output
[2, 0, 1, 2, 2] [1, 0, 0, 0, 0]
```
**題 3**：

```python
def conv(a, b, N, q):
    c = [0] * N
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            c[(i + j) % N] += ai * bj
    return [x % q for x in c]

def lift(a, q):
    return [x - q if x > q // 2 else x for x in (y % q for y in a)]

N, p, q = 7, 3, 41
f = [-1, 0, 1, 1, -1, 0, 1]
Fp = [1, 1, 1, 1, 0, 2, 1]
h = [30, 26, 8, 38, 2, 40, 20]
m = [0, 1, -1, 0, 1, 0, -1]
r = [1, 0, -1, 1, 0, -1, 0]
e = [(p * x + y) % q for x, y in zip(conv(h, r, N, q), m)]
a = lift(conv(f, e, N, q), q)
print(e, lift(conv(Fp, a, N, p), p) == m)
```
```output
[34, 25, 28, 6, 1, 22, 7] True
```
**題 4**：解密時需要 `a = p g ⋆ r + f ⋆ m` 在整數上成立（中心提升後沒有繞圈），也就是每個係數的絕對值要小於 q/2。f、g、r 有約 2d 個非零係數、m 的係數不超過 p/2，最壞情況係數可以到 `(6d + 1)p/2`。q 太小時某些係數會超過 q/2、被模 q 繞圈，中心提升得到錯的整數，解密失敗——而解密失敗還可能洩漏私鑰資訊。

**題 5**：GGH 的陷門是 **好基底**（能用 Babai 解 CVP）；NTRU 的陷門是 **短的 (f, g)**，它正是 NTRU 格中的最短向量。兩者的安全性都建立在「沒有陷門時，在高維格中找短向量 / 近向量很難」。
