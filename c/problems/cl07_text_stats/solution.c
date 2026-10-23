#include <stdio.h>
#include <ctype.h>
#include <string.h>

static char cur[1000001];    /* 目前正在讀的單字 */
static char best[1000001];   /* 目前最長的單字 */

int main(void) {
    long long lines = 0, words = 0, chars = 0;
    long long line_len = 0, longest_line = 0;
    size_t cur_len = 0, best_len = 0;
    int cnt[26] = {0};
    int c, last = '\n';

    while ((c = getchar()) != EOF) {
        chars++;

        if (c == '\n') {
            lines++;
            if (line_len > longest_line) longest_line = line_len;
            line_len = 0;
        } else {
            line_len++;
        }

        if (isspace(c)) {
            if (cur_len > 0) {                       /* 一個單字剛結束 */
                if (cur_len > best_len) {
                    cur[cur_len] = '\0';
                    memcpy(best, cur, cur_len + 1);
                    best_len = cur_len;
                }
                cur_len = 0;
            }
        } else {
            if (cur_len == 0) words++;               /* 一個新單字開始 */
            cur[cur_len++] = (char)c;
        }

        if (isalpha(c)) cnt[tolower(c) - 'a']++;
        last = c;
    }

    if (chars > 0 && last != '\n') {                 /* 最後一行沒有換行 */
        lines++;
        if (line_len > longest_line) longest_line = line_len;
    }
    if (cur_len > best_len) {                        /* 最後一個單字後面沒有空白 */
        cur[cur_len] = '\0';
        memcpy(best, cur, cur_len + 1);
    }

    printf("lines %lld\n", lines);
    printf("words %lld\n", words);
    printf("chars %lld\n", chars);
    printf("longest_line %lld\n", longest_line);
    printf("longest_word %s\n", best[0] ? best : "none");

    int top = 0;
    for (int i = 1; i < 26; i++)
        if (cnt[i] > cnt[top]) top = i;              /* 用 > 而不是 >=：同次數保留字母小的 */
    if (cnt[top] == 0) puts("top_letter none");
    else printf("top_letter %c %d\n", 'a' + top, cnt[top]);
    return 0;
}
