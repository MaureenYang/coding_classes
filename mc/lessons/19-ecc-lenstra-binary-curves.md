# 19. 橢圓曲線密碼、Lenstra 分解與二元體上的曲線（ECC, ECM, Curves over F_{2^k}）

> 對應課本：§5.4～§5.7
>
> 程式練習：`MC13 橢圓曲線運算`
>
> 先備知識：第 06 課（Diffie–Hellman、ElGamal）、第 12 課（Pollard p − 1）、第 18 課（橢圓曲線）。

**這一課分成四個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 橢圓曲線 Diffie–Hellman 與 ElGamal | ECDH、只傳 x 座標（點壓縮）、橢圓 ElGamal 與它的問題 |
| 第二部分 | 公鑰密碼的演進 | 1985 年 Koblitz 和 Miller 提出 ECC、它花多久被接受 |
| 第三部分 | Lenstra 橢圓曲線分解法 | 求反元素「失敗」反而找到因數、為什麼能換曲線 |
| 第四部分 | F₂ 與 F_{2^k} 上的曲線 | 廣義 Weierstrass 方程式、Frobenius 映射、Koblitz 曲線 |

---

# 第一部分：橢圓曲線 Diffie–Hellman 與 ElGamal

## 1.1 ECDH

把第 06 課的 Diffie–Hellman 中的「g 的次方」換成「P 的倍數」：

| | Alice | 公開 | Bob |
|---|---|---|---|
| 參數 | | 大質數 p、曲線 E、點 P ∈ E(F_p) | |
| 秘密 | n_A | | n_B |
| 公開值 | `Q_A = n_A P` | 交換 Q_A、Q_B | `Q_B = n_B P` |
| 共同秘密 | `n_A Q_B` | | `n_B Q_A` |

兩人都得到 `n_A n_B P`。Eve 要解的是 **橢圓曲線 Diffie–Hellman 問題**（ECDHP）：從 `n₁P`、`n₂P` 算出 `n₁n₂P`。

課本例 5.19：p = 3851，`E : Y² = X³ + 324X + 1287`，P = (920, 303)，n_A = 1194，n_B = 1759。

```python
p, A, B = 3851, 324, 1287

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

def mul(n, P):
    R = None
    while n:
        if n & 1:
            R = add(R, P)
        P = add(P, P)
        n >>= 1
    return R

P = (920, 303)
QA, QB = mul(1194, P), mul(1759, P)
print(QA, QB)
print(mul(1194, QB), mul(1759, QA))
```
```output
(2067, 2178) (3684, 3125)
(3347, 1242) (3347, 1242)
```
共同的點是 (3347, 1242)，習慣上只用它的 **x 座標** 3347 當作共同秘密。

## 1.2 只傳 x 座標（點壓縮）

y 座標幾乎不帶資訊：知道 x，由 `y² = x³ + Ax + B` 只剩兩個可能的 y（±）。所以 Alice 只傳 x，Bob 自己開根號。**p ≡ 3 (mod 4)** 時開根號只要一次快速冪 `b^((p+1)/4)`（第 08 課）。

Bob 開出的 y 可能是正確的、也可能是相反的，他算出的就是 `±n_A n_B P`——**x 座標相同**，所以不影響共同秘密。課本例 5.21：

```python
p, A, B = 3851, 324, 1287

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

def mul(n, P):
    R = None
    while n:
        if n & 1:
            R = add(R, P)
        P = add(P, P)
        n >>= 1
    return R

def lift_x(x):                        # 從 x 還原一個點（p ≡ 3 mod 4）
    rhs = (x ** 3 + A * x + B) % p
    y = pow(rhs, (p + 1) // 4, p)
    assert y * y % p == rhs
    return (x, y)

P = (920, 303)
xA, xB = mul(2489, P)[0], mul(2286, P)[0]           # 只傳 x
print(xA, xB)
alice = mul(2489, lift_x(xB))
bob = mul(2286, lift_x(xA))
print(alice, bob, alice[0] == bob[0])
```
```output
593 3681
(509, 1108) (509, 2743) True
```
Alice 和 Bob 得到的點 **互為相反**（y 不同），但 x 座標都是 509。

## 1.3 橢圓 ElGamal

Alice 公鑰 `Q_A = n_A P`；Bob 要加密 **點** M：選臨時金鑰 k，送 `C₁ = kP`、`C₂ = M + kQ_A`；Alice 算 `C₂ − n_A C₁ = M`。

**兩個實務問題**：
1. **明文要是曲線上的點**，但沒有明顯的方法把訊息對應到點。
2. **4 比 1 的訊息膨脹**：明文 M 只有約 p 種（一個點），密文卻是兩個點、四個數。

常見的解法是 **不把訊息放在點上**：用 ECDH 得到的共同秘密當作對稱密碼的金鑰（這就是現在實際使用的 ECIES 的想法），或用 `kQ_A` 的 x 座標當作遮罩乘上訊息（課本習題 5.16）。

---

# 第二部分：公鑰密碼的演進（§5.5）

| 年份 | 事件 |
|---|---|
| 1976～78 | Diffie–Hellman、RSA |
| 1984 | Lenstra 提出 **橢圓曲線分解法**（第三部分），讓數學家開始注意橢圓曲線的計算 |
| 1985 | **Koblitz 與 Miller 各自獨立提出橢圓曲線密碼（ECC）** |
| 1990 年代 | MOV 攻擊（1993）、異常曲線攻擊（1998）等發現了一些 **弱曲線**，但對一般曲線沒有進展 |
| 2000 年代 | NSA 的 Suite B（2005）採用 ECC；之後 TLS、SSH、比特幣、行動裝置大量使用 |

ECC 從提出到廣泛使用花了將近 20 年——新的數學難題需要時間累積「沒人能破」的信心。另一個實際原因是早期的 **專利** 問題。

**為什麼最後被接受**：同樣安全度的金鑰短很多（256 位元對 RSA 的 3072 位元），運算更快、頻寬更少，對手機與智慧卡特別重要。

---

# 第三部分：Lenstra 橢圓曲線分解法

## 3.1 回顧 Pollard p − 1

Pollard 的方法（第 12 課）在 **群 (Z/pZ)*** 裡工作，群的大小是 p − 1。只要 p − 1 是光滑數，`a^(n!)` 在模 p 時會變成 1，gcd 就抓到 p。**弱點**：p − 1 不光滑就沒辦法——而群是固定的，換不了。

## 3.2 Lenstra 的想法

把群換成 **橢圓曲線的點群 E(F_p)**，大小約 p，在 `p + 1 ± 2√p` 之間 **隨曲線變動**。換一條曲線，就是換一個群大小——總有某條曲線的 #E(F_p) 是光滑數。

**怎麼「看到」模 p 的事情？** 我們只能在 **模 N** 下計算。用加法公式時要算 `(x₂ − x₁)⁻¹ mod N`。如果某個倍數 kP 在模 p 時已經變成 O（也就是 x 座標在模 p 下相等），這個分母就會 **在模 N 下沒有反元素**——擴展歐幾里得失敗，而 **gcd(分母, N) 就是 p**！

課本例 5.22～5.23：N = 187，`E : Y² = X³ + 3X + 7`，P = (38, 112)。算 5P 時分母 11 和 187 不互質，`gcd(11, 187) = 11`，所以 `187 = 11 · 17`。

## 3.3 演算法

```
1. 隨機選 A、點 P = (a, b)，令 B = b² − a³ − Aa（這樣 P 一定在曲線上）
2. for j = 2, 3, 4, …：P ← j·P（mod N）
       計算中若遇到分母 d 和 N 不互質：
           g = gcd(d, N)，1 < g < N 就回傳 g；g = N 就換一條曲線
```

課本例 5.24：N = 6887，P = (1512, 3166)，A = 14。

```python
from math import gcd

class FoundFactor(Exception):
    pass

def make_ops(N, A):
    def inv(d):
        d %= N
        g = gcd(d, N)
        if g != 1:
            raise FoundFactor(g)
        return pow(d, -1, N)

    def add(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2 and (y1 + y2) % N == 0:
            return None
        lam = ((3 * x1 * x1 + A) * inv(2 * y1) if P == Q else (y2 - y1) * inv(x2 - x1)) % N
        x3 = (lam * lam - x1 - x2) % N
        return (x3, (lam * (x1 - x3) - y1) % N)

    def mul(n, P):
        R = None
        while n:
            if n & 1:
                R = add(R, P)
            P = add(P, P)
            n >>= 1
        return R
    return mul

def lenstra(N, A, P, bound=1000):
    mul = make_ops(N, A)
    try:
        for j in range(2, bound):
            P = mul(j, P)
            print(f"{j}!·P = {P}")
    except FoundFactor as e:
        return int(str(e)), j
    return None, bound

N, A, P = 6887, 14, (1512, 3166)
B = (P[1] ** 2 - P[0] ** 3 - A * P[0]) % N
print("B =", B)
print(lenstra(N, A, P))
```
```output
B = 19
2!·P = (3466, 2996)
3!·P = (3067, 396)
4!·P = (6507, 2654)
5!·P = (2783, 6278)
6!·P = (6141, 5581)
(71, 7)
```
在算 7!·P 時失敗，找到 71：`6887 = 71 · 97`。原因是 P 在 E(F₇₁) 中的階是 63 = 3² · 7，**7! 是第一個被 63 整除的階乘**；而在 E(F₉₇) 中的階是 107（大質數），還沒變成 O。

## 3.4 花費：只看最小的質因數

**Remark 5.25**：Lenstra 法的期望時間約 `e^(√(2 ln p · ln ln p))`，**p 是 N 最小的質因數**——和 N 本身的大小無關！

- 對 RSA（p ≈ q ≈ √N）：和二次篩法差不多，但篩法每一步便宜得多，所以篩法較快。
- 對 **「很大的數裡藏著一個中等大小的因數」**（例如 30～60 位數）：Lenstra 法是最好的方法。實務上會先用它把小因數剝掉，再用數體篩法。

```python
from math import gcd
import random

def ecm(N, curves=200, bound=2000, seed=1):
    rng = random.Random(seed)
    for c in range(curves):
        A = rng.randrange(N)
        P = (rng.randrange(N), rng.randrange(N))
        try:
            for j in range(2, bound):
                # j·P，遇到不可逆的分母就丟出 gcd
                R, Q, n = None, P, j
                while n:
                    if n & 1:
                        if R is None:
                            R = Q
                        else:
                            (x1, y1), (x2, y2) = R, Q
                            if x1 == x2:
                                raise ZeroDivisionError(gcd(y1 + y2, N) if (y1 + y2) % N else N)
                            d = gcd(x2 - x1, N)
                            if d != 1:
                                raise ZeroDivisionError(d)
                            lam = (y2 - y1) * pow(x2 - x1, -1, N) % N
                            x3 = (lam * lam - x1 - x2) % N
                            R = (x3, (lam * (x1 - x3) - y1) % N)
                    x1, y1 = Q
                    d = gcd(2 * y1, N)
                    if d != 1:
                        raise ZeroDivisionError(d)
                    lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, N) % N
                    x3 = (lam * lam - 2 * x1) % N
                    Q = (x3, (lam * (x1 - x3) - y1) % N)
                    n >>= 1
                P = R
        except ZeroDivisionError as e:
            g = e.args[0]
            if 1 < g < N:
                return g, c + 1
    return None, curves

p, q = 1000003, 999999999989         # 一個 7 位數的小因數、一個 12 位數的大因數
N = p * q
print(ecm(N))
```
```output
(1000003, 2)
```
（這是簡化的教學版本；為了簡潔，把 P 在中途變成 O 的情況當作「換下一條曲線」處理。）

---

# 第四部分：F₂ 與 F_{2^k} 上的曲線

## 4.1 為什麼要用 F_{2^k}

電腦以二進位運作，在 2 = 0 的體裡計算特別快（加法就是 XOR）。但 E(F₂) 最多 5 個點，沒用；要用的是 **F_{2^k}**（第 09 課）。Hasse 定理照樣成立：`|#E(F_{p^k}) − (p^k + 1)| ≤ 2p^(k/2)`。

## 4.2 廣義 Weierstrass 方程式

在 F_{2^k} 中 `Y² = X³ + AX + B` 一定是奇異的（判別式含 16 這個因子 = 0）。所以要用更一般的形式：

```
E : Y² + a₁XY + a₃Y = X³ + a₂X² + a₄X + a₆
```

判別式有一個較複雜的公式（用 b₂、b₄、b₆、b₈ 表示），要求它不是 0。點的相反元素變成 `−(x, y) = (x, −y − a₁x − a₃)`；加法公式也跟著稍微改變（課本習題 5.19）。

## 4.3 Frobenius 映射

**定義**：`τ : F_{p^k} → F_{p^k}`，`τ(α) = α^p`。它保持加法和乘法：`τ(α + β) = τ(α) + τ(β)`（p = 2 時就是 `(α + β)² = α² + β²`，第 15 課的新生之夢）。

如果曲線的 **係數在 F₂ 裡**，就可以對點的座標做 τ：`τ(x, y) = (x², y²)`。它把曲線上的點映到曲線上的點，而且是群的同態：`τ(P + Q) = τ(P) + τ(Q)`。

**定理 5.29**：`t = p + 1 − #E(F_p)`，則
- (a) α、β 是 `Z² − tZ + p` 的兩個複數根時，`#E(F_{p^k}) = p^k + 1 − α^k − β^k`——**知道 E(F_p) 的點數，就知道所有擴張體上的點數**。
- (b) 對所有點 Q：`τ²(Q) − t·τ(Q) + p·Q = O`。

```python
# 用 (a) 從 #E(F_p) 推出 #E(F_{p^k})：α^k + β^k 可以用遞迴 s_k = t·s_{k−1} − p·s_{k−2} 算
def count_ext(p, t, k):
    s = [2, t]                       # s_0 = α⁰ + β⁰ = 2，s_1 = α + β = t
    for _ in range(2, k + 1):
        s.append(t * s[-1] - p * s[-2])
    return p ** k + 1 - s[k]

# Koblitz 曲線 E : Y² + XY = X³ + 1 over F₂：直接數 E(F₂) 的點
pts = [(x, y) for x in range(2) for y in range(2) if (y * y + x * y - x ** 3 - 1) % 2 == 0]
n1 = len(pts) + 1
t = 2 + 1 - n1
print(pts, n1, t)
print([count_ext(2, t, k) for k in range(1, 12)])
N233 = count_ext(2, t, 233)
print(N233 % 4, (N233 // 4).bit_length(), hex(N233 // 4))
```
```output
[(0, 1), (1, 0), (1, 1)] 4 -1
[4, 8, 4, 16, 44, 56, 116, 288, 508, 968, 2116]
0 232 0x8000000000000000000000000000069d5bb915bcd46efb1ad5f173abdf
```
最後一行：這條曲線在 F_{2^233} 上就是 **NIST 標準的 Koblitz 曲線 K-233**，點數是 4 乘一個 232 位元的質數——印出的十六進位值和標準文件公布的子群階 `0x8000…ABDF` 一致。我們只數了 F₂ 上的 4 個點，就得到了 2²³³ 量級的點數。

## 4.4 Koblitz 曲線：用 τ 取代倍點

**Koblitz 曲線**：係數在 F₂ 的曲線，但取 F_{2^k} 上的點，例如 `Y² + XY = X³ + 1`。由定理 5.29(b)，τ 滿足 `τ² − tτ + 2 = 0`，t = ±1。所以 **2 = tτ − τ²**，任何整數 n 都能寫成 `Σ vᵢ τ^i`（vᵢ ∈ {−1, 0, 1}，稱為 τ-展開）。

**好處**：算 τ(P) 只是把兩個座標 **平方**，在 F_{2^k} 中幾乎不花時間（用適當的基底只是位元的循環移位）；所以 nP 可以用「τ 加」代替「倍加」，省下所有昂貴的倍點運算。

**代價與提醒**：額外的結構有時會帶來安全疑慮；課本建議用 **k 是質數** 的 F_{2^k}（避免中間的子體被利用）。近年來，因為 F_{2^k} 上的特殊攻擊研究進展，業界更傾向使用 F_p 上的曲線（例如 P-256、Curve25519）。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 橢圓曲線 Diffie–Hellman | ECDH | 用 nP 取代 g^n 的金鑰交換 | 1.1 |
| 點壓縮 | Point Compression | 只傳 x 座標（加 1 位元的正負號） | 1.2 |
| 橢圓 ElGamal | Elliptic ElGamal | 明文是點，C₁ = kP、C₂ = M + kQ | 1.3 |
| Lenstra 分解法 | Elliptic Curve Method (ECM) | 求反元素失敗時 gcd 給出因數 | 3.2 |
| 廣義 Weierstrass 方程式 | Generalized Weierstrass Equation | 含 XY、Y、X² 項的一般形式 | 4.2 |
| Frobenius 映射 | Frobenius Map | `α ↦ α^p`，點的座標各自乘方 | 4.3 |
| Koblitz 曲線 | Koblitz Curve | 係數在 F₂、點在 F_{2^k} 的曲線 | 4.4 |

---

# 習題

### 題 1：ECDH

用第 1.1 節的參數，Alice 選 n_A = 1000、Bob 選 n_B = 2000，算出他們的共同 x 座標。

### 題 2：點壓縮

在第 1.1 節的曲線上，x = 920 對應哪兩個點？它們的 y 加起來是多少？

### 題 3：Lenstra

用 Lenstra 法（A = 1，P = (0, 1)，所以 B = 1）分解 N = 455839，記下在第幾步成功。

### 題 4：觀念

Pollard p − 1 方法和 Lenstra 橢圓曲線法的共同想法是什麼？Lenstra 法多了什麼自由度？

### 題 5：觀念

為什麼在 F_{2^k} 上不能用 `Y² = X³ + AX + B` 這種形式？

---

# 習題解答

**題 1**：

```python
p, A = 3851, 324

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

def mul(n, P):
    R = None
    while n:
        if n & 1:
            R = add(R, P)
        P = add(P, P)
        n >>= 1
    return R

P = (920, 303)
S1 = mul(1000, mul(2000, P))
S2 = mul(2000, mul(1000, P))
print(S1, S1 == S2)
```
```output
(20, 3534) True
```
**題 2**：(920, 303) 和 (920, 3851 − 303) = (920, 3548)，兩個 y 加起來是 p = 3851 ≡ 0。

**題 3**：

```python
from math import gcd

N, A = 455839, 1
P = (0, 1)

def step(n, P):
    R = None
    while n:
        if n & 1:
            if R is None:
                R = P
            else:
                (x1, y1), (x2, y2) = R, P
                d = gcd(x2 - x1, N)
                if d != 1:
                    return None, d
                lam = (y2 - y1) * pow(x2 - x1, -1, N) % N
                x3 = (lam * lam - x1 - x2) % N
                R = (x3, (lam * (x1 - x3) - y1) % N)
        x1, y1 = P
        d = gcd(2 * y1, N)
        if d != 1:
            return None, d
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, N) % N
        x3 = (lam * lam - 2 * x1) % N
        P = (x3, (lam * (x1 - x3) - y1) % N)
        n >>= 1
    return R, 1

for j in range(2, 100):
    P, d = step(j, P)
    if d != 1:
        print(j, d, N // d)
        break
```
```output
31 761 599
```
**題 4**：兩者都是「在一個群裡乘上（或加上）一個大的光滑數 L，希望群元素在模 p 時變成單位元素，然後用 gcd 抓出 p」。Pollard 的群固定是 (Z/pZ)*，大小 p − 1 不能改；Lenstra 可以 **換曲線**，每條曲線的群大小都不同，總有一條是光滑的。

**題 5**：F_{2^k} 中 2 = 0，所以 `Y²` 的偏導數 `2Y = 0`；而判別式 `−16(4A³ + 27B²)` 也一定是 0——每條這種形式的曲線都是奇異的，不能形成群。所以要加上 `a₁XY + a₃Y` 這些項。
