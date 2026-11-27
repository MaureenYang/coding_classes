# MC01. 凱撒與替換密碼破解 (Caesar & Substitution Ciphers)

> 主題：替換密碼、頻率分析、卡方統計量　難度：★★　時間限制：1 秒　相關教學：`mc/lessons/01-substitution-ciphers.md`

## 題目

處理 q 個指令，每個指令一行：

| 指令 | 作用 |
|---|---|
| `ENC key text` | 用替換表 `key` 加密 `text` |
| `DEC key text` | 用替換表 `key` 解密 `text` |
| `BREAK text` | `text` 是一段英文用 **凱撒密碼**（每個字母往後位移 k 格，Z 之後接 A）加密的結果；找出 k 並解密 |

- `key` 是 26 個大寫字母的排列：明文字母 `'A' + i` 加密成 `key[i]`。
- `text` 只含大寫字母、空白和標點符號；**非字母的字元保持不變**。`text` 是指令後面一個空白之後的整行（可能含多個空白）。

**怎麼破解凱撒密碼**：對每個 k = 0, 1, …, 25，把密文往回位移 k 格，統計 26 個字母的次數 `cnt[i]`（總共 n 個字母），計算和英文頻率的 **卡方值**

```
χ²(k) = Σ (cnt[i] − n·F[i]/100)² / (n·F[i]/100)     （i = 0..25）
```

卡方值 **最小** 的 k 就是答案。F 是英文字母的頻率（%）：

```
A 8.167  B 1.492  C 2.782  D 4.253  E 12.702 F 2.228  G 2.015  H 6.094  I 6.966
J 0.153  K 0.772  L 4.025  M 2.406  N 6.749  O 7.507  P 1.929  Q 0.095  R 5.987
S 6.327  T 9.056  U 2.758  V 0.978  W 2.360  X 0.150  Y 1.974  Z 0.074
```

（樣板裡已經有這個表。）

## 輸入

第一行是 q，接下來 q 行，每行一個指令。

## 輸出

- `ENC`、`DEC`：輸出結果字串。
- `BREAK`：輸出 `k 明文`。

## 限制

- `1 ≤ q ≤ 100`，每行長度 `≤ 3000`
- `BREAK` 的文字至少有 75 個字母，而且測資保證卡方值最小的 k 唯一、明顯領先第二名（就是正確的位移）

## 範例

輸入
```
3
ENC QWERTYUIOPASDFGHJKLZXCVBNM HELLO, WORLD!
DEC QWERTYUIOPASDFGHJKLZXCVBNM ITSSG, VGKSR!
BREAK WKH ULYHU KDG EHHQ ULVLQJ IRU WKUHH GDBV EHIRUH DQBRQH LQ WKH YLOODJH WKRXJKW WR PRYH WKH JUDLQ.
```
輸出
```
ITSSG, VGKSR!
HELLO, WORLD!
3 THE RIVER HAD BEEN RISING FOR THREE DAYS BEFORE ANYONE IN THE VILLAGE THOUGHT TO MOVE THE GRAIN.
```

## 提示

- 解密替換密碼：先建 **反向表** `inv[key[i] - 'A'] = 'A' + i`，再用加密的程式。
- 往回位移 k：`'A' + (c - 'A' - k + 26) % 26`。
- 讀整行用 `fgets`，記得去掉結尾的 `'\n'`。
