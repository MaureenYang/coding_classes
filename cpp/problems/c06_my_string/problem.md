# C06. 自己做一個字串類別 (Rule of Five)

> 主題：RAII、複製 / 移動語意、五法則　難度：★★★　時間限制：1 秒　相關教學：`cpp/lessons/06_memory_raii.md`

## 題目

請 **不要使用 `std::string`**，用 `char*` 自己實作 `MyString`，必須正確處理：

| 成員 | 說明 |
|---|---|
| 建構子 `MyString(const char*)` | 複製一份字元陣列 |
| 解構子 | 釋放記憶體 |
| 複製建構子 / 複製指定 `=` | **深複製** |
| 移動建構子 / 移動指定 `=` | **偷走** 對方的記憶體，對方變成空字串 |
| `operator+=` | 接在後面 |

**所有的記憶體配置和釋放都要透過樣板提供的 `alloc_chars` / `free_chars`**，
程式結束時會檢查配置次數和釋放次數是否相同（有沒有記憶體洩漏）。

樣板的 `main` 已經寫好，有 `K` 個字串 `s[0] ~ s[K-1]`（一開始都是空字串），處理以下指令：

| 指令 | 對應的程式碼 | 輸出 |
|---|---|---|
| `set i w` | `s[i] = MyString(w)` | — |
| `copy i j` | `s[i] = s[j]` | — |
| `move i j` | `s[i] = std::move(s[j])` | — |
| `append i j` | `s[i] += s[j]` | — |
| `swap i j` | `std::swap(s[i], s[j])` | — |
| `print i` | | 內容；空字串輸出 `(empty)` |
| `len i` | | 長度 |

最後輸出 `leak check: ok`（或洩漏的訊息）。

## 規格細節（corner case）

- `move i j` 之後，`s[j]` 必須是 **空字串**（長度 0）。
- **自我指定**：`copy i i`、`move i i` 之後 `s[i]` **不變**。
- **自我附加**：`append i i` 之後，`s[i]` 變成自己重複兩次（`"ab"` → `"abab"`）。

## 輸入

第一行 `K Q`，接下來 `Q` 行指令。`w` 是長度 `1 ~ 20` 的小寫英文字串。

## 輸出

依照上表，最後一行是記憶體檢查結果。

## 限制

- `1 ≤ K ≤ 10`，`1 ≤ Q ≤ 2×10^5`，任何時刻每個字串長度 `≤ 10^4`

## 範例

輸入
```
3 8
set 0 hello
copy 1 0
append 1 1
print 1
move 2 0
print 0
len 2
print 2
```
輸出
```
hellohello
(empty)
5
hello
leak check: ok
```

## 提示

- **自我指定**：`copy i i` 時如果先 `free_chars(data)` 再從 `other.data` 複製 —— `other` 就是自己，資料已經被釋放了！
  常見解法：先檢查 `if (this == &other)`，或用 **copy-and-swap**。
- **自我附加**：`s += s` 時，如果先配置新空間、釋放舊空間，再從 `other` 複製 …… `other` 的資料也是舊空間。要先把 `other` 的資料複製完，再釋放舊的。
- 移動之後要把對方的指標設成 `nullptr`、長度設成 0，否則兩邊解構時會釋放同一塊記憶體（double free）。
- `std::swap` 會用到移動建構子和移動指定，兩個都要寫對。
- 寫完用 `--debug` 跑一次，sanitizer 會抓到 use-after-free 和 double free。
