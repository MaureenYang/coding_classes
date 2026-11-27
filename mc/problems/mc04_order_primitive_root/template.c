#include <stdio.h>

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

/* 把 n 的「相異」質因數存進 f，回傳個數（試除法） */
static int prime_factors(u64 n, u64 *f) {
    /* TODO */
    return 0;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        u64 p, g, f[64];
        scanf("%llu %llu", &p, &g);
        int k = prime_factors(p - 1, f);

        u64 ord = p - 1;
        /* TODO：g 的階整除 p − 1。對每個質因數 q，只要 q | ord 且 g^(ord/q) ≡ 1，就把 ord 除以 q */

        u64 r = 1;
        /* TODO：找最小的原根 r（p = 2 時是 1）：
           r 是原根 ⇔ 對 p − 1 的每個質因數 q，r^((p−1)/q) ≢ 1 (mod p) */

        printf("%llu %llu\n", ord, r);
    }
    return 0;
}
