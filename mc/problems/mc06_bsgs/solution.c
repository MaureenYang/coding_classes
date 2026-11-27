#include <stdio.h>
#include <stdlib.h>
#include <math.h>

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

/* ---- 開放定址雜湊表：key = g^j，val = j ---- */
#define HBITS 22
#define HSIZE (1u << HBITS)
static u64 hkey[HSIZE];
static long long hval[HSIZE];          /* -1 表示空格 */

static unsigned slot(u64 k) { return (unsigned)((k * 0x9E3779B97F4A7C15ULL) >> (64 - HBITS)); }

static void hput(u64 k, long long v) {  /* 已經有就不覆蓋（保留最小的 j） */
    unsigned i = slot(k);
    while (hval[i] != -1) {
        if (hkey[i] == k) return;
        i = (i + 1) & (HSIZE - 1);
    }
    hkey[i] = k; hval[i] = v;
}

static long long hget(u64 k) {
    unsigned i = slot(k);
    while (hval[i] != -1) {
        if (hkey[i] == k) return hval[i];
        i = (i + 1) & (HSIZE - 1);
    }
    return -1;
}

/* 最小的 x ≥ 0 使 g^x ≡ h (mod p)；沒有就回傳 -1 */
static long long bsgs(u64 g, u64 h, u64 p) {
    u64 n = (u64)sqrtl((long double)(p - 1)) + 1;          /* n² > p − 1 ≥ g 的階 */
    for (unsigned i = 0; i < HSIZE; i++) hval[i] = -1;
    u64 cur = 1;
    for (u64 j = 0; j < n; j++) {                           /* 嬰兒步：g^0 … g^(n−1) */
        hput(cur, (long long)j);
        cur = mulmod(cur, g, p);
    }
    u64 u = powmod(powmod(g, n, p), p - 2, p);              /* u = g^(−n) */
    u64 y = h % p;
    for (u64 i = 0; i <= n; i++) {                          /* 巨人步：h·u^i */
        long long j = hget(y);
        if (j >= 0) return (long long)(i * n + (u64)j);
        y = mulmod(y, u, p);
    }
    return -1;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        u64 p, g, h;
        scanf("%llu %llu %llu", &p, &g, &h);
        printf("%lld\n", bsgs(g, h, p));
    }
    return 0;
}
