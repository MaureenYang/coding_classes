# 08. 中國剩餘定理與 Pohlig–Hellman 演算法

> 對應課本：§2.8、§2.9
>
> 程式練習：`MC07 中國剩餘定理`、`MC08 Pohlig–Hellman`
>
> 先備知識：第 03 課（模反元素）、第 07 課（嬰兒步巨人步）。

**這一課分成四個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 中國剩餘定理 | 聯立同餘式的解存在且唯一、逐一代入法與公式法 |
| 第二部分 | 模合數的平方根 | p ≡ 3 (mod 4) 時的平方根公式、用 CRT 組合、為什麼「會開根號 ≈ 會分解」 |
| 第三部分 | Pohlig–Hellman 演算法 | 把階為 N 的 DLP 拆成階為質數次方的小 DLP |
| 第四部分 | 質數次方的 DLP | 一位一位解出 x 的 q 進位數字；p − 1 一定要有大質因數 |

> 課本說：中國剩餘定理不只是一個定理和一個演算法，**也是一種思考方式**——模 m 的問題，可以拆成模 m 的各個因數的問題分別解，再組回來。

---

# 第一部分：中國剩餘定理

## 1.1 一個 1700 年前的問題

《孫子算經》：「今有物不知其數，三三數之剩二，五五數之剩三，七七數之剩二，問物幾何？」用今天的寫法就是

```
x ≡ 2 (mod 3)，  x ≡ 3 (mod 5)，  x ≡ 2 (mod 7)
```

## 1.2 定理

**定理 2.25（中國剩餘定理，CRT）**：`m₁, …, m_k` **兩兩互質**，`a₁, …, a_k` 任意。則聯立同餘式

```
x ≡ a₁ (mod m₁)，  …，  x ≡ a_k (mod m_k)
```

**有解**，而且任兩個解模 `M = m₁m₂⋯m_k` 同餘——也就是說 **模 M 恰好有一個解**。

## 1.3 逐一代入法（課本的證明，也是演算法）

課本例 2.24：`x ≡ 1 (mod 5)`、`x ≡ 9 (mod 11)`。

1. 第一式的解是 `x = 1 + 5y`。
2. 代入第二式：`1 + 5y ≡ 9`，`5y ≡ 8 (mod 11)`。
3. `5⁻¹ ≡ 9 (mod 11)`，`y ≡ 72 ≡ 6`。
4. `x = 1 + 5 · 6 = 31`。

一般情況：每次手上有一個「滿足前 i 式」的解 `x = c + (m₁⋯mᵢ)·y`，代入第 i+1 式解出 y——因為 `m₁⋯mᵢ` 和 `m_{i+1}` 互質，一定能除（命題 1.13(b)）。

```python
def crt(residues, moduli):
    x, M = 0, 1
    for a, m in zip(residues, moduli):
        # 現在 x 滿足前面所有式子，解 x + M·y ≡ a (mod m)
        y = (a - x) * pow(M, -1, m) % m
        x += M * y
        M *= m
    return x % M, M

print(crt([1, 9], [5, 11]))
print(crt([2, 3, 4], [3, 7, 16]))          # 課本例 2.26
print(crt([2, 3, 2], [3, 5, 7]))           # 孫子算經
```
```output
(31, 55)
(164, 336)
(23, 105)
```
## 1.4 公式法

令 `Mᵢ = M / mᵢ`，`yᵢ = Mᵢ⁻¹ mod mᵢ`，則

```
x ≡ Σ aᵢ · Mᵢ · yᵢ (mod M)
```

**為什麼**：`Mᵢ yᵢ` 模 `mᵢ` 是 1，模其他 `mⱼ` 是 0（因為 `Mᵢ` 含 `mⱼ` 這個因數）。所以這一項在第 i 式「負責」貢獻 aᵢ，在其他式子都不出聲。

```python
from math import prod

def crt_formula(residues, moduli):
    M = prod(moduli)
    x = 0
    for a, m in zip(residues, moduli):
        Mi = M // m
        x += a * Mi * pow(Mi, -1, m)
    return x % M

print(crt_formula([2, 3, 4], [3, 7, 16]), crt_formula([2, 3, 2], [3, 5, 7]))
```
```output
164 23
```
## 1.5 不互質時

模數不互質時，CRT 不一定有解：`x ≡ 1 (mod 4)` 和 `x ≡ 2 (mod 6)` 無解（前者說 x 奇、後者說 x 偶）。有解的條件是 **兩兩之間 `aᵢ ≡ aⱼ (mod gcd(mᵢ, mⱼ))`**，有解時答案模 `lcm` 唯一。程式練習 MC07 只處理互質的情況。

> 🔍 **用環的語言說**：CRT 說的是 `Z/MZ ≅ Z/m₁Z × ⋯ × Z/m_kZ`——一個模 M 的數，等同於「它模各個 mᵢ 的餘數」這一組資料。加法和乘法都可以 **分量各自做**。這個觀點在 RSA 解密加速（第 10 課）和 Pohlig–Hellman 都會用到。

---

# 第二部分：模合數的平方根

## 2.1 模質數 p ≡ 3 (mod 4)

**命題 2.27**：p ≡ 3 (mod 4)，如果 a 在模 p 下有平方根，則 `b ≡ a^((p+1)/4)` 就是一個平方根。

**證明**：a 是平方數，寫成 `a = g^(2k)`（g 是原根）。則

```
b² = a^((p+1)/2) = g^(k(p+1)) = g^(k(p−1)) · g^(2k) = 1 · a
```

課本例 2.28：`2201` 模 `4127` 的平方根是 `2201^1032 ≡ 3718`。

```python
p, a = 4127, 2201
b = pow(a, (p + 1) // 4, p)
print(b, b * b % p)
```
```output
3718 2201
```
（p ≡ 1 (mod 4) 時也有有效率的方法——Tonelli–Shanks——但比較複雜。怎麼判斷 a 有沒有平方根，在第 14 課的二次剩餘介紹。）

## 2.2 模合數：先拆再組

課本例 2.29：解 `x² ≡ 197 (mod 437)`。`437 = 19 · 23`：

1. 模 19：`y² ≡ 197 ≡ 7`，得 `y ≡ ±8`。
2. 模 23：`z² ≡ 197 ≡ 13`，得 `z ≡ ±6`。
3. 用 CRT 組合 `(±8, ±6)`，共 **四個** 平方根。

```python
def crt(residues, moduli):
    x, M = 0, 1
    for a, m in zip(residues, moduli):
        x += M * ((a - x) * pow(M, -1, m) % m)
        M *= m
    return x % M

y = pow(197, (19 + 1) // 4, 19)
z = pow(197, (23 + 1) // 4, 23)
print(y, z)
roots = sorted(crt([sy * y, sz * z], [19, 23]) for sy in (1, -1) for sz in (1, -1))
print(roots, [r * r % 437 for r in roots])
```
```output
11 6
[144, 201, 236, 293] [197, 197, 197, 197]
```
模質數只有兩個平方根（±b），模兩個質數的乘積卻有四個。

## 2.3 會開根號就會分解

**反過來的事實**：如果有一台機器能對 **任何** 模 N = pq 的平方數開根號，就能分解 N。

**做法**：隨機選 r，把 `r² mod N` 交給機器，它回傳某個平方根 s。四個平方根中有兩個是 ±r，另外兩個不是；有一半的機率 `s ≢ ±r`。這時 `s² ≡ r²`，所以 `N | (s − r)(s + r)`，但 N 不整除任一因子——於是 `gcd(s − r, N)` 就是 p 或 q。

```python
from math import gcd
import random

p, q = 19, 23
N = p * q

def sqrt_oracle(a):            # 假裝這是一台只知道答案、不告訴你 p、q 的機器
    return random.choice([x for x in range(N) if x * x % N == a])

random.seed(3)
for _ in range(5):
    r = random.randrange(2, N)
    if gcd(r, N) != 1:
        continue
    s = sqrt_oracle(r * r % N)
    print(r, s, gcd(s - r, N))
```
```output
123 199 19
191 398 23
35 35 437
```
所以 **開根號和分解一樣難**（課本 Remark 2.31）。這個觀察是 Rabin 密碼系統的基礎，也會在第 12 課的平方差分解法再出現。

---

# 第三部分：Pohlig–Hellman 演算法

## 3.1 想法

要解 `g^x = h`，g 的階是 N，而 `N = q₁^e₁ · q₂^e₂ ⋯ q_t^e_t`。

**關鍵觀察**：取 `gᵢ = g^(N / qᵢ^eᵢ)`、`hᵢ = h^(N / qᵢ^eᵢ)`。那麼 `gᵢ` 的階是 `qᵢ^eᵢ`（小很多！），而且如果 `g^x = h`，

```
gᵢ^x = (g^x)^(N/qᵢ^eᵢ) = hᵢ
```

所以 `x mod qᵢ^eᵢ` 就是小 DLP `gᵢ^y = hᵢ` 的解。解出所有 `x ≡ yᵢ (mod qᵢ^eᵢ)` 之後，用 **CRT** 組回 `x mod N`。

**定理 2.32**：花費約 `Σ (解一個階為 qᵢ^eᵢ 的 DLP 的時間) + O(log N)`。

**結論**：DLP 的難度由 **N 最大的質因數** 決定，不是由 N 本身決定。

## 3.2 課本例 2.37

在 F₁₁₂₅₁* 中解 `23^x = 9689`。23 是原根，`N = 11250 = 2 · 3² · 5⁴`。

```python
def order_prime_power_dlp(g, h, p, n):        # 小 DLP：直接暴力（階很小）
    cur = 1
    for y in range(n):
        if cur == h:
            return y
        cur = cur * g % p

def crt(residues, moduli):
    x, M = 0, 1
    for a, m in zip(residues, moduli):
        x += M * ((a - x) * pow(M, -1, m) % m)
        M *= m
    return x % M

p, g, h = 11251, 23, 9689
N = p - 1
parts = [(2, 1), (3, 2), (5, 4)]
residues, moduli = [], []
for q, e in parts:
    qe = q ** e
    gi, hi = pow(g, N // qe, p), pow(h, N // qe, p)
    y = order_prime_power_dlp(gi, hi, p, qe)
    print(f"q^e = {qe:3}: g_i = {gi:5}, h_i = {hi:5}, x ≡ {y} (mod {qe})")
    residues.append(y)
    moduli.append(qe)
x = crt(residues, moduli)
print(x, pow(g, x, p))
```
```output
q^e =   2: g_i = 11250, h_i = 11250, x ≡ 1 (mod 2)
q^e =   9: g_i =  5029, h_i = 10724, x ≡ 4 (mod 9)
q^e = 625: g_i =  5448, h_i =  6909, x ≡ 511 (mod 625)
4261 9689
```
三個小 DLP 的大小只有 2、9、625，而不是 11250。

---

# 第四部分：質數次方的 DLP

## 4.1 再拆一層：一次解一位數

**命題 2.34**：g 的階是 `q^e` 時，可以只解 e 個 **階為 q** 的 DLP。

把未知的 x 寫成 q 進位：`x = x₀ + x₁q + x₂q² + ⋯ + x_{e−1}q^(e−1)`，`0 ≤ xᵢ < q`。

- **求 x₀**：兩邊取 `q^(e−1)` 次方。`g^(q^(e−1))` 的階是 q，而 `g^(x·q^(e−1)) = (g^(q^(e−1)))^(x₀)`（較高位的部分都乘出 `q^e`，變成 1）。所以 `x₀` 是 `(g^(q^(e−1)))^(x₀) = h^(q^(e−1))` 的解——一個階為 q 的 DLP。
- **求 x₁**：把已知的 x₀ 移掉，看 `h · g^(−x₀)`，再取 `q^(e−2)` 次方，同樣得到一個階為 q 的 DLP。
- 一直做到 `x_{e−1}`。

花費 `O(e · S_q)`，其中 `S_q` 是解一個階為 q 的 DLP 的時間（用嬰兒步巨人步就是 O(√q)）。直接對階 `q^e` 用嬰兒步巨人步要 `O(q^(e/2))`，e ≥ 2 時慢得多。

## 4.2 課本例 2.36

在 F₁₁₂₅₁* 中解 `5448^x = 6909`，5448 的階是 `5⁴ = 625`。

```python
def small_dlp(g, h, p, q):            # 階為 q 的 DLP（q 很小就暴力）
    cur = 1
    for y in range(q):
        if cur == h:
            return y
        cur = cur * g % p

def dlp_prime_power(g, h, p, q, e):
    x = 0
    gamma = pow(g, q ** (e - 1), p)       # 階為 q 的元素
    for k in range(e):
        hk = pow(h * pow(g, -x, p) % p, q ** (e - 1 - k), p)
        d = small_dlp(gamma, hk, p, q)
        print(f"x_{k} = {d}")
        x += d * q ** k
    return x

p, g, h = 11251, 5448, 6909
x = dlp_prime_power(g, h, p, 5, 4)
print(x, pow(g, x, p))
```
```output
x_0 = 1
x_1 = 2
x_2 = 0
x_3 = 4
511 6909
```
每一步只要在 5 個候選裡找，總共 4 × 5 = 20 次，而不是 625 次。

## 4.3 教訓：p − 1 要有大質因數

Pohlig–Hellman 說：F_p* 的 DLP 難度取決於 **p − 1 最大的質因數 q**，大約是 O(√q)。如果 p − 1 只有小質因數（叫 **光滑**，smooth），DLP 一下就被解開。

所以 Diffie–Hellman 和 ElGamal 要選：
- **安全質數** `p = 2q + 1`（q 是大質數），或
- 在 F_p* 中取 **階為大質數 q** 的子群，g 選在這個子群裡。

```python
def factor(n):
    f, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f

for p in (11251, 2**61 - 1, 1000000007):
    print(p, factor(p - 1))
```
```output
11251 {2: 1, 3: 2, 5: 4}
2305843009213693951 {2: 1, 3: 2, 5: 2, 7: 1, 11: 1, 13: 1, 31: 1, 41: 1, 61: 1, 151: 1, 331: 1, 1321: 1}
1000000007 {2: 1, 500000003: 1}
```
`2⁶¹ − 1` 是很大的質數，但 `p − 1` 只有小質因數，最大的才 1321——在它上面的 DLP 用 Pohlig–Hellman 瞬間就解開。`1000000007 − 1 = 2 · 500000003`，就安全得多。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 中國剩餘定理 | Chinese Remainder Theorem (CRT) | 兩兩互質的聯立同餘式，模乘積恰有一解 | 1.2 |
| 兩兩互質 | Pairwise Relatively Prime | 任兩個 gcd 都是 1 | 1.2 |
| 平方根（模 m） | Square Root modulo m | `x² ≡ a (mod m)` 的解 | 2.1 |
| Pohlig–Hellman 演算法 | Pohlig–Hellman Algorithm | 用 N 的分解把 DLP 拆小 | 3.1 |
| 光滑數 | Smooth Number | 只有小質因數的數 | 4.3 |
| 安全質數 | Safe Prime | `p = 2q + 1`，q 是質數 | 4.3 |

---

# 習題

### 題 1：CRT 手算

解 `x ≡ 3 (mod 7)`、`x ≡ 4 (mod 9)`、`x ≡ 1 (mod 5)`。

### 題 2：有沒有解

`x ≡ 3 (mod 6)` 和 `x ≡ 5 (mod 8)` 有沒有解？`x ≡ 3 (mod 6)` 和 `x ≡ 4 (mod 8)` 呢？

### 題 3：平方根

用 2.2 節的方法找出 `x² ≡ 340 (mod 437)` 的所有解。

### 題 4：Pohlig–Hellman

p = 433（`p − 1 = 432 = 2⁴ · 3³`），7 是原根。用 Pohlig–Hellman 解 `7^x ≡ 166 (mod 433)`。

### 題 5：觀念

為什麼「p 是很大的質數」還不足以讓 F_p* 的 DLP 很難？

---

# 習題解答

**題 1**：

```python
def crt(residues, moduli):
    x, M = 0, 1
    for a, m in zip(residues, moduli):
        x += M * ((a - x) * pow(M, -1, m) % m)
        M *= m
    return x % M, M

print(crt([3, 4, 1], [7, 9, 5]))
```
```output
(31, 315)
```
**題 2**：gcd(6, 8) = 2。第一組：3 和 5 模 2 都是 1，**有解**（模 lcm = 24 唯一）；第二組：3 是奇數、4 是偶數，模 2 不相容，**無解**。

```python
print([x for x in range(24) if x % 6 == 3 and x % 8 == 5])
print([x for x in range(24) if x % 6 == 3 and x % 8 == 4])
```
```output
[21]
[]
```
**題 3**：

```python
def crt(residues, moduli):
    x, M = 0, 1
    for a, m in zip(residues, moduli):
        x += M * ((a - x) * pow(M, -1, m) % m)
        M *= m
    return x % M

y = pow(340, 5, 19)          # (19 + 1) / 4 = 5
z = pow(340, 6, 23)          # (23 + 1) / 4 = 6
print(y, y * y % 19, 340 % 19, z, z * z % 23, 340 % 23)
roots = sorted(crt([sy * y, sz * z], [19, 23]) for sy in (1, -1) for sz in (1, -1))
print(roots, [r * r % 437 for r in roots])
```
```output
6 17 17 8 18 18
[146, 215, 222, 291] [340, 340, 340, 340]
```
**題 4**：

```python
def dlp_small(g, h, p, n):
    cur = 1
    for y in range(n):
        if cur == h:
            return y
        cur = cur * g % p

def crt(residues, moduli):
    x, M = 0, 1
    for a, m in zip(residues, moduli):
        x += M * ((a - x) * pow(M, -1, m) % m)
        M *= m
    return x % M

p, g, h, N = 433, 7, 166, 432
res, mods = [], []
for qe in (16, 27):
    res.append(dlp_small(pow(g, N // qe, p), pow(h, N // qe, p), p, qe))
    mods.append(qe)
x = crt(res, mods)
print(res, x, pow(g, x, p))
```
```output
[15, 20] 47 166
```
**題 5**：Pohlig–Hellman 把 DLP 拆成「p − 1 的每個質因數次方」上的小 DLP，難度只取決於 **p − 1 最大的質因數**。如果 p − 1 是光滑數，不管 p 多大，DLP 都很容易。
