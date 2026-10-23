# CL07. 文字統計 (Text Statistics)

> 主題：`getchar` 讀到 `EOF`、`<ctype.h>`、狀態追蹤　難度：★★☆　時間限制：1 秒　相關教學：`c/lessons/10_file_io.md`、`c/lessons/06_strings.md`

## 題目

讀入 **整份輸入**（直到 `EOF`），輸出這份文字的統計資料（類似 Linux 的 `wc` 指令）：

| 項目 | 定義 |
|---|---|
| `lines` | 行數 = 換行字元 `'\n'` 的個數；如果文字不是空的、而且最後一個字元不是 `'\n'`，再加 1 |
| `words` | 單字數 = 「連續的非空白字元」有幾段（空白是 `isspace` 為真的字元：空格、`\t`、`\n` 等） |
| `chars` | 總字元數（byte 數，包含空白和換行） |
| `longest_line` | 最長的一行有幾個字元（不含 `'\n'`） |
| `longest_word` | 最長的單字；一樣長的取 **最先出現** 的；沒有單字輸出 `none` |
| `top_letter` | 出現最多次的英文字母（**不分大小寫**，輸出小寫）和次數；次數相同取字母順序小的；沒有字母輸出 `none` |

## 輸入

一段文字，只包含可見的 ASCII 字元、空格、`\t` 和 `\n`。**最後不一定有換行，也可能完全是空的。**

## 輸出

```
lines 行數
words 單字數
chars 字元數
longest_line 最長行長度
longest_word 最長單字
top_letter 字母 次數
```

## 限制

- 總長度 `≤ 10^6` 個字元；一行或一個單字可能很長（最長 `10^6`）

## 範例

輸入
```
Hello, world!
  C is   fun.
```
輸出
```
lines 2
words 5
chars 28
longest_line 13
longest_word Hello,
top_letter l 3
```

（第二行前面有兩個空格；`Hello,` 和 `world!` 一樣長，取先出現的。）

## 提示

- 經典的讀取迴圈：

```c
int c;                          /* 一定要用 int，不能用 char！ */
while ((c = getchar()) != EOF) {
    ...
}
```

`getchar` 回傳 `int`：正常字元是 0 ~ 255，讀完時回傳 `EOF`（通常是 -1）。如果存進 `char`，就分不清「讀到 255 這個字元」和「讀完了」。

- 數單字：記錄「目前是不是在單字裡面」。從空白變成非空白的那一刻，單字數加 1。
- 最長單字：一邊讀一邊把目前的單字存進陣列（`static char cur[1000001]`，太大的陣列不要放在函式裡的區域變數），單字結束時和目前最長的比較。**別忘了最後一個單字後面可能沒有空白。**
- 字母計數：`int cnt[26]`，`cnt[tolower(c) - 'a']++`。
