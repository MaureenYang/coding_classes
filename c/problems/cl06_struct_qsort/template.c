#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[21];
    int score;
    int age;
    int rank;
} Student;

int cmp_rank(const void *a, const void *b) {
    /* TODO：分數高的在前；同分年齡小的在前；再相同名字小的在前 */
    return 0;
}

int cmp_name(const void *a, const void *b) {
    /* TODO */
    return 0;
}

Student *find_by_name(Student *arr, int n, const char *name) {
    /* TODO：用 bsearch；找不到回傳 NULL */
    return NULL;
}

/* ===== 以下不用修改 ===== */
static Student arr[100000];

int main(void) {
    int n, q;
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < n; i++)
        scanf("%20s %d %d", arr[i].name, &arr[i].score, &arr[i].age);

    qsort(arr, n, sizeof(Student), cmp_rank);
    for (int i = 0; i < n; i++) {
        arr[i].rank = i + 1;
        printf("%d %s %d %d\n", arr[i].rank, arr[i].name, arr[i].score, arr[i].age);
    }

    qsort(arr, n, sizeof(Student), cmp_name);    /* 改成依名字排序，才能二分搜尋 */
    if (scanf("%d", &q) != 1) q = 0;
    while (q--) {
        char name[32];
        scanf("%31s", name);
        Student *s = find_by_name(arr, n, name);
        if (s) printf("%s %d %d %d\n", s->name, s->score, s->age, s->rank);
        else printf("%s not found\n", name);
    }
    return 0;
}
