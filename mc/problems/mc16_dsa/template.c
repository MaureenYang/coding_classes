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
    u64 p, q, g;
    int n;
    if (scanf("%llu %llu %llu %d", &p, &q, &g, &n) != 4) return 0;
    while (n--) {
        char op[8];
        scanf("%7s", op);
        if (strcmp(op, "SIGN") == 0) {
            u64 s, D, e;
            scanf("%llu %llu %llu", &s, &D, &e);
            u64 S1 = 0, S2 = 0;
            /* TODO：S1 = (g^e mod p) mod q，S2 = (D + s·S1)·e⁻¹ mod q */
            printf("%llu %llu\n", S1, S2);
        } else {
            u64 v, D, S1, S2;
            scanf("%llu %llu %llu %llu", &v, &D, &S1, &S2);
            /* TODO：V1 = D·S2⁻¹、V2 = S1·S2⁻¹（mod q），
                     (g^V1 · v^V2 mod p) mod q == S1 就輸出 valid，否則 invalid */
        }
    }
    return 0;
}
