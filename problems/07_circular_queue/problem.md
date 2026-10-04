# 07. 環狀佇列 (Circular Queue)

> 主題：佇列 Queue　難度：★★☆　時間限制：1 秒　相關教學：`lessons/05_stack_queue.md`

## 題目

請用 **固定大小的陣列** 實作容量為 `K` 的環狀佇列（ring buffer），**不要用 `std::queue` / `std::deque`**。

| 指令 | 輸出 |
|---|---|
| `enqueue x` | 成功輸出 `ok`；滿了輸出 `full` |
| `dequeue` | 輸出被移除的元素；空的輸出 `empty` |
| `front` | 輸出最前面的元素；空的輸出 `empty` |
| `rear` | 輸出最後面的元素；空的輸出 `empty` |
| `size` | 輸出目前元素個數 |

## 輸入

第一行兩個整數 `K Q`，接下來 `Q` 行指令。

## 輸出

依照上表。

## 限制

- `1 ≤ K ≤ 10^5`，`1 ≤ Q ≤ 3×10^5`
- `-10^9 ≤ x ≤ 10^9`

## 範例

輸入
```
3 9
enqueue 1
enqueue 2
enqueue 3
enqueue 4
rear
dequeue
enqueue 4
rear
front
```
輸出
```
ok
ok
ok
full
3
1
ok
4
2
```

## 提示

- 用 `head`（第一個元素的位置）和 `count`（元素個數）兩個變數最不容易錯。
  最後一個元素的位置是 `(head + count - 1) % K`。
- 如果用 `head` 和 `tail` 兩個指標，要怎麼分辨「空」和「滿」？
- `K = 1` 是很好的 corner case。
