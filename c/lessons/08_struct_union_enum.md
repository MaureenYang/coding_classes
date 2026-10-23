# 08. struct、union、enum

> 程式練習：`CL06 學生成績排名`（`CL04`、`CL05`、`CL10` 也都用 `struct` 組織資料）
>
> 先備知識：第 05 課「指標」、第 07 課「動態記憶體」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | struct 基本用法 | 定義、初始化、存取成員、複製 |
| 第二部分 | struct 與函式、指標 | 傳值 vs 傳指標、`->`、`typedef`、自我參考的結構 |
| 第三部分 | 🔍 記憶體配置 | 對齊、填充 (padding)、`sizeof`、`offsetof`、彈性陣列成員 |
| 第四部分 | enum | 具名的整數常數、搭配 `switch`、名字對照表 |
| 第五部分 | union | 共用同一塊記憶體、標記聯合 (tagged union) |
| 第六部分 | 🔍 位元欄位與複合字面值 | `unsigned x : 3`、`(struct Point){1, 2}` |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際用 `gcc -std=c11` 在 x86-64 Linux 上編譯執行的結果。標 🔍 的是深入內容。

---

# 第一部分：struct 基本用法

## 1.1 為什麼需要 struct？

**問題**：要存 100 位學生的名字、分數、年齡。只用陣列的話：

```c
char names[100][21];
int scores[100];
int ages[100];
```

三個陣列靠「同一個索引」才連在一起：排序時要同時交換三個陣列、傳給函式要傳三個參數，很容易漏掉一個。

**解法**：`struct`（結構）把 **相關的資料綁成一個新型別**：

```c
struct Student {
    char name[21];
    int score;
    int age;
};
struct Student list[100];                 /* 一個陣列，每個元素都有三個欄位 */
```

**比喻**：`struct` 就像一張 **表格的格式**（名字欄、分數欄、年齡欄）；每宣告一個變數，就是印出一張空白表格來填。

## 1.2 定義與初始化

```c
struct Point {                            /* 定義型別：struct Point */
    int x;                                /* 成員 (member)，也叫欄位 (field) */
    int y;
};                                        /* ⚠️ 結尾的分號不能漏 */

struct Point p = {3, 4};                  /* 依照成員順序初始化 */
printf("%d %d\n", p.x, p.y);              // 輸出：3 4
```

**指定初始化 (designated initializer，C99)**：寫出成員名字，沒寫到的成員自動設成 0：

```c
struct Point q = {.y = 10};
printf("%d %d\n", q.x, q.y);              // 輸出：0 10
```

指定初始化更清楚，成員順序改了也不會出錯，建議多用。

**常見錯誤**：

```c
struct Point p;
p = {3, 4};                               /* ❌ 編譯錯誤：大括號只能用在「初始化」，不能用在賦值 */
p = (struct Point){3, 4};                 /* ✅ 複合字面值（第六部分） */
```

## 1.3 複製：`=` 會複製每一個成員

```c
struct Point r = p;                       /* 整個結構複製一份 */
r.x = 99;
printf("%d %d\n", p.x, r.x);              // 輸出：3 99（p 沒有被改到）
```

和陣列不一樣：**陣列不能用 `=` 複製，但結構可以**，就算結構裡有陣列也一樣，陣列會整個被複製。

### ⚠️ 淺複製 (Shallow Copy)

如果成員是 **指標**，`=` 只複製指標本身（位址），**不會** 複製它指向的資料：

```c
typedef struct { char name[20]; int age; } Person;    /* 名字存在結構裡 */
typedef struct { char *name;    int age; } PersonP;   /* 只存指標 */

Person b1 = {"Bob", 30};
Person b2 = b1;
b2.name[0] = 'R';
printf("%s %s\n", b1.name, b2.name);      // 輸出：Bob Rob（各自一份）

char buf[] = "Bob";
PersonP a1 = {buf, 30};
PersonP a2 = a1;                          /* a1.name 和 a2.name 指向同一個 buf */
a2.name[0] = 'R';
printf("%s %s\n", a1.name, a2.name);      // 輸出：Rob Rob（兩個都變了！）
```

如果 `name` 是 `malloc` 來的，兩個結構各自 `free` 一次就是 **double free**（第 07 課）。需要「深複製」時要自己寫函式，重新配置並複製資料。

## 1.4 不能直接比較

```c
if (p == r) { }                           /* ❌ 編譯錯誤：struct 不能用 == 比較 */
if (p.x == r.x && p.y == r.y) { }         /* ✅ 逐一比較成員 */
```

🔍 為什麼不能用 `memcmp(&p, &r, sizeof p)`？結構裡可能有 **填充位元組**（第三部分），內容是不確定的，兩個「成員都相同」的結構，`memcmp` 仍可能說不相等。

## 1.5 結構陣列

```c
Person class_[3] = {{"Amy", 20}, {"Bob", 22}, {"Cat", 19}};
int oldest = 0;
for (int i = 1; i < 3; i++)
    if (class_[i].age > class_[oldest].age) oldest = i;
printf("%s\n", class_[oldest].name);      // 輸出：Bob
```

`class_[i].age`：先用 `[i]` 取出第 `i` 個結構，再用 `.age` 取成員。

---

# 第二部分：struct 與函式、指標

## 2.1 typedef：省略 `struct` 這個字

在 C 裡，型別的全名是 `struct Point`，每次都要寫 `struct`（C++ 不用）。`typedef` 可以取一個別名：

```c
typedef struct Point Point;               /* 之後 Point 就等於 struct Point */

typedef struct {                          /* 常見寫法：定義和 typedef 一起做 */
    char name[20];
    int age;
} Person;

Person amy = {"Amy", 20};                 /* 不用寫 struct */
```

## 2.2 傳給函式：傳值 vs 傳指標

```c
void birthday_v(Person p) { p.age++; }    /* 傳值：改的是複本 */
void birthday(Person *p)  { p->age++; }   /* 傳指標：改的是本人 */

birthday_v(amy);
printf("%d\n", amy.age);                  // 輸出：20（沒變）
birthday(&amy);
printf("%d\n", amy.age);                  // 輸出：21
```

| 傳法 | 寫法 | 什麼時候用 |
|---|---|---|
| 傳值 | `void f(Person p)` | 結構很小（例如兩個 `int` 的 `Point`），而且不需要修改 |
| 傳指標 | `void f(Person *p)` | 要修改結構 |
| 傳 `const` 指標 | `void f(const Person *p)` | 結構大、只讀不改：**不用複製整個結構**，又保證不會改到 |

傳值會 **複製整個結構**。結構很大（例如裡面有 1000 個元素的陣列）時，每次呼叫都要複製一次，很浪費。所以實務上大部分的函式都傳指標。

## 2.3 箭頭運算子 `->`

透過指標存取成員：`p->age` 就是 `(*p).age` 的簡寫。

```c
Person *pp = &amy;
printf("%s %d\n", pp->name, (*pp).age);   // 輸出：Amy 21
```

**常見錯誤**：

```c
*pp.age                                   /* ❌ . 的優先順序比 * 高 → 變成 *(pp.age)，編譯錯誤 */
(*pp).age                                 /* ✅ 要加括號 */
pp->age                                   /* ✅ 最常用 */
```

**記法**：左邊是 **結構本身** 用 `.`，左邊是 **指標** 用 `->`。

## 2.4 函式回傳結構

結構可以當回傳值（會複製一份回去）：

```c
struct Point add(struct Point a, struct Point b) {
    return (struct Point){a.x + b.x, a.y + b.y};
}

struct Point s = add(p, (struct Point){1, 1});
printf("%d %d\n", s.x, s.y);              // 輸出：4 5
```

這是 C 裡「一次回傳多個值」的方法之一（另一個是傳指標進去讓函式寫入，第 05 課）。

## 2.5 自我參考的結構

**鏈結串列的節點** 要包含「指向另一個節點的指標」：

```c
typedef struct Node {                     /* ⚠️ 這裡一定要寫標籤名字 Node */
    int value;
    struct Node *next;                    /* 這時 typedef 還沒完成，只能寫 struct Node */
} Node;

Node n3 = {3, NULL}, n2 = {2, &n3}, n1 = {1, &n2};
for (Node *cur = &n1; cur != NULL; cur = cur->next)
    printf("%d ", cur->value);
printf("\n");                             // 輸出：1 2 3
```

**常見錯誤**：

```c
typedef struct {
    int value;
    Node *next;                           /* ❌ 編譯錯誤：Node 這個名字在這一行還不存在 */
} Node;

struct Bad {
    int value;
    struct Bad next;                      /* ❌ 結構不能包含「自己」：大小會無限大。只能包含指向自己的指標 */
};
```

## 2.6 🔍 前置宣告與不完整型別

```c
struct Tree;                              /* 前置宣告：告訴編譯器「有這個型別」，但還不知道內容 */
void tree_print(const struct Tree *t);    /* ✅ 可以宣告指標 */
// struct Tree t;                         /* ❌ 不知道大小，不能建立變數 */
```

只知道名字、不知道內容的型別叫 **不完整型別 (incomplete type)**。可以用它的指標，但不能建立變數、不能存取成員、不能 `sizeof`。第 12 課會用這個特性實作 **不透明指標**：使用者只拿得到指標，看不到結構內部。

---

# 第三部分：🔍 記憶體配置

## 3.1 對齊與填充

**問題**：下面這個結構有 `1 + 4 + 1 = 6` 個 byte 的資料，`sizeof` 卻是 12：

```c
struct A { char c; int i; char d; };
struct B { int i; char c; char d; };      /* 一樣的成員，順序不同 */
struct C { char c; double d; char e; };
struct D { double d; char c; char e; };
printf("%zu %zu %zu %zu\n", sizeof(struct A), sizeof(struct B),
       sizeof(struct C), sizeof(struct D));       // 輸出：12 8 24 16
```

**原因：對齊 (alignment)**。CPU 讀取 `int`（4 bytes）時，位址最好是 4 的倍數；讀 `double`（8 bytes）時，位址最好是 8 的倍數。所以編譯器會在成員之間插入沒用的 **填充位元組 (padding)**：

```
struct A（12 bytes）:
位移  0    1    2    3    4    5    6    7    8    9   10   11
     [ c ][ 填 ][ 填 ][ 填 ][ i  i  i  i ][ d ][ 填 ][ 填 ][ 填 ]
              ↑ i 要從 4 的倍數開始                ↑ 整體大小要是 4 的倍數（陣列中下一個元素的 i 才會對齊）

struct B（8 bytes）:
     [ i  i  i  i ][ c ][ d ][ 填 ][ 填 ]
```

用 `offsetof`（`<stddef.h>`）可以查看每個成員的位移：

```c
printf("%zu %zu %zu\n", offsetof(struct A, c), offsetof(struct A, i),
       offsetof(struct A, d));            // 輸出：0 4 8
```

**規則**：
1. 每個成員的位移是 **它自己大小（對齊需求）的倍數**。
2. 結構的總大小是 **最大成員對齊需求的倍數**。
3. 編譯器 **不會** 自動調整成員的順序。

**實用建議**：成員 **由大排到小**（`double` → `int` → `char`），填充最少。成員少的時候不必在意；當結構要存幾百萬份時（例如大陣列），差距就很可觀。

**常見錯誤**：
- 以為 `sizeof(struct)` 等於成員大小的總和。配置記憶體時 **一定用 `sizeof`**，不要自己加。
- 把結構直接 `fwrite` 到檔案、或透過網路傳送：不同編譯器 / 平台的填充可能不同，另一邊讀不回來。

## 3.2 🔍 彈性陣列成員 (Flexible Array Member，C99)

結構的 **最後一個成員** 可以是沒有寫大小的陣列，配置時再決定長度：

```c
typedef struct {
    int len;
    char data[];                          /* 彈性陣列成員：不佔 sizeof 的空間 */
} Str;

Str *st = malloc(sizeof *st + 6);         /* 結構本身 + 6 個 char */
st->len = 5;
memcpy(st->data, "hello", 6);
printf("%zu %d %s\n", sizeof(Str), st->len, st->data);   // 輸出：4 5 hello
free(st);                                 /* 一次配置、一次釋放 */
```

好處：資料和長度在同一塊連續的記憶體，只要 `malloc` / `free` 一次。很多 C 的字串函式庫和網路封包結構都用這個技巧。

---

# 第四部分：enum

## 4.1 是什麼

**是什麼**：`enum`（列舉）定義一組 **有名字的整數常數**。

**為什麼需要**：程式裡寫 `if (state == 2)`，沒人知道 2 是什麼意思（這叫「魔術數字」）。寫成 `if (state == STATE_RUNNING)` 就一目了然。

```c
enum Color { RED, GREEN, BLUE };          /* 自動從 0 開始編號：RED=0, GREEN=1, BLUE=2 */
enum Color c = GREEN;
printf("%d %d %d\n", RED, c, BLUE);       // 輸出：0 1 2
```

## 4.2 指定數值

```c
enum Http { OK = 200, NOT_FOUND = 404, ERR = 500 };
printf("%d\n", NOT_FOUND);                // 輸出：404

enum Level { LOW = 1, MID, HIGH = 10, MAX };   /* 沒指定的 = 前一個 + 1 */
printf("%d %d %d %d\n", LOW, MID, HIGH, MAX);  // 輸出：1 2 10 11
```

## 4.3 搭配 switch

```c
typedef enum { DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT } Dir;

void move(Dir d, int *x, int *y) {
    switch (d) {
        case DIR_UP:    (*y)--; break;
        case DIR_DOWN:  (*y)++; break;
        case DIR_LEFT:  (*x)--; break;
        case DIR_RIGHT: (*x)++; break;
    }
}
```

好處：用 `-Wall` 編譯時，如果 `switch` 漏了某個 enum 值，gcc 會警告 `enumeration value 'DIR_RIGHT' not handled in switch`。

## 4.4 enum 轉字串：對照表

C 沒辦法自動把 enum 值印成名字，常見的做法是一個字串陣列：

```c
static const char *COLOR_NAME[] = {
    [RED] = "red", [GREEN] = "green", [BLUE] = "blue",   /* 陣列的指定初始化 */
};
printf("%s\n", COLOR_NAME[c]);            // 輸出：green
```

## 4.5 常見錯誤：enum 只是 int

C 的 enum **沒有型別檢查**，任何整數都可以放進去：

```c
enum Color bad = 7;                       /* 編譯通過，沒有警告 */
printf("%d\n", bad);                      // 輸出：7
```

所以 `COLOR_NAME[bad]` 會越界。從外部（輸入、檔案）讀進來的值，要先檢查範圍。（C++ 的 `enum class` 就是為了修正這個問題。）

另外，enum 的名字是全域的：兩個 enum 不能有同名的成員。所以 C 的慣例是加上前綴，例如 `DIR_UP`、`COLOR_RED`。

---

# 第五部分：union

## 5.1 是什麼

**是什麼**：`union`（聯合）的所有成員 **共用同一塊記憶體**，大小等於最大的成員。同一時間只有一個成員是有效的。

```c
union Value {
    int i;                                /* 4 bytes */
    float f;                              /* 4 bytes */
    char s[8];                            /* 8 bytes */
};
union Value v;
printf("%zu\n", sizeof v);                // 輸出：8（最大成員的大小）
```

| | struct | union |
|---|---|---|
| 成員的記憶體 | 各自一塊，依序排列 | **全部重疊**，從同一個位址開始 |
| 大小 | 所有成員 + 填充 | 最大的成員 + 填充 |
| 同時有效的成員 | 全部 | 一個（最後寫入的那個） |

**為什麼需要**：一個值「可能是好幾種型別之一」時（例如 JSON 的值可能是數字、字串、陣列），用 union 只要佔最大的那種的空間，不用每種都留一份。

## 5.2 🔍 用 union 看浮點數的位元

寫入一個成員、讀另一個成員，等於把同一組位元「用另一種型別解讀」：

```c
v.f = 1.0f;
printf("%d\n", v.i);                      // 輸出：1065353216（就是 0x3F800000，1.0 的 IEEE 754 編碼）
```

C 允許這樣做（C++ 則是未定義行為）。但這依賴平台的位元表示方式，一般程式不要這樣用。

## 5.3 標記聯合 (Tagged Union)

**問題**：union 自己不知道「目前哪個成員有效」。

**解法**：放進 struct，再加一個 enum 欄位記錄目前的種類：

```c
typedef enum { SHAPE_CIRCLE, SHAPE_RECT } ShapeKind;

typedef struct {
    ShapeKind kind;                       /* 標記：目前是哪一種 */
    union {                               /* 匿名 union（C11）：直接用 s.circle 存取 */
        struct { double r; } circle;
        struct { double w, h; } rect;
    };
} Shape;

double area(const Shape *s) {
    switch (s->kind) {
        case SHAPE_CIRCLE: return 3.14159 * s->circle.r * s->circle.r;
        case SHAPE_RECT:   return s->rect.w * s->rect.h;
    }
    return 0;
}

Shape sh[2] = {
    {.kind = SHAPE_CIRCLE, .circle = {.r = 1.0}},
    {.kind = SHAPE_RECT,   .rect = {.w = 2, .h = 3}},
};
for (int i = 0; i < 2; i++) printf("%.2f\n", area(&sh[i]));
// 輸出：
// 3.14
// 6.00
```

這是 C 裡實作「多型」最常見的方法：直譯器裡的「值」、編譯器的語法樹節點、網路訊息……都是這樣設計的。（C++ 的 `std::variant`、Rust 的 `enum` 就是語言內建的標記聯合。）

**常見錯誤**：改了 union 的成員，卻忘了更新 `kind` → 之後用錯誤的成員解讀資料。

---

# 第六部分：🔍 位元欄位與複合字面值

## 6.1 位元欄位 (Bit Field)

指定成員只佔幾個 **位元**，把好幾個小欄位擠在一起：

```c
struct Flags {
    unsigned int read  : 1;               /* 只佔 1 個 bit：0 或 1 */
    unsigned int write : 1;
    unsigned int exec  : 1;
    unsigned int mode  : 4;               /* 4 個 bit：0 ~ 15 */
};
struct Flags f = {.read = 1, .exec = 1, .mode = 5};
printf("%u %u %u %u %zu\n", f.read, f.write, f.exec, f.mode, sizeof f);
// 輸出：1 0 1 5 4（7 個 bit 擠在一個 4 bytes 的 unsigned int 裡）
```

**常見錯誤**：值超過範圍會被截斷（只留下低位的 bit）：

```c
f.mode = 20;                              /* 20 = 10100（二進位），只留下低 4 位 0100 */
printf("%u\n", f.mode);                   // 輸出：4
```

gcc 會警告 `unsigned conversion from 'int' to 'unsigned char:4' changes value from '20' to '4'`。

**限制**：不能取位元欄位的位址（`&f.read` 是錯誤）；位元的排列順序由編譯器決定，所以不適合用來解析檔案格式。大部分情況用第 02 課的位元運算（`flags & READ`）就夠了。

## 6.2 複合字面值 (Compound Literal，C99)

`(型別){初始值}` 會建立一個 **沒有名字的物件**：

```c
struct Point s = add(p, (struct Point){1, 1});   /* 直接傳一個臨時的結構 */

int *arr = (int[]){5, 6, 7};              /* 沒有名字的陣列 */
printf("%d\n", arr[2]);                   // 輸出：7
```

**生命週期**：和寫在同一個區塊的區域變數一樣，離開區塊就失效（所以 **不能回傳它的位址**）。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 結構 | Struct | 把多個欄位綁成一個新型別 | 1.1 |
| 成員 / 欄位 | Member / Field | 結構裡的每一個變數 | 1.2 |
| 指定初始化 | Designated Initializer | `{.y = 10}`，用名字指定 | 1.2 |
| 淺複製 | Shallow Copy | 只複製指標，不複製指向的資料 | 1.3 |
| 型別別名 | typedef | 幫型別取另一個名字 | 2.1 |
| 箭頭運算子 | Arrow Operator `->` | 透過指標存取成員 | 2.3 |
| 不完整型別 | Incomplete Type | 只知道名字、不知道內容的型別 | 2.6 |
| 對齊 | Alignment | 資料的位址要是某個數的倍數 | 3.1 |
| 填充 | Padding | 為了對齊插入的無用 byte | 3.1 |
| 彈性陣列成員 | Flexible Array Member | 結構最後一個沒有大小的陣列 | 3.2 |
| 列舉 | Enum | 一組有名字的整數常數 | 4.1 |
| 聯合 | Union | 所有成員共用同一塊記憶體 | 5.1 |
| 標記聯合 | Tagged Union | union + 記錄目前種類的欄位 | 5.3 |
| 位元欄位 | Bit Field | 指定成員只佔幾個 bit | 6.1 |
| 複合字面值 | Compound Literal | `(型別){...}` 建立無名物件 | 6.2 |

---

# 習題

### 題 1：預測輸出

```c
typedef struct { int a[3]; int n; } Box;
Box x = {{1, 2, 3}, 3};
Box y = x;
y.a[0] = 100;
y.n = 1;
printf("%d %d %d %d\n", x.a[0], x.n, y.a[0], y.n);
```

### 題 2：找出錯誤

```c
typedef struct {
    char name[20];
    int score;
} Student;

void set_score(Student s, int v) { s.score = v; }

int main(void) {
    Student *p = malloc(sizeof(Student));
    set_score(*p, 90);
    printf("%d\n", *p.score);
    free(p);
}
```

### 題 3：在 x86-64 上，下面兩個結構的 `sizeof` 各是多少？為什麼？

```c
struct X { char a; long long b; char c; int d; };
struct Y { long long b; int d; char a; char c; };
```

### 題 4：下面的 `make_person` 有什麼問題？

```c
typedef struct { char *name; int age; } P;

P make_person(int age) {
    char buf[32];
    snprintf(buf, sizeof buf, "user%d", age);
    return (P){buf, age};
}
```

### 題 5：預測輸出

```c
enum Fruit { APPLE = 3, BANANA, CHERRY = 1, DATE };
printf("%d %d %d %d\n", APPLE, BANANA, CHERRY, DATE);
```

### 題 6：用標記聯合設計一個「值」型別 `Value`，可以是 `int`、`double` 或字串（`char *`）。寫出 `print_value(const Value *v)`。

### 題 7：`CL06` 的 `Student` 結構傳給 `qsort` 的比較函式時，參數型別是 `const void *`。要怎麼取出 `score` 欄位？

---

# 習題解答

**題 1**：`1 3 100 1`。`y = x` 複製了整個結構，包含裡面的陣列，所以修改 `y.a[0]` 不影響 `x`。

**題 2**：
- `set_score(Student s, ...)` 是傳值，改的是複本。應該寫成 `void set_score(Student *s, int v) { s->score = v; }`，呼叫 `set_score(p, 90)`。
- `*p.score`：`.` 優先於 `*`，變成 `*(p.score)`，編譯錯誤。應該寫 `p->score` 或 `(*p).score`。
- `malloc` 之後沒有檢查 `NULL`。

**題 3**：`struct X` 是 24，`struct Y` 是 16。
- `X`：`a` 在 0；`b` 要對齊 8 → 位移 8（填 7 bytes）；`c` 在 16；`d` 要對齊 4 → 位移 20（填 3 bytes）；結束在 24，剛好是 8 的倍數。
- `Y`：`b` 在 0；`d` 在 8；`a` 在 12；`c` 在 13；結束在 14，補到 8 的倍數 → 16。

**題 4**：`buf` 是區域陣列，函式結束後就失效了，回傳的結構裡的 `name` 是 **懸置指標**。修正：用 `malloc` 配置名字（呼叫者負責 `free`），或把結構改成 `char name[32]`，讓名字存在結構裡面。

**題 5**：`3 4 1 2`。沒有指定值的成員是「前一個 + 1」：`BANANA = APPLE + 1 = 4`、`DATE = CHERRY + 1 = 2`。

**題 6**：

```c
typedef enum { VAL_INT, VAL_DOUBLE, VAL_STR } ValueKind;

typedef struct {
    ValueKind kind;
    union {
        int i;
        double d;
        char *s;
    };
} Value;

void print_value(const Value *v) {
    switch (v->kind) {
        case VAL_INT:    printf("%d\n", v->i); break;
        case VAL_DOUBLE: printf("%g\n", v->d); break;
        case VAL_STR:    printf("\"%s\"\n", v->s); break;
    }
}
```

使用方式：`Value a = {.kind = VAL_INT, .i = 42};`、`Value b = {.kind = VAL_STR, .s = "hi"};`。

**題 7**：先把 `const void *` 轉回 `const Student *`，再用 `->`：

```c
int cmp_score(const void *a, const void *b) {
    const Student *x = a;                 /* C 裡 void * 可以直接指定給其他指標型別 */
    const Student *y = b;
    return (x->score < y->score) - (x->score > y->score);   /* 分數高的在前 */
}
```

（比較函式的細節在第 09 課。）
