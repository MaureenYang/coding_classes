#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int (*MapFn)(int x);
typedef int (*PredFn)(int x);
typedef long long (*FoldFn)(long long acc, int x);
typedef int (*CmpFn)(const void *a, const void *b);

#define MOD 1000000007LL

/* ===== 1. 小函式 ===== */
static int f_neg(int x)   { return -x; }
static int f_abs(int x)   { return x < 0 ? -x : x; }
static int f_half(int x)  { return x / 2; }
static int f_inc(int x)   { return x + 1; }
static int f_dec(int x)   { return x - 1; }
static int f_mod10(int x) { return x % 10; }

static int p_even(int x)    { return x % 2 == 0; }
static int p_odd(int x)     { return x % 2 != 0; }      /* 不能寫 x % 2 == 1：負的奇數 % 2 是 -1 */
static int p_pos(int x)     { return x > 0; }
static int p_neg(int x)     { return x < 0; }
static int p_nonzero(int x) { return x != 0; }

static long long fold_sum(long long acc, int x)     { return acc + x; }
static long long fold_count(long long acc, int x)   { (void)x; return acc + 1; }
static long long fold_prodmod(long long acc, int x) { return acc * (((long long)x % MOD + MOD) % MOD) % MOD; }

static int cmp_asc(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);                           /* 不用 x - y，避免溢位 */
}
static int cmp_desc(const void *a, const void *b) { return cmp_asc(b, a); }
static int cmp_absasc(const void *a, const void *b) {
    long long x = *(const int *)a, y = *(const int *)b;
    long long ax = x < 0 ? -x : x, ay = y < 0 ? -y : y;
    if (ax != ay) return (ax > ay) - (ax < ay);
    return (x > y) - (x < y);                           /* 絕對值相同：負數在前 */
}

/* ===== 2. 名字 → 函式指標的表 ===== */
typedef struct { const char *name; MapFn fn; } MapEntry;
typedef struct { const char *name; PredFn fn; } PredEntry;
typedef struct { const char *name; FoldFn fn; long long init; } FoldEntry;
typedef struct { const char *name; CmpFn fn; } CmpEntry;

static const MapEntry MAPS[] = {
    {"neg", f_neg}, {"abs", f_abs}, {"half", f_half}, {"inc", f_inc}, {"dec", f_dec}, {"mod10", f_mod10},
};
static const PredEntry PREDS[] = {
    {"even", p_even}, {"odd", p_odd}, {"pos", p_pos}, {"neg", p_neg}, {"nonzero", p_nonzero},
};
static const FoldEntry FOLDS[] = {
    {"sum", fold_sum, 0}, {"count", fold_count, 0}, {"prodmod", fold_prodmod, 1},
};
static const CmpEntry CMPS[] = {
    {"asc", cmp_asc}, {"desc", cmp_desc}, {"absasc", cmp_absasc},
};

/* ===== 3. 接受函式指標的通用函式 ===== */
void map_all(int *a, int n, MapFn f) {
    for (int i = 0; i < n; i++) a[i] = f(a[i]);
}

int filter_keep(int *a, int n, PredFn p) {
    int w = 0;                                          /* 下一個要寫入的位置 */
    for (int i = 0; i < n; i++)
        if (p(a[i])) a[w++] = a[i];
    return w;
}

long long fold(const int *a, int n, long long init, FoldFn f) {
    long long acc = init;
    for (int i = 0; i < n; i++) acc = f(acc, a[i]);
    return acc;
}

/* ===== 以下不用修改 ===== */
#define COUNT(t) ((int)(sizeof(t) / sizeof((t)[0])))   /* 陣列有幾個元素 */
static int a[10000];

int main(void) {
    int n, q;
    scanf("%d", &n);
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    scanf("%d", &q);
    while (q--) {
        char op[16], name[32];
        scanf("%15s", op);
        if (!strcmp(op, "print")) {
            if (n == 0) puts("empty");
            for (int i = 0; i < n; i++) printf("%d%c", a[i], i + 1 < n ? ' ' : '\n');
            continue;
        }
        scanf("%31s", name);
        int found = 0;
        if (!strcmp(op, "map")) {
            for (int k = 0; k < COUNT(MAPS); k++)
                if (!strcmp(MAPS[k].name, name) && MAPS[k].fn) { map_all(a, n, MAPS[k].fn); found = 1; }
        } else if (!strcmp(op, "filter")) {
            for (int k = 0; k < COUNT(PREDS); k++)
                if (!strcmp(PREDS[k].name, name) && PREDS[k].fn) { n = filter_keep(a, n, PREDS[k].fn); found = 1; }
        } else if (!strcmp(op, "reduce")) {
            if (!strcmp(name, "max") || !strcmp(name, "min")) {
                found = 1;
                if (n == 0) { puts("empty"); continue; }
                int best = a[0];
                for (int i = 1; i < n; i++)
                    if (name[1] == 'a' ? a[i] > best : a[i] < best) best = a[i];
                printf("%d\n", best);
            }
            for (int k = 0; k < COUNT(FOLDS); k++)
                if (!strcmp(FOLDS[k].name, name) && FOLDS[k].fn) {
                    printf("%lld\n", fold(a, n, FOLDS[k].init, FOLDS[k].fn));
                    found = 1;
                }
        } else if (!strcmp(op, "sort")) {
            for (int k = 0; k < COUNT(CMPS); k++)
                if (!strcmp(CMPS[k].name, name) && CMPS[k].fn) { qsort(a, n, sizeof(int), CMPS[k].fn); found = 1; }
        }
        if (!found) printf("unknown %s\n", name);
    }
    return 0;
}
