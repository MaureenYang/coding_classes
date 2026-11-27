#include <stdio.h>
#include <string.h>

typedef unsigned long long u64;
typedef unsigned __int128 u128;

static u64 p;

static u64 mulmod(u64 a, u64 b) { return (u64)((u128)a * b % p); }

static u64 powmod(u64 a, u64 e) {
    u64 r = 1 % p;
    for (a %= p; e; e >>= 1, a = mulmod(a, a))
        if (e & 1) r = mulmod(r, a);
    return r;
}

static u64 a[105], xs[105], ys[105];

int main(void) {
    int q;
    if (scanf("%llu %d", &p, &q) != 2) return 0;
    while (q--) {
        char op[10];
        scanf("%9s", op);
        if (strcmp(op, "SHARE") == 0) {
            int t, n;
            scanf("%llu %d %d", &a[0], &t, &n);
            for (int i = 1; i < t; i++) scanf("%llu", &a[i]);
            for (int x = 1; x <= n; x++) {           /* Horner 法求 f(x) */
                u64 y = 0;
                for (int i = t - 1; i >= 0; i--) y = (mulmod(y, (u64)x) + a[i]) % p;
                printf("%llu%c", y, x < n ? ' ' : '\n');
            }
        } else {
            int k;
            scanf("%d", &k);
            for (int i = 0; i < k; i++) scanf("%llu %llu", &xs[i], &ys[i]);
            u64 S = 0;                               /* f(0) = Σ yᵢ · Π xⱼ / (xⱼ − xᵢ) */
            for (int i = 0; i < k; i++) {
                u64 num = 1, den = 1;
                for (int j = 0; j < k; j++)
                    if (j != i) {
                        num = mulmod(num, xs[j]);
                        den = mulmod(den, (xs[j] + p - xs[i]) % p);
                    }
                S = (S + mulmod(ys[i], mulmod(num, powmod(den, p - 2)))) % p;
            }
            printf("%llu\n", S);
        }
    }
    return 0;
}
