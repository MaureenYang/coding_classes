#include <stdio.h>
#include <stddef.h>

void swap_int(int *a, int *b) {
    int t = *a;
    *a = *b;
    *b = t;
}

void min_max(const int *begin, const int *end, int *mn, int *mx) {
    *mn = *mx = *begin;
    for (const int *p = begin + 1; p != end; p++) {
        if (*p < *mn) *mn = *p;
        if (*p > *mx) *mx = *p;
    }
}

void reverse_range(int *begin, int *end) {
    while (begin < end) {
        end--;                       /* end 指向「最後一個的下一個」，先退一格 */
        if (begin == end) break;
        swap_int(begin, end);
        begin++;
    }
}

int *find_first(int *begin, int *end, int x) {
    for (int *p = begin; p != end; p++)
        if (*p == x) return p;
    return NULL;
}

void rotate_left(int *a, int n, int k) {
    k %= n;
    if (k == 0) return;
    reverse_range(a, a + k);         /* 1 2 | 3 4 5  →  2 1 | 3 4 5 */
    reverse_range(a + k, a + n);     /*                 2 1 | 5 4 3 */
    reverse_range(a, a + n);         /*                 3 4 5 1 2   */
}

/* ===== 以下不用修改 ===== */
int a[1000];

int main(void) {
    int n, q;
    scanf("%d", &n);
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    scanf("%d", &q);
    while (q--) {
        char op[8];
        scanf("%7s", op);
        if (op[0] == 's') {
            int i, j;
            scanf("%d %d", &i, &j);
            swap_int(&a[i], &a[j]);
        } else if (op[0] == 'm') {
            int l, r, mn = 0, mx = 0;
            scanf("%d %d", &l, &r);
            min_max(a + l, a + r + 1, &mn, &mx);
            printf("%d %d\n", mn, mx);
        } else if (op[0] == 'f') {
            int x;
            scanf("%d", &x);
            int *p = find_first(a, a + n, x);
            printf("%d\n", p ? (int)(p - a) : -1);
        } else if (op[0] == 'r' && op[1] == 'e') {
            int l, r;
            scanf("%d %d", &l, &r);
            reverse_range(a + l, a + r + 1);
        } else if (op[0] == 'r') {
            int k;
            scanf("%d", &k);
            rotate_left(a, n, k);
        } else {
            for (int i = 0; i < n; i++) printf("%d%c", a[i], i + 1 < n ? ' ' : '\n');
        }
    }
    return 0;
}
