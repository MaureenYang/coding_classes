#include <stdio.h>
#include <string.h>

typedef unsigned long long u64;
typedef unsigned __int128 u128;

static u64 mulmod(u64 a, u64 b, u64 m) { return (u64)((u128)a * b % m); }

static u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1 % m;
    a %= m;
    for (; e; e >>= 1, a = mulmod(a, a, m))
        if (e & 1) r = mulmod(r, a, m);
    return r;
}

int main(void) {
    u64 p, g;
    int q;
    if (scanf("%llu %llu %d", &p, &g, &q) != 3) return 0;
    while (q--) {
        char op[8];
        scanf("%7s", op);
        if (strcmp(op, "DH") == 0) {
            u64 a, b;
            scanf("%llu %llu", &a, &b);
            /* TODO：輸出 A = g^a、B = g^b、共同金鑰 */
        } else if (strcmp(op, "ENC") == 0) {
            u64 A, k, m;
            scanf("%llu %llu %llu", &A, &k, &m);
            /* TODO：輸出 c1 c2 */
        } else {
            u64 a, c1, c2;
            scanf("%llu %llu %llu", &a, &c1, &c2);
            /* TODO：輸出明文 m */
        }
    }
    return 0;
}
