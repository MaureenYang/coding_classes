# 26. 密碼學的其他主題（Additional Topics in Cryptography）

> 對應課本：第 8 章（§8.1～§8.10）
>
> 程式練習：`MC17 Shamir 秘密分享`
>
> 先備知識：第 05 課（對稱與非對稱）、第 14 課（平方剩餘）、第 16 課（生日悖論）、第 25 課（數位簽章）。

課本最後一章是一系列短篇介紹，每一節都是一個獨立領域的入門。這一課照著課本的順序走，每個主題都附上一個能動手跑的小程式。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 雜湊函數與偽隨機數 | 雜湊的三個性質、Merkle–Damgård 結構、用雜湊做 PRNG 和串流密碼 |
| 第二部分 | 零知識證明與身分識別 | 平方根的零知識證明、為什麼它「零知識」、Schnorr 識別與 Fiat–Shamir 轉換 |
| 第三部分 | 秘密分享 | 加法分享、Shamir 門檻分享、Lagrange 內插 |
| 第四部分 | 填充、可證明安全與協定 | OAEP、隨機預言模型、為什麼「證明」也會出錯 |
| 第五部分 | 超橢圓曲線、量子計算、DES 與 AES | 虧格 2 曲線的 Jacobian、Shor 演算法的古典部分、Feistel 結構和 AES 的 S-box |

---

# 第一部分：雜湊函數與偽隨機數

## 1.1 雜湊函數的性質（§8.1）

**雜湊函數**把任意長的文件 D 變成一個短的位元串 `Hash(D)`，要求：

| 性質 | 意思 | 用來 |
|---|---|---|
| 好算 | 線性時間 | 簽好幾 MB 的程式 |
| **單向**（抗原像） | 給 H，找不到 D 使 `Hash(D) = H` | 存密碼、承諾 |
| **抗碰撞** | 找不到 D₁ ≠ D₂ 使雜湊值相同 | 數位簽章（Remark 8.1） |

**Remark 8.1**：如果 Eve 找到「付持票人 5 元」和「付持票人 500 元」兩份雜湊值相同的文件，請 Alice 簽前者，就等於拿到後者的簽章。

輸出 n 位元的雜湊：找原像約 2ⁿ 步，找碰撞只要約 **2^(n/2)** 步（生日悖論，第 16 課）。所以 SHA-256 的抗碰撞強度是 128 位元。

```python
import hashlib

for msg in [b"Pay the bearer $5", b"Pay the bearer $500", b"Pay the bearer $6"]:
    print(msg.decode().ljust(20), hashlib.sha256(msg).hexdigest()[:32])

a = int(hashlib.sha256(b"Pay the bearer $5").hexdigest(), 16)    # 雪崩效應
b = int(hashlib.sha256(b"Pay the bearer $6").hexdigest(), 16)
print("改一個字元，256 位元中有", bin(a ^ b).count("1"), "位元改變")
```
```output
Pay the bearer $5    f3af7d82df1441829960deabf701e04a
Pay the bearer $500  9fd3cac43b4fff14e2013d4915f9039e
Pay the bearer $6    a135d1e51152fa62e2f8f244f97cc598
改一個字元，256 位元中有 129 位元改變
```
## 1.2 用生日攻擊找碰撞

把 SHA-256 截短成 32 位元，生日攻擊只要 `√(2³²) = 65536` 這個數量級的嘗試就能找到碰撞（暴力找原像則要約 2³² ≈ 43 億次）：

```python
import hashlib

def h32(m):
    return hashlib.sha256(m).digest()[:4]

seen = {}
i = 0
while True:
    m = f"Pay the bearer ${i}".encode()
    d = h32(m)
    if d in seen:
        print(seen[d], "和", m, "的 32 位元雜湊都是", d.hex())
        print("試了", i + 1, "次")
        break
    seen[d] = m
    i += 1
```
```output
b'Pay the bearer $61411' 和 b'Pay the bearer $97207' 的 32 位元雜湊都是 3ff47541
試了 97208 次
```
## 1.3 Merkle–Damgård 結構與 SHA

實務上的雜湊函數重複使用一個 **混合函數**：把文件切成固定長度的區塊 D₁、D₂、…，從固定的初始值 H₀ 出發，`Hᵢ = 混合(Hᵢ₋₁, Dᵢ)`，最後的 H_k 就是雜湊值。SHA-1 把每個 512 位元區塊做 **80 輪** 混合；SHA-2（SHA-256、SHA-512）也是這個架構。2015 年 NIST 選出的 **SHA-3**（Keccak）則改用「海綿結構」。

速度很重要，所以雜湊函數不建立在因數分解之類的數學難題上，而是用位元運算 **特製** 的混合操作；它的安全性沒有數學證明，只靠長年的分析（SHA-1 在 2017 年被找到實際碰撞，現在已淘汰）。

下面是一個 **玩具** Merkle–Damgård 雜湊（不安全，只為了看結構）：

```python
def mix(h, block):                          # 32 位元的混合函數（玩具）
    for r in range(8):                      # 8 輪
        h = (h ^ block) * 0x01000193 % 2**32
        h = ((h << 13) | (h >> 19)) % 2**32  # 循環左移 13 位
        block = (block * 31 + r) % 2**32
    return h

def toy_hash(data):
    data += b"\x80" + b"\x00" * (-(len(data) + 1) % 4)   # 填充到 4 的倍數
    h = 0x12345678                                      # 固定的初始值 H0
    for i in range(0, len(data), 4):
        h = mix(h, int.from_bytes(data[i:i + 4], "big"))
    return f"{h:08x}"

for m in [b"", b"abc", b"abd", b"hello world"]:
    print(repr(m).ljust(15), toy_hash(m))
```
```output
b''             ad9679d1
b'abc'          66aa125d
b'abd'          fb7ee2bf
b'hello world'  562bd101
```
## 1.4 偽隨機數產生器（§8.2）

密碼學到處需要隨機數：產生金鑰、ElGamal / DSA 的臨時金鑰、NTRU 加密、機率加密。真正的隨機源（量子現象、熱雜訊）很慢，所以實務上從一個 **隨機種子 S** 出發，用 **偽隨機數產生器**（PRNG）展開成一長串看起來隨機的位元。

**密碼學安全**的 PRNG 要求：(1) 知道前 k 位元，猜下一位元的成功率不超過 50%；(2) 知道後面的輸出，推不出前面的輸出。

**例 8.4**：`Rᵢ = Hash(i ‖ S)`。**Remark 8.6**：PRNG 可以直接當串流密碼用：`Cᵢ = Mᵢ ⊕ Rᵢ`。

```python
import hashlib

def prng(seed, nbytes):
    out = b""
    i = 0
    while len(out) < nbytes:
        out += hashlib.sha256(i.to_bytes(8, "big") + seed).digest()   # R_i = Hash(i || S)
        i += 1
    return out[:nbytes]

key = b"shared secret seed"
msg = "攻擊黎明".encode()
stream = prng(key, len(msg))
ct = bytes(m ^ r for m, r in zip(msg, stream))
print(ct.hex())
print(bytes(c ^ r for c, r in zip(ct, prng(key, len(ct)))).decode())   # Bob 用相同種子解密

bits = "".join(f"{b:08b}" for b in prng(b"seed", 10000))
print("1 的比例：", round(bits.count("1") / len(bits), 4))
```
```output
623e0fa39355945118eef26a
攻擊黎明
1 的比例： 0.5032
```
⚠️ 一般程式語言的 `random`（例如 Python 的 Mersenne Twister、C 的 `rand()`）**不是** 密碼學安全的：觀察 624 個輸出就能還原內部狀態。密碼學用途要用 `secrets`、`/dev/urandom` 或作業系統提供的 CSPRNG。

---

# 第二部分：零知識證明與身分識別

## 2.1 零知識證明（§8.3）

新角色：**Peggy**（證明者）和 **Victor**（驗證者）。Peggy 要讓 Victor 相信某件事是真的，但 **不給 Victor 任何能拿去說服別人的資訊**。

好的零知識證明要滿足：

| 性質 | 意思 |
|---|---|
| **完備性** | 事情是真的，Victor 一定接受 |
| **可靠性** | 事情是假的，Victor 接受的機率極小 |
| **零知識** | Victor 能 **自己偽造** 和真實對話分不出來的紀錄 |

## 2.2 例 8.8：證明 y 是模 N 的平方

Peggy 知道 N = pq 的分解，所以能算出 x 使 `x² ≡ y (mod N)`。每一回合：

1. Peggy 選隨機 r，送出 `s ≡ r² (mod N)`。
2. Victor 隨機選 β ∈ {0, 1}。
3. Peggy 回 `z ≡ r`（β = 0）或 `z ≡ xr`（β = 1）。
4. Victor 檢查 `z² ≡ s`（β = 0）或 `z² ≡ ys`（β = 1）。

**完備**：`z² = x^(2β) r² = y^β s`。**可靠**：如果 y 不是平方，s 和 ys 不可能 **都** 是平方，所以 Peggy 每回合至少有一半機率答不出來；80 回合都過的機率是 2⁻⁸⁰。

```python
import random
rng = random.Random(8)

p, q = 1009, 2003
N = p * q
x = 123456
y = x * x % N                               # 公開 y；只有 Peggy 知道 x

def one_round(knows_root):
    r = rng.randrange(1, N)
    beta = rng.randrange(2)
    if knows_root:
        s = r * r % N
        z = r if beta == 0 else x * r % N
    else:                                   # 騙子：猜 Victor 會選 0 還是 1
        guess = rng.randrange(2)
        s = r * r * pow(y, -guess, N) % N   # 為猜測的 β 準備好 s
        z = r if beta == guess else rng.randrange(N)
    return z * z % N == pow(y, beta, N) * s % N

print("誠實的 Peggy 過了", sum(one_round(True) for _ in range(80)), "/ 80 回合")
print("騙子過了", sum(one_round(False) for _ in range(80)), "/ 80 回合")
```
```output
誠實的 Peggy 過了 80 / 80 回合
騙子過了 41 / 80 回合
```
## 2.3 為什麼是「零知識」：Victor 可以自己偽造紀錄

**例 8.9**：Victor 不必和 Peggy 說話，就能產生合法的 (s, β, z)：先隨機選 z 和 β，再令 `s ≡ z² y^(−β) (mod N)`。這樣的紀錄和真實對話的分布 **完全一樣**（完美零知識），所以真實對話不可能給 Victor 任何他自己做不出來的資訊——他也就無法拿去說服第三人 Valerie。

```python
import random
rng = random.Random(9)
N = 1009 * 2003
y = 123456 ** 2 % N

transcript = []
for _ in range(5):                          # 不知道 x 也能做出來
    z, beta = rng.randrange(1, N), rng.randrange(2)
    s = z * z * pow(y, -beta, N) % N
    transcript.append((s, beta, z))
for s, beta, z in transcript:
    print(s, beta, z, z * z % N == pow(y, beta, N) * s % N)
```
```output
1999833 1 970997 True
1385427 0 560222 True
1141744 0 390375 True
1815782 1 709521 True
871965 0 1883868 True
```
關鍵在於：偽造時 Victor **先知道 β** 才決定 s；真實對話中 Peggy 必須 **先送出 s** 才看到 β。順序不同，所以偽造的紀錄說服不了現場參與的人。

## 2.4 身分識別與 Schnorr 協定（§8.5）

**身分識別**：Alice 透過網路向 Bob 證明「我就是 Alice」，而且偷聽的 Eve、甚至 Bob 本人都不能冒充她。做法通常是 **挑戰—回應**：Bob 出題，Alice 用只有她知道的私鑰回答。（Alice 的公鑰本身要由可信機構 TA 簽章——這就是憑證。）

**Schnorr 識別**（基於 DLP）：公開 g（階為質數 q）、`v = g^s`。

1. Alice 選隨機 k，送 **承諾** `t = g^k`。
2. Bob 送隨機 **挑戰** c。
3. Alice 回 `r ≡ k + cs (mod q)`。
4. Bob 檢查 `g^r ≡ t · v^c`。

**Fiat–Shamir 轉換**：把挑戰 c 換成 `Hash(t ‖ 文件)`，任何挑戰—回應的識別協定就變成 **數位簽章**（這就是 Schnorr 簽章、EdDSA 的原理）。

```python
import hashlib, random
rng = random.Random(10)

p, q = 48731, 443                           # 借用第 25 課 DSA 的參數
g = pow(7, (p - 1) // q, p)
s = 242
v = pow(g, s, p)

k = rng.randrange(1, q)                     # 互動式識別
t = pow(g, k, p)
c = rng.randrange(q)
r = (k + c * s) % q
print("識別：", pow(g, r, p) == t * pow(v, c, p) % p)

def H(t, doc):                              # Fiat–Shamir：挑戰改成雜湊值
    return int(hashlib.sha256(f"{t}|{doc}".encode()).hexdigest(), 16) % q

def sign(doc):
    k = rng.randrange(1, q)
    t = pow(g, k, p)
    return t, (k + H(t, doc) * s) % q

def verify(doc, sig):
    t, r = sig
    return pow(g, r, p) == t * pow(v, H(t, doc), p) % p

sig = sign("I owe Bob $10")
print("簽章", sig, verify("I owe Bob $10", sig), verify("I owe Bob $1000", sig))
```
```output
識別： True
簽章 (25225, 323) True False
```
---

# 第三部分：秘密分享（§8.4）

## 3.1 加法分享：n 個人都到齊才能還原

把秘密 S 分給 n 個人：隨機選 D₁、…、D_{n−1}，令 `Dₙ ≡ S − D₁ − … − D_{n−1} (mod m)`。全部加起來就是 S；任何 n − 1 個人的份額都是均勻隨機的數，**對 S 毫無資訊**。

（課本指出：把保險箱密碼「切成三段」分給三個人 **不是** 好的秘密分享——知道其中一段就讓猜測變容易了。）

## 3.2 Shamir 門檻分享

**(t, n) 門檻**：n 個人中任 t 個人可以還原，t − 1 個人得不到任何資訊。Shamir（1979）的想法：**t 個點決定一個 t − 1 次多項式**（兩點決定一條直線）。

1. 令 a₀ = S，隨機選 a₁、…、a_{t−1}，`f(x) = a₀ + a₁x + … + a_{t−1}x^(t−1)`（係數在 F_p 中）。
2. 第 i 個人拿到 `(i, f(i))`。
3. 任 t 個人用 **Lagrange 內插** 求出 `f(0) = S`：

```
S = f(0) = Σ yᵢ · Π_{j≠i} xⱼ / (xⱼ − xᵢ)   (mod p)
```

```python
import random
rng = random.Random(84)
p = 2**61 - 1                               # 質數

def share(S, t, n):
    coeffs = [S] + [rng.randrange(p) for _ in range(t - 1)]
    f = lambda x: sum(c * pow(x, k, p) for k, c in enumerate(coeffs)) % p
    return [(i, f(i)) for i in range(1, n + 1)]

def recover(points):
    S = 0
    for i, (xi, yi) in enumerate(points):
        num = den = 1
        for j, (xj, _) in enumerate(points):
            if i != j:
                num = num * xj % p
                den = den * (xj - xi) % p
        S = (S + yi * num * pow(den, -1, p)) % p
    return S

secret = 31415926535
shares = share(secret, t=3, n=5)
for s in shares:
    print(s)
print(recover(shares[:3]), recover([shares[0], shares[2], shares[4]]))
print("只有 2 份：", recover(shares[:2]))
```
```output
(1, 134873212852802308)
(2, 1537516689452961596)
(3, 1902087452002710448)
(4, 1228585500502048864)
(5, 1822853844164670795)
31415926535 31415926535
只有 2 份： 1038072745466336971
```
**為什麼 t − 1 份沒有資訊**：對任何候選秘密 S'，都恰好有一個 t − 1 次多項式通過 (0, S') 和這 t − 1 個點，所以每個 S' 都一樣可能。

```python
p = 101                                      # 小例子：t = 2（直線），只拿到一份 (1, 30)
for S_guess in [0, 1, 50, 100]:
    a1 = (30 - S_guess) % p                  # f(x) = S + a1·x 通過 (1, 30)
    print(f"秘密若是 {S_guess:3}，斜率就是 {a1:3}")
```
```output
秘密若是   0，斜率就是  30
秘密若是   1，斜率就是  29
秘密若是  50，斜率就是  81
秘密若是 100，斜率就是  31
```
每個秘密都對應一條合法的直線，所以一份不夠。實務上 Shamir 分享用在：多人共管的根金鑰、加密貨幣錢包的備份、門檻簽章。

---

# 第四部分：填充、可證明安全與協定

## 4.1 可證明安全（§8.6）

課本開頭舉了一個荒謬的系統：Bob 送出 `y ≡ x^e (mod N)` 和 `z = N ⊕ x`——Eve 直接從 z 算出 x，RSA 再強也沒用。這就像把前門鎖得再牢，卻留著側門沒關。

**可證明安全**的目標：明確指出底層的難題，並 **證明「能破解系統的人也能解出難題」**。但這很難：

| 系統 | 已知的狀況 |
|---|---|
| RSA | 不知道破解 RSA 是否等價於因數分解 |
| Diffie–Hellman / ElGamal | 不知道是否等價於 DLP |
| **Rabin 密碼系統**（1979） | **可以證明** 解密等價於分解 N——但這也代表它對 **選擇密文攻擊** 毫無抵抗力 |

**選擇密文攻擊**聽起來很人為（誰會幫敵人解密？），但現在的 Alice 是電腦程式，程式會照它被寫的去做——例如回應「這個密文格式對不對」。Bleichenbacher（1998）就靠大量送出密文、看伺服器 **接不接受**（甚至不需要看到解密結果）破解了早期的 RSA 填充（PKCS #1 v1.5）。

## 4.2 OAEP

**OAEP**（Optimal Asymmetric Encryption Padding，Bellare–Rogaway 1994）用兩個雜湊函數 G、H 和隨機數 r 把訊息「打散」：

```
b = G(r) ⊕ (m ‖ 00…0)
c = E( b ‖ (H(b) ⊕ r) )
```

解密：拿到 b 和 `H(b) ⊕ r`，先算 r，再算 `G(r) ⊕ b`；結尾的 0 不對就拒絕。改變 m 或 r 的任何一位元，c 的每一位元都有 50% 機率改變。

```python
import hashlib, os

def G(r, n): return hashlib.shake_256(b"G" + r).digest(n)
def H(b, n): return hashlib.shake_256(b"H" + b).digest(n)
def xor(a, b): return bytes(x ^ y for x, y in zip(a, b))

K0, PAD = 16, 8                              # r 的長度、結尾 0 的長度
def oaep_pad(m, r):
    b = xor(G(r, len(m) + PAD), m + b"\x00" * PAD)
    return b + xor(H(b, K0), r)

def oaep_unpad(em, mlen):
    b, hr = em[:mlen + PAD], em[mlen + PAD:]
    r = xor(H(b, K0), hr)
    mz = xor(G(r, len(b)), b)
    return mz[:mlen] if mz[mlen:] == b"\x00" * PAD else None

m = b"HELLO"
r1, r2 = bytes(range(16)), bytes(range(1, 17))
print(oaep_pad(m, r1).hex())
print(oaep_pad(m, r2).hex())                 # 同一個訊息、不同的 r：完全不同
print(oaep_unpad(oaep_pad(m, r1), len(m)))
bad = bytearray(oaep_pad(m, r1)); bad[0] ^= 1
print(oaep_unpad(bytes(bad), len(m)))         # 被竄改：結尾的 0 不對，拒絕
```
```output
e4dff43b6392bcc1bbcaab5184ea16019f750968cef0270bed53826787
e8a887453f9c4777aef8ec650bbd9538e6fe2920e72d633fdcc45aca3e
b'HELLO'
None
```
（真正的 RSA-OAEP 會把這個結果當成整數 x，再算 `x^e mod N`。）

## 4.3 隨機預言模型與「證明」的極限

OAEP 的安全證明假設雜湊函數表現得像 **隨機預言**（random oracle）：既是確定的函數，又像完全隨機——這叫 **隨機預言模型**。OAEP 的證明被接受了 7 年、寫進產業標準，直到 2001 年 Shoup 指出證明中有一個不合理的假設（他提出修正版 OAEP+ 並給了正確證明）。

教訓：**「可證明安全」只和它的假設與邏輯一樣可靠**。也因此發展出不靠隨機預言的「標準模型」證明。

## 4.4 從基本元件到協定（§8.7）

真實應用會組合很多元件：例如用 RSA 簽章的公鑰（憑證）、OAEP 填充的 RSA 傳送 AES 金鑰、SHA-256 做雜湊與 PRNG。一份 **密碼協定** 要規定 **所有** 細節：金鑰長度、每個 byte 的意義、甚至 **位元組順序**（little-endian 或 big-endian，名稱來自《格列佛遊記》裡從小頭或大頭敲蛋的兩個王國）。

```python
n = 0x12345678
print(n.to_bytes(4, "big").hex(), n.to_bytes(4, "little").hex())
print(int.from_bytes(n.to_bytes(4, "big"), "little") == n)   # 兩邊搞錯就讀成另一個數
```
```output
12345678 78563412
False
```
即使每個元件都安全，組起來的協定也很容易出問題；所以協定通常由 IETF（RFC，例如 TLS 1.3 是 RFC 8446）、IEEE、ANSI 等標準組織花好幾年制定。

---

# 第五部分：超橢圓曲線、量子計算、DES 與 AES

## 5.1 超橢圓曲線（§8.8）

**虧格 g 的超橢圓曲線**：`C : Y² = X^(2g+1) + A₁X^(2g) + … + A_{2g+1}`（右邊沒有重根）。橢圓曲線就是 g = 1。

g ≥ 2 時，點本身不能相加，但 **g 個點的集合** 可以——精確的說法是 **除子**（divisor）模掉「函數的除子」得到的群，叫 **Jacobian** J(F_p)。Weil 證明了 Hasse 定理的推廣：

```
#J(F_p) = p^g + O(p^(g − 1/2))
```

所以虧格 2 的 Jacobian 大約有 **p²** 個元素，Pollard ρ 要 O(p) 步——**質數只要一半的位數** 就有和橢圓曲線相同的安全度，簽章也縮短一半（適合 RFID 之類受限的裝置）。但加法公式複雜得多，而且 g 太大時有指標演算法（Adleman–DeMarrais–Huang、Gaudry），所以只考慮 g = 2、3。

虧格 2 時，`#J(F_p)` 可以從曲線在 F_p 和 F_{p²} 上的點數 N₁、N₂ 算出：

```
#J(F_p) = (N₁² + N₂) / 2 − p
```

```python
p = 31
F = lambda x: (x**5 + 3*x**3 + 2*x + 5) % p          # C : Y² = X⁵ + 3X³ + 2X + 5（沒有重根）

# 每個 x：F(x) 是非零平方 → 2 點，F(x) = 0 → 1 點，否則 0 點；再加無窮遠點
N1 = 1 + sum(1 if F(x) == 0 else (2 if pow(F(x), (p - 1) // 2, p) == 1 else 0) for x in range(p))

class Fp2:                                            # F_{p²} = F_p[i]/(i² − 3)（3 是模 31 的非平方）
    def __init__(s, a, b): s.a, s.b = a % p, b % p
    def __add__(s, o): return Fp2(s.a + o.a, s.b + o.b)
    def __mul__(s, o): return Fp2(s.a * o.a + 3 * s.b * o.b, s.a * o.b + s.b * o.a)
    def __pow__(s, e):
        r, x = Fp2(1, 0), s
        while e:
            if e & 1: r = r * x
            x, e = x * x, e >> 1
        return r
    def zero(s): return s.a == 0 and s.b == 0

def F2(x):
    c = lambda k: Fp2(k, 0)
    return x**5 + c(3) * x**3 + c(2) * x + c(5)

N2 = 1
for a in range(p):
    for b in range(p):
        v = F2(Fp2(a, b))
        if v.zero(): N2 += 1
        elif (v ** ((p * p - 1) // 2)).a == 1: N2 += 2
J = (N1 * N1 + N2) // 2 - p
print("N1 =", N1, " N2 =", N2, " #J =", J, " p² =", p * p)
print("Weil 範圍：", (p**0.5 - 1)**4, "≤ #J ≤", (p**0.5 + 1)**4)
```
```output
N1 = 32  N2 = 978  #J = 970  p² = 961
Weil 範圍： 435.326161557757 ≤ #J ≤ 1860.6738384422424
```
## 5.2 量子計算與 Shor 演算法（§8.9）

量子位元的狀態是 `α|0⟩ + β|1⟩`（|α|² + |β|² = 1），n 個量子位元可以處在 2ⁿ 個基底狀態的 **疊加** 中。Shor（1994）給出 **多項式時間** 的量子演算法，能夠：

- **分解整數**：找出 a 模 n 的階 r；若 r 是偶數，`gcd(a^(r/2) − 1, n)` 很可能是 n 的因數。
- 解 **DLP** 和 **ECDLP**。

量子部分只負責「找階」：用 **量子傅立葉轉換**，測量到的 c 會讓 c/q 很接近某個 d/r（q 是 n² 到 2n² 之間的 2 的冪），再用 **連分數** 從 c/q 找出 r。下面用古典電腦模擬：先「假裝」量子電腦給出一個好的 c，再做古典的後處理。

```python
from fractions import Fraction
from math import gcd

n, a = 3233, 3                               # n = 61 · 53
r = next(k for k in range(1, n) if pow(a, k, n) == 1)   # 古典暴力找階（量子電腦的工作）
q = 1 << (n * n).bit_length()                # n² ≤ q < 2n² 的 2 的冪
d = 7                                        # 量子測量大約得到 c ≈ q·d/r
c = round(q * d / r)
print("r =", r, " q =", q, " 測到 c =", c)

guess = Fraction(c, q).limit_denominator(n)  # 連分數：找最接近 c/q、分母 < n 的分數
print("c/q ≈", guess, " → 候選 r =", guess.denominator)

r2 = guess.denominator
x = pow(a, r2 // 2, n)
print(pow(a, r2, n) == 1, r2 % 2 == 0, gcd(x - 1, n), gcd(x + 1, n))
```
```output
r = 260  q = 16777216  測到 c = 451694
c/q ≈ 7/260  → 候選 r = 260
True True 61 53
```
這裡 d = 7 和 r 互質，所以分母直接就是 r；若 gcd(d, r) > 1，得到的是 r 的因數，重試幾次就好。

**後量子密碼**：Shor 演算法讓 RSA、DH、ECC 在大型量子電腦面前全部失效；但目前 **沒有** 解 SVP / CVP 的有效量子演算法（Grover 搜尋只帶來平方根加速），所以 **格密碼**（第 21～24 課）是後量子密碼的主力。2024 年 NIST 公布的標準：ML-KEM（Kyber，加密 / 金鑰交換）、ML-DSA（Dilithium）和 SLH-DSA（雜湊型）簽章，FN-DSA（Falcon，NTRU 格）也在進行中。

（**量子密碼學**則是另一回事：利用測不準原理做金鑰交換，Eve 偷聽必然會擾動量子態而被發現。）

## 5.3 DES 與 Feistel 結構（§8.10）

**DES**（Data Encryption Standard，1977）：64 位元區塊、56 位元金鑰、**16 輪 Feistel 網路**。Feistel 結構把區塊切成左右兩半，每輪：

```
L_{i+1} = R_i
R_{i+1} = L_i ⊕ F(R_i, K_i)
```

神奇之處：**F 不需要可逆**，解密只要把輪金鑰 **倒過來** 用同一套程序。DES 的金鑰太短（1998 年 EFF 用專用機 56 小時暴力破解），後來用 3DES 延長壽命，最後由 AES 取代。

```python
import hashlib

def F(half, key):                            # 輪函數：不需要可逆（這裡直接用雜湊）
    return int.from_bytes(hashlib.sha256(half.to_bytes(4, "big") + key).digest()[:4], "big")

def feistel(block, keys):
    L, R = block >> 32, block & 0xFFFFFFFF
    for k in keys:
        L, R = R, L ^ F(R, k)
    return (R << 32) | L                     # 最後交換左右，讓解密程序完全相同

keys = [f"round key {i}".encode() for i in range(16)]
pt = 0x0123456789ABCDEF
ct = feistel(pt, keys)
print(f"{pt:016x} → {ct:016x}")
print(f"解密：{feistel(ct, keys[::-1]):016x}")
```
```output
0123456789abcdef → b9924e98972340da
解密：0123456789abcdef
```
## 5.4 AES

**AES**（Rijndael，Daemen 和 Rijmen 設計，2001 年經公開競賽選為標準）：128 位元區塊、128 / 192 / 256 位元金鑰、10 / 12 / 14 輪。它 **不是** Feistel 結構，而是 **代換—置換網路**：每輪把 16 bytes 排成 4 × 4 方陣，做

| 步驟 | 作用 |
|---|---|
| SubBytes | 每個 byte 過 **S-box**（非線性） |
| ShiftRows | 第 i 列循環左移 i 格 |
| MixColumns | 每一行乘上一個固定的矩陣（在 F₂₅₆ 中） |
| AddRoundKey | 和輪金鑰 XOR |

AES 的數學很漂亮：每個 byte 是 **有限體 F₂₅₆ = F₂[x]/(x⁸ + x⁴ + x³ + x + 1)** 的元素（第 09 課）。**S-box = 在 F₂₅₆ 中求反元素，再做一個 F₂ 上的仿射轉換**：

```python
def gmul(a, b):                              # F_256 中的乘法
    r = 0
    while b:
        if b & 1: r ^= a
        a <<= 1
        if a & 0x100: a ^= 0x11B             # 模 x⁸ + x⁴ + x³ + x + 1
        b >>= 1
    return r

def ginv(a):                                 # a^254 = a^(-1)（因為 F_256* 的階是 255）
    r = 1
    for _ in range(254): r = gmul(r, a)
    return r if a else 0

def sbox(a):
    b = ginv(a)
    rot = lambda x, k: ((x << k) | (x >> (8 - k))) & 0xFF
    return b ^ rot(b, 1) ^ rot(b, 2) ^ rot(b, 3) ^ rot(b, 4) ^ 0x63

print(hex(gmul(0x57, 0x83)))                 # FIPS-197 的範例：0x57 · 0x83 = 0xc1
print([hex(sbox(x)) for x in (0x00, 0x01, 0x53, 0xFF)])
S = [sbox(x) for x in range(256)]
print("S-box 是一一對應：", len(set(S)) == 256, " 沒有不動點：", all(S[x] != x for x in range(256)))
```
```output
0xc1
['0x63', '0x7c', '0xed', '0x16']
S-box 是一一對應： True  沒有不動點： True
```
`sbox(0x53) = 0xed` 正是 FIPS-197 標準裡的範例值。用「求反元素」做 S-box 讓它離任何線性函數都很遠，能抵抗差分和線性密碼分析。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 抗碰撞 | Collision Resistance | 找不到兩個雜湊值相同的輸入 | 1.1 |
| 偽隨機數產生器 | PRNG | 種子展開成隨機外觀的位元串 | 1.4 |
| 零知識證明 | Zero-Knowledge Proof | 證明為真，但不洩漏任何資訊 | 2.1 |
| 完備性 / 可靠性 | Completeness / Soundness | 真的會被接受 / 假的幾乎不會被接受 | 2.1 |
| Fiat–Shamir 轉換 | Fiat–Shamir Transform | 挑戰改用雜湊值，識別變簽章 | 2.4 |
| 門檻秘密分享 | Threshold Secret Sharing | 任 t 人可還原，t − 1 人不行 | 3.2 |
| Lagrange 內插 | Lagrange Interpolation | 由 t 個點還原 t − 1 次多項式 | 3.2 |
| 選擇密文攻擊 | Chosen Ciphertext Attack | 攻擊者能讓對方解密（或檢查）密文 | 4.1 |
| 隨機預言模型 | Random Oracle Model | 假設雜湊函數是完全隨機的函數 | 4.3 |
| Jacobian | Jacobian Variety | 超橢圓曲線上點集合形成的群 | 5.1 |
| 後量子密碼 | Post-Quantum Cryptography | 能抵抗量子電腦的密碼系統 | 5.2 |
| Feistel 網路 | Feistel Network | 左右兩半交替混合，F 不必可逆 | 5.3 |
| S-box | Substitution Box | AES 中 F₂₅₆ 求反元素 + 仿射轉換 | 5.4 |

---

# 習題

### 題 1：生日攻擊

一個雜湊函數輸出 40 位元，大約要試多少個輸入才有 50% 機率找到碰撞？

### 題 2：Shamir 分享

p = 101，(t, n) = (2, 3) 的分享中，三個人分別拿到 (1, 45)、(2, 79)、(3, 12)。用任兩份還原秘密，並檢查三份是否一致。

### 題 3：零知識

在例 8.8 中，如果 Victor 每回合都選 β = 1，騙子 Peggy（不知道 x）能不能騙過他？怎麼做？

### 題 4：Shor 的後處理

a = 2 模 n = 15 的階是多少？用 `gcd(a^(r/2) ± 1, n)` 分解 15。

### 題 5：觀念

為什麼 Feistel 網路的輪函數 F 不需要可逆，整個加密卻仍然可逆？

---

# 習題解答

**題 1**：約 `1.1774 · √(2⁴⁰) ≈ 1.18 · 2²⁰ ≈ 123 萬` 個（第 16 課：50% 機率需要約 `√(2 ln 2 · N)` 個）。

```python
from math import sqrt, log
print(round(sqrt(2 * log(2) * 2**40)))
```
```output
1234604
```
**題 2**：

```python
p = 101
def recover2(P, Q):
    (x1, y1), (x2, y2) = P, Q
    return (y1 * x2 * pow(x2 - x1, -1, p) + y2 * x1 * pow(x1 - x2, -1, p)) % p
pts = [(1, 45), (2, 79), (3, 12)]
print(recover2(pts[0], pts[1]), recover2(pts[0], pts[2]), recover2(pts[1], pts[2]))
```
```output
11 11 11
```
三組都得到 11，所以秘密是 11（f(x) = 11 + 34x，f(3) = 113 ≡ 12）。

**題 3**：可以。她選隨機 z，送 `s ≡ z² y⁻¹`，等 Victor 送 β = 1 時回 z，就有 `z² ≡ ys`。所以 Victor 的挑戰 **必須隨機**、而且要在 Peggy 送出 s **之後** 才決定。

**題 4**：

```python
from math import gcd
n, a = 15, 2
r = next(k for k in range(1, n) if pow(a, k, n) == 1)
x = pow(a, r // 2, n)
print(r, x, gcd(x - 1, n), gcd(x + 1, n))
```
```output
4 4 3 5
```
**題 5**：每一輪 `(L, R) → (R, L ⊕ F(R))`。知道輸出 (R, L ⊕ F(R)) 時，R 直接就有，再算一次 F(R) 和第二半 XOR 就得到 L。整個過程只需要 **計算** F，不需要 **反轉** F。
