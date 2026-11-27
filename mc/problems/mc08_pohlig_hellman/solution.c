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

static u64 inv(u64 a, u64 p) { return powmod(a, p - 2, p); }

/* a 模 m 的反元素（m 不一定是質數，gcd(a, m) = 1）：擴展歐幾里得 */
static u64 inv_general(u64 a, u64 m) {
    long long r0 = (long long)m, r1 = (long long)a, s0 = 0, s1 = 1;
    while (r1) {
        long long q = r0 / r1, t;
        t = r0 - q * r1; r0 = r1; r1 = t;
        t = s0 - q * s1; s0 = s1; s1 = t;
    }
    return (u64)(((s0 % (long long)m) + (long long)m) % (long long)m);
}

/* 解 gᵢ^x = hᵢ，其中 gᵢ 的階是 q^e；一次解一個 q 進位的位數 */
static u64 dlp_prime_power(u64 g, u64 h, u64 p, u64 q, int e) {
    u64 qe1 = 1;
    for (int i = 1; i < e; i++) qe1 *= q;           /* q^(e−1) */
    u64 gamma = powmod(g, qe1, p);                   /* 階為 q 的元素 */
    u64 x = 0, qk = 1, ginv = inv(g, p);
    u64 cur = h;                                     /* cur = h · g^(−x) */
    for (int k = 0; k < e; k++) {
        u64 pw = qe1;                                /* q^(e−1−k) */
        for (int i = 0; i < k; i++) pw /= q;
        u64 target = powmod(cur, pw, p);
        u64 d = 0, t = 1;                            /* 暴力找 gamma^d = target */
        while (t != target) { t = mulmod(t, gamma, p); d++; }
        x += d * qk;
        cur = mulmod(cur, powmod(ginv, d * qk, p), p);
        qk *= q;
    }
    return x;
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
            u64 gi = powmod(g, N / qe, p), hi = powmod(h, N / qe, p);
            u64 y = dlp_prime_power(gi, hi, p, q, e);    /* x ≡ y (mod q^e) */
            /* 合併：x + M·t ≡ y (mod qe)，t ≡ (y − x)·M⁻¹ */
            u64 diff = (y + qe - x % qe) % qe;
            u64 t = mulmod(diff, inv_general(M % qe, qe), qe);
            x += M * t;
            M *= qe;
        }
        printf("%llu\n", x);
    }
    return 0;
}
