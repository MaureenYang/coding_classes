# 20. 雙線性配對及其應用（Bilinear Pairings）

> 對應課本：§5.8～§5.10
>
> 先備知識：第 09 課（F_{p²}）、第 18 課（橢圓曲線）、第 19 課（ECDH）。
>
> 這一課是整本書數學上最深的一節之一。證明大多超出課本範圍，重點放在 **配對有什麼性質、能拿來做什麼**——它既能 **攻擊**（MOV），也能 **建構** 以前做不到的系統（三方金鑰交換、身分式加密）。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 有限階的點與除子 | E[m] ≅ Z/m × Z/m、有理函數的零點與極點、除子 |
| 第二部分 | Weil 配對 | 定義、三個性質（m 次單位根、雙線性、交錯）、和行列式的關係 |
| 第三部分 | Miller 演算法 | 用倍加法算出需要的函數值；課本例 5.43 |
| 第四部分 | 嵌入度與 MOV 攻擊 | 把 ECDLP 搬到 F_{p^k}* 的 DLP；超奇異曲線、異常曲線 |
| 第五部分 | 配對的正面應用 | 扭曲映射與修正 Weil 配對、Joux 三方 Diffie–Hellman、Boneh–Franklin 身分式加密 |

---

# 第一部分：有限階的點與除子

## 1.1 E[m]

**定義**：`mP = O` 的點叫 **m-扭點**（torsion point），全體記作 `E[m]`。它是 E 的子群。

**命題 5.33**：
- 在複數上，`E(C)[m] ≅ Z/mZ × Z/mZ`。
- 在 F_p 上（p ∤ m），**只要把體擴大到某個 F_{p^k}**，就有 `E(F_{p^k})[m] ≅ Z/mZ × Z/mZ`。

所以 E[m] 就像一個 **二維的向量空間**（m 是質數 ℓ 時真的是 F_ℓ 上的二維向量空間），可以選一組基底 `{P₁, P₂}`，每個點都寫成 `aP₁ + bP₂`。

## 1.2 有理函數與除子

曲線上的 **有理函數** f(x, y)（多項式的比）有零點和極點。用 **除子**（divisor）記錄它們：

```
div(f) = Σ n_P [P]，  n_P = 零點的重數（正）或極點的重數（負）
```

例：曲線 `Y² = (X − α₁)(X − α₂)(X − α₃)` 上，函數 Y 在三個 2 階點 `Pᵢ = (αᵢ, 0)` 為零，在 O 有三重極點：`div(Y) = [P₁] + [P₂] + [P₃] − 3[O]`。

**定理 5.36**：一個除子 `D = Σ n_P[P]` 是某個有理函數的除子 ⟺
1. **次數為 0**：`Σ n_P = 0`；
2. **和為 O**：`Σ n_P P = O`（用曲線的加法）。

例：P 是 m 階點時，`m[P] − m[O]` 滿足兩個條件，所以存在函數 `f_P` 使 `div(f_P) = m[P] − m[O]`。

---

# 第二部分：Weil 配對

## 2.1 定義

P、Q ∈ E[m]，取 `div(f_P) = m[P] − m[O]`、`div(f_Q) = m[Q] − m[O]`，再取一個輔助點 S（不在 {O, P, −Q, P − Q} 中）：

```
e_m(P, Q) = [ f_P(Q + S) / f_P(S) ] ÷ [ f_Q(P − S) / f_Q(−S) ]
```

結果和 S 的選法無關。

## 2.2 性質（定理 5.38）

| 性質 | 內容 |
|---|---|
| **m 次單位根** | `e_m(P, Q)^m = 1` |
| **雙線性** | `e_m(P₁ + P₂, Q) = e_m(P₁, Q) · e_m(P₂, Q)`，第二個位置也一樣 |
| **交錯** | `e_m(P, P) = 1`，所以 `e_m(Q, P) = e_m(P, Q)⁻¹` |
| **非退化** | 如果 `e_m(P, Q) = 1` 對所有 Q 都成立，則 P = O |

**直觀**（Remark 5.39）：E[m] 是二維空間，而二維空間上天生就有一個交錯雙線性函數——**行列式**。如果 `P = aP₁ + bP₂`、`Q = cP₁ + dP₂`，那麼

```
e_m(P, Q) = e_m(P₁, P₂)^(ad − bc)
```

**雙線性帶來的關鍵公式**：`e_m(aP, bQ) = e_m(P, Q)^(ab)`。

---

# 第三部分：Miller 演算法

## 3.1 想法

直接找 `f_P` 很難（它的次數大約是 m）。Miller 的想法：用 **倍加法** 一邊算 `T = 2T` 或 `T + P`，一邊把對應的「直線除以垂直線」函數乘起來，最後就得到 `f_P` 在指定點的 **值**，不必寫出整個函數。

**定理 5.41**：
- 令 λ 是過 P、Q 的直線斜率（或切線斜率），定義 `g_{P,Q} = (y − y_P − λ(x − x_P)) / (x + x_P + x_Q − λ²)`（垂直線時 `g = x − x_P`），則 `div(g_{P,Q}) = [P] + [Q] − [P + Q] − [O]`。
- **Miller 演算法**（m 的二進位 `m_{n−1} … m₀`）：

```
T ← P，f ← 1
for i = n − 2 down to 0:
    f ← f² · g_{T,T}，T ← 2T
    if m_i = 1: f ← f · g_{T,P}，T ← T + P
回傳 f        （div(f) = m[P] − [mP] − (m−1)[O]，P ∈ E[m] 時就是 f_P）
```

## 3.2 實作

下面的程式把 F_p 和 F_{p²} 一起處理：元素寫成 `a + bi`（`i² = −1`，需要 p ≡ 3 (mod 4)）；只用到 F_p 時 b 都是 0。

```python
class F2:
    """F_{p²} = F_p[i]/(i² + 1) 的元素 a + bi。"""
    p = 631
    def __init__(self, a, b=0):
        self.a, self.b = a % F2.p, b % F2.p
    def __add__(s, o): return F2(s.a + o.a, s.b + o.b)
    def __sub__(s, o): return F2(s.a - o.a, s.b - o.b)
    def __neg__(s): return F2(-s.a, -s.b)
    def __mul__(s, o): return F2(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)
    def inv(s):
        n = pow(s.a * s.a + s.b * s.b, -1, F2.p)        # 1/(a+bi) = (a−bi)/(a²+b²)
        return F2(s.a * n, -s.b * n)
    def __truediv__(s, o): return s * o.inv()
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __pow__(s, e):
        r, x = F2(1), s
        while e:
            if e & 1:
                r = r * x
            x, e = x * x, e >> 1
        return r
    def __repr__(s): return f"{s.a}" if s.b == 0 else f"{s.a}+{s.b}i"

A = F2(30)                                   # E : y² = x³ + 30x + 34 over F₆₃₁（課本例 5.43）

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and y1 == -y2: return None
    lam = (F2(3) * x1 * x1 + A) / (F2(2) * y1) if P == Q else (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)

def neg(P): return (P[0], -P[1])

def mul(n, P):
    R = None
    while n:
        if n & 1: R = add(R, P)
        P, n = add(P, P), n >> 1
    return R

def g(P, Q, R):                              # g_{P,Q} 在點 R 的值
    (xP, yP), (xQ, yQ), (x, y) = P, Q, R
    if xP == xQ and yP == -yQ:
        return x - xP
    lam = (F2(3) * xP * xP + A) / (F2(2) * yP) if P == Q else (yQ - yP) / (xQ - xP)
    return (y - yP - lam * (x - xP)) / (x + xP + xQ - lam * lam)

def miller(P, R, m):                         # 回傳 f_P(R)，div(f_P) = m[P] − m[O]
    T, f = P, F2(1)
    for bit in bin(m)[3:]:
        f = f * f * g(T, T, R)
        T = add(T, T)
        if bit == "1":
            f = f * g(T, P, R)
            T = add(T, P)
    return f

def weil(P, Q, m, S):
    return (miller(P, add(Q, S), m) / miller(P, S, m)) / (miller(Q, add(P, neg(S)), m) / miller(Q, neg(S), m))

pt = lambda x, y: (F2(x), F2(y))
P, Q, S = pt(36, 60), pt(121, 387), pt(0, 36)
print(miller(P, add(Q, S), 5) / miller(P, S, 5), miller(Q, add(P, neg(S)), 5) / miller(Q, neg(S), 5))
e = weil(P, Q, 5, S)
print("e5(P, Q) =", e, " e^5 =", e ** 5)
P2, Q2 = mul(3, P), mul(4, Q)
print(P2, Q2, weil(P2, Q2, 5, S), e ** 12)        # 雙線性：e(3P, 4Q) = e(P, Q)^12
print(weil(P, P, 5, S), weil(Q, P, 5, S) * e)       # 交錯：e(P, P) = 1，e(Q, P) = e(P, Q)⁻¹
```
```output
473 88
e5(P, Q) = 242  e^5 = 1
(617, 5) (121, 244) 512 512
1 1
```
和課本例 5.43 完全一樣：兩個比值是 473 和 88，`e₅(P, Q) = 242`；`(3P, 4Q) = ((617, 5), (121, 244))`，配對值 512 = 242¹²。

> 🔍 **Tate 配對**（§5.8.5）是另一種常用的配對，只要算一次 Miller 迴圈再做一次乘方，比 Weil 配對快，實務上（例如區塊鏈用的 BLS 簽章）多半用 Tate 或它的改良版（ate 配對）。

---

# 第四部分：嵌入度與 MOV 攻擊

## 4.1 嵌入度

E[ℓ] 的點不一定都在 E(F_p) 裡。**嵌入度**（embedding degree）k 是讓 `E(F_{p^k})[ℓ] ≅ Z/ℓ × Z/ℓ` 的最小 k。

**命題 5.45**：ℓ 是 E(F_p) 點數的大質因數時（且不是特殊情況），**嵌入度是使 `p^k ≡ 1 (mod ℓ)` 的最小 k**——也就是 p 在 (Z/ℓZ)* 中的階。

對 **隨機的曲線**，k 通常大得驚人（和 ℓ 差不多大），完全不能用。但有些特殊曲線 k 很小。

## 4.2 MOV 攻擊

Menezes、Okamoto、Vanstone（1993）：要解 ECDLP `Q = jP`（P 的階是 ℓ），
1. 找一個點 T ∈ E(F_{p^k})[ℓ]，和 P 獨立。
2. 算 `α = e_ℓ(P, T)`、`β = e_ℓ(Q, T)`，都在 F_{p^k}* 中。
3. 由雙線性 `β = e_ℓ(jP, T) = α^j`，**在 F_{p^k}* 中解 DLP** 就得到 j。

ECDLP 被「搬」到有限體的 DLP，而後者有 **次指數** 的演算法（第 13 課）。

**超奇異曲線**（#E(F_p) = p + 1）的嵌入度最多 6，通常是 2——這類曲線的 ECDLP 只和 F_{p²}* 的 DLP 一樣難，必須用夠大的 p，或乾脆避開。另外，**異常曲線**（#E(F_p) = p）有線性時間的攻擊（Remark 5.48），也必須避開。

```python
def embedding_degree(p, l, kmax=10**6):
    x = p % l
    for k in range(1, kmax):
        if x == 1:
            return k
        x = x * p % l
    return None

# 課本例 5.54：y² = x³ + x over F₅₄₇（超奇異），#E = 548 = 4 · 137
print(embedding_degree(547, 137))
# 一條隨機曲線：y² = x³ + 2x + 3 over F₁₀₀₀₀₇，點數 = ?
p = 100007
sq = {}
for y in range(p):
    sq[y * y % p] = sq.get(y * y % p, 0) + 1
n = 1 + sum(sq.get((x ** 3 + 2 * x + 3) % p, 0) for x in range(p))
f, m, d = [], n, 2
while d * d <= m:
    while m % d == 0:
        f.append(d)
        m //= d
    d += 1
if m > 1:
    f.append(m)
l = max(f)
print(n, f, l, embedding_degree(p, l))
```
```output
2
104842 [2, 19, 31, 89] 89 88
```
超奇異曲線的嵌入度是 2；隨機曲線的嵌入度和 ℓ 同樣量級——在 F_{p^k} 中解 DLP 比直接解 ECDLP 還難得多。

## 4.3 實際做一次 MOV（課本例 5.54～5.55 的方法）

```python
class F2:
    p = 547
    def __init__(self, a, b=0):
        self.a, self.b = a % F2.p, b % F2.p
    def __add__(s, o): return F2(s.a + o.a, s.b + o.b)
    def __sub__(s, o): return F2(s.a - o.a, s.b - o.b)
    def __neg__(s): return F2(-s.a, -s.b)
    def __mul__(s, o): return F2(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)
    def inv(s):
        n = pow(s.a * s.a + s.b * s.b, -1, F2.p)
        return F2(s.a * n, -s.b * n)
    def __truediv__(s, o): return s * o.inv()
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __hash__(s): return hash((s.a, s.b))
    def __pow__(s, e):
        r, x = F2(1), s
        while e:
            if e & 1: r = r * x
            x, e = x * x, e >> 1
        return r
    def __repr__(s): return f"{s.a}" if s.b == 0 else f"{s.a}+{s.b}i"

A = F2(1)                                       # E : y² = x³ + x

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and y1 == -y2: return None
    lam = (F2(3) * x1 * x1 + A) / (F2(2) * y1) if P == Q else (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)

def neg(P): return (P[0], -P[1])

def mul(n, P):
    R = None
    while n:
        if n & 1: R = add(R, P)
        P, n = add(P, P), n >> 1
    return R

def g(P, Q, R):
    (xP, yP), (xQ, yQ), (x, y) = P, Q, R
    if xP == xQ and yP == -yQ:
        return x - xP
    lam = (F2(3) * xP * xP + A) / (F2(2) * yP) if P == Q else (yQ - yP) / (xQ - xP)
    return (y - yP - lam * (x - xP)) / (x + xP + xQ - lam * lam)

def miller(P, R, m):
    T, f = P, F2(1)
    for bit in bin(m)[3:]:
        f = f * f * g(T, T, R)
        T = add(T, T)
        if bit == "1":
            f = f * g(T, P, R)
            T = add(T, P)
    return f

def weil(P, Q, m, S):
    return (miller(P, add(Q, S), m) / miller(P, S, m)) / (miller(Q, add(P, neg(S)), m) / miller(Q, neg(S), m))

phi = lambda P: (-P[0], F2(0, 1) * P[1])        # 扭曲映射 (x, y) ↦ (−x, iy)
pt = lambda x, y: (F2(x), F2(y))
l = 137
P = mul(4, pt(2, 253))
Q = pt(167, 405)
S = pt(2, 253)                                  # 輔助點（階 548，不在會出問題的集合裡）
print("P =", P, " 137P =", mul(l, P))
alpha = weil(P, phi(P), l, S)                   # 修正 Weil 配對 ê(P, P) = e(P, φ(P))
beta = weil(Q, phi(P), l, S)                    # ê(Q, P) = α^j
print(alpha, alpha ** l, beta)
j = next(j for j in range(l) if alpha ** j == beta)   # F_{547²}* 中的 DLP（這裡直接暴力）
print("j =", j, mul(j, P) == Q)
```
```output
P = (67, 481)  137P = None
37+452i 1 530+455i
j = 83 True
```
我們沒有在曲線上解 ECDLP，而是在 F_{547²}* 中解了一個 DLP。

---

# 第五部分：配對的正面應用

## 5.1 扭曲映射與修正 Weil 配對

Weil 配對是交錯的：`e(aP, bP) = e(P, P)^(ab) = 1`。但應用時通常所有點都是同一個 P 的倍數，這樣配對永遠是 1，沒有用。

**扭曲映射**（distortion map）φ：把 P 映到一個「獨立」的點，而且 `φ(nP) = nφ(P)`。**修正 Weil 配對** `ê(Q, Q') = e(Q, φ(Q'))` 就滿足

```
ê(aP, bP) = ê(P, P)^(ab)，而且 ê(P, P) ≠ 1
```

**命題 5.51、5.52**：曲線 `y² = x³ + x`、p ≡ 3 (mod 4) 時，`φ(x, y) = (−x, iy)`（i² = −1，i ∈ F_{p²}）就是扭曲映射。上面的 MOV 例子就用了它。

## 5.2 Joux 三方 Diffie–Hellman（2000）

兩人用 ECDH 交換金鑰只要一輪。**三個人** 用一般的 Diffie–Hellman 需要兩輪。配對讓三人 **一輪** 就完成：

| | Alice | Bob | Carl |
|---|---|---|---|
| 秘密 | n_A | n_B | n_C |
| 公開 | `Q_A = n_A P` | `Q_B = n_B P` | `Q_C = n_C P` |
| 共同秘密 | `ê(Q_B, Q_C)^(n_A)` | `ê(Q_A, Q_C)^(n_B)` | `ê(Q_A, Q_B)^(n_C)` |

三個人都得到 `ê(P, P)^(n_A n_B n_C)`。

## 5.3 Boneh–Franklin 身分式加密（2001）

**問題**：公鑰密碼要先取得對方的公鑰（還要確認它是真的）。能不能 **直接拿對方的 email 當作公鑰**？這叫 **身分式加密**（ID-based encryption），Shamir 在 1984 年提出問題，直到 2001 年 Boneh 和 Franklin 才用配對做出來。

| 角色 | 做什麼 |
|---|---|
| **可信中心（PKG）** | 秘密主金鑰 s，公布 `P` 和 `P_pub = sP` |
| **Alice 取得私鑰** | 把身分 ID 雜湊成點 `Q_ID = H₁(ID)`；中心給她私鑰 `D_ID = s · Q_ID` |
| **Bob 加密 m 給 Alice** | 只需要 Alice 的 ID：選 r，送 `(rP, m ⊕ H₂(ê(Q_ID, P_pub)^r))` |
| **Alice 解密** | `ê(D_ID, rP) = ê(sQ_ID, rP) = ê(Q_ID, P)^(sr) = ê(Q_ID, P_pub)^r`，得到同一個遮罩 |

```python
import hashlib

class F2:
    p = 547
    def __init__(self, a, b=0):
        self.a, self.b = a % F2.p, b % F2.p
    def __add__(s, o): return F2(s.a + o.a, s.b + o.b)
    def __sub__(s, o): return F2(s.a - o.a, s.b - o.b)
    def __neg__(s): return F2(-s.a, -s.b)
    def __mul__(s, o): return F2(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)
    def inv(s):
        n = pow(s.a * s.a + s.b * s.b, -1, F2.p)
        return F2(s.a * n, -s.b * n)
    def __truediv__(s, o): return s * o.inv()
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __pow__(s, e):
        r, x = F2(1), s
        while e:
            if e & 1: r = r * x
            x, e = x * x, e >> 1
        return r
    def __repr__(s): return f"{s.a}" if s.b == 0 else f"{s.a}+{s.b}i"

A = F2(1)

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and y1 == -y2: return None
    lam = (F2(3) * x1 * x1 + A) / (F2(2) * y1) if P == Q else (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)

def neg(P): return (P[0], -P[1])

def mul(n, P):
    R = None
    while n:
        if n & 1: R = add(R, P)
        P, n = add(P, P), n >> 1
    return R

def g(P, Q, R):
    (xP, yP), (xQ, yQ), (x, y) = P, Q, R
    if xP == xQ and yP == -yQ:
        return x - xP
    lam = (F2(3) * xP * xP + A) / (F2(2) * yP) if P == Q else (yQ - yP) / (xQ - xP)
    return (y - yP - lam * (x - xP)) / (x + xP + xQ - lam * lam)

def miller(P, R, m):
    T, f = P, F2(1)
    for bit in bin(m)[3:]:
        f = f * f * g(T, T, R)
        T = add(T, T)
        if bit == "1":
            f = f * g(T, P, R)
            T = add(T, P)
    return f

l = 137
S = (F2(2), F2(253))
phi = lambda P: (-P[0], F2(0, 1) * P[1])

def pair(Q1, Q2):                                 # 修正 Weil 配對 ê(Q1, Q2)
    R = phi(Q2)
    return (miller(Q1, add(R, S), l) / miller(Q1, S, l)) / (miller(R, add(Q1, neg(S)), l) / miller(R, neg(S), l))

P = mul(4, (F2(2), F2(253)))

# Joux 三方 Diffie–Hellman
nA, nB, nC = 23, 71, 101
QA, QB, QC = mul(nA, P), mul(nB, P), mul(nC, P)
print(pair(QB, QC) ** nA, pair(QA, QC) ** nB, pair(QA, QB) ** nC)

# Boneh–Franklin（玩具版：H₁ 把 ID 雜湊成 P 的倍數，真實系統不能這樣做，見下方說明）
def H1(identity):
    return mul(int.from_bytes(hashlib.sha256(identity.encode()).digest(), "big") % (l - 1) + 1, P)

def H2(z):
    return hashlib.sha256(f"{z.a},{z.b}".encode()).digest()

s = 57                                            # 中心的主金鑰
Ppub = mul(s, P)
Q_alice = H1("alice@example.com")
D_alice = mul(s, Q_alice)                         # 中心交給 Alice 的私鑰

m = b"meet at noon"
r = 88
U = mul(r, P)
mask = H2(pair(Q_alice, Ppub) ** r)
V = bytes(a ^ b for a, b in zip(m, mask))         # Bob 只用了 Alice 的 email

mask2 = H2(pair(D_alice, U))
print(bytes(a ^ b for a, b in zip(V, mask2)))
```
```output
522+201i 522+201i 522+201i
b'meet at noon'
```
> ⚠️ 這裡的 H₁ 只是為了示範：把 ID 雜湊成「P 的某個倍數 kP」會洩漏 k，任何人都能算出 `D_ID = k · P_pub`。真正的 Boneh–Franklin 要用把字串 **直接映射成曲線上的點** 的雜湊（沒有人知道它是 P 的幾倍），而且參數要大到 ECDLP 和 F_{p²}* 的 DLP 都難解。

**身分式加密的代價**：可信中心知道所有人的私鑰（**金鑰託管**），必須完全信任它。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 扭點 | Torsion Point, E[m] | mP = O 的點 | 1.1 |
| 除子 | Divisor | 函數零點與極點的帳本 | 1.2 |
| Weil 配對 | Weil Pairing | E[m] × E[m] → m 次單位根的雙線性映射 | 2.1 |
| 雙線性 / 交錯 / 非退化 | Bilinear / Alternating / Nondegenerate | 配對的三個核心性質 | 2.2 |
| Miller 演算法 | Miller's Algorithm | 倍加法計算 f_P 的值 | 3.1 |
| Tate 配對 | Tate Pairing | 另一種較快的配對 | 3.2 |
| 嵌入度 | Embedding Degree | 使 `p^k ≡ 1 (mod ℓ)` 的最小 k | 4.1 |
| MOV 攻擊 | MOV Attack | 用配對把 ECDLP 轉成有限體 DLP | 4.2 |
| 超奇異 / 異常曲線 | Supersingular / Anomalous Curve | 點數 p + 1 / p 的弱曲線 | 4.2 |
| 扭曲映射 | Distortion Map | 把 P 映到獨立的點 | 5.1 |
| 三方 Diffie–Hellman | Tripartite Diffie–Hellman | 三人一輪的金鑰交換 | 5.2 |
| 身分式加密 | Identity-Based Encryption | 用身分字串當公鑰 | 5.3 |

---

# 習題

### 題 1：雙線性

用第 3.2 節的程式驗證 `e₅(2P, Q) = e₅(P, Q)²` 和 `e₅(P + Q, Q) = e₅(P, Q)`。後者為什麼成立？

### 題 2：嵌入度

對 p = 547、ℓ = 137，驗證 `547² ≡ 1 (mod 137)` 但 `547 ≢ 1`。

### 題 3：觀念

為什麼對大部分隨機的曲線，MOV 攻擊沒有威脅？

### 題 4：觀念

修正 Weil 配對為什麼需要扭曲映射？直接用 `e(aP, bP)` 會怎樣？

---

# 習題解答

**題 1**：`e(P + Q, Q) = e(P, Q) · e(Q, Q) = e(P, Q) · 1`（交錯性）。

```python
class F2:
    p = 631
    def __init__(self, a, b=0):
        self.a, self.b = a % F2.p, b % F2.p
    def __add__(s, o): return F2(s.a + o.a, s.b + o.b)
    def __sub__(s, o): return F2(s.a - o.a, s.b - o.b)
    def __neg__(s): return F2(-s.a, -s.b)
    def __mul__(s, o): return F2(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)
    def inv(s):
        n = pow(s.a * s.a + s.b * s.b, -1, F2.p)
        return F2(s.a * n, -s.b * n)
    def __truediv__(s, o): return s * o.inv()
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __pow__(s, e):
        r, x = F2(1), s
        while e:
            if e & 1: r = r * x
            x, e = x * x, e >> 1
        return r
    def __repr__(s): return f"{s.a}" if s.b == 0 else f"{s.a}+{s.b}i"

A = F2(30)

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and y1 == -y2: return None
    lam = (F2(3) * x1 * x1 + A) / (F2(2) * y1) if P == Q else (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)

def neg(P): return (P[0], -P[1])

def g(P, Q, R):
    (xP, yP), (xQ, yQ), (x, y) = P, Q, R
    if xP == xQ and yP == -yQ:
        return x - xP
    lam = (F2(3) * xP * xP + A) / (F2(2) * yP) if P == Q else (yQ - yP) / (xQ - xP)
    return (y - yP - lam * (x - xP)) / (x + xP + xQ - lam * lam)

def miller(P, R, m):
    T, f = P, F2(1)
    for bit in bin(m)[3:]:
        f = f * f * g(T, T, R)
        T = add(T, T)
        if bit == "1":
            f = f * g(T, P, R)
            T = add(T, P)
    return f

def weil(P, Q, m, S):
    return (miller(P, add(Q, S), m) / miller(P, S, m)) / (miller(Q, add(P, neg(S)), m) / miller(Q, neg(S), m))

P, Q, S = (F2(36), F2(60)), (F2(121), F2(387)), (F2(0), F2(36))
e = weil(P, Q, 5, S)
print(weil(add(P, P), Q, 5, S), e ** 2)
print(weil(add(P, Q), Q, 5, S), e)
```
```output
512 512
242 242
```
**題 2**：

```python
print(547 % 137, 547 ** 2 % 137)
```
```output
136 1
```
**題 3**：MOV 把 ECDLP 搬到 F_{p^k}* 的 DLP，k 是嵌入度。隨機曲線的 k 通常和 ℓ 差不多大（例如 10⁷⁵ 量級），F_{p^k} 大到連寫下一個元素都不可能，更別說解 DLP。只有 k 很小（例如超奇異曲線 k ≤ 6）時才有威脅。

**題 4**：所有點都是 P 的倍數時，`e(aP, bP) = e(P, P)^(ab) = 1^(ab) = 1`（交錯性），配對永遠是 1，什麼資訊都沒有。扭曲映射讓第二個位置變成「和 P 獨立」的 φ(P)，`ê(P, P) = e(P, φ(P))` 是一個本原的 ℓ 次單位根，雙線性才有用處。
