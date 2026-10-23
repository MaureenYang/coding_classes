# 10. 檔案與輸入輸出

> 程式練習：`CL07 文字統計`（讀到 `EOF`、逐字元處理）
>
> 先備知識：第 01 課 `printf` / `scanf`、第 06 課「字串」、第 08 課「struct」。

**這一課分成六個部分：**

| 部分 | 內容 | 讀完你會知道 |
|---|---|---|
| 第一部分 | 串流 | `stdin` / `stdout` / `stderr`、`FILE *`、緩衝區、重新導向 |
| 第二部分 | 逐字元讀寫 | `getchar` / `putchar`、`EOF` 為什麼要用 `int`、狀態機 |
| 第三部分 | 逐行讀取 | `fgets` 的行為、去掉換行、一行太長怎麼辦 |
| 第四部分 | 格式化讀取 | `scanf` 的回傳值、讀到結束、`sscanf` 解析一行 |
| 第五部分 | 檔案 | `fopen` 模式、`fclose`、`perror`、文字檔、二進位檔 |
| 第六部分 | 錯誤處理 | `feof` 的錯誤用法、`ferror`、所有 I/O 都可能失敗 |

**閱讀方式**：每個觀念依序說明 **是什麼 → 為什麼需要 → 怎麼用（範例）→ 常見錯誤**。範例裡的 `// 輸出：` 都是實際用 `gcc -std=c11` 編譯執行過的結果。標 🔍 的是深入內容。

---

# 第一部分：串流

## 1.1 三個預設的串流

**是什麼**：C 把所有輸入輸出都看成 **串流 (stream)**：一連串的位元組，一個接一個地讀或寫。程式一開始就有三個打開的串流：

| 名字 | 是什麼 | 預設接到 | 用途 |
|---|---|---|---|
| `stdin` | 標準輸入 | 鍵盤 | `scanf`、`getchar` 從這裡讀 |
| `stdout` | 標準輸出 | 螢幕 | `printf`、`putchar` 寫到這裡 |
| `stderr` | 標準錯誤 | 螢幕 | 錯誤訊息：`fprintf(stderr, ...)` |

它們的型別都是 `FILE *`，和用 `fopen` 打開的檔案 **完全一樣**。所以每個 I/O 函式都有「指定串流」的版本：

| 用預設串流 | 指定串流 |
|---|---|
| `printf(...)` | `fprintf(fp, ...)` |
| `scanf(...)` | `fscanf(fp, ...)` |
| `getchar()` | `fgetc(fp)` / `getc(fp)` |
| `putchar(c)` | `fputc(c, fp)` / `putc(c, fp)` |
| `puts(s)`（會加換行） | `fputs(s, fp)`（不加換行） |

## 1.2 重新導向

在命令列，可以把 `stdin` / `stdout` 接到檔案，**程式完全不用改**：

```bash
./prog < input.txt                # stdin 改成從 input.txt 讀
./prog > output.txt               # stdout 寫到 output.txt（stderr 還是在螢幕）
./prog < in.txt > out.txt 2> err.txt
./prog1 | ./prog2                 # 管線：prog1 的 stdout 接到 prog2 的 stdin
```

本平台的評測就是這樣做的：把測資檔接到你的 `stdin`、把你的 `stdout` 和正確答案比對。所以 **錯誤訊息、除錯訊息一定要寫到 `stderr`**，寫到 `stdout` 就會被當成答案的一部分而判 WA。

## 1.3 🔍 緩衝區

**是什麼**：每次 `printf` 都直接叫作業系統輸出，很慢。所以 `stdout` 有一塊 **緩衝區 (buffer)**：先把資料存起來，累積到一定程度才一次送出。

| 串流 | 緩衝方式 | 什麼時候真正輸出 |
|---|---|---|
| `stdout` 接到 **終端機** | 行緩衝 | 遇到 `'\n'`、緩衝區滿、程式結束、要讀 `stdin` 時 |
| `stdout` 接到 **檔案 / 管線** | 全緩衝 | 緩衝區滿（通常 4 KB 以上）、程式正常結束 |
| `stderr` | 不緩衝 | 立刻 |

```c
printf("A\n");
fprintf(stderr, "B\n");
printf("C\n");
```

```
在終端機執行：           ./prog > out.txt 2>&1 之後看 out.txt：
A                       B
B                       A
C                       C
```

輸出到檔案時，`A` 和 `C` 在緩衝區裡等到程式結束，`B` 卻立刻寫進去了。

**會造成的問題**：
- 程式當掉（例如 segmentation fault）時，緩衝區裡的東西 **來不及輸出**。所以「用 printf 除錯，但當掉前的訊息沒印出來」常常是緩衝的關係 —— 除錯訊息請寫到 `stderr`。
- 需要立刻輸出時，用 `fflush(stdout);`。

---

# 第二部分：逐字元讀寫

## 2.1 getchar 與 EOF

**是什麼**：`getchar()` 從 `stdin` 讀 **一個字元**，回傳它的值（0 ~ 255）；沒有資料了就回傳 **`EOF`**（一個負數，通常是 -1）。

**EOF (End Of File)** 不是檔案裡的一個字元，而是「已經沒有東西可讀了」的 **訊號**。
- 從檔案讀：讀到檔案結尾。
- 從鍵盤讀：Linux / Mac 按 `Ctrl+D`，Windows 按 `Ctrl+Z` 再按 Enter。

**標準寫法**：

```c
int c;                                    /* ⚠️ 一定要用 int，不能用 char */
while ((c = getchar()) != EOF) {
    putchar(toupper(c));                  /* <ctype.h>：轉大寫 */
}
// 輸入：Hi there
// 輸出：HI THERE
```

`(c = getchar()) != EOF` 做了兩件事：先把讀到的字元存進 `c`，再拿 `c` 和 `EOF` 比較。外面那層括號不能少（`!=` 的優先順序比 `=` 高）。

### ⚠️ 為什麼一定要用 int？

`getchar` 要能回傳 **257 種** 不同的值：256 種位元組（0 ~ 255），加上 `EOF`。`char` 只能存 256 種，裝不下。

```c
char c;                                   /* ❌ */
int n = 0;
while ((c = getchar()) != EOF) n++;
printf("%d\n", n);
// 輸入 5 個位元組：a b 0xFF c d
// 輸出：2（讀到 0xFF 就停了！）
```

`char` 在 x86 上是有號的，位元組 `0xFF`（255）存進 `char` 變成 -1，剛好等於 `EOF`，迴圈就提早結束了。（如果 `char` 是無號的平台，則 `c` 永遠不會等於 -1，變成無窮迴圈。）一般的英文文字沒有 `0xFF`，所以這個 bug 常常測不出來；但中文的 UTF-8 編碼、二進位檔都可能出現。

## 2.2 例子：自己寫 wc（字數統計）

**問題**：統計行數、單字數、字元數。「單字」是連續的非空白字元。

**關鍵**：用一個變數記錄 **目前的狀態**（在單字裡面 / 外面），只在「從外面進入單字」的那一刻加 1。這種寫法叫 **狀態機 (state machine)**。

```c
int c;
long chars = 0, lines = 0, words = 0;
int in_word = 0;                          /* 狀態：0 = 在單字外，1 = 在單字裡 */
while ((c = getchar()) != EOF) {
    chars++;
    if (c == '\n') lines++;
    if (isspace(c)) in_word = 0;          /* 空白：離開單字 */
    else if (!in_word) {                  /* 非空白，而且原本在單字外 → 新單字開始 */
        in_word = 1;
        words++;
    }
}
printf("%ld %ld %ld\n", lines, words, chars);
// 輸入（最後沒有換行）：
// hello world
//   foo<Tab>bar baz
// (空行)
// end
// 輸出：3 6 30
```

注意行數是 3：只算 `'\n'` 的個數，最後一行 `end` 後面沒有換行。`CL07` 的定義會把這種「最後一行」也算進去，要特別處理。

**為什麼逐字元讀？** 不需要知道一行有多長、不需要緩衝區、不會溢位。`CL07` 的一行可能長達 10⁶ 字元，逐字元處理最簡單也最安全。

## 2.3 🔍 ungetc：把字元放回去

```c
int c = getchar();
if (isdigit(c)) {
    ungetc(c, stdin);                     /* 放回去，下次讀的時候會再讀到它 */
    int x;
    scanf("%d", &x);                      /* 從那個數字開始讀整數 */
}
```

用來「偷看」下一個字元。標準只保證能放回 **一個** 字元。

---

# 第三部分：逐行讀取

## 3.1 fgets

```c
char *fgets(char *buf, int size, FILE *fp);
```

**是什麼**：讀一行到 `buf`，**最多讀 `size - 1` 個字元**（留一格給 `'\0'`）。讀到 `'\n'` 時停下來，**而且 `'\n'` 會被存進 `buf`**。檔案結束（沒讀到任何東西）時回傳 `NULL`。

**為什麼用 fgets**：它 **一定不會寫超過 `size` 個 byte**，不會緩衝區溢位。（舊的 `gets` 不知道緩衝區有多大，已經從 C11 移除了，**永遠不要用**。）

```c
char buf[8];                              /* 一次最多讀 7 個字元 */
while (fgets(buf, sizeof buf, stdin) != NULL) {
    size_t len = strlen(buf);
    int has_nl = len > 0 && buf[len - 1] == '\n';
    buf[strcspn(buf, "\n")] = '\0';       /* 去掉換行（如果有的話） */
    printf("\"%s\" %zu %s\n", buf, len, has_nl ? "完整的一行" : "還沒讀完");
}
// 輸入兩行：hi、abcdefghijk
// 輸出：
// "hi" 3 完整的一行
// "abcdefg" 7 還沒讀完
// "hijk" 5 完整的一行
```

**重點**：
1. `"hi\n"` 的長度是 3：`fgets` 保留了換行。
2. 一行比緩衝區長時，**一次讀不完**，剩下的部分下一次呼叫才讀到。判斷方法：最後一個字元是不是 `'\n'`。
3. 檔案最後一行沒有換行時，那一行讀進來也不會有 `'\n'`。

## 3.2 去掉換行

```c
buf[strcspn(buf, "\n")] = '\0';           /* ✅ 最安全的寫法 */
```

`strcspn(buf, "\n")` 回傳「第一個 `'\n'` 之前有幾個字元」；沒有 `'\n'` 時回傳整個字串長度，那個位置本來就是 `'\0'`，寫進去也沒有影響。

```c
buf[strlen(buf) - 1] = '\0';              /* ❌ 沒有換行時會刪掉最後一個真正的字元；空字串時 strlen 是 0，0 - 1 會變成超大的數 */
```

## 3.3 一行長度不確定怎麼辦

- 長度有上限（題目說一行最多 100 字元）：緩衝區開大一點，例如 `char buf[128]`（要留 `'\n'` 和 `'\0'` 的空間）。
- 長度沒有上限：用第 07 課 5.2 節的 `read_line`，或者乾脆逐字元處理（2.2 節）。

---

# 第四部分：格式化讀取

## 4.1 scanf 的回傳值

`scanf` 回傳 **成功讀到並存入的項目個數**；還沒讀到任何項目就遇到檔案結尾時，回傳 `EOF`。

```c
int x, sum = 0, n = 0, r;
while ((r = scanf("%d", &x)) == 1) {
    sum += x;
    n++;
}
printf("n=%d sum=%d last=%d\n", n, sum, r);
// 輸入「1 2 3」         → 輸出：n=3 sum=6 last=-1（讀到結尾，回傳 EOF）
// 輸入「1 2 3 x 4」     → 輸出：n=3 sum=6 last=0（遇到 x 讀不成整數，回傳 0）
```

**常見錯誤**：

```c
while (scanf("%d", &x) != EOF) { ... }    /* ❌ 遇到 x 時回傳 0，不是 EOF；x 留在輸入裡，下一次又失敗 → 無窮迴圈 */
while (scanf("%d", &x) == 1) { ... }      /* ✅ 和「應該讀到的個數」比較 */
```

## 4.2 sscanf：先讀一行，再解析

**問題**：用 `scanf` 直接讀，格式錯誤時很難恢復（錯誤的資料卡在輸入裡）；也分不出「哪些資料在同一行」。

**解法**：先用 `fgets` 讀一整行，再用 `sscanf`（從 **字串** 讀）解析：

```c
char line[100];
while (fgets(line, sizeof line, stdin)) {
    char name[21];
    int a, b;
    int got = sscanf(line, "%20s %d %d", name, &a, &b);   /* %20s：最多讀 20 個字元，防止溢位 */
    if (got == 3) printf("%s %d\n", name, a + b);
    else printf("bad line (%d fields)\n", got);
}
// 輸入：
// amy 1 2
// bob x
// (空行)
// cat 3 4
// 輸出：
// amy 3
// bad line (1 fields)
// bad line (-1 fields)
// cat 7
```

格式錯誤的那一行被跳過了，**不影響後面的行**。空行沒有任何資料，`sscanf` 回傳 `EOF`（-1）。

## 4.3 輸出到字串：snprintf

```c
char msg[32];
int n = snprintf(msg, sizeof msg, "%s scored %d", "amy", 90);   /* 不會超過 sizeof msg */
```

回傳值是「**如果空間足夠**，會寫入幾個字元」。`n >= sizeof msg` 表示被截斷了。（`sprintf` 不檢查長度，和 `gets` 一樣危險。）

---

# 第五部分：檔案

## 5.1 開檔、讀寫、關檔

```c
FILE *out = fopen("scores.txt", "w");     /* 開啟檔案來寫入 */
if (out == NULL) {                        /* ⚠️ 一定要檢查 */
    perror("fopen");
    return 1;
}
fprintf(out, "amy 90\nbob 85\ncat 77\n"); /* 和 printf 一樣，只是多了第一個參數 */
fclose(out);                              /* 關檔：把緩衝區寫進檔案、釋放資源 */

FILE *in = fopen("scores.txt", "r");      /* 開啟檔案來讀取 */
if (!in) { perror("fopen"); return 1; }
char name[21];
int score, total = 0, n = 0;
while (fscanf(in, "%20s %d", name, &score) == 2) {
    total += score;
    n++;
}
fclose(in);
printf("%d %d %.2f\n", n, total, (double)total / n);   // 輸出：3 252 84.00
```

**`fopen` 的模式**：

| 模式 | 意義 | 檔案不存在 | 檔案已存在 |
|---|---|---|---|
| `"r"` | 讀 | 失敗（回傳 `NULL`） | 從頭讀 |
| `"w"` | 寫 | 建立新檔 | **清空內容！** |
| `"a"` | 附加 (append) | 建立新檔 | 寫在最後面 |
| `"r+"` | 讀寫 | 失敗 | 從頭開始，不清空 |
| 加上 `"b"`（`"rb"`、`"wb"`） | 二進位模式 | | 見 5.4 節 |

```c
FILE *ap = fopen("scores.txt", "a");
fprintf(ap, "dan 60\n");                  /* 加在最後面，原本的 3 行還在 */
fclose(ap);                               /* 現在檔案有 4 行 */
```

**常見錯誤**：
- 用 `"w"` 開啟想讀的檔案 → 內容被清空了。
- 忘了 `fclose`：資料可能還在緩衝區裡沒寫進檔案；同時能開啟的檔案數量有上限（通常 1024 個），在迴圈裡開檔不關，最後 `fopen` 就會失敗。
- 沒有檢查 `fopen` 的回傳值，對 `NULL` 呼叫 `fprintf` → 當掉。

## 5.2 錯誤訊息：perror 與 errno

`fopen` 失敗時，會把 **錯誤原因的代碼** 存到全域變數 `errno`（`<errno.h>`）。`perror` 把它轉成文字印到 `stderr`：

```c
FILE *nf = fopen("no_such_file.txt", "r");
if (nf == NULL) perror("no_such_file.txt");
// stderr 輸出：no_such_file.txt: No such file or directory
```

也可以用 `strerror(errno)`（`<string.h>`）取得錯誤訊息字串，自己決定怎麼印。

⚠️ `errno` 只有在函式 **回報失敗之後** 才有意義，而且 **之後任何函式呼叫都可能改掉它**（包括 `printf`、`perror` 自己），要用的話先存到另一個變數。

## 5.3 逐行讀檔

```c
FILE *in = fopen("scores.txt", "r");
if (!in) { perror("scores.txt"); return 1; }
char line[64];
int ln = 0;
while (fgets(line, sizeof line, in)) ln++;   /* 和讀 stdin 一模一樣，只是把 stdin 換成 in */
fclose(in);
printf("%d\n", ln);                       // 輸出：4
```

**好的設計**：處理資料的函式接收 `FILE *` 參數，就可以同時用在 `stdin` 和檔案上：

```c
void count_lines(FILE *fp);               /* count_lines(stdin) 或 count_lines(in) 都可以 */
```

## 5.4 二進位檔：fread / fwrite

**文字檔** 存的是「人看得懂的字元」：數字 `12345` 存成 5 個字元。**二進位檔** 直接存記憶體裡的位元組：一個 `int` 就是 4 個 byte。

```c
int data[5] = {1, 2, 3, 4, 5};
FILE *bf = fopen("data.bin", "wb");
size_t w = fwrite(data, sizeof data[0], 5, bf);   /* 寫 5 個元素，每個 sizeof data[0] bytes */
fclose(bf);

int back[5] = {0};
bf = fopen("data.bin", "rb");
size_t r = fread(back, sizeof back[0], 5, bf);    /* 回傳實際讀到的「元素」個數 */
fseek(bf, 0, SEEK_END);                   /* 移到檔案結尾 */
long sz = ftell(bf);                      /* 目前位置 = 檔案大小 */
fclose(bf);
printf("%zu %zu %d %ld\n", w, r, back[4], sz);    // 輸出：5 5 5 20
```

| | 文字檔 | 二進位檔 |
|---|---|---|
| 讀寫函式 | `fprintf` / `fscanf` / `fgets` | `fwrite` / `fread` |
| 人能直接看 | ✅ | ❌ |
| 速度、大小 | 較慢、通常較大 | 快、固定大小 |
| 跨平台 | ✅ | ❌ `int` 大小、位元組順序、struct 填充（第 08 課）可能不同 |

🔍 **`"b"` 的差別**：在 Linux / Mac 上沒有差別。在 **Windows** 上，文字模式會把 `"\n"` 寫成 `"\r\n"`、讀的時候再轉回來；二進位資料剛好有 `0x0A` 時就會被改掉。所以 **二進位檔一定要加 `"b"`**。

---

# 第六部分：錯誤處理

## 6.1 ⚠️ `while (!feof(fp))` 是錯的

```c
int cnt = 0;
while (!feof(in)) {                       /* ❌ */
    fgets(line, sizeof line, in);
    cnt++;
}
printf("%d\n", cnt);                      // 檔案有 4 行，輸出：5
```

**原因**：`feof` 不是「預測下一次會不會讀到結尾」，而是回報「**上一次讀取** 是不是因為碰到結尾而失敗」。讀完第 4 行時還沒「碰到」結尾，`feof` 仍然是假；第 5 次的 `fgets` 才失敗，但迴圈本體已經進來了，`cnt` 多算一次（而且 `line` 還是上一行的內容，會被重複處理）。

**正確寫法**：**用讀取函式的回傳值** 控制迴圈：

| 函式 | 迴圈條件 |
|---|---|
| `getchar` / `fgetc` | `(c = fgetc(fp)) != EOF` |
| `fgets` | `fgets(...) != NULL` |
| `scanf` / `fscanf` | `fscanf(...) == 應讀的個數` |
| `fread` | `fread(...) == 要讀的個數`（或 `> 0`） |

`feof` / `ferror` 的正確用途是 **迴圈結束之後**，判斷「是正常讀完，還是發生錯誤」：

```c
while ((c = fgetc(fp)) != EOF) { ... }
if (ferror(fp)) {
    perror("read");                       /* 讀取錯誤（例如硬碟壞了、網路斷了） */
} /* 否則就是正常讀到結尾 */
```

## 6.2 每個 I/O 都可能失敗

| 函式 | 失敗時回傳 |
|---|---|
| `fopen` | `NULL` |
| `fgets` | `NULL` |
| `fgetc` / `getchar` | `EOF` |
| `scanf` / `fscanf` | 小於預期的個數，或 `EOF` |
| `fread` / `fwrite` | 小於要求的個數 |
| `fclose` | `EOF`（例如硬碟滿了，緩衝區寫不進去） |
| `printf` / `fprintf` | 負數 |

練習題可以假設輸入格式正確；但寫真正的程式時，**至少要檢查 `fopen` 和輸入函式的回傳值**。

---

# 名詞總表

| 中文 | 英文 | 一句話白話 | 出現在 |
|---|---|---|---|
| 串流 | Stream | 一個接一個讀寫的位元組流 | 1.1 |
| 標準輸入 / 輸出 / 錯誤 | stdin / stdout / stderr | 程式一開始就打開的三個串流 | 1.1 |
| 重新導向 | Redirection | 用 `<`、`>` 把串流接到檔案 | 1.2 |
| 管線 | Pipe | 用 `|` 把一個程式的輸出接到另一個的輸入 | 1.2 |
| 緩衝區 | Buffer | 先存起來、累積後一次輸出 | 1.3 |
| 檔案結尾 | EOF (End Of File) | 「沒有東西可讀了」的訊號 | 2.1 |
| 狀態機 | State Machine | 用變數記錄目前的狀態來決定怎麼處理 | 2.2 |
| 二進位檔 | Binary File | 直接存記憶體位元組的檔案 | 5.4 |
| 錯誤碼 | errno | 記錄最近一次錯誤原因的變數 | 5.2 |

---

# 習題

### 題 1：下面的程式想把輸入原封不動地輸出，有什麼問題？

```c
char c;
while (c = getchar() != EOF)
    putchar(c);
```

### 題 2：`char buf[5];` 用 `fgets(buf, sizeof buf, stdin)` 讀入一行 `abcdefg`（後面有換行），每次呼叫讀到什麼？一共呼叫幾次才回傳 `NULL`？

### 題 3：輸入是 `10 20 abc 30`，下面的程式輸出什麼？

```c
int x, n = 0;
while (scanf("%d", &x) == 1) n++;
printf("%d\n", n);
```

如果把條件改成 `!= EOF`，會發生什麼事？

### 題 4：找出錯誤

```c
FILE *fp = fopen("data.txt", "w");
char line[100];
while (!feof(fp)) {
    fgets(line, 100, fp);
    printf("%s", line);
}
```

### 題 5：寫一個程式，從 `stdin` 讀入文字，輸出 **每一行的行號和內容**（類似 `cat -n`），假設一行最多 200 個字元。

### 題 6：程式在輸出很多 `printf` 之後當掉了，可是最後幾行 `printf` 的內容沒有出現在輸出檔裡。可能的原因是什麼？怎麼避免？

### 題 7：用文字模式寫入一個 `int` 值 `1000000` 和用二進位模式寫入，檔案大小各是多少？（不含換行，`int` 是 4 bytes）

---

# 習題解答

**題 1**：兩個錯誤。
- `c = getchar() != EOF`：`!=` 優先順序比 `=` 高，變成 `c = (getchar() != EOF)`，`c` 永遠是 0 或 1。要寫 `(c = getchar()) != EOF`。
- `c` 應該是 `int`：用 `char` 時，位元組 `0xFF` 會被誤認成 `EOF`（2.1 節）。

**題 2**：每次最多讀 4 個字元。第 1 次 `"abcd"`、第 2 次 `"efg\n"`（剛好讀到換行就停）、第 3 次回傳 `NULL`。一共呼叫 3 次。

**題 3**：輸出 `2`。讀到 `abc` 時 `scanf` 回傳 0，迴圈結束。改成 `!= EOF` 的話：`scanf` 回傳 0，不等於 `EOF`，迴圈繼續；但 `abc` 還留在輸入裡，下一次又失敗、又回傳 0…… **無窮迴圈**。

**題 4**：
- 用 `"w"` 開啟：檔案內容被清空了，而且這個模式不能讀。應該用 `"r"`。
- 沒有檢查 `fopen` 是否回傳 `NULL`。
- 用 `!feof(fp)` 控制迴圈：最後一行會多處理一次。應該寫 `while (fgets(line, sizeof line, fp) != NULL)`。
- 沒有 `fclose(fp)`。

**題 5**：

```c
#include <stdio.h>

int main(void) {
    char line[256];                       /* 200 + '\n' + '\0'，多留一點 */
    int no = 0;
    while (fgets(line, sizeof line, stdin) != NULL) {
        printf("%6d  %s", ++no, line);    /* line 自己帶了 '\n' */
    }
    return 0;
}
```

（最後一行沒有換行時，輸出的最後也不會有換行，和原檔一致。）

**題 6**：輸出被重新導向到檔案時，`stdout` 是 **全緩衝** 的：資料還在緩衝區，程式就當掉了，來不及寫進檔案。避免方法：除錯訊息寫到 `stderr`（不緩衝）；或在重要的輸出後呼叫 `fflush(stdout)`；當然最根本的是用 `--debug`（AddressSanitizer）找出當掉的原因。

**題 7**：文字模式是 `"1000000"`，7 個字元 = **7 bytes**；二進位模式是 `sizeof(int)` = **4 bytes**。
