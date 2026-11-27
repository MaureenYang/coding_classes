# 17. 資訊理論與計算複雜度（Information Theory, P vs NP）

> 對應課本：§4.6、§4.7
>
> 先備知識：第 05 課（一次性密碼本）、第 16 課（機率、條件機率）。

**這一課分成四個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 完全保密 | Shannon 的定義、金鑰至少要和明文一樣多、一次性密碼本是完全保密的 |
| 第二部分 | 熵 | 資訊量怎麼算、熵的性質、條件熵與金鑰模糊度 |
| 第三部分 | 自然語言的冗餘 | 英文每個字母只有約 1～1.5 位元的資訊、唯一解距離 |
| 第四部分 | 計算複雜度 | P、NP、NP 完全；為什麼密碼學需要「平均情況」的困難 |

1948～49 年，Claude Shannon 的兩篇論文奠定了現代密碼學的數學基礎：完全保密的定義、自然語言的熵、用機率證明安全性。這一課介紹其中最核心的想法，以及「困難」在計算理論中的意義。

---

# 第一部分：完全保密

## 1.1 定義

把明文、密文、金鑰都看成 **隨機變數** M、C、K（明文有自己的機率分布，例如英文信件；金鑰隨機選）。

**定義**：如果對所有明文 m 和密文 c

```
Pr(M = m | C = c) = Pr(M = m)
```

就說密碼系統是 **完全保密**（perfect secrecy）的：**看到密文之後，Eve 對明文的猜測完全沒有改變**。

由貝氏公式，等價於 `Pr(C = c | M = m) = Pr(C = c)`：不管明文是什麼，看到某個密文的機率都一樣。

## 1.2 金鑰至少要和明文一樣多

**命題 4.54**：完全保密 ⇒ `#K ≥ #M`。

**證明**：固定一個會出現的密文 c。完全保密要求每個明文 m 都有正的機率加密成 c，所以每個 m 都至少有一把金鑰 `k_m` 使 `e_{k_m}(m) = c`。不同的 m 用的金鑰一定不同（同一把金鑰是一對一的，不能把兩個明文都加密成 c），所以金鑰至少有 #M 把。

**這就是完全保密不實用的原因**：要用一次性密碼本傳 1 GB 的資料，就要事先安全地交換 1 GB 的金鑰。

## 1.3 什麼時候完全保密

**定理 4.55**：如果 `#K = #M = #C`，則系統完全保密 **若且唯若**：
1. 每把金鑰的機率都一樣；
2. 對任何明文 m、密文 c，**恰好有一把** 金鑰把 m 加密成 c。

**一次性密碼本**（例 4.56）：n 位元的明文、金鑰、密文，`c = m ⊕ k`。給定 m 和 c，唯一的金鑰是 `k = m ⊕ c`；金鑰均勻隨機——兩個條件都成立，所以完全保密。

**每個字母用新的隨機移位的凱撒密碼**（例 4.52）也一樣是完全保密的。

```python
from fractions import Fraction
from collections import defaultdict

# 3 位元的一次性密碼本：明文分布不均勻，金鑰均勻
pm = {0b000: Fraction(1, 2), 0b101: Fraction(1, 4), 0b111: Fraction(1, 4)}
keys = range(8)
joint = defaultdict(Fraction)            # Pr(M = m, C = c)
for m, p in pm.items():
    for k in keys:
        joint[(m, m ^ k)] += p * Fraction(1, 8)
pc = defaultdict(Fraction)
for (m, c), p in joint.items():
    pc[c] += p
ok = all(joint[(m, c)] / pc[c] == pm[m] for m in pm for c in range(8))
print(ok, pc[0b011], joint[(0b000, 0b011)] / pc[0b011])
```
```output
True 1/8 1/2
```
不管看到哪個密文，明文是 000 的機率都還是 1/2——密文沒有洩漏任何資訊。

---

# 第二部分：熵

## 2.1 定義

隨機變數 X 取值 `x₁, …, xₙ`，機率 `p₁, …, pₙ`。它的 **熵**（entropy）是

```
H(X) = − Σ pᵢ log₂ pᵢ   （pᵢ = 0 的項當作 0）
```

**意義**：描述 X 的結果 **平均需要幾個位元**，或者說 X 的 **不確定性** 有多大。

Shannon 證明（定理 4.58）：只要要求三個合理的性質——連續、均勻分布時隨 n 增加、可以分階段計算——熵的公式 **只能是** 這個（差一個常數倍）。

## 2.2 性質

| 情況 | 熵 |
|---|---|
| 公平的硬幣 | 1 位元 |
| 一定出現的結果 | 0（沒有不確定性） |
| n 種結果 | **最多 log₂ n**，而且只有在 **均勻分布** 時才等於 log₂ n（推論 4.60，用 Jensen 不等式證明） |
| 128 位元的隨機金鑰 | 128 位元 |
| 從 1000 個常用字選的密碼 | log₂ 1000 ≈ 10 位元——不管它看起來多長 |

```python
import math

def H(ps):
    return -sum(p * math.log2(p) for p in ps if p > 0) + 0.0     # + 0.0 把 −0.0 變成 0.0

print(H([0.5, 0.5]), H([1.0]), H([0.25] * 4), round(H([0.9, 0.1]), 3))
print(round(H([1 / 4, 1 / 4, 1 / 2]), 3))          # 課本例 4.61 的明文分布
FREQ = [8.15, 1.44, 2.76, 3.79, 13.11, 2.92, 1.99, 5.26, 6.35, 0.13, 0.42, 3.39, 2.54,
        7.10, 8.00, 1.98, 0.12, 6.83, 6.10, 10.47, 2.46, 0.92, 1.54, 0.17, 1.98, 0.08]
print(round(H([f / sum(FREQ) for f in FREQ]), 3), round(math.log2(26), 3))
```
```output
1.0 0.0 2.0 0.469
1.5
4.132 4.7
```
最後一行：只看單一字母的頻率，英文每個字母的熵約 4.13 位元，比均勻的 log₂ 26 ≈ 4.70 少一些。

## 2.3 條件熵與金鑰模糊度

**條件熵**（equivocation）`H(X | Y)`：已知 Y 之後，X 還剩多少不確定性。

**金鑰模糊度** `H(K | C)`：看到密文後，Eve 對金鑰還有多少不確定性。Shannon 證明

```
H(K | C) = H(K) + H(M) − H(C)
```

`H(K | C)` 越大越好；完全保密的系統中 `H(M | C) = H(M)`。

---

# 第三部分：自然語言的冗餘

## 3.1 英文的熵

只看單一字母：約 4.13 位元。但字母之間 **高度相關**（q 後面幾乎一定是 u）。看雙字母時 `H(L²)/2 ≈ 3.56`；看越長的字串越低。定義語言的熵

```
H(L) = lim H(Lⁿ) / n
```

實驗估計 **1.0 ≤ H(英文) ≤ 1.5 位元 / 字母**。表示一個字母要用約 4.7 位元表示，卻只帶 1～1.5 位元的資訊：**英文大約有 70% 是冗餘的**。

> Th prblms o crptgry nd scrcy sysms frnsh n ntrstng aplcatn o comm thry.

拿掉近 40% 的字母還是讀得懂——這就是冗餘。

```python
import math
from collections import Counter

text = """the problems of cryptography and secrecy systems furnish an interesting application
of communication theory in this paper a theory of secrecy systems is developed the approach is
on a theoretical level and is intended to complement the treatment found in standard works on
cryptography there a detailed study is made of the many standard types of codes and ciphers"""
s = "".join(ch for ch in text if ch.isalpha())

def H_n(s, n):
    grams = Counter(s[i:i + n] for i in range(len(s) - n + 1))
    total = sum(grams.values())
    return -sum(c / total * math.log2(c / total) for c in grams.values()) / n

print(len(s), [round(H_n(s, n), 2) for n in (1, 2, 3)])
```
```output
306 [4.06, 3.36, 2.56]
```
（樣本很短，n 大時會低估——每個 n-字母組幾乎都只出現一次。但趨勢很清楚：考慮越長的上下文，每個字母的平均資訊量越少。）

## 3.2 冗餘讓密碼可以被破解：唯一解距離

**冗餘度** `R = log₂ 26 − H(L) ≈ 3.2～3.7` 位元 / 字母。直覺：每多看一個密文字母，Eve 就多得到 R 位元「哪些金鑰不可能」的資訊。當看到的密文長度 n 滿足

```
n · R ≥ H(K)
```

一般來說就只剩 **唯一** 一把金鑰能解出有意義的明文。這個長度叫 **唯一解距離**（unicity distance）：`n₀ ≈ H(K) / R`。

```python
import math
R = math.log2(26) - 1.5                       # 取 H(英文) ≈ 1.5
for name, keybits in (("凱撒", math.log2(26)),
                      ("簡單替換", math.log2(math.factorial(26))),
                      ("Vigenère k = 6", 6 * math.log2(26)),
                      ("AES-128", 128)):
    print(f"{name:14} H(K) = {keybits:6.1f} 位元   唯一解距離 ≈ {keybits / R:5.1f} 個字母")
```
```output
凱撒             H(K) =    4.7 位元   唯一解距離 ≈   1.5 個字母
簡單替換           H(K) =   88.4 位元   唯一解距離 ≈  27.6 個字母
Vigenère k = 6 H(K) =   28.2 位元   唯一解距離 ≈   8.8 個字母
AES-128        H(K) =  128.0 位元   唯一解距離 ≈  40.0 個字母
```
**意義**：簡單替換密碼只要大約 28 個字母，理論上就只有一種合理的解（實際用頻率分析需要更長，像第 01 課的 298 個字母）。另一方面，**一次性密碼本** 的金鑰和明文一樣長，H(K) 隨 n 增加，永遠追不上——這是它完全保密的另一個說法。現代密碼會先 **壓縮**（降低冗餘）或在明文中加入隨機位元，讓攻擊者更難利用冗餘。

> 🔍 **Shannon 的「乘積系統」**（例 4.64）：把兩個密碼系統串接（先 e 再 e'）。Shannon 指出好的密碼要結合 **混淆**（confusion，讓密文和金鑰的關係複雜）和 **擴散**（diffusion，讓明文的一個位元影響很多密文位元）——這正是 DES、AES 反覆做「替換 + 排列」的設計原則（第 26 課）。

---

# 第四部分：計算複雜度

## 4.1 P 和 NP

完全保密的代價太高，所以實務上的密碼只追求 **計算上的安全**：破解在理論上可能，但需要的計算量大到做不到。那「做不到」要怎麼定義？

**決策問題**：答案是「是 / 否」的問題。

| 類別 | 定義 | 例子 |
|---|---|---|
| **P** | 有多項式時間演算法能 **解** | gcd、模反元素、判斷質數（AKS） |
| **NP** | 答案是「是」時，有一個證據（certificate）能在多項式時間 **驗證** | 「N 有小於 k 的因數嗎？」（給因數就能驗證）；SAT；背包問題 |

P ⊆ NP（能解就能驗證）。**P = NP 嗎？** 這是計算機科學最著名的開放問題，也是千禧年百萬美元問題之一。大多數人相信 P ≠ NP。

```python
import itertools, time

# 子集合和（背包）問題：驗證很快、找解很慢
weights = [267, 493, 869, 961, 1000, 1153, 1246, 1598, 1766, 1922]
target = 5842

certificate = [0, 0, 1, 1, 1, 0, 1, 0, 1, 0]         # 有人給你答案，驗證只要一次加總
print(sum(w for w, b in zip(weights, certificate) if b) == target)

count = 0
for bits in itertools.product([0, 1], repeat=len(weights)):    # 自己找：試 2^n 種
    count += 1
    if sum(w for w, b in zip(weights, bits) if b) == target:
        print(bits, "試了", count, "種")
        break
```
```output
True
(0, 0, 1, 1, 1, 0, 1, 0, 1, 0) 試了 235 種
```
## 4.2 NP 完全

**歸約**：問題 A 能在多項式時間轉換成問題 B 的實例，就說 A 可以歸約到 B——解 B 的演算法能拿來解 A，所以 B 至少和 A 一樣難。

**NP 完全**（Cook 1971）：一個 NP 問題，而且 **所有** NP 問題都能歸約到它。Cook 證明 SAT 是 NP 完全；之後發現成千上萬個 NP 完全問題，包括 **子集合和（背包）問題**（第 21 課的背包密碼就建立在它上面）。只要任一個 NP 完全問題有多項式解，P = NP。

**分解與離散對數在哪？** 它們都在 NP（給因數或給 x 就能驗證），也都在 co-NP，但 **一般認為不是 NP 完全**。目前沒有多項式時間演算法，也沒有證明它們很難。

## 4.3 密碼學需要的困難和複雜度理論的困難不一樣

複雜度理論談的是 **最壞情況**：「存在某些實例很難」。密碼學需要的是 **平均情況**（甚至幾乎每個實例）都很難：Bob 隨機產生的金鑰，必須幾乎總是難以破解。

**歷史教訓**：Merkle–Hellman 背包密碼建立在 NP 完全的子集合和問題上，但它用的是 **特殊結構** 的實例（超遞增序列偽裝而成），結果被 Shamir 等人用格的方法（第 24 課 LLL）在多項式時間內破解。**底層問題是 NP 完全，不代表密碼系統安全。**

另外，所有公鑰密碼都 **只建立在「目前沒人找到快速演算法」的假設上**。量子電腦上的 Shor 演算法能在多項式時間分解整數和解離散對數（第 26 課）——如果夠大的量子電腦造得出來，RSA、Diffie–Hellman、ECC 都會失效，這是格密碼（第 21～24 課）受到重視的原因。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 完全保密 | Perfect Secrecy | 密文不改變對明文的猜測 | 1.1 |
| 熵 | Entropy | 平均需要幾個位元描述結果 | 2.1 |
| 條件熵、模糊度 | Equivocation | 已知 Y 時 X 剩下的不確定性 | 2.3 |
| 冗餘 | Redundancy | 表示的位元數 − 實際資訊量 | 3.2 |
| 唯一解距離 | Unicity Distance | 密文長到只剩一把合理金鑰的長度 | 3.2 |
| 混淆 / 擴散 | Confusion / Diffusion | 好密碼的兩個設計原則 | 3.2 |
| P / NP | P / NP | 能快速解 / 能快速驗證 | 4.1 |
| NP 完全 | NP-complete | NP 中最難的問題 | 4.2 |
| 歸約 | Reduction | 把一個問題轉成另一個問題 | 4.2 |

---

# 習題

### 題 1：熵

算擲一顆公平骰子的熵，以及擲兩顆骰子 **點數和** 的熵。哪一個比較大？為什麼點數和的熵小於 log₂ 11？

### 題 2：完全保密

模 26 的移位密碼，如果整段訊息只用 **一把** 隨機金鑰，是完全保密的嗎？用唯一解距離的觀點說明。

### 題 3：密碼強度

一個密碼是從 7776 個字的字典中隨機選 5 個字串起來（diceware）。它的熵是多少位元？和隨機 10 個「大小寫字母 + 數字」比較。

### 題 4：觀念

為什麼「建立在 NP 完全問題上」不能保證密碼系統安全？

---

# 習題解答

**題 1**：

```python
import math
from collections import Counter

def H(ps):
    return -sum(p * math.log2(p) for p in ps if p > 0)

one = H([1 / 6] * 6)
sums = Counter(a + b for a in range(1, 7) for b in range(1, 7))
two = H([c / 36 for c in sums.values()])
print(round(one, 3), round(two, 3), round(math.log2(11), 3))
```
```output
2.585 3.274 3.459
```
點數和的熵（約 3.27）比一顆骰子（約 2.58）大，但小於 log₂ 11 ≈ 3.46，因為 11 種結果的機率不均勻（7 最常見）。

**題 2**：不是。完全保密要求 `#K ≥ #M`：金鑰只有 26 種，長度超過 1 的訊息就超過 26 種了。唯一解距離約 `log₂ 26 / 3.2 ≈ 1.5` 個字母——只要兩三個字母，理論上就只剩一個合理的解。

**題 3**：

```python
import math
print(round(5 * math.log2(7776), 1), round(10 * math.log2(62), 1))
```
```output
64.6 59.5
```
5 個字約 64.6 位元，10 個隨機字元約 59.5 位元——好記的密碼片語反而更強，前提是字 **真的隨機選**。

**題 4**：NP 完全只保證 **最壞情況** 很難，密碼需要的是隨機產生的實例 **平均** 都很難。而且密碼系統為了能解密，往往用了有特殊結構（陷門）的實例，這些結構可能讓問題變簡單——Merkle–Hellman 背包密碼就是例子。
