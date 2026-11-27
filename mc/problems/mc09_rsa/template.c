#include <stdio.h>
#include <string.h>

typedef unsigned long long u64;
typedef long long ll;
typedef unsigned __int128 u128;

static u64 mulmod(u64 a, u64 b, u64 m) { return (u64)((u128)a * b % m); }

static u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1 % m;
    a %= m;
    for (; e; e >>= 1, a = mulmod(a, a, m))
        if (e & 1) r = mulmod(r, a, m);
    return r;
}

/* e 模 phi 的反元素；不互質時回傳 0 */
static u64 inverse(u64 e, u64 phi) {
    /* TODO：擴展歐幾里得 */
    return 0;
}

int main(void) {
    int q;
    if (scanf("%d", &q) != 1) return 0;
    while (q--) {
        char op[8];
        scanf("%7s", op);
        if (strcmp(op, "KEY") == 0) {
            u64 p1, p2, e;
            scanf("%llu %llu %llu", &p1, &p2, &e);
            /* TODO：輸出 N d，或 invalid */
        } else if (strcmp(op, "ENC") == 0) {
            u64 N, e, m;
            scanf("%llu %llu %llu", &N, &e, &m);
            /* TODO：輸出 c */
        } else if (strcmp(op, "DEC") == 0) {
            u64 p1, p2, e, c;
            scanf("%llu %llu %llu %llu", &p1, &p2, &e, &c);
            /* TODO：輸出 m */
        } else {
            u64 N, e, D, S;
            scanf("%llu %llu %llu %llu", &N, &e, &D, &S);
            /* TODO：輸出 valid 或 invalid */
        }
    }
    return 0;
}
