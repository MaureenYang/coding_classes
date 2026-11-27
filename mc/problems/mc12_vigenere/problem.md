# MC12. 破解 Vigenère 密碼 (Breaking the Vigenère Cipher)

> 主題：Vigenère 密碼、重合指數、卡方統計量　難度：★★★　時間限制：1 秒　相關教學：`mc/lessons/15-counting-vigenere.md`

## 題目

Vigenère 密碼用一個金鑰字串 `k₀k₁…k_{L−1}` 加密：第 i 個字母往後位移 `k_{i mod L}` 格（A = 0、B = 1、…）。給一段英文的密文（只有大寫字母），找出金鑰並解密。

請 **照下面的方法** 做（測資保證這個方法會得到正確的金鑰）：

**第一步：找金鑰長度。** 對 L = 1, 2, …, 15：把密文分成 L 行（第 i 個字母放在第 `i mod L` 行），算出每一行的 **重合指數**

```
IndCo = Σ cnt[i]·(cnt[i] − 1) / (m·(m − 1))     （m 是這一行的字母數）
```

取 L 行的平均。**第一個平均 ≥ 0.060 的 L** 就是金鑰長度。

（英文的重合指數約 0.066，隨機字母約 1/26 ≈ 0.038。L 猜對時每一行都是單純的凱撒密碼，重合指數和英文一樣高。）

**第二步：找每個金鑰字母。** 每一行都是凱撒密碼：用 MC01 的 **卡方值** 找出位移 s（0..25，卡方值最小者），金鑰字母就是 `'A' + s`。英文頻率表和 MC01 相同（樣板裡已經有）。

## 輸入

第一行是 T，接下來 T 行，每行一段密文。

## 輸出

每筆輸出兩行：金鑰、明文。

## 限制

- `1 ≤ T ≤ 10`
- 金鑰長度 `1 ≤ L ≤ 15`，密文長度 `60·L ≤ n ≤ 4000`

## 範例

輸入
```
1
VYCGBJGIFPWPGVLGBGKEEUHFVYPTXRCPQQXTQICPGMQECXGHJVTXEZCXCIACWXFIMCOFTTMVGXPPBBDPRWXBVYCAHKGIDXXZFJUTKSCCPTTRALLSXFYRRTKOPURWXCNUKXEZIIMPGSFVTTKMVZKTMVGTSGKSPKQIKIEBGILKJVCAFOTKFPPONBCSTZQEEIASDRLZXOEYKDKBKEELBHJRJDGUUKGRDDWJFXGUKKGCMCVYCBNRVFQTXVQNQDYHVYCVKCWEBWTRDVADFSUYCLTGPFRIASQCBTLHRVPHHBKERWXJ
```
輸出
```
CRYPTO
THERIVERHADBEENRISINGFORTHREEDAYSBEFOREANYONEINTHEVILLAGETHOUGHTTOMOVETHEGRAINBYTHENTHELOWERFIELDSWEREALREADYUNDERWATERANDTHEOLDMILLGROANEDEVERYTIMETHECURRENTSTRUCKITSWHEELMARTHAWALKEDALONGTHEBANKEACHMORNINGWITHALONGSTICKPUSHINGITINTOTHEMUDTOSEEHOWSOFTTHEGROUNDHADBECOMESHEWASNOTTHEOLDESTPERSONINTHEV
```

## 提示

- L 的倍數也會有很高的重合指數（例如金鑰長度 6 時，L = 12 也很高），所以要找 **第一個** 超過門檻的 L。
- 解密：`'A' + (c − key[i % L] + 26) % 26`。
