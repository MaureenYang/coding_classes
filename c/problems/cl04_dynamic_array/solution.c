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

typedef struct {
    int *data;
    size_t size;
    size_t cap;
} IntVec;

void vec_init(IntVec *v) {
    v->data = NULL;
    v->size = v->cap = 0;
}

void vec_free(IntVec *v) {
    xfree(v->data);
    vec_init(v);
}

static void grow_if_full(IntVec *v) {
    if (v->size < v->cap) return;
    size_t new_cap = v->cap == 0 ? 1 : v->cap * 2;
    v->data = xrealloc(v->data, new_cap * sizeof(int));   /* 舊資料會被搬到新空間 */
    v->cap = new_cap;
}

void vec_push(IntVec *v, int x) {
    grow_if_full(v);
    v->data[v->size++] = x;
}

int vec_pop(IntVec *v) {
    return v->data[--v->size];
}

void vec_insert(IntVec *v, size_t pos, int x) {
    grow_if_full(v);
    /* [pos, size) 整段往後移一格；區域重疊所以用 memmove */
    memmove(v->data + pos + 1, v->data + pos, (v->size - pos) * sizeof(int));
    v->data[pos] = x;
    v->size++;
}

int vec_erase(IntVec *v, size_t pos) {
    int removed = v->data[pos];
    memmove(v->data + pos, v->data + pos + 1, (v->size - pos - 1) * sizeof(int));
    v->size--;
    return removed;
}

/* ===== 以下不用修改 ===== */
int main(void) {
    int q;
    if (scanf("%d", &q) != 1) return 0;
    IntVec v;
    vec_init(&v);
    while (q--) {
        char op[8];
        long long i;
        int x;
        scanf("%7s", op);
        if (!strcmp(op, "push")) {
            scanf("%d", &x);
            vec_push(&v, x);
        } else if (!strcmp(op, "pop")) {
            if (v.size == 0) puts("empty");
            else printf("%d\n", vec_pop(&v));
        } else if (!strcmp(op, "get")) {
            scanf("%lld", &i);
            if (i < 0 || (size_t)i >= v.size) puts("out of range");
            else printf("%d\n", v.data[i]);
        } else if (!strcmp(op, "set")) {
            scanf("%lld %d", &i, &x);
            if (i < 0 || (size_t)i >= v.size) puts("out of range");
            else v.data[i] = x;
        } else if (!strcmp(op, "insert")) {
            scanf("%lld %d", &i, &x);
            if (i < 0 || (size_t)i > v.size) puts("out of range");
            else vec_insert(&v, (size_t)i, x);
        } else if (!strcmp(op, "erase")) {
            scanf("%lld", &i);
            if (i < 0 || (size_t)i >= v.size) puts("out of range");
            else printf("%d\n", vec_erase(&v, (size_t)i));
        } else if (!strcmp(op, "size")) {
            printf("%zu\n", v.size);
        } else if (!strcmp(op, "cap")) {
            printf("%zu\n", v.cap);
        } else if (!strcmp(op, "print")) {
            if (v.size == 0) puts("empty");
            for (size_t k = 0; k < v.size; k++) printf("%d%c", v.data[k], k + 1 < v.size ? ' ' : '\n');
        } else if (!strcmp(op, "clear")) {
            vec_free(&v);
            vec_init(&v);
        }
    }
    vec_free(&v);
    if (g_live == 0) puts("leak check: ok");
    else printf("leak check: %lld block(s) not freed\n", g_live);
    return 0;
}
