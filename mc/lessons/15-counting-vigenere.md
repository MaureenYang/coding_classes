# 15. 計數原理與 Vigenère 密碼（Counting and the Vigenère Cipher）

> 對應課本：§4.1、§4.2
>
> 程式練習：`MC12 破解 Vigenère 密碼`
>
> 先備知識：第 01 課（頻率分析）。

**這一課分成四個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 計數原理 | 排列、組合、二項式定理、鴿籠原理 |
| 第二部分 | Vigenère 密碼 | 多表替換、為什麼頻率分析直接用會失敗 |
| 第三部分 | 找金鑰長度 | Kasiski 檢驗、重合指數 |
| 第四部分 | 找金鑰本身 | 分組後各自做頻率分析、互重合指數 |

---

# 第一部分：計數原理

密碼學一天到晚在數「有多少種」：有多少把金鑰、有多少種明文、碰撞的機率多大。這一部分是第 16、17 課的基礎。

## 1.1 乘法原理與排列

**乘法原理**：做一件事分成幾步，第一步 n₁ 種、第二步 n₂ 種……，總共 `n₁ · n₂ ⋯` 種。

**排列**：從 n 個 **不同** 的東西選 r 個 **排成一列**（順序有差）：

```
P(n, r) = n(n − 1)(n − 2) ⋯ (n − r + 1) = n! / (n − r)!
```

例：簡單替換密碼的金鑰數是 26 個字母的排列 `26!`（第 01 課）。

## 1.2 組合與二項式定理

**組合**：從 n 個選 r 個，**不管順序**：

```
C(n, r) = n! / (r! (n − r)!)
```

**二項式定理**：`(x + y)ⁿ = Σ C(n, k) x^k y^(n−k)`。

一個有用的推論：**p 是質數時，`(x + y)^p ≡ x^p + y^p (mod p)`**（新生之夢 freshman's dream），因為 `0 < k < p` 時 `C(p, k)` 都是 p 的倍數。這在有限體 F_{p^k} 中常用。

```python
from math import comb, perm, factorial

print(perm(26, 3), comb(26, 3), factorial(26) // factorial(23))
print([comb(7, k) for k in range(8)])
print([comb(7, k) % 7 for k in range(8)])           # 只有首尾不是 7 的倍數
# 課本例 4.20：100 顆球 21 白，抽 10 顆恰 3 白的機率
print(round(comb(21, 3) * comb(79, 7) / comb(100, 10), 4))
```
```output
15600 2600 15600
[1, 7, 21, 35, 35, 21, 7, 1]
[1, 0, 0, 0, 0, 0, 0, 1]
0.2227
```
## 1.3 鴿籠原理

把 n + 1 隻鴿子放進 n 個籠子，至少有一個籠子有兩隻。在密碼學裡：**一個函數的輸入比輸出多，就一定有碰撞**。例如任何輸出 256 位元的雜湊函數，輸入一定有碰撞——問題只是好不好找（第 16、26 課）。

---

# 第二部分：Vigenère 密碼

## 2.1 是什麼

**Vigenère 密碼**（16 世紀）：用一個 **關鍵字**（keyword）決定一串移位量，輪流使用。關鍵字 `cabbage` = 移位 `2, 0, 1, 1, 0, 6, 4`，明文第 1 個字母移 2、第 2 個移 0……第 8 個又從頭開始。

```
明文：t h e r a i n i n s p a i n
金鑰：c a b b a g e c a b b a g e
密文：V H F S A O R K N T Q A O R
```

```python
def vigenere(text, key, sign=1):
    text = [ch for ch in text.lower() if ch.isalpha()]
    ks = [ord(k) - 97 for k in key.lower()]
    return "".join(chr((ord(ch) - 97 + sign * ks[i % len(ks)]) % 26 + 97) for i, ch in enumerate(text))

c = vigenere("the rain in spain", "cabbage").upper()
print(c, vigenere(c, "cabbage", -1))
```
```output
VHFSAORKNTQAOR theraininspain
```
這是一種 **多表替換**（polyalphabetic substitution）：同一個明文字母在不同位置會變成不同的密文字母（上例中第一個 `n` 變 `R`、第二個 `n` 變 `T`），所以 **整段密文的字母頻率被「抹平」**，第 01 課的頻率分析直接用會失敗。歷史上它被稱為「不可破解的密碼」（le chiffre indéchiffrable）長達 300 年。

## 2.2 它的弱點

金鑰長度是 k 時，**第 1, k+1, 2k+1, … 個字母都用同一個移位**——它們合起來就是一段普通的凱撒密碼！所以破解分兩步：

1. 找出 **金鑰長度** k；
2. 把密文分成 k 組，每組各自用頻率分析破解凱撒密碼。

下面用一段範例文字示範整個過程：

```python
PLAIN = """It was the season of long evenings, and the old lighthouse keeper had
taken to writing letters that he never intended to send. He wrote about the
weather, about the ships that passed far out on the horizon, and about the
strange silence that settled over the island after the last ferry of the
autumn had gone. Every night he climbed the spiral stairs, trimmed the wick,
and watched the beam sweep across the dark water. He believed that a light
kept burning for no one in particular was still a kind of promise, and that
somewhere a sailor he would never meet was grateful for it. In the morning
he would read what he had written, smile at his own seriousness, and fold the
pages into a box that was slowly becoming too small to close."""

def vigenere(text, key, sign=1):
    text = [ch for ch in text.lower() if ch.isalpha()]
    ks = [ord(k) - 97 for k in key.lower()]
    return "".join(chr((ord(ch) - 97 + sign * ks[i % len(ks)]) % 26 + 97) for i, ch in enumerate(text))

C = vigenere(PLAIN, "harbor").upper()
print(len(C))
print(C[:60])
```
```output
587
PTNBGKOEJFOJVNFGZFUGVWSEPNXTOEKTYFCCKLZHVKOOLTSBLEGFFYHDKBYV
```
（金鑰是 `harbor`，假裝我們不知道。）

---

# 第三部分：找金鑰長度

## 3.1 Kasiski 檢驗

**觀察**：明文中重複出現的字串（例如 `the`），如果兩次出現的距離剛好是金鑰長度的倍數，就會被加密成 **一樣的密文**。所以找出密文中重複的三字母組，它們的 **距離** 大多是金鑰長度的倍數。

```python
from collections import defaultdict
from math import gcd
from functools import reduce

PLAIN = """It was the season of long evenings, and the old lighthouse keeper had
taken to writing letters that he never intended to send. He wrote about the
weather, about the ships that passed far out on the horizon, and about the
strange silence that settled over the island after the last ferry of the
autumn had gone. Every night he climbed the spiral stairs, trimmed the wick,
and watched the beam sweep across the dark water. He believed that a light
kept burning for no one in particular was still a kind of promise, and that
somewhere a sailor he would never meet was grateful for it. In the morning
he would read what he had written, smile at his own seriousness, and fold the
pages into a box that was slowly becoming too small to close."""

def vigenere(text, key, sign=1):
    text = [ch for ch in text.lower() if ch.isalpha()]
    ks = [ord(k) - 97 for k in key.lower()]
    return "".join(chr((ord(ch) - 97 + sign * ks[i % len(ks)]) % 26 + 97) for i, ch in enumerate(text))

C = vigenere(PLAIN, "harbor").upper()
pos = defaultdict(list)
for i in range(len(C) - 2):
    pos[C[i:i + 3]].append(i)
gaps = []
for tri, ps in sorted(pos.items(), key=lambda kv: -len(kv[1])):
    if len(ps) >= 3:
        d = [b - a for a, b in zip(ps, ps[1:])]
        gaps += d
        print(tri, ps, d)
print("距離的 gcd：", reduce(gcd, gaps))
votes = {k: sum(1 for d in gaps if d % k == 0) for k in range(2, 13)}
print(votes)
```
```output
KOE [5, 155, 173, 233, 467, 491] [150, 18, 60, 234, 24]
TYF [31, 205, 307, 325, 535] [174, 102, 18, 210]
KOA [77, 137, 347, 413, 551] [60, 210, 66, 138]
OAK [78, 138, 348, 414, 552] [60, 210, 66, 138]
GKO [4, 76, 136] [72, 60]
KTY [30, 306, 534] [276, 228]
AHV [114, 120, 258] [6, 138]
FVH [170, 424, 484] [254, 60]
JVY [202, 250, 442] [48, 192]
距離的 gcd： 2
{2: 27, 3: 26, 4: 11, 5: 9, 6: 26, 7: 3, 8: 4, 9: 4, 10: 9, 11: 2, 12: 11}
```
結果並不乾淨：gcd 只有 2，投票時 2、3、6 都差不多。原因是密文裡也有 **巧合** 的重複（兩段不同的明文剛好加密成同樣的三個字母，例如距離 155 − 5 = 150 雖然是 6 的倍數，但 254、6 這些就不是）。所以 Kasiski 檢驗通常只能給出 **候選**（這裡是 2、3、6），還要用下一節的重合指數確認。

## 3.2 重合指數

**定義**：字串 s 的 **重合指數**（index of coincidence）`IndCo(s)` 是「從 s 隨機抽兩個字母（不放回），兩個相同」的機率：

```
IndCo(s) = Σᵢ Fᵢ(Fᵢ − 1) / (n(n − 1))     Fᵢ 是第 i 個字母出現的次數，n 是長度
```

| 文字 | IndCo 大約 |
|---|---|
| 英文 | **0.0685**（= Σ pᵢ²，pᵢ 是英文字母頻率） |
| 完全隨機的字母 | **0.0385**（= 1/26） |

簡單替換 **不改變** IndCo（只是換名字）。所以：**猜一個金鑰長度 k，把密文分成 k 組，如果 k 猜對，每組都是凱撒密碼，IndCo 接近 0.068；猜錯則接近 0.038。**

```python
PLAIN = """It was the season of long evenings, and the old lighthouse keeper had
taken to writing letters that he never intended to send. He wrote about the
weather, about the ships that passed far out on the horizon, and about the
strange silence that settled over the island after the last ferry of the
autumn had gone. Every night he climbed the spiral stairs, trimmed the wick,
and watched the beam sweep across the dark water. He believed that a light
kept burning for no one in particular was still a kind of promise, and that
somewhere a sailor he would never meet was grateful for it. In the morning
he would read what he had written, smile at his own seriousness, and fold the
pages into a box that was slowly becoming too small to close."""

def vigenere(text, key, sign=1):
    text = [ch for ch in text.lower() if ch.isalpha()]
    ks = [ord(k) - 97 for k in key.lower()]
    return "".join(chr((ord(ch) - 97 + sign * ks[i % len(ks)]) % 26 + 97) for i, ch in enumerate(text))

def ind_co(s):
    n = len(s)
    return sum(s.count(c) * (s.count(c) - 1) for c in set(s)) / (n * (n - 1))

C = vigenere(PLAIN, "harbor").upper()
print("整段密文", round(ind_co(C), 4), " 明文", round(ind_co(vigenere(PLAIN, "a")), 4))
for k in range(1, 10):
    avg = sum(ind_co(C[i::k]) for i in range(k)) / k
    print(k, round(avg, 4))
```
```output
整段密文 0.0444  明文 0.0706
1 0.0444
2 0.0473
3 0.0597
4 0.047
5 0.0455
6 0.0715
7 0.0445
8 0.0489
9 0.0599
```
k = 6 時平均 IndCo 跳到 0.07，和英文一樣；k = 3、9 只有 0.06 左右——這是因為 `harbor` 的第 3 和第 6 個字母都是 `r`，分成 3 組時有一組剛好「對」了一半。其他 k 都在 0.045 附近。所以金鑰長度是 6。

---

# 第四部分：找金鑰本身

## 4.1 每組各自破解凱撒

知道 k = 6 之後，第 i 組（`C[i], C[i+6], C[i+12], …`）就是一段用移位 `keyᵢ` 加密的凱撒密碼，用第 01 課的卡方分數找最佳移位：

```python
PLAIN = """It was the season of long evenings, and the old lighthouse keeper had
taken to writing letters that he never intended to send. He wrote about the
weather, about the ships that passed far out on the horizon, and about the
strange silence that settled over the island after the last ferry of the
autumn had gone. Every night he climbed the spiral stairs, trimmed the wick,
and watched the beam sweep across the dark water. He believed that a light
kept burning for no one in particular was still a kind of promise, and that
somewhere a sailor he would never meet was grateful for it. In the morning
he would read what he had written, smile at his own seriousness, and fold the
pages into a box that was slowly becoming too small to close."""
FREQ = [8.15, 1.44, 2.76, 3.79, 13.11, 2.92, 1.99, 5.26, 6.35, 0.13, 0.42, 3.39, 2.54,
        7.10, 8.00, 1.98, 0.12, 6.83, 6.10, 10.47, 2.46, 0.92, 1.54, 0.17, 1.98, 0.08]

def vigenere(text, key, sign=1):
    text = [ch for ch in text.lower() if ch.isalpha()]
    ks = [ord(k) - 97 for k in key.lower()]
    return "".join(chr((ord(ch) - 97 + sign * ks[i % len(ks)]) % 26 + 97) for i, ch in enumerate(text))

def chi2_for_shift(group, s):
    n = len(group)
    counts = [0] * 26
    for ch in group:
        counts[(ord(ch) - 65 - s) % 26] += 1
    return sum((counts[i] - n * FREQ[i] / 100) ** 2 / (n * FREQ[i] / 100) for i in range(26))

C = vigenere(PLAIN, "harbor").upper()
k = 6
key = ""
for i in range(k):
    group = C[i::k]
    s = min(range(26), key=lambda s: chi2_for_shift(group, s))
    key += chr(s + 97)
print(key)
print(vigenere(C, key, -1)[:80])
```
```output
harbor
itwastheseasonoflongeveningsandtheoldlighthousekeeperhadtakentowritingletterstha
```
## 4.2 互重合指數（課本的方法）

課本用另一個統計量：兩段字串 s、t 的 **互重合指數** `MutIndCo(s, t)` 是「從 s 抽一個、從 t 抽一個，兩者相同」的機率：

```
MutIndCo(s, t) = Σᵢ Fᵢ(s) · Fᵢ(t) / (|s| · |t|)
```

如果第 i 組和第 j 組的移位差是 σ，把第 j 組 **再往回移 σ**，兩組就變成「同一個移位」，互重合指數會接近 0.068；移錯則接近 0.038。所以可以先找出 **各組之間的相對移位**，最後只剩 26 種可能（整體再移多少），逐一試看哪個是英文。這樣即使沒有英文字母頻率表也能破解。

```python
PLAIN = """It was the season of long evenings, and the old lighthouse keeper had
taken to writing letters that he never intended to send. He wrote about the
weather, about the ships that passed far out on the horizon, and about the
strange silence that settled over the island after the last ferry of the
autumn had gone. Every night he climbed the spiral stairs, trimmed the wick,
and watched the beam sweep across the dark water. He believed that a light
kept burning for no one in particular was still a kind of promise, and that
somewhere a sailor he would never meet was grateful for it. In the morning
he would read what he had written, smile at his own seriousness, and fold the
pages into a box that was slowly becoming too small to close."""

def vigenere(text, key, sign=1):
    text = [ch for ch in text.lower() if ch.isalpha()]
    ks = [ord(k) - 97 for k in key.lower()]
    return "".join(chr((ord(ch) - 97 + sign * ks[i % len(ks)]) % 26 + 97) for i, ch in enumerate(text))

def mut_ind_co(s, t):
    return sum(s.count(chr(65 + i)) * t.count(chr(65 + i)) for i in range(26)) / (len(s) * len(t))

def shift_group(g, s):
    return "".join(chr((ord(ch) - 65 - s) % 26 + 65) for ch in g)

C = vigenere(PLAIN, "harbor").upper()
k = 6
groups = [C[i::k] for i in range(k)]
rel = [0]
for j in range(1, k):                   # 第 j 組相對第 0 組多移了幾格
    best = max(range(26), key=lambda s: mut_ind_co(groups[0], shift_group(groups[j], s)))
    rel.append(best)
print("相對移位", rel)
for base in range(26):
    key = "".join(chr((base + r) % 26 + 97) for r in rel)
    p = vigenere(C, key, -1)
    if p.count("the") >= 5:
        print(base, key, p[:50])
```
```output
相對移位 [0, 19, 10, 20, 7, 10]
7 harbor itwastheseasonoflongeveningsandtheoldlighthousekee
```
## 4.3 教訓

Vigenère 密碼的金鑰有 `26^k` 種，k = 6 就有三億多種，但我們完全沒有逐一嘗試：**統計量（IndCo）找出結構（金鑰長度），再把問題拆成 k 個簡單問題**。這是「分而治之」在密碼分析中的典型例子。

**一次性密碼本** 可以看成「金鑰和明文一樣長」的 Vigenère：每組只有一個字母，沒有任何統計可以做——這正是第 17 課證明它 **完全保密** 的直觀理由。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 排列 / 組合 | Permutation / Combination | 有順序 / 沒順序地選 | 1.1、1.2 |
| 二項式定理 | Binomial Theorem | `(x + y)ⁿ` 的展開 | 1.2 |
| 鴿籠原理 | Pigeonhole Principle | 東西比箱子多就有重複 | 1.3 |
| 多表替換 | Polyalphabetic Substitution | 不同位置用不同的替換表 | 2.1 |
| Vigenère 密碼 | Vigenère Cipher | 用關鍵字決定輪流的移位 | 2.1 |
| Kasiski 檢驗 | Kasiski Test | 用重複字串的距離猜金鑰長度 | 3.1 |
| 重合指數 | Index of Coincidence | 抽兩個字母相同的機率 | 3.2 |
| 互重合指數 | Mutual Index of Coincidence | 兩段文字各抽一個相同的機率 | 4.2 |

---

# 習題

### 題 1：計數

一個 8 位字元的密碼只能用小寫字母和數字。(a) 有幾種？(b) 如果至少要有一個數字呢？

### 題 2：新生之夢

驗證 `(x + y)⁵ ≡ x⁵ + y⁵ (mod 5)` 對所有 x、y ∈ {0, …, 4}。

### 題 3：重合指數

算課本例 4.15 的字串 *A bird in hand is worth two in the bush* 的重合指數。

### 題 4：觀念

為什麼簡單替換密碼不會改變重合指數？Vigenère 為什麼會讓整段密文的重合指數變小？

### 題 5：加密

用關鍵字 `key` 加密 `vigenere`。

---

# 習題解答

**題 1**：(a) `36⁸`；(b) 扣掉全部是字母的 `26⁸`。

```python
print(36 ** 8, 36 ** 8 - 26 ** 8)
```
```output
2821109907456 2612282842880
```
**題 2**：

```python
print(all((x + y) ** 5 % 5 == (x ** 5 + y ** 5) % 5 for x in range(5) for y in range(5)))
```
```output
True
```
**題 3**：

```python
s = "".join(ch for ch in "A bird in hand is worth two in the bush".upper() if ch.isalpha())
n = len(s)
print(n, round(sum(s.count(c) * (s.count(c) - 1) for c in set(s)) / (n * (n - 1)), 4))
```
```output
30 0.0575
```
課本的值是 0.0575——短的句子統計波動很大，和英文的 0.0685 有差距。

**題 4**：簡單替換只是把每個字母「換名字」，各字母出現的次數不變，`Σ Fᵢ(Fᵢ − 1)` 只是加法的順序換了。Vigenère 把同一個明文字母分散到 k 個不同的密文字母，常用字母（e、t）的次數被平均分攤，`Σ Fᵢ²` 變小，所以重合指數往 1/26 靠近。

**題 5**：

```python
def vigenere(text, key, sign=1):
    ks = [ord(k) - 97 for k in key]
    return "".join(chr((ord(ch) - 97 + sign * ks[i % len(ks)]) % 26 + 97) for i, ch in enumerate(text))
print(vigenere("vigenere", "key").upper())
```
```output
FMEORCBI
```