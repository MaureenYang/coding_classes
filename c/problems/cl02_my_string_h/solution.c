#include <stdio.h>
#include <stddef.h>

/* ===== 這一題不能用 <string.h>（不要修改這一段）===== */
#define strlen  please_write_my_strlen
#define strcpy  please_write_my_strcpy
#define strcat  please_write_my_strcat
#define strcmp  please_write_my_strcmp
#define strchr  please_write_my_strchr
#define strstr  please_write_my_strstr
/* ===================================================== */

size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return (size_t)(p - s);
}

char *my_strcpy(char *dst, const char *src) {
    char *d = dst;
    while ((*d++ = *src++) != '\0') { }
    return dst;
}

char *my_strcat(char *dst, const char *src) {
    char *d = dst;
    while (*d) d++;
    while ((*d++ = *src++) != '\0') { }
    return dst;
}

int my_strcmp(const char *a, const char *b) {
    while (*a && *a == *b) { a++; b++; }
    return (unsigned char)*a - (unsigned char)*b;
}

char *my_strchr(const char *s, int c) {
    for (; *s; s++)
        if (*s == (char)c) return (char *)s;
    return NULL;
}

char *my_strstr(const char *hay, const char *needle) {
    if (*needle == '\0') return (char *)hay;
    for (; *hay; hay++) {
        const char *h = hay, *n = needle;
        while (*n && *h == *n) { h++; n++; }
        if (*n == '\0') return (char *)hay;
    }
    return NULL;
}

void my_strrev(char *s) {
    size_t n = my_strlen(s);
    for (size_t i = 0; i < n / 2; i++) {     /* 第 i 個和倒數第 i 個交換 */
        char t = s[i];
        s[i] = s[n - 1 - i];
        s[n - 1 - i] = t;
    }
}

/* ===== 以下是讀指令、呼叫你的函式（不用修改）===== */
static void read_str(char *buf) {
    scanf("%127s", buf);
    if (buf[0] == '"' && buf[1] == '"' && buf[2] == '\0') buf[0] = '\0';  /* "" 代表空字串 */
}
static void print_str(const char *s) {
    if (s[0] == '\0') puts("(empty)");
    else puts(s);
}

int main(void) {
    int q;
    if (scanf("%d", &q) != 1) return 0;
    char a[128], b[128], buf[256];
    while (q--) {
        char op[8];
        scanf("%7s", op);
        if (op[0] == 'l') {                       /* len */
            read_str(a);
            printf("%zu\n", my_strlen(a));
        } else if (op[0] == 'c' && op[1] == 'm') { /* cmp */
            read_str(a); read_str(b);
            int r = my_strcmp(a, b);
            printf("%d\n", (r > 0) - (r < 0));
        } else if (op[0] == 'c' && op[1] == 'a') { /* cat */
            read_str(a); read_str(b);
            my_strcpy(buf, a);
            my_strcat(buf, b);
            print_str(buf);
        } else if (op[0] == 'c' && op[1] == 'h') { /* chr */
            char c;
            read_str(a);
            scanf(" %c", &c);
            char *p = my_strchr(a, c);
            printf("%d\n", p ? (int)(p - a) : -1);
        } else if (op[0] == 's') {                 /* str */
            read_str(a); read_str(b);
            char *p = my_strstr(a, b);
            printf("%d\n", p ? (int)(p - a) : -1);
        } else {                                   /* rev */
            read_str(a);
            my_strrev(a);
            print_str(a);
        }
    }
    return 0;
}
