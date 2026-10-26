# 第 12 章　RSA

> 《Cryptography Engineering》— Ferguson, Schneier, Kohno，本章頁碼：p.195–211

---

## 1. 本章定位

RSA 大概是世界上使用最廣、也最知名的公鑰系統：

- 同時提供**數位簽章**與**公鑰加密**——非常多用途；
- 安全性建立在**大數分解的困難度**上——一個迷住人類數千年、被廣泛研究的問題；
- 由 **Rivest、Shamir、Adleman** 於 1978 年發表。

**與 DH 的差別** ⭐：

| | DH | RSA |
|---|---|---|
| 基礎 | **單向函式**：x → g^x mod p 容易，反向困難 | **陷門單向函式**：m → m^e mod n 容易，反向困難——**除非知道 n 的分解** |
| 陷門 | 無 | n 的因數分解 p、q |
| 用途 | 金鑰協商 | 加密 + 簽章 |

符號：p、q 為不同的大質數（各約一千位元以上），**n := pq**（普通乘法）。

本章也是全書**數學最重的一章的結尾**：之後的金鑰協商與 PKI 只會用到已經解釋過的數學。

---

## 2. 中國剩餘定理（CRT）⭐⭐

模合數 n 運算（Zn 不是體，數學家稱為「環」）。基本版本最早由一世紀的中國數學家**孫子**提出（「DH 與 RSA 需要的數學大多有數千年歷史，所以不會太難吧？」）。

> 對任意 x ∈ Zn，令 (a, b) := (x mod p, x mod q)。**CRT：由 (a, b) 可以唯一還原 x。**

**唯一性證明**：若 x、x' 給出同一組 (a, b)，令 d = x − x'。d mod p = a − a = 0 → d 是 p 的倍數；同理是 q 的倍數 → d 是 lcm(p, q) = pq = n 的倍數。但 d 在 −n+1 … n−1 之間 → d = 0。∎

### 2.1 Garner 公式

```
x = ( ((a − b) · (q⁻¹ mod p)) mod p ) · q + b
```

**驗證**：

- **範圍**：t := ((a−b)(q⁻¹ mod p)) mod p ∈ [0, p−1] ⇒ x = tq + b ≤ (p−1)q + (q−1) = n − 1。
- **mod q**：x = K·q + b ⇒ x mod q = b。
- **mod p**：x ≡ (a − b)·q⁻¹·q + b ≡ (a − b) + b ≡ a。

(q⁻¹ mod p) 只依賴 p、q，可以**預先計算** → Garner 只需一次模 p 減法、一次模 p 乘法、一次完整乘法、一次加法。

CRT 也適用於 n 是多個相異質數的乘積（本書不需要）。

### 2.2 CRT 的用途：加速

把 x 表示成 **CRT 表示法** (x mod p, x mod q)：

| 運算 | CRT 表示法中的做法 | 加速 |
|---|---|---|
| 加法 | 兩半分別模 p、模 q 相加 | 差不多 |
| 乘法 | 兩半分別模 p、模 q 相乘 | 約 **2 倍**（兩次 k/2-bit 乘法遠比一次 k-bit 便宜） |
| **冪次** x^s | 指數也可分別先 mod (p−1)、mod (q−1)：(x^(s mod (p−1)) mod p, x^(s mod (q−1)) mod q) | **3–4 倍** |

> 只有**知道 n 的分解**才能用 CRT 加速。作者認為 CRT 不只是實作技巧，更讓 RSA **容易理解**——所以先講它。

---

## 3. 模 n 的乘法

模質數時 x^(p−1) = 1；模合數 n 時不成立。RSA 需要一個 t 使得對（幾乎）所有 x，x^t ≡ 1 (mod n)。

**用 CRT 推導**：x^t ≡ 1 (mod n) ⟺ x^t ≡ 1 (mod p) 且 x^t ≡ 1 (mod q) ⟺ (p−1) | t 且 (q−1) | t。最小的 t：

```
t = lcm(p − 1, q − 1) = (p − 1)(q − 1) / gcd(p − 1, q − 1)
```

- 大多數教科書用 **Euler φ 函數** φ(n) = (p−1)(q−1)，它是 t 的倍數，用它也對，但 **t 更精確**。
- 小問題：若 x ≡ 0 (mod p)，x^t mod p 不可能是 1。這樣的值共 p + q − 1 個，佔 n 的比例微不足道。
- 更好的是，RSA 真正用到的性質是 **x^(t+1) ≡ x (mod n)**，對這些特殊值也成立（CRT 下 0^(t+1) = 0）→ **對 Zn 中所有數都成立**。

---

## 4. RSA 的定義 ⭐⭐

```
選兩個不同、大小（幾乎）相同的大質數 p、q；n = pq
t = lcm(p − 1, q − 1)
選小的奇數公開指數 e；用 extendedGCD 求 d = e⁻¹ mod t   （ed ≡ 1 mod t）

公鑰：(n, e)          私鑰：(p, q, t, d)

加密：c = m^e mod n
解密：c^d = m^(ed) = m^(kt+1) = (m^t)^k · m = m   (mod n)
```

**記號**：常把 c^d 寫成 **c^(1/e)**——指數都是模 t 計算的，d 是 e 模 t 的反元素，寫成 1/e 很自然，在有多把 RSA 金鑰時更容易閱讀。所以也說「取 **e 次方根**」。記住：**模 n 求任何根都需要私鑰**。

### 4.1 RSA 數位簽章

```
簽章：s = m^(1/e) mod n          → (m, s) 為已簽章訊息
驗證：s^e ≡? m (mod n)           → 任何知道公鑰的人都能驗證
```

安全性同樣基於「只有持有私鑰的人能算出 m 的 e 次方根」。

### 4.2 公開指數 ⭐

- 若 e 與 t 有公因數，d 不存在 → 必須選擇 p、q、e 避免這種情況（麻煩，但不是大問題）。
- e 越小，加密/驗證越快 → 本書**固定 e**，再選合適的 p、q。

**加密與簽章不可互相干擾**：簽「訊息 c」和解密「密文 c」是**同一個運算**！不能讓攻擊者騙私鑰持有者簽 c 來達成解密。

- 後面的編碼函式會防止這件事（概念上類似區塊加密模式——**不要直接使用原始 RSA 運算**）。
- 但即使如此，也不想讓兩個功能共用同一個 RSA 運算。用不同的 RSA 金鑰？複雜度增加、金鑰材料加倍。
- **本書的做法**：同一個 n，用**兩個不同的公開指數**：

| 用途 | e | 理由 |
|---|---|---|
| **簽章** | **3** | 簽章常被驗證多次，資料只加密一次 → 讓驗證更快 |
| **加密** | **5** | |

- 模 n 的立方根與五次方根彼此獨立，知道一個無助於計算另一個。
- 3、5 是最小的合適值（e = 2 理論上可行，但會帶來許多額外複雜度）。
- 限制：p − 1、q − 1 都**不能是 3 或 5 的倍數**（即 **p mod 3 ≠ 1 且 p mod 5 ≠ 1**），產生質數時很容易檢查。
- 其他常見的 e：17、**65537**。作者偏好更小的值（更有效率）；小指數的潛在問題由編碼函式消除。

> **不要為了快而選小的 d**——小 d 是不安全的（Wiener 攻擊）。不要在 d 上玩任何花招。

### 4.3 私鑰

- 只知道 (n, e) 時，求出 p、q、t、d 中任何一個都極難；已知最好的方法是**分解 n**——所以分解對密碼學如此重要。
- **知道 p、q、t、d 中任何一個，就能算出其他三個**：

| 已知 | 推導 |
|---|---|
| p | q = n/p，再算 t、d |
| t | gcd(p−1, q−1) 是最接近 n/t 的整數（不會很大）→ 得 (p−1)(q−1) → p + q = n − (p−1)(q−1) + 1 → 解二次方程式 **p² − (p+q)·p + n = 0** |
| d | e 很小、d < t ⇒ ed − 1 是 t 的小倍數 → 猜倍數得 t → 同上（還有更快的方法） |

- 所以可以合理假設私鑰持有者擁有全部四個值；實作只需存一個，但常為了解密方便存多個。
- 要解密或簽章就必須知道 d ⇒ 等同知道 p、q ⇒ **一定可以用 CRT**——d 次方是 RSA 最貴的運算，CRT 省 3–4 倍。

### 4.4 n 的大小

與 DH 的 p 相同（§11.7）：**至少 2048 bits**（保護 20 年，且下限會緩慢增加）；能負擔就用 **4096 bits**；軟體要**支援到 8192 bits**——能不換軟硬體就切換到更大的金鑰，可能救命。

p、q 大小相等：k-bit 的 n 就產生兩個 k/2-bit 質數相乘（可能得到 k−1 bits，沒什麼關係）。

### 4.5 產生 RSA 金鑰

```
function generateRSAPrime(k) → p
    assert 1024 ≤ k ≤ 4096
    r ← 100k
    repeat
        r ← r − 1
        assert r > 0
        n ∈R 2^(k−1), …, 2^k − 1
    until n mod 3 ≠ 1 ∧ n mod 5 ≠ 1 ∧ isPrime(n)
    return n

function generateRSAKey(k) → p, q, n, d3, d5
    assert 2048 ≤ k ≤ 8192
    p ← generateRSAPrime(k/2)
    q ← generateRSAPrime(k/2)
    assert p ≠ q                           以防 PRNG 很爛……
    t ← (p − 1)(q − 1) / GCD(p − 1, q − 1)
    g, (u, v) ← extendedGCD(3, t);  assert g = 1;  d3 ← u mod t     簽章指數
    g, (u, v) ← extendedGCD(5, t);  assert g = 1;  d5 ← u mod t     解密指數
    return p, q, pq, d3, d5
```

- 聰明的實作在 n mod 3、mod 5 不合格時根本不呼叫 isPrime（很貴）。
- **範圍這麼大，為何還要限制嘗試次數？** 不是怕區間沒有質數，而是怕**壞掉的 PRNG 一直回傳同一個合數**——很常見的 RNG 故障模式；或 isPrime 壞掉一直說「合數」。這個簡單的檢查讓函式不會在這些情況下當住。

---

## 5. 使用 RSA 的陷阱 ⭐⭐

**到目前為止的 RSA 非常危險**——問題出在**數學結構**。

### 5.1 乘法性質

Alice 簽了 m1 和 m2，Bob 就能算出 m3 = m1·m2 的簽章：

```
m1^(1/e) · m2^(1/e) = (m1 · m2)^(1/e)    (mod n)
```

### 5.2 小訊息沒有模約減

e = 5 且 m < n^(1/5) 時，m^5 < n，**從頭到尾沒有發生取模** → Eve 直接對 m^5 開五次方根（普通實數運算）就得到 m。

> 典型錯誤：Bob 把 256-bit 的 AES 金鑰直接當整數用 RSA 加密給 Alice → 密文 < 2^(256·5) = 2^1280，遠小於 n → 從未取模 → Eve 直接開五次方根拿到金鑰。

### 5.3 結論：摧毀結構

還有更進階的攻擊（解模 n 多項式方程式，例如 Coppersmith），全部歸結為一件事：

> **讓 RSA 運算的數字帶有任何結構，都非常糟糕。**

解法：使用能**摧毀所有結構**的函式。有人叫它「padding」，但這是**誤稱**——padding 通常指補足長度；人們用各種「padding」做 RSA，很多次都被攻破（例如 PKCS#1 v1.5 的 Bleichenbacher 攻擊）。作者稱它為**編碼函式（encoding function）**。

**標準**：PKCS #1 v2.1——兩種加密方案、兩種簽章方案，各可搭配多種雜湊。實務上用標準化演算法有很多好處：

- 加密：**RSA-OAEP**
- 簽章：**RSA-PSS**

本書為教學目的給出更簡單的方法。

**順帶一提：規格與實作混雜** ——PKCS #1 把 RSA 解密寫了兩次：一次用 m = c^d mod n，一次用 CRT 方程式。兩者結果相同，後者只是前者的最佳化實作，**不應出現在標準中**（不產生不同行為）。這是整個電腦產業普遍的問題。

> 對照第 8 章：功能規格只描述**外部可觀察的行為**；CRT 加速屬於實作設計。

---

## 6. 加密 ⭐⭐

RSA 加密是教科書上的標準應用，**實務上卻幾乎從不直接用來加密訊息**：

- 可加密的訊息大小受 n 限制（編碼函式還有額外開銷）；
- RSA 運算很貴，不想把訊息切成很多塊分別加密。

**標準解法（混合加密）**：選隨機對稱金鑰 K，用 RSA 加密 K，再用 K 加密訊息：送出 E_RSA(K), E_K(m)。

**本書更簡單的做法**：不加密 K，而是**加密一個隨機數 r**，令 **K := h(r)**：

```
function encryptRandomKeyWithRSA((n, e)) → K, c       e = 5
    k ← ⌊log2 n⌋                     最大的 k 使 2^k < n
    r ∈R 0, …, 2^k − 1
    K ← SHAd-256(r)
    c ← r^e mod n
    return (K, c)

function decryptRandomKeyWithRSA((n, d), c) → K
    assert 0 ≤ c < n
    K ← SHAd-256(c^(1/e) mod n)      用 CRT 加速 3–4 倍
    return K
```

- r 是隨機的 → RSA 部分**沒有任何結構**可供攻擊。
- 雜湊確保不同 r 之間的結構不會傳到 K（除了「相同輸入得相同輸出」）。
- 為了實作簡單，r 取 0 … 2^k − 1 而不是 Zn——產生 k-bit 隨機數更容易，這點小偏差在此無害。

**安全論證**：

1. Bob 的訊息只依賴隨機資料與 Alice 的公鑰 → 最壞也只可能洩漏 K 的資訊，**不可能洩漏 Alice 私鑰等其他秘密**。
2. 雜湊可視為隨機映射 → 要得知輸出的資訊，必須知道輸入的大部分 → 必須知道 r；而若 RSA 安全，從 r^e mod n 得不到 r 的有意義資訊。
3. **若 K 後來外洩**（系統其他部分出錯）：雜湊不可逆 → 推不出 r → 推不出 Alice 的私鑰（私鑰只用來計算 r）。

**為何解密函式裡一定要有雜湊？** ⭐

若直接回傳 c^(1/e) mod n，且系統其他部分的弱點讓 Eve 學到輸出的**最低位元**，Eve 就能送出特別挑選的 c1, c2, c3, … 給 Alice，得到 c1^(1/e), c2^(1/e), … 的最低位元——這些答案有各種代數性質，Eve 很可能學到有用的東西。雜湊**摧毀所有數學結構**：學到 K 的一個位元幾乎得不到 c^(1/e) 的資訊；即使拿到完整的 K 也沒多少用處。

> **加入雜湊，讓 RSA 常式在系統其他部分失敗時也更安全。**

**為何解密時「不檢查」r 是否在 0 … 2^k − 1？** ⭐

若檢查，就得處理可能的錯誤；錯誤處理一定會產生**不同的行為**，Eve 很可能偵測得到——這等於給 Eve 一個函式：任選 c，就能知道 c^(1/e) mod n 是否 < 2^k。這是 Eve 沒有 Alice 幫忙就算不出來的性質。不檢查，最多產生一個無意義的輸出——而這本來就可能發生（c 可能被破壞成另一個合法範圍的 r；Eve 也隨時可以用 Alice 的公鑰送她無意義的金鑰）。

> 對照第 7 章：同樣的原則——**不要替攻擊者提供 oracle**。Bleichenbacher（1998）正是利用 PKCS#1 v1.5 解密時的「填充格式是否正確」錯誤訊息，對 SSL 發動百萬次查詢還原明文。

**重要區別**：

- **公開隨機的 (c, c^(1/e)) 配對**沒有任何秘密：任何人都能選隨機 r，算 (r^e, r)。
- 但**替別人選的 c 計算 c^(1/e)**，就讓對方能挑選具有特殊性質的 c。**不要為攻擊者提供這種額外服務。**

---

## 7. 簽章 ⭐⭐

要簽的訊息 m 可能有大量結構，而我們不要任何結構出現在要開根號的數字中——必須**摧毀結構**。

1. 先雜湊：h(m)（SHAd-256 得 256 bits）。但 n 大得多，不能直接用 h(m)（又會變成沒有取模的小數字）。
2. 用**偽隨機映射**把 h(m) 擴展成 0 … n−1 範圍的隨機數 s，簽章 = s^(1/e)。
3. 簡化：映射到 0 … 2^k − 1（只需 k 個隨機位元）。**在這個特定情境下安全，但不要隨處使用**——密碼學中有許多情況這麼做會毀掉整個系統。
4. 使用 **Fortuna 的 generator**（ch9）——反正產生 RSA 金鑰也需要 PRNG，程式裡早就有了。

```
function MsgToRSANumber(n, m) → s
    G ← InitializeGenerator()
    Reseed(G, SHAd-256(m))
    k ← ⌊log2 n⌋
    x ← PseudoRandomData(G, ⌈k/8⌉)
    s ← x mod 2^k                  LSByte-first；只需對最後一個 byte 做 and
    return s

function SignWithRSA((n, d), m) → σ          e = 3
    s ← MsgToRSANumber(n, m)
    σ ← s^(1/e) mod n

function VerifyRSASignature((n, e), m, σ)
    s ← MsgToRSANumber(n, m)
    assert s = σ^e mod n
```

**驗證失敗時**：和密碼協定中的任何失敗一樣，視為**正遭受主動攻擊的明確訊號**——除非絕對必要，不要送出任何回應，並銷毀所有正在處理的資料。**你送出的資訊越多，給攻擊者的資訊就越多。**

**安全論證**：

- 請 Alice 簽一堆訊息，得到的是 (s, s^(1/e)) 配對，但 s 實質上是隨機的（雜湊安全 → 只能靠試誤影響 h(m)；generator 又是隨機映射）。
- 任何人都能為**隨機** s 產生 (s, s^(1/e))，所以這些配對不提供偽造簽章的新資訊。
- 但對**特定**訊息 m，s 必須由 h(m) 算出，再算 s^(1/e)——需要私鑰。所以驗證者知道一定是 Alice 簽的。

---

## 8. 參考實作（Python）

依書中虛擬碼寫成（`is_prime`、`extended_gcd` 來自 ch10；`Generator`、`shad256` 來自 ch9 的 Fortuna 實作）。實測：2048-bit 金鑰、金鑰傳輸、簽章驗證、竄改偵測，以及原始 RSA 的乘法性質。

```python
import secrets
from math import gcd
from primes import is_prime, extended_gcd
from fortuna import Generator, shad256

def generate_rsa_prime(k: int) -> int:
    """k-bit 質數，且 p mod 3 ≠ 1、p mod 5 ≠ 1（才能用 e = 3 與 e = 5）"""
    assert 1024 <= k <= 4096
    r = 100 * k
    while True:
        r -= 1
        assert r > 0, "PRNG or isPrime broken?"     # 防壞掉的 PRNG 一直給同一個合數
        n = (1 << (k - 1)) + secrets.randbelow(1 << (k - 1))
        if n % 3 != 1 and n % 5 != 1 and is_prime(n):   # 先做便宜的檢查
            return n

def generate_rsa_key(k: int):
    assert 2048 <= k <= 8192
    p = generate_rsa_prime(k // 2)
    q = generate_rsa_prime(k // 2)
    assert p != q                                    # 以防 PRNG 很爛
    t = (p - 1) * (q - 1) // gcd(p - 1, q - 1)       # t = lcm(p−1, q−1)
    g, u, _ = extended_gcd(3, t); assert g == 1; d3 = u % t
    g, u, _ = extended_gcd(5, t); assert g == 1; d5 = u % t
    return dict(p=p, q=q, n=p * q, d3=d3, d5=d5, qinv=pow(q, -1, p))

def root_crt(key, c: int, e: int) -> int:
    """c^(1/e) mod n，用 CRT 與 Garner 公式（約快 3–4 倍）"""
    p, q, qinv = key["p"], key["q"], key["qinv"]
    a = pow(c, pow(e, -1, p - 1), p)                 # 指數可先 mod (p−1)
    b = pow(c, pow(e, -1, q - 1), q)
    return ((a - b) * qinv % p) * q + b              # Garner

def encrypt_random_key(n: int):
    k = n.bit_length() - 1                           # 最大的 k 使 2^k < n
    r = secrets.randbits(k)
    K = shad256(r.to_bytes((n.bit_length() + 7) // 8, "little"))   # 固定長度編碼
    return K, pow(r, 5, n)

def decrypt_random_key(key, c: int) -> bytes:
    n = key["n"]
    assert 0 <= c < n
    r = root_crt(key, c, 5)                          # 刻意不檢查 r < 2^k：不替攻擊者提供 oracle
    return shad256(r.to_bytes((n.bit_length() + 7) // 8, "little"))

def msg_to_rsa_number(n: int, m: bytes) -> int:
    G = Generator()
    G.reseed(shad256(m))
    k = n.bit_length() - 1
    x = int.from_bytes(G.pseudo_random_data((k + 7) // 8), "little")
    return x % (1 << k)

def sign(key, m: bytes) -> int:
    return root_crt(key, msg_to_rsa_number(key["n"], m), 3)

def verify(n: int, m: bytes, sigma: int) -> bool:
    return msg_to_rsa_number(n, m) == pow(sigma, 3, n)

if __name__ == "__main__":
    key = generate_rsa_key(2048)
    n = key["n"]
    print("n bits:", n.bit_length())
    K, c = encrypt_random_key(n)
    print("key transport ok:", decrypt_random_key(key, c) == K)
    s = sign(key, b"pay Bob $10")
    print("verify:", verify(n, b"pay Bob $10", s), " tampered:", verify(n, b"pay Bob $1000", s))
    # 原始 RSA 的乘法性質：sig(m1)·sig(m2) = sig(m1·m2)
    m1, m2 = 5416, 2397
    print("raw RSA multiplicative:", root_crt(key, m1, 3) * root_crt(key, m2, 3) % n == root_crt(key, m1 * m2 % n, 3))
```

實測輸出：

```
n bits: 2048
key transport ok: True
verify: True  tampered: False
raw RSA multiplicative: True
```

> 最後一行示範 §5.1：**原始** RSA 簽章具有乘法性質——這正是要用 `msg_to_rsa_number` 摧毀結構的原因。

---

## 9. 設計觀念整理

| 觀念 | 說明 |
|---|---|
| 陷門單向函式 | 知道分解才能反轉——同時支援加密與簽章 |
| CRT 讓 RSA 易懂又快 | 拆成模 p、模 q 兩半；冪次快 3–4 倍 |
| t = lcm 比 φ(n) 精確 | x^(t+1) ≡ x 對所有 x 成立 |
| 用不同指數分離用途 | e = 3 簽章、e = 5 加密，共用 n |
| 私鑰四值等價 | 知道 p、q、t、d 任一即可推出其餘 |
| 不要直接用原始 RSA | 乘法性質、無取模的小訊息 → 必須用編碼函式 |
| 摧毀結構 | 加密：K = h(r)；簽章：h(m) 經 PRNG 擴展 |
| 不提供 oracle | 解密不檢查 r 範圍；失敗不回應 |
| 規格 ≠ 實作 | CRT 不該寫進標準 |
| 防壞掉的 PRNG | 即使區間很大，也要限制嘗試次數；assert p ≠ q |

> 對照第一本書：Hanson 的 `AP` 介面（ch18）提供 `AP_pow(x, y, p)`——p 非空時回傳 x^y mod p，再加上 `AP_mod`、`AP_div`，就足以實作本章的 RSA（`MP` 介面則提供固定位元數的版本）。他也刻意讓這些介面的錯誤以例外（如 `MP_Overflow`）或 checked runtime error 處理，不讓呼叫者忽略；本章則更進一步：在密碼情境中，連「錯誤是否發生」都可能是洩漏，所以有時寧可**不檢查**。

---

## 10. 延伸閱讀重點

- **Rivest, Shamir, Adleman**（1978）原始論文。
- **Boneh**（1999）：*Twenty Years of Attacks on the RSA Cryptosystem*——整理各種結構攻擊。
- **Wiener**（1990）：小 d 攻擊；**Coppersmith**（1996）：小指數與部分已知明文。
- **Bleichenbacher**（1998）：PKCS#1 v1.5 padding oracle；2017 年的 **ROBOT** 攻擊顯示它 19 年後仍存在於許多 TLS 實作。
- **Bellare & Rogaway**：OAEP（1994）、PSS（1996）。
- **RFC 8017**（PKCS #1 v2.2）。
- **Boneh, DeMillo, Lipton**（1997）：CRT 實作的**故障攻擊**——一次計算錯誤的 CRT 簽章就能分解 n（實作必須驗證簽章後再輸出）。
- 現代趨勢：TLS 1.3 移除了 RSA 金鑰傳輸，只保留 RSA-PSS 簽章；新系統多改用 Ed25519 / X25519。

---

## 11. 習題摘要

| 題號 | 題目 | 答案 |
|---|---|---|
| 12.1 | p = 89、q = 107，求 x 使 x ≡ 3 (mod p)、x ≡ 5 (mod q) | **x = 8458**（Garner 公式） |
| 12.2 | x = 1796、y = 8931，直接算與用 CRT 算 x + y (mod n) | **1204**（兩者相同） |
| 12.3 | 同上，x · y (mod n) | **3344** |
| 12.4 | p = 83、q = 101、e = 3 是合法 RSA 公鑰嗎？ | **是**：t = lcm(82, 100) = 4100，gcd(3, 4100) = 1；**d = 1367**（3 · 1367 = 4101 = 4100 + 1） |
| 12.5 | p = 79、q = 89、e = 3 呢？ | **否**：79 − 1 = 78 是 3 的倍數，t = 3432 與 3 不互質，d 不存在 |
| 12.6 | Alice 為了加速解密選 d = 3、再算 e = d⁻¹ mod t，好嗎？ | **非常糟**：d 小到可以直接猜（甚至 Wiener 攻擊）；而且 e 變成很大的數，驗證/加密變慢——書中明言「不要在 d 上玩花招」 |
| 12.7 | 256-bit 模數的 RSA 金鑰強度接近 256-bit AES 嗎？ | **完全不是**：256-bit n 在一般電腦上幾分鐘內就能分解；**永遠不要拿對稱金鑰長度和公鑰長度比較** |
| 12.8 | p = 71、q = 89、e = 3：求 d，並驗證 sig(m1)·sig(m2) = sig(m1·m2) | t = 3080，**d = 1027**；sig(5416) = 1876、sig(2397) = 2206、m3 = 2926、sig(m3) = **5830** = 1876 · 2206 mod n ✓ |

> 以上數值皆以 Python 實際計算驗證。

---

## 12. 本章重點整理

1. RSA = **陷門單向函式**；陷門是 n = pq 的分解；同時支援加密與簽章。
2. **CRT**：x ↔ (x mod p, x mod q)，Garner 公式還原；讓冪次運算快 3–4 倍。
3. t = lcm(p−1, q−1)；ed ≡ 1 (mod t)；x^(t+1) ≡ x 對所有 x 成立。
4. 本書用同一個 n、**e = 3 簽章、e = 5 加密**；p、q 須滿足 mod 3 ≠ 1、mod 5 ≠ 1；d 絕不可以小。
5. 知道 p、q、t、d 任一值就能推出全部——安全等同於分解 n。
6. n ≥ 2048 bits、盡量 4096、支援到 8192。
7. **原始 RSA 很危險**（乘法性質、未取模的小訊息）→ 必須用摧毀結構的**編碼函式**（實務上用 OAEP、PSS）。
8. 加密：傳送 r^5，K = SHAd-256(r)；簽章：SHAd-256(m) → PRNG 擴展 → 開立方根。不提供 oracle，失敗就沉默。

> **一句話**：RSA 的數學很優雅，但優雅的結構正是攻擊的入口——永遠不要直接用原始 RSA，先用雜湊和 PRNG 把數字攪成毫無結構的隨機數。
