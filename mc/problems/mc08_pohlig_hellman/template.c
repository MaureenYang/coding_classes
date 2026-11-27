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

/* a 模 m 的反元素（m 不一定是質數，gcd(a, m) = 1） */
static u64 inv_general(u64 a, u64 m) {
    /* TODO：擴展歐幾里得 */
    return 0;
}

/* 解 g^x = h，其中 g 的階是 q^e；回傳 0 ≤ x < q^e
   把 x 寫成 q 進位 x0 + x1·q + …，每一位都是一個「階為 q」的小 DLP */
static u64 dlp_prime_power(u64 g, u64 h, u64 p, u64 q, int e) {
    /* TODO */
    return 0;
}

int main(void) {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        u64 p, g, h;
        scanf("%llu %llu %llu", &p, &g, &h);
        u64 N = p - 1, n = N;
        u64 x = 0, M = 1;                            /* CRT：目前 x mod M */
        for (u64 q = 2; n > 1; q++) {                /* p − 1 的質因數都很小，試除即可 */
            if (n % q) continue;
            int e = 0;
            u64 qe = 1;
            while (n % q == 0) { n /= q; e++; qe *= q; }
            /* TODO：gi = g^(N/qe)、hi = h^(N/qe)，解出 x ≡ y (mod qe)，再用 CRT 併進 x、M */
        }
        printf("%llu\n", x);
    }
    return 0;
}
