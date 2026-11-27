# MC05. Diffie–Hellman 與 ElGamal (Diffie–Hellman & ElGamal)

> 主題：Diffie–Hellman 金鑰交換、ElGamal 公鑰加密　難度：★★　時間限制：1 秒　相關教學：`mc/lessons/06-dlp-diffie-hellman-elgamal.md`

## 題目

公開參數是質數 p 和 g。處理 q 個指令：

| 指令 | 意思 | 輸出 |
|---|---|---|
| `DH a b` | Alice 的秘密 a、Bob 的秘密 b | `A B K`：`A = gᵃ`、`B = gᵇ`、共同金鑰 `K = Bᵃ = Aᵇ`（都 mod p） |
| `ENC A k m` | 用 Alice 的公鑰 A、臨時金鑰 k 加密明文 m | `c1 c2`：`c1 = gᵏ`、`c2 = m·Aᵏ` |
| `DEC a c1 c2` | Alice 用私鑰 a 解密 | 明文 `m = c2 · (c1ᵃ)⁻¹` |

## 輸入

第一行 `p g`，第二行 q，接下來 q 行，每行一個指令。

## 限制

- `11 ≤ p < 2⁶²`，p 是質數；`2 ≤ g ≤ p − 2`
- `1 ≤ q ≤ 3 × 10⁴`
- `1 ≤ a, b, k ≤ p − 2`；`1 ≤ A, m, c1, c2 ≤ p − 1`

## 範例 1

輸入
```
941 627
1
DH 347 781
```
輸出
```
390 691 470
```

（課本例 2.7 的 Diffie–Hellman。）

## 範例 2

輸入
```
467 2
3
DH 153 197
ENC 224 197 331
DEC 153 87 57
```
輸出
```
224 87 367
87 57
331
```

課本例 2.8：Alice 的私鑰 a = 153，公鑰 `A = 2¹⁵³ ≡ 224`；Bob 用 k = 197 加密 m = 331 得到 (87, 57)；Alice 算 `87¹⁵³ ≡ 367`，`367⁻¹ ≡ 14`，`57 · 14 ≡ 331`。

## 提示

- 反元素用費馬小定理：p 是質數，`x⁻¹ ≡ x^(p−2) (mod p)`。
- p 接近 2⁶²，乘法要用 `unsigned __int128`。
