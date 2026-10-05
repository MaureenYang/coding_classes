# 05. 指標與參考 (Pointers & References)

> 程式練習：`C05 用指標做矩陣`
>
> 先備知識：第 01 課「變數與記憶體」、第 04 課「傳參考」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 指標的本質 | 位址、`&` 和 `*`、指標的型別、`void*`、空指標、野指標 |
| 第二部分 | 指標運算與陣列 | `p + 1` 到底加了多少、陣列退化、`a[i]` 的真面目、C 風格字串 |
| 第三部分 | const 與指標 | `const int*` 和 `int* const` 的差別，怎麼讀 |
| 第四部分 | 指標的指標與二維陣列 | `int**`、動態二維陣列的兩種做法、記憶體排列 |
| 第五部分 | 參考 | 參考的三條規則、跟指標比較、延長暫時物件的生命 |
| 第六部分 | 指標錯誤大全 | 每一種錯誤長什麼樣子、怎麼抓、怎麼避免 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：...` 是實際執行的結果（位址每次執行都不同，以 `0x7ffd...` 表示）。標 🔍 的是深入內容。

---

# 第一部分：指標的本質

## 1.1 位址 (Address)

**是什麼**：記憶體可以想成一排非常長的格子，**每個格子（1 byte）都有一個編號**，這個編號就是 **位址**。每個變數都佔用一段連續的格子，第一個格子的編號就是這個變數的位址。

**比喻**：一條街上每間房子都有門牌號碼。變數是房子，位址是門牌號碼。

```cpp
int x = 42;
double d = 3.14;
cout << &x << '\n';             // 輸出：0x7ffd5c3a1b4c（x 的位址，每次執行可能不同）
cout << &d << '\n';             // 輸出：0x7ffd5c3a1b50
cout << sizeof(x) << ' ' << sizeof(d) << '\n';   // 輸出：4 8（x 佔 4 個格子，d 佔 8 個）
```

`&x` 讀作「x 的位址」，`&` 叫做 **取址運算子 (address-of operator)**。

## 1.2 指標 (Pointer)

**是什麼**：一個 **存放位址** 的變數。指標本身也是變數，也有自己的位址、也佔記憶體（64 位元系統上是 8 bytes）。

**為什麼需要指標？**
1. **間接存取**：透過位址找到另一個變數，並且修改它。
2. **動態記憶體**：`new` 配置的記憶體沒有名字，只能透過指標使用（第 06 課）。
3. **資料結構**：鏈結串列、樹的節點用指標互相連接（DS 路線第 04、08 課）。

**比喻**：一張寫著門牌號碼的紙條。紙條不是房子，但照著它可以找到房子、進去改裝。

### 指標的四個基本操作

| 寫法 | 名稱 | 意思 |
|---|---|---|
| `int* p;` | 宣告 | `p` 是「指向 `int` 的指標」 |
| `p = &x;` | 取址 | 把 `x` 的位址存進 `p` |
| `*p` | **解參考 (dereference)** | 照著位址，拿到（或修改）那個 `int` |
| `p->m` | 箭頭 | 等於 `(*p).m`，存取指向的物件的成員 |

每個操作的範例：

```cpp
int x = 42;
int* p = &x;                    // 宣告 + 取址：p 存的是 x 的位址

cout << p << '\n';              // 印出指標本身（位址）→ 輸出：0x7ffd...（跟 &x 一樣）
cout << *p << '\n';             // 解參考：照著位址拿值 → 輸出：42

*p = 100;                       // 透過指標修改 x
cout << x << '\n';              // 輸出：100

int y = 7;
p = &y;                         // 指標可以改指向別的變數
cout << *p << '\n';             // 輸出：7

cout << sizeof(p) << '\n';      // 輸出：8（64 位元系統上，任何型別的指標都是 8 bytes）
cout << &p << '\n';             // 指標本身也有位址 → 輸出：0x7ffd...（跟 &x 不同）
```

**箭頭 `->` 的範例**：

```cpp
struct Point { int x, y; };
Point pt{3, 4};
Point* pp = &pt;
cout << (*pp).x << ' ' << pp->y << '\n';   // 兩種寫法一樣 → 輸出：3 4
pp->x = 10;
cout << pt.x << '\n';                      // 輸出：10
```

`(*pp).x` 一定要加括號，因為 `.` 的優先順序比 `*` 高：`*pp.x` 會被理解成 `*(pp.x)`。所以才發明了 `->` 這個比較好寫的寫法。

### 「*」的兩種意思

| 位置 | 意思 | 例子 |
|---|---|---|
| **宣告** 裡 | 「這是指標型別」 | `int* p;` |
| **運算式** 裡 | 「解參考」 | `*p = 5;`、`cout << *p;` |

（還有第三種：乘法 `a * b`，由前後文區分。）

### ⚠️ 宣告多個指標的陷阱

```cpp
int* a, b;          // 只有 a 是指標，b 是 int！
                    // * 屬於變數名稱，不屬於型別
int *c, *d;         // ✅ 兩個都是指標
int* e;             // ✅ 或者一行只宣告一個（推薦）
int* f;
```

## 1.3 指標的型別

**規則**：指標會記得「**它指向什麼型別**」。這樣解參考時，編譯器才知道要讀幾個 byte、用什麼格式解讀。

```cpp
int i = 5;
double d = 2.5;
int* pi = &i;           // ✅
double* pd = &d;        // ✅
// int* bad = &d;       // ❌ error: cannot convert 'double*' to 'int*'
```

為什麼不行？`int*` 解參考時會讀 4 bytes、當成整數；但 `d` 是 8 bytes 的浮點數，用整數的方式讀它的前 4 bytes，會得到毫無意義的結果。

### void*：可以指向任何東西的指標

**是什麼**：不記得型別的「通用指標」。任何指標都能自動轉成 `void*`，但 **`void*` 不能直接解參考**（不知道要讀幾個 byte），要先轉回正確的型別。

```cpp
int n = 42;
double v = 1.5;
void* vp = &n;                          // ✅ int* → void* 自動轉換
vp = &v;                                // ✅ double* → void* 也可以
// cout << *vp;                         // ❌ error: 'void*' is not a pointer-to-object type
double* back = static_cast<double*>(vp);   // 轉回原本的型別
cout << *back << '\n';                  // 輸出：1.5
```

`void*` 主要出現在 C 語言的函式庫（例如 `malloc`、`memcpy`、`qsort`）。C++ 程式通常用模板代替。

## 1.4 空指標 (Null Pointer)

**是什麼**：**不指向任何東西** 的指標。C++11 起用 `nullptr` 表示。

**為什麼需要**：表示「目前沒有指向任何東西」—— 串列的最後一個節點的 `next`、樹的葉節點的 `left` / `right`、「找不到」的回傳值。

```cpp
int* p = nullptr;
if (p == nullptr) cout << "p 是空的\n";   // 輸出：p 是空的
if (!p) cout << "也可以這樣寫\n";          // 空指標轉成 bool 是 false → 輸出：也可以這樣寫
// *p = 5;                                // ❌ 解參考空指標 → 程式當掉（SIGSEGV，評測是 RE）
```

**實際用途：找不到時回傳 nullptr**

```cpp
int* find_first_negative(int* arr, int n) {
    for (int i = 0; i < n; i++)
        if (arr[i] < 0) return &arr[i];
    return nullptr;                       // 找不到
}
int data[] = {3, 8, -2, 5};
int* r = find_first_negative(data, 4);
if (r) cout << *r << '\n';                // 輸出：-2
*r = 0;                                   // 透過指標修改陣列裡的元素
cout << data[2] << '\n';                  // 輸出：0
```

### nullptr vs NULL vs 0

`NULL` 和 `0` 其實是 **整數** 0，在函式多載時會出問題：

```cpp
void f(int)  { cout << "f(int)\n"; }
void f(int*) { cout << "f(int*)\n"; }
f(0);          // 輸出：f(int)  —— 你可能想呼叫指標版本
// f(NULL);    // GCC：編譯錯誤「模稜兩可」；其他編譯器可能呼叫 f(int)
f(nullptr);    // 輸出：f(int*) ✅ nullptr 只會轉成指標
```

`nullptr` 的型別是專門的 `std::nullptr_t`，只能轉成指標。**一律用 `nullptr`**。

## 1.5 野指標 (Wild Pointer)

**是什麼**：**沒有初始化** 的指標。裡面是垃圾值，指向不知道哪裡的記憶體。

```cpp
int* p;            // 野指標：p 裡面是隨機的值
// *p = 5;         // ❌ 寫到一個隨機的位置：
                   //    可能當掉、可能默默破壞了別的變數（最可怕：程式之後才出現奇怪的錯誤）
```

**和空指標的差別**：空指標「明確地什麼都不指」，可以檢查（`if (p)`）；野指標「指向某個未知的地方」，**沒有辦法檢查** 它是不是有效的。

**規則**：宣告指標時 **立刻初始化**。還不知道要指向哪裡，就設成 `nullptr`。

```cpp
int* q = nullptr;  // ✅
```

---

# 第二部分：指標運算與陣列

## 2.1 指標運算 (Pointer Arithmetic)

**規則**：指標加減整數時，移動的單位是「**一個元素**」，也就是 `sizeof(指向的型別)` 個 byte，**不是 1 個 byte**。

**比喻**：一排同樣大小的置物櫃，「往後一格」就是跳過一整個櫃子的寬度。不管櫃子是寬（`double`，8 bytes）還是窄（`char`，1 byte），「下一個」永遠是下一個櫃子。

| 運算 | 意思 | 例子（`int* p` 指向 `a[1]`） |
|---|---|---|
| `p + n` | 往後 n 個元素 | `p + 2` 指向 `a[3]` |
| `p - n` | 往前 n 個元素 | `p - 1` 指向 `a[0]` |
| `p++` / `p--` | 移到下一個 / 上一個元素 | |
| `q - p` | 兩個指標之間差幾個元素（型別 `ptrdiff_t`） | |
| `p < q`、`p == q` | 比較位置（只對同一個陣列有意義） | |
| `p[n]` | 等於 `*(p + n)` | `p[2]` 是 `a[3]` |

每一種運算的範例：

```cpp
int a[5] = {10, 20, 30, 40, 50};
int* p = &a[1];                        // 指向 20

cout << *(p + 2) << '\n';              // a[3] → 輸出：40
cout << *(p - 1) << '\n';              // a[0] → 輸出：10
cout << p[2] << ' ' << p[-1] << '\n';  // 一樣的意思 → 輸出：40 10

p++;                                   // 移到 a[2]
cout << *p << '\n';                    // 輸出：30

int* q = &a[4];
cout << q - p << '\n';                 // 差幾個元素 → 輸出：2
cout << (p < q) << '\n';               // p 在 q 前面 → 輸出：1
```

**位址實際增加了多少**：

```cpp
int ia[3];
double da[3];
char ca[3];
cout << (char*)(ia + 1) - (char*)ia << ' '    // int：4 bytes
     << (char*)(da + 1) - (char*)da << ' '    // double：8 bytes
     << (char*)(ca + 1) - (char*)ca << '\n';  // char：1 byte
// 輸出：4 8 1
```

**用指標走訪陣列**：

```cpp
int arr[] = {1, 2, 3, 4};
int sum = 0;
for (int* it = arr; it != arr + 4; ++it)   // it 從第一個元素走到「最後一個的下一個」
    sum += *it;
cout << sum << '\n';                       // 輸出：10
```

這就是 STL 迭代器的原型：`begin()` 是 `arr`、`end()` 是 `arr + 4`。

### 合法的範圍：尾後指標 (One-past-the-end)

指標只能指向 **陣列裡的元素**，或 **最後一個元素的「下一個位置」**：

```cpp
int b[5];
int* end_ptr = b + 5;      // ✅ 合法：尾後指標，可以拿來比較（迴圈的結束條件）
// int x = *end_ptr;       // ❌ 不能解參考：那裡沒有元素
// int* beyond = b + 6;    // ❌ 連「算出來」都是未定義行為
```

STL 的 `v.end()` 就是這個概念。

## 2.2 陣列退化 (Array-to-pointer Decay)

**是什麼**：在大部分的運算式裡，**陣列名稱會自動轉成「指向第一個元素的指標」**，而且 **陣列的大小資訊就消失了**。

```cpp
int a[5] = {1, 2, 3, 4, 5};
int* p = a;                    // a 自動退化成 &a[0]
cout << (p == &a[0]) << '\n';  // 輸出：1
```

**大小資訊消失了**：

```cpp
cout << sizeof(a) << '\n';     // 輸出：20（sizeof 是例外，不會退化：5 × 4 bytes）
cout << sizeof(p) << '\n';     // 輸出：8（只是一個指標的大小）

void show(int arr[]) {         // 參數寫 int arr[]，其實就是 int* arr
    cout << sizeof(arr) << '\n';   // 輸出：8（不是 20！）
}
show(a);
```

**比喻**：寄包裹時只寫了「第一個箱子的位置」，收件人不知道總共有幾箱。

**所以傳陣列給函式時，一定要另外傳長度**：

```cpp
int sum_array(const int* arr, int n) {   // 一定要知道 n
    int s = 0;
    for (int i = 0; i < n; i++) s += arr[i];
    return s;
}
cout << sum_array(a, 5) << '\n';         // 輸出：15

// 計算內建陣列的長度（只能在陣列還沒退化的地方用）
int len = sizeof(a) / sizeof(a[0]);      // 20 / 4 = 5
cout << len << '\n';                     // 輸出：5
```

**更好的做法**：用 `vector`、`std::array`（自己知道大小），或 C++20 的 `std::span`。

### 🔍 a[i] 的真面目

`a[i]` 被 **定義** 成 `*(a + i)`。所以下面四種寫法完全一樣：

```cpp
int c[3] = {7, 8, 9};
cout << c[2] << *(c + 2) << *(2 + c) << 2[c] << '\n';   // 輸出：9999
```

因為加法可以交換，`2[c]`（也就是 `*(2 + c)`）也是合法的 —— 這只是冷知識，**千萬不要這樣寫**。

## 2.3 C 風格字串 (C-string)

**是什麼**：以 `'\0'`（值為 0 的字元，叫做 **空字元 null terminator**）結尾的 `char` 陣列。

```cpp
const char* s = "hello";       // 實際佔 6 bytes：'h' 'e' 'l' 'l' 'o' '\0'
char buf[] = "hi";             // 陣列大小自動是 3
cout << sizeof(buf) << '\n';   // 輸出：3
```

**`strlen` 怎麼知道長度？** 從頭一個一個數到 `'\0'` 為止，所以是 `O(n)`：

```cpp
#include <cstring>
cout << strlen("hello") << '\n';   // 輸出：5（不算 '\0'）
```

**常見陷阱**：

**陷阱 1：用 `==` 比較 C 字串，比的是位址**

```cpp
char x1[] = "abc";
char x2[] = "abc";
cout << (x1 == x2) << '\n';           // 輸出：0（兩個不同的陣列，位址不同）
cout << (strcmp(x1, x2) == 0) << '\n';// 輸出：1（strcmp 比較內容，相等時回傳 0）
string s1 = "abc", s2 = "abc";
cout << (s1 == s2) << '\n';           // 輸出：1（std::string 的 == 比較內容）
```

**陷阱 2：緩衝區溢位 (Buffer Overflow)**

```cpp
char small[4];
// strcpy(small, "hello");            // ❌ 要寫 6 bytes 進 4 bytes 的陣列 → 寫出界
                                      //    這是歷史上最常見的資安漏洞來源之一
```

**陷阱 3：字串字面值是唯讀的**

```cpp
// char* bad = "hi";                  // ❌ C++11 起不允許（"hi" 的型別是 const char[3]）
const char* ok = "hi";                // ✅
// ok[0] = 'H';                       // ❌ 編譯錯誤：唯讀
char editable[] = "hi";               // ✅ 複製一份到自己的陣列，可以修改
editable[0] = 'H';
cout << editable << '\n';             // 輸出：Hi
```

**陷阱 4：忘了 '\0'**

```cpp
char no_end[3] = {'a', 'b', 'c'};     // 沒有 '\0'
// cout << no_end;                    // ❌ cout 會一直印下去，直到碰巧遇到 0 為止（讀出界）
```

**結論**：C++ 程式請用 `std::string`（第 12 課），它會自己管理長度和記憶體，`==` 比較內容，不會溢位。需要給舊的 C 函式用時，用 `s.c_str()` 取得 `const char*`。

---

# 第三部分：const 與指標

## 3.1 兩個不同的 const

指標牽涉到 **兩個東西**：「**指標本身**」和「**指標指向的資料**」。`const` 可以加在任何一個上面：

| 寫法 | 名稱 | 能改 `*p`（指向的值）？ | 能改 `p`（指向哪裡）？ |
|---|---|---|---|
| `int* p` | 一般指標 | ✅ | ✅ |
| `const int* p`（= `int const* p`） | **指向常數的指標** (pointer to const) | ❌ | ✅ |
| `int* const p` | **常數指標** (const pointer) | ✅ | ❌ |
| `const int* const p` | 兩個都是常數 | ❌ | ❌ |

**讀法：從變數名稱開始，由右往左讀**：

```
const int* p          →  p 是一個指標(*)，指向 int，那個 int 是 const
int const* p          →  （同上）
int* const p          →  p 是 const 的、一個指標(*)、指向 int
const int* const p    →  p 是 const 的指標，指向 const 的 int
```

**簡單的記法**：`const` 在 `*` 的 **左邊** → 保護「**值**」；在 `*` 的 **右邊** → 保護「**指標本身**」。

**比喻**：
- `const int* p`：**唯讀的導覽地圖**。你可以換一張地圖看別的地方（改 `p`），但不能透過地圖去改建房子（改 `*p`）。
- `int* const p`：**焊死在某間房子的鑰匙**。可以進去改裝（改 `*p`），但這把鑰匙永遠只能開這一間（不能改 `p`）。

**四種寫法逐一示範**：

```cpp
int x = 1, y = 2;

// 1. 一般指標：兩個都能改
int* p1 = &x;
*p1 = 10;                // ✅
p1 = &y;                 // ✅

// 2. 指向常數的指標：不能透過它改值，但能改指向
const int* p2 = &x;
// *p2 = 20;             // ❌ error: assignment of read-only location '*p2'
p2 = &y;                 // ✅ 改指向 y
cout << *p2 << '\n';     // 輸出：2
x = 30;                  // ✅ 注意：x 本身不是 const，直接改 x 是可以的
                         //    const int* 只是「不能透過這個指標改」

// 3. 常數指標：能改值，但不能改指向
int* const p3 = &x;
*p3 = 40;                // ✅
// p3 = &y;              // ❌ error: assignment of read-only variable 'p3'
cout << x << '\n';       // 輸出：40

// 4. 兩個都不能改
const int* const p4 = &x;
// *p4 = 50;             // ❌
// p4 = &y;              // ❌
cout << *p4 << '\n';     // 輸出：40
```

**`int* const` 必須在宣告時初始化**（之後就不能再改它指向哪裡了）：

```cpp
// int* const p5;        // ❌ error: uninitialized const 'p5'
```

## 3.2 const 正確性 (Const Correctness) 與函式參數

`const` 指標最重要的用途是 **函式參數**：讓呼叫者一看宣告就知道「這個函式會不會改我的資料」。

```cpp
size_t my_strlen(const char* s) {        // 承諾：我只讀不改
    size_t n = 0;
    while (s[n] != '\0') n++;
    // s[0] = 'X';                       // ❌ 編譯器會阻止我不小心修改
    return n;
}
void fill(int* arr, int n, int v) {      // 沒有 const：表示會修改
    for (int i = 0; i < n; i++) arr[i] = v;
}

int data[3];
fill(data, 3, 7);
cout << data[0] << data[2] << ' ' << my_strlen("abcd") << '\n';   // 輸出：77 4
```

**轉換規則**：

```cpp
int z = 1;
const int cz = 2;

int* a = &z;
const int* b = a;          // ✅ int* → const int*：加上限制，安全
// int* c = b;             // ❌ const int* → int*：拿掉限制，不安全
// int* d = &cz;           // ❌ 不能用一般指標指向 const 變數
const int* e = &cz;        // ✅
```

**比喻**：把房子的鑰匙換成「只能看不能動」的參觀證很安全；但把參觀證升級成能動的鑰匙，必須經過特別批准（`const_cast`，第 01 課）。

---

# 第四部分：指標的指標與二維陣列

## 4.1 指標的指標 (Pointer to Pointer)

**是什麼**：指向「**另一個指標**」的指標。

**比喻**：一張紙條寫著「另一張紙條放在哪個抽屜」，那張紙條才寫著房子的地址。

```cpp
int x = 5;
int* p = &x;          // p 指向 x
int** pp = &p;        // pp 指向 p

cout << **pp << '\n'; // 解參考兩次：pp → p → x → 輸出：5
**pp = 10;            // 透過兩層間接修改 x
cout << x << '\n';    // 輸出：10
cout << (*pp == p) << '\n';   // *pp 就是 p → 輸出：1
```

```
pp ──▶ p ──▶ x
       (int*)  (int = 10)
```

### 用途 1：讓函式修改「呼叫者的指標」

```cpp
// 想讓函式幫你配置記憶體，並把指標交給你
void alloc_bad(int* q) { q = new int(42); }        // ❌ 改的是指標的複製品，呼叫者的指標沒變（還洩漏記憶體）
void alloc_c(int** qq) { *qq = new int(42); }      // C 風格：傳指標的位址
void alloc_cpp(int*& q) { q = new int(42); }       // C++ 風格：傳指標的參考（比較好讀）

int* p1 = nullptr;
alloc_bad(p1);
cout << (p1 == nullptr) << '\n';    // 輸出：1（還是空的）

int* p2 = nullptr;
alloc_c(&p2);
cout << *p2 << '\n';                // 輸出：42

int* p3 = nullptr;
alloc_cpp(p3);
cout << *p3 << '\n';                // 輸出：42
delete p2;
delete p3;
```

這跟第 04 課的 `swap_bad` 是同一個道理：**要修改呼叫者的某個變數，就要傳它的參考（或位址）** —— 只是這次那個「變數」本身是一個指標。DS 路線第 08 課 BST 的 `insert(Node*& t, int x)` 就是用這個技巧。

### 用途 2：動態二維陣列（下一節）

## 4.2 動態二維陣列（C05 題）

**問題**：二維陣列的大小要執行時才知道（`int a[r][c]` 的 `r`、`c` 必須是編譯期常數）。

### 做法 1：指標陣列（每一列各自配置）

```cpp
int rows = 3, cols = 4;
long long** a = new long long*[rows];      // ① 配置一個陣列，存放「每一列的指標」
for (int i = 0; i < rows; i++)
    a[i] = new long long[cols]();          // ② 每一列各自配置；() 代表全部初始化為 0

a[1][2] = 7;                               // a[1] 是第 1 列的指標，[2] 再取第 2 個
cout << a[1][2] << ' ' << a[0][0] << '\n'; // 輸出：7 0

for (int i = 0; i < rows; i++) delete[] a[i];   // 釋放：順序和配置相反
delete[] a;
```

```
a ──▶ [ ● ] ──▶ [ 0 0 0 0 ]       ← 每一列在記憶體中可能不相鄰
      [ ● ] ──▶ [ 0 0 7 0 ]
      [ ● ] ──▶ [ 0 0 0 0 ]
```

**優點**：`a[i][j]` 的寫法很自然；每一列的長度可以不同（鋸齒陣列 jagged array）。
**缺點**：要 `new` 很多次、`delete` 很多次；每一列分散在記憶體各處，對快取不友善。

### 🔍 做法 2：一整塊連續記憶體

```cpp
int rows2 = 3, cols2 = 4;
long long* m = new long long[rows2 * cols2]();      // 只配置一次
auto at = [&](int i, int j) -> long long& { return m[i * cols2 + j]; };   // 自己算索引
at(1, 2) = 7;
cout << at(1, 2) << ' ' << m[1 * 4 + 2] << '\n';    // 輸出：7 7
delete[] m;                                         // 只釋放一次
```

**優點**：只要 `new` 一次、`delete` 一次；記憶體連續，快取友善，通常更快。
**實務上**：直接用 `vector<vector<long long>> a(rows, vector<long long>(cols))`，或 `vector<long long> m(rows * cols)` 搭配 `m[i * cols + j]`，完全不用自己管理記憶體。

## 4.3 內建二維陣列的記憶體排列

```cpp
int b[3][4];      // 3 列 4 行
```

在記憶體中是 **一整塊連續的 12 個 int**，**一列接一列** 排列，這叫 **列優先 (row-major)**：

```
b[0][0] b[0][1] b[0][2] b[0][3] | b[1][0] b[1][1] b[1][2] b[1][3] | b[2][0] ...
←───────── 第 0 列 ──────────→   ←───────── 第 1 列 ──────────→
```

```cpp
int b[3][4];
cout << &b[0][3] + 1 << ' ' << &b[1][0] << '\n';   // 兩個位址相同：第 0 列的尾端緊接著第 1 列的開頭
cout << sizeof(b) << ' ' << sizeof(b[0]) << '\n';   // 輸出：48 16（整個陣列 / 一列）
```

**影響效能**：外層迴圈跑「列」、內層迴圈跑「行」，存取的記憶體才是連續的：

```cpp
static int m[2000][2000];
long long s = 0;
for (int i = 0; i < 2000; i++)          // ✅ 連續存取：m[i][0], m[i][1], m[i][2] ...
    for (int j = 0; j < 2000; j++) s += m[i][j];
for (int j = 0; j < 2000; j++)          // ❌ 跳著存取：m[0][j], m[1][j], m[2][j] ... 每次跳 8000 bytes
    for (int i = 0; i < 2000; i++) s += m[i][j];
```

大陣列時，第二種寫法可能慢好幾倍，因為每次存取都跳到很遠的地方，CPU 快取幾乎派不上用場。

**傳二維陣列給函式**：除了第一維，其他維度的大小都要寫出來（編譯器要知道「一列多長」才能算位址）：

```cpp
int total(int arr[][4], int rows) {          // 第二維的 4 一定要寫
    int s = 0;
    for (int i = 0; i < rows; i++) for (int j = 0; j < 4; j++) s += arr[i][j];
    return s;
}
int g[2][4] = {{1, 2, 3, 4}, {5, 6, 7, 8}};
cout << total(g, 2) << '\n';                 // 輸出：36
```

---

# 第五部分：參考 (Reference)

## 5.1 參考是別名

**是什麼**：參考是一個 **已經存在的物件的另一個名字**。對參考做任何事，就是對原本的物件做。參考 **不是** 一個新的物件。

**比喻**：「小明」和他的綽號「阿明」。叫「阿明」去洗碗，洗碗的就是小明。

```cpp
int x = 1;
int& r = x;               // r 是 x 的別名
r = 5;                    // 就是 x = 5
cout << x << '\n';        // 輸出：5
x++;
cout << r << '\n';        // 輸出：6
cout << (&r == &x) << '\n';   // 位址完全相同 → 輸出：1
```

### 參考的三條規則

**規則 1：一定要初始化**

```cpp
// int& r1;               // ❌ error: 'r1' declared as reference but not initialized
```

別名一定要「是誰的別名」，不能先取好綽號再決定是誰。

**規則 2：不能改綁到別的物件**

```cpp
int a = 1, b = 2;
int& ra = a;
ra = b;                   // ⚠️ 不是讓 ra 改成 b 的別名！而是把 b 的值指定給 a
cout << a << ' ' << b << '\n';   // 輸出：2 2
b = 99;
cout << ra << '\n';       // 輸出：2（ra 還是 a 的別名，不受 b 影響）
```

**規則 3：沒有「空參考」**

參考一定綁著某個物件，**不需要（也沒辦法）檢查是不是空的**。這也是它比指標安全的原因。

## 5.2 參考的用途

**用途 1：函式參數（最常見，第 04 課）**

```cpp
void double_it(int& n) { n *= 2; }
int v = 21;
double_it(v);
cout << v << '\n';        // 輸出：42
```

**用途 2：範圍 for 修改元素（第 03 課）**

```cpp
vector<int> nums = {1, 2, 3};
for (int& n : nums) n *= 10;
cout << nums[2] << '\n';  // 輸出：30
```

**用途 3：幫很長的運算式取短名字**

```cpp
vector<vector<int>> grid(3, vector<int>(3, 0));
int& cell = grid[1][2];   // 之後用 cell 就好，不用一直寫 grid[1][2]
cell = 5;
cell += 3;
cout << grid[1][2] << '\n';   // 輸出：8
```

**用途 4：函式回傳參考，讓呼叫者可以修改（例如 `vector::operator[]`）**

```cpp
int arr[3] = {0, 0, 0};
int& at(int i) { return arr[i]; }
at(1) = 7;                // 能放在 = 左邊，因為回傳的是參考
cout << arr[1] << '\n';   // 輸出：7
```

## 5.3 指標 vs 參考

| | 指標 `T*` | 參考 `T&` | 範例 |
|---|---|---|---|
| 可以是空的 | ✅ `nullptr` | ❌ | 「找不到」時回傳 `nullptr` |
| 可以改指向別的物件 | ✅ `p = &y;` | ❌ | 走訪串列 `p = p->next` 只能用指標 |
| 一定要初始化 | 否（但應該要） | **是** | |
| 存取語法 | `*p`、`p->m` | 直接用 `r`、`r.m` | 參考比較好讀 |
| 指標運算 | ✅ `p + 1` | ❌ | 走訪陣列 |
| 能放進容器 | ✅ `vector<T*>` | ❌（要用 `reference_wrapper`） | |
| 本身佔記憶體 | 8 bytes | 通常不另外佔（編譯器實作） | |

**例：走訪鏈結串列只能用指標**（因為要不斷「改指向」）

```cpp
struct Node { int val; Node* next; };
Node n3{3, nullptr}, n2{2, &n3}, n1{1, &n2};
for (Node* p = &n1; p != nullptr; p = p->next)   // p 一直改指向下一個節點
    cout << p->val;
cout << '\n';                                     // 輸出：123
```

**怎麼選**：
- **能用參考就用參考**（比較安全：不會是空的、不會指錯地方）。
- 需要「**可以沒有**」、需要 **改指向**、需要 **指標運算**、要 **存進容器** 時，才用指標。

🔍 **參考在底層通常就是用指標實作的**，只是編譯器幫你自動加上 `*`，並禁止危險的操作（不能是空的、不能改指向、不能做運算）。

## 5.4 const 參考可以綁定暫時物件

```cpp
// int& r1 = 5;                 // ❌ 非 const 參考不能綁定右值（暫時的值）
const int& r2 = 5;              // ✅
const string& s = string("hi") + "!";   // ✅
cout << r2 << ' ' << s << '\n'; // 輸出：5 hi!
```

**生命週期延長 (lifetime extension)**：暫時物件原本在這一行結束就會被銷毀，但 **直接綁定到 const 參考** 時，它的生命會被延長到 **參考的作用域結束**。

這就是為什麼 `void f(const string& s)` 可以接受 `f("hello")`：編譯器建立一個暫時的 `string`，綁定到 `s`，在函式呼叫期間都有效。

**限制**：只有「**直接綁定**」才會延長。透過函式回傳的參考不會延長：

```cpp
const string& first(const string& a) { return a; }
const string& bad = first(string("temp"));   // ❌ 暫時的 string 在這一行結束就銷毀了
                                             //    bad 是懸空參考（第 04 課 2.7）
```

## 5.5 🔍 右值參考 (Rvalue Reference) 預告

C++11 加入了 `T&&`，**只能綁定右值**（快要消失的暫時物件）：

```cpp
void take(int& x)  { cout << "lvalue\n"; }
void take(int&& x) { cout << "rvalue\n"; }
int k = 5;
take(k);             // 輸出：lvalue（k 有名字，是左值）
take(5);             // 輸出：rvalue
take(k + 1);         // 輸出：rvalue（暫時的值）
take(std::move(k));  // 輸出：rvalue（std::move 把 k 轉成右值）
```

它是 **移動語意** 的基礎：既然這個物件馬上要消失了，就可以直接 **偷走** 它的資源（例如 `string` 內部的字元陣列），不用複製。第 06 課詳細說明。

---

# 第六部分：指標錯誤大全

每一種錯誤的範例都用註解標出「出事的那一行」。這些都是 **未定義行為**：可能當掉，也可能「看起來正常」—— 後者更可怕，因為 bug 會在之後莫名其妙地出現。

### 錯誤 1：解參考空指標 (Null Dereference)

```cpp
int* p = nullptr;
// cout << *p;         // ❌ 讀取位址 0 → 當掉（SIGSEGV）
```

**避免**：使用前檢查 `if (p)`；能用參考就用參考。

### 錯誤 2：野指標 (Wild Pointer)

```cpp
int* p;                // 沒有初始化
// *p = 5;             // ❌ 寫到隨機的位置
```

**避免**：宣告時一律初始化（`= nullptr` 或指向某個東西）。

### 錯誤 3：懸空指標 (Dangling Pointer) —— 指向已經離開作用域的變數

```cpp
int* p;
{
    int temp = 42;
    p = &temp;
}                      // temp 在這裡被銷毀了
// cout << *p;         // ❌ p 指向已經不存在的變數
```

**避免**：指標不要活得比它指向的東西久；不要回傳區域變數的位址。

### 錯誤 4：釋放後使用 (Use-after-free)

```cpp
int* p = new int(5);
delete p;
// *p = 10;            // ❌ 記憶體已經還給系統了，可能已經被別人拿去用
p = nullptr;           // ✅ 好習慣：delete 之後設成 nullptr，之後誤用會立刻當掉（比默默出錯好）
```

### 錯誤 5：重複釋放 (Double Free)

```cpp
int* a = new int(1);
int* b = a;            // 兩個指標指向同一塊記憶體
delete a;
// delete b;           // ❌ 同一塊記憶體 delete 兩次 → 當掉或破壞記憶體管理
```

### 錯誤 6：記憶體洩漏 (Memory Leak)

```cpp
void leak() {
    int* p = new int[1000];
    // 忘了 delete[] p;
}                      // p 消失了，但那 1000 個 int 永遠不會被釋放
for (int i = 0; i < 1000000; i++) leak();   // 每次洩漏 4 KB → 總共 4 GB
```

### 錯誤 7：越界存取 (Out of Bounds)

```cpp
int arr[5];
// arr[5] = 1;         // ❌ 寫到陣列後面的記憶體（可能是別的變數）
int* p = arr;
// p[-1] = 1;          // ❌ 寫到陣列前面
```

### 錯誤 8：new / delete 配錯

```cpp
int* one = new int(5);
int* many = new int[10];
delete one;            // ✅ new 配 delete
delete[] many;         // ✅ new[] 配 delete[]
// delete many;        // ❌ new[] 配 delete：未定義行為
```

### 怎麼抓？

```bash
python3 judge.py test c5 --debug     # 用 AddressSanitizer 編譯執行
```

AddressSanitizer 會告訴你錯誤的 **種類**（`heap-use-after-free`、`heap-buffer-overflow`、`double-free`、`memory leak`……）和 **行號**。

### 怎麼避免？

第 06 課的 **RAII** 和 **智慧指標**：讓物件自己負責釋放記憶體，就不會忘記（洩漏）、不會重複（double free）、不會在別人釋放後還在用（use-after-free）。**現代 C++ 程式裡幾乎不應該出現裸的 `new` / `delete`**。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 位址 | Address | 記憶體的編號 | 1.1 |
| 取址運算子 | Address-of Operator `&` | 拿到變數的位址 | 1.1 |
| 指標 | Pointer | 存放位址的變數 | 1.2 |
| 解參考 | Dereference `*` | 照著位址拿值 | 1.2 |
| 箭頭運算子 | Arrow Operator `->` | `(*p).m` 的簡寫 | 1.2 |
| 通用指標 | void* | 可以指向任何型別，不能直接解參考 | 1.3 |
| 空指標 | Null Pointer | 不指向任何東西（`nullptr`） | 1.4 |
| 野指標 | Wild Pointer | 沒初始化的指標 | 1.5 |
| 指標運算 | Pointer Arithmetic | `p + 1` 移動一個元素 | 2.1 |
| 尾後指標 | One-past-the-end | 最後一個元素的下一個位置 | 2.1 |
| 陣列退化 | Array Decay | 陣列自動轉成指向首元素的指標 | 2.2 |
| C 風格字串 | C-string | 以 `'\0'` 結尾的 char 陣列 | 2.3 |
| 空字元 | Null Terminator `'\0'` | C 字串的結尾標記 | 2.3 |
| 緩衝區溢位 | Buffer Overflow | 寫超過陣列的範圍 | 2.3 |
| 指向常數的指標 | Pointer to const | 不能透過它改值 | 3.1 |
| 常數指標 | Const Pointer | 不能改指向 | 3.1 |
| 指標的指標 | Pointer to Pointer | 指向另一個指標 | 4.1 |
| 列優先 | Row-major | 二維陣列一列接一列存放 | 4.3 |
| 參考 | Reference | 物件的別名 | 5.1 |
| 生命週期延長 | Lifetime Extension | const 參考讓暫時物件活久一點 | 5.4 |
| 右值參考 | Rvalue Reference `T&&` | 只綁定暫時物件，移動語意的基礎 | 5.5 |
| 懸空指標 | Dangling Pointer | 指向已經不存在的物件 | 6 |
| 釋放後使用 | Use-after-free | delete 之後還在用 | 6 |
| 重複釋放 | Double Free | 同一塊記憶體 delete 兩次 | 6 |
| 記憶體洩漏 | Memory Leak | new 了卻沒有 delete | 6 |

---

# 習題

### 題 1：預測輸出

```cpp
int a[] = {10, 20, 30, 40};
int* p = a + 1;
cout << *p << ' ' << *(p + 2) << ' ' << p[-1] << ' ' << (p + 2) - p;
```

### 題 2：預測輸出

```cpp
int x = 1, y = 2;
int* p = &x;
int& r = x;
r = y;
*p += 10;
cout << x << ' ' << y;
```

### 題 3：哪幾行會編譯錯誤？

```cpp
int x = 1, y = 2;
const int* a = &x;
int* const b = &x;
*a = 3;      // ①
a = &y;      // ②
*b = 3;      // ③
b = &y;      // ④
```

### 題 4：預測輸出（64 位元系統）

```cpp
void f(int arr[10]) { cout << sizeof(arr) << ' '; }
int main() {
    int a[10];
    cout << sizeof(a) << ' ';
    f(a);
}
```

### 題 5：找出所有錯誤

```cpp
int* make() {
    int local = 5;
    return &local;
}
int main() {
    int* p = new int[5];
    int* q = make();
    delete p;
    p[0] = 1;
}
```

### 題 6：`int* a, b;` 中，`a` 和 `b` 的型別各是什麼？

### 題 7：為什麼下面兩個迴圈的速度可能差很多？哪個比較快？

```cpp
static int m[5000][5000];
// A
for (int i = 0; i < 5000; i++) for (int j = 0; j < 5000; j++) m[i][j]++;
// B
for (int j = 0; j < 5000; j++) for (int i = 0; i < 5000; i++) m[i][j]++;
```

### 題 8：寫一個函式，把傳入的指標設成 `nullptr`。要用什麼參數型別？

### 題 9：預測輸出

```cpp
char s1[] = "cat";
const char* s2 = "cat";
string s3 = "cat";
cout << sizeof(s1) << ' ' << strlen(s2) << ' ' << s3.size() << ' ' << (s3 == s2);
```

### 題 10：預測輸出

```cpp
int v[] = {5, 6, 7};
int* p = v;
cout << *p++ << ' ';
cout << *p << ' ';
cout << (*p)++ << ' ';
cout << v[1];
```

---

# 習題解答

**題 1**：`20 40 10 2`。`p` 指向 `a[1]`；`*(p+2)` 是 `a[3]`；`p[-1]` 是 `a[0]`（往前一個，合法因為還在陣列內）；`(p + 2) - p` 兩個指標差 2 個元素。

**題 2**：`12 2`。`r = y` **不是改綁**，是把 `y` 的值（2）指定給 `x`；接著 `*p += 10`，`p` 指向 `x`，所以 `x = 12`。`y` 沒變。

**題 3**：① 和 ④。`a` 是指向常數的指標，不能改 `*a`；`b` 是常數指標，不能改 `b` 本身。

**題 4**：`40 8`。`sizeof(a)` 是整個陣列（10 × 4）；函式參數 `int arr[10]` 其實是 `int*`，大小是 8。

**題 5**：
1. `make` 回傳區域變數的位址 → `q` 是 **懸空指標**。
2. `new int[5]` 要用 `delete[]`，不能用 `delete`。
3. `delete` 之後還寫入 `p[0]` → **use-after-free**。

**題 6**：`a` 是 `int*`，`b` 是 **`int`**。`*` 只屬於緊接著的那個變數名稱。

**題 7**：**A 比較快**。二維陣列是 **列優先** 存放，A 依序存取連續的記憶體，CPU 快取能發揮作用；B 每次跳 5000 個 `int`（20 KB），幾乎每次都要重新從主記憶體讀取。實測可能差好幾倍。

**題 8**：參數要能修改 **呼叫者的指標本身**，所以用 **指標的參考** `int*&`（或 C 風格的 `int**`）：

```cpp
void clear_ptr(int*& p) { p = nullptr; }
```

**題 9**：`4 3 3 1`。`s1` 是陣列，`sizeof` 包含結尾的 `'\0'`；`strlen` 不算 `'\0'`；`string` 的 `==` 可以和 C 字串比較內容。

**題 10**：`5 6 6 7`。
- `*p++` 是 `*(p++)`：先用舊的 `p`（指向 5）解參考得到 5，然後 `p` 移到 `v[1]`。
- `*p` 是 6。
- `(*p)++` 回傳 6（舊值），然後 `v[1]` 變成 7。
- `v[1]` 是 7。
