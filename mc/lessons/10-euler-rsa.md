# 10. 歐拉公式與 RSA（Euler's Formula and RSA）

> 對應課本：§3.1～§3.3
>
> 程式練習：`MC09 RSA 加解密`
>
> 先備知識：第 03 課（模反元素、快速冪）、第 04 課（費馬小定理）、第 08 課（中國剩餘定理）。

**這一課分成五個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 模 p 與模 pq 的 e 次方根 | 歐拉公式 `a^((p−1)(q−1)) ≡ 1 (mod pq)`、知道分解就能開 e 次方根 |
| 第二部分 | RSA 公鑰密碼 | 金鑰建立、加密、解密、課本例 3.8 |
| 第三部分 | 為什麼 Eve 解不開 | 知道 φ(N) 等於知道分解；但「破 RSA」和「分解」是否一樣難仍未知 |
| 第四部分 | 實作與攻擊 | 選擇密文攻擊、共用模數、小指數、用 CRT 加速解密 |
| 第五部分 | 歐拉定理的一般形式 | `a^φ(m) ≡ 1 (mod m)`、φ 的公式 |

---

# 第一部分：模 p 與模 pq 的 e 次方根

## 1.1 模質數：容易

**命題 3.2**：p 是質數、`gcd(e, p − 1) = 1`。設 `de ≡ 1 (mod p − 1)`，則 `x^e ≡ c (mod p)` 的唯一解是 `x ≡ c^d`。

**為什麼**：`de = 1 + k(p − 1)`，所以 `(c^d)^e = c^(1 + k(p−1)) = c · (c^(p−1))^k ≡ c`（費馬小定理）。

課本例：`x^1583 ≡ 4714 (mod 7919)`。`1583⁻¹ ≡ 5277 (mod 7918)`，`x ≡ 4714^5277 ≡ 6059`。

```python
p, e, c = 7919, 1583, 4714
d = pow(e, -1, p - 1)
x = pow(c, d, p)
print(d, x, pow(x, e, p))
```
```output
5277 6059 4714
```
## 1.2 歐拉公式（兩個質數的情況）

**定理 3.1（歐拉公式）**：p、q 是相異質數，`g = gcd(p − 1, q − 1)`，`gcd(a, pq) = 1`，則

```
a^((p−1)(q−1)/g) ≡ 1 (mod pq)，特別地 a^((p−1)(q−1)) ≡ 1 (mod pq)
```

**證明**：令 `L = (p−1)(q−1)/g`，它是 p − 1 的倍數（`L = (p−1) · (q−1)/g`），所以由費馬小定理 `a^L ≡ 1 (mod p)`；同理 `a^L ≡ 1 (mod q)`。p 和 q 都整除 `a^L − 1`，而 p、q 互質，所以 `pq | a^L − 1`。

（這是「先分別在模 p、模 q 證明，再用 CRT 組合」的典型例子。）

## 1.3 模 pq：知道分解就容易

**命題 3.4**：p、q 是相異質數，`gcd(e, (p−1)(q−1)) = 1`，`de ≡ 1 (mod (p−1)(q−1))`，則 `x^e ≡ c (mod pq)` 的唯一解是 `x ≡ c^d (mod pq)`。

證明和 1.1 一樣，只是把費馬小定理換成歐拉公式。

課本例 3.6：`x^17389 ≡ 43927 (mod 64349)`，`64349 = 229 · 281`。

```python
p, q, e, c = 229, 281, 17389, 43927
N, phi = p * q, (p - 1) * (q - 1)
d = pow(e, -1, phi)
print(phi, d, pow(c, d, N))

from math import gcd
g = gcd(p - 1, q - 1)                       # Remark 3.5：模 φ/g 也行，d 比較小
d2 = pow(e, -1, phi // g)
print(g, phi // g, d2, pow(c, d2, N))
```
```output
63840 53509 14458
4 15960 5629 14458
```
**關鍵**：整個計算需要 `(p − 1)(q − 1)`，也就是需要 **知道 N 的分解**。課本例 3.7：Alice 叫 Eve 解 `x^9843 ≡ 134872 (mod 30069476293)`，Eve 不知道 `30069476293 = 104729 · 287117` 就束手無策；知道之後立刻算出來。

```python
N, e, c = 30069476293, 9843, 134872
p, q = 104729, 287117
d = pow(e, -1, (p - 1) * (q - 1))
x = pow(c, d, N)
print(p * q == N, d, x, pow(x, e, N) == c)
```
```output
True 18472798299 25470280263 True
```
**這就是 RSA 的陷門**：e 次方根在知道分解時容易算，不知道時（目前看來）很難。

---

# 第二部分：RSA 公鑰密碼

## 2.1 協定（課本表 3.1）

| | Bob（收信人） | Alice（寄信人） |
|---|---|---|
| **建金鑰** | 選兩個秘密的大質數 p、q；選加密指數 e 使 `gcd(e, (p−1)(q−1)) = 1`；公布 `(N, e)`，N = pq | |
| **加密** | | 把明文編碼成 `1 ≤ m < N`，算 `c ≡ m^e (mod N)` 送出 |
| **解密** | 算 `d ≡ e⁻¹ (mod (p−1)(q−1))`，`m ≡ c^d (mod N)` | |

用語：N 叫 **模數**（modulus），e 是 **加密指數**，d 是 **解密指數**。`(N, e)` 是公鑰，`d`（或 p、q）是私鑰。

## 2.2 課本例 3.8

```python
p, q = 1223, 1987                       # Bob 的秘密
N = p * q
e = 948047
phi = (p - 1) * (q - 1)
from math import gcd
print(N, phi, gcd(e, phi))

m = 1070777                             # Alice 的明文
c = pow(m, e, N)
print("密文", c)

d = pow(e, -1, phi)                     # Bob 解密
print("d =", d, " 解密 =", pow(c, d, N))
```
```output
2430101 2426892 1
密文 1473513
d = 1051235  解密 = 1070777
```
## 2.3 實際尺寸

實務上 p、q 各約 1024 位元（N 約 2048 位元），e 通常取 65537（`2¹⁶ + 1`，二進位只有兩個 1，加密只要 17 次乘法）。

```python
import random

def is_probable_prime(n, rounds=30):            # Miller–Rabin，第 11 課介紹
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % sp == 0:
            return n == sp
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def random_prime(bits):
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(n):
            return n

random.seed(2024)
e = 65537
while True:
    p, q = random_prime(1024), random_prime(1024)
    phi = (p - 1) * (q - 1)
    if p != q and phi % e:
        break
N = p * q
d = pow(e, -1, phi)
m = int.from_bytes("今晚老地方見".encode(), "big")
c = pow(m, e, N)
back = pow(c, d, N)
print(N.bit_length(), len(str(N)))
print(back.to_bytes((back.bit_length() + 7) // 8, "big").decode())
```
```output
2048 617
今晚老地方見
```
N 是 2048 位元（617 位數）。這段程式在一般電腦上不到一秒就完成——**建金鑰、加密、解密都是多項式時間**。

---

# 第三部分：為什麼 Eve 解不開

## 3.1 知道 φ(N) 就等於知道分解

Eve 知道 N 和 e。如果她能算出 `(p − 1)(q − 1)`，就能算 d、解密。但這不會比分解簡單（Remark 3.10）：

```
(p − 1)(q − 1) = N − (p + q) + 1   ⇒   p + q = N + 1 − (p−1)(q−1)
```

知道 `p + q` 和 `pq`，p、q 就是二次方程式 `X² − (p+q)X + N = 0` 的兩根。

```python
from math import isqrt

N, phi = 66240912547, 66240396760
s = N + 1 - phi                      # p + q
disc = s * s - 4 * N
r = isqrt(disc)
p, q = (s - r) // 2, (s + r) // 2
print(s, p, q, p * q == N)
```
```output
515788 241511 274277 True
```
更一般地，知道 d 也能有效率地分解 N（課本習題 3.15 的方向；第 12 課的平方差想法）。所以 **「從公鑰算出私鑰」和「分解 N」一樣難**。

## 3.2 一個未解的問題

**但這不代表破解 RSA 一定要分解 N**（Remark 3.11）：Eve 真正要做的是「解 `x^e ≡ c (mod N)`」，也許有不經過 φ(N) 的方法。**到現在沒有人知道** RSA 問題是否和分解一樣難。

| 問題 | 和分解的關係 |
|---|---|
| 從 N 算 φ(N) | 等價 |
| 從 (N, e) 算 d | 等價 |
| 模 N 開平方根 | 等價（第 08 課 2.3 節） |
| 模 N 開 e 次方根（RSA 問題） | 不比分解難；是否等價 **未知** |

---

# 第四部分：實作與攻擊（§3.3）

課本強調：數學難題只是安全的 **一部分**，實作上的疏忽一樣致命。

## 4.1 選擇密文攻擊（例 3.13）

假設 Alice 願意替任何人解密「看起來隨機」的訊息（例如為了證明自己擁有私鑰）。Eve 攔截到 Bob 給 Alice 的密文 c，她選隨機的 k，送出

```
c' ≡ k^e · c (mod N)
```

Alice 解密回傳 `m' ≡ (c')^d ≡ (k^e · m^e)^d ≡ k · m`。Eve 乘上 `k⁻¹` 就得到 m。

```python
p, q, e = 1223, 1987, 948047
N = p * q
d = pow(e, -1, (p - 1) * (q - 1))

def alice_decrypts(x):                  # Alice 天真地替人解密
    return pow(x, d, N)

m = 1070777
c = pow(m, e, N)                        # Eve 攔截到的密文
k = 31337
m_prime = alice_decrypts(pow(k, e, N) * c % N)
print(m_prime * pow(k, -1, N) % N)
```
```output
1070777
```
注意 Eve **完全沒有分解 N**；而 Alice 看到的 `c'`、`m'` 都像亂數，察覺不出和 c 有關。原因是 **RSA 的可乘性**：`(m₁m₂)^e = m₁^e · m₂^e`。防禦方法是加密前加上 **隨機填充**（第 26 課 OAEP），讓密文不再有這種代數結構。

## 4.2 同一個 N 用兩個 e（例 3.14）

Alice 用同一個 N 公布兩個指數 e₁、e₂，Bob 把同一個 m 用兩個都加密了。Eve 解 `e₁u + e₂v = gcd(e₁, e₂)`，

```
c₁^u · c₂^v ≡ m^(e₁u + e₂v) = m^gcd(e₁, e₂)
```

gcd 是 1 時直接得到 m（u 或 v 是負的時，用模反元素）。

```python
p, q = 1223, 1987
N = p * q
e1, e2 = 7, 11                          # 兩個公開指數（都和 φ 互質）
m = 424242
c1, c2 = pow(m, e1, N), pow(m, e2, N)

def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, u1, v1 = ext_gcd(b, a % b)
    return g, v1, u1 - (a // b) * v1

g, u, v = ext_gcd(e1, e2)
print(g, u, v)
print(pow(c1, u, N) * pow(c2, v, N) % N)          # Python 3.8+ 支援負指數（自動取反元素）
```
```output
1 -3 2
424242
```
**教訓**：一個模數只能配一個指數，而且 **不同使用者不能共用 N**。

## 4.3 小加密指數、沒有填充

e = 3 而且 `m³ < N`（短訊息），密文 `c = m³` 根本沒有被取模——直接開實數立方根就得到 m。如果同一則訊息用 e = 3 寄給三個不同的人（三個不同的 N），還能用 CRT 合併三個密文再開立方根（Håstad 廣播攻擊）。

```python
p, q = 2**127 - 1, 2**89 - 1            # 兩個梅森質數，只是示範用
N = p * q
m = int.from_bytes(b"yes", "big")
c = pow(m, 3, N)
r = round(c ** (1 / 3))
while r ** 3 > c:
    r -= 1
while (r + 1) ** 3 <= c:
    r += 1
print(c == m ** 3, r.to_bytes(3, "big"))
```
```output
True b'yes'
```
這又一次說明：**教科書版的 RSA（textbook RSA）不能直接拿來用**，一定要配合隨機填充。

## 4.4 中間人攻擊

和 Diffie–Hellman 一樣（第 06 課 3.4 節），如果 Eve 能把 Bob 的公鑰換成自己的，Alice 就會用 Eve 的公鑰加密。公鑰需要 **認證**（數位簽章與憑證，第 25 課）。

## 4.5 用 CRT 加速解密

Bob 知道 p、q，可以分別在模 p、模 q 解密再用 CRT 組合：

```
m_p = c^(d mod (p−1)) mod p，  m_q = c^(d mod (q−1)) mod q，  m = CRT(m_p, m_q)
```

兩次快速冪的模數和指數都只有一半長，乘法成本約是 1/4，總共約快 **4 倍**。實際的 RSA 函式庫都這樣做。

```python
p, q, e = 1223, 1987, 948047
N = p * q
d = pow(e, -1, (p - 1) * (q - 1))
c = 1473513
mp = pow(c, d % (p - 1), p)
mq = pow(c, d % (q - 1), q)
h = (mp - mq) * pow(q, -1, p) % p          # Garner 公式：m = mq + q·h
m = mq + q * h
print(mp, mq, m, m == pow(c, d, N))
```
```output
652 1771 1070777 True
```
> 🔍 用 CRT 加速也有風險：如果硬體在計算 `m_p` 時出錯（例如被故意照射干擾），算出錯的 m'，那 `gcd(m'^e − c, N)` 就會直接給出 q——這叫 **故障攻擊**（Boneh–DeMillo–Lipton）。所以實作上解密完要先用 e 驗算一次再輸出。

---

# 第五部分：歐拉定理的一般形式

## 5.1 歐拉定理

**定理（歐拉定理）**：`gcd(a, m) = 1` 時，

```
a^φ(m) ≡ 1 (mod m)
```

這就是 Lagrange 定理（第 07 課）套在群 (Z/mZ)* 上，因為 |(Z/mZ)*| = φ(m)。費馬小定理是 m = p 的特例，第一部分的歐拉公式是 m = pq 的特例（`φ(pq) = (p − 1)(q − 1)`）。

## 5.2 φ 的公式

| 情況 | φ |
|---|---|
| p 是質數 | `φ(p) = p − 1` |
| 質數次方 | `φ(p^k) = p^k − p^(k−1)`（扣掉 p 的倍數） |
| `gcd(m, n) = 1` | `φ(mn) = φ(m)φ(n)`（由 CRT：(Z/mnZ)* ≅ (Z/mZ)* × (Z/nZ)*） |
| 一般 | `φ(m) = m · Π (1 − 1/p)`，p 跑遍 m 的質因數 |

```python
from math import gcd

def phi_brute(m):
    return sum(1 for a in range(1, m + 1) if gcd(a, m) == 1)

def phi_formula(m):
    result, n, p = m, m, 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result

print([phi_formula(m) for m in (36, 97, 100, 1001)])
print(all(phi_brute(m) == phi_formula(m) for m in range(1, 500)))
print(pow(7, phi_formula(100), 100))
```
```output
[12, 96, 40, 720]
True
1
```
**注意**：算 φ(m) 的公式需要 **m 的質因數分解**——這正是為什麼 Eve 算不出 RSA 的 φ(N)。

---

# 名詞對照

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 歐拉公式 / 歐拉定理 | Euler's Formula / Theorem | `a^φ(m) ≡ 1 (mod m)` | 1.2、5.1 |
| e 次方根 | e-th Root modulo N | 解 `x^e ≡ c` | 1.3 |
| 模數 / 加密指數 / 解密指數 | Modulus / Encryption / Decryption Exponent | RSA 的 N、e、d | 2.1 |
| RSA 問題 | RSA Problem | 不知道分解時開 e 次方根 | 3.2 |
| 選擇密文攻擊 | Chosen Ciphertext Attack | 讓對方幫忙解密偽裝過的密文 | 4.1 |
| 共用模數攻擊 | Common Modulus Attack | 同一個 N 配兩個 e | 4.2 |
| 教科書 RSA | Textbook RSA | 沒有填充的 RSA，不安全 | 4.3 |
| 故障攻擊 | Fault Attack | 讓硬體算錯來洩漏私鑰 | 4.5 |

---

# 習題

### 題 1：RSA 手算

p = 11、q = 23、e = 3。算 N、φ(N)、d；加密 m = 7；再解密。

### 題 2：模質數開根號

解 `x^3 ≡ 2 (mod 101)`。（先確認 `gcd(3, 100) = 1`。）

### 題 3：從 φ 分解

N = 2038667，φ(N) = 2035800。分解 N。

### 題 4：共用模數

N = 1889570071，Alice 用 e₁ = 1021763679 和 e₂ = 519424709，同一個 m 的兩個密文是 c₁ = 1244183534、c₂ = 732959706（課本習題 3.12）。求 m。

### 題 5：觀念

為什麼 RSA 的 e 不能和 `(p − 1)(q − 1)` 有公因數？如果 e = 2 會發生什麼？

---

# 習題解答

**題 1**：

```python
p, q, e = 11, 23, 3
N, phi = p * q, (p - 1) * (q - 1)
d = pow(e, -1, phi)
c = pow(7, e, N)
print(N, phi, d, c, pow(c, d, N))
```
```output
253 220 147 90 7
```
**題 2**：

```python
p, e, c = 101, 3, 2
d = pow(e, -1, p - 1)
x = pow(c, d, p)
print(d, x, pow(x, 3, p))
```
```output
67 26 2
```
**題 3**：

```python
from math import isqrt
N, phi = 2038667, 2035800
s = N + 1 - phi
r = isqrt(s * s - 4 * N)
print((s - r) // 2, (s + r) // 2)
```
```output
1301 1567
```
**題 4**：

```python
N = 1889570071
e1, e2 = 1021763679, 519424709
c1, c2 = 1244183534, 732959706

def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, u1, v1 = ext_gcd(b, a % b)
    return g, v1, u1 - (a // b) * v1

g, u, v = ext_gcd(e1, e2)
m = pow(c1, u, N) * pow(c2, v, N) % N
print(g, m, pow(m, e1, N) == c1, pow(m, e2, N) == c2)
```
```output
1 1054592380 True True
```
**題 5**：如果 `gcd(e, (p−1)(q−1)) > 1`，e 沒有模 `(p−1)(q−1)` 的反元素，算不出 d；更根本的是 `m ↦ m^e` 不再是一對一，不同的明文會加密成同一個密文，無法唯一解密。e = 2 時一定有公因數 2（p − 1 是偶數）——每個平方數模 N 有 4 個平方根，解密有歧義。（不過 e = 2 變成 **Rabin 密碼**，配上額外的冗餘資訊就能使用，而且破解它等價於分解 N。）
