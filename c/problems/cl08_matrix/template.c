#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ===== 記憶體配置記錄（不要修改）===== */
static long long g_live = 0;   /* 目前還沒釋放的區塊數 */
void *xmalloc(size_t n) {
    void *p = malloc(n);
    if (!p) { puts("out of memory"); exit(1); }
    g_live++;
    return p;
}
void *xrealloc(void *p, size_t n) {
    void *q = realloc(p, n);
    if (!q) { puts("out of memory"); exit(1); }
    if (!p) g_live++;          /* realloc(NULL, n) 等於配置一塊新的 */
    return q;
}
void xfree(void *p) {
    if (p) { g_live--; free(p); }
}
#define malloc  please_use_xmalloc
#define calloc  please_use_xmalloc
#define realloc please_use_xrealloc
#define free    please_use_xfree
/* ===================================== */

long long **mat_alloc(int r, int c) {
    /* TODO：配置 r × c，全部填 0 */
    return NULL;
}

void mat_free(long long **m, int r) {
    /* TODO：釋放 mat_alloc 配置的所有東西 */
}

long long **mat_transpose(long long **a, int r, int c) {
    /* TODO：回傳新的 c × r 矩陣 */
    return NULL;
}

long long **mat_add(long long **a, long long **b, int r, int c) {
    /* TODO */
    return NULL;
}

long long **mat_mul(long long **a, long long **b, int r, int k, int c) {
    /* TODO：a 是 r × k、b 是 k × c */
    return NULL;
}

/* ===== 以下不用修改 ===== */
static long long **read_matrix(int *r, int *c) {
    scanf("%d %d", r, c);
    long long **m = mat_alloc(*r, *c);
    for (int i = 0; i < *r; i++)
        for (int j = 0; j < *c; j++)
            scanf("%lld", &m[i][j]);
    return m;
}

static void print_matrix(long long **m, int r, int c) {
    for (int i = 0; i < r; i++)
        for (int j = 0; j < c; j++)
            printf("%lld%c", m[i][j], j + 1 < c ? ' ' : '\n');
}

int main(void) {
    int r1, c1, r2, c2;
    long long **a = read_matrix(&r1, &c1);
    long long **b = read_matrix(&r2, &c2);

    puts("transpose of A:");
    long long **t = mat_transpose(a, r1, c1);
    print_matrix(t, c1, r1);
    mat_free(t, c1);

    puts("A + B:");
    if (r1 == r2 && c1 == c2) {
        long long **s = mat_add(a, b, r1, c1);
        print_matrix(s, r1, c1);
        mat_free(s, r1);
    } else {
        puts("cannot add");
    }

    puts("A * B:");
    if (c1 == r2) {
        long long **p = mat_mul(a, b, r1, c1, c2);
        print_matrix(p, r1, c2);
        mat_free(p, r1);
    } else {
        puts("cannot multiply");
    }

    mat_free(a, r1);
    mat_free(b, r2);
    if (g_live == 0) puts("leak check: ok");
    else printf("leak check: %lld block(s) not freed\n", g_live);
    return 0;
}
