#include <stdio.h>
#include <ctype.h>
#include <string.h>

static char cur[1000001];    /* 目前正在讀的單字 */
static char best[1000001];   /* 目前最長的單字 */

int main(void) {
    long long lines = 0, words = 0, chars = 0;
    long long line_len = 0, longest_line = 0;
    int cnt[26] = {0};
    int c, last = '\n';      /* last：上一個讀到的字元 */

    while ((c = getchar()) != EOF) {
        chars++;
        /* TODO：
         *  1. 換行：lines++，更新 longest_line，line_len 歸零；否則 line_len++
         *  2. 單字：維護 cur，單字結束時和 best 比較，words++
         *  3. 字母：cnt[...]++
         */
        last = c;
    }
    /* TODO：處理「最後一行沒有換行」和「最後一個單字後面沒有空白」 */

    printf("lines %lld\n", lines);
    printf("words %lld\n", words);
    printf("chars %lld\n", chars);
    printf("longest_line %lld\n", longest_line);
    printf("longest_word %s\n", best[0] ? best : "none");
    /* TODO：top_letter */
    return 0;
}
