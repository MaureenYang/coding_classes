# 13. 光滑數、篩法與指標演算法（Factorization II, Index Calculus）

> 對應課本：§3.7、§3.8
>
> 先備知識：第 12 課（三步驟分解法）、第 08 課（CRT）。

**這一課分成四個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 光滑數有多少 | ψ(X, B)、Canfield–Erdős–Pomerance 定理、次指數函數 L(N) |
| 第二部分 | 二次篩法 | 怎麼用「篩」一次找出一大批光滑數、課本例 3.50 |
| 第三部分 | 數體篩法 | 在更大的環裡找光滑數、L_{1/3}(N)、目前 RSA 的實際安全尺寸 |
| 第四部分 | 指標演算法 | 用光滑數解 F_p* 的 DLP，課本例 3.57 |

上一課的三步驟法（建立關係 → 消去 → gcd）中，最花時間的是 **建立關係**：要找到大量 `a² mod N` 是光滑數的 a。這一課回答兩個問題：(1) 光滑數有多常見？(2) 怎麼有效率地找到它們？

---

# 第一部分：光滑數有多少

## 1.1 ψ(X, B)

**定義**：n 的所有質因數都 ≤ B，就叫 **B-光滑**（B-smooth）。`ψ(X, B)` 是 1 < n ≤ X 中 B-光滑數的個數。

例：5-光滑數 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, …；`ψ(25, 5) = 15`。

```python
def is_smooth(n, B):
    for p in range(2, B + 1):
        while n % p == 0:
            n //= p
    return n == 1

print([n for n in range(2, 40) if is_smooth(n, 5)])
print(sum(is_smooth(n, 5) for n in range(2, 26)))
for X in (10**3, 10**5):
    for B in (10, 100):
        print(X, B, sum(is_smooth(n, B) for n in range(2, X + 1)))
```
```output
[2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 27, 30, 32, 36]
15
1000 10 140
1000 100 664
100000 10 693
100000 100 17441
```
## 1.2 Canfield–Erdős–Pomerance 定理

**定理 3.42**：令 `u = ln X / ln B`（「X 是 B 的幾次方」）。在合理的範圍內，

```
ψ(X, B) ≈ X · u^(−u)
```

也就是說，**隨機一個 ≤ X 的數是 B-光滑的機率約為 `u^(−u)`**。u 越大（B 相對 X 越小），機率掉得非常快。

## 1.3 怎麼選 B：次指數函數 L(N)

B 太小：光滑數太稀少，要試很多數。B 太大：要找的關係數（約 π(B) 個）太多，而且檢查光滑也慢。最佳的折衷落在

```
L(X) = e^(√(ln X · ln ln X))，  取 B ≈ L(N)^(1/√2)
```

**命題 3.47**：這樣大約要檢查 `L(N)^√2` 個數；如果 a 取在 √N 附近（讓 `a² − N` 只有 √N 大小，更容易光滑），可以降到約 `L(N)` 個（Remark 3.48）。

**L(X) 是次指數的**：比任何 `X^ε` 都慢，比任何 `(ln X)^k` 都快。

```python
import math

def L(bits, alpha=0.5, c=1.0):          # L_α(X) = e^(c (ln X)^α (ln ln X)^(1−α))，X = 2^bits
    lnX = bits * math.log(2)
    return c * lnX ** alpha * math.log(lnX) ** (1 - alpha) / math.log(2)   # 回傳 log₂

for bits in (100, 250, 500, 1000, 2000):
    print(f"X = 2^{bits:<5} L(X) ≈ 2^{L(bits):.1f}")
```
```output
X = 2^100   L(X) ≈ 2^24.7
X = 2^250   L(X) ≈ 2^43.1
X = 2^500   L(X) ≈ 2^65.0
X = 2^1000  L(X) ≈ 2^97.1
X = 2^2000  L(X) ≈ 2^144.5
```
和課本表 3.7 一致：`L(2¹⁰⁰⁰) ≈ 2⁹⁷`。這就是二次篩法分解 1000 位元數字的大致工作量。

---

# 第二部分：二次篩法

## 2.1 想法

要找很多 `t` 使 `F(t) = t² − N` 是 B-光滑（t 從 ⌈√N⌉ 開始往上）。笨方法：每個 F(t) 都用小質數試除。**篩法** 的聰明之處是反過來想：

> **對每個小質數 p，哪些 t 會讓 p | F(t)？**

`p | t² − N` ⟺ `t² ≡ N (mod p)`。這個同餘式只有 0 個或 2 個解 `α_p, β_p`（第 14 課的二次剩餘）。所以 **p 整除的位置是等間隔的**：`t ≡ α_p` 或 `t ≡ β_p (mod p)`，每隔 p 個就有一個。

就像埃拉托斯特尼篩法：不用逐一檢查每個數，而是對每個 p「跳著」把它的倍數劃掉。這組小質數叫做 **因子基底**（factor base）。

## 2.2 課本例 3.50：N = 221

`F(T) = T² − 221`，T 從 15 到 30，用質數 2、3、5、7（以及次方）篩：

```python
N = 221
ts = list(range(15, 31))
values = [t * t - N for t in ts]
print("原始  ", values)
remain = values[:]
for p in (2, 3, 5, 7):
    pe = p
    while pe <= max(values):
        roots = [t for t in range(pe) if (t * t - N) % pe == 0]   # t² ≡ N (mod p^e) 的解
        if not roots:
            break
        for i, t in enumerate(ts):
            if t % pe in roots:
                remain[i] //= p                 # 這一格再除掉一個 p
        pe *= p
    print(f"篩完 {p}", remain)
print("光滑的 t：", [(t, v) for t, v, r in zip(ts, values, remain) if r == 1])
```
```output
原始   [4, 35, 68, 103, 140, 179, 220, 263, 308, 355, 404, 455, 508, 563, 620, 679]
篩完 2 [1, 35, 17, 103, 35, 179, 55, 263, 77, 355, 101, 455, 127, 563, 155, 679]
篩完 3 [1, 35, 17, 103, 35, 179, 55, 263, 77, 355, 101, 455, 127, 563, 155, 679]
篩完 5 [1, 7, 17, 103, 7, 179, 11, 263, 77, 71, 101, 91, 127, 563, 31, 679]
篩完 7 [1, 1, 17, 103, 1, 179, 11, 263, 11, 71, 101, 13, 127, 563, 31, 97]
光滑的 t： [(15, 4), (16, 35), (19, 140)]
```
最後剩下 1 的位置就是 7-光滑的。實際程式會用「近似對數」代替除法（每一格加上 log p，最後看總和是否接近 log F(t)），篩一次就能處理上百萬個 t。

```python
from math import gcd, isqrt

N = 221
# 15² ≡ 4 = 2²，所以 15² ≡ 2² (mod 221)
print(15 * 15 % N, gcd(15 - 2, N), gcd(15 + 2, N))
```
```output
4 13 17
```
（課本註腳：這個小例子有個捷徑——`15² − 221 = 4` 本身就是平方。二次篩法真正的威力要在大數字上才看得出來。）

## 2.3 花費

二次篩法的工作量大約是 `L(N)^c`，c 是小常數。它曾是分解 100 位數以下最快的方法：1994 年用它分解了 129 位數的 **RSA-129**（Gardner 在 1977 年《科學美國人》專欄出的挑戰，原本估計要四京年）。

---

# 第三部分：數體篩法

## 3.1 想法

**數體篩法**（Number Field Sieve, NFS）把找光滑數的戰場搬到比 Z 更大的環。

1. 找一個整數 m 和 **次數 d 很小** 的不可約首一多項式 f，使 `f(m) ≡ 0 (mod N)`。課本例 3.53：`N = 2⁵¹² + 1`，取 `m = 2¹⁰³`、`f(x) = x⁵ + 8`，因為 `f(m) = 2⁵¹⁵ + 8 = 8(2⁵¹² + 1) ≡ 0`。
2. 在環 `Z[β] = Z[x]/(f(x))`（β 是 f 的根）裡運算。有一個「把 β 換成 m」的環同態 `Z[β] → Z/NZ`。
3. 找很多對 (a, b)，使 **兩邊都光滑**：整數 `a − bm` 是光滑數，而且 Z[β] 中的 `a − bβ` 也「光滑」（由小的質理想組成）。
4. 用線性代數讓兩邊都變成平方，透過同態得到 `X² ≡ Y² (mod N)`。

```python
f = lambda x: x**5 + 8
N = 2**512 + 1
m = 2**103
print(f(m) % N == 0)
```
```output
True
```
## 3.2 為什麼比較快

二次篩法要求光滑的數大約有 N 的 **一半位數**；數體篩法要求光滑的數大約只有 N 的位數的 **2/3 次方**。數字越小越容易光滑，所以花費從 `L_{1/2}` 降到 `L_{1/3}`。

**定理 3.55**：在合理的假設下，數體篩法的期望時間是 `L_{1/3}(N)^c`，其中

```
L_ε(X) = e^((ln X)^ε · (ln ln X)^(1−ε))，  一般數字 c ≈ 1.92（特殊形式的數 c ≈ 1.5）
```

```python
import math

def log2_L(bits, eps, c):
    lnX = bits * math.log(2)
    return c * lnX ** eps * math.log(lnX) ** (1 - eps) / math.log(2)

for bits in (512, 768, 1024, 2048, 3072):
    qs = log2_L(bits, 0.5, 1.0)
    nfs = log2_L(bits, 1 / 3, 1.923)
    print(f"{bits:5} 位元   二次篩 ≈ 2^{qs:.0f}   數體篩 ≈ 2^{nfs:.0f}")
```
```output
  512 位元   二次篩 ≈ 2^66   數體篩 ≈ 2^64
  768 位元   二次篩 ≈ 2^83   數體篩 ≈ 2^77
 1024 位元   二次篩 ≈ 2^98   數體篩 ≈ 2^87
 2048 位元   二次篩 ≈ 2^146   數體篩 ≈ 2^117
 3072 位元   二次篩 ≈ 2^184   數體篩 ≈ 2^139
```
（只是漸近公式，沒有算常數，用來比較量級。）實務上 10¹⁰⁰ 以下二次篩法較快，10¹³⁰ 以上數體篩法較快。目前公開紀錄是 2020 年用數體篩法分解的 **RSA-250**（829 位元）。這就是為什麼現在 RSA 至少要 **2048 位元**（約 112 位元的安全度），長期保護建議 3072 位元以上。

---

# 第四部分：指標演算法

## 4.1 想法

**指標演算法**（index calculus）用同樣的光滑數技巧解 F_p* 的 DLP。要解 `g^x ≡ h (mod p)`：

1. **選因子基底**：所有 ≤ B 的質數 `p₁, …, p_t`。
2. **建立關係**：試很多隨機的 i，看 `g^i mod p` 是否 B-光滑。如果 `g^i ≡ p₁^(e₁) ⋯ p_t^(e_t)`，取 log：

```
i ≡ e₁ · log_g(p₁) + ⋯ + e_t · log_g(p_t)   (mod p − 1)
```

3. **解線性方程組**：收集比 t 多一些的關係，解出每個 `log_g(pⱼ)`。（模 p − 1 不是質數，要先模 p − 1 的各個質因數解、再用 CRT 組合。）
4. **算目標**：試隨機的 k，直到 `h · g^(−k)` 是 B-光滑，`h · g^(−k) = Π pⱼ^(fⱼ)`，那

```
log_g(h) ≡ k + Σ fⱼ · log_g(pⱼ)   (mod p − 1)
```

第 3 步只做一次，之後每個新的 h 只要做第 4 步。

## 4.2 課本例 3.57：37^x ≡ 211 (mod 18443)

因子基底 {2, 3, 5}，`p − 1 = 18442 = 2 · 9221`。

```python
p, g, h = 18443, 37, 211
base = [2, 3, 5]

def exps(n):
    e = []
    for q in base:
        k = 0
        while n % q == 0:
            n //= q
            k += 1
        e.append(k)
    return e if n == 1 else None

# 課本找到的四個關係
rels = [(i, exps(pow(g, i, p))) for i in (12708, 11311, 15400, 2731)]
print(rels)

def solve_mod_prime(rows, rhs, q):            # 高斯消去，模質數 q（方程式比未知數多也可以）
    rows = [r[:] + [b] for r, b in zip(rows, rhs)]
    n = len(base)
    sol_row = []
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, len(rows)) if rows[i][c] % q), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], -1, q)
        rows[r] = [x * inv % q for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] % q:
                f = rows[i][c]
                rows[i] = [(x - f * y) % q for x, y in zip(rows[i], rows[r])]
        r += 1
    return [rows[i][-1] for i in range(n)]

A = [e for _, e in rels]
b = [i for i, _ in rels]
x2 = solve_mod_prime(A, b, 2)
x9221 = solve_mod_prime(A, b, 9221)
logs = [(a + 2 * ((c - a) * pow(2, -1, 9221) % 9221)) for a, c in zip(x2, x9221)]   # CRT 組合
print("log 2, log 3, log 5 =", logs, [pow(g, L, p) for L in logs])

k = 0
while True:
    e = exps(h * pow(g, -k, p) % p)
    if e:
        break
    k += 1
x = (k + sum(f * L for f, L in zip(e, logs))) % (p - 1)
print("k =", k, e, " x =", x, pow(g, x, p))
```
```output
[(12708, [3, 4, 1]), (11311, [3, 0, 2]), (15400, [3, 3, 1]), (2731, [3, 1, 4])]
log 2, log 3, log 5 = [5733, 15750, 6277] [2, 3, 5]
k = 76 [5, 3, 1]  x = 8500 211
```
前三個 log 的驗算（`37^log ≡ 2, 3, 5`）都對，最後解出 x，驗算 `37^x ≡ 211`。

## 4.3 花費與意義

指標演算法和二次篩法一樣是 **次指數** 時間；用數體篩法的想法可以降到 `L_{1/3}(p)`。

| 群 | 最佳的 DLP 演算法 | 安全所需大小（約 128 位元安全度） |
|---|---|---|
| F_p* | 指標演算法 / 數體篩法，次指數 | p 約 3072 位元 |
| 好的橢圓曲線 | 只有 O(√N) 的通用演算法（第 16 課 Pollard ρ） | 約 256 位元 |

這張表就是 **橢圓曲線密碼**（第 18～19 課）的動機：橢圓曲線的點 **沒有「質因數分解」這種結構**，指標演算法用不上，所以短很多的金鑰就有同樣的安全度。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| B-光滑 | B-smooth | 質因數都 ≤ B | 1.1 |
| ψ(X, B) | Smooth Number Counting Function | ≤ X 的 B-光滑數個數 | 1.1 |
| 次指數函數 L(N) | Subexponential Function | `e^(√(ln N ln ln N))` | 1.3 |
| 因子基底 | Factor Base | 用來分解的小質數集合 | 2.1 |
| 二次篩法 | Quadratic Sieve | 對每個小質數「跳著」篩出光滑的 `t² − N` | 2.1 |
| 數體篩法 | Number Field Sieve | 在 Z[β] 中找光滑數，L_{1/3} | 3.1 |
| 指標演算法 | Index Calculus | 用光滑數解 F_p* 的 DLP | 4.1 |

---

# 習題

### 題 1：ψ

算 ψ(100, 7)。

### 題 2：機率估計

用 `u^(−u)` 估計：隨機一個約 10²⁰ 的數是 10⁴-光滑的機率。再用程式在 10²⁰ 附近隨機抽樣驗證量級。

### 題 3：篩法

`N = 391`，`F(t) = t² − 391`，t = 20～30。哪些 F(t) 是 7-光滑的？能不能找到一組平方的組合並分解 391？

### 題 4：觀念

為什麼二次篩法要從 `t ≈ √N` 開始，而不是隨機的 t？

### 題 5：觀念

為什麼指標演算法不能直接用在橢圓曲線上？

---

# 習題解答

**題 1**：

```python
def is_smooth(n, B):
    for p in range(2, B + 1):
        while n % p == 0:
            n //= p
    return n == 1

print(sum(is_smooth(n, 7) for n in range(2, 101)))
```
```output
45
```
**題 2**：`u = 20 / 4 = 5`，`u^(−u) = 5⁻⁵ = 1/3125 ≈ 0.00032`。

```python
import random

def is_smooth(n, B):
    p = 2
    while p <= B and n > 1:
        while n % p == 0:
            n //= p
        p += 1
    return n == 1

random.seed(9)
trials = 20000
hits = sum(is_smooth(random.randrange(10**20, 2 * 10**20), 10**4) for _ in range(trials))
print(hits / trials, 5 ** -5)
```
```output
0.0003 0.00032
```
兩者量級吻合（u^(−u) 只是第一階近似，不能期待完全相等）。

**題 3**：

```python
from math import gcd, isqrt

def exps(n, base=(2, 3, 5, 7)):
    e = []
    for p in base:
        k = 0
        while n % p == 0:
            n //= p
            k += 1
        e.append(k)
    return e if n == 1 else None

N = 391
smooth = [(t, t * t - N, exps(t * t - N)) for t in range(20, 31) if exps(t * t - N)]
for row in smooth:
    print(row)
```
```output
(20, 9, [0, 2, 0, 0])
(21, 50, [1, 0, 2, 0])
(29, 450, [1, 2, 2, 0])
```
`t = 20` 時 `20² − 391 = 9 = 3²` 本身就是平方：`20² ≡ 3² (mod 391)`，`gcd(20 − 3, 391) = 17`，所以 `391 = 17 · 23`。

```python
from math import gcd
print(gcd(20 - 3, 391), 391 // 17)
```
```output
17 23
```
**題 4**：`t ≈ √N` 時 `t² − N` 只有大約 `2t·(t − √N)`，量級是 √N 而不是 N，**數字越小越容易光滑**。

**題 5**：指標演算法靠的是「把群元素 **分解成小質數的乘積**」，然後取 log 變成線性方程式。F_p* 的元素是整數，可以質因數分解；橢圓曲線上的點沒有對應的「小點」概念，也沒有自然的分解方式，所以建立不了關係。
