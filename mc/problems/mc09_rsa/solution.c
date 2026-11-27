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
    ll r0 = (ll)phi, r1 = (ll)(e % phi), s0 = 0, s1 = 1;
    while (r1) {
        ll q = r0 / r1, t;
        t = r0 - q * r1; r0 = r1; r1 = t;
        t = s0 - q * s1; s0 = s1; s1 = t;
    }
    if (r0 != 1) return 0;
    return (u64)(((s0 % (ll)phi) + (ll)phi) % (ll)phi);
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
            u64 d = inverse(e, (p1 - 1) * (p2 - 1));
            if (d) printf("%llu %llu\n", p1 * p2, d);
            else puts("invalid");
        } else if (strcmp(op, "ENC") == 0) {
            u64 N, e, m;
            scanf("%llu %llu %llu", &N, &e, &m);
            printf("%llu\n", powmod(m, e, N));
        } else if (strcmp(op, "DEC") == 0) {
            u64 p1, p2, e, c;
            scanf("%llu %llu %llu %llu", &p1, &p2, &e, &c);
            u64 d = inverse(e, (p1 - 1) * (p2 - 1));
            printf("%llu\n", powmod(c, d, p1 * p2));
        } else {
            u64 N, e, D, S;
            scanf("%llu %llu %llu %llu", &N, &e, &D, &S);
            puts(powmod(S, e, N) == D % N ? "valid" : "invalid");
        }
    }
    return 0;
}
