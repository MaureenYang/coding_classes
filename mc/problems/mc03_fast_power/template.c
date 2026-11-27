#include <stdio.h>

typedef unsigned long long u64;
typedef unsigned __int128 u128;

/* a·b mod m：a、b 都可能接近 2^63，乘積要用 128 位元 */
static u64 mulmod(u64 a, u64 b, u64 m) {
    /* TODO */
    return 0;
}

/* a^e mod m，用平方乘法（看 e 的每一個二進位位元） */
static u64 powmod(u64 a, u64 e, u64 m) {
    /* TODO：注意 m = 1 時答案是 0 */
    return 0;
}

int main(void) {
    int q;
    if (scanf("%d", &q) != 1) return 0;
    while (q--) {
        u64 a, e, m;
        scanf("%llu %llu %llu", &a, &e, &m);
        printf("%llu\n", powmod(a, e, m));
    }
    return 0;
}
