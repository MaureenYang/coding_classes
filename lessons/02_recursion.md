# 02. 遞迴：河內塔與回溯法

> 練習題：`01_hanoi`、`02_hanoi_kth`、`17_n_queens`

## 1. 遞迴的三個要素

1. **終止條件 (base case)**：最小的問題直接回答。
2. **縮小問題**：把問題變成「同樣形式、但比較小」的問題。
3. **相信遞迴**：假設小問題已經會解，只思考「怎麼用小問題的答案組出大問題的答案」。

```cpp
long long factorial(int n) {
    if (n == 0) return 1;            // 1. 終止條件
    return n * factorial(n - 1);     // 2+3. 相信 factorial(n-1) 是對的
}
```

## 2. 經典：河內塔 (Tower of Hanoi)

三根柱子 A、B、C，要把 `n` 個盤子從 A 搬到 C，大盤不能壓小盤。

```
    |         |         |
   -+-        |         |
  --+--       |         |
 ---+---      |         |
=========================
    A         B         C
```

**關鍵想法**：最大的盤子 `n` 一定要在某一步從 A 直接移到 C。那一刻，
A 上只有它、C 是空的 → 其他 `n-1` 個盤子全部都在 B 上。所以：

1. 把上面 `n-1` 個盤子從 A 搬到 B（借用 C）—— **這是一個比較小的河內塔！**
2. 把盤子 `n` 從 A 搬到 C。
3. 把 `n-1` 個盤子從 B 搬到 C（借用 A）—— **又是一個比較小的河內塔！**

```cpp
void hanoi(int n, char from, char via, char to) {
    if (n == 0) return;
    hanoi(n - 1, from, to, via);   // 注意：to 和 via 對調
    cout << "move disk " << n << " from " << from << " to " << to << '\n';
    hanoi(n - 1, via, from, to);
}
```

### 步數分析

設 `T(n)` = 搬 `n` 個盤子的步數：`T(n) = 2T(n-1) + 1`，`T(0) = 0`
→ `T(n) = 2^n - 1`。可以證明這也是 **最少** 步數（每一步盤子 `n` 都必須如上移動）。

`n = 64` 時要 `1.8×10^19` 步 —— 指數時間是很可怕的。

### 遞迴樹（n = 3）

```
hanoi(3,A,B,C)
├── hanoi(2,A,C,B)
│   ├── hanoi(1,A,B,C)  → move 1 A→C
│   ├── move 2 A→B
│   └── hanoi(1,C,A,B)  → move 1 C→B
├── move 3 A→C                          ← 第 4 步，正中間
└── hanoi(2,B,A,C)
    ├── hanoi(1,B,C,A)  → move 1 B→A
    ├── move 2 B→C
    └── hanoi(1,A,B,C)  → move 1 A→C
```

觀察：`hanoi(n)` 的第 `2^(n-1)` 步一定是「搬盤子 n」。
前面 `2^(n-1)-1` 步是左邊子樹、後面是右邊子樹 —— 這就是 `02_hanoi_kth` 的解法：
**不用真的走完，只往 `k` 所在的那一邊遞迴**，`O(n)` 就能找到第 `k` 步。

## 3. 遞迴的成本

每次函式呼叫都會在 **call stack** 上放一個 frame（參數、區域變數、返回位址）。

- 河內塔遞迴深度只有 `n`，沒問題。
- 但如果深度是 `10^6`（例如對一條很長的鏈結串列遞迴、對蛇形迷宮做 DFS），就可能 **stack overflow → RE**。
  這時改用迴圈或自己用 `stack` 模擬。

## 4. 回溯法 (Backtracking)

很多問題是「做一連串選擇，找出所有合法的組合」。回溯法的模板：

```cpp
void backtrack(狀態) {
    if (完成) { 記錄答案; return; }
    for (每個選擇) {
        if (不合法) continue;   // 剪枝 pruning：越早剪越快
        做選擇;
        backtrack(下一個狀態);
        撤銷選擇;               // 「回溯」：恢復原狀，才能試下一個選擇
    }
}
```

### 例：列出 1..n 的所有排列

```cpp
int n;
vector<int> cur;
vector<bool> used;

void perm() {
    if ((int)cur.size() == n) {
        for (int x : cur) cout << x << ' ';
        cout << '\n';
        return;
    }
    for (int x = 1; x <= n; x++) {
        if (used[x]) continue;
        used[x] = true; cur.push_back(x);
        perm();
        used[x] = false; cur.pop_back();
    }
}
```

### N 皇后

一列放一個皇后，第 `r` 列試每一行 `c`。衝突檢查用三個陣列：

- 同一行：`col[c]`
- 「\」斜線：同一條上的格子 `r - c` 相同 → `diag2[r - c + n - 1]`
- 「/」斜線：同一條上的格子 `r + c` 相同 → `diag1[r + c]`

這樣檢查是 `O(1)`。比起試所有 `n!` 種排列，剪枝能刪掉絕大部分的分支。

## 5. 練習時的 corner case 思考

- `n = 1`、`n = 0`（如果允許）時，你的終止條件對嗎？
- 答案會不會超過 `int`？（`2^60` 需要 `long long`）
- 遞迴深度最多多少？會不會 stack overflow？
- 輸出量很大時（`2^18` 行），有沒有用 `'\n'` 和關閉同步？
