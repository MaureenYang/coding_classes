# 01. 替換密碼與頻率分析（Simple Substitution Ciphers）

> 對應課本：Hoffstein、Pipher、Silverman《An Introduction to Mathematical Cryptography》§1.1、§1.6
>
> 程式練習：`MC01 凱撒與替換密碼破解`
>
> 先備知識：會寫簡單的 Python（迴圈、字串、字典）。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 密碼學的角色與用語 | Alice、Bob、Eve；明文、密文、金鑰；加密與解密 |
| 第二部分 | 凱撒密碼（移位密碼） | 怎麼加解密、為什麼 26 種金鑰一下就被試完 |
| 第三部分 | 簡單替換密碼 | 加密表與解密表、金鑰有 26! 種 |
| 第四部分 | 頻率分析 | 為什麼金鑰再多也擋不住統計；單字母與雙字母頻率 |
| 第五部分 | 歷史與教訓 | 密碼史上的幾個故事、「對手永遠用最好的方法」 |

**閱讀方式**：每個觀念都附 Python 範例，範例後面的「輸出」都是實際執行的結果。標 🔍 的是延伸內容，第一次讀可以跳過。

---

# 第一部分：密碼學的角色與用語

## 1.1 Alice、Bob 和 Eve

密碼學的故事裡永遠有三個人：

| 角色 | 做什麼 |
|---|---|
| **Bob** | 想傳一則秘密訊息給 Alice |
| **Alice** | 收訊息的人 |
| **Eve**（eavesdropper，竊聽者） | 能看到他們之間傳的每一個字，想讀出內容 |

**密碼學的目標**：就算 Eve 看到全部傳輸內容，也讀不懂訊息。

## 1.2 基本用語

| 用語 | 英文 | 意思 |
|---|---|---|
| 明文 | plaintext | 原本看得懂的訊息。課本用 **小寫字母** 寫明文 |
| 密文 | ciphertext | 加密後的亂碼。課本用 **大寫字母** 寫密文 |
| 金鑰 | key | 決定「怎麼加密」的秘密參數 |
| 加密 | encryption | 明文 → 密文 |
| 解密 | decryption | 密文 → 明文（知道金鑰的人做） |
| 密碼分析 | cryptanalysis | **不知道金鑰** 卻想讀出明文（Eve 做的事） |
| 密碼學 | cryptography | 希臘文 *kryptos*（隱藏）+ *graphikos*（書寫） |

**習慣**：加密前把空白、標點拿掉、全部連在一起，密文再每 5 個字母分一組（例如 `NURBK SUBVC`）。這樣 Eve 連「單字從哪裡斷開」都看不出來。

---

# 第二部分：凱撒密碼（移位密碼）

## 2.1 是什麼

**凱撒密碼**（Caesar cipher，又叫 **移位密碼** shift cipher）：每個字母往後移固定的 `k` 格，到 `z` 之後繞回 `a`。

```
明文：a b c d e f g h i j k l m n o p q r s t u v w x y z
k=5： F G H I J K L M N O P Q R S T U V W X Y Z A B C D E
```

**比喻**：兩個同心的字母輪盤，內圈轉 5 格。加密時從外圈找明文字母、讀內圈；解密反過來。

把字母編號 `a=0, b=1, …, z=25`，凱撒密碼就是 **模 26 的加法**（模運算在第 03 課詳細介紹，這裡先把「mod 26」理解成「除以 26 取餘數，讓數字繞回 0～25」）：

```
加密：c ≡ p + k (mod 26)
解密：p ≡ c − k (mod 26)
```

```python
def shift(text, k):
    out = []
    for ch in text.lower():
        if ch.isalpha():
            out.append(chr((ord(ch) - 97 + k) % 26 + 97))
    return "".join(out)

c = shift("Enemy falling back. Breakthrough imminent. Lucius.", 5).upper()
print(c)
print(shift(c, -5))
```
```output
JSJRDKFQQNSLGFHPGWJFPYMWTZLMNRRNSJSYQZHNZX
enemyfallingbackbreakthroughimminentlucius
```
注意 `% 26` 讓 `y + 5` 繞回 `d`，而 Python 的 `%` 對負數也會回傳 0～25 之間的值，所以解密直接用 `shift(c, -5)`。

## 2.2 為什麼凱撒密碼一點都不安全

金鑰只有 **26 種**（其中 k = 0 根本沒加密）。Eve 只要 **全部試一遍**，看哪一個像英文就好。這叫 **窮舉搜尋**（exhaustive search，也叫暴力法 brute force）。

```python
def shift(text, k):
    return "".join(chr((ord(ch) - 97 + k) % 26 + 97) for ch in text.lower() if ch.isalpha())

c = "LWKLQNWKDWLVKDOOQHYHUVHHDELOOERDUGORYHOBDVDWUHH"
for k in range(1, 8):          # 這裡只印前 7 個；實際上要試完 1～25
    print(k, shift(c, -k)[:30])
```
```output
1 kvjkpmvjcvkujcnnpgxgtuggcdknnd
2 juijoluibujtibmmofwfstffbcjmmc
3 ithinkthatishallneverseeabillb
4 hsghmjsgzshrgzkkmdudqrddzahkka
5 grfglirfyrgqfyjjlctcpqccyzgjjz
6 fqefkhqexqfpexiikbsbopbbxyfiiy
7 epdejgpdwpeodwhhjaranoaawxehhx
```
用眼睛掃一遍就知道 k = 3 是答案：`i think that i shall never see a billboard lovely as a tree`。

讓電腦自動判斷「像不像英文」，比找 `the` 更可靠的做法是 **比較字母頻率**，第四部分會用到。

---

# 第三部分：簡單替換密碼

## 3.1 是什麼

**簡單替換密碼**（simple substitution cipher）：每個明文字母換成 **另一個固定的字母**，但對應關係是 **任意排列**，不只是移位。金鑰就是一張 **加密表**：

```
明文 a b c d e f g h i j k l m n o p q r s t u v w x y z
密文 C I S Q V N F O W A X M T G U H P B K L R E Y D Z J      ← 課本表 1.1
```

**為什麼兩個明文字母不能對應到同一個密文字母？** 否則解密時不知道該還原成哪一個。數學上說加密函數必須是 **一對一**（injective）。

**解密表**：把加密表「反過來」，按密文字母 A～Z 排好，查起來比較快。

```python
plain = "abcdefghijklmnopqrstuvwxyz"
cipher = "CISQVNFOWAXMTGUHPBKLREYDZJ"
enc = dict(zip(plain, cipher))
dec = {c: p for p, c in enc.items()}        # 解密表：密文 → 明文

msg = "fourscoreandsevenyearsago"
c = "".join(enc[ch] for ch in msg)
print(" ".join(c[i:i + 5] for i in range(0, len(c), 5)))

received = "GVVQG VYKCM CQQBV KKWGF SCVKV B".replace(" ", "")
print("".join(dec[ch] for ch in received))
print("".join(dec[ch] for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"))   # 解密表的上排
```
```output
NURBK SUBVC GQKVE VGZVC BKCFU
neednewsaladdressingcaeser
jraxvgnpbzstlfhqducmoeikwy
```
- 第一行：課本例 1.1 的 *Four score and seven years ago*，照慣例每 5 個字母一組。
- 第二行：用解密表解出 `need new salad dressing caeser`（課本原文就拼成 caeser）。
- 第三行：解密表的上排，也就是課本表 1.2：`A→j`、`B→r`、`C→a`……因為加密表裡 `a→C`，反過來就是 `C→a`。**解密表就是加密函數的反函數。**
## 3.2 金鑰有多少種？

`a` 有 26 種選擇、`b` 剩 25 種、`c` 剩 24 種……所以總共

```
26 × 25 × 24 × … × 2 × 1 = 26!
```

```python
import math
n = math.factorial(26)
print(n)
print(f"{n:.3e}")
years = n / (10**6 * 60 * 60 * 24 * 365)      # 每秒試一百萬把
print(f"{years:.2e} 年")
```
```output
403291461126605635584000000
4.033e+26
1.28e+13 年
```
一秒試一百萬把也要 **10¹³ 年**，宇宙年齡才大約 10¹⁰ 年。看起來非常安全——**但其實一點也不安全**。

> **金鑰很多，不代表密碼安全。** 「金鑰空間很大所以很安全」這種說法在歷史上出現過很多次，也被推翻過很多次。

---

# 第四部分：頻率分析

## 4.1 核心觀念

英文裡的字母 **不是平均出現的**：`e` 約 13%、`t` 約 10%，`q`、`z` 不到 0.2%。簡單替換只是把字母「換名字」，**每個字母出現的次數完全沒變**。所以 Eve 只要數密文裡每個字母出現幾次，出現最多的大概就是 `e`。

課本表 1.3（英文字母頻率，由高到低）：

| 字母 | % | 字母 | % | 字母 | % |
|---|---|---|---|---|---|
| E | 13.11 | R | 6.83 | L | 3.39 |
| T | 10.47 | I | 6.35 | F | 2.92 |
| A | 8.15 | S | 6.10 | C | 2.76 |
| O | 8.00 | H | 5.26 | M | 2.54 |
| N | 7.10 | D | 3.79 | … | … |

**課本的實戰步驟**（破解表 1.4 的 298 個字母密文）：

1. **數單字母頻率**：`J` 出現 32 次最多 → 猜 `J = e`。
2. **數雙字母（bigram）頻率**：英文最常見的是 `th`、`he`；密文裡 `LO`、`OJ` 最多，又已知 `J = e` → 猜 `L = t`、`O = h`。
3. **代入、找單字片段**：出現 `th---ht` → 猜是 `thought`，得到 `S = o`、`C = u`、`I = g`。
4. **重複**：`-ition` 前面通常是 `s`……逐步把整張表填出來。

最後解出的是《血字的研究》中福爾摩斯的一段話。重點不是這段話，而是 **統計分析** 這個武器——它會在整本書反覆出現。

## 4.2 用程式數頻率

```python
from collections import Counter

c = """LOJUM YLJME PDYVJ QXTDV SVJNL DMTJZ WMJGG YSNDL UYLEO SKDVC
GEPJS MDIPD NEJSK DNJTJ LSKDL OSVDV DNGYN VSGLL OSCIO LGOYG
ESNEP CGYSN GUJMJ DGYNK DPPYX PJDGG SVDNT WMSWS GYLYS NGSKJ
CEPYQ GSGLD MLPYN IUSCP QOYGM JGCPL GDWWJ DMLSL OJCNY NYLYD
LJQLO DLCNL YPLOJ TPJDM NJQLO JWMSE JGGJG XTUOY EOOJO DQDMM
YBJQD LLOJV LOJTV YIOLU JPPES NGYQJ MOYVD GDNJE MSVDN EJM"""
c = "".join(ch for ch in c if ch.isalpha())
print(len(c))
print(Counter(c).most_common(8))
bigrams = Counter(c[i:i + 2] for i in range(len(c) - 1))
print(bigrams.most_common(4))
```
```output
298
[('J', 32), ('L', 27), ('D', 27), ('G', 24), ('Y', 23), ('S', 22), ('O', 19), ('N', 19)]
[('LO', 9), ('OJ', 7), ('GY', 6), ('DN', 6)]
```
和課本的表 1.5、表 1.6 幾乎一樣：`J` 32 次最多，雙字母 `LO` 9 次、`OJ` 7 次。（課本表 1.5 寫 `L` 28 次、`N` 18 次，實際數這段密文是 27 次和 19 次——把課本給的明文代回去檢查過，密文本身沒有錯，是課本的計數表有一點小誤差。這完全不影響推理：頻率分析本來就只看「大概哪些最多」。）

## 4.3 讓電腦判斷「像不像英文」：卡方分數

對凱撒密碼，可以自動找出最可能的金鑰：每個候選 k 解密之後，比較字母分布和英文的差距，差距最小的就是答案。常用的差距是 **卡方統計量**：

```
χ² = Σ (實際次數 − 期望次數)² / 期望次數，期望次數 = 文字長度 × 英文頻率
```

```python
FREQ = [8.15, 1.44, 2.76, 3.79, 13.11, 2.92, 1.99, 5.26, 6.35, 0.13, 0.42, 3.39, 2.54,
        7.10, 8.00, 1.98, 0.12, 6.83, 6.10, 10.47, 2.46, 0.92, 1.54, 0.17, 1.98, 0.08]

def shift(text, k):
    return "".join(chr((ord(ch) - 97 + k) % 26 + 97) for ch in text.lower() if ch.isalpha())

def chi2(text):
    n = len(text)
    counts = [text.count(chr(97 + i)) for i in range(26)]
    return sum((counts[i] - n * FREQ[i] / 100) ** 2 / (n * FREQ[i] / 100) for i in range(26))

c = "BGUTBMBGZTFHNLXMKTIPBMAVAXXLXTEPTRLEXTOXKHHFYHKMAXFHNLX"
best = min(range(26), key=lambda k: chi2(shift(c, -k)))
print(best, shift(c, -best))
```
```output
19 inbaitingamousetrapwithcheesealwaysleaveroomforthemouse
```
卡方分數最小的是 k = 19，解出 *In baiting a mouse trap with cheese, always leave room for the mouse.*（課本習題 1.2(c)）。整個過程完全自動，不需要人眼判斷。

> 🔍 寫程式解題時要記得：判斷「像不像英文」的函數不是神諭。文字太短、或用字很特殊時，頻率最接近英文的不一定是正確答案。程式練習 MC01 的測資會保證文字夠長。

---

# 第五部分：歷史與教訓

## 5.1 電腦時代以前的密碼學（§1.6 摘要）

| 時代 | 事件 |
|---|---|
| 古代 | 凱撒用移位密碼傳軍令；斯巴達人用 **密碼棒**（scytale）把皮帶纏在棍子上寫字——這是 **換位密碼**（transposition）：字母不變、順序打亂 |
| 9 世紀 | 阿拉伯學者 **al-Kindi** 寫下最早的頻率分析，簡單替換從此不再安全 |
| 15～16 世紀 | Alberti 的密碼輪盤；**Vigenère 密碼**（多表替換，用好幾個移位輪流加密）被稱為「無法破解的密碼」，直到 19 世紀被 Babbage、Kasiski 破解（第 15 課） |
| 1587 年 | 蘇格蘭瑪麗女王用替換密碼和支持者通信，被伊莉莎白一世的密碼分析師破解，成為她被判死刑的證據 |
| 第一次世界大戰 | **齊默爾曼電報** 被英國破解，促成美國參戰 |
| 第二次世界大戰 | 德國 **Enigma** 轉子機被波蘭與英國（Bletchley Park、Turing）破解；美國破解日本的 Purple 密碼 |
| 1970 年代 | 對稱密碼 DES 標準化；Diffie–Hellman 提出 **公開金鑰密碼學**（第 06 課） |

## 5.2 本課最重要的一句話

> **你的對手永遠用 *她自己* 最好的策略打敗你，而不是你希望她用的策略。所以一個密碼系統有多安全，取決於目前已知最好的破解方法。新方法出現後，安全性只會變差，不會變好。**

簡單替換密碼有 26! 把金鑰，但 Eve 根本不需要試金鑰——她用頻率分析。設計密碼時要問的永遠是「**最好的攻擊是什麼？**」，而不是「金鑰有幾把？」。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 明文 / 密文 | Plaintext / Ciphertext | 加密前 / 加密後的訊息 | 1.2 |
| 金鑰 | Key | 決定怎麼加密的秘密 | 1.2 |
| 密碼分析 | Cryptanalysis | 不知道金鑰而試圖解密 | 1.2 |
| 凱撒密碼、移位密碼 | Caesar / Shift Cipher | 每個字母移 k 格 | 2.1 |
| 窮舉搜尋 | Exhaustive Search | 把所有金鑰試一遍 | 2.2 |
| 簡單替換密碼 | Simple Substitution Cipher | 字母按一張任意排列表替換 | 3.1 |
| 一對一 | One-to-one / Injective | 不同的輸入給出不同的輸出 | 3.1 |
| 頻率分析 | Frequency Analysis | 用字母出現次數猜對應關係 | 4.1 |
| 雙字母 | Bigram | 連續的兩個字母 | 4.1 |
| 換位密碼 | Transposition Cipher | 字母不變，只打亂位置 | 5.1 |

---

# 習題

### 題 1：手算

用凱撒密碼、k = 11 加密 `apageofhistory`（只要前 6 個字母）。

### 題 2：計數

字母表有 26 個字母。
(a) 有多少種簡單替換密碼 **沒有任何字母對應到自己**（沒有「固定點」）？提示：這叫做 **錯排數**，可以用排容原理算。
(b) 用程式驗證你的答案。

### 題 3：解密表

課本表 1.11 的加密表是 `a→S, b→C, c→J, d→A, e→X, f→U, g→F, h→B, i→Q, j→K, k→T, l→P, m→R, n→W, o→E, p→Z, q→H, r→V, s→L, t→I, u→G, v→Y, w→D, x→N, y→M, z→O`。用它解密 `IBXLX JVXIZ SLLDE VAQLL DEVAU QLB`。

### 題 4：自動破解

用第 4.3 節的卡方方法破解課本習題 1.2(b)：`UXENRBWXCUXENFQRLQJUCNABFQNWRCJUCNAJCRXWORWMB`。金鑰是多少？

### 題 5：觀念

為什麼簡單替換密碼的「金鑰空間很大」卻擋不住頻率分析？如果想讓頻率分析變難，你會怎麼改這個密碼？

---

# 習題解答

**題 1**：`a(0)+11=11→L`、`p(15)+11=26≡0→A`、`a→L`、`g(6)+11=17→R`、`e(4)+11=15→P`、`o(14)+11=25→Z`，所以是 `LALRPZ`。

**題 2**：(a) 錯排數 D(26) = 26! × Σ(−1)ᵏ/k!（k = 0..26），約等於 26!/e。

```python
import math
n = 26
d = sum((-1) ** k * math.factorial(n) // math.factorial(k) for k in range(n + 1))
print(d)
D = [1, 0]                                   # 遞迴式 D(n) = (n-1)(D(n-1) + D(n-2)) 驗算
for m in range(2, n + 1):
    D.append((m - 1) * (D[-1] + D[-2]))
print(D[n] == d)
print(f"{d / math.factorial(n):.4f}")
```
```output
148362637348470135821287825
True
0.3679
```
大約 36.8%（= 1/e）的替換表沒有固定點；也就是說，隨便選一張表，有約 63% 的機率至少有一個字母對應到自己。

**題 3**：

```python
plain = "abcdefghijklmnopqrstuvwxyz"
cipher = "SCJAXUFBQKTPRWEZHVLIGYDNMO"
dec = {c: p for p, c in zip(plain, cipher)}
print("".join(dec[ch] for ch in "IBXLXJVXIZSLLDEVAQLLDEVAUQLB"))
```
```output
thesecretpasswordisswordfish
```
`The secret password is swordfish.`

**題 4**：

```python
FREQ = [8.15, 1.44, 2.76, 3.79, 13.11, 2.92, 1.99, 5.26, 6.35, 0.13, 0.42, 3.39, 2.54,
        7.10, 8.00, 1.98, 0.12, 6.83, 6.10, 10.47, 2.46, 0.92, 1.54, 0.17, 1.98, 0.08]

def shift(text, k):
    return "".join(chr((ord(ch) - 97 + k) % 26 + 97) for ch in text.lower())

def chi2(text):
    n = len(text)
    return sum((text.count(chr(97 + i)) - n * FREQ[i] / 100) ** 2 / (n * FREQ[i] / 100) for i in range(26))

c = "UXENRBWXCUXENFQRLQJUCNABFQNWRCJUCNAJCRXWORWMB"
k = min(range(26), key=lambda k: chi2(shift(c, -k)))
print(k, shift(c, -k))
```
```output
9 loveisnotlovewhichalterswhenitalterationfinds
```

k = 9：*Love is not love which alters when it alteration finds.*（莎士比亞十四行詩第 116 首）

**題 5**：替換只是「換名字」，每個字母的出現次數完全保留，所以頻率分析不需要試金鑰。讓頻率分析變難的方法：讓同一個明文字母在不同位置被換成 **不同** 的密文字母——例如 **同音替換**（常見字母有好幾個替代符號，讓頻率變平均），或 **多表替換**（Vigenère：好幾張移位表輪流用，第 15 課）。
