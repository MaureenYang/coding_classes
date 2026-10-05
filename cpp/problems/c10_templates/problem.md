# C10. 泛型堆疊 (Templates)

> 主題：類別模板、函式模板、模板多載　難度：★★☆　時間限制：1 秒　相關教學：`cpp/lessons/10_templates.md`

## 題目

寫 **一個** 類別模板 `Stack<T>`，同時拿來存三種型別：

| 型別名稱 | C++ 型別 | 輸入格式 | 輸出格式 |
|---|---|---|---|
| `int` | `int` | `42` | `42` |
| `str` | `std::string` | `abc` | `abc` |
| `pair` | `std::pair<int, std::string>` | `3 abc` | `(3,abc)` |

程式裡同時存在三個堆疊 `Stack<int>`、`Stack<string>`、`Stack<pair<int,string>>`，每個指令的第一個字指定要操作哪一個：

| 指令 | 輸出 |
|---|---|
| `T push v` | — |
| `T pop` | 被移除的元素；空的輸出 `empty` |
| `T top` | 頂端元素；空的輸出 `empty` |
| `T size` | 元素個數 |
| `T max` | 堆疊裡最大的元素（用 `<` 比較）；空的輸出 `empty` |
| `T sorted` | 所有元素 **由小到大** 排序後輸出，空白分隔（不改變堆疊本身）；空的輸出 `empty` |

`pair` 的大小比較是 **先比 `first`，相同再比 `second`**（`std::pair` 內建的 `<` 就是這樣）。
字串用字典序比較。

## 輸入

第一行 `Q`，接下來 `Q` 行指令。

## 限制

- `1 ≤ Q ≤ 2×10^5`
- `int` 的值在 `-10^9 ~ 10^9`；字串是長度 `1 ~ 5` 的小寫字母
- `sorted` 指令輸出的總元素數 `≤ 2×10^5`

## 範例

輸入
```
9
int push 5
int push -2
str push hi
pair push 2 b
pair push 2 a
int max
pair sorted
str pop
str top
```
輸出
```
5
(2,a) (2,b)
hi
empty
```

## 提示

- `Stack<T>` 內部可以用 `std::vector<T>` 存資料。
- `max` 和 `sorted` 可以寫成 **函式模板**，對任何「有 `<` 運算子」的型別都能用。
- 輸出的格式不同：寫一個函式模板 `void print(const T& x)`，再為 `pair` 寫一個 **多載版本**：

```cpp
template <class T> void print(const T& x) { cout << x; }
template <class A, class B> void print(const pair<A, B>& p) { cout << '(' << p.first << ',' << p.second << ')'; }
```

  呼叫 `print(x)` 時，編譯器會自動挑「最符合」的版本。

- 三種型別的指令處理流程完全一樣 —— 也寫成一個函式模板 `handle(Stack<T>& s, ...)`，就不用寫三次。
