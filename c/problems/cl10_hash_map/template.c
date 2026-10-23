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

typedef struct Entry {
    char *key;
    long long val;
    struct Entry *next;
} Entry;

typedef struct {
    Entry **buckets;
    size_t nbuckets;
    size_t size;
} HashMap;

/* djb2 雜湊函式（不用修改） */
unsigned long hash_str(const char *s) {
    unsigned long h = 5381;
    for (; *s; s++) h = h * 33 + (unsigned char)*s;
    return h;
}

void hm_init(HashMap *m) {
    /* TODO：8 個桶子，全部是 NULL */
}

void hm_free(HashMap *m) {
    /* TODO：每個 Entry 的 key、Entry 本身、最後是桶子陣列 */
}

long long *hm_get(HashMap *m, const char *key) {
    /* TODO：回傳指向值的指標，找不到回傳 NULL */
    return NULL;
}

void hm_put(HashMap *m, const char *key, long long val) {
    /* TODO：存在就覆蓋；不存在就新增（複製 key），必要時 rehash */
}

int hm_del(HashMap *m, const char *key) {
    /* TODO */
    return 0;
}

/* ===== 以下不用修改 ===== */
int main(void) {
    int q;
    if (scanf("%d", &q) != 1) return 0;
    HashMap m;
    hm_init(&m);
    char op[8], key[32];
    long long v;
    while (q--) {
        scanf("%7s", op);
        if (!strcmp(op, "size")) { printf("%zu\n", m.size); continue; }
        scanf("%31s", key);
        if (!strcmp(op, "put")) {
            scanf("%lld", &v);
            hm_put(&m, key, v);
        } else if (!strcmp(op, "get")) {
            long long *p = hm_get(&m, key);
            if (p) printf("%lld\n", *p);
            else puts("not found");
        } else if (!strcmp(op, "add")) {
            scanf("%lld", &v);
            long long *p = hm_get(&m, key);
            if (p) *p += v;              /* 透過指標直接修改表裡的值 */
            else hm_put(&m, key, v);
        } else if (!strcmp(op, "del")) {
            puts(hm_del(&m, key) ? "ok" : "not found");
        }
    }
    hm_free(&m);
    if (g_live == 0) puts("leak check: ok");
    else printf("leak check: %lld block(s) not freed\n", g_live);
    return 0;
}
