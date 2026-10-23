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

typedef struct Node {
    int val;
    struct Node *next;
} Node;

typedef struct {
    Node *head;
    Node *tail;
    size_t size;
} List;

void list_init(List *l) {
    /* TODO */
}

void list_free(List *l) {
    /* TODO：釋放每個節點，最後變回空串列 */
}

void push_front(List *l, int x) {
    /* TODO：空串列時 tail 也要指向新節點 */
}

void push_back(List *l, int x) {
    /* TODO：用 tail，O(1) */
}

int pop_front(List *l) {
    /* TODO：移除後變空的話，tail 也要變成 NULL */
    return 0;
}

int remove_first(List *l, int x) {
    /* TODO：提示：Node **pp = &l->head; 刪掉的是最後一個時記得更新 tail */
    return 0;
}

void list_reverse(List *l) {
    /* TODO */
}

void list_unique(List *l) {
    /* TODO：刪除相鄰重複，記得更新 tail */
}

/* ===== 以下不用修改 ===== */
int main(void) {
    int q;
    if (scanf("%d", &q) != 1) return 0;
    List l;
    list_init(&l);
    while (q--) {
        char op[8];
        int x;
        scanf("%7s", op);
        if (!strcmp(op, "pushf")) { scanf("%d", &x); push_front(&l, x); }
        else if (!strcmp(op, "pushb")) { scanf("%d", &x); push_back(&l, x); }
        else if (!strcmp(op, "popf")) {
            if (l.size == 0) puts("empty");
            else printf("%d\n", pop_front(&l));
        } else if (!strcmp(op, "del")) {
            scanf("%d", &x);
            puts(remove_first(&l, x) ? "ok" : "not found");
        } else if (!strcmp(op, "rev")) list_reverse(&l);
        else if (!strcmp(op, "uniq")) list_unique(&l);
        else if (!strcmp(op, "size")) printf("%zu\n", l.size);
        else if (!strcmp(op, "ends")) {
            if (!l.head) puts("empty");
            else printf("%d %d\n", l.head->val, l.tail->val);
        } else if (!strcmp(op, "print")) {
            if (!l.head) puts("empty");
            for (Node *p = l.head; p; p = p->next) printf("%d%c", p->val, p->next ? ' ' : '\n');
        }
    }
    list_free(&l);
    if (g_live == 0) puts("leak check: ok");
    else printf("leak check: %lld block(s) not freed\n", g_live);
    return 0;
}
