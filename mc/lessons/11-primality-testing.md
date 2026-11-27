# 11. 質數檢定（Primality Testing）

> 對應課本：§3.4
>
> 程式練習：`MC10 Miller–Rabin 質數檢定`
>
> 先備知識：第 04 課（費馬小定理、Carmichael 數）、第 10 課（RSA 需要大質數）。

**這一課分成四個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 為什麼需要質數檢定 | RSA 要隨機大質數；試除法太慢 |
| 第二部分 | 費馬檢定與它的漏洞 | 證人、偽質數、Carmichael 數 |
| 第三部分 | Miller–Rabin 檢定 | 演算法、正確性、至少 75% 是證人、課本例 3.18 與 3.19 |
| 第四部分 | 質數有多少、怎麼找 | 質數定理、1024 位元的質數要試幾次、機率檢定 vs 質數證明（AKS） |

---

# 第一部分：為什麼需要質數檢定

建 RSA 金鑰時，Bob 要兩個大約 1024 位元的 **質數**。如果他不小心挑到合數，不但自己算不出正確的 φ(N)，N 還可能有小因數而被輕易分解。

最直接的檢查是 **試除**：用 2, 3, …, √n 去除 n。但 n ≈ 2¹⁰²⁴ 時 √n ≈ 2⁵¹²——太陽燒完了都試不完。√n 步對輸入大小（log n 位元）來說是 **指數時間**。

我們要的是：**不分解 n，也能判斷它是不是質數**。第 04 課已經看到一個方向：費馬小定理可以 **證明** 一個數是合數，而且完全不用找到它的因數。

---

# 第二部分：費馬檢定與它的漏洞

## 2.1 證人

**定理 3.15（費馬小定理第二版）**：p 是質數時，對 **所有** 整數 a 都有 `a^p ≡ a (mod p)`。

**定義**：如果 `a^n ≢ a (mod n)`，就說 a 是 n 為合數的 **證人**（witness）。只要找到一個證人，n 就 **一定** 是合數。

課本的觀察：對大部分合數，絕大多數的 a 都是證人，所以隨便試幾個 a 很快就能抓到。

```python
n = 15485207                      # = 3853 · 4019
witnesses = sum(1 for a in range(1, 1000) if pow(a, n, n) != a % n)
print(witnesses)
```
```output
998
```
1 到 999 裡幾乎每個都是證人。

## 2.2 Carmichael 數：費馬檢定永遠被騙

**Carmichael 數**：合數 n，卻對 **所有** a 都滿足 `a^n ≡ a (mod n)`——也就是 **完全沒有費馬證人**。最小的是 561 = 3 · 11 · 17。

```python
def is_carmichael(n):
    if n < 3 or all(n % d for d in range(2, int(n ** 0.5) + 1)):     # 要排除質數
        return False
    return all(pow(a, n, n) == a for a in range(n))

print([n for n in range(2, 20000) if is_carmichael(n)])
```
```output
[561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841]
```
**Korselt 判準**：n 是 Carmichael 數 ⟺ n 沒有平方因數，而且對每個質因數 p，`p − 1 | n − 1`。例：561 − 1 = 560，而 2、10、16 都整除 560。已經證明 Carmichael 數 **有無限多個**（1994 年），所以不能只用費馬檢定。

---

# 第三部分：Miller–Rabin 檢定

## 3.1 關鍵觀察

**命題 3.16**：p 是奇質數，寫成 `p − 1 = 2^k · q`（q 是奇數）。對任何 p ∤ a，下面兩件事 **至少有一件** 成立：

1. `a^q ≡ 1 (mod p)`；
2. 數列 `a^q, a^(2q), a^(4q), …, a^(2^(k−1)·q)` 裡 **有一個 ≡ −1 (mod p)**。

**證明**：看數列 `a^q, a^(2q), …, a^(2^k · q)`，每一項是前一項的平方，最後一項是 `a^(p−1) ≡ 1`（費馬）。找第一個等於 1 的項：
- 如果是第一項，就是情況 1。
- 否則它前面那一項 b 滿足 `b² ≡ 1` 但 `b ≢ 1`。**模質數時 `b² ≡ 1` 只有 b ≡ ±1 兩個解**（因為 `p | (b − 1)(b + 1)`，由命題 1.20 p 整除其中一個），所以 `b ≡ −1`，就是情況 2。

模合數時，1 的平方根可以不只 ±1（第 08 課：模 pq 有 4 個平方根），這就是 Miller–Rabin 能抓到 Carmichael 數的原因。

## 3.2 演算法

**Miller–Rabin 證人**：n 是奇數，`n − 1 = 2^k · q`。a（`gcd(a, n) = 1`）如果同時滿足

```
(a) a^q ≢ 1 (mod n)，且
(b) 對所有 i = 0, 1, …, k − 1，a^(2^i · q) ≢ −1 (mod n)
```

就叫 Miller–Rabin 證人。由命題 3.16，**有證人 ⇒ n 一定是合數**。

```python
def mr_witness(a, n):
    """a 是不是 n 為合數的 Miller–Rabin 證人？"""
    q, k = n - 1, 0
    while q % 2 == 0:
        q //= 2
        k += 1
    x = pow(a, q, n)
    if x == 1 or x == n - 1:
        return False
    for _ in range(k - 1):
        x = x * x % n
        if x == n - 1:
            return False
    return True

# 課本例 3.18：n = 561、a = 2
n = 561
print(n - 1, [pow(2, 35 * 2 ** i, n) for i in range(5)], mr_witness(2, n))
```
```output
560 [263, 166, 67, 1, 1] True
```
`2³⁵ ≡ 263`，平方後 166、67、1。數列裡沒有 −1（560），但出現了 1——而 67 是 1 的一個「不是 ±1 的平方根」。所以 2 是證人，561 是合數。

## 3.3 至少 75% 的 a 是證人

**命題 3.17**：n 是奇合數時，1 到 n − 1 裡 **至少 75%** 的 a 是 Miller–Rabin 證人。

所以隨機試 t 個 a 都沒找到證人，而 n 其實是合數的機會大約是 `(1/4)^t`。試 50 次就是 `2⁻¹⁰⁰`，比硬體出錯的機率還小。（課本註腳：嚴格來說要用條件機率計算，結果大約要再乘上 ln n，第 16 課的貝氏定理會談到。）

```python
def mr_witness(a, n):
    q, k = n - 1, 0
    while q % 2 == 0:
        q //= 2
        k += 1
    x = pow(a, q, n)
    if x in (1, n - 1):
        return False
    for _ in range(k - 1):
        x = x * x % n
        if x == n - 1:
            return False
    return True

import random
random.seed(5)
for n in (561, 1105, 1373653, 172947529, 3215031751):
    sample = [random.randrange(1, n) for _ in range(5000)]
    w = sum(mr_witness(a, n) for a in sample)
    print(n, f"{w / len(sample):.1%}")
```
```output
561 98.2%
1105 97.5%
1373653 81.1%
172947529 87.5%
3215031751 75.9%
```
（每個 n 隨機抽 5000 個 a 估計比例。）全都超過 75%，Carmichael 數 561、1105 更是接近 100%。最後一個 3215031751 很狡猾：它騙得過底數 2、3、5、7（所以「只試小底數」很危險），但隨機的 a 大多數還是證人。

## 3.4 課本例 3.19：小心挑錯的 a

`n = 172947529`，`n − 1 = 2³ · 21618441`。

```python
def mr_witness(a, n):
    q, k = n - 1, 0
    while q % 2 == 0:
        q //= 2
        k += 1
    x = pow(a, q, n)
    if x in (1, n - 1):
        return False
    for _ in range(k - 1):
        x = x * x % n
        if x == n - 1:
            return False
    return True

n, q = 172947529, 21618441
for a in (17, 3, 23):
    print(a, [pow(a, q * 2 ** i, n) for i in range(4)], mr_witness(a, n))
```
```output
17 [1, 1, 1, 1] False
3 [172947528, 1, 1, 1] False
23 [40063806, 2257065, 1, 1] True
```
17 和 3 都「通過」了（不是證人），23 才是證人：`23^(4q) ≡ 1`，但前一項 2257065 不是 ±1。這個 n 其實是 Carmichael 數。教訓：**通過幾次不代表是質數，要用隨機的 a 多試幾次**。

## 3.5 完整的檢定

```python
import random

def is_probable_prime(n, rounds=40):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    q, k = n - 1, 0
    while q % 2 == 0:
        q //= 2
        k += 1
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, q, n)
        if x in (1, n - 1):
            continue
        for _ in range(k - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False                     # 找到證人：一定是合數
    return True                              # 很可能是質數

random.seed(1)
print([n for n in range(90, 120) if is_probable_prime(n)])
print(is_probable_prime(2**127 - 1), is_probable_prime(2**128 + 1), is_probable_prime(561))
```
```output
[97, 101, 103, 107, 109, 113]
True False False
```
> 🔍 **確定性版本**：對 64 位元以內的 n，只要用固定的底數 `a ∈ {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}` 檢查，就 **保證** 結果正確（已有人逐一驗證過所有可能的反例）。程式練習 MC10 就用這個版本，搭配第 03 課的 128 位元乘法避免溢位。

---

# 第四部分：質數有多少、怎麼找

## 4.1 質數定理

`π(X)` 表示不超過 X 的質數個數。

**定理 3.20（質數定理）**：`lim π(X) / (X / ln X) = 1`。

白話：**1 到 X 之間大約有 X / ln X 個質數**，或者說「N 附近的數是質數的機率大約是 1 / ln N」。

課本例 3.21：900000 到 1000000 之間預估 `10⁶/ln 10⁶ − 9×10⁵/ln(9×10⁵) ≈ 6737.6` 個，實際是 7224 個。

```python
import math

def count_primes(lo, hi):
    sieve = bytearray([1]) * (hi + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(hi ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return sum(sieve[lo:hi + 1])

print(count_primes(900000, 1000000))
print(round(10**6 / math.log(10**6) - 9 * 10**5 / math.log(9 * 10**5), 2))
for X in (10**3, 10**5, 10**7):
    pi = count_primes(2, X)
    print(X, pi, round(pi / (X / math.log(X)), 3))
```
```output
7224
6737.62
1000 168 1.161
100000 9592 1.104
10000000 664579 1.071
```
比值慢慢趨近 1（收斂得很慢；用 `Li(X)` 當近似會準得多）。

## 4.2 找一個 1024 位元的質數要試幾次

N ≈ 2¹⁰²⁴ 是質數的機率約 `1 / ln(2¹⁰²⁴) = 1 / (1024 · ln 2) ≈ 0.14%`，平均試 **約 700 個** 數。

**聰明一點**（課本例 3.22）：只考慮和 `2·3·5·7·11 = 2310` 互質的數，例如 `N = 2310K + 1139`。這樣的 N 是質數的機率提高到 `(2/1)(3/2)(5/4)(7/6)(11/10) / ln N ≈ 4.8 / ln N ≈ 0.67%`，平均 **約 150 個** 就夠。而且大部分候選在試除小質數時就被淘汰，真正要跑 Miller–Rabin 的很少。

```python
import math
ln_n = 1024 * math.log(2)
print(f"{1 / ln_n:.2%}  平均試 {ln_n:.0f} 個")
boost = (2 / 1) * (3 / 2) * (5 / 4) * (7 / 6) * (11 / 10)
print(f"{boost:.2f}  {boost / ln_n:.2%}  平均試 {ln_n / boost:.0f} 個")
# π(2^1024) − π(2^1023) ≈ 2^1023 · (2/1024 − 1/1023) / ln 2，用 log 避免浮點數溢位
print(f"1024 位元的質數約有 2^{1023 + math.log2((2 / 1024 - 1 / 1023) / math.log(2)):.2f} 個")
```
```output
0.14%  平均試 710 個
4.81  0.68%  平均試 147 個
1024 位元的質數約有 2^1013.53 個
```
1024 位元的質數有大約 2¹⁰¹³ 個——多到不可能被列舉或重複挑到。

> 🔍 **黎曼猜想**：質數定理的誤差項有多大，和黎曼 ζ 函數的零點位置有關。黎曼猜想（另一個百萬美元問題）等價於 `|π(X) − Li(X)| = O(√X · ln X)`。

## 4.3 機率檢定 vs 質數證明

Miller–Rabin 給的是「**很可能** 是質數」（probable prime），不是證明。

| 方法 | 能證明質數嗎 | 時間 |
|---|---|---|
| 試除法 | 能 | O(√n)，指數時間 |
| Miller–Rabin | 不能（只能證明合數） | 每次 O((log n)³)，非常快 |
| Miller–Rabin 試所有 `a ≤ 2(ln n)²` | 能，**如果廣義黎曼猜想成立**（命題 3.24） | 多項式時間 |
| **AKS**（Agrawal–Kayal–Saxena，2002） | 能，**無條件** | `O((ln n)^(6+ε))`，多項式時間，但實務上比 Miller–Rabin 慢很多 |

**定理 3.25（AKS）**：質數判定是多項式時間可解的。這是 2002 年的重大突破——兩個印度大學生和他們的指導教授完成的。

實務上：產生金鑰用 Miller–Rabin（幾十輪）；需要絕對證明時用橢圓曲線質數證明（ECPP）等方法。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 質數檢定 | Primality Test | 判斷 n 是否為質數 | 1 |
| 證人 | Witness | 能證明 n 是合數的 a | 2.1 |
| 偽質數 | Pseudoprime | 騙過某個底數的合數 | 2.1 |
| Carmichael 數 | Carmichael Number | 騙過所有底數的費馬檢定 | 2.2 |
| Miller–Rabin 檢定 | Miller–Rabin Test | 看 1 的平方根是否只有 ±1 | 3.2 |
| 很可能是質數 | Probable Prime | 通過機率檢定的數 | 3.5 |
| 質數定理 | Prime Number Theorem | `π(X) ≈ X / ln X` | 4.1 |
| AKS 檢定 | AKS Primality Test | 無條件的多項式時間質數判定 | 4.3 |

---

# 習題

### 題 1：手算 Miller–Rabin

用 a = 2 對 n = 221 做 Miller–Rabin 檢定，寫出每一步。

### 題 2：Korselt

用 Korselt 判準驗證 1105 = 5 · 13 · 17 是 Carmichael 數。

### 題 3：觀念

為什麼 Miller–Rabin 檢定說「是合數」時一定正確，說「可能是質數」時卻可能錯？

### 題 4：機率

如果每次試驗至少有 75% 的機率抓到合數，試 20 次都沒抓到的機率最多是多少？

### 題 5：質數定理

估計 10¹⁰⁰ 附近（10¹⁰⁰ 到 10¹⁰⁰ + 10⁶）大約有幾個質數。

---

# 習題解答

**題 1**：`220 = 2² · 55`。

```python
n, a = 221, 2
q, k = 55, 2
x = pow(a, q, n)
print(x)
print(x * x % n)
```
```output
128
30
```
`2⁵⁵ ≡ 128`，不是 ±1；平方得 `30`，也不是 −1（220）。數列結束，所以 2 是證人，221 = 13 · 17 是合數。

**題 2**：1105 沒有平方因數；`1104 / 4 = 276`、`1104 / 12 = 92`、`1104 / 16 = 69`，三個 `p − 1` 都整除 `n − 1`，所以是 Carmichael 數。

```python
n = 1105
print([(p, (n - 1) % (p - 1)) for p in (5, 13, 17)])
print(all(pow(a, n, n) == a for a in range(n)))
```
```output
[(5, 0), (13, 0), (17, 0)]
True
```
**題 3**：「是合數」的判斷來自命題 3.16：質數 **一定** 滿足那兩個條件之一，所以只要找到一個不滿足的 a，n 必是合數——這是證明。反過來，合數也可能讓某些 a 滿足條件（這些 a 叫「強說謊者」），所以沒找到證人只能說「很可能是質數」。

**題 4**：最多 `(1/4)²⁰ = 2⁻⁴⁰ ≈ 9 × 10⁻¹³`。

**題 5**：密度約 `1 / ln(10¹⁰⁰) = 1 / 230.26`，所以 10⁶ 個數裡約 `10⁶ / 230.26 ≈ 4343` 個質數。
