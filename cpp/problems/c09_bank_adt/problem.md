# C09. 銀行帳戶系統 (ADT + 繼承)

> 主題：抽象資料型別、介面、不變量、繼承　難度：★★★　時間限制：1 秒　相關教學：`cpp/lessons/09_adt_design.md`

## 題目

設計一個抽象類別 `Account`（帳戶的 **介面**），以及兩種實作：

| 類別 | 提款規則（不變量） | 月底結算 `monthEnd()` |
|---|---|---|
| `SavingsAccount`（儲蓄帳戶，利率 `rate`%） | 餘額 **不能小於 0** | 加上利息 `balance * rate / 100`（整數除法，無條件捨去） |
| `CheckingAccount`（支票帳戶，透支額度 `limit`） | 餘額 **不能小於 `-limit`** | 若餘額 `< 0`，扣手續費 `10`（扣完可以低於 `-limit`） |

銀行用帳號（字串）管理所有帳戶，處理以下指令：

| 指令 | 成功輸出 |
|---|---|
| `open savings ID RATE` | `ok` |
| `open checking ID LIMIT` | `ok` |
| `deposit ID AMT` | `ok` |
| `withdraw ID AMT` | `ok` |
| `transfer FROM TO AMT` | `ok` |
| `month` | `ok`（所有帳戶依 **帳號字典序** 做月底結算） |
| `balance ID` | 餘額 |
| `report` | 每個帳戶一行 `ID TYPE BALANCE`（依帳號字典序，`TYPE` 是 `savings` 或 `checking`）；沒有帳戶輸出 `no accounts` |

失敗時輸出錯誤訊息，**狀態完全不變**。檢查順序（同時有好幾個錯誤時，輸出最前面的那一個）：

1. `open` 的帳號已存在 → `error: duplicate id`
2. 帳號不存在（`transfer` 兩個帳號都要檢查，先檢查 `FROM`）→ `error: no such account`
3. 金額 `AMT ≤ 0` → `error: invalid amount`
4. `transfer` 的 `FROM` 和 `TO` 相同 → `error: same account`
5. 提款後會違反不變量 → `error: insufficient funds`

`transfer` 必須是 **原子操作 (atomic)**：要嘛完整成功，要嘛完全沒發生。

## 輸入

第一行 `Q`，接下來 `Q` 行指令。帳號是長度 `1 ~ 8` 的英數字串。

## 限制

- `1 ≤ Q ≤ 10^5`
- `0 ≤ RATE ≤ 20`，`0 ≤ LIMIT ≤ 10^9`，`|AMT| ≤ 10^9`
- 保證所有餘額的絕對值永遠 `≤ 10^15`（用 `long long`）

## 範例

輸入
```
9
open savings amy 10
open checking bob 100
deposit amy 50
transfer amy bob 80
transfer bob amy 90
withdraw bob 20
month
report
balance cat
```
輸出
```
ok
ok
ok
error: insufficient funds
ok
error: insufficient funds
ok
amy savings 154
bob checking -100
error: no such account
```

（`bob` 轉出 90 後是 `-90`，再提 20 會變 `-110 < -100`，失敗。月底 `amy` 140 + 14 = 154；`bob` 是負的，扣 10 變 `-100`。）

## 提示

- `Account` 只定義 **能做什麼**（純虛擬函式），`main` 和 `Bank` 只透過 `Account&` / `Account*` 使用帳戶，**不需要知道** 是哪一種 —— 這就是 ADT 和多型的威力。
- 「能不能提款」的規則不同，可以設計一個虛擬函式 `bool canWithdraw(long long amt) const`。
- `transfer` 先檢查 **所有** 條件，全部通過才真的修改；不要先提款再發現存不進去。
- `map<string, unique_ptr<Account>>` 會自動依帳號排序。
