# 第 7 章　安全通道（The Secure Channel）

> 《Cryptography Engineering》— Ferguson, Schneier, Kohno，本章頁碼：p.99–114

---

## 1. 本章定位

前四章準備好了積木——區塊加密器（ch3）、加密模式（ch4）、雜湊（ch5）、MAC（ch6）。本章終於要解決**第一個真實世界的問題**：

> **安全通道**——在 Alice 與 Bob 之間建立一條安全連線。這大概是所有實務問題中最常見的一個（TLS、SSH、IPsec 的核心都是它）。

本章的價值不只是一份設計，而是**示範如何思考**：每個細節（編號從 1 開始、錯誤檢查的順序、失敗時要銷毀什麼）背後都有理由。

---

## 2. 安全通道的性質

### 2.1 角色

- 連線幾乎都是**雙向**的；兩個方向的訊息流**不可混淆**，所以協定必須有**不對稱性**：client/server、initiator/responder……怎麼分都行，但雙方都必須清楚誰扮演 Alice、誰扮演 Bob。
- **Eve** 能讀取所有通訊，並任意**刪除、插入、修改**資料。

**把儲存視為「傳給未來」** ⭐：安全儲存（備份磁帶、USB 隨身碟）也適用本章——Alice 和 Bob 可以是同一人。差別在於：未來無法回傳訊息給過去，所以**不能使用互動式協定**。

### 2.2 金鑰

- 雙方共享秘密金鑰 K，**只有** Alice 與 Bob 知道。
- 密碼元件**永遠無法辨識「Alice 這個人」**，最多只能辨識**金鑰**。Bob 的驗證只能告訴他：

  > 「這則訊息是由某個**知道 K、並扮演 Alice 角色**的人送出的。」

  這句話只有在 Bob 確信 K 的知情範圍受限時才有用。

金鑰需求：

1. K 只有 Alice 與 Bob 知道。
2. **每次初始化安全通道，都要產生新的 K**（session key）。否則舊 session 的訊息可以被重放，造成混亂。即使用固定密碼當金鑰，也要跑金鑰協商協定產生唯一的 K（第 14 章）。

設計強度 128 bits → 依 §3.5.7，K 為 **256 bits**。

### 2.3 訊息還是串流？

- 只處理**離散訊息**；串流可以切成訊息、在接收端重組。實務上幾乎所有系統在密碼層都是訊息式。
- 假設底層傳輸**不可靠**。⭐ 即使 TCP 也只對**隨機事件**（封包遺失）可靠，攻擊者可以輕易修改、刪除、插入 TCP 資料而不中斷資料流。

> 從對抗的觀點看，**根本沒有可靠的通訊協定**。（這是密碼學家看世界方式的好例子。）

### 2.4 安全性質 ⭐⭐

Alice 送出 m1, m2, …；Bob 收到 m1', m2', …：

| 性質 | 要求 |
|---|---|
| **機密性** | Eve 除了訊息的**時間與大小**外，學不到任何東西 |
| **真實性 + 順序** | 即使 Eve 操縱資料，Bob 收到的序列是原序列的**子序列**，而且 Bob **確切知道**收到的是哪個子序列 |

**機密性的現實**：要隱藏大小與時間，已知方法是 Alice 以**最大頻寬持續發送**，沒東西就送假訊息——軍方或許能接受，民用不行。所以 Eve 仍可做**流量分析**（SSL/TLS、IPsec、SSH 也一樣），本書不解決。

**子序列的意義**：

- Eve 一定能刪訊息，所以 Bob 只能得到子序列；
- 但收到的訊息**依序、無重複、無竄改、無偽造**；
- 而且 Bob 知道漏了哪些（有些應用的語意取決於順序）。

**為何不在通道內做重送？** 重送是 Alice（或上層協定）的事：ACK 與重送是標準通訊技術，可以疊在安全通道之上。

> **讓安全關鍵模組保持簡單。**（對照第一本書：Hanson 也把「最小而完整的介面」當成首要原則。）

---

## 3. 認證與加密的順序 ⭐⭐

| 方式 | 做法 |
|---|---|
| **Encrypt-then-Authenticate (EtA)** | 先加密，再對密文做 MAC |
| **Authenticate-then-Encrypt (AtE)** | 先對明文做 MAC，再把明文 + MAC 一起加密 |
| **Encrypt-and-Authenticate (E&A)** | 分別加密明文、MAC 明文，再組合 |

### 3.1 支持 EtA 的理由

1. **理論結果**：在特定的安全定義下，EtA 可證明安全，其他兩者不行。
   - 但細看會發現：AtE 只有在加密方案有**特定弱點**時才不安全，實務上不會用那種方案；而且對串流加密（CTR）及「IV 有被認證的 CBC」，也有證明這些問題根本不會發生。
2. **更有效率地丟棄偽造訊息**：Bob 先驗 MAC，不必解密假訊息 → 對 DoS 稍有幫助，但**最多約 2 倍**；而且現實中更有效的 DoS 是塞爆頻寬，不是拖垮 CPU。

### 3.2 支持 E&A 的理由

- 加密與認證可**平行**進行。
- 但 MAC 是對**明文**、且**沒被加密**——MAC 是為真實性設計，不是為機密性，**MAC 值可能洩漏明文資訊**。需謹慎選擇元件並把 nonce 等額外資料納入 MAC，才能安全。

### 3.3 支持 AtE 的理由（作者的選擇）

1. **保護 MAC**：EtA 中，MAC 的輸入與輸出 Eve 都看得到；AtE 中，Eve 只看得到密文與**加密過的 MAC**。

   > 真正的選擇是：**哪個函式放在最後、直接暴露給 Eve？** 多數情況下**竄改比偷看危害更大**，所以作者寧可讓加密直接面對攻擊，把 MAC 盡量保護起來。（若兩者都安全，這些爭論都無意義；但專業偏執要求即使不假設這點也要有韌性。）

2. **Horton 原則**：認證密文 = 認證「說了什麼」，不是「意思」。危險：Bob 驗證密文的 MAC 正確後，卻用**另一把金鑰**解密，得到與 Alice 不同的明文（IPsec 有某種罕見設定確實如此）。
   - 把加密金鑰放進 MAC？作者不喜歡把金鑰用在正常用途以外。
   - 標準解法：**從同一把通道金鑰衍生加密金鑰與認證金鑰**（§5.1）——但這引入了交叉依賴：認證的安全突然取決於金鑰衍生。

> **結論**：三種順序都能做出好系統，也都能做出壞系統。本章選 **AtE**——因為它簡單，且在實務偏執模型下安全。
>
> 後見之明：TLS 的 MAC-then-Encrypt + CBC 後來吃了 **Lucky 13**、**POODLE** 等 padding oracle 攻擊；業界最終轉向 AEAD（TLS 1.3 只允許 AEAD）。作者的設計用 **CTR（無填充）** 且**驗證失敗時不洩漏任何資訊**，避開了這類問題。

---

## 4. 設計概觀：三個元件

### 4.1 訊息編號 ⭐

訊息編號的用途：

1. 作為加密的 **IV / nonce 來源**；
2. 讓 Bob **拒絕重放**，不必維護大型資料庫；
3. 告訴 Bob **哪些訊息遺失**；
4. 確保 Bob **依正確順序**收到訊息。

因此必須**單調遞增**且**唯一**。

- Alice 第一則編號 1、第二則 2……Bob 記住上一則的編號，只接受更大的編號。
- 使用 **32-bit** 編號，最多 **2^32 − 1** 則；溢位前必須重跑金鑰協商。**絕不可回繞到 0。**
- 64-bit 每則訊息要多 4 bytes；32 bits 對多數應用已足，而且金鑰本來就該定期更換（想用 40 或 48 bits 也無妨）。

**為何從 1 開始，而不是 C 程式設計師習慣的 0？** ⭐⭐

```
可指派的編號有 N 個 → 「已送出訊息數」有 N+1 種狀態 {0, …, N}

從 1 開始、上限 2^32 − 1：狀態 {0 … 2^32−1} 剛好塞進一個 32-bit 整數
從 0 開始：需要額外的旗標表示「還沒送過」或「編號已用盡」
```

> 額外的旗標會帶來大量**很少被執行的棘手程式碼**；很少執行 → 很少被測試 → 更可能是錯的。從 1 開始，就消滅了**一整類**容易犯的錯。

### 4.2 認證

- **HMAC-SHA-256**，使用完整 256-bit 結果。
- 輸入包含訊息 mi 與**額外認證資料 xi**（Horton 原則：協定識別、版本號、協商的欄位大小等，由應用提供，雙方相同）。

```
ai := mac( i ‖ ℓ(xi) ‖ xi ‖ mi )
```

- i 與 ℓ(xi) 都是 **32-bit 無號整數，最低位元組在前（little-endian）**。
- **ℓ(xi) 確保整串能唯一解析**；少了它，i、xi、mi 的切法有很多種，認證就有歧義。
- xi 本身要能不靠額外上下文解析成欄位——這在通道層無法保證，要由應用負責。

### 4.3 加密

**AES-CTR**。等等——第 4 章不是說 CTR 因 nonce 很危險嗎？

> 危險的是**把 nonce 的控制權交給開發者**。安全通道在**內部**處理 nonce（就是訊息編號），從不交給其他人。所以這裡用 CTR 沒問題；但作者仍建議**永遠不要直接使用 CTR**。

- 每則訊息上限 **16 · 2^32 bytes**（區塊計數器 32 bits，比 64 bits 好實作）。
- 金鑰流：

```
k0, k1, … := E(K, 0 ‖ i ‖ 0) ‖ E(K, 1 ‖ i ‖ 0) ‖ … ‖ E(K, 2^32−1 ‖ i ‖ 0)

每個區塊 = 32-bit 區塊編號 ‖ 32-bit 訊息編號 ‖ 64 個 0 位元
```

- 只用前 **ℓ(mi) + 32** bytes（訊息 + 32-byte MAC）；後面當然不用算。
- 把 mi ‖ ai 與金鑰流 xor。

### 4.4 封包格式

```
┌──────────────┬───────────────────────────────────┐
│ i (4 bytes,  │  (mi ‖ ai) ⊕ keystream            │
│  LSB first)  │  ℓ(mi) bytes      +   32 bytes    │
└──────────────┴───────────────────────────────────┘
```

---

## 5. 設計細節

通道定義為**雙向**、同一把金鑰兩個方向共用：

> 如果定義成單向，**你可以打賭一定有人把同一把金鑰用在兩個方向**，徹底摧毀安全性。定義成雙向就降低了這個風險。反過來說，若你用別人定義的安全通道，**特別小心不要兩個方向共用金鑰**。

### 5.1 初始化

從通道金鑰衍生 **4 把子金鑰**（兩個方向 × 加密/認證）：

```
function InitializeSecureChannel(K: 256-bit key, R: role) → S
    KeySendEnc  ← SHAd-256(K ‖ "Enc Alice to Bob")
    KeyRecEnc   ← SHAd-256(K ‖ "Enc Bob to Alice")
    KeySendAuth ← SHAd-256(K ‖ "Auth Alice to Bob")
    KeyRecAuth  ← SHAd-256(K ‖ "Auth Bob to Alice")
    if R = "Bob" then
        swap(KeySendEnc, KeyRecEnc)
        swap(KeySendAuth, KeyRecAuth)
    fi
    (MsgCntSend, MsgCntRec) ← (0, 0)
    return S = (四把金鑰, MsgCntSend, MsgCntRec)
```

- 字串是純 ASCII，不含長度或結尾 0。
- **用完要清除 S 的記憶體**——很多系統釋放記憶體並不會抹除內容，而裡面有金鑰。

### 5.2 傳送訊息

```
function SendMessage(S, m, x) → t
    assert MsgCntSend < 2^32 − 1          ← 極度重要！
    MsgCntSend ← MsgCntSend + 1
    i ← MsgCntSend
    a ← HMAC-SHA-256(KeySendAuth, i ‖ ℓ(x) ‖ x ‖ m)
    t ← m ‖ a
    k ← E_K(0 ‖ i ‖ 0) ‖ E_K(1 ‖ i ‖ 0) ‖ …     (K = KeySendEnc)
    t ← i ‖ (t ⊕ First-ℓ(t)-bytes(k))
    return t
```

- **計數器溢位檢查再怎麼強調都不為過**：計數器一旦回繞，整個安全性崩潰——作者常看到這個錯誤。
- 會修改狀態 S（MsgCntSend），這也至關重要。「這些演算法裡幾乎每一樣東西都關乎安全。」
- 若改用需要填充的加密，解密時要驗證填充內容。

### 5.3 接收訊息 ⭐⭐

```
function ReceiveMessage(S, t, x) → m
    assert ℓ(t) ≥ 36                       4-byte 編號 + 32-byte MAC
    i ‖ t ← t                              i 固定 4 bytes，切法唯一
    k ← E_K(0 ‖ i ‖ 0) ‖ …                 (K = KeyRecEnc)
    m ‖ a ← t ⊕ First-ℓ(t)-bytes(k)        a 固定 32 bytes，切法唯一
    a' ← HMAC-SHA-256(KeyRecAuth, i ‖ ℓ(x) ‖ x ‖ m)
    if a ≠ a' then
        destroy k, m
        return AuthenticationFailure
    else if i ≤ MsgCntRec then
        destroy k, m
        return MessageOrderError
    fi
    MsgCntRec ← i
    return m
```

**為何先驗 MAC、再檢查順序？** 如果先檢查編號，當 i 在傳輸中被破壞時，函式會回報「順序錯誤」而不是「訊息被竄改」。呼叫者可能對兩種情況有不同處理，所以**不應給出錯誤資訊**。至於「先檢查可以更快丟掉假訊息」——如果假封包多到這點速度有差，你早就有更大的問題了。

**最重要的一點：驗證通過前，絕不洩漏金鑰流或明文** ⭐⭐⭐

- 攻擊者知道密文 → **明文 = 金鑰流**的洩漏。
- 危險情境：攻擊者送出 MAC 錯誤的假訊息，卻從接收端釋出的資料中學到金鑰流。
- 偏執模型：**這個函式釋出或洩漏的任何資料，都假設會落入攻擊者手中**。所以失敗前要先**銷毀 k 與 m**。

### 5.4 訊息順序

接收端只接受**嚴格遞增**的編號 → 不會重複接受，但傳輸中被重排的合法訊息會遺失。

| 策略 | 適用 |
|---|---|
| 嚴格遞增（本章） | 修好底層傳輸、避免意外重排；多數應用無法處理亂序，能處理的也常有微妙（往往與安全有關的）bug |
| **IPsec 重放視窗** | IP 封包本來就會亂序，應用也都知道；維護最近 32 個編號的 bitmap |
| 遺失即終止 | 跑在 TCP 等可靠傳輸上：沒有惡意活動時不該遺失或亂序，一旦發生就中止連線 |

**IPsec 重放視窗**（c = 最後收到的編號）：

```
編號 < c−31          → 一律拒絕
c−31 ≤ 編號 ≤ c−1    → 對應 bit 為 0 才接受，並設為 1
編號 > c             → 更新 c，bitmap 位移
```

以很少的狀態允許有限度的重排。

---

## 6. 參考實作（Python）

以下依書中虛擬碼寫成的可執行版本（使用 `cryptography` 函式庫；已實測：正常收送、重放回報 `MessageOrderError`、竄改回報 `AuthenticationFailure`）。

```python
import hashlib, hmac, struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def shad256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b"\x00" * 64 + data).digest()).digest()

def keystream(key: bytes, i: int, n: int) -> bytes:
    enc = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    blocks = (n + 15) // 16
    data = b"".join(struct.pack("<II", j, i) + b"\x00" * 8 for j in range(blocks))
    return enc.update(data)[:n]

class SecureChannel:
    def __init__(self, K: bytes, role: str):
        a2b, b2a = b"Alice to Bob", b"Bob to Alice"
        self.send_enc, self.rec_enc = shad256(K + b"Enc " + a2b), shad256(K + b"Enc " + b2a)
        self.send_auth, self.rec_auth = shad256(K + b"Auth " + a2b), shad256(K + b"Auth " + b2a)
        if role == "Bob":
            self.send_enc, self.rec_enc = self.rec_enc, self.send_enc
            self.send_auth, self.rec_auth = self.rec_auth, self.send_auth
        self.cnt_send = self.cnt_rec = 0

    def send(self, m: bytes, x: bytes) -> bytes:
        assert self.cnt_send < 2**32 - 1, "rekey required"
        self.cnt_send += 1
        i = self.cnt_send
        a = hmac.new(self.send_auth, struct.pack("<II", i, len(x)) + x + m, hashlib.sha256).digest()
        t = m + a
        k = keystream(self.send_enc, i, len(t))
        return struct.pack("<I", i) + bytes(p ^ q for p, q in zip(t, k))

    def receive(self, t: bytes, x: bytes) -> bytes:
        if len(t) < 36:
            raise ValueError("too short")
        i = struct.unpack("<I", t[:4])[0]
        body = t[4:]
        k = keystream(self.rec_enc, i, len(body))
        ma = bytes(p ^ q for p, q in zip(body, k))
        m, a = ma[:-32], ma[-32:]
        a2 = hmac.new(self.rec_auth, struct.pack("<II", i, len(x)) + x + m, hashlib.sha256).digest()
        if not hmac.compare_digest(a, a2):
            raise ValueError("AuthenticationFailure")   # 不洩漏 m 或 k
        if i <= self.cnt_rec:
            raise ValueError("MessageOrderError")
        self.cnt_rec = i
        return m

if __name__ == "__main__":
    K = bytes(range(32))
    alice, bob = SecureChannel(K, "Alice"), SecureChannel(K, "Bob")
    x = b"proto=demo;v=1"
    t1 = alice.send(b"hello Bob", x)
    print(bob.receive(t1, x))
    for bad, why in [(t1, "replay"), (t1[:-1] + bytes([t1[-1] ^ 1]), "tamper")]:
        try: bob.receive(bad, x)
        except ValueError as e: print(why, "->", e)
    print(alice.receive(bob.send(b"hi Alice", x), x))
```

實作要點對照：

| 書中要求 | 程式中的位置 |
|---|---|
| SHAd-256 衍生 4 把金鑰 | `shad256` + `__init__` |
| Bob 交換收發金鑰 | `if role == "Bob"` |
| 計數器溢位檢查 | `assert self.cnt_send < 2**32 - 1` |
| little-endian 32-bit 整數 | `struct.pack("<II", …)` |
| 區塊 = 區塊號 ‖ 訊息號 ‖ 8 個 0 | `keystream` |
| 先驗 MAC、再檢查順序 | `receive` 的兩個 `raise` 順序 |
| 常數時間比較 | `hmac.compare_digest` |
| 失敗時不回傳 m、k | 例外中只帶錯誤名稱 |

> 註：Python 無法真正「抹除」記憶體中的 bytes 物件；書中「destroy k, m」與「wipe S」在 C 中應以不會被編譯器最佳化掉的方式清零（例如 `explicit_bzero`）。

---

## 7. 替代方案：專用的加密 + 認證模式

在嵌入式硬體上實作 SHA-256 相對昂貴，所以出現了**同時提供機密性與真實性**的專用區塊加密模式（今稱 **AEAD**）：

- 只需**一把金鑰**；輸入：訊息、額外認證資料、nonce。
- ⚠️ 不等於「CBC + CBC-MAC 用同一把金鑰」——那樣會出問題。

| 模式 | 設計者 / 特色 | 狀態 |
|---|---|---|
| **OCB** | 非常有效率，每個區塊可平行處理 | **專利**限制了採用 |
| **CCM** | Whiting、Housley、**Ferguson**；CTR + CBC-MAC，經特別設計可共用金鑰；計算量約 OCB 的 2 倍；Jonsson 提供安全證明 | NIST 標準；無專利 |
| **CWC** | Whiting、Viega、**Kohno**；CTR + 通用雜湊，可完全平行 | 避開 OCB 專利 |
| **GCM** | McGrew、Viega 改良 CWC，硬體效率更好的通用雜湊 | NIST 標準 |

- 這些模式都接受兩個字串：要傳送的訊息、要認證的額外資料。**GMAC 就是訊息為空字串的 GCM。**
- 作者偏好**標準化且無專利**的 **CCM 與 GCM**。
- GCM 的認證有 GMAC 的限制（§6.5）→ **只使用完整 128-bit tag**，不要截短。

**重要**：這些模式**本身不是完整的安全通道**——它們只提供加密/認證，仍需要金鑰和每個封包唯一的 nonce（第 4 章說過 nonce 交給外部有多危險）。改造本章的設計很容易：

- 4 把子金鑰 → **2 把**（每個方向一把）；
- nonce = 把訊息編號填充到所需長度。

---

## 8. 設計觀念整理

| 觀念 | 說明 |
|---|---|
| 儲存 = 傳給未來 | 同一套分析適用，但不能互動 |
| 密碼學只認金鑰不認人 | 驗證結果是「知道 K 且扮演 Alice 的人」 |
| 沒有可靠的傳輸 | TCP 只防隨機錯誤，不防攻擊者 |
| 子序列保證 | 無法防刪除，但能保證順序、無重複、可知遺失 |
| 安全模組要小 | 重送、ACK 交給上層 |
| 消滅罕見路徑 | 編號從 1 開始，省掉幾乎不會執行的旗標程式碼 |
| 金鑰分離 | 方向 × 用途 = 4 把子金鑰 |
| 失敗時什麼都不給 | 驗證前不釋出明文或金鑰流 |
| 正確的錯誤訊息 | 先驗 MAC，再判斷順序 |
| 防呆設計 | 定義成雙向，避免有人雙向共用金鑰 |

> 對照第一本書：「從 1 開始編號」與 Hanson 一再強調的**消除特例**、**讓不變量簡單**同出一轍；`ReceiveMessage` 中的 `assert ℓ(t) ≥ 36`，就像 CII 介面中的 checked runtime error——先確立前置條件，之後的切分才「定義良好」。

---

## 9. 延伸閱讀重點

- **Bellare & Namprempre**（2000）、**Krawczyk**（2001）：認證與加密的組合順序理論。
- **Vaudenay 2002、Lucky 13（2013）、POODLE（2014）**：MAC-then-Encrypt + CBC 填充的實際攻擊。
- **RFC 4303（IPsec ESP）**：重放視窗。
- **RFC 5116（AEAD 介面）**、**TLS 1.3（RFC 8446）**：只使用 AEAD，nonce 由序號衍生——與本章設計思路一致。
- **Noise Protocol Framework**、**WireGuard**：現代安全通道的精簡設計。

---

## 10. 習題摘要

| 題號 | 題目 | 提示 / 答案 |
|---|---|---|
| 7.1 | 訊息編號重複會怎樣？ | CTR 金鑰流重用 → C ⊕ C' = P ⊕ P' 洩漏明文；重放偵測失效；接收端無法判斷順序與遺失 |
| 7.2 | 改成 Encrypt-then-Authenticate | 先 CTR 加密 m，MAC 輸入改為 i ‖ ℓ(x) ‖ x ‖ c；接收端先驗 MAC、通過後才解密 |
| 7.3 | 改用 OCB/CCM/CWC/GCM 當黑盒子 | 2 把方向金鑰；nonce = 填充後的 i；AAD = i ‖ ℓ(x) ‖ x；保留計數器檢查與順序檢查 |
| 7.4 | 比較三種順序的優缺點 | 見 §3 |
| 7.5 | 找一個使用安全通道的產品做安全審查 | 依 §1.12 的方法，聚焦通道的安全與隱私 |
| 7.6 | Eve 能從加密通道做哪些流量分析？ | 通訊雙方、時間、頻率、訊息大小；例：從加密 VoIP 封包大小推測語句、從網站流量大小推測瀏覽的頁面 |

---

## 11. 本章重點整理

1. 安全通道 = 機密性（除了大小與時間）+ 真實性（Bob 收到**已知的子序列**）。
2. 每次建立通道都用**新的 256-bit session key**；傳輸層一律視為不可靠。
3. 作者選擇 **Authenticate-then-Encrypt**：保護 MAC、符合 Horton 原則；三種順序都可以做好或做壞。
4. 三個元件：**32-bit 訊息編號（從 1 開始、不可回繞）**、**HMAC-SHA-256(i ‖ ℓ(x) ‖ x ‖ m)**、**AES-CTR（nonce 由通道內部管理）**。
5. 從 K 用 SHAd-256 衍生 4 把子金鑰；通道定義成雙向。
6. 接收：先驗 MAC 再查順序；**驗證失敗時銷毀明文與金鑰流**。
7. AEAD 模式（CCM、GCM）可替代 MAC + 加密，但仍要通道層負責 nonce 與順序。

> **一句話**：安全通道的難處不在挑演算法，而在每一個細節——編號、金鑰分離、檢查順序、失敗時什麼都不給——全都關乎安全。
