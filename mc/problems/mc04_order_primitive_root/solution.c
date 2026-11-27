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

/* 把 n 的相異質因數存進 f，回傳個數 */
static int prime_factors(u64 n, u64 *f) {
    int k = 0;
    for (u64 d = 2; d * d <= n; d++)
        if (n % d == 0) {
            f[k++] = d;
            while (n % d == 0) n /= d;
        }
    if (n > 1) f[k++] = n;
    return k;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        u64 p, g, f[64];
        scanf("%llu %llu", &p, &g);
        int k = prime_factors(p - 1, f);

        u64 ord = p - 1;                 /* 階一定整除 p − 1：逐一拿掉多餘的質因數 */
        for (int i = 0; i < k; i++)
            while (ord % f[i] == 0 && powmod(g, ord / f[i], p) == 1) ord /= f[i];

        u64 r = 1;                       /* p = 2 時原根是 1 */
        if (p > 2)
            for (r = 2;; r++) {
                int ok = 1;
                for (int i = 0; i < k && ok; i++)
                    if (powmod(r, (p - 1) / f[i], p) == 1) ok = 0;
                if (ok) break;
            }
        printf("%llu %llu\n", ord, r);
    }
    return 0;
}
