# C11. 單字頻率統計 (STL Containers & Algorithms)

> 主題：`map` / `unordered_map`、`sort`、`transform`、lambda　難度：★★☆　時間限制：1 秒　相關教學：`cpp/lessons/11_stl.md`

## 題目

讀入一段文字，統計每個單字出現的次數。

- **單字** 的定義：連續的英文字母 `A-Z a-z`。其他所有字元（數字、標點、空白、`'`、`-`）都是分隔符號。
  例如 `don't` 是兩個單字 `don` 和 `t`；`abc123def` 是 `abc` 和 `def`。
- **不分大小寫**：一律轉成小寫再統計。

輸出：

```
total: 單字總數
distinct: 不同單字的數量
接下來最多 K 行：word count
```

排序規則：**次數多的在前**；次數相同時 **字典序小的在前**。`K` 大於不同單字數量時，全部輸出。

## 輸入

第一行整數 `K`。接下來直到檔案結束（EOF）都是文字，可能有很多行、也可能完全沒有文字。

## 限制

- `1 ≤ K ≤ 10^5`
- 文字總長度 `≤ 2×10^6` 個字元，只包含可列印的 ASCII 字元和換行

## 範例

輸入
```
3
The cat and the hat.
THE END -- isn't it?
```
輸出
```
total: 10
distinct: 8
the 3
and 1
cat 1
```

## 提示

- 讀到檔案結束：`while (getline(cin, line))` 或 `while (cin.get(c))`。
- `isalpha` / `tolower` 的參數要先轉成 `unsigned char`，否則遇到負的 `char` 是未定義行為：`tolower((unsigned char)c)`。
- 統計用 `unordered_map<string, int>`；排序時把它複製到 `vector<pair<string, int>>`，再用 `sort` 加 lambda。
- 只要前 `K` 名的話，`partial_sort` 比 `sort` 快（但這題用 `sort` 也夠）。
- 別忘了 **最後一個單字** 後面可能沒有分隔符號（檔案直接結束）。
