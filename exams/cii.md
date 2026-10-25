# C 介面與實作讀本考卷

> 涵蓋《C Interfaces and Implementations》讀書筆記第 1 ~ 20 章。題目著重在：每個介面的 **合約**（checked / unchecked runtime error、例外）、**設計取捨**（為什麼這樣設計）、和 **實作技巧**。
> 有程式的「預測輸出」題，答案都是實際用 `gcc -std=c11` 編譯執行的結果（程式只模擬書中模組的關鍵部分，不需要書的原始碼）。

@@@ ch01 | 導論

??? 觀念
文學式程式設計 (literate programming) 裡，`〈name〉≡`、`〈name〉+≡`、`〈double.c〉` 各代表什麼？這種寫法讓程式可以擺脫 C 的哪一個限制？
!!!
- `〈name〉≡`：**定義** 一個程式碼區塊。
- `〈name〉+≡`：把程式碼 **附加** 到已經存在的同名區塊，讓程式可以一點一點地呈現。
- `〈double.c〉`：**根區塊**，用檔名命名，把它展開（抽出所有子區塊）就得到整個原始檔。

好處是程式碼可以依照 **最好理解的順序** 呈現，而不是依照 C 要求的「先宣告再使用」的順序；文字說明取代了傳統的註解。區塊也不必對應任何語法單位，例如 `〈found a word?〉` 可以只是一個運算式。

??? 觀念
作者對「效率」的看法可以濃縮成幾句話。說出至少四個原則，並解釋「直接實作一個本來就快的演算法，勝過手工調校一個慢的演算法」。
!!!
- **夠快就好**：程式只需要 fast enough，不必 as fast as possible。
- **先量測**：程式設計師猜瓶頸出了名地不準；沒有量測數據證明太慢，就不該調校。
- **抓大放小**：I/O 佔 60% 的時間時，把搜尋常式省下 1% 沒有意義。
- **可靠優先**：「最快當掉的程式不是贏家」，交付會當機的快軟體，長期成本比較高。
- **調校有代價**：調校後的程式更大、更難懂、更容易出錯。
- **調校救不了爛設計**：到處都慢，問題出在設計本身。

演算法的層次影響最大：例如把線性搜尋的內迴圈調校得再快，複雜度還是 O(n)；改用二分搜尋直接變成 O(log n)，不需要任何技巧。

??? 觀念
作者說「程式是寫給人讀的」，對命名和註解各有什麼主張？為什麼他說「誤導的註解比沒有註解更糟」？
!!!
- **命名**：全域變數和函式用較長、能說明用途的名字；區域變數用短名字，可以沿用數學記號（`i`、`x`）。名字太長反而會遮住程式在做什麼（例如 `theindex`、`numofElements`）。程序的名字表達它 **做什麼**，函式的名字表達它 **回傳什麼**。
- **註解**：清楚的程式加上好的命名和縮排通常能自己解釋自己。註解只用來說明資料結構的細節、演算法的特殊情況、例外狀況。

誤導的註解更糟，是因為 **編譯器無法檢查註解和程式是否一致**：程式改了、註解沒改，讀者相信註解就會被帶錯方向；沒有註解時，讀者至少會去讀程式本身。

??? 觀念
第 1 章比較了兩種 `strcpy`。解釋指標版的 `while (*dst++ = *src++) ;` 每一步做了什麼、迴圈什麼時候停止，以及為什麼直接修改參數 `dst`、`src` 沒有問題。作者認為哪一版比較好懂？為什麼還是要學指標版？

```c
char *strcpy(char *dst, const char *src) {
    char *s = dst;
    while (*dst++ = *src++)
        ;
    return s;
}
```
!!!
- `*src++`：取出 `src` 指向的字元，然後 `src` 前進一格。
- `*dst++ = ...`：把字元寫到 `dst` 指向的位置，然後 `dst` 前進一格。
- 整個指定運算式的值就是 **剛剛複製的字元**；複製到結尾的 `'\0'` 時值是 0，迴圈停止。所以 `'\0'` 也會被複製到，不用另外補。
- 迴圈本體是空敘述 `;`，所有工作都在條件裡完成。

修改 `dst`、`src` 沒問題，因為 C 的參數是 **傳值**，它們本來就是已經初始化好的區域變數，改它們不影響呼叫者；但函式要回傳目的地的開頭，所以先用 `s` 存起來。

作者 **承認陣列版對所有人都比較好懂**。但指標版是有經驗的 C 程式設計師會寫的慣用寫法，讀別人的程式時最常遇到，要寫得流暢、讀得懂真實世界的 C 程式，就必須熟悉這些慣用寫法。

@@@ ch02 | 介面與實作

??? 預測輸出
下面是 `Arith` 的實作（第 2 章）。在 x86-64（C 的除法向零截斷）上，預測輸出：

```c
#include <stdio.h>

int Arith_div(int x, int y) {
    if (-13/5 == -2 && (x < 0) != (y < 0) && x%y != 0)
        return x/y - 1;
    else
        return x/y;
}

int Arith_mod(int x, int y) {
    if (-13/5 == -2 && (x < 0) != (y < 0) && x%y != 0)
        return x%y + y;
    else
        return x%y;
}

int Arith_ceiling(int x, int y) { return Arith_div(x, y) + (x%y != 0); }

int main(void) {
    printf("%d %d | %d %d\n", -13 / 5, -13 % 5, Arith_div(-13, 5), Arith_mod(-13, 5));
    printf("%d %d %d\n", Arith_div(13, 5), Arith_ceiling(-13, 5), Arith_ceiling(13, 5));
    int N = 5, i = 0;
    printf("%d %d\n", (i - 1) % N, Arith_mod(i - 1, N));
    return 0;
}
```
!!!
```output
-2 -3 | -3 2
2 -2 3
-1 4
```

- C 的 `/` 在這台機器上向零截斷：`-13/5 = -2`，於是 `-13%5 = -3`。
- `Arith_div` 一律 **向數線左邊截斷**（不超過實數商的最大整數）：−2.6 → **−3**；`Arith_mod = x − y·Arith_div(x, y)` = −13 + 15 = **2**。
- `Arith_ceiling(-13, 5)` = ⌈−2.6⌉ = −2；`Arith_ceiling(13, 5)` = ⌈2.6⌉ = 3。
- 讓 `i` 在 0..N−1 循環往回走時，`(i - 1) % N` 在 `i = 0` 得到 **−1**（不能當索引），`Arith_mod` 正確得到 N−1 = 4。

這就是「好的介面會補上語言的語意漏洞」：C 標準允許除法向零或向負無限大截斷，`Arith` 把它定義清楚。

??? 觀念
`stack.h` 裡寫：

```c
#define T Stack_T
typedef struct T *T;
extern void Stack_free(T *stk);
#undef T
```

1. `typedef struct Stack_T *Stack_T;` 達到了哪兩個目的？為什麼型別名稱可以和 struct tag 同名？
2. 為什麼最後要 `#undef T`？
3. 為什麼 `Stack_free` 的參數是 `T *`，不是 `T`？
!!!
1. - **隱藏表示方式**：client 只知道 `Stack_T` 是「指向某個結構的指標」，不知道結構內容，所以不能解參考，只有實作可以。
   - **型別檢查**：傳其他結構的指標進來會編譯錯誤（只有 `void *` 例外）。
   - 可以同名是因為 C 的 **struct tag 和一般識別字分屬不同的名稱空間**。
2. `T` 只是為了讓介面好讀的縮寫。`#undef T` 讓它不會洩漏到 client 的程式裡，client 必須寫完整的 `Stack_T`，也不會和 client 自己的 `T` 衝突。
3. 傳指標的指標，`Stack_free` 才能在釋放後 **把呼叫端的變數設成 NULL**，避免留下懸空指標。全書所有的 `_free` 函式都這樣設計。

??? 分類
第 2 章把錯誤分成三類。說明三類的差別，並把下面每一項歸類：

1. 對空的 `Stack_T` 呼叫 `Stack_pop`
2. `Arith_div(x, 0)`
3. `Stack_push` 時記憶體不足
4. 傳一個不是 `Stack_new` 產生的指標（例如隨便一個 `struct` 的位址轉型）給 `Stack_push`
5. 使用者輸入的檔名不存在，`fopen` 失敗
!!!
| 類別 | 定義 | 能復原嗎 |
|---|---|---|
| **Unchecked runtime error** | 違反合約，實作 **不保證** 偵測得到 | 不能，結果不可預期 |
| **Checked runtime error** | 違反合約，實作 **保證** 偵測到（用 `assert`） | 不能，這是程式的 bug |
| **Exception** | 可能發生但很少見的情況 | **可以**，client 可以處理 |

1. **Checked**：`Stack_pop` 用 `assert(stk->count > 0)` 檢查。
2. **Unchecked**：`Arith` 刻意模仿 C 內建除法的行為，把除以零留成 unchecked（作者也說改成 checked 是合理的設計選擇）。
3. **Exception**：`Mem_Failed`，client 可以用 TRY-EXCEPT 處理。
4. **Unchecked**：實作無法分辨一個指標是不是自己產生的。
5. **都不是**：這是 **可預期的使用者錯誤**，不是程式的 bug，應該用 **回傳值** 處理（runtime error 指的是程式本身的錯誤）。

??? 觀念
有人想把 `int Stack_empty(T stk);` 改成 `int Stack_empty(const T stk);`，表示「這個函式不會修改堆疊」。

1. 這樣寫實際上的意思是什麼？有沒有達到目的？
2. 就算改成 `const struct Stack_T *stk`，作者為什麼還是不用？
!!!
1. `T` 是 `struct Stack_T *` 的 typedef，`const T stk` 的意思是「`stk` 是一個 **常數指標**，指向（可以修改的）結構」，而不是「指向常數結構的指標」。指標本身是傳值的，加不加 `const` 對呼叫者完全沒有差別，**沒有達到目的**。
2. 作者認為 **`const` 會透露實作的資訊、限制其他實作的可能性**。例如某個實作想延後釋放元素以便重複使用，在 `Stack_empty` 被呼叫時才真正釋放，它就需要修改 `*stk`；如果介面承諾了 `const`，這種實作就做不到了。所以全書的 ADT 都不使用 `const`。（Atom 回傳 `const char *` 不衝突，因為 atom 不是不透明指標，`const` 在那裡表達的是「atom 不可修改」這個介面語意。）

@@@ ch03 | 原子字串

??? 觀念
1. Atom 是什麼？為什麼「比較兩個 atom 是否相等」只要比較指標？
2. `Atom_length` 為什麼是 O(atom 總數)？作者為什麼把這件事寫進介面？
3. Atom 有沒有釋放函式？這是什麼取捨？
!!!
1. Atom 是指向一段 **唯一、不可變** 的位元組序列的指標。`Atom_new` 會先查表，同樣內容的序列 **只會存一份**，所以內容相同 ⇔ 指標相同，比較只要 `==`，不用 `strcmp`，也省空間。
2. 雜湊表是用 **內容** 算雜湊值的，但 `Atom_length` 只拿到指標，不知道長度就算不出雜湊值，只能掃過整個表比對指標。作者把它寫進介面，是因為 **效能特性也是合約的一部分**：client 需要知道這個函式很慢。
3. **沒有**，atom 一旦建立就存在到程式結束。用空間換取簡單：作者說 C 程式裡不同字串的數量出奇地少，lcc 編譯器也這樣做。

??? 預測輸出
`Atom_int` 把 `long` 轉成字串時，特別處理了 `LONG_MIN`。下面的程式用同樣的演算法：

```c
#include <limits.h>
#include <stdio.h>

void long_to_str(long n, char *out) {
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
        *--s = m % 10 + '0';
    while ((m /= 10) > 0);
    if (n < 0)
        *--s = '-';
    int len = (int)((str + sizeof str) - s);
    for (int i = 0; i < len; i++) out[i] = s[i];
    out[len] = '\0';
}

int main(void) {
    char buf[64];
    long tests[] = {0, -42, 1234, LONG_MIN};
    for (int i = 0; i < 4; i++) {
        long_to_str(tests[i], buf);
        printf("%s\n", buf);
    }
    return 0;
}
```
說明：(1) 為什麼 `LONG_MIN` 要特別處理？(2) 為什麼用 `unsigned long` 做 `/` 和 `%`？(3) 為什麼字串是從尾端往前填？
!!!
```output
0
-42
1234
-9223372036854775808
```

1. 二補數的範圍 **不對稱**：負數比正數多一個，`-LONG_MIN` 放不進 `long`（溢位是未定義行為）。所以用 **無號運算** `LONG_MAX + 1UL` 得到它的絕對值。
2. 有號整數的 `/`、`%` 對負數的語意不明確（第 2 章的問題）；無號數的 `/`、`%` 定義是清楚的。
3. `m % 10` 先得到 **最低位**，所以從右往左產生數字；`*--s` 讓 `s` 從緩衝區尾端往前移，結束時 `s` 剛好指向字串開頭，**不需要再反轉**。`do-while` 確保 0 也會產生一個 `'0'`。

（43 是怎麼來的：就算 `long` 是 128 位元，用八進位表示也只要 128/3 + 1 = 43 個字元，十進位不會比八進位更長。）

??? 找錯
Atom 的雜湊函式是：

```c
for (h = 0, i = 0; i < len; i++)
    h = (h << 1) + scatter[(unsigned char)str[i]];
```

如果拿掉 `(unsigned char)` 轉型，在什麼機器上會出錯？會發生什麼事？
!!!
C 的 plain `char` **可能有號也可能無號**（由實作決定）。在 `char` 有號的機器上（例如 x86），值大於 127 的位元組（例如 UTF-8 中文、`0xFF`）會變成 **負數**，`scatter[負數]` 就是 **陣列越界**，讀到陣列前面的記憶體，得到垃圾值甚至讓程式當掉。轉成 `unsigned char` 才能保證索引落在 0 ~ 255。

??? 觀念
`Atom_new` 新增 atom 時寫：

```c
p = ALLOC(sizeof (*p) + len + 1);
p->len = len;
p->str = (char *)(p + 1);
```

1. 這三行做了什麼？為什麼不分成兩次配置？
2. 為什麼這裡不能用 `NEW(p)`？
3. 搜尋已經存在的 atom 時，為什麼先比長度、再一個位元組一個位元組地比，而不用 `strncmp`？
!!!
1. **一次配置同時放下結構和字串**：前面是 `struct atom`，緊接在後面的 `len + 1` 個位元組放字串（含結尾的 `'\0'`）。`p + 1` 是結構結束之後的位址，`p->str` 指向那裡。好處是只要一次配置（比較快、比較省空間），而且結構和字串一起存在、一起被釋放（atom 永遠不釋放）。
2. `NEW(p)` 配置的大小是 `sizeof *p`，只適用於 **編譯時就知道大小** 的情況；這裡的大小取決於 `len`，要用 `ALLOC`。
3. - **先比長度**：長度不同就一定不相等，不用逐一比較位元組。
   - **不用 `strncmp`**：atom 可以是 **任意位元組序列**，中間可能包含 `'\0'`；`strncmp` 遇到 `'\0'` 就會停下來，會把兩個只在 `'\0'` 之後不同的序列誤判成相等。

@@@ ch04 | 例外與斷言

??? 預測輸出（觀念）
```c
static Except_T e;
int i = 0;
TRY
    i++;
    RAISE(e);
EXCEPT(e)
    ;
END_TRY;
printf("%d\n", i);
```

這段程式會印出什麼？為什麼？怎麼修正？
!!!
**可能印出 0，也可能印出 1**。

TRY-EXCEPT 是用 `setjmp`/`longjmp` 實作的。標準 C 規定：在 `setjmp` 之後被修改的 **自動（區域）變數**，經過 `longjmp` 回來之後值 **不保證** 保留，因為編譯器可能把它放在暫存器裡，`longjmp` 恢復的是 `setjmp` 當時的暫存器內容。

修正：宣告成 `volatile int i = 0;`，強迫每次都從記憶體讀寫，保證印出 1。

??? 觀念
1. 在 `TRY` 裡面為什麼不能直接用 `return`，必須用 `RETURN`？用了 `return` 是哪一類錯誤？
2. TRY-FINALLY 的 `FINALLY` 區塊什麼時候執行？如果 TRY 裡丟出例外，`FINALLY` 執行完之後會怎樣？
!!!
1. 每個 TRY 會把一個 **例外框架** 推入一個全域的例外堆疊（框架本身是 TRY 所在函式的區域變數）。直接 `return` 會 **跳過 `END_TRY`**，框架沒有被彈出，堆疊頂端留著一個指向 **已經失效的堆疊框架** 的懸空指標；之後丟出例外時，`longjmp` 會跳到一個已經不存在的函式。這是 **unchecked runtime error**，很難除錯。`RETURN` 巨集會先把框架彈出再 `return`。
2. **不管 TRY 的主體有沒有丟出例外，`FINALLY` 都會執行**，用來清理資源（例如關檔）。如果主體丟出了例外，`FINALLY` 執行完之後會 **重新丟出同一個例外**，交給外層的 TRY 處理。

??? 觀念
1. 作者的 `assert` 失敗時做什麼？和標準的 `<assert.h>` 有什麼不同？
2. `void (assert)(int e) { assert(e); }` 為什麼要把函式名稱加上括號？
3. 作者主張正式版的程式 **要保留** assertion，理由是什麼？
!!!
1. 失敗時 **丟出 `Assert_Failed` 例外**，而不是直接 `abort`（也不提供運算式的文字）。沒有被處理時，輸出類似 `Uncaught exception Assertion failed raised at stmt.c:201`，功能上等同於標準的診斷訊息；但 client 可以在最上層用 TRY 接住它，給使用者友善的訊息。
2. `assert` 同時是 **巨集** 和 **函式**。`assert(e)` 這種寫法會被當成巨集呼叫展開；寫成 `(assert)(int e)`，名字後面緊接的不是 `(`，巨集不會展開，才能定義出同名的函式。
3. 拿掉 assertion 不會讓程式更正確，只會讓 bug **更隱蔽**：違反合約的情況照樣發生，只是沒人發現，程式帶著錯誤的狀態繼續跑，可能破壞資料。保留 assertion，加上最上層的 TRY-ELSE，可以安全地發現錯誤並提供有用的訊息。assertion 的成本通常小到可以忽略。

??? 觀念
1. `Except_Frame` 有四種狀態（`Except_entered`、`Except_raised`、`Except_handled`、`Except_finalized`）。為什麼 `Except_entered` **必須是 0**？
2. `Except_raise` 丟出例外時，為什麼要 **先把目前的例外框架從堆疊彈出**，再 `longjmp`？
!!!
1. TRY 用 `Except_flag = setjmp(Except_frame.env);` 判斷現在是哪一種情況。`setjmp` **第一次** 被呼叫（剛進入 TRY）時一定回傳 **0**；之後透過 `longjmp` 回來時回傳非 0 的值（`Except_raised`）。所以「剛進入」這個狀態必須剛好等於 0，才能直接拿 `setjmp` 的回傳值當狀態。
2. 處理程式（EXCEPT 或 ELSE 的區塊）執行時，這個 TRY **已經不再保護** 任何程式碼了。如果處理程式自己又丟出例外（或用 `RERAISE`），應該交給 **外層** 的 TRY 處理。先彈出框架，堆疊頂端就是外層的框架；如果不彈出，新的例外會跳回同一個處理程式，形成無窮迴圈。

@@@ ch05 | 記憶體管理

??? 預測輸出
`Mem` 介面的 `NEW` 和 `FREE` 巨集（這裡改用 `malloc`/`free` 模擬）：

```c
#include <stdio.h>
#include <stdlib.h>

#define NEW(p) ((p) = malloc((long)sizeof *(p)))
#define FREE(ptr) ((void)(free(ptr), (ptr) = 0))

int main(void) {
    int *a[3] = {0, 0, 0};
    int i = 0;
    NEW(a[i++]);
    printf("%d %d %d\n", i, a[0] != NULL, a[1] != NULL);

    NEW(a[1]);
    int j = 0;
    FREE(a[j++]);
    printf("%d %d %d\n", j, a[0] != NULL, a[1] != NULL);
    return 0;
}
```
!!!
```output
1 1 0
2 1 0
```

- `NEW(a[i++])`：`sizeof *(p)` 的運算元 **不會在執行期求值**（只取型別），所以 `a[i++]` 只被求值一次，`i` 是 1，配置給了 `a[0]`。介面特別說明 `NEW` 對參數 **只求值一次**，有副作用也安全。
- `FREE(a[j++])`：`ptr` 出現了 **兩次**，`j++` 執行兩次：`free(a[0])` 之後，被設成 NULL 的卻是 `a[1]`！結果 `a[0]` 變成懸空指標、`a[1]` 的記憶體洩漏。所以介面警告：**不要把有副作用的運算式傳給 `FREE` 和 `RESIZE`**。

??? 觀念
`Mem` 和標準的 `malloc`/`free` 比起來，有哪些改進？說出至少四項，並解釋為什麼參數用 `long` 而不是 `size_t`。
!!!
| 標準函式庫 | `Mem` |
|---|---|
| 配置失敗回傳 NULL（常常忘了檢查） | **丟出 `Mem_Failed`，永遠不回傳 NULL** |
| 大小為 0 的行為由實作決定 | 大小 ≤ 0 是 **checked runtime error** |
| 不知道是誰配置的 | `ALLOC` 等巨集自動帶入呼叫端的 `__FILE__`、`__LINE__`，例外會回報呼叫位置 |
| `free` 之後指標還是舊值（懸空） | `FREE` 把指標 **設成 NULL**，之後誤用會立刻崩潰（確定的錯誤） |
| `realloc` 身兼配置、釋放、改大小三職 | `Mem_resize` 只做改大小一件事 |

**用 `long`**：如果 client 不小心傳了負數（例如 `int n = -1; malloc(n)`），轉成無號的 `size_t` 會變成一個巨大的數，很多 `malloc` 實作抓不到。用有號的 `long`，`Mem_alloc` 就能用 `assert(nbytes > 0)` 抓出來。

??? 觀念
第 5 章有「正式版」和「檢查版」兩種 `Mem` 實作。

1. 同一個錯誤（例如對同一個指標 `Mem_free` 兩次），在兩種實作裡分別屬於哪一類錯誤？
2. 檢查版要偵測「這個指標不是我配置的」和「這個指標已經釋放過了」，核心的想法是什麼？
!!!
1. 正式版是 **unchecked**（直接交給 `free`，不保證偵測得到）；檢查版是 **checked**。**同一個介面，不同實作提供不同強度的保證**，介面裡要寫清楚。除錯時只要換連結檢查版的實作就好，不用改 client 的程式。
2. 兩個要點：
   - **永不重複使用位址**：釋放的區塊不會很快再配置給別人，所以「已釋放」的位址可以一直被辨認出來。
   - **記住每個位址的狀態**：用一個以位址為鍵的 **描述子雜湊表** 記錄每個區塊（位址、大小、是否已釋放、配置位置）。`Mem_free` 時查表：查不到 → 不是我配置的；查到但標記為已釋放 → 重複釋放。兩種都 `assert` 失敗。

??? 觀念
檢查版 `Mem` 的 `Mem_alloc` 用 first-fit 從空閒區塊配置，有三個看起來很奇怪的設計。各是為了什麼？

1. 從空閒區塊的 **尾端** 切下需要的大小，而不是從開頭。
2. 判斷條件寫 `bp->size > nbytes`，而不是 `>=`。
3. **不合併** 相鄰的空閒區塊。
!!!
這三個設計都是為了檢查版的核心目標：**永遠不重複使用同一個位址**，這樣「已經釋放的位址」才能一直被辨認出來（偵測 double free 和存取已釋放的記憶體）。

1. 從尾端切，空閒區塊的 **起始位址 `bp->ptr` 永遠不變**，只有大小變小；切出去的位址都是新的。
2. 用 `>`（嚴格大於），空閒區塊 **永遠至少留下一點**，所以它的起始位址 `bp->ptr` **永遠不會被回傳** 給 client。如果用 `>=`，剛好相等時整塊交出去，這個位址就可能和某個曾經發出去、後來被釋放的位址重複。
3. 合併相鄰的空閒區塊之後，再從合併後的大區塊配置，就可能回傳一個 **以前發出去過的位址**，破壞「永不重複」的保證。代價是記憶體使用效率比較差，但檢查版本來就只用在除錯時。

@@@ ch06 | Arena 區域式配置

??? 觀念
1. Arena 和 `malloc`/`free` 的配置策略根本差別在哪裡？
2. `Arena_free(arena)` 和 `Arena_dispose(&ap)` 有什麼不同？
3. 作者說 arena 「最重要的好處」是什麼？
!!!
1. `malloc` 是以 **大小** 為主，每個物件各自配置、各自釋放；arena 是以 **生命週期** 為主：把 **一起結束** 的物件配置在同一個 arena，最後 **一次全部釋放**，不用逐一 `free`。
2. - `Arena_free(arena)`：釋放 arena 裡自建立（或上次 `Arena_free`）以來配置的 **所有空間**，但 **arena 本身保留**，還能繼續配置。
   - `Arena_dispose(&ap)`：連 arena 本身都銷毀，並把 `*ap` 設成 NULL。
3. **讓程式碼更簡單**：不用記得每個物件什麼時候該 `free`，鼓勵使用 applicative 的演算法（配置新的資料結構，而不是修改既有的），也幾乎不會有洩漏。速度快是附帶的好處。

??? 計算
`Arena_alloc` 會先把請求的大小向上取整到對齊單位的倍數：

```c
nbytes = ((nbytes + sizeof (union align) - 1) / (sizeof (union align))) * (sizeof (union align));
```

假設 `sizeof (union align)` 是 16。依序配置 1、16、17、40 bytes，每次實際用掉多少？總共用掉多少？這個取整為什麼必要？
!!!
- 1 → **16**
- 16 → **16**
- 17 → **32**
- 40 → **48**
- 總共 **112** bytes。

`(n + 15) / 16 * 16` 是「向上取到 16 的倍數」的慣用寫法。必要性：arena 配置就是把 `avail` 指標往後加，下一個物件從上一個物件的結尾開始；如果不取整，下一個物件的位址可能不符合對齊要求（例如 `double` 要 8 的倍數），在某些機器上會讓存取變慢甚至當掉。`union align` 包含各種型別，它的大小就是最嚴格的對齊單位。

??? 觀念
Arena 的缺點有哪些？作者為什麼說它們實務上很少造成問題？
!!!
1. **可能用掉比較多記憶體**：個別物件不能提早釋放，要等整個 arena 一起釋放。
2. **懸空指標**：物件配置在 **太早** 被釋放的 arena 裡，arena 釋放後還在使用它。
3. **洩漏（或說佔用太久）**：物件配置在 **太晚** 才釋放的 arena 裡。

作者說 arena 的管理非常容易（通常一個 arena 對應一個清楚的階段，例如「處理一個函式」、「一個視窗」），所以這些問題很少發生。Arena 是介於 `malloc`/`free` 和垃圾回收之間的一種選擇。

??? 觀念
Arena 的實作有一個 **所有 arena 共用** 的空閒 chunk 串列 `freechunks`。

1. `Arena_free` 釋放的 chunk 為什麼不直接 `free`，而是先放進這個串列？
2. 向 `malloc` 要新 chunk 時，為什麼大小是「header + 這次的請求 + 額外 10 KB」？
3. 從 `freechunks` 取 chunk 的那段程式為什麼是放在 `while` 迴圈裡，而不是 `if`？
!!!
1. 為了 **重複使用**：arena 通常是「配置一批 → 全部釋放 → 再配置一批」的循環（例如每處理一個函式），下次需要 chunk 時直接從串列拿，省掉 `malloc`/`free` 的成本。串列的長度有上限（`THRESHOLD = 10`），超過的才真正 `free`，避免囤積太多記憶體。
2. 多要 10 KB，讓 **之後的配置可以直接在這個 chunk 裡完成**（只是指標加法），不用每次都要新的 chunk；同時至少保證這次的請求放得下（請求很大時 chunk 就跟著變大）。
3. 從 `freechunks` 拿到的 chunk **大小不一定夠**（它當初可能是為比較小的請求配置的）。拿到之後要再檢查一次能不能放下這次的請求，不夠就再取下一個（或向 `malloc` 要），所以是迴圈。

@@@ ch07 | 串列

??? 觀念
大多數 ADT 都隱藏表示方式，`List` 卻在介面裡直接公開 `struct List_T { List_T rest; void *first; };`。作者的理由是什麼？公開之後帶來哪些方便？
!!!
作者認為對這個 ADT 來說，**隱藏帶來的麻煩超過好處**：表示方式極其簡單，很難想像有哪種別的表示方式好到值得隱藏「元素是有兩個欄位的結構」。

公開之後的方便：
1. 可以 **靜態定義並初始化** 串列，不用配置記憶體。
2. 其他結構可以 **內嵌** `struct List_T`。
3. **NULL 就是空串列**，所有函式都接受 NULL。
4. 存取 `first`、`rest` 不需要呼叫函式。

這是「隱藏不是教條，要看值不值得」的具體例子。

??? 找錯
下面的程式想建立一個「串列的串列」，在某些機器上會出錯。為什麼？怎麼改？這屬於哪一類錯誤？

```c
List_T p = List_list(List_list("Atom", NULL),
                     List_list("Mem", NULL),
                     List_list("Arena", NULL), NULL);
```
!!!
`List_list(void *x, ...)` 只有第一個參數有原型（`void *`），**可變參數部分沒有原型提供隱含轉換**，傳進去的是 `List_T`（`struct List_T *`），函式卻用 `va_arg(ap, void *)` 取出。在 `struct` 指標和 `void *` 表示方式不同的機器上就會出錯。（`char *` 和 `void *` 保證表示方式相同，所以字串不用轉型。）

修正：第二個以後的參數要自己轉型：

```c
List_T p = List_list(List_list("Atom", NULL),
                     (void *)List_list("Mem", NULL),
                     (void *)List_list("Arena", NULL), NULL);
```

漏掉轉型是 **unchecked runtime error**。

??? 觀念
1. `List_map(list, apply, cl)` 的 `apply` 拿到的是 `void **x`（`first` 欄位的指標），而不是 `void *`。這代表什麼？
2. `cl` 參數的作用是什麼？
3. `apply` 在走訪時新增或刪除串列的節點，屬於哪一類錯誤？
!!!
1. `apply` 拿到的是 **元素的位置**，所以可以 **修改元素本身**（例如把字串換成對應的 atom：`*x = (void *)Atom_string(*x);`）。
2. `apply` + `cl` 合起來是一個 **閉包 (closure)**：`apply` 指定操作，`cl` 是 client 自帶、跟情境有關的資料（例如要輸出到哪個檔案、累加到哪個變數），`List_map` 不知道它是什麼，只負責原封不動地轉交。C 沒有 lambda，這是傳遞額外資料的標準方法。
3. **Unchecked runtime error**（List 的實作沒有檢查）。

??? 寫程式
`List` 的表示方式是公開的：`struct List_T { List_T rest; void *first; };`，NULL 代表空串列。寫出 **原地反轉** 的 `List_T List_reverse(List_T list)`（不配置任何節點），並說明它是 applicative 還是破壞性的。
!!!
```c
List_T List_reverse(List_T list) {
    List_T head = NULL, next;
    for ( ; list; list = next) {
        next = list->rest;      /* 先記住下一個節點 */
        list->rest = head;      /* 把目前節點接到新串列的前端 */
        head = list;
    }
    return head;
}
```

- 每次從原串列的前端拿下一個節點，接到新串列的前端，原串列就整個反過來了。O(n) 時間、O(1) 額外空間。
- 空串列（NULL）時迴圈不執行，直接回傳 NULL；所有 List 函式都接受 NULL。
- 這是 **破壞性的 (nonapplicative)**：它修改了傳入串列的節點，呼叫之後原本的 `list` 不能再當成原串列使用，要用回傳值：`p = List_reverse(p);`。需要保留原串列時，用 `List_reverse(List_copy(p))`。

@@@ ch08 | 關聯表

??? 觀念
`Table_new(hint, cmp, hash)`：

1. `cmp` 和 `hash` 之間必須滿足什麼條件？
2. 傳 NULL 給 `cmp` 和 `hash` 代表什麼？
3. 雜湊表的實作只需要「相等與否」，為什麼介面要求 `cmp` 回傳 **大小關係**？作者怎麼評價這件事？
!!!
1. **`cmp(x, y) == 0` ⇒ `hash(x) == hash(y)`**。兩個相等的鍵必須落在同一個桶子，否則同一個鍵會被存成兩份、或查不到。
2. 代表 **鍵是 atom**：用內建的雜湊函式，比較時 `x == y` 就相等（atom 的特性）。
3. 為了保留 **多種實作** 的可能：例如用 **平衡樹** 實作時不需要 `hint` 和 `hash`，但需要 `cmp` 的大小順序。作者說這種複雜度是 **允許多種實作所付出的代價**，也是設計好介面之所以困難的原因之一。

??? 觀念
1. `Table_put` 和 `Table_get` 各回傳什麼？這個設計有什麼歧義？
2. 在 `Table_map` 的 `apply` 裡呼叫 `Table_put` 或 `Table_remove` 會怎樣？實作是怎麼偵測的？
3. `Table_free` 會不會釋放鍵和值？正確的釋放順序是什麼？
!!!
1. `Table_put`：鍵已存在就覆蓋，回傳 **舊值**；新增時回傳 **NULL**。`Table_get`：找到回傳值，沒找到回傳 **NULL**。歧義：如果表裡存的值本身就是 NULL，`Table_get` 回傳 NULL 時 **分不出** 是「沒找到」還是「值是 NULL」。介面直接寫明這一點。
2. 是 **checked runtime error**。實作用 **時間戳記 (timestamp)**：表裡有一個計數器，每次 `put`/`remove` 都加 1；`Table_map` 開始時記下計數器的值，每呼叫完一次 `apply` 就檢查計數器有沒有改變，變了就 `assert` 失敗。
3. **不會**。要先用 `Table_map` 走訪一次，釋放每個值（以及非 atom 的鍵），再 `Table_free(&table)`。

??? 觀念
`Table_toArray(table, end)` 回傳的陣列長什麼樣子？要用 `qsort` 依鍵排序時，元素大小該傳什麼？
!!!
陣列有 **2N + 1** 個元素：**鍵在偶數索引、對應的值在下一個奇數索引**，最後一個（索引 2N）是 `end`（通常是 NULL，當哨兵）。順序不指定，client 負責釋放陣列。

用 `qsort` 排序時，要把「一個鍵 + 一個值」當成 **一個元素**：

```c
void **array = Table_toArray(table, NULL);
qsort(array, Table_length(table), 2 * sizeof (*array), compare);
```

元素個數是 N（不是 2N），每個元素的大小是 `2 * sizeof (void *)`，這樣交換時鍵和值才會一起移動。

??? 觀念
`Table_new` 依照 `hint` 從一張質數表（509、1021、2053、4093……）選雜湊表的大小，而第 3 章的 Atom 用的是 2048（2 的冪次）。為什麼兩者不同？
!!!
雜湊表的大小用 **質數**，可以減少「不好的雜湊值」造成的碰撞：如果雜湊值有某種規律（例如都是某個數的倍數、或低位元變化很少），對 2 的冪次取模只會看到 **最低的幾個位元**，很容易全部擠在少數幾個桶子裡；對質數取模則會用到所有位元，分得比較開。

- **Table** 的雜湊函式是 **client 提供的**，Table 無法控制它的品質，所以用質數大小來保護自己。
- **Atom** 的雜湊值是 **自己計算的**（用 `scatter` 隨機數表打亂過，分布已經很均勻），所以可以用比較簡單的 2 的冪次。

（另外 Table 的實作也和 Atom 一樣，用一次 `ALLOC` 同時配置結構和桶子陣列。）

@@@ ch09 | 集合

??? 觀念
1. `Set` 為什麼沒有「補集」運算？第 13 章的 `Bit` 為什麼有？
2. `Set_map` 的 `apply` 拿到的是成員本身（`const void *`），不是成員的指標（不像 `Table_map` 給值的指標）。為什麼這樣設計？
!!!
1. `Set` **不依賴全集**（成員可以是任何東西），沒有全集就無法定義「不在集合裡的所有東西」。`Bit` 是 **固定全集** {0, …, N−1} 的集合，所以補集就是把所有位元反轉。
2. 集合成員存放的位置是由它的 **雜湊值** 決定的。如果允許 `apply` 把成員換成另一個值，新值的雜湊值不同，卻放在舊值的桶子裡，之後就找不到了，集合結構被破壞。所以只給成員本身，不讓 `apply` 替換。

??? 觀念
`Set_union`、`Set_inter`、`Set_minus`、`Set_diff` 四個集合運算：

1. 會不會修改傳入的集合？
2. 參數是 NULL 時代表什麼？兩個參數都是 NULL 時會怎樣？為什麼？
3. 兩個集合是用不同的 `cmp` 建立的，會怎樣？
!!!
1. **不會**，它們是 applicative 的，一定 **建立並回傳新的集合**（即使結果和某個參數一樣，例如 `Set_union(s, NULL)` 回傳 s 的 **複本**）。
2. NULL 被當成 **空集合**。兩個都是 NULL 是 **checked runtime error**，因為新集合需要 `cmp` 和 `hash`，兩個都是 NULL 就無從得知該用哪一組。
3. **Checked runtime error**：兩個集合必須用相同的 `cmp` 和 `hash` 建立，否則「相等」的定義不一致，運算沒有意義。

??? 找錯
第 9 章提醒比較函式要避免用減法。下面的比較函式哪裡有問題？

```c
int intcmp(const void *x, const void *y) {
    return *(int *)x - *(int *)y;
}
```
!!!
兩個 `int` 相減可能 **溢位**，例如 `x = INT_MAX`、`y = -1`，差應該是正的，溢位之後卻可能變成負數（而且有號溢位是未定義行為），比較結果就錯了，集合或表會找不到元素。

安全的寫法：

```c
int intcmp(const void *x, const void *y) {
    int a = *(const int *)x, b = *(const int *)y;
    if (a < b) return -1;
    else if (a > b) return 1;
    else return 0;
}
```

??? 手動模擬
集合 `s = {a, b, c}`、`t = {b, c, d}`（用相同的 `cmp`、`hash` 建立）。寫出下面每個運算的結果：

1. `Set_union(s, t)`
2. `Set_inter(s, t)`
3. `Set_minus(s, t)` 和 `Set_minus(t, s)`
4. `Set_diff(s, t)`
5. `Set_union(s, NULL)`
6. `Set_inter(NULL, NULL)`
!!!
1. 聯集 s + t = **{a, b, c, d}**
2. 交集 s ∗ t = **{b, c}**
3. 差集 s − t = **{a}**（在 s 裡、不在 t 裡）；t − s = **{d}**（差集沒有交換律）
4. 對稱差 s / t = **{a, d}**（只在其中一個裡）
5. NULL 當成空集合，結果是 **s 的複本 {a, b, c}**（一定回傳一個新的集合，不會直接回傳 s）
6. **Checked runtime error**：兩個都是 NULL，無法知道新集合該用哪一組 `cmp` 和 `hash`。

所有集合運算都是 applicative 的：不修改 s、t，回傳新的集合，用完要用 `Set_free` 釋放（但集合裡的成員本身不會被釋放）。

@@@ ch10 | 動態陣列

??? 觀念
1. `Array` 和 `List`、`Table`、`Set` 存放的元素有什麼根本的不同？為什麼這樣設計？
2. `Array_get(a, i)` 回傳什麼？`Array_put(a, i, elem)` 回傳什麼？為什麼 `Array_put` 不像 `Table_put` 回傳舊值？
!!!
1. 其他 ADT 存的是 `void *` 指標；`Array` 的每個元素是 **固定大小（`size` 個位元組）的區塊**，可以直接存 `int`、`double`、結構等任何值。理由是 `Array` 最常被用來 **建構其他 ADT**（例如第 11 章的 Seq），需要這種彈性。
2. - `Array_get` 回傳 **第 i 個元素的指標**（等同於 `&a[i]`），要讀值就解參考：`*(int *)Array_get(a, i)`。
   - `Array_put` 把 `elem` 指向的內容 **複製** 進第 i 個元素，回傳 **`elem`**。
   - 因為元素 **不一定是指標**，長度也任意，沒辦法用一個 `void *` 回傳「舊值」。

??? 找錯
下面的程式有什麼問題？屬於哪一類錯誤？

```c
Array_T a = Array_new(10, sizeof (int));
int *p = Array_get(a, 3);
Array_resize(a, 1000);
*p = 42;
```
!!!
`Array_resize` 可能把底層的陣列 **搬移** 到新的位置，之前 `Array_get` 回傳的指標全部 **失效**，`*p = 42` 寫進已經釋放的記憶體（use-after-free）。這是 **unchecked runtime error**（實作無法偵測）。和 C++ `vector` 重新配置後 iterator 失效是同一個問題。

修正：resize 之後重新呼叫 `Array_get(a, 3)`。

??? 觀念
第 10 章有 `Array` 和 `ArrayRep` 兩個介面。

1. `ArrayRep` 公開了什麼？client 可以做什麼、不可以做什麼？
2. 這種「兩層介面」的設計有什麼好處？誰是 `ArrayRep` 的典型使用者？
!!!
1. 公開 `struct Array_T { int length; int size; char *array; }` 的表示方式。client 可以 **讀** 欄位（而且第 i 個元素的位址保證是 `array + i*size`），但 **不能寫**；只能用 `ArrayRep_init` 初始化。
2. 大部分 client 只用安全的 `Array`（有邊界檢查）；少數 **需要速度、或需要內嵌結構** 的 client 才引用 `ArrayRep`。好處是：
   - 哪些 client 依賴表示方式 **一目了然**（看它有沒有 include `arrayrep.h`）；
   - 表示方式改變時，受影響的範圍最小。

   典型使用者是第 11 章的 **Seq**：它把 `struct Array_T` 直接內嵌在自己的結構裡。

??? 手動模擬
```c
Array_T a = Array_new(3, sizeof (int));   /* 3 個 int */
int v;
v = 1; Array_put(a, 0, &v);
v = 2; Array_put(a, 1, &v);
v = 3; Array_put(a, 2, &v);
Array_T b = Array_copy(a, 5);
Array_resize(a, 2);
```

1. 執行完之後，`a` 和 `b` 各有幾個元素？內容是什麼？
2. `Array_put` 回傳什麼？為什麼 `Array_put(a, 0, &v)` 之後再改 `v`，`a` 的第 0 個元素不會跟著變？
3. 接著呼叫 `Array_get(a, 2)` 會怎樣？
!!!
1. - `b = Array_copy(a, 5)`：新的陣列，前 3 個是 a 的內容，**超過原長度的部分初始化成 0** → `b = [1, 2, 3, 0, 0]`，5 個元素。
   - `Array_resize(a, 2)`：縮小成 2 個 → `a = [1, 2]`。（擴大時新增的元素也會初始化成 0。）
2. 回傳 **`elem`**（也就是 `&v`）。`Array_put` 是用 `memcpy` 把 `v` 的 **位元組複製** 進陣列，陣列裡存的是值的複本，不是指向 `v` 的指標，所以之後改 `v` 不影響陣列。
3. **Checked runtime error**：a 現在只有 2 個元素，索引 2 超出範圍（i 必須在 0 到 length − 1 之間）。

@@@ ch11 | 序列

??? 手動模擬
Seq 用 **環狀緩衝區** 實作：第 i 個值存在陣列的第 `(head + i) % array.length` 個元素。

一個序列的陣列長度是 8，`head = 6`，`length = 4`（值是 A、B、C、D）。

1. A、B、C、D 分別存在陣列的哪一格？
2. 執行 `Seq_addlo(seq, Z)` 之後，`head` 是多少？Z 存在哪一格？`Seq_get(seq, 1)` 是什麼？
3. 再執行 `Seq_remlo(seq)` 兩次，回傳什麼？`head` 和 `length` 變成多少？
!!!
1. A → 格 6、B → 格 7、C → 格 (6+2)%8 = **0**、D → 格 **1**。
2. `addlo` 讓 `head` 往前一格：`head = 5`，Z 存在 **格 5**，`length = 5`。原本所有值的索引都 +1，所以 `Seq_get(seq, 1)` 是 **A**。
3. 第一次回傳 **Z**、第二次回傳 **A**；`head = 7`、`length = 3`（剩下 B、C、D）。

（`Seq_addlo` 在 `head` 是 0 時要變成 `array.length - 1`，實作裡 **明確處理** head 變成負數的情況，不依賴 `%` 對負數的行為。）

??? 觀念
1. Seq 的哪兩個操作 **保證是常數時間**？這個承諾寫在哪裡？
2. 怎麼用 Seq 當作堆疊、佇列？
3. Seq 的結構裡放的是 `struct Array_T array;`（結構本身）而不是 `Array_T array;`（指標）。這需要哪個介面？`Seq_free` 依賴了什麼假設？
!!!
1. `Seq_get` 和 `Seq_put` 保證是常數時間（另外兩端的加入和移除也很快），這個效能承諾寫在 **介面** 裡。
2. - **堆疊**：`Seq_addhi` 放入、`Seq_remhi` 取出。
   - **佇列**：`Seq_addhi` 放入、`Seq_remlo` 取出。
   - 兩端都用就是 **雙端佇列**，`Seq_get`/`Seq_put` 就是陣列。
3. 要內嵌結構本身就必須知道它的定義，所以 Seq 的實作引用了 **`ArrayRep`**（第 10 章的兩層介面）。`Seq_free` 依賴「**`Array_T` 是 Seq 結構的第一個欄位**」：指向 Seq 結構的指標也就是指向內嵌陣列的指標，可以直接交給 `Array_free` 一起釋放；實作用 `assert` 守住這個假設。

??? 觀念
環狀緩衝區滿了要擴大（`expand`）時，為什麼不能只把陣列加倍就好？要做什麼額外的處理？
!!!
值可能 **繞過陣列的尾端**（例如 head 在後半段，後面的值存在陣列開頭）。陣列加倍之後，原本「繞回到格 0」的那些值，在新的長度下位置計算 `(head + i) % 新長度` 就對不上了。

`expand` 的處理：把陣列加倍後，把 **`head` 之後到舊陣列尾端** 的那一段搬到 **新陣列的尾端**，再調整 `head` 指向搬過去的位置。這樣所有值在新的長度下仍然依序排列。

??? 觀念
下面每個需求，應該選 `List`、`Array`、`Seq`、`Ring` 中的哪一個？說明理由。

1. 存放 10 萬個 `double`，偶爾要改變大小，需要用索引快速存取。
2. 存放指標，需要 **用索引常數時間存取**，而且兩端都要能常數時間加入和移除（例如當作雙端佇列）。
3. 存放指標，需要在 **任意位置** 插入和刪除，還需要 **旋轉** 整個序列（例如輪流發牌）。
4. 一個很簡單的、從前端加入和取出的指標堆疊，希望可以用 NULL 表示空的、還可以靜態初始化。
!!!
1. **Array**：元素是固定大小的 **值**（不是指標），可以直接存 `double`；有 `Array_resize`；`Array_get` 是常數時間。
2. **Seq**：介面保證 `Seq_get`/`Seq_put` 是 **常數時間**，`addlo`/`addhi`/`remlo`/`remhi` 都很快（環狀緩衝區實作）。
3. **Ring**：雙向環狀串列，可以在任意位置插入、刪除，`Ring_rotate` 只要移動 head；代價是索引存取不是 O(1)。
4. **List**：表示方式公開、NULL 就是空串列、可以靜態初始化，`List_push`/`List_pop` 就是堆疊。

@@@ ch12 | 環

??? 手動模擬
Ring 用 **位置**（值與值之間的間隙）表示插入點。一個環依序存放 `A B C D E`（索引 0 ~ 4）。

1. 位置 1、3、6、0、−2 分別在哪兩個值之間？
2. 依序執行 `Ring_add(ring, 3, X)`、`Ring_add(ring, 0, Y)`、`Ring_add(ring, -1, Z)` 之後，環的內容是什麼？
3. 為什麼「加入」用位置，「移除」（`Ring_remove(ring, i)`）卻用索引？
!!!
1. - 位置 1：A 的左邊（最前面）。
   - 位置 3：B 和 C 之間。
   - 位置 6：E 的右邊（最後面）。
   - 位置 0：也是最後面。
   - 位置 −2：D 和 E 之間。
2. - `Ring_add(ring, 3, X)`：`A B X C D E`
   - `Ring_add(ring, 0, Y)`（0 = 最後面）：`A B X C D E Y`
   - `Ring_add(ring, -1, Z)`（−1 = 最後一個值的左邊）：`A B X C D E Z Y`
3. 插入的目標是一個 **間隙**（N 個值有 N+1 個間隙），移除的目標是一個 **值**（N 個）。非正位置從尾端算起，不需要知道環的長度，0 永遠代表「最後面」。

??? 手動模擬
環依序存放 `A B C D E F G H`。`Ring_rotate(ring, 3)` 之後，索引 0 ~ 7 依序是什麼？如果改成 `Ring_rotate(ring, -2)` 呢？為什麼實作負數旋轉時要轉換成 `n + length`？
!!!
- `Ring_rotate(ring, 3)`：向右旋轉，每個值的索引 +3（對長度取模），原本索引 0 的 A 變成索引 3：**F G H A B C D E**。
- `Ring_rotate(ring, -2)`：向左旋轉，每個值的索引 −2：原本索引 2 的 C 變成索引 0：**C D E F G H A B**。

實作只要移動 `head`（找到新的第一個節點），不用搬任何節點。負數的 `n` 轉成 `n + length`（向左轉 2 等於向右轉 length − 2），是為了 **避免 `%` 對負數的實作相依行為**（第 2 章的問題）。

??? 觀念
1. Ring 用什麼資料結構實作？為什麼找第 i 個節點最多只要走 N/2 步？
2. 和 Seq 比，Ring 用什麼換了什麼？
!!!
1. **雙向環狀串列**，`head` 指向索引 0 的節點，`head->llink`（往左一步）就是最後一個節點。因為是雙向而且環狀的，找第 i 個節點時可以選擇 **從 head 往右走 i 步** 或 **往左走 N − i 步**，取比較短的那條，最多 N/2 步。
2. Ring 換到的是 **任意位置的插入、刪除**（找到位置之後只要改幾個指標：插入 4 次指標賦值、刪除 2 次）和 **常數時間的旋轉**；付出的代價是 **索引存取不再是 O(1)**（Seq 的 `get`/`put` 是常數時間，但從中間插入要搬移資料）。

??? 手動模擬
環依序存放 `A B C D E`。依序執行下面的操作，寫出每一步的回傳值和環的內容：

```c
Ring_remove(ring, 1);
Ring_remlo(ring);
Ring_addlo(ring, X);
Ring_remhi(ring);
Ring_get(ring, 2);
Ring_put(ring, 0, Y);
```
!!!
| 操作 | 回傳 | 環的內容 |
|---|---|---|
| `Ring_remove(ring, 1)` | **B**（索引 1） | A C D E |
| `Ring_remlo(ring)` | **A** | C D E |
| `Ring_addlo(ring, X)` | X | X C D E |
| `Ring_remhi(ring)` | **E** | X C D |
| `Ring_get(ring, 2)` | **D** | X C D |
| `Ring_put(ring, 0, Y)` | **X**（舊值） | Y C D |

注意 `Ring_remove` 的參數是 **索引**（值本身，0 ~ N−1），不是位置；`Ring_put` 和 `Seq_put` 一樣回傳被換掉的舊值。

@@@ ch13 | 位元向量

??? 手動模擬
```c
Bit_T s = Bit_new(10);      /* 全集 {0..9}，一開始全是 0 */
Bit_set(s, 2, 5);
Bit_not(s, 4, 7);
int old = Bit_put(s, 3, 0);
```

執行完之後，`s` 代表哪個集合？`Bit_count(s)` 和 `old` 是多少？補集要怎麼寫？
!!!
- `Bit_set(s, 2, 5)`：範圍 **含兩端**，集合是 {2, 3, 4, 5}。
- `Bit_not(s, 4, 7)`：4、5 變 0，6、7 變 1 → {2, 3, 6, 7}。
- `Bit_put(s, 3, 0)`：把 3 清掉，**回傳舊值** `old = 1` → {2, 6, 7}。
- `Bit_count(s)` = **3**。
- 補集：`Bit_not(s, 0, Bit_length(s) - 1);` → {0, 1, 3, 4, 5, 8, 9}。

??? 觀念
`Bit_map` 的 `apply` **可以修改** 位元向量，而 `Table_map`、`Set_map` 的 `apply` 修改表或集合是 checked runtime error。為什麼 Bit 可以？介面對「修改」有什麼額外的規定？這讓實作少了什麼最佳化？
!!!
位元向量的結構是 **固定的**（長度建立後就不變），修改一個位元不會改變任何連結結構，走訪不會出問題；而 Table、Set 增刪成員會改變串列，可能讓走訪中的指標懸空。

規定：從第 0 個位元開始依序呼叫 `apply`；如果處理第 n 個位元時，`apply` 改了第 k 個位元（k > n），**之後的呼叫會看到新值**。

因此實作 **不能** 先把一整個位元組（或 word）讀進區域變數再逐位處理（位元組快取的最佳化），必須每次都從向量本身讀取，才能看到 `apply` 剛做的修改。

??? 觀念
Bit 的實作同時用 `bytes`（`unsigned char *`）和 `words`（`unsigned long *`）兩種方式看同一塊記憶體。各用在什麼操作？為什麼「多出來的位元」必須保持 0？
!!!
- **`bytes`**：單一位元的存取（`get`/`put`）、範圍操作的遮罩，以及 `Bit_count` 的 **查表**（每個位元組拆成兩個 4 位元，用 16 個元素的表查 1 的個數）。
- **`words`**：集合運算（聯集、交集、差集）和比較，**一次處理一整個 word**（例如 64 個位元），比逐位元組快得多。

長度不一定剛好是 word 的倍數，最後一個 word 會有 **不屬於集合的多餘位元**。如果它們不是 0，`Bit_count` 會多算、`Bit_eq` 比較兩個 word 時會誤判不相等。所以所有操作都必須維持「多出來的位元是 0」這個不變式（例如 `Bit_not` 只能反轉範圍內的位元）。

??? 手動模擬
全集大小 8（`Bit_new(8)`），`s = {1, 3}`、`t = {1, 3, 5}`。寫出下面每個呼叫的結果：

1. `Bit_lt(s, t)`、`Bit_leq(t, s)`、`Bit_eq(s, t)`
2. `Bit_inter(s, t)`、`Bit_minus(t, s)`、`Bit_diff(s, t)`
3. `Bit_union(s, NULL)`、`Bit_union(NULL, NULL)`
4. 對 s 做 `Bit_not(s, 0, 7)` 之後，`Bit_count(s)` 是多少？
!!!
1. `Bit_lt(s, t)` = **1**（s 是 t 的 **真子集**）；`Bit_leq(t, s)` = **0**（t 有 5，s 沒有）；`Bit_eq(s, t)` = **0**。
2. - 交集（AND）**{1, 3}**
   - t − s（`t & ~s`）**{5}**
   - 對稱差（XOR）**{5}**

   都回傳新的位元向量。
3. `Bit_union(s, NULL)`：NULL 當成空集合，回傳 **s 的複本**。`Bit_union(NULL, NULL)`：**checked runtime error**，需要至少一個參數來決定結果的長度。
4. 補集是 {0, 2, 4, 5, 6, 7}，`Bit_count` = **6**。

（s 和 t 長度不同時，比較和集合運算都是 checked runtime error。）

@@@ ch14 | 格式化輸出

??? 觀念
作者列出 `printf` 系列的四個缺點，`Fmt` 解決了其中哪三個？各用什麼方法？
!!!
四個缺點：
1. 格式碼固定，不能擴充；
2. 輸出目的地固定（檔案或字串）；
3. `sprintf` 可能緩衝區溢位；
4. 沒有型別檢查。

Fmt 解決了前三個：
1. **可擴充**：`Fmt_register(code, cvt)` 註冊自訂的格式碼（例如 AP 的 `%D`），回傳舊的轉換函式。
2. **任意輸出目的地**：核心函式 `Fmt_fmt(put, cl, fmt, ...)` 每產生一個字元就呼叫 `put(c, cl)`，輸出可以導向檔案、字串、網路、甚至只是計算長度的函式。
3. **不會溢位**：`Fmt_sfmt(buf, size, ...)` 超過大小就丟出 `Fmt_Overflow`；`Fmt_string` 自動配置剛好夠大的字串（client 負責釋放）。

第 4 個（型別檢查）在 C 的可變參數機制下無法解決。

??? 觀念
`Fmt_fmt((int (*)(int, void *))fputc, stdout, "...", ...)` 可以直接用 `fputc` 當 `put` 函式。

1. 為什麼 `put` 被設計成回傳 `int`（Fmt 根本不用這個回傳值）？
2. 為什麼需要轉型？這種用法在什麼條件下才正確？
!!!
1. 為了讓標準函式 **`fputc` 可以直接當 `put` 用**：`fputc` 的回傳型別是 `int`。
2. `fputc` 的型別是 `int (*)(int, FILE *)`，而 `put` 要求 `int (*)(int, void *)`，第二個參數的型別不同，所以要轉型。透過轉型後的函式指標呼叫，只有在 **`FILE *` 和 `void *` 的表示方式相同** 的機器上才正確（實際上幾乎所有機器都是）。

??? 觀念
1. Fmt 的轉換函式型別 `Fmt_T` 的參數裡，為什麼是 `va_list *app`（指標），而不是 `va_list ap`？
2. 轉換函式裡要取得一個 `char` 參數時，為什麼要寫 `va_arg(*app, int)` 而不是 `va_arg(*app, char)`？
3. width 或 precision 的值是 `INT_MIN` 為什麼是 checked runtime error？
!!!
1. 一個格式字串裡有很多個轉換，每個轉換函式都要從 **同一個** 參數串列依序取出參數。傳指標，轉換函式取走參數之後，`Fmt_vfmt` 那邊的 `va_list` 也跟著前進，下一個轉換才會拿到下一個參數。（直接傳 `va_list` 的值，在某些平台上取走的參數不會反映回呼叫者。）
2. 可變參數會經過 **預設參數提升**：`char`、`short` 會被提升成 `int`、`float` 提升成 `double`。所以 `%c` 的參數實際上是以 `int` 傳進來的，用 `va_arg(*app, char)` 是未定義行為。
3. Fmt 用 `INT_MIN` 這個值來 **表示「沒有指定」** width 或 precision，所以 client 不能真的傳入這個值，否則會和「沒指定」混淆。

??? 寫程式
寫一個 Fmt 轉換函式 `cvt_b`，把 `unsigned` 參數用 **二進位** 印出來（例如 10 印成 `1010`，0 印成 `0`），並支援寬度和對齊（交給 `Fmt_puts` 處理），再寫出註冊和使用它的程式碼。
!!!
```c
static void cvt_b(int code, va_list *app,
        int put(int c, void *cl), void *cl,
        unsigned char flags[], int width, int precision) {
    unsigned m = va_arg(*app, unsigned);      /* 取出參數，*app 會前進 */
    char buf[sizeof m * 8];                   /* 每個位元一個字元 */
    char *p = buf + sizeof buf;
    do
        *--p = (m & 1) + '0';                 /* 從最低位往前填 */
    while ((m >>= 1) != 0);
    Fmt_puts(p, (buf + sizeof buf) - p, put, cl, flags, width, precision);
}

Fmt_register('b', cvt_b);                     /* 回傳舊的轉換函式（這裡是 NULL） */
Fmt_print("[%b] [%8b] [%-8b]\n", 10u, 5u, 5u);  /* [1010] [     101] [101     ] */
```

- 轉換函式的簽名必須是 `Fmt_T`。
- 用 `va_arg(*app, unsigned)` 取參數：型別錯誤（例如傳了 `long`）是 unchecked runtime error。
- 和 `Atom_int` 一樣從尾端往前填，就不用反轉。`do-while` 確保 0 也會輸出一個 `0`。
- 寬度、`-` 旗標、精確度（截斷）都交給 `Fmt_puts`，不用自己處理。

@@@ ch15 | 低階字串

??? 預測輸出
Str 介面用 **位置** 表示子字串，`Str_sub(s, i, j)` 回傳位置 i、j 之間的子字串。下面的程式用書中的 `idx` 巨集把位置轉成索引：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define idx(i, len) ((i) <= 0 ? (i) + (len) : (i) - 1)

char *Str_sub(const char *s, int i, int j) {
    int len = strlen(s);
    i = idx(i, len);
    j = idx(j, len);
    if (i > j) { int t = i; i = j; j = t; }
    char *str = malloc(j - i + 1);
    memcpy(str, s + i, j - i);
    str[j - i] = '\0';
    return str;
}

int main(void) {
    const char *s = "Interface";
    int pos[][2] = {{6, 10}, {0, -4}, {-4, 6}, {1, 0}, {3, 3}, {2, 5}, {-9, -6}, {4, -5}};
    for (int k = 0; k < 8; k++) {
        char *t = Str_sub(s, pos[k][0], pos[k][1]);
        printf("[%s]", t);
        free(t);
    }
    printf("\n");
    return 0;
}
```
!!!
```output
[face][face][][Interface][][nte][Int][e]
```

`"Interface"` 的位置（位置是 **字元之間** 的間隙）：

```
正位置：    1   2   3   4   5   6   7   8   9   10
字元：        I   n   t   e   r   f   a   c   e
非正位置： −9  −8  −7  −6  −5  −4  −3  −2  −1   0
```

- `[6:10]` 和 `[0:-4]` 都是 `face`：**兩個位置的順序可以顛倒**。
- `[-4:6]`：位置 −4 和位置 6 是 **同一個間隙**（r 和 f 之間），所以是空字串。
- `[1:0]`：從最左到最右，**整個字串**。
- `[3:3]`：兩個位置相同，空字串。
- `[2:5]`：n 的左邊到 r 的左邊 → `nte`。
- `[-9:-6]`：最左邊到 e 的左邊 → `Int`。
- `[4:-5]`：e 的左邊到 e 的右邊 → `e`（正、非正位置可以混用）。

`idx` 把正位置 i 轉成索引 i − 1（位置 i 右邊那個字元的索引），非正位置 i 轉成 i + len。

??? 觀念
Str 的搜尋函式（`Str_chr`、`Str_find`……）和跨越函式（`Str_many`、`Str_rmatch`……）失敗時都回傳 **0**。下面這行去掉字串尾端空白的程式，如果 `name` 尾端 **沒有** 空白，會發生什麼事？為什麼「失敗回傳 0」是一個巧妙的設計？

```c
char *t = Str_sub(name, 1, Str_rmany(name, 1, 0, " \t"));
```
!!!
`Str_rmany` 從右邊跨過一段屬於 `" \t"` 的字元，回傳那段字元 **之前** 的位置。尾端沒有空白時，跨不過任何字元，回傳 **0**。結果變成 `Str_sub(name, 1, 0)`，而位置 0 代表「最右邊」，所以得到的正好是 **整個字串**，正是想要的結果。

巧妙之處：成功時回傳正位置，失敗時回傳 0，而 0 剛好是一個 **合法而且有意義** 的位置（字串的右端）。很多情況下「沒找到」時希望的結果就是「到結尾為止」，所以根本 **不需要特別處理失敗的情況**。例如 `basename` 裡，沒有 `/` 時 `Str_rchr` 回傳 0，`0 + 1 = 1` 剛好是字串開頭；沒有副檔名時 `Str_rmatch` 回傳 0，剛好是字串結尾。

??? 觀念
和 `<string.h>` 比起來，Str 的函式有什麼主要的不同？付出了什麼代價？
!!!
- `<string.h>` 的函式（`strcpy`、`strcat`）要求 **client 自己準備結果的空間**，而且不檢查大小，很容易 **緩衝區溢位**。
- Str 建立字串的函式（`Str_sub`、`Str_cat`、`Str_dup`……）**自己配置結果的空間**，剛好夠大，所以不會溢位；位置參數也會被檢查（指定不存在的子字串是 checked runtime error）。

代價：每次建立字串都要 **配置記憶體**（比較慢），而且 client 仍然要負責 **釋放** 回傳的字串。查詢資訊和搜尋的函式（`Str_len`、`Str_find`……）則不配置記憶體。

??? 計算
`s = "The rain in Spain"`（長度 17）。寫出下面每個呼叫的回傳值（都是 **位置**，失敗回傳 0）：

1. `Str_find(s, 1, 0, "ain")`、`Str_rfind(s, 1, 0, "ain")`
2. `Str_chr(s, 1, 0, 'S')`
3. `Str_upto(s, 1, 0, "aeiou")`
4. `Str_many(s, 1, 0, "Teh")`
5. `Str_match(s, 1, 0, "The ")`、`Str_match(s, 1, 0, "the")`
!!!
字元的索引是 0 ~ 16，位置 p 在索引 p − 1 那個字元的 **左邊**。

1. `"ain"` 第一次出現在索引 5（rain 的 a），回傳它左邊的位置 **6**；最後一次在索引 14（Spain 的 a），`Str_rfind` 回傳 **15**。（`r` 系列從右邊找，但回傳的仍然是目標 **左邊** 的位置。）
2. `'S'` 在索引 12 → **13**。
3. 第一個母音是 `'e'`（索引 2）→ **3**。
4. `Str_many` 跨過開頭一段連續屬於 `"Teh"` 的字元：T、h、e 都是，空白不是，跨過 3 個字元，回傳它們 **之後** 的位置 **4**。
5. s 以 `"The "` 開頭，回傳它 **之後** 的位置 **5**；`"the"` 大小寫不同，不符合，回傳 **0**。

@@@ ch16 | 高階字串

??? 觀念
`Text_T` 的表示方式是 `struct { int len; const char *str; }`，而且以 **傳值** 的方式傳遞。

1. 和 C 字串比起來，有哪三個不同？
2. 為什麼 `Text_sub` 不需要配置記憶體？client 可以假設子字串和原字串一定共用記憶體嗎？
3. 為什麼 Text 的函式從來不配置描述子？
!!!
1. - 長度存在描述子裡，取得長度是 **O(1)**（C 字串要 `strlen`，O(N)）。
   - `str` **不以 NUL 結尾**，字串裡 **可以包含 NUL**。
   - 字串是 **不可變** 的（修改 `Text_T` 描述的字元是 unchecked runtime error）。
2. 字串不會被修改、也不需要 NUL 結尾，所以子字串只要一個新的描述子：`str` 指向子字串的第一個字元、`len` 是子字串的長度，**和原字串共用字元**。但 client **不能假設一定共用**，因為 Text 可能對空字串、單一字元字串做特別處理（例如指向共用的常數）。
3. 描述子只有兩個 word，以 **傳值** 的方式傳遞和回傳很便宜，所以根本不需要在堆積上配置描述子，也就不用管描述子的記憶體。

??? 找錯
```c
static char editmsg[] = "Last edited by: ";
Text_T msg = Text_box(editmsg, sizeof (editmsg));
```

這樣建立的 `msg` 有什麼問題？`Text_box` 和 `Text_put` 有什麼不同？
!!!
`sizeof (editmsg)` 包含了結尾的 `'\0'`，所以 `msg.len` 比實際的文字多 1，**NUL 字元被當成字串的一部分**（Text 允許字串裡有 NUL），之後串接或輸出時會多出一個 NUL。應該寫 `sizeof (editmsg) - 1`。

- `Text_box(str, len)`：**不複製**，直接把 client 的字元陣列「裝箱」成描述子。用於常數字串或 client 自己配置的字串。
- `Text_put(str)`：把 C 字串 **複製** 到 Text 管理的字串空間，可能丟出 `Mem_Failed`。

??? 觀念
1. 字串空間由 Text 管理，client 可以用 `free` 釋放 `Text_T` 的字元嗎？那 Text 的字串空間要怎麼回收？
2. `Text_cat(s1, s2)` 在什麼情況下可以 **完全不複製**？
!!!
1. **不行**，用 `free`、`Mem_free` 釋放 Text 的字串是 unchecked runtime error。Text 用類似 arena 的方式管理字串空間，提供 **堆疊式** 的回收：`Text_save()` 記下目前字串空間的位置，`Text_restore(&save)` 把在那之後配置的字串 **一次全部釋放**。
2. 如果 **s2 在記憶體中緊接在 s1 後面**（`s1.str + s1.len == s2.str`，例如兩者原本就是同一個字串相鄰的兩段子字串），串接的結果就是一個從 s1 開始、長度 `s1.len + s2.len` 的描述子，**一個字元都不用複製**。另外，如果 s1 剛好在字串空間的 **最尾端**（`isatend` 檢查），只要把 s2 複製接在後面，不用複製 s1。這是 Text 實作「盡量不複製」的核心技巧。

??? 觀念
`char *Text_get(char *str, int size, Text_T s)` 把 Text 轉成 C 字串。

1. `str` 不是 NULL 時，`size` 至少要多大？太小會怎樣？
2. `str` 是 NULL 時會發生什麼事？誰負責釋放？
3. 為什麼需要這個函式？直接用 `s.str` 當 C 字串有什麼問題？
!!!
1. 至少 **`s.len + 1`**（要放得下所有字元和結尾的 `'\0'`）。太小是 **checked runtime error**。字元會被複製到 `str[0..size-2]` 並補上 `'\0'`。
2. `Text_get` 會用 `Mem_alloc` **自動配置** 剛好夠大的空間並回傳，**client 負責釋放**（用 `FREE`）。
3. Text 的字串 **不以 `'\0'` 結尾**，而且可能和別的字串共用字元（`s.str` 後面緊接著的可能是其他字串的內容）；把 `s.str` 直接交給 `printf("%s")`、`strcmp` 等 C 函式，會一直讀到某個 `'\0'` 才停，讀到不屬於這個字串的內容。另外 Text 的字串不可修改，C 函式可能會修改它。所以要先 **複製** 成一個獨立的、以 `'\0'` 結尾的 C 字串。

@@@ ch17 | 擴展精度算術 XP

??? 預測輸出
XP 用底數 256、**最低位在前** 的 `unsigned char` 陣列表示無號大整數。下面的 `xp_add` 是 `XP_add` 的核心邏輯（z = x + y + carry，回傳最高位的進位）：

```c
#include <stdio.h>

int xp_add(int n, unsigned char *z, const unsigned char *x, const unsigned char *y, int carry) {
    for (int i = 0; i < n; i++) {
        carry += x[i] + y[i];
        z[i] = carry % 256;
        carry /= 256;
    }
    return carry;
}

void show(int n, const unsigned char *z) {
    unsigned long v = 0;
    for (int i = n - 1; i >= 0; i--) v = v * 256 + z[i];
    for (int i = 0; i < n; i++) printf("%d ", z[i]);
    printf("= %lu\n", v);
}

int main(void) {
    unsigned char x[3] = {255, 255, 0}, y[3] = {1, 0, 0}, z[3];
    int c = xp_add(3, z, x, y, 0);
    printf("carry %d: ", c);
    show(3, z);
    c = xp_add(2, z, x, y, 0);
    printf("carry %d: ", c);
    show(2, z);
    unsigned char big[4] = {255, 255, 255, 127};
    show(4, big);
    return 0;
}
```
!!!
```output
carry 0: 0 0 1 = 65536
carry 1: 0 0 = 0
255 255 255 127 = 2147483647
```

- 65535 是 `{255, 255, 0}`，加 1：最低位 255 + 1 = 256，寫 0 進 1；下一位 255 + 0 + 1 = 256，寫 0 進 1；最高位 0 + 1 = 1 → `{0, 0, 1}` = 65536，最後沒有進位。
- 同樣的運算只用 **2 位數**（n = 2）：結果 `{0, 0}` 放不下，回傳 **進位 1**，代表結果溢出了 n 位數。XP 不檢查也不配置記憶體，溢位只靠回傳值告訴你。
- 2³¹ − 1 = 2147483647 的底數 256 表示，最低位在前是 `{255, 255, 255, 127}`。

**最低位在前** 是實作算術最方便的順序：加、減、乘都是從低位往高位進位，陣列索引從 0 往上走就好。

??? 觀念
1. XP 為什麼選底數 2⁸ = 256？
2. XP 幾乎沒有 checked runtime error、也不配置記憶體，作者為什麼刻意把它設計得這麼「危險」？
3. `XP_tostr` 有什麼副作用需要注意？
!!!
1. 長除法估計商的時候要計算三位數的中間值，需要 **b³ − 1 放得進 32 位元的 `unsigned long`**，所以 b ≤ 1625。在這個限制下，256 是最大的、而且剛好是內建型別（`unsigned char`）大小的 2 的冪次，每一位數就是一個位元組，換算和位移都很方便。
2. XP 的使用者是 **AP 和 MP**（更高層的介面），不是一般的應用程式。高層會負責配置和檢查，XP 只追求 **速度**；簡單、不配置記憶體的介面也方便用 **組合語言** 實作來加速。安全和便利交給上層，這是 **分層設計**：低層求快，高層求安全。
3. `XP_tostr` 透過不斷除以 base 來產生數字，**會把輸入的 x 清成 0**（破壞輸入）。所以 AP 的 `AP_tostr` 會先 **複製** 一份再呼叫它。

??? 計算
用底數 256、最低位在前的表示法：

1. 十進位的 1000 是什麼？
2. `{0, 0, 1}` 乘以 `{2}`（一位數）是什麼？
3. 兩個 n 位數相乘，結果最多有幾位數？`XP_mul(z, n, x, m, y)` 做的是 `z = x · y` 還是別的？
!!!
1. 1000 = 3 × 256 + 232 → **`{232, 3}`**。
2. `{0, 0, 1}` = 65536，乘以 2 = 131072 = 2 × 65536 → **`{0, 0, 2}`**。
3. n 位數乘 m 位數最多 **n + m** 位數（所以 z 要有 n + m 位數的空間）。`XP_mul` 做的是 **z = z + x · y**（累加到 z 上），所以呼叫前要先把 z 清成 0；它回傳擴增後乘積最高位的進位。

??? 預測輸出
XP 的減法 `z = x − y − borrow`（底數 256、最低位在前），回傳最高位的借位。下面是同樣的演算法：

```c
#include <stdio.h>

#define BASE 256

int xp_sub(int n, unsigned char *z, const unsigned char *x, const unsigned char *y, int borrow) {
    for (int i = 0; i < n; i++) {
        int d = (x[i] + BASE) - borrow - y[i];    /* 先加 BASE，d 一定不是負數 */
        z[i] = d % BASE;
        borrow = 1 - d / BASE;                    /* d < BASE 代表借了位 */
    }
    return borrow;
}

void show(int n, const unsigned char *z) {
    for (int i = 0; i < n; i++) printf("%d ", z[i]);
}

int main(void) {
    unsigned char x1[2] = {0, 1}, y1[2] = {1, 0}, z[2];
    int b = xp_sub(2, z, x1, y1, 0);
    show(2, z);
    printf("borrow %d\n", b);
    unsigned char x2[2] = {1, 0}, y2[2] = {2, 0};
    b = xp_sub(2, z, x2, y2, 0);
    show(2, z);
    printf("borrow %d\n", b);
    return 0;
}
```
!!!
```output
255 0 borrow 0
255 255 borrow 1
```

- 第一組：x = `{0, 1}` = 256，y = 1。最低位 0 − 1 不夠減，借 1：(0 + 256) − 1 = 255，借位 1；下一位 1 − 0 − 1 = 0 → `{255, 0}` = 255，最後沒有借位。
- 第二組：x = 1、y = 2，x < y。結果「繞回」成 2¹⁶ − 1 = `{255, 255}`，**回傳借位 1**，代表 y > x（無號數算不出負數）。
- 每一位先加上 BASE 再減，所以中間值 `d` 一定不是負數，不必依賴 C 對負數 `/`、`%` 的行為。

@@@ ch18 | 任意精度算術 AP

??? 觀念
1. AP 和 XP 有哪三個主要的不同？
2. AP 的每個運算都回傳一個 **新配置** 的 `AP_T`。下面的程式有什麼問題？怎麼改？
```c
AP_T x = AP_new(2), y = AP_new(3);
AP_T z = AP_add(AP_mul(x, x), AP_mul(y, y));   /* z = x² + y² */
```
!!!
1. - **有號**：AP 用「符號 + 大小」表示，XP 只有無號。
   - **任意精度**：大小會自動成長，不會溢位；XP 是固定 n 位數。
   - **安全**：AP 自己配置記憶體，並檢查所有錯誤（傳 NULL、除以 0 等是 checked runtime error）；XP 幾乎不檢查。
   - AP 是 **不透明指標** 的 ADT，XP 的 `XP_T` 就是公開的 `unsigned char *`。
2. `AP_mul(x, x)` 和 `AP_mul(y, y)` 回傳的兩個 **中間結果** 沒有被任何變數接住，再也無法釋放 → **記憶體洩漏**。要分開寫：
```c
AP_T x2 = AP_mul(x, x), y2 = AP_mul(y, y);
AP_T z = AP_add(x2, y2);
AP_free(&x2);
AP_free(&y2);
```

??? 計算
AP 的除法 **向左截斷**（和第 2 章的 `Arith` 一致），所以除數是正數時餘數永遠是正的。

1. `AP_div(-13, 5)` 和 `AP_mod(-13, 5)` 是多少？（以 C 內建除法向零截斷來比較。）
2. 實作上，AP 先用 XP 算出 **大小** 的商和餘數（|−13| ÷ 5 = 2 餘 3），在什麼情況下要調整？怎麼調整？
!!!
1. 實數商是 −2.6，向左截斷 → **商 −3**，餘數 −13 − 5 × (−3) = **2**。（C 內建的 `-13 / 5` 是 −2、`-13 % 5` 是 −3。）
2. 當 **x、y 異號而且餘數不是 0** 時要調整：商的大小 **加 1**（2 → 3，符號是負的，得到 −3），餘數改成 **|y| − r**（5 − 3 = 2）。

??? 觀念
1. AP 的表示方式 `{sign, ndigits, size, digits}` 為什麼規定 **零只有 +0** 而且 **永遠正規化**（沒有多餘的前導零）？
2. 計算 xʸ mod p 時，為什麼要用快速冪加上「每一步都取模」？
!!!
1. 為了讓每個值 **只有一種表示方式**：如果 0 可以是 +0 或 −0、或 5 可以有前導零，比較、相加的程式就要處理很多等價的情況，容易出錯。規定唯一的表示方式之後，例如「是不是 0」只要看 `ndigits == 1 && digits[0] == 0`，比較大小時也可以先比位數。代價是每個運算結束時都要正規化，而且加減法要特別處理結果是 0 的符號。
2. - **快速冪**（反覆平方）：只需要 O(log y) 次乘法，而不是 y − 1 次。
   - **每一步都取模**：讓中間值保持在 p² 以下。否則 xʸ 本身可能有天文數字的位數，計算時間和記憶體都會爆炸。

??? 計算
`AP_toint(x)` 回傳一個和 x **同號**、大小是 **|x| mod (LONG_MAX + 1)** 的 `long`。在 `long` 是 64 位元（LONG_MAX = 2⁶³ − 1）的機器上，下面每個 AP_T 呼叫 `AP_toint` 會得到什麼？

1. x = 12345
2. x = 2⁶³ + 5
3. x = −(2⁶³ + 5)
4. x = 2⁶³
5. 為什麼不乾脆在 x 放不進 `long` 時丟出例外或當成錯誤？
!!!
1. **12345**（放得進 `long`，值不變）。
2. |x| mod 2⁶³ = **5**。
3. 同號 → **−5**。
4. 2⁶³ mod 2⁶³ = **0**。
5. 這個定義讓 `AP_toint` **對任何 AP_T 都有定義**，不會失敗，client 可以用它取得「低位的部分」（類似 C 的整數截斷）。需要確認數值放得下的 client，可以先用比較函式（例如和 `LONG_MAX` 比較）檢查。介面的選擇是把「範圍檢查」留給需要的 client，而不是對所有呼叫都強制檢查。

@@@ ch19 | 多精度算術 MP

??? 觀念
1. MP 和 AP 最大的差別是什麼？`MP_set(n)` 做了什麼？
2. 為什麼 MP 幾乎不需要配置記憶體，而且任何 `MP_T` 都可以同時當來源和目的（例如 `MP_add(z, z, z)`）？
!!!
1. - AP 是 **任意精度**（自動成長）、符號 + 大小。
   - MP 是 **固定 n 位元**：無號整數和 **二補數** 有號整數都支援，可以精確 **模擬 n 位元的機器算術**。

   `MP_set(n)` 設定之後所有運算的位元數（全域設定，預設 32），回傳之前的值。
2. `MP_set` 時就 **預先配置好暫存空間**：因為某些運算（例如乘除法）需要的暫存空間只取決於 n，可以一次配置好、所有運算共用。運算時先在暫存空間算出結果再複製到目的地，所以來源和目的重疊也沒關係，也不需要每次配置記憶體（除了 `MP_set`，只有少數幾個函式會配置）。

??? 計算
`MP_set(8)` 之後（8 位元）：

1. `MP_fromintu(z, 0xFFF)`：z 會是多少？會發生什麼事？
2. 有號加法 `100 + 100`：8 位元的結果的位元是什麼？當成二補數有號整數是多少？怎麼偵測到溢位？
3. client 想要「溢位時就截斷，不要當成錯誤」，該怎麼寫？
!!!
1. 0xFFF 放不進 8 位元。MP 的原則是 **先算出並設定好結果，再丟出例外**：z 被設成截斷後的 **0xFF**（255），然後丟出 **`MP_Overflow`**。
2. 100 + 100 = 200 = **11001000₂**（0xC8）。當成 8 位元二補數，最高位（符號位元）是 1，代表 200 − 256 = **−56**。偵測方法：兩個運算元 **同號**（都是正的），結果的符號卻 **不同**（變成負的）→ 溢位。二補數的好處是有號加減法可以直接用無號的 XP 運算，只要比較運算元和結果的符號位元。
3. 用 TRY-EXCEPT 接住並忽略 `MP_Overflow`，因為結果已經是截斷後的值了：
```c
TRY
    MP_add(z, x, y);
EXCEPT(MP_Overflow)
    ;                   /* 忽略溢位，z 已經是截斷後的結果 */
END_TRY;
```
（在 TRY 裡修改、之後還要用的區域變數記得宣告成 `volatile`。）

??? 觀念
XP、AP、MP 三個算術介面是怎麼 **分層** 的？各適合什麼樣的使用者？
!!!
- **XP（最底層）**：無號、固定 n 位數、底數 256、不配置記憶體、幾乎不檢查錯誤，追求速度。使用者是 AP 和 MP 的實作，不是一般應用。
- **AP（建在 XP 之上）**：有號、任意精度、自動配置、完整檢查，最方便安全。適合「數字可能非常大，而且不在乎配置成本」的應用，例如計算機程式 `calc`。
- **MP（建在 XP 之上）**：固定 n 位元、無號和二補數有號、全域精度、幾乎不配置、溢位丟出例外。適合需要 **精確模擬 n 位元整數**（例如編譯器、模擬器）或需要控制配置的應用。

這是全書「低層求快、高層求安全」的分層設計的代表。

??? 計算
`MP_set(8)` 之後（8 位元），有一個 MP_T 的位元是 `1000 0000₂`（0x80）。

1. 把它當成 **無號數** 和 **二補數有號數**，值各是多少？
2. **邏輯右移** 1 位和 **算術右移** 1 位，結果的位元和（有號）值各是多少？
3. MP 為什麼同時需要兩種右移？
!!!
1. 無號數 **128**；有號數（第 7 位是符號位元）**−128**。
2. - **邏輯右移**：左邊補 0 → `0100 0000₂` = **64**（有號、無號都是 64）。
   - **算術右移**：左邊補 **符號位元**（1）→ `1100 0000₂`，當成有號數是 **−64**（相當於除以 2）。
3. MP 同時支援無號和二補數有號整數：無號數右移等於除以 2 的冪次，要用邏輯右移；有號數要保留正負號，必須用算術右移。C 對負數右移的結果是 **實作定義** 的，MP 把兩種都明確地提供出來，才能精確模擬 n 位元機器的行為。

@@@ ch20 | 執行緒

??? 觀念
下面是 `spin` 範例裡「不安全」的版本，多個執行緒同時執行：

```c
for (i = 0; i < 100000; i++)
    *ip = *ip + 1;
```

1. 為什麼最後的總和常常 **小於** 執行緒數 × 100000？這叫做什麼問題？
2. 用 `Sem` 的 `LOCK` 怎麼修正？
3. 什麼情況 **不能** 用 LOCK-END_LOCK？要改用什麼？
!!!
1. `*ip = *ip + 1` 不是原子操作：「讀取 → 加 1 → 寫回」。如果一個執行緒 **讀取之後、寫回之前** 被切換出去，其他執行緒在這期間遞增了 `*ip`；等它恢復執行時，寫回的是 **舊值加 1**，把別人的遞增全部蓋掉。這是 **競爭條件 (race condition)**。
2. 用一個初值為 1 的信號量當 mutex，把臨界區域包起來：
```c
LOCK(mutex)
    *ip = *ip + 1;
END_LOCK;
```
3. 如果臨界區域裡的程式 **可能丟出例外**，例外發生時會跳過 `END_LOCK`，mutex **永遠不會被釋放**，其他執行緒全部卡住。要改用 TRY-FINALLY：
```c
Sem_wait(&mutex);
TRY
    statements;
FINALLY
    Sem_signal(&mutex);
END_TRY;
```

??? 觀念
1. `Chan` 是 **同步** 的通道。`Chan_send` 什麼時候返回？通道有沒有緩衝區？
2. 傳送端送了 100 bytes，接收端的 `Chan_receive` 只給了 64 bytes 的空間，會怎樣？
3. 在 `sieve` 這類範例裡，怎麼用 Chan 通知接收端「已經沒有資料了」？
!!!
1. `Chan_send` 會 **等到另一個執行緒對同一個通道呼叫 `Chan_receive`**，兩邊 **會合 (rendezvous)** 時資料從傳送端複製到接收端，兩邊才一起返回。**沒有緩衝區**，傳送和接收都會阻塞直到對方到達。
2. 只複製 64 bytes，**多的部分被丟掉**；`Chan_receive` 和 `Chan_send` 都回傳實際接受的位元組數（64），傳送端可以據此知道資料被截斷了。
3. 傳送一個 **size = 0** 的訊息當作結束訊號，接收端收到回傳 0 就知道傳送端結束了。

??? 觀念
1. Thread 介面為什麼 **沒有** 強制終止另一個執行緒的函式？要讓另一個執行緒結束，該怎麼做？
2. 非搶占式排程下，一個執行很久的計算迴圈應該做什麼，才不會讓其他執行緒餓死？
3. Sem 為什麼要設計成 **公平的 (FIFO)**？
!!!
1. 強制終止一個執行緒時，它可能正持有 mutex、正在修改共用的資料結構，或配置了還沒釋放的資源；從外面直接殺掉會留下壞掉的狀態。Thread 介面改用 **`Thread_alert(t)`**：設定目標執行緒的旗標，它在 **阻塞點**（或下一次阻塞時）會丟出 **`Thread_Alerted`** 例外，由它 **自己決定** 怎麼清理和結束（例如在 TRY-FINALLY 裡釋放資源，再呼叫 `Thread_exit`）。如果目標執行緒沒有捕捉 `Thread_Alerted`，整個程式會因為未捕捉的例外而結束。
2. 非搶占式排程下，執行緒只有在自己阻塞或讓出時才會切換。長時間的計算迴圈應該 **定期呼叫 `Thread_pause()`** 讓出處理器，其他執行緒才有機會執行。
3. 公平的信號量 **依照等待的順序** 喚醒執行緒，而且直接把信號量 **交給** 被喚醒的執行緒（不是讓它重新競爭），避免某個執行緒一直搶不到而 **飢餓 (starvation)**。

??? 觀念
1. `Thread_join(t)` 和 `Thread_join(NULL)` 各做什麼？
2. 下面三種情況分別會怎樣？
   - (a) 一個執行緒呼叫 `Thread_join(Thread_self())`
   - (b) 兩個執行緒都呼叫 `Thread_join(NULL)`
   - (c) `t` 已經結束了（或根本不存在），呼叫 `Thread_join(t)`
3. 主程式結束前通常要做什麼？
!!!
1. - `Thread_join(t)`：暫停目前的執行緒，**直到 t 呼叫 `Thread_exit`**，然後回傳 t 的結束碼。
   - `Thread_join(NULL)`：**等待所有其他執行緒結束**（包括之後才建立的），回傳 0。
2. - (a) **Checked runtime error**：等待自己結束，永遠不會發生。
   - (b) **Checked runtime error**：不能有超過一個執行緒用 NULL 呼叫（兩個都在等「所有其他執行緒」，會互相等待）。
   - (c) **立即回傳 −1**。
3. 呼叫 `Thread_join(NULL)` 等所有工作的執行緒都完成，再結束程式（或呼叫 `Thread_exit`）；否則主執行緒先結束，其他執行緒的工作可能還沒做完。另外，所有執行緒都在等待、沒有任何可以執行的執行緒時（死結），也是 checked runtime error。
