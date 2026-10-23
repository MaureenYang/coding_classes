# CL02. 自己寫 string.h (My string.h)

> 主題：C 字串（`char` 陣列 + `'\0'`）、指標走訪　難度：★★☆　時間限制：1 秒　相關教學：`c/lessons/06_strings.md`

## 題目

C 語言的字串就是「以 `'\0'` 結尾的 `char` 陣列」。標準函式庫 `<string.h>` 提供了 `strlen`、`strcpy`、`strcmp` 等函式 —— 這一題請你 **不使用 `<string.h>`**，自己把它們寫出來：

| 函式 | 作用（和標準函式庫的同名函式一樣） |
|---|---|
| `size_t my_strlen(const char *s)` | 字串長度（不含 `'\0'`） |
| `char *my_strcpy(char *dst, const char *src)` | 把 `src`（含 `'\0'`）複製到 `dst`，回傳 `dst` |
| `char *my_strcat(char *dst, const char *src)` | 把 `src` 接在 `dst` 後面，回傳 `dst` |
| `int my_strcmp(const char *a, const char *b)` | 字典序比較：`a < b` 回傳負數、相等回傳 0、`a > b` 回傳正數 |
| `char *my_strchr(const char *s, int c)` | 回傳 `c` 第一次出現的位置；找不到回傳 `NULL` |
| `char *my_strstr(const char *hay, const char *needle)` | 回傳 `needle` 第一次出現的位置；找不到回傳 `NULL`；`needle` 是空字串時回傳 `hay` |
| `void my_strrev(char *s)` | 原地反轉字串 |

樣板的 `main` 已經寫好，會讀入指令並呼叫你的函式：

| 指令 | 輸出 |
|---|---|
| `len s` | `my_strlen(s)` |
| `cmp a b` | `my_strcmp(a, b)` 的 **正負號**：`-1`、`0` 或 `1` |
| `cat a b` | 先 `my_strcpy(buf, a)` 再 `my_strcat(buf, b)`，輸出 `buf` |
| `chr s c` | `my_strchr(s, c)` 的位置（索引）；找不到輸出 `-1` |
| `str s t` | `my_strstr(s, t)` 的位置（索引）；找不到輸出 `-1` |
| `rev s` | `my_strrev(s)` 之後的 `s` |

輸入中的 `""` 代表 **空字串**；輸出時空字串印成 `(empty)`。

## 輸入

第一行整數 `Q`，接下來 `Q` 行指令。字串由小寫字母和數字組成，長度 `0 ~ 100`；`chr` 的 `c` 是一個小寫字母或數字。

## 限制

- `1 ≤ Q ≤ 20000`
- **不可以** 使用 `<string.h>` 的函式（樣板用巨集擋住了，呼叫的話會編譯或連結失敗）

## 範例

輸入
```
8
len hello
len ""
cmp abc abd
cmp ab abc
cat foo bar
chr banana n
str banana nan
rev abc
```
輸出
```
5
0
-1
-1
foobar
2
2
cba
```

## 提示

- 每個函式都是「用指標一個一個字元往後走，直到遇到 `'\0'`」：

```c
size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p != '\0') p++;
    return p - s;          /* 兩個指標相減 = 中間有幾個元素 */
}
```

- `my_strcmp`：兩個字串同時往後走，遇到 **第一個不同的字元** 就回傳它們的差；其中一個先結束時，`'\0'`（值是 0）比任何字元都小，所以 `"ab" < "abc"`。
- `my_strchr` 回傳的是 **指標**，`main` 用 `p - s` 算出索引。注意 `const char *` 轉成 `char *` 要寫 `(char *)`。
- `my_strstr`：對 `hay` 的每個起點，檢查 `needle` 是不是從那裡開始。
- `my_strrev`：兩個指標，一個從頭、一個從尾，往中間交換。
