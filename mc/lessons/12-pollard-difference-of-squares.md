# 12. Pollard p − 1 與平方差分解法（Factorization I）

> 對應課本：§3.5、§3.6
>
> 程式練習：`MC11 整數分解`
>
> 先備知識：第 02 課（gcd）、第 03 課（快速冪）、第 08 課（模 pq 的平方根）。

**這一課分成四個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | Pollard p − 1 方法 | 為什麼 p − 1 是光滑數時 N 很好分解、演算法、課本例 3.29 |
| 第二部分 | 平方差 | Fermat 分解法、`kN + b²` 的技巧 |
| 第三部分 | 同餘的平方差 | `a² ≡ b² (mod N)` ⇒ `gcd(a − b, N)`；三步驟分解法 |
| 第四部分 | 線性代數 | 怎麼把一堆 `a² ≡ 光滑數` 組合成平方：F₂ 上的高斯消去 |

---

# 第一部分：Pollard p − 1 方法

## 1.1 想法

RSA 的矛盾（課本語）：為了讓 RSA 有效率，我們想用好算的特殊數字；但特殊的數字往往有特殊的弱點。Pollard 的 p − 1 方法就是一例。

設 N = pq。假設 **p − 1 恰好整除某個 L**（例如 L = n!，而 p − 1 只有不超過 n 的小質因數）。那麼由費馬小定理：

```
a^L = (a^(p−1))^(L/(p−1)) ≡ 1 (mod p)   ⇒   p | a^L − 1
```

如果 q − 1 不整除 L，通常 `a^L ≢ 1 (mod q)`，於是 q ∤ a^L − 1。所以

```
gcd(a^L − 1, N) = p
```

**我們不需要知道 p 就能做這個計算！**

## 1.2 演算法

不用真的算 `a^(n!)`（2^(100!) 的位數比宇宙中的粒子還多），只要 **模 N** 算，而且 `a^(n!) = (a^((n−1)!))^n`，每一步只要一次快速冪：

```
a ← 2
for j = 2, 3, 4, …:
    a ← a^j mod N            # 現在 a = 2^(j!) mod N
    d ← gcd(a − 1, N)
    if 1 < d < N: 回傳 d
    if d == N: 換一個起始值或改變策略
```

課本例 3.29：N = 13927189。

```python
from math import gcd

def pollard_p_minus_1(N, bound=10**6, verbose=False):
    a = 2
    for j in range(2, bound):
        a = pow(a, j, N)
        d = gcd(a - 1, N)
        if verbose and j >= 9:
            print(f"2^({j}!) − 1 ≡ {(a - 1) % N:>9} (mod N)，gcd = {d}")
        if 1 < d < N:
            return d, j
        if d == N:
            return None, j
    return None, bound

N = 13927189
d, j = pollard_p_minus_1(N, verbose=True)
print(d, N // d)

def factor(n):
    f, p = [], 2
    while p * p <= n:
        while n % p == 0:
            f.append(p)
            n //= p
        p += 1
    return f + ([n] if n > 1 else [])

print(factor(3823 - 1), factor(3643 - 1))
```
```output
2^(9!) − 1 ≡  13867883 (mod N)，gcd = 1
2^(10!) − 1 ≡   5129508 (mod N)，gcd = 1
2^(11!) − 1 ≡   4405233 (mod N)，gcd = 1
2^(12!) − 1 ≡   6680550 (mod N)，gcd = 1
2^(13!) − 1 ≡   6161077 (mod N)，gcd = 1
2^(14!) − 1 ≡    879290 (mod N)，gcd = 3823
3823 3643
[2, 3, 7, 7, 13] [2, 3, 607]
```
`3823 − 1 = 2 · 3 · 7² · 13`，最大的質因數 13 ≤ 14，所以 `3822 | 14!`；而 `3643 − 1 = 2 · 3 · 607`，有大質因數 607，不整除 14!。

課本例 3.30：N = 168441398857，到 53! 才找到 350437：

```python
from math import gcd

def pollard_p_minus_1(N, bound=10**6):
    a = 2
    for j in range(2, bound):
        a = pow(a, j, N)
        d = gcd(a - 1, N)
        if 1 < d < N:
            return d, j
        if d == N:
            return None, j
    return None, bound

def factor(n):
    f, p = [], 2
    while p * p <= n:
        while n % p == 0:
            f.append(p)
            n //= p
        p += 1
    return f + ([n] if n > 1 else [])

N = 168441398857
d, j = pollard_p_minus_1(N)
print(d, N // d, j)
print(factor(d - 1), factor(N // d - 1))
```
```output
350437 480661 53
[2, 2, 3, 19, 29, 53] [2, 2, 3, 5, 8011]
```
## 1.3 失敗的情況與花費

- **gcd 變成 N**：p − 1 和 q − 1 同時整除 j!。這時可以退回上一步，改成逐個質數慢慢加。
- **一直是 1**：p − 1、q − 1 都有很大的質因數。

花費：到第 n 步做了約 n 次快速冪，每次 O(log j) 次乘法，總共 O(n log n) 次模 N 的乘法。**成功與否只取決於 p − 1 最大質因數的大小**，跟 p 有多大無關。

## 1.4 對 RSA 的教訓

建 RSA 金鑰時要確認 **p − 1 和 q − 1 都有大質因數**——隨機選的大質數幾乎都滿足。課本（Remark 3.31）的重點是一個更普遍的教訓：

> **一個建立在看似困難的問題（大數分解）上的系統，也要提防這個問題的「特殊情況」。** 誰想得到 p − 1 的分解，竟然會影響 pq 的分解難度？

> 🔍 第 19 課的 **Lenstra 橢圓曲線分解法** 把同樣的想法推廣：把群 F_p*（階 p − 1）換成橢圓曲線的點群（階約 p，但可以隨便換曲線），只要某條曲線的階是光滑數就成功。

---

# 第二部分：平方差

## 2.1 Fermat 分解法

最強大的分解法都建立在一個國中公式上：

```
X² − Y² = (X + Y)(X − Y)
```

找 b 使 `N + b²` 是完全平方數 `a²`，就有 `N = a² − b² = (a + b)(a − b)`。

課本例 3.33：N = 25217，試 b = 1, 2, 3, …：

```python
from math import isqrt

def fermat(N, k=1, limit=10**6):
    for b in range(1, limit):
        t = k * N + b * b
        a = isqrt(t)
        if a * a == t:
            return a, b
    return None

N = 25217
a, b = fermat(N)
print(a, b, a + b, a - b, (a + b) * (a - b))
```
```output
159 8 167 151 25217
```
b = 8 時 `25217 + 64 = 25281 = 159²`，所以 `N = 167 · 151`。

**為什麼有時很快**：如果 `N = pq` 而 p、q 很接近，`a = (p + q)/2`、`b = (q − p)/2`，b 很小，很快就找到。**所以 RSA 的 p 和 q 不能太接近！**

## 2.2 kN + b² 的技巧

如果 `N + b²` 一直不是平方數，可以試 `kN + b²`。如果 `kN = a² − b² = (a + b)(a − b)`，那 `gcd(N, a − b)` 有機會給出 N 的因數。

課本例 3.34：N = 203299，`N + b²` 在 b ≤ 100 都不是平方，但 `3N + b²` 在 b = 4 時是：

```python
from math import gcd, isqrt

def fermat(N, k=1, limit=10**6):
    for b in range(1, limit):
        t = k * N + b * b
        a = isqrt(t)
        if a * a == t:
            return a, b
    return None

N = 203299
print(fermat(N, 1, 101))
a, b = fermat(N, 3)
print(a, b, gcd(N, a - b), N // gcd(N, a - b))
```
```output
None
781 8 773 263
```
**為什麼不試 2N + b²？** N 是奇數時，`2N + b² ≡ 2 或 3 (mod 4)`，而平方數模 4 只會是 0 或 1，所以永遠不會是平方數（Remark 3.35）。

---

# 第三部分：同餘的平方差

## 3.1 只要模 N 同餘就夠了

再放寬一步：不需要 `kN = a² − b²` 的 k 是什麼，只要

```
a² ≡ b² (mod N)，  而且 a ≢ ±b (mod N)
```

那 `N | (a − b)(a + b)`，但 N 不整除任一因子，所以 **`gcd(a − b, N)` 是 N 的非平凡因數**。

**成功機率**（Remark 3.38）：N = pq 時，對一組「隨機的」a、b，`a − b` 恰好被 p、q 之一整除（而不是兩個都整除或都不整除）的機率大約是 1/2。所以找到幾組，幾乎一定成功。（和第 08 課「會開根號就會分解」是同一件事。）

## 3.2 怎麼找 a² ≡ b²？三步驟分解法（課本表 3.4）

直接找很難。聰明的辦法是：

1. **建立關係**（relation building）：找很多 `a₁, a₂, …, a_r`，使每個 `cᵢ ≡ aᵢ² (mod N)` 都是 **B-光滑數**（只有不超過 B 的質因數）。
2. **消去**（elimination）：挑出其中一些 cᵢ，使它們的乘積是 **完全平方**——也就是每個質數的總次數都是偶數。
3. **gcd**：令 `a = Π aᵢ`、`b = √(Π cᵢ)`，則 `a² ≡ b² (mod N)`，算 `gcd(a − b, N)`。

課本例 3.36：N = 914387。

```
1869² ≡ 750000 = 2⁴ · 3 · 5⁶
1909² ≡ 901120 = 2¹⁴ · 5 · 11
3387² ≡ 499125 = 3 · 5³ · 11³
```

三個乘起來：`2¹⁸ · 3² · 5¹⁰ · 11⁴`，每個次方都是偶數——是完全平方 `(2⁹ · 3 · 5⁵ · 11²)²`。

```python
from math import gcd

N = 914387
a_list = [1869, 1909, 3387]
print([a * a % N for a in a_list])
a = 1869 * 1909 * 3387 % N
b = 2**9 * 3 * 5**5 * 11**2 % N
print(a * a % N == b * b % N)
d = gcd(a - b, N)
print(d, N // d)
```
```output
[750000, 901120, 499125]
True
1103 829
```
## 3.3 小心：可能得到平凡因數

課本例 3.37：N = 636683，

```
1387² ≡ 13720 = 2³ · 5 · 7³，  2774² ≡ 54880 = 2⁵ · 5 · 7³
```

相乘是平方 `(2⁴ · 5 · 7³)² = 27440²`。但 `gcd(636683, 1387 · 2774 − 27440) = 636683`——失敗了！因為 `2774 = 2 · 1387`，所以 `a = 1387 · 2774 = 2 · 1387²`，而 b 也剛好是 ±a。

```python
from math import gcd
N = 636683
a = 1387 * 2774 % N
b = 2**4 * 5 * 7**3
print(a, b, (a - b) % N, gcd(a - b, N))
```
```output
27440 27440 0 636683
```
這就是為什麼要收集 **比需要多一些** 的關係：多找幾個平方組合，總有一個 `a ≢ ±b`。

---

# 第四部分：線性代數

## 4.1 把「乘積是平方」變成方程式

設光滑數用的質數是 `p₁, …, p_t`，每個 `cᵢ = p₁^(e_i1) · ⋯ · p_t^(e_it)`。選 `uᵢ ∈ {0, 1}` 表示「第 i 個要不要選」，乘積是平方的條件是

```
對每個 j：Σᵢ uᵢ · e_ij ≡ 0 (mod 2)
```

這是 **F₂ 上的線性方程組**（t 個方程式、r 個未知數）。只要 **r > t**（關係比質數多），就一定有非零解。所以每個 cᵢ 只需要記下「次方的奇偶」這個 0/1 向量。

## 4.2 課本例 3.39：N = 9788111

在 3129 到 4700 之間找 a，使 `a² mod N` 是 50-光滑（質因數都在 {2, 3, 5, …, 47} 裡），然後用高斯消去找平方組合。

```python
from math import gcd, isqrt

N = 9788111
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

def exponents(c):
    e = []
    for p in primes:
        k = 0
        while c % p == 0:
            c //= p
            k += 1
        e.append(k)
    return e if c == 1 else None          # 不是 50-光滑就回傳 None

relations = []
for a in range(3129, 4701):
    e = exponents(a * a % N)
    if e:
        relations.append((a, e))
print(len(relations), "個關係，例如", relations[0])

# F₂ 上的高斯消去：每列記「奇偶向量」和「用到哪些關係」
rows = []
for i, (a, e) in enumerate(relations):
    vec = sum((x & 1) << j for j, x in enumerate(e))
    rows.append([vec, 1 << i])
pivots = {}
deps = []
for vec, used in rows:
    for bit in range(len(primes)):
        if vec >> bit & 1 and bit in pivots:
            pv, pu = pivots[bit]
            vec ^= pv
            used ^= pu
    if vec == 0:
        deps.append(used)                  # 找到一組乘積是平方的關係
    else:
        low = (vec & -vec).bit_length() - 1
        pivots[low] = (vec, used)

for used in deps:
    chosen = [relations[i] for i in range(len(relations)) if used >> i & 1]
    a = 1
    total = [0] * len(primes)
    for ai, e in chosen:
        a = a * ai % N
        total = [x + y for x, y in zip(total, e)]
    b = 1
    for p, k in zip(primes, total):
        b = b * pow(p, k // 2, N) % N
    d = gcd(a - b, N)
    print(len(chosen), "個關係 →", d)
    if 1 < d < N:
        print("N =", d, "×", N // d)
        break
```
```output
20 個關係，例如 (3129, [1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0])
5 個關係 → 1
3 個關係 → 9788111
3 個關係 → 9788111
3 個關係 → 9788111
5 個關係 → 1
4 個關係 → 1
5 個關係 → 2741
N = 2741 × 3571
```
前幾組可能給出 1 或 N（平凡因數），多試幾組很快就成功。

## 4.3 規模

真正分解幾百位數時，用的質數多達 **幾十萬到幾百萬個**，方程組也有幾百萬個。好在每個光滑數只有少數幾個質因數，矩陣非常 **稀疏**，可以用專門的方法（Lanczos、Wiedemann）解。

整個方法的瓶頸在第一步：**怎麼快速找到大量的光滑數**？這是下一課的二次篩法與數體篩法。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| Pollard p − 1 方法 | Pollard's p − 1 Method | p − 1 光滑時用 `gcd(a^(n!) − 1, N)` 分解 | 1.2 |
| 光滑數 | B-smooth Number | 質因數都 ≤ B | 1.4、3.2 |
| Fermat 分解法 | Fermat Factorization | 找 `N + b² = a²` | 2.1 |
| 同餘的平方差 | Congruence of Squares | `a² ≡ b² (mod N)` | 3.1 |
| 建立關係 | Relation Building | 找 `a² mod N` 是光滑數的 a | 3.2 |
| 消去 | Elimination | 用 F₂ 線性代數組出平方 | 4.1 |
| 稀疏矩陣 | Sparse Matrix | 大部分元素是 0 | 4.3 |

---

# 習題

### 題 1：Pollard p − 1

用 Pollard p − 1 方法分解 N = 1739。到第幾步成功？用 p − 1 的分解解釋。

### 題 2：Fermat 分解

用 Fermat 分解法分解 N = 5959。為什麼很快？

### 題 3：平方差

已知 `1142² ≡ 6² (mod 2911)`（自己驗證），用它分解 2911。

### 題 4：觀念

RSA 產生金鑰時，為什麼要避免 p 和 q 太接近？為什麼要避免 p − 1 是光滑數？

### 題 5：mod 4

證明：N 是奇數時，`2N + b²` 永遠不是完全平方數。

---

# 習題解答

**題 1**：

```python
from math import gcd

N = 1739
a = 2
for j in range(2, 100):
    a = pow(a, j, N)
    d = gcd(a - 1, N)
    if d > 1:
        print(j, d, N // d)
        break
```
```output
6 37 47
```
`1739 = 37 · 47`，`37 − 1 = 36 = 2² · 3²` 整除 `6! = 720`；`47 − 1 = 46 = 2 · 23` 要到 23! 才會被整除。

**題 2**：

```python
from math import isqrt
N = 5959
for b in range(1, 100):
    t = N + b * b
    a = isqrt(t)
    if a * a == t:
        print(b, a, a - b, a + b)
        break
```
```output
21 80 59 101
```
5959 = 59 · 101，兩個因數差 42，所以 b = 21 就找到。（Fermat 法要的步數大約是 `(q − p)/2`。）

**題 3**：

```python
from math import gcd
N = 2911
print(1142 * 1142 % N, 36)
print(gcd(1142 - 6, N), gcd(1142 + 6, N))
```
```output
36 36
71 41
```
**題 4**：p、q 太接近時 `(q − p)/2` 很小，Fermat 分解法幾步就成功；p − 1 光滑時 Pollard p − 1 方法很快成功。兩者都是「大數分解」的特殊情況，隨機選的大質數幾乎不會遇到，但用了奇怪的產生方式就可能中招。

**題 5**：平方數模 4 只有 0 或 1（偶數平方是 4 的倍數、奇數平方 ≡ 1）。N 奇數，所以 `2N ≡ 2 (mod 4)`，`2N + b² ≡ 2 + (0 或 1) = 2 或 3 (mod 4)`，不可能是平方數。
