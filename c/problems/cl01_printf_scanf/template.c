#include <stdio.h>
#include <ctype.h>

int main(void) {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        char type[16];
        scanf("%15s", type);
        if (type[0] == 'i') {            /* int */
            int x;
            scanf("%d", &x);
            /* TODO：[%d] [%5d] [%-5d] [%05d] [%+d] [%x] [%o] */
        } else if (type[0] == 'f') {     /* float */
            double f;
            /* TODO：讀進 f（用 %lf），輸出 [%.2f] [%8.3f] [%-8.1f] [%e] [%g] */
        } else if (type[0] == 's') {     /* str */
            char s[32];
            /* TODO：讀字串、輸出 [%s] [%10s] [%-10s] [%.3s] */
        } else if (type[0] == 'c') {     /* char */
            char c;
            /* TODO：讀字元（小心空白）、輸出 [%c] [%d] [%c] */
        } else {                         /* time */
            long long h, m, s;
            /* TODO：讀三個數、正規化、輸出 [%02d:%02d:%02d] */
        }
    }
    return 0;
}
