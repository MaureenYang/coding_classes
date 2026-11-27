# 25. 數位簽章（Digital Signatures）

> 對應課本：第 7 章（§7.1～§7.5）
>
> 程式練習：`MC09 RSA 加解密`（簽章就是反過來用）、`MC16 DSA 簽章與驗證`
>
> 先備知識：第 06 課（ElGamal）、第 10 課（RSA）、第 22～23 課（GGH、NTRU）。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 什麼是數位簽章 | 簽章和加密的差別、安全的條件、為什麼要先雜湊 |
| 第二部分 | RSA 簽章 | 用私鑰「加密」就是簽章；課本例 7.4 |
| 第三部分 | ElGamal 簽章 | 簽章公式、為什麼驗證會成立、臨時金鑰重複使用的災難 |
| 第四部分 | DSA 與 ECDSA | 在階為 q 的子群中簽章，讓簽章變短；課本例 7.7 |
| 第五部分 | 格上的簽章 | GGH 簽章、NTRU 簽章、謄本攻擊 |

---

# 第一部分：什麼是數位簽章

## 1.1 簽章 vs 加密

課本換了兩個角色：**Samantha**（簽章者）和 **Victor**（驗證者）。

| | 公鑰加密 | 數位簽章 |
|---|---|---|
| 比喻 | 有投信口的保險箱：任何人都能投、只有主人能開 | **印章戒指**：只有主人能蓋，任何人都能核對印記 |
| 私鑰用來 | 解密 | **簽章** |
| 公鑰用來 | 加密 | **驗證** |
| 保護的是 | 機密性 | **真實性、完整性、不可否認性** |

數位簽章系統包含：私鑰 K_pri、公鑰 K_pub、**簽章演算法** `Sign(D, K_pri) → D_sig`、**驗證演算法** `Verify(D, D_sig, K_pub) → True / False`。驗證者 **不需要也不知道** 私鑰。

**日常的重要性**（Remark 7.1）：作業系統和程式更新、HTTPS 憑證、程式碼簽章、電子文件、區塊鏈交易——都靠數位簽章確認「這真的是對方發的，而且沒被改過」。

## 1.2 安全的條件

1. 從 K_pub 算不出 K_pri（也算不出任何能產生相同簽章的私鑰）。
2. 即使看到很多「文件 + 簽章」，也 **無法替一份新文件偽造簽章**。

第 2 點和加密不同：加密時任何人都能自己用公鑰產生「明文—密文」配對；但每簽一份文件就公開了一組新的配對，這是 **只有私鑰能產生** 的新資訊。利用大量簽章的攻擊叫 **謄本攻擊**（transcript attack）。

## 1.3 先雜湊再簽章

簽章演算法一次只能處理幾百位元的資料。長文件 D 的做法：計算 **雜湊值** `Hash(D)`（固定長度，例如 256 位元），**簽雜湊值**。驗證者也算雜湊值再驗證。這要求雜湊函數 **難以找到碰撞**——否則 Eve 找到 `Hash(D) = Hash(D')`，Samantha 簽了 D 也等於簽了 D'（第 26 課）。

---

# 第二部分：RSA 簽章

## 2.1 系統

| | 做什麼 |
|---|---|
| **建金鑰** | 秘密質數 p、q，N = pq；公開 **驗證指數** v；算 **簽章指數** s，`sv ≡ 1 (mod (p−1)(q−1))` |
| **簽章** | `S ≡ D^s (mod N)` |
| **驗證** | 檢查 `S^v ≡ D (mod N)` |

就是 RSA 加密「反過來用」：用 **私鑰** 那個指數做運算，任何人都能用 **公鑰** 那個指數還原。

```python
p, q = 1223, 1987                          # 課本例 7.4
N = p * q
v = 948047
s = pow(v, -1, (p - 1) * (q - 1))
D = 1070777
S = pow(D, s, N)
print(N, s, S)
print(pow(S, v, N) == D)                   # Victor 驗證
print(pow(S, v, N) == 1070778)             # 改了文件就驗不過
```
```output
2430101 1051235 153337
True
False
```
## 2.2 為什麼要雜湊：存在性偽造

沒有雜湊時，Eve 可以 **先挑簽章 S**，再算出 `D = S^v mod N`——(D, S) 就是一組合法的「文件 + 簽章」。雖然 D 是亂碼，但這叫 **存在性偽造**（existential forgery）。另外 RSA 的可乘性也讓 Eve 能把兩個簽章相乘，得到乘積文件的簽章。先雜湊（再加上適當的填充，例如 RSA-PSS）就能擋掉這些。

```python
p, q = 1223, 1987
N = p * q
v = 948047
s = pow(v, -1, (p - 1) * (q - 1))

S_fake = 123456                            # Eve 隨便挑一個簽章
D_fake = pow(S_fake, v, N)                 # 反推出對應的「文件」
print(D_fake, pow(S_fake, v, N) == D_fake)

D1, D2 = 1000, 2000                         # 可乘性
S1, S2 = pow(D1, s, N), pow(D2, s, N)
print(S1 * S2 % N == pow(D1 * D2 % N, s, N))
```
```output
945364 True
True
```
---

# 第三部分：ElGamal 簽章

## 3.1 系統（課本表 7.2）

| | 做什麼 |
|---|---|
| **公開參數** | 大質數 p、原根 g |
| **建金鑰** | 秘密 s，公開 `v ≡ g^s (mod p)` |
| **簽章 D** | 選 **隨機臨時金鑰** e（和 p − 1 互質）：`S₁ ≡ g^e (mod p)`，`S₂ ≡ (D − sS₁)e⁻¹ (mod p − 1)` |
| **驗證** | 檢查 `v^(S₁) · S₁^(S₂) ≡ g^D (mod p)` |

**為什麼成立**：

```
v^(S₁) S₁^(S₂) = g^(sS₁) · g^(e · (D − sS₁)e⁻¹) = g^(sS₁ + D − sS₁) = g^D
```

注意 **S₂ 是模 p − 1**——因為它出現在指數上，而指數只看模 p − 1（費馬小定理）。

**偽造要做什麼**：Eve 要找 x、y 使 `v^x x^y ≡ g^D`。x 同時出現在底數和指數，很奇特；目前唯一知道的方法是先解 DLP。

課本例 7.6：p = 21739、g = 7、s = 15140、D = 5331、e = 10727。

```python
p, g = 21739, 7
s = 15140
v = pow(g, s, p)
D, e = 5331, 10727
S1 = pow(g, e, p)
S2 = (D - s * S1) * pow(e, -1, p - 1) % (p - 1)
print(v, (S1, S2))
print(pow(v, S1, p) * pow(S1, S2, p) % p, pow(g, D, p))
```
```output
17702 (15775, 791)
13897 13897
```
## 3.2 ⚠️ 臨時金鑰重複使用 = 私鑰外洩

如果 Samantha 用同一個 e 簽了兩份文件 D、D'，兩個簽章的 S₁ 一樣，而

```
S₂ e ≡ D − sS₁，  S₂' e ≡ D' − sS₁   ⇒   (S₂ − S₂') e ≡ D − D' (mod p − 1)
```

Eve 解出 e，再從 `sS₁ ≡ D − S₂e` 解出 **私鑰 s**（gcd 不是 1 時有幾個候選，逐一用 `g^s = v` 驗證）。

```python
from math import gcd

p, g, s = 21739, 7, 15140
v = pow(g, s, p)
e = 10727                                  # 不小心用了兩次
def sign(D):
    S1 = pow(g, e, p)
    return S1, (D - s * S1) * pow(e, -1, p - 1) % (p - 1)

(S1, S2), (_, S2b) = sign(5331), sign(1234)
n = p - 1

def solve_linear(a, b, n):                 # 解 a·x ≡ b (mod n)，回傳所有解
    g_ = gcd(a, n)
    if b % g_:
        return []
    x0 = (b // g_) * pow(a // g_, -1, n // g_) % (n // g_)
    return [x0 + k * (n // g_) for k in range(g_)]

for e_guess in solve_linear((S2 - S2b) % n, (5331 - 1234) % n, n):
    if pow(g, e_guess, p) != S1:
        continue
    for s_guess in solve_linear(S1 % n, (5331 - S2 * e_guess) % n, n):
        if pow(g, s_guess, p) == v:
            print("Eve 算出 e =", e_guess, " 私鑰 s =", s_guess)
```
```output
Eve 算出 e = 10727  私鑰 s = 15140
```
這正是 2010 年 Sony PS3 被破解的原因（他們的 ECDSA 每次都用同一個 e）。實務上 e 由 **私鑰和訊息的雜湊** 決定（RFC 6979 的確定性臨時金鑰），既不重複也不依賴亂數品質。

---

# 第四部分：DSA 與 ECDSA

## 4.1 讓簽章變短

ElGamal 簽章要抵抗指標演算法，p 要 1000～2000 位元以上，簽章就是 2000～4000 位元。**DSA**（Digital Signature Algorithm，1991 年提出、1994 年成為美國標準 DSS）的想法：**在 F_p* 中一個階為質數 q 的子群裡做**。指標演算法還是要對付整個 F_p（所以 p 仍然要大），但碰撞類攻擊只看子群大小 q，所以 q 只要 160～320 位元，簽章就是兩個 mod q 的數。

## 4.2 系統（課本表 7.3）

| | 做什麼 |
|---|---|
| **公開參數** | 質數 p、q，`p ≡ 1 (mod q)`；g 的階恰好是 q（取 `g = g₁^((p−1)/q)`，g₁ 是原根） |
| **建金鑰** | 秘密 s（1 ≤ s < q），公開 `v ≡ g^s (mod p)` |
| **簽章 D**（1 ≤ D < q） | 隨機 e：`S₁ = (g^e mod p) mod q`，`S₂ ≡ (D + sS₁)e⁻¹ (mod q)` |
| **驗證** | `V₁ ≡ D S₂⁻¹`、`V₂ ≡ S₁ S₂⁻¹ (mod q)`，檢查 `(g^(V₁) v^(V₂) mod p) mod q = S₁` |

**為什麼成立**：`g^(V₁) v^(V₂) = g^((D + sS₁) S₂⁻¹) = g^e`（指數模 q 計算，因為 g 的階是 q）。

課本例 7.7：p = 48731、q = 443、g = 5260、s = 242、D = 343、e = 427。

```python
p, q = 48731, 443
g = pow(7, (p - 1) // q, p)                # 7 是模 48731 的原根
print(g, pow(g, q, p))
s = 242
v = pow(g, s, p)
D, e = 343, 427
S1 = pow(g, e, p) % q
S2 = (D + s * S1) * pow(e, -1, q) % q
print(v, (S1, S2))
V1, V2 = D * pow(S2, -1, q) % q, S1 * pow(S2, -1, q) % q
print(V1, V2, pow(g, V1, p) * pow(v, V2, p) % p % q == S1)
```
```output
5260 1
3438 (59, 166)
357 414 True
```
## 4.3 ECDSA

把 DSA 搬到 **橢圓曲線**（課本習題 7.11）：點 G 的階是 n，私鑰 s，公鑰 `V = sG`；簽章時 `S₁ = x(eG) mod n`、`S₂ ≡ (D + sS₁)e⁻¹ (mod n)`；驗證算 `V₁G + V₂V` 的 x 座標。因為 ECDLP 更難，256 位元的曲線就有 128 位元安全度，簽章只有 64 bytes。注意 n 必須是 **質數**——S₂ 要對 n 求反元素。下面的曲線有 1964 = 4 · 491 個點，所以改用 4P₀，它的階是質數 491（就像 DSA 取階為 q 的子群）。比特幣、TLS、手機的安全晶片都用 ECDSA（或它的近親 EdDSA / Ed25519）。

```python
p, A, B = 3851, 324, 1287                  # 借用第 19 課的曲線（只是示範，數字太小不安全）

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    lam = ((3 * x1 * x1 + A) * pow(2 * y1, -1, p) if P == Q else (y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

def mul(k, P):
    R = None
    while k:
        if k & 1: R = add(R, P)
        P, k = add(P, P), k >> 1
    return R

P0 = (920, 303)
m, R = 1, P0                               # P0 的階
while R is not None:
    R, m = add(R, P0), m + 1
G = mul(4, P0)                             # m = 1964 = 4·491，取階為質數 491 的點
n = m // 4
print(m, "G =", G, " G 的階 n =", n, mul(n, G))

s = 123                                    # 私鑰
V = mul(s, G)
D, e = 100, 77
S1 = mul(e, G)[0] % n
S2 = (D + s * S1) * pow(e, -1, n) % n
w = pow(S2, -1, n)
X = add(mul(D * w % n, G), mul(S1 * w % n, V))
print((S1, S2), X[0] % n == S1)
```
```output
1964 G = (490, 204)  G 的階 n = 491 None
(16, 97) True
```
---

# 第五部分：格上的簽章

## 5.1 GGH 簽章

**想法**：Samantha 有好基底（能解 apprCVP），文件 d 是 Zⁿ 中的一個向量。她用 Babai 演算法找一個 **離 d 很近** 的格點 s，再用 **壞基底** 表示它（係數就是簽章）。Victor 用公開的壞基底算出 s，檢查 s 在格上（自動成立）而且 **‖s − d‖ 夠小**。

課本例 7.9：用第 23 課的 GGH 金鑰簽 `d = (678846, 651685, 160467)`。

```python
from fractions import Fraction as F
import math

def solve(B, e):
    n = len(B)
    A = [[F(B[j][i]) for j in range(n)] + [F(e[i])] for i in range(n)]
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

V = [[-97, 19, 19], [-36, 30, 86], [-184, -64, 78]]
U = [[4327, -15447, 23454], [3297, -11770, 17871], [5464, -19506, 29617]]
W = [combo(U[i], V) for i in range(3)]

d = [678846, 651685, 160467]
s = combo([round(x) for x in solve(V, d)], V)              # Samantha 用好基底
sig = [int(x) for x in solve(W, s)]                        # 用壞基底的係數表示
print("簽章", sig)
s_check = combo(sig, W)                                    # Victor 只用公鑰
print(s_check, round(math.dist(s_check, d), 2))
s_eve = combo([round(x) for x in solve(W, d)], W)          # Eve 只有壞基底
print(s_eve, f"{math.dist(s_eve, d):.3e}")
```
```output
簽章 [1531010, -553385, -878508]
[678835, 651671, 160437] 34.89
[2773584, 1595134, -131844] 2.316e+06
```
## 5.2 謄本攻擊

每個 GGH 簽章都洩漏一點資訊：`d − s = Σ εᵢ vᵢ`，其中 εᵢ 在 −1/2 到 1/2 之間（Babai 四捨五入的誤差）。所以 **d − s 都落在私鑰的基本平行多面體裡**。收集夠多的簽章，Eve 就能統計出這個平行多面體的形狀，也就是 **私鑰的好基底**——Nguyen 和 Regev（2006）就這樣破解了 GGH 簽章和早期的 NTRU 簽章（NTRUSign）。

**現代的格簽章**（例如 NIST 標準 ML-DSA / Dilithium、FN-DSA / Falcon）用 **拒絕取樣** 或 **高斯取樣**，讓簽章的分布和私鑰無關，從根本上擋住謄本攻擊。

## 5.3 NTRU 簽章（§7.5）

GGH 的公鑰太大（n² 個數）。NTRU 格只要一個多項式 h 就能描述，但它只有「半組」短向量 `(x^i ⋆ f, x^i ⋆ g)`，簽章需要 **一整組** 短基底。課本給出的方法：用結式（resultant）和擴展歐幾里得找出另外一組多項式 (F, G)，滿足

```
f ⋆ G − g ⋆ F = q
```

而且 F、G 也不太大（命題 7.14）。這樣 `(f, g), (F, G)` 就是 NTRU 格的一組好基底，可以像 GGH 一樣用 Babai 簽章。這個「補完基底」的構造後來成為 Falcon 簽章的核心。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 數位簽章 | Digital Signature | 私鑰簽、公鑰驗 | 1.1 |
| 簽章 / 驗證金鑰 | Signing / Verification Key | 私鑰 / 公鑰 | 1.1 |
| 不可否認性 | Non-repudiation | 簽了就不能說沒簽 | 1.1 |
| 謄本攻擊 | Transcript Attack | 利用大量已知簽章 | 1.2 |
| 存在性偽造 | Existential Forgery | 偽造某份（可能無意義的）文件的簽章 | 2.2 |
| ElGamal 簽章 | ElGamal Signature | `S₂ = (D − sS₁)e⁻¹ mod p − 1` | 3.1 |
| DSA / ECDSA | Digital Signature Algorithm / Elliptic Curve DSA | 在階 q 的子群 / 橢圓曲線上簽章 | 4 |
| GGH 簽章 | GGH Signature | 用好基底解 apprCVP 當簽章 | 5.1 |

---

# 習題

### 題 1：RSA 簽章

N = 1739（= 37 · 47）、v = 5。求 s，簽 D = 100，並驗證。

### 題 2：ElGamal 簽章驗證

p = 21739、g = 7、v = 17702。判斷 (D, S₁, S₂) = (5331, 15775, 791) 和 (5331, 15775, 792) 哪個是合法簽章。

### 題 3：DSA

用課本例 7.7 的參數，Samantha 以 e = 100 簽 D = 200。算出簽章並驗證。

### 題 4：觀念

為什麼簽章要先對文件做雜湊？列出兩個理由。

### 題 5：觀念

為什麼 DSA 的簽章比 ElGamal 簽章短，安全性卻差不多？

---

# 習題解答

**題 1**：

```python
p, q, v = 37, 47, 5
N = p * q
s = pow(v, -1, (p - 1) * (q - 1))
S = pow(100, s, N)
print(s, S, pow(S, v, N))
```
```output
1325 1379 100
```
**題 2**：

```python
p, g, v = 21739, 7, 17702
for S2 in (791, 792):
    print(S2, pow(v, 15775, p) * pow(15775, S2, p) % p == pow(g, 5331, p))
```
```output
791 True
792 False
```
**題 3**：

```python
p, q = 48731, 443
g, s = 5260, 242
v = pow(g, s, p)
D, e = 200, 100
S1 = pow(g, e, p) % q
S2 = (D + s * S1) * pow(e, -1, q) % q
V1, V2 = D * pow(S2, -1, q) % q, S1 * pow(S2, -1, q) % q
print((S1, S2), pow(g, V1, p) * pow(v, V2, p) % p % q == S1)
```
```output
(376, 274) True
```
**題 4**：(1) 效率：簽章演算法一次只能處理幾百位元，雜湊把任意長的文件壓成固定長度，只要簽一次。(2) 安全：沒有雜湊時 RSA 簽章有存在性偽造和可乘性的問題；雜湊（加上填充）破壞了這些代數結構。

**題 5**：DSA 在階為 q 的子群中運算，簽章是兩個 mod q 的數（q 約 160～320 位元），而不是 mod p（1000～3000 位元）。安全上：指標演算法攻擊的是整個 F_p，所以 p 仍然很大；碰撞類演算法（Pollard ρ）只和子群大小 q 有關，`√q ≥ 2⁸⁰～2¹⁶⁰` 就夠了。
