# 06. 字串

> 程式練習：`CL02 自己寫 string.h`、`CL07 文字統計`
>
> 先備知識：第 04 課「陣列」、第 05 課「指標」。

**這一課分成七個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | C 字串是什麼 | `'\0'` 結尾、`sizeof` vs `strlen`、`char s[]` vs `char *s` |
| 第二部分 | 讀取字串 | `scanf("%s")` 的限制、`fgets` 讀一整行、去掉換行 |
| 第三部分 | `<string.h>` | 每一個常用函式的用法與陷阱 |
| 第四部分 | 緩衝區溢位與安全的寫法 | 為什麼 `strcpy` 危險、`snprintf`、`strncpy` 的陷阱 |
| 第五部分 | 字串與數字互轉 | `atoi` 的問題、`strtol`、`sscanf`、`snprintf` |
| 第六部分 | 字元處理與常見操作 | `<ctype.h>`、反轉、大小寫、trim、切字串 |
| 第七部分 | 字串陣列 | 二維 `char` 陣列 vs 指標陣列、排序字串 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際用 `gcc -std=c11` 編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：C 字串是什麼

## 1.1 以 '\0' 結尾的 char 陣列

**是什麼**：C 沒有字串型別。**字串就是一個 `char` 陣列，最後放一個值為 0 的字元 `'\0'`（空字元 null character）表示結束**。

```c
char s[6] = {'h', 'e', 'l', 'l', 'o', '\0'};
char t[] = "hello";              /* 簡寫：編譯器自動在最後加 '\0' */
printf("%s %s\n", s, t);         // 輸出：hello hello
```

```
t:  [ 'h' | 'e' | 'l' | 'l' | 'o' | '\0' ]
       0     1     2     3     4     5
```

**為什麼用 `'\0'`？** C 的字串函式（`printf("%s")`、`strlen`……）只拿到 **第一個字元的位址**，不知道長度。它們從頭開始一個一個讀，**讀到 `'\0'` 就停**。

**比喻**：一列火車，車廂後面掛一節「終點標誌」。函式只知道火車頭在哪，要一直往後走，看到終點標誌才知道火車有多長。

### ⚠️ 忘了 '\0' 的後果

```c
char bad[5] = {'h', 'e', 'l', 'l', 'o'};   /* 沒有 '\0' */
// printf("%s\n", bad);          // ❌ printf 會一直往後讀，直到碰巧遇到 0 → 印出亂碼或當掉
char ok[5] = "hell";             /* 4 個字元 + '\0' 剛好 5 格 */
// char tight[5] = "hello";      // ⚠️ C 允許（剛好放 5 個字元，沒有 '\0'），但這就不是字串了！
```

**規則：字串陣列的大小至少是「字元數 + 1」。**

## 1.2 sizeof vs strlen

```c
#include <string.h>
char s[20] = "hello";
printf("%zu %zu\n", sizeof s, strlen(s));    // 輸出：20 5
char t[] = "hello";
printf("%zu %zu\n", sizeof t, strlen(t));    // 輸出：6 5
```

| | `sizeof s` | `strlen(s)` |
|---|---|---|
| 意思 | 陣列佔幾個 byte | 字串有幾個字元（到 `'\0'` 之前） |
| 什麼時候算 | 編譯時 | 執行時（要一個一個數，`O(n)`） |
| 包含 `'\0'` 嗎 | 包含（整個陣列） | 不包含 |

**常見錯誤：在迴圈條件裡呼叫 `strlen`**

```c
for (size_t i = 0; i < strlen(s); i++) { ... }   /* 每一輪都重新數一次 → O(n²) */
size_t n = strlen(s);
for (size_t i = 0; i < n; i++) { ... }           /* ✅ 先算好 */
for (size_t i = 0; s[i] != '\0'; i++) { ... }    /* ✅ 或直接看 '\0' */
```

## 1.3 char s[] 和 char *s 的差別

```c
char arr[] = "hello";            /* 陣列：在堆疊上配置 6 bytes，把 "hello" 複製進來 */
const char *ptr = "hello";       /* 指標：指向唯讀記憶體裡的字串字面值 */

arr[0] = 'H';                    /* ✅ 陣列是自己的，可以改 */
// ptr[0] = 'H';                 // ❌ 修改字串字面值：未定義行為（通常直接當掉）
ptr = "world";                   /* ✅ 指標可以改指向別的字串 */
// arr = "world";                // ❌ 陣列不能重新指定
printf("%s %s %zu %zu\n", arr, ptr, sizeof arr, sizeof ptr);   // 輸出：Hello world 6 8
```

**字串字面值 (string literal)** `"hello"` 放在程式的 **唯讀區**，整個程式執行期間都存在。
- `char *p = "hello";` 在 C 裡可以編譯（歷史原因），但修改它是未定義行為。
- **規則：指向字串字面值的指標一律寫 `const char *`**，不小心修改時編譯器就會擋下來。

**🔍 相鄰的字串字面值會自動接起來**：

```c
const char *msg = "Hello, "
                  "world";       /* 編譯時就接成 "Hello, world" */
printf("%s\n", msg);             // 輸出：Hello, world
```

---

# 第二部分：讀取字串

## 2.1 scanf("%s")：只能讀一個「字」

```c
char name[20];
scanf("%19s", name);             // 輸入：Mary Ann → name 只有 "Mary"
```

- 讀到 **空白就停**。
- **一定要寫最大寬度**（陣列大小 - 1），否則輸入太長就溢位（第 01 課）。

## 2.2 fgets：讀一整行（推薦）

```c
char line[100];
if (fgets(line, sizeof line, stdin) != NULL) {   /* 最多讀 sizeof line - 1 個字元，一定會加 '\0' */
    printf("[%s]\n", line);
}
// 輸入：hello world
// 輸出：[hello world
//       ]                       ← fgets 會把換行字元 '\n' 也存進去！
```

**`fgets(buf, size, stdin)`**：
- 讀到換行（**包含換行字元**）或讀滿 `size - 1` 個字元為止。
- **一定會** 在最後放 `'\0'`，不會溢位。
- 讀到檔案結尾、什麼都沒讀到時回傳 `NULL`。

### 去掉結尾的換行

```c
line[strcspn(line, "\n")] = '\0';   /* strcspn：第一個 '\n' 的位置；沒有的話是字串長度 */
printf("[%s]\n", line);             // 輸出：[hello world]
```

（如果檔案是 Windows 產生的，結尾可能是 `"\r\n"`，用 `strcspn(line, "\r\n")`。）

### 一行比緩衝區還長時

```c
char small[8];
fgets(small, sizeof small, stdin);  // 輸入：abcdefghijk → small = "abcdefg"（7 個字元 + '\0'）
                                    // 剩下的 "hijk\n" 還留在輸入裡，下一次 fgets 會讀到
```

判斷有沒有讀完整行：看最後一個字元是不是 `'\n'`。

### ⚠️ 永遠不要用 gets

`gets(buf)` 不知道緩衝區有多大，輸入太長就溢位。它危險到 **C11 直接把它從標準中刪除**了。

## 2.3 scanf 和 fgets 混用的陷阱

```c
int n;
char name[50];
scanf("%d", &n);                 // 輸入：「3\nAmy\n」，scanf 讀完 3，換行還留著
fgets(name, sizeof name, stdin); // ❌ 立刻讀到那個換行 → name = "\n"
```

**解法**：`scanf` 之後，先把這一行剩下的字元讀掉：

```c
int ch;
while ((ch = getchar()) != '\n' && ch != EOF) { }   /* 丟掉這一行剩下的 */
fgets(name, sizeof name, stdin);                    /* ✅ 讀到 "Amy\n" */
```

或者乾脆 **全部用 `fgets` 讀，再用 `sscanf` 解析**（第五部分）。

---

# 第三部分：<string.h>

## 3.1 長度與複製

| 函式 | 作用 | 注意 |
|---|---|---|
| `strlen(s)` | 長度（不含 `'\0'`） | 回傳 `size_t`；`O(n)` |
| `strcpy(dst, src)` | 把 `src`（含 `'\0'`）複製到 `dst` | ⚠️ 不檢查 `dst` 夠不夠大 |
| `strncpy(dst, src, n)` | 最多複製 `n` 個字元 | ⚠️ `src` 太長時 **不會加 `'\0'`**（4.3 節） |
| `strcat(dst, src)` | 把 `src` 接到 `dst` 後面 | ⚠️ 不檢查空間 |
| `strncat(dst, src, n)` | 最多接 `n` 個字元，**一定會** 加 `'\0'` | `n` 是「最多接幾個」，不是 `dst` 的大小 |

```c
char buf[32];
strcpy(buf, "Hello");
strcat(buf, ", ");
strcat(buf, "world");
printf("%s %zu\n", buf, strlen(buf));   // 輸出：Hello, world 12
```

**為什麼不能寫 `buf = "Hello";`？** 陣列不能整個指定（第 04 課）。字串的指定、串接、比較 **全部都要用函式**。

## 3.2 比較

| 函式 | 作用 |
|---|---|
| `strcmp(a, b)` | 字典序比較：`a < b` 回傳負數、相等回傳 0、`a > b` 回傳正數 |
| `strncmp(a, b, n)` | 只比較前 `n` 個字元 |

```c
printf("%d\n", strcmp("apple", "apple") == 0);   // 輸出：1
printf("%d\n", strcmp("apple", "banana") < 0);   // 輸出：1
printf("%d\n", strcmp("ab", "abc") < 0);          // 前面相同、比較短的比較小 → 輸出：1
printf("%d\n", strcmp("Zebra", "apple") < 0);     // 比的是字元編碼：'Z' (90) < 'a' (97) → 輸出：1
printf("%d\n", strncmp("hello", "help", 3) == 0); // 只比前 3 個 → 輸出：1
```

**⚠️ 最常見的錯誤：用 `==` 比較字串**

```c
char input[10] = "yes";
if (input == "yes") { }          /* ❌ 比較的是兩個「位址」，幾乎永遠是假 */
if (strcmp(input, "yes") == 0) { }   /* ✅ */
```

GCC 會警告：`comparison with string literal results in unspecified behavior`。

**⚠️ `strcmp` 的回傳值只保證正負號**：不要寫 `strcmp(a, b) == 1` 或 `== -1`，要寫 `> 0`、`< 0`。

## 3.3 搜尋

| 函式 | 回傳 |
|---|---|
| `strchr(s, c)` | 字元 `c` **第一次** 出現的位置（指標）；找不到回傳 `NULL` |
| `strrchr(s, c)` | 字元 `c` **最後一次** 出現的位置 |
| `strstr(s, sub)` | 子字串 `sub` 第一次出現的位置 |
| `strcspn(s, set)` | 從頭開始，**不在** `set` 裡的字元有幾個（= 第一個在 `set` 裡的位置） |
| `strspn(s, set)` | 從頭開始，**在** `set` 裡的字元有幾個 |

```c
const char *s = "hello world";
const char *p = strchr(s, 'o');
printf("%td %s\n", p - s, p);                    /* 位置 = 指標相減 → 輸出：4 o world */
printf("%td\n", strrchr(s, 'o') - s);            // 輸出：7
printf("%s\n", strstr(s, "wor"));                // 輸出：world
printf("%d\n", strstr(s, "xyz") == NULL);        // 輸出：1
printf("%zu %zu\n", strcspn(s, " "), strspn("123abc", "0123456789"));   // 輸出：5 3

const char *path = "/home/amy/notes.txt";
printf("%s\n", strrchr(path, '/') + 1);          /* 檔名 → 輸出：notes.txt */
```

**回傳的是指標**：要得到索引，用「回傳值 - 字串開頭」。用之前一定要檢查是不是 `NULL`。

## 3.4 strtok：切字串（會修改原字串）

```c
char data[] = "apple,banana,,cherry";   /* 一定要是可以修改的陣列！ */
for (char *tok = strtok(data, ","); tok != NULL; tok = strtok(NULL, ","))   /* 之後的呼叫傳 NULL */
    printf("[%s]", tok);
printf("\n");                           // 輸出：[apple][banana][cherry]
```

**`strtok` 的特性與陷阱**：
- 它會 **把分隔字元改成 `'\0'`**，原字串被破壞了。不能用在字串字面值上。
- **連續的分隔字元會被當成一個**，空欄位會被跳過（上面的 `,,` 沒有產生空字串）。需要保留空欄位時，自己用 `strchr` 切。
- 它用 **內部的靜態變數** 記住切到哪裡，所以不能同時切兩個字串（巢狀使用會出錯）。

## 3.5 記憶體函式：mem 系列

`mem` 系列處理 **任意的 byte**，不看 `'\0'`，所以要給長度：

| 函式 | 作用 |
|---|---|
| `memset(p, value, n)` | 把 `n` 個 byte 都設成 `value` |
| `memcpy(dst, src, n)` | 複製 `n` 個 byte（區域 **不能重疊**） |
| `memmove(dst, src, n)` | 複製 `n` 個 byte（區域 **可以重疊**） |
| `memcmp(a, b, n)` | 比較 `n` 個 byte |

```c
int arr[5];
memset(arr, 0, sizeof arr);              /* 全部清成 0 */
char mm[] = "abcdef";
memmove(mm + 1, mm, 3);                  /* 重疊的區域：把 "abc" 往後搬一格 */
printf("%d %s\n", arr[4], mm);           // 輸出：0 aabcef
```

**⚠️ `memset` 是以 byte 為單位**：`memset(arr, 1, sizeof arr)` **不會** 讓每個 `int` 變成 1，而是每個 byte 都是 1 → 每個 `int` 是 `0x01010101` = 16843009。只有設成 0 或 -1（所有 byte 都是 `0xFF`）對 `int` 是安全的。

---

# 第四部分：緩衝區溢位與安全的寫法

## 4.1 緩衝區溢位 (Buffer Overflow)

**是什麼**：寫入的資料超過陣列的大小，蓋到後面的記憶體。

```c
char small[8];
strcpy(small, "this string is way too long");   /* ❌ 寫出陣列外面 */
```

**後果**：改壞其他變數、程式當掉，甚至 **被攻擊者利用來執行任意程式碼** —— 這是歷史上最多安全漏洞的來源之一。GCC 有時候能在編譯時發現（`-Wstringop-overflow`），用 `--debug`（ASan）執行時一定會被抓到。

## 4.2 snprintf：最安全的字串組合方式

**是什麼**：像 `printf`，但結果寫進字串，而且 **最多寫 `size - 1` 個字元，一定會加 `'\0'`**。

```c
char buf[16];
int need = snprintf(buf, sizeof buf, "%s-%d", "item", 42);
printf("[%s] %d\n", buf, need);          // 輸出：[item-42] 7

char tiny[8];
need = snprintf(tiny, sizeof tiny, "%s", "abcdefghijkl");
printf("[%s] %d\n", tiny, need);         /* 被截斷了，但不會溢位 → 輸出：[abcdefg] 12 */
```

**回傳值**：「**如果空間足夠，總共需要幾個字元**」。回傳值 ≥ `size` 就表示被截斷了：

```c
if (need >= (int)sizeof tiny) printf("被截斷\n");   // 輸出：被截斷
```

**`snprintf` 可以取代 `strcpy` 和 `strcat`**：

```c
char full[32];
snprintf(full, sizeof full, "%s %s", "Hello", "world");   /* 安全地串接 */
```

## 4.3 ⚠️ strncpy 的陷阱

很多人以為 `strncpy` 是「安全版的 `strcpy`」，但它有兩個問題：

```c
char d[5];
strncpy(d, "abcdefg", sizeof d);     /* src 太長：複製 5 個字元，但「不會」加 '\0'！ */
d[sizeof d - 1] = '\0';              /* 一定要自己補 */
printf("%s\n", d);                   // 輸出：abcd
```

1. `src` 的長度 ≥ `n` 時，**不會** 加 `'\0'`。
2. `src` 比 `n` 短時，會把剩下的空間 **全部填 0**（浪費時間）。

**規則**：需要「安全複製」時用 `snprintf(dst, size, "%s", src)`。

## 4.4 計算大小時記得 + 1

```c
const char *a = "hello", *b = "world";
char joined[sizeof "hello" + sizeof "world" - 1];   /* 5 + 5 + 1：兩段字元 + 一個 '\0' */
strcpy(joined, a);
strcat(joined, b);
printf("%s %zu\n", joined, sizeof joined);           // 輸出：helloworld 11
```

動態配置時也一樣：`malloc(strlen(s) + 1)`（第 07 課）。

---

# 第五部分：字串與數字互轉

## 5.1 字串 → 數字

### atoi：簡單但沒辦法偵測錯誤

```c
#include <stdlib.h>
printf("%d %d %d\n", atoi("123"), atoi("  42abc"), atoi("abc"));   // 輸出：123 42 0
```

`atoi("abc")` 回傳 0，`atoi("0")` 也回傳 0 —— **分不出是錯誤還是真的 0**。溢位時是未定義行為。

### strtol：能偵測錯誤（推薦）

```c
#include <errno.h>
const char *text = "123abc";
char *end;
errno = 0;
long v = strtol(text, &end, 10);         /* 第三個參數：進位制 */
printf("%ld [%s]\n", v, end);            /* end 指向「沒有被轉換的部分」 → 輸出：123 [abc] */
```

**完整檢查一個字串是不是合法的整數**：

```c
int parse_int(const char *s, long *out) {
    char *end;
    errno = 0;
    long v = strtol(s, &end, 10);
    if (end == s) return 0;              /* 一個數字都沒有 */
    if (*end != '\0') return 0;          /* 後面還有多餘的字元 */
    if (errno == ERANGE) return 0;       /* 超出 long 的範圍 */
    *out = v;
    return 1;
}
long val;
printf("%d %d %d\n", parse_int("42", &val), parse_int("42x", &val), parse_int("", &val));   // 輸出：1 0 0
printf("%ld %ld\n", strtol("ff", NULL, 16), strtol("-101", NULL, 2));   // 輸出：255 -5
```

| 函式 | 轉成 |
|---|---|
| `strtol` / `strtoll` | `long` / `long long` |
| `strtoul` / `strtoull` | `unsigned long` / `unsigned long long` |
| `strtod` | `double` |

### sscanf：從字串讀取

```c
int y, m, d;
if (sscanf("2024-03-09", "%d-%d-%d", &y, &m, &d) == 3)
    printf("%d/%d/%d\n", m, d, y);       // 輸出：3/9/2024

char cmd[16];
int amount;
int n = sscanf("deposit 500", "%15s %d", cmd, &amount);
printf("%d %s %d\n", n, cmd, amount);    // 輸出：2 deposit 500
```

「`fgets` 讀一行 + `sscanf` 解析」是處理輸入最穩健的方式：格式錯誤時只影響這一行，不會像 `scanf` 那樣卡住。

## 5.2 數字 → 字串

```c
char out[32];
snprintf(out, sizeof out, "%d", -1234);
printf("%s %zu\n", out, strlen(out));    // 輸出：-1234 5
snprintf(out, sizeof out, "%.2f%%", 12.345);
printf("%s\n", out);                     // 輸出：12.35%
```

（`itoa` 不是標準 C 的函式，不要用。）

---

# 第六部分：字元處理與常見操作

## 6.1 <ctype.h>

| 函式 | 判斷 / 作用 |
|---|---|
| `isalpha(c)`、`isdigit(c)`、`isalnum(c)` | 字母、數字、字母或數字 |
| `isspace(c)` | 空白（空格、`\t`、`\n`、`\r`、`\v`、`\f`） |
| `isupper(c)`、`islower(c)`、`ispunct(c)` | 大寫、小寫、標點 |
| `toupper(c)`、`tolower(c)` | 轉大寫 / 小寫（不是字母就原樣回傳） |

**⚠️ 參數必須是 `unsigned char` 的值或 `EOF`**：`char` 可能是負的（例如中文的 UTF-8 byte），直接傳進去是未定義行為。

```c
#include <ctype.h>
const char *s = "Hi 2u!";
int letters = 0, digits = 0;
for (const char *p = s; *p; p++) {
    unsigned char c = (unsigned char)*p;   /* 先轉成 unsigned char */
    if (isalpha(c)) letters++;
    else if (isdigit(c)) digits++;
}
printf("%d %d\n", letters, digits);        // 輸出：3 1
```

## 6.2 常見操作

### 轉大寫（原地修改）

```c
void to_upper(char *s) {
    for (; *s; s++) *s = (char)toupper((unsigned char)*s);
}
char word[] = "Hello, C!";
to_upper(word);
printf("%s\n", word);                      // 輸出：HELLO, C!
```

### 反轉

```c
void reverse(char *s) {
    size_t n = strlen(s);
    for (size_t i = 0; i < n / 2; i++) {
        char t = s[i]; s[i] = s[n - 1 - i]; s[n - 1 - i] = t;
    }
}
char r[] = "abcde";
reverse(r);
printf("%s\n", r);                         // 輸出：edcba
```

### 去掉前後空白 (trim)

```c
char *trim(char *s) {
    while (isspace((unsigned char)*s)) s++;          /* 前面：把開頭往後移 */
    if (*s == '\0') return s;
    char *end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) end--;
    end[1] = '\0';                                   /* 後面：在最後一個非空白字元後面放 '\0' */
    return s;                                        /* 回傳新的開頭（可能不是原本的位址） */
}
char padded[] = "   hi there \n";
printf("[%s]\n", trim(padded));            // 輸出：[hi there]
```

### 不分大小寫比較

```c
int equal_ignore_case(const char *a, const char *b) {
    for (; *a && *b; a++, b++)
        if (tolower((unsigned char)*a) != tolower((unsigned char)*b)) return 0;
    return *a == *b;                       /* 兩個都要同時結束 */
}
printf("%d %d\n", equal_ignore_case("Hello", "hELLO"), equal_ignore_case("Hi", "Hit"));   // 輸出：1 0
```

### 數單字

```c
int count_words(const char *s) {
    int count = 0, in_word = 0;
    for (; *s; s++) {
        if (isspace((unsigned char)*s)) in_word = 0;
        else if (!in_word) { in_word = 1; count++; }   /* 從空白進入單字的那一刻 */
    }
    return count;
}
printf("%d\n", count_words("  the quick  brown fox "));   // 輸出：4
```

`CL07` 用同樣的「狀態」技巧。

---

# 第七部分：字串陣列

## 7.1 兩種寫法

```c
/* 寫法一：二維 char 陣列 —— 每個字串都佔固定的 10 bytes，可以修改 */
char names[3][10] = {"amy", "bob", "christine"};

/* 寫法二：指標陣列 —— 每個元素是一個指向字串字面值的指標，不能修改內容 */
const char *colors[] = {"red", "green", "blue"};

printf("%s %s\n", names[2], colors[1]);    // 輸出：christine green
printf("%zu %zu\n", sizeof names, sizeof colors);   // 輸出：30 24
names[0][0] = 'A';                         /* ✅ 可以改 */
printf("%s\n", names[0]);                  // 輸出：Amy
```

```
names（3 × 10 的連續空間）:              colors（3 個指標）:
[a|m|y|\0|.|.|.|.|.|.]                    [ptr] ──▶ "red"
[b|o|b|\0|.|.|.|.|.|.]                    [ptr] ──▶ "green"
[c|h|r|i|s|t|i|n|e|\0]                    [ptr] ──▶ "blue"
```

| | `char names[3][10]` | `const char *colors[3]` |
|---|---|---|
| 記憶體 | 每個字串固定大小，可能浪費 | 只存指標，字串長度不限 |
| 可以修改內容 | ✅ | ❌（指向字面值） |
| 交換兩個字串 | 要複製字元（`strcpy` 三次） | 只要交換指標 |

`main` 的 `char *argv[]` 就是指標陣列。

## 7.2 排序字串

用指標陣列排序，只要 **交換指標**，不用搬動字元：

```c
const char *words[] = {"pear", "apple", "fig", "banana"};
int n = 4;
for (int i = 0; i < n - 1; i++)             /* 選擇排序 */
    for (int j = i + 1; j < n; j++)
        if (strcmp(words[i], words[j]) > 0) {
            const char *t = words[i]; words[i] = words[j]; words[j] = t;
        }
for (int i = 0; i < n; i++) printf("%s ", words[i]);
printf("\n");                               // 輸出：apple banana fig pear
```

第 09 課會用 `qsort` 做同樣的事。

## 7.3 🔍 中文與 UTF-8

C 的 `char` 是一個 byte。中文字在 UTF-8 編碼裡通常佔 **3 個 byte**：

```c
const char *zh = "你好";
printf("%zu\n", strlen(zh));               // 輸出：6（不是 2）
```

所以 `strlen` 算的是 byte 數，`s[0]` 只是「你」的第一個 byte。處理多國文字需要專門的函式庫。本平台的題目都只用 ASCII。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 空字元 | Null Character `'\0'` | 字串的結尾標記，值是 0 | 1.1 |
| 字串字面值 | String Literal | 程式碼裡的 `"..."`，放在唯讀區 | 1.3 |
| 緩衝區 | Buffer | 用來暫存資料的陣列 | 2 |
| 緩衝區溢位 | Buffer Overflow | 寫入超過陣列大小 | 4.1 |
| 截斷 | Truncation | 資料太長，只保留放得下的部分 | 4.2 |
| 分隔字元 | Delimiter | 切字串時的分界字元 | 3.4 |
| 字典序 | Lexicographical Order | 字串比較的順序 | 3.2 |
| 指標陣列 | Array of Pointers | 每個元素都是指標的陣列 | 7.1 |

---

# 習題

### 題 1：預測輸出

```c
char s[10] = "abc";
printf("%zu %zu ", sizeof s, strlen(s));
s[1] = '\0';
printf("%zu %s\n", strlen(s), s);
```

### 題 2：找出所有錯誤

```c
char name[5];
char *greeting = "hello";
strcpy(name, "Alexander");
greeting[0] = 'H';
if (name == "Alexander") printf("same\n");
```

### 題 3：預測輸出

```c
const char *s = "programming";
printf("%td %td %s\n", strchr(s, 'g') - s, strrchr(s, 'g') - s, strstr(s, "ram"));
```

### 題 4：輸入是 `hello` 換行，下面的程式印出什麼？怎麼去掉換行？

```c
char buf[20];
fgets(buf, sizeof buf, stdin);
printf("[%s] %zu\n", buf, strlen(buf));
```

### 題 5：預測輸出

```c
char buf[6];
int n = snprintf(buf, sizeof buf, "%d-%d", 123, 456);
printf("%s %d\n", buf, n);
```

### 題 6：`atoi("0")` 和 `atoi("zero")` 都回傳 0，怎麼分辨哪一個是合法的輸入？寫出用 `strtol` 的判斷方式。

### 題 7：寫一個函式 `int is_palindrome(const char *s)`，判斷字串是否為迴文（正著讀和反著讀一樣），例如 `"racecar"`。

### 題 8：預測輸出

```c
char data[] = "a b  c";
int count = 0;
for (char *t = strtok(data, " "); t; t = strtok(NULL, " ")) count++;
printf("%d %s\n", count, data);
```

---

# 習題解答

**題 1**：`10 3 1 a`。`sizeof` 是陣列大小 10；`strlen` 是 3。把 `s[1]` 改成 `'\0'` 之後，字串在那裡就結束了：長度 1，內容 `"a"`。

**題 2**：
- `name` 只有 5 格，`"Alexander"` 需要 10 格 → **緩衝區溢位**。
- `greeting` 指向字串字面值，`greeting[0] = 'H'` 修改唯讀記憶體 → 未定義行為（應該宣告成 `const char *`，或用陣列 `char greeting[] = "hello";`）。
- `name == "Alexander"` 比較的是位址，要用 `strcmp(name, "Alexander") == 0`。

**題 3**：`3 10 ramming`。第一個 `g` 在索引 3（`p-r-o-g`），最後一個在索引 10；`strstr` 回傳指向 `"ram"` 開頭的指標，印出從那裡到結尾的 `ramming`。

**題 4**：印出 `[hello` 換行 `] 6`。`fgets` 會把換行字元存進去，所以長度是 6。去掉換行：`buf[strcspn(buf, "\n")] = '\0';`。

**題 5**：`123-4 7`。完整的結果 `"123-456"` 需要 7 個字元，緩衝區只放得下 5 個字元 + `'\0'`，所以被截斷成 `"123-4"`；回傳值是「需要的長度」7。

**題 6**：

```c
char *end;
errno = 0;
long v = strtol(s, &end, 10);
if (end == s || *end != '\0' || errno == ERANGE) { /* 不是合法的整數 */ }
```

`"0"`：`end` 指向結尾的 `'\0'`，合法；`"zero"`：一個數字都沒讀到，`end == s`，不合法。

**題 7**：

```c
int is_palindrome(const char *s) {
    size_t n = strlen(s);
    for (size_t i = 0; i < n / 2; i++)
        if (s[i] != s[n - 1 - i]) return 0;
    return 1;
}
```

**題 8**：`3 a`。`strtok` 把連續的空白當成一個分隔，切出 `a`、`b`、`c` 三個；它會把分隔字元改成 `'\0'`，所以之後 `data` 從開頭讀到第一個 `'\0'` 只剩 `"a"`。
