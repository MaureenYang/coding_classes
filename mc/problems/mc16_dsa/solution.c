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
            u64 S1 = powmod(g, e, p) % q;
            u64 einv = powmod(e, q - 2, q);                       /* q 是質數 */
            u64 S2 = mulmod((D + mulmod(s, S1, q)) % q, einv, q);
            printf("%llu %llu\n", S1, S2);
        } else {
            u64 v, D, S1, S2;
            scanf("%llu %llu %llu %llu", &v, &D, &S1, &S2);
            u64 w = powmod(S2, q - 2, q);
            u64 V1 = mulmod(D, w, q), V2 = mulmod(S1, w, q);
            u64 x = mulmod(powmod(g, V1, p), powmod(v, V2, p), p) % q;
            puts(x == S1 ? "valid" : "invalid");
        }
    }
    return 0;
}
