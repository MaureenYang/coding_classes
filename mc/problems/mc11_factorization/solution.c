#include <stdio.h>
#include <stdlib.h>

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

static int is_prime(u64 n) {
    static const u64 B[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    if (n < 2) return 0;
    for (int i = 0; i < 12; i++)
        if (n % B[i] == 0) return n == B[i];
    u64 d = n - 1;
    int s = 0;
    while (d % 2 == 0) { d /= 2; s++; }
    for (int i = 0; i < 12; i++) {
        u64 x = powmod(B[i], d, n);
        if (x == 1 || x == n - 1) continue;
        int ok = 0;
        for (int r = 1; r < s && !ok; r++) {
            x = mulmod(x, x, n);
            if (x == n - 1) ok = 1;
        }
        if (!ok) return 0;
    }
    return 1;
}

static u64 gcd(u64 a, u64 b) { while (b) { u64 t = a % b; a = b; b = t; } return a; }

/* Pollard ρ：f(x) = x² + c，Floyd 判圈，每 128 步才做一次 gcd */
static u64 rho(u64 n) {
    if (n % 2 == 0) return 2;
    for (u64 c = 1;; c++) {
        u64 x = 2, y = 2, d = 1;
        while (d == 1) {
            u64 xs = x, ys = y, prod = 1;
            for (int i = 0; i < 128; i++) {
                x = (mulmod(x, x, n) + c) % n;
                y = (mulmod(y, y, n) + c) % n;
                y = (mulmod(y, y, n) + c) % n;
                prod = mulmod(prod, x > y ? x - y : y - x, n);
            }
            d = gcd(prod, n);
            if (d == n) {                     /* 一次跨太多步：退回去一步一步做 */
                x = xs; y = ys; d = 1;
                while (d == 1) {
                    x = (mulmod(x, x, n) + c) % n;
                    y = (mulmod(y, y, n) + c) % n;
                    y = (mulmod(y, y, n) + c) % n;
                    d = gcd(x > y ? x - y : y - x, n);
                }
            }
        }
        if (d != n) return d;                 /* 失敗（d = n）就換一個 c */
    }
}

static u64 fac[128];
static int nf;

static void factor(u64 n) {
    if (n == 1) return;
    if (is_prime(n)) { fac[nf++] = n; return; }
    u64 d = rho(n);
    factor(d);
    factor(n / d);
}

static int cmp(const void *a, const void *b) {
    u64 x = *(const u64 *)a, y = *(const u64 *)b;
    return x < y ? -1 : x > y;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        u64 n;
        scanf("%llu", &n);
        nf = 0;
        for (u64 p = 2; p < 100; p++)          /* 先除掉小質因數，ρ 比較好做 */
            while (n % p == 0) { fac[nf++] = p; n /= p; }
        factor(n);
        qsort(fac, nf, sizeof fac[0], cmp);
        for (int i = 0; i < nf;) {
            int j = i;
            while (j < nf && fac[j] == fac[i]) j++;
            if (i) putchar(' ');
            if (j - i == 1) printf("%llu", fac[i]);
            else printf("%llu^%d", fac[i], j - i);
            i = j;
        }
        putchar('\n');
    }
    return 0;
}
