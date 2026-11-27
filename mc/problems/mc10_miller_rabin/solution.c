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

/* a 是不是 n 的 Miller–Rabin 證人（證明 n 是合數）；n − 1 = 2^s · d */
static int is_witness(u64 a, u64 n, u64 d, int s) {
    u64 x = powmod(a, d, n);
    if (x == 1 || x == n - 1) return 0;
    for (int i = 1; i < s; i++) {
        x = mulmod(x, x, n);
        if (x == n - 1) return 0;
    }
    return 1;
}

static int is_prime(u64 n) {
    static const u64 bases[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    if (n < 2) return 0;
    for (int i = 0; i < 12; i++)
        if (n % bases[i] == 0) return n == bases[i];
    u64 d = n - 1;
    int s = 0;
    while (d % 2 == 0) { d /= 2; s++; }
    for (int i = 0; i < 12; i++)
        if (is_witness(bases[i], n, d, s)) return 0;
    return 1;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        u64 n;
        scanf("%llu", &n);
        puts(is_prime(n) ? "prime" : "composite");
    }
    return 0;
}
