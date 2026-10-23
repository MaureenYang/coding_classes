# 第 1 章　Introduction（導論）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.1–14

---

## 1. 本章定位

第 1 章說明**為什麼要寫這本書**，以及**全書用什麼方式寫**：

- 問題：理想上，大程式由許多現成、測試過的小模組組成，只有應用專屬的程式碼需要自己寫，bug 也只會出現在那裡。但現實是大多數程式從零開始寫，連記憶體管理這種低階元件都常被重寫（例如自己取代 `malloc`/`free`）。
- 原因：
  - 好的函式庫很少，有的品質普通、缺乏標準。
  - 有些函式庫太大，學會它的成本接近自己重寫。
  - 設計函式庫很難，要在**通用性、簡單性、效率**之間取得平衡。作者點名 C 標準函式庫的 `realloc` 是「混亂的傑作」。
  - 實作也很難：太慢、太大（或只是「看起來」如此）、有 bug，使用者就會自己重寫。
- 本書目標：設計並實作一套適用於「小規模程式設計」（programming-in-the-small）的 C 函式庫，模組可以當作幾千行程式裡的「零件」。
- 內容大多是大學資料結構與演算法課教過的東西，但**重點放在怎麼包裝，以及怎麼讓它們穩健可靠**。

---

## 2. Literate Programming（文學式程式設計）

### 2.1 基本概念

全書是一份 **literate program**：英文說明和**有名字的程式區塊（chunk）**交錯排列，而且**這本書本身就是原始碼**，程式是從書稿自動抽出來的（用 Norman Ramsey 的 noweb 工具中的 `notangle`），「所見即所得」。

```
〈compute x • y〉≡
    sum = 0;
    for (i = 0; i < n; i++)
        sum += x[i]*y[i];
```

其他區塊可以引用它：

```
〈function dotproduct〉≡
    int dotProduct(int x[], int y[], int n) {
        int i, sum;
        〈compute x • y〉
        return sum;
    }
```

抽出程式時，引用的區塊會被展開成實際程式碼。

### 2.2 符號約定

| 符號 | 意義 |
|---|---|
| `〈name〉≡` | 定義一個區塊 |
| `〈name〉+≡` | **附加**程式碼到已存在的區塊，讓程式可以一點一點地呈現 |
| `〈double.c 4〉` | 數字是該區塊定義所在的**頁碼**，方便讀者跳轉 |
| 根區塊（root chunk） | 以檔名命名，例如 `〈double.c〉`，抽出它就得到整個檔案 |

### 2.3 好處

- 程式可以拆成小塊，每塊都有完整說明；**文字取代了傳統註解**，不受語言註解語法的限制，可以放表格、公式、圖片和引用。
- **擺脫語言的順序限制**：程式碼可以依照「最好理解」的順序呈現，而不是依照 C 要求的「先宣告再使用」。
- 區塊不必對應任何語法單位，它就只是文字。例如 `〈found a word?〉` 只是一個運算式 `buf[0] != '\0'`。

---

## 3. 範例程式：`double`

### 3.1 功能

找出輸入中**相鄰的重複單字**（例如 "the the"），印出行號：

```
% double intro.txt inter.txt
intro.txt:10: the
inter.txt:110: interface
...
```

沒有給參數時讀標準輸入，輸出也省略檔名。

### 3.2 結構

```
〈double.c 4〉≡
    〈includes 5〉
    〈data 6〉
    〈prototypes 6〉
    〈functions 5〉
```

### 3.3 主要函式

**`main`**：逐一開啟檔案並呼叫 `doubleword`，開檔失敗時用 `strerror(errno)` 印出錯誤訊息。

**`getword`**：讀取下一個單字（連續的非空白字元）放進 `buf[0..size-1]`，有讀到就回傳 1、讀到檔尾回傳 0。

```c
int getword(FILE *fp, char *buf, int size) {
    int c;
    c = getc(fp);
    for ( ; c != EOF && isspace(c); c = getc(fp))   // 跳過空白
        if (c == '\n')
            linenum++;
    {
        int i = 0;
        for ( ; c != EOF && !isspace(c); c = getc(fp))
            if (i < size - 1)
                buf[i++] = tolower(c);   // 轉小寫，丟掉超長的部分
        if (i < size)
            buf[i] = '\0';
    }
    if (c != EOF)
        ungetc(c, fp);
    return buf[0] != '\0';
}
```

**`doubleword`**：比較每個字和前一個字，相同而且以字母開頭就印出來。

```c
void doubleword(char *name, FILE *fp) {
    char prev[128], word[128];
    linenum = 1;
    prev[0] = '\0';
    while (getword(fp, word, sizeof word)) {
        if (isalpha(word[0]) && strcmp(prev, word)==0) {
            if (name)
                printf("%s:", name);
            printf("%d: %s\n", linenum, word);
        }
        strcpy(prev, word);
    }
}
```

### 3.4 值得注意的細節

- `linenum` 在**第一次用到的地方**才定義（`〈data〉` 區塊），而不是放在檔案開頭。這就是 literate programming 擺脫順序限制的例子。
- `〈prototypes〉` 區塊是對 C「先宣告再使用」規則的妥協，有了它，函式就可以用任意順序呈現。
- `if (i < size)` 是為了處理 `size == 0` 的情況。`double` 裡不會發生這種事，但這是**防禦式程式設計**，用來抓出「不可能發生」的 bug。
- `〈word is a duplicate〉` 寫成複合敘述 `{ ... }`，才能直接放在 `if` 後面當作主體。

---

## 4. Programming Style（程式風格）

> "It is more important for programs to be read easily and understood by people than it is for them to be compiled easily by computers."

### 4.1 核心態度

風格慣例**不是必須死守的規則**，而是一種追求最大可讀性的哲學。如果打破慣例能突顯重點或讓複雜的程式更好讀，就打破它。

### 4.2 具體慣例

| 面向 | 做法 |
|---|---|
| **命名** | 全域變數和函式用較長、能說明用途的名字；區域變數用短名字，可以沿用數學記號（`i`、`x`、`y`） |
| **反例** | `for (theindex = 0; theindex < numofElements; theindex++)`：名字太長反而遮住了程式在做什麼 |
| **宣告位置** | 變數宣告在第一次使用的附近；區域變數盡量宣告在所屬複合敘述的開頭 |
| **函式命名** | 程序用名字表達它**做什麼**，函式用名字表達它**回傳什麼**（`getword` 回傳下一個字） |
| **長度** | 大多數函式不超過一頁；區塊更短，通常不到十幾行 |
| **註解** | 幾乎不寫，因為周圍的文字取代了註解 |

### 4.3 對註解的看法

- 清楚的程式加上好的命名和縮排，通常可以**自己解釋自己**。
- 註解只用來說明：資料結構的細節、演算法的特殊情況、例外狀況。
- **編譯器無法檢查註解和程式是否一致，誤導的註解比沒有註解更糟。**
- 有些註解只是雜訊，過多的排版符號反而把程式淹沒了。

### 4.4 C 的慣用寫法（Idioms）

用 `strcpy` 對比兩種寫法：

```c
/* 新手常見：陣列版 */
char *strcpy(char dst[], const char src[]) {
    int i;
    for (i = 0; src[i] != '\0'; i++)
        dst[i] = src[i];
    dst[i] = '\0';
    return dst;
}

/* 慣用寫法：指標版 */
char *strcpy(char *dst, const char *src) {
    char *s = dst;
    while (*dst++ = *src++)
        ;
    return s;
}
```

- 指標版把「賦值、指標遞增、測試結果」合併成一個運算式；直接修改參數 `dst`、`src` 也沒問題，因為 C 的參數是傳值，本質上就是已初始化的區域變數。
- 作者**承認陣列版對所有人都比較好懂**，但指標版是有經驗的 C 程式設計師會寫的，也是你讀別人的程式時最常遇到的。
- 結論：要寫得流暢，就必須掌握這些慣用寫法，尤其是指標相關的部分。

---

## 5. Efficiency（效率）

### 5.1 作者對「效率狂熱」的批評

| 觀點 | 說明 |
|---|---|
| **直覺不可靠** | 程式設計師猜程式把時間花在哪裡，出了名地不準 |
| **調校有代價** | 調校後的程式幾乎都會更大、更難懂、更容易出錯 |
| **夠快就好** | 程式只需要 *fast enough*，不必 *as fast as possible* |
| **先量測** | 沒有量測數據證明太慢，就不該調校；瓶頸很少出現在你預期的地方 |
| **抓大放小** | I/O 佔了 60% 的時間時，把搜尋常式省下 1% 沒有意義 |
| **可靠優先** | "The fastest program to a crash isn't a winner." 交付會當機的快軟體，長期成本比夠快的可靠軟體更高 |
| **層次要對** | 直接實作一個本來就快的演算法，勝過手工調校一個慢的演算法（二分搜尋 > 優化線性搜尋的內迴圈） |
| **調校救不了爛設計** | 如果到處都慢，問題出在設計本身 |

### 5.2 本書的做法

- 使用平均表現好、**最差情況容易描述**的演算法；可能出現效能問題的地方會明確標示。
- **盡量避免巨集和條件編譯**：
  - 用巨集省掉函式呼叫很少有必要，只有量測證明呼叫成本壓過其他部分時才值得。I/O（`getc`、`putc` 等）是少數合理的例外。
  - 條件編譯是「逃避問題的捷徑」，一定會讓程式更難讀。
  - 平台差異比較好的做法是**在執行期選擇**。例如一個能在執行時選擇目標架構的 cross compiler，勝過分別建置六個編譯器。
  - 如果真的必須在編譯期設定，用**版本控制工具**會比 `#ifdef` 好。

---

## 6. 延伸閱讀重點

- **C 語言參考**：ANSI/ISO C 標準、Kernighan & Ritchie (1988)、Harbison & Steele (1995)、Plauger (1992) 的標準函式庫實作。
- **Literate programming**：Knuth 的 WEB、Ramsey 的 noweb；作者另一本書（Fraser & Hanson, 1995）把整個 lcc 編譯器寫成 literate program。
- **程式風格**：本書沿用 Kernighan & Pike (1984)《The UNIX Programming Environment》和 K&R 的風格。
  > "The best way to learn good programming style is to read programs that use good style."
- **效率**：Sedgewick (1990)、Knuth (1973)、Bentley (1982)。

---

## 7. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 1.1 | 為什麼單字剛好在換行處結束時，`getword` 不增加 `linenum`？ | `ungetc` 會把換行字元放回輸入，下次掃描空白時才會算到 |
| 1.2 | 三個以上連續相同的字，`double` 會印出什麼？請修正 | 目前每多一個重複字就印一次 |
| 1.3 | 比較 `while (*dst++ = *src++)` 和加上 `!= '\0'` 的明確比較寫法 | 明確比較能表示這裡的賦值不是打錯字；lint 工具會對前者發出警告 |

---

## 8. 本章重點整理

1. **函式庫的理想**：由現成、可靠的模組組成程式，bug 只會出現在應用專屬的程式碼裡。
2. **設計難在三方平衡**：通用性、簡單性、效率。
3. **Literate programming**：文字和程式區塊交錯，依照好理解的順序呈現，書本身就是原始碼。
4. **可讀性第一**：好命名、短函式、少而精的註解，寫道地的 C 慣用寫法。
5. **效率觀**：先量測、夠快就好、可靠比快重要、選對演算法、避免巨集和條件編譯。

> **一句話**：這一章為全書定調，我們要寫的是給人讀、可靠、夠快的函式庫，而這本書本身就是範本。
