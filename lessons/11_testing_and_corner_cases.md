# 11. 如何找 Corner Case、自己產生測資、對拍

寫完程式、範例過了，**不代表程式是對的**。這一課教你像出題者一樣思考。

## 1. Corner case 從哪裡來？—— 一份萬用清單

拿到題目後，對每一項問自己「這個情況我的程式會怎樣？」

### 大小的邊界
- **最小**：`n = 0`、`n = 1`、空字串、空的容器。
- **最大**：`n` 是上限時會不會 TLE？會不會溢位？會不會 stack overflow？
- **剛好**：容量剛好滿、`k = n`、`k = 1`。

### 數值的邊界
- 負數、0、`int` 的極值 `-2^31` / `2^31 - 1`、`±10^18`。
- 兩個大數相加 / 相乘會不會超過型別範圍？
- 負數取餘數、負數除法（C++ 向 0 取整）。

### 結構的特殊形狀
- 全部相同、嚴格遞增、嚴格遞減、交錯（zigzag）。
- 樹：一條鏈（退化）、星狀（一個中心連所有點）、完全二元樹。
- 圖：不連通、自環、重邊、有環、只有一個點。
- 網格：`1 × n`、`n × 1`、全是牆、蛇形長路。

### 操作序列
- 對空的結構做刪除 / 查詢。
- 刪光之後再加入（指標有沒有重設？）。
- 同一個元素重複加入、重複刪除。
- 刪除「第一個」、「最後一個」、「唯一一個」。

### 輸出格式
- 每行結尾、最後要不要換行（本平台會忽略行尾空白）。
- 「無解」時要輸出什麼？

> 在這個平台上，`corner_xxx` 測資的名稱就是在告訴你它測的是哪一種情況。
> 先試著 **自己猜** 有哪些 corner case，再去「測資」分頁對答案。

## 2. 用 assert 檢查自己的假設

```cpp
#include <cassert>
assert(i >= 0 && i < n);   // 條件不成立時程式立刻中止，並告訴你是哪一行
```

## 3. 用 sanitizer 抓記憶體錯誤

```bash
python3 judge.py test 04_linked_list --debug
```

等同於用這些參數編譯：

```bash
g++ -std=c++17 -g -fsanitize=address,undefined -D_GLIBCXX_DEBUG my.cpp
```

- `address`：越界存取、use-after-free、memory leak。
- `undefined`：整數溢位（有號數）、空指標、移位過多。
- `_GLIBCXX_DEBUG`：讓 STL 檢查 `v[i]` 越界、對空 `stack` 呼叫 `top()` 等。

程式會變慢（所以 debug 模式時間限制放寬 4 倍），但錯誤訊息會直接指出 **哪一行** 出事。

## 4. 對拍 (Stress Testing)

**最強大的除錯技巧**：寫一個「暴力但一定對」的版本，用大量 **隨機小測資** 比較兩者的輸出，
直到找到不一樣的那一筆。小測資的好處是 —— 找到反例後你可以 **用手算**。

這個平台已經內建：

```bash
python3 judge.py stress 06_min_stack        # 和標準解比對 300 筆隨機小測資
python3 judge.py stress 06_min_stack -n 2000
```

找到反例會存在 `workspace/<題目>.failed.in`，然後：

```bash
python3 judge.py run workspace/06_min_stack.cpp workspace/06_min_stack.failed.in
```

### 自己寫對拍（沒有標準解的時候）

1. `brute.cpp`：暴力解（例如 next greater 用 `O(n^2)` 雙迴圈）—— 簡單到不會錯。
2. `gen.py`：隨機產生小測資。
3. 迴圈比對：

```bash
g++ -O2 -o mine mine.cpp && g++ -O2 -o brute brute.cpp
for i in $(seq 1 1000); do
    python3 gen.py $i > in.txt
    ./mine  < in.txt > out1.txt
    ./brute < in.txt > out2.txt
    if ! diff -wq out1.txt out2.txt > /dev/null; then
        echo "第 $i 筆不同："; cat in.txt; break
    fi
done
```

`gen.py` 範例（用 seed 讓每次結果可重現）：

```python
import random, sys
rng = random.Random(int(sys.argv[1]))
n = rng.randint(1, 8)                       # 小！方便手算
print(n)
print(*[rng.randint(-5, 5) for _ in range(n)])   # 值的範圍也小，才容易出現重複
```

**重點：值的範圍要小**。`randint(-10^9, 10^9)` 幾乎不會產生重複的值，就測不到「相等」的情況。

## 5. 寫給自己的題目產生器

想在這個平台新增題目？看任何一題的 `gen.py`：

```python
TITLE = "題目名稱"
TOPIC = "主題"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0          # 秒

def manual_cases():
    """回傳 [(名稱, 輸入字串), ...]，名稱會變成 corner_名稱"""
    return [("n1", "1\n5"), ...]

def random_case(rng, size):
    """size 是 'small' / 'medium' / 'large'；rng 是 random.Random"""
    n = {"small": rng.randint(1, 8), "medium": 1000}.get(size, 200000)
    return f"{n}\n" + " ".join(str(rng.randint(-9, 9)) for _ in range(n))
```

`large` 的測資要做到題目上限，才能檢查時間複雜度；
並且特別設計 **讓錯誤做法變慢** 的資料（例如針對雜湊函數的規律 key、讓沒優化的併查集變成長鏈）。

## 6. 除錯流程總結

1. 範例過了嗎？
2. 自己列出 corner case，手動測試（網頁版的「自訂輸入」）。
3. WA → 看失敗的測資名稱、看第幾行不一樣。
4. RE → `--debug` 看錯誤位置。
5. TLE → 重新算複雜度；檢查 I/O 有沒有加速、有沒有 `endl`。
6. 還是找不到 → **對拍**。
