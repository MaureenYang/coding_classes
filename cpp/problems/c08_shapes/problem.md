# C08. 圖形與多型 (Inheritance & Polymorphism)

> 主題：繼承、虛擬函式、抽象類別、多型　難度：★★☆　時間限制：1 秒　相關教學：`cpp/lessons/08_inheritance_polymorphism.md`

## 題目

設計以下的類別階層：

```
           Shape（抽象類別）
         /     |      \
     Circle  Rectangle  Triangle
                |
              Square
```

`Shape` 有三個 **純虛擬函式**：`name()`、`area()`、`perimeter()`。
`Square` **繼承** `Rectangle`（正方形是長寬相等的長方形），只需要改寫 `name()`。

讀入 `N` 個圖形，全部存在 `vector<unique_ptr<Shape>>` 裡（**用基底類別的指標存不同的子類別**），然後：

1. 依照 **面積由大到小** 排序後輸出每個圖形：`name area perimeter`（兩位小數）。
   面積相同（差距小於 `1e-9`）時，**保持輸入順序**。
2. 最後輸出一行 `total area: X`（兩位小數）。

| 輸入格式 | `name()` | 面積 | 周長 |
|---|---|---|---|
| `circle r` | `circle` | `π r²` | `2 π r` |
| `rect w h` | `rectangle` | `w h` | `2(w + h)` |
| `square s` | `square` | `s²` | `4 s` |
| `triangle a b c` | `triangle` | 海龍公式 | `a + b + c` |

`π` 請用 `acos(-1.0)`。**海龍公式**：`s = (a + b + c) / 2`，面積 `= √(s(s-a)(s-b)(s-c))`。

## 輸入

第一行 `N`，接下來 `N` 行圖形。所有長度都是 `1 ~ 1000` 的整數，三角形保證合法（任兩邊和大於第三邊）。

## 輸出

`N` 行圖形資訊，最後一行總面積。用 `fixed << setprecision(2)` 輸出。

## 限制

- `1 ≤ N ≤ 10^5`

## 範例

輸入
```
4
rect 2 3
circle 1
square 2
triangle 3 4 5
```
輸出
```
rectangle 6.00 10.00
triangle 6.00 12.00
square 4.00 8.00
circle 3.14 6.28
total area: 19.14
```

## 提示

- **基底類別一定要有虛擬解構子** `virtual ~Shape() = default;`。
  否則透過 `Shape*` 刪除 `Circle` 時，`Circle` 的解構子不會被呼叫（未定義行為）。
- 子類別覆寫時加上 `override`，打錯函式名稱時編譯器會直接報錯。
- `Square` 的建構子要呼叫 `Rectangle(s, s)`（成員初始化串列）。
- 排序 `unique_ptr` 時，比較函式的參數寫 `const unique_ptr<Shape>&`；保持輸入順序用 `stable_sort`。
- 如果你把物件 **以值** 存進 `vector<Shape>`，會發生 **物件切割 (object slicing)** —— 其實這樣根本編譯不過，因為 `Shape` 是抽象類別。
