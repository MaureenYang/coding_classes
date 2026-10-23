# 第 3 章　Atoms（原子字串）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.33–44

---

## 1. 本章定位

**Atom** 是指向一段**唯一、不可變**位元組序列的指標，可以是零個或多個任意位元組。大多數 atom 指向以 NUL 結尾的字串，但任何位元組序列都可以當 atom。

- 同一段內容**只會存在一份**，這就是「原子」這個名字的由來。
- **兩個 atom 相等 ⇔ 指標相等**，比較內容只要比指標，不用 `strcmp`。
- 每段內容只存一份，所以**省空間**。
- 用途：當作以位元組序列索引的資料結構的**鍵**。第 8 章的 Table 和第 9 章的 Set 預設都用 atom 當鍵。

本章是第一個「真正的」模組，介面極小，實作是一個**雜湊表**。

---

## 2. 介面（3.1 Interface）

```c
/* atom.h */
#ifndef ATOM_INCLUDED
#define ATOM_INCLUDED

extern       int   Atom_length(const char *str);
extern const char *Atom_new   (const char *str, int len);
extern const char *Atom_string(const char *str);
extern const char *Atom_int   (long n);

#endif
```

注意：Atom **不是 ADT**，沒有 `T` 型別，atom 就是 `const char *`。回傳 `const` 正是為了提醒使用者**不可以修改**。

### 2.1 各函式語意

| 函式 | 功能 |
|---|---|
| `Atom_new(str, len)` | 接受任意位元組序列 `str[0..len-1]`。表中沒有就**複製一份**加進 atom 表，然後回傳 atom（指向表中那份複本）。**永遠不回傳 NULL**，而且一定會在結尾補上 `'\0'` |
| `Atom_string(str)` | `Atom_new` 的便利版，接受以 NUL 結尾的字串 |
| `Atom_int(n)` | 回傳 `long` 整數 `n` 的十進位字串表示對應的 atom |
| `Atom_length(str)` | 回傳 atom 的長度 |

**Atom 一旦建立，就存在到程式結束為止**，沒有釋放函式。

### 2.2 完整合約

| 類別 | 內容 |
|---|---|
| **Checked runtime error** | 傳 NULL 給任何函式；傳負數 `len` 給 `Atom_new`；傳**不是 atom** 的指標給 `Atom_length` |
| **Unchecked runtime error** | **修改** atom 指向的位元組 |
| **效能** | `Atom_length` 的執行時間**可能和 atom 總數成正比** |
| **Exception** | `Atom_new`、`Atom_string`、`Atom_int` 可能丟出 `Mem_Failed` |

> 這裡示範了第 2 章的主張：**效能特性也是介面的一部分**，`Atom_length` 很慢，所以直接寫在規格裡。

---

## 3. 實作（3.2 Implementation）

```
〈atom.c〉≡
    〈includes〉
    〈macros〉
    〈data〉
    〈functions〉
```

### 3.1 `Atom_string`：建立在 `Atom_new` 之上

```c
const char *Atom_string(const char *str) {
    assert(str);
    return Atom_new(str, strlen(str));
}
```

不需要知道 atom 表怎麼表示，就能實作。

### 3.2 `Atom_int`：數字轉字串的細節

```c
const char *Atom_int(long n) {
    char str[43];
    char *s = str + sizeof str;
    unsigned long m;

    if (n == LONG_MIN)
        m = LONG_MAX + 1UL;
    else if (n < 0)
        m = -n;
    else
        m = n;
    do
        *--s = m%10 + '0';
    while ((m /= 10) > 0);
    if (n < 0)
        *--s = '-';
    return Atom_new(s, (str + sizeof str) - s);
}
```

**這段程式處理了兩個陷阱：**

1. **二補數範圍不對稱**：負數比正數多一個，所以 `-LONG_MIN` 無法表示，會溢位。因此先特判 `LONG_MIN`，用 `LONG_MAX + 1UL`（無號運算）取得它的絕對值。
2. **有號除法與取餘數的語意不明確**（第 2 章 `Arith` 談過的問題）：改用 **unsigned 運算**，因為無號的 `/` 和 `%` 定義是清楚的。

**其他技巧：**
- 從右到左產生數字，`*--s` 讓 `s` 從緩衝區尾端往回移動，最後 `s` 就指向字串開頭，不需要反轉。
- 長度是 `&str[43] - s`。

**為什麼是 43？**
假設 `long` 是 128 位元，128 位元整數用**八進位**表示最多需要 128/3 + 1 = 43 個字元，而十進位的位數不會比八進位多，所以 43 對「任何可以想像的機器」都夠用。

### 3.3 Magic Number 的取捨

43 是一個「magic number」。一般建議替它取個符號名稱，但作者的原則是：

> **只有當一個值出現不只一次，或者它是介面的一部分時，才定義符號名稱。**

這裡 43 只出現一次，其他地方都用 `sizeof str` 取得。另外定義名稱雖然可能比較好讀，但會讓程式變長，也污染名稱空間。後面雜湊表大小 2048 也是同樣的處理。

### 3.4 Atom 表：雜湊表

```c
static struct atom {
    struct atom *link;
    int len;
    char *str;
} *buckets[2048];
```

- `buckets` 是指標陣列，每個元素指向一條**鏈結串列**，串列上是雜湊到該位置的所有 atom（separate chaining）。
- `link` 指向下一個項目，`len` 是長度，`str` 指向序列本身。
- 每個項目**剛好**夠放它的序列。

```
buckets
  [0]    → atom → atom → NULL
  [1]    → NULL
  ...
  [2047] → atom → NULL
```

**單一項目的記憶體配置**（以 `Atom_string("an atom")` 為例）：

```
+--------+
| link   |
| len=7  |
| str  ──┼──┐
+--------+  │
| a n _ a │ ←┘  序列緊接在結構後面
| t o m \0│
+--------+
```

### 3.5 `Atom_new`：核心函式

```c
#define NELEMS(x) ((sizeof (x))/(sizeof ((x)[0])))

const char *Atom_new(const char *str, int len) {
    unsigned long h;
    int i;
    struct atom *p;

    assert(str);
    assert(len >= 0);
    for (h = 0, i = 0; i < len; i++)                 /* 計算雜湊值 */
        h = (h<<1) + scatter[(unsigned char)str[i]];
    h %= NELEMS(buckets);
    for (p = buckets[h]; p; p = p->link)             /* 搜尋 */
        if (len == p->len) {
            for (i = 0; i < len && p->str[i] == str[i]; )
                i++;
            if (i == len)
                return p->str;                        /* 已存在 */
        }
    /* 配置新項目 */
    p = ALLOC(sizeof (*p) + len + 1);
    p->len = len;
    p->str = (char *)(p + 1);
    if (len > 0)
        memcpy(p->str, str, len);
    p->str[len] = '\0';
    p->link = buckets[h];
    buckets[h] = p;
    return p->str;
}
```

**重點解析：**

- **`NELEMS` 巨集**：常見的 C 慣用寫法，陣列元素個數 = 整個陣列大小 ÷ 單一元素大小。`sizeof` 在編譯期求值，所以只適用於編譯期已知大小的陣列。
- **先比長度再比內容**：長度不同就不用逐一比較位元組。
- **逐一比較位元組，不用 `strncmp`**：因為序列可以包含 `'\0'`（習題 3.3）。
- **一次 `ALLOC` 同時配置結構和序列**：`p->str = (char *)(p + 1)` 讓字串緊接在結構後面，減少配置次數。這裡不能用 `NEW`，因為大小取決於 `len`，而 `NEW` 只適用於編譯期已知大小的情況。
- **新項目插在串列前端**：插在尾端也可以，但插在前端比較簡單。

### 3.6 雜湊函式：`scatter` 查表法

```c
for (h = 0, i = 0; i < len; i++)
    h = (h<<1) + scatter[(unsigned char)str[i]];
```

- `scatter` 是一個 **256 個元素的陣列**，把每個位元組對應到一個**隨機數**（用 `rand` 產生）。
- 經驗顯示，這個簡單的方法能讓雜湊值分布得比較均勻。這個雜湊函式是 Hans Boehm 建議的，lcc 編譯器也用它。
- **`(unsigned char)` 轉型很關鍵**：C 的「plain `char`」可能有號也可能無號，由實作決定。不轉型的話，在 `char` 有號的機器上，大於 127 的值會變成**負數索引**。

**效能分析**：如果 N 個序列平均分布，每條串列有 N/2048 個元素，平均搜尋時間是 N/(2·2048)。**N 小於大約 2×2048 時，搜尋時間基本上是常數**。

### 3.7 `Atom_length`：慢但正確

```c
int Atom_length(const char *str) {
    struct atom *p;
    int i;

    assert(str);
    for (i = 0; i < NELEMS(buckets); i++)
        for (p = buckets[i]; p; p = p->link)
            if (p->str == str)
                return p->len;
    assert(0);
    return 0;
}
```

- 不知道長度就沒辦法計算雜湊值，所以只能**掃過整個表比對指標**，因此是 O(atom 總數)。
- **`assert(0)`** 有兩個用途：
  1. 實作 checked runtime error：傳進來的不是 atom。
  2. 標示「**不可能發生**」（can't happen）的情況。

---

## 4. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **介面極簡** | 只有 4 個函式，都是 client 最常用的（習題 3.7 提到介面是「演化」成這樣的） |
| **用 `const` 表達不可變** | 回傳 `const char *`。這和第 2 章「ADT 不用 const」不衝突，因為 atom 不是不透明指標，`const` 表達的是**介面語意** |
| **以空間換簡單** | atom 永不釋放。作者在延伸閱讀說，lcc 也這樣做，因為 C 程式裡不同字串的數量出奇地少，不管原始碼多大都一樣 |
| **避開 C 的語意陷阱** | 二補數不對稱、有號除法、plain char 的正負號 |
| **效能寫進合約** | 明確說明 `Atom_length` 很慢 |
| **防禦式程式設計** | 用 `assert` 檢查所有 checked runtime error |

---

## 5. 延伸閱讀重點

- Atom 這個名字來自 **LISP**；字串處理語言 **SNOBOL4** 的字串實作幾乎和本章完全一樣（Griswold, 1972）。
- **lcc 編譯器**（Fraser & Hanson, 1995）有一個類似的模組，是 Atom 實作的前身：所有識別字和常數字串都存在同一張表裡，而且從不釋放。
- 雜湊相關：Sedgewick (1990)、Knuth (1973b)。

---

## 6. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 3.1 | 把 `buckets` 從 2048（2 的冪）改成質數 2039，量測速度和串列長度分布 | 教科書常說 2 的冪不好，**實際量測**看看是否真的如此 |
| 3.2 | 從文獻找更好的雜湊函式並量測 | 實證導向 |
| 3.3 | 為什麼 `Atom_new` 不用 `strncmp`？ | 序列可以包含 `'\0'` |
| 3.4 | 改用 `char str[1]` 放在結構尾端（struct hack），省掉一次間接存取，值得違反標準嗎？ | 存取 `str[0]` 之後的位元組在 C89 是未定義行為（C99 之後有 flexible array member） |
| 3.5 | 在 `struct atom` 裡也存完整雜湊值以便比較，值得嗎？ | 量測再判斷 |
| 3.6 | 讓 `Atom_length` 和 `Atom_new` 一樣快 | 例如利用 atom 前面就是 `struct atom` 的特性，或另建以指標為鍵的雜湊 |
| 3.7 | 實作 `Atom_init(int hint)` | 什麼時候可以呼叫？需要哪些 checked error？ |
| 3.8 | 實作 `Atom_free`、`Atom_reset` | 釋放會破壞「atom 永遠存在」的假設，合約要怎麼改？ |
| 3.9 | 實作 `Atom_vload(...)`、`Atom_aload(strs[])` | 可變參數、批次載入 |
| 3.10 | 實作不複製內容的 `Atom_add` | 所有權：client 承諾不釋放，和 `Atom_free` 並存時的合約問題 |

> 習題 3.7–3.10 都在探討**介面擴充對合約的影響**，這是本書習題的典型風格。

---

## 7. 本章重點整理

1. **Atom = 唯一、不可變的位元組序列**，比較只要比指標，而且省空間。
2. **介面極小**：`Atom_new`、`Atom_string`、`Atom_int`、`Atom_length`。
3. **實作**：2048 個 bucket 的雜湊表加串列；結構和字串一次配置；新項目插在串列前端。
4. **雜湊**：`scatter` 隨機數表加左移；記得把 `char` 轉成 `unsigned char`。
5. **C 陷阱**：`LONG_MIN` 的絕對值、有號除法語意、plain char 的正負號。
6. **風格**：magic number 只出現一次就不另外取名；用 `assert(0)` 標示不可能發生的情況。
7. **Atom 是後續 Table、Set 的基礎設施。**

> **一句話**：Atom 用一個簡單的雜湊表換來「字串比較等於指標比較」，是一個用極小的介面解決常見問題的範例。
