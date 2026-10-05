# C13. 安全的計算機 (Exceptions)

> 主題：例外處理、自訂例外類別、強例外保證　難度：★★★　時間限制：1 秒　相關教學：`cpp/lessons/13_exceptions.md`

## 題目

實作一個 **逆波蘭表示法（RPN）** 計算機：數字放在堆疊上，運算子從堆疊拿出兩個數 `a`（下面）、`b`（上面），把 `a op b` 放回去。

| 指令 | 說明 |
|---|---|
| `push x` | 把 `x` 放上堆疊 |
| `add` `sub` `mul` `div` `mod` | 取出 `b`、`a`，放回 `a+b`、`a-b`、`a*b`、`a/b`、`a%b` |
| `dup` | 複製頂端元素 |
| `pop` | 移除頂端元素 |
| `top` | 輸出頂端元素 |
| `size` | 輸出元素個數 |

所有數字是 `long long`，`/` 和 `%` 照 C++ 規則（向 0 取整，`%` 正負號跟 `a` 一樣）。

**錯誤處理**：發生錯誤時要 **丟出例外**，由 `main` 捕捉並輸出 `error: 訊息`，而且 **堆疊必須完全不變**（強例外保證 strong exception guarantee）。

| 錯誤 | 訊息 |
|---|---|
| 堆疊裡的元素不夠（運算需要 2 個；`dup` `pop` `top` 需要 1 個） | `stack underflow` |
| `div` 或 `mod` 的 `b` 是 0 | `division by zero` |
| 運算結果超出 `long long` 範圍 | `overflow` |

最後輸出一行 `errors: 錯誤總數`。

## 輸入

第一行 `Q`，接下來 `Q` 行指令。

## 限制

- `1 ≤ Q ≤ 2×10^5`
- `push` 的數字在 `long long` 範圍內（包含 `-9223372036854775808`）

## 範例

輸入
```
8
push 7
add
push 0
div
size
push 9223372036854775807
push 1
add
```
輸出
```
error: stack underflow
error: division by zero
2
error: overflow
errors: 3
```

## 陷阱提示

- **有號整數溢位是未定義行為**，不能「先算再檢查」。要在計算 **之前** 判斷，或用 GCC 的 `__builtin_add_overflow(a, b, &result)`（`sub`、`mul` 也有）。
- `LLONG_MIN / -1` 會溢位（結果是 `2^63`）。
- `LLONG_MIN % -1` 在數學上是 `0`，**不算溢位**，但在 x86 電腦上直接計算會讓程式 **當掉（SIGFPE）**。`b == -1` 時餘數一定是 0。
- 強例外保證：先 **檢查** 所有會出錯的條件（或先算出結果），確定沒問題之後才修改堆疊。不要先 pop 再發現出錯。
- 自訂例外類別可以繼承 `std::runtime_error`，`what()` 回傳訊息。
