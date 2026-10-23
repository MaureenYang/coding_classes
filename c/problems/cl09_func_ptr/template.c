#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int (*MapFn)(int x);
typedef int (*PredFn)(int x);
typedef long long (*FoldFn)(long long acc, int x);
typedef int (*CmpFn)(const void *a, const void *b);

#define MOD 1000000007LL

/* ===== 1. 小函式（TODO：寫出函式本體，再填進下面的表）===== */
static int f_neg(int x) { /* TODO */ return x; }
/* TODO：f_abs、f_half、f_inc、f_dec、f_mod10 */

/* TODO：p_even、p_odd、p_pos、p_neg、p_nonzero */

/* TODO：fold_sum、fold_count、fold_prodmod（形式：long long name(long long acc, int x)） */

/* TODO：cmp_asc、cmp_desc、cmp_absasc（形式：int name(const void *a, const void *b)） */

/* ===== 2. 名字 → 函式指標的表（TODO：把 NULL 換成你的函式）=====
 * 還是 NULL 的項目，main 會當成「找不到」而輸出 unknown。 */
typedef struct { const char *name; MapFn fn; } MapEntry;
typedef struct { const char *name; PredFn fn; } PredEntry;
typedef struct { const char *name; FoldFn fn; long long init; } FoldEntry;
typedef struct { const char *name; CmpFn fn; } CmpEntry;

static const MapEntry MAPS[] = {
    {"neg", f_neg}, {"abs", NULL}, {"half", NULL}, {"inc", NULL}, {"dec", NULL}, {"mod10", NULL},
};
static const PredEntry PREDS[] = {
    {"even", NULL}, {"odd", NULL}, {"pos", NULL}, {"neg", NULL}, {"nonzero", NULL},
};
static const FoldEntry FOLDS[] = {
    {"sum", NULL, 0}, {"count", NULL, 0}, {"prodmod", NULL, 1},
};
static const CmpEntry CMPS[] = {
    {"asc", NULL}, {"desc", NULL}, {"absasc", NULL},
};

/* ===== 3. 接受函式指標的通用函式（TODO）===== */
void map_all(int *a, int n, MapFn f) {
    /* TODO */
}

int filter_keep(int *a, int n, PredFn p) {
    /* TODO：保持順序，回傳新的長度 */
    return n;
}

long long fold(const int *a, int n, long long init, FoldFn f) {
    /* TODO */
    return init;
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
