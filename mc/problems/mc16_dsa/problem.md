# MC16. DSA 簽章與驗證 (Digital Signature Algorithm)

> 主題：數位簽章、DSA　難度：★★★　時間限制：1 秒　相關教學：`mc/lessons/25-digital-signatures.md`

## 題目

DSA 的公開參數：質數 p、q，`q | p − 1`，g 模 p 的階是 q。Samantha 的私鑰是 s，公鑰是 `v = gˢ mod p`。處理 n 個指令：

| 指令 | 意思 | 輸出 |
|---|---|---|
| `SIGN s D e` | 用私鑰 s、臨時金鑰 e 簽文件 D | `S1 S2` |
| `VERIFY v D S1 S2` | 用公鑰 v 驗證簽章 | `valid` 或 `invalid` |

**簽章**：

```
S1 = (gᵉ mod p) mod q
S2 = (D + s·S1) · e⁻¹  mod q
```

**驗證**：

```
V1 = D · S2⁻¹  mod q
V2 = S1 · S2⁻¹ mod q
(g^V1 · v^V2 mod p) mod q == S1   →  valid
```

**為什麼成立**：`g^V1 · v^V2 = g^((D + s·S1)·S2⁻¹) = gᵉ`（g 的階是 q，指數可以模 q 計算）。

## 輸入

第一行 `p q g`，第二行 n，接下來 n 行，每行一個指令。

## 限制

- `p < 2⁶²`，p、q 是質數，`q | p − 1`，g 的階是 q
- `1 ≤ n ≤ 2 × 10⁴`
- `1 ≤ s, D, e < q`；測資保證 `SIGN` 得到的 S1、S2 都不是 0，`VERIFY` 的 `1 ≤ S1, S2 < q`

## 範例

輸入
```
48731 443 5260
4
SIGN 242 343 427
VERIFY 3438 343 59 166
VERIFY 3438 344 59 166
VERIFY 3438 343 59 165
```
輸出
```
59 166
valid
invalid
invalid
```

課本例 7.7：私鑰 s = 242、公鑰 v = 3438，用 e = 427 簽 D = 343 得到 (59, 166)。驗證時 `V1 = 357`、`V2 = 414`，`5260³⁵⁷ · 3438⁴¹⁴ ≡ 2717 (mod 48731)`，`2717 mod 443 = 59`。文件或簽章改一點就驗不過。

## 提示

- q 是質數，反元素用費馬：`x⁻¹ ≡ x^(q−2) (mod q)`。
- 注意兩種模數：指數相關的運算 mod q，冪次 mod p，最後再 mod q。
- 乘法用 `unsigned __int128`。
