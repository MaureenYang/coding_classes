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
    l->head = l->tail = NULL;
    l->size = 0;
}

void list_free(List *l) {
    Node *cur = l->head;
    while (cur) {
        Node *next = cur->next;      /* 先記下下一個，free 之後就不能讀 cur->next 了 */
        xfree(cur);
        cur = next;
    }
    list_init(l);
}

static Node *new_node(int x, Node *next) {
    Node *n = xmalloc(sizeof *n);
    n->val = x;
    n->next = next;
    return n;
}

void push_front(List *l, int x) {
    l->head = new_node(x, l->head);
    if (l->tail == NULL) l->tail = l->head;   /* 原本是空串列 */
    l->size++;
}

void push_back(List *l, int x) {
    Node *n = new_node(x, NULL);
    if (l->tail) l->tail->next = n;
    else l->head = n;                         /* 原本是空串列 */
    l->tail = n;
    l->size++;
}

int pop_front(List *l) {
    Node *n = l->head;
    int v = n->val;
    l->head = n->next;
    if (l->head == NULL) l->tail = NULL;
    xfree(n);
    l->size--;
    return v;
}

int remove_first(List *l, int x) {
    Node *prev = NULL;
    for (Node **pp = &l->head; *pp; pp = &(*pp)->next) {
        Node *cur = *pp;
        if (cur->val == x) {
            *pp = cur->next;                  /* 讓「指向 cur 的指標」改指向 cur 的下一個 */
            if (l->tail == cur) l->tail = prev;
            xfree(cur);
            l->size--;
            return 1;
        }
        prev = cur;
    }
    return 0;
}

void list_reverse(List *l) {
    Node *prev = NULL, *cur = l->head;
    l->tail = l->head;                        /* 原本的第一個會變成最後一個 */
    while (cur) {
        Node *next = cur->next;
        cur->next = prev;
        prev = cur;
        cur = next;
    }
    l->head = prev;
}

void list_unique(List *l) {
    Node *cur = l->head;
    while (cur && cur->next) {
        if (cur->next->val == cur->val) {
            Node *dup = cur->next;
            cur->next = dup->next;
            xfree(dup);
            l->size--;
        } else {
            cur = cur->next;
        }
    }
    l->tail = cur;                            /* 走到最後的 cur 就是最後一個節點（空串列時是 NULL） */
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
