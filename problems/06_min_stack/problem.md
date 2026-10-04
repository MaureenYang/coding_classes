# 06. 最小值堆疊 (Min Stack)

> 主題：堆疊 Stack　難度：★★☆　時間限制：1 秒　相關教學：`lessons/05_stack_queue.md`

## 題目

設計一個 stack，除了 `push / pop / top` 以外，還能在 **`O(1)`** 時間內查詢目前 stack 中的最小值。

| 指令 | 輸出 |
|---|---|
| `push x` | 無 |
| `pop` | 空的時候輸出 `empty` |
| `top` | 輸出頂端元素；空的輸出 `empty` |
| `getmin` | 輸出最小值；空的輸出 `empty` |

## 輸入

第一行 `Q`，接下來 `Q` 行指令。

## 輸出

依照上表。

## 限制

- `1 ≤ Q ≤ 3×10^5`
- `-2^31 ≤ x ≤ 2^31 - 1`（剛好是 `int` 的範圍）
- 每次 `getmin` 都掃過整個 stack 會 **TLE**

## 範例

輸入
```
8
push 3
push 1
push 1
getmin
pop
getmin
pop
getmin
```
輸出
```
1
1
3
```

## 提示

- 另外維護一個 stack，存「到目前這一層為止的最小值」。
- **重複的最小值** 是經典陷阱：如果輔助 stack 只在 `x < min` 時才 push，pop 掉一個 1 之後最小值會錯。
- 如果你用「存差值」的技巧，注意 `int` 相減會溢位。
