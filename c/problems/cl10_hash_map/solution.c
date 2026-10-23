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

static Entry **alloc_buckets(size_t n) {
    Entry **b = xmalloc(n * sizeof(Entry *));
    for (size_t i = 0; i < n; i++) b[i] = NULL;
    return b;
}

void hm_init(HashMap *m) {
    m->nbuckets = 8;
    m->buckets = alloc_buckets(m->nbuckets);
    m->size = 0;
}

void hm_free(HashMap *m) {
    for (size_t i = 0; i < m->nbuckets; i++) {
        Entry *e = m->buckets[i];
        while (e) {
            Entry *next = e->next;
            xfree(e->key);
            xfree(e);
            e = next;
        }
    }
    xfree(m->buckets);
    m->buckets = NULL;
    m->nbuckets = m->size = 0;
}

long long *hm_get(HashMap *m, const char *key) {
    for (Entry *e = m->buckets[hash_str(key) % m->nbuckets]; e; e = e->next)
        if (strcmp(e->key, key) == 0) return &e->val;
    return NULL;
}

static void rehash(HashMap *m) {
    size_t new_n = m->nbuckets * 2;
    Entry **nb = alloc_buckets(new_n);
    for (size_t i = 0; i < m->nbuckets; i++) {
        Entry *e = m->buckets[i];
        while (e) {
            Entry *next = e->next;
            size_t k = hash_str(e->key) % new_n;
            e->next = nb[k];            /* 把節點本身搬到新桶子的最前面 */
            nb[k] = e;
            e = next;
        }
    }
    xfree(m->buckets);
    m->buckets = nb;
    m->nbuckets = new_n;
}

void hm_put(HashMap *m, const char *key, long long val) {
    long long *p = hm_get(m, key);
    if (p) { *p = val; return; }
    Entry *e = xmalloc(sizeof *e);
    e->key = xmalloc(strlen(key) + 1);
    strcpy(e->key, key);
    e->val = val;
    size_t k = hash_str(key) % m->nbuckets;
    e->next = m->buckets[k];
    m->buckets[k] = e;
    m->size++;
    if (m->size > 2 * m->nbuckets) rehash(m);
}

int hm_del(HashMap *m, const char *key) {
    for (Entry **pp = &m->buckets[hash_str(key) % m->nbuckets]; *pp; pp = &(*pp)->next) {
        Entry *e = *pp;
        if (strcmp(e->key, key) == 0) {
            *pp = e->next;
            xfree(e->key);
            xfree(e);
            m->size--;
            return 1;
        }
    }
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
