#include <stdio.h>
#include <ctype.h>

int main(void) {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        char type[16];
        scanf("%15s", type);
        if (type[0] == 'i') {
            int x;
            scanf("%d", &x);
            printf("[%d] [%5d] [%-5d] [%05d] [%+d] [%x] [%o]\n",
                   x, x, x, x, x, (unsigned)x, (unsigned)x);
        } else if (type[0] == 'f') {
            double f;
            scanf("%lf", &f);
            printf("[%.2f] [%8.3f] [%-8.1f] [%e] [%g]\n", f, f, f, f, f);
        } else if (type[0] == 's') {
            char s[32];
            scanf("%31s", s);
            printf("[%s] [%10s] [%-10s] [%.3s]\n", s, s, s, s);
        } else if (type[0] == 'c') {
            char c;
            scanf(" %c", &c);
            printf("[%c] [%d] [%c]\n", c, c, toupper((unsigned char)c));
        } else {
            long long h, m, s;
            scanf("%lld %lld %lld", &h, &m, &s);
            long long total = h * 3600 + m * 60 + s;
            printf("[%02lld:%02lld:%02lld]\n", total / 3600, total / 60 % 60, total % 60);
        }
    }
    return 0;
}
