# 第 18 章　PKI 的理想（The Dream of PKI）

> 《Cryptography Engineering》— Ferguson, Schneier, Kohno，本章頁碼：p.275–280

---

## 1. 本章定位

上一章的金鑰伺服器只適合小系統。對大系統，業界的標準答案是 **PKI（Public-Key Infrastructure，公鑰基礎建設）**——一個讓你**辨認哪把公鑰屬於誰**的基礎設施。

本章與接下來兩章是一組：

| 章 | 主題 |
|---|---|
| **ch18 PKI 的理想**（本章） | 標準說法：PKI 如何解決金鑰管理問題——一個**完美世界** |
| ch19 PKI 的現實 | 實務上的挑戰 |
| ch20 PKI 實務 | 作者建議的做法 |

> 為什麼要先談「夢想」？因為 **PKI 是業界大多數人對金鑰管理的第一句話也是最後一句話**。人們在這個夢想中長大，把它視為理所當然、不需要說明。要理解他們，就必須理解 PKI 的夢想——他們說的很多話都是在這個夢想的脈絡中說的。

---

## 2. PKI 極簡概觀 ⭐⭐

```
                     ┌──────────────────────────────┐
                     │  CA（憑證機構）                │
                     │  公開金鑰 PK_CA 人人皆知        │
                     └──────┬──────────────┬────────┘
            ①「我是 Alice，    │              │  ① 同樣程序
              PKA 是我的公鑰」  │              │
            ② 驗證身分後簽發   ▼              ▼
              Cert_A = Sign_CA(「PKA 屬於 Alice」)    Cert_B
                   Alice ◄──── ③ 交換 (PK, Cert) ────► Bob
                         ④ 用 PK_CA 驗證對方憑證
                         ⑤ 用彼此公鑰跑金鑰協商（ch14）→ session key
```

1. **CA** 有一對公私鑰（例如 RSA），公開其公鑰。假設人人都知道 CA 的公鑰——它長期不變，所以容易做到。
2. Alice 產生自己的金鑰對，私鑰保密，帶著公鑰 PKA 去找 CA：「嗨，我是 Alice，PKA 是我的公鑰。」
3. CA 驗證 Alice 確實是她所說的人，然後簽一份數位聲明：「金鑰 PKA 屬於 Alice。」——這份簽章聲明就是**憑證（certificate）**。
4. Alice 要和 Bob 通訊時，把公鑰和憑證送給他。Bob 有 CA 的公鑰，可以驗證憑證上的簽章——**只要 Bob 信任 CA**，他也就信任 PKA 確實屬於 Alice。
5. Bob 也照同樣程序取得憑證並送給 Alice。雙方知道彼此的公鑰後，用它們跑**金鑰協商協定**建立 session key。

**需要的只有**：一個**人人都信任的中央 CA**；每個參與者都讓自己的公鑰被認證，並知道 CA 的公鑰。之後，**每個人都能和每個人安全通訊**。

> 聽起來夠簡單了。

> 對照第 17 章：金鑰伺服器要**永遠在線**、**知道所有金鑰**；CA 只在**簽發**時需要，而且**不知道任何人的私鑰**——這是 PKI 能擴展到大系統的根本原因。

---

## 3. PKI 的例子

| 例子 | CA | 目的 |
|---|---|---|
| **通用 PKI**（終極夢想） | 例如郵局這種大型組織，認證**所有人**的公鑰 | 每人只需認證一把金鑰，所有應用通用；人人都信任郵局，於是人人都能安全通訊，從此過著幸福快樂的日子 |
| **VPN 存取** | 公司 IT 部門 | 員工從家裡或旅館連入公司網路；VPN 存取點要辨認誰有權存取、權限多大 |
| **網路銀行** | 銀行自己 | 正確辨識客戶至關重要，還要能產生**法庭可接受的證據** |
| **煉油廠感測器** | 公司 | 數英里的管線與道路間分佈數百個溫度、流量、壓力感測器。偽造感測器資料是非常嚴重的攻擊——可能誘使操作員採取導致**大爆炸**的行動。標準認證技術能確保資料未被竄改，但要確定資料**真的來自那個感測器**，需要某種金鑰基礎設施 |
| **信用卡組織** | 信用卡組織 | 全球數千家銀行的合作事業：A 銀行的持卡人要能付款給在 B 銀行開戶的商家，A、B 銀行之間要安全結算 |

> 通用 PKI 聽起來像童話——**因為它就是童話。通用 PKI 不存在，也永遠不會存在。**（下一章說明為什麼。）

---

## 4. 更多細節

### 4.1 多層憑證（憑證鏈）⭐

在許多情況下 CA 會被拆成多個部分。例如信用卡總部不會直接認證每家銀行，而是由**區域辦公室**處理：

```
中央 CA ──簽──►「金鑰 PKX 屬於區域辦公室 X，且允許認證其他金鑰」   （委派訊息）
                         │
            區域辦公室 X ──簽──►「金鑰 PK_bank 屬於某銀行」          （認證訊息）

銀行的憑證 = [ 中央 CA 的委派訊息 , 區域辦公室的認證 ]
          = 憑證鏈（certificate chain），可延伸到任意層數
```

| 優點 | 缺點 |
|---|---|
| 把 CA 功能拆成階層，符合大多數組織的結構 | 憑證變大，驗證需要更多計算（多數情況下成本不大） |
| 幾乎所有 PKI 都是多層結構 | **每多一個 CA，就多一個攻擊點**，降低整體安全性 |

**作者的點子：摺疊階層**（未見於實務）——銀行取得兩層憑證後送回中央 CA，中央 CA 驗證後用主金鑰簽發一張**單層**憑證。階層摺疊後，增加層數的效能成本就變得很小。但話說回來，**多層的階層結構很少是有效的**，增加層數未必是好主意。

**憑證鏈的危險：一個小 bug 摧毀整個系統** ⭐⭐

```
每張憑證有一個旗標：它認證的金鑰「是不是 CA 金鑰」
    CA 金鑰：允許認證其他金鑰
    非 CA 金鑰：不允許

某個所有 Microsoft 作業系統都使用的憑證驗證函式庫——沒有檢查這個旗標。

攻擊：
  1. 合法購買 nastyattacker.com 的憑證（非 CA）
  2. 用它簽一張 amazon.com 的假憑證
  3. Internet Explorer 接受這條鏈，把假網站顯示為真正的 Amazon
```

> 一個耗費鉅資建立的全球安全系統，被**單一函式庫中的一個簡單小 bug** 完全繞過。bug 公開後發布了修補（**試了好幾次**才修好所有問題）——這仍是「小 bug 摧毀整個系統安全」的好例子。（而且現實中，大多數使用者本來就不檢查網站名稱，這個系統在實務上本來就不太安全。）

> 歷史註：這是 2002 年 Moxie Marlinspike 公開的 **basicConstraints** 漏洞；同類問題後來在 2014 年的 iOS/OS X **goto fail**、GnuTLS 的憑證驗證錯誤中一再出現——**憑證驗證程式碼是整個 PKI 中最脆弱的一環**。

### 4.2 到期 ⭐

- **沒有任何密碼金鑰應該被無限期使用**——總有外洩的風險。定期更換金鑰讓你能從外洩中恢復（雖然很慢）。
- 憑證也不應永遠有效：CA 的金鑰和被認證的公鑰都會到期。
- 除了密碼學理由，到期也有助於**保持資訊最新**：憑證到期就要重新簽發，這是更新憑證資訊的機會。
- 典型的到期間隔：**數個月到數年**。
- 幾乎所有憑證系統都包含到期日期時間，過了就沒人應該接受 → **這就是 PKI 參與者需要時鐘的原因**（第 16 章的雞與蛋問題）。

**其他欄位**：生效起始時間（not-valid-before）、憑證類別、序號、簽發日期時間……有些有用，有些沒用。

**X.509 v3**：最常用的憑證格式，**過於複雜**（參見 Peter Gutmann 的 *X.509 Style Guide*）。

> 若你的系統**不需要**與其他系統互通，可以認真考慮**完全不用 X.509**。當然，X.509 是標準，用標準也很難被挑毛病。

### 4.3 獨立的註冊機構（RA）⭐

**問題是政治性的**：公司裡決定「誰是員工」的是**人資部門**；但 CA 必須由 **IT 部門**營運——那是技術工作，IT 不會讓人資做。

| 方案 | 說明 | 評價 |
|---|---|---|
| **多層憑證：人資當子 CA** | 讓人資部門成為自己的 sub-CA | ✅ 好——自動提供支援多據點的彈性 |
| **多層 + 換發單層** | 同上，但使用者拿到兩層憑證後到中央 CA 換成單層憑證 | ✅ 好——省去每次檢查兩層憑證的開銷，代價只是加一個簡單的兩則訊息協定 |
| **在密碼協定中加入第三方 RA** | 規格書談 CA 與另一個叫 RA（Registration Authority）的角色，兩者被視為完全不同的實體 | ❌ **很糟** |

**為什麼 RA 方案很糟？**

- 光是把 CA 和 RA 當成不同實體，就能讓系統文件**多出 100 頁以上**——這本身就很糟。
- 還要規範 RA–CA 的互動；作者甚至看過 RA 授權 CA 簽發憑證的**三方協定**。

> 這是「**把使用者需求直接強加在技術方案上**」的好例子。使用者需求只規定系統的**外部行為**：公司需要人資和 IT 有不同的功能——但這**不代表**軟體要為人資和 IT 寫不同的程式碼。在許多情況下（包括這個），兩個部門可以使用大部分相同的功能、相同的程式碼。
>
> 使用同一套憑證函式的設計，比直接依原始需求（同時包含 CA 與 RA）設計的方案**更簡單、更便宜、更強大、更有彈性**。兩層 CA 方案讓人資與 IT 共用大部分程式碼與協定，差異主要在**使用者介面**——大概只多幾百行程式碼，而不是多出數百頁規格、最後變成數萬行程式碼。

> 對照第 8 章：「功能規格只描述外部可量測的行為；實作設計才描述內部怎麼做。」RA 方案的錯誤正是把**需求層**的組織劃分，直接搬進了**實作層**。對照第一本書：Hanson 一再強調「用少數通用的介面組合出各種功能」——兩層 CA 就是用同一個「憑證」介面同時滿足人資與 IT。

---

## 5. 參考實作（Python 玩具）

一個極簡的憑證鏈驗證器（Ed25519 簽章、JSON 編碼），重現 §4.1 的漏洞：**不檢查 CA 旗標**的驗證器會接受 nastyattacker 替 amazon 簽發的假憑證；正確的驗證器則會拒絕。

```python
import json, time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.exceptions import InvalidSignature

def raw(pk): return pk.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()

def issue(issuer_name, issuer_sk, subject, subject_pk, is_ca, days=365):
    body = dict(issuer=issuer_name, subject=subject, key=raw(subject_pk),
                ca=is_ca, not_before=int(time.time()), not_after=int(time.time()) + days * 86400)
    msg = json.dumps(body, sort_keys=True).encode()      # 可唯一解析的編碼
    return dict(body=body, sig=issuer_sk.sign(msg).hex())

def verify_chain(chain, root_name, root_pk, name, check_ca_flag=True, now=None):
    now = now or time.time()
    issuer_name, issuer_pk = root_name, root_pk
    for i, cert in enumerate(chain):
        b = cert["body"]
        assert b["issuer"] == issuer_name, "issuer mismatch"
        try:
            issuer_pk.verify(bytes.fromhex(cert["sig"]), json.dumps(b, sort_keys=True).encode())
        except InvalidSignature:
            raise AssertionError("bad signature")
        assert b["not_before"] <= now <= b["not_after"], "expired / not yet valid"
        last = (i == len(chain) - 1)
        if not last and check_ca_flag:
            assert b["ca"], f"{b['subject']} is not a CA but signed another cert!"   # ← 關鍵檢查
        issuer_name, issuer_pk = b["subject"], Ed25519PublicKey.from_public_bytes(bytes.fromhex(b["key"]))
    assert issuer_name == name, "name mismatch"
    return issuer_pk

if __name__ == "__main__":
    root_sk = Ed25519PrivateKey.generate(); root_pk = root_sk.public_key()
    reg_sk = Ed25519PrivateKey.generate()
    shop_sk = Ed25519PrivateKey.generate()
    evil_sk = Ed25519PrivateKey.generate(); fake_sk = Ed25519PrivateKey.generate()

    reg = issue("Root", root_sk, "Regional-X", reg_sk.public_key(), is_ca=True)      # 委派
    shop = issue("Regional-X", reg_sk, "shop.example", shop_sk.public_key(), is_ca=False)
    print("legit chain ok:", verify_chain([reg, shop], "Root", root_pk, "shop.example") is not None)

    # 攻擊者合法買到一張「非 CA」憑證，再用它替 amazon.example 簽發假憑證
    evil = issue("Regional-X", reg_sk, "nastyattacker.example", evil_sk.public_key(), is_ca=False)
    fake = issue("nastyattacker.example", evil_sk, "amazon.example", fake_sk.public_key(), is_ca=False)
    print("buggy validator accepts fake amazon:",
          verify_chain([reg, evil, fake], "Root", root_pk, "amazon.example", check_ca_flag=False) is not None)
    try:
        verify_chain([reg, evil, fake], "Root", root_pk, "amazon.example")
    except AssertionError as e:
        print("correct validator:", e)
```

實測輸出：

```
legit chain ok: True
buggy validator accepts fake amazon: True
correct validator: nastyattacker.example is not a CA but signed another cert!
```

> 真實的 X.509 驗證還要檢查：路徑長度限制（pathLenConstraint）、名稱限制（nameConstraints）、金鑰用途（keyUsage / extendedKeyUsage）、撤銷狀態（下一章）、簽章演算法……每一項都是一個可能被漏掉的旗標。

---

## 6. 設計觀念整理

| 觀念 | 說明 |
|---|---|
| PKI = 公鑰 ↔ 身分的對應 | CA 簽發「PK 屬於某人」的憑證 |
| CA 不需在線、不知私鑰 | 比金鑰伺服器更能擴展 |
| 信任 CA → 信任憑證 | 整個系統的信任根基 |
| 通用 PKI 是童話 | 不存在、也不會存在 |
| 憑證鏈 | 符合組織階層，但每個 CA 都是攻擊點 |
| 一個旗標毀掉全局 | CA 旗標未檢查 → 任何人都能簽任何網站 |
| 到期 | 限制外洩損害、更新資訊；需要時鐘 |
| X.509 過度複雜 | 不需互通就考慮別用 |
| 需求 ≠ 實作 | 人資/IT 分工用兩層 CA，不要發明 RA 協定 |

---

## 7. 延伸閱讀重點

- **Kohnfelder**（1978，MIT 學士論文）：首次提出「憑證」的概念。
- **RFC 5280**：X.509 v3 憑證與 CRL 的 Internet profile。
- **Peter Gutmann**：*X.509 Style Guide*；*Everything you Never Wanted to Know about PKI but were Forced to Find Out*。
- **Ellison & Schneier**（2000）：*Ten Risks of PKI: What You're not Being Told about Public Key Infrastructure*。
- **Moxie Marlinspike**（2002）：IE basicConstraints 漏洞；（2009）：*Null Prefix Attacks Against SSL/TLS Certificates*。
- **Georgiev et al.**（2012）：*The Most Dangerous Code in the World: Validating SSL Certificates in Non-Browser Software*。

---

## 8. 習題摘要

| 題號 | 題目 | 提示 |
|---|---|---|
| 18.1 | 若 CA 是惡意的，它能做哪些壞事？ | 替任何人簽發假憑證 → **中間人攻擊**任何使用者（CA 不知道私鑰，但不需要——它直接簽一把自己的公鑰說是 Alice 的）；拒絕簽發/撤銷合法使用者（DoS、審查）；記錄誰申請了憑證（隱私）；為政府或犯罪者簽發監聽用憑證（如 2011 年 DigiNotar 事件）。注意：CA **無法**解密使用者用自己私鑰保護的舊資料 |
| 18.2 | 假設通用 PKI 存在，跨多個應用使用同一個 PKI 會有安全問題嗎？ | **同一把金鑰用於多個用途**（違反「一個秘密只用於一件事」）：某應用的漏洞或簽章 oracle 可能被用來攻擊另一個應用（如 ch14 的智慧卡兩協定干擾）；一次外洩影響所有應用；不同應用需要不同的身分語意、信任程度與撤銷速度；隱私——所有應用可藉同一把金鑰關聯你的行為 |
| 18.3 | 哪些政策或組織上的挑戰會阻礙全球通用 PKI？ | 沒有全世界都信任的單一機構（國家間不互信、政府監控疑慮）；不同國家的法律、責任歸屬與身分證明制度；誰付錢、誰承擔錯誤簽發的責任；商業競爭；身分本身的定義（同名同姓、改名）——第 19 章詳述 |
| 18.4 | 除了書中例子，再舉三個 PKI 可行的情境 | 例：**程式碼簽章**（作業系統廠商當 CA，驗證軟體更新來源）；**物聯網裝置**（製造商在出廠時為每台裝置簽發憑證，如煉油廠感測器的延伸）；**企業內部 mTLS**（服務間互相認證，CA 由平台團隊營運）；**電子護照**（各國政府當 CA 簽署晶片資料） |

---

## 9. 本章重點整理

1. **PKI** 讓你辨認公鑰屬於誰：CA 驗證身分後簽發「PK 屬於某人」的**憑證**；只要信任 CA，就能信任憑證。
2. 雙方交換公鑰與憑證，驗證後用公鑰跑金鑰協商。
3. 例子：VPN（IT 部門當 CA）、網路銀行、煉油廠感測器、信用卡組織；**通用 PKI 是童話**。
4. **多層憑證/憑證鏈**符合組織階層，但每個 CA 都是攻擊點；**一個未檢查的 CA 旗標**就讓 IE 接受任何人簽的假 Amazon 憑證。
5. 憑證要**到期**（數月到數年），因此 PKI 需要時鐘；X.509 過度複雜。
6. 人資/IT 分工用**兩層 CA**（人資當子 CA），不要發明獨立 RA 的三方協定——需求只規定外部行為，不該直接變成實作結構。
7. PKI 是業界對金鑰管理的「標準夢想」——要理解它，才能理解業界的對話；下一章看夢想與現實的落差。

> **一句話**：PKI 的夢想是「信任一個 CA，就能信任全世界的公鑰」——這個夢很美、很重要，也必須先懂；但下一章會告訴你它在現實中有多少裂縫。
