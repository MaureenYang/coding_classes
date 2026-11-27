# 16. 機率、碰撞演算法與 Pollard ρ（Probability, Collisions, Pollard's ρ）

> 對應課本：§4.3～§4.5
>
> 程式練習：`MC11 整數分解`（用 Pollard ρ）
>
> 先備知識：第 07 課（嬰兒步巨人步）、第 15 課（計數）。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 機率基礎 | 樣本空間、事件、獨立、條件機率、貝氏公式、隨機變數與期望值 |
| 第二部分 | 生日悖論與碰撞定理 | 為什麼 √N 次就會碰撞 |
| 第三部分 | 碰撞演算法的應用 | 隨機版 DLP 碰撞、中間相遇攻擊（雙重加密為什麼不安全） |
| 第四部分 | Pollard ρ 方法 | 只用 O(1) 記憶體找碰撞、Floyd 找環法 |
| 第五部分 | 用 ρ 解 DLP 與分解 | 課本例 4.51、Pollard ρ 分解法 |

---

# 第一部分：機率基礎

## 1.1 樣本空間、事件

| 用語 | 意思 | 例：擲兩顆骰子 |
|---|---|---|
| **樣本空間** Ω | 所有可能的結果（有限集合） | 36 個 `(n, m)` |
| **機率函數** | 每個結果 ω 有 `Pr(ω) ≥ 0`，總和是 1 | 每個 1/36 |
| **事件** E | Ω 的子集合 | 「至少一個 6」= 11 個結果 |
| `Pr(E)` | E 中結果的機率總和 | 11/36 |

**補事件**：`Pr(Eᶜ) = 1 − Pr(E)`。「至少一個」的問題通常用補事件算比較快：至少一個 6 = 1 − 兩個都不是 6 = `1 − (5/6)² = 11/36`。

## 1.2 獨立與條件機率

**獨立**：`Pr(E ∩ F) = Pr(E) · Pr(F)`。

**條件機率**：已知 E 發生時 F 發生的機率

```
Pr(F | E) = Pr(F ∩ E) / Pr(E)
```

例：從一副牌連抽兩張（不放回），第一張是 K 的條件下第二張也是 K 的機率是 3/51，不是 4/52——兩個事件不獨立。

## 1.3 貝氏公式

**命題 4.24**：

```
Pr(E) = Pr(E | F) Pr(F) + Pr(E | Fᶜ) Pr(Fᶜ)               （全機率公式）
Pr(F | E) = Pr(E | F) Pr(F) / Pr(E)                          （貝氏公式）
```

**和密碼學的關係**：第 11 課的 Miller–Rabin 檢定。我們知道「n 是合數時，一次測試抓到它的機率 ≥ 3/4」，也就是 `Pr(通過 | 合數) ≤ 1/4`。但我們真正想知道的是反過來的 `Pr(合數 | 通過 t 次)`——這要用貝氏公式，而且和「隨機挑的 n 本來是質數的機率 ≈ 1/ln n」有關。

```python
import math

def prob_composite_given_pass(bits, t):
    prior_prime = 1 / (bits * math.log(2))          # 質數定理：隨機數是質數的機率
    prior_comp = 1 - prior_prime
    pass_if_comp = 0.25 ** t                         # 最壞情況
    return pass_if_comp * prior_comp / (pass_if_comp * prior_comp + 1 * prior_prime)

for t in (1, 5, 10, 20, 40):
    print(t, f"{prob_composite_given_pass(1024, t):.2e}", f"{0.25 ** t:.2e}")
```
```output
1 9.94e-01 2.50e-01
5 4.09e-01 9.77e-04
10 6.75e-04 9.54e-07
20 6.45e-10 9.09e-13
40 5.86e-22 8.27e-25
```
結果大約是 `(1/4)^t × ln n`：先天上隨機數大多是合數，所以要多測幾次才能把信心拉回來（課本第 3 章的註腳、習題 4.29）。

**監獄悖論**（課本例 4.26，也就是蒙提霍爾問題）：答案取決於「透露資訊的人用什麼策略」——條件機率的直覺常常是錯的，要老實地列出所有情況。

```python
import random
random.seed(1)
stay = switch = 0
trials = 100000
for _ in range(trials):
    car, pick = random.randrange(3), random.randrange(3)
    opened = random.choice([d for d in range(3) if d != car and d != pick])   # 主持人知道車在哪
    other = next(d for d in range(3) if d != pick and d != opened)
    stay += pick == car
    switch += other == car
print(round(stay / trials, 3), round(switch / trials, 3))
```
```output
0.335 0.665
```
## 1.4 蒙地卡羅演算法

**蒙地卡羅演算法**：輸出不保證正確，但錯的機率可以控制。例：Miller–Rabin——說「合數」一定對，說「質數」有小機率錯。重複執行可以把錯誤機率壓到任意小。

## 1.5 隨機變數與期望值

**隨機變數** X：把結果對應到一個數。**期望值** `E(X) = Σ x · Pr(X = x)`。

例：擲一顆骰子直到出現 6，期望擲幾次？每次成功機率 p = 1/6，期望值是 `1/p = 6`（幾何分布）。後面分析演算法時常問「期望要幾步才成功」。

---

# 第二部分：生日悖論與碰撞定理

## 2.1 生日悖論

40 個人裡：
- 有人和 **你** 同一天生日的機率：`1 − (364/365)⁴⁰ ≈ 10.4%`。
- **某兩個人** 同一天生日的機率：`1 − (365/365)(364/365)⋯(326/365) ≈ 89.1%`。

差這麼多，因為第二個問題要比較的是 **所有配對**，配對數是 `C(40, 2) = 780`。

```python
def someone_has_yours(n):
    return 1 - (364 / 365) ** n

def some_pair(n):
    p = 1.0
    for i in range(n):
        p *= (365 - i) / 365
    return 1 - p

print(f"{someone_has_yours(40):.3f} {some_pair(40):.3f}")
print(min(n for n in range(1, 400) if some_pair(n) > 0.5), min(n for n in range(1, 400) if someone_has_yours(n) > 0.5))
```
```output
0.104 0.891
23 253
```
23 人就有過半機率兩人同生日；要有過半機率「有人和你同生日」卻要 253 人。

## 2.2 碰撞定理

**定理 4.38**：甕裡有 N 顆球，其中 n 顆紅色。每次隨機抽一顆（放回），抽 m 次，至少抽到一顆紅球的機率

```
Pr = 1 − (1 − n/N)^m ≥ 1 − e^(−mn/N)
```

**應用**：Bob 先選 n 個元素做第一張表（「紅球」），再隨機抽 m 個做第二張表，兩表有共同元素的機率約 `1 − e^(−mn/N)`。取 `m = n ≈ √N`，機率約 `1 − 1/e ≈ 63%`；要 99.99% 只要 `n ≈ 3√N`。

```python
import math
N = 10**10
n = m = 100000
print(round(1 - (1 - n / N) ** m, 6), round(1 - math.exp(-m * n / N), 6))   # 課本例 4.40
for target in (0.5, 0.9999):
    k = math.sqrt(-math.log(1 - target))           # n = m = k·√N
    print(target, round(k, 3), "√N")
```
```output
0.632122 0.632121
0.5 0.833 √N
0.9999 3.035 √N
```
**結論**：在 N 個元素中找碰撞，大約只要 **√N** 次，而不是 N 次。這是所有「平方根演算法」的來源：嬰兒步巨人步（第 07 課）、本課的 Pollard ρ、雜湊函數的生日攻擊（第 26 課：n 位元的雜湊只有 n/2 位元的抗碰撞安全）。

---

# 第三部分：碰撞演算法的應用

## 3.1 隨機版的 DLP 碰撞（命題 4.44）

解 `h^x = b`，h 的階是 N：隨機選 y₁, y₂, …，算 `h^(yᵢ)` 做第一張表；隨機選 z₁, z₂, …，算 `b · h^(zⱼ)` 做第二張表。一旦 `h^(yᵢ) = b · h^(zⱼ)`，就有 `x = yᵢ − zⱼ`。由碰撞定理，兩張表各約 √N 個就很可能碰到。

課本例 4.45：在 F₆₅₉ 中解 `2^x = 390`。

```python
import random
random.seed(42)
p, h, b, N = 659, 2, 390, 658
table = {}
for _ in range(40):                       # 約 1.5·√658
    y = random.randrange(N)
    table[pow(h, y, p)] = y
for tries in range(1, 200):
    z = random.randrange(N)
    v = b * pow(h, z, p) % p
    if v in table:
        x = (table[v] - z) % N
        print(tries, table[v], z, x, pow(h, x, p))
        break
```
```output
19 223 46 177 390
```
## 3.2 中間相遇攻擊：雙重加密為什麼不安全

假設某個對稱密碼的金鑰是 k 位元，太短。直覺的補救是 **加密兩次**：`c = e_{k₂}(e_{k₁}(m))`，以為金鑰變成 2k 位元。

**中間相遇攻擊**（meet-in-the-middle）：Eve 有一組 `(m, c)`。
1. 對所有 k₁ 算 `e_{k₁}(m)`，存成表（2^k 筆）。
2. 對所有 k₂ 算 `d_{k₂}(c)`，查表。
3. 碰撞 `e_{k₁}(m) = d_{k₂}(c)` 就是候選金鑰對。

總共約 `2 · 2^k` 次運算——**雙重加密只多了 1 位元的安全度**，不是 k 位元。這就是為什麼 DES 的強化版是 **三重** DES（3DES），而不是雙重。

```python
import random

# 一個玩具密碼：16 位元的區塊、10 位元的金鑰
def enc(k, m):
    for r in range(4):
        m = ((m ^ (k * 2654435761 >> r & 0xFFFF)) * 40503 + r) & 0xFFFF
        m = ((m << 5) | (m >> 11)) & 0xFFFF
    return m

def dec(k, c):
    inv = pow(40503, -1, 1 << 16)
    for r in reversed(range(4)):
        c = ((c >> 5) | (c << 11)) & 0xFFFF
        c = ((c - r) * inv) & 0xFFFF
        c ^= (k * 2654435761 >> r) & 0xFFFF
    return c

random.seed(7)
k1, k2 = random.randrange(1024), random.randrange(1024)
pairs = [(m, enc(k2, enc(k1, m))) for m in (1234, 4321)]
print(dec(k1, dec(k2, pairs[0][1])) == 1234)

m, c = pairs[0]
middle = {}
for a in range(1024):
    middle.setdefault(enc(a, m), []).append(a)
cands = [(a, b) for b in range(1024) for a in middle.get(dec(b, c), [])]
cands = [(a, b) for a, b in cands if enc(b, enc(a, pairs[1][0])) == pairs[1][1]]   # 用第二組過濾
print(len(cands), (k1, k2) in cands, "嘗試了", 2 * 1024, "次，而不是", 1024 * 1024, "次")
```
```output
True
1 True 嘗試了 2048 次，而不是 1048576 次
```
---

# 第四部分：Pollard ρ 方法

## 4.1 碰撞演算法的缺點：記憶體

嬰兒步巨人步和上面的碰撞法都要存 **√N 個元素**。N ≈ 2¹⁶⁰ 時，√N = 2⁸⁰ 個元素——記憶體才是真正的瓶頸。Pollard（1974）的想法：**用一個「看起來隨機」的函數一直迭代，碰撞自己找上門**，幾乎不用記憶體。

## 4.2 ρ 的形狀

有限集合 S（N 個元素）上的函數 f，從 x₀ 開始迭代 `x_{i+1} = f(xᵢ)`。因為 S 有限，數列 **一定會重複**；一旦重複就進入一個環。畫出來像希臘字母 **ρ**：一段「尾巴」（長度 T）接一個「環」（長度 M）。

**定理 4.47**：如果 f 夠隨機，`T + M` 的期望值約 `√(πN/2) ≈ 1.25√N`。（又是生日悖論。）

## 4.3 Floyd 找環法：龜兔賽跑

不想存整個數列，怎麼偵測重複？同時走兩個指標：**烏龜** 每次走一步（`xᵢ`），**兔子** 每次走兩步（`y_i = x_{2i}`）。兩者進入環之後，兔子每次多追一步，**一定會追上**：存在 `1 ≤ i < T + M` 使 `x_{2i} = xᵢ`。

```python
def rho_shape(f, x0):
    seen = {}
    x, i = x0, 0
    while x not in seen:
        seen[x] = i
        x, i = f(x), i + 1
    T = seen[x]                   # 尾巴長度
    M = i - T                     # 環長度
    return T, M

def floyd(f, x0):
    x, y, i = f(x0), f(f(x0)), 1
    while x != y:
        x, y, i = f(x), f(f(y)), i + 1
    return i

N = 10007
f = lambda x: (x * x + 1) % N
T, M = rho_shape(f, 2)
print(T, M, T + M, round((3.14159 * N / 2) ** 0.5, 1))
print(floyd(f, 2))
```
```output
39 5 44 125.4
40
```
Floyd 法在第 i 步找到 `x_{2i} = xᵢ`，i 小於 T + M，而且 **只用了兩個變數**。

---

# 第五部分：用 ρ 解 DLP 與分解

## 5.1 Pollard ρ 解 DLP

要解 `g^t = a`（在 F_p*）。用一個能「記帳」的混合函數：

```
f(x) = g · x    如果 0 ≤ x < p/3
       x²       如果 p/3 ≤ x < 2p/3
       a · x    如果 2p/3 ≤ x < p
```

從 x₀ = 1 開始，每個 xᵢ 都能寫成 `g^(αᵢ) · a^(βᵢ)`，指數跟著更新（乘 g：α+1；平方：α、β 都乘 2；乘 a：β+1，指數都 mod p − 1）。用 Floyd 法找到 `xᵢ = x_{2i}`，就得到

```
g^(α) a^(β) = g^(γ) a^(δ)   ⇒   g^(α − γ) = a^(δ − β)
```

再解 `(δ − β) · t ≡ α − γ (mod p − 1)`，可能有 gcd 個解，逐一驗證。

課本例 4.51：`19^t ≡ 24717 (mod 48611)`。

```python
from math import gcd

p, g, a = 48611, 19, 24717
N = p - 1

def step(x, al, be):
    if x < p // 3:
        return g * x % p, (al + 1) % N, be
    if x < 2 * p // 3:
        return x * x % p, 2 * al % N, 2 * be % N
    return a * x % p, al, (be + 1) % N

x, al, be = 1, 0, 0
y, ga, de = 1, 0, 0
i = 0
while True:
    x, al, be = step(x, al, be)
    y, ga, de = step(*step(y, ga, de))
    i += 1
    if x == y:
        break
print(i, x, (al, be, ga, de))

u, v = (al - ga) % N, (de - be) % N        # g^u = a^v
d = gcd(v, N)
print("g^", u, "= a^", v, " gcd =", d)
# 解 v·t ≡ u (mod N)：先除以 d，再試 d 個可能
t0 = (u // d) * pow(v // d, -1, N // d) % (N // d)
sols = [t0 + k * (N // d) for k in range(d) if pow(g, t0 + k * (N // d), p) == a]
print(sols)
```
```output
548 33252 (12133, 20155, 47273, 46665)
g^ 13470 = a^ 26510  gcd = 10
[37869]
```
和課本一樣在第 548 步碰撞，最後的答案 37869。

## 5.2 Pollard ρ 分解法

同樣的想法也能 **分解整數**。N = pq，迭代 `x ↦ x² + c (mod N)`。我們看不到「模 p」的數列，但它也在默默地走一個 ρ（只有 p 個可能值，大約 √p 步就重複）。重複時 `xᵢ ≡ x_{2i} (mod p)`，所以 **`gcd(x_{2i} − xᵢ, N)` 會冒出 p**。

```python
from math import gcd

def pollard_rho(N, c=1):
    f = lambda x: (x * x + c) % N
    x, y, d, steps = 2, 2, 1, 0
    while d == 1:
        x, y = f(x), f(f(y))
        d = gcd(abs(x - y), N)
        steps += 1
    return (d if d != N else None), steps

for N in (8051, 10403, 1000000016000000063, 2**64 + 1):
    d, steps = pollard_rho(N)
    print(N, d, N // d if d else None, steps)
```
```output
8051 97 83 3
10403 101 103 9
1000000016000000063 1000000007 1000000009 27573
18446744073709551617 274177 67280421310721 808
```
`1000000016000000063 = 1000000007 × 1000000009`，兩個因數約 10⁹，ρ 只走了大約 √(10⁹) 這個量級的步數。花費是 **O(√p)**，p 是 N 最小的質因數——所以它適合找「中等大小」的因數；對 RSA 的 N（p 約 2¹⁰²⁴）完全無效。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 樣本空間 / 事件 | Sample Space / Event | 所有結果 / 結果的集合 | 1.1 |
| 條件機率 | Conditional Probability | 已知 E 時 F 的機率 | 1.2 |
| 貝氏公式 | Bayes's Formula | 把條件反過來算 | 1.3 |
| 蒙地卡羅演算法 | Monte Carlo Algorithm | 可能出錯、但錯誤機率可控 | 1.4 |
| 期望值 | Expected Value | 加權平均 | 1.5 |
| 生日悖論 | Birthday Paradox | √N 個就容易碰撞 | 2.1 |
| 中間相遇攻擊 | Meet-in-the-Middle Attack | 從兩端各算一半找碰撞 | 3.2 |
| Pollard ρ | Pollard's ρ Method | 迭代隨機函數、不用記憶體找碰撞 | 4.1 |
| Floyd 找環法 | Floyd's Cycle Finding | 龜兔賽跑 | 4.3 |

---

# 習題

### 題 1：生日

一個班 30 人，至少兩人同一天生日的機率？

### 題 2：雜湊碰撞

一個 64 位元的雜湊函數，大約要算幾個雜湊值，才有 50% 機率找到碰撞？

### 題 3：貝氏

某種病的盛行率是 1%。檢驗的靈敏度 99%（有病時 99% 陽性）、偽陽性 5%。驗出陽性時真的有病的機率是多少？

### 題 4：Pollard ρ 分解

用 Pollard ρ（`x² + 1`、從 2 開始）分解 N = 455459。

### 題 5：觀念

為什麼「加密兩次」不會讓金鑰長度加倍？

---

# 習題解答

**題 1**：

```python
p = 1.0
for i in range(30):
    p *= (365 - i) / 365
print(round(1 - p, 3))
```
```output
0.706
```
**題 2**：大約 `1.177 · √(2⁶⁴) = 1.177 · 2³² ≈ 50 億` 個。

```python
import math
print(f"{math.sqrt(-math.log(0.5) * 2) * 2**32:.3e}")
```
```output
5.057e+09
```
（這裡的常數是 `√(2 ln 2) ≈ 1.177`：單一張表內兩兩比較，和兩張表比較的常數略有不同。）

**題 3**：

```python
prior = 0.01
pos_if_sick, pos_if_well = 0.99, 0.05
p_pos = pos_if_sick * prior + pos_if_well * (1 - prior)
print(round(pos_if_sick * prior / p_pos, 4))
```
```output
0.1667
```
只有約 17%——因為先天盛行率很低，大部分陽性是偽陽性。（和 Miller–Rabin 的貝氏分析同一個道理。）

**題 4**：

```python
from math import gcd
N = 455459
f = lambda x: (x * x + 1) % N
x, y, d = 2, 2, 1
while d == 1:
    x, y = f(x), f(f(y))
    d = gcd(abs(x - y), N)
print(d, N // d)
```
```output
743 613
```
**題 5**：中間相遇攻擊：從明文往前加密一次、從密文往回解密一次，兩邊在「中間值」碰面。工作量是 `2 · 2^k` 而不是 `2^(2k)`，只等於多了 1 位元的金鑰。（代價是要存 2^k 筆資料。）
