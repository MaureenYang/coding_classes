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
    const Student *x = a, *y = b;
    if (x->score != y->score) return y->score - x->score;   /* 分數高的在前 */
    if (x->age != y->age) return x->age - y->age;           /* 年齡小的在前 */
    return strcmp(x->name, y->name);                        /* 名字小的在前 */
}

int cmp_name(const void *a, const void *b) {
    const Student *x = a, *y = b;
    return strcmp(x->name, y->name);
}

Student *find_by_name(Student *arr, int n, const char *name) {
    if (strlen(name) > 20) return NULL;          /* 比 20 個字元長：放不進 name[21]，一定找不到 */
    Student key;                                 /* 只填 name 的「查詢用」學生 */
    strcpy(key.name, name);
    return bsearch(&key, arr, n, sizeof(Student), cmp_name);
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
