# 05. 堆疊、佇列、雙端佇列 (Stack / Queue / Deque)

> 練習題：`05_brackets`、`06_min_stack`、`07_circular_queue`、`08_next_greater`、`09_sliding_window_max`

## 1. Stack：後進先出 (LIFO)

像一疊盤子，只能從最上面拿、放。

```
push 1, push 2, push 3        pop → 3
   |   |                       |   |
   | 3 | ← top                 |   |
   | 2 |                       | 2 | ← top
   | 1 |                       | 1 |
   +---+                       +---+
```

```cpp
stack<int> st;
st.push(1);
st.top();    // 看頂端（空的時候呼叫 → 未定義行為！）
st.pop();    // 移除頂端（不回傳值）
st.empty();
```

用陣列實作只要一個陣列和一個 `top` 索引，所有操作 `O(1)`。

### 什麼時候用 stack？

「**最近的** 還沒處理完的東西要先處理」：
- 括號配對：遇到右括號時，要和 **最近一個** 還沒配對的左括號比。
- 函式呼叫（call stack）、遞迴改迴圈。
- 復原 (undo)、瀏覽器上一頁。
- DFS。

### 括號配對

```cpp
for (char c : s) {
    if (c 是左括號) st.push(c);
    else {
        if (st.empty() || st.top() 不是對應的左括號) return false;  // 先檢查 empty！
        st.pop();
    }
}
return st.empty();   // 還有沒配對的左括號 → false
```

### Min Stack：O(1) 取最小值

另外維護一個 stack `mn`，`mn` 的第 `i` 層存「前 `i` 個元素的最小值」：

```
st:  3  5  1  1  4
mn:  3  3  1  1  1
```

push 時 `mn.push(min(x, mn.top()))`，pop 時兩個一起 pop。
**陷阱**：如果只在 `x < mn.top()` 時才 push 到 `mn`，遇到重複的最小值就會出錯。

## 2. Queue：先進先出 (FIFO)

像排隊。從後面進，從前面出。

```
enqueue →  [ 4 | 3 | 2 | 1 ]  → dequeue
           rear          front
```

```cpp
queue<int> q;
q.push(1);
q.front();
q.pop();
```

用途：BFS、工作排程、緩衝區（buffer）。

### 環狀佇列 (Circular Queue / Ring Buffer)

用普通陣列實作 queue，`front` 一直往後走，前面的空間就浪費了。
解法：走到底就 **繞回開頭**，用 `% K`：

```
K = 5, head = 3, count = 3
索引:  0    1    2    3    4
     [ c ][   ][   ][ a ][ b ]
                      ▲head
元素順序: a, b, c
最後一個的位置 = (head + count - 1) % K = 0
下一個要放的位置 = (head + count) % K = 1
```

用 `head + count` 兩個變數，「空」是 `count == 0`，「滿」是 `count == K`，非常清楚。
如果用 `head + tail` 兩個指標，空和滿時 `head == tail` 都成立，就得多留一格或多一個旗標。

## 3. Deque：雙端佇列

兩邊都可以 push / pop，全部 `O(1)`。`std::deque` 支援 `push_front / push_back / pop_front / pop_back / [i]`。

## 4. 單調堆疊 (Monotonic Stack)

**問題**：對每個元素，找右邊第一個比它大的元素。暴力是 `O(n^2)`。

**想法**：從左到右掃，stack 裡放「還沒找到答案」的元素。這些元素一定是 **由底到頂遞減** 的
（如果有一個比較小的在下面，它早就被上面那個比較大的元素「解決」了）。

```
a = [2, 7, 3, 5, 4, 6]

i=0 a=2: stack [2]
i=1 a=7: 7>2 → ans[2的位置]=7，pop。stack [7]
i=2 a=3: stack [7,3]
i=3 a=5: 5>3 → ans=5，pop。stack [7,5]
i=4 a=4: stack [7,5,4]
i=5 a=6: 6>4 → ans=6；6>5 → ans=6；stack [7,6]
結束：stack 中剩下的答案是 -1
```

每個元素最多 push 一次、pop 一次 → **`O(n)`**。stack 裡要存 **索引**，才知道答案要填在哪裡。

## 5. 單調佇列 (Monotonic Deque)：滑動視窗最大值

視窗往右滑，要隨時知道視窗內的最大值。用 deque 存索引，對應的值 **由前到後遞減**：

1. 新元素 `a[i]` 進來：從 **後面** 把所有 `≤ a[i]` 的丟掉（它們比 `a[i]` 舊又不比它大，永遠不會再是最大值）。
2. 把 `i` 放到後面。
3. 如果 **前面** 的索引已經滑出視窗（`≤ i - k`），丟掉。
4. 前面就是目前視窗的最大值。

每個索引進出 deque 各一次 → **`O(n)`**。

## 6. Corner case checklist

- 對空的 stack / queue 呼叫 `top()` / `front()` / `pop()` —— STL 不會幫你檢查，結果是未定義行為。
- 括號：只有右括號、只有左括號、長度 1、深度 `10^5` 的巢狀。
- min stack：重複的最小值、`int` 的極值（`-2^31`）。
- 環狀佇列：`K = 1`、填滿 → 清空 → 再填滿（繞圈好幾次）。
- 單調堆疊：全部相等（「嚴格大於」還是「大於等於」？）、遞增、遞減、`n = 1`。
- 滑動視窗：`k = 1`、`k = n`。
