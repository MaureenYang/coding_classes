# C12. 成績單解析 (String Parsing & I/O)

> 主題：`getline`、`stringstream`、字串處理、格式化輸出　難度：★★☆　時間限制：1 秒　相關教學：`cpp/lessons/12_strings_io.md`

## 題目

讀入一份用逗號分隔的成績單（CSV），每一行是：

```
姓名, 分數1, 分數2, ...
```

規則：

- 每個欄位前後 **可能有空白**，要去掉（trim）；欄位中間的空白要保留（姓名 `Mary Ann` 是合法的）。
- **空的分數欄位**（例如 `amy, 90, , 80` 或結尾多一個逗號 `amy, 90,`）代表缺考，**跳過不算**。
- 一行可能 **只有姓名**，沒有任何分數。

對每一行輸出：

```
姓名: 平均分數（兩位小數）
```

沒有任何分數時輸出 `姓名: no scores`。

最後輸出全班 **所有分數** 的平均（不是每個人平均的平均）：`class average: X`；全班都沒有分數時輸出 `class average: no scores`。

## 輸入

第一行整數 `N`，接下來 `N` 行成績資料。

## 限制

- `1 ≤ N ≤ 10^4`，每行最多 100 個分數
- 分數是 `0 ~ 100` 的整數；姓名不為空，由英文字母和空白組成

## 範例

輸入
```
4
amy, 90, 80
  Mary Ann ,100,  , 95
bob
cat, 70,
```
輸出
```
amy: 85.00
Mary Ann: 97.50
bob: no scores
cat: 70.00
class average: 86.25
```

## 提示

- **`cin >>` 和 `getline` 混用的陷阱**：`cin >> N` 讀完數字後，換行字元還留在輸入裡，
  接著第一次 `getline` 會讀到一個 **空字串**。要先 `getline(cin, dummy)` 或 `cin.ignore()` 把它吃掉。
- 用 `getline(ss, field, ',')` 可以用逗號切欄位（`ss` 是 `stringstream`）。
- 注意：`"cat, 70,"` 用 `getline(ss, field, ',')` 切的時候，**最後那個空欄位不會被讀到**；而 `", , "` 中間的空欄位會讀到空字串 —— 兩種都要正確處理成「跳過」。
- trim 可以用 `find_first_not_of(' ')` 和 `find_last_not_of(' ')`。
- 輸出兩位小數：`cout << fixed << setprecision(2) << x;`（`<iomanip>`）。
